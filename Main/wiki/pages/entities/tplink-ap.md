---
title: "TP-Link TL-WA801N (Access Point)"
category: entity
tags: [hardware, network, wifi, access-point, vlan1]
created: 2026-04-07
updated: 2026-04-07
sources: [router-setup-complete]
status: stub
---

# TP-Link TL-WA801N

**Type:** device — WiFi access point
**Status:** ⏳ Mentioned in router setup / not yet deployed
**Related:** [[entities/gl-mt6000]]

## Overview

A TP-Link TL-WA801N configured as an AP (not a router) to extend HomeMain WiFi coverage via the GL-MT6000's lan5 port. lan5 carries VLAN 1 untagged — the AP operates on VLAN 1 (main user network) and bridges wireless clients directly to VLAN 1.

## Key Properties

- Mode: Access Point (not router mode)
- Connected to: GL-MT6000 lan5 (VLAN 1 untagged)
- Network: VLAN 1 / 192.168.1.0/24
- SSID: HomeMain (extends the main GL-MT6000 SSID)

## Setup Notes

- lan5 is used as a recovery port during router setup. **Do not connect the AP until after the router setup is fully validated** — you need lan5 free for your management laptop during Phase 2.
- No router-side config changes needed when transitioning from recovery laptop to AP.
- AP should be configured in AP mode (disable DHCP, set static IP in 192.168.1.x range for management).

## Open Questions

- [ ] Confirm AP is configured in AP mode (not NAT/router mode)
- [ ] Note AP MAC address for DHCP reservation if static IP desired

## Change Log

- 2026-04-07: Page created — stub. Discovered in router_setup_complete.md Phase 1 and 2.
