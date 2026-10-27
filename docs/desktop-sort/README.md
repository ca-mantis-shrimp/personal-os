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
| base | 231 | 2 |
| hardware: intel | 6 | 0 |
| hardware: nvidia | 1 | 0 |
| hardware: desktop | 3 | 2 |
| flatpak | 23 | 8 |
| chezmoi | 11 | 6 |
| services | 4 | 0 |
| services: N150 | 7 | 0 |
| drop | 176 | 32 |

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
- **Pruning, second round:** DisplayLink (never worked) and the Wacom GUI go; no graphical file manager (Thunar and
  Dolphin go; yazi covers files); kitty and ghostty both stay; browsers are Firefox and Brave (Flatpak) and
  qutebrowser (a system package, for its chezmoi config); no speech to text; fonts are the ones the configs name,
  Hack and kitty's D2CodingLigature.
- **Third round:** printing and scanning are driverless (the Epson WF-7720 scans over eSCL and prints over AirPrint,
  and CUPS had no printers), so the driver databases go; cuda goes; nushell stays while Darrion experiments, zsh,
  mercurial, glab, systemd-ui, tiktoken and the extra text browsers go; mpd moves to the services machine and
  replaces mopidy.
- **Services move to the services profile:** radicale, copyparty, netdata, samba, vsftpd, mpd and mympd. syncthing stays here as
  the vault share's client (treated as how).

## Still open (both can wait for the profile)

- The Brother DS-620 didn't appear on USB at all (2026-10-21); it was the cable, and Darrion has it connected on the
  desktop (2026-10-27). Left: confirm it scans once the profile's driver, libsane-dsseries (built from Brother's own
  package), is in.
- gamemode: whether Flatpak Steam uses the host's; check once Steam runs.

## Costs to know

- **Leaving the AUR** (Darrion, 2026-10-21: security). Of 22 AUR packages that would have been built into the
  image, 2 remain without question: agent-sandbox-system (Darrion's own package) and 1Password, built from 1Password's
  own signed tarball and checked the way chezmoi checks op. The 2 Brother scanner drivers stay only if the scanner
  is still used. The rest are dropped as covered or moved to chezmoi (buku via uv,
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
