"""Sort the desktop's explicit packages into personal-os layers.

Each rule is (group, layer, names-or-regexes, note). The first matching rule wins.
A note starting with '?' marks a call for Darrion.
"""
import re, sys, csv

Q = '?'
RULES = [
  # --- leaving the AUR (Darrion, 2026-10-21: security) ---
  ('AUR: vendor build', 'base', ['1password'], 'not from AUR: 1Password\'s own signed tarball, checked like op (chezmoi external)'),
  ('AUR: own package', 'base', ['agent-sandbox-system'], 'built from Darrion\'s agent-sandbox repo, not third-party'),
  ('AUR: covered', 'drop', ['1password-cli', 'nvimpager', 'tree-sitter-html', 'libgnome-keyring', 'kgamma', 'nerdfetch', 'sysd-manager', 'hyprwhspr'],
     'covered: op is a chezmoi external; MANPAGER="nvim +Man!"; nvim-treesitter builds parsers; deprecated; systemctl-tui; Hyprland is gone'),
  ('AUR: to chezmoi', 'chezmoi', ['buku', 'js-beautify', 'topiary', 'python-pywhispercpp-cuda'],
     'PyPI (uv), npm, a release binary; pywhispercpp is already a uv tool'),
  ('speech to text', 'drop', ['vocalinux', 'python-pywhispercpp-cuda', 'python-webrtcvad', 'ydotool'], 'none for now (Darrion, 2026-10-21); ydotool only typed the dictation'),
  ('AUR: open', 'drop', ['luajit-tiktoken-bin', 'mopidy-iris', 'mopidy-mpd'],
     '? AUR-only: tiktoken for nvim AI token counts, mopidy plugins (PyPI if mopidy stays)'),
  ('DisplayLink and Wacom', 'drop', ['evdi-dkms', 'wacomtablet'], 'DisplayLink never worked; the Wacom GUI is not needed (Darrion, 2026-10-21)'),
  ('AUR: scanner', 'hardware: desktop', ['brscan5', 'libsane-dsseries'], '? AUR-only Brother scanner drivers; goes with the printing call'),
  # --- drop: duplicates, X11 leftovers, tools the image makes moot ---
  ('debug builds', 'drop', [r'.*-debug$'], 'paru built these by default'),
  ('containers', 'drop', ['docker', 'docker-compose', 'podman', 'fuse-overlayfs'], 'nothing uses containers (charter, 2026-10-20)'),
  ('AUR helpers', 'drop', ['paru', 'yay'], 'an image has no pacman at run time; AUR packages need an image build step instead'),
  ('package tooling', 'drop', ['apt', 'pkgfile', 'pkgstats', 'arch-install-scripts', 'appimagelauncher', 'distribution-gpg-keys'], 'pacman-era or foreign-distro tools'),
  ('kernel module building', 'drop', ['dkms', 'linux-headers'], 'out-of-tree modules are built into the image, not on the machine'),
  ('X11 leftovers', 'drop', ['dmenu', 'xclip', 'xsel', 'kwin-x11', 'kwayland5', 'python-pyqt5'], 'Wayland only; wl-clipboard covers the clipboard'),
  ('superseded', 'drop', ['youtube-dl', 'ntp', 'vim', 'most', 'cvs', 'wpa_supplicant_gui', 'iwqt', 'profile-sync-daemon', 'typobuster', 'catfish', 'libotr'],
     'covered by something kept: yt-dlp, timesyncd, neovim, nvimpager, iwd+impala'),
  ('archivers', 'drop', ['engrampa', 'file-roller', 'xarchiver'], 'KDE has Ark'),
  ('text browsers', 'drop', ['elinks', 'chawan', 'browsh'], '? lynx stays (on the phone too); three more text browsers'),

  # --- hardware ---
  ('Intel CPU and iGPU', 'hardware: intel', ['intel-ucode', 'intel-media-driver', 'libva-intel-driver', 'vulkan-intel', 'turbostat', 'cpupower'], ''),
  ('NVIDIA GPU', 'hardware: nvidia', ['nvidia-open', 'cuda'], '? cuda is large and was for local speech and LLMs; ollama here is the CPU build, so is it still needed?'),
  ('displays and devices', 'hardware: desktop', ['displaylink', 'evdi-dkms', 'v4l2loopback-dkms', 'wacomtablet', 'brscan5', 'libsane-dsseries'],
     'DisplayLink and v4l2loopback are out-of-tree modules: built into the image'),

  # --- base: what every boot needs ---
  ('Arch base', 'base', ['base', 'sudo', 'linux', 'linux-firmware', 'man-db', 'man-pages', 'logrotate', 'zram-generator'], 'mostly the personal-os base already'),
  ('shell and terminal', 'base', ['fish', 'tmux', 'starship', 'fzf', 'zoxide', 'fd', 'ripgrep', 'yazi', 'lazygit', 'btop', 'htop', 'chafa', 'zsh', 'nushell', 'kitty', 'ghostty', 'rlwrap'],
     'kitty and ghostty both (Darrion, 2026-10-21); ? zsh and nushell beside fish'),
  ('editor', 'base', ['neovim', 'neovide', 'nvimpager', 'tree-sitter-cli', 'hunspell-en_us'], ''),
  ('version control', 'base', ['git', 'github-cli', 'glab', 'jujutsu', 'mercurial', 'chezmoi'], '? mercurial and glab: still used?'),
  ('networking', 'base', ['tailscale', 'iwd', 'impala', 'iw', 'openssh', 'rsync', 'wget', 'sshfs', 'mtr', 'tcpdump', 'iftop', 'speedtest-cli', 'cfssl'], ''),
  ('bluetooth', 'base', ['bluez', 'bluetui'], ''),
  ('replaced by KDE', 'drop', ['blueman', 'pavucontrol', 'pwvucontrol', 'nwg-look'], 'KDE has bluedevil, plasma-pa and its own GTK settings'),
  ('audio', 'base', ['gst-plugin-pipewire', 'gst-plugins-good', 'gst-plugins-bad', 'gst-libav'], ''),
  ('Wayland common', 'base', ['xdg-desktop-portal-gtk', 'wl-clipboard', 'qt5-wayland', 'qt6-wayland', 'layer-shell-qt', 'ydotool', 'sddm', 'vulkan-mesa-layers', 'vulkan-validation-layers'],
     'what KDE and GTK apps on Wayland need; sddm is the login screen'),
  ('Hyprland desktop', 'drop', ['hyprland', 'hypridle', 'hyprlock', 'hyprpaper', 'hyprlauncher', 'hyprpolkitagent', 'uwsm', 'xdg-desktop-portal-hyprland',
     'waybar', 'wofi', 'mako', 'nwg-dock-hyprland', 'dex', 'grimblast-git', 'shotman', 'walker', 'elephant', r'elephant-.*', 'ashell', 'wtype', 'wayvnc'],
     'KDE is the desktop (Darrion, 2026-10-21); wtype and wayvnc only work on wlroots compositors'),
  ('files', 'base', ['ark', '7zip', 'unrar', 'unzip'], ''),
  ('Thunar', 'drop', ['thunar', 'thunar-archive-plugin', 'thunar-media-tags-plugin', 'thunar-volman', 'tumbler', 'nautilus-python'],
     'no graphical file manager (Darrion, 2026-10-21); yazi covers files'),
  ('secrets', 'base', ['1password', '1password-cli', 'pass', 'qtpass', 'libgnome-keyring'], '1Password as a system package for browser and polkit integration; AUR, so it needs an image build step'),
  ('printing and scanning', 'base', ['cups-browsed', 'foomatic-db', 'foomatic-db-engine', 'foomatic-db-nonfree', 'foomatic-db-nonfree-ppds', 'foomatic-db-ppds',
     'foomatic-db-gutenprint-ppds', 'gutenprint', 'ipp-usb', 'print-manager', 'sane', 'sane-airscan', 'skanlite'], '? a full printing stack; is there a printer or scanner in use?'),
  ('fonts', 'base', ['noto-fonts', 'noto-fonts-cjk', 'noto-fonts-emoji', 'noto-fonts-extra', 'ttf-opensans', 'ttf-nerd-fonts-symbols', 'ttf-nerd-fonts-symbols-mono', 'adobe-source-code-pro-fonts'], ''),
  ('terminal fonts', 'base', ['ttf-hack-nerd', 'ttf-d2coding-nerd'], 'Hack (Darrion, 2026-10-21); kitty.conf names D2CodingLigature, so it stays until kitty switches'),
  ('nerd font collection', 'drop', [r'(ttf|otf)-.*-nerd'], 'only the fonts the configs name (Darrion, 2026-10-21)'),
  ('system tools', 'base', ['gptfdisk', 'nvme-cli', 'fwupd', 'lynx', 'rclone', 'power-profiles-daemon', 'geoclue', 'systemctl-tui', 'sysd-manager', 'systemd-ui', 'zk', 'calcurse', 'newsboat', 'visidata', 'buku', 'nerdfetch', 'resvg', 'pdfjs-legacy'],
     '? three systemd GUIs/TUIs'),

  # --- add-ons (sysext): optional /usr sets ---
  ('image building', 'base', ['mkosi', 'systemd-ukify', 'sbctl', 'sbsigntools', 'efitools', 'edk2-ovmf', 'edk2-shell', 'swtpm', 'erofs-utils', 'erofsfuse',
     'squashfs-tools', 'cpio', 'mtools', 'dosfstools', 'xfsprogs'], 'stays on the desktop (Darrion, 2026-10-21); devbox may build too, but the signing keys stay off it (dev pod: no durable secrets)'),
  ('gaming', 'flatpak', ['steam', 'lutris'], 'Flatpak first (Darrion, 2026-10-21); a sysext later only if performance or compatibility needs it'),
  ('Windows compatibility', 'drop', ['wine', 'winetricks', 'umu-launcher', 'lib32-vkd3d'], 'Steam ships Proton and Bottles (already a Flatpak) ships its own wine'),
  ('game tuning', 'base', ['gamemode'], '? unverified: whether Flatpak Steam uses the host gamemode; check once Steam runs'),
  ('toolchains', 'base', ['base-devel', 'rust', 'rust-analyzer', 'nodejs', 'npm', 'uv', 'cmake', 'meson', 'ninja', 'ccache'],
     'C, Rust, Node and Python in base (Darrion, 2026-10-21); npm too, since chezmoi installs the editor language servers with it'),
  ('other languages', 'base', ['go', 'ruby', 'ruby-docs', 'ruby-stdlib', 'fennel', 'fnlfmt', 'clisp', 'tcl', 'tk', 'vala',
     'lua51', 'luarocks', 'lua-sec', 'lua-language-server', 'stylua', 'clojure', 'leiningen', 'jre25-openjdk', 'python-ruff', 'ty', 'tombi', 'topiary',
     'mdbook', 'texinfo', 'texlive-bin', 'python-.*', 'pyside6', 'luajit-tiktoken-bin', 'tree-sitter-html', 'js-beautify', 'webkitgtk-6.0'],
     'in base on the desktop (Darrion, 2026-10-21)'),
  ('KDE Plasma', 'base', [r'plasma.*', r'k[a-z].*', 'breeze', 'breeze-gtk', 'breeze-plymouth', 'aurorae', 'bluedevil', 'drkonqi', 'discover', 'flatpak-kcm', 'milou',
     'oxygen', 'oxygen-sounds', 'ocean-sound-theme', 'qqc2-breeze-style', 'polkit-kde-agent', 'powerdevil', 'systemsettings', 'spectacle', 'libkscreen', 'libksysguard',
     'libplasma', 'sddm-kcm', 'plymouth-kcm', 'xdg-desktop-portal-kde', 'qt6-tools', 'libkeyfinder'], 'the desktop (Darrion, 2026-10-21)'),
  ('other desktops', 'drop', ['gnome-shell', 'sway', 'sway-contrib', 'nwg-shell'], 'KDE only (Darrion, 2026-10-21)'),

  # --- Flatpak: GUI apps ---
  ('chat', 'flatpak', ['discord', 'signal-desktop', 'telegram-desktop'], ''),
  ('mail', 'flatpak', ['thunderbird', 'external-editor-revived'], 'the editor add-on is a Thunderbird extension, installed inside Thunderbird'),
  ('office and media', 'flatpak', ['libreoffice-fresh', 'obs-studio', 'vlc', 'vlc-plugins-all', 'calibre', 'evince', 'filezilla', 'openaudible-bin', 'protege', 'rclone-ui-bin'], ''),
  ('browsers', 'flatpak', ['firefox', 'brave-bin'], 'Firefox and Brave (Darrion, 2026-10-21); both publish official Flathub builds'),
  ('vim browser', 'base', ['qutebrowser'], 'kept (Darrion, 2026-10-21); a system package because chezmoi manages its config'),
  ('other browsers', 'drop', ['firefoxpwa', 'chromium', 'vivaldi', 'vivaldi-ffmpeg-codecs', 'helium-browser-bin', 'nyxt'], 'three browsers are enough (Darrion, 2026-10-21)'),
  ('AI apps', 'flatpak', ['claude-desktop', 'antigravity', 'geekbench', 'parsec-bin'], 'AUR today; Flathub has some (Parsec); otherwise an image build step or drop'),

  # --- ~/.local via chezmoi: pinned user tools ---
  ('agent and LSP CLIs', 'chezmoi', ['gemini-cli', 'opencode', 'claude-agent-acp', 'nodejs-mcp-hub', 'markdownlint-cli2', 'vscode-json-languageserver', 'wrangler'],
     'markdownlint-cli2 and the JSON server are already in chezmoi\'s npm list; wrangler is per project (npx)'),

  # --- services ---
  ('services machine', 'services: N150', ['radicale', 'copyparty', 'netdata', 'samba', 'vsftpd'], 'the services profile (Darrion, 2026-10-21)'),
  ('desktop services', 'services', ['syncthing', 'mpd', 'mopidy', 'mympd', 'ollama', 'vdirsyncer', 'yt-dlp'],
     '? mpd and mopidy both. syncthing stays here as the vault share\'s client'),
]

def match(name):
    for group, layer, pats, note in RULES:
        for p in pats:
            if re.fullmatch(p, name):
                return group, layer, note
    return None

rows, missing = [], []
listed = set(open(sys.argv[2]).read().split())
for line in open(sys.argv[1]):
    name, src, size, date, desc = line.rstrip('\n').split('\t')
    m = match(name)
    if not m:
        missing.append(name); continue
    group, layer, note = m
    rows.append(dict(package=name, layer=layer, group=group, source='aur' if src == 'foreign' else 'repo',
                     in_packages_yaml='yes' if name in listed else 'no', size=size, call=note, description=desc))
if missing:
    print('UNCLASSIFIED:', ' '.join(missing), file=sys.stderr)
order = ['base', 'hardware: intel', 'hardware: nvidia', 'hardware: desktop',
         'flatpak', 'chezmoi', 'services', 'services: N150', 'drop']
rows.sort(key=lambda r: (order.index(r['layer']), r['group'], r['package']))
w = csv.DictWriter(sys.stdout, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n')
w.writeheader(); w.writerows(rows)
