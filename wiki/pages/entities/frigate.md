---
title: "Frigate NVR"
category: entity
tags: [software, frigate, cctv, docker, nvr]
created: 2026-04-07
updated: 2026-05-23
sources: [project-readme, frigate-vm-setup-guide, igpu-passthrough-guide]
status: active
---

# Frigate NVR

**Type:** integration - network video recorder
**Status:** VM live (Debian 13, Docker installed) / Frigate not yet started
**Related:** [[entities/proxmox]], [[entities/home-assistant]], [[entities/mosquitto-mqtt]], [[entities/openmediavault-nas]]

## Overview

Frigate NVR runs in Docker on Proxmox VM 101 (Debian 13). Frigate image is
pulled and config is staged at `/opt/frigate/`. The container is not yet started
because it needs camera hardware, a finalized `.env`, and MQTT TLS/cert details.

## Key Properties

- VM: Proxmox VM 101 (`frigate-nvr`)
- VLAN: 30 (NVR)
- Static IP: `192.168.30.20`
- MAC: `BC:24:11:9C:25:87`
- Image pulled: `ghcr.io/blakeblackshear/frigate:stable`
- NVR internet access: blocked by design
- `apt-cacher-ng` proxy: `http://192.168.20.102:3142`

## Staging Gaps

- [ ] Create `/opt/frigate/.env` with RTSP and MQTT secrets.
- [ ] Finalize MQTT TLS cert path.
- [ ] Confirm camera RTSP URLs.
- [ ] Run `docker compose up -d` from `/opt/frigate/`.

## NAS Storage

- Will mount [[entities/openmediavault-nas]] at `/mnt/nas/frigate` via NFS when NAS hardware is ready.
- Do not use local daily Proxmox snapshots for VM 101 once video data is active.

## Change Log

- 2026-05-23: Updated storage target from deprecated Pi NAS plan to OMV NAS.
- 2026-05-08: Major update - VM 101 live on Debian 13; Frigate staged not started; Bambuddy moved to VM 103; apt-cache proxy noted.
- 2026-04-07: Page created from project-wide ingest.
