#!/usr/bin/python3
"""Build image-owned agent binaries in mkosi's disposable build overlay.

No agent is launched, no home configuration/authentication is imported, no
curl installer is executed. Only generated runtime payload goes into DESTDIR.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
import tempfile
import urllib.request

PI = "@earendil-works/pi-coding-agent"


def read_inputs(source):
    directory = source / "packages/agent-tools"
    artifacts = json.loads((directory / "artifacts.json").read_bytes())
    package = json.loads((directory / "package.json").read_bytes())
    lock = json.loads((directory / "package-lock.json").read_bytes())
    if artifacts["version"] != 1 or artifacts["architecture"] != "x86-64":
        raise ValueError("Unsupported agent artifact policy")
    for name, base, suffix in (
            ("claude", "https://downloads.claude.ai/claude-code-releases/", "/linux-x64/claude"),
            ("shpool", "https://static.crates.io/crates/shpool/shpool-", ".crate")):
        artifact = artifacts[name]
        if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", artifact["version"]):
            raise ValueError("Artifact requires an exact release")
        if artifact["url"] != base + artifact["version"] + suffix or not re.fullmatch(r"[a-f0-9]{64}", artifact["sha256"]):
            raise ValueError("Invalid artifact source/integrity")
    version = package["dependencies"][PI]
    if set(package["dependencies"]) != {PI} or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version):
        raise ValueError("Pi requires an exact version")
    if lock["lockfileVersion"] != 3 or lock["packages"][""]["dependencies"] != package["dependencies"]:
        raise ValueError("Dependency lock does not match package input")
    if lock["packages"]["node_modules/" + PI]["version"] != version:
        raise ValueError("Locked Pi version differs")
    for name, entry in lock["packages"].items():
        if not name:
            continue
        if not entry.get("resolved", "").startswith("https://registry.npmjs.org/") or not entry.get("integrity", "").startswith("sha512-"):
            raise ValueError("All npm dependencies need public registry integrity locks")
    return directory, artifacts, version


def download(artifact, path):
    maximum = artifact.get("size", 16 * 1024 * 1024)
    actual = hashlib.sha256()
    size = 0
    with urllib.request.urlopen(artifact["url"], timeout=60) as response, path.open("xb") as output:
        # Do not accept a redirect to an unreviewed artifact host.
        if response.geturl() != artifact["url"]:
            raise ValueError("Unexpected artifact redirect")
        while block := response.read(1024 * 1024):
            size += len(block)
            if size > maximum:
                raise ValueError("Artifact exceeds its size bound")
            actual.update(block)
            output.write(block)
    if actual.hexdigest() != artifact["sha256"] or "size" in artifact and size != artifact["size"]:
        raise ValueError("Artifact integrity/size mismatch")


def run(args, *, cwd, env):
    # Build command output can contain URLs/environment-derived data. Don't echo it.
    result = subprocess.run(args, cwd=cwd, env=env, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, timeout=1200)
    if result.returncode:
        raise RuntimeError("Agent-tool build command failed; raw output suppressed")


def build(source, destination, architecture, fetch=download, execute=run):
    inputs, artifacts, pi_version = read_inputs(source)
    if architecture != artifacts["architecture"]:
        raise ValueError("Agent artifacts currently support only x86-64; review new platform pins first")
    root = destination / "usr/lib/personal-os/agent-tools"
    if root.exists() or root.is_symlink():
        raise ValueError("Refusing an existing agent runtime payload")
    with tempfile.TemporaryDirectory(prefix="personal-os-agent-build-") as scratch:
        work = Path(scratch)
        npm = work / "npm"
        npm.mkdir()
        for name in ("package.json", "package-lock.json"):
            shutil.copyfile(inputs / name, npm / name)
        for name in ("user.npmrc", "global.npmrc"):
            (work / name).touch()
        env = {"PATH": "/usr/sbin:/usr/bin", "HOME": str(work / "home"), "LANG": "C.UTF-8",
               "npm_config_cache": str(work / "npm-cache"), "npm_config_userconfig": str(work / "user.npmrc"),
               "npm_config_globalconfig": str(work / "global.npmrc"), "npm_config_registry": "https://registry.npmjs.org",
               "npm_config_ignore_scripts": "true", "CARGO_HOME": str(work / "cargo-home"),
               "CARGO_TARGET_DIR": str(work / "cargo-target")}
        execute(["npm", "ci", "--ignore-scripts", "--omit=dev", "--omit=optional", "--engine-strict",
                 "--audit=false", "--fund=false"], cwd=npm, env=env)
        pi_entry = npm / "node_modules" / PI / "dist/bundle/cli.js"
        if not pi_entry.is_file() or pi_entry.is_symlink():
            raise ValueError("Pi bundle entry is missing/unsafe")
        installed = json.loads((npm / "node_modules" / PI / "package.json").read_bytes())
        if installed["version"] != pi_version:
            raise ValueError("Installed Pi version mismatch")
        fetch(artifacts["claude"], work / "claude")
        fetch(artifacts["shpool"], work / "shpool.crate")
        crate = work / "source"
        crate.mkdir()
        with tarfile.open(work / "shpool.crate") as archive:
            # Python's data filter rejects device nodes, traversal and escaping links.
            archive.extractall(crate, filter="data")
        project = crate / ("shpool-" + artifacts["shpool"]["version"])
        if not (project / "Cargo.lock").is_file():
            raise ValueError("shpool source lacks its locked dependency graph")
        execute(["cargo", "install", "--locked", "--path", str(project), "--root", str(work / "shpool-install")],
                cwd=project, env=env)
        shpool = work / "shpool-install/bin/shpool"
        if not shpool.is_file() or shpool.is_symlink():
            raise ValueError("shpool runtime binary missing/unsafe")
        # Publish only after ALL dependency/artifact/build checks succeed.
        root.mkdir(parents=True)
        shutil.copytree(npm / "node_modules", root / "node_modules", symlinks=True)
        for name, binary in (("claude", work / "claude"), ("shpool", shpool)):
            shutil.copyfile(binary, root / name)
            (root / name).chmod(0o755)
        provenance = {"version": 1, "pi": pi_version, "artifacts": artifacts,
                      "npm_lock_sha256": hashlib.sha256((inputs / "package-lock.json").read_bytes()).hexdigest(),
                      "cargo_lock_sha256": hashlib.sha256((project / "Cargo.lock").read_bytes()).hexdigest()}
        (root / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")


def main():
    # Never default to /usr or a live desktop user's prefix.
    if not all(os.environ.get(name) for name in ("SRCDIR", "DESTDIR", "ARCHITECTURE")):
        raise RuntimeError("This script requires mkosi's disposable build context")
    build(Path(os.environ["SRCDIR"]), Path(os.environ["DESTDIR"]), os.environ["ARCHITECTURE"])


if __name__ == "__main__":
    main()
