# Desktop sort (draft, 2026-10-21)

The working sheet for =desktop-sort in the desktop charter: everything installed by hand on the Arch desktop, sorted
into the charter's layers or dropped. The desktop profile replaces it, so delete this folder once the profile lands.

- `installed.tsv`: the 462 explicitly installed packages, collected over ssh by `collect.sh` on 2026-10-21.
- `rules.py`: one rule per group, mapping it to a layer, and the first rule that matches wins. A note starting
  with `?` is a call for Darrion.
- `sort.tsv`: the result (`python3 rules.py installed.tsv chezmoi-listed.txt > sort.tsv`). `vd sort.tsv` to browse.

To change a call, edit its rule and regenerate `sort.tsv`; don't hand-edit `sort.tsv`.

## Counts

| Layer | Packages | From AUR |
|---|---|---|
| base | 144 | 17 |
| hardware (intel 6, nvidia 3, desktop devices 5) | 14 | 5 |
| add-on: dev | 56 | 4 |
| add-on: kde | 69 | 1 |
| add-on: image-builder | 15 | 0 |
| add-on: gaming | 7 | 0 |
| flatpak | 28 | 9 |
| chezmoi | 7 | 2 |
| services (here 11, services machine 6) | 17 | 5 |
| drop | 105 | 7 |

Base is larger than it will end up, because the pruning calls below haven't been made yet.

## Calls that shape the profile

1. **Toolchains** (56): one dev add-on, or in base because this is the dev machine?
2. **Image building** (15: mkosi, ukify, sbctl, OVMF, swtpm and so on): stays on the desktop, or moves to devbox
   (=carry mkosi in the dev-pod image)?
3. **Gaming** (7): a sysext, whose 32-bit libraries must match the NVIDIA driver in base, or Flatpak Steam?
4. **KDE Plasma** (69): keep the backup desktop as an add-on, or drop it?
5. **GNOME, sway, nwg-shell**: the proposal drops them, since Hyprland is primary and KDE is already the backup.
6. **Services machine**: radicale, copyparty, netdata, samba and vsftpd move to the N150 (services charter). Does
   syncthing also stay here as a client?

## Pruning calls ("still used?" or "pick one")

- Launchers wofi or walker (walker plus elephant is 7 AUR packages); bars waybar or ashell; the nwg dock.
- Shells zsh and nushell beside fish; terminals kitty and ghostty.
- mercurial, glab; tcl/tk, vala, clisp, ruby.
- pavucontrol or pwvucontrol; blueman beside bluetui.
- Printing and scanning stack, Brother scanner drivers, Wacom tablet, DisplayLink dock.
- Nine browsers. qutebrowser has chezmoi-managed config and may stay a system package.
- mpd or mopidy; two speech-to-text tools (hyprwhspr, vocalinux).
- Four GUI archivers (the proposal drops all four; thunar-archive-plugin needs one); three more text browsers
  beyond lynx; about 60 Nerd Fonts (keep the ones the terminals use); three systemd GUIs/TUIs.

## Costs to know

- **AUR in the image:** mkosi installs only from repositories, so every AUR package kept in base, hardware or an
  add-on, or behind a service, needs a build step. Today that is 32 packages: 17 in base (7 of them walker and
  elephant), 5 hardware, 5 add-ons and 5 services. Flatpak covers 9 more.
- **Duplicates:** tree-sitter-cli, markdownlint-cli2 and the JSON language server come both from pacman and from
  chezmoi; vdirsyncer comes from pacman and from uv.
- **Out-of-tree modules:** evdi (DisplayLink) and v4l2loopback are built into the image instead of by dkms.

## User level (not pacman)

- **Flatpak:** Logseq, Obsidian, Bottles stay.
- **cargo:** clearhead, clearhead-graphd and clearhead-lsp go into the image (=image-clearhead). bob is dropped,
  since nvim comes from the image. cargo-binstall, cargo-insta, cargo-install-update, cargo-watch, agent-workspace,
  gen_man and nvim-mcp go with the dev call.
- **uv tools:** vdirsyncer (duplicate), vectorcode, hns, pywhispercpp.
- **/opt:** containerd (left by docker) goes; brother goes with the printing call; cuda is hardware: nvidia.
- **~/.local/bin beyond chezmoi:** claude, gemini, robot, hns, the pwcpp tools, vectorcode.
