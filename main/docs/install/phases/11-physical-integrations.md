---
title: Phase 11 - Physical Integrations
description: VentSys hardware, printers, cameras, ESPHome, and physical deployment
tags: [install, physical, ventsys, cameras, printers]
created: 2026-05-24
modified: 2026-05-25
type: install-guide
status: active
---

# Phase 11 - Physical Integrations

## Purpose

Connect the software platform to physical devices: VentSys ESPHome boards,
printer integration, PoE cameras, smart plugs, sensors, and wiring.

## Runs on

- Admin laptop for flashing and repository edits.
- Home Assistant UI and Terminal add-on.
- OpenWrt router over SSH for MAC reservations.
- Physical device UIs where applicable.

## Prerequisites

- Network, HA, Frigate, docker-host, and storage phases validated.
- Hardware purchased and labelled.
- Wiring reference read before power is applied.

## Inputs

- `<P1S_SERIAL>`
- `<MQTT_PASSWORD>`
- Camera RTSP credentials
- ESPHome API/encryption values if used

## Commands

Run on: Home Assistant Terminal add-on.

```sh
mosquitto_sub -h localhost -p 8883 --cafile /ssl/ca.crt -u mqtt -P '<MQTT_PASSWORD>' -t 'ventsys/#' -v
```

Run on: OpenWrt router over SSH after collecting a device MAC.

```sh
uci show dhcp | grep ventsys
```

## Explanation

Physical integration is where mistakes can create safety problems. Validate one
device path at a time: network, MQTT, HA entity, automation, dashboard, then
physical actuator behavior.

Safety-critical VentSys behavior must fail toward a safe state: power cutoff on
fire detection, ventilation response to temperature/VOC/smoke thresholds,
alerts on sensor failure, and manual override paths that do not depend on a
custom dashboard. Treat AI or convenience automation as advisory only; it must
not replace Home Assistant, ESPHome, MQTT, or physical safety checks.

## Expected result

- Devices have static DHCP reservations.
- ESPHome devices appear in HA.
- MQTT TLS migration path is followed.
- Camera feeds are reachable by Frigate only over intended paths.
- PoE camera and switch staging follows
  `docs/procedures/frigate_camera_preflight_checklist.md` before permanent
  mounting or production Frigate activation.
- Fire/smoke/temperature/VOC test scenarios produce harmless test alerts before
  any real emergency automation is trusted.

## Validation

Run on: Home Assistant Terminal add-on.

```sh
ha core check
```

Run on: Frigate CT over SSH.

```sh
docker compose logs --tail=80 frigate
```

## Failure recovery

- If a physical actuator behaves unexpectedly, remove power before debugging YAML.
- If an ESPHome device is unreachable, verify WiFi/VLAN/DHCP before reflashing.
- If camera credentials fail, validate RTSP outside Frigate before changing NVR config.

## Completion checklist

- [ ] Wiring checked before power.
- [ ] Device MACs recorded.
- [ ] MQTT topics verified.
- [ ] HA entities verified.
- [ ] Safety automations tested with harmless triggers first.
- [ ] Manual override and power cutoff paths tested.
- [ ] Sensor failure behavior tested.
