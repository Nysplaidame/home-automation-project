---
title: "VentSys TLS Technical Specifications"
category: source
tags: [ventsys, tls, mqtt, esphome, security]
created: 2026-04-07
updated: 2026-04-07
status: stable
---

# Source: VentSys TLS Technical Specifications

**Original file:** `home-automation-safety/ventsys/integration-process/ventsys_technical_specifications.md`
**Date ingested:** 2026-04-07
**Type:** technical specification

## Summary

Complete technical reference for migrating VentSys MQTT communications from plaintext (port 1883) to TLS-encrypted (port 8883) using a local Certificate Authority hosted on Home Assistant. Covers CA directory structure, Mosquitto TLS config, ACL rules per device class, ESPHome base TLS template, device-specific YAML for fan and valve controllers, certificate lifecycle management, and validation procedures.

## Key Takeaways

- Local CA lives at `/config/ssl/ca/` on HA; root CA is 10-year, device certs 3-year validity
- MQTT port 8883 TLS only; port 1883 explicitly blocked by firewall after migration
- Three MQTT user classes: `ventsys_controllers`, `ventsys_sensors`, `ventsys_nodered` (granular ACL)
- ESPHome devices embed the CA certificate at flash time — no internet dependency
- Canonical device names (corrected from earlier stale names): `ventsys-main-fan` (.21), `ventsys-sla-print-valve` (.56), `ventsys-fdm-print-valve` (.55), `ventsys-booth-sensor` (.33)
- TimeZone for ESPHome: `Europe/London` (project is UK-based)
- Node-RED and HA both updated to use TLS broker; certificate expiry monitoring via HA template sensors
- Total estimated implementation: 44–58 hours over 9 weeks

## Entities Mentioned

[[entities/home-assistant]], [[entities/mosquitto-mqtt]], [[entities/ventsys]], [[entities/esphome]]

## Concepts Mentioned

[[concepts/mqtt-tls]], [[concepts/ventsys-architecture]]

## Contradictions / Updates

Earlier docs used stale device names (`ventsys-fan-controller`, `ventsys-sla-valve`). Canonical names per `dhcp-config.conf` are as listed above. Any reference to `.83` or `.84` IP addresses for FDM/booth valves is outdated — correct IPs are `.55` and `.33` respectively.
