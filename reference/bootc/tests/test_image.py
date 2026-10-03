#!/usr/bin/env python3
"""Container smoke tests; never production paths, identities or cloud credentials.

Run inside a disposable image container with --network=none. These are not
UEFI/SELinux/mount-loss/rollback tests and cannot replace booted VM validation.
"""
import base64
import json
import os
from pathlib import Path
import secrets
import subprocess
import tempfile
import time
import unittest
import urllib.error
import urllib.request


def run(*args, **kwargs):
    return subprocess.run(args, check=True, text=True, capture_output=True, **kwargs)


class ImageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="mini-server-test-")
        cls.root = Path(cls.temp.name)
        if subprocess.run(["getent", "passwd", "dab"], stdout=subprocess.DEVNULL).returncode == 0:
            raise AssertionError("Image unexpectedly contains the installation account")
        run("useradd", "--uid", "1000", "--groups", "wheel", "--create-home", "dab")

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_sudo_is_account_scoped_and_unattended(self):
        run("visudo", "--check")
        result = run("runuser", "-u", "dab", "--", "sudo", "-n", "id", "-u")
        self.assertEqual(result.stdout.strip(), "0")
        rule = Path("/etc/sudoers.d/90-mini-server-dab").read_text()
        self.assertIn("dab ALL=(ALL:ALL) NOPASSWD: ALL", rule)
        self.assertNotIn("%wheel", rule)

    def test_ssh_policy(self):
        run("ssh-keygen", "-A")
        policy = run("sshd", "-T").stdout.splitlines()
        for expected in ("passwordauthentication no", "kbdinteractiveauthentication no", "permitrootlogin no"):
            self.assertIn(expected, policy)

    def test_absent_storage_fails_closed(self):
        result = subprocess.run(["/usr/libexec/mini-server-storage-ready", "test-fs", "test-md"], text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not mounted", result.stderr)
        self.assertFalse(Path("/srv/storage").exists())

    def test_no_desktop_manager_or_automatic_workloads(self):
        for package in ("lightdm", "gdm", "sddm"):
            self.assertNotEqual(subprocess.run(["rpm", "-q", package], stdout=subprocess.DEVNULL).returncode, 0)
        for unit in ("radicale.service", "syncthing@dab.service"):
            status = subprocess.run(["systemctl", "is-enabled", unit], text=True, capture_output=True)
            self.assertNotEqual(status.stdout.strip(), "enabled")

    def test_collector_validates_chezmoi_configuration(self):
        env = dict(os.environ, HOME=str(self.root / "collector-home"))
        run("otelcol", "validate", "--config=file:/otelcol-test.yaml", env=env)
        dropin = Path("/etc/systemd/user/otelcol.service.d/10-image-binary.conf").read_text()
        self.assertIn("/usr/bin/otelcol", dropin)
        neovim = Path("/etc/systemd/user/neovim-server.service.d/10-private-listener.conf").read_text()
        self.assertIn("127.0.0.1:6666", neovim)
        self.assertNotIn("0.0.0.0", neovim)

    def test_collector_accepts_synthetic_telemetry(self):
        home = self.root / "telemetry-home"
        log_path = self.root / "collector.log"
        log = log_path.open("w")
        process = subprocess.Popen(["otelcol", "--config=file:/otelcol-test.yaml"], env=dict(os.environ, HOME=str(home)), stdout=log, stderr=log)
        log.close()
        payload = json.dumps({"resourceLogs": [{"scopeLogs": [{"logRecords": [{"timeUnixNano": str(time.time_ns()), "body": {"stringValue": "synthetic telemetry"}}]}]}]}).encode()
        try:
            ready = False
            for _ in range(50):
                try:
                    request = urllib.request.Request("http://127.0.0.1:4318/v1/logs", data=payload, headers={"Content-Type": "application/json"})
                    with urllib.request.urlopen(request, timeout=2) as response:
                        self.assertEqual(response.status, 200)
                    ready = True
                    break
                except (OSError, urllib.error.URLError):
                    time.sleep(0.1)
            self.assertTrue(ready, log_path.read_text())
        finally:
            process.terminate()
            process.wait(timeout=5)
        output = home / ".local/state/otelcol/agent-logs.jsonl"
        self.assertIn("synthetic telemetry", output.read_text())

    def test_syncthing_generates_fresh_isolated_identity(self):
        home = self.root / "syncthing"
        run("syncthing", "generate", "--home", str(home), "--no-port-probing")
        for name in ("config.xml", "cert.pem", "key.pem"):
            self.assertTrue((home / name).is_file())
        self.assertEqual((home / "key.pem").stat().st_mode & 0o077, 0)

    def test_restic_encrypted_unattended_restore_with_metadata(self):
        folder = self.root / "restic"
        folder.mkdir()
        data = folder / "data"
        data.mkdir()
        original = data / "scan.pdf"
        original.write_bytes(b"synthetic scanned document\n")
        original.chmod(0o640)
        os.setxattr(original, "user.mini-server-test", b"preserved")
        os.link(original, data / "scan-hardlink.pdf")
        (data / "scan-link.pdf").symlink_to("scan.pdf")
        password_file = folder / "password"
        password_file.write_text(secrets.token_urlsafe(32))
        password_file.chmod(0o600)
        env = dict(os.environ, RESTIC_REPOSITORY=str(folder / "repo"), RESTIC_PASSWORD_FILE=str(password_file), RESTIC_CACHE_DIR=str(folder / "cache"))
        run("restic", "init", env=env)
        run("restic", "backup", ".", cwd=data, env=env)
        run("restic", "check", "--read-data", env=env)
        destination = folder / "restore"
        run("restic", "restore", "latest", "--target", str(destination), env=env)
        restored = next(destination.rglob("scan.pdf"))
        self.assertEqual(restored.read_bytes(), original.read_bytes())
        self.assertEqual(restored.stat().st_mode & 0o777, 0o640)
        self.assertEqual(os.getxattr(restored, "user.mini-server-test"), b"preserved")
        self.assertEqual(restored.stat().st_ino, (restored.parent / "scan-hardlink.pdf").stat().st_ino)
        self.assertEqual(os.readlink(restored.parent / "scan-link.pdf"), "scan.pdf")
        snapshots = json.loads(run("restic", "snapshots", "--json", env=env).stdout)
        self.assertEqual(len(snapshots), 1)

    def test_radicale_synthetic_collection_survives_restart(self):
        password = secrets.token_urlsafe(24)
        run("htpasswd", "-iBc", "/etc/radicale/users", "test", input=password + "\n")
        run("chown", "root:radicale", "/etc/radicale/users")
        run("chmod", "0640", "/etc/radicale/users")
        run("install", "-d", "-o", "radicale", "-g", "radicale", "/var/lib/radicale/collections")
        auth = "Basic " + base64.b64encode(("test:" + password).encode()).decode()
        def request(path, method="GET", data=None, content_type=None):
            headers = {"Authorization": auth}
            if content_type:
                headers["Content-Type"] = content_type
            with urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:5232" + path, data=data, headers=headers, method=method), timeout=5) as response:
                return response.status, response.read()
        log_path = self.root / "radicale.log"
        def start():
            log = log_path.open("w")
            process = subprocess.Popen(["runuser", "-u", "radicale", "--", "radicale", "--config", "/etc/radicale/config"], stdout=log, stderr=log)
            log.close()
            for _ in range(50):
                try:
                    request("/")
                    return process
                except (OSError, urllib.error.URLError):
                    time.sleep(0.1)
            process.terminate()
            process.wait(timeout=5)
            self.fail("Radicale did not become ready: " + log_path.read_text())
        process = start()
        try:
            xml = b'<C:mkcalendar xmlns:D="DAV:" xmlns:C="urn:ietf:params:xml:ns:caldav"><D:set><D:prop><D:displayname>Test</D:displayname><C:supported-calendar-component-set><C:comp name="VTODO"/></C:supported-calendar-component-set></D:prop></D:set></C:mkcalendar>'
            self.assertEqual(request("/test/tasks/", "MKCALENDAR", xml, "application/xml")[0], 201)
            todo = b"BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//mini-server-test//EN\r\nBEGIN:VTODO\r\nUID:synthetic-test\r\nDTSTAMP:20261002T000000Z\r\nSUMMARY:Synthetic task\r\nEND:VTODO\r\nEND:VCALENDAR\r\n"
            self.assertIn(request("/test/tasks/task.ics", "PUT", todo, "text/calendar")[0], (201, 204))
            self.assertIn(b"Synthetic task", request("/test/tasks/task.ics")[1])
        finally:
            process.terminate()
            process.wait(timeout=5)
        process = start()
        try:
            self.assertIn(b"Synthetic task", request("/test/tasks/task.ics")[1])
        finally:
            process.terminate()
            process.wait(timeout=5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
