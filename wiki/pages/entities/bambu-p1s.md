---
title: "Bambu Lab P1S (3D Printer)"
category: entity
tags: [hardware, 3d-printer, bambulab, p1s]
created: 2026-04-07
updated: 2026-08-25
sources: [project-readme, troubleshooting-reference]
status: active
---

# Bambu Lab P1S

**Type:** device — FDM 3D printer
**Status:** Deployed on printer VLAN 35; currently unreachable from VM 103
**Related:** [[entities/bambuddy]], [[entities/home-assistant]], [[entities/ventsys]]

## Overview

Bambu Lab P1S FDM printer monitored via [[entities/bambuddy]]. It belongs on the
isolated HomePrinters/VLAN 35 network and requires Developer Mode for local
MQTT. The current architecture remains valid, but the printer or VLAN path must
be restored before Bambuddy can leave host networking.

## Key Properties

- Network: VLAN 35 (Printers — `192.168.35.0/24`), HomePrinters Wi-Fi
- Static IP: `192.168.35.200`
- Protocol: Bambu Lab proprietary MQTT (port 8883 on printer)
- Developer Mode: required — enable via Settings → Network on printer touchscreen

## HA Entities (via Bambuddy)

- `binary_sensor.p1s_printing` — is the printer currently printing?
- Print state entities published to `bambuddy/printers/<serial>/status`

## Firewall Rule

- `Bambuddy to P1S`: docker-host VM 103 (`192.168.20.102`, VLAN 20) → P1S
  (`192.168.35.200`) on TCP `21` and `8883` only

## Open Questions

- [ ] Confirm actual MAC address → add static DHCP reservation in `dhcp-config.conf`
- [ ] Replace `<P1S_SERIAL>` in `bambuddy_p1s_package.yaml` with real serial
- [ ] Verify Developer Mode remains enabled after firmware updates

## Change Log

- 2026-08-25: Corrected the stale VLAN 1/Frigate placement to the live VLAN 35
  and docker-host architecture; recorded the current reachability blocker.
- 2026-04-07: Page created from project-wide ingest
