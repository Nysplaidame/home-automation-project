---
title: "OpenWrt DHCP Config"
category: source
tags: [openwrt, dhcp, dns, network, config]
created: 2026-04-07
updated: 2026-04-07
status: stable
---

# Source: OpenWrt DHCP Config

**Original file:** `configs/openwrt/dhcp-config.conf`
**Date ingested:** 2026-04-07
**Type:** configuration file

## Summary

Complete DHCP and DNS configuration for all 9 VLANs. Includes all static DHCP reservations for infrastructure devices and the full VentSys ESP32 fleet (17 boards + 8 smart plugs). Also defines local DNS entries for all devices under the `home.local` domain. Contains placeholder MACs throughout — all must be replaced at deployment time.

## Key Takeaways

- **Local domain:** `home.local`; DNS entries for all key devices (homeassistant.home.local, frigate.home.local, nas.home.local, proxmox.home.local, bambuddy.home.local, p1s.home.local, plus all VLAN gateway .home.local names)
- **DHCP lease times:** Guest 2h, IoT 6h, User/CCTV/Storage 12h, Management/Automation 24h
- **IoT DHCP pool:** 192.168.50.100–190 (91 addresses for dynamic, all static reservations in .21–.89)
- **Smart plugs at VLAN 50:** 8 total — .71 (FDM printer), .72 (SLA printer), .73 (UV-1), .74 (UV-2), .75 (wash/cure), .76 (ultrasonic), .77 (AMS-HT), .78 (eSUN dryer)
- **Raspberry Pi display units:** 2× on VLAN 1 at 192.168.1.201 (`rpi-display-1`) and 192.168.1.202 (`rpi-display-2`) — kiosk mode for HA dashboard
- **TP-Link AP** (TL-WA801N): DHCP reservation at 192.168.1.203 (`homeextender`)
- **Automation DHCP pool** starts at .110 (not .100) — IPs .101–.109 reserved for HA and future services
- **Bambu P1S:** 192.168.1.200 on VLAN 1 — stays on LAN so Bambu Studio on user laptop can reach it directly
- **Duplicate dnsmasq block removed** from config (would have caused conflicts)

## Complete Static Reservation Summary

| Device | IP | VLAN |
|---|---|---|
| Proxmox host | 192.168.10.10 | 10 |
| Home Assistant | 192.168.20.101 | 20 |
| Frigate NVR | 192.168.30.20 | 30 |
| OMV NAS | 192.168.40.50 | 40 |
| ventsys-main-fan | 192.168.50.21 | 50 |
| ventsys-booth-fan | 192.168.50.22 | 50 |
| enc-fdm-sensors | 192.168.50.31 | 50 |
| enc-sla-sensors | 192.168.50.32 | 50 |
| enc-booth-sensors | 192.168.50.33 | 50 |
| ventsys-garage-sensor | 192.168.50.34 | 50 |
| ventsys-fdm-airflow | 192.168.50.41 | 50 |
| ventsys-sla-airflow | 192.168.50.42 | 50 |
| ventsys-booth-airflow | 192.168.50.43 | 50 |
| ventsys-main-valve-1 | 192.168.50.51 | 50 |
| ventsys-main-valve-2 | 192.168.50.52 | 50 |
| ventsys-fdm-branch-valve | 192.168.50.53 | 50 |
| ventsys-sla-branch-valve | 192.168.50.54 | 50 |
| ventsys-fdm-print-valve | 192.168.50.55 | 50 |
| ventsys-sla-print-valve | 192.168.50.56 | 50 |
| ventsys-fdm-360-valve | 192.168.50.61 | 50 |
| ventsys-sla-360-valve | 192.168.50.62 | 50 |
| plug-fdm-printer | 192.168.50.71 | 50 |
| plug-sla-printer | 192.168.50.72 | 50 |
| ventsys-plug-uv-1 | 192.168.50.73 | 50 |
| ventsys-plug-uv-2 | 192.168.50.74 | 50 |
| plug-wash-cure | 192.168.50.75 | 50 |
| ventsys-plug-ultrasonic | 192.168.50.76 | 50 |
| plug-ams-ht | 192.168.50.77 | 50 |
| plug-esun-dryer | 192.168.50.78 | 50 |
| monitoring-vm | 192.168.60.10 | 60 |
| Bambu P1S | 192.168.1.200 | 1 |
| rpi-display-1 | 192.168.1.201 | 1 |
| rpi-display-2 | 192.168.1.202 | 1 |
| homeextender (AP) | 192.168.1.203 | 1 |

## Entities Mentioned

[[entities/gl-mt6000]], [[entities/home-assistant]], [[entities/frigate]], [[entities/proxmox]], [[entities/openmediavault-nas]], [[entities/ventsys]], [[entities/bambu-p1s]], [[entities/tplink-ap]], [[entities/monitoring-vm]]

## Concepts Mentioned

[[concepts/vlan-segmentation]]

## Contradictions / Updates

Smart plug count is 8 (not previously specified). Raspberry Pi display units (.201, .202) are new entities — not previously documented. DHCP config says 17 VentSys boards, matching the corrected count from the adoption guide.
