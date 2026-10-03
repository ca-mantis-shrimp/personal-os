# Mini-server data inventory

Read-only SSH scout as `dab`, 2026-10-01. This is a recovery inventory, not proof
that anything has been backed up. No workloads were started, services changed,
files deleted, disks mounted, or disks written. Secret values were not read.

## Coverage and limitations

- Measured directory sizes and file metadata, inspected Git status/local refs,
  inspected user unit launch paths, and listed rootless Podman volumes.
- Git discovery pruned build/dependency/cache/game/VM trees and did not follow
  symlinks. Bare repositories and data inside pruned trees still need review.
- Git commands used optional locks disabled and disabled fsmonitor/hooks. No
  fetch, push, checkout, reset, clean, or stash operation was performed.
- The server is active: repository state changed between successive reads.
  Counts below describe observations, not a frozen, consistent snapshot.
- Ordinary `du` undercounts rootless container files because subordinate IDs
  own some data. Repeating size reads with `podman unshare` exposed that data.
- Root-owned containers/volumes, Radicale collections, root's home, and privileged
  configuration remain inaccessible without sudo. Operator-provided SMART
  reports on 2026-10-02 show no concerning sector/error counters on either USB
  drive. The bridge limits overall status reporting; self-tests have not been
  performed. The owner chose to skip them; see the image README and charter.

## Capacity baseline

Namespace-aware `/home/dab` usage was approximately **556 GiB**. Ordinary `du`
reported only 436 GiB, so that smaller estimate must not size the backup.
Directory totals can overlap through hard links; do not sum the rows below.

| Location under `/home/dab` | Observed usage | Treatment |
| --- | ---: | --- |
| `Products/platform/clearhead-core/target` | 225 GiB | Review output |
| `.local/share/containers/storage` | 134 GiB | Review images/volumes |
| `.cache` | 59 GiB | Candidate cache, not approved for deletion |
| `VirtualBox VMs` | 16 GiB | VM disk and installer; ask whether to retain |
| `go` | 16 GiB | Review source versus dependency cache |
| `arch_desktop` | 13 GiB | Contents not yet classified |
| `.npm` | 12 GiB | Candidate dependency cache |
| `Products/clearhead-cli` | 11 GiB | Preserve Git and unique state |
| `Experiments` | 4.9 GiB | Preserve local projects/state |

The USB mirror has ample nominal capacity for a conservative full-home backup.
Do not exclude large trees merely because they look regenerable; classification
and restore verification come first. All system/application data outside home
must also be covered by the final backup manifest.

## Git recovery risks

The bounded scan found 101 `.git` markers, of which 87 supported Git status;
14 markers under Lua language-server third-party metadata were unusable.
The later live snapshot showed:

- seven roots with tracked modifications;
- nine roots with untracked entries;
- five roots with branches ahead of cached upstream refs; and
- 63 roots with at least one branch lacking an upstream, including agent-run
  clones and worktrees. No upstream alone does not prove a commit is unpushed.

Examples requiring preservation/review:

- `.local/share/chezmoi`: five actual stash entries and one branch reported
  `ahead 2, behind 2`. Back up the `.git` directory, refs, and reflogs as well as
  its working tree. A clone or bundle alone does not preserve all working state.
- `.todo`, `journal`, and `knowledge_base`: modified and untracked entries.
- `Products/clearhead-cli`, `Products/tree-sitter-projects`, and nested platform
  repositories: working changes and/or local commit/branch risks observed.
- `Experiments/agent-workspace`: untracked entries and an ahead branch.
- `Experiments/plot`: six branches without upstreams and six linked worktrees,
  five under `worktrees/plot/pilot/`. Some worktrees contain modifications or
  untracked entries. Preserve both the common Git administrative directory and
  all worktree directories, with their path relationships.
- `agent-runs/`: cloned/nested project repositories with local branches; some
  working changes were seen. These are not automatically disposable logs.

These comparisons used existing remote-tracking refs only. Remote reachability,
pushed state, LFS objects, submodules, ignored data, and bare repositories remain
unverified. Do not infer that clean Git status means a recoverable remote copy.

## Data outside Git

Required preservation candidates include:

- `gym`, `Documents/knowledge_base`, and `.local/share/clearhead`: the three
  Syncthing trees; none has a Git marker at its root.
- `knowledge_base` is a separate directory from `Documents/knowledge_base`.
  Preserve both; only the latter is configured as a Syncthing folder.
- `.local/state/syncthing`: config, identity keys, and application state.
- `.local/share/clearhead-conflicts-20260926`,
  `.local/share/clearhead-vevent-backup-20260723`, and `.local/state/clearhead`:
  conflict copies, previous calendar backups, telemetry, and e2e backups/probes.
  Do not discard these while resolving ClearHead recovery requirements.
- `Product`, `sketchbook`, `neorg`, `journal`, `docs`, `Diagrams`, `Downloads`,
  browser/app profiles, and agent histories: personal/project data to classify.
- `.local/bin`, `.cargo/bin`, and `.config/systemd/user`: custom tooling and
  service definitions, including the local OpenTelemetry binary and rclone
  wrapper. Record how required tools will be reconstructed on Fedora.

The metadata scan also found environment files, Compose definitions, and database
files in scanned paths; these were counted without reading their contents.
A filename or database extension is not evidence of an unused workload.

### Credentials and sensitive configuration

Back up securely, outside Git and OS images:

- `.ssh`, `.gnupg`, `.password-store`, `.pki`, and desktop keyrings;
- `.env` (observed mode 0644; review permissions separately);
- `.config/rclone`, `.config/chezmoi`, `.config/otelcol`, `.config/clearhead`;
- agent/application authentication and session state, including `.pi`, `.claude`,
  browser profiles, and any retained container volumes;
- vdirsyncer credentials/configuration and `.vdirsyncer` sync status; and
- privileged Radicale authentication/configuration and Tailscale state, if an
  identity migration is intentionally chosen instead of fresh enrollment.

Do not emit secret contents into inventory files, CLI action text, or build logs.

## Rootless containers and subordinate ownership

`podman ps -a` succeeded with no rootless containers. Three local volumes remain,
all reporting mount count zero:

| Volume | Namespace-aware usage | Preservation requirement |
| --- | ---: | --- |
| `agent-cargo` | 234 MiB | Review before treating as cache |
| `agent-target` | 81 GiB | Build-cache candidate; not approved for exclusion |
| `agent-pi` | 366 MiB | Preserve potential sessions/auth/state |

Paths are `.local/share/containers/storage/volumes/<name>/_data`.
Ordinary `du` saw only the wrapper directories; the contents were measured using
`podman unshare`. Backups must preserve the underlying data and ownership, not
just those visible wrappers.

Arch allocates `dab:100000:65536` in both `/etc/subuid` and `/etc/subgid`.
Record these allocations and validate the chosen Fedora restore/import method;
UID/GID 1000 alone is insufficient to preserve subordinate-owned files.
Raw Podman storage is not guaranteed portable across OS/runtime versions.

`/usr/bin/docker` is owned by `podman-docker`, so invoking it does not independently
inventory the old Docker data under `/var/lib/docker`. That privileged data and
any root-owned Podman/containerd state must be inspected separately.

## User services

Observed custom units include Neovim server, OpenTelemetry Collector, vdirsyncer,
rclone-onecloud-docs, Handy, Neovide clients, and Walker. No unit environment
values or command arguments containing credentials were printed.

- OpenTelemetry invokes `%h/.local/bin/otelcol`; config is under
  `.config/otelcol`, with approximately 29 MiB state under `.local/state/otelcol`.
- vdirsyncer runs from home and also invokes `%h/.cargo/bin/clearhead`; its timer
  declares a two-minute boot delay and five-minute interval.
- rclone-onecloud-docs uses a custom local wrapper and an EnvironmentFile; its
  timer declares an hourly schedule. Enabled/running status and actual backup
  coverage still require verification.
- Desktop clients are not implied requirements for the headless server.
  Keep/remove decisions remain with the owner.

## Targeted arch_desktop review (2026-10-02)

The owner separately approved a read-only review of `/home/dab/arch_desktop`.
Only this directory was inspected over SSH: path/size metadata, Git working
state, and selected non-secret documentation/configuration. No image was mounted
or booted, no credential values were read, and no files or services were changed.
This approval does not extend to the outstanding privileged inventory.

- This is a small mkosi experiment for an immutable Arch image with systemd
  repart/A-B partition ideas, not an observed archive of desktop personal files.
- `build/` occupies about 10.6 GiB and `mkosi.output/` about 2.0 GiB allocated.
  These contain raw/compressed images, kernels, initrds, an EFI image and a build
  log. One raw output has about 161 GiB apparent size but is sparse. Allocated
  sizes explain the earlier approximately 13 GiB directory measurement.
- Documentation and source/configuration, including `.git`, occupy under 1 MiB
  allocated. Useful preservation candidates are `README.md`,
  `docs/TROUBLESHOOTING.md`, `mkosi.conf`, profiles, repart definitions, the
  `mkosi.extra` tree, and Git administrative state.
- `mkosi.repart/10-root-a.conf` is locally modified: root size bounds changed from
  5–20 GiB to 40–100 GiB with 120 GiB minimum padding.
- Three untracked files define two runtime `_empty` ext4 root partitions and
  enable `systemd-repart.service`. They would not survive a clone of committed
  history. Preserve them if retaining the experiment.
- `master` showed no divergence from cached `origin/master`; no stashes were
  found. No fetch or remote backup verification was performed.
- `mkosi.rootpw` is ignored and was not read. Keep credentials out of Git and
  the OS image. Generated images may contain credentials or mutable VM state;
  their contents were not inspected, so discardability is an owner decision,
  not proven by filename alone.

Retention decisions and the remaining owner review are tracked in the charter
and its `mini-server-arch-desktop-review` action. The source describes a separate
Arch experiment; this review established no requirement to incorporate its
partition configuration into the Fedora bootc image.

## Focused service/configuration inventory and cleanup (2026-10-02)

The owner authorized a focused read-only service/configuration pass plus limited
cleanup, with chezmoi as source of truth and small reconstruction gaps acceptable.

- SSH, Tailscale, Radicale and `syncthing@dab` are active/enabled. OpenTelemetry
  and Neovim user services are active/enabled; vdirsyncer's timer is active/enabled.
- `rclone-onecloud-docs.service` and its timer are disabled/inactive. Chezmoi
  contains their definitions and wrapper; the wrapper uses `rclone move`, not a
  versioned backup operation, and defaults to dry-run if not overridden. Runtime
  environment values were not read, so actual sources/destination and past
  transfers remain unverified.
- Selected live user units (OpenTelemetry, Neovim, vdirsyncer and rclone), the
  rclone wrapper, and OpenTelemetry config match the server's chezmoi source by
  content hash. That source had a clean working tree at commit
  `9c212a9e4b33d7e4c4798d15d1efa122562d9db7`. Local branches still exist; no fetch,
  push or comprehensive history/stash recovery review was performed.
- OpenTelemetry uses an executable local binary of about 120 MiB, and ClearHead
  an executable under `.cargo/bin` of about 17 MiB. Configuration is reproducible
  from chezmoi, but required binaries still need a Fedora provisioning method.
- Neovim still listens on all IPv4 interfaces at 6666. The intended replacement
  policy is private/deliberate access, not replication of that broad listener.
- The retired `rsync-usb-system-backup.timer` remains active/enabled; its service
  was inactive. `/mnt/fat32` is a root-owned directory on `/` ext4, not a mount.
  No backup job was stopped and that directory was not removed.
- Noninteractive sudo is unavailable; root-owned data/container contents were
  not inspected and no password was requested. This is a remaining coverage gap,
  not proof of required unique data.
- Cleanup removed only `/home/dab/arch_desktop`, already retired by the owner.
  Before removal its exact real path, directory type, owner, experiment markers
  and absence of mounts beneath it were checked. Absence afterward was verified.
  No other source, synced data, cache, container volume, service configuration,
  disk partition or mount was changed.

### Subsequent operator cleanup follow-up

The owner disabled/stopped `rsync-usb-system-backup.timer`, then removed the
retired `/mnt/fat32` directory using sudo. Before removal, a read-only check
verified the exact real directory and no mounts at/beneath it. Follow-up verified
both `/mnt/fat32` and `/home/dab/arch_desktop` absent and the backup timer still
inactive/disabled. No other server data has been deleted in this cleanup.

## Coverage status

Privileged state, pruned trees, bare repositories, and remote recoverability
remain unverified. No retain/exclude manifest, backup, or successful application
restore is established by this scout.

Intentions, remaining actions, operator checks, approvals, and handoff live in
[the ClearHead charter](../../.clearhead/charters/mini-server.md) and its paired
actions. This document contains technical observations only.
