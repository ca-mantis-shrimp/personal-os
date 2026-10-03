"""Agent packaging tests: fake npm/Cargo/downloads, never agents/auth/installers."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
OVERLAY = ROOT / "mkosi.profiles/mini-server/mkosi.extra"
spec = importlib.util.spec_from_file_location("agents", ROOT / "scripts/build-agent-tools.py")
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

    def fetch(self, artifact, path):
        self.calls.append("fetch")
        if path.name == "claude":
            path.write_bytes(b"synthetic native binary, not executable")
        else:
            with tarfile.open(path, "w:gz") as archive:
                payload = b"# synthetic lock\n"
                entry = tarfile.TarInfo("shpool-0.11.5/Cargo.lock")
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
            output = Path(args[args.index("--root") + 1]) / "bin/shpool"
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
        lock = json.loads((ROOT / "packages/agent-tools/package-lock.json").read_bytes())
        self.assertGreater(len(lock["packages"]), 100)

    def test_stages_only_runtime_payload_not_homes_caches_or_build_inputs(self):
        self.build()
        runtime = self.dest / "usr/lib/personal-os/agent-tools"
        self.assertEqual({path.name for path in runtime.iterdir()}, {"claude", "shpool", "node_modules", "provenance.json"})
        self.assertEqual((runtime / "claude").stat().st_mode & 0o777, 0o755)
        provenance = json.loads((runtime / "provenance.json").read_bytes())
        self.assertEqual(provenance["pi"], "0.85.1")
        self.assertEqual(provenance["npm_lock_sha256"], hashlib.sha256((self.source / "packages/agent-tools/package-lock.json").read_bytes()).hexdigest())
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
        def fail(*args, **kwargs):
            raise RuntimeError("Synthetic build failure")
        with self.assertRaises(RuntimeError):
            agents.build(self.source, self.dest, "x86-64", self.fetch, fail)
        self.assertFalse(self.dest.exists())

    def test_download_verifies_checksum_and_size_without_executing(self):
        data = b"synthetic reviewed artifact"
        artifact = {"url": "https://downloads.claude.ai/synthetic", "size": len(data), "sha256": hashlib.sha256(data).hexdigest()}
        class Response(io.BytesIO):
            def geturl(self):
                return artifact["url"]
        with patch.object(agents.urllib.request, "urlopen", return_value=Response(data)):
            agents.download(artifact, self.root / "download")
        with patch.object(agents.urllib.request, "urlopen", return_value=Response(b"corrupt")):
            with self.assertRaises(ValueError):
                agents.download(artifact, self.root / "corrupt")

    def test_effective_config_selects_build_only_compilers_and_runtime_tools(self):
        result = subprocess.run(["mkosi", "--json", "summary"], cwd=ROOT, capture_output=True, check=True, timeout=30)
        main = next(x for x in json.loads(result.stdout)["Images"] if x["Image"] == "main")
        self.assertTrue({"nodejs", "npm", "git-core", "ripgrep", "fd-find", "tmux"}.issubset(set(main["Packages"])))
        self.assertTrue({"cargo", "rust", "gcc"}.issubset(set(main["BuildPackages"])))
        self.assertNotIn("cargo", main["Packages"])
        self.assertIn(str(ROOT / "mkosi.profiles/mini-server/mkosi.build.chroot"), main["BuildScripts"])
        self.assertTrue(main["WithNetwork"])

    def test_existing_payload_is_not_overwritten(self):
        self.build()
        with self.assertRaises(ValueError):
            self.build()

    def test_wrapper_update_guards_do_not_launch_desktop_agents(self):
        for name, args in (("pi", ["update"]), ("pi", ["update", "--extensions", "--self"]), ("claude", ["update"]), ("claude", ["install"])):
            result = subprocess.run(["sh", str(OVERLAY / "usr/bin" / name), *args], capture_output=True, timeout=10)
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
        self.assertIn("NoNewPrivileges=yes", service)
        self.assertIn("disable shpool.socket", preset)
        self.assertIn("disable shpool.service", preset)

    @unittest.skipUnless(shutil.which("systemd-analyze"), "systemd-analyze required")
    def test_shpool_units_verify_offline(self):
        directory = self.root / "units"
        directory.mkdir()
        for name in ("shpool.service", "shpool.socket"):
            text = (OVERLAY / "usr/lib/systemd/user" / name).read_text()
            text = text.replace("/usr/bin/shpool", str(OVERLAY / "usr/bin/shpool"))
            (directory / name).write_text(text)
        result = subprocess.run(["systemd-analyze", "--user", "verify", str(directory / "shpool.service"), str(directory / "shpool.socket")], capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr.decode())


if __name__ == "__main__":
    unittest.main()
