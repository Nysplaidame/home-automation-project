---
title: "ESPHome Device Adoption Guide"
category: source
tags: [esphome, ventsys, esp32, adoption, mqtt, ota]
created: 2026-04-07
updated: 2026-04-07
status: stable
---

# Source: ESPHome Device Adoption Guide

**Original file:** `scripts/setup/ventsys/esphome_adoption_guide.md`
**Date ingested:** 2026-04-07
**Type:** setup guide

## Summary

5-phase guide for flashing and adopting all 21 VentSys ESPHome boards. Phases: USB first-flash → HA adoption → MQTT verification → OTA updates → TLS migration. Includes the canonical board-to-YAML mapping table (21 devices), secrets.yaml template, DS18B20 address discovery, BME680 I2C address verification, and VLAN 50 IP block allocation reference.

## Key Takeaways

- **21 boards total** (not 17 as previously documented — includes plugs and airflow sensors not in earlier count)
- **Board identification critical:** flashing wrong YAML installs wrong device name, MQTT topics, and GPIO pins — recovery requires full USB re-flash. Verify label before flashing.
- **Pre-TLS variants:** use `_pretls.yaml` configs for initial flash; switch to production YAML via OTA after TLS migration
- **secrets.yaml:** must be in both `ventsys/ventsys_bundle_updated/` AND `configs/esphome/` before flashing
- **DS18B20 address:** placeholder `0x0000000000000000` in YAML — must be replaced with real address from logs after first flash. Each board has a unique address.
- **BME680 I2C:** default `0x76`; check logs — if SDO pin is high it will be `0x77`; update YAML accordingly
- **ESPHome on Windows:** use pipx (`pipx install esphome`) or WSL — direct `pip install` has known path-length issues
- **MAC address collection:** after first flash, check router DHCP leases (`cat /tmp/dhcp.leases | grep 192.168.50`) — note MACs and update `dhcp-config.conf` static reservations
- **OTA port:** 3232 (ESPHome OTA), must be reachable from HA for wireless updates after adoption
- **`ventsys_ha_optional.yaml`:** has explicit "DO NOT LOAD YET" header — only deploy after all sensor boards are live and baro_pressure entities confirmed

## Canonical Device Fleet (21 boards)

| Board | YAML | device_name | IP |
|---|---|---|---|
| Main fan | ventsys_fan_controller.yaml | ventsys-main-fan | 192.168.50.21 |
| Booth fan | ventsys_booth_fan.yaml | ventsys-booth-fan | 192.168.50.22 |
| FDM sensor | ventsys_fdm_sensor.yaml | enc-fdm-sensors | 192.168.50.31 |
| SLA sensor | ventsys_sla_sensor.yaml | enc-sla-sensors | 192.168.50.32 |
| Booth sensor | ventsys_booth_sensor.yaml | enc-booth-sensors | 192.168.50.33 |
| Garage sensor | ventsys_garage_sensor.yaml | ventsys-garage-sensor | 192.168.50.34 |
| FDM airflow | ventsys_fdm_airflow.yaml | ventsys-fdm-airflow | 192.168.50.41 |
| SLA airflow | ventsys_sla_airflow.yaml | ventsys-sla-airflow | 192.168.50.42 |
| Booth airflow | ventsys_booth_airflow.yaml | ventsys-booth-airflow | 192.168.50.43 |
| Main valve 1 | ventsys_main_valve1.yaml | ventsys-main-valve-1 | 192.168.50.51 |
| Main valve 2 | ventsys_main_valve2.yaml | ventsys-main-valve-2 | 192.168.50.52 |
| FDM branch valve | ventsys_fdm_branch_valve.yaml | ventsys-fdm-branch-valve | 192.168.50.53 |
| SLA branch valve | ventsys_sla_branch_valve.yaml | ventsys-sla-branch-valve | 192.168.50.54 |
| FDM print valve | ventsys_fdm_print_valve.yaml | ventsys-fdm-print-valve | 192.168.50.55 |
| SLA print valve | ventsys_sla_print_valve.yaml | ventsys-sla-print-valve | 192.168.50.56 |
| FDM 360 intake | ventsys_fdm_360_valve.yaml | ventsys-fdm-360-valve | 192.168.50.61 |
| SLA 360 intake | ventsys_sla_360_valve.yaml | ventsys-sla-360-valve | 192.168.50.62 |
| UV plug 1 | ventsys_plug_uv1.yaml | ventsys-plug-uv-1 | 192.168.50.73 |
| UV plug 2 | ventsys_plug_uv2.yaml | ventsys-plug-uv-2 | 192.168.50.74 |
| Wash/cure plug | ventsys_plug_wash_cure.yaml | ventsys-plug-wash-cure | 192.168.50.75 |
| Ultrasonic plug | ventsys_plug_ultrasonic.yaml | ventsys-plug-ultrasonic | 192.168.50.76 |

## Entities Mentioned

[[entities/ventsys]], [[entities/esphome]], [[entities/home-assistant]], [[entities/mosquitto-mqtt]], [[entities/gl-mt6000]]

## Concepts Mentioned

[[concepts/ventsys-architecture]], [[concepts/mqtt-tls]]

## Contradictions / Updates

Previous wiki said 17 boards — **corrected to 21** (plugs at .73–.76 and additional airflow sensors at .41–.43 not previously counted). Also: garage sensor (.34) is new — not in earlier entity pages.
