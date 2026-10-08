#!/usr/bin/env python3
"""Opt-in native account bridge inside a disposable, networkless Arch container.

Usage: python3 tests/check_account_native_arch.py --inside
The caller supplies a reviewed/pinned image with Python, Shadow, sudo and SSH.
Only hostnamectl/logind RPCs are mocked. No boot/PAM-login/rootless namespace pass.
"""
import base64
import ctypes
import importlib.machinery
import importlib.util
import json
import os
import secrets
import struct
import subprocess
import sys
from pathlib import Path


def inside():
    helper = Path('/test/personal-os-account')
    if (os.geteuid() != 0 or not Path('/.dockerenv').is_file()
            or not helper.is_file() or 'ID=arch' not in Path('/usr/lib/os-release').read_text()):
        raise RuntimeError('Native bridge requires the disposable Arch container')
    loader = importlib.machinery.SourceFileLoader('native_account', str(helper))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    if spec is None:
        raise RuntimeError('Cannot load the reviewed account helper')
    account = importlib.util.module_from_spec(spec)
    loader.exec_module(account)

    class Backend(account.Backend):
        host = 'unconfigured'
        commands = []

        def hostname(self):
            return self.host

        def run(self, args, input=None):
            self.commands.append(args[0])  # Never retain secret stdin.
            if args[0] == 'hostnamectl':
                self.host = args[-1]
            elif args[0] == 'loginctl':
                marker = Path('/var/lib/systemd/linger/synthetic')
                marker.parent.mkdir(parents=True, exist_ok=True)
                marker.touch(mode=0o644)
            elif args[0] == 'restorecon':
                raise RuntimeError('Arch adapter attempted a Fedora relabel')
            else:
                super().run(args, input=input)

    library = ctypes.CDLL('libcrypt.so.2')
    library.crypt.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    library.crypt.restype = ctypes.c_char_p
    hashed = library.crypt(secrets.token_bytes(32).hex().encode(),
                           ('$6$' + secrets.token_hex(8) + '$').encode())
    if not hashed or hashed.startswith(b'*'):
        raise RuntimeError('Native hash generation failed')
    blob = b''.join(struct.pack('>I', len(field)) + field
                    for field in (b'ssh-ed25519', secrets.token_bytes(32)))
    public = 'ssh-ed25519 ' + base64.b64encode(blob).decode() + ' synthetic-test'
    config = {'version': 1, 'username': 'synthetic', 'uid': 1000, 'gid': 1000,
              'hostname': 'synthetic-server', 'shell': '/usr/bin/bash',
              'ssh_public_keys': [public], 'passwordless_sudo': True}
    # Ensure the fixture itself did not pre-create the enrollment identity.
    if account.Backend.lookup('user', 'synthetic') is not None:
        raise RuntimeError('Fixture identity already exists')
    backend = Backend()
    enrolled = account.provision(Path('/'), json.dumps(config).encode(), hashed, backend)
    account.publish_context(Path('/'), enrolled)
    if account.Backend.lookup('user', 'synthetic').pw_uid != 1000:
        raise RuntimeError('Native enrollment failed')
    for args in (['getsubids', 'synthetic'], ['getsubids', '-g', 'synthetic']):
        result = subprocess.run(args, check=True, capture_output=True, timeout=10)
        if b'100000 65536' not in result.stdout:
            raise RuntimeError('Native libsubid mapping check failed')
    if Path('/var/spool/mail/synthetic').exists():
        raise RuntimeError('Native useradd mail suppression failed')
    keys = Path('/home/synthetic/.ssh/authorized_keys')
    if keys.stat().st_mode & 0o777 != 0o600:
        raise RuntimeError('Unsafe SSH key file mode')
    shadow = Path('/etc/shadow').read_bytes()
    if b'synthetic:' + hashed + b':' not in shadow:
        raise RuntimeError('Native encrypted password enrollment failed')
    if hashed in Path('/var/lib/personal-os/account.json').read_bytes():
        raise RuntimeError('Journal contains a password hash')
    # Completed boots need no inputs and preserve edited access keys/passwords.
    keys.write_text(public + ' edited\n')
    before = keys.read_bytes()
    backend.commands.clear()
    account.provision(Path('/'), None, None, backend)
    if backend.commands or keys.read_bytes() != before or Path('/etc/shadow').read_bytes() != shadow:
        raise RuntimeError('Repeat enrollment did not preserve mutable access state')
    # Native Shadow must honor our common PID locks. This second identity is a
    # lock fixture only, never a manually pre-created enrollment bypass.
    account.Backend.run(['useradd', '--uid', '1001', '--gid', '1000', '--no-create-home',
                         '--no-user-group', '--no-log-init', '--key', 'SUB_UID_COUNT=0',
                         '--key', 'SUB_GID_COUNT=0', 'lockprobe'])
    files = account.Files(Path('/'), config)
    command = ['usermod', '--add-subuids', '1000000-1065535', 'lockprobe']
    with account.subid_locks(files):
        result = subprocess.run(command, capture_output=True, timeout=20)
        if result.returncode == 0 or b'lock /etc/subuid' not in result.stderr:
            raise RuntimeError('Native Shadow ignored shared locks')
    account.Backend.run(command)  # Positive unlocked control.
    account.provision(Path('/'), None, None, backend)
    print('Native Arch enrollment/hash/visudo/libsubid/repeat/Shadow-lock checks: OK; hostname/logind mocked.')


if __name__ == '__main__':
    if sys.argv[1:] != ['--inside']:
        raise SystemExit('Run only with --inside in the disposable Arch fixture')
    inside()
