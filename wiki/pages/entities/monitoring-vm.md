---
title: "Monitoring VM (planned)"
category: entity
tags: [software, monitoring, grafana, proxmox]
created: 2026-04-07
updated: 2026-05-08
sources: [proxmox-setup-guide]
status: stub
---

# Monitoring VM

**Type:** integration — observability stack
**Status:** ⏳ Planned / not yet created
**Related:** [[entities/proxmox]], [[entities/home-assistant]]

## Overview

A monitoring VM (Grafana / InfluxDB / Telegraf or Uptime Kuma) was planned for Proxmox on VLAN 60 at `192.168.60.10`. It has not been created. VM ID 102 was reserved for it, but the docker-host workload was created as VM 103 instead.

The monitoring roadmap is documented at `docs/procedures/monitoring_roadmap.md`. It is blocked on getting core infrastructure stable first.

## Key Properties (planned)

- VM ID: 102 (reserved but not created)
- VLAN: 60 (Monitoring)
- Planned IP: `192.168.60.10`
- Stack: Uptime Kuma → InfluxDB/Grafana/Telegraf (decision pending)

## Open Questions

- [ ] Decide on monitoring stack (Uptime Kuma vs Grafana/InfluxDB)
- [ ] Create VM 102 when ready
- [ ] Add Fail2ban to exposed services once centralized logging is live

## Change Log

- 2026-05-08: Clarified — VM 102 never created; docker-host is VM 103; monitoring still planned
- 2026-04-07: Page created as stub from proxmox-setup-guide ingest
