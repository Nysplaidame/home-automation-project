---
title: "Proxmox VE"
category: entity
tags: [software, proxmox, virtualisation, hypervisor]
created: 2026-04-07
updated: 2026-04-07
sources: [project-readme, network-architecture-decision]
status: active
---

# Proxmox VE

**Type:** integration — hypervisor / virtualisation platform
**Status:** ✅ Documented / ⏳ Not yet installed
**Related:** [[entities/minix-neo-z350]], [[entities/home-assistant]], [[entities/frigate]]

## Overview

Proxmox VE runs bare-metal on the MINIX NEO Z350. It hosts all project VMs via a VLAN-aware bridge (`vmbr0`). The Proxmox host itself sits on VLAN 10 (Management) at 192.168.10.10, separate from its workload VMs.

## Key Properties

- Host IP: `192.168.10.10` (VLAN 10)
- Web UI: `https://192.168.10.10:8006`
- Bridge: `vmbr0` (VLAN-aware, trunk on `enp1s0`)
- IOMMU: `intel_iommu=on` required for iGPU passthrough to Frigate VM

## VMs

| VM ID | Purpose | VLAN tag | IP |
|---|---|---|---|
| 100 | HAOS (Home Assistant) | 20 | 192.168.20.101 |
| 101 | Frigate NVR + Bambuddy | 30 | 192.168.30.20 |

## Setup Files

- `configs/proxmox/vm-configs.conf` — expected `qm config` output for both VMs
- `configs/proxmox/vm-setup.sh` — shell script to create VMs 100 and 101
- `scripts/setup/proxmox/proxmox_setup_guide.md` — full setup guide

## Backup

- Daily backup scheduled at 02:00 for VMs 100 + 101
- Backup target: Pi NAS (NFS share)

## Open Questions

- [ ] Install Proxmox on MINIX, configure vmbr0 trunk
- [ ] Run `vm-setup.sh` to create both VMs
- [ ] Note MAC addresses of both VMs → update `dhcp-config.conf`
- [ ] Confirm `onboot: 1` and `startup: order=1` set on both VMs

## Change Log

- 2026-04-07: Page created from project-wide ingest
