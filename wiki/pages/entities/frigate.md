---
title: "Frigate NVR"
category: entity
tags: [software, frigate, cctv, docker, nvr]
created: 2026-04-07
updated: 2026-05-30
sources: [project-readme, frigate-vm-setup-guide, igpu-passthrough-guide]
status: active
---

# Frigate NVR

**Type:** integration - network video recorder
**Status:** VM shell live / Docker staging complete / Frigate app unbuilt for regular use
**Related:** [[entities/proxmox]], [[entities/home-assistant]], [[entities/mosquitto-mqtt]], [[entities/openmediavault-nas]]

## Overview

Frigate NVR is staged for Docker on Proxmox VM 101 (Debian 13). The VM shell,
Docker base, config, MQTT secret, and MQTT CA trust are staged, but the Frigate
application is not live for regular use. It still needs camera hardware, final
RTSP credentials, HTTPS/SSL, and WebRTC audio planning.

## Key Properties

- VM: Proxmox VM 101 (`frigate-nvr`)
- VLAN: 30 (NVR)
- Static IP: `192.168.30.20`
- MAC: `BC:24:11:9C:25:87`
- Image pulled: `ghcr.io/blakeblackshear/frigate:stable`
- NVR internet access: blocked by design
- `apt-cacher-ng` proxy: `http://192.168.20.102:3142`
- MQTT path: TLS `192.168.20.101:8883` verified with staged CA

## Staging Gaps

- [x] Stage `/opt/frigate/.env` with MQTT secret.
- [x] Stage MQTT CA trust and verify TLS path.
- [ ] Set final RTSP password after camera model/credentials are selected.
- [ ] Confirm camera RTSP URLs.
- [ ] Configure HTTPS/SSL for regular Frigate UI use.
- [ ] Configure WebRTC audio path for camera streams.
- [ ] Run `docker compose up -d` from `/opt/frigate/`.

## NAS Storage

- Will mount [[entities/openmediavault-nas]] at `/mnt/nas/frigate` via NFS when NAS hardware is ready.
- Do not use local daily Proxmox snapshots for VM 101 once video data is active.

## Change Log

- 2026-05-30: Synced staging state: MQTT secret/CA are staged and TLS verified, but Frigate remains unbuilt for regular use until cameras, RTSP, HTTPS, and audio are ready.
- 2026-05-23: Updated storage target from deprecated Pi NAS plan to OMV NAS.
- 2026-05-08: Major update - VM 101 live on Debian 13; Frigate staged not started; Bambuddy moved to VM 103; apt-cache proxy noted.
- 2026-04-07: Page created from project-wide ingest.
