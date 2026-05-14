---
title: "Proxmox VE"
category: entity
tags: [software, proxmox, virtualisation, hypervisor]
created: 2026-04-07
updated: 2026-05-08
sources: [project-readme, proxmox-setup-guide]
status: stable
---

# Proxmox VE

**Type:** integration — hypervisor / virtualisation platform
**Status:** ✅ Live — MINIX NEO Z350, Proxmox VE 9.1.9, kernel 7.0.0-3-pve
**Related:** [[entities/minix-neo-z350]], [[entities/home-assistant]], [[entities/frigate]]

## Overview

Proxmox VE runs bare-metal on the MINIX NEO Z350. It hosts all project VMs via a VLAN-aware bridge (`vmbr0`). The Proxmox host itself sits on VLAN 10 (Management) at 192.168.10.10. No-subscription repository configured; enterprise/Ceph repos disabled. SSH root login is key-only.

## Key Properties

- Host IP: `192.168.10.10` (VLAN 10)
- Web UI: `https://192.168.10.10:8006`
- PVE version: 9.1.9
- Kernel: `7.0.0-3-pve`
- Bridge: `vmbr0` (VLAN-aware, trunk on `enp86s0` toward lan1 of router)
- IOMMU: configured (`intel_iommu=on`) for iGPU passthrough

## VMs

| VM ID | Name | VLAN | IP | Status |
|---|---|---|---|---|
| 100 | home-assistant | 20 | 192.168.20.101 | ✅ Running (HAOS 2026.5.0) |
| 101 | frigate-nvr | 30 | 192.168.30.20 | ✅ Running (Debian 13, Frigate staged) |
| 103 | docker-host | 20 | 192.168.20.102 | ✅ Running (Debian 13, Bambuddy live) |

Note: VM 102 (monitoring) was planned but never created. Docker-host was created as VM 103 instead.

## VM Config Highlights

**VM 100 (home-assistant):** HAOS, q35, OVMF. `onboot: 1`, startup order 1.

**VM 101 (frigate-nvr):** Debian 13 genericcloud. 64 GiB SCSI. MAC `BC:24:11:9C:25:87`. `onboot: 1`, startup order 2. Docker + Frigate image pulled; Frigate not yet started (needs `.env`, camera RTSP, MQTT TLS certs).

**VM 103 (docker-host):** Debian 13 genericcloud. 16 GiB SCSI. MAC `BC:24:11:BC:B8:1A`. `qemu-guest-agent` installed. `onboot: 1`, startup order 3. Runs Bambuddy as first Compose workload.

## Backup

- Known good HA backup: `post-ha-ventsys-staged-20260507-db-excluded` (slug `5fdeaff7`, ~80KB, at `/backup/5fdeaff7.tar`)
- Daily backup scheduled at 02:00 for VMs 100+101 (VM 103 to be added)
- Backup target: Pi NAS (NFS) — not yet connected (NAS hardware pending)
- Note: do NOT use local daily snapshots for VM 101 (Frigate video data fills SSD)

## Setup Files

- `configs/proxmox/vm-configs.conf` — expected `qm config` output for VMs 100, 101, 103
- `configs/proxmox/vm-setup.sh` — shell script to create VMs
- `scripts/setup/proxmox/proxmox_setup_guide.md` — full setup guide

## Open Questions

- [ ] Enable iGPU passthrough on VM 101 after confirming IOMMU groups
- [ ] Add VM 103 to daily backup schedule
- [ ] Add Pi NAS as backup target once NAS hardware purchased

## Change Log

- 2026-05-08: Major update — Proxmox live; VM table corrected (102 never created, 103 is docker-host); backup slug recorded; Frigate/Bambuddy staging status updated
- 2026-04-07: Page created from project-wide ingest
