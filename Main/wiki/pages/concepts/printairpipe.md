---
title: "PrintAirPipe"
category: concept
tags: [hardware, ventilation, 3d-printing, ducting, printairpipe]
created: 2026-04-07
updated: 2026-04-07
sources: [project-readme, hardware-bom, ventsys-technical-specs]
status: active
---

# PrintAirPipe

## Definition

PrintAirPipe is a commercial 3D-printable modular ducting system (125mm diameter) designed for 3D printer fume extraction. Available from nerdiy.de (€29 for STL files). Components include pipe segments, servo-actuated butterfly valves, filter housings, and connectors.

## Relevance to This Project

PrintAirPipe forms the physical duct network for [[entities/ventsys]]. Butterfly valves in the duct are actuated by MG90S servos controlled by [[entities/esphome]] valve controllers. The duct runs from each printer enclosure to the inline exhaust fan.

## Print Materials

| Component | Material | Reason |
|---|---|---|
| Pipe segments | PLA+ | Adequate for ambient temperature |
| Servo valve housings | PLA+ | Mechanical strength sufficient |
| Sensor housings | PLA+ | OK for sensor placement |
| Filter housings | PLA-HT (fire-retardant) | Mandatory — fire safety critical |

## Hardware Integration

- Servo: MG90S (or equivalent) — 4× minimum for valve actuation
- Controller: ESP32 valve controller via GPIO18 → servo PWM (50Hz, 0–180°)
- Valve position: 0% = fully closed, 100% = fully open (0–180°)

## Status

- STL files: ✅ Purchased (£29, nerdiy.de)
- 3D printing: ⏳ Pending — requires PLA+ and PLA-HT filament
- Hardware: ⏳ MG90S servos, mounting hardware still to purchase
- Installation: ⏳ Pending hardware and 3D printing

## Key Entities Using This Concept

- [[entities/ventsys]]
- [[entities/esphome]]

## Sources

- [[sources/project-readme]]
- [[sources/hardware-bom]]
- [[sources/ventsys-technical-specs]]
