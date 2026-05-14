---
title: "Home Assistant (HAOS)"
category: entity
tags: [software, home-assistant, automation, mqtt, esphome]
created: 2026-04-07
updated: 2026-05-08
sources: [project-readme, ha-vm-setup-guide, ha-configuration-yaml]
status: stable
---

# Home Assistant (HAOS)

**Type:** integration — home automation platform
**Status:** ✅ Live — HAOS core 2026.5.0, Supervisor 2026.04.2
**Related:** [[entities/proxmox]], [[entities/mosquitto-mqtt]], [[entities/esphome]], [[entities/frigate]], [[entities/ventsys]], [[entities/bambuddy]]

## Overview

Home Assistant OS runs on Proxmox VM 100 at 192.168.20.101. It is the central automation hub — brokering MQTT, hosting the ESPHome add-on, integrating Frigate CCTV, controlling VentSys, and monitoring the Bambu P1S via Bambuddy. VentSys packages are staged and config-checked. MQTT is currently pre-TLS on port 1883.

## Key Properties

- VM: Proxmox VM 100
- VLAN: 20 (Automation)
- Static IP: `192.168.20.101`
- HA Core: `2026.5.0`
- Supervisor: `2026.04.2`
- Port: 8123 (HTTP, pre-TLS)
- 2FA: enabled (TOTP)
- Terminal & SSH add-on: exposed on port 22

## Add-ons Installed

- **Mosquitto MQTT** — broker on port 1883 (pre-TLS); 8883 after TLS migration
- **ESPHome** — compiles and manages all ESP32 firmware (hardware not yet purchased)
- **Terminal & SSH** — command line access
- **File Editor** — config file management

## Live Config on HA

- `/config/configuration.yaml` — fresh HAOS default + `packages: !include_dir_named packages`
- `/config/packages/ventsys_ha_package.yaml` ✅ deployed
- `/config/packages/ventsys_ha_scripts.yaml` ✅ deployed
- `/config/www/ventsys-dashboard.html` ✅ deployed, Long-Lived Token inserted

## VentSys Entities (staged, hardware pending)

Key registered entities:
`fan.inline_fan`, `fan.spray_booth_fan`, `number.fdm_valve`, `number.sla_valve`,
`number.main_duct_valve_1`, `sensor.fdm_temperature`, `sensor.sla_temperature`,
`binary_sensor.mqtt_broker_online`, `input_boolean.ventsys_failsafe`

Broad automations are staged but disabled with `initial_state: false` — do not enable until physical devices/sensors are live.

## Known Good Backup

- Name: `post-ha-ventsys-staged-20260507-db-excluded`
- Slug: `5fdeaff7`
- File: `/backup/5fdeaff7.tar` (~80KB, database excluded)

## Packages NOT Yet Deployed

- `ventsys_ha_optional.yaml` — do not load until all sensor boards live
- `bambuddy_p1s_package.yaml` — do not deploy until `<P1S_SERIAL>` replaced and MQTT topics confirmed

## Pending (blocking other work)

- MQTT TLS (8883) — see [[concepts/mqtt-tls]]; guide at `docs/procedures/ssl_tls_guide.md`
- Frigate integration — pending camera hardware and Frigate `.env`
- HA HTTPS — pending SSL/TLS setup

## Troubleshooting Quick Reference

- UI not loading: `ping 192.168.20.101` then `nc -zv 192.168.20.101 8123`
- Restart loops after config change: check YAML via `ha core check`
- Long-Lived Token expired: regenerate at Settings → Profile → Security
- See [[sources/troubleshooting-reference]] for full diagnostics

## Change Log

- 2026-05-08: Major update — HA live at 2026.5.0; VentSys packages staged; backup slug recorded; MQTT still pre-TLS; 2FA enabled
- 2026-04-07: Page created from project-wide ingest
