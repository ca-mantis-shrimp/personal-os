"""Target account logic against disposable files and a fake account backend.

No real useradd/groupadd/chpasswd/hostnamectl/restorecon operations are executed.
Synthetic public keys and password-like test inputs are generated at runtime.
"""
import base64
import importlib.machinery
import importlib.util
import json
import os
import secrets
import shutil
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "mkosi.profiles/mini-server/mkosi.extra/usr/libexec/personal-os-account"
class SourceOnlyLoader(importlib.machinery.SourceFileLoader):
    """Load trusted repository source, never read/write ExtraTrees bytecode."""

    def get_code(self, fullname):
        return self.source_to_code(self.get_data(self.path), self.path)


loader = SourceOnlyLoader("account", str(HELPER))
spec = importlib.util.spec_from_loader(loader.name, loader)
if spec is None:
    raise RuntimeError("Unable to load the account test module")
account = importlib.util.module_from_spec(spec)
loader.exec_module(account)


def key():
    fields = [b"ssh-ed25519", secrets.token_bytes(32)]
    blob = b"".join(struct.pack(">I", len(field)) + field for field in fields)
    return "ssh-ed25519 " + base64.b64encode(blob).decode() + " synthetic-test"


def password():
    alphabet = "./abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return ("$6$" + "".join(secrets.choice(alphabet) for _ in range(16)) + "$" +
            "".join(secrets.choice(alphabet) for _ in range(86))).encode()


class FakeBackend:
    def __init__(self, root):
        self.root = root
        self.users = {}
        self.groups = {"wheel": SimpleNamespace(gr_name="wheel", gr_gid=10, gr_mem=[])}
        self.calls = []
        self.host = "unconfigured"
        self.fail_on: str | None = None

    def lookup(self, kind, value):
        if kind == "user":
            return self.users.get(value)
        if kind == "group":
            return self.groups.get(value)
        if kind == "uid":
            return next((u for u in self.users.values() if u.pw_uid == value), None)
        return next((g for g in self.groups.values() if g.gr_gid == value), None)

    def hostname(self):
        return self.host

    def ids(self, kind):
        return ([u.pw_uid for u in self.users.values()] if kind == "subuid"
                else [g.gr_gid for g in self.groups.values()])

    def run(self, args, input: bytes | None = None):
        # Only command names/flags are retained. Secret stdin is not recorded.
        self.calls.append(args)
        if self.fail_on == args[0]:
            self.fail_on = None
            raise account.ProvisionError("Injected synthetic failure")
        name = args[-1]
        if args[0] == "groupadd":
            self.groups[name] = SimpleNamespace(gr_name=name, gr_gid=int(args[2]), gr_mem=[])
        elif args[0] == "useradd":
            self.users[name] = SimpleNamespace(pw_name=name,
                pw_uid=int(args[args.index("--uid") + 1]),
                pw_gid=int(args[args.index("--gid") + 1]),
                pw_dir=args[args.index("--home-dir") + 1],
                pw_shell=args[args.index("--shell") + 1])
            (self.root / "etc/shadow").write_bytes(name.encode() + b":!!:1:0:99999:7:::\n")
        elif args[0] == "usermod":
            self.groups["wheel"].gr_mem.append(name)
        elif args[0] == "loginctl":
            marker = self.root / "var/lib/systemd/linger" / name
            marker.parent.mkdir(parents=True, exist_ok=True)
            marker.write_bytes(b"")
            marker.chmod(0o644)
        elif args[0] == "hostnamectl":
            self.host = name
        elif args[0] == "chpasswd":
            if input is None:
                raise AssertionError("Synthetic chpasswd requires stdin")
            user, hashed = input.strip().split(b":", 1)
            (self.root / "etc/shadow").write_bytes(user + b":" + hashed + b":1:0:99999:7:::\n")
        elif args[0] not in ("restorecon", "visudo"):
            raise AssertionError("Unexpected account command")


@unittest.skipUnless(1000 <= os.getuid() <= 60000, "file tests use the unprivileged test UID")
class AccountTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="personal-os-account-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "etc").mkdir()
        (self.root / "etc/shadow").write_bytes(b"")
        (self.root / "etc/shadow").chmod(0o600)
        (self.root / "usr/lib").mkdir(parents=True)
        (self.root / "usr/lib/os-release").write_text("ID=fedora\n")
        self.config = {"version": 1, "username": "synthetic", "uid": os.getuid(),
            "gid": os.getgid(), "hostname": "synthetic-server", "shell": "/usr/bin/bash",
            "ssh_public_keys": [key()], "passwordless_sudo": True}
        self.password: bytes | None = password()
        self.backend = FakeBackend(self.root)

    def provision(self, config=True, password=True):
        return account.provision(self.root, json.dumps(self.config).encode() if config else None,
            self.password if password else None, self.backend, os.getuid(), os.getgid())

    def test_enrollment_and_repeat_preserve_local_changes(self):
        home = self.root / "home/synthetic"
        home.mkdir(parents=True)
        personal = home / "keep-me"
        personal.write_text("mutable data\n")
        self.provision()
        keys = home / ".ssh/authorized_keys"
        self.assertEqual(keys.stat().st_mode & 0o777, 0o600)
        policy = self.root / "etc/sudoers.d/90-personal-os-account"
        self.assertEqual(policy.stat().st_mode & 0o777, 0o440)
        self.assertEqual(policy.read_text(), "synthetic ALL=(ALL:ALL) NOPASSWD: ALL\n")
        state = self.root / "var/lib/personal-os/account.json"
        self.assertEqual(json.loads(state.read_text())["phase"], "complete")
        assert self.password is not None
        self.assertNotIn(self.password, state.read_bytes())
        self.assertEqual(personal.read_text(), "mutable data\n")
        keys.write_text(key() + "\n")
        (self.root / "etc/shadow").write_text("synthetic:operator-changed:1:0:99999:7:::\n")
        self.backend.calls.clear()
        self.provision(config=False, password=False)
        self.assertEqual(self.backend.calls, [])
        self.assertIn("operator-changed", (self.root / "etc/shadow").read_text())
        self.assertEqual(personal.read_text(), "mutable data\n")

    def test_arch_enrollment_without_restorecon_preserves_retry_policy(self):
        (self.root / "usr/lib/os-release").write_text('ID="arch"\n')
        # Arch's regular local NSS file, not a Fedora authselect chain.
        (self.root / "etc/nsswitch.conf").write_text("passwd: files systemd\nsubid: files\n")
        self.backend.fail_on = "restorecon"
        self.provision()
        self.assertNotIn("restorecon", [call[0] for call in self.backend.calls])
        state = self.root / "var/lib/personal-os/account.json"
        self.assertEqual(json.loads(state.read_text())["phase"], "complete")
        self.assertIn("synthetic:", (self.root / "etc/subuid").read_text())
        self.assertEqual((self.root / "home/synthetic/.ssh/authorized_keys").stat().st_mode & 0o777,
                         0o600)
        self.backend.calls.clear()
        self.provision(config=False, password=False)
        self.assertEqual(self.backend.calls, [])

    def test_fedora_restorecon_failure_is_not_skipped(self):
        self.backend.fail_on = "restorecon"
        with self.assertRaises(account.ProvisionError):
            self.provision()
        self.assertIn("restorecon", [call[0] for call in self.backend.calls])
        state = self.root / "var/lib/personal-os/account.json"
        self.assertEqual(json.loads(state.read_text())["phase"], "pending")
        self.provision()
        self.assertEqual(json.loads(state.read_text())["phase"], "complete")

    def test_platform_identity_is_not_taken_from_mutable_etc(self):
        (self.root / "etc/os-release").write_text("ID=arch\n")
        self.provision()
        self.assertIn("restorecon", [call[0] for call in self.backend.calls])

    def test_platform_identity_missing_unknown_duplicate_or_symlink_fails_early(self):
        release = self.root / "usr/lib/os-release"
        for content in ("ID=debian\n", "ID=arch\nID=fedora\n", "NAME=Arch\n"):
            with self.subTest(content=content):
                release.write_text(content)
                with self.assertRaises(account.ProvisionError):
                    self.provision()
                self.assertEqual(self.backend.calls, [])
                self.assertFalse((self.root / "var/lib/personal-os").exists())
        release.unlink()
        with self.assertRaises(account.ProvisionError):
            self.provision()
        release.symlink_to(self.root / "etc/os-release")
        (self.root / "etc/os-release").write_text("ID=arch\n")
        with self.assertRaises(OSError):
            self.provision()
        self.assertEqual(self.backend.calls, [])
        self.assertFalse((self.root / "var/lib/personal-os").exists())

    def test_arch_rejects_active_selinux_filesystem_before_mutation(self):
        (self.root / "usr/lib/os-release").write_text("ID=arch\n")
        (self.root / "sys/fs/selinux").mkdir(parents=True)
        (self.root / "sys/fs/selinux/enforce").write_text("1\n")
        with self.assertRaisesRegex(account.ProvisionError, "active SELinux"):
            self.provision()
        self.assertEqual(self.backend.calls, [])
        self.assertFalse((self.root / "var/lib/personal-os").exists())

    def test_runtime_context_contains_only_identity_and_is_retry_safe(self):
        self.provision()
        account.publish_context(self.root, self.config, os.getuid(), os.getgid())
        path = self.root / "run/personal-os/account-context.json"
        context = json.loads(path.read_text())
        self.assertEqual(set(context), {"version", "username", "uid", "gid", "hostname"})
        self.assertNotIn(self.password, path.read_bytes())
        self.assertNotIn("ssh_public_keys", context)
        self.assertEqual(path.stat().st_mode & 0o777, 0o644)
        account.publish_context(self.root, self.config, os.getuid(), os.getgid())
        context["hostname"] = "divergent-runtime-context"
        path.write_text(json.dumps(context))
        with self.assertRaisesRegex(account.ProvisionError, "Runtime account context differs"):
            account.publish_context(self.root, self.config, os.getuid(), os.getgid())
        self.assertEqual(json.loads(path.read_text())["hostname"], "divergent-runtime-context")

    def test_retry_after_useradd_failure(self):
        self.backend.fail_on = "useradd"
        with self.assertRaises(account.ProvisionError):
            self.provision()
        state = self.root / "var/lib/personal-os/account.json"
        self.assertEqual(json.loads(state.read_text())["phase"], "pending")
        self.provision()
        self.assertEqual(json.loads(state.read_text())["phase"], "complete")
        self.assertEqual(sum(c[0] == "groupadd" for c in self.backend.calls), 1)

    def test_retry_after_password_applied_but_final_journal_write_failed(self):
        original = account.Files.write
        def fail_complete(files, path, data, **kwargs):
            if path.endswith("account.json") and b'"phase": "complete"' in data:
                raise OSError("Synthetic journal write failure")
            return original(files, path, data, **kwargs)
        with (patch.object(account.Files, "write", fail_complete),
              self.assertRaises(OSError)):
            self.provision()
        self.provision()
        self.assertEqual(sum(c[0] == "chpasswd" for c in self.backend.calls), 1)

    def test_refuses_numeric_identity_conflict(self):
        self.backend.users["someone-else"] = SimpleNamespace(pw_name="someone-else", pw_uid=os.getuid())
        with self.assertRaises(account.ProvisionError):
            self.provision()
        self.assertEqual(self.backend.calls, [])

    def test_refuses_existing_account_without_journal(self):
        self.backend.users["synthetic"] = SimpleNamespace(pw_name="synthetic", pw_uid=os.getuid(),
            pw_gid=os.getgid(), pw_dir="/home/synthetic", pw_shell="/usr/bin/bash")
        with self.assertRaises(account.ProvisionError):
            self.provision()
        self.assertEqual(self.backend.calls, [])

    def test_refuses_changed_enrollment_configuration(self):
        self.provision()
        self.backend.calls.clear()
        self.config["hostname"] = "different-target"
        with self.assertRaises(account.ProvisionError):
            self.provision()
        self.assertEqual(self.backend.calls, [])

    def test_home_symlink_is_not_followed(self):
        (self.root / "home").mkdir()
        outside = self.root / "outside"
        outside.mkdir()
        (self.root / "home/synthetic").symlink_to(outside, target_is_directory=True)
        with self.assertRaises(OSError):
            self.provision()
        self.assertEqual(self.backend.calls, [])
        self.assertEqual(list(outside.iterdir()), [])

    def test_conflicting_keys_are_never_replaced(self):
        directory = self.root / "home/synthetic/.ssh"
        directory.mkdir(parents=True)
        path = directory / "authorized_keys"
        path.write_text(key() + "\n")
        path.chmod(0o600)
        before = path.read_bytes()
        with self.assertRaises(account.ProvisionError):
            self.provision()
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(self.backend.calls, [])

    def test_missing_and_plaintext_console_credentials_fail_before_commands(self):
        for value in (None, b"", b"plaintext", b"!"):
            self.password = value
            with self.assertRaises(account.ProvisionError):
                self.provision()
            self.assertEqual(self.backend.calls, [])

    def test_unsupported_journal_version_is_not_downgraded(self):
        self.provision()
        path = self.root / "var/lib/personal-os/account.json"
        state = json.loads(path.read_text())
        state["version"] = 2
        path.write_text(json.dumps(state))
        before = path.read_bytes()
        self.backend.calls.clear()
        with self.assertRaises(account.ProvisionError):
            self.provision(config=False, password=False)
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(self.backend.calls, [])

    def test_unprotected_journal_fails_closed(self):
        self.provision()
        path = self.root / "var/lib/personal-os/account.json"
        path.chmod(0o644)
        self.backend.calls.clear()
        with self.assertRaises(account.ProvisionError):
            self.provision(config=False, password=False)
        self.assertEqual(self.backend.calls, [])

    def test_account_readiness_requires_expected_hostname(self):
        self.provision()
        self.backend.calls.clear()
        self.backend.host = "operator-changed"
        with self.assertRaises(account.ProvisionError):
            self.provision(config=False, password=False)
        self.assertEqual(self.backend.calls, [])

    @unittest.skipUnless(shutil.which("visudo"), "visudo is required")
    def test_generated_sudo_policy_parses_with_real_visudo(self):
        self.provision()
        subprocess.run(["visudo", "--check", "--file",
            str(self.root / "etc/sudoers.d/90-personal-os-account")],
            capture_output=True, check=True, timeout=10)


class ValidationTests(unittest.TestCase):
    def test_configuration_rejects_root_identity_and_ssh_options(self):
        config = {"version": 1, "username": "synthetic", "uid": 1000,
            "gid": 1000, "hostname": "synthetic-server", "shell": "/usr/bin/bash",
            "ssh_public_keys": [key()], "passwordless_sudo": True}
        for field, value in [("uid", 0), ("gid", True), ("username", "../../escape"),
                             ("ssh_public_keys", ['command="shell" ' + key()]),
                             ("ssh_public_keys", ["ssh-ed25519 invalid"]),
                             ("hostname", "host\ninjection")]:
            candidate = dict(config)
            candidate[field] = value
            with self.subTest(field=field), self.assertRaises(account.ProvisionError):
                account.config_from_json(json.dumps(candidate))

    def test_profile_postinstall_only_masks_units_in_disposable_buildroot(self):
        with tempfile.TemporaryDirectory(prefix="personal-os-buildroot-") as temp:
            root = Path(temp)
            units = root / "usr/lib/systemd/system"
            units.mkdir(parents=True)
            for name in ("systemd-homed.service", "systemd-homed-firstboot.service"):
                (units / name).write_text("synthetic vendor unit\n")
            subprocess.run(["/bin/bash", str(ROOT / "mkosi.postinst")],
                env={"PATH": "/usr/bin:/bin", "BUILDROOT": temp},
                capture_output=True, check=True, timeout=10)
            for name in ("systemd-homed.service", "systemd-homed-firstboot.service"):
                self.assertEqual(os.readlink(units / name), "/dev/null")
            self.assertFalse((root / "etc/passwd").exists())
            self.assertFalse((root / "home").exists())

    def test_factory_ssh_policy_survives_inherited_finalize(self):
        with tempfile.TemporaryDirectory(prefix="personal-os-factory-") as temp:
            root = Path(temp)
            factory = root / "usr/share/factory/etc/ssh/sshd_config.d"
            factory.mkdir(parents=True)
            policy = ROOT / "mkosi.profiles/mini-server/mkosi.extra/usr/share/factory/etc/ssh/sshd_config.d/00-mini-server.conf"
            shutil.copyfile(policy, factory / policy.name)
            source = root / "etc/ssh/sshd_config.d"
            source.mkdir(parents=True)
            (root / "etc/ssh/sshd_config").write_text("Include /etc/ssh/sshd_config.d/*.conf\n")
            (source / "50-vendor.conf").write_text("# synthetic vendor default\n")
            # This fixture covers factory merge/hook wiring, not privileged
            # SELinux staging. The real helper's metadata/failure cases live in
            # test_root_bootstrap; never add a production skip-labels switch.
            srcdir = root / "fixture-source"
            (srcdir / "scripts").mkdir(parents=True)
            (srcdir / "scripts/stage-root-bootstrap.py").write_text(
                "import json, os, pathlib, sys\n"
                "assert sys.argv[1:] == ['--distribution=fedora', '--buildroot', os.environ['BUILDROOT']]\n"
                "(pathlib.Path(os.environ['BUILDROOT']) / 'hook-invocation.json')"
                ".write_text(json.dumps(sys.argv[1:]))\n"
            )
            subprocess.run(["/bin/bash", str(ROOT / "mkosi.finalize")],
                env={"PATH": "/usr/bin:/bin", "BUILDROOT": temp, "SRCDIR": str(srcdir), "DISTRIBUTION": "fedora"},
                capture_output=True, check=True, timeout=10)
            self.assertEqual(json.loads((root / "hook-invocation.json").read_text()),
                             ["--distribution=fedora", "--buildroot", temp])
            self.assertEqual((factory / policy.name).read_bytes(), policy.read_bytes())
            self.assertTrue((factory / "50-vendor.conf").exists())

    @unittest.skipUnless(shutil.which("systemd-analyze"), "systemd-analyze is required")
    def test_enrollment_unit_verifies_with_local_executable_path(self):
        original = ROOT / "mkosi.profiles/mini-server/mkosi.extra/usr/lib/systemd/system/personal-os-account.service"
        with tempfile.TemporaryDirectory(prefix="personal-os-unit-") as temp:
            unit = Path(temp) / original.name
            unit.write_text(original.read_text().replace("/usr/libexec/personal-os-account", str(HELPER)))
            # Syntax/dependency inspection only, never a service start or target
            # image validation. The executable path is adapted for this checkout.
            subprocess.run(["systemd-analyze", "verify", "--man=no", str(unit)],
                           capture_output=True, check=True, timeout=10)

    def test_fork_authselect_always_uses_conventional_accounts(self):
        # Execute only the isolated authselect block with a stub. Never run the
        # rest of the chroot script, which moves the target's PAM files.
        block = (ROOT / "mkosi.postinst.chroot").read_text().split("# Arch's PAM", 1)[0]
        with tempfile.TemporaryDirectory(prefix="personal-os-authselect-") as temp:
            stub = Path(temp) / "authselect"
            calls = Path(temp) / "calls"
            stub.write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> "$CALLS"\n')
            stub.chmod(0o755)
            for profile in ("mini-server", "gnome", ""):
                expected = ["select local"]
                calls.write_text("")
                subprocess.run(["/bin/bash", "-c", block],
                    env={"PATH": temp, "PROFILES": profile, "CALLS": str(calls)},
                    capture_output=True, check=True, timeout=10)
                self.assertEqual(calls.read_text().splitlines(), expected)

    def test_pam_layout_keeps_arch_native_directory_and_fedora_vendor_fallback(self):
        script = (ROOT / "mkosi.postinst.chroot").read_text()
        block = "# Arch's PAM" + script.split("# Arch's PAM", 1)[1].split("# Preserve the distro", 1)[0]
        for distro in ("arch", "fedora"):
            with self.subTest(distro=distro), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                native, vendor = root / "etc/pam.d", root / "usr/lib/pam.d"
                native.mkdir(parents=True)
                vendor.mkdir(parents=True)
                policy = "auth required pam_shells.so\nauth required pam_unix.so\n"
                (native / "login").write_text(policy)
                adapted = block.replace("/etc/pam.d", str(native)).replace(
                    "/usr/lib/pam.d", str(vendor))
                subprocess.run(["bash", "-eu", "-c", adapted], check=True,
                               capture_output=True, timeout=10,
                               env={"PATH": "/usr/bin:/bin", "DISTRIBUTION": distro})
                if distro == "arch":
                    self.assertEqual((native / "login").read_text(), policy)
                    self.assertFalse((vendor / "login").exists())
                else:
                    self.assertFalse(native.exists())
                    self.assertEqual((vendor / "login").read_text(),
                                     "auth required pam_unix.so\n")

    def test_arch_rolling_branding_does_not_need_fedora_version_fields(self):
        block = (ROOT / "mkosi.postinst.chroot").read_text().split("\n(\n", 1)[1]
        with tempfile.TemporaryDirectory(prefix="personal-os-arch-branding-") as temp:
            root = Path(temp)
            release = root / "os-release"
            issue = root / "issue"
            release.write_text('NAME="Arch Linux"\nID=arch\n')
            block = "(\n" + block.replace("/usr/lib/os-release", str(release)).replace(
                "/usr/lib/issue", str(issue))
            subprocess.run(["/bin/bash", "-eu", "-c", block],
                           capture_output=True, check=True, timeout=10)
            values = dict(line.split("=", 1) for line in release.read_text().splitlines()
                          if line)
            self.assertEqual(values["ID"], '"arch"')
            self.assertEqual(values["ID_LIKE"], '"personal-os particleos-arch arch"')
            self.assertNotIn("VERSION_ID", values)
            self.assertIn("Personal OS / Arch Linux rolling", issue.read_text())

    def test_fork_branding_preserves_fedora_and_immutable_guard_ancestry(self):
        # Execute only branding against disposable files, never the chroot/PAM
        # operations against this desktop. mkosi adds IMAGE_ID afterward.
        block = (ROOT / "mkosi.postinst.chroot").read_text().split("\n(\n", 1)[1]
        with tempfile.TemporaryDirectory(prefix="personal-os-branding-") as temp:
            root = Path(temp)
            release = root / "os-release"
            issue = root / "issue"
            release.write_text('NAME="Fedora Linux"\nID=fedora\nVERSION="44"\nVERSION_ID=44\n')
            block = "(\n" + block.replace("/usr/lib/os-release", str(release)).replace(
                "/usr/lib/issue", str(issue))
            subprocess.run(["/bin/bash", "-eu", "-c", block],
                capture_output=True, check=True, timeout=10)
            values = dict(line.split("=", 1) for line in release.read_text().splitlines())
            self.assertEqual(values["ID"], '"fedora"')
            self.assertEqual(values["VERSION_ID"], '"44"')
            self.assertEqual(values["ID_LIKE"], '"personal-os particleos-fedora fedora"')
            self.assertIn("Personal OS", values["PRETTY_NAME"])
            self.assertNotIn("DEFAULT_HOSTNAME", values)
            self.assertIn("Personal OS / Fedora Linux 44", issue.read_text())
            self.assertNotIn("ParticleOS/", issue.read_text())

    def test_direct_execution_is_blocked_outside_target_profile(self):
        result = subprocess.run([str(HELPER)], capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 1)
        self.assertIn(b"enrollment failed", result.stderr)
