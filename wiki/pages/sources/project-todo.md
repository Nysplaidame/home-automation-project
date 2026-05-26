---
title: "Project Task List"
category: source
tags: [tasks, implementation, phases, todo]
created: 2026-04-07
updated: 2026-04-07
status: stable
---

# Source: Project Task List

**Original file:** `home-automation-safety/TO-DO.md`
**Date ingested:** 2026-04-07
**Type:** task list (living document)

## Summary

Full implementation task list organised across 6 phases. As of March 2026, Phase 1 configs are complete but the router has not been deployed. Phases 2–6 are pending deployment of Phase 1. VentSys hardware (sensors, ESP32 boards, servos) not yet purchased. Cameras not yet selected.

## Key Takeaways

- **Immediate unblocked actions:** Deploy GL-MT6000 router → test network → install Proxmox → create VMs → deploy HA → deploy Frigate
- **Phase 3 (VentSys):** 17 ESP32 boards to flash and adopt in ESPHome; sensors still to be purchased
- **Phase 5 (CCTV):** Camera models TBD; RTSP URLs are placeholders
- **Phase 6 (Security):** MQTT TLS migration, HTTPS on HA, Fail2ban, WireGuard DDNS
- **Ongoing:** Monthly backup health check; update MAC addresses in DHCP config when hardware arrives
- ESPHome device YAMLs for all 17 boards exist in `configs/esphome/`; only flashing remains

## Entities Mentioned

[[entities/gl-mt6000]], [[entities/proxmox]], [[entities/home-assistant]], [[entities/frigate]], [[entities/bambuddy]], [[entities/ventsys]], [[entities/esphome]], [[entities/openmediavault-nas]]

## Concepts Mentioned

[[concepts/vlan-segmentation]], [[concepts/mqtt-tls]]

## Contradictions / Updates

None — this is the current canonical task list.
