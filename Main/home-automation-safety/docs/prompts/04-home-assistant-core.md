# Sub-Project Prompt: Home Assistant Core Automation

## Context
Part of home automation project with fire safety focus. Home Assistant serves as the central automation hub, coordinating all systems and providing the primary user interface.

## System Role
- **Primary Function:** Central automation and control hub
- **Network:** VLAN 20 (Management) - Internet access for remote control
- **Platform:** Proxmox VM (ID: 101)
- **Key Responsibility:** Bridge between isolated networks for control

## Integration Requirements
- **PrintAirPipe System:** Monitor sensors, control ventilation, fire response
- **CCTV System:** Bridge access to Frigate NVR (VLAN 30)
- **Storage System:** Access Pi NAS (VLAN 40) for data/backups
- **Claude MCP:** AI-driven automation and natural language control

## Network Architecture
- **Direct Access:** VLAN 20 (full internet access)
- **Bridge Access:** VLAN 30 (CCTV), VLAN 40 (Storage), VLAN 50 (IoT)
- **Security:** Firewall rules allow HA to control other VLANs

## Current Status
- [ ] Home Assistant installation and basic setup
- [ ] Network integration (VLAN bridging)
- [ ] PrintAirPipe integration (ESPHome)
- [ ] Frigate integration (camera feeds)
- [ ] Pi NAS integration
- [ ] Remote access configuration
- [ ] Claude MCP integration
- [ ] Automation rule development

## Goals
1. Install and configure Home Assistant on Proxmox VM
2. Set up network bridges to isolated VLANs
3. Integrate PrintAirPipe controllers via ESPHome
4. Configure Frigate camera access and controls
5. Set up Pi NAS integration for storage
6. Implement remote access (secure external connectivity)
7. Create automation rules for fire safety and ventilation
8. Integrate Claude MCP for AI-driven control

## Key Configurations
- [[configs/home-assistant/configuration.yaml]] - Main HA config
- [[configs/home-assistant/automations.yaml]] - Safety/ventilation automations
- Network bridge configuration for VLAN access

## Safety Focus
- **Fire Detection Response:** Immediate actions on smoke/temperature alerts
- **Ventilation Control:** Automated response to air quality sensors
- **Emergency Protocols:** Power cutoff and alert systems

## Dependencies
- **Requires:** Network (all VLANs), Proxmox VM, PrintAirPipe controllers
- **Enables:** All automation and remote monitoring capabilities

---
**Priority:** Critical (central control system)  
**Risk:** High (single point of failure for automation)  
**Timeline:** After infrastructure, parallel with other applications