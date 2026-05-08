---
title: "Frigate NVR"
category: entity
tags: [software, frigate, cctv, docker, nvr]
created: 2026-04-07
updated: 2026-04-07
sources: [project-readme, network-architecture-decision, troubleshooting-reference]
status: active
---

# Frigate NVR

**Type:** integration — network video recorder
**Status:** ✅ Documented / ⏳ VM not yet deployed
**Related:** [[entities/proxmox]], [[entities/home-assistant]], [[entities/bambuddy]], [[entities/mosquitto-mqtt]]

## Overview

Frigate NVR runs in Docker on Proxmox VM 101 (Debian 12). It processes RTSP streams from 4 PoE cameras on VLAN 30, records footage to NAS, and integrates with Home Assistant via Frigate integration card. Runs alongside [[entities/bambuddy]] on the same VM.

## Key Properties

- VM: Proxmox VM 101
- VLAN: 30 (CCTV)
- Static IP: `192.168.30.20`
- UI port: 8971 (Frigate 0.14+) — note older versions used port 5000
- Deploy path: `/opt/frigate/`
- Docker compose: `configs/frigate/docker-compose.yml`
- Config: `configs/frigate/config.yml`

## Camera Setup (planned)

- 4× PoE cameras at `192.168.30.21–24` (static DHCP)
- H.265, RTSP — model TBD
- RTSP URLs currently placeholder `/stream1` in config
- iGPU passthrough from MINIX for hardware decode (requires IOMMU on Proxmox)

## MQTT Integration

- Connects to Mosquitto at `192.168.20.101:8883` (TLS post-migration)
- Firewall rule: `Frigate MQTT to HA` already in `firewall-config.conf`

## NAS Storage

- Mounts Pi NAS at `/mnt/nas/frigate` via NFS
- Volume defined in `docker-compose.yml`

## Troubleshooting Quick Reference

- Camera grey/offline: `ffprobe rtsp://...` to test stream directly
- MQTT unreachable: `nc -zv 192.168.20.101 8883` from VM
- Container not starting: `docker compose logs frigate`
- See [[sources/troubleshooting-reference]]

## iGPU Passthrough (Phase 6 of setup)

Full guide: `scripts/setup/proxmox/igpu_passthrough_guide.md`
- PCI device: `00:02.0` (Intel Xe on i3-N350) — must be in own IOMMU group
- VM config: `qm set 101 --hostpci0 0000:00:02.0,pcie=1,x-vga=0` (x-vga=0 is critical)
- Drivers in VM: `intel-media-va-driver-non-free` + `intel-opencl-icd`
- docker-compose: uncomment `/dev/dri/renderD128` device + add `group_add:` with numeric video/render group IDs
- Frigate config: replace `cpu1` detector with `openvino` (device: GPU); add `hwaccel_args: preset-vaapi` to all cameras
- Expected result: CPU load drops from 60–90% → 10–30%

## Open Questions

- [ ] Select PoE camera models
- [ ] Fill in RTSP URLs in `configs/frigate/config.yml`
- [ ] Fill in MAC addresses in `dhcp-config.conf`
- [ ] Enable iGPU passthrough after confirming IOMMU

## Change Log

- 2026-04-07: Page created from project-wide ingest
