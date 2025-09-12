# Decision: 4-VLAN Security-Segmented Network Architecture

**Date:** 2025-09-09
**Status:** Accepted
**Context:** Need secure network design isolating safety systems from internet while enabling remote access

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

## Implementation
- **Files Affected:** 
  - configs/openwrt/firewall-rules.conf
  - configs/openwrt/vlan-config.conf 
  - Network device configurations
  
---
**Related Sessions:** 20250909-initial-planning, 20250912-documentation-setup
