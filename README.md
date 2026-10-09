# Personal OS

A small, repository-defined OS using [ParticleOS](https://github.com/systemd/particleos)'s
mkosi, signed UKI/verity and systemd-sysupdate foundations. Two independent machines:

| Role | Purpose |
| --- | --- |
| **Services** (`mini-server-arch`) | Deliberately managed homelab services and persistent operational data; conventional operator account, no root SSH. |
| **Dev pod** (`dev-pod`) | Disposable product development/testing; agents may run as root, creating sandboxes only when useful. No operational services, personal data or durable secrets. |

The architectural decision is in `~/Products/meta-analysis/DECISIONS.md`; OS
implementation, approvals and evidence live in the [canonical charter](.clearhead/charters/mini-server.md).
Profiles share OS foundations, not account/configuration/workload prerequisites.
They cannot be combined. Chezmoi and personal dotfiles are optional.

## Inspect and test

```sh
scripts/mkosi-arch summary                           # Arch services role
scripts/mkosi-arch dev-pod summary                   # Disposable root-agent role
scripts/mkosi-arch dev-pod --profile=chezmoi summary  # Optional BYO dotfiles tool
scripts/mkosi-arch --profile=personal-dotfiles summary # Optional pinned snapshot
mkosi summary                                      # Retained Fedora 44 recipe
python3 -m unittest discover -s tests -v             # Offline tests, no target apply
```

Boot the dev pod (disposable keys in a private 0700 directory, removed afterwards). Pass all three
signing key pairs to the build (`--secure-boot-*`, `--sign-expected-pcr-*`, `--verity-*`), then:

```sh
scripts/mkosi-arch dev-pod --ephemeral=yes --ram=4G --cpus=4 --tpm=yes --vsock=no --firmware=uefi \
  --register=no --console=read-only --runtime-network=none vm -- \
  -nic user,model=virtio-net-pci,hostfwd=tcp:127.0.0.1:42222-:22 \
  -smbios "type=11,value=io.systemd.credential.binary:ssh.authorized_keys.root=$(base64 -w0 < key.pub)"
```

Run an agent there as root: install the harness under `/root`, allowing only its own postinstall
(`npm install -g --prefix /root/.local --allow-scripts=@anthropic-ai/claude-code @anthropic-ai/claude-code`), and
stream the token from 1Password into tmpfs, never onto argv or disk:
`op read op://<vault>/<item>/<field> | ssh pod 'umask 077; mkdir -p /run/agent; cat > /run/agent/claude.token'`.
Work arrives by `git push` from the desktop and leaves by `git fetch`. The one exception is the facilitator's
memory repo (`assistant`): a GitHub deploy key with write on that repo only (`gh repo deploy-key add --allow-write`),
its private half kept on the desktop and streamed into `/run/agent` after each boot, with GitHub's host key pinned
against `gh api /meta`'s fingerprint. Other repos refuse it.
ClearHead comes from its release, checked against the published digest:
`gh release download <tag> -R ClearHeadToDo-Devs/clearhead-core -p 'clearhead-x86_64-unknown-linux-gnu.tar.xz'`
into `/root/.local/bin`; the user-level queries (`~/.config/clearhead/queries`) are copied from the desktop.
Persistent sessions use shpool, installed at run time from its release after checking GitHub's published digest
(`gh api repos/shell-pool/shpool/releases/tags/<tag> --jq '.assets[].digest'`), then
`shpool attach -b -d <dir> -c "bash -c '. /root/.agent-env; claude; exec bash'" facilitator`. Attach from the
desktop with `ssh -p 42222 root@127.0.0.1 -t /root/.local/bin/shpool attach -f facilitator`.

The SMBIOS form is deliberate: mkosi's `--credential` splits a public key on whitespace. Vsock needs the
host's `vhost_vsock` module, which is not loaded on the desktop.

Inspect configuration before builds. The wrapper selects Arch before distro
fragment discovery; target/initrd/tools use the `2026/10/04` archive. Services
selects 65 direct packages; dev selects 61. Dev caches/outputs are separate from
services and Fedora. Arch has no npm/Cargo build hook or installed agent CLI.
Add only tools needed for a concrete task. Plain mkosi retains Fedora 44 and its
historical agent-build composition; it is not the next VM to boot.

**Evidence boundary:** the previous frozen Arch image passed isolated first boot,
credential-free reboot, key-only operator SSH/sudo, console password login,
rootless Podman, TPM root re-unlock, preserved identity/home edits, native services
and real container HTTP. Later temporary workloads produced Arch Island and a
synthetic Radicale calendar/contact bundle. All sessions ended with verified
owned cleanup; no VM is active. These passes belong to the old image, **not** the
new profile split. Dev-pod (2026-10-08): built unprivileged on the desktop with disposable keys and booted
in an ephemeral QEMU VM with a TPM: root SSH by key credential, password refused, `running` with no failed
units, encrypted btrfs root, verity `/usr`, network, clean poweroff. Keys removed afterwards.
Neither image is installed or installation-ready. Recovery/update/rollback/rescue,
real-data restore and application/schema compatibility remain unproven.

## Optional dotfiles

Neither role requires a dotfiles checkout or Git history to build. `chezmoi`
installs only the tool: bring your own source and explicitly init/review/apply
**on the target as the intended user**, never on the builder or this desktop.
Review hooks and role conditions first. Dev dotfiles must not introduce personal
secrets/data or operational services. Packages belong in the image, not immutable
OS package-install hooks.

`dotfiles/` is already a pinned Git submodule, not vendored OS code. The optional
`personal-dotfiles` profile includes chezmoi and exports only the gitlink committed
in OS `HEAD` to `/usr/share/personal-os/dotfiles`. The snapshot records its revision
and manifest, excludes histories/plans/caches/builds/known runtime credentials,
and never runs init/apply/hooks. Inspect any new pin for secrets before staging.
No implicit `--remote` advance; changing the staged pin requires an OS commit.
The current pin is `1338e50103645df922e1411a523edeaf709336d7` on
`personal-os-immutable-hooks`.

The unused custom source-merge/automatic-apply controller and transition policy
have been removed, not replaced with a plugin framework. There is no boot-time
apply or source reset. Configuration remains an explicit operator operation;
record the applied source revision and preserve local edits. OS rollback does
**not** restore mutable home or application state.

## Access and services

**Services:** `personal-os-account.service` enrolls the conventional operator from
protected runtime `personal-os.account.json` and `personal-os.console-password.hash`
credentials. No target user, password or home is created on the builder. The
account journal preserves password/key edits and safe retries; subordinate IDs
and linger choices remain stable. Enrollment grants access, not workload readiness.
SSH is key-only and disallows root. Production credentials come from 1Password,
not Git/image inputs; tests use fresh synthetic identities.

Automatic service configuration is not implemented. Workloads/shpool remain
disabled and service-specific drop-ins require
`/run/personal-os/configuration-ready`. Do not manufacture that marker: listener,
authentication and runtime inputs still need deliberate integration. Applying
optional dotfiles does not imply service readiness. Arch's temporary Radicale
container pass is not native image-service integration.

**Dev pod:** root SSH is public-key-only, with no operator account, sudo policy,
subid/linger enrollment or configuration gates. Use stock systemd's runtime
`ssh.authorized_keys.root` credential to provision a **public** management key;
its tmpfiles rule preserves an existing authorized_keys file. Root account/PAM
and credential handoff still need a booted pass. No access key is baked into the
image. Keep private keys and provider authentication on the controlling machine;
harvest results locally and push from there. No agent starts automatically.

Root privileges are inside the disposable dev machine, never this desktop.
Sandboxes are optional experiment tools; sandbox images are built here as
profiles, while agent-sandbox runs the sessions; do not invent a competing launcher. Shpool is session
tooling, not an isolation boundary. The shared signed `/usr` remains immutable;
root does not make pacman installation there supported. Use image packages or
containers for extra tools, and do not silently remove the immutable guards.

## Safety and repository map

Signing/PCR policy, coupled `/usr`/verity/UKI updates, TPM-encrypted Btrfs root/swap,
unencrypted Btrfs home and no-reset mutable partitions remain. Secure Boot keys
are not auto-enrolled. Production signing/recovery custody and installer/rescue
access remain unresolved. Explicit Arch has no SELinux; retained Fedora stays enforcing.
Only the normal signed UKI is built; inactive installer/debug/demo examples are
not supported rescue media.

Local source changes/builds and isolated synthetic VMs are approved within current
scope. Production disk writes/RAID/backups/installation, publishing, host package
or service changes and reboots need separate approval. Never expose host disks,
the external homed drive, management sockets or production identities to dev VMs.
Use disposable file-backed state, bounded resources, protected temporary access
and independently verified owned cleanup. Preserve successful/failed receipts;
the private recovery-harness draft stays parked.

| Path | Ownership |
| --- | --- |
| `mkosi.*`, `mkosi.extra/`, `mkosi.conf.d/` | OS foundations, distro packages, partition/update policy |
| `mkosi.profiles/mini-server{,-arch}/` | Services role and retained Fedora prototypes |
| `mkosi.profiles/dev-pod/` | Independent disposable root-agent role |
| `mkosi.profiles/{chezmoi,personal-dotfiles}/`, `dotfiles/` | Optional user configuration composition |
| `scripts/`, `tests/` | Build/staging helpers and offline regressions |
| `.clearhead/charters/mini-server.*` | Sole plan, decisions, evidence and handoff |
| `reference/`, `docs/PARTICLEOS-UPSTREAM.md` | Preserved alternatives/upstream provenance |

Use ClearHead from this root; `dotfiles/.clearhead/` is historical. ClearHead
release work belongs in `~/Products/platform`, not this task. Source remote:
`https://github.com/ca-mantis-shrimp/personal-os.git`; previous source pushes do not
authorize future publication. `LICENSE` and ParticleOS provenance remain intact.
