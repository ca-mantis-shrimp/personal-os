# Personal OS agent instructions

## Read first

1. `README.md` — repository purpose and current scaffold limitations.
2. `.clearhead/charters/mini-server.md` — canonical decisions, permission scope,
   retained test evidence and **Next-agent handoff**.
3. `.clearhead/charters/mini-server.actions` and the paired completed file.
4. `docs/PARTICLEOS-UPSTREAM.md`, then the relevant mkosi configuration and
   upstream documentation before implementing changes.

Use ClearHead from this repository root. Do not introduce another PLAN,
NEXT-STEPS or parallel migration handoff. Preserve the charter `.md`, `.actions`,
`.completed.actions` and tool-managed `.mini-server.json` together.

## Ownership and source composition

- This fork owns OS packages, partitions, update/boot/recovery policy and target
  bootstrap integration. `dotfiles/` owns user configuration as a pinned submodule.
- Stage committed dotfiles during image creation; run chezmoi initialization/apply
  only on the actual target, as the intended user, after account/home/hostname
  provision. Reuse chezmoi's existing conditional mechanisms.
- The dotfiles package hook is mutable-Arch-only with container/immutable guards.
  Preserve those guards before target-side application. Do not execute it on the
  builder, run `chezmoi apply` against this desktop, or add a competing bootstrap
  system. OS package installation belongs to the
  image build; machine/distro guards must also suppress package-installing hooks
  on immutable targets, including any future Arch image profile.
- First-boot/update handling must preserve edits and existing mutable data, allow
  safe retries, record the applied source revision, and keep dependent services
  stopped after failed/incomplete configuration. Do not force-reset a writable
  chezmoi source checkout on every boot. OS rollback does not restore mutable
  home/application state; test configuration/schema compatibility and independent
  state recovery, including what an older pinned dotfiles source may safely do.
- Do not import `.git` histories, ClearHead plans, caches, builds or credentials
  into the staged user configuration by copying an entire live checkout blindly.
  Review the committed build payload and test target-side rendering.
- `dotfiles/.clearhead/` is a pinned historical snapshot, **not** this repo's plan.
  Do not normalize it, register it as an additional workspace or silently advance
  submodules. Do not edit the separate live dotfiles checkout accidentally.
- ClearHead release work is separate in `~/Products/platform`. Read its own
  AGENTS before any work there; migration does not authorize source/branch changes
  or replacing the desktop's installed CLI.

## Permission scope

Local fork/profile implementation, builds and isolated synthetic VM tests are
approved. No production storage formatting, RAID creation, backup execution,
installation/flashing, public publishing, production service change or reboot is
approved. Exact physical disks require explicit confirmation. Never pass a real
host disk/USB caddy to a test VM or run cloned production identities.

Keep SELinux enforcing; a container test is not a booted SELinux/console/rollback
pass. Do not disable security to make a test work. Keep credentials, hashes,
private signing keys, B2 keys, 1Password service tokens and device identities out
of Git, images, shared command output and logs. The approved console passphrase
and runtime secrets come from 1Password, not image source.

The active fork is Fedora 44 plus mini-server with a Fedora 44 headless tools
tree. Inactive upstream desktop/distro/OBS/demo/UKI examples are preserved in
`reference/particleos/`; do not re-enable them implicitly. Only the normal signed
UKI is currently built: replacement installer/rescue access is still a gate.
TPM-encrypted Btrfs root/swap, unencrypted Btrfs home and signing/PCR requirements
remain; mutable partitions are not factory-reset candidates and Secure Boot
keys are not auto-enrolled. Homed is masked; conventional-account/configuration
prototypes remain unbooted and automatic configuration stays disabled. Before
builds, understand what mkosi will do; use profile summary/config inspection.
Production signing-key generation and Secure Boot enrollment need a separately
agreed custody/recovery policy.
Disposable isolated VM test keys are permitted as part of approved synthetic
testing; keep them outside Git, remove them afterward and never reuse them for
production.

## Tool and workspace care

Read source before changing it; prefer small owned configuration changes and
preserve useful upstream examples outside active discovery rather than deleting
them blindly. Keep update/rollback coupling between `/usr`, verity and UKIs.
`ImageId=PersonalOS` matches discovery filters and `%M` artifact/partition patterns.
Preserve Fedora programmatic identity and the ParticleOS ancestry token used by
the pinned dotfiles' immutable guards, plus the immutable marker/environment guards.
Avoid wholesale filesystem archaeology: owner accepts small reconstruction gaps
and wants generic reprovisioning, with only significant unique state retained.

The installed ClearHead CLI has emitted identity warnings and has auto-stamped
historical completed rows on mutation. Do not invent completion dates or repair
unrelated identities. Inspect diffs after CLI writes. Keep actual new completion
dates, and leave historical I001 notices informational. Do not hand-edit UUIDs or
tool-managed sidecar identity/provenance.

The 2026-10-03 disposable Personal OS builder and software TPM were stopped;
all their credentials/signing keys, VM state and build scratch were removed.
The first pre-Podman candidate built, but latest rootless/account changes are
unbuilt and no candidate boot pass exists. Use fresh isolated artifacts; load
matching stock target policy modules in an enforcing builder before relabeling.
Sandbox extraction is delegated to another agent; do not interfere with its
workspace/processes or invent another launcher. The desktop was owner-rebooted
and kernel/modules now match; do not reboot it automatically.
