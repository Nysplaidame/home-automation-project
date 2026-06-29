---
title: "Frigate NVR"
category: entity
tags: [software, frigate, cctv, docker, nvr]
created: 2026-04-07
updated: 2026-06-29
sources: [project-readme, frigate-vm-setup-guide, igpu-passthrough-guide]
status: active
---

# Frigate NVR

**Type:** integration - network video recorder
**Status:** CT 111 baseline live; cameras and MQTT deliberately disabled
**Related:** [[entities/proxmox]], [[entities/home-assistant]], [[entities/mosquitto-mqtt]], [[entities/openmediavault-nas]]

## Overview

Frigate 0.17.1 runs on unprivileged Proxmox CT 111. OpenVINO detection and
VA-API use the Intel iGPU shared with [[entities/llm-host]]. The migration-safe
baseline is healthy, but cameras and MQTT remain disabled until camera hardware,
RTSP credentials and final production configuration exist.

## Key Properties

- LXC: Proxmox CT 111 (`frigate-nvr`)
- VLAN: 30 (NVR)
- Static IP: `192.168.30.20`
- MAC: `BC:24:11:71:18:A1`
- Image pulled: `ghcr.io/blakeblackshear/frigate:stable`
- NVR internet access: blocked by design
- `apt-cacher-ng` proxy: `http://192.168.20.102:3142`
- MQTT: disabled in the live baseline
- Fail2ban: `sshd` jail live at `/etc/fail2ban/jail.d/frigate-nvr-sshd.local`

## Staging Gaps

- [x] Stage `/opt/frigate/.env` with MQTT secret.
- [x] Stage MQTT CA trust and verify TLS path.
- [ ] Set final RTSP password after camera model/credentials are selected.
- [ ] Confirm camera RTSP URLs.
- [ ] Configure HTTPS/SSL for regular Frigate UI use.
- [ ] Configure WebRTC audio path for camera streams.
- [x] Run Frigate baseline with a healthy OpenVINO detector.

## NAS Storage

- [[entities/openmediavault-nas]] is live on VLAN 40; production recording cutover will mount `/export/frigate` on Proxmox and bind-mount it into CT 111.
- CT 111 requires explicit Proxmox backup coverage; there are no production camera recordings yet.

## Change Log

- 2026-06-29: Source config was cleaned to the documented migration-safe baseline: `mqtt.enabled: false` and `cameras: {}` until camera hardware and final integrations are ready.
- 2026-06-20: Migrated production identity from VM 101 to CT 111; OpenVINO and
  VA-API share the host iGPU with CT 114. VM 101 is rollback-only.

- 2026-05-30: Added VM-level Fail2ban SSH hardening baseline; `sshd` jail active with 0 failed and 0 banned after install.
- 2026-05-30: Synced staging state: MQTT secret/CA are staged and TLS verified, but Frigate remains unbuilt for regular use until cameras, RTSP, HTTPS, and audio are ready.
- 2026-05-23: Updated storage target from deprecated Pi NAS plan to OMV NAS.
- 2026-05-08: Major update - VM 101 live on Debian 13; Frigate staged not started; Bambuddy moved to VM 103; apt-cache proxy noted.
- 2026-04-07: Page created from project-wide ingest.
