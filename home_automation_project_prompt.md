# Home Automation Project - Master Prompt

A comprehensive home automation system focused on fire safety and safe ventilation for 3D printing operations, with integrated CCTV monitoring, secure network architecture, and AI-driven automation through Claude MCP integration.

## Project Overview

**Primary Objective:** Create a comprehensive home automation system focused on fire safety and safe ventilation for 3D printing operations, with integrated CCTV monitoring, secure network architecture, and AI-driven automation through Claude MCP integration.

**Project Status:**
- **Current Phase:** Network Architecture & Planning
- **Progress:** 25% Complete
- **Priority:** Safety systems implementation first
- **Risk Level:** High (due to fire safety requirements)

## Hardware Infrastructure

### Core Computing Platform
- **Device:** MINIX Fanless Mini PC (NEO Z350-0dB)
- **CPU:** Intel i3-N350
- **RAM:** 16GB DDR4
- **Storage:** 512GB M.2 PCIe Gen3
- **OS:** Windows 11 Pro (running Proxmox virtualization)

### Network Infrastructure
- **Router:** GL.iNet GL-MT6000 (flashed with OpenWrt firmware)
- **Additional:** POE switch (for CCTV cameras)
- **Storage:** Raspberry Pi NAS for CCTV footage storage

## System Architecture

### System 1: Smart Ventilation & Fire Safety System
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
- **Platform:** Frigate NVR running on dedicated Proxmox VM
- **Storage:** Raspberry Pi NAS integration
- **Features:** Motion detection, object recognition, remote monitoring

### System 3: Network Storage (NAS)
- **Platform:** Raspberry Pi
- **Purpose:** CCTV footage storage and general network storage

### System 4: AI Integration
- **Claude MCP Integration:** Model Context Protocol for advanced AI automation
- **Features:**
  - Natural language control of home automation
  - Intelligent emergency response coordination
  - Predictive maintenance and anomaly detection
  - Advanced automation logic based on multiple sensor inputs

## Virtualization Strategy

**Host:** Proxmox on MINIX mini PC

**VMs:**
1. Home Assistant (primary automation hub)
2. Frigate NVR (CCTV management)
3. Claude MCP integration service
4. Additional services as needed

## Network Security & Segmentation

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

## Implementation Phases

### Phase 1: Network Architecture & Security
- [x] OpenWrt router configuration
- [x] VLAN design and implementation
- [ ] Firewall rules and security policies
- [ ] Device inventory system
- [x] Network diagram creation

### Phase 2: Core Infrastructure Setup
- [ ] Proxmox installation and configuration
- [ ] Home Assistant VM deployment
- [ ] Frigate NVR VM deployment
- [ ] Raspberry Pi NAS setup

### Phase 3: Smart Ventilation System Development
- [ ] PrintAirPipe system fabrication from provided STL files
- [ ] ESPHome controller programming using provided code repository
- [ ] Sensor integration and calibration
- [ ] Servo control system for automated dampers
- [ ] Fire detection logic and emergency protocols
- [ ] Smart plug automation and safety cutoffs

### Phase 4: CCTV Integration
- [ ] Camera installation and POE configuration
- [ ] Frigate configuration and optimization
- [ ] NAS storage integration
- [ ] Motion detection and alerting

### Phase 5: AI Integration & Advanced Automation
- [ ] Claude MCP setup with Home Assistant
- [ ] Natural language control implementation
- [ ] Intelligent automation rule development
- [ ] Emergency response AI coordination

### Phase 6: System Integration & Testing
- [ ] Cross-system communication setup
- [ ] Comprehensive safety testing
- [ ] Remote access configuration
- [ ] Documentation and monitoring setup

## Key Technical Challenges

1. **Network Segmentation:** Balancing security isolation with remote access needs
2. **Fire Safety Logic:** Developing reliable sensor-based emergency response
3. **Resource Management:** Optimizing multiple VMs on single hardware platform
4. **Remote Access Security:** Secure external access without compromising isolation
5. **Integration Complexity:** Coordinating multiple systems and platforms
6. **AI Integration:** Implementing Claude MCP for intelligent automation while maintaining security
7. **PrintAirPipe Integration:** Properly implementing the smart ventilation system with ESPHome

## Success Criteria

- [ ] Safe, automated ventilation for 3D printing operations using PrintAirPipe system
- [ ] Reliable fire detection and emergency shutoff capability
- [ ] Secure network architecture with proper segmentation
- [ ] Remote monitoring and control capabilities
- [ ] Comprehensive CCTV coverage with reliable storage
- [ ] AI-driven automation with natural language control
- [ ] System monitoring and alerting functionality
- [ ] Complete documentation and network mapping

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

### Project Resources
- **Repository:** https://github.com/[username]/home-automation-project.git
- **Network Architecture:** 4-VLAN security segmented design
- **AI Integration:** Claude MCP for intelligent automation
- **Hardware Platform:** MINIX mini PC with Proxmox virtualization

## Safety Considerations

⚠️ **Critical Safety Requirements:**
- Prioritize safety systems and fail-safes throughout development
- Consider power failure scenarios and backup power needs
- Test all emergency response systems thoroughly before deployment
- Implement redundant safety mechanisms for fire detection
- Plan for system maintenance without compromising safety

## Risk Assessment

- **Project Start Date:** [Current Date]
- **Estimated Duration:** [To be determined based on phase completion]
- **Risk Level:** High (due to fire safety requirements)
- **Priority:** Critical safety features first, convenience features second

## Repository Structure

```
home-automation-project/
├── docs/
│   ├── session-states/      # Claude session management
│   ├── decisions/           # Architecture decision records
│   ├── procedures/          # Step-by-step processes
│   └── troubleshooting/     # Issue resolution guides
├── configs/
│   ├── openwrt/            # Router configurations
│   ├── home-assistant/     # HA automation configs
│   ├── frigate/            # NVR system configs
│   ├── esphome/           # Sensor controller configs
│   └── proxmox/           # Virtualization configs
├── hardware/
│   ├── stl-files/         # 3D printing files
│   ├── wiring-diagrams/   # Circuit documentation
│   └── part-lists/        # Component specifications
└── scripts/
    ├── setup/             # Installation automation
    ├── backup/            # Backup procedures
    └── monitoring/        # Health check scripts
```

## Session Management

This project uses structured session state management for Claude conversations. When starting a new session:

1. **Load Current State:** Reference the latest session state document from `docs/session-states/`
2. **Specify Focus:** Identify which system or phase to work on
3. **Update Documentation:** Create new session state files for each work session
4. **Commit Changes:** Push configuration updates to GitHub repository

## Next Steps

**Immediate Priority (Next Session):**
1. Begin OpenWrt router configuration for 4-VLAN network
2. Create specific VLAN interface configurations
3. Implement firewall rules for security segmentation
4. Set up network testing procedures

**Current Dependencies:**
- Router ready for OpenWrt firmware flash
- Network planning documentation complete (✅ done)
- Repository structure established (✅ done)
- GitHub backup active (✅ done)

---

**Document Version:** 1.0  
**Last Updated:** September 14, 2025  
**Status:** Active Project - Network Architecture Phase  
**Next Review:** Upon phase completion