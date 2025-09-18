---
title: Complete Hardware Parts List - Home Automation Project
description: Comprehensive hardware requirements list organized by system
  component and project relevance
tags:
  - hardware
  - parts-list
  - project-planning
  - shopping-list
  - component-specifications
aliases:
  - Hardware Parts List
  - Component Requirements
  - Shopping List
created: 2025-09-17
modified: 2025-09-18
type: hardware-specification
project_context: "[[main/home-automation-safety/README|Home Automation Project]]"
status: active
phase: Hardware Planning & Procurement
---
---

title: Complete Hardware Parts List - Home Automation Project description: Comprehensive hardware requirements list organized by system component and project relevance tags:

- hardware
- parts-list
- project-planning
- shopping-list
- component-specifications aliases:
- Hardware Parts List
- Component Requirements
- Shopping List created: 2025-09-17 modified: 2025-09-18 type: hardware-specification project_context: "[[main/home-automation-safety/README|Home Automation Project]]" status: active phase: Hardware Planning & Procurement

---

# 🔧 Complete Hardware Parts List - Home Automation Project

> **Project Context:** [[main/home-automation-safety/README|Home Automation Project]] | **Master Index:** [[PROJECT-INDEX|Documentation Hub]]

## 📋 Hardware Summary by System

| System                     | Component Count | Estimated Cost |
| -------------------------- | --------------- | -------------- |
| **Core Computing**         | 1 device        | ~£320          |
| **Network Infrastructure** | 2 devices       | ~£120          |
| **CCTV Surveillance**      | 4-6 devices     | ~£320          |
| **Storage & NAS**          | 2 devices       | ~£160          |
| **Tools & Accessories**    | Various         | ~£120          |

### System Status Checklist:

- [ ] Core Computing
- [ ] Network Infrastructure
- [ ] CCTV Surveillance
- [ ] Storage & NAS
- [ ] Tools & Accessories

**Total Estimated Cost:** ~£1,360

---

## 🖥️ Core Computing Platform

|Component|Model|Specifications|Purpose|
|---|---|---|---|
|**Mini PC**|MINIX Fanless Mini PC (NEO Z350-0dB)|Intel i3-N350, 32GB DDR4, 512GB M.2 PCIe Gen3|Proxmox hypervisor host|
|**Operating System**|Windows 11 Pro|Licensed OS for Proxmox installation|Base OS for virtualization|

### Core Computing Checklist:

- [ ] MINIX Fanless Mini PC (NEO Z350-0dB)
- [ ] Windows 11 Pro License

**System Role:** Runs Proxmox virtualization with Home Assistant VM (101), Frigate NVR VM (102), and future VMs

---

## 🌐 Network Infrastructure

### Router & Network Equipment

|Component|Model|Specifications|Purpose|
|---|---|---|---|
|**Main Router**|GL.iNet GL-MT6000|4x GbE ports, WiFi 6, OpenWrt compatible|4-VLAN network segmentation|
|**PoE Switch**|8-Port Gigabit PoE Switch|8x PoE+ ports (30W per port), managed|CCTV camera power & data|

### Network Equipment Checklist:

- [x] GL.iNet GL-MT6000 Router ✅ 2025-09-18
- [ ] 8-Port Gigabit PoE Switch

**Network Design:** [[001-network-architecture|4-VLAN Security Architecture]]

- VLAN 20: Automation & Management (192.168.20.0/24)
- VLAN 30: CCTV (192.168.30.0/24)
- VLAN 40: Storage (192.168.40.0/24)
- VLAN 50: IoT Sensors (192.168.50.0/24)

---

## 📹 CCTV Surveillance System

> **System Focus:** [[05-cctv-surveillance|CCTV & Surveillance System]]

### CCTV Hardware Components

|Component|Model/Specification|Quantity|Purpose|Network Assignment|
|---|---|---|---|---|
|**PoE IP Cameras**|4MP PoE, H.265, IR night vision|4x|Perimeter monitoring|VLAN 30 (CCTV)|
|**PoE Switch**|8-port Gigabit PoE+|1x|Camera power & data|VLAN 20 (Management)|
|**NVR Storage**|See Pi NAS section below|-|Recording storage|VLAN 40 (Storage)|
|**CAT6 Cable**|Outdoor rated, 305m roll|1x|Camera connections|Physical layer|
|**RJ45 Connectors**|Waterproof outdoor connectors|8x|Weatherproof connections|Physical layer|

### CCTV Hardware Checklist:

- [ ] 4MP PoE IP Cameras (H.265, IR night vision) - 4x
- [ ] 8-port Gigabit PoE+ Switch - 1x
- [ ] CAT6 Cable (outdoor rated, 305m roll) - 1x
- [ ] RJ45 Waterproof outdoor connectors - 8x

**Network Integration:** Frigate NVR on Proxmox VM, isolated VLAN 30, Home Assistant bridge only

---

## 💾 Storage & NAS System

> **System Focus:** [[06-pi-nas-storage|Pi NAS Storage System]]

### NAS Hardware Components

|Component|Model/Specification|Quantity|Purpose|Network Assignment|
|---|---|---|---|---|
|**Raspberry Pi**|Pi 4 Model B, 8GB RAM|1x|NAS controller|VLAN 40 (Storage)|
|**Storage Drive**|4TB USB 3.0 external HDD|2x|RAID 1 for redundancy|Local storage|
|**MicroSD Card**|64GB Class 10, A2 rated|1x|Pi OS boot drive|Local storage|
|**Pi Case**|Official Pi 4 case with fan|1x|Cooling & protection|Physical housing|
|**USB 3.0 Hub**|Powered 4-port hub|1x|Multiple drive connections|Data connections|

### NAS Hardware Checklist:

- [ ] Raspberry Pi 4 Model B (8GB RAM) - 1x
- [ ] 4TB USB 3.0 external HDD - 2x
- [ ] 64GB Class 10 A2 MicroSD Card - 1x
- [ ] Official Pi 4 case with fan - 1x
- [ ] Powered 4-port USB 3.0 Hub - 1x

**Storage Purpose:** CCTV footage, configuration backups, general network storage

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
| **CCTV System**              | £240         | £400          | MEDIUM   |
| **Storage & NAS**            | £120         | £200          | MEDIUM   |
| **Tools & Consumables**      | £80          | £160          | LOW      |
| **Contingency (15%)**        | £112         | £168          | BUFFER   |

**Total Project Cost:** £792 - £1,328

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

|Criteria|Requirement|Justification|
|---|---|---|
|**Fire Safety Rating**|UL/CE certified for electrical components|Safety-critical application|
|**Temperature Rating**|-10°C to +60°C minimum|Environmental resilience|
|**IP Rating**|IP54+ for outdoor network components|Weather protection|
|**MTBF Rating**|>50,000 hours for critical components|System reliability|

### Testing Requirements Checklist:

- [ ] All electrical components bench-tested before installation
- [ ] 3D printed parts fit-tested with actual hardware
- [ ] Network equipment verified with VLAN configuration
- [ ] Sensor accuracy calibrated against reference standards

---

## 📚 Related Documentation

### Implementation Guides

- **Network Setup:** [[01-network-infrastructure|Network Infrastructure]]
- **PrintAirPipe Build:** [[03-printairpipe-ventilation|Ventilation System]]
- **CCTV Installation:** [[05-cctv-surveillance|Surveillance System]]

### Configuration References

- **Hardware Configs:** [[Main/home-automation-safety/configs/|System Configurations]]
- **Architecture Decisions:** [[Main/home-automation-safety/docs/decisions/|Decision Records]]
- **Session History:** [[Main/home-automation-safety/docs/session-states/|Development Sessions]]

---

## ⚠️ Safety Considerations

### Critical Safety Requirements

- **Fire-rated components** for all high-temperature applications
- **Emergency shutoff capability** through smart plugs
- **Redundant sensors** for safety-critical measurements
- **Fail-safe operation** if any sensor becomes unresponsive
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
**Related Project:** [[main/home-automation-safety/README|Home Automation Project]]

## Next Steps

- [ ] Download PrintAirPipe STL files from nerdiy.de
- [ ] Create procurement spreadsheet with supplier links and current pricing
- [ ] Begin Phase 1 purchasing focusing on safety-critical components
- [ ] Set up 3D printing queue for PrintAirPipe components