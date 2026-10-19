---
id: 01a15273-e4ee-79d3-8c4b-5a34bb365308
alias: services
parent: personal-os
state: New
---
# Services machine

The N150: what Darrion and others rely on, with operational data and deliberate access policy, kept apart from the
disposable dev pod (meta-analysis DECISIONS.md). Its image starts from the Arch services recipe
(`scripts/mkosi-arch` default, `mkosi.conf.d/arch`).

## Carried from mini-server

The mini-server charter (closed 2026-10-19, after the 2026-10-11 devbox install wiped mini-travel-server) settled
these with Darrion; the records are archived in `.clearhead/archive/01a0fb15-b777-75a3-a048-7e0da5722a02.*`:

- **Services** (=mini-server-service-decisions): SSH, Tailscale, Syncthing, Radicale, the OpenTelemetry Collector,
  vdirsyncer and a private Neovim server; restic replaces rclone.
- **Access** (=mini-server-identity-decisions): `dab` UID/GID 1000 in wheel, the desktop key, key-only SSH,
  passwordless sudo scoped to `dab`, a typable console passphrase kept in 1Password.
- **Storage** (#01a0fb16-9546-742f-905b-71bb131e3044): the two 4 TB WD USB disks as mdadm RAID1 on GPT partitions,
  ext4 at `/srv/storage`, optional at boot, with workloads and backups refusing to run when it is absent. SMART
  reports were clean; extended tests were skipped by choice.
- **Backups** (=mini-server-backup-destination): restic to the USB mirror and to Backblaze B2, with credentials and
  repository-password copies in 1Password.
- Disk writes need Darrion's explicit approval.

## Decided here

- 2026-10-19, Darrion: the agent telemetry hub runs here (chezmoi's agent-logs charter owns the pipeline).

## Log
