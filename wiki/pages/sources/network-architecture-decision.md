---
title: "Network Architecture Decision — 9-VLAN Security Segmentation"
category: source
tags: [network, vlan, security, architecture-decision]
created: 2026-04-07
updated: 2026-04-07
status: stable
---

# Source: Network Architecture Decision — 9-VLAN Security Segmentation

**Original file:** `home-automation-safety/docs/decisions/01-network-architecture.md`
**Date ingested:** 2026-04-07
**Type:** architecture decision record

## Summary

Documents the decision to use a 9-VLAN fully segmented network on the GL.iNet GL-MT6000 (OpenWrt DSA). The design evolved from an initial 4-VLAN layout; a Sept 2025 firewall audit identified critical gaps (no user VLAN, no management VLAN, Frigate and Proxmox misplaced), driving a full revision. All OpenWrt configs were rewritten for the 9-VLAN architecture. Deployment is still pending as of March 2026.

## Key Takeaways

- VLAN 50 (IoT Sensors) has **no internet access** — safety-critical isolation for VentSys ESP32 devices
- VLAN 30 (CCTV) also has no internet access; Frigate resides here, not on VLAN 20
- Proxmox is on VLAN 10 (Management), not VLAN 20 — infrastructure separated from workloads
- WiFi-only VLANs (50 and 99): no physical port carries them untagged — prevents Layer 2 attacks
- WireGuard VPN on VLAN 70 (DMZ) provides secure remote access to HA
- lan1 carries a tagged trunk to Proxmox (VLANs 10/20/30/40/50/60/70)

## VLAN Table

| VLAN | Name | Subnet | Internet | Purpose |
|---|---|---|---|---|
| 1 | LAN | 192.168.1.0/24 | Full | Everyday users |
| 10 | Management | 192.168.10.0/24 | Full | Admin, Proxmox host |
| 20 | Automation | 192.168.20.0/24 | Limited | HA VM |
| 30 | CCTV | 192.168.30.0/24 | None | Cameras, Frigate |
| 40 | Storage | 192.168.40.0/24 | None | Pi NAS |
| 50 | IoT Sensors | 192.168.50.0/24 | None | VentSys ESP32, smart plugs |
| 60 | Monitoring | 192.168.60.0/24 | Limited | Future Grafana/Zabbix |
| 70 | DMZ | 192.168.70.0/24 | Controlled | WireGuard VPN |
| 99 | Guest | 192.168.99.0/24 | Full | Visitor WiFi only |

## Entities Mentioned

[[entities/gl-mt6000]], [[entities/proxmox]], [[entities/home-assistant]], [[entities/frigate]], [[entities/ventsys]], [[entities/raspberry-pi-nas]]

## Concepts Mentioned

[[concepts/vlan-segmentation]], [[concepts/wireguard-vpn]]

## Contradictions / Updates

Older dashboard (Sep 2025) still refers to 4-VLAN. Current canonical design is 9-VLAN (Mar 2026).
