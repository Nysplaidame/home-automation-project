---
title: "Home Assistant (HAOS)"
category: entity
tags: [software, home-assistant, automation, mqtt, esphome]
created: 2026-04-07
updated: 2026-05-18
sources: [project-readme, ha-vm-setup-guide, ha-configuration-yaml]
status: stable
---

# Home Assistant (HAOS)

**Type:** integration — home automation platform
**Status:** ✅ Live — HAOS core 2026.5.0, Supervisor 2026.04.2
**Related:** [[entities/proxmox]], [[entities/mosquitto-mqtt]], [[entities/esphome]], [[entities/frigate]], [[entities/ventsys]], [[entities/bambuddy]], [[entities/monitoring-vm]]

## Overview

Home Assistant OS runs on Proxmox VM 100 at `192.168.20.101`. It is the central automation hub — brokering MQTT, hosting the ESPHome add-on, integrating Frigate CCTV, controlling VentSys, monitoring the Bambu P1S via Bambuddy, and exporting state history to InfluxDB on the monitoring VM.

Mosquitto TLS is live on port `8883`; port `1883` is still open as a staged bootstrap path for clients that have not moved to TLS yet. Bambuddy is already on TLS. `ventsys-main-valve-1` is still using plain MQTT on `1883` via a temporary source-specific firewall rule until its ESPHome config is migrated.

## Key Properties

- VM: Proxmox VM 100
- VLAN: 20 (Automation)
- Static IP: `192.168.20.101`
- HA Core: `2026.5.0`
- Supervisor: `2026.04.2`
- Port: 8123 (HTTP; HTTPS still pending)
- 2FA: enabled (TOTP)
- Terminal & SSH add-on: exposed on port 22
- InfluxDB export: `homeassistant` bucket on `192.168.60.10`

## Add-ons Installed

- **Mosquitto MQTT** — broker on ports `1883` (bootstrap) and `8883` (TLS live).
- **ESPHome** — compiles and manages ESP32 firmware.
- **Terminal & SSH** — command line access.
- **File Editor** — config file management.

## Live Config on HA

- `/config/configuration.yaml` — fresh HAOS default + `packages: !include_dir_named packages`; deprecated InfluxDB YAML connection/auth keys removed.
- `/config/packages/ventsys_ha_package.yaml` ✅ deployed.
- `/config/packages/ventsys_ha_scripts.yaml` ✅ deployed; mode scripts now use server-side stepped valve ramping via `script.ventsys_ramp_valve`.
- `/config/www/ventsys-dashboard.html` ✅ deployed.
- `/config/www/ventsys-config.js` ✅ live-only token/config file; do not commit.
- `/config/www/ventsys-card-wrapper.html` ✅ deployed for Lovelace iframe/card use.

## VentSys Entities

Key registered entities include:
`fan.inline_fan`, `fan.spray_booth_fan`, `number.fdm_valve`, `number.sla_valve`,
`number.main_duct_valve_1`, `sensor.fdm_temperature`, `sensor.sla_temperature`,
`binary_sensor.mqtt_broker_online`, and `input_boolean.ventsys_failsafe`.

`ventsys-main-valve-1` is live and controllable. Broad safety automations are staged but disabled with `initial_state: false`; do not enable them until the physical devices/sensors they depend on are present and tested.

## Known Good Backup

- Name: `post-ha-ventsys-staged-20260507-db-excluded`
- Slug: `5fdeaff7`
- File: `/backup/5fdeaff7.tar` (~80KB, database excluded)

## Packages NOT Yet Deployed

- `ventsys_ha_optional.yaml` — do not load until all sensor boards live.
- `bambuddy_p1s_package.yaml` — do not deploy until `<P1S_SERIAL>` is replaced and MQTT topics are confirmed.

## Pending

- Finish MQTT TLS migration for remaining clients, especially `ventsys-main-valve-1`; then remove the temporary plain-MQTT firewall rule.
- Frigate integration — pending camera hardware, Frigate `.env`, and Frigate start.
- HA HTTPS/reverse proxy path — needed before treating Grafana/Kuma embedding as stable.

## Troubleshooting Quick Reference

- UI not loading: `ping 192.168.20.101` then `nc -zv 192.168.20.101 8123`.
- Restart loops after config change: check YAML via `ha core check`.
- Long-Lived Token expired: regenerate at Settings → Profile → Security, then update live-only `/config/www/ventsys-config.js`.
- See [[sources/troubleshooting-reference]] for full diagnostics.

## Change Log

- 2026-05-18: Corrected MQTT status to mixed-mode with TLS live on 8883; added monitoring Influx export, external dashboard token config, card wrapper, and live valve-1 note.
- 2026-05-08: Major update — HA live at 2026.5.0; VentSys packages staged; backup slug recorded; MQTT still pre-TLS; 2FA enabled.
- 2026-04-07: Page created from project-wide ingest.
