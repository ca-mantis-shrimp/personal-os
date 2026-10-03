#!/usr/bin/env python3
"""Offline configuration smoke tests; these do not build or boot an image."""

import json
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("mkosi"), "mkosi is required")
class ServerConfigTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        result = subprocess.run(
            ["mkosi", "--json", "summary"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
            timeout=30,
        )
        cls.images = json.loads(result.stdout)["Images"]
        cls.main = next(image for image in cls.images if image["Image"] == "main")

    def test_target_and_initrd_use_stable_fedora(self):
        for image in self.images:
            with self.subTest(image=image["Image"]):
                self.assertEqual(image["Distribution"], "fedora")
                self.assertEqual(image["Release"], "44")
        self.assertEqual(self.main["Profiles"], ["mini-server"])
        self.assertIsNone(self.main["Hostname"])
        self.assertEqual(self.main["Credentials"], [])

    def test_host_arch_fragments_do_not_leak_into_target(self):
        packages = set(self.main["Packages"])
        self.assertTrue(packages.isdisjoint({"pacman", "archlinux-keyring", "linux"}))
        scripts = self.main["PostInstallationScripts"]
        self.assertFalse(any("mkosi.conf.d/arch/" in script for script in scripts))

    def test_account_enrollment_is_target_only_profile_content(self):
        overlay = ROOT / "mkosi.profiles/mini-server/mkosi.extra"
        self.assertIn(str(ROOT / "mkosi.profiles/mini-server/mkosi.postinst"),
                      self.main["PostInstallationScripts"])
        self.assertIn(str(overlay), {tree["Source"] for tree in self.main["ExtraTrees"]})
        self.assertIn("shadow-utils", self.main["Packages"])
        for tree in self.main["ExtraTrees"]:
            for path in Path(tree["Source"]).rglob("*"):
                self.assertNotIn("__pycache__", path.parts)
                self.assertFalse(any(part.startswith("credstore") for part in path.parts))
        script = (ROOT / "mkosi.profiles/mini-server/mkosi.postinst").read_text()
        self.assertIn("systemd-homed-firstboot.service", script)
        self.assertNotIn("useradd", script)
        policy = (overlay / "usr/share/factory/etc/ssh/sshd_config.d/00-mini-server.conf").read_text()
        self.assertIn("PasswordAuthentication no", policy)
        self.assertIn("PermitRootLogin no", policy)

    def test_workloads_have_fail_closed_startup_guards(self):
        overlay = ROOT / "mkosi.profiles/mini-server/mkosi.extra/usr/lib/systemd"
        for unit in ("user/neovim-server.service", "user/otelcol.service",
                     "user/vdirsyncer.service", "user/vdirsyncer.timer", "user/syncthing.service",
                     "system/radicale.service", "system/syncthing@.service"):
            dropin = overlay / (unit + ".d/10-configuration-gate.conf")
            self.assertIn("ConditionPathExists=/run/personal-os/chezmoi-ready", dropin.read_text())
        helper = ROOT / "mkosi.profiles/mini-server/mkosi.extra/usr/libexec/personal-os-account"
        self.assertNotIn("chezmoi-ready", helper.read_text())

    def test_staging_is_a_profile_finalize_hook(self):
        scripts = self.main["FinalizeScripts"]
        self.assertIn(str(ROOT / "mkosi.finalize"), scripts)
        self.assertIn(str(ROOT / "mkosi.profiles/mini-server/mkosi.finalize"), scripts)

    def test_server_and_selinux_prerequisites_present(self):
        expected = {
            "chezmoi", "openssh-server", "sudo", "restic", "mdadm",
            "smartmontools", "syncthing", "radicale3", "radicale3-selinux",
            "selinux-policy-targeted", "policycoreutils",
        }
        self.assertTrue(expected.issubset(set(self.main["Packages"])))


if __name__ == "__main__":
    unittest.main()
