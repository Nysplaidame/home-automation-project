---
title: "VentSys TLS Implementation Roadmap"
category: source
tags: [ventsys, tls, roadmap, implementation]
created: 2026-04-07
updated: 2026-04-07
status: stable
---

# Source: VentSys TLS Implementation Roadmap

**Original file:** `home-automation-safety/ventsys/integration-process/ventsys_implementation_roadmap.md`
**Date ingested:** 2026-04-07
**Type:** implementation roadmap

## Summary

6-phase, 9-week plan for migrating VentSys to MQTT TLS. Phases cover: network/CA foundation → MQTT TLS deployment → ESPHome device certificate provisioning → HA + Node-RED integration → certificate lifecycle automation → testing and documentation. Each phase includes validation criteria and key deliverables.

## Key Takeaways

- Phase 1 (Wks 1–2): OpenWrt NTP on VLAN 50 + local CA on HA
- Phase 2 (Wk 3): Mosquitto TLS on 8883, ACL for 3 device classes
- Phase 3 (Wks 4–5): Flash all ESPHome devices with TLS certs; add FDM + Booth valve controllers
- Phase 4 (Wk 6): Update HA MQTT integration, Node-RED flows
- Phase 5 (Wks 7–8): Automated certificate renewal via MQTT publish topics
- Phase 6 (Wk 9): Full system test, documentation
- Certificate CN must match ESPHome `device_name` exactly (= mDNS hostname) or TLS validation fails
- Additional hardware needed for Phase 3: 2× ESP32 DevKit + 2× servo motors (~£55–80 total)
- Success metric: <200ms added latency from TLS; zero internet dependency for any VentSys operation

## Entities Mentioned

[[entities/home-assistant]], [[entities/mosquitto-mqtt]], [[entities/ventsys]], [[entities/esphome]], [[entities/gl-mt6000]]

## Concepts Mentioned

[[concepts/mqtt-tls]], [[concepts/ventsys-architecture]]

## Contradictions / Updates

None — this is the current implementation plan.
