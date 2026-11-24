---
id: 01a20c58-7420-7bb3-9881-4c40efb6326c
alias: quieter
parent: personal-os
state: Active
---
# Modular client: the Quieter

The MeLE Quieter 4C (Amazon B0F3DBKSC2), arrival date unknown: Darrion's final attempt at a local modular client,
the Duet's replacement. Listed as Intel N150, fanless, 8 GB soldered RAM, 128 GB eMMC, WiFi 5, BT 5.1, two HDMI and
one USB-C carrying power, display and data. Same CPU family as the [services](services.md) N150, so records call
this one the Quieter. Windows comes off it on arrival.

## Decided

- 2026-11-24, Darrion: its own personal-os profile, graphical, with KDE Plasma ("my current default rn"). It is
  the first graphical personal-os machine on real hardware; the [desktop](desktop.md) still runs hand-configured
  Arch.
- 2026-11-24, Darrion: no seamless power-off. A dropped cable cuts the Quieter; that is a battery limitation, not
  the machine's, and the tradeoff is accepted. No unplug test.
- 2026-11-24, Darrion: 128 GB is enough for full KDE.
- 2026-11-24, Darrion: a shared `kde` profile for the desktop and the Quieter ("try the shared profile and see
  where things break"). `scripts/mkosi-arch desktop|quieter` adds it; the desktop resolves to the same 283 packages as
  before the split.

## Open

- Which hardware rows the machine needs beyond the listing (=quieter-inventory).

## Log
