---
title: CCTV & Surveillance System Sub-Project
description: Video surveillance with motion detection and AI object recognition for security monitoring
tags: [sub-project, cctv-surveillance, frigate, security]
aliases: [CCTV Surveillance, Surveillance Sub-Project]
created: 2025-09-15
modified: 2025-09-23
type: sub-project
status: planning
---

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
- **Frigate UI:** Must be accessed via HTTPS/SSL before regular use
- **Privacy:** No external access to raw camera feeds

## Current Status
- [ ] Camera selection and procurement
- [ ] POE switch setup and VLAN configuration
- [ ] Frigate NVR installation and configuration
- [ ] Frigate HTTPS/SSL UI access
- [ ] WebRTC audio for camera streams
- [ ] Lumen setup on Apple device for camera feeds (manual user step, in addition to Android UI)
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
7. Configure WebRTC audio for supported camera streams
8. Set up Lumen on an Apple device for camera feed access, alongside the Android UI
9. Implement fire safety visual confirmation alerts
10. Optimize performance and storage management

## Integration Points
- **Fire Safety:** Visual confirmation of smoke/fire alerts
- **Home Assistant:** Camera feeds and motion alerts
- **Storage:** Automatic footage archiving to Pi NAS
- **Network:** Secure isolation while maintaining control access

## Key Configurations
- [[configs/frigate/config.yml|Frigate Configuration]] - NVR configuration
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
