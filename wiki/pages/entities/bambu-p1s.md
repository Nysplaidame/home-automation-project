---
title: "Bambu Lab P1S (3D Printer)"
category: entity
tags: [hardware, 3d-printer, bambulab, p1s]
created: 2026-04-07
updated: 2026-10-20
sources: [project-readme, troubleshooting-reference]
status: active
---

# Bambu Lab P1S

**Type:** device — FDM 3D printer
**Status:** Commissioned on VLAN35; VM103 MQTT/FTPS reachable on October20
**Related:** [[entities/bambuddy]], [[entities/home-assistant]], [[entities/ventsys]]

## Overview

Bambu Lab P1S FDM printer monitored via [[entities/bambuddy]]. It belongs on the
isolated HomePrinters/VLAN 35 network and requires Developer Mode for local
MQTT. October20 checks confirmed VM103 MQTT/FTPS reachability. Bambuddy's
host-network exception remains a separate deployment decision.

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
  (`192.168.35.200`) uses TCP8883/990; live rules also cover camera TCP6000
  and FTPS data TCP2024/50000–50100.

## Admin desktop access

The canonical [[main/docs/reference/windows-admin-pc-routes|desktop route inventory]]
records five persistent project routes via `.10.1`. Physical P1S uses
`192.168.35.200/32`, added October20 after loss of HomePrinters Wi-Fi exposed
the missing route under Mullvad. Desktop TCP8883/990/6000 passed; Orca
application acceptance remains pending. VM103 ping rejection is not service failure.

## Open Questions

- [ ] Confirm actual MAC address → add static DHCP reservation in `dhcp-config.conf`
- [ ] Replace `<P1S_SERIAL>` in `bambuddy_p1s_package.yaml` with real serial
- [ ] Verify Developer Mode remains enabled after firmware updates

## Change Log

- 2026-10-20: Reconciled stale reachability/port claims and linked route inventory.

- 2026-08-25: Corrected the stale VLAN 1/Frigate placement to the live VLAN 35
  and docker-host architecture; recorded the current reachability blocker.
- 2026-04-07: Page created from project-wide ingest
