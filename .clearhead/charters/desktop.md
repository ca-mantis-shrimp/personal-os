---
id: 01a15bc6-1057-7252-84ec-d5f8926296f1
alias: desktop
parent: personal-os
state: Active
---
# Desktop

Darrion's daily machines on personal-os: first the desktop (i7-12700K, Intel UHD 770 and RTX 3060 Ti), then the same
image booted from a USB-C NVMe so the whole machine travels. The Arch desktop today is configured by hand; sorting
what it has is how we learn what the image needs.

## Decided

- 2026-10-20, Darrion: git and the cloud are the integration point between machines, not a portable user. homed
  accounts weren't as portable as hoped ("if im going to do this might as well make it a whole damn bootable
  operating system"). Each piece that travels has one owner: the image (OS), chezmoi (config), git (work),
  1Password (keys and secrets), Syncthing and the vault (bulk data).
- 2026-10-20, Darrion: fewer tools are better unless that costs understandability.

## Proposed, to confirm

Layers, one tool each (facilitator, 2026-10-20; Darrion: "for the most part they look right"):

| Layer | Tool |
|---|---|
| Base image and hardware (Intel, NVIDIA) | mkosi profile |
| Optional /usr: add-ons (Steam, wine) and toolchains | mkosi-built sysext |
| GUI apps | Flatpak |
| Pinned user binaries, npm | chezmoi into `~/.local` |
| Services | systemd units; portable services for daemons |
| Mounts | mount units (`/home` and `/data` are separate disks) |

No distrobox, podman or docker. The desktop's two docker containers had both exited weeks ago, podman had none,
and nothing used quadlets (2026-10-20). Two accounts sharing one Steam library broke games, because Proton's
prefixes are owned by one user and Wine refuses a prefix owned by another.

## Measured (2026-10-20)

- Packages: 412 explicit repo and 98 foreign. chezmoi's packages.yaml lists 318 and 33; every listed repo package
  is installed, and 98 repo plus 66 foreign ones are unlisted (about 20 are paru -debug builds).
- Disks: nvme2n1 holds `/`, `/boot` and swap; nvme0n1 is `/home`; nvme1n1 is `/data` (group `data`, setgid, default
  ACLs); the 1 TB USB NVMe (sda) holds the homed `Darrion` home (28 GB used, last changed 2026-08-09).
- Flatpaks: Logseq, Obsidian, Bottles.
