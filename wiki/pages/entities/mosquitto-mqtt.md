---
title: "Mosquitto MQTT Broker"
category: entity
tags: [software, mqtt, mosquitto, broker, tls]
created: 2026-04-07
updated: 2026-04-07
sources: [project-readme, ventsys-technical-specs, ventsys-implementation-roadmap, troubleshooting-reference]
status: active
---

# Mosquitto MQTT Broker

**Type:** integration — MQTT message broker (HA add-on)
**Status:** ✅ Documented / ⏳ Not yet deployed (runs on HA VM)
**Related:** [[entities/home-assistant]], [[entities/ventsys]], [[entities/esphome]], [[entities/frigate]], [[entities/bambuddy]], [[concepts/mqtt-tls]]

## Overview

Mosquitto runs as a Home Assistant add-on at `192.168.20.101`. It is the central message bus for all VentSys ESP32 devices, Node-RED flows, Frigate, and Bambuddy. Pre-TLS it listens on port 1883; post-TLS migration it listens exclusively on port 8883 with local CA certificate authentication.

## Ports

| Port | Status | Purpose |
|---|---|---|
| 1883 | Pre-TLS only; blocked by firewall after migration | Plain MQTT |
| 8883 | Post-TLS (target state) | MQTT over TLS with local CA |

## User Accounts & ACL

| User | Topics | Purpose |
|---|---|---|
| `ha_secure_user` | `readwrite #` | Home Assistant full access |
| `ventsys_controllers` | `ventsys/fan/+`, `ventsys/+/valve/+`, `ventsys/devices/+/+` | Fan + valve ESP32s |
| `ventsys_sensors` | Environmental sensor topics + `homeassistant/sensor/ventsys/+` | Sensor ESP32s |
| `ventsys_nodered` | `ventsys/#`, `homeassistant/#` | Node-RED orchestration |

## TLS Config (target state)

- Config: `/config/mosquitto/mosquitto.conf`
- CA cert: `/mosquitto/config/certs/ca-cert.pem`
- TLS version: 1.2 minimum
- `require_certificate: false` — username/password + TLS (no client certs)
- `allow_anonymous: false`

## Troubleshooting

```bash
# Test broker connectivity (pre-TLS)
mosquitto_pub -h localhost -p 1883 -u mqtt -P <password> -t test -m hello

# Test broker connectivity (post-TLS)
mosquitto_pub -h 192.168.20.101 -p 8883 --cafile /ssl/ca.crt -u mqtt -P <password> -t test -m hello

# Subscribe to all VentSys topics
mosquitto_sub -h localhost -p 1883 -u mqtt -P <password> -t 'ventsys/#' -v
```

- Broker not running: Settings → Add-ons → Mosquitto → Start
- Auth failure: check credentials in Settings → Devices & Services → MQTT → Configure
- See [[sources/troubleshooting-reference]]

## Change Log

- 2026-04-07: Page created from project-wide ingest
