---
title: Home Automation Project - Main Overview
description: Comprehensive home automation system with fire safety, CCTV, and AI integration
tags:
  - home-automation
  - fire-safety
  - project-overview
  - network-security
aliases:
  - Home Automation Main
  - Project Overview
  - Main Project
created: 2025-09-15
modified: 2025-09-17
status: active
phase: Network Architecture & Planning
progress: 25
priority: high
related_sessions:
  - "[[session_state_20250912]]"
  - "[[session_state_20250909]]"
related_decisions:
  - "[[001-network-architecture]]"
sub_projects:
  - "[[01-network-infrastructure]]"
  - "[[02-core-infrastructure]]"
  - "[[03-printairpipe-ventilation]]"
  - "[[04-home-assistant-core]]"
  - "[[05-cctv-surveillance]]"
  - "[[06-pi-nas-storage]]"
  - "[[07-claude-mcp-ai]]"
---

# Home Automation Project

A comprehensive home automation system focused on fire safety and safe ventilation for 3D printing operations, with integrated CCTV monitoring, secure network architecture, and AI-driven automation through Claude MCP integration.

## Project Navigation

### Core Documentation
- **Project Status & Overview**: This document
- **Network Architecture**: [[001-network-architecture|Network Architecture Decision]]
- **Latest Session**: [[session_state_20250912|Latest Development Session]]
- **Session History**: [[session_state_20250909|Initial Planning Session]]

### Sub-Project Prompts
- **Network & Security**: [[01-network-infrastructure|Network Infrastructure]]
- **Virtualization**: [[02-core-infrastructure|Core Infrastructure (Proxmox)]]
- **Fire Safety**: [[03-printairpipe-ventilation|PrintAirPipe Ventilation System]]
- **Automation Hub**: [[04-home-assistant-core|Home Assistant Core]]
- **Surveillance**: [[05-cctv-surveillance|CCTV & Surveillance]]
- **Storage**: [[06-pi-nas-storage|Pi NAS Storage]]
- **AI Integration**: [[07-claude-mcp-ai|Claude MCP Integration]]

## Project Overview

**Primary Objective:** Create a comprehensive home automation system focused on fire safety and safe ventilation for 3D printing operations, with integrated CCTV monitoring, secure network architecture, and AI-driven automation through Claude MCP integration.

**GitHub Repository:** https://github.com/Nysplaidame/home-automation-project

## Project Status
- **Current Phase:** Network Architecture & Planning
- **Progress:** 25% Complete
- **Priority:** Safety systems implementation first
- **Risk Level:** High (due to fire safety requirements)

## Hardware Infrastructure

### Core Computing Platform
- **Device:** MINIX Fanless Mini PC (NEO Z350-0dB)
- **CPU:** Intel i3-N350
- **RAM:** 32GB DDR4
- **Storage:** 512GB M.2 PCIe Gen3
- **OS:** Windows 11 Pro (running Proxmox virtualisation)

### Network Infrastructure
- **Router:** GL.iNet GL-MT6000 (flashed with OpenWrt firmware)
- **Additional:** POE switch (for CCTV cameras)
- **Storage:** Raspberry Pi NAS for CCTV footage storage

## System Architecture

### System 1: Smart Ventilation & Fire Safety System
> **⚠️ CRITICAL SAFETY SYSTEM** - See [[03-printairpipe-ventilation|PrintAirPipe Ventilation System]]

**Primary Function:** Extract fumes from 3D printers and provide fire detection/prevention

**Components:**
- Two 3D printer enclosures (1x SLA, 1x FDM)
- PrintAirPipe 125 Smart Ventilation System with servo-controlled dampers
- Sensor array per enclosure:
  - Temperature sensors
  - Humidity sensors
  - Pressure sensors
  - Smoke detectors
  - VOC (Volatile Organic Compound) sensors
- Smart plugs for emergency power cutoff
- ESPHome-based controllers for Home Assistant integration
- Automated scripts for fire detection and response

**Safety Requirements:**
- Immediate power cutoff capability upon fire detection
- Automated ventilation response to sensor thresholds
- Fail-safe mechanisms for sensor failures

### System 2: CCTV Security System
> See [[05-cctv-surveillance|CCTV & Surveillance System]]

- **Platform:** Frigate NVR running on dedicated Proxmox VM
- **Storage:** Raspberry Pi NAS integration
- **Features:** Motion detection, object recognition, remote monitoring

### System 3: Network Storage (NAS)
> See [[06-pi-nas-storage|Pi NAS Storage System]]

- **Platform:** Raspberry Pi
- **Purpose:** CCTV footage storage and general network storage

### System 4: AI Integration
> See [[07-claude-mcp-ai|Claude MCP AI Integration]]

- **Claude MCP Integration:** Model Context Protocol for advanced AI automation
- **Features:**
  - Natural language control of home automation
  - Intelligent emergency response coordination
  - Predictive maintenance and anomaly detection
  - Advanced automation logic based on multiple sensor inputs

## Network Security & Segmentation
> See [[001-network-architecture|Network Architecture Decision]] for full details

### Security Requirements
- **Critical:** Isolate ventilation system from internet access
- **Critical:** Isolate CCTV system from internet access
- **Requirement:** Remote access to Home Assistant when away from home
- **Requirement:** Strong firewall configuration and security

### Network Design
- **Architecture:** 4-VLAN security-segmented design
- **VLAN 20:** Automation & Management (192.168.20.0/24) - Internet access
- **VLAN 30:** CCTV (192.168.30.0/24) - No internet, HA bridge access
- **VLAN 40:** Storage (192.168.40.0/24) - No internet, Frigate access
- **VLAN 50:** IoT Sensors (192.168.50.0/24) - No internet, HA control only

## Quick Start
1. Review [[docs/decisions/|Architecture Decisions]] for design rationale
2. Check [[docs/session-states/|Session States]] for latest development context  
3. See [[Main/home-automation-safety/configs/|System Configurations]] for current setup
4. Refer to [[docs/procedures/|Setup Procedures]] for implementation steps

## Repository Structure
```
docs/                   # Documentation and session states
├── session-states/     # Claude session documentation
├── decisions/          # Architecture decisions and rationale
├── procedures/         # Step-by-step procedures
├── prompts/           # Sub-project focused prompts
└── troubleshooting/    # Known issues and solutions
configs/                # System configurations
├── openwrt/            # Router configurations
├── home-assistant/     # HA configs and automations
├── frigate/            # NVR configurations
├── esphome/            # PrintAirPipe and sensor configs
└── proxmox/            # VM configurations
hardware/               # Physical system documentation
├── stl-files/          # 3D printing files
├── wiring-diagrams/    # Circuit diagrams
└── part-lists/         # Component specifications
scripts/                # Automation and setup scripts
├── setup/              # Installation scripts
├── backup/             # Backup procedures
└── monitoring/         # Health check scripts
```

## Implementation Phases

### Phase 1: Network Architecture & Security
> Primary: [[01-network-infrastructure|Network Infrastructure]]

- [x] OpenWrt router configuration
- [x] VLAN design and implementation
- [ ] Firewall rules and security policies
- [ ] Device inventory system
- [x] Network diagram creation 

### Phase 2: Core Infrastructure Setup
> Primary: [[02-core-infrastructure|Core Infrastructure]]

- [ ] Proxmox installation and configuration
- [ ] Home Assistant VM deployment
- [ ] Frigate NVR VM deployment
- [ ] Raspberry Pi NAS setup

### Phase 3: Smart Ventilation System Development
> Primary: [[03-printairpipe-ventilation|PrintAirPipe Ventilation]]

- [ ] PrintAirPipe system fabrication from provided STL files
- [ ] ESPHome controller programming using provided code repository
- [ ] Sensor integration and calibration
- [ ] Servo control system for automated dampers
- [ ] Fire detection logic and emergency protocols
- [ ] Smart plug automation and safety cutoffs

### Phase 4: CCTV Integration
> Primary: [[05-cctv-surveillance|CCTV & Surveillance]]

- [ ] Camera installation and POE configuration
- [ ] Frigate configuration and optimization
- [ ] NAS storage integration
- [ ] Motion detection and alerting

### Phase 5: AI Integration & Advanced Automation
> Primary: [[07-claude-mcp-ai|Claude MCP AI]] + [[04-home-assistant-core|Home Assistant Core]]

- [ ] Claude MCP setup with Home Assistant
- [ ] Natural language control implementation
- [ ] Intelligent automation rule development
- [ ] Emergency response AI coordination

### Phase 6: System Integration & Testing
> All sub-projects integrate

- [ ] Cross-system communication setup
- [ ] Comprehensive safety testing
- [ ] Remote access configuration
- [ ] Documentation and monitoring setup

## 📋 Key Architecture Documents
- **Network Design:** [[001-network-architecture|Network Architecture Decision]] - 4-VLAN security architecture rationale
- **Current Session:** [[session_state_20250912|Latest Session State]] - Latest development context

## 🔧 Implementation Status by System

### Network (OpenWrt Router)
> See [[01-network-infrastructure|Network Infrastructure]] for focused work

- **Architecture Decision:** [[001-network-architecture|Architecture Decision]] - ✅ Complete
- **Firewall Rules:** `configs/openwrt/firewall-config.sh` - ✅ Complete (128-line security config)
- **VLAN Configuration:** `configs/openwrt/vlan-config.conf` - 🚧 Pending implementation
- **Main Configuration:** `configs/openwrt/main-config.conf` - 🚧 Pending implementation
- **Status:** Ready for router implementation

### Home Assistant (Core Automation)
> See [[04-home-assistant-core|Home Assistant Core]] for focused work

- **Main Config:** `configs/home-assistant/configuration.yaml` - 🚧 Placeholder
- **Automations:** `configs/home-assistant/automations.yaml` - 🚧 Placeholder  
- **Network Integration:** Depends on [[001-network-architecture|Network Architecture]] (VLAN 20)
- **Status:** Architecture complete, awaiting implementation

### Safety Systems (ESPHome/PrintAirPipe)
> See [[03-printairpipe-ventilation|PrintAirPipe Ventilation]] for focused work

- **PrintAirPipe Controller:** `configs/esphome/printairpipe-controller.yaml` - 🚧 Placeholder
- **Network Assignment:** VLAN 50 (IoT Sensors) per [[001-network-architecture|Network Architecture]]
- **Safety Priority:** Critical - fire detection and emergency shutoff
- **Status:** Design complete, implementation pending

### CCTV System (Frigate NVR)
> See [[05-cctv-surveillance|CCTV & Surveillance]] for focused work

- **NVR Configuration:** `configs/frigate/config.yml` - 🚧 Placeholder
- **Network Assignment:** VLAN 30 (isolated) per [[001-network-architecture|Network Architecture]]
- **Remote Access:** Via Home Assistant bridge only
- **Status:** Architecture defined, awaiting camera selection

### Virtualization (Proxmox)
> See [[02-core-infrastructure|Core Infrastructure]] for focused work

- **VM Setup Scripts:** `configs/proxmox/vm-setup.sh` - 🚧 Placeholder
- **Network Assignment:** VLAN 20 (Automation) per [[001-network-architecture|Network Architecture]]
- **VM Plan:** Home Assistant (101) + Frigate (102) + future expansion
- **Status:** Hardware ready, scripts pending

## 📚 Session Management System
- **Current Session:** [[session_state_20250912|Current Session State]] - Repository setup complete
- **Session Template:** [[session-template-complete|Session Template]] - For future development sessions  
- **Session History:** [[session_state_20250909|Initial Planning]] - Original planning session
- **All Sessions:** Browse [[docs/session-states/|Session States Directory]] for complete development chronology

## Essential Resources

### PrintAirPipe Resources
- **Hardware STL Files:** https://nerdiy.de/en/product-2/printairpipe-125-actuator-sensor-set-3d-printable-stl-files/
  - 3D printable STL files for actuator and sensor housings
  - Servo mounts and sensor integration components
  - Designed for 125mm ducting systems

- **ESPHome Software:** https://github.com/Nerdiyde/ESPHomeSnippets/tree/c0135795dc180c6ff4a1306b2f5982ef3db386c3/Snippets/PrintAirPipe
  - Complete ESPHome YAML configurations
  - Home Assistant integration templates
  - Servo control and sensor implementations

## Safety Considerations

⚠️ **Critical Safety Requirements:**
- Prioritize safety systems and fail-safes throughout development
- Consider power failure scenarios and backup power needs
- Test all emergency response systems thoroughly before deployment
- Implement redundant safety mechanisms for fire detection
- Plan for system maintenance without compromising safety

## Session Management

This project uses structured session state management for Claude conversations. When starting a new session:

1. **Load Current State:** Reference the latest session state document from [[docs/session-states/|Session States]]
2. **Specify Focus:** Choose a [[docs/prompts/|Sub-Project Prompt]] or continue main project
3. **Update Documentation:** Create new session state files for each work session
4. **Commit Changes:** Push configuration updates to GitHub repository

## Next Steps

**Immediate Priority (Next Session):**
1. Begin OpenWrt router configuration for 4-VLAN network
2. Create specific VLAN interface configurations
3. Implement firewall rules for security segmentation
4. Set up network testing procedures

**Focus Area:** [[01-network-infrastructure|Network Infrastructure Sub-Project]]

**Current Dependencies:**
- Router ready for OpenWrt firmware flash
- Network planning documentation complete (✅ done)
- Repository structure established (✅ done)
- GitHub backup active (✅ done)

---

**Safety Warning**  
⚠️ This system includes fire safety components. Always prioritise safety features and test thoroughly before deployment.

**Related Documents:**
- [[001-network-architecture|Network Architecture Decision]]
- [[session_state_20250912|Latest Session State]]
- [[session_state_20250909|Initial Planning Session]]

**Document Version:** 2.0  
**Last Updated:** September 15, 2025  
**Status:** Active Project - Network Architecture Phase