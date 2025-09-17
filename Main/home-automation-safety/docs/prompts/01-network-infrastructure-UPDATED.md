---
title: "Network Infrastructure & Security Sub-Project"
description: "Foundational network architecture implementation for home automation project"
tags:
  - sub-project
  - network-infrastructure
  - security
  - openwrt
  - vlan
  - firewall
aliases:
  - "Network Infrastructure"
  - "Network Sub-Project"
  - "01-Network-Infrastructure"
created: 2025-09-15
modified: 2025-09-16
sub_project_id: "01-network-infrastructure"
project_context: "[[Main/home-automation-safety/README|Home Automation Project]]"
priority: critical
status: planning
dependencies: 
  - "Router ready for OpenWrt flash"
related_decisions:
  - "[[Main/home-automation-safety/docs/decisions/001-network-architecture|Network Architecture Decision]]"
related_sessions:
  - "[[Main/home-automation-safety/docs/session-states/session_state_20250909|Initial Planning Session]]"
  - "[[Main/home-automation-safety/docs/session-states/session_state_20250912|Repository Setup Session]]"
implementation_files:
  - "configs/openwrt/firewall-config.sh"
  - "configs/openwrt/vlan-config.conf"
  - "configs/openwrt/main-config.conf"
network_diagram: "[[Main/home-automation-safety/docs/diagrams/Network Diagram|Network Topology]]"
---

# Sub-Project Prompt: Network Infrastructure & Security

## Context
Part of the larger [[Main/home-automation-safety/README|home automation project]] with fire safety focus. This sub-project handles the foundational network architecture that all other systems depend on.

## Project Navigation
- **Main Project:** [[Main/home-automation-safety/README|Home Automation Project Overview]]
- **Architecture Decision:** [[Main/home-automation-safety/docs/decisions/001-network-architecture|Network Architecture Decision]]
- **Network Diagram:** [[Main/home-automation-safety/docs/diagrams/Network Diagram|Visual Topology]]
- **Related Sessions:** [[Main/home-automation-safety/docs/session-states/session_state_20250909|Initial Planning]], [[Main/home-automation-safety/docs/session-states/session_state_20250912|Repository Setup]]

## Hardware
- **Router:** GL.iNet GL-MT6000 (OpenWrt)
- **Network:** 4-VLAN security-segmented design
- **Additional:** POE switch for cameras

## Network Design
Based on [[Main/home-automation-safety/docs/decisions/001-network-architecture|Network Architecture Decision]]:
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
- [x] Architecture designed ([[Main/home-automation-safety/docs/decisions/001-network-architecture|Decision Record]])
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

## Key Files & Dependencies
- **Security Rules:** `configs/openwrt/firewall-config.sh` - Already created ✅
- **VLAN Config:** `configs/openwrt/vlan-config.conf` - Pending creation 🚧
- **Main Router Config:** `configs/openwrt/main-config.conf` - Pending creation 🚧
- **Network Topology:** [[Main/home-automation-safety/docs/diagrams/Network Diagram|Network Diagram]] - Visual reference ✅

## Dependencies
- Router ready for OpenWrt flash
- Other sub-projects depend on this network foundation:
  - [[Main/home-automation-safety/docs/prompts/04-home-assistant-core|Home Assistant Core]]
  - [[Main/home-automation-safety/docs/prompts/05-cctv-surveillance|CCTV & Surveillance]]
  - [[Main/home-automation-safety/docs/prompts/03-printairpipe-ventilation|PrintAirPipe Ventilation]]

## Related Sub-Projects
Once this network foundation is complete, it enables:
- [[Main/home-automation-safety/docs/prompts/02-core-infrastructure|Core Infrastructure (Proxmox)]]
- [[Main/home-automation-safety/docs/prompts/04-home-assistant-core|Home Assistant Core]]
- [[Main/home-automation-safety/docs/prompts/05-cctv-surveillance|CCTV & Surveillance]]
- [[Main/home-automation-safety/docs/prompts/06-pi-nas-storage|Pi NAS Storage]]
- [[Main/home-automation-safety/docs/prompts/03-printairpipe-ventilation|PrintAirPipe Ventilation]]
- [[Main/home-automation-safety/docs/prompts/07-claude-mcp-ai|Claude MCP Integration]]

---
**Priority:** Critical (foundation for all other systems)  
**Risk:** High (security failure affects entire project)  
**Timeline:** Complete before other sub-projects begin
**Next Action:** Configure VLAN interfaces and implement router setup