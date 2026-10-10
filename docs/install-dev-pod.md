# Installing the dev pod on hardware

The dev pod's target is the NUC (meta-analysis DECISIONS, 2026-10-09). Every step below was rehearsed on
2026-10-09 in QEMU: the production-key image written raw onto a blank 64 GB NVMe, OVMF without and then with
Secure Boot, swtpm, and no SMBIOS credentials. Re-run after adding polkit and the encrypted `/home`: first boot,
the facilitator's user, `run0`, unattended reboot. What the rehearsal could not cover is marked **untested**.

No installer runs on the target: the built disk image is written to the NVMe as is, and its first boot creates
encrypted swap, root and `/home` (dev pod only; services keeps `/home` plain) with systemd-repart, sized to the disk. Upstream's live/installer UKI profiles
stay in `reference/` on purpose (fixed root password, autologin, unsigned PCR policy).

## On the desktop

Keys live outside Git in `~/.local/share/personal-os/keys` (0700): one pair, `mkosi.key`/`mkosi.crt`, signs
Secure Boot, verity and the PCR policy. Losing it means reinstalling and re-enrolling; updates need it.

```sh
k=~/.local/share/personal-os/keys
scripts/mkosi-arch dev-pod --secure-boot-key=$k/mkosi.key --secure-boot-certificate=$k/mkosi.crt \
  --verity-key=$k/mkosi.key --verity-certificate=$k/mkosi.crt \
  --sign-expected-pcr-key=$k/mkosi.key --sign-expected-pcr-certificate=$k/mkosi.crt --force build

# Secure Boot enrollment files: ours plus Microsoft's CAs (from github.com/microsoft/secureboot_objects).
scripts/secure-boot-auth $k ~/.local/share/personal-os/secureboot/microsoft ~/.local/share/personal-os/secureboot/auth

# Root's SSH key as a credential the boot stub hands to the OS. A null key is accepted only while
# Secure Boot is off, or on first boot; tmpfiles copies it to /root/.ssh/authorized_keys once.
systemd-creds encrypt --with-key=null --name=ssh.authorized_keys.root ~/.ssh/id_ed25519.pub ssh.authorized_keys.root.cred
```

## On the NUC

1. **Firmware:** Secure Boot off (the Arch ISO is not signed for it), boot from USB. Set a firmware admin password.
   If the firmware menu is hard to reach (the NUC, a GMKtec NucBox M6, reboots too fast and doesn't support
   `systemctl reboot --firmware-setup`), boot the stick once from the old system: `efibootmgr` lists a
   removable-device entry, then `efibootmgr --bootnext <num> && systemctl reboot`.
2. **Live system:** boot the Arch ISO stick, `passwd` for root, note `ip -br a`. Find the NVMe with
   `lsblk -o NAME,SIZE,MODEL,SERIAL` and check it's the one you mean: everything on it is destroyed.
3. **Write the image** from the desktop (`nuc` = the live system's address):
   ```sh
   ssh root@nuc 'blkdiscard -f /dev/nvme0n1'   # untested on the NUC; clears old partitions and LUKS headers
   ssh root@nuc 'dd of=/dev/nvme0n1 bs=4M conv=fsync status=progress' < mkosi.output/dev-pod/PersonalOS__x86-64.raw
   ssh root@nuc 'blockdev --rereadpt /dev/nvme0n1 && mount /dev/nvme0n1p1 /mnt && mkdir -p /mnt/loader/credentials /mnt/loader/keys/personal-os'
   scp ssh.authorized_keys.root.cred root@nuc:/mnt/loader/credentials/
   scp ~/.local/share/personal-os/secureboot/auth/*.auth root@nuc:/mnt/loader/keys/personal-os/
   # Boot the new disk first; drop entries for the old installation.
   ssh root@nuc 'efibootmgr --create --disk /dev/nvme0n1 --part 1 --loader "\\EFI\\BOOT\\BOOTX64.EFI" --label "Personal OS"'
   ssh root@nuc 'umount /mnt && systemctl poweroff'
   ```
4. **First boot:** remove the stick and boot. First boot builds the partitions and seals root and `/home` to the TPM.
   `ssh root@<address>` should work with the desktop key.
5. **Recovery keys:** the TPM is otherwise the only key slot, and an AMD firmware TPM can be reset by a BIOS
   update. Run this in a terminal of your own (not through an agent, whose output is logged) and store both keys
   in 1Password. Swap keeps only its TPM slot; it can be recreated.
   ```sh
   for v in root home; do echo "== $v"; systemd-cryptenroll --unlock-tpm2-device=auto --recovery-key /dev/disk/by-designator/$v-luks; done
   rm /boot/loader/credentials/ssh.authorized_keys.root.cred
   ```
6. **The facilitator's user:** Claude Code refuses its bypass-permissions mode as root, so the facilitator runs
   as `agent-facilitator` in `wheel`. Its password stays locked; the image's polkit rule lets `wheel` use `run0`
   without one. Add it to `agents` once agent-sandbox has created that group.
   ```sh
   useradd -m -U -G wheel -s /bin/bash agent-facilitator   # -U: the image has no login.defs
   install -d -m700 -o agent-facilitator -g agent-facilitator /home/agent-facilitator/.ssh
   install -m600 -o agent-facilitator -g agent-facilitator /root/.ssh/authorized_keys /home/agent-facilitator/.ssh/
   ```
7. **Secure Boot:** `systemctl reboot --firmware-setup`, clear or reset the Secure Boot keys so the firmware is in
   setup mode, enable Secure Boot. In the systemd-boot menu choose "Enroll Secure Boot keys: personal-os"; it
   enrolls and reboots. Then `bootctl status` shows `Secure Boot: enabled (user)` and
   `rm -r /boot/loader/keys/personal-os`. The firmware menu wording is **untested** (rehearsed on OVMF only).
   The root stays unlockable: its TPM token is bound to the signed PCR 11 policy only, not PCR 7.

## Moving in (interim, until the image carries it)

Done on the NUC 2026-10-10 as `agent-facilitator`; the first sandboxed Claude session finished there.
agent-sandbox's host integration and mkosi are not in the image yet, so they live in mutable `/etc` and `~/.local`:

1. `agent-sandbox/system/usr/lib/...` and `usr/share/polkit-1/rules.d/...` copied to the same paths under `/etc`,
   then `systemd-sysusers`, `systemd-tmpfiles --create`, `systemctl daemon-reload`, `usermod -aG agents agent-facilitator`,
   `loginctl enable-linger agent-facilitator`.
2. mkosi from git at the desktop's version (`git clone --branch v27.1 https://github.com/systemd/mkosi`), linked
   into `~/.local/bin`. Claude Code with `npm install -g --prefix ~/.local --allow-scripts=@anthropic-ai/claude-code`.
3. `~/.config/environment.d/50-agent-sandbox.conf`: `PATH`, `AGENT_BASE`, `AGENT_LAYERS`, `XDG_CACHE_HOME` (agent-layer's
   mkosi otherwise picks `/var/cache`) and `AGENT_REPART_DEFINITIONS` (mkosi isn't an installed module).
   `~/.bashrc` sources it; `~/.bash_profile` sources `~/.bashrc`.
4. Base: `scripts/mkosi-arch sandbox-worker build` in a personal-os clone (73 s). Harness layer: `agent-layer`.
5. Credentials, each by Darrion from their own terminal: the sandbox Claude token sealed with
   `run0 systemd-creds encrypt --name=agent.claude_token - /etc/credstore.encrypted/agent.claude_token` (TPM and
   host key, signed PCR 11 policy by default, so updates and Secure Boot keep it readable); `gh auth login
   --with-token` and `gh auth setup-git`; `claude` then `/login`. The pi login is still to do.

## Known gaps

- Done on the NUC 2026-10-10 through step 6. Secure Boot (step 7) waits: its firmware exposes no `SecureBoot` or
  `SetupMode` variables to the OS, so whether it can enroll custom keys is unknown until someone reaches the menu.
  The `.auth` files are staged on its ESP.
- First boot on the NUC showed no login prompt for minutes: Bluetooth firmware retries flooded the console. The
  image now blacklists btusb; the NUC has the same line in `/etc/modprobe.d/no-bluetooth.conf`.

- The hostname defaults to `archlinux`; set it with `hostnamectl hostname`.
- Updates (sysupdate into the spare A/B `/usr` slots) and rollback are not rehearsed yet.
