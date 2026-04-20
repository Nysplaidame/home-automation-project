---
title: "9-VLAN Network Segmentation"
category: concept
tags: [network, vlan, security, openwrt, architecture]
created: 2026-04-07
updated: 2026-04-07
sources: [network-architecture-decision, project-readme, troubleshooting-reference]
status: stable
---

# 9-VLAN Network Segmentation

## Definition

A network architecture that divides devices into 9 isolated Layer 2 broadcast domains (VLANs), each with its own subnet, firewall zone, and internet access policy. Implemented on the [[entities/gl-mt6000]] using OpenWrt DSA.

## Relevance to This Project

The 9-VLAN design is the security foundation for the entire home automation system. It ensures that safety-critical IoT devices (VLAN 50) and CCTV equipment (VLAN 30) are completely isolated from the internet and from each other, while still allowing controlled inter-VLAN communication through Home Assistant as a bridge.

## VLAN Reference Table

| VLAN | Name | Subnet | Internet | Key Devices |
|---|---|---|---|---|
| 1 | LAN | 192.168.1.0/24 | Full | Everyday users, [[entities/bambu-p1s]] |
| 10 | Management | 192.168.10.0/24 | Full | [[entities/proxmox]] (192.168.10.10), admin devices |
| 20 | Automation | 192.168.20.0/24 | Limited | [[entities/home-assistant]] (192.168.20.101) |
| 30 | CCTV | 192.168.30.0/24 | None | [[entities/frigate]], [[entities/bambuddy]] (192.168.30.20) |
| 40 | Storage | 192.168.40.0/24 | None | [[entities/raspberry-pi-nas]] (192.168.40.50) |
| 50 | IoT Sensors | 192.168.50.0/24 | None | [[entities/ventsys]] ESP32 fleet |
| 60 | Monitoring | 192.168.60.0/24 | Limited | Future Grafana/Zabbix |
| 70 | DMZ | 192.168.70.0/24 | Controlled | [[concepts/wireguard-vpn]] endpoint |
| 99 | Guest | 192.168.99.0/24 | Full | WiFi-only visitor access |

## Key Design Decisions

- **Proxmox on VLAN 10, not 20:** Infrastructure separated from workloads. The hypervisor host should be on the management plane.
- **Frigate on VLAN 30, not 20:** CCTV belongs with cameras. No-internet posture is correct for NVR.
- **VLANs 50 and 99 WiFi-only:** No physical port carries them untagged — prevents Layer 2 attacks from wired access.
- **HA as inter-VLAN bridge:** IoT devices (VLAN 50) reach CCTV data (VLAN 30) only via HA's controlled integrations, not directly.

## Inter-VLAN Traffic Rules (key)

- VLAN 50 → VLAN 20 port 8883: ALLOW (VentSys MQTT TLS to HA)
- VLAN 50 → Router port 123: ALLOW (NTP — no internet needed)
- VLAN 50 → WAN: DENY + log
- VLAN 30 → VLAN 20 port 8883: ALLOW (Frigate MQTT to HA)
- VLAN 20 → VLAN 30: ALLOW (HA pulls Frigate)
- VLAN 20 → VLAN 40 port 2049: ALLOW (HA backup to NAS)

## History

Started as 4-VLAN design (Sep 2025). A firewall audit (Sep 24, 2025) identified: missing user VLAN, missing management VLAN, Frigate and Proxmox misplaced. Revised to 9-VLAN (Sep 25, 2025) and all OpenWrt configs rewritten.

## Sources

- [[sources/network-architecture-decision]]
- [[sources/project-readme]]
