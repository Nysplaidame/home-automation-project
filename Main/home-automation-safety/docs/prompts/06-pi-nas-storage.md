# Sub-Project Prompt: Network Storage (Pi NAS)

## Context
Part of home automation project with fire safety focus. Provides secure, isolated storage for CCTV footage and system backups with no internet access for enhanced security.

## System Overview
- **Platform:** Raspberry Pi NAS
- **Network:** VLAN 40 (Storage) - No internet access
- **Primary Use:** CCTV footage storage and system backups
- **Access:** Frigate NVR (VLAN 30) via controlled bridge

## Storage Requirements
- **CCTV Footage:** Multi-day retention with automatic archiving
- **System Backups:** Home Assistant configs, automation rules
- **Security:** Air-gapped from internet, encrypted storage
- **Performance:** Sufficient for multi-camera video streams

## Network Architecture
- **Isolation:** VLAN 40 with no internet connectivity
- **Access Control:** Only Frigate (VLAN 30) can write footage
- **Backup Access:** Home Assistant (VLAN 20) for config backups
- **Security:** Encrypted storage, access logging

## Current Status
- [ ] Raspberry Pi setup and OS installation
- [ ] Network configuration (VLAN 40)
- [ ] Storage configuration and optimization
- [ ] Frigate integration for CCTV footage
- [ ] Home Assistant backup integration
- [ ] Security hardening and encryption
- [ ] Performance testing and optimization
- [ ] Monitoring and maintenance scripts

## Goals
1. Set up Raspberry Pi with optimized NAS OS/software
2. Configure network connectivity on VLAN 40 (storage)
3. Implement secure, encrypted storage solution
4. Integrate with Frigate for automatic CCTV footage storage
5. Set up Home Assistant backup procedures
6. Implement storage monitoring and alerting
7. Create maintenance and cleanup scripts
8. Test performance with expected video load

## Technical Considerations
- **Performance:** Optimize for video streaming write performance
- **Reliability:** RAID/redundancy for critical footage
- **Security:** Encryption at rest, access controls
- **Maintenance:** Automatic cleanup, health monitoring

## Key Configurations
- Network bridge configuration for VLAN access
- Storage optimization for video workloads
- Backup scheduling and retention policies
- Security and access control settings

## Dependencies
- **Requires:** Network (VLAN 40), basic infrastructure
- **Serves:** Frigate NVR, Home Assistant backups

---
**Priority:** Medium (supporting infrastructure)  
**Risk:** Medium (data loss risk if fails)  
**Timeline:** After network, parallel with CCTV setup