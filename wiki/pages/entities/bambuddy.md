---
title: "Bambuddy"
category: entity
tags: [software, bambuddy, docker, bambulab, p1s, mqtt]
created: 2026-04-07
updated: 2026-04-07
sources: [project-readme, troubleshooting-reference]
status: active
---

# Bambuddy

**Type:** integration — Bambu Lab printer bridge (Docker container)
**Status:** ✅ Documented / ⏳ Not yet deployed
**Related:** [[entities/frigate]], [[entities/bambu-p1s]], [[entities/home-assistant]], [[entities/mosquitto-mqtt]]

## Overview

Bambuddy is a Docker container that bridges the Bambu Lab P1S printer's proprietary protocol to MQTT, making print state available to Home Assistant. It runs on Proxmox VM 101 alongside Frigate (port 8000), using `network_mode: host` so it shares the VM's IP (`192.168.30.20`).

## Key Properties

- VM: Proxmox VM 101 (alongside [[entities/frigate]])
- Host IP: `192.168.30.20` (VLAN 30)
- Web UI: `http://192.168.30.20:8000`
- Network mode: `host` (same IP as Frigate VM)
- Printer IP: `192.168.1.200` (Bambu P1S on VLAN 1 / LAN)
- Deploy path: `/opt/frigate/` (shared with Frigate)

## Environment Variables (`.env` file)

```
BAMBU_PRINTER_IP=192.168.1.200
BAMBU_ACCESS_CODE=<from printer>
BAMBU_SERIAL=<P1S serial>
FRIGATE_RTSP_PASSWORD=<password>
FRIGATE_MQTT_PASSWORD=<password>
HA_LONG_LIVED_TOKEN=<optional — can use web UI instead>
```

## HA Integration

- HA package: `configs/home-assistant/bambuddy_p1s_package.yaml`
- Replace `<P1S_SERIAL>` placeholder before deployment
- Publishes: `binary_sensor.p1s_printing`, print state entities
- MQTT topics: `bambuddy/printers/<serial>/status`

## Firewall Rules Required

- `Bambuddy to P1S` — VM 101 (VLAN 30) → P1S (VLAN 1, port 8883)
- `Bambuddy MQTT to HA` — VM 101 (VLAN 30) → HA (VLAN 20, port 8883)
- `Bambuddy to HA API` — VM 101 (VLAN 30) → HA (VLAN 20, port 8123)

## Troubleshooting

- Container won't start: `docker compose logs bambuddy --tail=40`
- P1S "Connection Failed": ensure Developer Mode enabled on printer; verify access code
- MQTT not publishing: `mosquitto_sub -t 'bambuddy/#' -v` from HA terminal
- See [[sources/troubleshooting-reference]]

## Change Log

- 2026-04-07: Page created from project-wide ingest
