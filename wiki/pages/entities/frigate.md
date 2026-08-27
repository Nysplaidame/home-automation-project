---
title: "Frigate NVR"
category: entity
tags: [software, frigate, cctv, docker, nvr]
created: 2026-04-07
updated: 2026-07-28
sources: [project-readme, frigate-vm-setup-guide, igpu-passthrough-guide]
status: active
---

# Frigate NVR

**Type:** integration - network video recorder
**Status:** Operational with three live cameras, MQTT TLS, and NAS recordings
**Related:** [[entities/proxmox]], [[entities/home-assistant]], [[entities/mosquitto-mqtt]], [[entities/openmediavault-nas]], [[entities/cctv-camera-fleet]]

## Overview

Frigate 0.17.1 runs on unprivileged Proxmox CT 111. OpenVINO detection and
VA-API use the Intel iGPU shared with [[entities/llm-host]]. Three exterior
cameras are live through go2rtc main/sub restreams, MQTT uses TLS to Home
Assistant, and recordings write to OMV-backed storage.

## Key Properties

- LXC: Proxmox CT 111 (`frigate-nvr`)
- VLAN: 30 (NVR)
- Static IP: `192.168.30.20`
- MAC: `BC:24:11:71:18:A1`
- Image pulled: `ghcr.io/blakeblackshear/frigate:stable`
- NVR internet access: blocked by design
- `apt-cacher-ng` proxy: `http://192.168.20.102:3142`
- MQTT: TLS to Home Assistant Mosquitto on `8883`
- Cameras: Camera 1 (`.21`), Gate (`.22`), Patio (`.23`)
- Camera-health alerts: three-minute offline debounce plus recovery notification
- Fail2ban: `sshd` jail live at `/etc/fail2ban/jail.d/frigate-nvr-sshd.local`

## Camera Rollout

- [x] Stage `/opt/frigate/.env` with MQTT secret.
- [x] Stage MQTT CA trust and verify TLS path.
- [x] Set live RTSP credential through `/opt/frigate/.env`.
- [x] Confirm main/sub RTSP URLs for all three cameras.
- [x] Configure trusted local HTTPS for regular Frigate UI use.
- [x] Configure go2rtc/WebRTC viewing path.
- [x] Run Frigate baseline with a healthy OpenVINO detector.
- [ ] Define final zones, masks, and alert rules for Gate and Patio.
- [x] Confirm all three cameras are ANNKE C500 `I51HJ` units running firmware
  `v5.8.10 build 250917`.

## NAS Storage

- [[entities/openmediavault-nas]] is live on VLAN 40; `/export/frigate` is
  mounted on Proxmox and bind-mounted into CT 111 for recordings.
- CT 111 is covered by the Proxmox backup workflow; media retention remains
  event/motion-oriented rather than continuous.

## Change Log

- 2026-07-28: Synced to the three-camera production configuration, MQTT TLS,
  OMV recordings, saved switch ports 2-7 as CCTV VLAN 30 access ports, and
  added debounced Home Assistant camera-offline/recovery alerts.
- 2026-06-29: Source config was cleaned to the documented migration-safe baseline: `mqtt.enabled: false` and `cameras: {}` until camera hardware and final integrations are ready.
- 2026-06-20: Migrated production identity from VM 101 to CT 111; OpenVINO and
  VA-API share the host iGPU with CT 114. VM 101 is rollback-only.

- 2026-05-30: Added VM-level Fail2ban SSH hardening baseline; `sshd` jail active with 0 failed and 0 banned after install.
- 2026-05-30: Synced staging state: MQTT secret/CA are staged and TLS verified, but Frigate remains unbuilt for regular use until cameras, RTSP, HTTPS, and audio are ready.
- 2026-05-23: Updated storage target from deprecated Pi NAS plan to OMV NAS.
- 2026-05-08: Major update - VM 101 live on Debian 13; Frigate staged not started; Bambuddy moved to VM 103; apt-cache proxy noted.
- 2026-04-07: Page created from project-wide ingest.
