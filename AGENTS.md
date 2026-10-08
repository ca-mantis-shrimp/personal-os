# Personal OS agent instructions

## Read first

1. `README.md` — current scope and entry points.
2. `.clearhead/charters/mini-server.md` — canonical decisions, approvals, evidence
   and **Next-agent handoff**. Read the latest direction before historical notes.
3. `.clearhead/charters/mini-server.actions` and `.completed.actions`.
4. `docs/PARTICLEOS-UPSTREAM.md`, relevant mkosi configuration and upstream docs
   before implementation changes.

Use ClearHead from this repository root. Preserve the charter, paired actions
and tool-managed `.mini-server.json` together. No additional PLAN/NEXT-STEPS or
parallel handoff. Do not hand-edit UUIDs/provenance or invent completion dates.
Inspect diffs after CLI mutations; historical I001 notices are informational.

## Current direction

This is an experimental homelab for **agents to do useful work**, not a production
certification project. Prioritize **SIMPLICITY, FLEXIBILITY and RESILIENCY**.
The owner explicitly requested less code/edge-case machinery and iterative use.
Keep safeguards proportional; explain scope/cost before expanding validation.
Prefer existing distro tools over new orchestration. The owner now separates
services and product development onto independent machines/profiles (architectural
decision in `~/Products/meta-analysis/DECISIONS.md`). Services owns operational data
and deliberate service configuration. The disposable dev pod has no operational
services, personal data or durable secrets; agents may run as root on that machine
and create sandboxes only when useful. Neither role requires personal dotfiles.
Focus next on useful root-agent work in a bounded dev VM, not service readiness,
a sandbox-integration prerequisite or another recovery/refactoring project.
Existing sandbox extraction remains separately owned.

The frozen Arch candidate passed isolated first boot, credential-free persisted
reboot, key-only SSH/sudo, rootless Podman/unshare, encrypted-root TPM re-unlock,
identity/home-edit preservation and native operator console-password login/logout.
Both successful baselines and failed receipts remain private and separate; exact
identities/hashes are in the charter. The bounded arch-play-7oit0hm4 session also
passed native service lifecycle and real rootless container data/nginx HTTP.
It has ended with clean native shutdown and independently verified owned cleanup;
no VM is active and its temporary SSH command is no longer usable. Later artifact
and synthetic Radicale experiments also passed and ended cleanly; see the charter.
The dev-pod profile passed one build and booted root-access pass (2026-10-08, see README);
the services profile split has only offline checks.
These passes do **not** prove
TPM-loss recovery, updates/rollback/rescue, backup restores or schema compatibility.
Services/shpool remain disabled or gated; Arch agent payloads are still deferred.
The never-enabled automatic chezmoi lifecycle/controller has been removed.
Do not claim the image is installed or installation-ready.

The unfinished `arch-tpmloss-tgw231na` private draft is **parked**. Its final local
suite passed 108 tests with one explicit remote-only TPM skip (109 collected).
It has not been frozen/staged/booted for recovery. Its former freeze/stage/launch
entry points now refuse execution; originals are preserved privately under
`deferred-wrapper-sources/`. Retain it as evidence, not production OS code.

## Permission and security boundaries

- Local fork/profile changes, builds and isolated synthetic VM tests are approved,
  subject to the owner's latest pause/priorities. No production formatting, RAID
  creation, backup execution, installation/flashing, publishing, service changes,
  host package installation or reboot without separate approval. Exact physical
  disks require explicit confirmation.
- Never pass a host disk/USB caddy to a VM or clone production identities. Keep the
  external homed drive excluded. Use disposable file-backed disks, firmware, TPM
  state and credentials; bound resources and independently verify owned cleanup.
- Preserve failures and working baselines. No unchanged cold retries, competing
  VMs, resource polling, shrinking limits or stopping unrelated work to fit a test.
- Keep passwords/hashes/private keys/B2 keys/1Password service tokens and device
  identities out of Git, images, arguments and shared logs. Production passphrases
  and runtime secrets come from 1Password, not image source. Disposable VM keys
  stay outside Git, are removed afterward and never become production keys.
- Signing/PCR policy, coupled `/usr`/verity/UKI updates, TPM-encrypted root/swap,
  unencrypted Btrfs home and no-reset mutable partitions remain. Secure Boot keys
  are not auto-enrolled. Production key custody and installer/rescue access are
  unresolved. Deferring tests does not remove these requirements.
- Keep Fedora SELinux-enforcing. Explicit Arch intentionally has no SELinux;
  this is an architectural choice, not a Fedora bypass. Do not mask failing
  services, disable encryption/security or manufacture readiness to pass a test.
- Agents may run as root on the **disposable dev pod**, not on this desktop or
  services machine. Sandboxes are optional tools there, not a mandatory wrapper.
  Root inside a dev VM must not imply desktop sudo, devices or management sockets.
  Keep provider authentication/private keys on the controller; harvest/push locally.
  No dedicated/per-agent host user or new launcher is required. Do not interfere
  with separately owned sandbox extraction. Shpool is not an isolation boundary.

## Ownership and bootstrap

- This fork owns OS packages, partitions, boot/update/recovery policy and target
  integration. `dotfiles/` is pinned user configuration. Never silently advance
  it or edit the separate live chezmoi checkout.
- Dotfiles are opt-in, not OS bootstrap. `chezmoi` installs only the optional tool;
  `personal-dotfiles` stages the committed gitlink without histories/plans/caches/
  builds/credentials. Never run init/apply/hooks on the builder or this desktop.
  Review source/hooks and apply only on the target as its intended user; dev sources
  must not introduce personal secrets/data or operational services.
- OS packages belong in the image. Preserve mutable-Arch-only package hooks and
  their container/immutable guards, including on immutable Arch targets.
- Services-role accounts use `personal-os-account.service`, not manual users or
  ready markers. Preserve password/key edits, stable subids/linger choices and
  existing mutable data; allow safe retries without resetting established state.
  Dev root access uses stock systemd runtime public-key provisioning.
- Optional configuration is an explicit target operation: record its revision,
  preserve edits and keep dependent services stopped on incomplete/failed apply.
  No boot-time apply/reset or custom lifecycle controller remains. Services still
  require `/run/personal-os/configuration-ready`; no implementation grants it.
  Do not manufacture readiness. OS rollback does not restore home/app state.
- `dotfiles/.clearhead/` is historical, not another active workspace. ClearHead
  release work belongs in `~/Products/platform`; read its AGENTS before work
  there. This task does not authorize source/branch changes or replacing the
  desktop's installed CLI.

## Build and workspace care

Plain mkosi selects retained Fedora 44 + mini-server with Fedora tools. Use
`scripts/mkosi-arch` for Arch services or `scripts/mkosi-arch dev-pod` for the
independent root-agent role. Both use shared Arch distro fragments and dated
2026/10/04 target/initrd/tools, with separate dev caches/outputs and no npm/Cargo
hook. Services enrollment passed in the old image; dev access is not boot-tested.
Chezmoi and personal snapshots are optional profiles, never build prerequisites.
Fedora candidates and inactive examples in `reference/particleos/` stay intact, outside active discovery.
Only the normal signed UKI is built; do not implicitly enable installer/debug/
factory-reset/demo profiles. Do not boot retained Fedora as the default next step.

Inspect profile summary/configuration before builds. Preserve `ImageId=PersonalOS`,
partition/discovery patterns, distro identities/ParticleOS ancestry and immutable
marker/environment guards. Keep public image-tree permissions separate from
private builder/key/state protections. Use matching stock policy in enforcing
builders; never relax relabeling to pass.

Read source before edits; prefer small owned changes. Preserve pre-existing dirty
work and upstream provenance. Avoid exhaustive filesystem archaeology: retain
significant unique state and favor generic reprovisioning. LSP silence is not a
confirmed-clean result. Await background terminal notifications rather than poll.
The desktop was owner-rebooted and kernel/modules match; do not reboot it yourself.
