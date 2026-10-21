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
| base (KDE 69, languages and toolchains 56, image building 15) | 252 | 12 |
| hardware (intel 6, nvidia 3, desktop devices 5) | 14 | 5 |
| flatpak (Steam and Lutris included) | 30 | 9 |
| chezmoi | 7 | 2 |
| services (here 12, services machine 5) | 17 | 5 |
| drop | 142 | 17 |

## Decided (Darrion, 2026-10-21)

- **KDE is the desktop**, in base. Hyprland, GNOME, sway and nwg-shell go, and with them walker, elephant, the bars and
  the launchers. KDE's own tools replace blueman, pavucontrol, the archivers and the screenshot helpers.
- **Languages and toolchains in base:** C (base-devel), Rust, Node with npm (chezmoi installs the editor's language
  servers with it), Python (uv), cmake, meson, ninja, and the other languages too (go, ruby, tcl/tk, vala, clisp,
  fennel, clojure, texlive). So the desktop has no add-ons for now: the sysext layer stays empty unless Steam needs it.
- **Image building stays on the desktop**, in base. Devbox may build too, "as long as we do it right": the signing
  keys stay off it, since the dev pod holds no durable secrets.
- **Steam from Flatpak first**, with Lutris; a sysext only if performance or compatibility needs it. wine,
  winetricks and umu-launcher go, since Proton and Bottles ship their own.
- **Services move to the services profile:** radicale, copyparty, netdata, samba, vsftpd. syncthing stays here as
  the vault share's client (treated as how).

## Still open

- **Files:** Thunar and its plugins, or Dolphin (KDE's, not installed yet)?
- zsh and nushell beside fish; kitty and ghostty both.
- mercurial, glab; three systemd GUIs/TUIs.
- Printing and scanning stack, Brother scanner drivers, Wacom tablet, DisplayLink dock: still used?
- Nine browsers. qutebrowser has chezmoi-managed config and may stay a system package.
- mpd or mopidy; two speech-to-text tools (hyprwhspr, vocalinux).
- About 60 Nerd Fonts (keep the ones the terminals use); three more text browsers beyond lynx.
- gamemode: unverified whether Flatpak Steam uses the host's; check once Steam runs.
- AUR-only leftovers: tiktoken for nvim AI token counts, vocalinux, the mopidy plugins.

## Costs to know

- **Leaving the AUR** (Darrion, 2026-10-21: security). Of 22 AUR packages that would have been built into the
  image, 2 remain without question: agent-sandbox-system (Darrion's own package) and 1Password, built from 1Password's
  own signed tarball and checked the way chezmoi checks op. 4 more are hardware that stays only if still used
  (DisplayLink, Brother scanner, Wacom GUI). The rest are dropped as covered or moved to chezmoi (buku via uv,
  js-beautify via npm, topiary as a release binary). Nine AUR apps go to Flatpak instead; whether each is on Flathub
  is unchecked (claude-desktop and antigravity are the doubtful ones).
- **Duplicates:** tree-sitter-cli, markdownlint-cli2 and the JSON language server come both from pacman and from
  chezmoi; vdirsyncer comes from pacman and from uv.
- **Out-of-tree modules:** evdi (DisplayLink) and v4l2loopback are built into the image instead of by dkms.
- **chezmoi:** the Hyprland, waybar, wofi, mako and sway configs it manages become unused on the desktop.

## User level (not pacman)

- **Flatpak:** Logseq, Obsidian, Bottles stay.
- **cargo:** clearhead, clearhead-graphd and clearhead-lsp go into the image (=image-clearhead). bob is dropped,
  since nvim comes from the image. cargo-binstall, cargo-insta, cargo-install-update, cargo-watch, agent-workspace,
  gen_man and nvim-mcp go to chezmoi (=locked-installers in chezmoi).
- **uv tools:** vdirsyncer (duplicate), vectorcode, hns, pywhispercpp.
- **/opt:** containerd (left by docker) goes; brother goes with the printing call; cuda is hardware: nvidia.
- **~/.local/bin beyond chezmoi:** claude, gemini, robot, hns, the pwcpp tools, vectorcode.
