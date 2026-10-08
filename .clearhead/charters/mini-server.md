---
id: 01a0fb15-b777-75a3-a048-7e0da5722a02
alias: mini-server
parent: personal-os
state: Active
---
# Mini-server migration and storage

## Intent

Turn `mini-travel-server` into a dedicated headless server with repository-defined
immutable OS updates and a tested rollback/recovery path. The owner's intended
architecture is a trimmed ParticleOS fork using mkosi/DDIs/sysupdate, in a
separate OS repository with the chezmoi repository pinned at `dotfiles/` as a Git
submodule.
Stage the pinned chezmoi source and tool in the image, then initialize/apply
chezmoi automatically on the real target after build, once the intended account,
hostname and home are ready. Do not render the target's home configuration using
the builder's identity. This is automatic target-side configuration, not manual
post-install dotfile setup. Bootc remains a
retained tested alternative, not the predetermined destination.

Keep canonical OS build configuration in this fork and user configuration in
`dotfiles/`. Intentions, planning, handoff and execution tracking have moved here
from the live chezmoi checkout, preserving this charter's identity and paired
files. This repository is now the canonical migration workspace; do not maintain
another PLAN or next-steps document or treat the dotfiles submodule's historical
charter snapshot as a second active plan.

Prepare the two available 4 TB USB disks as persistent storage before
reinstalling the NVMe so they can hold migration backups. The server must boot
when USB storage is absent, but storage-dependent workloads and backup jobs must
refuse to run against an unmounted directory.

## Boundaries and safety gates

- **Planning by default, with scoped inventory/cleanup approval.** The owner
  authorized a focused read-only inventory of retained services/configuration and
  cleanup of explicitly retired data, emphasizing chezmoi as source of truth and
  accepting small reconstruction gaps. `/home/dab/arch_desktop` was removed by
  the agent; the owner disabled the retired backup timer and removed `/mnt/fat32`.
  Both directory removals were verified. No broad cache/container purge is approved.
  The owner subsequently approved local image/service provisioning, builds and
  isolated VM validation with synthetic data/fresh identities. Production storage
  setup, backups, publishing, installation and reboots remain unapproved; neither
  a desktop reboot nor host kernel repair is authorized by VM-test approval.
- Do not wipe the mini-server until required data is inventoried, independently
  backed up, and restore-tested, and the replacement is ready.
- Obtain explicit approval for the exact disks before array creation, formatting,
  installation, or a production reboot. The owner confirms both USB disks are
  empty; this is not blanket approval to write them or the NVMe.
- Keep another independent copy of irreplaceable data. A mirror is not a backup,
  and both disks share a USB dock/hub and power failure domain.
- Arrange physical console access and rescue media; Tailscale alone is not a
  recovery plan. Disconnect USB storage during the eventual NVMe installation.
- Never bake credentials or machine identities into the OS image. Do not run
  cloned production Syncthing or Tailscale identities in a VM.
- Preserve SELinux enforcement. OS rollback does not restore mutable application
  data, configuration, or schemas; workload rollback needs separate backups.
- Start with manually approved updates; automate only after health checks,
  backups, and recovery are proven reliable.

## Current position

The minimal Fedora 44 image passed bootc lint and local UEFI VM tests, including
SSH, sudo, networking, SELinux, image switch/reboot/rollback, and persistence.
Real workload restoration and Tailscale enrollment still need testing.

The expanded local `mini-server:services` image now includes native workload,
RAID and backup tooling, a pinned Collector, scoped passwordless sudo, key-only
SSH, loopback Neovim policy and a fail-closed storage startup guard. It passed
bootc lint and nine isolated container smoke tests with synthetic state. User
configuration remains in chezmoi; image drop-ins supply OS-specific binary/access
policy. The owner identifies `~/Products/platform` as the ClearHead development
source; its documented locked Cargo install builds the CLI/LSP from pinned
submodules. Source/build entry points are now identified, but a staged build,
Fedora runtime test and fresh host-specific vdirsyncer credentials are still
needed before enabling that timer. Do not replace the desktop's installed CLI
or modify the active platform development checkout as part of migration.

The initial expanded-image VM build hit a desktop kernel/module mismatch and
loop ENODEV; the in-VM fallback stalled. The builder was stopped and all scratch
storage, manifests, test keys/password/config and artifacts removed. The owner
subsequently rebooted this desktop: kernel/modules now both 7.2.8-arch1-2, and
a privileged isolated builder can open loop-control. That blocker is resolved,
and the owner has now chosen the ParticleOS-derived repository model. The local
fork and stable-Fedora server overlay are initialized; three offline config
smoke tests pass and ClearHead doctor reports no findings. This validates config
selection/prerequisites only, not image package availability or target behavior.
No new guest boot/SELinux/recovery, RAID presence/degradation, update/rollback or
real workload restore pass is claimed. Bootc evidence stays in `reference/bootc`.
At initial scaffold validation no ParticleOS-derived image had been built or
installed. A first pre-Podman candidate has since built successfully (evidence
below). At that stage the rootless/account follow-up was unbuilt and no
candidate had booted or been installed. Subsequent retained Fedora builds/failed
boots and the first Arch build are recorded below; use **Next-agent handoff**
for the latest status. No installation has occurred.

The owner subsequently authorized making this a minimal, explicitly owned fork.
The active recipe is now Fedora 44 plus mini-server, with a Fedora 44 tools tree
and no GUI tools profile. Explicit target package selections fell from 124 to 92;
requested workloads and agent tools remain. Unused desktop/distro/OBS/netboot,
demo credentials, all eight extra UKI profiles and upstream publishing examples
are preserved in `reference/particleos/`, outside active discovery and image
payloads. Personal OS branding and `ImageId=PersonalOS` replace upstream identity;
Fedora ID/version plus the ParticleOS ancestry token retain pinned immutable guards.
Only the normal signed UKI is currently built. Auditing/enforcing SELinux and
fail-on-error relabeling are explicit; weak dependencies and Secure Boot automatic
enrollment are disabled, and mutable root/home/swap are not factory-reset candidates.
The TPM-encrypted Btrfs root/swap and unencrypted Btrfs home layout is retained,
not newly boot-validated. 100 offline tests pass, including synthetic fork branding
and archive rendering without apply. No image-size/transitive-package, booted
SELinux/update/rollback, installer or recovery pass is claimed. No production,
credential, submodule or publication changes occurred.

Latest owner request makes Podman core host infrastructure. The mini-server now
selects Podman, container-selinux, crun/netavark, passt/pasta, fuse-overlayfs and
shadow-utils-subid explicitly. Enrollment supplies stable subordinate UID/GID
ranges and enables operator lingering once; later explicit disabling is preserved.
Shpool now permits mapping helpers (`NoNewPrivileges=no`) but remains disabled
and is not the sandbox boundary. This local follow-up has 119 offline tests plus
a narrow native Fedora Shadow/libsubid bridge, not a rootless namespace/shpool/
logind/SELinux or booted-target pass. Package selections are now 98; the first
build predates these changes. No host/server account, subids, linger or services
were changed. Sandbox extraction was delegated to another agent; do not work in
platform or introduce a second runner here.

USB identities and topology are recorded. Operator-provided SMART reports show
clean sector/error counters on both CMR drives. The owner has chosen to skip
extended self-tests and use those reports as the baseline for non-critical home
storage. Tests are optional, not an outstanding setup gate or a claimed pass.

Other privileged inventory remains outstanding. The retired weekly backup wrote
to a directory on the live NVMe and excluded `/home`; it is not an independent
migration backup. The owner disabled/stopped its timer; a read-only follow-up
verified the timer is inactive/disabled and its service inactive. No migration
backups have been made; retained services, partitioning and mounts are unchanged.
Approved file cleanup removed `/home/dab/arch_desktop` and `/mnt/fat32` (the
latter by the owner); both absences were verified. Focused inventory confirms
selected live user-service configuration matches chezmoi; rclone is disabled.
The retired weekly backup timer remains disabled/inactive.

## Planning sequence

Task state lives in [mini-server.actions](mini-server.actions); completed and
cancelled history lives in
[mini-server.completed.actions](mini-server.completed.actions).

1. **Finish the storage design locally.** Proposed: mdadm RAID1, GPT member
   partitions, ext4, and `/srv/storage`. Specify exact members, assembly and
   monitoring, optional UUID-based mounting with bounded waits, and healthy,
   degraded, and absent-storage behavior. Fstab `nofail` alone is not the whole
   RAID boot policy. None of the creation choices is approved for execution.
2. **Agree what to retain.** Use the observed inventory to draft the manifest.
   Cover required home data, hidden configuration, secrets, custom tooling,
   modified/untracked/ignored Git state, local refs/stashes, linked worktrees,
   ClearHead conflict copies and required application state. Use the owner's
   retention decisions below rather than assuming both knowledge bases or all
   credentials need copying. Review caches, large Rust targets, old VMs and
   `agent-pi`; only explicitly retired paths are excluded. Mark privileged
   coverage gaps separately.
3. **Specify backups and recovery.** Select an independent second destination,
   protect credentials/encrypt sensitive backups as appropriate, and preserve
   ownership, ACLs, xattrs, hard links, and symlinks where required. Plan consistent
   database exports/snapshots/quiescing and coordinate active editing before final
   sync. If any rootless volumes are retained, subordinate ownership needs a
   tested restore/import method; otherwise recreate containers rather than
   imposing raw-storage migration work.
   Choose representative file, credential, Git/worktree, and application restores.
4. **Implement and test the ParticleOS-derived profile.** Trim upstream defaults,
   define account/mutable-state/SELinux and signing/recovery policy, and implement
   pinned chezmoi staging with automatic real-target application. Reuse upstream
   partition/UKI/sysupdate machinery. Integrate RAID/monitoring tooling, optional
   mounts and fail-closed storage guards, workloads, runtime secrets, artifact
   distribution/trust and release workflow. Local implementation/builds and
   isolated validation are approved. Service tooling/policy exists as a bootc
   reference only; the new profile and first-boot integration are not complete. VM tests must still cover restored
   workloads, fresh identities, SELinux, missing storage, network loss,
   console recovery, update/rollback, and mutable application recovery.
5. **Prepare the eventual migration procedure.** NVMe layout, downtime/final sync,
   restore ordering, physical recovery access/rescue media, and separate explicit
   installation approval. The owner prefers not to open the machine: plan to
   reinstall onto the existing NVMe, without a spare internal disk or retained
   bootable old installation. Required recovery copies and tested rescue access
   must substitute for that fallback. Disconnect USB storage during installation,
   then reassemble the existing
   array rather than recreating it. Keep old backups until stable.

## Initial storage and migration overview

This is a first design proposal, not an execution procedure or disk-write
approval. The immediate goal is to prepare recoverable migration storage while
leaving the live NVMe installation intact. The target is a headless immutable
server whose management access remains available without USB disks.

### Proposed storage layout

- Use the two recorded 4 TB drives as an mdadm RAID1 mirror, with one aligned
  Linux RAID member partition on each GPT disk:
  - WD40EFPX-68C6CN0 — serial `WD-WX22D55EMYVE`,
    WWN `0x50014ee2c187373e`;
  - WD40EZAX-00C8UB0 — serial `WD-WX52D847K1PS`,
    WWN `0x50014ee21684b72b`.
- Resolve stable ATA/WWN device paths and recheck serials, capacity, existing
  signatures, and mount/use status during the eventual approved preflight.
  Never select members by `/dev/sdX` or the duplicated USB bridge serial.
- Proposed array: md metadata 1.2, ext4, mounted at `/srv/storage` by filesystem
  UUID. Expect roughly 4 TB decimal usable capacity before filesystem overhead,
  not 8 TB. Record array, member and filesystem UUIDs after approved creation.
- Keep OS boot, accounts, SSH, Tailscale and recovery tooling on the NVMe.
  Proposed storage subdirectories separate `migration`, `backups`, and workload
  `data`; these are organizational boundaries, not independent backups.

### Boot, failure and monitoring policy

| Storage state | Proposed behavior |
| --- | --- |
| Both members healthy | Assemble the known array, mount the expected filesystem, and allow guarded jobs/workloads. |
| One member missing | Permit degraded assembly of the known array for recovery; alert immediately. Routine backup writes and workloads remain stopped until an operator accepts degraded operation. |
| Both members absent, assembly failure or wrong filesystem | Boot the OS and management services normally; leave storage-dependent jobs/workloads stopped and report why. Never fall back to the bare mount directory. |

Assembly must be restricted to the recorded array identity, without creating a
new array or forcing stale members. Specify systemd/mdadm and initramfs behavior
for both Arch preparation and the eventual Fedora image: `nofail` on the mount
alone does not settle degraded assembly or boot dependencies. Target an optional
mount with bounded device and mount waits (initial target: 30 seconds each), not
an unbounded wait or a required root filesystem dependency. Exact configuration
and observed boot timing remain to be validated in separately approved tests.

Each storage-dependent service and backup must depend on the mount and check its
expected filesystem UUID, read/write status, and accepted array health before
starting. Mount-directory permissions are defense in depth, not the main guard.
Define stop/failure handling for mount loss and runtime I/O errors; startup checks
alone do not cover dock disconnection. Monitoring should cover degraded arrays,
resync/recovery, member disappearance, filesystem errors and free space. Alert
delivery, periodic SMART reads and scrub schedules remain to be chosen; declined
extended SMART self-tests are not reinstated as a gate.

### Backup and migration approach

The approximately 556 GiB namespace-aware home measurement is the unfiltered
baseline, not the eventual backup size. The owner reports that much of the old
data is no longer needed, especially temporary Rust builds and container data.
Treat these as exclusion candidates for an exact-path review, not permission to
delete or omit entire container trees: retained volumes may contain auth/session
state. The owner has retired the old `/mnt/fat32` system-backup directory and
agrees it need not be included in migration backups. This is a retention decision,
not approval to run deletion commands during the planning-only phase.
After the targeted read-only review, the owner reports pushing `~/arch_desktop`
to GitHub and retires the whole tree, including generated artifacts. Exclude it
from migration backups; no integration into chezmoi/the OS build is needed.
GitHub completeness was not independently verified. This is the owner's decision
to retire the experiment, not a claim that all other home/application state is
disposable. Under the owner's subsequent cleanup approval, the exact
`/home/dab/arch_desktop` tree was removed after directory/owner/marker checks and
confirmation of no mounts at or beneath it. Its absence was verified.
The owner has also completed their `Experiments` review and reports that all
content they want to keep is pushed to GitHub. Its owner source-retention review
is resolved; remote completeness was not independently verified. No additional
migration copy is requested for that reviewed source. This does not resolve Git
recovery or non-Git retention requirements for other repositories and paths.

The manifest should cover only data the owner requires, not a blanket home or
system archive. The owner identifies 1Password as the authoritative credential
store; plan to reprovision required secrets from it rather than assume local
credential files need duplication. Verify recovery access to 1Password without
exposing vault contents. The owner accepts loss of the separate
`~/knowledge_base` if it contains anything not already on the desktop; that path
may be excluded. Google is authoritative for calendars, so server-local calendar
copies can be rebuilt instead of being treated as irreplaceable. Any unique
Radicale contacts/tasks or other non-Google collections are not yet established.
Required synced personal/ClearHead data, custom configuration and remaining
unique Git state still need a compact recovery manifest. Do not commit secrets
or raw machine backups to Git.

The old `/mnt/fat32` backup, the whole `~/arch_desktop` tree and the separate
`~/knowledge_base` are explicitly retired or accepted as disposable. Other
exact-path exclusions remain open. Cleanup removed `/home/dab/arch_desktop` and `/mnt/fat32`; their absence
was verified. The owner disabled/stopped the old backup timer before removing
`/mnt/fat32`, after target/mount checks; the timer remains inactive/disabled.
The separate `~/knowledge_base` and all other server data have not been deleted.

The owner reports that required personal/application data is already synced
through Syncthing to the current desktop. This is useful recovery coverage but
has not been verified as a complete, consistent or restore-tested migration copy.
The recorded server Syncthing folders are `~/gym`,
`~/Documents/knowledge_base` and `~/.local/share/clearhead`. The separate
`~/knowledge_base` no longer requires preservation, credentials come from
1Password and calendars from Google per the owner's decisions above. Verify only
remaining required synced data, local Git state and service configuration, plus
any unique non-Google application data. Sync can propagate deletions, so
freeze/version a verified independent copy of required data and restore-test it
before wiping the server. No backup or wipe-readiness gate is marked complete
based solely on the report of synchronization.

The mirror may hold a migration backup, but a second independent destination
must hold all required recovery data before the NVMe is wiped. Choose its capacity,
encryption and offline recovery-key custody without putting secrets in ClearHead.
Define consistent application capture and metadata-preserving restore methods,
including subordinate-ID-safe export/import only for volumes actually retained.
Restore-test representative
personal files, credentials, Git/stashes/worktrees and application state before
installation approval.

Later, separately approved VM tests must exercise healthy/degraded/absent storage,
wrong filesystem, dock/mount loss, guarded backups, restored workloads, fresh test
identities, SELinux, console/network-loss recovery and update/rollback. Installation
also requires physical recovery access, a final consistent sync, an approved NVMe
layout, and USB disconnection. Reattach and assemble the existing array afterward;
never recreate it as part of restoration.

### Owner decisions

The owner clarifies the intended alternative: fork ParticleOS and cut it down
to a repository-defined, purpose-built server OS, rather than install stock
ParticleOS or assemble an unrelated mkosi design from scratch. Treat its existing
partition/UKI/sysupdate machinery as the starting point, with a minimal headless
profile and explicit mutable-state/access/recovery policy. The OS fork will be
a separate repository with this dotfiles repository as a pinned submodule;
image creation stages the selected committed chezmoi source without invoking
chezmoi initialization/apply or its hooks in the builder. Run initialization/apply
as the intended user on the real target after account/home/hostname provisioning,
using the actual machine/distro context. Reuse chezmoi templates, ignore rules
and machine/distro/profile guards instead of a parallel bootstrap/filter system.
The existing Linux read-source hook invokes `bootstrap-paru.sh` unless
`CHEZMOI_CONTAINER=1`; narrow its Arch applicability before applying on Fedora.
Do not bake vault credentials, password hashes, SSH private keys or device
identities into the image. Define safe first-boot application and subsequent
pinned-source updates explicitly rather than blindly overwriting user files on
every boot; runtime-only secret provisioning must precede secret-dependent jobs.

The initial local fork now lives at `~/Products/personal-os`, on branch
`personal-os`, derived from upstream ParticleOS commit
`e55d7a95e3b9da8a2291ca17b7327b204f2c5a56`. Its `dotfiles/` submodule records
`https://github.com/ca-mantis-shrimp/dotfiles.git` at committed revision
`c84190f5aaa1f63e542ffff5f198ce3de75899c0`, not the live checkout's uncommitted
migration changes. The `mini-server` profile is a stable-Fedora starting overlay,
not yet a trimmed/bootstrapping/deployable implementation. Root/home/homed/signing
choices remain inherited and must be resolved deliberately. The USB mdadm/ext4
design is independent of ParticleOS's internal root/home filesystem defaults.
At scaffold creation no personal remote fork/origin or publication existed.
The owner subsequently created `origin` and pushed the OS source (see handoff).
No production signing-key generation or switch/install has been performed.

Bootc remains a retained working fallback, not an irrevocable choice. Pause
bootc-specific implementation and fresh test builds while designing the
ParticleOS-derived candidate. Evaluate the trimmed fork against the same stable
base, enforcing SELinux, SSH/console recovery, update/rollback, fresh identity and
missing-USB requirements. Upstream's experimental/default-profile choices are
things to review in the fork, not proof that the intended customized model is
unsuitable. ClearHead release work stays separate in platform.

The owner agrees with the storage design: the two recorded USB members,
mdadm RAID1, GPT member partitions, ext4 at `/srv/storage`, optional storage and
fail-closed workloads. Ext4 is chosen over Btrfs to prioritize straightforward
operation and recovery; additional resilience effort goes into independent
backups and restore tests. This design agreement does not authorize disk writes
or implementation; creation parameters and the exact-disk preflight still need
separate execution approval.

The owner selects Backblaze B2 for cloud backups, confirms the account and
reports creating an application key scoped to a bucket. Keep server backups
separate from the owner's 1 TB Google Drive allocation used mainly for email
and photos. No key values were requested or read. Verify current B2 pricing,
key capabilities and bucket lifecycle policy before approved backup setup;
bucket scoping alone does not establish restic compatibility.

The owner has selected restic as the backup CLI for both local and cloud backups.
Plan separate encrypted repositories on the USB mirror and B2, with retention,
integrity checks and restore tests for each. The B2 application key authorizes
storage access; it is not the restic repository encryption password. Store both
securely outside Git/images/chat and keep recovery access independent of the
server. The owner approves encrypted restic repositories with unattended
credential loading from protected runtime files or an equivalent mechanism, and
recovery copies of repository passwords and B2 credentials in 1Password.
Configured backups/restores should require no recurring password prompts or
per-job vault unlock. Use a nonempty automatically loaded repository password;
no empty-password repository is wanted. Destination and recovery-key custody
decisions are settled; no repository has been initialized or backup executed. The owner has not yet decided what belongs on the USB mirror
long-term or which datasets belong in cloud backups. The mirror's initial purpose
remains migration backups; do not assume documents or all workloads will move to
it. Cloud coverage should be selected from the approved recovery manifest, not
inferred from mirror capacity. Destination and recovery-key custody choices are
settled; exact dataset placement and retention remain open. Backup execution is
not approved.
Retention decisions are recorded above.
For retained application state, ownership and consistency still need a tested
capture/restore method; choosing restic alone does not settle those requirements.
The owner prioritizes generic deployments with chezmoi as source of truth and
accepts small reconstruction gaps. Do not expand this into a forensic archive or
require raw-container restoration unless significant unique required data is
identified.

The owner intends to retain SSH, Tailscale, Syncthing, Radicale, OpenTelemetry,
vdirsyncer and the Neovim server, and replace the rclone job with restic backup
jobs. The owner clarifies that rclone was intended for cloud backup and may not have
been running; enabled/running status remains unverified. The owner clarifies
that occasional scanned documents currently arrive on the desktop used for this
session, not the homelab server. Desktop-to-cloud document backup is a separate
workflow, not a requirement to create a server scan folder or move documents to
the USB mirror. Restic can serve that workflow, but its repositories are not
browsable cloud sync folders. Keep desktop backup planning distinct from this
server migration. Verify any existing server rclone source/destination coverage
and status during a separately approved operator pass; do not assume the old job
ever produced a backup. Keep Neovim
access deliberate and private; retaining the service does not approve its current
all-interface listener or public exposure. Service definitions, packaging,
backup schedules and network exposure remain to be designed; no services have
been changed or removed.

The owner chooses fresh Syncthing enrollment after reinstallation rather than
preserving the server's device identity/configuration. They report having checked
and prepared the required data on the current desktop earlier. Plan to pair the
new device and seed selected folders from that desktop, protecting the desktop
copy during initial synchronization; do not treat an empty new server as the
authoritative source. No production Syncthing identity backup is required for
continuity. Exact folder mapping and a recoverable independent copy still belong
in the cutover procedure. The owner also agrees to fresh Tailscale enrollment
and intends to configure services remotely from the current desktop once SSH is
available. Bootstrap reachable SSH access independently of Tailscale (or use the
physical console to establish access); then enroll Tailscale interactively.
The owner wants the initial account provisioned in `wheel` with this desktop's
SSH public key. Use a host-specific installation configuration rather than
baking access policy into the reusable OS image; no private key is needed.
Initial account: `dab`, UID/GID 1000, in `wheel`, with this desktop's SSH public
key. Plan key-only SSH and passwordless sudo scoped specifically to `dab`, not
a blanket passwordless rule for all wheel members. Use an explicit sudoers
`NOPASSWD` policy, validate it with `visudo`, and test it in a separately approved
VM; ordinary wheel membership alone is insufficient. This is an access-policy
design choice, not permission to change the current host.

The trade-off is that compromise of `dab`'s SSH key/session gives root without
another prompt. Bootc immutability does not protect mutable `/etc` or `/var` from
root, and Tailscale is not a substitute for host access controls. Keep SSH access
and tailnet policy restrictive. The owner chooses a readily typable console
passphrase stored in 1Password so local login remains available if SSH fails.
SSH remains public-key-only; passwordless sudo does not remove the account's
console password. Provision the password hash securely outside Git and chat.
Separately approved tests must verify console login and sudo with networking/SSH
unavailable, plus rescue-media repair without reinstalling. Initial identity and
access-policy decisions are settled; secret provisioning, testing and recovery
media preparation remain execution gates. No installation, reboot or enrollment
is authorized by these decisions.

The owner does not want to open the server to swap/add an NVMe. Plan installation
onto the existing NVMe rather than a spare internal disk; do not assume the old
installation remains bootable afterward. This target-strategy decision is not
approval to wipe: exact NVMe identity/layout, required recoverable data,
replacement validation and rescue readiness remain installation gates.

The owner has a portable monitor and keyboard available for physical console
access, plus USB sticks that can be flashed when execution is approved. Hardware
availability is confirmed; rescue/install media have not yet been prepared or
boot-tested. Arrange local console access during installation and prove the
rescue path before relying on it. No flashing or reboot is authorized now.

Owner decisions and operator tasks are tagged `+human` in
[mini-server.actions](mini-server.actions). Review the storage proposal, select
an independent backup destination, approve retention and service/identity choices,
and arrange recovery access. Administrator inventory, disk writes, VM testing and
installation retain their separate approval gates; agreement with this overview
is not permission to execute them.

## Future administrator-assisted inventory

The owner approved a focused read-only inventory, but this agent cannot obtain
sudo noninteractively. The following are reference commands for an operator pass,
not instructions to run the entire original checklist now. Prioritize only
significant state outside chezmoi and the retired backup timer/directory. SMART reports have already been supplied; the main
remaining sudo gap is root-owned state. Connect as `dab@mini-travel-server` and
authenticate to sudo normally. Never share passwords, tokens, private keys, or
full container inspect/configuration output.

### Root-owned containers

```sh
sudo podman ps -a --format '{{.Names}} | {{.Image}} | {{.Status}}'
sudo podman volume ls --format '{{.Name}} | {{.Driver}}'
sudo podman volume inspect --all \
  --format '{{.Name}} | {{.Mountpoint}} | {{.Driver}}'
```

Do not start workloads to populate a listing. Podman queries may initialize or
update runtime bookkeeping. If any containers exist, inspect their bind-mount
metadata in a targeted follow-up, without exposing environment variables/labels.

The installed `docker` command is a Podman wrapper and cannot independently
inventory old `/var/lib/docker`. Check for a real daemon without starting it:

```sh
sudo test -S /run/docker.sock && echo docker-socket-present
systemctl is-active docker.service docker.socket containerd.service
```

If a socket or old Docker data exists, record it for a targeted follow-up. Do not
delete that data or start a new daemon against it.

### Privileged sizes and ownership

```sh
sudo timeout 180 du -x -sh \
  /root /var/lib/radicale /var/lib/tailscale \
  /var/lib/docker /var/lib/containerd /var/lib/containers \
  /var/backups /mnt/fat32

sudo stat -c '%n | owner %U:%G | mode %a | type %F' \
  /etc/radicale /etc/radicale/config /etc/radicale/users \
  /var/lib/radicale /var/lib/tailscale \
  /etc/ssh /etc/sudoers /etc/sudoers.d \
  /etc/NetworkManager/system-connections
```

Missing paths, errors, and timeouts are findings, not reasons to create paths or
change permissions. Do not print password files, Tailscale state, private keys,
sudoers, connection credentials, or `/root` contents into shared output. This
limited pass will not complete the whole restore manifest by itself.

## Next-agent handoff

### Current direction — independent services/dev profiles; optional dotfiles

Owner adopted the split recorded in `~/Products/meta-analysis/DECISIONS.md` and
explicitly authorized simplifying this repository. Two headless machines now have
independent purposes: services with operational data and deliberate access policy;
a disposable dev pod for product development/testing, with agents allowed to run
as root on the pod and create sandboxes only when useful. Dev has no operational
services, personal data or durable secrets. Provider authentication/private keys
stay on the controller; harvest changes and push locally. This supersedes the
previous mandatory root-inside-existing-sandbox architecture **for dev**, not the
services host or desktop. Existing sandbox extraction remains separately owned.

Neither OS role requires personal dotfiles. Optional `chezmoi` installs just the
tool for bring-your-own sources; optional `personal-dotfiles` stages the existing
committed submodule pin for offline use. No init/apply/hooks on builder/desktop,
no boot-time source merge/reset/apply, no implicit pin advance. The never-enabled
custom chezmoi lifecycle/controller and transition-policy machinery are removed;
service configuration remains explicit and unfinished, with startup guards closed.
The service readiness marker is now tool-neutral `configuration-ready`, not proof
that a particular personal dotfiles repository was applied. No code grants it.

**Completed source-only simplification:** Arch package/snapshot/PAM foundation is
now in `mkosi.conf.d/arch`, before role/addon parsing. `mini-server-arch` retains
operator enrollment/rootless policy (65 direct packages); `dev-pod` has only the
shared foundation and a key-only root SSH policy (61 packages), separate caches/
outputs, no account/configuration/service drop-ins and no agent auto-start. Native
mkosi assertions reject combining dev with either services recipe. Select with
`scripts/mkosi-arch dev-pod summary`; the unchanged default selects Arch services.
Optional `--profile=chezmoi` installs just the tool, while `personal-dotfiles` stages
the existing committed pin/revision/manifest without running source hooks.

Removed 700 Python runtime lines (476-line lifecycle +224-line controller), their
32-line unit, 636 lines of obsolete mocked tests and the predecessor-policy code/
test. Personal source staging is opt-in; duplicate Arch finalize logic is removed
and both distros share the existing factory/root-metadata hook. Common homed masks
are now the root `mkosi.postinst`, not a services prerequisite. Services retain
key-only/no-root SSH, account journals, stable subids/linger, disabled workloads
and generic fail-closed configuration gates. No account-helper or agent-builder
changes were made in this pass; pre-existing dirty work remains intact.

Evidence: full offline suite **116 tests passed, no skips, 2.199s**. Includes native
OpenSSH config inspection with a freshly generated/deleted temporary host key;
role conflict rejection; summaries from a synthetic checkout with neither Git nor
dotfiles; services enrollment/rootless mocks; stock-label/metadata tests; opt-in
staging and isolated dotfiles rendering. Initial local failures were test-fixture
assumptions (moved paths/CLI argument shape, symlink copying and OpenSSH output/key
requirements); fixes were fixture-only, not a security relaxation. Arch services/
dev/addon and retained enforcing Fedora/addon summaries parse; shell syntax and
Git whitespace checks pass. These are **not** image/TPM/access/workload boot passes.
No build, VM launch, target apply, desktop services/packages, credentials borrowed,
submodule change, physical writes or publication. The obsolete automatic-lifecycle
action is cancelled, not marked as a successful target apply.

Next practical work is building/booting the small dev profile and performing one
root-agent task, not reattaching service/account/configuration prerequisites. Stock
systemd public-key/root provisioning must be tested in the actual guest before
claiming access works. Shared signed immutable `/usr`, TPM-encrypted root/swap,
no-reset mutable partitions, distro identity and Fedora enforcing policy remain;
root does not make immutable pacman writes supported. Production credentials/data,
host devices/management sockets, physical installation and publication stay outside
this approval. Keep bounded VM resources and owned cleanup. The old successful
image/receipts remain untouched; recovery harness stays parked. No VM is active.

### History

Earlier directions, the implementation record and validation receipts (2026-10-03 to 2026-10-06) are in
[docs/history/mini-server-build-history.md](../../docs/history/mini-server-build-history.md).

### Separate platform feedback

`~/Products/platform` has a Support Ergonomics action with stable alias
`deduplicate-cli-warnings`. It is now about routing background workspace-health
findings through doctor/explicit repair, not merely deduplicating stderr. Read
that repo's `AGENTS.md` and the action before continuing it. The installed
`clearhead_cli 0.2.1` printed three distinct identity warnings twice within one
successful invocation; its build revision was not matched to source. Keep
operation-blocking errors visible and avoid automatic identity repairs.

An earlier handoff recorded edits to platform's `support.actions` and
`support.md` in commit `2eb1b3d`, without implementation/specification changes.
That is historical context, not a current HEAD or cleanliness assertion. This
fork-scaffolding session made no platform changes; the owner is working on
releases separately. Inspect current state and its AGENTS before any separately
agreed follow-up, and do not repair that work merely to provision this server.

## Log

- 2026-10-01T22:29-07:00 — Local VM passed UEFI boot, SSH, sudo, SELinux,
  bootc switch/reboot/rollback and persistence. USB SMART reads need sudo.
  No mini-server disks, mounts or configuration have been changed.
- 2026-10-01T22:47-07:00 — Read-only scout: home is about 556 GiB with
  namespace-aware reads; 87 readable Git roots include local work and five
  chezmoi stashes. Rootless volumes persist despite no containers. Technical
  findings are in os/mini-server/INVENTORY.md; privileged reads need sudo.
- 2026-10-01T23:56-07:00 — Operator checklist prepared; now consolidated above.
- 2026-10-02T00:20-07:00 — SMART counters clean; extended tests pending.
- 2026-10-02T00:24-07:00 — Owner opts out of extended SMART tests.
- 2026-10-02T00:26-07:00 — Planning only; implementation awaits go-ahead.
- 2026-10-02T00:45-07:00 — Plan/handoff now live in this charter.
- 2026-10-02T14:59-07:00 — Owner separately approved targeted read-only SSH review of ~/arch_desktop only. Small mkosi Arch experiment with local source changes; generated artifacts dominate space. Findings in os/mini-server/INVENTORY.md. No credentials read, image mounts, backups, deletion or server changes; broader SSH/privileged inventory remains gated.
- 2026-10-02T15:45-07:00 — Owner authorizes focused inventory and limited cleanup, with chezmoi authoritative and small gaps acceptable. Selected live configs match source; rclone disabled, old weekly backup timer still enabled; sudo requires operator. Removed only retired /home/dab/arch_desktop with path/mount checks. No other data/services/disks changed; no build/backup/install approval.
- 2026-10-02T15:47-07:00 — Verified operator retirement of old system-backup timer: inactive/disabled, service inactive. /mnt/fat32 is a real root-owned directory with no mounts at/beneath; operator deletion still pending. No further files deleted.
- 2026-10-02T15:49-07:00 — Verified owner removed retired /mnt/fat32; both it and /home/dab/arch_desktop are absent, and old backup timer remains inactive/disabled. Agreed two-target cleanup complete; other server data untouched.
- 2026-10-02T16:31-07:00 — Owner approved local image/service builds and isolated VM validation. Expanded Fedora44 image passes bootc lint and nine synthetic container tests; native Radicale/Collector, restic/RAID tooling and access-policy drop-ins added. VM disk build blocked by desktop kernel/module mismatch; in-VM fallback stalled/stopped. All scratch credentials/artifacts removed; local tags retained. No production disk/build deployment/backup/reboot changes.
- 2026-10-02T18:36-07:00 — Owner chooses a trimmed ParticleOS fork with pinned chezmoi submodule, staged at build and automatically applied on the real target after build. Initialized local `~/Products/personal-os` with upstream provenance, committed dotfiles pin, README/AGENTS, server overlay, canonical charter/history and bootc reference. Three offline configuration tests pass; default Fedora44 target/initrd selection verified, including protection against host-Arch fragments; ClearHead doctor has no findings. No new image/VM, personal remote/push, production signing keys, storage writes, backups, install or server changes. Target-side first-boot integration and trimmed storage/account/security defaults remain implementation work for the next session here.
- 2026-10-06T21:31-07:00 — Owner requested an experimental artifact task. Arch Island generated and deterministically reproduced inside fresh bounded Arch VM arch-art-97ga86v3, served via rootless nginx, retrieved and checksum-verified at ~/Downloads/arch-island-arch-art-97ga86v3/index.html. Native shutdown and independent owned cleanup passed; no VM active. No rebuild, publication, production identity or nested-agent claim; detailed receipts and next direction in handoff.
- 2026-10-06T21:37-07:00 — Owner feedback after artifact experiment: cut the ceremony down; this has been too much. Default to boot, useful work, retrieve result, native shutdown and owned cleanup. Preserve short resource/concurrency, integrity and credential safeguards; broad suites only for relevant changes or observed failures. Narrowly simplify existing wrappers when next used, not another harness/orchestration/refactoring project.
- 2026-10-06T21:46-07:00 — Shorter-loop arch-work-63phfdf7 reused unchanged successful image/controller/helper regression evidence without suite reruns. Inside Arch, synthetic authenticated Radicale CalDAV/CardDAV artifacts survived container restart byte/ETag-identically; retrieved and verified at ~/Downloads/dav-workshop-arch-work-63phfdf7/index.html. Native shutdown/independent cleanup passed; no VM active. Existing sandbox UID1000/login snapshot mismatch left untouched; no nested-agent claim. Details in handoff.
- 2026-10-08T00:08-07:00 — Owner-approved independent services/dev roles and optional BYO dotfiles implemented source-only. Dev root access uses stock systemd public-key provisioning without services/account/configuration dependencies; removed 700-line automatic chezmoi lifecycle/controller and obsolete tests/policy. Full offline suite 116 passed; no image build/boot, credentials borrowed, host/production changes or publication. Next useful dev VM task; old baselines intact and recovery parked.
