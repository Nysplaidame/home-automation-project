---
title: "Mosquitto MQTT Broker"
category: entity
tags: [software, mqtt, mosquitto, broker, tls]
created: 2026-04-07
updated: 2026-05-18
sources: [project-readme, ventsys-technical-specs, ventsys-implementation-roadmap, troubleshooting-reference]
status: active
---

# Mosquitto MQTT Broker

**Type:** integration — MQTT message broker (HA add-on)
**Status:** ✅ Live — plaintext bootstrap on `1883` and TLS on `8883`
**Related:** [[entities/home-assistant]], [[entities/ventsys]], [[entities/esphome]], [[entities/frigate]], [[entities/bambuddy]], [[concepts/mqtt-tls]]

## Overview

Mosquitto runs as a Home Assistant add-on at `192.168.20.101`. It is the central message bus for VentSys ESP32 devices, Frigate, Bambuddy, and Home Assistant automations.

The broker is in a mixed migration state: TLS on port `8883` is live and verified, while port `1883` remains open as a staged bootstrap path. Bambuddy has migrated to `8883` with TLS. `ventsys-main-valve-1` still uses `1883` temporarily and depends on a live OpenWrt exception that is not yet reflected in the canonical firewall source.

## Ports

| Port | Status | Purpose |
|---|---|---|
| 1883 | Temporary bootstrap / legacy clients | Plain MQTT; keep only until remaining clients migrate |
| 8883 | ✅ Live | MQTT over TLS with local CA |

## Live Validations

- `192.168.20.101:1883` reachable as bootstrap MQTT.
- `192.168.20.101:8883` reachable; authenticated TLS publish/subscribe with `/ssl/ca.crt` verified.
- Bambuddy logs confirmed MQTT relay and smart-plug service connected to `192.168.20.101:8883`.
- Mosquitto logs confirmed Bambuddy negotiated TLSv1.3 from `192.168.20.102`.
- Retained `bambuddy/status` was verified over TLS on `8883`.

## User Accounts & ACL

The durable design uses named MQTT users/classes for HA, VentSys controllers, VentSys sensors, and orchestration. The current live bootstrap/migration path uses the project MQTT credential stored outside the repo; do not commit passwords or live tokens.

| User / class | Topics | Purpose |
|---|---|---|
| `mqtt` | live migration user | Current bootstrap/TLS migration credential |
| `ventsys_controllers` | `ventsys/fan/+`, `ventsys/+/valve/+`, `ventsys/devices/+/+` | Target class for fan + valve ESP32s |
| `ventsys_sensors` | Environmental sensor topics + `homeassistant/sensor/ventsys/+` | Target class for sensor ESP32s |
| `ventsys_nodered` | `ventsys/#`, `homeassistant/#` | Target class for orchestration if Node-RED is added |

## TLS Config

- CA cert: `/ssl/ca.crt` for HA-side validation/testing.
- Broker cert/key live under the Mosquitto add-on config path.
- TLS version: TLSv1.2 minimum by design; Bambuddy observed negotiating TLSv1.3.
- `require_certificate: false` by design — username/password + TLS, no client certificates.
- `allow_anonymous: false`.

## Troubleshooting

```bash
# Test broker connectivity (bootstrap/plain MQTT)
mosquitto_pub -h localhost -p 1883 -u mqtt -P <password> -t test -m hello

# Test broker connectivity (TLS)
mosquitto_pub -h 192.168.20.101 -p 8883 --cafile /ssl/ca.crt -u mqtt -P <password> -t test -m hello

# Subscribe to VentSys topics during bootstrap
mosquitto_sub -h localhost -p 1883 -u mqtt -P <password> -t 'ventsys/#' -v
```

- Broker not running: Settings → Add-ons → Mosquitto → Start.
- Auth failure: check credentials in Settings → Devices & Services → MQTT → Configure.
- TLS failure from ESPHome: confirm `mqtt_ca_cert` exists in both repo and HA-side ESPHome `secrets.yaml` before flashing TLS YAMLs.
- See [[sources/troubleshooting-reference]].

## Change Log

- 2026-05-18: Updated from planned/pre-TLS to live mixed-mode state: 8883 TLS verified, 1883 still open temporarily, Bambuddy migrated to TLS, valve-1 still on plain MQTT.
- 2026-04-07: Page created from project-wide ingest.
