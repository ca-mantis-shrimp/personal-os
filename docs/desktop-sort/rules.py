"""Sort the desktop's explicit packages into personal-os layers.

Each rule is (group, layer, names-or-regexes, note). The first matching rule wins.
A note starting with '?' marks a call for Darrion.
"""
import re, sys, csv

Q = '?'
RULES = [
  # --- drop: duplicates, X11 leftovers, tools the image makes moot ---
  ('debug builds', 'drop', [r'.*-debug$'], 'paru built these by default'),
  ('containers', 'drop', ['docker', 'docker-compose', 'podman', 'fuse-overlayfs'], 'nothing uses containers (charter, 2026-10-20)'),
  ('AUR helpers', 'drop', ['paru', 'yay'], 'an image has no pacman at run time; AUR packages need an image build step instead'),
  ('package tooling', 'drop', ['apt', 'pkgfile', 'pkgstats', 'arch-install-scripts', 'appimagelauncher', 'distribution-gpg-keys'], 'pacman-era or foreign-distro tools'),
  ('kernel module building', 'drop', ['dkms', 'linux-headers'], 'out-of-tree modules are built into the image, not on the machine'),
  ('X11 leftovers', 'drop', ['dmenu', 'xclip', 'xsel', 'kwin-x11', 'kwayland5', 'python-pyqt5'], 'Wayland only; wl-clipboard covers the clipboard'),
  ('superseded', 'drop', ['youtube-dl', 'ntp', 'vim', 'most', 'cvs', 'wpa_supplicant_gui', 'iwqt', 'profile-sync-daemon', 'typobuster', 'catfish', 'libotr'],
     'covered by something kept: yt-dlp, timesyncd, neovim, nvimpager, iwd+impala'),
  ('archivers', 'drop', ['ark', 'engrampa', 'file-roller', 'xarchiver'], '? four GUI archivers; keep one (thunar-archive-plugin needs one) or none (7zip/unzip CLI)'),
  ('text browsers', 'drop', ['elinks', 'chawan', 'browsh'], '? lynx stays (on the phone too); three more text browsers'),

  # --- hardware ---
  ('Intel CPU and iGPU', 'hardware: intel', ['intel-ucode', 'intel-media-driver', 'libva-intel-driver', 'vulkan-intel', 'turbostat', 'cpupower'], ''),
  ('NVIDIA GPU', 'hardware: nvidia', ['nvidia-open', 'cuda', 'python-pywhispercpp-cuda'], 'cuda and whisper-cuda are large; only for local speech and LLMs'),
  ('displays and devices', 'hardware: desktop', ['displaylink', 'evdi-dkms', 'v4l2loopback-dkms', 'wacomtablet', 'brscan5', 'libsane-dsseries'],
     'DisplayLink and v4l2loopback are out-of-tree modules: built into the image'),

  # --- base: what every boot needs ---
  ('Arch base', 'base', ['base', 'sudo', 'linux', 'linux-firmware', 'man-db', 'man-pages', 'logrotate', 'zram-generator'], 'mostly the personal-os base already'),
  ('shell and terminal', 'base', ['fish', 'tmux', 'starship', 'fzf', 'zoxide', 'fd', 'ripgrep', 'yazi', 'lazygit', 'btop', 'htop', 'chafa', 'zsh', 'nushell', 'kitty', 'ghostty', 'rlwrap'],
     '? zsh and nushell beside fish; kitty and ghostty both'),
  ('editor', 'base', ['neovim', 'neovide', 'nvimpager', 'tree-sitter-cli', 'hunspell-en_us'], ''),
  ('version control', 'base', ['git', 'github-cli', 'glab', 'jujutsu', 'mercurial', 'chezmoi'], '? mercurial and glab: still used?'),
  ('networking', 'base', ['tailscale', 'iwd', 'impala', 'iw', 'openssh', 'rsync', 'wget', 'sshfs', 'mtr', 'tcpdump', 'iftop', 'speedtest-cli', 'cfssl'], ''),
  ('bluetooth', 'base', ['bluez', 'bluetui', 'blueman'], '? blueman beside bluetui (and bluedevil in KDE)'),
  ('audio', 'base', ['gst-plugin-pipewire', 'gst-plugins-good', 'gst-plugins-bad', 'gst-libav', 'pavucontrol', 'pwvucontrol'], '? pavucontrol and pwvucontrol both'),
  ('Hyprland desktop', 'base', ['hyprland', 'hypridle', 'hyprlock', 'hyprpaper', 'hyprlauncher', 'hyprpolkitagent', 'uwsm', 'xdg-desktop-portal-hyprland', 'xdg-desktop-portal-gtk',
     'waybar', 'wofi', 'mako', 'wl-clipboard', 'qt5-wayland', 'qt6-wayland', 'layer-shell-qt', 'nwg-look', 'nwg-dock-hyprland', 'dex', 'grimblast-git', 'shotman',
     'walker', 'elephant', r'elephant-.*', 'ashell', 'wtype', 'ydotool', 'wayvnc', 'sddm', 'vulkan-mesa-layers', 'vulkan-validation-layers'],
     '? two launchers (wofi, walker+elephant), two bars (waybar, ashell), a dock; sddm is the login screen'),
  ('files', 'base', ['thunar', 'thunar-archive-plugin', 'thunar-media-tags-plugin', 'thunar-volman', 'tumbler', 'nautilus-python', '7zip', 'unrar', 'unzip'], 'nautilus-python without nautilus does nothing'),
  ('secrets', 'base', ['1password', '1password-cli', 'pass', 'qtpass', 'libgnome-keyring'], '1Password as a system package for browser and polkit integration; AUR, so it needs an image build step'),
  ('printing and scanning', 'base', ['cups-browsed', 'foomatic-db', 'foomatic-db-engine', 'foomatic-db-nonfree', 'foomatic-db-nonfree-ppds', 'foomatic-db-ppds',
     'foomatic-db-gutenprint-ppds', 'gutenprint', 'ipp-usb', 'print-manager', 'sane', 'sane-airscan', 'skanlite'], '? a full printing stack; is there a printer or scanner in use?'),
  ('fonts', 'base', ['noto-fonts', 'noto-fonts-cjk', 'noto-fonts-emoji', 'noto-fonts-extra', 'ttf-opensans', 'ttf-nerd-fonts-symbols', 'ttf-nerd-fonts-symbols-mono', 'adobe-source-code-pro-fonts'], ''),
  ('nerd font collection', 'drop', [r'(ttf|otf)-.*-nerd'], '? about 60 patched fonts; keep the one or two the terminals use'),
  ('system tools', 'base', ['gptfdisk', 'nvme-cli', 'fwupd', 'lynx', 'rclone', 'power-profiles-daemon', 'geoclue', 'systemctl-tui', 'sysd-manager', 'systemd-ui', 'zk', 'calcurse', 'newsboat', 'visidata', 'buku', 'nerdfetch', 'resvg', 'pdfjs-legacy'],
     '? three systemd GUIs/TUIs'),

  # --- add-ons (sysext): optional /usr sets ---
  ('image building', 'add-on: image-builder', ['mkosi', 'systemd-ukify', 'sbctl', 'sbsigntools', 'efitools', 'edk2-ovmf', 'edk2-shell', 'swtpm', 'erofs-utils', 'erofsfuse',
     'squashfs-tools', 'cpio', 'mtools', 'dosfstools', 'xfsprogs'], '? builds and signs personal-os; does that stay on the desktop or move to devbox (=carry mkosi in the dev-pod image)?'),
  ('gaming', 'add-on: gaming', ['steam', 'lutris', 'wine', 'winetricks', 'umu-launcher', 'gamemode', 'lib32-vkd3d'], '? sysext (needs 32-bit libraries matching the NVIDIA driver in base) or Flatpak Steam'),
  ('toolchains', 'add-on: dev', ['base-devel', 'rust', 'rust-analyzer', 'go', 'nodejs', 'npm', 'uv', 'ruby', 'ruby-docs', 'ruby-stdlib', 'fennel', 'fnlfmt', 'clisp', 'tcl', 'tk', 'vala',
     'lua51', 'luarocks', 'lua-sec', 'lua-language-server', 'stylua', 'clojure', 'leiningen', 'jre25-openjdk', 'cmake', 'meson', 'ninja', 'ccache', 'python-ruff', 'ty', 'tombi', 'topiary',
     'mdbook', 'texinfo', 'texlive-bin', 'python-.*', 'pyside6', 'luajit-tiktoken-bin', 'tree-sitter-html', 'js-beautify', 'webkitgtk-6.0'],
     '? toolchains as one dev add-on, or in base since this is the dev machine; tcl/tk, vala, clisp, ruby: still used?'),
  ('KDE Plasma', 'add-on: kde', [r'plasma.*', r'k[a-z].*', 'breeze', 'breeze-gtk', 'breeze-plymouth', 'aurorae', 'bluedevil', 'drkonqi', 'discover', 'flatpak-kcm', 'milou',
     'oxygen', 'oxygen-sounds', 'ocean-sound-theme', 'qqc2-breeze-style', 'polkit-kde-agent', 'powerdevil', 'systemsettings', 'spectacle', 'libkscreen', 'libksysguard',
     'libplasma', 'sddm-kcm', 'plymouth-kcm', 'xdg-desktop-portal-kde', 'qt6-tools', 'libkeyfinder'], '? the backup desktop: an add-on, or dropped'),
  ('other desktops', 'drop', ['gnome-shell', 'sway', 'sway-contrib', 'nwg-shell'], '? Hyprland is primary; GNOME, sway and nwg-shell are a third and fourth backup'),

  # --- Flatpak: GUI apps ---
  ('chat', 'flatpak', ['discord', 'signal-desktop', 'telegram-desktop'], ''),
  ('mail', 'flatpak', ['thunderbird', 'external-editor-revived'], 'the editor add-on is a Thunderbird extension, installed inside Thunderbird'),
  ('office and media', 'flatpak', ['libreoffice-fresh', 'obs-studio', 'vlc', 'vlc-plugins-all', 'calibre', 'evince', 'filezilla', 'openaudible-bin', 'protege', 'rclone-ui-bin'], ''),
  ('browsers', 'flatpak', ['firefox', 'firefoxpwa', 'chromium', 'brave-bin', 'vivaldi', 'vivaldi-ffmpeg-codecs', 'helium-browser-bin', 'nyxt', 'qutebrowser'],
     '? nine browsers; qutebrowser has managed config (chezmoi) and may stay a system package'),
  ('AI apps', 'flatpak', ['claude-desktop', 'antigravity', 'geekbench', 'parsec-bin'], 'AUR today; Flathub has some (Parsec); otherwise an image build step or drop'),

  # --- ~/.local via chezmoi: pinned user tools ---
  ('agent and LSP CLIs', 'chezmoi', ['gemini-cli', 'opencode', 'claude-agent-acp', 'nodejs-mcp-hub', 'markdownlint-cli2', 'vscode-json-languageserver', 'wrangler'],
     'markdownlint-cli2 and the JSON server are already in chezmoi\'s npm list; wrangler is per project (npx)'),

  # --- services ---
  ('services machine', 'services: N150', ['radicale', 'copyparty', 'netdata', 'samba', 'vsftpd', 'syncthing'],
     '? radicale and syncthing belong to the services machine (services charter); syncthing may also stay here as a client'),
  ('desktop services', 'services', ['mpd', 'mopidy', 'mopidy-iris', 'mopidy-mpd', 'mympd', 'ollama', 'vdirsyncer', 'agent-sandbox-system', 'hyprwhspr', 'vocalinux', 'yt-dlp'],
     '? mpd and mopidy both; two speech-to-text tools'),
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
order = ['base', 'hardware: intel', 'hardware: nvidia', 'hardware: desktop', 'add-on: dev', 'add-on: image-builder', 'add-on: gaming', 'add-on: kde',
         'flatpak', 'chezmoi', 'services', 'services: N150', 'drop']
rows.sort(key=lambda r: (order.index(r['layer']), r['group'], r['package']))
w = csv.DictWriter(sys.stdout, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n')
w.writeheader(); w.writerows(rows)
