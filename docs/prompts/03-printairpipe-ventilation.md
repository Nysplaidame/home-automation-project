# Sub-Project Prompt: PrintAirPipe Smart Ventilation System

## Context
**CRITICAL SAFETY SYSTEM** for home automation project. Provides automated fume extraction and fire detection for 3D printing operations. Failure could result in fire hazard.

## System Overview
- **Primary Function:** Extract fumes from 3D printers + fire detection/prevention
- **Enclosures:** 2x printer enclosures (1x SLA, 1x FDM)
- **Network:** VLAN 50 (IoT Sensors) - No internet, HA control only

## Hardware Components
- **PrintAirPipe 125:** Smart ventilation with servo dampers
- **Sensors per enclosure:**
  - Temperature sensors
  - Humidity sensors
  - Pressure sensors
  - Smoke detectors
  - VOC sensors
- **Controllers:** ESPHome-based for HA integration
- **Safety:** Smart plugs for emergency power cutoff

## Safety Requirements
- **CRITICAL:** Immediate power cutoff on fire detection
- **CRITICAL:** Automated ventilation response to thresholds
- **CRITICAL:** Fail-safe mechanisms for sensor failures
- **CRITICAL:** Redundant safety systems

## Current Status
- [ ] PrintAirPipe hardware fabrication (STL files)
- [ ] ESPHome controller programming
- [ ] Sensor integration and calibration
- [ ] Fire detection logic implementation
- [ ] Emergency shutoff automation
- [ ] Home Assistant integration
- [ ] Safety testing and validation

## Goals
1. 3D print PrintAirPipe components from provided STL files
2. Program ESPHome controllers using provided code templates
3. Install and calibrate all sensors
4. Implement fire detection algorithms
5. Set up emergency power cutoff automation
6. Integrate with Home Assistant for monitoring/control
7. Conduct comprehensive safety testing

## Key Resources
- **STL Files:** https://nerdiy.de/en/product-2/printairpipe-125-actuator-sensor-set-3d-printable-stl-files/
- **ESPHome Code:** https://github.com/Nerdiyde/ESPHomeSnippets/tree/c0135795dc180c6ff4a1306b2f5982ef3db386c3/Snippets/PrintAirPipe
- **Config:** [[configs/esphome/printairpipe-controller.yaml]]

## Dependencies
- **Requires:** Network (VLAN 50), Home Assistant VM operational
- **Blocks:** Nothing (can work in parallel with other systems)

---
**Priority:** CRITICAL (fire safety)  
**Risk:** VERY HIGH (safety system failure)  
**Timeline:** High priority - safety systems first