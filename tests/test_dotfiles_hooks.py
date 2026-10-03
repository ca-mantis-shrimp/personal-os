"""Render only isolated templates; never init/apply against a real home."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("chezmoi"), "chezmoi is required")
class HookTemplateTests(unittest.TestCase):
    def render(self, os_name="linux", distro="arch", id_like="", **env_overrides):
        with tempfile.TemporaryDirectory(prefix="personal-os-template-") as temp:
            home = Path(temp)
            config = home / "chezmoi.toml"
            config.write_text("")
            source = home / "source"
            source.mkdir()
            env = os.environ.copy()
            env.update(HOME=temp, XDG_CONFIG_HOME=str(home / "config"),
                       XDG_CACHE_HOME=str(home / "cache"),
                       XDG_DATA_HOME=str(home / "data"),
                       CHEZMOI_CONTAINER="", CHEZMOI_IMMUTABLE="")
            env.update(env_overrides)
            data = {"chezmoi": {"os": os_name, "osRelease": {"id": distro, "idLike": id_like},
                                "homeDir": temp, "hostname": "synthetic-server",
                                "sourceDir": str(source)}}
            result = subprocess.run(
                ["chezmoi", "--config", str(config), "--source", str(source),
                 "--destination", temp, "--persistent-state", str(home / "state.boltdb"),
                 "--override-data", json.dumps(data), "execute-template", "--init",
                 (ROOT / "dotfiles/.chezmoi.toml.tmpl").read_text()],
                env=env, text=True, capture_output=True, check=True, timeout=10,
            )
            return tomllib.loads(result.stdout)

    def test_hook_only_on_mutable_arch(self):
        self.assertIn("hooks", self.render())
        for kwargs in [
            {"distro": "fedora"},
            {"distro": "debian"},
            {"id_like": "particleos-arch"},
            {"id_like": "personal-os particleos-arch arch"},
            {"CHEZMOI_IMMUTABLE": "1"},
            {"CHEZMOI_CONTAINER": "1"},
            {"os_name": "windows"},
        ]:
            with self.subTest(kwargs=kwargs):
                self.assertNotIn("hooks", self.render(**kwargs))


@unittest.skipUnless(shutil.which("chezmoi"), "chezmoi is required")
class TargetRenderTests(unittest.TestCase):
    def test_committed_source_renders_for_synthetic_fedora_without_apply(self):
        spec = importlib.util.spec_from_file_location("stage", ROOT / "scripts/stage-dotfiles.py")
        staging = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(staging)
        with tempfile.TemporaryDirectory(prefix="personal-os-render-") as temp:
            t = Path(temp)
            repo = t / "os"
            repo.mkdir()
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            (repo / "dotfiles").symlink_to(ROOT / "dotfiles", target_is_directory=True)
            revision = subprocess.check_output(
                ["git", "-C", str(ROOT / "dotfiles"), "rev-parse", "HEAD"], text=True).strip()
            subprocess.run(["git", "-C", str(repo), "update-index", "--add", "--cacheinfo",
                            "160000", revision, "dotfiles"], check=True)
            subprocess.run(["git", "-C", str(repo), "-c", "user.name=Synthetic test",
                            "-c", "user.email=test@example.invalid", "commit", "-qm",
                            "Synthetic export pin"], check=True)
            factory = staging.stage(repo, t / "factory")
            source = factory / "source"
            home = t / "home"
            home.mkdir()
            config = t / "config.toml"
            config.write_text("")
            env = os.environ.copy()
            # Fork branding alone must retain the pinned source's ignore rules;
            # the real lifecycle additionally sets CHEZMOI_IMMUTABLE=1.
            env.update(HOME=str(home), CHEZMOI_IMMUTABLE="",
                       XDG_CONFIG_HOME=str(t / "config"), XDG_CACHE_HOME=str(t / "cache"),
                       XDG_DATA_HOME=str(t / "data"))
            data = {"chezmoi": {"os": "linux", "osRelease": {
                "id": "fedora", "idLike": "personal-os particleos-fedora fedora", "versionID": "44"},
                "hostname": "mini-travel-server", "username": "dab",
                "homeDir": str(home), "sourceDir": str(source)}}
            cmd = ["chezmoi", "--config", str(config), "--source", str(source),
                   "--destination", str(home), "--persistent-state", str(t / "state.boltdb"),
                   "--override-data", json.dumps(data)]
            rendered = subprocess.check_output(cmd + ["execute-template", "--init",
                (source / ".chezmoi.toml.tmpl").read_text()], env=env, text=True, timeout=10)
            self.assertNotIn("hooks", tomllib.loads(rendered))
            config.write_text(rendered)
            archive = t / "rendered.tar"
            subprocess.run(cmd + ["archive", "--output", str(archive)], env=env,
                           capture_output=True, check=True, timeout=20)
            with tarfile.open(archive) as targets:
                names = {member.name.rstrip("/").removeprefix("./") for member in targets}
            self.assertTrue(any("vdirsyncer/config" in name for name in names))
            self.assertFalse(any("rclone" in name for name in names))
            self.assertFalse(any(".clearhead" in name for name in names))
            # archive is a rendering operation, not an apply to the destination.
            self.assertEqual(list(home.iterdir()), [])


class PackageScriptTests(unittest.TestCase):
    def test_direct_invocation_exits_before_commands_on_immutable_target(self):
        with tempfile.TemporaryDirectory(prefix="personal-os-hook-") as temp:
            # An empty PATH proves the guard runs before id/git/makepkg/mktemp.
            result = subprocess.run(
                ["/bin/sh", str(ROOT / "dotfiles/bootstrap-paru.sh")],
                env={"PATH": temp, "CHEZMOI_IMMUTABLE": "1"},
                text=True, capture_output=True, timeout=10,
            )
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout + result.stderr, "")
