"""Agent packaging tests: fake npm/Cargo/downloads, never agents/auth/installers."""
import hashlib
import importlib.util
import io
import json
import shutil
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
OVERLAY = ROOT / "mkosi.profiles/mini-server/mkosi.extra"
TOOLS_OVERLAY = ROOT / "mkosi.profiles/mini-server/mkosi.agent-extra"
spec = importlib.util.spec_from_file_location("agents", ROOT / "scripts/build-agent-tools.py")
assert spec is not None and spec.loader is not None
agents = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agents)


class AgentToolsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source"
        shutil.copytree(ROOT / "packages/agent-tools", self.source / "packages/agent-tools")
        self.dest = self.root / "dest"
        self.calls = []

    def fetch(self, _artifact, path):
        self.calls.append("fetch")
        if path.name == "claude":
            path.write_bytes(b"synthetic native binary, not executable")
        else:
            with tarfile.open(path, "w:gz") as archive:
                payload = b"# synthetic lock\n"
                name = path.stem
                version = agents.read_inputs(self.source)[1][name]["version"]
                entry = tarfile.TarInfo(f"{name}-{version}/Cargo.lock")
                entry.size = len(payload)
                archive.addfile(entry, io.BytesIO(payload))

    def execute(self, args, *, cwd, env):
        self.calls.append(args)
        self.assertNotIn("CREDENTIALS_DIRECTORY", env)
        self.assertNotIn("OP_SERVICE_ACCOUNT_TOKEN", env)
        self.assertNotIn("ANTHROPIC_API_KEY", env)
        if args[:2] == ["npm", "ci"]:
            self.assertIn("--ignore-scripts", args)
            self.assertIn("--engine-strict", args)
            self.assertEqual(env["npm_config_ignore_scripts"], "true")
            self.assertNotEqual(env["npm_config_userconfig"], env["npm_config_globalconfig"])
            package = cwd / "node_modules" / agents.PI
            (package / "dist/bundle").mkdir(parents=True)
            (package / "dist/bundle/cli.js").write_text("// synthetic, not run\n")
            (package / "package.json").write_text(json.dumps({"version": "0.85.1"}))
        elif args[:2] == ["cargo", "install"]:
            self.assertIn("--locked", args)
            self.assertTrue((cwd / "Cargo.lock").is_file())
            self.assertEqual(env["CARGO_BUILD_JOBS"], "2")
            name = cwd.name.rsplit("-", 1)[0]
            output = Path(args[args.index("--root") + 1]) / "bin" / name
            output.parent.mkdir(parents=True)
            output.write_bytes(b"synthetic shpool, not run")
        else:
            self.fail("Unexpected packaging command")

    def build(self, arch="x86-64"):
        agents.build(self.source, self.dest, arch, self.fetch, self.execute)

    def test_exact_inputs_and_complete_registry_integrity_locks(self):
        _, artifacts, version = agents.read_inputs(ROOT)
        self.assertEqual(version, "0.85.1")
        self.assertEqual(artifacts["claude"]["version"], "2.1.288")
        self.assertEqual(artifacts["shpool"]["version"], "0.11.5")
        self.assertEqual(artifacts["starship"]["version"], "1.24.2")
        self.assertEqual(artifacts["starship"]["size"], 379095)
        lock = json.loads((ROOT / "packages/agent-tools/package-lock.json").read_bytes())
        self.assertGreater(len(lock["packages"]), 100)

    def test_stages_only_runtime_payload_not_homes_caches_or_build_inputs(self):
        self.build()
        runtime = self.dest / "usr/lib/personal-os/agent-tools"
        self.assertEqual({path.name for path in runtime.iterdir()}, {"claude", "shpool", "starship", "node_modules", "provenance.json"})
        self.assertEqual((runtime / "claude").stat().st_mode & 0o777, 0o755)
        provenance = json.loads((runtime / "provenance.json").read_bytes())
        self.assertEqual(provenance["pi"], "0.85.1")
        self.assertEqual(provenance["npm_lock_sha256"], hashlib.sha256((self.source / "packages/agent-tools/package-lock.json").read_bytes()).hexdigest())
        self.assertEqual(len(provenance["starship_cargo_lock_sha256"]), 64)
        self.assertEqual((runtime / "starship").stat().st_mode & 0o777, 0o755)
        self.assertFalse((self.dest / "home").exists())

    def test_unsupported_architecture_fails_before_commands(self):
        with self.assertRaises(ValueError):
            self.build("arm64")
        self.assertEqual(self.calls, [])

    def test_changed_package_without_lock_update_is_refused(self):
        package = self.source / "packages/agent-tools/package.json"
        data = json.loads(package.read_bytes())
        data["dependencies"][agents.PI] = "latest"
        package.write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            self.build()
        self.assertEqual(self.calls, [])

    def test_builder_failure_does_not_publish_partial_payload(self):
        def fail(*_args, **_kwargs):
            raise RuntimeError("Synthetic build failure")
        with self.assertRaises(RuntimeError):
            agents.build(self.source, self.dest, "x86-64", self.fetch, fail)
        self.assertFalse(self.dest.exists())

    def test_commands_use_bounded_native_build_budget(self):
        with patch.object(agents.subprocess, "run", return_value=subprocess.CompletedProcess([], 0)) as command:
            agents.run(["npm", "ci"], cwd=self.root, env={})
            self.assertEqual(command.call_args.kwargs["timeout"], 1200)
            self.assertTrue(command.call_args.kwargs["capture_output"])
            agents.run(["cargo", "install"], cwd=self.root, env={})
            self.assertEqual(command.call_args.kwargs["timeout"], 2400)

    def test_command_timeout_suppresses_raw_output_and_exception_context(self):
        failure = subprocess.TimeoutExpired(["cargo", "install"], 2400,
                                            output=b"synthetic-private-output", stderr=b"synthetic-private-error")
        with (patch.object(agents.subprocess, "run", side_effect=failure),
              self.assertRaisesRegex(RuntimeError, "timed out; raw output suppressed") as error):
            agents.run(["cargo", "install"], cwd=self.root, env={})
        self.assertTrue(error.exception.__suppress_context__)
        self.assertNotIn("synthetic-private", str(error.exception))

    def test_invalid_installed_pi_metadata_does_not_publish_payload(self):
        def execute(args, **kwargs):
            self.execute(args, **kwargs)
            if args[:2] == ["npm", "ci"]:
                (kwargs["cwd"] / "node_modules" / agents.PI / "package.json").write_text("invalid synthetic JSON")
        with self.assertRaisesRegex(ValueError, "metadata is missing or invalid"):
            agents.build(self.source, self.dest, "x86-64", self.fetch, execute)
        self.assertFalse(self.dest.exists())

    def test_starship_failure_does_not_publish_other_completed_tools(self):
        def execute(args, **kwargs):
            if args[:2] == ["cargo", "install"] and kwargs["cwd"].name.startswith("starship-"):
                raise RuntimeError("Synthetic prompt-tool build failure")
            self.execute(args, **kwargs)
        with self.assertRaises(RuntimeError):
            agents.build(self.source, self.dest, "x86-64", self.fetch, execute)
        self.assertFalse((self.dest / "usr/lib/personal-os/agent-tools").exists())

    def test_starship_pin_or_source_drift_is_refused(self):
        path = self.source / "packages/agent-tools/artifacts.json"
        original = json.loads(path.read_bytes())
        for key, value in (("version", "latest"), ("url", "https://unreviewed.invalid/starship.crate"),
                           ("sha256", "not-a-checksum")):
            data = json.loads(json.dumps(original))
            data["starship"][key] = value
            path.write_text(json.dumps(data))
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.build()
            self.assertEqual(self.calls, [])

    def test_invalid_packaging_metadata_is_rejected_without_commands(self):
        for name in ("artifacts.json", "package.json", "package-lock.json"):
            path = self.source / "packages/agent-tools" / name
            original = path.read_bytes()
            path.write_text("invalid synthetic JSON")
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, "metadata is missing or invalid"):
                self.build()
            path.write_bytes(original)
        self.assertEqual(self.calls, [])
        self.assertFalse(self.dest.exists())

    def test_download_rejects_non_https_unapproved_or_credential_urls_before_io(self):
        for url in ("file:///synthetic", "http://downloads.claude.ai/synthetic",
                    "https://unreviewed.invalid/synthetic", "https://user:synthetic@downloads.claude.ai/synthetic"):
            with (self.subTest(url=url), patch.object(agents.urllib.request, "urlopen") as request,
                  self.assertRaisesRegex(ValueError, "approved HTTPS publisher")):
                agents.download({"url": url}, self.root / "rejected")
            request.assert_not_called()
        self.assertFalse((self.root / "rejected").exists())

    def download_fixture(self):
        data = b"synthetic reviewed artifact"
        artifact = {"url": "https://downloads.claude.ai/synthetic", "size": len(data), "sha256": hashlib.sha256(data).hexdigest()}
        class Response(io.BytesIO):
            def geturl(self):
                return artifact["url"]
        return data, artifact, Response

    def test_download_verifies_checksum_and_size_without_executing(self):
        data, artifact, response = self.download_fixture()
        with patch.object(agents.urllib.request, "urlopen", return_value=response(data)):
            agents.download(artifact, self.root / "download")
        with (patch.object(agents.urllib.request, "urlopen", return_value=response(b"corrupt")) as request,
              patch.object(agents.time, "sleep") as delay, self.assertRaises(ValueError)):
            agents.download(artifact, self.root / "corrupt")
        request.assert_called_once()
        delay.assert_not_called()
        self.assertFalse((self.root / "corrupt").exists())

    def test_transport_retry_discards_partial_bytes_before_verified_publication(self):
        data, artifact, response = self.download_fixture()
        class Interrupted(response):
            def read(self, size: int | None = -1) -> bytes:
                if self.tell():
                    raise TimeoutError("synthetic transport timeout")
                return super().read(3 if size is None or size < 0 else min(size, 3))
        with (patch.object(agents.urllib.request, "urlopen", side_effect=[Interrupted(data), response(data)]) as request,
              patch.object(agents.time, "sleep") as delay):
            agents.download(artifact, self.root / "download")
        self.assertEqual(request.call_count, 2)
        delay.assert_called_once_with(1)
        self.assertEqual((self.root / "download").read_bytes(), data)
        self.assertEqual(list(self.root.glob("personal-os-download-*")), [])

    def test_transport_retries_are_bounded_and_raw_errors_suppressed(self):
        _, artifact, _ = self.download_fixture()
        failure = agents.urllib.error.URLError("synthetic-private-transport-data")
        with (patch.object(agents.urllib.request, "urlopen", side_effect=failure) as request,
              patch.object(agents.time, "sleep") as delay,
              self.assertRaisesRegex(RuntimeError, "exhausted bounded retries") as error):
            agents.download(artifact, self.root / "download")
        self.assertEqual(request.call_count, 3)
        self.assertEqual([call.args for call in delay.call_args_list], [(1,), (2,)])
        self.assertTrue(error.exception.__suppress_context__)
        self.assertNotIn("synthetic-private", str(error.exception))
        self.assertFalse((self.root / "download").exists())
        self.assertEqual(list(self.root.glob("personal-os-download-*")), [])

    def test_only_transient_http_errors_are_retried(self):
        data, artifact, response = self.download_fixture()
        for code in (503, 404):
            failure = agents.urllib.error.HTTPError(artifact["url"], code, "synthetic", {}, None)
            with (self.subTest(code=code),
                  patch.object(agents.urllib.request, "urlopen", side_effect=[failure, response(data)]) as request,
                  patch.object(agents.time, "sleep") as delay):
                if code == 503:
                    agents.download(artifact, self.root / str(code))
                    self.assertEqual(request.call_count, 2)
                    delay.assert_called_once_with(1)
                else:
                    with self.assertRaisesRegex(RuntimeError, "HTTP request failed"):
                        agents.download(artifact, self.root / str(code))
                    request.assert_called_once()
                    delay.assert_not_called()
                    self.assertFalse((self.root / str(code)).exists())

    def test_artifact_redirect_is_a_hard_failure_without_partial_publication(self):
        data, artifact, response = self.download_fixture()
        class Redirect(response):
            def geturl(self):
                return "https://unreviewed.invalid/synthetic"
        with (patch.object(agents.urllib.request, "urlopen", return_value=Redirect(data)) as request,
              patch.object(agents.time, "sleep") as delay,
              self.assertRaisesRegex(ValueError, "Unexpected artifact redirect")):
            agents.download(artifact, self.root / "download")
        request.assert_called_once()
        delay.assert_not_called()
        self.assertFalse((self.root / "download").exists())
        self.assertEqual(list(self.root.glob("personal-os-download-*")), [])

    def test_existing_or_raced_download_destination_is_never_overwritten(self):
        data, artifact, response = self.download_fixture()
        destination = self.root / "download"
        destination.write_bytes(b"original")
        with (patch.object(agents.urllib.request, "urlopen") as request,
              self.assertRaisesRegex(ValueError, "existing artifact")):
            agents.download(artifact, destination)
        request.assert_not_called()
        destination.unlink()
        real_link = agents.os.link
        def competing_writer(source, target):
            Path(target).write_bytes(b"original")
            return real_link(source, target)
        with (patch.object(agents.urllib.request, "urlopen", return_value=response(data)),
              patch.object(agents.os, "link", side_effect=competing_writer), self.assertRaises(FileExistsError)):
            agents.download(artifact, destination)
        self.assertEqual(destination.read_bytes(), b"original")
        self.assertEqual(list(self.root.glob("personal-os-download-*")), [])

    def test_effective_config_selects_build_only_compilers_and_runtime_tools(self):
        result = subprocess.run(["mkosi", "--json", "summary"], cwd=ROOT, capture_output=True, check=True, timeout=30)
        main = next(x for x in json.loads(result.stdout)["Images"] if x["Image"] == "main")
        self.assertTrue({"nodejs", "npm", "git-core", "ripgrep", "fd-find", "tmux"}.issubset(set(main["Packages"])))
        self.assertTrue({"cargo", "rust", "gcc"}.issubset(set(main["BuildPackages"])))
        self.assertNotIn("cargo", main["Packages"])
        self.assertNotIn("starship", main["Packages"])
        wrapper = (TOOLS_OVERLAY / "usr/bin/starship").read_text()
        self.assertIn("exec /usr/lib/personal-os/agent-tools/starship", wrapper)
        self.assertIn(str(ROOT / "mkosi.profiles/mini-server/mkosi.build.chroot"), main["BuildScripts"])
        self.assertTrue(main["WithNetwork"])

    def test_existing_payload_is_not_overwritten(self):
        self.build()
        with self.assertRaises(ValueError):
            self.build()

    def test_wrapper_update_guards_do_not_launch_desktop_agents(self):
        for name, args in (("pi", ["update"]), ("pi", ["update", "--extensions", "--self"]), ("claude", ["update"]), ("claude", ["install"])):
            result = subprocess.run(["sh", str(TOOLS_OVERLAY / "usr/bin" / name), *args], capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 1)
            self.assertIn(b"image-owned", result.stderr)

    def test_shpool_is_private_and_disabled(self):
        socket = (OVERLAY / "usr/lib/systemd/user/shpool.socket").read_text()
        service = (OVERLAY / "usr/lib/systemd/user/shpool.service").read_text()
        preset = (OVERLAY / "usr/lib/systemd/user-preset/05-mini-server.preset").read_text()
        self.assertIn("ListenStream=%t/shpool/shpool.socket", socket)
        self.assertIn("SocketMode=0600", socket)
        self.assertIn("DirectoryMode=0700", socket)
        self.assertIn("KillMode=control-group", service)
        self.assertIn("NoNewPrivileges=no", service)
        self.assertNotIn("NoNewPrivileges=yes", service)
        self.assertIn("disable shpool.socket", preset)
        self.assertIn("disable shpool.service", preset)

    @unittest.skipUnless(shutil.which("systemd-analyze"), "systemd-analyze required")
    def test_shpool_units_verify_offline(self):
        directory = self.root / "units"
        directory.mkdir()
        for name in ("shpool.service", "shpool.socket"):
            text = (OVERLAY / "usr/lib/systemd/user" / name).read_text()
            text = text.replace("/usr/bin/shpool", str(TOOLS_OVERLAY / "usr/bin/shpool"))
            (directory / name).write_text(text)
        result = subprocess.run(["systemd-analyze", "--user", "verify", str(directory / "shpool.service"), str(directory / "shpool.socket")], capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr.decode())


if __name__ == "__main__":
    unittest.main()
