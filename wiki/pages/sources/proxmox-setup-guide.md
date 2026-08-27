---
title: "Proxmox Setup Guide"
category: source
tags: [proxmox, setup, hypervisor, vms, vlan]
created: 2026-04-07
updated: 2026-08-25
status: stable
---

# Source: Proxmox Setup Guide

**Original file:** `scripts/setup/proxmox/proxmox_setup_guide.md`
**Date ingested:** 2026-04-07
**Type:** setup guide

## Summary

Current production guide for Proxmox VE 9 on the MINISFORUM M1 Pro-125H. It
covers the VLAN-aware bridge, current VM/LXC build order, shared iGPU mapping,
rollback identities and links to the canonical guest/backup references.

## Key Takeaways

- Host: MINISFORUM M1 Pro-125H, 32 GiB RAM, 1 TiB NVMe.
- Running VMs: 100, 102 and 103; running unprivileged LXCs: 111 and 114.
- VM 101 and 104 are stopped rollback points and must not run alongside their
  same-address LXC replacements.
- CT 111 and CT 114 share the host Intel iGPU through `/dev/dri` mappings; this
  is not exclusive PCI passthrough and does not require `intel_iommu=on`.
- Backup configuration is delegated to the current backup strategy and OMV
  storage references.

## VM Reference Table

| ID | Name | VLAN | IP | RAM | Cores | Boot |
|---|---|---|---|---|---|---|
| 100 | home-assistant | 20 | 192.168.20.101 | 4096 MB | 2 | order 1 |
| 102 | monitoring | 60 | 192.168.60.10 | 2048 MB | 2 | order 3 |
| 103 | docker-host | 20 | 192.168.20.102 | 6144 MB | 2 | running |
| 111 | frigate-nvr (LXC) | 30 | 192.168.30.20 | see guest config | see guest config | running |
| 114 | llm-host (LXC) | 20 | 192.168.20.104 | see guest config | see guest config | running |

## Entities Mentioned

[[entities/proxmox]], [[entities/minisforum-m1-pro-125h]], [[entities/gl-mt6000]], [[entities/home-assistant]], [[entities/frigate]]

## Concepts Mentioned

[[concepts/vlan-segmentation]]

## Contradictions / Updates

The April ingest described the retired MINIX/VM 101 architecture. The source
guide and this summary now follow the live MINISFORUM plus shared-iGPU LXC design.
