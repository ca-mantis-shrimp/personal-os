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
        self.assertEqual(self.main["Hostname"], "mini-travel-server")

    def test_host_arch_fragments_do_not_leak_into_target(self):
        packages = set(self.main["Packages"])
        self.assertTrue(packages.isdisjoint({"pacman", "archlinux-keyring", "linux"}))
        scripts = self.main["PostInstallationScripts"]
        self.assertFalse(any("mkosi.conf.d/arch/" in script for script in scripts))

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
