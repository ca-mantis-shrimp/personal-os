# Personal OS

A purpose-built, repository-defined OS for personal machines, starting with the
headless `mini-travel-server`. This is a local fork of
[systemd/particleos](https://github.com/systemd/particleos), not a new image/update
implementation written from scratch.

**Status: trimmed Fedora server fork with unbooted prototypes. Not ready to install.**
The server profile exports committed dotfiles into the factory image and has
target-only conventional-account and chezmoi lifecycle prototypes. Automatic
first-boot integration, workload readiness and production storage/signing/recovery
policy are not complete or boot-validated yet.

## The design

- Retain ParticleOS's mkosi/DDI, partition, UKI and systemd-sysupdate machinery.
- Use a small, stable Fedora headless profile, rather than rawhide/desktop defaults.
- Pin this OS repository and the `dotfiles/` chezmoi submodule together.
- Build stages the committed dotfiles source and chezmoi executable. It does
  **not** initialize/apply chezmoi or run its hooks on the build machine.
- On the installed target, provision the account, hostname and mutable home;
  then initialize/apply chezmoi automatically as that user. Its normal machine,
  distro and profile conditions evaluate on the real target.
- Enable dependent workloads only after their configuration and runtime inputs
  are ready. Define deliberate behavior when the pinned dotfiles revision changes;
  do not force-reset edits or blindly overwrite user files on every boot.
- Keep secrets, credentials, signing private keys and device identities out of
  committed source and OS images. Target-side application must not copy local
  development histories, build outputs or credential state into the image.

The intended result is one reproducible source composition that boots into the
owner's configured environment, without a manual dotfiles setup phase. The image
owns OS package installation; target-side chezmoi hooks must not try to mutate
immutable `/usr`. Automatic dotfile application does not eliminate the initial
runtime credential/enrollment step.

OS rollback restores the OS/factory-source version, **not** mutable home files or
application data. Configuration/schema compatibility and separate state restores
must be tested; do not treat image rollback as a backup.

Pinning Git inputs alone does not pin moving package repositories or the builder;
those also need a recorded, reviewed build/release policy.

## Minimal fork boundary

The active recipe is Fedora 44 plus `mini-server`, with a Fedora 44 tools tree
and no graphical VM tools profile. Personal OS owns package selection, visible
branding and boot policy; ParticleOS remains the provenance of the integrated
partition/UKI/verity/sysupdate design. This is purpose-minimal, not an empty OS:
requested server workloads, recovery tools and image-pinned agent CLIs remain.
Explicit target RPM selections are now 98 (originally 124), including the core
Podman/rootless stack. Starship is a pinned source-built tool because Fedora 44
has no matching RPM. A first pre-Podman candidate built successfully; the latest
rootless/account changes still require a fresh build and boot test.

Unused desktop, other-distro, OBS repository/update and network-boot examples,
all eight inherited extra UKI profiles, the demo homed credential and upstream
OBS workflow/TODO now live under `reference/particleos/`, outside mkosi discovery.
They are not staged or supported install instructions. The normal signed UKI is
currently the only boot profile: no demo password/autologin, public storage-target
mode, factory-reset/TPM-clear mode or secret-bearing debug-console logging.
**Removing those examples does not provide replacement installer/rescue media.**
A reviewed credential handoff and boot-tested independent rescue path remain gates.

Artifact identity is `PersonalOS`; partition labels, discovery filters and
sysupdate patterns remain coupled through that identity. No deployed image exists
to migrate from the former `ParticleOS` labels. Versioned builds must set an image
version; an unversioned summary can emit `%v` warnings. Visible branding changes
while Fedora `ID`/version and the `particleos-fedora` ancestry token stay intact
for the pinned chezmoi immutable guards; no submodule update is needed.

Auditing and enforcing SELinux are explicit, relabel errors fail the build, weak
RPM dependencies are disabled, and Secure Boot auto-enrollment is disabled.
Signing/PCR signatures remain required; production key custody is not settled.
Mutable root/home/swap partitions are no longer factory-reset candidates. The
inherited TPM-encrypted Btrfs root/swap and unencrypted Btrfs home layout is retained
pending recovery review, not claimed as the final validated storage design.

## Repository map

| Path | Purpose |
| --- | --- |
| `mkosi.*`, `mkosi.extra/` | Fork-owned minimal Fedora base and retained coupled build/update machinery |
| `mkosi.profiles/mini-server/` | Server account/configuration/workload and agent-tool overlay |
| `dotfiles/` | Pinned chezmoi source submodule, not a place for OS build logic |
| `.clearhead/charters/mini-server.md` | Canonical intent, decisions, approvals and next-agent handoff |
| `.clearhead/charters/mini-server.actions` | Active execution tracking (`+human` identifies owner tasks) |
| `reference/bootc/` | Retained alternative prototype, inventory and test evidence—not the chosen build path |
| `reference/particleos/` | Inactive upstream examples removed from build discovery, not a second plan |
| `docs/PARTICLEOS-UPSTREAM.md` | Original upstream README, preserved for reference |
| `AGENTS.md` | Start here before editing or testing |

## Start the next session here

```sh
cd ~/Products/personal-os
# Read AGENTS.md, then the mini-server charter and its paired actions.
clearhead show charter mini-server
clearhead read actions --charter mini-server --open-only --format ids
git status --short
git submodule status
```

For another checkout, initialize submodules at the revisions recorded by the OS
repo with `git submodule update --init --recursive`. Never use `--remote` as an
implicit upgrade. The authoritative plan/handoff is the charter; do not add a
second PLAN or NEXT-STEPS file.

The default configuration selects `mini-server` and Fedora 44 for both target
and tools tree. Other distro/profile examples are inactive reference material.
Configuration inspection and offline smoke tests (not builds/installations):

```sh
mkosi summary
python3 -m unittest discover -s tests -v
```

These checks cover configuration selection, synthetic source staging/rendering
and account/source-lifecycle logic with fake command/NSS/chezmoi backends, plus
isolated sudoers syntax and unit verification. Lifecycle tests never run real
chezmoi init/apply. They do not establish package availability, actual account
commands on Fedora, a booted SELinux pass or a working first-boot lifecycle.

The profile finalize hook calls `scripts/stage-dotfiles.py` to export the gitlink
recorded in OS `HEAD` into `/usr/share/personal-os/dotfiles/source`, with a revision
file, per-entry SHA-256 manifest and forward-transition policy. The policy contains
only previous OS-recorded dotfiles pins proved ancestors of the new pin (bounded
to 256 pin-changing OS commits); no Git history objects are exported. Missing
shallow-clone ancestry is not guessed or fetched. Working-tree changes and an advanced submodule
HEAD are not exported. Historical plans, archived/build trees and the committed
rclone runtime environment file are excluded; internal source symlinks must point
to included regular files. No chezmoi command runs during staging. The 115-entry
current payload has passed a disposable local export and synthetic Fedora target
rendering (archive only, never apply). A limited secret-indicator review found no
private-key blocks in the exported payload; this is not a credential-free proof
or a booted target pass. The package hook is now restricted to mutable Arch,
with immutable environment/branding/marker guards. Retired rclone targets are
ignored on immutable systems. Account provisioning and fail-closed workload
ordering still need booted validation and completion before automatic target-side
application. Changes to the gitlink must be committed in the OS repo to change the exported pin.

The server **still retains** upstream Secure Boot/PCR signing, TPM-encrypted
Btrfs root/swap and unencrypted Btrfs home. Homed/homed-firstboot are masked;
PAM uses conventional accounts and no demo credentials or extra UKI profiles are
loaded. Storage, production signing/enrollment and replacement installer/rescue
access must still be deliberately reviewed and VM-tested before installation.
All 119 unit tests are offline evidence, including effective configuration,
fork branding, retained immutable guards and synthetic target archive rendering.
Separately, a pre-Podman candidate built in an enforcing Fedora VM: 310 runtime
RPMs, no Rust/Cargo/GCC, a verified signed UKI and strict relabel pass; raw disk
2,189,987,840 bytes logical / about 732.7 MiB allocated. See the charter for
provenance and limits. This is not a target boot/recovery/update/SELinux pass;
latest rootless changes are not included in that artifact.

## Target account enrollment prototype

`mini-server` supplies `personal-os-account.service` and a target-only helper.
Image builds and offline unit tests never create a host/target user. The enrollment layer embeds no
selected username, access key or console hash: it reads systemd credentials named
`personal-os.account.json` and `personal-os.console-password.hash` from the runtime
manager/credential stores. For an approved installed-target or isolated VM setup,
keep input files outside Git/images, in root-owned protected credential storage
(e.g. `/etc/credstore`, mode 0700; files mode 0600). The installer-to-credential-store
integration still needs validation; do not manually pre-create the user, which
would be rejected as an untracked existing identity.

The account JSON must contain exactly these fields (public-key placeholder must
be replaced in the protected runtime input, not in this README):

```json
{
  "version": 1,
  "username": "dab",
  "uid": 1000,
  "gid": 1000,
  "hostname": "mini-travel-server",
  "shell": "/usr/bin/bash",
  "ssh_public_keys": ["<desktop SSH public key>"],
  "passwordless_sudo": true
}
```

The separate console credential contains a nonempty yescrypt or SHA-512 crypt
hash provisioned securely from the approved 1Password passphrase. Do not put its
value in shell arguments, chat, logs, this repository or image build inputs.
The helper passes it to `chpasswd --encrypted` through stdin only.

Enrollment creates a conventional primary group/account, wheel membership,
`/home/<username>`, `.ssh/authorized_keys` and a user-specific sudoers rule. It sets
the actual hostname before allowing the SSH daemon or user manager to start.
Remote SSH is key-only; the passphrase is for console recovery. Existing home
contents are not recursively chowned or removed. Identity collisions, symlinked
paths and divergent initial access-policy files fail rather than being adopted
or overwritten. A root-owned journal at `/var/lib/personal-os/account.json`
records pending/completed enrollment without the password/hash. It allows retries
and subsequent boots without the original credentials; completed enrollment
preserves edited authorized keys and passwords. Identity, hostname, protected
path or sudo-policy changes require operator review rather than implicit repair.
Do not delete the journal to force adoption or reset an established account.
After success, enrollment publishes only username/UID/GID/hostname and schema
version to root-owned `/run/personal-os/account-context.json`; no key/hash or
workload-ready marker is published.

Workload drop-ins currently require `/run/personal-os/chezmoi-ready`. Account
success **does not** create that marker, so account readiness alone cannot start
the Collector, Neovim, Syncthing, Radicale or calendar jobs. These are startup
guards only, not runtime stop/recovery handling. The future chezmoi lifecycle must
validate its pinned revision and runtime inputs, stop dependents on failed apply,
and manage readiness deliberately; do not touch the marker to bypass that work.
No real SSH/console/sudo, SELinux, update or rollback pass is claimed.

## Target configuration lifecycle prototype

The profile stages `/usr/libexec/personal-os-chezmoi` and a root-side
`personal-os-configuration.service`, but **its preset explicitly disables startup**. Its CLI refuses root/builders, other users/profiles, incomplete
account enrollment and non-enforcing SELinux. Actual target NSS/home, hostname
and OS context drive chezmoi; no builder identity or template-data override is used.

The helper verifies factory contents against the manifest, then maintains the
user's writable `~/.local/share/chezmoi` and private
`~/.local/state/personal-os/chezmoi.json`. Three-way comparison against the prior
factory baseline promotes unedited paths, preserves unrelated edits/deletions,
untracked files and Git metadata, and rejects conflicting edits before promotion.
It never resets a checkout, recursively deletes directories or adopts an existing
untracked source. Interrupted per-file promotion can retry; a private lock prevents
parallel helper invocations. Coordinate manual editing during apply: this is not
a whole-home transaction or a substitute for backups.

Chezmoi generates configuration on the target into a private candidate. Divergent
local config edits block replacement and retain the candidate for review. Apply
uses `--less-interactive --error-on-conflict --force=false` and a dry-run preflight;
pre-existing/edited targets must not be silently overwritten, including unmanaged
files in exact directories. Command output is captured, not logged. Immutable and
legacy container package-hook guards are set; other target template identity is
real. No secrets are skipped to manufacture success.

The applied revision/context is recorded only after full apply succeeds. Same
pin/context boots do not blindly reapply. A target-context change requests another
conflict-checked apply. Different pins require a forward ancestry allowlist entry;
older/unrelated pins, unknown state schemas and changed payloads under the same
pin fail for recovery/review, not automatic mutable-state downgrade. An ancestry
allowlist is **not** application-schema compatibility evidence.

The CLI requires readiness revoked and known system/user workloads already
stopped before mutation. It does not stop them itself or create readiness after
success. The root controller now revokes readiness, validates the runtime/NSS
identity, synchronously stops/verifies known system/user workloads (timers first),
and invokes the child through runuser with a clean target-user environment.
It reloads active user managers and repeats stopping after both success and
failure. Stop/query failures block apply; remaining stops are still attempted.
It never stops SSH, Tailscale or the user manager, and does not start an inactive
manager merely to stop jobs. Control-plane/identity failures need operator review;
without a working bus it cannot prove all jobs actually stopped.

The disabled oneshot unit supplies control-group cancellation and ExecStopPost
cleanup, including partial startup failure. Its successful result means only
configuration applied with workloads blocked, not service health or readiness.
Runtime-secret/binary/private-listener gates, readiness/health checks,
adoption/recovery procedures and booted Fedora/SELinux/update/rollback testing
remain outstanding. Keep automatic application disabled and never create the
ready marker manually. All 82 tests are offline synthetic/mocked evidence,
not an actual target apply, runtime systemd stop or cancellation pass.

## Rootless containers and persistent user sessions

Podman is core host infrastructure, not a chezmoi installer or a new sandbox
launcher. The image explicitly selects `podman`, `container-selinux`, `crun`,
`netavark`, `passt` (pasta), `fuse-overlayfs` and `shadow-utils-subid`, alongside
`shadow-utils`' setuid `newuidmap`/`newgidmap`. Weak dependencies remain disabled.
Factory `/etc/containers` is copied only if absent; existing site policy and
rootful Quadlet definitions remain mutable and are not replaced during updates.
No Podman API socket, auto-update timer or restart service is enabled by presets.
Rootless Quadlets/workloads remain deliberate operator configuration.

Account enrollment allocates one free 65,536-ID block in each of `/etc/subuid`
and `/etc/subgid`, starting at 100,000 when free and skipping existing ranges and
NSS identities. Mappings belong to the operator account, not each agent. Other
users' entries are preserved, including numeric-UID owners. A separate protected
`/var/lib/personal-os/rootless.json` records the allocation and pending/complete
phase; the original version-1 account journal is unchanged. Partial writes retry
with the same IDs. Changed/missing/composite/overlapping recorded mappings fail
for review, never implicit remapping or recursive container-storage chown. A
trusted previously completed account may retain its existing valid single ranges
rather than receive replacements. Local `files` subid delegation is required.
Shared Shadow PID locks serialize registry writes; ambiguous/live locks fail,
validated dead-PID locks can be recovered. Do not manually edit ranges while
containers or enrollment are running; coordinate storage migration separately.

**Lingering is enabled once for the enrolled operator account.** This supports
user managers/Quadlets and sessions after logout. Later deliberate
`loginctl disable-linger` is preserved, not reverted on every boot. Enabling
linger does not enable shpool, an API socket, agents or guarded server workloads.
The account unit creates its runtime context directory before sandbox setup;
mail-spool suppression uses the supported factory `useradd` default, not an
invalid `useradd -K CREATE_MAIL_SPOOL` override.

Shpool explicitly has `NoNewPrivileges=no`, allowing the mapping helpers and
ordinary operator sudo inside host sessions. It is **not** an agent isolation
boundary; run untrusted agents inside the separately owned sandbox. Its private
socket, disabled preset, umask and control-group cleanup remain unchanged.
Root enrollment/configuration units retain their `NoNewPrivileges=yes` setting.

`python3 tests/check_rootless_native.py` is an opt-in, networkless disposable
Fedora bridge: native useradd/getsubids and shared Shadow locking pass, with
logind mocked and a protected synthetic state hierarchy. It is NOT a Podman
namespace, SELinux, lingering/logout, shpool or booted target pass. Next prove
those, cgroup delegation, pasta, scoped SELinux mounts and stable mappings across
update/rollback in a fresh isolated VM. The latest integration remains unbuilt;
no live account, subids, linger or services were changed.

## Agent workspace tooling prototype

Running Claude Code and pi is a first-class mini-server use case; shpool supplies
persistent sessions across SSH disconnects. Its packaging passed the first
pre-Podman image build, separate from target chezmoi/account initialization:

- Node.js, npm, Git, ripgrep, fd and tmux are image RPMs.
- Pi `@earendil-works/pi-coding-agent@0.85.1` uses the committed
  `packages/agent-tools/package-lock.json`. Build-only `npm ci --ignore-scripts`
  checks integrity and Node >=22.19 engines; optional clipboard support is omitted.
- Native Claude Code `2.1.288` uses an exact official download URL, size and SHA-256
  from its release manifest. No curl installer or agent binary runs during build.
  These HTTPS-publisher checksums are not independent signature verification.
- shpool `0.11.5` and Starship `1.24.2` build from checksum-verified crates.io sources
  using their published Cargo.lock and `cargo install --locked`, with two Cargo
  jobs. Starship's 428-package lock and Rust >=1.90 requirement were inspected;
  Fedora 44 package resolution proved its previously assumed RPM unavailable.
  Rust/Cargo/compiler packages stay in the disposable overlay, not the runtime image.

`mkosi.build.chroot` runs `scripts/build-agent-tools.py` in the target build overlay;
only runtime files under `/usr/lib/personal-os/agent-tools` enter DESTDIR. Build
networking is explicitly enabled for public dependency/artifact retrieval. Caches,
NPM configuration, Cargo build output and homes remain disposable; no desktop
CLI is replaced. Runtime wrappers expose `/usr/bin/{pi,claude,shpool,starship}` and discourage
core self-updates; image changes own core versions. This is update policy, not a
security sandbox. Pi extensions and project dependencies remain user configuration.
Packaging passed in the first Fedora build; binary ABI/startup, authentication,
actual target boot and agent session behavior remain unvalidated.

Shpool's vendor user socket is private (0600, directory 0700); socket/service are
DISABLED by user preset. Its service permits mapping helpers and uses control-group
cleanup; neither constitutes agent isolation. Interactive shpool is deliberately not a
server-workload dependency to be killed by configuration retries. Target-side
lingering, logout/reconnect, TUI key handling, resource limits and maintenance
quiescing still need a reviewed policy and VM test. Session persistence survives a
connection loss, NOT daemon restart or OS reboot; pi/Claude session files must be
retained separately. No agent starts automatically.

Authentication, OAuth refresh, sessions, workspaces and tool caches are private
mutable target data, never image inputs. The existing dotfiles pi configuration
contains unpinned extensions (including `@latest`); review/pin those executable
resources before unattended use rather than silently rewriting the submodule.
**Agent isolation follows the owner's existing sandbox setup:** agents run as root
INSIDE their own sandbox environments, not as root on this OS host. No dedicated
host agent account or host user per concurrent agent is required; the existing
operator account manages multiple sandboxes. Reuse that setup rather than creating
a competing sandbox launcher. Keep each sandbox's writable state, credentials and
explicitly shared workspace access scoped deliberately; sandbox root must not
imply host root, privileged host devices or access to the host's management socket.
Preserve enforcing SELinux. The existing sandbox definition/runtime and its Fedora
integration still need inspection and validation; this decision is not a sandbox
security pass. The prototype's shpool NoNewPrivileges restriction is now explicitly
removed for rootless mapping helpers. Validate inherited session/user-manager
settings too; do not mistake host-session hardening for sandbox isolation.
Host CLI provisioning alone does not put those tools inside a sandbox image; reuse
the existing sandbox's tool composition and validate version/update compatibility.

## Source and release boundaries

The clone has an `upstream` fetch remote (push disabled locally), a
`personal-os` branch and owner-created `origin` at
`https://github.com/ca-mantis-shrimp/personal-os.git`. The owner published the initial fork; the agent subsequently pushed the reviewed
guard/rendering changes with explicit approval.
This is source publication, not a deployable image release. Production signing,
artifact distribution and release custody remain undecided.

The dotfiles guard changes are published on
`origin/personal-os-immutable-hooks` at `1338e50103645df922e1411a523edeaf709336d7`.
With explicit owner approval, the agent pushed that branch first, then the OS
`personal-os` branch at `7245209`, so another checkout can retrieve the exact
gitlink. The dotfiles changes have not been merged into its other branches.
The owner subsequently approved publication of the account/source-lifecycle
prototypes; `da3be00` and `fa74ae0` were pushed to `origin/personal-os` without
advancing the dotfiles pin. The controller follow-up is local work only.
Future publication still requires approval; this source push does not authorize
image releases, production signing or deployment.

The initial dotfiles gitlink is the committed source revision, not the unrelated
live working tree in `~/.local/share/chezmoi`. Planning and bootc-reference files
were migrated from that checkout into this repository; its deletions/forwarding
README remain uncommitted for owner review. The submodule may therefore contain
an older historical charter snapshot: it is not this project's live plan.

ClearHead CLI/LSP release work belongs in `~/Products/platform` and is being
handled separately by the owner. Consume a tested release/pinned artifact here
when available; do not edit platform code or invent a released binary.

## Safety

Local profile work, builds and isolated synthetic VM tests are approved.
Production formatting/RAID creation, backups, installation, flashing, publishing
and reboots need separate approval. The old OS is still live. Use only file-backed
virtual test disks, fresh identities and disposable credentials. See the charter
for the exact disk identities, accepted data-loss decisions and recovery gates.

Keep upstream licensing/provenance intact; `LICENSE` remains the upstream license.
