---
title: "Home Assistant (HAOS)"
category: entity
tags: [software, home-assistant, automation, mqtt, esphome]
created: 2026-04-07
updated: 2026-06-20
sources: [project-readme, ha-vm-setup-guide, ha-configuration-yaml]
status: stable
---

# Home Assistant (HAOS)

**Type:** integration — home automation platform
**Status:** ✅ Live — HAOS core 2026.6.3
**Related:** [[entities/proxmox]], [[entities/mosquitto-mqtt]], [[entities/esphome]], [[entities/frigate]], [[entities/ventsys]], [[entities/bambuddy]], [[entities/monitoring-vm]]

## Overview

Home Assistant OS runs on Proxmox VM 100 at `192.168.20.101`. It is the
central automation hub: brokering MQTT, hosting the ESPHome add-on, staging
VentSys packages/dashboard assets, monitoring the Bambu P1S through Bambuddy
when printer details are available, and exporting state history to InfluxDB on
the monitoring VM. Frigate integration remains planned until cameras, RTSP
details, HTTPS, and audio requirements are ready.

Mosquitto TLS is live on port `8883`. Plain MQTT `1883` is deprecated and must
not be reintroduced through router policy for VentSys; the 2026-05-28 parity
check found no live/source valve-specific `1883` exception. Bambuddy is already
on TLS, and remaining Frigate/VentSys paths should use the TLS migration plan.

## Key Properties

- VM: Proxmox VM 100
- VLAN: 20 (Automation)
- Static IP: `192.168.20.101`
- HA Core: `2026.6.3`
- Supervisor: `2026.04.2`
- Port: 8123 (HTTP; HTTPS still pending)
- 2FA: enabled (TOTP)
- Terminal & SSH add-on: exposed on port 22
- InfluxDB export: `homeassistant` bucket on `192.168.60.10`

## Add-ons Installed

- **Mosquitto MQTT** — TLS broker on `8883`; plain `1883` is deprecated.
- **ESPHome** — compiles and manages ESP32 firmware.
- **Terminal & SSH** — command line access.
- **File Editor** — config file management.

Home and Overwatch Assist pipelines are live through [[entities/llm-host]].
Overwatch can perform bounded read-only SearXNG searches. It cannot currently
save recipes to Obsidian or Mealie.

## Live Config on HA

- `/config/configuration.yaml` — fresh HAOS default + `packages: !include_dir_named packages`; deprecated InfluxDB YAML connection/auth keys removed.
- `/config/packages/ventsys_ha_package.yaml` ✅ deployed.
- `/config/packages/ventsys_ha_scripts.yaml` ✅ deployed; mode scripts now use server-side stepped valve ramping via `script.ventsys_ramp_valve`.
- `/config/www/ventsys-dashboard.html` ✅ deployed.
- `/config/www/ventsys-config.js` ✅ live-only token/config file; do not commit.
- `/config/www/ventsys-card-wrapper.html` ✅ deployed for Lovelace iframe/card use.
- `/config/packages/monitoring_external_health_package.yaml` ✅ deployed for monitoring-stack external health visibility.

## VentSys Entities

VentSys packages and dashboard assets are written/staged, but hardware-dependent
entities must not be treated as globally live until ESPHome devices are built,
adopted, and explicitly revalidated. Broad safety automations remain staged;
do not enable them until the physical devices/sensors they depend on are
present and tested.

## Known Good Backup

- Name: `post-ha-ventsys-staged-20260507-db-excluded`
- Slug: `5fdeaff7`
- File: `/backup/5fdeaff7.tar` (~80KB, database excluded)

## Packages NOT Yet Deployed

- `ventsys_ha_optional.yaml` — do not load until all sensor boards live.
- `bambuddy_p1s_package.yaml` — do not deploy until `<P1S_SERIAL>` is replaced and MQTT topics are confirmed.

## Pending

- Finish MQTT TLS migration for remaining Frigate/VentSys clients without reintroducing broad or source-specific plain-MQTT router access.
- Frigate integration — pending camera hardware, Frigate `.env`, and Frigate start.
- HA HTTPS/reverse proxy path — needed before treating Grafana/Kuma embedding as stable.
- Apply `configs/home-assistant/lovelace/monitoring-grafana-links.yaml` to the storage-managed Monitoring dashboard through the HA UI.

## Troubleshooting Quick Reference

- UI not loading: `ping 192.168.20.101` then `nc -zv 192.168.20.101 8123`.
- Restart loops after config change: check YAML via `ha core check`.
- Long-Lived Token expired: regenerate at Settings → Profile → Security, then update live-only `/config/www/ventsys-config.js`.
- See [[sources/troubleshooting-reference]] for full diagnostics.

## Change Log

- 2026-06-20: Added live local LLM/Wyoming Assist and bounded SearXNG tool state;
  verified HA 2026.6.3 configuration.

- 2026-05-30: Corrected Frigate/VentSys/MQTT posture: Frigate integration remains planned, VentSys hardware entities are staged, and no valve-specific router `1883` exception should be treated as live.
- 2026-05-18: Corrected MQTT status to mixed-mode with TLS live on 8883; added monitoring Influx export, external dashboard token config, card wrapper, and live valve-1 note.
- 2026-05-08: Major update — HA live at 2026.5.0; VentSys packages staged; backup slug recorded; MQTT still pre-TLS; 2FA enabled.
- 2026-04-07: Page created from project-wide ingest.
