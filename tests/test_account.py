"""Target account logic against disposable files and a fake account backend.

No real useradd/groupadd/chpasswd/hostnamectl/restorecon operations are executed.
Synthetic public keys and password-like test inputs are generated at runtime.
"""
import base64
import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import secrets
import shutil
import struct
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "mkosi.profiles/mini-server/mkosi.extra/usr/libexec/personal-os-account"
loader = importlib.machinery.SourceFileLoader("account", str(HELPER))
spec = importlib.util.spec_from_loader(loader.name, loader)
account = importlib.util.module_from_spec(spec)
# Compile from source without caching bytecode inside the mkosi ExtraTrees.
exec(compile(HELPER.read_text(), str(HELPER), "exec"), account.__dict__)


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
        self.fail_on = None

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

    def run(self, args, input=None):
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
        elif args[0] == "hostnamectl":
            self.host = name
        elif args[0] == "chpasswd":
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
        self.config = {"version": 1, "username": "synthetic", "uid": os.getuid(),
            "gid": os.getgid(), "hostname": "synthetic-server", "shell": "/usr/bin/bash",
            "ssh_public_keys": [key()], "passwordless_sudo": True}
        self.password = password()
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
        self.assertFalse(self.password in state.read_bytes())
        self.assertEqual(personal.read_text(), "mutable data\n")
        keys.write_text(key() + "\n")
        (self.root / "etc/shadow").write_text("synthetic:operator-changed:1:0:99999:7:::\n")
        self.backend.calls.clear()
        self.provision(config=False, password=False)
        self.assertEqual(self.backend.calls, [])
        self.assertIn("operator-changed", (self.root / "etc/shadow").read_text())
        self.assertEqual(personal.read_text(), "mutable data\n")

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
        with patch.object(account.Files, "write", fail_complete):
            with self.assertRaises(OSError):
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
            subprocess.run(["/bin/bash", str(ROOT / "mkosi.profiles/mini-server/mkosi.postinst")],
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
            subprocess.run(["/bin/bash", str(ROOT / "mkosi.finalize")],
                env={"PATH": "/usr/bin:/bin", "BUILDROOT": temp},
                capture_output=True, check=True, timeout=10)
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

    def test_authselect_homed_feature_is_skipped_only_for_server_profile(self):
        # Execute only the isolated authselect block with a stub. Never run the
        # rest of the chroot script, which moves the target's PAM files.
        block = (ROOT / "mkosi.postinst.chroot").read_text().split("if [[ -d /etc/pam.d ]]", 1)[0]
        with tempfile.TemporaryDirectory(prefix="personal-os-authselect-") as temp:
            stub = Path(temp) / "authselect"
            calls = Path(temp) / "calls"
            stub.write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> "$CALLS"\n')
            stub.chmod(0o755)
            for profile, expected in [("mini-server", ["select local"]),
                ("gnome", ["select local", "enable-feature with-systemd-homed"])]:
                calls.write_text("")
                subprocess.run(["/bin/bash", "-c", block],
                    env={"PATH": temp, "PROFILES": profile, "CALLS": str(calls)},
                    capture_output=True, check=True, timeout=10)
                self.assertEqual(calls.read_text().splitlines(), expected)

    def test_direct_execution_is_blocked_outside_target_profile(self):
        result = subprocess.run([str(HELPER)], capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 1)
        self.assertIn(b"enrollment failed", result.stderr)
