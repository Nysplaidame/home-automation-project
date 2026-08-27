---
title: "Troubleshooting Dashboard"
category: entity
tags: [software, troubleshooting, dashboard, docker-host, diagnostics]
created: 2026-08-25
updated: 2026-08-25
sources: [project-readme, project-todo, troubleshooting-reference]
status: active
---

# Troubleshooting Dashboard

**Type:** service - read-only diagnostic guide
**Status:** Staged live - management-only acceptance path
**Related:** [[entities/docker-host]], [[entities/proxmox]],
[[entities/monitoring-vm]], [[entities/homepage]]

## Overview

The Troubleshooting Dashboard turns five visible symptoms into ordered,
architecture-aware evidence sequences: Homepage access, Home Assistant
availability, one camera path, P1S telemetry and backup freshness. It imports
health-check JSON locally in the browser and does not probe, upload evidence,
run commands, restart services, change firewalls or restore backups.

## Key Properties

- Host: [[entities/docker-host]] VM 103 at `192.168.20.102`.
- Staged URL: `http://192.168.20.102:8094/`.
- Stack path: `/opt/stacks/troubleshooting-dashboard/`.
- Docker network: explicit `10.240.32.0/24` bridge.
- Access: Management VLAN `192.168.10.0/24` only; LAN, Tailscale, monitoring
  and IPv6 are denied by live policy.
- Data sources: Windows `health_check.ps1 -Full -Json` and Proxmox-host
  `health_check.sh --json`.
- Missing or skipped evidence remains `Needs evidence`.

## Acceptance State

- Real Windows snapshot passed 13/13 checks and imported successfully.
- Desktop and mobile browser flows passed against the staged service.
- Container uses a read-only root filesystem, drops all capabilities before
  adding only Nginx's required identity capabilities, and enables
  `no-new-privileges`.
- Stop/start rollback removed the listener and network, failed closed, then
  recreated the service with the same access boundaries.
- No DNS alias or [[entities/homepage]] card is approved.

## Open Questions

- [ ] Authorize an appropriate workstation key on [[entities/proxmox]] and
  accept a real Proxmox JSON snapshot for mount and backup-freshness evidence.
- [ ] Decide separately whether DNS and Homepage exposure add enough value.

## Change Log

- 2026-08-25: Staged live on management-only port `8094`; Windows snapshot,
  desktop/mobile flow, access-denial checks and rollback proof passed.
