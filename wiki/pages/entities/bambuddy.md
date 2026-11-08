---
title: "Bambuddy"
category: entity
tags: [software, bambuddy, docker, bambulab, p1s, mqtt]
created: 2026-04-07
updated: 2026-10-02
sources: [project-readme, bambuddy-p1s-setup-guide]
status: stable
---

# Bambuddy

**Type:** integration — Bambu Lab printer bridge (Docker container)
**Status:** ✅ Running on VM 103 (docker-host) at `http://192.168.20.102:8000`
**Related:** [[entities/bambu-p1s]], [[entities/home-assistant]], [[entities/mosquitto-mqtt]], [[entities/proxmox]], [[entities/docker-host]]

## Overview

Bambuddy bridges the Bambu Lab P1S's proprietary protocol to MQTT, publishing
print state to Home Assistant. It runs on VM 103 (docker-host) at
`192.168.20.102`, port 8000, using `network_mode: host`. The P1S is commissioned
on VLAN35 with Home Assistant MQTT telemetry and a P1S dashboard. The container
is healthy on release 1.2.5.6 as of October 2. The prepared `10.240.23.0/24`
bridge migration remains a separate unaccepted change.

Note: Bambuddy originally planned to run on VM 101 (frigate-nvr). It was moved to VM 103 (docker-host) as a dedicated, trusted Docker host on VLAN 20.

## Key Properties

- VM: Proxmox VM 103 (`docker-host`)
- VLAN: 20 (Automation)
- Host IP: `192.168.20.102`
- Web UI: `http://192.168.20.102:8000`
- Network mode: `host`
- Prepared network: explicit `bambuddy` bridge at `10.240.23.0/24`; not yet
  attached to the live container
- Printer IP: `192.168.35.200` (Bambu P1S on VLAN 35 / Printers)
- Deploy path: `/opt/stacks/bambuddy/`
- Runtime image: updater-owned local staged tag; release 1.2.5.6 was verified
  on October 2. Future installed versions are in VM103's updater receipt.

## Scheduled offline updates

The owner authorized a Bambuddy-only automatic-update exception on October 2.
Windows/Ubuntu WSL checks stable releases at 09:00 while Admin is signed in,
downloads an amd64 image and sends a checksummed bundle over existing SSH to
VM103. A London-time timer checks at 04:30, then every half-hour through 06:30.
Disconnected/busy printers, active heaters and nonterminal queue entries defer it.
VM103 uses local image loading with pulling disabled; no registry egress is
needed. Major releases require manual review. Watchtower remains monitor-only.

Before installation the updater saves a stopped-service data/config checkpoint
and old image to OMV, tests copied-data migration with networking disabled, and
verifies production version/image/network identity plus printer reconnection.
Failure restores matching old data and image, preserves failed data, and blocks
the bundle from automatic retry. Three successful checkpoint generations are
retained. The first manual 1.2.5.5 to 1.2.5.6 run passed; the first unattended
window remains unproven.

Canonical procedure: [[main/docs/procedures/bambuddy_offline_updates]].
Current state: [[main/docs/reference/current-live-state]].

## Original base Docker Compose

The live updater now adds an image-only override with `pull_policy: never`.
The base below records placement and environment; the tracked rebuild template
uses the prepared bridge and must not replace the running file during an update.

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

## HA Integration

- HA package: `configs/home-assistant/bambuddy_p1s_package.yaml`
- Verify `<P1S_SERIAL>` is replaced and live MQTT topics exist before relying
  on the package entities
- Publishes/defines `binary_sensor.p1s_printing` and print-state entities when
  the printer path is available
- P1S must be in Developer Mode (LAN Only Mode) with known access code and serial

## Pending

- [x] P1S commissioned on VLAN35; current file-transfer context is FTPS990.
- [ ] Retry the prepared bridge migration and pass
  `docker-host-security-audit.sh --verify` with zero failures.
- [x] P1S telemetry and Home Assistant dashboard commissioned.
- [ ] Confirm first unattended staging/install window after October 2 setup.

## Troubleshooting

- Container won't start: `docker compose logs bambuddy --tail=40`.
- P1S "Connection Failed": ensure Developer Mode enabled; verify access code.
- MQTT not publishing: subscribe to `bambuddy/#` over TLS from HA Terminal.
- See [[sources/troubleshooting-reference]].

## Change Log

- 2026-10-02: Reconciled commissioned P1S state and documented the owner-approved
  staged offline updater from canonical procedure/current-live-state. First manual
  release update passed; unattended schedule remains to be observed.

- 2026-08-25: Recorded the controlled bridge attempt, rollback and current P1S
  reachability blocker; the prepared explicit network remains the target.
- 2026-05-18: Updated MQTT status from 1883 pending migration to live TLS on 8883; added verification details.
- 2026-05-08: Major update — Bambuddy live on VM 103 (moved from VM 101); compose/env details added; P1S integration still parked.
- 2026-04-07: Page created from project-wide ingest.
