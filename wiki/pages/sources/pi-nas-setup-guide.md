---
title: "Pi NAS Setup Guide (Superseded)"
category: source
tags: [nas, raspberry-pi, nfs, samba, storage]
created: 2026-04-07
updated: 2026-04-07
status: stable
---

# Source: Pi NAS Setup Guide (Superseded)

**Original file:** `scripts/setup/nas/pi_nas_setup_guide.md`
**Date ingested:** 2026-04-07
**Type:** setup guide

## Summary

Superseded historical guide for deploying a Raspberry Pi as a NAS on VLAN 40.
The active project direction is now [[entities/openmediavault-nas]] using
`main/scripts/setup/nas/omv_nas_setup_guide.md`.

## Key Takeaways

- **Status:** superseded by OMV NAS direction
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

[[entities/openmediavault-nas]], [[entities/frigate]], [[entities/home-assistant]]

## Concepts Mentioned

[[concepts/vlan-segmentation]]

## Contradictions / Updates

Superseded by the OMV NAS plan selected on 2026-05-23.
