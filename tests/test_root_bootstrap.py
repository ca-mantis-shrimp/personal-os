"""Synthetic metadata-only staging tests; mock privileged SELinux/ownership calls."""
import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("root_bootstrap", ROOT / "scripts/stage-root-bootstrap.py")
if spec is None or spec.loader is None:
    raise RuntimeError("Unable to load the bootstrap staging module")
bootstrap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bootstrap)


class RootBootstrapTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="personal-os-root-bootstrap-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / "buildroot"
        self.root.mkdir()
        for name in (*bootstrap.PUBLIC_DIRECTORIES, "etc/selinux", "usr/share/factory"):
            directory = self.root / name
            directory.mkdir(parents=True, exist_ok=True)
            directory.chmod(0o755)
        for name, target in bootstrap.USR_LINKS.items():
            (self.root / name).symlink_to(target)
        # Deliberately present data that must never enter the bootstrap template.
        for name in ("etc/passwd", "etc/machine-id", "etc/selinux/policy.35"):
            (self.root / name).write_text("synthetic not-to-copy data")
        self.labels = {self.root: b"system_u:object_r:root_t:s0\0",
                       self.root / "etc": b"system_u:object_r:etc_t:s0\0",
                       self.root / "etc/selinux": b"system_u:object_r:selinux_config_t:s0\0"}
        for name in bootstrap.USR_LINKS:
            self.labels[self.root / name] = b"system_u:object_r:lib_t:s0\0"
        self.set_calls = []
        self.addCleanup(patch.stopall)
        patch.object(bootstrap.os, "chown").start()
        patch.object(bootstrap.os, "getxattr", side_effect=self.get_context).start()
        patch.object(bootstrap.os, "setxattr", side_effect=self.set_context).start()

    def get_context(self, path, attribute, *, follow_symlinks):
        self.assertEqual(attribute, "security.selinux")
        self.assertFalse(follow_symlinks)
        return self.labels[Path(path)]

    def set_context(self, path, attribute, value, *, follow_symlinks):
        self.assertEqual(attribute, "security.selinux")
        self.assertFalse(follow_symlinks)
        self.labels[Path(path)] = value
        self.set_calls.append(Path(path))

    def test_copies_only_stock_labels_and_empty_metadata(self):
        template = bootstrap.stage(self.root)
        self.assertEqual({str(p.relative_to(template)) for p in template.rglob("*")},
                         {"etc", "etc/selinux", *bootstrap.USR_LINKS})
        self.assertEqual(os.readlink(template / "etc/selinux"), bootstrap.POLICY_LINK)
        for name, target in bootstrap.USR_LINKS.items():
            self.assertEqual(os.readlink(template / name), target)
            self.assertEqual(self.labels[template / name], self.labels[self.root / name])
        self.assertEqual(self.labels[template], self.labels[self.root])
        self.assertEqual(self.labels[template / "etc"], self.labels[self.root / "etc"])
        self.assertEqual(template.stat().st_mode & 0o777, 0o755)
        self.assertEqual((template / "etc").stat().st_mode & 0o777, 0o755)
        self.assertTrue(all(path.is_relative_to(template) for path in self.set_calls))

    def test_rejects_restricted_payload_modes_before_writes(self):
        (self.root / "usr").chmod(0o700)
        with self.assertRaisesRegex(ValueError, "readable/searchable"):
            bootstrap.stage(self.root)
        self.assertFalse((self.root / bootstrap.TEMPLATE).exists())
        self.assertFalse(self.set_calls)

    def test_rejects_missing_or_unlabeled_reference(self):
        self.labels[self.root] = b"system_u:object_r:unlabeled_t:s0"
        with self.assertRaisesRegex(ValueError, "reference label"):
            bootstrap.stage(self.root)
        self.assertFalse((self.root / bootstrap.TEMPLATE).exists())

    def test_label_failure_propagates_and_removes_partial_output(self):
        with (patch.object(bootstrap.os, "setxattr", side_effect=PermissionError("synthetic")),
              self.assertRaises(PermissionError)):
            bootstrap.stage(self.root)
        self.assertFalse((self.root / bootstrap.TEMPLATE).exists())

    def test_never_overwrites_an_existing_template(self):
        template = self.root / bootstrap.TEMPLATE
        template.mkdir()
        (template / "operator").write_text("preserve")
        with self.assertRaises(FileExistsError):
            bootstrap.stage(self.root)
        self.assertEqual((template / "operator").read_text(), "preserve")

    def arch_fixture(self):
        # Explicit Arch target identity; no policy path in a non-SELinux image.
        (self.root / "usr/lib/os-release").write_text('ID=arch\nNAME="Arch Linux"\n')
        (self.root / "etc/selinux/policy.35").unlink()
        (self.root / "etc/selinux").rmdir()
        (self.root / "usr/libexec").rmdir()
        for name, target in bootstrap.ARCH_USR_LINKS.items():
            (self.root / name).unlink()
            (self.root / name).symlink_to(target)

    def test_arch_stages_only_unix_metadata_without_mac_calls(self):
        self.arch_fixture()
        with (patch.object(bootstrap.os, "getxattr", side_effect=AssertionError("MAC read")),
              patch.object(bootstrap.os, "setxattr", side_effect=AssertionError("MAC write"))):
            template = bootstrap.stage(self.root, distribution="arch")
        self.assertEqual({str(p.relative_to(template)) for p in template.rglob("*")},
                         {"etc", *bootstrap.ARCH_USR_LINKS})
        self.assertEqual(template.stat().st_mode & 0o777, 0o755)
        self.assertEqual((template / "etc").stat().st_mode & 0o777, 0o755)
        self.assertFalse((template / "etc/selinux").exists())
        self.assertFalse(self.set_calls)
        for name, target in bootstrap.ARCH_USR_LINKS.items():
            self.assertEqual(os.readlink(template / name), target)
        self.assertFalse((self.root / "usr/libexec").exists())

    def test_arch_cannot_bypass_fedora_target_label_checks(self):
        self.arch_fixture()
        (self.root / "usr/lib/os-release").write_text("ID=fedora\n")
        with self.assertRaisesRegex(ValueError, "actual Arch target"):
            bootstrap.stage(self.root, distribution="arch")
        self.assertFalse((self.root / bootstrap.TEMPLATE).exists())

    def test_arch_rejects_fedora_usr_merge_layout(self):
        self.arch_fixture()
        (self.root / "sbin").unlink()
        (self.root / "sbin").symlink_to("usr/sbin")
        with self.assertRaisesRegex(ValueError, "Unexpected image usr-merge link: sbin"):
            bootstrap.stage(self.root, distribution="arch")
        self.assertFalse((self.root / bootstrap.TEMPLATE).exists())

    def test_arch_rejects_policy_payload(self):
        self.arch_fixture()
        (self.root / "etc/selinux").mkdir()
        with self.assertRaisesRegex(ValueError, "Unexpected SELinux payload"):
            bootstrap.stage(self.root, distribution="arch")
        self.assertFalse((self.root / bootstrap.TEMPLATE).exists())

    def test_arch_rejects_restricted_modes_too(self):
        self.arch_fixture()
        (self.root / "usr/lib").chmod(0o700)
        with self.assertRaisesRegex(ValueError, "readable/searchable"):
            bootstrap.stage(self.root, distribution="arch")
        self.assertFalse((self.root / bootstrap.TEMPLATE).exists())

    def test_arch_rejects_external_os_release(self):
        self.arch_fixture()
        (self.root / "usr/lib/os-release").unlink()
        (self.root / "usr/lib/os-release").symlink_to("/usr/lib/os-release")
        with self.assertRaisesRegex(ValueError, "in-image os-release"):
            bootstrap.stage(self.root, distribution="arch")
        self.assertFalse((self.root / bootstrap.TEMPLATE).exists())

    def test_arch_failure_removes_partial_template(self):
        self.arch_fixture()
        with (patch.object(bootstrap.os, "chown", side_effect=PermissionError("synthetic")),
              self.assertRaises(PermissionError)):
            bootstrap.stage(self.root, distribution="arch")
        self.assertFalse((self.root / bootstrap.TEMPLATE).exists())

    def test_rejects_running_host_root(self):
        with self.assertRaisesRegex(ValueError, "running host"):
            bootstrap.stage(Path("/"))


if __name__ == "__main__":
    unittest.main()
