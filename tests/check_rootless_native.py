#!/usr/bin/env python3
"""Opt-in native Shadow/libsubid bridge in a disposable Fedora container.

Run: python3 tests/check_rootless_native.py
No host account operations, container privilege/SELinux exceptions, or network.
This is NOT a booted Fedora/SELinux/Podman namespace/shpool/logind test.
"""
from pathlib import Path
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
IMAGE = "quay.io/fedora/fedora-bootc:44@sha256:62e0fe047be7b9c00abab3911fc84f8a22b2b2e097a6ca76119ebe395a6da3bf"
OVERLAY = ROOT / "mkosi.profiles/mini-server/mkosi.extra"


def inside():
    if os.geteuid() != 0 or not Path("/.dockerenv").is_file() or not Path("/test/personal-os-account").is_file():
        raise RuntimeError("Native fixture must run only inside the disposable container")
    namespace = {"__name__": "account_native_test"}
    path = Path("/test/personal-os-account")
    exec(compile(path.read_bytes(), str(path), "exec"), namespace)
    B = namespace["Backend"]
    config = {"username": "synthetic", "uid": 1000, "gid": 1000}
    B.run(["groupadd", "--gid", "1000", "synthetic"])
    B.run(["useradd", "--uid", "1000", "--gid", "1000", "--no-create-home", "--no-user-group",
           "--no-log-init", "--key", "SUB_UID_COUNT=0", "--key", "SUB_GID_COUNT=0", "synthetic"])

    class Backend(B):
        @staticmethod
        def run(args, input=None):
            if args[0] == "loginctl":
                # No systemd/logind here: only this RPC is mocked.
                marker = Path("/var/lib/systemd/linger/synthetic")
                marker.parent.mkdir(parents=True, exist_ok=True)
                marker.touch(mode=0o644)
            else:
                B.run(args, input=input)

    # Synthetic protected state hierarchy; bootc's pre-existing /var/lib is
    # group-writable. This does not prove the actual target's first-boot layout.
    Path("/var/lib").chmod(0o755)
    Path("/var/lib/personal-os").mkdir(mode=0o700, exist_ok=True)
    files = namespace["Files"](Path("/"), config)
    namespace["rootless_enrollment"](files, Backend())
    for args in (["getsubids", "synthetic"], ["getsubids", "-g", "synthetic"]):
        result = subprocess.run(args, check=True, capture_output=True, text=True, timeout=10)
        assert "100000 65536" in result.stdout, "Native libsubid did not read the allocated block"
    B.run(["useradd", "--uid", "1001", "--gid", "1000", "--no-create-home", "--no-user-group",
           "--no-log-init", "--key", "SUB_UID_COUNT=0", "--key", "SUB_GID_COUNT=0", "lockprobe"])
    command = ["usermod", "--add-subuids", "1000000-1065535", "lockprobe"]
    with namespace["subid_locks"](files):
        result = subprocess.run(command, capture_output=True, timeout=20)
        assert result.returncode != 0 and b"lock /etc/subuid" in result.stderr, "Shadow failed to honor the shared PID lock"
    # Positive control: the same native operation succeeds without our lock.
    B.run(command)
    namespace["rootless_enrollment"](files, Backend())
    for kind in ("subuid", "subgid"):
        assert Path("/etc/" + kind).read_text().count("synthetic:") == 1
    assert not Path("/var/spool/mail/synthetic").exists(), "useradd default did not suppress mail spool"
    print("Fedora native useradd, libsubid/getsubids and Shadow lock interoperability: OK (logind mocked)")


def main():
    if sys.argv[1:] == ["--inside"]:
        inside()
        return
    if sys.argv[1:]:
        raise SystemExit("Usage: python3 tests/check_rootless_native.py")
    args = ["docker", "run", "--rm", "--pull=never", "--network=none", "--cap-drop=ALL",
            "--cap-add=CHOWN", "--cap-add=DAC_OVERRIDE", "--security-opt=no-new-privileges"]
    # Only public source/default/fixture mounts, all read-only; no host homes,
    # runtime secrets, engine sockets, signing material or user storage.
    for source, destination in ((OVERLAY / "usr/libexec/personal-os-account", "/test/personal-os-account"),
                                (OVERLAY / "usr/share/factory/etc/default/useradd", "/etc/default/useradd"),
                                (Path(__file__).resolve(), "/test/check_rootless_native.py")):
        args += ["--mount", f"type=bind,source={source},target={destination},readonly"]
    args += ["--entrypoint=python3", IMAGE, "/test/check_rootless_native.py", "--inside"]
    subprocess.run(args, check=True, timeout=60)


if __name__ == "__main__":
    main()
