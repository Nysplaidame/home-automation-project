---
title: "Proxmox Monitoring VM (VM 102)"
category: entity
tags: [hardware, vm, proxmox, monitoring, grafana]
created: 2026-04-07
updated: 2026-04-07
sources: [proxmox-setup-guide]
status: stub
---

# Proxmox Monitoring VM (VM 102)

**Type:** device — virtual machine (future)
**Status:** ⏳ Documented in Proxmox guide / not yet created
**Related:** [[entities/proxmox]], [[entities/minix-neo-z350]]

## Overview

VM 102 is a planned monitoring VM on VLAN 60 for future Grafana/Zabbix deployment. Appears in the Proxmox VM reference table but is not yet in the active deployment plan. Lower priority than VMs 100 and 101.

## Key Properties

- VM ID: 102
- Name: monitoring
- VLAN: 60 (Monitoring)
- IP: 192.168.60.10
- RAM: 2048 MB
- Cores: 2
- Boot order: 3

## Open Questions

- [ ] When is this VM needed? Not in TO-DO.md — confirm priority
- [ ] What monitoring stack: Grafana + Prometheus? Zabbix?
- [ ] MAC address → add to dhcp-config.conf when created

## Change Log

- 2026-04-07: Page created — stub. Discovered in proxmox_setup_guide.md VM reference table; not previously documented.
