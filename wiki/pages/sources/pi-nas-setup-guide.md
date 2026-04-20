---
title: "Pi NAS Setup Guide"
category: source
tags: [nas, raspberry-pi, nfs, samba, storage]
created: 2026-04-07
updated: 2026-04-07
status: stable
---

# Source: Pi NAS Setup Guide

**Original file:** `scripts/setup/nas/pi_nas_setup_guide.md`
**Date ingested:** 2026-04-07
**Type:** setup guide

## Summary

6-phase guide for deploying the Raspberry Pi 4 as a NAS on VLAN 40. Covers OS flash (Pi OS Lite 64-bit), static IP, UFW hardening, storage formatting, NFS exports for Frigate and HA, optional Samba for Windows access, HA backup integration, and SMART monitoring.

## Key Takeaways

- **Boot from USB SSD** (not microSD) — SD cards fail under continuous NAS write loads; highly recommended
- **Imager settings:** hostname `pi-nas`, SSH key-based, no WiFi, locale Europe/London
- **Static IP:** `192.168.40.50/24`, gw `192.168.40.1` via nmcli
- **UFW rules:** allow only VLAN 10 (SSH), HA VM (SSH, NFS, Samba), Frigate VM (NFS, Samba) — deny everything else
- **NFS exports:** `/mnt/nas/frigate` → Frigate VM only; `/mnt/nas/ha-backups` → HA VM only; `/mnt/nas/configs` → Management + HA
- **NFS option `no_root_squash`** on Frigate and HA shares — needed for Docker to write recordings properly
- **HA backup:** daily at 03:00, keep 14 copies on NAS (more than local retention)
- **SMART monitoring:** weekly short test, monthly long test via crontab; disk usage alert at 85% threshold
- **Samba:** optional, only for Windows management access from VLAN 10; admin share and ha-backups share (read-only)

## NFS Export Reference

| Share path | Allowed client | Access | Use |
|---|---|---|---|
| `/mnt/nas/frigate` | 192.168.30.20 | rw, no_root_squash | Frigate recordings |
| `/mnt/nas/ha-backups` | 192.168.20.101 | rw, no_root_squash | HA daily backups |
| `/mnt/nas/configs` | 192.168.10.0/24, 192.168.20.101 | rw | Config backups |

## Entities Mentioned

[[entities/raspberry-pi-nas]], [[entities/frigate]], [[entities/home-assistant]]

## Concepts Mentioned

[[concepts/vlan-segmentation]]

## Contradictions / Updates

None — first detailed NAS guide ingested.
