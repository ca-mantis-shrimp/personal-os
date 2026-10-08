---
title: Mini-server build history and evidence
description: The mini-server charter's earlier directions, implementation record and validation receipts, through the 2026-10-06 simplification. Moved out of the charter on 2026-10-08 so the charter carries only the current direction.
---

# Mini-server build history and evidence

Moved verbatim from `.clearhead/charters/mini-server.md` (Next-agent handoff) on 2026-10-08. The current direction
lives in that charter; this is the record behind it. Headings keep their original levels.

### Previous direction — 2026-10-06 owner simplification

**Latest owner feedback after Arch Island:** “we need to cut the ceremony down
this has been too much”. Make the default experimental loop boot → useful work →
retrieve result → native shutdown/owned cleanup. Keep short resource/concurrency,
input-integrity and credential safeguards; broad regression suites belong with
relevant code changes or observed failures, not every unchanged-image experiment.
The `arch-work-63phfdf7` launch wrappers now reuse the verified prior regression
receipt when controller/helper hashes are unchanged; no local/remote suites were
rerun. Fresh input/resource/concurrency gates, the existing native guest lifecycle
and independent cleanup remain. Controller/image/security policy unchanged; no
new orchestration. This trims repeated suites, not the entire remaining launch
ceremony. Do not turn further simplification into another refactoring project.

**Latest shorter-loop useful work:** fresh bounded `arch-work-63phfdf7` passed
native boot/reboot/console gates, then ran authenticated **Radicale3.5.7** in a
rootless Python container inside Arch. Synthetic CalDAV event and CardDAV contact
creation/retrieval passed; anonymous protected-path access was rejected. Both
contents and ETags survived a container restart; guest data ownership stayed1000.
Returned checksum-verified bundle:
`/home/backup-admin/Downloads/dav-workshop-arch-work-63phfdf7/index.html`
(with ICS/VCF, package versions, workload receipt, README and SHA256SUMS). Service
container/test credentials removed, then native VM shutdown/clean QEMU+TPM exits
and independent owned cleanup passed. **No VM is active.** No OS rebuild, image
package installation, automatic configuration, production identity or publication.
Protected local/remote receipts remain under `~/.cache/personal-os-validation/arch-work-63phfdf7`;
final session SHA256 `5568b4ab67338a5933939dfdd6b342a572fcd0bfe959c82da230857f656e5182`;
workload receipt `d402b24fcdab2c429a3c76b3a96b5eb3cdb31f8f8c657c1a6985473c85e69c0b`.
This is a temporary service workload, not native Arch Radicale integration.
The inspected existing sandbox snapshot `2ba8bf43dd0e6a47f8002abb0df520dd831dc22a`
still uses UID1000/keep-id and its own Pi login/Claude token, unlike the requested
root-inside-sandbox architecture. It was read only, not changed or launched;
no host authentication was borrowed. A nested autonomous-agent pass remains open.

**Previous useful-work experiment:** owner requested “just do something experimental,
maybe have it make some artifact to bring back or push something”. A fresh private
`arch-art-97ga86v3` reused the unchanged successful Arch image/controller/helpers
and bounded interactive session, without rebuilding or resuming recovery work.
Local81pass/1explicitTPMskip and remote82pass/no skips; resource/firmware/hash gates
passed (available RAM27,696,472,064B, free disk155,491,065,856B). Native first boot,
credential-free reboot, console login/logout and account/rootless gates passed.
Inside the guest, a bounded native user service generated **Arch Island**, a
self-contained SVG/HTML procedural scene with580land tiles/82trees and reproducible
Python-standard-library source. A second guest render matched every file byte-for-
byte. Digest-pinned rootless nginx served all six files identically over guest
loopback, then was removed. Key-only SSH retrieval and local SHA256SUMS verification
passed; SVG parsing/offline-page checks and local preview rendering also passed.
User artifact: `/home/backup-admin/Downloads/arch-island-arch-art-97ga86v3/index.html`
(with SVG, source, scene JSON, README and checksums beside it). No publication,
production state/identity, automatic configuration or new image payload. This is
an artifact-making OS workload, **not** a nested autonomous-agent or existing-
sandbox-integration pass; Pi/shpool/intended homelab services remain absent.

The session was deliberately ended after retrieval through its existing stop
marker: native shutdown, clean QEMU/TPM exits and independent owned-scope/temp-state/
credential cleanup all passed. **No VM is active and its temporary SSH key is gone.**
Protected local/remote receipts and sanitized logs remain under
`~/.cache/personal-os-validation/arch-art-97ga86v3` (0700/0600).
Final results SHA256 `58effd522e82cdd216118c350191831dc71833fa48579ca3f2cf8e147e403f76`;
artifact receipt `1f7f17df236aebd244ecc367506ab90b8c5df951119958184dbd09e64243eccc`;
returned HTML `2f71ed7ee3484ff265eb4c64b6b67e216e54ce8deee2e7cbad89c10dcc20fd8b`.
Prior successes/failures stay untouched. Next remains a useful intended workload
or agent task with only its needed Arch tools, reusing the separately owned sandbox;
not another recovery matrix or automatic unchanged VM retry.

**Owner clarified the practical milestone:** “get the vm running and play around
in there, get the systems running etc and make sure they work from in the vm.”
Boot the already successful Arch image for a bounded hands-on guest session, not
an unrelated repo task. Start with native services and actual rootless containers;
report missing workload payloads honestly and fix observed gaps. No image rebuild
or recovery expansion is indicated just to make the VM available. A fresh private
arch-play-7oit0hm4 fork adds only a hold-open option after the successful boot/reboot
and console gates; original successes and parked recovery code stay untouched.
Initial usable session20minutes, original RAM/CPU/no-swap envelope unchanged;
reboot scope30minutes/TPM40minutes and supervisor45minutes bound the session and
cleanup. Fresh integrity/resource/native prerequisites still apply. No physical
installation, host changes or production identities/services are authorized.
Preparation/launch b589f91cf COMPLETED0: local81pass/1explicitTPMskip, all82 remote
passed2.859s including native TPM restart and the two new stop/expiry fixtures;
public-only staging/hash/firmware/port/hygiene passed, RAM27,751,342,080B and disk
155,494,301,696B passed unchanged resource gates. One deliberate VM reached READY:
full first boot/credential-free reboot/native guest checks/console proof/logout
passed again. Fresh synthetic key/state used private arch-target-br3q0zf4 and
homelab-loopback SSH22265; owner received a nested SSH command for the20minute
usable session. It has now ended: watcher b5900e9e5 COMPLETED0, native clean
shutdown PASS and independent owned-scope/temp-state/credential cleanup PASS.
Both QEMU/TPM exits clean; controller passed/interactive_session_completed/
cleanup_confirmed all true. No VM is active; the temporary SSH command is expired.
Final private results5414B SHA591b302d380d354de0db53c5c5d9123b1347620e55663106699b8ed1a29b6c82;
guest service/container proof SHAfefb4bded6e25bcc0eae1277392c0cc35856a5549fca8ea125fcac9870deabf5.
Local/remote arch-play-7oit0hm4 results and sanitized console/QEMU logs retained
0700/0600; old successes/failures remain separate. Actual guest service/container
exploration b276c89be FAILED at the demo web command, not boot: guest system state
running/no failed units, native HTTP service start/restart/stop passed; real Alpine
rootless container ran as namespaceUID0 with scoped data owned by guestUID1000.
Native diagnosis: container network creation returned0, but Alpine3.23 BusyBox
reports `httpd: applet not found`/exit127. Initial report/source retained privately;
no VM restart/security change. b0492e845 FAILED its immediate nginx HTTP check:
native same-guest diagnosis confirms nginx start0/running/noOOM/ready workers,
but immediate curl55/reset (not refused). Protected reports/source/diagnostic
retained; previous check retried only refused connections. One bounded native
readiness flag correction `--retry-all-errors` completed b982778c3 exit0, SAME VM:
all guest checks PASS, including actual nginx Welcome HTTP via rootless guest
loopback mapping, namespaceUID0/scoped data owned guestUID1000 and test-container
removal. Digest0985e772fb9f729e6fa0980da05fca5d9c468e870eed43071545afa9d2e27d94;
Alpine digest1f3591b8a02ea153f41c5bba878ad477f63ab3d19349762cb77504db02a23e15.
No image rebuild/VM restart/OS security change. A separate personal-os-demo-nginx
container was left running/HTTP checked at guest http://127.0.0.1:18081/ for owner
hands-on use until the original session expired; it is now gone with the VM.
No host port exposure beyond SSH, startup enablement, production identity or
readiness marker. Tailscale/Syncthing/Radicale/shpool/pi are absent from this
minimal image: the next practical gap is intended Arch service/agent composition,
not another fault-test matrix. No automatic unchanged VM retry or recovery resume.

**This direction supersedes the historical recovery continuation below.** The owner
said the purpose is for agents to use the system, with iteration rather than an
exhaustive pre-use validation project, and explicitly requested less code for
minimal edge cases. Stop expanding the private recovery/fault-injection harness.
Do not automatically freeze, stage or launch it, or replace it with another large
refactor. Keep the already working Arch baseline and move toward one useful agent
task using the existing sandbox and a scoped workspace. Add only tools needed for
that task, reuse native tooling, and fix observed problems with focused checks.
Automatic configuration, extra workloads and new orchestration are not prerequisites
for this milestone; their prototypes stay deferred, not bypassed with ready markers.

The frozen candidate passed isolated first boot, credential-free reboot, key-only
SSH/sudo, rootless Podman/unshare, stable identity/home/key edits, TPM encrypted-root
re-unlock and native operator console password login/UIDGID1000 proof/logout.
Protected successes: arch-tpmfix-9fyvy41d/b106cbd9f and
arch-consolelogin-nycy11kw/b3416d8ae. Both clean shutdowns and independent owned
cleanup passed; no VM was retained from those attempts. Preserve these baselines, all eight failed boots,
failed preflight and their evidence. Exact hashes/limits remain recorded below.

The 3,139-line private arch-tpmloss-tgw231na draft is validation code, **not image
payload**. Its last controller regression bf21110b2 passed108 tests2.969s/1explicit
remote-only native TPM skip (109 collected); b6d88552d passed100+skip2.944s (101,
not the previously predicted102). The controller/guest probes/hashguards were
subsequently integrated locally, including existing root+swap key prerequisites
and an original-state-inert hardware-absent third phase. These are mocked/offline
results, NOT a recovery boot. Partial freeze/stage wrappers were updated109 but
launcher remained inherited80; nothing was staged/launched from this draft.
The three original wrappers are now retained byte-identically under the private
`deferred-wrapper-sources/` directory (0700/0600); their former entry points are
three-line refusal stubs. No recovery staging or VM can be started through those
entry points. Runtime/controller/tests and successful baselines were not altered.

Simplification does not waive signing/encryption, credential protection, safe edit
preservation, sandbox isolation or physical-installation approval. Recovery/update/
rollback/rescue/backup-restore/schema compatibility and physical microcode/key/
storage readiness remain unproven. Root header acceptance does not establish swap
recovery. Do not remove policy, mask failures or claim missing tests passed.

This pass trims duplicated/stale instructions from AGENTS/README; chronological
results stay here. Most newly added code was private validation (3,139 lines), not
image payload; its unfinished launch orchestration is now explicitly inactive.
OS runtime code/image/security policy and paired/tool-managed ClearHead identities
remain unchanged. Avoid another validation/refactoring marathon
before a real agent-use task shows what is actually needed.

### Historical implementation and retained evidence

**Latest Arch continuation (2026-10-05, historical):** owner approved the proposed adaptation
→ one controlled build → basic VM access/reboot milestones, not production disk
writes or installation. Earlier `be6892b2f` completed with all 150 tests passing.
The stock Arch link/public-directory map and identity-selected account relabel
adapter are now present. Native PAM is retained in `/etc/pam.d` with a non-replacing
factory link, because stock Arch PAM is built without a vendor-directory fallback.
Fedora-only agent wrappers moved to explicit `mini-server/mkosi.agent-extra`;
Arch now cannot overwrite repository Starship with an absent-payload wrapper.
Target/initrd/tools select dated Snapshot=2026/10/04, keeping signature checks on
and repository-key fetching off. Corrected configuration preset name is
personal-os-configuration.service; activation still disabled.

First expanded offline run `bdfda962c` failed only the new PAM test fixture's
comment extraction. Production script was not changed to satisfy it. Corrected
fixture rerun `ba222784c` COMPLETED: all 159 tests passed in 1.801 seconds. Active
LSP checks on changed Python tests/bootstrap report no primary errors. Native
Arch bridge `b7759d1b6` failed at the fixture's missing CAP_FOWNER: root must fchmod
its newly user-owned atomic key file. Only that capability was added to the
networkless NNP fixture, alongside CHOWN/DAC_OVERRIDE; target service policy and
account code were not changed. Corrected bridge `b07514717` COMPLETED: actual
Arch account/hash/visudo/libsubid/repeat-preservation/Shadow-lock checks passed.
Stock versions: filesystem2025.10.12-1, shadow4.20.0.arch1-1, pam1.7.3-1,
pambase20260616-1, systemd262-1, pacman7.1.0.r9.g54d9411-2, python3.14.7-1,
sudo1.9.17.p2-6, openssh10.5p1-1. Normal enrollment created the fixture account;
only hostname/logind RPCs were mocked. This cannot prove boot/login, real linger
or rootless namespaces. The owned container/image were removed; no host account
was changed. Arch enrollment preset is now enabled for isolated boot validation;
configuration/shpool/workloads remain disabled/gated.

Snapshot check `bc1b1b1f0` failed on virtual udev; core metadata proves systemd
provides udev=262. Provider-aware `b738e5884` then found ambiguous virtual man in
the inherited tools profile. Arch ToolsTreePackages now explicitly selects man-db
(target remains66 selections). Third review `bf18a8cb9` COMPLETED: all direct
main66/initrd16/tools59 selections resolve in dated core/extra metadata, with
checksums and signature metadata. Bootstrap keyring matches that dated record.
Metadata SHA-256: core `373a91595792d33d02ef809742d109db27b2a5039152904f808f7943f6d0b6cb`;
extra `823815022358b353e960223ea9d6abdfdf916b166d223c9190e71adcb9702cc9`.
Recorded target kernel is linux7.2.8.arch1-2; Podman6.1.3-1. This is metadata/provider
availability only, not full dependency closure, actual target signature verification
or installed size. Signature checks remain required during the build.

Private scratch: `/home/backup-admin/.cache/personal-os-validation/arch-first-eyTioWOX`.
A VM-only harness adapted from the retained enforcing Fedora builder is prepared
but UNRUN: no image build, VM, signing keys or runtime enrollment credentials
have been generated. Public Arch bootstrap keyring 20260909-1 passed detached
signature verification against the desktop's existing trusted keyring. Freeze
only after native/snapshot/regression gates; retain scoped public 022/private
0700+0600 protections and resource preflight. Source patch was frozen with a
temporary Git index (real index unchanged), SHA-256
`e7127130ad3910a52e71707ef536e9ba3f3627093d7183fd128f15e17f09134c`.
Replay/regression task `bf68dc2ff` COMPLETED: clean bundle/patch replay, public
extra-tree modes and all159 tests passed in1.300 seconds on that exact frozen
input. The replay checkout was removed. `validation-input.json` now records the
accepted terminal evidence and updated preflight hash; launcher refuses an
unaccepted source gate. Native harness policy checks passed normal022/private modes and rejected077/exposed-key/exposed-
parent cases; frozen hashes, free port and187.7GiB scratch passed. Resource gate
BLOCKED: available RAM5.83GiB, required6.5GiB for the retained5GiB guest envelope.
No keys/seed/VM were generated. Do not shrink limits, stop desktop/another agent
or start a polling/wait job to force a launch. Recheck deliberately only after
headroom is available; do not make another cold build attempt without preflight.
Frozen patch remains unchanged; no VM/key/seed state exists. All retained
artifacts and the external homed drive remain excluded/unchanged. Configuration/shpool stay disabled
throughout core-host validation. See subsequent result updates before acting on this in-flight note.

**Remote build approval:** owner offered the homelab over SSH, then said "yea on
either" after the isolated-VM proposal. This authorizes the one controlled build
on either machine, not installation, production services/storage or privileged
mkosi against the live host. Selected `dab@mini-travel-server`: read-only checks
found12CPU threads,25.9GiB available RAM,152GiB free home filesystem space,
accessible KVM, QEMU/mkosi/Python/Git and firmware/seed/signature utilities already
installed. A native64MiB transient user-scope probe passed; no tool installation
or production service change was needed.

Fresh remote private scratch:
`/home/dab/.cache/personal-os-validation/arch-build-mkNQRnaj` (0700).
Transfer/preflight task `ba99b4f2e` is running with an explicit frozen-source/public-
input allowlist and128Mbit/s transfer cap. No live home, auth, credential store,
prior VM variables or signing keys are copied. No remote VM/key/seed is prepared
until transfer hashes and the remote native preflight pass. The remote harness
uses a path-relative launcher, disables SSH agent/X11 forwarding and user config
inside VM connections, handles HUP/TERM through owned cleanup, and adds an80min
VM lifetime cap. Guest remains5GiB/4vCPU, host scope6GiB/350%CPU/no-swap, build
scope4GiB/300%CPU/one hour. All disks are regular files; no NVMe/USB/device
passthrough. Stock Fedora builder remains enforcing; Arch image deliberately
has no SELinux. Frozen payload patch and build.sh are byte-identical. Python/Bash
syntax and a synthetic interruption/finally probe passed; active private-script
LSP had no reported errors but was inconclusive (push-only), not confirmed clean.
Transfer task `ba99b4f2e` COMPLETED: source/bootstrap hashes and native remote
preflight passed. Retained remote receipt reports25.68GiB available RAM and151.4GiB
free scratch; all scoped-umask/private-mode cases passed, port free, hashes matched.
Build task `b0a2f16fb` COMPLETED (exit0), full runner243.4 seconds: stock builder
Enforcing check, actual022/private modes, metadata-only Arch skeleton staging,
signed usr/verity/signature coupling and UKI sbverify all passed. This is the
first Arch build pass, not a target boot pass. Raw logical size is reported2.1GiB,
original mkosi allocation822.4MiB; UKI reported116.1MiB. Exact verified export
bytes/package count appear below. Remote checksum recheck:
raw `fa9f5e85cc7b04161c71974a372b0e409efae20df42f128db35e21354c6b1728`;
UKI `c6ba8f902474ead807c850b0af56b88efbb89eabd8ddd0c1cc2295d55fb97e5f`;
manifest `8371232feff68fca71630368b2b8b03948678bfdd79d6470221e695c1fbd9a16`.
Independent remote hygiene check confirms the owned builder scope is stopped
and disposable disk/firmware/SSH keys/seed/QMP state absent. Private public
artifacts remain under the remote scratch, never a published release.

Local export/verification task `bf05f3119` COMPLETED exit0. Private destination:
`~/.cache/personal-os-validation/arch-first-eyTioWOX/remote-artifacts/`.
All three hashes matched, exact Arch identity/direct snapshot versions and
absence of gcc/rust/cargo/clang compiler packages passed. Independent local
sbverify passed against the exported disposable public certificate. Manifest:
224 runtime packages; raw logical2226045440 bytes, UKI121750504 bytes. Receipt
`export-receipt.json` is retained. No private keys or VM state were exported.
Installed-size caveat: mkosi27.1's Arch manifest implementation sets size=0;
do not sum those zeros or infer installed size from raw/SCP allocation. Build
warned that amd/intel microcode files were absent; review the physical-target
firmware/microcode composition before installation, not a claim of hardware
readiness. One deliberate desktop target-resource probe found4.1GiB available
RAM, below5.5GiB required for a4GiB guest/5GiB scope. Do not force a launch,
shrink limits, stop other work or poll resources. Remote swtpm/dump.erofs commands
are absent, but read-only inventory found existing libtpms0.10.2/json-glib/SSL/GLib,
Python3.14.7, glibc2.44 and Podman; a privately extracted utility may be viable
without installing host packages. Task `b18d64deb` COMPLETED exit0: frozen
extra.db hash, package SHA256, native REQUIRED pacman signature verification
(db-only/no-scriptlet in pinned networkless disposable container), data-filter
extraction passed. swtpm0.10.2 package SHA256
`e2c91249a83e75a2aa45d8009bc651eb2860e40d9cd2e6861fff57670471dd7f`;
receipt in local `private-tpm/receipt.json`. No host package DB modification.

Remote probe `bae4b362c` FAILED exit1 at the initial dependency guard, BEFORE
TPM fixture/state/scopes or target VM creation. Diagnostic ldd identifies
`libswtpm_libtpms.so.0 => not found`: the transfer omitted the swtpm package's OWN
bundled library, not a reason to install/upgrade host packages or rebuild the OS.
The setup executable had not yet reached its chmod/check step (ldd's execution
warning is explained by that early abort). Independent hygiene check confirms
all owned probe/target scopes inactive, no tpm-probe/arch-target temporary dirs,
no target result or successful tool-gate receipt. No retry was launched.
The library is already in the signature-verified package at
`usr/lib/swtpm/libswtpm_libtpms.so.0.0.0` with relative soname aliases. Actual
extracted bytes match the verified archive member; library SHA256
`2d08a16574edd980c86832262a13015e9fc119387d5fd85ee171c28104220a71`.
Owner said "okay then go ahead" after the tooling/isolated validation explanation;
this continues tooling correction and VM tests, NOT production installation or
disk erasure. BOTH private probe and target controller now carry the fixed library
hash/relative-alias guard and child-only LD_LIBRARY_PATH for TPM operations;
QEMU/SSH/host environments remain unchanged. Package library bytes and aliases,
controller/embedded/shell syntax, positive/negative hash guards passed. Active
LSP has no findings but remains push-only inconclusive. No OS rebuild/package
installation/source payload change. Updated controller transport hashes match.
Probe `bf47e797c` FAILED at setup after dependency/version/help guards passed.
Independent hygiene confirms owned scopes inactive and fixture removed, no target
state/success gate. Read-only native help and upstream swtpm0.10.2 C source
identified the second harness defect: the exact selector is --tpm, requiring
'<executable> socket'; --swtpm was only accepted as the deprecated --swtpm_ioctl
abbreviation and had no effect. The substring help guard was inadequate.
A non-state native --tpm '<private-swtpm> socket' --print-capabilities check PASSED
(version0.10.2, TPM2 supported), proving selection before initialization.
Source: https://raw.githubusercontent.com/stefanberger/swtpm/v0.10.2/src/swtpm_setup/swtpm_setup.c
Both scripts now use the exact selector; probe checks the exact help line and
non-state capabilities first. Correct aliases/private payload may be reused only
when hash/owner/mode/relative-link guards pass. Setup failure retains a protected
diagnostic log, never prints raw key/state/environment values. Shell/controller/
embedded syntax passed; staged controller transport hash matches; LSP has no
findings but remains push-only inconclusive. Corrected initialization task
`bbae94a6c` COMPLETED exit0: complete ABI, actual disposable setup, socket and
owned scope/fixture cleanup passed. Library-inclusive receipt retained locally
as `remote-target-tools-preflight.json` and remotely as `target-tools-preflight.json`.
No host package installation was required. Updated probe SHA256
`b7775e19986eac4fab5dc4e58a3b896a8d2045986f334ced201688e6b91cb609`.
Arch target runner/fresh vars passed guarded target preflight; controller SHA
`7835134bfb8b7c71cd39bbf40b559d4eaa3d9eba1929699c1e719d27d49fd0f8`;
vars template `3ac11bfc2e1c7896bdd0356a7273d6bed14d5a86104708add0b974af70fc4c8d`.
Template is made from checksum-matched stock blank vars, enrolling only the current
public disposable certificate through the retained wheel-hash-checked firmware
utility. Remote secureboot code SHA256
`cc150d941d4f1d39e596dedc545384a66ccfb3c9ba5cf9bc3a54d8d427d4d88f`.
Both controller and embedded guest-probe syntax passed locally/remotely; exact
HUP/TERM handler/finally temporary cleanup smoke passed. Pyright possibly-unbound
cleanup variable was corrected; active recheck has no findings but is push-only
inconclusive, not confirmed clean.

Native tool receipt and controller/vars hashes inspected, then target
`--preflight-only` PASSED: RAM26.24GiB available, scratch144.9GiB free, KVM/port,
image hash, firmware and private tools gates passed, no target state created.
The wrapper's broad arch-target-* absence assertion hit its own preflight JSON
file; corrected directory-only hygiene check passed without rerunning preflight
or changing target code. Receipt retained as `remote-arch-target-preflight.json`.
First actual isolated target run `be1ad5cf6` FAILED exit1 at300s SSH deadline;
credential-free reboot was NOT attempted. Independent hygiene confirms all owned
VM/TPM/setup scopes inactive and disposable target directory/disk/firmware/
credentials/SSH keys removed; results cleanup_confirmed=true. No retry launched.
Protected results/console/QEMU logs copied into local `target-preparation/`;
console SHA256 `167f8774f44f60063ac926b58bd18247fcc97c7eb160dbcc3686a36e0c12241a`.
Diagnosis JSON and ANSI-clean text also retained. Raw candidate remains separate.

Console diagnosis: Arch initrd started; usr verity setup/mount, early TPM SRK,
root repartition, encrypted-root cryptography setup and root/sysroot mount
milestones observed. Main-OS switch-root/account/SSH probes NOT reached. Boot is
waiting at the normal systemd262 first-boot **Additional Disk Encryption Key
Enrollment** menu, which reports existing tpm2 enrollment and offers recovery key,
passphrase or FIDO2 rescan. The serial=file harness has no input path, so it cannot
complete that wizard. No observed panic/reboot loop; no claim of full boot or
guest SecureBoot flag/PCR-bound re-unlock/recovery proof from these log milestones.
Runtime manifest confirms systemd262-1. Read-only installed unit and upstream v262
unit agree: systemd-cryptenroll --firstboot --prompt-suppress=password,recovery,fido2
--unlock-headless --mute-console=yes, before switch-root, encrypted sysroot/var
and empty machine-ID conditions. Sources:
https://raw.githubusercontent.com/systemd/systemd/v262/units/systemd-cryptenroll-firstboot.service
https://www.freedesktop.org/software/systemd/man/latest/systemd-cryptenroll.html

Next corrective step is owned BIDIRECTIONAL VM serial console support and actual
synthetic recovery-passphrase enrollment through this stock wizard, followed by
normal runtime account enrollment/SSH probes and persisted credential-free reboot.
Do NOT mask the service, pass systemd.firstboot=off, silently choose empty/skip,
remove encryption, bake recovery secrets into image, or use production passphrases
just to meet SSH readiness. Keep secret input out of shared argv/logs; use fresh
protected synthetic inputs, validate the console state machine offline, preserve
this failed receipt and review corrected harness before another deliberate VM.
No image/package/profile change or blind rebuild is indicated by this timeout.
Guest4GiB/2vCPU, scope5GiB/250%CPU/no-swap/15min per boot;
private TPM192MiB/100%CPU/no-swap/30min. Controlled first boot supplies fresh
synthetic runtime enrollment only; on success a clean poweroff/second boot reuses
the same disposable disk/firmware/TPM state WITHOUT enrollment SMBIOS credentials.
Probe checks actual Arch identity, secure boot, encrypted Btrfs root/read-only usr,
service-led account/SSH/sudo/linger/subids/rootless namespace and preserves home/
authorized-key edit/machine-ID/mappings. This is not console-login or rollback
proof. Panic/unexpected reboot/deadline/native-probe failure stops without retry;
all owned scopes/temp state cleaned. Old Fedora getenforce/enforcement assertions
remain unchanged; Arch assertion explicitly expects Arch/non-SELinux, not a Fedora
bypass. Normal signed candidate only, all disks regular files, no homed drive.
Configuration/shpool stay disabled. No Arch console/SSH/Podman namespace/reboot/
TPM unlock/update/rollback/rescue pass yet. Stop on a new validation failure;
no cold retry loop.

**2026-10-06 interactive-console correction:** owner said "sorry go ahead".
Fresh owned local harness directory:
`/home/backup-admin/.cache/personal-os-validation/arch-console-2ezee3fj`.
The original failed controller/results and frozen candidate remain unchanged.
New controller uses a private Unix serial socket and the stock systemd262 menu:
select exactly item2/passphrase, supply a fresh synthetic secret only at the
initial/repeat prompts for the same virtual disk, require enrollment acknowledgement.
No skip, wipe, manual account or image change. Enrollment-dialog output (including
systemd-generated password suggestions) is omitted; exact chosen-secret echoes
are also redacted across read boundaries. Acknowledged enrollment will be checked
with guest cryptsetup --test-passphrase via private SSH stdin before native probes;
this would prove header acceptance, not a TPM-loss/rescue boot.
Initial offline task `b38a2543a` passed13 tests; subsequent exact-menu tightening
and extended controller lifecycle/failure/actual HUP/TERM cleanup fixtures were
checked by `bdeb3a53c`:14 console tests passed;7 lifecycle tests failed in fixture
setup because its AST selector chose the TPM-gate loop instead of signal handlers
(NameError: tool_gate). No lifecycle/VM ran. Fixture now selects the signal loop's
named target; corrected check `b1225afd1` PASSED all21 tests in0.007s, including
actual HUP/TERM delivery and finally cleanup against fake external commands.
No QEMU/TPM/host service ran in those fixtures. No controller change from this
fixture correction. Frozen controller SHA256
`edbbba8b9460aada1c1d0da1754f05a49b82587b242c2b94fa41e58b75bafbde`;
helper `827c6d02d2564941ddbdbf3c9ad528a4e696fbb4955a62c0c6a8b78af4b29eb1`.
Code/input manifest is `console-validation-input.json`; successful offline receipt
and local frozen hashes inspected. Fresh public-only homelab staging/regression/
resource-integrity preflight task `ba9904076` PASSED exit0: all21 tests repeated
in0.011s, public/code/input/artifact transfer hashes, private tools/firmware/KVM/
loopback port gates, RAM26.22GiB available and144.86GiB free scratch. Independent
scope/temp-state hygiene passed; no target state at preflight. Local receipt
`remote-arch-target-preflight.json` inspected. New remote scratch is
`/home/dab/.cache/personal-os-validation/arch-console-2ezee3fj`.
After gate review, corrected isolated attempt `b8a6ef020` FAILED exit1 at300s SSH
deadline via bounded `launch-remote.py` (35min outer, reload-retained ordinary task).
Controller's actual pre-state integrity/resource gates passed. Results report
wizard_state=complete and enrollment_acknowledged=true; sanitized console confirms
the key-slot acknowledgement marker, then stock `-- Press any key to proceed --`.
The harness omitted this post-enrollment continuation stage. Console stops before
observed switch-root; SSH, independent header-usability/native-account/rootless
probes and credential-free reboot were NOT reached. No panic/reboot observed.
Native key-slot acknowledgement is real progress, NOT passphrase usability,
full boot, guest SecureBoot flag/PCR re-unlock or rescue proof.

Wrapper cleanup and separate SSH hygiene both confirm all NEW/OLD owned scopes
inactive, disposable target directory/disk/firmware/TPM/credentials/keys absent,
cleanup_confirmed=true. Protected results/console/QEMU logs copied into local
fresh scratch, diagnosis `arch-interactive-boot-diagnosis.json` retained. Console
SHA256 `d339181ec695daf15bafd32f038145a0e2984f5d2a2f11239aeb2fe788c7ac0d`;
QEMU log `0ab7fcf75377de327d75b8855693cbdc0224e61f4273841114b155344bf8f517`.
No task/VM remains, no retry or harness change after this failure. No image rebuild,
host install/production devices/service change/homed drive involved.
Read-only upstream v262 cryptenroll.c run() ends with any_key_to_proceed() for
arg_firstboot, on BOTH success and failure paths. Thus a future continuation
response must be strictly gated on prior successful key-slot acknowledgement,
not the final prompt alone. Source:
https://raw.githubusercontent.com/systemd/systemd/v262/src/cryptenroll/cryptenroll.c

Next narrow correction: explicit bounded post-success continuation stage, with
fragmented/coalesced prompt, missing-ack/failure/duplicate prompt and private-log/
cleanup regressions; review changed harness before any separately deliberate
attempt. Do not skip/mask enrollment, auto-answer arbitrary prompts, reuse prior
state or rebuild the unchanged OS. Active LSP's earlier zero-findings checks were
push-only inconclusive. Stop here on this new failure; no cold retry/competing VM.
Both attempts have separate results; never remove either failed receipt to retry.
Upstream v262 password/interactive implementations were read:
https://raw.githubusercontent.com/systemd/systemd/v262/src/cryptenroll/cryptenroll-interactive.c
https://raw.githubusercontent.com/systemd/systemd/v262/src/cryptenroll/cryptenroll-password.c

**Subsequent owner "okay go ahead then":** scoped continuation approved, not
installation. New private local scratch `arch-proceed-vk02904r` preserves both
failed harnesses/receipts. It adds explicit post-ACK `proceed` state and sends
one SPACE only at the exact final stock prompt after native enrollment success;
ACK alone no longer satisfies readiness. Coalesced/fragmented ACK/footer data
is retained, missing-ACK/failure/duplicate/persisted-boot prompts fail without
continuation. Results distinguish enrollment acknowledgement from final input.
The actual v262 basic/terminal-util.c any_key_to_proceed() and read_one_char()
were read: canonical mode is disabled for one no-echo character; SPACE is valid
and does not queue a newline for another prompt. Source:
https://raw.githubusercontent.com/systemd/systemd/v262/src/basic/terminal-util.c
Console/controller/lifecycle regression task `b0d5b92b4` PASSED29 tests in0.011s,
including every ACK/footer split, duplicate/missing-ACK/failure/persisted-boot footer,
private-log real socket and continuation-failure/HUP/TERM cleanup fixtures.
All Python/embedded guest/Bash syntax checks passed; active LSP found no diagnostics
but all6 checks are push-only inconclusive. Successful `console-validation-input.json`
receipt and frozen code hashes inspected; previous failed controller/console unchanged.
New controller SHA256 `8f8280925316c7941b590a63528eea9f174a87e0443bc26fab50c7945a9ec0bb`;
helper `8a700ae0eaacc573818bf8c7bfb8cf0d6ba28dc3f32fbd5f0e37838cd01e18ba`.
Fresh public-only homelab staging/regression/preflight `b14061077` PASSED exit0:
29 tests repeated0.017s, frozen transport/public artifact/input hashes, image,
firmware/private tools/KVM/loopback port gates; RAM25.29GiB available and144.86GiB
free scratch. Independent new/old owned scope and no-target-state hygiene passed.
Local `remote-arch-target-preflight.json` inspected; actual controller rechecks
current gates before generating any state. Remote scratch:
`/home/dab/.cache/personal-os-validation/arch-proceed-vk02904r`.
After gate review, changed-harness isolated attempt `baf0eea2d` FAILED exit1:
ConsoleError 'Repeated menu instead of enrollment'. Last saved wizard_state=new,
ACK=false, continuation=false. No SSH/header/native-account/rootless/reboot probes
reached. Verity usr/encrypted-root/initrd menu milestones repeated; no observed
main-OS switch-root/panic. The fail-closed guard stopped, not auto-resubmitted input.
Entire UI was intentionally omitted for secrecy, so the exact guest rejection
reason and terminal query timing were NOT retained; do not claim a proven cause.

Wrapper plus separate SSH hygiene confirms ALL new/prior owned scopes inactive,
disposable target directory/disk/firmware/TPM/credentials/SSH keys absent and
cleanup_confirmed=true. Protected results/console/QEMU logs copied into fresh local
scratch; `arch-proceed-boot-diagnosis.json` records observed facts/limits. Console
SHA256 `4c1f8ee6e8ebeb89a4f336a0e6f65ca1ad15f2278ee099105b6200727843a5d8`;
QEMU `6c3b4f2a6c22248656ebe679dac3ee8397e80b7c96250f3fc1ebadb6718b4c19`.
No background/VM remains; no retry or harness mutation after failure.

Read-only source review identifies a REAL driver timing flaw: serial.pump() shares
the readiness loop with blocking subprocess.run(ssh true), ConnectTimeout=3 and
Python timeout=15. Upstream v262 terminal-util.c ANSI queries have333ms deadlines,
flush stale input on timeout, and return to later interactive input. Delayed
terminal replies could thus contaminate a menu field. This is a PLAUSIBLE cause,
not established live causality;29 immediate socket/FSM fixtures did not prove
slow-SSH/real-TTY scheduling. Before any future deliberate attempt, keep console
handling responsive while SSH probes run, add only secret-free prompt-kind/query
latency/rejection metadata, and validate bounded slow-SSH/interleaved-query/TTY,
privacy/signal/cleanup behavior. Do not blanket retry selections, disable guards,
skip enrollment or rebuild the unchanged OS. Stop here and preserve all3 failed
receipts. No package/profile/security relaxation; production devices, credentials/
services/homed drive/install remain excluded.

**Owner's continuing authorization:** "you can keep going until you can login
dont need to keep asking for permission". Continue scoped isolated correction/
validation without a fresh permission question at each diagnosed failure. Preserve
failures, test/review changed code and gates before deliberate iterations; do not
repeat unchanged failures or compete for resources. Production permissions are
unchanged (no physical disk/install/host packages/services/reboots/real identities,
security weakening or configuration/workload gate bypass). Login remains unproven.

Fresh local code-only scratch `arch-responsive-14y1akgi` now has a continuous
single-owner serial reader in `responsive_console.py`, lock-protected snapshots,
bounded stop/join and expected-poweroff EOF handling. SSH/header/native probes
can block the main thread without starving terminal I/O. ACK/final-input guards
and suppressed private UI are retained. Only fixed state/counters/booleans and
reader-cycle timing/rejection flags enter diagnostics, never entered text/secrets.
Controller finally preserves those snapshots even if the reader fails. All3
prior scope sets are checked; new runs still refuse an existing result receipt.
Offline timed regression `b71df6cd4` PASSED35 tests in1.782s: slow foreground
process while terminal queries/dialog operate, actual disposable PTY termios/
query/input exchange within250ms (<stock333ms), EOF/error/private-log and worker
shutdown plus previous FSM/controller HUP/TERM/failure fixtures. Python/embedded
Bash syntax passed. Active LSP found4 optional-thread-access diagnostics in the
new test only; explicit started-thread assertions corrected these. Recheck has
zero findings but push-only inconclusive. No production-code change from this fix.
Frozen local rerun/public-only remote stage/regression/preflight `ba9167503`
PASSED exit0:35 local tests1.722s then35 remote tests1.783s, unchanged code/source
hashes and prior failed console, artifact/vars/private tools/firmware/KVM/port
gates, RAM25.77GiB available and144.85GiB scratch. Independent old/new owned scope
and no-target-state hygiene passed. Local receipt/preflight inspected.
Controller SHA256 `e933d5efc97dd8c18b56f3d89c9a85e12fb8e39a10ca21962eb643afb5309131`;
FSM `8e355ee8a56cdb52bfd763debc8d468dd283b940a85b51b74674e98438539622`;
reader `3d176b46e8e91974ab687701102af03232c13f7b239838ae8a751503fefba1dd`.
Remote `/home/dab/.cache/personal-os-validation/arch-responsive-14y1akgi`.
After gate review, ONE changed-harness attempt `b346cb648` FAILED the300s SSH
readiness deadline, but console scheduling correction WORKED: wizard=complete,
ACK=true/final-continuation=true,8 terminal queries, no selection/empty rejection,
max reader cycle25.199ms, no reader error. Console reached initrd switch-root,
Arch main system/journal/network/home/encrypted swap/tmpfiles. Stock Initial Setup
(systemd-firstboot.service) then waited at its timezone prompt before sysinit/
account/SSH. This is not a full boot/login/header-usability/reboot pass. No panic
or observed core-service failure; no rebuild/security bypass indicated.
Wrapper+separate independent SSH confirmed all4 attempt scope sets inactive,
disposable disk/vars/TPM/credentials/SSH keys absent, cleanup=true. Protected local
results/console/QEMU and `arch-responsive-boot-diagnosis.json` retained.
Console45046B SHA256 `aedfbd7982c327247951e0dedf2b2858b38144763484d671332d3e379075921b`;
QEMU410B `42b79952f8a21a106e82750e5e6e5aa67b2dc245a97642b7fa4c5ce637289db2`.
Read v262 stock unit/source: imports firstboot.*, accepts firstboot.timezone/locale;
root initialization skips existing passwd+shadow (no root password needed).
Fresh local CODE-ONLY `arch-firstboot-1tb1vlal` adds initial-only native UTC/C.UTF-8
credentials, preserves all account/recovery/root/SSH gates and no credentials on
persisted reboot, checks native firstboot result/timezone/locale in guest probe,
and guards all4 prior scope sets. Lifecycle fixtures verify exact private SMBIOS
files/values and absent reboot inputs. Native firstboot fixture targets only a
disposable offline root, tests settings, existing root-account preservation and
non-replacing repeat. `bb51839d8` FAILED9 fixture/assertion checks:8 lifecycle
AST fixtures omit controller's global077 umask and newly added privacy-mode
assertions caught that omission; native firstboot returned0 and wrote a relative
`../usr/share/zoneinfo/UTC` link rather than the expected absolute link. No native
credential failure/VM/state involved. Fixtures now scope/restore real077 umask;
normalize timezone link for fixture AND guest assertion without weakening UTC
requirement. LSP3 recheck0findings/all inconclusive. Earlier syntax passed.
Frozen37 local-rerun/public-only remote-stage/regression/preflight `b70b8078d`
PASSED exit0:37 local tests1.728s +37 remote1.743s, including native firstboot
settings/root-account preservation/non-replacing repeat and private credential
transport/credential-free reboot fixtures. Hash/source/artifact/vars/private-tool/
firmware/KVM/port gates passed, available RAM25.24GiB/disk144.85GiB, independent
all4 old/new scope/no-state hygiene. Successful local receipt/preflight reviewed.
Controller `669ca2b5125eeb2e4e56f8931844115b1a42fb9fe8603c27e05b1ac15c5f03c1`;
new native fixture `cc0acdaffc97a47625b63e4d6afdd1e192d089abfdfe6cfd9906893167c0f619`.
Helpers unchanged. Local/remote scratch `arch-firstboot-1tb1vlal`.
ONE native-firstboot-corrected login attempt `b21af2931` FAILED300s SSH deadline.
Recovery ACK/continuation true,8 queries/max cycle25.72ms/no rejection/error;
switch-root into Arch. Native timezone credential WORKED: /etc/localtime written.
Stock firstboot then waited at new-root-password prompt. Earlier native fixture
preinitialized passwd+shadow and did not cover missing root-account state. No
login/header/native-account/rootless/reboot pass. No OS/security bypass indicated.
Wrapper+separate SSH independently confirmed ALL5 scope sets inactive, disposable
disk/vars/TPM/credentials/keys absent, cleanup=true. Protected local results/logs/
`arch-firstboot-boot-diagnosis.json` retained. Console44915B SHA256
`79f20c77af30fbab7d25b9a9f1df68d9bca89899392221a4bfe0f71fd68232aa`;
QEMU408B `ff3aad27a0b0e23ea66857918bd87b8fc0d6ffe698b7ea1c715beb294aab0d6c`.
Fresh local CODE-ONLY `arch-rootcred-el0lo3xu` adds distinct32-byte-random root
password hashed via OpenSSL stdin/captured output and stock
`passwd.hashed-password.root` credential through private600 SMBIOS file. Plaintext
is immediately discarded, hash never argv/log/source/image; absent on persisted
reboot. Does not manually create guest accounts or skip/mask firstboot. Intended
operator still comes solely from personal-os-account.service; root SSH forbidden
and key-only SSH/security gates unchanged. All5 prior scope sets guarded.
Read v262 native password/Shadow writers: missing account/shadow uses credential;
existing passwd+shadow stays unchanged even with a new credential. New offline
native fixture covers missing passwd+shadow AND missing shadow alone, checks
root UID/GID/native hash without exporting values, stock0000 shadow mode then
opens ONLY owned fixture for assertions; preserves existing locked root/repeats.
Lifecycle fixtures assert distinct stdin secrets, private credential transport,
no values in argv/output and no reboot inputs. `b7d8bc41b` PASSED38 tests1.864s,
including both missing-account subcases, existing locked-root preservation and
edited locale repeat. No fixture failure/security relaxation.
Python/embedded guest/Bash syntax and diff check passed; LSP6 nofindings but all
inconclusive. Frozen38 rerun/public-only remote stage/regression/preflight
`bb8123495` PASSED exit0:38 local tests1.860s +38 remote1.763s; unchanged frozen
code/previous-failure/artifact/vars/tool/firmware/KVM/port gates, available RAM
25.87GiB/disk144.85GiB and independent all5 old/new scope/no-state hygiene.
Successful local receipt/preflight inspected. Local/remote `arch-rootcred-el0lo3xu`.
Controller `438780293ea5bb063b271aefea8b8bfe2314969ea1813a0b087bf2ce1d890fe3`;
native fixture `a1e91d8d49759dada062cc6b33184114d661f59066da2280ad9295ed28579c74`;
FSM/reader unchanged. `b8cbc594c` overall FAILED at the native guest probe, BUT
**GUEST SSH LOGIN REACHED**: real key-only SSH as testop UID/GID1000, native
personal-os-account active/phase complete, rootless journal complete, hostname
personal-os-test, sudo works. Stock firstboot succeeded, UTC applied; native
recovery ACK/footer and independent SSH-stdin cryptsetup header acceptance passed.
Guest SecureBoot=true, TPM present, encrypted Btrfs root/read-only usr. Linger=yes,
exact single subuid/subgid ranges testop:100000:65536, actual rootless Podman
cgroupv2/netavark and podman-unshare UID0 mapping worked. Configuration disabled,
ready marker absent, pinned factory revision correct. These are retained observed
milestones, not an overall probe/reboot pass.
Probe stopped with KeyError after Podman namespace collection, before SSH-policy
report/home sentinel/assertion block. Exact missing key not recorded; cannot yet
claim complete SSH policy verification. locale_utf8=false from literal
`LANG=C.UTF-8` line comparison: may be quoting/preserved image value, not diagnosed.
No mutable edit or persisted reboot attempted. Do not force existing locale or
weaken SSH policy to satisfy diagnostics. Read actual native output/defaults and
add bounded, private-safe probe fixtures/error metadata before another iteration.
Wrapper+separate independent SSH verified ALL6 scope sets inactive, no disposable
disk/firmware/TPM/credentials/keys remain, cleanup=true. Protected local results/
console/QEMU/`arch-login-probe-diagnosis.json` in arch-rootcred-el0lo3xu retained.
Console48556B SHA256 `32ff79aa4c356e4452cf5128ba34d218645134632c881417d4b2b60d76da456e`;
QEMU406B `23a42dd52a34d213155d4af0cec29d49630f15ae2a43c4a2fd4abb0d67480ccd`.
Standing owner's 'until you can login' milestone is reached; no VM/task/retry is
active. Next gate is corrected full probe and persisted credential-free reboot,
then recovery/TPM-loss, update/rollback/rescue and state compatibility. Installation
is NOT ready/authorized. No security relaxation/OS rebuild/production change.
Preserve all6 attempt receipts/harnesses, including this overall-failed login run.

**Post-login continuation (owner go-ahead 2026-10-06):** Owner says 'okay well
lets keep going then go ahead' after reviewing probe/reboot/recovery gates.
Continue isolated validation, not physical install/production operations.
Read manifest/native homelab tool: both target/host OpenSSH10.5p1, target
package10.5p1-1. Native pure config dump (`sshd -G -f /dev/null -o HostKey=none`,
no daemon/key/config/host changes) prints capitalized PermitRootLogin,
PubkeyAuthentication, PasswordAuthentication, KbdInteractiveAuthentication.
Existing lowercase dictionary lookup therefore explains the SSH KeyError.
Fresh CODE-ONLY local `arch-probes-d10gp7rt` adds hash-guarded `guest_checks.py`
(681097ca698a5a730fb7c108d081a159a67d36d1f836c598ca4a4fb8674e94d1), normalizes
case/whitespace, rejects missing/duplicate/invalid selected options, preserves
EXACT existing SSH-policy gate. No raw config/error values exported; fixed-stage/
error codes/allowlisted missing-option names only. Locale check now parses quoted
LANG without executing/evaluating input, recognizes UTF8 aliases/codesets;
requires actual UTF8 but preserves existing configured language rather than
force-resetting it to synthetic C. Exact prior guest locale syntax unretained;
no source/image/guest settings changes to make probe pass. Duplicate/invalid
LANG fails closed. Policy/locale checks occur before mutable proof edits.
New actual embedded-probe first/reboot/missing/bad-policy/nonUTF8 fixtures plus
native OpenSSH config dump and helper fixtures cover corrected logic. All6 old
scope sets guarded; helper enters guest only through SSH stdin, not image payload.
`bedd443c8` PASSED49 tests1.871s, including native config dump, real embedded
first/reboot and policy/locale negative/fail-before-state fixtures. Python/complete
embedded guest/Bash syntax passed; active LSP6 zero findings/all inconclusive.
Frozen49 rerun/public-only remote staging/regression/preflight `bf632fa03` PASSED
exit0:49 local1.857s+remote1.830s, unchanged frozen source/helper/previous-console/
artifact/vars/tool/firmware/KVM/port gates, available RAM25.61GiB/disk144.85GiB and
independent all6 old/new scope/no-state hygiene. Local successful receipt/preflight
inspected. Controller `7317b2e886325859e1f127c2f4cd32f532228827dbba11f64837f9b1f6514bab`,
helper `681097ca698a5a730fb7c108d081a159a67d36d1f836c598ca4a4fb8674e94d1`;
fixture `1a4e60c1a5d44a81c5084156b71a4277c0700ad68b42e6ada5272c242063fc31`.
Local/remote scratch arch-probes-d10gp7rt.
`b529c1a4c` overall FAILED at guest poweroff request, BUT **FULL FIRST GUEST PROBE
PASSED**: account/login/sudo, exact SSH policy, UTF8, UTC/firstboot, guest Secure
Boot/TPM, encrypted Btrfs root/read-only usr, factory pin/config gating, linger/
subids/rootless Podman+unshare, recovery header acceptance and synthetic home/key
comment edits. Native first report passed=true. No persisted reboot attempted.
Compat `sudo -n poweroff` returned unexpected status (exact code/error discarded by
original harness). Console ends at normal login, no shutdown sequence observed.
Do not claim clean poweroff or bypass inhibitors/security to pass. Wrapper+separate
SSH confirmed ALL7 scope sets inactive/no disposable disk/vars/TPM/credentials/
keys remain, cleanup=true. Frozen code unchanged; protected local results/logs/
`arch-firstpass-shutdown-diagnosis.json` retained in arch-probes-d10gp7rt.
Console48481B `5dbe4bf7bfd94a09234403b5c8137977bdb36ba815b4e9c7dbc7ce88a14c87e6`;
QEMU402B `ffae46c0af9da209c0c3a8f53c1ad0785612040289053d7686ea1bf1368235cd`.
Non-stateful native host inspection: systemd262-1, poweroff->systemctl; --help
explicitly recommends systemctl poweroff. Read v262 systemctl-compat-halt.c:
logind/inhibitors first; authorization/unsupported/in-progress errors abort. Exact
guest cause remains unretained, so next iteration includes safe native diagnostics.
Fresh CODE-ONLY arch-shutdown-g9ku91s6 adds hash-guarded shutdown_guest.py
(77115cacd2dcf7b5eebfd365774c8512465d12bc8839d58195c15c5c582f27cf), sent only via
SSH stdin under sudo in disposable guest. Collects root UID/PID1/systemctl/compat
alias/manager socket/CAP_SYS_BOOT booleans, explicit stock systemctl poweroff
return code and fixed error categories; no raw values/stdout/stderr exported.
No force/no-inhibitor/no-sync/fallback bypass. Controller retains SSH/guest status
before cleanup; requires accepted request AND clean QEMU exit before second boot.
New shutdown failure/privacy/precondition/exact-native-selector fixtures + existing
49 checks; all7 old scope sets guarded. Six Pyright heterogeneous-dict errors were
corrected with explicit dict[str,object] annotations; recheck0findings/push-only
inconclusive. Complete Python/guest/Bash syntax passed. `baa12c97e` PASSED55 tests
1.755s, including shutdown failure/no-reboot, precondition/no request, exact native
selector/no bypass and private fixed-error/exception cases. Frozen55 local rerun/
public-only remote staging/55 regressions/hash/resource/integrity/hygiene preflight
`b714df6fe` PASSED:55 local1.829s+remote1.833s, source/previous-console/artifact/
vars/private-tool/firmware/KVM/port and independent old7+new no-state hygiene;
available RAM26.00GiB/disk144.84GiB. Successful receipt/frozen hashes/preflight
inspected. Controller54c7edf6e446ddfebfb0d8c55e4d7453399640888c617d8ab894171cf9d51c11.
`b0ed14df3` overall FAILED before second QEMU's serial socket, BUT full first native
probe/header/security/policy/UTF8/rootless/home PASSED again and **native clean
shutdown PASSED**: systemctl return0/errornone, root UID/PID1/CAP_SYS_BOOT/manager
true, clean QEMU exit0. Root PATH has no compat poweroff command, consistent with
previous discarded-status failure. Serial reached swap teardown/unmount targets/
System Power Off and kernel Power down; systemd-shutdown warned remaining DM
finalization ignored (retained, not masked). Credential-free second QEMU launch
attempted, but failed connecting absent tpm.sock BEFORE guest/serial initialization.
Separate QEMU reboot log is explicit ENOENT. Review QEMU tpm_emulator_shutdown/
finalize: sends CMD_SHUTDOWN to swtpm. v0.10.2 control ABI =3. Original harness
incorrectly assumed one daemon/socket would survive first QEMU exit.
Wrapper+independent SSH confirmed ALL8 scope sets/state cleanup, protected local
arch-shutdown-g9ku91s6 results/logs/arch-clean-shutdown-tpm-diagnosis.json retained.
Console61800B167841a9604d18f3392c022c04545c5364e74df348be5c16f6626094fcea5d9f;
firstQEMU321B9f4561f352d8dc9af1a5785fc826ca934e0dc809ff91dc10e560f840342b2fbc;
rebootQEMU288B82dac607bffb084768e0880b6b1c3aafcfa2df2450865779452d3a6e69b6c7d1.
No persisted reboot/guest re-unlock/state preservation pass yet.
Fresh CODE-ONLY arch-tpmcycle-4c8rx6hu starts one private swtpm daemon per guest boot
using SAME directory/permanent data; setup ONCE, no wipe/re-enroll/new TPM identity.
Hash-guarded tpm_cycle.py b73a4ee974fb5d68708586b0377cbf81b02b659f7e8f5ac9b051b28921dc99e5
requires clean daemon exit/socket absence, owner/private metadata, permanent state
present/bounded/regular and internal directory identity+data comparison before
restart and before QEMU boot. No state bytes/digests/identities exported. Report
only preservation/setup-repeated/clean-exit booleans. Actual lifecycle fixtures
now emulate socket teardown, assert setup once/two daemon starts/same state and
fail closed on dirty TPM exit/restarted socket failure. Native remote-only fixture
verifies binary/library hashes+aliases and uses bounded128M setup/192M daemon
scopes, actual CMD_SHUTDOWN and two same-state daemon starts; removes state after
scopes stop. No VM/host packages/production state in fixture.
`b55241efb` PASSED62 tests1.825s/1 explicit native-utilities-not-local skip (63
collected): actual lifecycle two-daemon/setup-once/same-state/safe shutdown and
dirty-exit/restart-socket-failure cases plus permanent-state/privacy guards.
Python/complete guest/Bash syntax passed; active LSP7 zero findings/all push-only
inconclusive. `b393e7d2c` FAILED remote native fixture BEFORE TPM setup: library
hash guard used raw package usr/lib/swtpm path while staged target-tools uses lib/.
Local63 (one native skip) and remote62 other tests passed; native error/receipt
retained, no successful native or target-preflight receipt. Separate SSH inspection
confirmed actual regular library+relative aliases at target-tools/lib, no native/
VM temp state/results, fixture and target scopes inactive. No new VM was launched.
Protected arch-tpmcycle-4c8rx6hu/arch-native-preflight-diagnosis.json retained.
Fresh CODE-ONLY arch-tpmfix-9fyvy41d corrects fixture paths/child lookup to actual
flattened lib directory and adds an AST fixture comparing actual controller's
libdir assignment (prevents future packaging drift). Signed tool/library/hash/alias
and state guards remain strict; no daemon/TPM setup logic or OS change. Native
fixture explicitly stops its completed daemon scope between two starts, matching
controller lifecycle. Guards old failed preflight scopes too; preserve old files.
`bf276c1f7` PASSED63 tests1.895s/1 explicit native-tools-not-local skip (64
collected), including actual controller AST layout and state/lifecycle guards.
Complete Python/guest/Bash syntax passed; active LSP5 zero findings/all push-only
inconclusive. Freeze/stage/launcher require64 local (one explicit skip) and ALL64
remote WITHOUT skips plus native fixture receipt, hashes/fresh resource/integrity/
hygiene before ONE deliberate first/persisted reboot. `b5ef19a50` PASSED local63
+1explicit native skip1.910s, remoteALL64/no-skips2.174s including actual native
CMD_SHUTDOWN/two-daemon/same-state fixture and its cleanup. Native no-skip receipt
passed64/skipped0; artifact/source/helper/previous-console/vars/tool/fw/KVM/port/
old8+failed-preflight+new scope/no-state hygiene and RAM25.73GiB/disk144.84GiB gates
passed. Local receipt/native proof/frozen hashes/fresh gates inspected. Controller
7b9a84981a15d81e28baf92550f4d3dfa13e027bb0b2863f68770b0ad34d5479;
fixture b68e4cd3000772d123999291930317d0cf9a98482e89e3575efa57d93ed81409.
**`b106cbd9f` PASSED exit0: full first boot AND credential-free persisted reboot.**
Both guest reports passed all native account/SSH-key/sudo/exact SSH policy/UTF8/
UTC/firstboot/guest Secure Boot/encrypted Btrfs root/read-only usr/linger/subids/
rootless Podman+unshare/config-disabled/no-ready-marker gates. Same machine-ID,
subids, pinned factory revision and synthetic home sentinel/key-comment edits
preserved. SAME disk/firmware/permanent TPM state, setup ONCE/per-boot daemon;
second boot supplied NO account/root-hash/firstboot/enrollment credentials and
console state stayed boot/ACKfalse/continuationfalse: no recovery enrollment or
secret input. Automatic encrypted-root TPM unlock succeeded on persisted boot.
Recovery-passphrase independent header acceptance true; native clean shutdown/
QEMUexit0+TPMexit0/socket teardown both phases. First12 terminal queries/max25.136ms;
reboot5/max26.075ms, no reader/rejection errors. No installation readiness implied.
Wrapper+separate SSH independently verified ALL9 VM scope sets/failed-preflight/
native-fixture scopes stopped, no target disk/vars/TPM/credentials/SSH keys/temp
state, cleanup=true; frozen source hashes unchanged. Protected local/remote
arch-tpmfix-9fyvy41d results/logs + local arch-persisted-reboot-pass.json retained:
results5076B03639e8bd983c83b17236c88469a0150af7ff6c80f59d3f4d00ea10a9b7421fe;
firstconsole60605B1549090acf46840591dd6dc8ecf1023ed781462133bd26bdd358561401342cd7;
firstQEMU317B0d06bfb8573f5bc5e3a8168eee081e73971d3d81916502a59eab2c9ccd33ac53;
rebootconsole58141Bc93e40a6d83160f07e70c46f565d0c6590fcadf59db2b66c5dbec3abc94552fe;
rebootQEMU319Baec16745491fec47bcf202fc97c16f4ff891f48b909c58449ae1d1f65a2d4609.
No VM active. Console-password login, TPM-loss/passphrase recovery boot, update/
rollback/rescue/state-schema compatibility/backup restore/physical hardware and
installation gates remain; installed size still unmeasured.
Next under standing post-login owner go-ahead: private single-reader native
console-login proof, then stock TPM-loss recovery UI. Read SafeLog/SerialConsole/
plain bodies; current log supports ONE secret, so integration MUST add safe
multi-secret streaming redaction + suppress whole login UI + worker-only writes,
no foreground socket owner. Arm only after native SSH/account gates, authenticate
existing testop (no manual user/ready marker), prove actual UID/GID1000 with random
nonce + exact line/terminator (terminal command echo must not count), then logout.
Fresh CODE-ONLY arch-consolelogin-nycy11kw adds standalone ConsoleLogin FSM and8
protocol tests: explicitly armed/exact host/password/shell stages, bounded buffer,
one credential send/no retry, fixed errors/snapshot, fragmented input, echo and
wrong/root/unterminated proof negatives. `b5629947b` PASSED71 tests1.912s+1explicit
remote-only native TPM skip (72 collected). Active LSP2 zero findings/inconclusive.
NOW integrated into SerialConsole/ResponsiveConsole and controller: optional login
observer, state-only locked arm AFTER reboot full SSH/native account/security/home
checks; SOLE reader handles sends on recv/timeouts, ANSI query replies precede
credential input. Suppress whole active login UI; SafeLog handles BOTH recovery
and operator secrets across reads, overlapping prefixes and conservative EOF.
Require nonce/exact terminated UID/GID1000 proof+logout within45s before expected
poweroff; incomplete login cannot enable allowed EOF. First boot has no login flow.
No manually created users/markers, locale or shell/profile edits, bypass or password
SSH. Report fixed state/booleans only. Helper hashes now recovery84aef7a61c2b96bbec5a3ba2c8a5fbd4e21bd9a18f27dc24dd615d44c36b9102,
responsive d3b1baa06b3243bba2ff6533303271d44be1f0c580057758cae144b40a130f7e,
login2621220dbd0d021fb4802274292c0ea527b627f4ddb7695980c5f131044f7d1f.
New real-socket/disposable-PTY/query-during-foreground-block/sole-writer audit/
UI+multi-secret suppression/prefix/partial/auth/EOF/early-arm cases and actual
controller successful/failed/deadline console-login lifecycle fixtures.
`b0d279d9b` PASSED79 tests2.399s/1explicit remote-only native TPM skip (80
collected), including full socket/PTY/privacy/sole-writer/controller integration.
One Pyright socket-vs-test-audit-proxy assignment corrected via test-only setattr;
recheck0 findings/all inconclusive. Python/complete guest/Bash syntax passed.
Freeze/stage/launcher80/new helper+tests, prior SUCCESSFUL baseline result+console
hash verification and no-skip native receipt required. `b67ee04f8` PASSED local79+
1explicit native skip2.394s/remoteALL80 zero-skips2.816s, including privacy/TTY/sole
worker and actual native TPM shutdown/restart. Passed baseline result+console,
frozen source/helpers/artifact/vars/tool/fw/KVM/port/hygiene and RAM26.01GiB/disk
144.84GiB gates verified. Local receipt/native80 no-skip proof/frozen hashes/fresh
preflight inspected. Controllerdc3ca9a538c1bbac4b2f60503622b0f32bbc8de5141a8fd4a5af521a3730da23,
IOfixture4c364246f1f023a52796527fb791bf274c5268c42f51745215bba6d8547c2faa.
ONE `b3416d8ae` Arch native console login PASSEDexit0, full first boot and
credential-free persisted reboot/native/policy/security/rootless/home gates passed
again. SAMEdisk/fw/permanentTPMstate/setupONCE/two-clean-daemons, initial-only
credentials absent on reboot, encrypted-root automatic TPM re-unlock, stable
machine-ID/subids/factory pin and home/key-comment edits. AFTER full reboot SSH
native gates, SOLE worker authenticated the existing testop via stock console
password/PAM, nonce-qualified actual UID/GID1000 proof and logout all TRUE; state
complete/password_sent/uid_gid_proof/logged_out=true. No shell/profile/locale/manual
account or SSH policy changes. ALL active login UI omitted, BOTH secrets streamed
redacted; no raw enrollment/login UI, marker, password or hash exported.
First12queries/max25.261ms, reboot8/max26.830ms/reader errors NONE. Recovery-header
acceptance passed (not TPM-loss boot). Clean native QEMU/TPM exits both phases;
first shutdown SSH255 report connection_closed, clean QEMU exit required/pass;
reboot stock systemctlrc0/root/PID1/capability/socket/QEMUexit0, no force/bypass.
Wrapper + INDEPENDENT SSH ALL10 VM attempt sets/failed-preflight/native fixture
scopes inactive, disposable disk/vars/credentials/keys/TPM/temp absent, frozen code
UNCHANGED. Protected local+remote results/logs retained0700/0600 + local
arch-console-login-pass.json0600; all export hashes/modes independently matched:
results5108B ffe61ccb81e5bed9f3df4ff6d1b9aac4a00a9146ab99265250c9bc6714986d61,
firstconsole61998B25f711c0098f22fbf5a748c45f44f1ef4035ddee86c0db5d064d6c94a44aaf8d,
firstQEMU329B1a069d115d9476c7172fc6a3a8156c65c6684edc1fb3cdb2fac345a9c908abe4,
rebootconsole57132B149c7bdf9e38e89c39a652add07834a4f790da9beaa045b8e04444b1f1d2bec8,
rebootQEMU331Bbe12f9523846ca768e2fe8f6aad5c959f56dc140684e9e8caa9b5d2647f54e71.
No VM active. Preserve8failedVM+failedpreflight+TWO separate successful baselines
(arch-tpmfix-9fyvy41d/b106cbd9f, arch-consolelogin-nycy11kw/b3416d8ae). No OS/image/
security/production changes. NEXT under standing owner continuation: inspect stock
systemd262 cryptsetup ask-password/recovery and partition/token composition, design
isolated persisted-disk TPM-loss/passphrase UI boot without removing security or
re-enrolling/wiping the established TPM, then unit/PTY/lifecycle/privacy/hashguard/
freeze/full-native/fresh gates before ONE deliberate recovery attempt. No cold retry
or production/physical disk operations. Rollback/rescue/backup-restore/state-schema
compatibility still unpassed; configuration and workloads stay gated. Not install
ready/authorized. Native console milestone does not establish recovery usability.
Read-only upstream v262 review:
https://raw.githubusercontent.com/systemd/systemd/v262/src/cryptsetup/cryptsetup.c
(`get_password`, `friendly_disk_name`, TPM fallback) +
https://raw.githubusercontent.com/systemd/systemd/v262/src/shared/ask-password-api.c
(`ask_password_tty`) + cryptenroll.c/cryptenroll-interactive.c. Stock prompt is
`Please enter passphrase[ or recovery key] for disk <friendly volume>:`; friendly
name contains exact volume `root` or descriptor `(root)`, optional mountpoint.
Missing EFI TPM falls back to traditional unlocking; token errors are nonfatal
and password comes only after token/key attempts. TTY attrs set before writing
prompt, optional lock emoji/ANSI/no-echo footer; no prompt text implies success.
IMPORTANT pending gate: root AND swap use separate `Encrypt=tpm2` repart policies,
FactoryReset=no. Native firstboot cryptenroll defaults to backing /var/root and
contains no swap enrollment path. Thus root header acceptance DOES NOT prove
swap recovery; swap fallback/slots must be probed explicitly, no assumptions,
skipping/masking/degrading/resetting an encrypted swap service to pass. Actual
swap header/TPM-loss service behavior not yet measured.
Fresh CODE-ONLY arch-tpmloss-tgw231na copies successful .py public harness and adds
standalone RecoveryUnlock +8protocol fixtures: explicit arm/clear stale buffer,
bounded private input, exact root-volume role/passphrase type, one send/no retry,
fragmented emoji/ANSI friendly prompts, wrong disk/verification/PAM/PIN/new/current
UI fail-closed, private errors/snapshot. Submitted is NOT recovery success; complete
requires full native SSH report/encrypted Btrfs root/SecureBoot/missingTPM/UIDGID1000/
stable home/key edits/ACTIVE ENCRYPTED SWAP + required crypto services healthy.
`b7dffd6e6` PASSED87 tests2.603s/1explicit remote-only native skip (88 collected);
syntax passed, LSP2 zero findings/inconclusive. RecoveryUnlock NOW optionally wired
into SerialConsole/ResponsiveConsole, incompatible with enrollment/login/mismatched
secret configurations. Locked state-only arm BEFORE worker starts, query replies
FIRST, SOLE reader sends recovery credential; entire active root-unlock UI omitted
until full native recovery confirmation, fixed completion tag worker-only, snapshot
fixed states/booleans. Incomplete recovery cannot allow EOF/poweroff; no handler
bypasses enrollment/no reset/re-enrollment. Adds6 live Unix/native controlling-PTY
fixtures: coalesced query+root prompt/sole-writer audit/UI+secret suppression,
unarmed/stale/no-send/invalid modes, wrong root role/repeated prompt/no retry,
missing swap gates/EOF failure, confirmed expected EOF/idempotent cleanup, REAL
systemd-ask-password bound to allocated private controlling PTY. Native stdout
PRIVATE pipe only, no raw assertion/diagnostic, TTY verified before native exec,
no agent/keyring flags/host accounts or terminal use; terminal attrs restored.
`bafefbca0` PASSED93 tests2.943s/1explicit remote-only native TPM skip (94
collected), INCLUDING actual stock private controlling-TTY password UI, stdout
proof, termios restoration/no agent state. Python syntax passed/LSP4zero all
inconclusive. Adds public standalone guest_crypto.py READONLY selected root/swap
metadata: refuse non-root/non-synthetic hostname before any command, exact mapper
root, exact PersonalOS partition labels/crypto_LUKS/ONLY /dev/vdaN regular VM
partition roles from bounded lsblk JSON (no guessed swap disk). LUKS metadata
parses bounded slots/token references but exports ONLY counts (TPM/recovery/other/
unreferenced slots), never token/KDF/salt/digest data. Active LUKS2 mapping must
match that virtual partition; inactive/unavailable statuses distinguished. Selected
swapon source and failed cryptsetup service names/booleans; no commands open/modify
volumes or credentials. Metadata does NOT demonstrate a particular key works.
Eight mock/pure-parser fixtures cover root-password candidate vs TPM-only swap,
unknown-token privacy, corrupt refs/size/depth/roles/duplicates/real-host devices,
mapping/units identity, active/inactive/error handling and early host-storage guards.
`b6d88552d` RUNNING102 expected101pass/1nativeTPM skip. LSP reported unresolved
new sibling test import; fixture now binds EXACT private helper via importlib/Path
instead of ambient paths. Recheck0/all inconclusive, syntax/git-diff-check passed.
Still NOT VMcontroller/fault-injection/guest-probe/hashguard integrated or staged/
booted. Copied80 freeze/stage/previous-dir/hashguards MUST NOT execute. No VM active.
Next actual private-PTY/native ask-password/privacy/single-worker/fault-injection/
controller fixtures and selected root/swap header/service metadata (never blobs),
then frozen full native/fresh gates before one recovery VM. Preserve original TPM
permanent state INERT during hardware-absent third boot; do not clear/re-enroll. Do not force
shell/profile or UI policy to pass; no password/root SSH enablement. Preserve ALL8
failed boot receipts + failed preflight + successful two-boot baseline/harness.
Image/policy/credential/account source unchanged; all production limits remain.
No polling, competition, live mutation or cold retry.

The next session should run from `~/Products/personal-os`. Read `AGENTS.md` and
the root README, then this charter. Use the CLI from this repository root:

```sh
clearhead show charter mini-server
clearhead read actions --charter mini-server --open-only --format ids
```

Latest local evidence: policy-matched task `b341164f0` built the current
Podman/account candidate and verified its signed UKI. The builder and its
private keys/state were removed. Read **Fresh candidate validation** below for
source/patch identities, artifact hashes, stock-policy correction and active test
status. The first target boot reported Secure Boot enabled and encrypted-root
mount, then froze at SELinux policy loading during switch-root; no account/SSH,
rootless or rollback pass exists. The early-root MakeSymlinks fix passed all 131
tests and fresh strict build/signature task `bb4b20652`. Corrected-candidate boot
`b8f48ad42` FAILED its SSH deadline, but policy loading and switch-root succeeded.
Early machine-ID creation returned Permission denied; journald/modules-load exited
127 and pcrmachine failure caused a reboot loop. Account/rootless remain untested.
Bounded diagnostic `b223e4d29` COMPLETED: journald's shared-library loader returned
Permission denied. Offline inode/ELF inspection `bd7093698` COMPLETED: signed
/usr and /usr/lib are 0700, matching the source-checkout umask-077 defect. Selected
stored SELinux labels and the library/runpath are correct. Generic repart-created
/etc/var fixture paths have no SELinux attrs. Diagnostic `b91da66e3` COMPLETED:
global Enforcing, with AVCs identifying live / and /etc as unlabeled_t. A minimal
stock-labeled first-creation skeleton now has a strict build pass but is UNBOOTED;
test task `b5384b65d` FAILED one legacy finalize-fixture setup; all six new tests
and native metadata-copy fixture passed. Adapted fixture rerun `bcb86e5d8`
COMPLETED: all 137 tests passed on the fixture adaptation. Subsequent small test-only typing/import/loader
cleanup now has no primary LSP findings; latest full rerun `b4868091a` COMPLETED:
all 137 tests passed. Fresh build `b951e85e6` FAILED at the public image-directory
guard for /usr, after source-input mode checks and strict relabeling passed.
Checkout/application umask 022 alone was insufficient: mkosi build still inherited
077. A native synthetic mkosi merge fixture reproduces preserved 0700 existing
directories versus 0755 when constructed under 022. Owner subsequently approved
one bounded harness-corrected cycle. Fresh build `b10858735` COMPLETED: actual
image process inherited 022, private modes remained protected, strict relabeling,
public-image guard, real stock-label template staging and UKI signature checks
passed. Export hashes match and the manifest has 339 RPMs without Rust/Cargo/GCC.
Owned builder/key/state cleanup completed. All three candidates remain separate.
This is a build pass, not a boot pass or independent signed-payload metadata
inspection. Owner subsequently approved the Arch-first non-SELinux direction.
Owned source prototype is now implemented: scripts/mkosi-arch explicitly selects
mini-server-arch before distro discovery; default Fedora remains intact. Arch
summary has 66 direct selections, no compiler/npm/Cargo build hook, separate
cache/output paths and preserved signing/encryption/no-reset coupling. No Arch
build or boot exists. Regression task `be6892b2f` is running. Next validate source,
port native enrollment's Fedora-specific assumptions, then review/freeze an Arch
snapshot and controlled build. Do not automatically boot the retained Fedora.
Do not weaken policy, mask failing services or rebuild blindly. Preserve both
retained candidates. Use only file-backed copies and isolated firmware/TPM; keep
the external homed drive excluded and automatic configuration disabled.

Inherited ParticleOS context is in
[the upstream README](../PARTICLEOS-UPSTREAM.md). Retained bootc technical
facts and test scope are in [its reference README](../../reference/bootc/README.md)
and [the inventory](../../reference/bootc/INVENTORY.md). These are evidence and
reference, not another live plan. Preserve this `.md`, `.actions`,
`.completed.actions` and tool-managed `.mini-server.json` together.

Initial staging implementation (owner committed/pushed at `6a4c73e`): the mini-server
finalize hook calls `scripts/stage-dotfiles.py`, exporting the OS HEAD gitlink's
committed blobs into `/usr/share/personal-os/dotfiles/source` with revision and
SHA-256 manifest. It excludes historical ClearHead/development/archive/OS-build
trees and the committed rclone runtime environment file, ignores dirty/untracked
source and unpinned submodule HEAD changes, and validates internal source symlinks.
A disposable local export of the current pin produced 115 entries and was removed.
The owner created/pushed `origin` at
`https://github.com/ca-mantis-shrimp/personal-os.git`; production release custody
is still open. Follow-up work committed two local dotfiles changes on branch
`personal-os-immutable-hooks`, now at `1338e50103645df922e1411a523edeaf709336d7`:
the paru hook is mutable-Arch-only with container/immutable environment, branding
and filesystem marker guards, and immutable targets ignore the retired rclone
configuration/scripts/units. The OS supplies `/usr/lib/personal-os/immutable`.
The owner subsequently explicitly authorized pushing both repositories. The agent
pushed `origin/personal-os-immutable-hooks` at `1338e50` first, then OS
`origin/personal-os` at `7245209`, without force pushes. The pin is now retrievable;
no dotfiles branch merge, image release or deployment was performed. The separate
live chezmoi checkout was not edited or reset.

The prior eleven-test guard/rendering pass included isolated hook-template cases and a complete
synthetic Fedora/mini-travel-server target archive rendered to disposable storage,
without init/apply or writing the synthetic destination home. Exported source
inspection found no private-key blocks; credential/package/template indicators
were reviewed without printing secret values. This is a limited indicator review,
not proof of absence of all credentials, a real-target apply, image build or VM
pass. All scratch rendering/export data was removed.

Target rendering confirms that Collector and vdirsyncer are auto-enabled by
source symlinks; vdirsyncer still references an old runtime credential/account
mapping, Collector binary provisioning is missing, and Neovim's user unit still
listens on all interfaces. Keep automatic application disabled until the
retry/edit-preserving lifecycle and complete fail-closed workload handling are implemented;
port the private listener/runtime guards from the bootc reference deliberately.
Re-review vdirsyncer mapping and fresh runtime credentials before enabling its
timer. No production secrets, keys, services, disks or platform source changed.
Do not mark the lifecycle action complete.

Current account prototype: `mini-server` now stages `personal-os-account.service`
and `/usr/libexec/personal-os-account` as profile-only content. Enrollment consumes
host-specific runtime systemd credentials (`personal-os.account.json` and
`personal-os.console-password.hash`) from protected credential storage, not build
inputs. The README defines schema/version 1; the chosen target values are dab,
UID/GID 1000, wheel, mini-travel-server, desktop public key, and scoped NOPASSWD.
No actual key or console hash was read or provisioned. The profile no longer bakes
its hostname or supplies upstream demo VM credentials; it masks homed/firstboot,
omits the homed authselect feature and selects daemon SSH with key-only/root-denied
policy. Other inherited root/home/signing and live/recovery UKI defaults still
need deliberate review before builds or installation.

The helper rejects pre-existing untracked accounts, numeric identity collisions,
symlinked/protected-path conflicts and divergent enrollment configuration. It
preserves home data without recursive chown, installs initial keys/sudo policy,
and keeps a root-owned pending/complete journal in
`/var/lib/personal-os/account.json` without password/hash values. Completed boots
need no original inputs and do not reset passwords or edited authorized keys;
identity/hostname/sudo changes fail for operator review, not silent repair. The
SSH daemon and user manager require account success. Workloads have startup-only
`ConditionPathExists=/run/personal-os/chezmoi-ready` guards; enrollment does not
create that marker, so source autostarts stay gated. Do not bypass it manually.
Runtime dependent-service stopping, secret readiness and automatic chezmoi
application are still incomplete, not satisfied by account enrollment.

Thirty-two offline tests pass. Account/NSS/hostname/password/relabel operations use a
fake backend and disposable synthetic files only; sudoers syntax was checked with
real visudo on a temporary file. Unit syntax/dependencies were checked offline
with ExecStart adapted to the local helper path; authselect logic ran only as an
isolated block with a stub. Tests cover retries including the post-password /
pre-completion window, local edit preservation, conflicts, protected journal/schema
failures and absence of caches/credential stores from extra trees. Synthetic buildroot
tests verify homed masks and that inherited factory capture preserves the SSH
policy. The console-hash setting is parsed with libxcrypt using a non-secret probe,
not authenticated against a real passphrase. These are NOT
real Fedora account commands, a package/image build, enforcing SELinux, actual SSH
or console login, or a VM/update/rollback pass. The installer-to-credential-store
handoff also remains to be validated; do not manually create the user and expect
implicit adoption. No host/server accounts, passwords, services, disks, credentials,
platform source or submodule revision changed. All synthetic artifacts were removed.
Follow-up source lifecycle prototype now stages `/usr/libexec/personal-os-chezmoi`
without an automatic startup unit. Enrollment publishes a root-owned, runtime-only
account context (username/UID/GID/hostname/version, no keys/hash); the child CLI
requires this identity, successful active enrollment and enforcing SELinux. Factory
staging adds a policy containing only OS-recorded ancestor pin IDs, capped at 256
pin-changing OS commits; missing shallow ancestry is not guessed or fetched. No
Git history objects, live checkout state or credentials are exported.

The user helper verifies the factory manifest and journals source promotion plus
applied revision/context privately under `~/.local/state/personal-os`. Conservative
file-level three-way source comparison preserves unrelated edits/deletions,
untracked files and target Git metadata; conflicting edits fail before promotion.
Atomic per-file writes and a helper lock support interrupted retries without a
force reset. Chezmoi alone generates config/templates; local generated-config
conflicts retain a private candidate for review. Native apply uses BOTH
`--less-interactive` and `--error-on-conflict` with force/interactive disabled and
a dry-run preflight: error-on-conflict alone does not protect previously unmanaged
files. Output is captured/suppressed rather than exposing secret-bearing errors.
The immutable and compatibility container package-hook guards are set, while
actual target machine/distro/home template identity is retained.

Successful apply records the revision only afterward; same pin/context boots do
not reapply over edits. Context changes request another conflict-checked apply.
Forward transitions require an OS-recorded ancestor allowlist entry; older or
unrelated pins (including never-before-seen ones), unknown state schemas and
changed exports under the same pin fail rather than downgrade mutable state.
Ancestry is not application-schema compatibility proof. Coordinate editing during
apply; this is not a whole-home transaction, application-state backup or restore.

Sixty-two offline tests now pass, including source conflicts, untracked/source/home
edit preservation, Git metadata preservation, pre-existing targets, template/config
conflicts, first-boot failures, interrupted promotion/retries, unknown schemas and
older/unrelated pins. All lifecycle chezmoi calls and workload-state checks are
mocked: NO real init/apply, Fedora account/SELinux/systemd/console/image/VM or
update/rollback pass occurred. Disposable fixture data was removed. No publication,
production changes, submodule advance or readiness marker creation occurred.

The owner subsequently authorized publishing both local prototypes; account
commit `da3be00` and lifecycle commit `fa74ae0` were pushed to `origin/personal-os`.
The existing dotfiles pin was already published and did not advance. This is source
publication only, not an image release, signing or installation approval.

Root-controller follow-up now stages `/usr/libexec/personal-os-configuration` and
`personal-os-configuration.service`, explicitly DISABLED by preset. The controller
revokes readiness, validates trusted runtime context/NSS identity, stops and verifies
known system/user workloads (timer before service), then executes the existing
child as the enrolled user using runuser and a clean environment. It never forwards
manager enrollment credentials/tokens or runs home/source code as root. Active user
managers are reloaded; stopping/verification is repeated after success and failure.
Stop/query/reload errors block apply while other stops are still attempted. SSH,
Tailscale and the user manager are not stopped; inactive user managers are not
started for cleanup. Identity/bus failures require operator review and cannot
prove all workloads stopped. The service uses control-group cancellation and
ExecStopPost cleanup for failure, partial startup and stop; real cancellation and
ordering still need a VM. Success NEVER grants readiness or starts workloads.

Eighty-two offline tests pass, including controller ordering, child failure/retry,
stop/verification/reload/enrollment failure, cleanup-only execution, missing/bad
identity, symlink/lock protection, sanitized child invocation and mocked timeout
process-group killing. Systemd/runuser/workload operations are fake; unit verification
uses adapted temporary local paths. No real stop/start, init/apply, credential
provision, image/VM, SELinux or rollback test occurred. This controller chunk remains
local/unpublished and does not complete the lifecycle action.

The owner adds frequent Claude Code/pi agent operation as an important server use
case, including shpool persistent sessions, and authorizes local implementation.
Agent tooling is OS-owned; authentication, workspaces, settings and session state
are target-user mutable data. This does not authorize production agent execution,
host root access, credential import or public artifact release. The owner clarifies
that their existing sandbox setup runs agents as root INSIDE their own sandbox
environments. The sandbox, not a separate host agent user, is the isolation boundary.
No dedicated host agent account or per-agent host user is wanted: multiple concurrent
sandboxes are managed through the existing operator account. This supersedes the
previous separate non-sudo agent-user recommendation; keep dab's enrollment policy
unchanged. Reuse and inspect the existing sandbox setup rather than introduce a
competing launcher or assume a particular runtime. Sandbox root must not imply host
root: validate namespace/identity boundaries, mounts/devices, management-socket
access, per-sandbox credential/writable-state scoping and explicit workspace sharing
with enforcing SELinux. Exact runtime integration and concurrency tests remain
unvalidated; this owner architecture clarification is not a containment pass.
Host CLI packaging does not automatically provide CLI tools in sandbox images;
review existing sandbox tool composition and version/update compatibility.

Agent packaging prototype now selects image RPMs Node.js/npm/Git/ripgrep/fd/tmux/
Starship and a mini-server mkosi.build.chroot hook with explicit build networking.
Exact candidate pins: pi @earendil-works/pi-coding-agent 0.85.1 (public npm metadata
matches installed documentation; 161-entry transitive integrity lock), native
Claude Code 2.1.288 (official manifest checksum/size, not deprecated npm installer),
and shpool 0.11.5 (crates.io checksum, published Cargo.lock, locked source build).
Only runtime payload/provenance enters DESTDIR; Cargo/Rust/compiler packages,
caches and NPM config remain in the disposable build context. No installer,
agent process, credentials or live user configuration runs/imports during build.
Artifact checksums are publisher HTTPS assertions, not independent signing trust;
Fedora/toolchain snapshots and reproducible build provenance remain release work.

Shpool's private per-user socket/service are disabled; control-group cleanup and
NoNewPrivileges do not make it a sandbox. Review that disabled prototype setting
against the existing sandbox launcher: inherited NoNewPrivileges can prevent
setuid newuidmap/newgidmap required by rootless container namespace setup. Do not
change a live service or weaken sandbox confinement blindly to fix it. Shpool is
interactive host management state, not the agent containment boundary or an entry
in the configuration controller's server-workload stop list. Review lingering,
logout/SSH-loss reconnect, TUI modifier keys, daemon-loss/reboot session recovery,
resource limits and maintenance quiescing in a fresh VM before enabling it. No
session survives daemon/OS restart merely because shpool is installed. Agent
provider login/OAuth/token/session data stays private under target user control;
never stage desktop auth or trust files. Core wrappers discourage self-updates;
OS image updates own core versions, user configuration owns extensions/deps.
Existing dotfiles pi packages include floating names and @latest, and Neovim has
an explicitly permission-skipping Claude adapter. Review/pin executable extension
resources and validate the existing sandbox isolation before unattended operation;
do not edit the
separate live checkout or silently advance the submodule. No agent user, linger,
production service or credential changes occurred. 93 offline tests now pass (including fake npm/Cargo/staging, update wrappers,
checksum failures, effective mkosi summary and adapted-path user-unit verify).
Real checksum-verified shpool source review confirms its 191-package Cargo.lock
and Rust >=1.85 declaration; that disposable archive was removed uncompiled.
These checks and source metadata inspection are not an actual Fedora build,
CLI startup, authentication, session, SELinux or booted VM pass.

The owner has now approved slimming the inherited scaffold into OUR fork.
Inactive upstream examples were relocated byte/link-identically (128 tracked
files) under `reference/particleos/`; this is reference material, not a second
plan or selectable production recipe. Remaining active configuration is Fedora
44 plus mini-server, with fork-owned packages, presets, factory links and branding.
The normal signed UKI is the only boot profile. Demo/live/installer, public-storage,
reset/TPM-clear and debug profiles are no longer loaded, and no replacement rescue
or installer credential handoff has been proven. Do not re-enable demo access to
make a build/VM pass. The `PersonalOS` identity remains coupled through discovery
filters, `%M` partition/artifact patterns and timestamp-version GPT label limits;
no deployed image exists to migrate from the previous `ParticleOS` labels.
Fedora ID/version and `particleos-fedora` ancestry are preserved for pinned
chezmoi guards, along with immutable environment and filesystem markers.

100 offline tests pass after trimming, with mkosi 27.1 configuration inspection,
Fedora headless tools-tree selection, signing/enforcing/auditing settings, reset
exclusion, source staging and synthetic fork-branding/archive rendering. Removed
package selections are not proof those packages have no transitive dependencies;
image size/package closure requires a real build. Byte/link archive verification,
shell syntax and diff whitespace checks also pass. ClearHead doctor reports
zero violations and two charter-without-objective warnings; unrelated charter
metadata was not repaired, and the completed action history was unchanged by the
CLI description update. No build/guest/actual apply,
SELinux/recovery/update pass, key generation, production change or publication
occurred. The dotfiles pin is unchanged and configuration/shpool remain disabled.

### First candidate build and rootless follow-up (2026-10-03)

An uncommitted trimmed candidate based on OS HEAD
`608105bccdd75330a8ca8ae54cd79763a9d42776`, unchanged dotfiles pin
`1338e50103645df922e1411a523edeaf709336d7`, mkosi 27.1 and image version
`20261003000100` built in an isolated Fedora Cloud Generic 44 KVM VM. The public
cloud image checksum/signature was checked against Fedora 44 key
`36F612DCF27F7D1A48A835E4DBFCF71C6D9F90A6` from the pinned Fedora reference image.
The initial restricted Docker builder failed pivot_root with EPERM; unrestricted
privilege/security disabling was not used to make it work. The VM stayed enforcing,
with 4 CPUs/8 GiB RAM; build unit capped at 3 CPUs, 6 GiB and 20 minutes, no swap.
All disks were files, not host devices. Disposable two-day signing material stayed
outside Git/build source and was used only for this isolated test.

Real package resolution rejected the assumed Starship RPM. The source hook now
builds Starship 1.24.2 from its checksum-pinned crates.io archive (379,095 bytes),
published 428-package Cargo.lock and Rust >=1.90, alongside shpool with two Cargo
jobs. No floating installer, target package hook or agent process was executed.
Strict relabel initially rejected target-only policy types; updating the builder's
stock targeted policy to 44.11 and loading matching packaged Radicale and smartmon
modules fixed it without permissive mode or custom policy. A future Podman build
also needs matching container-selinux types loaded in its enforcing builder.

Successful build: 310 runtime RPMs; Rust/Cargo/GCC absent from the final manifest;
strict target relabel and dotfiles finalize passed. Signed UKI plus usr/verity/
verity-signature partitions were generated, and `sbverify --cert` passed. Raw
image: 2,189,987,840 logical bytes, about 732.7 MiB allocated; UKI 64,262,128 bytes.
Retained artifact identities (public integrity digests, NOT password hashes):
- raw SHA-256 `2802a9afd472b0ed292edcf0252376284dad8cbd79abb6f3f153a47a63dad941`;
- UKI SHA-256 `b58759950baca16d68605bd4a20ca1bb9bfeca3d00cfcf9f0e2f4b2811ac2fd5`;
- manifest SHA-256 `b876d383d6a4640c6882fa8da9412609030369ff37b1e0bd495b0668c27ad9c0`;
- initial tracked-diff digest `f66a72b1c2c85d7d2044c9715d4f4601d536d4f0f41dedf1f0001d4ec5fc3485`;
- Starship/config source-update archive digest
  `9471db16698d9b711e1f5a54ffa71530d013d822abaf35d185bd59fae1eaf488`.
These identify a dirty test candidate, not a reproducible published release.
All associated signing/SSH keys, synthetic runtime credentials, VM/TPM state,
images/caches and source scratch were removed after the builder/TPM stopped;
only these public integrity/provenance facts remain. Fresh testing needs new keys.

The builder was powered off. Target preparation stopped before QEMU launch
because host qemu-img is absent; no target boot/ABI, Secure Boot firmware, TPM,
SSH/console, SELinux runtime, update or recovery pass occurred. A future test may
use a sparse raw file/copy and file-backed growth rather than installing host
packages. New Podman/account changes are NOT in this first artifact.

Owner-requested current integration:
- Explicit core Podman/rootless RPMs (98 total selections), no package-installing
  user hook or extra launcher. Factory container config copies only when absent;
  mutable site policy/rootful Quadlets are preserved. System/user API sockets,
  auto-update timers and restart services are disabled by preset.
- Account bootstrap allocates free 65,536-ID subuid/subgid blocks from 100,000,
  avoiding both existing mappings and NSS IDs. A separate protected pending/
  complete `rootless.json` ledger preserves the original account-journal schema.
  Partial writes retry the same allocation. Recorded mappings never silently
  change, disappear, overlap or shrink; container state is never recursively
  chowned/reset. Valid pre-existing single ranges for an already trusted completed
  account may be retained; untracked/composite/ambiguous mappings require review.
  Native Shadow PID locks serialize writes; dead, validated PID locks recover;
  live/ambiguous locks fail. Local files subid delegation is required, including
  validated Fedora authselect/factory link chains; no unreviewed NSS plugin.
- Enable linger once for the operator after mappings succeed, before account
  readiness. Preserve subsequent explicit disable-linger instead of forcing it
  back on every boot. This starts no shpool/API/agent or guarded server workload.
- Shpool explicitly sets NoNewPrivileges=no for setuid mapping helpers (also
  permits operator sudo); retain private socket, umask, control-group cleanup and
  disabled preset. Host management sessions are not agent confinement. Root
  enrollment/configuration retain NoNewPrivileges=yes; inspect inherited user-
  manager/session settings in the real VM too.
- RuntimeDirectory now provides the account service's /run namespace exception.
  Native checks found the previous CREATE_MAIL_SPOOL -K override invalid in
  shadow 4.19; suppression is now a factory useradd default instead.

119 offline tests pass, including allocation/conflicts, shared-lock/dead-PID
recovery, partial-table retries, lingering failure/once-only behavior, immutable
mapping preservation, authselect/hardlink config and preset policy. Opt-in
`python3 tests/check_rootless_native.py` passes native Fedora useradd, getsubids
and Shadow lock interoperability (with positive unlocked control) in a networkless
container with only CHOWN/DAC_OVERRIDE and NNP. Logind is mocked and the state
hierarchy synthetic/protected; bootc's existing /var/lib was group-writable, so
actual target parent permissions still need validation. This is NOT a rootless
Podman namespace, real lingering, shpool or enforcing-console VM pass.

Next build the current candidate with matching stock builder policies, then prove
minimal boot/account, stable subids, real linger/logout, Podman unshare/storage/
pasta/cgroup v2 and scoped SELinux mounts from SSH AND shpool in a fresh isolated
VM. Check actual policy loading/factory availability and namespace paths, not
just an enforcing flag. Update/rollback must retain subordinate ownership and
container/home state without remapping. Sandbox extraction remains the other
agent's work; this repo consumes it, not a competing runner. Production signing-key custody/enrollment and independent rescue
access still need owner decisions; disposable isolated VM keys are allowed, not
production enrollment. Retain the existing UKI/verity/sysupdate coupling. Then
implement workload-specific private-listener/binary/runtime-secret gates,
readiness/health checks and reviewed controller activation. Keep automatic
application disabled and never create the marker manually. Test
actual native CLI first boot, exact-directory deletion conflicts, partial apply,
retry after power-loss windows, SELinux labels, updates/rollback, schema
compatibility and independent state recovery; offline mocks are not that evidence.

Start by inspecting `mkosi summary` (the default is the `mini-server` profile)
and the effective configuration, then run the offline smoke tests with
`python3 -m unittest discover -s tests -v`. Implement the profile's account/mutable-state/SELinux policy and
chezmoi staging/first-boot lifecycle before claiming the image can just run.
Reuse upstream UKI/verity/sysupdate machinery, not an unrelated custom updater.
The dotfiles package hook has been narrowed locally as described above; preserve
its immutable guards and record/test future user-config changes as committed
submodule pins. Do not reset or automatically advance either source checkout.

Then test a fresh isolated VM: intended UID/GID 1000 account, scoped passwordless
sudo, console passphrase and key-only SSH; real-target chezmoi conditions,
retry/idempotence, user-edit preservation and service ordering; enforcing SELinux;
absent/degraded/wrong USB storage; fresh identities; network loss, updates,
rollback and separate mutable-state recovery. Include a failed/incomplete
chezmoi application to prove dependent services stay stopped. OS rollback does
not restore mutable home/application state: test schema/config compatibility,
independent restore and safe handling of an older dotfiles pin. Package
installation belongs in the immutable image, not target-side chezmoi hooks.
The desktop kernel
and modules now match and privileged loop-control opens; the earlier builder
blocker is resolved, not a reason to reboot again.

ClearHead release work is being handled by the owner in platform. Consume a
reviewed artifact/pinned source when available; it is not required to publish
every platform crate before designing/test-driving this OS lifecycle. Tailscale
repository and Collector binary provisioning remain explicit image dependencies.
Do not enable calendar syncing without the ClearHead binary, fresh credential
and verified collection mapping.

The owner has published the initial fork/staging source; no image release or
deployability is claimed. Review `git status` and `git submodule status` before making any
new changes. The live `~/.local/share/chezmoi` checkout has migration-file
removals and a forwarding README awaiting its own review/commit; do not silently
commit or reset unrelated dotfiles work. The pinned `dotfiles/.clearhead` content
is historical and must not be registered as another active workspace.

Local images
`mini-server:validation` (historically VM-tested minimal image) and
`mini-server:services` (expanded image, container-tested only) remain available.
No VM, builder or test registry is running; all disposable test credentials,
configuration, storage and artifacts were removed. A future test needs fresh
isolated artifacts; the desktop kernel/module blocker is already resolved. Do not reboot
this desktop automatically or look for retained credentials. Read the new image
README's test scope/blocker details before claiming migration readiness.

ClearHead action lint has informational I001 findings for historical completed
rows imported from the original plan without completion dates. Do not invent
dates or normalize unrelated charters simply to silence diagnostics. During this
session CLI completion operations auto-stamped several already-closed historical
rows; those unsupported dates were removed from the action text, preserving
actual new decision/completion dates and the tool-managed sidecar. Check future
CLI diffs for that behavior rather than accepting invented historical dates.

### Fresh candidate validation (2026-10-04)

The owner asked to continue local validation and explicitly excluded the reinserted
external homed drive from all work. No external/host disk was mounted, formatted
or passed to a VM. Fresh source input is OS HEAD
`e8ee0fe366e3c7be00e8bcce97a27c3c1bce8c2d` with unchanged dotfiles pin
`1338e50103645df922e1411a523edeaf709336d7`. All 119 existing offline tests passed;
the local build-helper follow-up adds ten packaging checks, for 129 passing tests.
Active LSP checks found no Python type errors after test import guards were added.
Generic urllib/tar security findings were reviewed as false positives: publisher
HTTPS URLs are explicitly allowlisted before I/O, redirects must equal the original,
and checksum-pinned crates use Python's `filter="data"` extraction.

The Fedora Cloud Generic 44-1.7 input passed the signed Fedora CHECKSUM against
key `36F612DCF27F7D1A48A835E4DBFCF71C6D9F90A6`; image SHA-256 is
`28680fe5b371a5a82ebf43a31926e086a168e59949d03969c5093e7071f90b7f`.
QEMU grew only a disposable qcow2 copy through QMP; host qemu-img remains absent.
Builder SSH is loopback-forwarded with fresh keys, no production identities or
shared host trees/devices. Enforcing builder startup and stock module loading were
observed. Setup explicitly upgrades stock selinux-policy-targeted to 44.11 and
container-selinux to 2.251.0 and checks container/Radicale/smartmon modules.
Installing an already-present package alone did not upgrade the cloud baseline.

Several attempts stopped during disposable runner setup (cloud-init hostname
warning, unavailable PyPI mkosi package, launcher/source ownership/permissions,
and missing distribution-gpg-keys). These are not image/target failures or passes.
The runner now preserves hostname during NoCloud setup, uses root-owned VM-only
stock-labeled tooling and a bounded CLI scope, and installs the distribution key
package without disabling repository checks. Exact installed Arch mkosi 27.1
Python package was copied privately rather than replacing the desktop CLI;
archive SHA-256 `d566fc48f4a17da8ea5156ce0051a275b7902607bcd639482910f041d0868694`.

The subsequent real image build reached the agent-tool hook, but Starship's
locked Cargo install command exceeded its 1,200-second limit (captured output
was not inspected to distinguish compilation from dependency-network waits).
No candidate or partial agent runtime was exported. Each failed VM stopped;
its signing keys, SSH keys, seed and credential-bearing qcow2/firmware state
were removed.
Local `scripts/build-agent-tools.py` now permits Cargo install up to 2,400 seconds
while retaining the 1,200-second npm budget; timeout errors suppress raw captured
output. Metadata errors also fail with suppressed raw content; HTTPS publisher
validation and its rejection tests are explicit. The 124-test pass includes
bounded-command budgets, timeout suppression and malformed input/installed metadata.

Revised isolated build `b906dc257` also failed: an artifact download in the native
crate loop hit a TLS handshake timeout. Its source patch SHA-256 was
`66aa10f16fc6c05e4bb501b443092478ab7aee276b20f3ac070e3a00fa70b603` on the OS
HEAD above, not a committed/released candidate. It used 6 GiB/4 vCPUs,
3-CPU/5-GiB/one-hour build limits, two Cargo jobs and no guest swap. No artifact
was exported; the builder stopped and its keys, seed, qcow2 and firmware state
were removed. Public inputs/test scripts remain privately under
`/home/backup-admin/.cache/personal-os-validation/run-gLX7DUSa`.

The next local follow-up adds exactly three transport attempts with 1/2-second
backoff, private per-attempt downloads and verified, no-overwrite publication.
Only transport/transient HTTP failures retry; bad integrity, size, redirects or
publisher URLs fail immediately. Captured transport errors remain suppressed.
The updated source/test patch SHA-256 is
`d073d63f6e4c82db43cb416efd398d28b7d991b270c696b4251258dc608eb681`;
all 129 tests pass and an active diagnostic probe reports no findings on the two
changed Python files. Final cold-build attempt `b5299e336` FAILED and builds
were stopped pending owner review. It completed the agent-tool build hook and
systemd-boot signing, then strict setfiles relabel rejected
`/buildroot/usr/bin/pesto` with `Invalid argument` (exit 255). No final
image/UKI/manifest or factory dotfiles export was retained. The 6-GiB/4-vCPU
enforcing builder stopped; its signing/SSH keys, seed, qcow2 and firmware state
were removed. Only private public inputs/scripts and
bounded task logs remain. No further cold build was launched until the subsequent
owner authorization recorded below.

The target transaction installed `passt` and `passt-selinux` at
`0^20260728.gf8df3f1-2.fc44`; the builder installed/upgraded container policy but
omitted passt-selinux. Read-only upstream checking confirms that exact Fedora
subpackage ships `/usr/share/selinux/packages/targeted/pesto.pp` (plus passt,
pasta and passt-repair modules), and upstream pesto policy declares
`pesto_exec_t`. Missing matching stock builder pesto types are the leading
explanation, not yet proven by a fresh enforcing relabel pass. References:
https://packages.fedoraproject.org/pkgs/passt/passt-selinux/fedora-44-updates.html
and https://archives.passt.top/passt-dev/991833a/s/?b=contrib%2Fselinux%2Fpesto.te.
The private test script now adds/upgrades passt-selinux and requires loaded passt,
pasta and pesto modules before build; at that stop the correction was UNRUN.
Next inspect actual loaded policy/file-context compatibility, then resume one
isolated build; keep strict relabel and enforcing SELinux. Do not disable security,
silence setfiles, invent a custom policy or treat the successful transient tool
compile as a retained image/ABI/target pass.
No target boot, Secure Boot firmware/TPM, native account/rootless/linger/shpool,
actual chezmoi apply, update/rollback or recovery result is claimed yet. Automatic
configuration and shpool remain disabled; no readiness marker, external-drive
access, platform change, submodule advance, publication or production operation
occurred.

#### Authorized policy-matched retry and reader notes

The owner subsequently authorized resuming the isolated builder-policy correction
and asked for reader-facing notes during the work. Task `b341164f0` COMPLETED
successfully with the unchanged tested source patch in a fresh file-backed VM.
The private bootstrap script SHA-256 is
`7c83abebd6d75d9bec3573a1b7aac193eaf950706efff70cbbb15ad76177c59a`.
Stock passt/pasta/pesto modules loaded successfully; matchpathcon and chcon on
one private disposable file proved that the enforcing builder accepted
`pesto_exec_t`. The probe was removed. Full strict target relabel then passed,
followed by both finalize hooks, signed usr/verity/signature artifacts and the
signed UKI. `sbverify --cert` reported Signature verification OK. The builder
stopped and its private signing/SSH keys, seed, qcow2 and firmware state were
removed. The external homed drive remained excluded; no production or publishing
operation occurred.

Retained private candidate: image version `20261004000100`, Fedora 44, mkosi 27.1,
339 runtime RPMs, including Podman 5.8.7, with Rust/Cargo/GCC absent from its
manifest. Raw image is 2,247,905,280 logical bytes; mkosi reported about 788.4 MiB
allocated before SCP export (host SCP copies are not a sparse-size measurement).
UKI is 64,262,616 bytes. Host-side SHA-256 rechecks match the builder results:
- raw: `591d816b729290e9bf0413dd91031b25fbaaa813914330df85f8984bae7d6820`;
- UKI: `9b54792116cefb955f9a4bda51472117db066b0c9239b4145f3d08707b84cb34`;
- manifest: `334b6b8991c6b284004609523138737e1b082f37ec7fa50de8d44802bf6a8d97`.

Artifacts and the disposable public certificate are private under the existing
scratch `artifacts/` directory, not Git or a published release. This is the
first retained current-Podman candidate, not a boot pass. Firmware utility task
`b73d219a6` FAILED before creating firmware or launching a VM: PyPI has no binary
crypt_r wheel. The checked source release is crypt_r 3.13.1, SHA-256
`5bd46ad51f5b7fe5f0ecf49d8ba2cafd6fbd43aa3bb5efbcaa6b44df6340c1a6`.
Its complete build configuration and small CPython/libcrypt wrapper were reviewed.
Corrected task `b579a201d` COMPLETED: that reviewed dependency built in the
private virtual environment with existing host headers/compiler and a clean
environment. No desktop distro package or target security changes were made.
Setuptools is pinned to 80.9.0; other dependencies remain binary-only.
The utility pins virt-firmware 26.9 and checks its PyPI wheel SHA-256
`64d0078e6dd0c82a1df3a97c3cc8a149340068095cf8cfb6beb02005e3194160`, records
all dependency-wheel digests. The tool successfully enrolled only the disposable
public certificate into a copied VM variable store. No host firmware/key
enrollment was performed. First target task `b4210925c` FAILED at its SSH
readiness deadline. The console proves that Fedora kernel 7.2.8 booted with
Secure Boot enabled and lockdown active; PID 1 received both named runtime
credentials without logging their values. Repart completed the disposable layout,
cryptsetup opened root, and encrypted Btrfs `/sysroot` plus `/sysroot/usr` mounted.
At about 6.66 kernel seconds, switch-root froze with Failed to load SELinux
policy. This is not an account/SSH/rootless pass: those probes were never reached.
The owned VM/TPM stopped; its disk, firmware, credentials and SSH keys were removed.
The original candidate remains unchanged. No account was manually pre-created.

Leading hypothesis is policy availability at the early root boundary, not another
builder relabel failure. The failed recipe seeded only `/var`/journal directories;
factory `/etc` is stored under `/usr/share/factory/etc`, and the fork-owned
etc.conf has no SELinux link. PID 1 must load policy before normal target tmpfiles.
Read-only utility task `ba62ee537` installed signature-verified erofs-utils but
failed opening the copied 0600 usr file: all capabilities, including DAC override,
were dropped. Its container was removed. Corrected task `b5ff37b3c` completed
with only a disposable public-image copy made 0644 inside a private directory;
the original stays 0600 and the container gains no capabilities or privileges.
Task `b5ff37b3c` COMPLETED and its container/input copy were removed. The actual
EROFS payload has factory SELINUX=enforcing, SELINUXTYPE=targeted and a regular
3,779,095-byte policy.35 (binary version 35, magic 0xf97cff8c). Only share/selinux
exists as a vendor policy path; no stock tmpfiles SELinux rule was found. Thus the
policy exists in signed /usr but the blank root lacks its normal lookup path.
No host mount/device or custom policy was involved. This file-parser result is
not an enforcing-boot validation.
Upstream systemd 259 SELinux setup confirms the fail-closed path and warns that
libselinux does not supply useful errno here. The correct repart option is
MakeSymlinks (since systemd 257), not MakeSymbolicLinks. Systemd 259 documents
this specifically for links needed before tmpfiles and implements it at filesystem
creation. The first correction created /etc and
`/etc/selinux -> /usr/share/factory/etc/selinux` at that early boundary, without
copying packaged policy into mutable /etc. Btrfs, TPM encryption and no-reset
policy remain unchanged. Existing root filesystems are not reinitialized, and
mutable overrides remain preserved.

Two regression tests were added: exact recipe/security guards and a separate
64-MiB generic ext4 file fixture that exercises native MakeSymlinks, inspects the
link with debugfs, then proves an updated recipe leaves the existing image intact.
It uses offline mode, random IDs and only generated regular files; it does not
open host block/TPM devices, mount filesystems or claim encrypted-Btrfs/SELinux
boot coverage. Active LSP reports the changed tests clean. Full suite task
`b036c7f70` COMPLETED: all 131 tests passed, including the native link fixture.
The prior candidate retains its original hash and failing layout. The root
correction has now BUILT, but has no completed target boot pass.

One deliberate fresh build with this verified correction COMPLETED as task
`bb4b20652`, not an automatic retry loop. Its separate private directory is
`/home/backup-admin/.cache/personal-os-validation/root-policy-rlRM4N9w`, image
version `20261005024339`. Source HEAD and dotfiles pin remain as above. The new
four-file source/test patch SHA-256 is
`870e86527dd592b1523d10cc14249b1323c5682d7148c1db43930dd44c5628e6`;
the private builder script SHA-256 is
`933c9d5cd34dace58d567274d1844d3d4271a0e79254b5eff87c22c7afd5e470`.
The patch applied cleanly to a disposable checkout of the original bundle. That
checkout was removed; the prior raw artifact's original hash was rechecked.
Fresh signature-verified public cloud input, stock enforcing policy checks,
6-GiB/4-vCPU VM, 3-CPU/5-GiB/one-hour build cap, no guest swap and two Cargo jobs
are unchanged. Preflight saw about 9.4 GiB available host RAM and 211 GiB free
in scratch storage. Strict relabel and signed UKI verification passed. The builder
stopped; its disposable keys, disk, seed and firmware state were removed. No old
artifact/certificate was overwritten, no external drive was inspected or attached,
and no production operation or publishing occurred.

The corrected candidate has 339 runtime RPMs, no Rust/Cargo/GCC, a
2,247,892,992-byte raw image and a 64,262,616-byte UKI. Host SHA-256 rechecks match:
- raw: `82a160269679141ac3aaa95d1b9c349a4a10be847c04b0215ad23f328d79b6eb`;
- UKI: `cc3691d5b893ac9778518ce907f90cb77193409c17a19b8c06db356435d756d9`;
- manifest: `a58e2e07d29aeee091b7345ec389785741e3e031d570e78ac2fc008c5b89f134`.

Second isolated target task `b8f48ad42` FAILED at its SSH readiness deadline. The existing verified private
firmware utility enrolled this candidate's new disposable public certificate into
another copied VM variable store, not the desktop. SSH keys, account inputs,
software TPM state and target disk are all newly generated. Limits/gates remain
unchanged. The new private launcher SHA-256 is
`d6867243395c2303aad7e1adb25795e88fb82c8cde603d01d8eb439da2b54d8e`.
Its fixed fatal markers cover the old policy freeze/panic, but did not cover this
new reboot failure. Syntax checks passed; the active LSP found no errors but
remained inconclusive on its push-only server. The private console proves
Successfully loaded SELinux policy (37.742ms on the last captured boot), normal
main-system startup and successful initrd-switch-root deactivation. The original
policy-path blocker is therefore resolved in this candidate, not a full boot pass.
PID 1 cannot create /etc/machine-id (Permission denied); preset operations report
missing /etc/systemd links. Journald/modules-load exit 127, pcrmachine exits 1 and
its existing failure action forcibly reboots the guest. No raw AVC or useful
loader stderr was captured, so missing labels/configuration are hypotheses, not
a proven cause. Owned VM/TPM stopped; test disk, firmware and credentials were
removed. Account/SSH/rootless probes remain unreached. No bypass was introduced.

One bounded diagnostic boot of the SAME unchanged candidate COMPLETED as
`b223e4d29`. Documented systemd 259 unit-dropin credentials route only stderr from
journald, modules-load and pcrmachine to the private serial console. No debug
shell, verbose credential logging, masking, manual account or policy relaxation.
Separate diagnostic-console.log, diagnostic-qemu.log and diagnostic-results.json
preserve the failed boot's original evidence. Fresh software TPM/disk/credentials,
the existing memory/CPU caps, a 120-second observation bound, and a new explicit
pcrmachine-reboot stop marker apply. Acceptance probes are not run; even diagnostic
SSH readiness would not constitute a normal configuration pass. Private launcher
SHA-256: `4031db2ee400bf747e4fd640705a624a2ce214f3fe65a49f903dde3d9bced1b4`.
Syntax and port preflight passed; active LSP reported no errors but was inconclusive.
The diagnostic ended at its explicit pcrmachine-reboot marker; SSH stayed false.
Exit 0 means successful diagnostic capture, NOT successful OS startup. Journald
reported: error while loading shared libraries: libsystemd-shared-259.9-1.fc44.so:
cannot open shared object file: Permission denied. This is an access failure,
not a reported absent library. /etc/machine-id and /var/lib/systemd/nvpcr creation
also returned Permission denied. No direct AVC or live inode contexts were
captured. The owned VM/TPM, disk, firmware and synthetic credentials were removed.

Offline access inspection `bd7093698` COMPLETED against only a disposable
copy of this candidate's public usr partition. A capability-dropped, no-new-
privileges utility container uses package signature checks, dump.erofs inode
metadata and readelf dependency/runpath parsing; it executes no candidate binary
and receives no host disks, mounts, credentials or extra privileges. The private
script SHA-256 is
`6b830066955a1e54071fc05aaf0f86a92d2d928e6d4ba0a4fffe8b09da28846c`.
Extraction uses no-preserve, so extracted modes/labels cannot prove image metadata.
Native dump.erofs proves /usr and /usr/lib are root-owned 0700; /usr/lib/systemd
is 0755, /usr/lib64 is 0555, and lib64/systemd plus the expected shared library
are 0755. Journald/modules-load both record RUNPATH=/usr/lib64/systemd and the
exact shared-library name, which exists. Factory /etc is 0755 and ld.so.cache is
0644. The utility container and copied input were removed; original artifacts
remain unchanged. This is a real payload directory-permission defect.

Independent tiny checkout fixture (temporary Git index; host index/source untouched)
reproduced the builder's umask 077: usr/lib directories 0700 and a tracked public
unit 0600. With umask 022, these are 0755/0644. Fixture/index were removed. This
explains the world-inaccessible-unit warnings and the actual signed directory
modes, not a defect to fix with permissive mode or extra guest capabilities. A
future checkout needs a scoped normal payload umask plus input-mode assertions;
keep parent/key/credential protection 0700/0600. This does not yet establish every
root-service denial, especially machine-ID writes by root.

A read-only bounded EROFS inode/xattr decoder cross-checks the native NIDs/modes,
rejects unsupported formats and prints only selected SELinux contexts. Retained
access-labels.json shows /usr=usr_t, selected library dirs/DSO=lib_t, factory
/etc=etc_t and ld.so.cache=ld_so_cache_t. No inode is modified or image mounted.
Decoder SHA-256:
`5f671d1747f8ca2694b32a563ed0bea5267351a0215f5849dd4f10250c978c70`.
Layout reference: https://github.com/torvalds/linux/blob/v6.19/fs/erofs/erofs_fs.h.
A separate 64-MiB generic offline ext4 repart fixture was removed after debugfs
found no SELinux attrs on generated /etc, its selinux link or /var directories.
This is NOT a target encrypted-Btrfs/boot proof; it motivates live context checks.

Bounded diagnostic boot `b91da66e3` COMPLETED on the unchanged candidate with
fresh owned disk/TPM/credentials. A read-only extra unit runs echo/getenforce/ls
before the unchanged pcrmachine service; it reports only root-directory metadata,
not files, credentials or user state. Runtime ordering/logging changes are
explicitly diagnostic-only. No debug shell, labels changed, enforcement relaxed,
failing service masked or account created manually. Same caps/deadline/reboot
marker/cleanup apply; label-diagnostic-* files preserve earlier evidence.
Launcher SHA-256:
`0f87d1d3d3af0bca7fec33b4d531962b61660c18cd2565a6bfb6604709d0f6fb`.
Both Python scripts passed syntax checks; active LSP found no errors but was
inconclusive. It reached its 120-second deadline rather than the intended exact
reboot marker: console/kmsg rate-limiting hid the plain marker, while formatted
reboot notices remained. Several disposable guest reboots occurred; cleanup
stopped VM/TPM and removed all secret-bearing state. Future label diagnostics
should stop on LABEL_DIAGNOSTIC_END, not rely on a rate-limited failure message.
The read-only unit printed Enforcing. ls returned ? for /, /etc, its policy link
and /lib* links; AVCs explicitly identify / and /etc as unlabeled_t. /var, /var/lib
and /var/log were correctly var_t/var_lib_t/var_log_t by observation time. Thus
not every mutable directory is broken. pcrmachine reports Failed to acquire
machine ID: No such file or directory, after PID 1's earlier creation denial.
Its stock domain AVCs show permissive=1 even though global getenforce is Enforcing;
no domain/permissive setting was changed by the test. This is not proof that all
service domains enforce, nor an account/SSH/container pass.

A minimal owned correction now stages /usr/share/factory/root in mkosi.finalize,
after mkosi 27.1's normal strict target relabel. The Python helper copies ONLY
validated existing stock reference labels into an empty root + /etc, four
usr-merge links and the policy symlink. It copies no machine ID, account, binary
policy, home or application state. Root and /etc modes are explicitly 0755;
label-write/verification failures abort and remove partial output. Public image
directory mode guards reject a repeated restricted checkout. The repart recipe
uses CopyFiles=/usr/share/factory/root:/ on FIRST filesystem creation, preserving
Btrfs, /var subvolume, TPM encryption and FactoryReset=no. Existing filesystems
are not a repair/reset target; policy still follows the selected signed /usr.

Upstream systemd 259 prefers mounted /sysusr/usr in the initrd and uses /sysusr
as the default CopyFiles source root; the original console confirms that mount
preceded repart. Its implementation requests COPY_ALL_XATTRS and copies source-root
attributes. No custom runtime launcher, early privileged login or new policy is
introduced. The strict-relabel order was checked in installed mkosi 27.1 source;
stock Fedora usr-merge link values were checked in a no-network utility container.
The new helper/config/tests are UNBUILT and UNBOOTED. Six synthetic staging tests
mock privileged label/ownership calls; the native generic ext4 fixture now checks
root/etc user-xattr and link preservation, plus byte-identical existing-FS retries.
It does NOT prove target security.selinux/Btrfs copying or enforcing boot. Active
LSP confirms all three changed Python files clean; bash syntax and git whitespace
checks passed. Full offline suite task `b5384b65d` FAILED: 137 tests ran with one
error in the old SSH factory-merge fixture, which lacked SRCDIR and a privileged
labeling-capable buildroot. All six new staging tests and native metadata-copy
checks passed. The existing factory-merge test now supplies a clearly synthetic
helper stub and verifies the exact hook arguments; production has no skip-labels
switch. Actual privileged staging behavior remains covered separately by the
mocked helper tests and pending enforcing builder/target validation.
The changed legacy test's four pre-existing Pyright findings (old module-loader,
fake stdin, optional test password and fake failure attribute) were explicitly
deferred rather than silently suppressed or claimed clean. The adapted full
suite rerun `bcb86e5d8` COMPLETED: all 137 tests passed. Await the later cleanup
verification task below before freezing the expanded patch
(including new files and test_account.py), and correct scoped checkout/input modes
in a fresh builder harness before any deliberate next build. At that test stage,
no new cold build had been launched.

Before freezing inputs, the four legacy typing blockers were then fixed explicitly:
optional module-spec guard, typed optional synthetic stdin/failure/password fields,
and a non-None assertion for the generated password. Imports/nested test contexts
were cleaned up. A SourceOnlyLoader now uses importlib execution from trusted
repository bytes without reading or writing ExtraTrees bytecode; no raw exec is
needed. Production account logic is unchanged. Active LSP across all four changed
Python files reports no primary findings. Two auxiliary findings were reviewed as
false positives: 0755 is necessary for empty root/etc directory traversal (not
secret file permissions), and passt is an exact Fedora package name. These are
explicit session dispositions, not silent clean claims. Latest full test task
`b4868091a` COMPLETED: all 137 tests passed in 2.041 seconds. The earlier
fixture-only rerun `bcb86e5d8` also passed all 137, but does not replace this latest
input verification.

One deliberate fresh build `b951e85e6` FAILED; no automatic cold retry was launched.
Private scratch: /home/backup-admin/.cache/personal-os-validation/root-labels-CAGGSvG7.
Image version: 20261005041322. HEAD and dotfiles pin remain unchanged. The frozen
eight-file source/test patch (including the two new untracked files) SHA-256 is
`66abef60726a0d0b3f6f6a5f98be3b2ef032bc7bef806fcacd83e0457719e606`.
Builder script SHA-256:
`6f0c26d388b32e54f631ebccd7157b582044ef8081889676416329411dee10f9`.
Its checkout AND patch application run under a subshell umask 022 within the
private 0700 disposable builder home. All public OS extra-tree directories and
files are checked against 0755/0644 inputs before compilation. Outside that
subshell remains 077; keys/credentials remain private. A host-side private bundle
replay proved clean patch application and those mode assertions, then was removed.
Shell, embedded Python and copied harness syntax checks passed; the loopback
builder port was free. Both retained raw candidates' original hashes were
rechecked unchanged. Preflight found about 9.7 GiB available RAM and 203.5 GiB
scratch space. Stock enforcing policy checks, package/image signature checks,
6-GiB/4-vCPU VM, 3-CPU/5-GiB/one-hour build cap, no guest swap and two Cargo jobs
remain unchanged. The reused public cloud image/mkosi archive are reverified;
no disposable signing key, SSH identity, seed or VM state is reused. Owned
credential-bearing builder state is removed on exit. External drive, host
firmware, production identities/services and publishing remain excluded.
Result: source compilation, postinstall and strict targeted-policy relabeling
passed, but finalize aborted before template staging with
`ValueError: Public image directory is not readable/searchable: usr`.
The early public-input mode assertion passed. The guard did not print an exact
resulting mode, so do not claim a measured 0700 for this attempt. Bootloader
signing occurred earlier, but no finished image/UKI signature pass or artifact
export occurred. Cleanup reported the owned builder stopped and disposable
keys/disk/seed removed. Only builder-console.log remains among the bounded
builder/seed/user-data filename check; no new target boot was attempted.

The frozen harness still invoked mkosi under inherited 077. Installed mkosi 27.1
`install_extra_trees()` uses `install_tree(..., preserve=False)`, whose copy path
preserves existing target-directory stat via `preserve_target_directories_stat()`.
Thus public 0755 checkout dirs do not repair already restrictive image dirs.
A least-privilege native synthetic fixture used the exact installed
`mkosi.tree.copy_tree(..., preserve=False)` after making target dirs under 077 or
022. With identical 0755/0644 public input, it retained /usr and /usr/lib as 0700
in the 077 case and 0755 in the 022 case; the public file was 0644 in both.
Evidence: `native-merge-mode-results.json` in this scratch; fixture removed.
This is not a package-install/full-build/boot proof, and does not pinpoint the
first restrictive mkdir in the failed guest. Next harness correction must scope
mkosi image construction itself to 022, keeping private key/credential/workspace/
cache parents 0700 and secret files 0600, asserting those protections and leaving
the image guard intact. Do not blanket chmod the image or relax SELinux.
At that failure stage no next build had been launched. The owner then reviewed
the architecture and explicitly approved one narrow validation cycle: correct
the harness, freeze/preflight, build once, then normal boot/enrollment/SSH and
reboot/TPM unlock only if the build passes. On any new failure stop and bring back
evidence before another attempt; freeze feature work and do not accumulate
workarounds. This is not production installation approval.

Fresh task `b10858735` COMPLETED (exit 0) in private scratch
`/home/backup-admin/.cache/personal-os-validation/build-modes-n308vl_o`.
Image version: `20261005045439`. Source HEAD, dotfiles pin and the eight-file
`66abef60726a0d0b3f6f6a5f98be3b2ef032bc7bef806fcacd83e0457719e606` patch are
byte-identical to the latest 137-test inputs; no payload/source change was made.
Fresh builder script SHA-256:
`bdfb90328adf286d5a09689700b6f3f0d70bbab9535b2974513ed247da858a3f`.
It creates private artifact/workspace/cache parents under 077 before scoped
image assembly under 022. The actual root build launcher checks inherited 022
and private parent/key modes before importing mkosi; post-assembly checks repeat
private modes. These checks do not print secret values or alter image modes.
All original stock-policy/signature/relabel and public-image guards remain.

Native preflight executed only the launcher's stdlib policy checks with
synthetic private paths in a transient USER scope, never mkosi build. Correct
022/0700/0600 passed; wrong 077, exposed 0644 synthetic key, and 0755 private
parent were each rejected; restored protections passed and the fixture was
removed. This is not a root build proof: the real guest launcher must still pass.
Embedded Python, Bash and copied harness syntax passed. Active LSP found no
remaining errors in the two private changed Python scripts but is inconclusive
(push-only) rather than confirmed clean. Evidence/hash manifest are
`harness-preflight-results.json` and `validation-input.json` in this scratch.
Initial preflight blocked on RAM without generating keys/seed or launching a VM.
A subsequent verification of corrected preflight result recording/type guard
passed at 7.0 GiB available RAM and 195.2 GiB free scratch, with loopback port free.
The launch wrapper rechecks those gates, hashes and synthetic checks before
preparation. No resource polling/automatic wait job was started.

Because desktop headroom is lower, guest RAM is 5 GiB (four vCPUs), host scope
MemoryMax=6G/CPUQuota=350%, build scope MemoryMax=4G/CPUQuota=300%/one hour,
no swap and two Cargo jobs. Minimum launch headroom is 6.5 GiB available RAM.
Do not further shrink limits or stop another agent's/desktop's work to force a
launch. Background activation is Fish; the command explicitly invokes Bash on
`launch-build.sh`, not an implicitly POSIX compound command. Public input is
reverified; keys/seed/VM identities are newly generated and cleaned up by the
owned runner. Preserve the old failed harness and both retained candidates.
Terminal result: actual guest image-process 022 and private modes passed, strict
relabel passed, real helper printed stock-labeled metadata-only staging success,
private modes passed again afterward, and sbverify reported Signature verification
OK. Host export hashes match builder values. Manifest: 339 runtime RPMs, no
Rust/Cargo/GCC. Cleanup stopped the owned VM and removed keys/disk/seed; the
bounded disposable-state filename check found nothing remaining.
Raw: 2,247,892,992 bytes, SHA-256
`385d5b42dd49bf7ba938cb183f960728214b8c6d4041271b0bbc0b1e337e5ed0`.
UKI: 64,262,616 bytes, SHA-256
`7da59bfa581a5da309f7206cc619ebf28e3207e630e57cff77f337f4d4eb7d31`.
Manifest SHA-256:
`fc31e00bb3d6374d8cbf9dc4af67eb9253a6cf3cfef6fadecab69bee8cd468a0`.
Receipt: `build-receipt.json`; artifact hashes: `artifact-sha256.txt` in this
scratch. No finished signed-payload inode inspection or target boot has run yet.

During the build the owner questioned cold rebuild cost, Arch as a base, SELinux
maintenance and alternative agent privileges. No architectural change was
implemented: full cold rebuilds are the current harness choice, not intrinsically
required by Fedora; unrestricted sudo is not an agent isolation boundary;
root inside the existing rootless sandbox is distinct from host root. Keep the
current enforcing recipe intact. Further boot work is paused while the security
model/distro choice is settled; do not automatically launch a target or disable
SELinux. If continuing this candidate is agreed, next verify actual signed
skeleton attrs/public directory modes and then normal target startup using fresh
matching certificate/firmware/TPM/state. A build remains no account/rootless/
recovery readiness pass.

**Owner's clarified design brief:** this is a homelab for experiments, not a
production server, but it may need to be RELIED UPON. Primary values are
SIMPLICITY, FLEXIBILITY and RESILIENCY, with minimal base size, fast builds and
familiar administration. Arch interest is principally size/familiarity; do not
reduce it to a build-speed objection. Owner did not request SELinux as mandatory.
Treat extra hardening as an explicit trade-off, not a presumed prerequisite.
Reliability should mean stable host access, contained/disposable experiments,
controlled changes and tested rollback/state restoration without babysitting.
Do not equate a separate unrestricted-sudo username with isolation, or rootless
containers with protection for all user data if whole-home/credentials are
mounted. Existing operator-access decisions have not been changed; agent privilege
boundaries remain a design question. No Arch profile, enforcement change or new
build/boot is authorized by this values clarification alone. Keep retained Fedora
evidence intact; agree the revised architecture before implementing it.

**Subsequent owner go-ahead:** after confirming the changed recommendation toward
Arch/non-mandatory SELinux, the owner said "okay now you can go". Local prototype
implementation and isolated validation are authorized; production permissions
remain unchanged. No inherited signing, TPM/Btrfs or recovery requirement was
implicitly removed, and no dedicated agent user or sandbox launcher was added.

Implemented explicit owned `mkosi.profiles/mini-server-arch` and
`scripts/mkosi-arch`. Plain mkosi still selects the retained Fedora recipe; its
profile selection now resides in the early Fedora-matched fragment, preventing
both profiles from being merged under the explicit Arch CLI. Actual JSON summaries
show only mini-server-arch, Arch rolling target/initrd/tools, misc/runtime tools,
66 unique direct packages, package signature checks and incremental builds on,
separate root-level mkosi.cache/arch and mkosi.output/arch. No OBS, desktop/AUR,
compiler build packages or npm/Cargo build script are selected. Repository
Starship replaces source compilation for this variant. Node/agent releases,
shpool payload and server workload packages are deferred composition work, not
abandoned requirements. Shared overlay/configuration gates and committed dotfiles
staging are reused; the prototype is not feature-complete or size-measured.

Arch's sole finalize script reuses stage-root-bootstrap.py with explicit
--distribution=arch. This mode requires a regular in-image Arch os-release,
rejects any SELinux policy path and copies only empty root/etc and usr-merge
links with normal modes/root ownership—no MAC calls, policy, machine ID/accounts
or mutable state. Fedora's default path still requires stock labels and aborts
on label errors; Arch mode cannot bypass a Fedora identity. New synthetic tests
cover identity, unexpected policy, external release symlink, mode/ownership
failure and cleanup. Shared branding handles Arch's absent VERSION/VERSION_ID,
preserves ID=arch and particleos-arch immutable ancestry, and does not invent a
numeric release. Fedora identity output remains under regression test.

Arch prototype presets keep enrollment/configuration/shpool disabled until native
account helpers are adapted: existing restorecon calls and distro/NSS/PAM policy
must be reviewed, not bypassed with manually created users. Existing operator
sudo policy has not changed, and agent host privilege remains a design boundary.
SIMPLE does not mean mounting all home/credentials into an unrestricted sandbox.

Full offline regression task `be6892b2f` is running with new Arch guards and retained
Fedora tests. Bash syntax, actual Arch JSON inspection and git diff --check passed.
Active LSP has no primary findings in the five changed Python files. Auxiliary
0755-empty-OS-directory and exact passt-package findings have explicit false-
positive dispositions. Official package pages confirm repository Starship,
chezmoi and Podman/rootless pieces (URLs below); this is not full signature-
verified package closure. No builder, signing-key generation, target account,
chezmoi apply, VM boot or production mutation occurred in this Arch step.

Read-only upstream inspection while that regression runs found a required
follow-up before any build: stock Arch filesystem uses /sbin -> usr/bin and
/lib64 -> usr/lib (Fedora uses usr/sbin and usr/lib64), and does not guarantee
/usr/libexec. The initial synthetic Arch fixture still models Fedora usr-merge
paths. After the current test terminal result, use a separate Arch link/public-
directory map and stock-layout fixture; keep Fedora's mapping/guards unchanged.
Do not freeze/build the current prototype until this real-source gap is fixed.
Reference: https://gitlab.archlinux.org/archlinux/packaging/packages/filesystem/-/raw/main/PKGBUILD
(read-only, no PKGBUILD executed).

Next: inspect that regression terminal result, fix any real source issue without
changing tested payload mid-run, adapt/test Arch native enrollment, then select
and record a reviewed Arch repository/tools snapshot before a bounded build.
Rolling package version drift means Git pins alone are not release reproducibility.
Cached builds are permitted by the new profile, but only reverified public/package/
compiler artifacts may be reused—not keys, identities, runtime secrets or unsafe
source histories. Installation still needs normal boot, access, reboot/unlock,
rollback/rescue and independent mutable-state recovery passes.
Arch sources: https://archlinux.org/packages/extra/x86_64/starship/,
https://archlinux.org/packages/extra/x86_64/chezmoi/,
https://archlinux.org/packages/extra/x86_64/podman/,
https://wiki.archlinux.org/title/Podman.

Source references: https://github.com/systemd/systemd/blob/v259/src/repart/repart.c
and https://github.com/systemd/systemd/blob/v259/units/systemd-repart.service.
Credential/drop-in reference:
https://github.com/systemd/systemd/blob/v259/man/systemd-debug-generator.xml.
References: https://github.com/systemd/systemd/blob/v259/src/core/selinux-setup.c
and https://github.com/systemd/systemd/blob/v259/man/repart.d.xml.
Private `run-target.py` SHA-256
`68cb6bb03c461935b528a5afcd86d5720d062ff8abf2be1f8cfad4638f76717b`.
Its first test copies the hash-checked candidate, grows only that sparse file to
30 GiB, uses 4 GiB/2 CPUs with a 5-GiB host memory cap, and forwards SSH only on
loopback port 22265. SMBIOS credential payloads come from protected files, never
argv values. Host and embedded guest code passed syntax checks; an active LSP
probe had no remaining errors but could not confirm clean on its push-only server.
Cleanup stops the owned VM/TPM before removing its disk, firmware and credentials.

**First-boot evidence limits:** successful encrypted-root creation/mounting does
not prove subsequent TPM unlock. Podman info/user-namespace probes over SSH do
not prove container networking, SELinux mounts, shpool operation, logout/linger
persistence, update/rollback or recovery. Console password authentication remains
a separate test. Preserve disabled automatic configuration and workload gates;
do not replace failed native enrollment with a manually created user.

**For readers:** the builder and the built OS have distinct SELinux policies.
Setfiles calculates labels from the target policy, but writes labels through the
builder's running kernel. A target-only type can therefore fail with `Invalid
argument` even when the target package supplied its correct policy. Matching stock
policy modules in the builder is the intended prerequisite; turning enforcement
off or suppressing relabel failures would hide the issue rather than validate it.
The one-file probe proves only that label boundary. A complete build plus UKI
signature check still does not prove firmware Secure Boot, TPM unlock, account
creation, console/SSH access, rootless containers or update/rollback. Those require
fresh target boots after an actual candidate is retained. Track each result at its
real layer; keep automatic configuration disabled and never bypass readiness.
