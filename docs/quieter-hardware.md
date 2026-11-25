# The Quieter: hardware

MeLE Quieter 4C (DMI: "Mini PC" / "Quieter 4C"), the modular client. Recorded 2026-11-25 over SSH from the
installed Fedora 45 KDE (kernel 7.3.4), not a live USB: Windows was already gone.

| Part | Device | Linux driver |
| --- | --- | --- |
| CPU / iGPU | Intel Alder Lake-N (N150), Intel Graphics [8086:46d4] | i915 (xe also offered) |
| WiFi | Intel CNVi [8086:54f0], firmware so-a0-jf-b0-77 | iwlwifi (mvm) |
| Bluetooth | Intel 9460/9560 Jefferson Peak [8087:0aaa], firmware ibt-0040-2120 | btintel |
| Ethernet | Realtek RTL8111/8168 [10ec:8168] | r8169 |
| Audio | Alder Lake-N HDA [8086:54c8] | snd_hda_intel |
| Storage | 116.5 GiB eMMC (mmcblk0) [8086:54c4] | sdhci-pci |
| RAM | 7.5 GiB usable, soldered | |

Firmware loaded without errors: i915 DMC adlp_dmc 2.20, GuC 70.49.4, HuC 7.9.3, iwlwifi, Bluetooth.

**USB-C:** power and display both work under Linux. The monitor is on DP-1 (USB-C alt mode); the three HDMI
connectors are unused. A VIA Labs USBC-PDMON sits in the chain.

**Memory pressure:** at recording, 4.0 GiB RAM and 4.2 GiB of zram swap were in use (Chrome and 1Password
Flatpaks plus Plasma). 8 GB is tight for a browser-heavy session.

## What Fedora needed by hand

From `dnf history list` and `flatpak list`, beyond the stock Fedora KDE install: ghostty, tailscale, chezmoi,
gh, neovim (dnf); rust and cargo (dnf, for a cargo-binstall of Neovide); Google Chrome and 1Password (Flathub).
This is the requirements list for the quieter profile: system packages go in the image, apps stay Flatpaks.
