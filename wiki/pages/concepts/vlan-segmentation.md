---
title: "10-Segment Network Segmentation"
category: concept
tags: [network, vlan, security, openwrt, architecture]
created: 2026-04-07
updated: 2026-08-25
sources: [network-architecture-decision, project-readme, troubleshooting-reference]
status: stable
---

# 10-Segment Network Segmentation

## Definition

A network architecture that divides devices into 10 isolated Layer 2 broadcast
domains, each with its own subnet, firewall zone, and internet access policy.
Implemented on the [[entities/gl-mt6000]] using OpenWrt DSA.

## Relevance to This Project

The 10-segment design is the security foundation for the home automation system.
It keeps safety-critical IoT devices, NVR/cameras, printers, and storage
isolated while allowing only narrow, documented inter-VLAN paths.

## VLAN Reference Table

| VLAN | Name | Subnet | Internet | Key Devices |
|---|---|---|---|---|
| 1 | LAN | 192.168.1.0/24 | Full | Everyday users |
| 10 | Management | 192.168.10.0/24 | Full | [[entities/proxmox]], admin devices |
| 20 | Automation | 192.168.20.0/24 | Limited | [[entities/home-assistant]], [[entities/docker-host]] |
| 30 | NVR | 192.168.30.0/24 | None | [[entities/frigate]], cameras |
| 35 | Printers | 192.168.35.0/24 | OTA only | [[entities/bambu-p1s]], Athena 2 |
| 40 | Storage | 192.168.40.0/24 | None | [[entities/openmediavault-nas]] |
| 50 | IoT Sensors | 192.168.50.0/24 | None | [[entities/ventsys]] ESP32 fleet |
| 60 | Monitoring | 192.168.60.0/24 | Limited | Monitoring stack |
| 70 | DMZ | 192.168.70.0/24 | Controlled | Fallback/public-service staging |
| 99 | Guest | 192.168.99.0/24 | Full | Visitor WiFi |

## Key Design Decisions

- **Proxmox on VLAN 10, not 20:** infrastructure stays on the management plane.
- **Frigate on VLAN 30, not 20:** NVR belongs with cameras and has no default internet.
- **Printers on VLAN 35:** Bambu P1S and Athena 2 are multi-service devices, not simple IoT sensors.
- **Storage on VLAN 40:** OMV is storage-focused and not the Docker app platform.
- **Tailscale host routes:** admin paths use exactly the HA, Frigate, OMV and
  monitoring-host `/32` routes through docker-host; the OnePlus daily portal
  path instead uses fixed Homepage proxy ports.
- **WireGuard fallback:** kept dormant and split-tunnel, not the daily access layer.
- **CCTV switch access standard:** Zyxel port 1 is the router trunk, ports 2-7
  are untagged VLAN 30/PVID 30 PoE camera ports, and port 8 remains the VLAN 40
  NAS access port.

## Inter-VLAN Traffic Rules (Key)

- VLAN 50 -> VLAN 20 port 8883: VentSys MQTT TLS to HA
- VLAN 50 -> Router port 123: router-local NTP safety net
- VLAN 50 -> WAN: denied and logged
- VLAN 30 -> VLAN 20 port 8883: Frigate MQTT to HA
- VLAN 20 -> VLAN 30: HA pulls Frigate
- VLAN 20 -> VLAN 40: HA/Frigate/docker-host reach only required OMV services

## History

Started as a 4-VLAN design in September 2025. A firewall audit revised it to 9
VLANs, then the printer VLAN decision added VLAN 35, making the active
architecture 10 segments.

- 2026-08-25: Reconciled the live GS1900/OMV physical path and four-route plus
  fixed-proxy remote-access model.

## Sources

- [[sources/network-architecture-decision]]
- [[sources/project-readme]]
