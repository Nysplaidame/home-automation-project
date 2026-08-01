---
title: "OpenMediaVault NAS"
category: entity
tags: [storage, nas, omv, openmediavault, backups]
created: 2026-05-23
updated: 2026-08-01
sources: [project-readme, project-todo]
status: active
---

# OpenMediaVault NAS

**Type:** device/service - storage appliance
**Status:** Live on Storage VLAN 40
**Related:** [[entities/home-assistant]], [[entities/frigate]], [[entities/docker-host]], [[concepts/tailscale-remote-access]], [[concepts/wireguard-vpn]]

## Overview

OpenMediaVault is the project's live NAS at `192.168.40.50` on VLAN 40. It
provides storage shares for Home Assistant
backups, Frigate archive storage, Immich media, and configuration backups.

OMV is storage-focused. It is not the Docker app platform; app containers belong
on [[entities/docker-host]] under `/opt/stacks/<service>/`.

## Key Properties

- IP: `192.168.40.50`
- VLAN: 40 (Storage)
- DNS names: `omv-nas.home.local`, `omv.home.local`, `nas.home.local`
- Shares: `ha-backups`, `frigate`, `immich`, `configs`
- Dedicated `media` NFS export to docker-host with qBittorrent
  `incoming/incomplete`, `incoming/complete`, and separate manual quarantine
- Access: HA, Frigate, docker-host/Immich, and Management only
- Remote access: host route `192.168.40.50/32` via Tailscale; WireGuard fallback also host-only
- SMART: global 1,800-second polling; 5 C change and 55 C maximum alerts; all
  five physical disks monitored and `Good` at 33-44 C on 2026-07-29
- Vault backup: guarded dry-run helper exists for the `configs` share; no
  scheduled vault-backup task has been created
- Monitoring: Uptime Kuma web and NFS TCP `2049` checks are live, ntfy-enabled,
  and returned `Up` from VLAN 60 on 2026-07-29
- SMART heartbeat: aggregate `smartctl -H` service/timer and Kuma monitor 34 are
  installed but disabled/paused until VM 102's host firewall accepts the narrow
  OMV push path

## Open Questions

- [ ] Run the first approved vault copy and restore-to-temporary-folder proof
  before creating any schedule.
- [ ] Continue monthly SMART health checks.

## Change Log

- 2026-08-01: Recorded the live OMV-backed qBittorrent staging/quarantine
  boundary and successful isolated config restore from the docker-host backup.
- 2026-07-29: Added the live OMV web/NFS Kuma checks after deploying the narrow
  monitoring-VLAN firewall path.
- 2026-07-29: Synced live VLAN/DNS/storage state, verified SMART monitoring on all five disks, and recorded the dry-run-only vault backup helper.
- 2026-05-23: Page created after project selected OMV over the old Raspberry Pi NAS direction.
