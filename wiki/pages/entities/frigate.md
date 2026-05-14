---
title: "Frigate NVR"
category: entity
tags: [software, frigate, cctv, docker, nvr]
created: 2026-04-07
updated: 2026-05-08
sources: [project-readme, frigate-vm-setup-guide, igpu-passthrough-guide]
status: active
---

# Frigate NVR

**Type:** integration — network video recorder
**Status:** ✅ VM live (Debian 13, Docker installed) / ⏳ Frigate not yet started
**Related:** [[entities/proxmox]], [[entities/home-assistant]], [[entities/mosquitto-mqtt]]

## Overview

Frigate NVR runs in Docker on Proxmox VM 101 (Debian 13). Frigate image is pulled and config is staged at `/opt/frigate/`. The container is not yet started — it is blocked on camera hardware, a finalised `.env` file, and MQTT TLS certs. Bambuddy has moved to VM 103 (docker-host) — it no longer runs on this VM.

## Key Properties

- VM: Proxmox VM 101 (`frigate-nvr`)
- VLAN: 30 (NVR)
- Static IP: `192.168.30.20`
- MAC: `BC:24:11:9C:25:87`
- OS: Debian 13, kernel `6.x`
- Docker: installed (official repo)
- Image pulled: `ghcr.io/blakeblackshear/frigate:stable`
- Config staged: `/opt/frigate/`
- NVR internet access: blocked by design (internet was temporarily unblocked for Docker/image install, now re-blocked)
- `apt-cacher-ng` proxy: `http://192.168.20.102:3142` (docker-host on VLAN 20, permanent firewall rule `Frigate to APT Cache`)

## Staging Gaps (before Frigate can start)

- [ ] Create `/opt/frigate/.env` with `FRIGATE_RTSP_PASSWORD` and `FRIGATE_MQTT_PASSWORD`
- [ ] Finalise MQTT TLS cert path for the config
- [ ] Confirm camera RTSP URLs (cameras not yet purchased)
- [ ] Run `docker compose up -d` from `/opt/frigate/`

## Camera Setup (planned)

- 4× PoE cameras at `192.168.30.21–24` (static DHCP reservations to be filled)
- H.265, RTSP — model TBD
- RTSP URLs currently placeholder `/stream1` in config
- iGPU passthrough from MINIX for hardware decode (IOMMU already configured)

## MQTT Integration

- Connects to Mosquitto at `192.168.20.101:1883` (pre-TLS); switch to 8883 after TLS
- Firewall rule: `Frigate MQTT to HA` in `firewall-config.conf`

## NAS Storage

- Will mount Pi NAS at `/mnt/nas/frigate` via NFS when NAS hardware purchased
- Note: do NOT use local daily Proxmox snapshots for VM 101 — video data will fill the SSD

## Config Files

- `configs/frigate/config.yml` — cameras, MQTT, retention, detector
- `configs/frigate/docker-compose.yml` — Frigate service, volumes, env vars

## iGPU Passthrough (Phase 6 of setup — deferred)

- Full guide: `scripts/setup/proxmox/igpu_passthrough_guide.md`
- PCI device: `00:02.0` (Intel Xe on i3-N350) — must be in own IOMMU group
- VM config: `x-vga=0` is critical
- Expected CPU reduction: 60–90% → 10–30%

## Troubleshooting Quick Reference

- Camera grey/offline: `ffprobe rtsp://...` to test stream directly
- MQTT unreachable: `nc -zv 192.168.20.101 1883` from VM (or 8883 post-TLS)
- Container not starting: `docker compose logs frigate`
- See [[sources/troubleshooting-reference]]

## Change Log

- 2026-05-08: Major update — VM 101 live on Debian 13; Frigate staged not started; Bambuddy moved to VM 103; apt-cache proxy noted; staging gaps listed
- 2026-04-07: Page created from project-wide ingest
