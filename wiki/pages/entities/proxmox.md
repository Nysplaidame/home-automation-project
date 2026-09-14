---
title: "Proxmox VE"
category: entity
tags: [software, proxmox, virtualisation, hypervisor]
created: 2026-04-07
updated: 2026-08-25
sources: [project-readme, proxmox-setup-guide]
status: stable
---

# Proxmox VE

**Type:** integration - hypervisor / virtualisation platform
**Status:** Live - MINISFORUM M1 Pro-125H, Proxmox VE 9
**Related:** [[entities/minisforum-m1-pro-125h]], [[entities/home-assistant]], [[entities/frigate]], [[entities/monitoring-vm]], [[entities/docker-host]], [[entities/openmediavault-nas]]

## Overview

Proxmox VE runs bare-metal on the MINISFORUM M1 Pro-125H. It hosts the project guests via a
VLAN-aware bridge (`vmbr0`). The Proxmox host itself sits on VLAN 10
(Management) at `192.168.10.10`.

## Guests

| Guest ID | Name | VLAN | IP | Status |
|---|---|---|---|---|
| 100 | home-assistant | 20 | 192.168.20.101 | Running |
| 101 | frigate-nvr | - | - | Stopped rollback VM |
| 102 | monitoring | 60 | 192.168.60.10 | Running, Grafana/Influx/Kuma/Telegraf live |
| 103 | docker-host | 20 | 192.168.20.102 | Running, docker-host services and metrics live |
| 104 | llm-host | - | - | Stopped rollback VM |
| 111 | frigate-nvr (LXC) | 30 | 192.168.30.20 | Running, three-camera Frigate live |
| 114 | llm-host (LXC) | 20 | 192.168.20.104 | Running, local AI/voice live |

## Backup

- OMV `omv-backups` is the live Proxmox backup target.
- Daily/monthly retention keeps 7 daily and 6 monthly generations.
- VM 100/102/103 scheduled backups and manual CT 111/114 backup proofs have
  passed; CT jobs use host-local `/var/tmp` for temporary backup work.
- Frigate recordings use the separate OMV Frigate export bind-mounted from the
  Proxmox host into unprivileged CT 111.

## Metrics

- Native Proxmox metrics export writes to InfluxDB bucket `proxmox`.
- Grafana dashboard `Proxmox Resource Overview` includes host, VM, storage, docker-host, and container panels.
- 2026-05-31 datasource validation found high unlabeled VM percentage cards are
  guest-memory values (`mem / maxmem`), not CPU or disk saturation. Dashboard
  panels should label `CPU`, `Guest memory`, `Root disk`, or equivalent.
- `Proxmox Resource Overview` is exported to repo source and live dashboard
  version `6` has explicit labels for guest RAM, RAM pressure, and root disk.
- `NAS Resource Overview` and OMV/SMART monitoring are live.

## Open Questions

- [x] Share render/card DRM devices with unprivileged CT 111 and CT 114.
- [ ] Run the planned whole-system restore/resilience exercise under explicit
  stop/ask gates.

## Change Log

- 2026-06-20: Replaced production VM 101/104 identities with CT 111/114 and
  validated concurrent shared-iGPU use.
- 2026-08-25: Corrected production hardware, live OMV backup/recording state,
  and current guest architecture.

- 2026-05-30: Added backup drill status and Proxmox/Grafana metrics state.
- 2026-05-31: Clarified Proxmox dashboard percent values, exported the dashboard source, and applied metric labels live.
- 2026-05-23: Updated backup target direction from deprecated Pi NAS plan to OMV NAS.
- 2026-05-18: Added VM 102 monitoring as live and corrected backup schedule/current VM table.
- 2026-05-08: Major update - Proxmox live; VM table corrected for then-current state.
- 2026-04-07: Page created from project-wide ingest.
