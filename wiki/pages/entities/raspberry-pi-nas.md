---
title: "Raspberry Pi NAS"
category: entity
tags: [hardware, nas, raspberry-pi, storage, nfs]
created: 2026-04-07
updated: 2026-04-07
sources: [project-readme, hardware-bom, troubleshooting-reference]
status: stub
---

# Raspberry Pi NAS

**Type:** device — network-attached storage
**Status:** ⏳ Not yet purchased
**Related:** [[entities/frigate]], [[entities/home-assistant]], [[entities/proxmox]]

## Overview

Raspberry Pi 4 used as a NAS providing NFS shares for Frigate footage storage, HA backups, and general config backup via rsync. Lives on VLAN 40 (Storage — no internet access).

## Key Properties

- Hardware: Raspberry Pi 4 Model B, 8GB RAM
- Storage: 2× 4TB USB 3.0 HDD (RAID 1 for redundancy)
- Boot: 64GB Class 10 A2 microSD
- VLAN: 40 (Storage)
- Static IP: `192.168.40.50`
- Port connection: GL-MT6000 `lan4` (VLAN 40 untagged)

## NFS Exports

| Share | Consumer | Mount point |
|---|---|---|
| `/mnt/nas/frigate` | Frigate VM | `/mnt/nas/frigate` on VM 101 |
| `/mnt/nas/ha-backups` | Home Assistant | Network storage target |
| `/mnt/nas/configs` | General rsync | Config backup |

## Firewall Rules Required

- HA (VLAN 20) → NAS (VLAN 40) port 2049: ALLOW (NFS)
- Frigate (VLAN 30) → NAS (VLAN 40) ports 2049, 445: ALLOW

## Open Questions

- [ ] Purchase Pi 4 8GB + 2× 4TB HDDs + microSD + case
- [ ] Follow `scripts/setup/nas/pi_nas_setup_guide.md`
- [ ] Configure NFS exports and test mounts from both consumers
- [ ] Enable SMART monitoring on drives
- [ ] Add MAC to `dhcp-config.conf`

## Change Log

- 2026-04-07: Page created from project-wide ingest. Status: stub (hardware not purchased)
