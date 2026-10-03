# Personal OS

A purpose-built, repository-defined OS for personal machines, starting with the
headless `mini-travel-server`. This is a local fork of
[systemd/particleos](https://github.com/systemd/particleos), not a new image/update
implementation written from scratch.

**Status: initial fork and handoff scaffold. Not ready to install.** The new
server profile now exports committed dotfiles into the factory image; first-boot
chezmoi integration and the trimmed storage/account/security policy are not
implemented or validated yet.

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

## Repository map

| Path | Purpose |
| --- | --- |
| `mkosi.*`, `mkosi.extra/` | Inherited ParticleOS build/update machinery; still needs trimming |
| `mkosi.profiles/mini-server/` | Initial stable-Fedora server overlay |
| `dotfiles/` | Pinned chezmoi source submodule, not a place for OS build logic |
| `.clearhead/charters/mini-server.md` | Canonical intent, decisions, approvals and next-agent handoff |
| `.clearhead/charters/mini-server.actions` | Active execution tracking (`+human` identifies owner tasks) |
| `reference/bootc/` | Retained alternative prototype, inventory and test evidence—not the chosen build path |
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

The default configuration selects the `mini-server` profile and Fedora early,
so conditional distro fragments do not accidentally follow the Arch builder.
Configuration inspection and offline smoke tests (not builds/installations):

```sh
mkosi summary
python3 -m unittest discover -s tests -v
```

These checks establish configuration selection/prerequisites and synthetic source
staging only, not package availability, a booted SELinux pass or a working
first-boot lifecycle.

The profile finalize hook calls `scripts/stage-dotfiles.py` to export the gitlink
recorded in OS `HEAD` into `/usr/share/personal-os/dotfiles/source`, with a revision
file and per-entry SHA-256 manifest. Working-tree changes and an advanced submodule
HEAD are not exported. Historical plans, archived/build trees and the committed
rclone runtime environment file are excluded; internal source symlinks must point
to included regular files. No chezmoi command runs during staging. The 115-entry
current payload has passed a disposable local export and synthetic Fedora target
rendering (archive only, never apply). A limited secret-indicator review found no
private-key blocks in the exported payload; this is not a credential-free proof
or a booted target pass. The package hook is now restricted to mutable Arch,
with immutable environment/branding/marker guards. Retired rclone targets are
ignored on immutable systems. Account provisioning and fail-closed workload
ordering are still required before automatic target-side application. Changes
to the gitlink must be committed in the OS repo to change the exported pin.

The server overlay **still inherits** upstream Secure Boot signing, TPM-encrypted
Btrfs root, Btrfs home and homed-firstboot behavior. These must be explicitly
reviewed/changed and VM-tested before any installation. The README's desired
conventional account/recovery policy is not implemented merely by naming a
profile. Never use upstream VM demo passwords/autologin for production.

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
