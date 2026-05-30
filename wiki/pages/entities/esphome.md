---
title: "ESPHome"
category: entity
tags: [software, esphome, esp32, firmware, iot]
created: 2026-04-07
updated: 2026-05-30
sources: [project-readme, ventsys-technical-specs, troubleshooting-reference]
status: active
---

# ESPHome

**Type:** integration — ESP32 firmware platform and HA add-on
**Status:** ✅ Add-on installed / ⏳ VentSys hardware adoption pending revalidation
**Related:** [[entities/home-assistant]], [[entities/ventsys]], [[entities/mosquitto-mqtt]], [[concepts/mqtt-tls]]

## Overview

ESPHome compiles and manages firmware for VentSys ESP32 devices. It runs as a
Home Assistant add-on. VentSys devices use MQTT for telemetry/control, while the
native ESPHome API (port `6053`) remains active for HA adoption, logs, and OTA
updates.

The current planning baseline treats VentSys hardware/entities as unbuilt until
explicitly revalidated. Historical valve-1 work should be brought forward only
on the TLS path, not by reintroducing a plain-MQTT router exception.

## Device Adoption Flow

1. Flash device via USB using the device-specific YAML from `configs/esphome/`.
2. Device connects to HomeIoT WiFi (VLAN 50).
3. Adopt in ESPHome add-on / verify native API on port `6053`.
4. Verify MQTT topics with `mosquitto_sub -t 'ventsys/#' -v`.
5. For TLS devices, confirm `mqtt_ca_cert` exists in both repo and HA-side ESPHome `secrets.yaml` before compile/flash.

## Key Config Locations

- Individual device YAMLs: `configs/esphome/`.
- VentSys bundle: `ventsys/ventsys_bundle_updated/`.
- HA-side secrets: `/config/esphome/secrets.yaml` (live, contains secrets; do not commit).
- Repo secrets template/source: `configs/esphome/secrets.yaml` (must not contain live-only untracked secret material beyond intended placeholders/managed values).

## Important Config Details

- Devices use static IPs on `192.168.50.x`.
- Gateway and DNS: `192.168.50.1` (GL-MT6000 VLAN 50 interface).
- NTP: `192.168.50.1` (OpenWrt local NTP — no internet).
- Timezone: `Europe/London`.
- OTA: enabled with safe mode and retry behavior.
- Logger: serial disabled (`baud_rate: 0`) in production configs.
- TLS-ready YAMLs require `mqtt_ca_cert` before deployment.

## Device Baseline

| Device | IP | MQTT | HA entity | Notes |
|---|---|---|---|---|
| `ventsys-main-valve-1` | `192.168.50.51` | target `192.168.20.101:8883` | `number.main_duct_valve_1` | Historical valve-1 state needs TLS-path revalidation before being treated as live |

## Troubleshooting

- Device offline in HA: `ping 192.168.50.x` → `nc -zv <ip> 6053`.
- Not publishing MQTT: check ESPHome logs for "MQTT connected".
- ESPHome dashboard shows offline despite live logs: restart ESPHome add-on to clear stale MQTT discovery cache.
- Re-flash needed: device won't adopt OTA — must USB flash again.
- See [[sources/troubleshooting-reference]].

## Change Log

- 2026-05-30: Synced planning baseline: VentSys hardware/entities are treated as unbuilt until revalidated, and remaining rollout should use MQTT TLS rather than plain `1883`.
- 2026-05-18: Updated for live `ventsys-main-valve-1`, mixed MQTT/TLS state, and `mqtt_ca_cert` blocker for remaining TLS-ready YAMLs.
- 2026-04-07: Page created from project-wide ingest.
