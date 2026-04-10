---
title: "Bambuddy + P1S Setup Guide"
category: source
tags: [bambuddy, bambulab, p1s, setup, mqtt, ventsys]
created: 2026-04-07
updated: 2026-04-07
status: stable
---

# Source: Bambuddy + P1S Setup Guide

**Original file:** `scripts/setup/printers/bambuddy_p1s_setup_guide.md`
**Date ingested:** 2026-04-07
**Type:** setup guide

## Summary

9-phase integration guide for Bambuddy + Bambu Lab P1S. Covers printer prep (Developer Mode, LAN Only Mode, static IP), firewall rules, Docker deployment alongside Frigate, MQTT publishing to Mosquitto, HA API connection, VentSys automation linkage, bambuddy_p1s_package.yaml deployment, and notification setup.

## Key Takeaways

- **LAN Only Mode disables Bambu Cloud** — printer still works with Bambu Studio / OrcaSlicer locally
- **SSDP does not work across VLANs** — always add printer by IP manually in Bambuddy UI
- **MQTT port:** `MQTT_PORT=8883` in docker-compose env (not 1883); `Bambuddy MQTT to HA` firewall rule uses 8883
- **FTP port:** only port 21 (explicit FTPS) — port 990 was removed (FIX #34 in guide)
- **VentSys integration:** done via HA automations on `binary_sensor.p1s_printing`, NOT via Bambuddy "Smart Plug" entries — FIX #25; automations live in `automations.yaml` not in the package file
  - Print start → `script.ventsys_mode_fdm_print`
  - Print stop → `script.ventsys_mode_fdm_purge`
- **`<P1S_SERIAL>` placeholder** in `bambuddy_p1s_package.yaml` must be replaced before deploying
- **Bambuddy data dirs:** `/opt/frigate/bambuddy/{data,logs}` — not `db/` or `archive/` (FIX #4)
- **Three firewall rules required** (in `firewall-config.conf` Bambuddy section):
  1. `Bambuddy to P1S` — VLAN 30 → VLAN 1 port 8883 + 21
  2. `Bambuddy MQTT to HA` — VLAN 30 → VLAN 20 port 8883
  3. `Bambuddy to HA API` — VLAN 30 → VLAN 20 port 8123
- **Auto power off:** configure in Bambuddy via smart plug + cooldown temp 40°C
- **HA entities after package deploy:** 9 sensors + 1 binary sensor (p1s_printing)

## HA Entities Created by Package

- `sensor.p1s_print_progress` — percent complete
- `sensor.p1s_state` — IDLE / PRINTING / FAILED
- `sensor.p1s_bed_temperature`, `p1s_nozzle_temperature`, `p1s_chamber_temperature`
- `sensor.p1s_layer` — current/total
- `sensor.p1s_remaining_time` — minutes
- `sensor.p1s_current_print` — filename
- `binary_sensor.p1s_printing` — the key trigger for VentSys automations

## Entities Mentioned

[[entities/bambuddy]], [[entities/bambu-p1s]], [[entities/home-assistant]], [[entities/mosquitto-mqtt]], [[entities/ventsys]], [[entities/frigate]]

## Concepts Mentioned

[[concepts/ventsys-architecture]], [[concepts/mqtt-tls]]

## Contradictions / Updates

MQTT port is 8883 (not 1883) throughout — confirmed in docker-compose.yml and firewall rule. VentSys trigger mechanism is HA automations, not Bambuddy smart plug entries.
