---
title: "Project README — Home Automation Safety Vault"
category: source
tags: [project-overview, hardware, status, deployment]
created: 2026-04-07
updated: 2026-04-07
status: stable
---

# Source: Project README — Home Automation Safety Vault

**Original file:** `home-automation-safety/README.md`
**Date ingested:** 2026-04-07
**Type:** project overview doc

## Summary

Home automation system focused on fire safety and ventilation for 3D printing operations, layered with CCTV monitoring, a 9-VLAN secure network, Proxmox virtualisation, and AI integration. All configs and setup guides are written; physical deployment is partially pending (router not yet switched over, hardware procurement in progress as of March 2026).

## Key Takeaways

- Primary compute: [[entities/minix-neo-z350]] (i3-N350, 16GB RAM, 512GB SSD) — owned, ready
- Router: [[entities/gl-mt6000]] (OpenWrt, WiFi 6) — owned, not yet deployed
- [[entities/home-assistant]] runs on Proxmox VM 100 at 192.168.20.101
- [[entities/frigate]] + [[entities/bambuddy]] on Proxmox VM 101 at 192.168.30.20
- [[entities/ventsys]] is the fire safety ventilation subsystem for FDM + SLA 3D printing enclosures
- [[entities/raspberry-pi-nas]] (Pi 4) still needed — pending purchase
- 4× PoE cameras still TBD; RTSP URLs are placeholders in Frigate config
- Deployment sequence: Router → Proxmox → HA VM → Frigate VM → NAS → VentSys hardware → Cameras → VPN

## Entities Mentioned

[[entities/minix-neo-z350]], [[entities/gl-mt6000]], [[entities/home-assistant]], [[entities/proxmox]], [[entities/frigate]], [[entities/bambuddy]], [[entities/bambu-p1s]], [[entities/ventsys]], [[entities/raspberry-pi-nas]], [[entities/esphome]], [[entities/mosquitto-mqtt]]

## Concepts Mentioned

[[concepts/vlan-segmentation]], [[concepts/ventsys-architecture]], [[concepts/printairpipe]]

## Contradictions / Updates

Dashboard (Sep 2025) references 4-VLAN design; README (Mar 2026) confirms 9-VLAN design. The 9-VLAN design is current.
