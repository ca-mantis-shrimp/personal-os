"""Synthetic committed-source staging tests; no chezmoi execution."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("staging", ROOT / "scripts/stage-dotfiles.py")
staging = importlib.util.module_from_spec(spec)
spec.loader.exec_module(staging)


class StagingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / "os"
        self.source = self.repo / "dotfiles"
        self.source.mkdir(parents=True)
        for repo in (self.repo, self.source):
            self.git(repo, "init", "-q")
            self.git(repo, "config", "user.email", "test@example.invalid")
            self.git(repo, "config", "user.name", "Synthetic test")
        for name, content in {
            "dot_bashrc": "committed\n",
            ".chezmoi.toml.tmpl": "target template\n",
            ".clearhead/history.md": "historical plan\n",
            "os/image": "build artifact\n",
            "archive/old": "archive\n",
            "dot_config/rclone/gdrive-backup.env": "synthetic runtime input\n",
        }.items():
            path = self.source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        self.git(self.source, "add", ".")
        self.git(self.source, "commit", "-qm", "Synthetic source")
        self.revision = self.git(self.source, "rev-parse", "HEAD").strip()
        self.git(self.repo, "update-index", "--add", "--cacheinfo",
                 "160000", self.revision, "dotfiles")
        self.git(self.repo, "commit", "-qm", "Pin source")
        self.buildroot = Path(self.temp.name) / "buildroot"

    @staticmethod
    def git(repo, *args):
        return subprocess.check_output(["git", "-C", str(repo), *args],
                                       stderr=subprocess.PIPE, text=True)

    def test_exports_pin_not_dirty_tree_or_new_head(self):
        (self.source / "dot_bashrc").write_text("new commit\n")
        self.git(self.source, "commit", "-qam", "Unpinned change")
        (self.source / "dot_bashrc").write_text("dirty\n")
        (self.source / "untracked-secret").write_text("synthetic\n")
        destination = staging.stage(self.repo, self.buildroot)
        self.assertEqual((destination / "source/dot_bashrc").read_text(), "committed\n")
        self.assertEqual((destination / "revision").read_text().strip(), self.revision)
        self.assertFalse((destination / "source/untracked-secret").exists())
        manifest = json.loads((destination / "manifest.json").read_text())
        self.assertEqual({row["path"] for row in manifest},
                         {"dot_bashrc", ".chezmoi.toml.tmpl"})
        self.assertFalse((destination / "source/.git").exists())

    def test_refuses_existing_destination(self):
        staging.stage(self.repo, self.buildroot)
        with self.assertRaises(ValueError):
            staging.stage(self.repo, self.buildroot)

    def test_preserves_internal_source_symlink(self):
        (self.source / "link").symlink_to("dot_bashrc")
        self.git(self.source, "add", "link")
        self.git(self.source, "commit", "-qm", "Internal link")
        revision = self.git(self.source, "rev-parse", "HEAD").strip()
        self.git(self.repo, "update-index", "--cacheinfo", "160000", revision, "dotfiles")
        self.git(self.repo, "commit", "-qm", "Pin internal link")
        destination = staging.stage(self.repo, self.buildroot)
        self.assertTrue((destination / "source/link").is_symlink())
        self.assertEqual((destination / "source/link").read_text(), "committed\n")

    def test_rejects_escaping_source_symlinks(self):
        (self.source / "escape").symlink_to("/etc/passwd")
        self.git(self.source, "add", "escape")
        self.git(self.source, "commit", "-qm", "Synthetic unsafe source")
        revision = self.git(self.source, "rev-parse", "HEAD").strip()
        self.git(self.repo, "update-index", "--cacheinfo", "160000", revision, "dotfiles")
        self.git(self.repo, "commit", "-qm", "Pin unsafe source")
        with self.assertRaises(ValueError):
            staging.stage(self.repo, self.buildroot)
        self.assertFalse(self.buildroot.exists())
