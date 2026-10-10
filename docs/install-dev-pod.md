# Installing the dev pod on hardware

The dev pod's target is the NUC (meta-analysis DECISIONS, 2026-10-09). Every step below was rehearsed on
2026-10-09 in QEMU: the production-key image written raw onto a blank 64 GB NVMe, OVMF without and then with
Secure Boot, swtpm, and no SMBIOS credentials. What the rehearsal could not cover is marked **untested**.

No installer runs on the target: the built disk image is written to the NVMe as is, and its first boot creates
swap, an encrypted root and `/home` with systemd-repart, sized to the disk. Upstream's live/installer UKI profiles
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
2. **Live system:** boot the Arch ISO stick, `passwd` for root, note `ip -br a`. Find the NVMe with
   `lsblk -o NAME,SIZE,MODEL,SERIAL` and check it's the one you mean: everything on it is destroyed.
3. **Write the image** from the desktop (`nuc` = the live system's address):
   ```sh
   ssh root@nuc 'blkdiscard -f /dev/nvme0n1'   # untested on the NUC; clears old partitions and LUKS headers
   ssh root@nuc 'dd of=/dev/nvme0n1 bs=4M conv=fsync status=progress' < mkosi.output/dev-pod/PersonalOS__x86-64.raw
   ssh root@nuc 'blockdev --rereadpt /dev/nvme0n1 && mount /dev/nvme0n1p1 /mnt && mkdir -p /mnt/loader/credentials /mnt/loader/keys/personal-os'
   scp ssh.authorized_keys.root.cred root@nuc:/mnt/loader/credentials/
   scp ~/.local/share/personal-os/secureboot/auth/*.auth root@nuc:/mnt/loader/keys/personal-os/
   ssh root@nuc 'umount /mnt && systemctl poweroff'
   ```
4. **First boot:** remove the stick and boot. First boot builds the partitions and seals the root to the TPM.
   `ssh root@<address>` should work with the desktop key.
5. **Recovery key:** the TPM is otherwise the only key slot. Store the printed key in 1Password.
   ```sh
   systemd-cryptenroll --unlock-tpm2-device=auto --recovery-key /dev/disk/by-designator/root-luks
   rm /boot/loader/credentials/ssh.authorized_keys.root.cred
   ```
6. **Secure Boot:** `systemctl reboot --firmware-setup`, clear or reset the Secure Boot keys so the firmware is in
   setup mode, enable Secure Boot. In the systemd-boot menu choose "Enroll Secure Boot keys: personal-os"; it
   enrolls and reboots. Then `bootctl status` shows `Secure Boot: enabled (user)` and
   `rm -r /boot/loader/keys/personal-os`. The firmware menu wording is **untested** (rehearsed on OVMF only).
   The root stays unlockable: its TPM token is bound to the signed PCR 11 policy only, not PCR 7.

## Known gaps

- `/home` is not encrypted (`mkosi.extra/usr/lib/repart.d/50-home.conf`). Root's home is on the encrypted root.
- The hostname defaults to `archlinux`; set it with `hostnamectl hostname`.
- Updates (sysupdate into the spare A/B `/usr` slots) and rollback are not rehearsed yet.
