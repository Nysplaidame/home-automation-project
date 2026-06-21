---
title: "Proxmox VE"
category: entity
tags: [software, proxmox, virtualisation, hypervisor]
created: 2026-04-07
updated: 2026-06-20
sources: [project-readme, proxmox-setup-guide]
status: stable
---

# Proxmox VE

**Type:** integration - hypervisor / virtualisation platform
**Status:** Live - MINIX NEO Z350, Proxmox VE 9.1.9
**Related:** [[entities/minix-neo-z350]], [[entities/home-assistant]], [[entities/frigate]], [[entities/monitoring-vm]], [[entities/docker-host]], [[entities/openmediavault-nas]]

## Overview

Proxmox VE runs bare-metal on the MINIX NEO Z350. It hosts the project VMs via a
VLAN-aware bridge (`vmbr0`). The Proxmox host itself sits on VLAN 10
(Management) at `192.168.10.10`.

## Guests

| VM ID | Name | VLAN | IP | Status |
|---|---|---|---|---|
| 100 | home-assistant | 20 | 192.168.20.101 | Running |
| 101 | frigate-nvr | - | - | Stopped rollback VM |
| 102 | monitoring | 60 | 192.168.60.10 | Running, Grafana/Influx/Kuma/Telegraf live |
| 103 | docker-host | 20 | 192.168.20.102 | Running, docker-host services and metrics live |
| 104 | llm-host | - | - | Stopped rollback VM |
| 111 | frigate-nvr (LXC) | 30 | 192.168.30.20 | Running, Frigate baseline live |
| 114 | llm-host (LXC) | 20 | 192.168.20.104 | Running, local AI/voice live |

## Backup

- Temporary local Proxmox backups are scheduled daily at 02:00 for VMs `100/101/102/103`, keep 2, until the NAS backup target is live.
- Longer-term direction: keep fast local MINIX recovery for VM/system backups.
- Move HA scheduled backups to [[entities/openmediavault-nas]] when available.
- Keep Frigate live recordings local first, then add OMV archiving/storage later.
- 2026-05-28 restore-readiness drill passed for latest VM `100/101/102/103` backups (`zstd -t` plus `Finished Backup` log checks).

## Metrics

- Native Proxmox metrics export writes to InfluxDB bucket `proxmox`.
- Grafana dashboard `Proxmox Resource Overview` includes host, VM, storage, docker-host, and container panels.
- 2026-05-31 datasource validation found high unlabeled VM percentage cards are
  guest-memory values (`mem / maxmem`), not CPU or disk saturation. Dashboard
  panels should label `CPU`, `Guest memory`, `Root disk`, or equivalent.
- `Proxmox Resource Overview` is exported to repo source and live dashboard
  version `6` has explicit labels for guest RAM, RAM pressure, and root disk.
- `NAS Resource Overview` is only a planned shell until the NAS is built.

## Open Questions

- [x] Share render/card DRM devices with unprivileged CT 111 and CT 114.
- [ ] Add OMV NAS as backup target once NAS hardware is purchased.
- [ ] Decide whether Frigate VM local snapshots should remain excluded once camera/video storage is active.

## Change Log

- 2026-06-20: Replaced production VM 101/104 identities with CT 111/114 and
  validated concurrent shared-iGPU use.

- 2026-05-30: Added backup drill status and Proxmox/Grafana metrics state.
- 2026-05-31: Clarified Proxmox dashboard percent values, exported the dashboard source, and applied metric labels live.
- 2026-05-23: Updated backup target direction from deprecated Pi NAS plan to OMV NAS.
- 2026-05-18: Added VM 102 monitoring as live and corrected backup schedule/current VM table.
- 2026-05-08: Major update - Proxmox live; VM table corrected for then-current state.
- 2026-04-07: Page created from project-wide ingest.
