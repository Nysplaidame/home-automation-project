---
title: "Network Architecture Decision - Historical 9-VLAN Design"
category: source
tags: [network, vlan, security, architecture-decision]
created: 2026-04-07
updated: 2026-05-25
status: stable
---

# Source: Network Architecture Decision - Historical 9-VLAN Design

**Original file:** `main/docs/decisions/01-network-architecture.md`
**Date ingested:** 2026-04-07; refreshed after documentation consolidation on 2026-05-25
**Type:** architecture decision record

## Summary

Documents the historical 9-VLAN fully segmented network decision on the GL.iNet
GL-MT6000 running OpenWrt DSA. The design evolved from an initial 4-VLAN layout
and was later superseded by the printer VLAN decision, making the active design a
10-segment architecture. Router first-flight deployment is live; canonical
current state lives in project docs, not this historical source summary.

## Key Takeaways

- VLAN 50 isolates VentSys ESPHome devices from the internet.
- VLAN 30 isolates NVR/camera workloads from the internet.
- VLAN 35 now separates printers from simple IoT sensor boards.
- Proxmox is on VLAN 10, not VLAN 20.
- Tailscale is now the daily remote-access layer.
- WireGuard remains configured as a dormant fallback.

## VLAN Table

| VLAN | Name | Subnet | Internet | Purpose |
|---|---|---|---|---|
| 1 | LAN | 192.168.1.0/24 | Full | Everyday users |
| 10 | Management | 192.168.10.0/24 | Full | Admin, Proxmox host |
| 20 | Automation | 192.168.20.0/24 | Limited | HA, docker-host |
| 30 | NVR | 192.168.30.0/24 | None | Cameras, Frigate |
| 35 | Printers | 192.168.35.0/24 | OTA only | Bambu P1S, Athena 2 |
| 40 | Storage | 192.168.40.0/24 | None | OMV NAS |
| 50 | IoT Sensors | 192.168.50.0/24 | None | VentSys ESP32, smart plugs |
| 60 | Monitoring | 192.168.60.0/24 | Limited | Monitoring stack |
| 70 | DMZ | 192.168.70.0/24 | Controlled | Fallback/public-service staging |
| 99 | Guest | 192.168.99.0/24 | Full | Visitor WiFi |

## Entities Mentioned

[[entities/gl-mt6000]], [[entities/proxmox]], [[entities/home-assistant]],
[[entities/frigate]], [[entities/docker-host]], [[entities/ventsys]],
[[entities/openmediavault-nas]]

## Concepts Mentioned

[[concepts/vlan-segmentation]], [[concepts/tailscale-remote-access]],
[[concepts/wireguard-vpn]]

## Contradictions / Updates

Older dashboard and prompt-era files referred to 4-VLAN or 9-VLAN planning
states. Current canonical design is 10 segments with VLAN 35 for printers,
Tailscale daily access, and WireGuard fallback.
