---
title: "VentSys Architecture"
category: concept
tags: [ventsys, architecture, safety, esphome, nodered, mqtt]
created: 2026-04-07
updated: 2026-04-07
sources: [project-readme, ventsys-technical-specs, ventsys-implementation-roadmap]
status: stable
---

# VentSys Architecture

## Definition

VentSys is the fire safety ventilation control system for two 3D printer enclosures (FDM and SLA) and a spray booth. It uses a layered architecture: ESP32 microcontrollers (ESPHome) → MQTT → Node-RED (logic) → Home Assistant (monitoring, automations, dashboard). All communication is over VLAN 50 (IoT, no internet).

## Relevance to This Project

This is the most safety-critical subsystem. Failure to ventilate a resin printer enclosure during a thermal event could result in fire or toxic fume exposure. The architecture is deliberately designed with multiple redundant layers and failsafe defaults.

## Layers

```
Physical sensors / actuators
        ↓ GPIO
ESP32 (ESPHome firmware)
        ↓ MQTT (VLAN 50 → VLAN 20)
Mosquitto broker (on Home Assistant)
        ↓ subscribe
Node-RED flows (logic, PID, coordination)
        ↓ publish / service calls
Home Assistant (monitoring, automations, alerts)
        ↓
VentSys Dashboard (ventsys-dashboard.html)
```

## Zones

| Zone | Enclosure | Valve(s) | Sensor Node |
|---|---|---|---|
| FDM | FDM printer enclosure | fdm-print-valve, fdm-branch-valve, fdm-360-valve | enc-fdm-sensors |
| SLA | SLA resin printer enclosure | sla-print-valve, sla-branch-valve, sla-360-valve | enc-sla-sensors |
| Booth | Spray booth | (fdm-branch or sla-branch covers booth) | enc-booth-sensors |
| Main | Shared duct | main-valve1, main-valve2, main-fan | — |

## Control Modes (12 scripts in `ventsys_ha_scripts.yaml`)

Scripts handle ventilation modes such as: idle, print-start, print-running, print-end, emergency, purge, and maintenance. Node-RED handles PID fan speed tuning.

## Failsafe Behaviour

- `input_boolean.ventsys_failsafe` in HA triggers emergency mode: all valves OPEN, fan 100%
- ⚠️ Recommendation: add a hardware normally-closed relay on fan PWM line — keeps fan ON if ESP32 loses power, independent of HA

## MQTT Topic Structure

```
ventsys/<zone>/temperature
ventsys/<zone>/humidity
ventsys/<zone>/pressure
ventsys/<zone>/voc
ventsys/<zone>/smoke
ventsys/<zone>/valve/control    ← subscribe (set position 0–100)
ventsys/<zone>/valve/state      ← publish (current position)
ventsys/fan/percent             ← subscribe (set speed 0–100)
ventsys/fan/state               ← publish
ventsys/devices/<name>/birth    ← device lifecycle
ventsys/devices/<name>/heartbeat
```

## Key Entities Using This Concept

- [[entities/ventsys]] (the subsystem itself)
- [[entities/esphome]] (firmware)
- [[entities/mosquitto-mqtt]] (bus)
- [[entities/home-assistant]] (orchestration)
- [[concepts/mqtt-tls]] (security layer)
- [[concepts/printairpipe]] (physical ducting)

## Sources

- [[sources/ventsys-technical-specs]]
- [[sources/ventsys-implementation-roadmap]]
- [[sources/project-readme]]
