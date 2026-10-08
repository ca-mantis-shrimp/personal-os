#!/usr/bin/env python3
"""Stage only stock-labeled root metadata for first-creation repart population.

Fedora runs after strict target relabeling. The explicit Arch variant stages
Unix metadata only and refuses SELinux payloads; it cannot bypass Fedora labels.
Never copy accounts, machine identity, policy binaries or mutable builder state.
"""
import argparse
import os
import shlex
import shutil
import stat
from pathlib import Path

TEMPLATE = Path("usr/share/factory/root")
PUBLIC_DIRECTORIES = ("usr", "usr/bin", "usr/lib", "usr/libexec", "usr/share")
USR_LINKS = {"bin": "usr/bin", "sbin": "usr/sbin", "lib": "usr/lib", "lib64": "usr/lib64"}
# Match stock Arch filesystem: neither a separate sbin/lib64 nor libexec is required.
ARCH_PUBLIC_DIRECTORIES = ("usr", "usr/bin", "usr/lib", "usr/share")
ARCH_USR_LINKS = {"bin": "usr/bin", "sbin": "usr/bin", "lib": "usr/lib", "lib64": "usr/lib"}
POLICY_LINK = "/usr/share/factory/etc/selinux"


def stage(buildroot: Path, *, distribution: str = "fedora") -> Path:
    if distribution not in ("fedora", "arch"):
        raise ValueError("Unsupported bootstrap distribution")
    root = buildroot.resolve(strict=True)
    if root == Path("/"):
        raise ValueError("Refusing to stage against the running host root")
    if distribution == "arch":
        release = root / "usr/lib/os-release"
        if (release.is_symlink() or not release.is_file()
                or not release.resolve().is_relative_to(root)
                or release.stat().st_size > 16384):
            raise ValueError("Arch metadata requires an in-image os-release")
        ids = [shlex.split(line.partition("=")[2])
               for line in release.read_text().splitlines()
               if line.partition("=")[0] == "ID"]
        if ids != [["arch"]]:
            raise ValueError("Arch metadata requires the actual Arch target identity")
        for name in ("etc/selinux", "usr/share/factory/etc/selinux"):
            path = root / name
            if path.exists() or path.is_symlink():
                raise ValueError("Unexpected SELinux payload in the Arch variant")
    links = ARCH_USR_LINKS if distribution == "arch" else USR_LINKS
    directories = ARCH_PUBLIC_DIRECTORIES if distribution == "arch" else PUBLIC_DIRECTORIES
    # A private checkout umask must not become permissions in the public OS tree.
    for name in directories:
        directory = root / name
        if directory.is_symlink() or not directory.is_dir():
            raise ValueError("Expected a real public image directory: " + name)
        if stat.S_IMODE(directory.stat().st_mode) & 0o005 != 0o005:
            raise ValueError("Public image directory is not readable/searchable: " + name)
    factory = root / TEMPLATE.parent
    if factory.is_symlink() or not factory.is_dir() or not factory.resolve().is_relative_to(root):
        raise ValueError("Expected an in-image factory directory")
    template = root / TEMPLATE
    # Fail closed on an unexpected existing object rather than overwriting it.
    if template.exists() or template.is_symlink():
        raise FileExistsError("Root metadata template already exists")

    # Read all reference labels before writing anything. mkosi's strict relabel
    # has already mapped these paths using the target's stock policy.
    references = {".": root, "etc": root / "etc"}
    if distribution == "fedora":
        references["etc/selinux"] = root / "etc/selinux"
    for name, target in links.items():
        source = root / name
        if not source.is_symlink() or os.readlink(source) != target:
            raise ValueError("Unexpected image usr-merge link: " + name)
        references[name] = source
    labels = {}
    if distribution == "fedora":
        for name, source in references.items():
            label = os.getxattr(source, "security.selinux", follow_symlinks=False)
            if not label.startswith(b"system_u:object_r:") or b":unlabeled_t:" in label:
                raise ValueError("Missing stock reference label: " + name)
            labels[name] = label

    template.mkdir(mode=0o755)
    try:
        (template / "etc").mkdir(mode=0o755)
        for name, target in links.items():
            (template / name).symlink_to(target)
        if distribution == "fedora":
            (template / "etc/selinux").symlink_to(POLICY_LINK)
        for name in (".", "etc"):
            os.chmod(template / name, 0o755)
        for name, source in references.items():
            path = template / name
            # Match the image's own ownership rather than assuming uid 0 is
            # mapped: an unprivileged build's finalize namespace may not map it.
            owner = os.lstat(source)
            os.chown(path, owner.st_uid, owner.st_gid, follow_symlinks=False)
            if distribution == "fedora":
                # Copy stock labels only. Any write/verification failure aborts.
                os.setxattr(path, "security.selinux", labels[name], follow_symlinks=False)
                if os.getxattr(path, "security.selinux", follow_symlinks=False) != labels[name]:
                    raise RuntimeError("Root template label verification failed: " + name)
    except BaseException:
        shutil.rmtree(template)
        raise
    return template


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--buildroot", type=Path, required=True)
    parser.add_argument("--distribution", choices=("fedora", "arch"), default="fedora")
    args = parser.parse_args()
    stage(args.buildroot, distribution=args.distribution)
    kind = "stock-labeled" if args.distribution == "fedora" else "Arch Unix-metadata"
    print(f"Staged metadata-only {kind} root template; no mutable state copied.")


if __name__ == "__main__":
    main()
