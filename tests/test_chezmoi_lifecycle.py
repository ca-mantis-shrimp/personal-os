"""Disposable source reconciliation + mocked chezmoi. NO real init/apply.

These are not Fedora/SELinux, systemd, or booted-image lifecycle validation.
"""
import hashlib
import json
import os
from pathlib import Path
import tempfile
from types import ModuleType
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "mkosi.profiles/mini-server/mkosi.extra/usr/libexec/personal-os-chezmoi"
lifecycle = ModuleType("lifecycle")
exec(compile(HELPER.read_text(), str(HELPER), "exec"), lifecycle.__dict__)
A, B, C = (letter * 40 for letter in "abc")


class FakeBackend:
    def __init__(self, home):
        self.home = home
        self.calls = []
        self.failure = None
        self.active = False
        self.last_written = None

    def confirm_stopped(self):
        self.calls.append("guard")
        if self.active:
            raise lifecycle.LifecycleError("Workloads still active")

    def initialize_repo(self, source):
        self.calls.append("git-init")
        (source / ".git").mkdir()
        (source / ".git/opaque-history").write_bytes(b"preserve this target-only metadata")

    def init(self, candidate):
        self.calls.append("init")
        if self.failure == "init":
            raise lifecycle.LifecycleError("Injected init failure")
        candidate.write_bytes((self.home / lifecycle.SOURCE_PATH / ".chezmoi.toml.tmpl").read_bytes())
        candidate.chmod(0o600)

    def apply(self, dry_run):
        name = "preflight" if dry_run else "apply"
        self.calls.append(name)
        if self.failure == name:
            raise lifecycle.LifecycleError("Injected apply failure")
        desired = (self.home / lifecycle.SOURCE_PATH / "dot_bashrc").read_bytes()
        target = self.home / ".bashrc"
        current = target.read_bytes() if target.exists() else None
        # Emulates --less-interactive --error-on-conflict, not a renderer.
        if current is not None and current not in (desired, self.last_written):
            raise lifecycle.LifecycleError("Existing/edited target conflict")
        if not dry_run:
            target.write_bytes(desired)
            self.last_written = desired


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.home = self.base / "home"
        self.home.mkdir(mode=0o700)
        self.backend = FakeBackend(self.home)
        self.context = {"hostname": "synthetic-vm", "distro": "fedora", "version": "44"}
        self.files = {".chezmoi.toml.tmpl": b'[data]\nprofile="synthetic"\n',
                      "dot_bashrc": b"factory one\n", "dot_config/demo": b"unchanged\n"}
        self.factory = self.make_factory(A, self.files)

    def make_factory(self, revision, files, predecessors=(), links=None, modes=None):
        factory = self.base / ("factory-" + str(len(list(self.base.glob("factory-*")))))
        source = factory / "source"
        source.mkdir(parents=True)
        manifest = []
        for name, data in files.items():
            path = source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            mode = (modes or {}).get(name, "100644")
            path.chmod(0o755 if mode == "100755" else 0o644)
            manifest.append({"path": name, "mode": mode, "sha256": hashlib.sha256(data).hexdigest()})
        for name, target in (links or {}).items():
            (source / name).symlink_to(target)
            manifest.append({"path": name, "mode": "120000", "sha256": hashlib.sha256(target.encode()).hexdigest()})
        (factory / "revision").write_text(revision + "\n")
        (factory / "manifest.json").write_text(json.dumps(manifest))
        (factory / "policy.json").write_text(json.dumps({"version": 1, "revision": revision,
                                                        "approved_predecessors": list(predecessors)}))
        return factory

    def run_configure(self, factory=None, context=None):
        return lifecycle.configure(self.home, factory or self.factory, self.backend, context or self.context)

    def state(self):
        return json.loads((self.home / lifecycle.STATE_PATH).read_bytes())

    def source(self, name):
        return self.home / lifecycle.SOURCE_PATH / name

    def test_first_apply_records_only_after_success(self):
        self.assertEqual(self.run_configure(), "applied")
        self.assertEqual(self.backend.calls, ["guard", "git-init", "init", "preflight", "apply"])
        self.assertEqual(self.state()["applied_revision"], A)
        self.assertEqual(self.state()["phase"], "complete")
        self.assertEqual((self.home / lifecycle.STATE_PATH).stat().st_mode & 0o777, 0o600)
        self.assertFalse((self.home / lifecycle.NEXT_CONFIG).exists())

    def test_same_pin_and_context_do_not_reapply_home_or_source_edits(self):
        self.run_configure()
        self.backend.calls.clear()
        (self.home / ".bashrc").write_bytes(b"home edit\n")
        self.source("dot_bashrc").write_bytes(b"source edit\n")
        (self.home / lifecycle.CONFIG_PATH).write_bytes(b"config edit\n")
        self.assertEqual(self.run_configure(), "unchanged")
        self.assertEqual(self.backend.calls, [])
        self.assertEqual((self.home / ".bashrc").read_bytes(), b"home edit\n")
        self.assertEqual(self.source("dot_bashrc").read_bytes(), b"source edit\n")

    def test_forward_update_preserves_unrelated_edits_untracked_files_and_git(self):
        self.run_configure()
        self.source("dot_config/demo").write_bytes(b"local source edit\n")
        self.source("untracked").write_bytes(b"local file\n")
        files = {**self.files, "dot_bashrc": b"factory two\n"}
        self.run_configure(self.make_factory(B, files, [A]))
        self.assertEqual(self.source("dot_config/demo").read_bytes(), b"local source edit\n")
        self.assertEqual(self.source("untracked").read_bytes(), b"local file\n")
        self.assertEqual(self.source(".git/opaque-history").read_bytes(), b"preserve this target-only metadata")
        self.assertEqual(self.state()["applied_revision"], B)
        self.assertEqual(self.backend.calls.count("init"), 1)
        self.assertEqual(self.backend.calls.count("git-init"), 1)

    def test_conflicting_source_preflights_all_paths_before_mutation(self):
        self.run_configure()
        self.source("dot_config/demo").write_bytes(b"local conflict\n")
        files = {**self.files, "dot_bashrc": b"factory two\n", "dot_config/demo": b"new upstream\n"}
        with self.assertRaisesRegex(lifecycle.LifecycleError, "conflicting local edits"):
            self.run_configure(self.make_factory(B, files, [A]))
        self.assertEqual(self.source("dot_bashrc").read_bytes(), self.files["dot_bashrc"])
        self.assertEqual(self.state()["source_revision"], A)

    def test_source_deletion_is_preserved_if_upstream_unchanged(self):
        self.run_configure()
        self.source("dot_config/demo").unlink()
        self.run_configure(self.make_factory(B, {**self.files, "dot_bashrc": b"two\n"}, [A]))
        self.assertFalse(self.source("dot_config/demo").exists())

    def test_removed_factory_file_does_not_remove_local_neighbor(self):
        self.run_configure()
        self.source("dot_config/extra").write_bytes(b"local\n")
        files = {name: data for name, data in self.files.items() if name != "dot_config/demo"}
        self.run_configure(self.make_factory(B, files, [A]))
        self.assertFalse(self.source("dot_config/demo").exists())
        self.assertEqual(self.source("dot_config/extra").read_bytes(), b"local\n")

    def test_removed_factory_file_with_local_edit_fails(self):
        self.run_configure()
        self.source("dot_config/demo").write_bytes(b"keep local\n")
        files = {name: data for name, data in self.files.items() if name != "dot_config/demo"}
        with self.assertRaises(lifecycle.LifecycleError):
            self.run_configure(self.make_factory(B, files, [A]))
        self.assertEqual(self.source("dot_config/demo").read_bytes(), b"keep local\n")

    def test_existing_untracked_source_is_not_adopted(self):
        self.source("existing").parent.mkdir(parents=True)
        self.source("existing").write_bytes(b"keep\n")
        with self.assertRaisesRegex(lifecycle.LifecycleError, "adoption"):
            self.run_configure()
        self.assertFalse((self.home / lifecycle.STATE_PATH).exists())

    def test_existing_home_file_is_not_overwritten(self):
        (self.home / ".bashrc").write_bytes(b"pre-existing mutable data\n")
        with self.assertRaisesRegex(lifecycle.LifecycleError, "target conflict"):
            self.run_configure()
        self.assertEqual((self.home / ".bashrc").read_bytes(), b"pre-existing mutable data\n")
        self.assertIsNone(self.state()["applied_revision"])

    def test_apply_failure_then_retry_does_not_reinitialize(self):
        self.backend.failure = "apply"
        with self.assertRaises(lifecycle.LifecycleError):
            self.run_configure()
        self.assertIsNone(self.state()["applied_revision"])
        self.backend.failure = None
        self.run_configure()
        self.assertEqual(self.state()["applied_revision"], A)
        self.assertEqual(self.backend.calls.count("init"), 1)

    def test_init_failure_then_retry(self):
        self.backend.failure = "init"
        with self.assertRaises(lifecycle.LifecycleError):
            self.run_configure()
        self.assertIsNone(self.state()["config_digest"])
        self.backend.failure = None
        self.run_configure()
        self.assertEqual(self.state()["applied_revision"], A)

    def test_interrupted_source_promotion_retries_without_resetting_edits(self):
        self.run_configure()
        files = {**self.files, "dot_bashrc": b"two\n", "dot_config/new": b"new\n"}
        factory = self.make_factory(B, files, [A])
        original = lifecycle.Home.put
        def fail_after_first_write(home, name, node):
            original(home, name, node)
            if name == lifecycle.SOURCE_PATH + "/dot_config/new":
                raise lifecycle.LifecycleError("Injected interruption")
        with patch.object(lifecycle.Home, "put", fail_after_first_write):
            with self.assertRaises(lifecycle.LifecycleError):
                self.run_configure(factory)
        self.assertEqual(self.state()["source_revision"], A)
        self.source("dot_config/demo").write_bytes(b"edit between attempts\n")
        self.run_configure(factory)
        self.assertEqual(self.source("dot_config/demo").read_bytes(), b"edit between attempts\n")
        self.assertEqual(self.state()["applied_revision"], B)

    def test_config_template_update_preserves_manual_config_edit(self):
        self.run_configure()
        config = self.home / lifecycle.CONFIG_PATH
        config.write_bytes(b"local generated-config edit\n")
        files = {**self.files, ".chezmoi.toml.tmpl": b'[data]\nprofile="changed"\n'}
        with self.assertRaisesRegex(lifecycle.LifecycleError, "config conflicts"):
            self.run_configure(self.make_factory(B, files, [A]))
        self.assertEqual(config.read_bytes(), b"local generated-config edit\n")
        self.assertEqual(self.state()["applied_revision"], A)
        self.assertTrue((self.home / lifecycle.NEXT_CONFIG).exists())

    def test_config_template_updates_unedited_generated_config(self):
        self.run_configure()
        files = {**self.files, ".chezmoi.toml.tmpl": b'[data]\nprofile="changed"\n'}
        self.run_configure(self.make_factory(B, files, [A]))
        self.assertEqual((self.home / lifecycle.CONFIG_PATH).read_bytes(), files[".chezmoi.toml.tmpl"])

    def test_candidate_config_symlink_is_rejected_before_init(self):
        self.backend.failure = "init"
        with self.assertRaises(lifecycle.LifecycleError):
            self.run_configure()
        outside = self.base / "outside"
        outside.write_bytes(b"do not overwrite\n")
        (self.home / lifecycle.NEXT_CONFIG).symlink_to(outside)
        self.backend.failure = None
        count = self.backend.calls.count("init")
        with self.assertRaises(lifecycle.LifecycleError):
            self.run_configure()
        self.assertEqual(self.backend.calls.count("init"), count)
        self.assertEqual(outside.read_bytes(), b"do not overwrite\n")

    def test_context_change_reapplies_conservatively(self):
        self.run_configure()
        self.run_configure(context={**self.context, "version": "45"})
        self.assertEqual(self.backend.calls.count("apply"), 2)
        (self.home / ".bashrc").write_bytes(b"local home edit\n")
        self.source("dot_bashrc").write_bytes(b"different desired source\n")
        with self.assertRaises(lifecycle.LifecycleError):
            self.run_configure(context={**self.context, "version": "46"})
        self.assertEqual((self.home / ".bashrc").read_bytes(), b"local home edit\n")

    def test_both_seen_and_unseen_older_or_unrelated_pins_are_blocked(self):
        self.run_configure()
        new = self.make_factory(B, {**self.files, "dot_bashrc": b"two\n"}, [A])
        self.run_configure(new)
        for factory in (self.factory, self.make_factory(C, self.files)):
            with self.subTest(factory=factory):
                with self.assertRaisesRegex(lifecycle.LifecycleError, "Older or unrelated"):
                    self.run_configure(factory)
                self.assertEqual(self.state()["applied_revision"], B)
                self.assertEqual(self.source("dot_bashrc").read_bytes(), b"two\n")

    def test_changed_payload_under_same_pin_is_blocked(self):
        self.run_configure()
        factory = self.make_factory(A, {**self.files, "dot_bashrc": b"different export\n"})
        with self.assertRaisesRegex(lifecycle.LifecycleError, "without a new dotfiles pin"):
            self.run_configure(factory)

    def test_unknown_state_schema_is_blocked(self):
        self.run_configure()
        state = self.state()
        state["version"] = 2
        (self.home / lifecycle.STATE_PATH).write_text(json.dumps(state))
        with self.assertRaisesRegex(lifecycle.LifecycleError, "Unsupported lifecycle state"):
            self.run_configure()

    def test_payload_corruption_and_unmanifested_files_fail_before_state(self):
        (self.factory / "source/dot_bashrc").write_bytes(b"corrupt\n")
        with self.assertRaises(lifecycle.LifecycleError):
            self.run_configure()
        self.assertFalse((self.home / lifecycle.STATE_PATH).exists())
        (self.factory / "source/dot_bashrc").write_bytes(self.files["dot_bashrc"])
        (self.factory / "source/unmanifested").write_bytes(b"unknown\n")
        with self.assertRaises(lifecycle.LifecycleError):
            self.run_configure()

    def test_safe_source_link_and_escaping_factory_link(self):
        factory = self.make_factory(A, self.files, links={"link": "dot_bashrc"})
        self.run_configure(factory)
        self.assertEqual(os.readlink(self.source("link")), "dot_bashrc")
        bad = self.make_factory(B, self.files, [A], links={"link": "/etc/passwd"})
        with self.assertRaises(lifecycle.LifecycleError):
            self.run_configure(bad)

    def test_symlink_source_parent_and_active_workloads_block_mutation(self):
        self.backend.active = True
        with self.assertRaises(lifecycle.LifecycleError):
            self.run_configure()
        self.assertFalse((self.home / lifecycle.STATE_PATH).exists())
        self.backend.active = False
        self.run_configure()
        outside = self.base / "outside-dir"
        outside.mkdir()
        self.source("dot_config/demo").unlink()
        self.source("dot_config").rmdir()
        self.source("dot_config").symlink_to(outside)
        with self.assertRaises(lifecycle.LifecycleError):
            self.run_configure(self.make_factory(B, {**self.files, "dot_bashrc": b"two\n"}, [A]))
        self.assertEqual(list(outside.iterdir()), [])

    def test_source_permission_edits_are_not_overwritten(self):
        self.run_configure()
        self.source("dot_bashrc").chmod(0o600)
        with self.assertRaises(lifecycle.LifecycleError):
            self.run_configure(self.make_factory(B, {**self.files, "dot_bashrc": b"two\n"}, [A]))
        self.assertEqual(self.source("dot_bashrc").stat().st_mode & 0o777, 0o600)

    def test_native_commands_enforce_safety_flags_and_real_destination(self):
        backend = lifecycle.Backend(self.home, "synthetic", os.getuid())
        command = backend.command()
        for flag in ("--less-interactive", "--error-on-conflict", "--force=false", "--interactive=false", "--no-tty"):
            self.assertIn(flag, command)
        self.assertEqual(command[command.index("--destination") + 1], str(self.home))
        self.assertEqual(backend.env["CHEZMOI_IMMUTABLE"], "1")
        self.assertEqual(backend.env["CHEZMOI_CONTAINER"], "1")
        self.assertNotIn("CREDENTIALS_DIRECTORY", backend.env)

    def test_parallel_configuration_attempts_fail_without_mutation(self):
        import fcntl
        lock = self.home / ".local/state/personal-os/chezmoi.lock"
        lock.parent.mkdir(parents=True, mode=0o700)
        with lock.open("wb") as stream:
            lock.chmod(0o600)
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with self.assertRaisesRegex(lifecycle.LifecycleError, "Another configuration"):
                self.run_configure()
        self.assertFalse((self.home / lifecycle.STATE_PATH).exists())
        self.assertEqual(self.backend.calls, [])

    def test_native_command_errors_do_not_expose_raw_output(self):
        from types import SimpleNamespace
        backend = lifecycle.Backend(self.home, "synthetic", os.getuid())
        with patch.object(lifecycle.subprocess, "run", return_value=SimpleNamespace(returncode=1, stdout=b"synthetic-sensitive-output", stderr=b"synthetic-sensitive-error")):
            with self.assertRaises(lifecycle.LifecycleError) as error:
                backend.run(["chezmoi", "not-executed"])
        self.assertNotIn("synthetic-sensitive", str(error.exception))

    def test_untrusted_runtime_account_context_is_not_accepted(self):
        path = self.base / "runtime/account-context.json"
        path.parent.mkdir()
        path.write_text(json.dumps({"version": 1, "uid": os.getuid(), "gid": os.getgid(), "username": "synthetic", "hostname": "synthetic-vm"}))
        if os.getuid() != 0:
            with self.assertRaisesRegex(lifecycle.LifecycleError, "Untrusted runtime"):
                lifecycle.enrolled_context(path)
        else:
            path.chmod(0o666)
            with self.assertRaises(lifecycle.LifecycleError):
                lifecycle.enrolled_context(path)

    def test_main_cannot_run_on_builder_or_desktop(self):
        with patch.object(lifecycle.os, "geteuid", return_value=0), patch.object(lifecycle, "configure") as configure:
            with patch("sys.stderr"):
                self.assertEqual(lifecycle.main(), 1)
            configure.assert_not_called()
        with patch.object(lifecycle.Path, "is_file", return_value=False), patch.object(lifecycle, "configure") as configure:
            with patch("sys.stderr"):
                self.assertEqual(lifecycle.main(), 1)
            configure.assert_not_called()


if __name__ == "__main__":
    unittest.main()
