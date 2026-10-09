"""Sandbox worker composition: a non-bootable base tree for agent sandboxes."""
import shutil
import subprocess
import unittest

from test_dev_config import ROOT, main, summary


@unittest.skipUnless(shutil.which("mkosi"), "mkosi is required")
class SandboxWorkerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.configuration = summary("sandbox-worker")
        cls.worker = main(cls.configuration)

    def test_is_a_directory_tree_without_a_boot_chain(self):
        self.assertEqual(self.worker["Format"], "directory")
        self.assertEqual(self.worker["Bootable"], "disabled")
        self.assertFalse(self.worker["SecureBoot"])
        self.assertEqual(self.worker["SignExpectedPcr"], "disabled")
        self.assertEqual(self.worker["KernelCommandLine"], [])
        # No initrd sub-image: nothing here boots.
        self.assertEqual([image["Image"] for image in self.configuration["Images"]], ["main"])

    def test_carries_agent_tools_not_os_policy(self):
        packages = set(self.worker["Packages"])
        self.assertTrue({"bash", "git", "nodejs", "npm", "python", "ripgrep", "shadow"}.issubset(packages))
        self.assertTrue(packages.isdisjoint({"linux", "systemd", "openssh", "podman", "sudo", "cryptsetup"}))
        self.assertEqual(self.worker["ExtraTrees"], [])
        self.assertEqual(self.worker["FinalizeScripts"], [])
        # One script, which records the snapshot as the extension level.
        self.assertEqual(self.worker["PostInstallationScripts"],
                         [str(ROOT / "mkosi.profiles/sandbox-worker/extension-level.chroot")])

    def test_keeps_package_metadata_for_layers(self):
        # Layers install packages against this tree's pacman database.
        self.assertEqual(self.worker["CleanPackageMetadata"], "disabled")

    def test_shares_the_os_snapshot_with_separate_outputs(self):
        self.assertEqual(self.worker["Snapshot"], "2026/10/04")
        self.assertEqual(self.worker["CacheDirectory"], str(ROOT / "mkosi.cache/sandbox-worker"))
        self.assertEqual(self.worker["OutputDirectory"], str(ROOT / "mkosi.output/sandbox-worker"))

    def test_cannot_be_combined_with_a_machine_role(self):
        for extra in ("dev-pod", "mini-server-arch", "mini-server"):
            with self.subTest(extra=extra):
                result = subprocess.run(
                    ["bash", str(ROOT / "scripts/mkosi-arch"), "sandbox-worker",
                     "--profile=" + extra, "-f", "--json", "summary"],
                    cwd=ROOT, text=True, capture_output=True, timeout=30)
                self.assertNotEqual(result.returncode, 0)
