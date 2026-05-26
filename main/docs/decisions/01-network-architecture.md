---
title: Network Architecture Decision - 9-VLAN Security Segmentation
description: Security-segmented network design isolating safety systems from internet
tags: [architecture-decision, network-security, vlan, firewall, safety-critical]
created: 2025-09-09
modified: 2026-05-25
type: decision
status: superseded
superseded_by: docs/decisions/02-printer-vlan-architecture.md
---

# Decision: 9-VLAN Security-Segmented Network Architecture

**Date:** 2025-09-09 (revised 2025-09-25)
**Status:** Superseded by `docs/decisions/02-printer-vlan-architecture.md`, which adds the dedicated printer VLAN 35 segment.
**Context:** Need secure network design isolating safety systems from internet while enabling remote access and normal user connectivity

## Problem Statement
Design a network architecture that:
- Completely isolates fire safety sensors (VLAN 50) from internet access
- Isolates CCTV system (VLAN 30) from internet access
- Provides a separate management plane for administrative access
- Enables secure remote access to Home Assistant; current daily access is superseded by Tailscale host routes with WireGuard fallback
- Supports normal everyday users on a dedicated LAN
- Provides DMZ and guest isolation for untrusted traffic
- Balances security with operational needs

## Decision
**Chosen Option:** 9-VLAN Full Segmentation Architecture (GL.iNet GL-MT6000 / OpenWrt DSA)

**Rationale:**
- Provides required security isolation for safety-critical systems
- Enables remote access through Home Assistant bridge
- Separates management plane (Proxmox, admin devices) from workloads
- Proper CCTV isolation (Frigate on VLAN 30, no internet)
- Normal users on dedicated LAN with full internet access
- Manageable complexity with clear security boundaries

## Network Design

| VLAN | Name | Subnet | Internet | Purpose |
|------|------|--------|----------|---------|
| 1 | LAN | 192.168.1.0/24 | Full | Everyday users — phones, laptops, tablets |
| 10 | Management | 192.168.10.0/24 | Full | Admin devices, Proxmox host |
| 20 | Automation | 192.168.20.0/24 | Limited (HA only) | Home Assistant VM, automation services |
| 30 | CCTV | 192.168.30.0/24 | None | Cameras, Frigate NVR VM |
| 40 | Storage | 192.168.40.0/24 | None | OMV NAS |
| 50 | IoT Sensors | 192.168.50.0/24 | None | Fire safety sensors, smart plugs — CRITICAL ISOLATION |
| 60 | Monitoring | 192.168.60.0/24 | Limited | Future monitoring VMs (Grafana, Zabbix) |
| 70 | DMZ | 192.168.70.0/24 | Controlled | VPN endpoints, public-facing services |
| 99 | Guest | 192.168.99.0/24 | Full | Visitor WiFi — internet only, fully isolated |

## Physical Port Assignment (GL-MT6000)

| Port | Assignment | VLAN |
|------|-----------|------|
| lan1 | Trunk → Proxmox | Tagged: 10,20,30,40,50,60,70 |
| lan2 | Management access | VLAN 10 untagged |
| lan3 | Camera POE switch | VLAN 30 untagged |
| lan4 | NAS direct | VLAN 40 untagged |
| WiFi (main SSIDs) | Users / IoT / Guest | VLANs 1 / 50 / 99 |

## Key IP Assignments (Static)

| Device | IP | VLAN |
|--------|-----|------|
| Proxmox Host | 192.168.10.10 | VLAN 10 — Management |
| Home Assistant VM | 192.168.20.101 | VLAN 20 — Automation |
| Frigate NVR VM | 192.168.30.20 | VLAN 30 — CCTV |
| OMV NAS | 192.168.40.50 | VLAN 40 — Storage |
| Smart Plugs (emergency) | 192.168.50.71–79 | VLAN 50 — IoT |

## Architecture Notes

### Why Proxmox is on VLAN 10 (not VLAN 20)
Proxmox is infrastructure, not a workload. Placing the hypervisor on the management VLAN separates the physical host from the VMs it runs. Admin devices connect directly to VLAN 10 via lan2.

### Why Frigate is on VLAN 30 (not VLAN 20)
Frigate is a CCTV system and should live alongside the cameras it processes, not on the automation VLAN. VLAN 30 has no internet access at all, which is the correct posture for a CCTV system. Home Assistant reaches Frigate via the HA→CCTV inter-VLAN firewall rule.

### Why VLAN 50 (IoT) has no wired ports
IoT/VentSys sensors connect via WiFi (HomeIoT SSID) only. No physical port carries VLAN 50 untagged traffic, preventing unauthorized wired access to the safety sensor network.

### Guest VLAN WiFi-only
VLAN 99 has no physical port assignments. WiFi-only access prevents Layer 2 attacks (ARP poisoning, VLAN hopping) from guest devices against internal infrastructure.

## Implementation Status

| Item | Status |
|------|--------|
| Architecture design | Superseded by `02-printer-vlan-architecture.md` |
| `configs/openwrt/vlan-config.conf` | Superseded by current 10-segment config |
| `configs/openwrt/firewall-config.conf` | Superseded by current 10-segment config |
| `configs/openwrt/dhcp-config.conf` | Superseded by current 10-segment config |
| `configs/openwrt/wireless-config.conf` | Superseded by current 10-segment config |
| Router VLANs deployed | First-flight deployed and smoke-tested on 2026-05-07 |
| Network isolation tested | Router-side validators pass; client port DHCP/DNS smoke tests pass |
| WireGuard fallback configured | ⏳ Pending |

## Related Documents

- **Configs:** `configs/openwrt/` — complete OpenWrt configuration files
- **Firewall Analysis:** [[docs/decisions/firewall_analysis_summary|Firewall Analysis Summary]] — Sept 24 analysis that drove the 4→9 VLAN revision
- **Implementation Guide:** `scripts/setup/router/` — phased 8-step deployment procedure
- **Current Rebuild Path:** [[docs/install/phases/01-router-openwrt|Router/OpenWrt phase]]

## History

This architecture began as a 4-VLAN design (VLANs 20/30/40/50) documented on 2025-09-09. On 2025-09-24, a detailed firewall analysis (`firewall_analysis_summary.md`) identified critical gaps: missing user network, missing management VLAN, Frigate misplaced on VLAN 20, Proxmox misplaced on VLAN 20, no DMZ or guest isolation. The architecture was revised to a 9-VLAN design on 2025-09-25 and all OpenWrt configs were rewritten accordingly. It was later superseded by the printer VLAN decision, which adds VLAN 35 and makes the active design a 10-segment architecture.

---
**Implementation Priority:** Critical (foundation for all other systems)
**Next Action:** Use the current rebuild path in [[docs/install/phases/01-router-openwrt|Router/OpenWrt phase]] and the active router-deploy toolkit.
