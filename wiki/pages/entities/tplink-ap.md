---
title: "TP-Link TL-WA801N (Access Point)"
category: entity
tags: [hardware, network, wifi, access-point, vlan1]
created: 2026-04-07
updated: 2026-08-25
sources: [router-setup-complete, project-todo]
status: stub
---

# TP-Link TL-WA801N

**Type:** device — WiFi access point
**Status:** ⏳ Mentioned in router setup / not yet deployed
**Related:** [[entities/gl-mt6000]]

## Overview

A planned TP-Link TL-WA801N configured as an AP (not a router) to extend
HomeMain WiFi. The current design keeps GL-MT6000 `lan5` as the direct VLAN 1
LAN/recovery port. The AP therefore needs a managed-switch access port carrying
VLAN 1 untagged, but the current eight-port switch allocation has no free port;
capacity and wiring must be decided before deployment.

## Key Properties

- Mode: Access Point (not router mode)
- Connected to: not deployed; future managed-switch VLAN 1 access port
- Network: VLAN 1 / 192.168.1.0/24
- SSID: HomeMain (extends the main GL-MT6000 SSID)

## Setup Notes

- Keep router `lan5` available for a normal LAN device or recovery laptop.
- Before installing the AP, free or add managed-switch capacity and validate an
  untagged VLAN 1/PVID 1 access port.
- AP should be configured in AP mode (disable DHCP, set static IP in 192.168.1.x range for management).

## Open Questions

- [ ] Confirm AP is configured in AP mode (not NAT/router mode)
- [ ] Note AP MAC address for DHCP reservation if static IP desired
- [ ] Decide and document the physical switch port/capacity change

## Change Log

- 2026-04-07: Page created — stub. Discovered in router_setup_complete.md Phase 1 and 2.
- 2026-08-25: Corrected the planned attachment: router `lan5` remains the LAN/recovery port; AP switch capacity is unresolved.
