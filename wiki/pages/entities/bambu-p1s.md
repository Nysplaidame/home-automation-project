---
title: "Bambu Lab P1S (3D Printer)"
category: entity
tags: [hardware, 3d-printer, bambulab, p1s]
created: 2026-04-07
updated: 2026-04-07
sources: [project-readme, troubleshooting-reference]
status: active
---

# Bambu Lab P1S

**Type:** device — FDM 3D printer
**Status:** ✅ Owned (assumed) / operational on VLAN 1
**Related:** [[entities/bambuddy]], [[entities/home-assistant]], [[entities/ventsys]]

## Overview

Bambu Lab P1S FDM printer monitored via [[entities/bambuddy]] bridge. Lives on VLAN 1 (LAN) at a static IP. Requires Developer Mode enabled for MQTT access. The P1S is one of the two printers whose enclosure is managed by [[entities/ventsys]].

## Key Properties

- Network: VLAN 1 (LAN — 192.168.1.0/24)
- Static IP: `192.168.1.200` (DHCP reservation by MAC)
- Protocol: Bambu Lab proprietary MQTT (port 8883 on printer)
- Developer Mode: required — enable via Settings → Network on printer touchscreen

## HA Entities (via Bambuddy)

- `binary_sensor.p1s_printing` — is the printer currently printing?
- Print state entities published to `bambuddy/printers/<serial>/status`

## Firewall Rule

- `Bambuddy to P1S`: Frigate VM (192.168.30.20, VLAN 30) → P1S (192.168.1.200, port 8883)

## Open Questions

- [ ] Confirm actual MAC address → add static DHCP reservation in `dhcp-config.conf`
- [ ] Replace `<P1S_SERIAL>` in `bambuddy_p1s_package.yaml` with real serial
- [ ] Verify Developer Mode remains enabled after firmware updates

## Change Log

- 2026-04-07: Page created from project-wide ingest
