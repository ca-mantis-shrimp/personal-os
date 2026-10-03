# mini-server bootc reference

Retained alternative prototype and historical evidence. The preferred build path
is now the ParticleOS-derived profile in this repository; see the root README
and canonical charter. Completed bootc tests are not tests of the new profile.

This is the narrow, non-secret build context for `mini-travel-server`. Build it
from this directory. Never add credentials, SSH private keys, Tailscale state,
home-directory contents, or application data.

Intentions, task state, operator planning, approvals, and the next-agent handoff
live in [the project-local ClearHead charter](../../.clearhead/charters/mini-server.md).
This document records technical build/reference information and test results.

## Base image

The image uses Fedora bootc 44, pinned to the multi-architecture OCI index:

```text
quay.io/fedora/fedora-bootc:44@sha256:62e0fe047be7b9c00abab3911fc84f8a22b2b2e097a6ca76119ebe395a6da3bf
```

The pin was resolved on 2026-10-01. Fedora's lifecycle documentation was
rechecked on 2026-10-02: 44 and 43 are supported, and 45 is upcoming. The presence
of a 45 registry tag is not proof of a released/supported stable base. Keep 44.
The digest fixes the base input, but added RPMs still resolve from moving
repositories: this is not yet a bit-for-bit reproducible package build. Record
and review each resulting image digest; package/repository locking remains
separate release-workflow work.

Before refreshing it:

1. Check the [Fedora lifecycle](https://docs.fedoraproject.org/en-US/releases/lifecycle/)
   and [Fedora bootc documentation](https://docs.fedoraproject.org/en-US/bootc/).
2. Inspect the numbered tag and record its OCI index digest:
   `skopeo inspect --raw docker://quay.io/fedora/fedora-bootc:44 | sha256sum`.
3. Review package/configuration changes, update both `FROM` and this document,
   build, and complete the VM update/rollback tests.
4. Treat a change from Fedora 44 to 45 as a separately reviewed upgrade.

Tailscale uses its official stable Fedora repository. Its repo file is tracked
under `files/`; RPM and repository signature checks remain enabled.

## Current host inventory (read-only, 2026-10-01)

No host configuration, mounts, containers, or disks were changed.
See [the detailed data inventory](INVENTORY.md) for home/Git recovery risks,
namespace-aware container-volume sizes, and coverage limitations. Future operator
checks and migration gates are in the ClearHead charter, not this build context.

- `dab` is a conventional UID/GID 1000 account from NSS with `/home/dab` and
  `/bin/fish`; `homectl` has no home record for it.
- Required running system services appear to be SSH, Tailscale, Radicale, and
  `syncthing@dab`. Desktop services (LightDM, Bluetooth, Bolt, audio/session
  components) are not required for the target image.
- Radicale runs as `radicale`, uses `/var/lib/radicale`, and authenticates from
  `/etc/radicale/users` using htpasswd. Back up both paths, including ownership
  and SELinux labels. Collection contents could not be inspected without sudo.
- Syncthing state is under `/home/dab/.local/state/syncthing`. It has three
  send/receive folders: `~/gym`, `~/Documents/knowledge_base`, and
  `~/.local/share/clearhead`, shared with two remote devices. Preserve
  `config.xml`, `cert.pem`, and `key.pem`; never commit them.
- User services include an OpenTelemetry Collector using
  `~/.config/otelcol/config.yaml`, Neovim listening on all interfaces at port
  6666, and a vdirsyncer timer. Decide whether Neovim and vdirsyncer survive.
- Relevant listeners include SSH 22, Radicale 5232 (loopback), Syncthing 8384
  (loopback) and 22000/21027, Tailscale, OTLP 4317/4318, and Neovim 6666.
  OTLP and Radicale are also exposed through Tailscale. Recreate only deliberate
  exposure and do not expose Neovim publicly by default.
- The 954 GiB NVMe contains the live EFI, swap, and ext4 root filesystems. Two
  4 TB disks are unmounted; one has an ext4 filesystem. The owner confirms both
  are empty/available for storage; array creation still requires explicit approval.
- Passwordless sudo is unavailable. Root-owned/stopped containers, firewall
  rules, the complete Radicale state, and privileged disk details still require
  an administrator-assisted inventory.

### USB storage inspection

Read-only SSH inspection identified two equal-capacity 4 TB, 512-byte logical /
4096-byte physical sector drives:

- WD40EFPX-68C6CN0, serial `WD-WX22D55EMYVE`, WWN `0x50014ee2c187373e`;
- WD40EZAX-00C8UB0, serial `WD-WX52D847K1PS`, WWN `0x50014ee21684b72b`.

Both use UAS at 5 Gbit/s through the same VIA USB hub and NS-PCHDEDS19 dock.
The USB bridge serial is duplicated between bays; use drive ATA/WWN identifiers,
not the bridge serial or `/dev/sdX`, when selecting array members. No disconnect,
reset, or I/O error appeared in the filtered current-boot storage log. Operator
SMART reports supplied on 2026-10-02 show both drives as CMR with zero
reallocated/pending/uncorrectable sectors, zero CRC errors, and no logged errors.
Temperatures were 32/33 degrees C and power-on hours 2944/8615 respectively.
The USB bridge omits ATA status registers, so the reported health pass is only
attribute-based. No self-tests have been logged. The owner accepts that remaining
uncertainty for non-critical home storage and has chosen to skip extended tests;
they are optional rather than a setup gate. Approval/task state is in ClearHead.

`mdadm` and `smartctl` are installed on Arch. RAID1 is a proposed design, not an
existing array. Health checks and explicit disk-write approval must precede
creation. Shared USB/power infrastructure remains a common failure point, so
keep an independent copy of irreplaceable migration data.

### Backup blocker

The old weekly `rsync-usb-system-backup` job was **not an independent backup**:
`/mnt/fat32` was a directory on the live NVMe root, containing approximately
126 GiB and excluding `/home`. During owner-approved cleanup on 2026-10-02, the
owner disabled/stopped its timer and removed that directory. Read-only follow-up
verified it absent and the timer disabled/inactive. It is not a recovery source.

Required preservation candidates and ownership constraints are recorded in
[INVENTORY.md](INVENTORY.md). The actual backup manifest, restore-test choices,
and approvals are tracked in ClearHead.

## Expanded service image (2026-10-02)

Local tag `mini-server:services`, Docker image ID:

```text
sha256:dc35f7fcafcb6331f26979235242afb232bdc987cf4519c52fce7b3563f51d6a
```

This is an image/config ID, not a published registry manifest digest. Nothing
has been published or installed on the server.

- Adds Fedora `chezmoi`, fish, Neovim, `radicale3`, its SELinux policy and bcrypt
  backend, vdirsyncer, htpasswd tooling, restic, mdadm, smartmontools, ext4 and GPT
  tooling. Weak dependencies are disabled to avoid unnecessary desktop/developer
  packages. Radicale remains a native service rather than adding Quadlet overhead.
- Adds Collector contrib **0.162.0** at `/usr/bin/otelcol`, with reviewed upstream
  SHA256 pins for amd64 and arm64. The amd64 archive was downloaded and checked;
  arm64 has not been built/tested. SHA256 pinning provides artifact integrity,
  not a claim of independent signature/provenance verification.
- Keeps user units/configuration in chezmoi. Image user-unit drop-ins select the
  Collector binary and restrict Neovim to `127.0.0.1:6666`. Use an SSH tunnel for
  Neovim, e.g. `ssh -N -L 16666:127.0.0.1:6666 dab@SERVER`.
- SSH is key-only, root SSH login disabled. Sudo is passwordless **only for dab**;
  the account, SSH key and console-password hash are installation-time inputs.
- Radicale binds loopback, uses bcrypt htpasswd authentication supplied at
  `/etc/radicale/users`, and stores collections under
  `/var/lib/radicale/collections`. It is disabled by default and has a runtime-auth
  condition. Provision users as root:radicale, mode 0640, then apply SELinux labels.
- Syncthing, Radicale, user services and restic jobs are opt-in. No B2 key,
  repository password, identity, cloud enrollment or backup timer is included.
- `/usr/libexec/mini-server-storage-ready FS_UUID MD_UUID` is a root-run startup
  guard: it requires the actual `/srv/storage` mount, the exact UUIDs, writable
  ext4 and a healthy/idle md RAID1. Missing/incorrect/degraded storage is rejected.
  It does not assemble/mount storage or handle runtime mount loss by itself.
  Mount units, exact runtime UUIDs, stop dependencies and monitoring still need
  integration and booted tests. No fstab/array identity is fabricated in the image.

ClearHead is developed in the owner's `~/Products/platform` super-repo, not
obtained from an assumed published release. Its documented `scripts/startup`
installs both `clearhead` and `clearhead-lsp` from
`clearhead-core/crates/clearhead-cli` using `cargo install --locked --path`.
Run Cargo from the platform root so its `.cargo/config.toml` selects the pinned
sibling tree-sitter grammar. For a staging build, use an external Cargo target
and install root rather than replacing the desktop's existing binaries.

Read-only source inspection found platform commit
`e9aac6741f22df85bceb10c601764f856822fd3e`, clean/pinned `clearhead-core` at
`651ac2e55dedf0442a5853b8462ff8a95847b178` and `tree-sitter-actions` at
`65f3f4a67b92f6f5767ab827ba87cdd9cbd4466f`. The platform checkout was clean on the final check; earlier documentation/action
edits were committed externally during this read-only review. Its Rust/grammar
pins did not change and no platform files were modified by migration work.
Record source revisions,
compiler and binary checksums when staging an artifact; verify it runs in Fedora
before installation. No build or runtime compatibility pass is claimed yet.

The chezmoi vdirsyncer unit requires `%h/.cargo/bin/clearhead`. Its existing
`password.fetch` also requires reprovisioning the host-specific Radicale
credential from the external source; an old TPM-sealed file is not portable.
Do not enable vdirsyncer until that binary, credentials and mappings are ready.

### Container smoke tests

The expanded image passed `bootc container lint --fatal-warnings` (14 passed,
one skipped) and all **nine** tests in `tests/test_image.py`. From repository root:

```sh
docker build --network=host --pull=false \
  -f reference/bootc/Containerfile -t mini-server:services reference/bootc
docker run --rm --network=none --entrypoint python3 \
  --mount "type=bind,source=$PWD/reference/bootc/tests,target=/tests,readonly" \
  --mount "type=bind,source=$PWD/dotfiles/dot_config/otelcol/config.yaml,target=/otelcol-test.yaml,readonly" \
  mini-server:services /tests/test_image.py
```

Tests cover scoped passwordless sudo, effective SSH policy, absent-storage refusal,
no display managers/automatic workloads, Collector config plus synthetic OTLP
log ingestion, fresh isolated Syncthing identity generation, synthetic Radicale
VTODO create/read/application-restart persistence, and encrypted unattended local
restic backup/check/restore with modes, xattrs, hard links and symlinks. They use
only synthetic data and a container-local network; no cloud credentials or real
workload state. The narrow `.dockerignore` excludes tests/docs and unexpected
files from the OS build context.

### Alternative architecture under review

The owner pointed to `~/Experiments/particleos`, inspected at commit
`e55d7a95e3b9da8a2291ca17b7327b204f2c5a56`. It is a mkosi-built image with signed,
verity-protected EROFS `/usr`, sysupdate transfer definitions and versioned UKIs
configured with three boot tries and two retained instances. Those definitions
are evidence of intended update/rollback mechanisms, not a tested recovery pass.

The inspected defaults select Fedora **rawhide**, require Secure Boot signing,
create a TPM-encrypted Btrfs root and Btrfs home, enable homed-firstboot, and
reshape much of `/etc` through `/usr` symlinks. Its README explicitly warns of
ongoing development and no backwards-compatibility guarantees, and recommends
mkosi main; local mkosi is 27.1. Enforcing SELinux operation for our services is
not established by this review. It was not built, booted, signed or installed.

A disk image is an installation artifact, not a complete update strategy.
Bootc can also produce single-disk images; mkosi/DDI with sysupdate is a distinct
ongoing update/configuration model. Architecture deliberation/approval remains
in the charter; neither adoption nor rejection of mkosi follows from these defaults.

### Initial VM-builder blocker and subsequent reboot

An isolated QCOW2 build was attempted using the previously tested builder digest.
This desktop runs `7.2.8-arch1-1` but has modules for `7.2.8-arch1-2`; the loop
control device cannot be opened (`ENODEV`). Docker bridge networking also fails
with unsupported veth creation, so builds used host networking without running
workload listeners. The builder's `--in-vm` fallback stalled before its image
pipeline made progress and was stopped after 15 minutes.

The builder's original repository/documentation is now deprecated in favor of
[osbuild/image-builder](https://github.com/osbuild/image-builder). The owner then
rebooted the desktop: running kernel and modules now both `7.2.8-arch1-2`, and an
isolated privileged builder successfully opens loop-control without allocation.
The agent did not reboot or repair the host. Further builds are paused for
architecture review. Reassess the builder version when resuming.
No booted validation of the new
service image, enforcing-SELinux workloads, console recovery, healthy/degraded
RAID, mount-loss handling, network-loss or update/rollback is claimed. The earlier
minimal-image VM results below remain historical evidence only.

All disposable builder storage, manifests, configuration, test SSH keys/passwords
and artifacts were removed; no test VM, builder or registry is running. Only the
local image tags are retained. Production installation remains unapproved.

## Build and inspect

The initial image was built on 2026-10-01. All listed packages resolved, the four
host services were enabled, and `bootc container lint --fatal-warnings` passed
(14 checks passed, one inapplicable check skipped). The VM results below validate
basic bootability, but not the complete migration procedure.

The retained local Docker tag is `mini-server:validation`, image digest:

```text
sha256:20261f8f7feb049d490582476e6c1688efa46b6d243a0ee8058b4575ca2f4e0b
```

Use rootful Podman on an SELinux-capable Fedora builder:

```sh
cd reference/bootc
sudo podman build --pull=never -t localhost/mini-server:dev .
sudo podman run --rm localhost/mini-server:dev bootc container lint
sudo podman history --no-trunc localhost/mini-server:dev
```

`--pull=never` enforces use of the already reviewed digest. Pull that exact base
explicitly first when refreshing the local cache. Review image history and a
saved-image file listing before publishing. The initial registry, trust policy,
and release naming scheme are still undecided, so this image must not yet be
published or deployed.

## Accounts and first access

The image deliberately contains no `dab` account or authorized key. Supply the
UID/GID 1000 account and a public SSH key through an untracked
`bootc-image-builder` installation config (or another reviewed first-boot
mechanism). Keep its config outside this repository if it contains a password
hash or identifying key. Put `dab` in wheel; the image's account-scoped sudoers
rule supplies passwordless sudo. Supply a hash for a typable console passphrase
stored in 1Password: passwordless sudo does not eliminate console recovery login.
Never put plaintext passwords or password hashes in Git or build logs.

After first boot, enroll Tailscale interactively with `tailscale up`; never use
an auth key in the image. Generate a fresh Syncthing identity, pair with the
prepared desktop and seed the selected folders while protecting its data;
no production identity is copied into tests. Provision/rebuild required Radicale
data with its service stopped and apply correct ownership and SELinux labels
(`restorecon -RFv` on restored paths). The owner's actual retention/source-of-truth
decisions are in the charter, not inferred from the old inventory.

## VM validation results (2026-10-01)

A disposable 10 GiB XFS QCOW2 was generated with `bootc-image-builder` and
booted under QEMU/KVM with UEFI firmware, 2 GiB RAM, and two virtual CPUs. The
builder needed `--rootfs xfs` because this Fedora base does not declare a default
root filesystem. The tested builder image was:

```text
quay.io/centos-bootc/bootc-image-builder@sha256:2b52843ea2bfda73b0a08d97e76b734393b1d3a804681b9fabb26723bd3a2f0b
```

It used a separately populated Podman storage directory and an untracked
installation config. The builder printed overlay-unmount and compiled-SELinux
regex-version warnings, but installation completed and the guest booted with
SELinux enforcing.

Passed:

- UEFI boot, DHCP networking, SSH public-key login, UID/GID 1000 `dab`, and sudo
  using the untracked installation-time password hash;
- SELinux enforcing, rootless Podman using overlayfs, firewalld allowing SSH, and
  no failed systemd units;
- active NetworkManager, firewalld, sshd, and tailscaled services;
- installed Syncthing and Tailscale binaries, with Tailscale intentionally logged
  out and no production identity copied;
- persistence across an ordinary reboot: `/home` is a link to `/var/home`, and
  the test file under `/var/home/dab` survived;
- `bootc switch` to a second image, reboot into that deployment, and verification
  of its immutable `/usr` marker;
- `bootc rollback`, reboot back to the original digest, and removal of the second
  image's marker; and
- preservation of both `/var/home` data and a local `/etc` override across the
  update and rollback.

Still untested: Tailscale enrollment, restored Radicale/Syncthing data, workload
containers, `/etc` merge conflicts, network-loss recovery, and application data
rollback. The VM used only synthetic state and a newly generated test password;
no mini-server identity or application data was copied.

The disposable VM, disk files, temporary password/config, local registry, and
update test tag were removed. No test VM or registry remains running; only the
validated base tag is retained. No production identity or data was copied.

For future approved test procedures, use the current
[`bootc-image-builder` documentation](https://osbuild.org/docs/bootc/). Remaining
validation actions and deployment/recovery gates live in the ClearHead charter
and actions; past test success is not approval for further operations.
