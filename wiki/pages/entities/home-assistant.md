---
title: "Home Assistant (HAOS)"
category: entity
tags: [software, home-assistant, automation, mqtt, esphome]
created: 2026-04-07
updated: 2026-04-07
sources: [project-readme, network-architecture-decision, troubleshooting-reference, ventsys-technical-specs]
status: stable
---

# Home Assistant (HAOS)

**Type:** integration — home automation platform
**Status:** ✅ Documented / ⏳ VM not yet deployed
**Related:** [[entities/proxmox]], [[entities/mosquitto-mqtt]], [[entities/esphome]], [[entities/frigate]], [[entities/ventsys]], [[entities/bambuddy]]

## Overview

Home Assistant Operating System (HAOS) runs on Proxmox VM 100. It is the central automation hub — brokering MQTT, hosting ESPHome add-on, integrating Frigate CCTV, controlling VentSys, and publishing automations. Also hosts the local Certificate Authority for MQTT TLS.

## Key Properties

- VM: Proxmox VM 100
- VLAN: 20 (Automation)
- Static IP: `192.168.20.101`
- Port: 8123 (HTTP pre-TLS), future HTTPS via local CA or DuckDNS
- Dashboard: `ventilation_v9k.html` → deploy to `/config/www/ventsys-dashboard.html`

## Add-ons Installed

- **Mosquitto MQTT** — broker on ports 1883 (pre-TLS) / 8883 (TLS)
- **ESPHome** — compiles and manages all ESP32 firmware
- **File Editor** — config file management
- **Terminal & SSH** — command line access for CA operations

## Key Config Files (on HA)

- `/config/configuration.yaml` — core config, packages directive
- `/config/automations.yaml` — fire safety, temp, air quality, watchdog
- `/config/packages/ventsys_ha_package.yaml` — VentSys entities + automations
- `/config/packages/ventsys_ha_scripts.yaml` — 12 ventilation mode scripts
- `/config/packages/bambuddy_p1s_package.yaml` — Bambu Lab P1S MQTT entities
- `/config/www/ventsys-dashboard.html` — VentSys control dashboard

## Local CA (for MQTT TLS)

- Location: `/config/ssl/ca/`
- Root CA: 10-year validity
- Device certs: 3-year validity
- See [[concepts/mqtt-tls]] for full CA architecture

## Troubleshooting Quick Reference

- UI not loading: `ping 192.168.20.101` then `nc -zv 192.168.20.101 8123`
- Restart loops after config change: check YAML syntax via Proxmox VM console
- Long-Lived Token expired: regenerate at Settings → Profile → Security
- See [[sources/troubleshooting-reference]] for full diagnostics

## Open Questions

- [ ] Deploy VM 100, complete HAOS onboarding
- [ ] Set static IP via nmcli
- [ ] Generate Long-Lived Token for VentSys dashboard
- [ ] Enable 2FA (TOTP)

## Change Log

- 2026-04-07: Page created from project-wide ingest
