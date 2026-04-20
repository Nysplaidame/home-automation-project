---
title: "MINIX NEO Z350-0dB"
category: entity
tags: [hardware, compute, proxmox, minipc]
created: 2026-04-07
updated: 2026-04-07
sources: [project-readme, hardware-bom]
status: stable
---

# MINIX NEO Z350-0dB

**Type:** device — compute hardware (Mini PC)
**Status:** ✅ Owned / ⏳ Proxmox not yet installed
**Related:** [[entities/proxmox]], [[entities/home-assistant]], [[entities/frigate]]

## Overview

Fanless Intel mini PC used as the Proxmox hypervisor host for the entire home automation stack. Runs all VMs (Home Assistant, Frigate, and future workloads) from a single silent device.

## Key Properties

- CPU: Intel i3-N350
- RAM: 16GB DDR4 (BOM lists 32GB — verify actual on receipt)
- Storage: 512GB M.2 PCIe Gen3 SSD
- Form factor: fanless / passively cooled
- OS: Proxmox VE (bare metal)
- Network: single NIC (`enp1s0`), connected to GL-MT6000 `lan1` as a VLAN trunk

## Network Assignment

- VLAN: 10 (Management)
- Static IP: `192.168.10.10`
- Bridge: `vmbr0` (VLAN-aware), tag trunk on `enp1s0`
- IOMMU: must be enabled (`intel_iommu=on`) for iGPU passthrough to Frigate VM

## VMs Hosted

| VM ID | Name | VLAN | IP |
|---|---|---|---|
| 100 | Home Assistant (HAOS) | 20 | 192.168.20.101 |
| 101 | Frigate NVR + Bambuddy | 30 | 192.168.30.20 |

## Open Questions

- [ ] Verify actual installed RAM (README says 16GB, BOM says 32GB)
- [ ] Confirm M.2 slot is PCIe Gen3 or Gen4

## Change Log

- 2026-04-07: Page created from README + BOM ingest
