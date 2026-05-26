---
title: "OpenMediaVault NAS"
category: entity
tags: [storage, nas, omv, openmediavault, backups]
created: 2026-05-23
updated: 2026-05-23
sources: [project-readme, project-todo]
status: active
---

# OpenMediaVault NAS

**Type:** device/service - storage appliance
**Status:** Planned
**Related:** [[entities/home-assistant]], [[entities/frigate]], [[entities/docker-host]], [[concepts/tailscale-remote-access]], [[concepts/wireguard-vpn]]

## Overview

OpenMediaVault is the active NAS direction for the project. It will run at
`192.168.40.50` on VLAN 40 and provide storage shares for Home Assistant
backups, Frigate archive storage, Immich media, and configuration backups.

OMV is storage-focused. It is not the Docker app platform; app containers belong
on [[entities/docker-host]] under `/opt/stacks/<service>/`.

## Key Properties

- IP: `192.168.40.50`
- VLAN: 40 (Storage)
- DNS names: `omv-nas.home.local`, `omv.home.local`, `nas.home.local`
- Shares: `ha-backups`, `frigate`, `immich`, `configs`
- Access: HA, Frigate, docker-host/Immich, and Management only
- Remote access: host route `192.168.40.50/32` via Tailscale; WireGuard fallback also host-only

## Open Questions

- [ ] Select final NAS hardware.
- [ ] Create OMV service users and share permissions.
- [ ] Add SMART, disk usage, NFS, and backup-write monitoring.

## Change Log

- 2026-05-23: Page created after project selected OMV over the old Raspberry Pi NAS direction.
