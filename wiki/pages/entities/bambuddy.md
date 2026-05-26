---
title: "Bambuddy"
category: entity
tags: [software, bambuddy, docker, bambulab, p1s, mqtt]
created: 2026-04-07
updated: 2026-05-18
sources: [project-readme, bambuddy-p1s-setup-guide]
status: stable
---

# Bambuddy

**Type:** integration — Bambu Lab printer bridge (Docker container)
**Status:** ✅ Running on VM 103 (docker-host) at `http://192.168.20.102:8000`
**Related:** [[entities/bambu-p1s]], [[entities/home-assistant]], [[entities/mosquitto-mqtt]], [[entities/proxmox]], [[entities/docker-host]]

## Overview

Bambuddy bridges the Bambu Lab P1S's proprietary protocol to MQTT, publishing print state to Home Assistant. It runs on VM 103 (docker-host) at `192.168.20.102`, port 8000, using `network_mode: host`. The container is live and healthy. P1S integration in HA is parked until the printer's serial number and RTSP/details are physically available.

Note: Bambuddy originally planned to run on VM 101 (frigate-nvr). It was moved to VM 103 (docker-host) as a dedicated, trusted Docker host on VLAN 20.

## Key Properties

- VM: Proxmox VM 103 (`docker-host`)
- VLAN: 20 (Automation)
- Host IP: `192.168.20.102`
- Web UI: `http://192.168.20.102:8000`
- Network mode: `host`
- Printer IP: `192.168.35.200` (Bambu P1S on VLAN 35 / Printers)
- Deploy path: `/opt/stacks/bambuddy/`
- Image: `ghcr.io/maziggy/bambuddy:latest` (ID `debbfe09b1cf`, ~1.57GB)

## Docker Compose

```yaml
services:
  bambuddy:
    container_name: bambuddy
    image: ghcr.io/maziggy/bambuddy:latest
    restart: unless-stopped
    network_mode: host
    environment:
      - TZ=Europe/London
      - PORT=8000
      - MQTT_HOST=${MQTT_HOST}
      - MQTT_PORT=${MQTT_PORT}
      - MQTT_USER=${MQTT_USER}
      - MQTT_PASSWORD=${MQTT_PASSWORD}
    volumes:
      - /opt/stacks/bambuddy/data:/app/data
      - /opt/stacks/bambuddy/logs:/app/logs
```

## Environment (`.env` on VM 103)

```env
MQTT_HOST=192.168.20.101
MQTT_PORT=8883
MQTT_USER=mqtt
MQTT_PASSWORD=<from Bitwarden>
```

Bambuddy's application database settings also use `mqtt_enabled=true`, `mqtt_broker=192.168.20.101`, `mqtt_port=8883`, `mqtt_username=mqtt`, `mqtt_use_tls=true`, and `mqtt_topic_prefix=bambuddy`.

## Live MQTT Verification

- Bambuddy logs confirmed both MQTT relay and MQTT smart-plug service connected to `192.168.20.101:8883`.
- Mosquitto logs confirmed Bambuddy negotiated TLSv1.3 from `192.168.20.102`.
- Retained `bambuddy/status` was verified over TLS on `8883`.

## Firewall (VM 103 UFW)

- Incoming default: deny
- Allow `192.168.10.0/24` → TCP 22 (management SSH)
- Allow `192.168.10.0/24` → TCP 8000 (web UI from management)
- Allow `192.168.1.0/24` → TCP 8000
- Allow `192.168.20.0/24` → TCP 8000

## HA Integration (parked)

- HA package: `configs/home-assistant/bambuddy_p1s_package.yaml`
- **Do not deploy** until `<P1S_SERIAL>` placeholder is replaced and MQTT topics are confirmed
- Will publish: `binary_sensor.p1s_printing`, print state entities
- P1S must be in Developer Mode (LAN Only Mode) with known access code and serial

## Pending

- [ ] Add P1S details and HA Long-Lived Token in Bambuddy web UI once printer is physically available.
- [ ] Replace `<P1S_SERIAL>` in `bambuddy_p1s_package.yaml` then deploy to HA.
- [ ] Confirm Bambuddy P1S MQTT topics before enabling HA package entities.

## Troubleshooting

- Container won't start: `docker compose logs bambuddy --tail=40`.
- P1S "Connection Failed": ensure Developer Mode enabled; verify access code.
- MQTT not publishing: subscribe to `bambuddy/#` over TLS from HA Terminal.
- See [[sources/troubleshooting-reference]].

## Change Log

- 2026-05-18: Updated MQTT status from 1883 pending migration to live TLS on 8883; added verification details.
- 2026-05-08: Major update — Bambuddy live on VM 103 (moved from VM 101); compose/env details added; P1S integration still parked.
- 2026-04-07: Page created from project-wide ingest.
