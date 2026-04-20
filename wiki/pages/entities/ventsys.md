---
title: "VentSys — Fire Safety Ventilation System"
category: entity
tags: [ventsys, esphome, mqtt, safety, ventilation, 3d-printing]
created: 2026-04-07
updated: 2026-04-07
sources: [project-readme, ventsys-technical-specs, ventsys-implementation-roadmap, troubleshooting-reference]
status: active
---

# VentSys — Fire Safety Ventilation System

**Type:** integration — custom fire safety ventilation subsystem
**Status:** ✅ Software complete / ⏳ Hardware not yet purchased
**Related:** [[entities/esphome]], [[entities/home-assistant]], [[entities/mosquitto-mqtt]], [[concepts/ventsys-architecture]], [[concepts/printairpipe]], [[concepts/mqtt-tls]]

## Overview

VentSys is a bespoke fire safety and ventilation system built around ESP32 microcontrollers, ESPHome firmware, and Home Assistant automations. It manages airflow across two 3D printer enclosures (FDM and SLA) and a spray booth using servo-controlled butterfly valves and an inline duct fan. Sensors monitor temperature, humidity, smoke, VOC, and differential pressure. Emergency power cutoff is handled via smart plugs.

## Physical Setup

- **Ducting:** PrintAirPipe 125mm with servo-controlled butterfly valves
- **Enclosures:** FDM printer, SLA printer, spray booth
- **Fan:** 1× inline duct fan (PWM-controlled via GPIO23)
- **Valves:** Multiple servo-driven butterfly valves per zone

## ESP32 Device Fleet (21 boards total)

> Full canonical table from `esphome_adoption_guide.md`. All YAMLs exist in `configs/esphome/`. None yet flashed (hardware pending). **Flash wrong YAML = wrong GPIO/MQTT topics; requires full USB re-flash to fix.**

| Role | device_name | IP | YAML |
|---|---|---|---|
| Main fan | ventsys-main-fan | 192.168.50.21 | ventsys_fan_controller.yaml |
| Booth fan | ventsys-booth-fan | 192.168.50.22 | ventsys_booth_fan.yaml |
| FDM sensor | enc-fdm-sensors | 192.168.50.31 | ventsys_fdm_sensor.yaml |
| SLA sensor | enc-sla-sensors | 192.168.50.32 | ventsys_sla_sensor.yaml |
| Booth sensor | enc-booth-sensors | 192.168.50.33 | ventsys_booth_sensor.yaml |
| Garage sensor | ventsys-garage-sensor | 192.168.50.34 | ventsys_garage_sensor.yaml |
| FDM airflow | ventsys-fdm-airflow | 192.168.50.41 | ventsys_fdm_airflow.yaml |
| SLA airflow | ventsys-sla-airflow | 192.168.50.42 | ventsys_sla_airflow.yaml |
| Booth airflow | ventsys-booth-airflow | 192.168.50.43 | ventsys_booth_airflow.yaml |
| Main valve 1 | ventsys-main-valve-1 | 192.168.50.51 | ventsys_main_valve1.yaml |
| Main valve 2 | ventsys-main-valve-2 | 192.168.50.52 | ventsys_main_valve2.yaml |
| FDM branch valve | ventsys-fdm-branch-valve | 192.168.50.53 | ventsys_fdm_branch_valve.yaml |
| SLA branch valve | ventsys-sla-branch-valve | 192.168.50.54 | ventsys_sla_branch_valve.yaml |
| FDM print valve | ventsys-fdm-print-valve | 192.168.50.55 | ventsys_fdm_print_valve.yaml |
| SLA print valve | ventsys-sla-print-valve | 192.168.50.56 | ventsys_sla_print_valve.yaml |
| FDM 360 intake | ventsys-fdm-360-valve | 192.168.50.61 | ventsys_fdm_360_valve.yaml |
| SLA 360 intake | ventsys-sla-360-valve | 192.168.50.62 | ventsys_sla_360_valve.yaml |
| UV plug 1 | ventsys-plug-uv-1 | 192.168.50.73 | ventsys_plug_uv1.yaml |
| UV plug 2 | ventsys-plug-uv-2 | 192.168.50.74 | ventsys_plug_uv2.yaml |
| Wash/cure plug | ventsys-plug-wash-cure | 192.168.50.75 | ventsys_plug_wash_cure.yaml |
| Ultrasonic plug | ventsys-plug-ultrasonic | 192.168.50.76 | ventsys_plug_ultrasonic.yaml |

## MQTT Architecture

- **Pre-TLS:** port 1883 (temporary)
- **Post-TLS:** port 8883 with local CA (see [[concepts/mqtt-tls]])
- **Topic structure:** `ventsys/<zone>/<sensor|control>/<type>`
- **User classes:** `ventsys_controllers`, `ventsys_sensors`, `ventsys_nodered`
- **WiFi:** HomeIoT SSID (VLAN 50, 2.4GHz, channel 6, WPA2)

## HA Integration Files

- `/config/packages/ventsys_ha_package.yaml` — entities + automations
- `/config/packages/ventsys_ha_scripts.yaml` — 12 ventilation mode scripts
- `/config/www/ventsys-dashboard.html` — `ventilation_v9k.html` control dashboard

## Safety Notes

- Software failsafe via `input_boolean.ventsys_failsafe` in HA
- ⚠️ Hardware failsafe relay recommended (normally-closed, keeps fan ON if ESP32 loses power)
- MQ sensors require 24–48h burn-in before calibration
- DS18B20 one-wire addresses must be discovered after first flash and added to YAML

## Open Questions

- [ ] Purchase ESP32 boards (4+ needed), BME680, DS18B20, MQ-135, MQ-2, SDP610 sensors
- [ ] Purchase MG90S servos and IRLZ44N MOSFET (or PWM fan controller board)
- [ ] 3D print PrintAirPipe components (PLA+ segments; PLA-HT for filter housings)
- [ ] Flash controllers via USB; adopt in ESPHome add-on
- [ ] Record DS18B20 addresses after first flash; update YAMLs
- [ ] Execute MQTT TLS migration (see [[concepts/mqtt-tls]])

## Change Log

- 2026-04-07: Page created; full device fleet, MQTT architecture, and safety notes from ingest
