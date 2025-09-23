---
title: Network Architecture Decision - 4-VLAN Security Segmentation
description: Security-segmented network design isolating safety systems from internet
tags: [architecture-decision, network-security, vlan, firewall, safety-critical]
created: 2025-09-09
modified: 2025-09-23
type: decision
status: accepted
---

# Decision: 4-VLAN Security-Segmented Network Architecture

**Date:** 2025-09-09  
**Status:** Accepted  
**Context:** Need secure network design isolating safety systems from internet while enabling remote access

> **Related Sub-Project:** [[docs/prompts/01-network-infrastructure|Network Infrastructure & Security]]

## Problem Statement
Design a network architecture that:
- Completely isolates fire safety sensors from internet access
- Isolates CCTV system from internet access  
- Enables secure remote access to Home Assistant
- Provides management access to all systems
- Balances security with operational needs

## Decision
**Chosen Option:** 4-VLAN Hybrid Architecture

**Rationale:** 
- Provides required security isolation for safety systems
- Enables remote access through Home Assistant bridge
- Manageable complexity with clear security boundaries
- Allows controlled inter-system communication

## Network Design
- **VLAN 20:** Automation & Management (192.168.20.0/24) - Internet access
- **VLAN 30:** CCTV (192.168.30.0/24) - No internet, HA bridge access  
- **VLAN 40:** Storage (192.168.40.0/24) - No internet, Frigate access
- **VLAN 50:** IoT Sensors (192.168.50.0/24) - No internet, HA control only

## Implementation Status
- **Files Affected:** 
  - `configs/openwrt/firewall-rules.conf`
  - `configs/openwrt/vlan-config.conf` 
  - Network device configurations
  
**Related Sessions:** *Session files deep-archived*

## Related Documents & Implementation

### Core Project Context
- **Project Overview:** [[README|Main Project Overview]] - Current project status and roadmap
- **Network Implementation:** [[docs/prompts/01-network-infrastructure|Network Infrastructure Sub-Project]] - Focused implementation guide

### Session Context
- **Original Planning:** *Session file deep-archived* - Context and rationale
- **Repository Setup:** *Session file deep-archived* - Implementation progress

### Implementation Files
- **Firewall Rules:** `configs/openwrt/firewall-config.sh` - Security rules implementing this architecture ✅
- **VLAN Configuration:** `configs/openwrt/vlan-config.conf` - VLAN interface configuration 🚧
- **Main Router Config:** `configs/openwrt/main-config.conf` - Router main configuration 🚧

### Affected System Configurations
This architecture decision drives the configuration of:
- `configs/home-assistant/configuration.yaml` - HA network integration 🚧
- `configs/frigate/config.yml` - NVR network configuration 🚧
- `configs/esphome/printairpipe-controller.yaml` - Safety system network setup 🚧

## Security Implementation Status
- ✅ **Architecture Design** - 4-VLAN segmentation complete
- ✅ **Firewall Rules** - Comprehensive security policies defined
- 🚧 **Router Configuration** - VLAN setup pending
- 🚧 **Device Assignment** - IP allocation per VLAN pending
- 🚧 **Testing Procedures** - Network isolation validation pending

**Next Implementation Step:** Focus on [[docs/prompts/01-network-infrastructure|Network Infrastructure Sub-Project]] for VLAN configuration

## Cross-References

### Sub-Projects Affected
- **Primary Implementation:** [[docs/prompts/01-network-infrastructure|Network Infrastructure]]
- **HA Integration:** [[docs/prompts/04-home-assistant-core|Home Assistant Core]]
- **CCTV Integration:** [[docs/prompts/05-cctv-surveillance|CCTV & Surveillance]]
- **Storage Integration:** [[docs/prompts/06-pi-nas-storage|Pi NAS Storage]]
- **Safety Integration:** [[docs/prompts/03-printairpipe-ventilation|PrintAirPipe Ventilation]]

### Related Decisions
- Future decision: Remote access security implementation
- Future decision: Inter-VLAN communication policies
- Future decision: Emergency network access procedures

---
**Implementation Priority:** Critical (foundation for all other systems)  
**Next Action:** [[docs/prompts/01-network-infrastructure|Begin Network Infrastructure Implementation]]