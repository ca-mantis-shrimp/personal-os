"""Offline role composition; no VM, services, package install or chezmoi apply."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def summary(*arguments, cwd=ROOT):
    result = subprocess.run(
        ["bash", str(cwd / "scripts/mkosi-arch"), *arguments, "-f", "--json", "summary"],
        cwd=cwd, text=True, capture_output=True, check=True, timeout=30)
    return json.loads(result.stdout)


def main(configuration):
    return next(image for image in configuration["Images"] if image["Image"] == "main")


@unittest.skipUnless(shutil.which("mkosi"), "mkosi is required")
class DevProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.configuration = summary("dev-pod")
        cls.dev = main(cls.configuration)

    def test_dev_has_no_services_account_enrollment_or_personal_configuration(self):
        self.assertEqual(self.dev["Profiles"], ["dev-pod"])
        trees = [Path(tree["Source"]) for tree in self.dev["ExtraTrees"]]
        self.assertNotIn(ROOT / "mkosi.profiles/mini-server/mkosi.extra", trees)
        for tree in trees:
            self.assertFalse((tree / "usr/libexec/personal-os-account").exists())
            self.assertFalse((tree / "usr/lib/personal-os/account-provisioning").exists())
            self.assertFalse(list(tree.rglob("10-account-enrollment.conf")))
            self.assertFalse(list(tree.rglob("10-configuration-gate.conf")))
        self.assertTrue(set(self.dev["Packages"]).isdisjoint({
            "chezmoi", "sudo", "syncthing", "radicale", "vdirsyncer", "restic",
            "nodejs", "npm", "fish", "neovim", "starship"}))
        self.assertTrue({"openssh", "git", "python", "podman", "tmux"}.issubset(self.dev["Packages"]))
        self.assertEqual(self.dev["FinalizeScripts"], [str(ROOT / "mkosi.finalize")])
        self.assertEqual(self.dev["BuildScripts"], [])
        self.assertEqual(self.dev["BuildPackages"], [])
        self.assertEqual(self.dev["Credentials"], [])
        self.assertIsNone(self.dev["RootPassword"])
        self.assertIsNone(self.dev["Hostname"])

    def test_dev_keeps_shared_signing_storage_and_bounded_vm_policy(self):
        for image in [*self.configuration["Images"], self.configuration["Tools"]]:
            self.assertEqual(image["Distribution"], "arch")
            self.assertEqual(image["Snapshot"], "2026/10/04")
        self.assertTrue(self.dev["SecureBoot"])
        self.assertFalse(self.dev["SecureBootAutoEnroll"])
        self.assertEqual(self.dev["SignExpectedPcr"], "enabled")
        self.assertEqual(self.dev["SELinuxRelabel"], "disabled")
        self.assertEqual(self.dev["ImageId"], "PersonalOS")
        self.assertTrue(any("root=encrypted" in arg and "usr=signed" in arg
                            for arg in self.dev["KernelCommandLine"]))
        self.assertTrue(self.dev["Ephemeral"])
        self.assertEqual(self.dev["CacheDirectory"], str(ROOT / "mkosi.cache/dev-pod"))
        self.assertEqual(self.dev["OutputDirectory"], str(ROOT / "mkosi.output/dev-pod"))

    def test_dev_boots_headless_without_interactive_recovery_enrollment(self):
        # systemd 262's initrd prompts for recovery enrollment on first boot and
        # waits forever on a headless pod; services keeps the stock behavior.
        self.assertIn("rd.systemd.mask=systemd-cryptenroll-firstboot.service",
                      self.dev["KernelCommandLine"])
        self.assertIn("systemd.firstboot=no", self.dev["KernelCommandLine"])

    def test_chezmoi_and_personal_snapshot_are_separate_opt_ins(self):
        tool = main(summary("dev-pod", "--profile=chezmoi"))
        personal = main(summary("dev-pod", "--profile=personal-dotfiles"))
        self.assertEqual(set(tool["Packages"]) - set(self.dev["Packages"]), {"chezmoi"})
        self.assertEqual(tool["FinalizeScripts"], self.dev["FinalizeScripts"])
        self.assertEqual(set(personal["Packages"]) - set(self.dev["Packages"]), {"chezmoi"})
        self.assertEqual(personal["FinalizeScripts"], [*self.dev["FinalizeScripts"],
            str(ROOT / "mkosi.profiles/personal-dotfiles/mkosi.finalize")])
        # The distro foundation is parsed before addons, regardless of role order.
        reversed_order = main(summary("--profile=", "--profile=chezmoi", "--profile=dev-pod"))
        self.assertIn("chezmoi", reversed_order["Packages"])
        services = main(summary("--profile=personal-dotfiles"))
        self.assertIn("chezmoi", services["Packages"])
        self.assertIn("personal-dotfiles", services["Profiles"])

    def test_roles_cannot_be_combined(self):
        for extra in ("mini-server-arch", "mini-server"):
            with self.subTest(extra=extra):
                result = subprocess.run(
                    ["bash", str(ROOT / "scripts/mkosi-arch"), "dev-pod",
                     "--profile=" + extra, "-f", "--json", "summary"],
                    cwd=ROOT, text=True, capture_output=True, timeout=30)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("[assert]", result.stderr.lower())

    def test_roles_parse_without_git_or_dotfiles_checkout(self):
        with tempfile.TemporaryDirectory(prefix="personal-os-no-dotfiles-") as temp:
            checkout = Path(temp)
            for name in ("mkosi.conf", "mkosi.conf.d", "mkosi.profiles", "mkosi.extra",
                         "mkosi.repart", "mkosi.sysupdate", "mkosi.postinst",
                         "mkosi.postinst.chroot", "mkosi.finalize", "scripts"):
                source = ROOT / name
                if source.is_dir():
                    shutil.copytree(source, checkout / name, symlinks=True,
                                    ignore=shutil.ignore_patterns("__pycache__"))
                else:
                    shutil.copy2(source, checkout / name)
            for role in ("dev-pod", "mini-server-arch"):
                with self.subTest(role=role):
                    image = main(summary(role, cwd=checkout))
                    self.assertEqual(image["Profiles"], [role])
                    self.assertNotIn("chezmoi", image["Packages"])
                    self.assertEqual(image["FinalizeScripts"], [str(checkout / "mkosi.finalize")])

    @unittest.skipUnless(shutil.which("sshd") and shutil.which("ssh-keygen"),
                         "sshd and ssh-keygen are required")
    def test_root_ssh_policy_uses_only_public_keys(self):
        policy = ROOT / "mkosi.profiles/dev-pod/mkosi.extra/usr/share/factory/etc/ssh/sshd_config.d/00-dev-pod.conf"
        with tempfile.TemporaryDirectory(prefix="personal-os-sshd-policy-") as temp:
            hostkey = Path(temp) / "hostkey"
            subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(hostkey)],
                           capture_output=True, check=True, timeout=10)
            result = subprocess.run([shutil.which("sshd"), "-T", "-f", str(policy), "-h", str(hostkey)],
                                    text=True, capture_output=True, check=True, timeout=10)
        settings = {key.lower(): value for key, value in
                    (line.split(" ", 1) for line in result.stdout.splitlines())}
        self.assertIn(settings["permitrootlogin"], ("prohibit-password", "without-password"))
        self.assertEqual(settings["authenticationmethods"], "publickey")
        self.assertEqual(settings["passwordauthentication"], "no")
        self.assertEqual(settings["kbdinteractiveauthentication"], "no")


if __name__ == "__main__":
    unittest.main()
