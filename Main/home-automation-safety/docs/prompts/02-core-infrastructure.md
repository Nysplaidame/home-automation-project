# Sub-Project Prompt: Core Infrastructure (Proxmox & VMs)

## Context
Part of home automation project with fire safety focus. This sub-project creates the virtualized infrastructure hosting Home Assistant, Frigate NVR, and future services.

## Hardware
- **Host:** MINIX Mini PC (Intel i3-N350, 16GB RAM, 512GB SSD)
- **Current OS:** Windows 11 Pro
- **Target:** Proxmox hypervisor

## VM Architecture
1. **Home Assistant VM (ID: 101)**
   - **Network:** VLAN 20 (Management)
   - **Role:** Central automation hub
   - **Resources:** 4GB RAM, 2 CPU cores, 32GB storage

2. **Frigate NVR VM (ID: 102)**
   - **Network:** VLAN 30 (CCTV)
   - **Role:** Video surveillance and AI detection
   - **Resources:** 8GB RAM, 4 CPU cores, 100GB storage

3. **Future VMs:** Claude MCP integration, additional services

## Current Status
- [ ] Proxmox installation
- [ ] Network configuration (VLAN integration)
- [ ] VM template creation
- [ ] Home Assistant VM deployment
- [ ] Frigate NVR VM deployment
- [ ] Inter-VM communication setup

## Goals
1. Install and configure Proxmox hypervisor
2. Set up VLAN networking within Proxmox
3. Create and deploy Home Assistant VM
4. Create and deploy Frigate NVR VM
5. Configure VM backup procedures
6. Test VM performance and resource allocation

## Dependencies
- **Requires:** Network infrastructure (VLAN 20/30 operational)
- **Blocks:** All application-level sub-projects

## Key Configurations
- [[configs/proxmox/vm-setup.sh]] - VM creation scripts
- Network bridge configuration for VLAN integration
- Resource allocation optimization

---
**Priority:** Critical (hosts all automation services)  
**Risk:** Medium (hardware failure affects entire system)  
**Timeline:** Complete after network, before applications