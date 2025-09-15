# Sub-Project Prompt: CCTV & Surveillance System

## Context
Part of home automation project with fire safety focus. Provides video surveillance with motion detection and AI object recognition, integrated with fire detection systems for visual confirmation.

## System Overview
- **Platform:** Frigate NVR on dedicated Proxmox VM (ID: 102)
- **Network:** VLAN 30 (CCTV) - Isolated from internet
- **Storage:** Raspberry Pi NAS (VLAN 40) integration
- **Access:** Home Assistant bridge only (no direct internet)

## Hardware Components
- **NVR:** Frigate running on Proxmox VM
- **Cameras:** POE cameras (selection TBD)
- **Network:** POE switch for camera power/connectivity
- **Storage:** Pi NAS for footage retention

## Security Architecture
- **Network Isolation:** VLAN 30 with no internet access
- **Storage Isolation:** VLAN 40 for secure footage storage
- **Access Control:** Only HA (VLAN 20) can bridge to camera feeds
- **Privacy:** No external access to raw camera feeds

## Current Status
- [ ] Camera selection and procurement
- [ ] POE switch setup and VLAN configuration
- [ ] Frigate NVR installation and configuration
- [ ] Pi NAS integration for storage
- [ ] Motion detection and AI setup
- [ ] Home Assistant integration
- [ ] Fire safety integration (visual confirmation)
- [ ] Performance optimization

## Goals
1. Select and procure appropriate POE cameras
2. Install and configure POE switch on VLAN 30
3. Deploy and configure Frigate NVR on Proxmox VM
4. Integrate Pi NAS for secure footage storage
5. Set up motion detection and object recognition
6. Create Home Assistant integration for monitoring
7. Implement fire safety visual confirmation alerts
8. Optimize performance and storage management

## Integration Points
- **Fire Safety:** Visual confirmation of smoke/fire alerts
- **Home Assistant:** Camera feeds and motion alerts
- **Storage:** Automatic footage archiving to Pi NAS
- **Network:** Secure isolation while maintaining control access

## Key Configurations
- [[configs/frigate/config.yml]] - NVR configuration
- Camera positioning and coverage planning
- Motion detection zones and sensitivity
- Storage retention policies

## Dependencies
- **Requires:** Network (VLAN 30/40), Proxmox VM, Pi NAS operational
- **Integrates:** Home Assistant for monitoring and alerts

---
**Priority:** Medium (security/monitoring support)  
**Risk:** Low (supplementary system)  
**Timeline:** After core infrastructure, parallel with other applications