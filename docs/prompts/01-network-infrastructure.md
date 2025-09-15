# Sub-Project Prompt: Network Infrastructure & Security

## Context
Part of larger home automation project with fire safety focus. This sub-project handles the foundational network architecture that all other systems depend on.

## Hardware
- **Router:** GL.iNet GL-MT6000 (OpenWrt)
- **Network:** 4-VLAN security-segmented design
- **Additional:** POE switch for cameras

## Network Design
- **VLAN 20:** Automation & Management (192.168.20.0/24) - Internet access
- **VLAN 30:** CCTV (192.168.30.0/24) - No internet, HA bridge only
- **VLAN 40:** Storage (192.168.40.0/24) - No internet, Frigate access
- **VLAN 50:** IoT Sensors (192.168.50.0/24) - No internet, HA control only

## Security Requirements
- **Critical:** Isolate VLAN 30, 40, 50 from internet
- **Critical:** Allow HA (VLAN 20) to bridge to other VLANs for control
- **Requirement:** Remote access to HA when away from home
- **Requirement:** Strong firewall rules between segments

## Current Status
- [x] Architecture designed
- [x] Firewall config created (128 lines)
- [ ] VLAN interface configuration
- [ ] Router implementation
- [ ] Security testing

## Goals
1. Configure OpenWrt VLAN interfaces
2. Implement firewall rules for security segmentation
3. Set up remote access for HA
4. Test network isolation and connectivity
5. Document network topology

## Key Files
- [[configs/openwrt/firewall-config.sh]] - Security rules
- [[docs/decisions/001-network-architecture]] - Design rationale
- network_diagram.mermaid - Visual topology

## Dependencies
- Router ready for OpenWrt flash
- Other sub-projects depend on this network foundation

---
**Priority:** Critical (foundation for all other systems)  
**Risk:** High (security failure affects entire project)  
**Timeline:** Complete before other sub-projects begin