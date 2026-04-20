---
title: "Frigate VM Setup Guide"
category: source
tags: [frigate, docker, debian, setup, cctv, igpu, bambuddy]
created: 2026-04-07
updated: 2026-04-07
status: stable
---

# Source: Frigate VM Setup Guide

**Original file:** `scripts/setup/proxmox/frigate_vm_setup_guide.md`
**Date ingested:** 2026-04-07
**Type:** setup guide

## Summary

Full Frigate NVR setup on Debian 12 (VM 101), including Docker install, UFW rules, docker-compose deployment of both Frigate and Bambuddy, Frigate config.yml, NAS storage integration, HA integration, and Intel iGPU passthrough for hardware-accelerated detection.

## Key Takeaways

- **Debian install:** hostname `frigate-nvr`, SSH only, no desktop, static IP 192.168.30.20 at install time
- **UFW rules:** must explicitly open ports 8971 (Frigate 0.14+), 8554 (RTSP), 8000 (Bambuddy), 22 (SSH from VLAN 10)
- **Frigate port:** 8971 for Frigate 0.14+; 5000 for earlier versions — check version after deploy
- **docker-compose.yml:** single source of truth is `configs/frigate/docker-compose.yml` — do NOT hand-write it inline; copy from vault to avoid drift
- **MQTT in config.yml:** post-TLS uses port 8883 with `tls_ca_cert: /config/certs/ca-cert.pem`; initial setup can use 1883 for first test
- **Bambuddy:** runs in same compose file on port 8000 with `network_mode: host` — shares VM IP; `MQTT_PORT=8883` in env (NOT 1883)
- **`.env` file:** must set `FRIGATE_RTSP_PASSWORD`, `FRIGATE_MQTT_PASSWORD`, `BAMBU_PRINTER_IP`, `BAMBU_ACCESS_CODE`, `BAMBU_SERIAL` before `docker compose up`
- **NAS storage:** mount `/mnt/nas/frigate` via NFS after NAS is online, then swap volume in compose file
- **iGPU passthrough:** full guide in `igpu_passthrough_guide.md`; reduces CPU from ~70–90% to ~10–30% using VA-API + OpenVINO; `devices:` block pre-commented in compose file
- **Detect tracking:** all 4 cameras track `person` and `car`; cams 1+2 also track `cat` and `dog`
- **Recording retention:** 7 days motion, 14 days events/snapshots

## UFW Port Summary

| Port | Source | Purpose |
|---|---|---|
| 8971 | VLAN 20, VLAN 10 | Frigate web UI / API (0.14+) |
| 5000 | VLAN 20 | Frigate web UI / API (<0.14) |
| 8554 | VLAN 20 | RTSP restream |
| 8000 | VLAN 20, VLAN 10 | Bambuddy UI + API |
| 22 | VLAN 10 | SSH management |

## Entities Mentioned

[[entities/frigate]], [[entities/bambuddy]], [[entities/home-assistant]], [[entities/mosquitto-mqtt]], [[entities/raspberry-pi-nas]], [[entities/proxmox]]

## Concepts Mentioned

[[concepts/vlan-segmentation]], [[concepts/mqtt-tls]]

## Contradictions / Updates

Earlier docs said Frigate port 5000 — correct port for 0.14+ is 8971. Both UFW rules kept so guide works regardless of version.
