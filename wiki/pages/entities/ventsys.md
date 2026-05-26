---
title: "VentSys — Fire Safety Ventilation System"
category: entity
tags: [ventsys, esphome, mqtt, safety, ventilation, 3d-printing]
created: 2026-04-07
updated: 2026-05-18
sources: [project-readme, ventsys-technical-specs, ventsys-implementation-roadmap, troubleshooting-reference]
status: active
---

# VentSys — Fire Safety Ventilation System

**Type:** integration — custom fire safety ventilation subsystem
**Status:** ⏳ Partially live — HA/dashboard complete; `ventsys-main-valve-1` flashed and controllable; remaining hardware/device rollout pending
**Related:** [[entities/esphome]], [[entities/home-assistant]], [[entities/mosquitto-mqtt]], [[concepts/ventsys-architecture]], [[concepts/printairpipe]], [[concepts/mqtt-tls]]

## Overview

VentSys is a bespoke fire safety and ventilation system built around ESP32 microcontrollers, ESPHome firmware, MQTT, and Home Assistant automations. It manages airflow across two 3D printer enclosures (FDM and SLA) and a spray booth using servo-controlled butterfly valves and inline duct fans. Sensors monitor temperature, humidity, smoke, VOC, and differential pressure. Emergency power cutoff is handled via smart plugs.

The Home Assistant integration, dashboard, mode scripts, and package layer are deployed. `ventsys-main-valve-1` is flashed, online at `192.168.50.51`, and controllable from Home Assistant and the VentSys dashboard. Most physical VentSys devices remain pending.

## Physical Setup

- **Ducting:** PrintAirPipe 125mm with servo-controlled butterfly valves.
- **Enclosures:** FDM printer, SLA printer, spray booth.
- **Fan:** inline duct fan plus spray booth fan control in HA entities/scripts.
- **Valves:** multiple servo-driven butterfly valves per zone.
- **Live device:** main duct valve 1 (`ventsys-main-valve-1`).

## ESP32 Device Fleet (21 YAML/device entries)

> Full canonical table from `esphome_adoption_guide.md` and current handoff state. All YAMLs exist in `configs/esphome/`. `ventsys-main-valve-1` is live on the temporary pre-TLS path; the rest remain pending hardware/flash/adoption. **Flash wrong YAML = wrong GPIO/MQTT topics; requires full USB re-flash to fix.**

| Role | device_name | IP | YAML | State |
|---|---|---|---|---|
| Main fan | ventsys-main-fan | 192.168.50.21 | ventsys_fan_controller.yaml | pending |
| Booth fan | ventsys-booth-fan | 192.168.50.22 | ventsys_booth_fan.yaml | pending |
| FDM sensor | enc-fdm-sensors | 192.168.50.31 | ventsys_fdm_sensor.yaml | pending |
| SLA sensor | enc-sla-sensors | 192.168.50.32 | ventsys_sla_sensor.yaml | pending |
| Booth sensor | enc-booth-sensors | 192.168.50.33 | ventsys_booth_sensor.yaml | pending |
| Garage sensor | ventsys-garage-sensor | 192.168.50.34 | ventsys_garage_sensor.yaml | pending |
| FDM airflow | ventsys-fdm-airflow | 192.168.50.41 | ventsys_fdm_airflow.yaml | pending |
| SLA airflow | ventsys-sla-airflow | 192.168.50.42 | ventsys_sla_airflow.yaml | pending |
| Booth airflow | ventsys-booth-airflow | 192.168.50.43 | ventsys_booth_airflow.yaml | pending |
| Main valve 1 | ventsys-main-valve-1 | 192.168.50.51 | ventsys_main_valve1.yaml | ✅ live on 1883 temp path |
| Main valve 2 | ventsys-main-valve-2 | 192.168.50.52 | ventsys_main_valve2.yaml | pending |
| FDM branch valve | ventsys-fdm-branch-valve | 192.168.50.53 | ventsys_fdm_branch_valve.yaml | pending |
| SLA branch valve | ventsys-sla-branch-valve | 192.168.50.54 | ventsys_sla_branch_valve.yaml | pending |
| FDM print valve | ventsys-fdm-print-valve | 192.168.50.55 | ventsys_fdm_print_valve.yaml | pending |
| SLA print valve | ventsys-sla-print-valve | 192.168.50.56 | ventsys_sla_print_valve.yaml | pending |
| FDM 360 intake | ventsys-fdm-360-valve | 192.168.50.61 | ventsys_fdm_360_valve.yaml | pending |
| SLA 360 intake | ventsys-sla-360-valve | 192.168.50.62 | ventsys_sla_360_valve.yaml | pending |
| UV plug 1 | ventsys-plug-uv-1 | 192.168.50.73 | ventsys_plug_uv1.yaml | pending |
| UV plug 2 | ventsys-plug-uv-2 | 192.168.50.74 | ventsys_plug_uv2.yaml | pending |
| Wash/cure plug | ventsys-plug-wash-cure | 192.168.50.75 | ventsys_plug_wash_cure.yaml | pending |
| Ultrasonic plug | ventsys-plug-ultrasonic | 192.168.50.76 | ventsys_plug_ultrasonic.yaml | pending |

## Main Valve 1 Live Facts

- Device name: `ventsys-main-valve-1`.
- MAC: `EC:E3:34:B4:79:7C`.
- Static IP: `192.168.50.51` (VLAN 50 / HomeIoT).
- ESPHome API: port `6053` with noise encryption.
- OTA: port `3232`.
- MQTT broker: `192.168.20.101:1883` for now.
- Control topic: `ventsys/main/valve1/control`.
- State topic: `ventsys/main/valve1/state`.
- HA entity: `number.main_duct_valve_1`.

## MQTT Architecture

- **Current mixed state:** broker TLS on `8883` is live; `1883` remains open temporarily for `ventsys-main-valve-1` and other not-yet-migrated clients.
- **Required next migration:** add `mqtt_ca_cert` to repo and HA-side ESPHome `secrets.yaml`, move `ventsys_main_valve1.yaml` to `8883` with `certificate_authority`, OTA/flash it, then remove the temporary plain-MQTT firewall rule.
- **Topic structure:** `ventsys/<zone>/<sensor|control>/<type>`.
- **WiFi:** HomeIoT SSID (VLAN 50, 2.4GHz, channel 6, WPA2).

## HA Integration Files

- `/config/packages/ventsys_ha_package.yaml` — entities + automations.
- `/config/packages/ventsys_ha_scripts.yaml` — 12 mode scripts plus `script.ventsys_ramp_valve` helper; mode changes now ramp valves server-side.
- `/config/www/ventsys-dashboard.html` — live dashboard.
- `/config/www/ventsys-config.js` — live-only dashboard token/config; never commit.
- `/config/www/ventsys-card-wrapper.html` — iframe/card wrapper for HA UI embedding.

## Safety Notes

- Software failsafe via `input_boolean.ventsys_failsafe` in HA.
- Broad safety automations remain disabled until the physical sensors/devices they depend on are present and tested.
- ⚠️ Hardware failsafe relay recommended (normally-closed, keeps fan ON if ESP32 loses power).
- MQ sensors require 24–48h burn-in before calibration.
- DS18B20 one-wire addresses must be discovered after first flash and added to YAML.

## Open Questions

- [ ] Finish MQTT TLS migration for valve 1 and remove the live temporary 1883 firewall exception.
- [ ] Purchase/build/flash/adopt the remaining VentSys devices.
- [ ] Record DS18B20 addresses after first flash; update YAMLs.
- [ ] Deploy/verify HA card wrapper in a Lovelace iframe if not already stable.
- [ ] Stand up the garage Pi 4 kiosk once display hardware is ready.
- [ ] Consider `mode: restart` on mode scripts if rapid mode clicks cause valve ramp races.
- [ ] Harden dashboard page-init valve visuals so a future script reorder cannot publish `0` to valve topics on refresh.
- [ ] Revisit `restore_value` behavior for valve position entities so device restarts do not assume `0%` after physical movement.

## Change Log

- 2026-05-18: Updated for live main-valve-1, dashboard token externalization, HA-side ramp helper, mixed MQTT state, and current TLS migration blockers.
- 2026-04-07: Page created; full device fleet, MQTT architecture, and safety notes from ingest.
