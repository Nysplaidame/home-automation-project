---
title: "MINISFORUM M1 Pro-125H"
category: entity
tags: [hardware, compute, proxmox, minipc, intel-core-ultra]
created: 2026-08-25
updated: 2026-08-25
sources: [project-readme, proxmox-setup-guide]
status: stable
---

# MINISFORUM M1 Pro-125H

**Type:** device - production virtualisation host
**Status:** Live
**Related:** [[entities/proxmox]], [[entities/home-assistant]],
[[entities/frigate]], [[entities/llm-host]], [[entities/monitoring-vm]],
[[entities/docker-host]]

## Overview

The production Proxmox host is a MINISFORUM M1 Pro-125H at
`192.168.10.10` on management VLAN 10. It replaces the superseded
[[entities/minix-neo-z350]] plan.

## Key Properties

- CPU: Intel Core Ultra 5 125H
- RAM: 32 GiB
- Storage: 1 TiB NVMe
- OS: Proxmox VE 9
- Network: VLAN-aware `vmbr0` over the tagged router `lan1` trunk
- Graphics: Intel Meteor Lake iGPU shared with unprivileged CT 111 and CT 114
  through `/dev/dri` device mappings; this is not exclusive PCI passthrough.

## Production Guests

| ID | Type | Name | Network | Status |
|---:|---|---|---|---|
| 100 | VM | home-assistant | `192.168.20.101` | Live |
| 102 | VM | monitoring | `192.168.60.10` | Live |
| 103 | VM | docker-host | `192.168.20.102` | Live |
| 111 | LXC | frigate-nvr | `192.168.30.20` | Live |
| 114 | LXC | llm-host | `192.168.20.104` | Live |
| 101 | VM | frigate-nvr | offline | Rollback only |
| 104 | VM | llm-host | offline | Rollback only |

## Change Log

- 2026-08-25: Page created from the reconciled production README, Proxmox
  guide, and current-live-state reference.
