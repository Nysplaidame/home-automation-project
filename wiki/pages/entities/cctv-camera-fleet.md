---
title: "CCTV Camera Fleet"
category: entity
tags: [hardware, cctv, camera, frigate, vlan-30]
created: 2026-07-28
updated: 2026-07-29
sources: [project-readme, frigate-vm-setup-guide]
status: active
---

# CCTV Camera Fleet

**Type:** device fleet
**Status:** Three cameras operational
**Related:** [[entities/frigate]], [[entities/home-assistant]], [[concepts/vlan-segmentation]]

## Overview

The exterior CCTV fleet streams main and sub RTSP feeds to [[entities/frigate]]
on isolated VLAN 30. The Zyxel GS1900-8HP provides PoE and access switching.

## Live Inventory

| Frigate identity | Location | IP | Switch port | MAC | Model status |
|---|---|---:|---:|---|---|
| `cam_01_annke_c500` | Camera 1 / original bench view | `192.168.30.21` | 2 | `D0:3B:F4:07:71:45` | ANNKE C500 `I51HJ`, firmware verified |
| `cam_02_gate` | Gate | `192.168.30.22` | 4 | `D0:3B:F4:07:71:A0` | ANNKE C500 `I51HJ`, firmware `v5.8.10 build 250917` |
| `cam_03_patio` | Patio | `192.168.30.23` | 3 | `D0:3B:F4:07:72:BE` | ANNKE C500 `I51HJ`, firmware `v5.8.10 build 250917` |

## Network and Monitoring

- Switch ports 2-7 are saved as PoE access ports: VLAN 30 untagged, PVID 30.
- Port 1 remains the router trunk and port 8 remains the VLAN 40 NAS port.
- Home Assistant consumes Frigate MQTT stats and alerts after three continuous
  minutes below 1 fps. A recovery message clears the persistent alert and
  replaces the mobile notification.
- Uptime Kuma now pings `.21`, `.22`, and `.23` from monitoring VM
  `192.168.60.10`; all three ntfy-enabled checks returned `Up` after OpenWrt was
  limited to ICMP for exactly those hosts.

## Open Questions

- [ ] Record the next camera's MAC and location before adopting it on ports 5-7.

## Change Log

- 2026-07-29: Added direct Uptime Kuma reachability checks for all three camera
  hosts through a host-scoped ICMP firewall rule.
- 2026-07-28: Page created from the verified live switch, Frigate, and Home
  Assistant state after recovery of the Gate camera.
- 2026-07-28: Confirmed Gate and Patio match Camera 1: ANNKE C500 `I51HJ`,
  firmware `v5.8.10 build 250917`.
