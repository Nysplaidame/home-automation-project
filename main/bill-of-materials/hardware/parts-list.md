---
title: Complete Hardware Parts List - Home Automation Project
description: Comprehensive hardware requirements list organized by system component and project relevance
tags: [hardware, parts-list, shopping-list]
aliases: [Hardware Parts List, Shopping List]
created: 2025-09-17
modified: 2026-06-06
type: hardware-specification
status: active
---

# Complete Hardware Parts List - Home Automation Project

> **Project Context:** [[README|Home Automation Project]] | **Master Index:** [[PROJECT-INDEX|Documentation Hub]]

## 📋 Hardware Summary by System

| System                     | Component Count | Estimated Cost |
| -------------------------- | --------------- | -------------- |
| **Core Computing**         | 1 device        | ~£320          |
| **Network Infrastructure** | 2 devices       | ~£120          |
| **NVR / Camera Surveillance** | 4-6 devices  | ~£320          |
| **Storage & NAS**          | 2 devices       | ~£160          |
| **Tools & Accessories**    | Various         | ~£120          |

### System Status Checklist:

- [ ] Core Computing
- [ ] Network Infrastructure
- [ ] NVR / Camera Surveillance
- [ ] Storage & NAS
- [ ] Tools & Accessories

**Total Estimated Cost:** ~£1,360

---

💻 Core Computing Platform

|Component|Model|Specifications|Purpose|
|---|---|---|---|
|**Mini PC**|MINISFORUM M1 Pro-125H|Intel Core Ultra 5 125H, 32GB RAM, 1TB NVMe|Proxmox hypervisor host|
|**Operating System**|Proxmox VE installer|Bare-metal hypervisor|Base OS for virtualization|

### Core Computing Checklist:

- [x] MINISFORUM M1 Pro-125H
- [x] Proxmox VE installed

**System Role:** Runs Proxmox with Home Assistant VM 100, monitoring VM 102,
docker-host VM 103, Frigate CT 111 and local-AI CT 114.

---

## 🌐 Network Infrastructure

### Router & Network Equipment

|Component|Model|Specifications|Purpose|
|---|---|---|---|
|**Main Router**|GL.iNet GL-MT6000|4x GbE ports, WiFi 6, OpenWrt compatible|10-segment OpenWrt network architecture|
|**PoE Switch**|8-Port Gigabit PoE Switch|8x PoE+ ports (30W per port), managed|NVR camera power & data|

### Network Equipment Checklist:

- [x] GL.iNet GL-MT6000 Router âœ… 2025-09-18
- [ ] 8-Port Gigabit PoE Switch

**Network Design:** [[docs/decisions/02-printer-vlan-architecture|10-segment security architecture]]

- VLAN 1: LAN/users (192.168.1.0/24)
- VLAN 10: Management (192.168.10.0/24)
- VLAN 20: Automation (192.168.20.0/24)
- VLAN 30: NVR/cameras (192.168.30.0/24)
- VLAN 35: Printers (192.168.35.0/24)
- VLAN 40: Storage (192.168.40.0/24)
- VLAN 50: IoT Sensors (192.168.50.0/24)
- VLAN 60: Monitoring (192.168.60.0/24)
- VLAN 70: DMZ (192.168.70.0/24)
- VLAN 99: Guest (192.168.99.0/24)

---

## 📹 NVR / Camera Surveillance System

> **System Focus:** [[docs/install/phases/04-frigate|Frigate/NVR install phase]]

### NVR Hardware Components

|Component|Model/Specification|Quantity|Purpose|Network Assignment|
|---|---|---|---|---|
|**PoE IP Cameras**|4MP PoE, H.265, IR night vision|4x|Perimeter monitoring|VLAN 30 (NVR)|
|**PoE Switch**|8-port Gigabit PoE+|1x|Camera power & data|VLAN 20 (Management)|
|**NVR Storage**|See OMV NAS section below|-|Recording storage|VLAN 40 (Storage)|
|**CAT6 Cable**|Outdoor rated, 305m roll|1x|Camera connections|Physical layer|
|**RJ45 Connectors**|Waterproof outdoor connectors|8x|Weatherproof connections|Physical layer|

### NVR Hardware Checklist:

- [ ] 4MP PoE IP Cameras (H.265, IR night vision) - 4x
- [ ] 8-port Gigabit PoE+ Switch - 1x
- [ ] CAT6 Cable (outdoor rated, 305m roll) - 1x
- [ ] RJ45 Waterproof outdoor connectors - 8x

**Network Integration:** Frigate NVR on CT 111, isolated VLAN 30, Home Assistant bridge only

---

💾 Storage & NAS System

> **System Focus:** [[docs/install/phases/06-omv-nas|OMV NAS install phase]]

### NAS Hardware Components

|Component|Model/Specification|Quantity|Purpose|Network Assignment|
|---|---|---|---|---|
|**OMV-capable host**|Low-power x86 or suitable NAS hardware|1x|NAS controller|VLAN 40 (Storage)|
|**Storage Drive**|4TB+ HDD/SSD, matched pair preferred|2x|Redundant storage|Local storage|
|**Boot Drive**|Small SSD or reliable flash boot device|1x|OMV boot drive|Local storage|
|**Case/Enclosure**|NAS case or drive enclosure with cooling|1x|Cooling & protection|Physical housing|
|**Network Cable**|CAT6 patch cable|1x|VLAN 40 uplink|lan4|

### NAS Hardware Checklist:

- [ ] OMV-capable NAS host - 1x
- [ ] 4TB+ storage drives - 2x
- [ ] Boot drive - 1x
- [ ] NAS case/enclosure with cooling - 1x
- [ ] CAT6 patch cable - 1x

**Storage Purpose:** Home Assistant backups, Frigate archive storage, Immich media, configuration backups, and general network storage.

---

## 🔨 Tools & Accessories

### Essential Tools

|Tool|Purpose|Priority|
|---|---|---|
|**Crimping Tool**|RJ45 connector installation|HIGH|
|**Network Cable Tester**|Verify cable integrity|MEDIUM|
|**Multimeter**|Electronic troubleshooting|HIGH|
|**Heat Gun**|Heat shrink, cable work|MEDIUM|
|**Drill & Bits**|Mounting holes|HIGH|
|**3D Printer**|PrintAirPipe fabrication|CRITICAL|

### Essential Tools Checklist:

- [ ] Crimping Tool (for RJ45 connectors)
- [ ] Network Cable Tester
- [ ] Multimeter
- [ ] Heat Gun
- [ ] Drill & Bits

### Consumables

| Item                   | Quantity                | Purpose                |
| ---------------------- | ----------------------- | ---------------------- |
| **Heat Shrink Tubing** | Assorted pack           | Cable protection       |
| **Cable Ties**         | 100-pack, various sizes | Cable management       |
| **Electrical Tape**    | 5 rolls                 | Insulation             |
| **Solder & Flux**      | 60/40 rosin core        | Electronic connections |

### Consumables Checklist:

- [ ] Heat Shrink Tubing (assorted pack)
- [ ] Cable Ties (100-pack, various sizes)
- [ ] Electrical Tape - 5 rolls
- [ ] Solder & Flux (60/40 rosin core)

---

## 💰 Budget Breakdown

### Cost Estimates by Category

| Category                     | Low Estimate | High Estimate | Priority |
| ---------------------------- | ------------ | ------------- | -------- |
| **PrintAirPipe Electronics** | £160         | £240          | CRITICAL |
| **Network Equipment**        | £80          | £160          | HIGH     |
| **NVR / Camera System**      | £240         | £400          | MEDIUM   |
| **Storage & NAS**            | £120         | £200          | MEDIUM   |
| **Tools & Consumables**      | £80          | £160          | LOW      |
| **Contingency (15%)**        | £112         | £168          | BUFFER   |

**Total Project Cost:** Â£792 - Â£1,328

### Funding Strategy Checklist:

- [ ] **Phase 1 (Safety Critical):** £240 - Immediate procurement
- [ ] **Phase 2 (Core Functionality):** £320 - Month 1
- [ ] **Phase 3 (Enhancement):** £400 - Month 2
- [ ] **Phase 4 (Optimization):** £240+ - Month 3+

---

## 📦 Supplier Information

### Primary Suppliers

| Category              | Supplier              | Advantages                                |
| --------------------- | --------------------- | ----------------------------------------- |
| **Electronics**       | DigiKey, Mouser       | Component authenticity, technical support |
| **3D Printing**       | Prusa Research, SUNLU | Quality filament, consistent diameter     |
| **Network Equipment** | Amazon Business, CDW  | Competitive pricing, fast shipping        |
| **HVAC Components**   | Local HVAC suppliers  | Professional grade, bulk pricing          |
| **General Hardware**  | Home Depot, Lowe's    | Immediate availability, local pickup      |

---

## 🔍 Quality Assurance & Standards

### Component Selection Criteria

| Criteria               | Requirement                               | Justification               |
| ---------------------- | ----------------------------------------- | --------------------------- |
| **Fire Safety Rating** | UL/CE certified for electrical components | Safety-critical application |
| **Temperature Rating** | -10°C to +60°C minimum                    | Environmental resilience    |
| **IP Rating**          | IP54+ for outdoor network components      | Weather protection          |
| **MTBF Rating**        | >50,000 hours for critical components     | System reliability          |

### Testing Requirements Checklist:

- [ ] All electrical components bench-tested before installation
- [ ] 3D printed parts fit-tested with actual hardware
- [ ] Network equipment verified with VLAN configuration
- [ ] Sensor accuracy calibrated against reference standards

---

## 📚 Related Documentation

### Implementation Guides

- **Network Setup:** [[docs/install/phases/01-router-openwrt|Router/OpenWrt phase]]
- **PrintAirPipe Build:** [[docs/install/phases/11-physical-integrations|Physical integrations phase]]
- **NVR Installation:** [[docs/install/phases/04-frigate|Frigate/NVR phase]]

### Configuration References

- **Hardware Configs:** [[PROJECT-INDEX|System Configurations]]
- **Architecture Decisions:** [[docs/decisions/01-network-architecture|Decision Records]]
- **Session History:** [[docs/session-states/session-template|Development Sessions]]

---

## ⚠️ Safety Considerations

### Critical Safety Requirements

- **Fire-rated components** for all high-temperature applications
- **Emergency shutoff capability** through smart plugs
- **Redundant sensors** for safety-critical measurements
- **Fail-safe operation** if any sensor becomes unresponsive

> **I-1 audit note (hardware failsafe relay):** The current fail-safe is implemented in software via
> Home Assistant automations (input_boolean.ventsys_failsafe). For a safety-critical ventilation
> system, consider adding a hardware failsafe relay that defaults to the safe state (fans ON /
> valves OPEN) on power loss or MCU failure, independent of the HA VM. A normally-closed relay
> wired in series with the fan PWM signal would keep fans running if the ESP32 loses power or
> firmware hangs. This is an architectural recommendation; no firmware change is required to
> implement it, only additional hardware wiring.
- **Proper electrical isolation** between low and high voltage systems

### Installation Safety Checklist:

- [ ] Qualified electrician consulted for high-voltage connections
- [ ] Proper grounding verified for all electrical equipment
- [ ] Arc-fault protection installed for printer circuits
- [ ] Ventilation testing completed before printer operation

---

**Document Version:** 1.0  
**Created:** September 17, 2025  
**Last Updated:** September 18, 2025  
**Status:** Active - Procurement Planning Phase  
**Related Project:** [[README|Home Automation Project]]

## Next Steps

- [ ] Download PrintAirPipe STL files from nerdiy.de
- [ ] Create procurement spreadsheet with supplier links and current pricing
- [ ] Begin Phase 1 purchasing focusing on safety-critical components
- [ ] Set up 3D printing queue for PrintAirPipe components
