---
title: PrintAirPipe Smart Ventilation System Sub-Project
description: Critical safety system for automated fume extraction and fire detection for 3D printing operations
tags: [sub-project, printairpipe, fire-safety, ventilation, esphome, sensors, safety-critical]
aliases: [PrintAirPipe Ventilation, PrintAirPipe Sub-Project, Fire Safety System]
created: 2025-09-15
modified: 2025-09-23
type: sub-project
status: planning
---

# Sub-Project Prompt: PrintAirPipe Smart Ventilation System

## Context
**⚠️ CRITICAL SAFETY SYSTEM** for [[README|home automation project]]. Provides automated fume extraction and fire detection for 3D printing operations. Failure could result in fire hazard.

## Project Navigation
- **Main Project:** [[README|Home Automation Project Overview]]
- **Network Architecture:** [[docs/decisions/01-network-architecture|Network Architecture Decision]]
- **Project Index:** [[PROJECT-INDEX|Documentation Hub]]
- **Latest Session:** *Session file deep-archived*

## System Overview
- **Primary Function:** Extract fumes from 3D printers + fire detection/prevention
- **Enclosures:** 2x printer enclosures (1x SLA, 1x FDM)
- **Network:** VLAN 50 (IoT Sensors) - No internet, HA control only
- **Integration:** ESPHome controllers with Home Assistant

## Hardware Components
- **PrintAirPipe 125:** Smart ventilation with servo dampers
- **Sensors per enclosure:**
  - Temperature sensors
  - Humidity sensors
  - Pressure sensors
  - Smoke detectors
  - VOC (Volatile Organic Compound) sensors
- **Controllers:** ESPHome-based for HA integration
- **Safety:** Smart plugs for emergency power cutoff

## Safety Requirements
- **CRITICAL:** Immediate power cutoff on fire detection
- **CRITICAL:** Automated ventilation response to thresholds
- **CRITICAL:** Fail-safe mechanisms for sensor failures
- **CRITICAL:** Redundant safety systems
- **CRITICAL:** Regular safety testing and validation

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
- **Config File:** `configs/esphome/printairpipe-controller.yaml`

## Dependencies
- **Requires:** [[docs/prompts/01-network-infrastructure|Network infrastructure]] (VLAN 50)
- **Requires:** [[docs/prompts/04-home-assistant-core|Home Assistant]] VM operational
- **Blocks:** Nothing (can work in parallel with other systems)

## Related Sub-Projects
- **Network Foundation:** [[docs/prompts/01-network-infrastructure|Network Infrastructure & Security]]
- **Core Platform:** [[docs/prompts/02-core-infrastructure|Core Infrastructure (Proxmox)]]
- **Automation Hub:** [[docs/prompts/04-home-assistant-core|Home Assistant Core]]
- **Monitoring Integration:** [[docs/prompts/05-cctv-surveillance|CCTV & Surveillance]]
- **Storage Systems:** [[docs/prompts/06-pi-nas-storage|Pi NAS Storage]]
- **AI Integration:** [[docs/prompts/07-claude-mcp-ai|Claude MCP Integration]]

---
**Priority:** CRITICAL (fire safety)  
**Risk:** VERY HIGH (safety system failure)  
**Timeline:** High priority - safety systems first  
**Next Action:** Begin hardware fabrication and ESPHome programming