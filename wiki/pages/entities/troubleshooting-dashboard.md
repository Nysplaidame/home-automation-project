---
title: "Troubleshooting Dashboard"
category: entity
tags: [software, troubleshooting, dashboard, docker-host, diagnostics]
created: 2026-08-25
updated: 2026-09-11
sources: [project-readme, project-todo, troubleshooting-reference]
status: active
---

# Troubleshooting Dashboard

**Type:** service - read-only diagnostic guide
**Status:** Live with owner-approved Homepage preview; Proxmox evidence acceptance open
**Related:** [[entities/docker-host]], [[entities/proxmox]],
[[entities/monitoring-vm]], [[entities/homepage]]

## Overview

The Troubleshooting Dashboard provides 27 read-only routes across network/access,
hosts/storage, home/devices, monitoring/maintenance and applications/data.
Search and collapsible categories lead to ordered checks with execution hosts,
expected observations and failure interpretation. It imports health JSON locally;
manual route evidence remains explicit. It does not probe hosts, upload evidence,
execute commands or remediate faults. The original five walkthroughs and the
[[main/docs/troubleshooting/extended-app-routes|22 extended routes]] are available
offline when the dashboard host fails.

## Key Properties

- Host: [[entities/docker-host]] VM 103 at `192.168.20.102`.
- Homepage URL: `https://homepage.home.local/portal-preview/troubleshooting/`
  under Tools > Troubleshooting, with Preview and Open tab.
- Direct management URL: `http://192.168.20.102:8094/`.
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
- Owner approved the [[entities/homepage]] card on 2026-09-11; no new DNS alias.

## Open Questions

- [ ] Authorize an appropriate workstation key on [[entities/proxmox]] and
  accept a real Proxmox JSON snapshot for mount and backup-freshness evidence.
- [x] Owner-approved Homepage preview deployed on 2026-09-11.

## Change Log

- 2026-09-11: Expanded and deployed 27 searchable routes; 17 model tests and
  live desktop/mobile route checks passed. Offline guide generated from app
  definitions; no new live probes or remediation. Canonical app/handoff wins.

- 2026-08-25: Staged live on management-only port `8094`; Windows snapshot,
  desktop/mobile flow, access-denial checks and rollback proof passed.
