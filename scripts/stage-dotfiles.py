#!/usr/bin/env python3
"""Export the OS gitlink's committed chezmoi payload; never render or apply it."""

import argparse
import hashlib
import json
import posixpath
from pathlib import Path, PurePosixPath
import subprocess

# Build payload boundaries only, not a replacement for chezmoi's target guards.
# Keep development trees, historical plans and runtime environment files out.
EXCLUDED_ROOTS = {".clearhead", ".devcontainer", ".git", "archive", "mkosi", "os"}
EXCLUDED_FILES = {"dot_config/rclone/gdrive-backup.env"}


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args])


def approved_predecessors(repository, source, revision):
    """Export only reviewed forward-transition IDs, never Git histories.

    A predecessor must be an OS-recorded gitlink and a Git ancestor of the new
    dotfiles pin. Missing shallow-clone objects are not guessed or fetched.
    """
    predecessors = set()
    commits = git(repository, "rev-list", "--max-count=256", "HEAD", "--", "dotfiles").decode().splitlines()
    for commit in commits:
        entry = git(repository, "ls-tree", commit, "--", "dotfiles").decode().split()
        if len(entry) != 4 or entry[:2] != ["160000", "commit"]:
            continue
        candidate = entry[2]
        if candidate == revision:
            continue
        result = subprocess.run(
            ["git", "-C", str(source), "merge-base", "--is-ancestor", candidate, revision],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        if result.returncode == 0:
            predecessors.add(candidate)
    return sorted(predecessors)


def stage(repository, buildroot):
    entry = git(repository, "ls-tree", "HEAD", "--", "dotfiles").decode().split()
    if len(entry) != 4 or entry[:2] != ["160000", "commit"] or entry[3] != "dotfiles":
        raise ValueError("HEAD must record a dotfiles gitlink")
    revision = entry[2]
    source = repository / "dotfiles"
    # Resolve the recorded object, not submodule HEAD or the live working tree.
    git(source, "cat-file", "-e", revision + "^{commit}")
    records = git(source, "ls-tree", "-rz", revision).split(b"\0")
    payload = []
    for record in filter(None, records):
        metadata, raw_path = record.split(b"\t", 1)
        mode, kind, object_id = metadata.decode().split()
        name = raw_path.decode()
        path = PurePosixPath(name)
        if path.parts[0] in EXCLUDED_ROOTS or name in EXCLUDED_FILES:
            continue
        if path.is_absolute() or ".." in path.parts or ".git" in path.parts:
            raise ValueError("Unsafe payload path")
        if kind != "blob" or mode not in {"100644", "100755", "120000"}:
            raise ValueError(f"Unsupported source entry: {name}")
        content = git(source, "cat-file", "blob", object_id)
        payload.append((name, mode, content))

    regular_paths = {name for name, mode, _ in payload if mode != "120000"}
    for name, mode, content in payload:
        if mode == "120000":
            link = content.decode()
            target = posixpath.normpath(posixpath.join(posixpath.dirname(name), link))
            if link.startswith("/") or target not in regular_paths:
                raise ValueError(f"Source symlink must refer to an included regular file: {name}")

    policy = {"version": 1, "revision": revision,
              "approved_predecessors": approved_predecessors(repository, source, revision)}
    destination = buildroot / "usr/share/personal-os/dotfiles"
    if destination.exists():
        raise ValueError("Refusing to overwrite an existing factory payload")
    destination.mkdir(parents=True)
    manifest = []
    for name, mode, content in payload:
        target = destination / "source" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if mode == "120000":
            target.symlink_to(content.decode())
        else:
            target.write_bytes(content)
            target.chmod(0o755 if mode == "100755" else 0o644)
        manifest.append({"path": name, "mode": mode,
                         "sha256": hashlib.sha256(content).hexdigest()})
    (destination / "revision").write_text(revision + "\n")
    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (destination / "policy.json").write_text(json.dumps(policy, indent=2) + "\n")
    return destination


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--buildroot", type=Path, required=True)
    args = parser.parse_args()
    stage(args.repository, args.buildroot)
