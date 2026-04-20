---
title: Home Assistant Core - Automation Hub Sub-Project
description: Central automation platform implementation for home automation project
tags: [sub-project, home-assistant, automation-hub, smart-home, integration]
aliases: [Home Assistant Core, HA Core Sub-Project]
created: 2025-09-15
modified: 2025-09-23
type: sub-project
status: planning
---

# Sub-Project Prompt: Home Assistant Core - Automation Hub

## Project Navigation
- **Main Project:** [[README|Home Automation Project Overview]]
- **Project Index:** [[PROJECT-INDEX|Complete Documentation Hub]]
- **Network Architecture:** [[docs/decisions/01-network-architecture|Network Architecture Decision]]
- **Latest Session:** *Session file deep-archived*

## Context
Part of the larger [[README|home automation project]] with fire safety focus. Home Assistant serves as the central automation hub that coordinates all systems while maintaining security isolation through the [[docs/decisions/01-network-architecture|4-VLAN network architecture]].

## Hardware & Infrastructure
- **Platform:** Home Assistant OS on Proxmox VM
- **VM Specs:** TBD based on [[docs/prompts/02-core-infrastructure|Core Infrastructure]] setup
- **Network:** VLAN 20 (Automation & Management) - 192.168.20.0/24
- **Access:** Internet enabled for updates/integrations, bridge access to other VLANs

## Core Responsibilities

### 🛡️ Safety System Integration (CRITICAL PRIORITY)
**Primary Integration:** [[docs/prompts/03-printairpipe-ventilation|PrintAirPipe Ventilation System]]
- Receive sensor data from VLAN 50 (IoT Sensors)
- Process fire detection logic
- Coordinate emergency responses
- Manage automated ventilation control
- Smart plug emergency power cutoff

### 🏠 System Coordination
**CCTV Integration:** [[docs/prompts/05-cctv-surveillance|CCTV & Surveillance]]
- Access Frigate NVR data from VLAN 30
- Motion detection notifications
- Security event logging

**Storage Integration:** [[docs/prompts/06-pi-nas-storage|Pi NAS Storage]]
- Access storage services from VLAN 40
- Backup automation data
- Media storage for notifications

**AI Integration:** [[docs/prompts/07-claude-mcp-ai|Claude MCP Integration]]
- Natural language automation control
- Intelligent decision making
- Emergency response coordination

## Network Security Implementation
Based on [[docs/decisions/01-network-architecture|Network Architecture Decision]]:

### VLAN Access Configuration
- **Home Network (VLAN 20):** Full bidirectional access
- **CCTV Network (VLAN 30):** HA can query Frigate, no reverse access
- **Storage Network (VLAN 40):** HA can access NAS services, no reverse access  
- **IoT Sensors (VLAN 50):** HA receives sensor data, can send control commands

### Remote Access Security
- **Internal Access:** Full functionality on local network
- **External Access:** Secure tunnel (VPN or HTTPS with strong auth)
- **Mobile Access:** HA companion app through secure connection
- **Emergency Access:** Separate emergency contact system for critical alerts

## Key Integrations

### ESPHome Integration (Safety Critical)
**PrintAirPipe Controllers:** [[docs/prompts/03-printairpipe-ventilation|PrintAirPipe Ventilation System]]
- Temperature sensors per enclosure
- Humidity sensors for environmental monitoring  
- Smoke detection for fire safety
- VOC sensors for air quality
- Servo control for ventilation dampers
- Smart plug control for emergency power cutoff

### Frigate Integration (Security)
**NVR System:** [[docs/prompts/05-cctv-surveillance|CCTV & Surveillance]]
- Camera feed access and control
- Motion detection events
- Object recognition notifications
- Recording management through NAS

### Claude MCP Integration (AI)
**AI Coordination:** [[docs/prompts/07-claude-mcp-ai|Claude MCP Integration]]
- Natural language automation control
- Intelligent emergency response
- Predictive maintenance alerts
- Complex automation logic

## Safety-First Configuration

### Fire Safety Automations (CRITICAL)
```yaml
# Emergency Response Automation
- Fire detected → Immediate power cutoff → Ventilation activation → Emergency notification
- Sensor failure → Fail-safe mode activation → Manual intervention alert
- Temperature threshold → Graduated response (warning → ventilation → emergency)
```

### Fail-Safe Design Principles
- **Sensor Redundancy:** Multiple sensor types per enclosure
- **Communication Backup:** Multiple notification channels
- **Manual Overrides:** Physical emergency controls
- **Network Independence:** Critical functions work during network failures

## Implementation Dependencies

### Prerequisites (Must Complete First)
1. **Network Foundation:** [[docs/prompts/01-network-infrastructure|Network Infrastructure]] - VLAN 20 operational
2. **Virtualization Platform:** [[docs/prompts/02-core-infrastructure|Core Infrastructure]] - Proxmox VM ready
3. **Safety System Design:** [[docs/prompts/03-printairpipe-ventilation|PrintAirPipe Ventilation]] - ESPHome configs ready

### Enables (Dependent Sub-Projects)
- **CCTV Integration:** [[docs/prompts/05-cctv-surveillance|CCTV & Surveillance]] - Frigate coordination
- **AI Integration:** [[docs/prompts/07-claude-mcp-ai|Claude MCP Integration]] - MCP connectivity
- **All Safety Systems:** Central coordination point for emergency response

## Current Status
- [x] Architecture designed within [[docs/decisions/01-network-architecture|Network Architecture]]
- [x] Network assignment planned (VLAN 20)
- [x] Safety integration strategy defined
- [ ] VM specifications determined
- [ ] Base configuration created
- [ ] ESPHome integration implemented
- [ ] Safety automations configured
- [ ] Remote access secured
- [ ] Testing and validation completed

## Goals
1. Deploy Home Assistant OS on Proxmox VM
2. Configure network access per VLAN architecture
3. Implement ESPHome integration for PrintAirPipe
4. Create safety-critical automation logic
5. Set up secure remote access
6. Integrate with Frigate NVR system
7. Configure Claude MCP connectivity
8. Test all emergency response scenarios

## Key Configuration Files
- **Main Config:** `configs/home-assistant/configuration.yaml` - Core HA setup
- **Automations:** `configs/home-assistant/automations.yaml` - Safety and convenience automations
- **Scripts:** `configs/home-assistant/scripts.yaml` - Emergency response scripts
- **ESPHome Configs:** Reference from [[docs/prompts/03-printairpipe-ventilation|PrintAirPipe System]]

## Related Sub-Projects
- **Foundation:** [[docs/prompts/01-network-infrastructure|Network Infrastructure & Security]]
- **Platform:** [[docs/prompts/02-core-infrastructure|Core Infrastructure (Proxmox)]]
- **Safety (PRIORITY):** [[docs/prompts/03-printairpipe-ventilation|PrintAirPipe Ventilation System]]
- **Security:** [[docs/prompts/05-cctv-surveillance|CCTV & Surveillance]]
- **Storage:** [[docs/prompts/06-pi-nas-storage|Pi NAS Storage]]
- **AI:** [[docs/prompts/07-claude-mcp-ai|Claude MCP Integration]]

## Session References
- **Architecture Planning:** *Session file deep-archived*
- **Infrastructure Setup:** *Session file deep-archived*
- **Next Session Template:** *Session template deep-archived*

## External Resources
- **Home Assistant Documentation:** https://www.home-assistant.io/docs/
- **ESPHome Integration:** https://esphome.io/guides/getting_started_hassio.html
- **PrintAirPipe ESPHome Code:** https://github.com/Nerdiyde/ESPHomeSnippets/tree/c0135795dc180c6ff4a1306b2f5982ef3db386c3/Snippets/PrintAirPipe
- **Frigate Integration:** https://docs.frigate.video/integrations/home-assistant

## Security Considerations
- **Network Isolation:** Strict VLAN enforcement per [[docs/decisions/01-network-architecture|Network Architecture]]
- **Authentication:** Strong passwords, 2FA, limited user accounts
- **Updates:** Regular security updates with staging environment
- **Backup:** Automated configuration backups to [[docs/prompts/06-pi-nas-storage|Pi NAS Storage]]
- **Monitoring:** Security event logging and alerting

## Testing & Validation
- **Safety System Testing:** Comprehensive fire detection scenario testing
- **Network Security Testing:** VLAN isolation verification
- **Emergency Response Testing:** Full emergency procedure validation
- **Automation Logic Testing:** All automation scenarios verified
- **Remote Access Testing:** Secure connectivity validation

---
**Priority:** High (Central coordination hub for all systems)  
**Risk:** High (Safety-critical system coordination)  
**Dependencies:** Network + Virtualization + Safety System Design  
**Next Action:** Deploy after network infrastructure is operational
