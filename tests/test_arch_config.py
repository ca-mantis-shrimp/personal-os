"""Arch services summary guards; no package install, image build or target apply."""
import json
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("mkosi"), "mkosi is required")
class ArchConfigTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        result = subprocess.run(
            ["bash", str(ROOT / "scripts/mkosi-arch"), "-f", "--json", "summary"],
            cwd=ROOT, text=True, capture_output=True, check=True, timeout=30)
        summary = json.loads(result.stdout)
        cls.images = summary["Images"]
        cls.tools = summary["Tools"]
        cls.main = next(image for image in cls.images if image["Image"] == "main")

    def test_target_initrd_and_tools_are_arch_not_fedora(self):
        for image in [*self.images, self.tools]:
            self.assertEqual(image["Distribution"], "arch")
            self.assertEqual(image["Release"], "rolling")
            self.assertEqual(image["Snapshot"], "2026/10/04")
        self.assertEqual(self.main["Profiles"], ["mini-server-arch"])
        self.assertEqual(self.tools["Profiles"], ["misc", "runtime"])
        self.assertIn("man-db", self.tools["Packages"])
        self.assertNotIn("man-db", self.main["Packages"])
        self.assertEqual(self.main["Credentials"], [])
        self.assertIsNone(self.main["Hostname"])

    def test_baseline_uses_repo_binaries_not_fedora_or_cargo_payload(self):
        packages = self.main["Packages"]
        self.assertEqual(len(packages), len(set(packages)))
        self.assertTrue({"linux", "archlinux-keyring", "openssh", "shadow", "podman",
                         "crun", "netavark", "passt", "fuse-overlayfs",
                         "starship", "fish", "neovim", "git"}.issubset(packages))
        self.assertTrue(set(packages).isdisjoint({
            "base", "base-devel", "cargo", "rust", "gcc", "nodejs", "npm", "chezmoi",
            "selinux-policy-targeted", "policycoreutils", "container-selinux",
            "kernel-core", "openssh-server", "shadow-utils", "python3-bcrypt",
            "radicale3", "git-core", "gdisk", "fd-find", "udev"}))
        self.assertEqual(self.main["BuildPackages"], [])
        self.assertEqual(self.main["BuildScripts"], [])
        self.assertTrue(set(self.tools["Packages"]).isdisjoint({
            "pipewire", "qemu-ui-sdl", "qemu-ui-opengl"}))

    def test_arch_has_no_selinux_requirement_but_keeps_signing_encryption(self):
        self.assertEqual(self.main["SELinuxRelabel"], "disabled")
        cmdline = self.main["KernelCommandLine"]
        self.assertEqual(len(cmdline), len(set(cmdline)))
        self.assertTrue(set(cmdline).isdisjoint({"selinux=1", "enforcing=1",
                                               "selinux=0", "enforcing=0"}))
        self.assertTrue(self.main["SecureBoot"])
        self.assertFalse(self.main["SecureBootAutoEnroll"])
        self.assertEqual(self.main["SignExpectedPcr"], "enabled")
        self.assertEqual(self.main["ImageId"], "PersonalOS")
        self.assertTrue(any("usr=signed" in arg and "root=encrypted" in arg for arg in cmdline))
        self.assertTrue(any("usr=PersonalOS_*" in arg for arg in cmdline))

    def test_only_arch_finalize_runs_and_source_is_reused(self):
        self.assertEqual(self.main["FinalizeScripts"], [
            str(ROOT / "mkosi.finalize")])
        self.assertIn(str(ROOT / "mkosi.postinst.chroot"), self.main["PostInstallationScripts"])
        trees = {tree["Source"] for tree in self.main["ExtraTrees"]}
        self.assertIn(str(ROOT / "mkosi.profiles/mini-server/mkosi.extra"), trees)
        self.assertNotIn(str(ROOT / "mkosi.profiles/mini-server/mkosi.agent-extra"), trees)
        for tree in trees:
            self.assertNotIn("reference", Path(tree).parts)
            for name in ("starship", "pi", "claude", "shpool"):
                self.assertFalse((Path(tree) / "usr/bin" / name).exists())
        finalize = (ROOT / "mkosi.finalize").read_text()
        self.assertIn('--distribution="${DISTRIBUTION:?}"', finalize)
        self.assertNotIn("stage-dotfiles.py", finalize)
        self.assertNotIn("chezmoi apply", finalize)

    def test_arch_native_pam_factory_link_preserves_mutable_overrides(self):
        path = ROOT / "mkosi.conf.d/arch/mkosi.extra/usr/lib/tmpfiles.d/arch-pam.conf"
        rules = [line for line in path.read_text().splitlines() if line and not line.startswith("#")]
        self.assertEqual(rules, ["L /etc/pam.d - - - - /usr/share/factory/etc/pam.d"])

    def test_caches_and_outputs_are_separate(self):
        self.assertEqual(self.main["CacheDirectory"], str(ROOT / "mkosi.cache/arch"))
        self.assertEqual(self.main["OutputDirectory"], str(ROOT / "mkosi.output/arch"))
        self.assertEqual(self.main["Incremental"], "yes")
        self.assertTrue(self.main["RepositoryKeyCheck"])
        self.assertFalse(self.main["WithRecommends"])

    def test_enrollment_is_enabled_but_configuration_and_sessions_stay_closed(self):
        preset = (ROOT / "mkosi.profiles/mini-server-arch/mkosi.extra/usr/lib/systemd/"
                  "system-preset/00-arch-prototype.preset").read_text()
        self.assertIn("enable personal-os-account.service", preset)
        self.assertFalse((ROOT / "mkosi.profiles/mini-server/mkosi.extra/usr/lib/systemd/"
                          "system/personal-os-configuration.service").exists())
        self.assertEqual([line for line in preset.splitlines() if line.startswith("enable ")],
                         ["enable personal-os-account.service"])
        # Nothing creates an account on the builder or defaults to root access.
        self.assertEqual(self.main["Credentials"], [])


if __name__ == "__main__":
    unittest.main()
