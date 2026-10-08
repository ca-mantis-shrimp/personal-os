#!/usr/bin/env python3
"""Offline configuration smoke tests; these do not build or boot an image."""

import configparser
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("mkosi"), "mkosi is required")
class ServerConfigTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        result = subprocess.run(
            ["mkosi", "-f", "--json", "summary"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
            timeout=30,
        )
        summary = json.loads(result.stdout)
        cls.images = summary["Images"]
        cls.tools = summary["Tools"]
        cls.main = next(image for image in cls.images if image["Image"] == "main")

    def test_target_and_initrd_use_stable_fedora(self):
        for image in self.images:
            with self.subTest(image=image["Image"]):
                self.assertEqual(image["Distribution"], "fedora")
                self.assertEqual(image["Release"], "44")
        self.assertEqual(self.main["Profiles"], ["mini-server"])
        self.assertIsNone(self.main["Hostname"])
        self.assertEqual(self.main["Credentials"], [])

    def test_builder_is_fedora_without_graphical_vm_stack(self):
        self.assertEqual(self.tools["Distribution"], "fedora")
        self.assertEqual(self.tools["Release"], "44")
        self.assertEqual(self.tools["Profiles"], ["misc", "runtime"])
        self.assertTrue(set(self.tools["Packages"]).isdisjoint({
            "pipewire", "pipewire-audio", "qemu-ui-sdl", "qemu-ui-opengl",
        }))

    def test_only_server_recipe_is_active_and_reference_is_not_staged(self):
        self.assertEqual({p.name for p in (ROOT / "mkosi.profiles").iterdir()},
                         {"mini-server", "mini-server-arch", "dev-pod", "chezmoi", "personal-dotfiles"})
        self.assertEqual({p.name for p in (ROOT / "mkosi.conf.d").iterdir()}, {"fedora", "arch"})
        for path in ("mkosi.images", "mkosi.uki-profiles", "mkosi.credentials", ".obs"):
            self.assertFalse((ROOT / path).exists())
            self.assertTrue((ROOT / "reference/particleos" / path).exists())
        for image in self.images:
            self.assertFalse(image["UnifiedKernelImageProfiles"])
            for tree in image["ExtraTrees"]:
                self.assertNotIn("reference", Path(tree["Source"]).parts)
            for script in image["PostInstallationScripts"] + image["FinalizeScripts"]:
                self.assertNotIn("reference", Path(script).parts)

    def test_signed_audited_enforcing_boot_has_no_demo_or_reset_modes(self):
        self.assertTrue(self.main["SecureBoot"])
        self.assertFalse(self.main["SecureBootAutoEnroll"])
        self.assertEqual(self.main["SignExpectedPcr"], "enabled")
        self.assertEqual(self.main["SELinuxRelabel"], "enabled")
        self.assertFalse(self.main["WithRecommends"])
        cmdline = self.main["KernelCommandLine"]
        self.assertTrue({"root=dissect", "mount.usr=dissect", "audit=1",
                         "selinux=1", "enforcing=1"}.issubset(cmdline))
        self.assertTrue(any("usr=signed" in arg for arg in cmdline))
        for arg in cmdline:
            self.assertFalse(any(token in arg for token in (
                "audit=0", "selinux=0", "enforcing=0", "ipe.enforce=0",
                "set-credential", "autologin", "noauth", "factory_reset",
                "storage-target-mode", "image_policy=-",
            )))

    def test_fork_artifact_identity_stays_coupled_to_partition_filters(self):
        image_id = self.main["ImageId"]
        self.assertEqual(image_id, "PersonalOS")
        version = self.main["ImageVersion"]
        # %v is blank during unversioned inspection; actual releases must set it.
        self.assertEqual(self.main["Output"],
                         f"{image_id}_{version or ''}_{self.main['Architecture']}")
        filters = next(arg for arg in self.main["KernelCommandLine"]
                       if arg.startswith("systemd.image_filter="))
        for name in ("usr", "usr-verity", "usr-verity-sig"):
            self.assertIn(f"{name}={image_id}_*", filters)
        for name in ("root", "swap", "home"):
            self.assertIn(f"{name}={image_id}-*", filters)
        # Timestamp-versioned labels still fit GPT's 36-character label limit.
        self.assertLessEqual(len(f"{image_id}_20261003000000_verity_sig"), 36)
        for name in ("10-usr-verity-sig", "11-usr-verity", "12-usr"):
            build = (ROOT / "mkosi.repart" / (name + ".conf")).read_text()
            target = (ROOT / "mkosi.extra/usr/lib/repart.d" / (name + ".conf")).read_text()
            self.assertIn("Label=%M_%A", build)
            self.assertIn("Label=%M_%A", target)
            transfer = (ROOT / "mkosi.sysupdate" / (name + ".transfer")).read_text()
            self.assertIn("ProtectVersion=%A", transfer)
            self.assertIn("MatchPattern=%M_@v", transfer)
        uki = (ROOT / "mkosi.sysupdate/20-uki.transfer").read_text()
        self.assertIn("MatchPattern=%M_@v_%a.efi", uki)
        self.assertIn("InstancesMax=2", uki)
        self.assertIn("TriesLeft=3", uki)

    def test_headless_package_selection_retains_use_cases_not_upstream_extras(self):
        packages = set(self.main["Packages"])
        self.assertEqual(len(packages), len(self.main["Packages"]))
        self.assertTrue(packages.isdisjoint({
            "gdb", "fwupd", "exfatprogs", "kexec-tools", "opensc", "pcsc-lite",
            "pcsc-lite-ccid", "pkcs11-provider", "yubikey-manager", "perf", "bpftool",
            "fido2-tools", "dnf5", "wget2", "gdm", "sddm", "pipewire", "NetworkManager",
        }))
        self.assertTrue({"nodejs", "npm", "git-core", "neovim", "fish", "tmux",
                         "cryptsetup", "tpm2-tools", "btrfs-progs", "veritysetup"}.issubset(packages))
        for filename in ("30-swap.conf", "40-root.conf", "50-home.conf"):
            contents = (ROOT / "mkosi.extra/usr/lib/repart.d" / filename).read_text()
            self.assertIn("FactoryReset=no", contents)
            self.assertNotIn("FactoryReset=yes", contents)
        root = (ROOT / "mkosi.extra/usr/lib/repart.d/40-root.conf").read_text()
        self.assertIn("Encrypt=tpm2", root)
        self.assertIn("Format=btrfs", root)

    def test_presets_enable_management_not_desktop_or_workloads(self):
        preset = (ROOT / "mkosi.extra/usr/lib/systemd/system-preset/10-personal-os.preset").read_text()
        for unit in ("systemd-networkd.service", "systemd-resolved.service", "sshd.service"):
            self.assertIn(f"enable {unit}", preset)
        for unit in ("pcscd.*", "NetworkManager.service", "debug-shell.service",
                     "systemd-homed.service", "radicale.service", "syncthing@.service"):
            self.assertIn(f"disable {unit}", preset)
        for line in preset.splitlines():
            if line.startswith("enable "):
                self.assertNotIn(line.split()[1], {"pcscd.service", "NetworkManager.service",
                    "power-profiles-daemon.service", "systemd-homed-firstboot.service"})
        tmpfiles = (ROOT / "mkosi.extra/usr/lib/tmpfiles.d/etc.conf").read_text()
        for path in ("/etc/gdm", "/etc/cups", "/etc/PackageKit", "/etc/pacman.conf"):
            self.assertNotIn(path, tmpfiles)

    def test_core_rootless_podman_is_image_owned_not_an_enabled_api(self):
        self.assertTrue({"podman", "container-selinux", "shadow-utils", "shadow-utils-subid",
                         "crun", "netavark", "passt", "fuse-overlayfs"}.issubset(set(self.main["Packages"])))
        for kind in ("system", "user"):
            preset = (ROOT / f"mkosi.extra/usr/lib/systemd/{kind}-preset/10-personal-os.preset").read_text()
            for unit in ("podman.socket", "podman.service", "podman-auto-update.timer", "podman-restart.service"):
                self.assertIn(f"disable {unit}", preset)
                self.assertNotIn(f"enable {unit}", preset)
        factory = (ROOT / "mkosi.extra/usr/lib/tmpfiles.d/etc.conf").read_text()
        self.assertIn("C /etc/containers", factory)
        self.assertIn("L /etc/default/useradd", factory)
        default = (ROOT / "mkosi.profiles/mini-server/mkosi.extra/usr/share/factory/etc/default/useradd").read_text()
        self.assertIn("CREATE_MAIL_SPOOL=no", default)
        helper = (ROOT / "mkosi.profiles/mini-server/mkosi.extra/usr/libexec/personal-os-account").read_text()
        self.assertNotIn('"CREATE_MAIL_SPOOL=no"', helper)  # Not a valid useradd -K override.
        self.assertNotIn("L /etc/subuid", factory)
        self.assertNotIn("L /etc/subgid", factory)
        unit = (ROOT / "mkosi.profiles/mini-server/mkosi.extra/usr/lib/systemd/system/personal-os-account.service").read_text()
        self.assertIn("RuntimeDirectory=personal-os", unit)
        self.assertIn("NoNewPrivileges=yes", unit)  # Root enrollment needs no new setuid privilege.

    def test_host_arch_fragments_do_not_leak_into_target(self):
        packages = set(self.main["Packages"])
        self.assertTrue(packages.isdisjoint({"pacman", "archlinux-keyring", "linux"}))
        scripts = self.main["PostInstallationScripts"]
        self.assertFalse(any("mkosi.conf.d/arch/" in script for script in scripts))

    def test_account_enrollment_is_target_only_profile_content(self):
        overlay = ROOT / "mkosi.profiles/mini-server/mkosi.extra"
        self.assertIn(str(ROOT / "mkosi.postinst"),
                      self.main["PostInstallationScripts"])
        self.assertIn(str(overlay), {tree["Source"] for tree in self.main["ExtraTrees"]})
        self.assertIn("shadow-utils", self.main["Packages"])
        for tree in self.main["ExtraTrees"]:
            for path in Path(tree["Source"]).rglob("*"):
                self.assertNotIn("__pycache__", path.parts)
                self.assertFalse(any(part.startswith("credstore") for part in path.parts))
        script = (ROOT / "mkosi.postinst").read_text()
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
            self.assertIn("ConditionPathExists=/run/personal-os/configuration-ready", dropin.read_text())
        helper = ROOT / "mkosi.profiles/mini-server/mkosi.extra/usr/libexec/personal-os-account"
        self.assertNotIn("configuration-ready", helper.read_text())

    def test_dotfiles_are_not_a_default_build_dependency(self):
        self.assertEqual(self.main["FinalizeScripts"], [str(ROOT / "mkosi.finalize")])
        self.assertNotIn("chezmoi", self.main["Packages"])
        self.assertNotIn("stage-dotfiles.py", (ROOT / "mkosi.finalize").read_text())

    def test_selinux_policy_is_linked_during_new_root_creation(self):
        parser = configparser.ConfigParser(interpolation=None)
        parser.read(ROOT / "mkosi.extra/usr/lib/repart.d/40-root.conf")
        partition = parser["Partition"]
        self.assertEqual(partition["CopyFiles"], "/usr/share/factory/root:/")
        self.assertEqual(partition["MakeDirectories"], "/var/log/journal")
        self.assertNotIn("MakeSymlinks", partition)
        self.assertIn("stage-root-bootstrap.py", (ROOT / "mkosi.finalize").read_text())
        # Copy a metadata-only skeleton, never the packaged policy or mutable /etc.
        # The real encrypted, non-resettable Btrfs root recipe stays intact.
        self.assertEqual(partition["Type"], "root")
        self.assertEqual(partition["Format"], "btrfs")
        self.assertEqual(partition["Encrypt"], "tpm2")
        self.assertEqual(partition["FactoryReset"], "no")

    @unittest.skipUnless(all(shutil.which(tool) for tool in
                            ("systemd-repart", "mke2fs", "debugfs")),
                         "native offline repart/ext4 tools are required")
    def test_native_repart_symlink_is_first_creation_only(self):
        # A generic ext4 fixture tests CopyFiles metadata/links and no-reset,
        # not target encrypted Btrfs, TPM, SELinux enforcement or target boot.
        # Synthetic user xattrs test preservation without changing host MAC policy.
        # Explicit offline mode, random IDs and regular-file operands mean no
        # host block/TPM device is discovered, opened or formatted.
        parser = configparser.ConfigParser(interpolation=None)
        parser.read(ROOT / "mkosi.extra/usr/lib/repart.d/40-root.conf")
        partition = parser["Partition"]
        with tempfile.TemporaryDirectory(prefix="personal-os-repart-link-") as temporary:
            directory = Path(temporary)
            definitions = directory / "definitions"
            definitions.mkdir()
            definition = definitions / "00-fixture.conf"
            source = directory / "source"
            (source / "etc").mkdir(parents=True)
            (source / "etc/selinux").symlink_to("/usr/share/factory/etc/selinux")
            (source / "lib64").symlink_to("usr/lib64")
            os.setxattr(source, "user.bootstrap", b"synthetic-root")
            os.setxattr(source / "etc", "user.bootstrap", b"synthetic-etc")
            content = ("[Partition]\nType=linux-generic\nFormat=ext4\n"
                       "SizeMinBytes=32M\nLabel=link-fixture\nSplitName=fs\n"
                       f"MakeDirectories={partition['MakeDirectories']}\n"
                       f"CopyFiles={source}:/\n")
            definition.write_text(content)
            image = directory / "fixture.raw"
            command = ["systemd-repart", "--offline=yes", "--dry-run=no",
                       "--seed=random", f"--definitions={definitions}", str(image)]
            subprocess.run(command + ["--empty=create", "--size=64M", "--split=yes"],
                           capture_output=True, check=True, timeout=30)
            filesystem = directory / "fixture.fs.raw"
            inspected = subprocess.run(
                ["debugfs", "-R", "stat /etc/selinux", str(filesystem)],
                capture_output=True, text=True, check=True, timeout=10,
            )
            self.assertIn("Type: symlink", inspected.stdout)
            self.assertIn("/usr/share/factory/etc/selinux", inspected.stdout)
            for path, marker in (("/", "synthetic-root"), ("/etc", "synthetic-etc")):
                attrs = subprocess.run(
                    ["debugfs", "-R", "ea_list " + path, str(filesystem)],
                    capture_output=True, text=True, check=True, timeout=10,
                )
                self.assertIn(marker, attrs.stdout)
            before = hashlib.sha256(image.read_bytes()).digest()
            # Updated source metadata/links must not reinitialize an existing FS.
            (source / "etc/selinux").unlink()
            (source / "etc/selinux").symlink_to("/operator/override")
            os.setxattr(source / "etc", "user.bootstrap", b"changed")
            subprocess.run(command, capture_output=True, check=True, timeout=30)
            self.assertEqual(hashlib.sha256(image.read_bytes()).digest(), before)

    def test_server_and_selinux_prerequisites_present(self):
        expected = {
            "openssh-server", "sudo", "restic", "mdadm",
            "smartmontools", "syncthing", "radicale3", "radicale3-selinux",
            "selinux-policy-targeted", "policycoreutils",
        }
        self.assertTrue(expected.issubset(set(self.main["Packages"])))


if __name__ == "__main__":
    unittest.main()
