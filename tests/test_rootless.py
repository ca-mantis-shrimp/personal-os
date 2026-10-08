"""Synthetic enrollment of local subordinate IDs/linger; never host account changes."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from test_account import account, FakeBackend, key, password


@unittest.skipUnless(1000 <= os.getuid() <= 60000, "uses unprivileged test ownership")
class RootlessEnrollmentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="personal-os-rootless-")
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
        self.password = password()
        self.backend = FakeBackend(self.root)

    def provision(self, first=True):
        return account.provision(self.root, json.dumps(self.config).encode() if first else None,
                                 self.password if first else None, self.backend, os.getuid(), os.getgid())

    def ledger(self):
        return json.loads((self.root / "var/lib/personal-os/rootless.json").read_bytes())

    def test_fresh_account_has_stable_ranges_and_linger_only_once(self):
        self.provision()
        for kind in ("subuid", "subgid"):
            path = self.root / "etc" / kind
            self.assertEqual(path.read_text(), "synthetic:100000:65536\n")
            self.assertEqual(path.stat().st_mode & 0o777, 0o644)
        self.assertEqual(self.ledger()["phase"], "complete")
        self.assertEqual(self.ledger()["subuid"], [100000, 65536])
        self.assertTrue(self.ledger()["linger_on_enrollment"])
        base = json.loads((self.root / "var/lib/personal-os/account.json").read_bytes())
        self.assertEqual(set(base), {"version", "phase", "config"})
        self.assertEqual(base["version"], 1)  # Preserve the earlier account journal schema.
        command = next(call for call in self.backend.calls if call[0] == "useradd")
        self.assertIn("SUB_UID_COUNT=0", command)
        self.assertIn("SUB_GID_COUNT=0", command)
        marker = self.root / "var/lib/systemd/linger/synthetic"
        self.assertTrue(marker.exists())
        marker.unlink()  # Operator intentionally turns lingering off later.
        self.backend.calls.clear()
        self.provision(first=False)
        self.assertEqual(self.backend.calls, [])
        self.assertFalse(marker.exists())

    def test_arch_rootless_mapping_and_linger_remain_stable_without_mac_tools(self):
        (self.root / "usr/lib/os-release").write_text("ID=arch\n")
        self.backend.fail_on = "restorecon"
        self.provision()
        self.assertEqual(self.ledger()["phase"], "complete")
        self.assertEqual(self.ledger()["subuid"], [100000, 65536])
        self.assertEqual(self.ledger()["subgid"], [100000, 65536])
        self.assertNotIn("restorecon", [call[0] for call in self.backend.calls])
        self.backend.calls.clear()
        self.provision(first=False)
        self.assertEqual(self.backend.calls, [])

    def test_other_users_and_comments_preserved_and_joint_block_skips_both_tables(self):
        original = {"subuid": b"# retain\nother:100000:65536", "subgid": b"else:165536:65536\n"}
        for kind, data in original.items():
            (self.root / "etc" / kind).write_bytes(data)
        self.provision()
        for kind, data in original.items():
            self.assertTrue((self.root / "etc" / kind).read_bytes().startswith(data))
            self.assertEqual(self.ledger()[kind], [231072, 65536])

    def test_retry_after_first_table_write_is_not_a_new_allocation(self):
        write = account.Files.write
        def fail(files, path, data, **kwargs):
            if path == "etc/subgid":
                raise OSError("Synthetic power-loss window")
            return write(files, path, data, **kwargs)
        with patch.object(account.Files, "write", fail):
            with self.assertRaises(OSError):
                self.provision()
        self.assertEqual(self.ledger()["phase"], "pending")
        self.assertEqual(json.loads((self.root / "var/lib/personal-os/account.json").read_bytes())["phase"], "pending")
        before = (self.root / "etc/subuid").read_bytes()
        self.provision()
        self.assertEqual((self.root / "etc/subuid").read_bytes(), before)
        self.assertEqual(self.ledger()["subgid"], [100000, 65536])
        self.assertFalse((self.root / "etc/subuid.lock").exists())
        self.assertFalse((self.root / "etc/subgid.lock").exists())

    def test_linger_failure_blocks_enrollment_completion_and_retries(self):
        self.backend.fail_on = "loginctl"
        with self.assertRaises(account.ProvisionError):
            self.provision()
        self.assertEqual(self.ledger()["phase"], "pending")
        self.assertEqual(json.loads((self.root / "var/lib/personal-os/account.json").read_bytes())["phase"], "pending")
        self.provision()
        self.assertEqual(self.ledger()["phase"], "complete")
        self.assertEqual(sum(c[0] == "useradd" for c in self.backend.calls), 1)

    def test_completed_mapping_loss_change_or_overlap_is_not_repaired(self):
        self.provision()
        path = self.root / "etc/subuid"
        original = path.read_bytes()
        for data in (b"", b"synthetic:200000:65536\n", original + b"other:110000:65536\n",
                     original + f"{os.getuid()}:100000:65536\n".encode()):
            path.write_bytes(data)
            self.backend.calls.clear()
            with self.subTest(data_kind=len(data)), self.assertRaises(account.ProvisionError):
                self.provision(first=False)
            self.assertEqual(path.read_bytes(), data)
            self.assertEqual(self.backend.calls, [])
        path.write_bytes(original)

    def test_existing_identity_ids_are_not_allocated_as_subordinates(self):
        original = self.backend.ids
        self.backend.ids = lambda kind: original(kind) + [150000]
        self.provision()
        self.assertEqual(self.ledger()["subuid"], [150001, 65536])

    def test_legacy_complete_account_adopts_valid_existing_ranges_without_remapping(self):
        self.provision()
        (self.root / "var/lib/personal-os/rootless.json").unlink()
        for kind, start in (("subuid", 900000), ("subgid", 1200000)):
            (self.root / "etc" / kind).write_text(f"{os.getuid()}:{start}:131072\n")
        self.backend.calls.clear()
        self.provision(first=False)
        self.assertEqual(self.ledger()["subuid"], [900000, 131072])
        self.assertEqual(self.ledger()["subgid"], [1200000, 131072])
        self.assertFalse(any(c[0] in ("useradd", "usermod", "loginctl") for c in self.backend.calls))
        self.assertEqual((self.root / "etc/subuid").read_text(), f"{os.getuid()}:900000:131072\n")

    def test_stale_untracked_owner_or_nonlocal_delegation_blocks_before_account_commands(self):
        for path, data in (("subuid", b"synthetic:100000:65536\n"),
                           ("subgid", f"{os.getuid()}:100000:65536\n".encode()),
                           ("nsswitch.conf", b"subid: sss\n"),
                           ("subuid", b"broken:not-a-range\n")):
            file = self.root / "etc" / path
            file.write_bytes(data)
            with self.subTest(path=path), self.assertRaises(account.ProvisionError):
                self.provision()
            self.assertEqual(self.backend.calls, [])
            file.unlink()

    def test_protected_tables_and_ledger_reject_symlinks_or_writable_modes(self):
        outside = self.root / "outside"
        outside.write_bytes(b"other:100000:65536\n")
        path = self.root / "etc/subuid"
        path.symlink_to(outside)
        with self.assertRaises(OSError):
            self.provision()
        self.assertEqual(outside.read_bytes(), b"other:100000:65536\n")
        path.unlink()
        self.provision()
        ledger = self.root / "var/lib/personal-os/rootless.json"
        ledger.chmod(0o644)
        self.backend.calls.clear()
        with self.assertRaises(account.ProvisionError):
            self.provision(first=False)
        self.assertEqual(self.backend.calls, [])

    def test_unknown_rootless_schema_is_preserved(self):
        self.provision()
        path = self.root / "var/lib/personal-os/rootless.json"
        state = self.ledger()
        state["version"] = 2
        path.write_text(json.dumps(state))
        before = path.read_bytes()
        with self.assertRaises(account.ProvisionError):
            self.provision(first=False)
        self.assertEqual(path.read_bytes(), before)

    def test_live_database_lock_is_not_stolen(self):
        lock = self.root / "etc/subgid.lock"
        lock.write_text(str(os.getpid()) + "\n")
        with self.assertRaises(account.ProvisionError):
            self.provision()
        self.assertTrue(lock.exists())
        self.assertFalse((self.root / "etc/subuid.lock").exists())
        self.assertEqual(self.backend.calls, [])

    def test_dead_pid_lock_is_recovered(self):
        child = subprocess.Popen(["true"])
        child.wait()
        (self.root / "etc/subuid.lock").write_text(str(child.pid) + "\n")
        self.provision()
        self.assertFalse((self.root / "etc/subuid.lock").exists())

    def test_existing_complete_ranges_do_not_require_another_free_block(self):
        self.provision()
        for kind in ("subuid", "subgid"):
            path = self.root / "etc" / kind
            with path.open("a") as stream:
                stream.write(f"other:165536:{account.SUBID_MAX - 165536 + 1}\n")
        self.backend.calls.clear()
        self.provision(first=False)
        self.assertEqual(self.backend.calls, [])

    def test_fedora_authselect_factory_chain_and_read_only_hardlinks(self):
        factory = self.root / "usr/share/factory/etc"
        authselect = factory / "authselect"
        authselect.mkdir(parents=True)
        (factory / "nsswitch.conf").symlink_to("authselect/nsswitch.conf")
        source = authselect / "nsswitch.conf"
        source.write_text("passwd: files\nsubid: files\n")
        os.link(source, authselect / "deduplicated")
        (self.root / "etc/nsswitch.conf").symlink_to("/usr/share/factory/etc/nsswitch.conf")
        self.provision()
        self.assertEqual(self.ledger()["phase"], "complete")

    def test_nonstandard_nss_link_is_not_followed(self):
        outside = self.root / "outside"
        outside.write_text("subid: files\n")
        (self.root / "etc/nsswitch.conf").symlink_to(outside)
        with self.assertRaises(account.ProvisionError):
            self.provision()
        self.assertEqual(self.backend.calls, [])

    def test_known_factory_nss_link_uses_local_files(self):
        factory = self.root / "usr/share/factory/etc"
        factory.mkdir(parents=True)
        (factory / "nsswitch.conf").write_text("passwd: files\nsubid: files\n")
        (self.root / "etc/nsswitch.conf").symlink_to("/usr/share/factory/etc/nsswitch.conf")
        self.provision()
        self.assertEqual(self.ledger()["phase"], "complete")
