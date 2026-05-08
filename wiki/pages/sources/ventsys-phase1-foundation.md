---
title: "VentSys Phase 1 — Network & Security Foundation"
category: source
tags: [ventsys, tls, network, phase1, foundation]
created: 2026-04-07
updated: 2026-04-07
status: stable
---

# Source: VentSys Phase 1 — Network & Security Foundation

**Original file:** `scripts/setup/ventsys/ventsys_phase1_foundation.md`
**Date ingested:** 2026-04-07
**Type:** implementation guide (Weeks 1–3 detail)

## Summary

Detailed 3-week implementation guide for Phase 1 of VentSys TLS: network validation → certificate authority deployment → initial device TLS connectivity. More granular than the roadmap — each week has sub-tasks, code requirements, interdependencies, testing procedures, and success criteria.

## Key Takeaways

- **Week 1 focus:** validate existing network (VLANs 20+50 connectivity, HomeIoT WiFi assignment, internet isolation); create VentSys device registry; validate firewall rules; target <50ms latency VLAN 20↔VLAN 50
- **Week 2 focus:** deploy OpenWrt NTP (router serves VLAN 50 on UDP/123); create 10-year root CA on HA; configure Mosquitto TLS on 8883; create cert monitoring (alert 6 months before expiry)
- **Week 3 focus:** create `ventsys_base_tls.yaml` template; provision certs for first devices; test TLS connectivity; integrate HA MQTT with TLS
- **Device registry** in `/config/ventsys_device_registry.yaml` tracks MAC, IP, device type, cert expiry, MQTT user, topics — created in Week 1.2
- **Smart plug count:** DHCP config shows 8 plugs (.71–.78); Phase 1 doc references 17 ESP32 boards + 8 smart plugs = 25 total devices for cert provisioning
- **Network validation script** to be created: tests VLAN 50→VLAN 20 connectivity, DHCP assignment on HomeIoT, internet isolation — should be run first before any other VentSys work
- **Backup schedule:** daily at 2:00 AM; manual backup before any major config change

## Entities Mentioned

[[entities/home-assistant]], [[entities/ventsys]], [[entities/esphome]], [[entities/mosquitto-mqtt]], [[entities/gl-mt6000]]

## Concepts Mentioned

[[concepts/mqtt-tls]], [[concepts/ventsys-architecture]]

## Contradictions / Updates

Week 3.2 references 17 ESP32 boards (consistent with corrected count). Smart plug count (8) confirmed by DHCP config. This doc is consistent with `ventsys-technical-specs` and `ventsys-implementation-roadmap` — adds implementation detail, no conflicts.
