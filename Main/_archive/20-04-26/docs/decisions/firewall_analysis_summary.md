# OpenWrt Firewall Configuration Analysis Summary
**Date:** September 24, 2025
**Project:** Home Automation Safety Project - Network Infrastructure Phase
**Focus:** 4-VLAN Security Architecture Implementation
**Repository:** https://github.com/Nysplaidame/home-automation-project

> **⚠️ HISTORICAL DOCUMENT — September 24, 2025**
> This is a point-in-time analysis. All decisions referenced here have since been resolved:
> - Proxmox Host: **192.168.10.10** (VLAN 10) — static, outside DHCP range
> - Frigate NVR VM: **192.168.30.20** (VLAN 30 CCTV) — internet isolated
> - Architecture: **9-VLAN** (not 4-VLAN) — see [[01-network-architecture]]
> - Configs written: `configs/openwrt/` contains the final, corrected implementations
>
> IPs and recommendations below reflect the pre-decision state and are superseded.

## Executive Summary

Systematic analysis of `configs/openwrt/firewall-config.sh` against documented network architecture revealed critical implementation gaps and architectural inconsistencies. The current configuration has solid security logic but lacks foundational network infrastructure and contains scope confusion between firewall and router configurations.

## Critical Issues Identified

### 1. Configuration File Scope Confusion ⚠️
**Problem:** Firewall script contains router configuration elements
**Current Impact:** 
- Network interface creation in firewall config
- DHCP configuration in firewall config
- Bridge VLAN configuration in wrong file
- Referenced networks don't exist when firewall loads

**Technical Details:**
- `uci set network.automation=interface` belongs in `/etc/config/network`
- DHCP scopes belong in `/etc/config/dhcp`
- Bridge-VLAN trunk port config belongs in router config
- Firewall should ONLY contain zones, rules, and policies

### 2. Missing Network Interface Prerequisites ⚠️
**Problem:** Firewall zones reference non-existent networks
**Affected Zones:**
- 'automation' network (VLAN 20)
- 'cctv' network (VLAN 30)
- 'storage' network (VLAN 40)
- 'iot_sensors' network (VLAN 50)

**Impact:** Firewall zones will fail to bind, rules won't apply

### 3. Proxmox Trunk Port Configuration Missing ⚠️
**Problem:** No switch configuration for Proxmox single-port connection
**Requirements:**
- Physical port (lan1) must be trunk carrying VLAN tags 10,20,30,40,50
- DSA switch configuration needed for modern OpenWrt
- Bridge-VLAN configuration for each VLAN on trunk port

### 4. Missing User Network Architecture ⚠️
**Problem:** No configuration for normal users on 192.168.1.0/24
**Discovery:** Network diagram shows router at 192.168.1.1
**Impact:** 
- Everyday users have no defined network access
- No WiFi client network configured
- VPN access model too restrictive for normal users

### 5. VLAN Numbering Inconsistency
**Architecture Doc:** VLANs 20, 30, 40, 50
**Firewall Config:** VLANs 10, 20, 30, 40, 50 (adds VLAN 10)
**Network Diagram:** Shows VLAN 10-50 with router on 192.168.1.1
**Resolution Needed:** Clarify if VLAN 10 should be added to architecture or removed from config

### 6. Frigate VM Misplacement 🔒
**Current:** Frigate on VLAN 20 (automation) with internet access
**Security Issue:** CCTV system has internet exposure
**Recommended:** Frigate on VLAN 30 (CCTV) with cameras, no internet
**Benefits:** Proper security isolation, eliminates internet attack vector

### 7. Proxmox Host Placement Issue 🏗️
**Current:** Proxmox host on VLAN 20 (automation) at 192.168.20.100
**Analysis:** Hypervisor mixed with workload VMs
**Recommended:** Proxmox host on VLAN 10 (management) at 192.168.10.100
**Rationale:**
- Infrastructure separation from workloads
- Administrative access alignment
- Enterprise best practices
- Security isolation of hypervisor

### 8. Over-Privileged Access Policies 🔒
**Management VLAN:** Full internet access (excessive)
**Home Assistant:** Full internet access (should be port-specific)
**VPN Access:** Only HA access (too restrictive for everyday users)

## Architectural Analysis

### Current Network Model Issues
1. **No User Network:** Missing 192.168.1.0/24 for everyday WiFi users
2. **Admin Network Overreach:** Management VLAN has excessive internet access
3. **Service Isolation Gaps:** CCTV system has internet exposure via Frigate
4. **VPN Model:** Too restrictive for normal user needs

### Recommended Network Architecture

#### Zone Structure
```
lan (VLAN 1): 192.168.1.0/24 - Normal users, WiFi clients
├─ Internet: Full access
├─ Services: HA dashboard (8123), NAS (SMB/NFS)
└─ Internal: No direct VLAN access

management (VLAN 10): 192.168.10.0/24 - Admin devices + Proxmox
├─ Internet: Updates only (80,443,specific repos)
├─ Services: Full administrative access
├─ Internal: Full VLAN access for administration
└─ Proxmox: 192.168.10.100 (moved from VLAN 20)

automation (VLAN 20): 192.168.20.0/24 - Home Assistant only
├─ Internet: Specific ports (HA integrations, 443)
├─ Services: Bridge to all service VLANs
├─ Internal: Access to VLANs 30,40,50
└─ VMs: HA VM 192.168.20.101

cctv (VLAN 30): 192.168.30.0/24 - Cameras + Frigate
├─ Internet: None (complete isolation)
├─ Services: Video recording, processing
├─ Internal: Storage access only
└─ VMs: Frigate VM 192.168.30.102 (moved from VLAN 20)

storage (VLAN 40): 192.168.40.0/24 - NAS
├─ Internet: None
├─ Services: File storage, backup
└─ Internal: Serve automation, CCTV, users

iot_sensors (VLAN 50): 192.168.50.0/24 - Safety sensors
├─ Internet: None (critical safety isolation)
├─ Services: Fire safety monitoring
└─ Internal: HA control only
```

### Service Access Model
```
Users (VLAN 1) → HA dashboard, NAS services
VPN Users → Same as local users (not just HA)
Management → Everything (administrative)
HA → All VLANs (integration hub)
Frigate → CCTV + Storage only
```

### Internet Access Policies
```
VLAN 1 (Users): Full internet ✅
VLAN 10 (Management): Updates only ✅
VLAN 20 (HA): Specific ports only ✅
VLAN 30 (CCTV): No internet ✅
VLAN 40 (Storage): No internet ✅
VLAN 50 (IoT): No internet ✅
```

## Configuration Requirements by File

### `/etc/config/network` (Router Config - Missing)
**Purpose:** Network interfaces and VLAN configuration
**Required Elements:**
```bash
# Bridge VLAN configuration for Proxmox trunk port
config bridge-vlan
    option device 'br-lan'
    option vlan '10'
    list ports 'lan1:t'  # Trunk port to Proxmox
    list ports 'lan2:u'  # Management access port

# Network interfaces for each VLAN
config interface 'lan'          # User network 192.168.1.0/24
config interface 'management'   # Admin network 192.168.10.0/24
config interface 'automation'   # HA network 192.168.20.0/24
config interface 'cctv'        # Camera network 192.168.30.0/24
config interface 'storage'     # NAS network 192.168.40.0/24
config interface 'iot_sensors' # Sensor network 192.168.50.0/24
```

### `/etc/config/dhcp` (Router Config - Missing)
**Purpose:** DHCP server configuration for each VLAN
**Required Elements:**
```bash
config dhcp 'lan'        # Users: .100-.199
config dhcp 'management' # Admin: .100-.149
config dhcp 'automation' # HA: .100-.149
config dhcp 'cctv'      # Cameras: .100-.149
config dhcp 'storage'   # NAS: .100-.149
config dhcp 'iot_sensors' # Sensors: .70-.90
```

### `/etc/config/wireless` (Router Config - Not Analyzed)
**Purpose:** WiFi configuration
**Requirements:**
- Main WiFi → VLAN 1 (users)
- Guest WiFi → Isolated network
- IoT WiFi → VLAN 50 (sensors)

### `/etc/config/firewall` (Current File - Needs Revision)
**Purpose:** Security policies only
**Required Changes:**
- Remove network interface creation
- Remove DHCP configuration
- Add user network zone
- Fix internet access policies
- Update VM IP assignments
- Add proper service access rules

## Technical Implementation Details

### Proxmox Trunk Port Configuration
**Physical Connection:** Single Ethernet cable to router
**Switch Port:** lan1 configured as trunk
**VLAN Tags:** Carries 10,20,30,40,50 tagged traffic
**Proxmox Host:** Uses VLAN 10 for management IP
**VM Networking:** Virtual bridges map to specific VLANs

### VM Network Assignment Changes
```
Current:
- Proxmox Host: 192.168.20.100 (VLAN 20)
- HA VM: 192.168.20.101 (VLAN 20)
- Frigate VM: 192.168.20.102 (VLAN 20)

Decided:
- Proxmox Host: 192.168.10.10 (VLAN 10) ← Moved to management, static outside DHCP range
- HA VM: 192.168.20.101 (VLAN 20)
- Frigate VM: 192.168.30.20 (VLAN 30) ← Moved to CCTV
```

### Home Assistant Internet Security
**Current:** Full internet access
**Recommended:** Port-specific access
- 443 (HTTPS for cloud integration)
- Specific integration ports as needed
- Consider reverse proxy for enhanced security
- NAT reflection for local access

### Emergency Access Protocols
**Keep Existing:** Smart plug emergency access from management
**Add:** Emergency HA access from management
**Consider:** Emergency internet bypass for critical updates

## Security Assessment

### Current Security Strengths
✅ Network segmentation philosophy  
✅ Safety system isolation (VLAN 50)  
✅ Emergency protocols with disabled rules  
✅ Comprehensive logging  
✅ Attack port blocking  
✅ SSH rate limiting

### Security Gaps
❌ CCTV system internet exposure (Frigate placement)  
❌ Over-privileged management access  
❌ Missing user network security policies  
❌ No validation of trunk port security  
❌ HA full internet access

### Security Improvements Needed
🔒 Move Frigate to CCTV VLAN (no internet)  
🔒 Restrict management internet to updates only  
🔒 Add user network with controlled service access  
🔒 Limit HA internet to specific ports  
🔒 Implement proper VPN user model

## OpenWrt Best Practices Compliance

### Compliant Elements
✅ UCI configuration system usage  
✅ Proper firewall zone structure concept  
✅ Modern security practices  
✅ Systematic rule organization

### Non-Compliant Elements
❌ Missing DSA switch configuration  
❌ No bridge-vlan configuration for modern OpenWrt  
❌ Incomplete network interface setup  
❌ Configuration scope confusion  
❌ Missing prerequisite network creation

## Action Items

### High Priority (Blocking Issues)

#### 1. Create Router Configuration Files
**Files to Create:**
- `/etc/config/network` - Network interfaces and VLANs
- `/etc/config/dhcp` - DHCP server configuration
- `/etc/config/wireless` - WiFi configuration

**Key Elements:**
- Proxmox trunk port configuration (lan1)
- VLAN interface definitions for all networks
- DHCP scopes with appropriate IP ranges
- Bridge-VLAN configuration for DSA switch

#### 2. Revise Firewall Configuration Scope
**Remove from firewall config:**
- All network interface creation commands
- All DHCP configuration commands
- Bridge-VLAN trunk port setup

**Keep in firewall config:**
- Zone definitions (referencing networks from router config)
- Security rules and policies
- Inter-zone forwarding rules
- Internet access controls

#### 3. Add User Network Zone
**Network:** 192.168.1.0/24 (VLAN 1 or untagged)
**Purpose:** Normal users, WiFi clients
**Access:** Internet + controlled service access (HA dashboard, NAS)
**Security:** No direct VLAN access

### Medium Priority (Architecture Changes)

#### 4. Relocate Proxmox Host
**From:** VLAN 20 (192.168.20.100)
**To:** VLAN 10 (192.168.10.100)
**Rationale:** Infrastructure belongs with management
**Impact:** Update firewall rules, admin access paths

#### 5. Relocate Frigate VM
**From:** VLAN 20 (192.168.20.102)
**To:** VLAN 30 (192.168.30.102)
**Rationale:** CCTV system security isolation
**Impact:** Remove internet access, maintain storage access

#### 6. Revise Internet Access Policies
**Management VLAN:** Reduce to updates only
**Home Assistant:** Specific ports instead of full access
**VPN Model:** Allow broader user service access

### Low Priority (Documentation & Optimization)

#### 7. Update Architecture Documentation
**File:** `docs/decisions/01-network-architecture.md`
**Changes:**
- Add user network (192.168.1.0/24)
- Clarify VLAN numbering (10-50 vs 20-50)
- Document Proxmox placement decision
- Update Frigate placement rationale

#### 8. Network Diagram Corrections
**Missing Elements:**
- User network (192.168.1.0/24)
- Corrected Proxmox placement
- Corrected Frigate placement
- Connection type differentiation

#### 9. Enhanced Validation Procedures
**Add to config:**
- Trunk port functionality tests
- Inter-VLAN isolation verification
- VM connectivity validation
- Service access testing

## Decision Points Required

### 1. VLAN Numbering Standardization
**Option A:** Use VLANs 10-50 (add VLAN 10 to architecture)
**Option B:** Use VLANs 20-50 (remove VLAN 10 from config)
**Option C:** Use VLAN 1 for users + VLANs 10-50

**Recommendation:** Option C - VLAN 1 for users, VLAN 10-50 for infrastructure/services

### 2. Management Network Internet Access
**Option A:** Full internet access (current, excessive)
**Option B:** No internet access (too restrictive)
**Option C:** Updates only (ports 80,443, specific repos)

**Recommendation:** Option C - Updates only for security

### 3. Home Assistant Internet Access Method
**Option A:** Full internet access (current, risky)
**Option B:** No internet access (breaks cloud integration)
**Option C:** Specific ports only (443 + integration ports)
**Option D:** Reverse proxy with port forwarding

**Recommendation:** Option C initially, Option D for enhanced security

### 4. VPN User Landing Network
**Option A:** Dedicated VPN zone (current, restrictive)
**Option B:** Management VLAN (too privileged)
**Option C:** User network (same as WiFi clients)

**Recommendation:** Option C - VPN users = local users

### 5. Configuration File Organization
**Option A:** Single large script (current, problematic)
**Option B:** Separate files by function (recommended)
**Option C:** Separate scripts with dependencies

**Recommendation:** Option B - Proper OpenWrt file structure

## Implementation Order

### Phase 1: Foundation (Critical)
1. Create `/etc/config/network` with all VLAN interfaces
2. Create `/etc/config/dhcp` with DHCP scopes
3. Configure Proxmox trunk port
4. Test basic VLAN connectivity

### Phase 2: Security (High Priority)
1. Revise firewall config scope (remove router elements)
2. Add user network zone and rules
3. Relocate Frigate to CCTV VLAN
4. Implement restricted internet access policies

### Phase 3: Management (Medium Priority)
1. Relocate Proxmox to management VLAN
2. Update VPN access model
3. Test administrative access paths
4. Validate service access from user network

### Phase 4: Documentation & Validation (Low Priority)
1. Update architecture documentation
2. Revise network diagram
3. Implement comprehensive testing
4. Document operational procedures

## Context for Future Sessions

### Key Files Analyzed
- `configs/openwrt/firewall-config.sh` (current firewall script)
- `docs/decisions/01-network-architecture.md` (architecture doc)
- Network diagram (Mermaid format, contained VLAN20 duplication error)

### Configuration Status
- **Router Config:** Missing (network interfaces, DHCP, trunk port)
- **Firewall Config:** Exists but has scope issues and missing elements
- **WiFi Config:** Not analyzed
- **Network Diagram:** Needs corrections for user network and VM placement

### Hardware Context
- **Router:** GL.iNet GL-MT6000 with OpenWrt
- **Proxmox Server:** MINIX NEO Z350-0dB, single Ethernet connection
- **Network:** 4-VLAN security architecture for home automation safety

### Security Model
- **Primary Goal:** Complete isolation of fire safety sensors (VLAN 50)
- **Secondary Goal:** CCTV system isolation (VLAN 30)
- **User Access:** Controlled access to HA dashboard and NAS
- **Admin Access:** Full system administration via management VLAN

### Project Context
- **Overall Project:** Home automation with PrintAirPipe fire safety
- **Current Phase:** Network infrastructure implementation (47% complete)
- **Next Phase:** PrintAirPipe safety system deployment
- **Repository:** Public GitHub repo for configuration tracking

This analysis provides the foundation for completing the network infrastructure phase and moving to safety system implementation.