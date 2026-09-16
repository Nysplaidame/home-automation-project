---
title: "Raspberry Pi Display Units"
category: entity
tags: [hardware, raspberry-pi, display, kiosk, vlan1]
created: 2026-04-07
updated: 2026-08-25
sources: [openwrt-dhcp-config, openwrt-vlan-firewall-configs]
status: stub
---

# Raspberry Pi Display Units

**Type:** device — wall-mounted kiosk displays
**Status:** ⏳ Mentioned in configs / not yet deployed
**Related:** [[entities/home-assistant]], [[entities/gl-mt6000]]

## Overview

Two Raspberry Pi units configured as kiosk-mode displays for the HA dashboard. Placed on VLAN 1 (LAN) as trusted household devices. Access is controlled via HA user permissions (a restricted "display" user account), not firewall path filtering.

## Key Properties

- `rpi-display-1`: 192.168.1.201 (VLAN 1)
- `rpi-display-2`: 192.168.1.202 (VLAN 1)
- Network path: covered by `LAN to Home Assistant UI` firewall rule (port 8123)
- Mode: kiosk browser planned to use `https://homeassistant.home.local:8123`

## Open Questions

- [ ] Which Pi model? (Pi 3B+ or Pi 4?)
- [ ] Which kiosk software? (Chromium in kiosk mode? Fully Kiosk Browser?)
- [ ] Are these purchased yet?
- [ ] What HA dashboard / view is shown?

## Change Log

- 2026-04-07: Page created — stub. Discovered in dhcp-config.conf and firewall-config.conf comments.
- 2026-08-25: Updated the planned kiosk endpoint to the current local-CA HTTPS URL.
