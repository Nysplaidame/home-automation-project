---
title: "ESPHome"
category: entity
tags: [software, esphome, esp32, firmware, iot]
created: 2026-04-07
updated: 2026-04-07
sources: [project-readme, ventsys-technical-specs, troubleshooting-reference]
status: active
---

# ESPHome

**Type:** integration — ESP32 firmware platform and HA add-on
**Status:** ✅ Add-on installed (on HA, once deployed) / ⏳ Devices not yet flashed
**Related:** [[entities/home-assistant]], [[entities/ventsys]], [[entities/mosquitto-mqtt]]

## Overview

ESPHome compiles and manages firmware for all 17 VentSys ESP32 boards. Runs as a Home Assistant add-on. Devices use MQTT (not the native ESPHome API) for all VentSys telemetry and control. The native API (port 6053) is still active for HA adoption and OTA updates.

## Device Adoption Flow

1. Flash device via USB using the device-specific YAML from `configs/esphome/`
2. Device connects to HomeIoT WiFi (VLAN 50)
3. Adopt in ESPHome add-on → assigns device to HA
4. Verify MQTT topics with `mosquitto_sub -t 'ventsys/#' -v`

## Key Config Locations

- Individual device YAMLs: `home-automation-safety/configs/esphome/`
- TLS-ready bundle: `home-automation-safety/ventsys/ventsys_bundle_updated/`
- Base TLS template: `ventsys_base_tls_config.yaml` (in bundle)

## Important Config Details

- All devices use static IPs on 192.168.50.x subnet
- Gateway and DNS: `192.168.50.1` (GL-MT6000 VLAN 50 interface)
- NTP: `192.168.50.1` (OpenWrt local NTP — no internet)
- Timezone: `Europe/London`
- OTA: enabled with safe mode and 5 retry attempts
- Logger: serial disabled (`baud_rate: 0`) in production configs

## Troubleshooting

- Device offline in HA: `ping 192.168.50.x` → `nc -zv <ip> 6053`
- Not publishing MQTT: check ESPHome logs for "MQTT connected"
- Re-flash needed: device won't adopt OTA — must USB flash again
- See [[sources/troubleshooting-reference]]

## Change Log

- 2026-04-07: Page created from project-wide ingest
