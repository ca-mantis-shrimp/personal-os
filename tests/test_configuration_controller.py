"""Root-controller tests: fake systemd/runuser only; no host service operations."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
OVERLAY = ROOT / "mkosi.profiles/mini-server/mkosi.extra"
HELPER = OVERLAY / "usr/libexec/personal-os-configuration"
controller = ModuleType("controller")
exec(compile(HELPER.read_text(), str(HELPER), "exec"), controller.__dict__)
CONTEXT = {"version": 1, "username": "synthetic", "uid": 1234, "gid": 1234, "hostname": "synthetic-vm"}


class FakeBackend(controller.Backend):
    def __init__(self, runtime):
        super().__init__()
        self.runtime = runtime
        self.calls = []
        self.states = {unit: b"active" for unit in controller.USER_UNITS}
        self.states.update({"radicale.service": b"active", "syncthing@synthetic.service": b"active",
                            "user@1234.service": b"active"})
        self.fail_stop = None
        self.fail_apply = False
        self.fail_enrollment = False
        self.fail_reload = False

    def identity(self, context):
        self.calls.append("identity")

    def enrollment(self, context):
        self.calls.append("enrollment")
        if self.fail_enrollment:
            raise controller.ControlError("Injected enrollment failure")

    def run(self, args):
        self.calls.append(args)
        self.assert_no_readiness()
        unit = args[-1]
        if "show" in args:
            return self.states.get(unit, b"inactive") + b"\n"
        if "stop" in args:
            if unit == self.fail_stop:
                raise controller.ControlError("Injected stop failure")
            self.states[unit] = b"inactive"
        if "daemon-reload" in args and self.fail_reload:
            raise controller.ControlError("Injected reload failure")
        return b""

    def assert_no_readiness(self):
        if (self.runtime / "chezmoi-ready").exists():
            raise AssertionError("Commands ran before readiness revocation")

    def apply(self, context):
        self.calls.append("apply")
        self.assert_no_readiness()
        for unit, value in self.states.items():
            if not unit.startswith("user@"):
                if value not in controller.STOPPED:
                    raise AssertionError("Apply started with a running workload")
        # Simulate a user hook starting a job even during a partial apply.
        self.states["otelcol.service"] = b"active"
        if self.fail_apply:
            raise controller.ControlError("Injected child failure")


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.runtime = Path(self.temp.name) / "runtime"
        self.runtime.mkdir(mode=0o755)
        self.context = self.runtime / "account-context.json"
        self.context.write_text(json.dumps(CONTEXT))
        self.context.chmod(0o644)
        (self.runtime / "chezmoi-ready").write_text("old readiness")
        self.backend = FakeBackend(self.runtime)

    def control(self, apply=True):
        with controller.Runtime(self.runtime, (os.getuid(), os.getgid())) as runtime:
            return controller.control(runtime, self.backend, apply)

    def test_success_stops_before_and_after_apply_without_granting_readiness(self):
        self.assertEqual(self.control(), "configured-workloads-blocked")
        self.assertFalse((self.runtime / "chezmoi-ready").exists())
        self.assertIn("apply", self.backend.calls)
        self.assertTrue(all(value in controller.STOPPED for unit, value in self.backend.states.items() if not unit.startswith("user@")))
        stops = [args[-1] for args in self.backend.calls if isinstance(args, list) and "stop" in args]
        self.assertLess(stops.index("vdirsyncer.timer"), stops.index("vdirsyncer.service"))
        self.assertEqual(stops.count("otelcol.service"), 2)
        self.assertTrue(set(stops).isdisjoint({"sshd.service", "tailscaled.service", "user@1234.service"}))

    def test_child_failure_cleans_up_and_allows_safe_retry(self):
        self.backend.fail_apply = True
        with self.assertRaises(controller.ControlError):
            self.control()
        self.assertEqual(self.backend.states["otelcol.service"], b"inactive")
        self.assertFalse((self.runtime / "chezmoi-ready").exists())
        self.backend.fail_apply = False
        self.control()
        self.assertEqual(self.backend.calls.count("apply"), 2)

    def test_failed_stop_blocks_apply_but_attempts_other_stops(self):
        self.backend.fail_stop = "radicale.service"
        with self.assertRaisesRegex(controller.ControlError, "stopping/verification"):
            self.control()
        self.assertNotIn("apply", self.backend.calls)
        self.assertEqual(self.backend.states["syncthing.service"], b"inactive")
        self.assertEqual(self.backend.states["syncthing@synthetic.service"], b"inactive")

    def test_failed_reload_blocks_apply_but_still_stops_jobs(self):
        self.backend.fail_reload = True
        with self.assertRaises(controller.ControlError):
            self.control()
        self.assertNotIn("apply", self.backend.calls)
        self.assertEqual(self.backend.states["vdirsyncer.service"], b"inactive")

    def test_unverified_stop_state_blocks_apply(self):
        self.backend.states["radicale.service"] = b"active"
        original = self.backend.run
        def stubborn(args):
            result = original(args)
            if "stop" in args and args[-1] == "radicale.service":
                self.backend.states["radicale.service"] = b"deactivating"
            return result
        self.backend.run = stubborn
        with self.assertRaises(controller.ControlError):
            self.control()
        self.assertNotIn("apply", self.backend.calls)

    def test_enrollment_failure_keeps_workloads_stopped(self):
        self.backend.fail_enrollment = True
        with self.assertRaises(controller.ControlError):
            self.control()
        self.assertNotIn("apply", self.backend.calls)
        self.assertFalse((self.runtime / "chezmoi-ready").exists())

    def test_cleanup_only_ignores_enrollment_and_never_applies(self):
        self.backend.fail_enrollment = True
        self.assertEqual(self.control(False), "stopped")
        self.assertNotIn("enrollment", self.backend.calls)
        self.assertNotIn("apply", self.backend.calls)

    def test_inactive_manager_is_not_started(self):
        self.backend.states["user@1234.service"] = b"inactive"
        self.control(False)
        self.assertFalse(any(isinstance(args, list) and ("--user" in args or "start" in args) for args in self.backend.calls))

    def test_transitioning_manager_blocks_apply(self):
        self.backend.states["user@1234.service"] = b"activating"
        with self.assertRaises(controller.ControlError):
            self.control()
        self.assertNotIn("apply", self.backend.calls)

    def test_missing_or_malformed_context_revokes_readiness_without_apply(self):
        for data in (None, b"not json", json.dumps({**CONTEXT, "uid": True}).encode()):
            with self.subTest(data=data):
                if data is None:
                    self.context.unlink()
                else:
                    self.context.write_bytes(data)
                (self.runtime / "chezmoi-ready").write_text("old")
                with self.assertRaises((OSError, ValueError, controller.ControlError)):
                    self.control()
                self.assertFalse((self.runtime / "chezmoi-ready").exists())
        self.assertNotIn("apply", self.backend.calls)

    def test_context_symlink_is_not_followed(self):
        original = self.context.read_bytes()
        outside = Path(self.temp.name) / "outside"
        outside.write_bytes(original)
        self.context.unlink()
        self.context.symlink_to(outside)
        with self.assertRaises(OSError):
            self.control()
        self.assertEqual(outside.read_bytes(), original)
        self.assertFalse((self.runtime / "chezmoi-ready").exists())

    def test_readiness_symlink_is_unlinked_without_touching_destination(self):
        outside = Path(self.temp.name) / "outside"
        outside.write_bytes(b"keep")
        (self.runtime / "chezmoi-ready").unlink()
        (self.runtime / "chezmoi-ready").symlink_to(outside)
        self.control(False)
        self.assertEqual(outside.read_bytes(), b"keep")

    def test_parallel_controller_is_rejected(self):
        with controller.Runtime(self.runtime, (os.getuid(), os.getgid())):
            with self.assertRaisesRegex(controller.ControlError, "Another controller"):
                self.control()

    def test_child_identity_and_environment_are_explicit(self):
        command = controller.Backend.child_command(CONTEXT)
        self.assertEqual(command[:4], ["/usr/sbin/runuser", "--user", "synthetic", "--"])
        self.assertIn("-i", command)
        self.assertIn("HOME=/home/synthetic", command)
        self.assertEqual(command[-1], "/usr/libexec/personal-os-chezmoi")
        backend = controller.Backend()
        self.assertEqual(set(backend.env), {"PATH", "LANG"})
        self.assertNotIn("CREDENTIALS_DIRECTORY", backend.env)

    def test_nss_divergence_rejected_before_targeting_another_user(self):
        user = SimpleNamespace(pw_uid=1235, pw_gid=1234, pw_dir="/home/synthetic", pw_name="synthetic")
        with patch.object(controller.pwd, "getpwnam", return_value=user), patch.object(controller.pwd, "getpwuid", return_value=user):
            with self.assertRaisesRegex(controller.ControlError, "diverged"):
                controller.Backend.identity(CONTEXT)

    def test_command_failure_does_not_expose_raw_output(self):
        with patch.object(controller.subprocess, "run", return_value=SimpleNamespace(returncode=1, stdout=b"sensitive-output", stderr=b"sensitive-error")):
            with self.assertRaises(controller.ControlError) as error:
                controller.Backend().run(["never-executed"])
        self.assertNotIn("sensitive-", str(error.exception))

    def test_child_timeout_kills_process_group_before_returning_failure(self):
        child = MagicMock()
        child.pid = 98765
        child.__enter__.return_value = child
        child.communicate.side_effect = [subprocess.TimeoutExpired("synthetic", 480), (b"", b"")]
        with patch.object(controller.subprocess, "Popen", return_value=child), patch.object(controller.os, "killpg") as kill:
            with self.assertRaisesRegex(controller.ControlError, "timed out"):
                controller.Backend().apply(CONTEXT)
        kill.assert_called_once_with(child.pid, controller.signal.SIGKILL)
        self.assertEqual(child.communicate.call_count, 2)

    def test_main_rejects_desktop_and_unprivileged_execution(self):
        with patch.object(controller.os, "geteuid", return_value=1000), patch.object(controller, "Runtime") as runtime, patch("sys.stderr"):
            self.assertEqual(controller.main(), 1)
            runtime.assert_not_called()

    def test_unit_is_disabled_and_cgroup_cleanup_is_configured(self):
        unit = (OVERLAY / "usr/lib/systemd/system/personal-os-configuration.service").read_text()
        preset = (OVERLAY / "usr/lib/systemd/system-preset/05-mini-server.preset").read_text()
        self.assertIn("disable personal-os-configuration.service", preset)
        self.assertIn("ExecStopPost=/usr/libexec/personal-os-configuration --stop", unit)
        self.assertIn("KillMode=control-group", unit)
        self.assertNotIn("Before=sshd", unit)
        self.assertIn("Requires=personal-os-account.service", unit)

    @unittest.skipUnless(shutil.which("systemd-analyze"), "systemd-analyze required")
    def test_unit_verifies_offline_with_adapted_local_paths(self):
        directory = Path(self.temp.name)
        for name in ("personal-os-account", "personal-os-configuration"):
            text = (OVERLAY / f"usr/lib/systemd/system/{name}.service").read_text()
            text = text.replace(f"/usr/libexec/{name}", str(OVERLAY / f"usr/libexec/{name}"))
            (directory / f"{name}.service").write_text(text)
        result = subprocess.run(["systemd-analyze", "verify", str(directory / "personal-os-configuration.service")], capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
