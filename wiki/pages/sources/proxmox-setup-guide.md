---
title: "Proxmox Setup Guide"
category: source
tags: [proxmox, setup, hypervisor, vms, vlan]
created: 2026-04-07
updated: 2026-04-07
status: stable
---

# Source: Proxmox Setup Guide

**Original file:** `scripts/setup/proxmox/proxmox_setup_guide.md`
**Date ingested:** 2026-04-07
**Type:** setup guide

## Summary

Complete Proxmox VE setup guide for the MINIX NEO Z350. Uses a two-phase network approach: configure on the existing home network first (temporary IP 192.168.1.220), then cut over to the GL-MT6000 trunk after router VLANs are live. Covers host hardening, VLAN-aware bridge, VM creation for both VM 100 (HAOS) and VM 101 (Frigate/Debian), and backup configuration.

## Key Takeaways

- **Two-phase network:** `vmbr0.1` temporary IP (192.168.1.220) removed after router cutover; permanent IP is `vmbr0.10` at 192.168.10.10
- **HAOS image:** use `curl` to fetch the latest HAOS version tag from GitHub API — do NOT hardcode a version number (releases frequently)
- **VM creation:** use `configs/proxmox/vm-setup.sh` to create both VMs in one run (recommended over manual); creates 64GB disk for VM 101
- **VM 102:** monitoring VM (192.168.60.10, VLAN 60, 2GB RAM) documented — not in original README
- **Backup strategy:** DO NOT include VM 101 (Frigate) in daily local backups — video data makes snapshots huge and will fill the 512GB SSD. Use NAS for VM 101 once available. VM 100 (HA) is small enough for 3× local daily snapshots
- **IOMMU:** `intel_iommu=on iommu=pt` added to GRUB for iGPU passthrough to Frigate VM
- **Enterprise repo:** must be disabled and replaced with no-subscription repo before `apt update`
- **Subscription nag:** removed via sed patch on `proxmoxlib.js`; apt hook installed to reapply after upgrades automatically

## VM Reference Table

| ID | Name | VLAN | IP | RAM | Cores | Boot |
|---|---|---|---|---|---|---|
| 100 | home-assistant | 20 | 192.168.20.101 | 4096 MB | 2 | order 1 |
| 101 | frigate-nvr | 30 | 192.168.30.20 | 4096 MB | 2 | order 2 |
| 102 | monitoring | 60 | 192.168.60.10 | 2048 MB | 2 | order 3 |

## Entities Mentioned

[[entities/proxmox]], [[entities/minix-neo-z350]], [[entities/gl-mt6000]], [[entities/home-assistant]], [[entities/frigate]]

## Concepts Mentioned

[[concepts/vlan-segmentation]]

## Contradictions / Updates

VM 102 (monitoring) not previously documented in README or PROJECT-INDEX — new entity. Backup strategy note overrides the simple "daily backup for all VMs" described in TO-DO.
