---
title: Home Automation Project Overview
description: Home automation system with fire safety, CCTV, and AI integration
tags: [home-automation, project-overview]
aliases: [Project Overview]
type: project-overview
status: active
phase: Network Implementation
progress: 47
---

# Home Automation Project

Home automation system focused on fire safety and ventilation for 3D printing operations, with CCTV monitoring, secure network architecture, and AI integration.

**Navigation:** [[PROJECT-INDEX|ðŸ“‹ Full Index]] | [[docs/session-states|ðŸ“‚ Sessions]] | **Repository:** https://github.com/Nysplaidame/home-automation-project

## Project Status
- **Phase:** Network Implementation (47% complete)
- **Current:** VLAN deployment and testing
- **Next:** PrintAirPipe safety systems
- **GitHub:** https://github.com/Nysplaidame/home-automation-project

## Hardware
- **Compute:** MINIX NEO Z350-0dB (i3-N350, 32GB RAM, 512GB SSD)
- **Network:** GL.iNet GL-MT6000 (OpenWrt)
- **Storage:** Raspberry Pi NAS
- **CCTV:** POE switch + IP cameras

## System Components

### PrintAirPipe Fire Safety [[03-printairpipe-ventilation]]
- Two 3D printer enclosures with smart ventilation
- Multi-sensor arrays (temperature, VOC, smoke)
- Emergency power cutoff capability
- ESPHome controllers on isolated network

### Network Security [[01-network-architecture]]
- 4-VLAN architecture: Management (20), CCTV (30), Storage (40), IoT (50)
- OpenWrt firewall with inter-VLAN isolation
- Safety systems isolated from internet

### CCTV System [[05-cctv-surveillance]]
- Frigate NVR on dedicated Proxmox VM
- Motion detection and object recognition
- Raspberry Pi NAS storage integration

### Home Assistant Core [[04-home-assistant-core]]
- Proxmox virtualization platform
- Central automation and monitoring hub
- Claude MCP integration for AI control



## Implementation Status
- **Network:** Architecture complete, VLAN deployment pending
- **Safety Systems:** Planning complete, hardware pending
- **Infrastructure:** Hardware ready, Proxmox installation pending
- **CCTV:** Design complete, camera selection pending



## Implementation Phases
1. **Network** [[01-network-infrastructure]] - VLAN deployment remaining
2. **Infrastructure** [[02-core-infrastructure]] - Proxmox installation
3. **Safety Systems** [[03-printairpipe-ventilation]] - PrintAirPipe implementation  
4. **CCTV** [[05-cctv-surveillance]] - Camera installation
5. **AI Integration** [[07-claude-mcp-ai]] - Advanced automation





## Key Resources
- **PrintAirPipe Hardware:** [STL Files](https://nerdiy.de/en/product-2/printairpipe-125-actuator-sensor-set-3d-printable-stl-files/)
- **PrintAirPipe Software:** [ESPHome Code](https://github.com/Nerdiyde/ESPHomeSnippets/tree/c0135795dc180c6ff4a1306b2f5982ef3db386c3/Snippets/PrintAirPipe)

## Safety Notes
PrintAirPipe system includes fire detection and emergency power cutoff. Test thoroughly before deployment.

## Next Session
**Priority:** [[01-network-infrastructure|Network Infrastructure]] - Deploy VLAN configuration and test isolation
**Context:** [[docs/session-states|Session States]] - Load latest development context

**Last Updated:** September 21, 2025
