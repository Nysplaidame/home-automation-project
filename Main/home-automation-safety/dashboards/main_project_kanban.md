---
title: Main Project Kanban Board
description: Visual workflow management for all home automation systems
tags: [kanban, project-management, workflow]
aliases: [Main Project Board]
created: 2025-09-18
modified: 2025-09-23
type: kanban-board
status: active
---

# 📋 Main Project Kanban Board

**Project Context:** [[README|Home Automation Project]] | [[dashboards/main-project-dashboard|Dashboard]]

---

## Backlog

- [ ] **Additional CCTV Cameras** - Expand surveillance coverage #medium
- [ ] **Voice Control Integration** - Amazon Alexa/Google Home setup #low
- [ ] **Advanced Analytics Dashboard** - Grafana with custom metrics #low
- [ ] **Mobile App Development** - Custom control interface #low
- [ ] **Backup Power System** - UPS for critical components #medium #safety-critical
- [ ] **Smart Lighting Integration** - Philips Hue/LIFX automation #medium
- [ ] **Climate Control** - Smart thermostats and environmental monitoring #medium
- [ ] **Security System Expansion** - Door/window sensors, motion detectors #high
- [ ] **Fire Suppression System** - Automatic sprinklers for workshop area #safety-critical
- [ ] **Emergency Power Backup** - UPS for safety systems during outages #safety-critical
- [ ] **Remote Monitoring Alerts** - SMS/email notifications for safety events #high #safety-critical
- [ ] **Backup Ventilation** - Secondary extraction system for redundancy #medium #safety-critical
- [ ] **Emergency Communication** - Two-way radio system for workshop #medium #safety-critical
- [ ] **Raspberry Pi NAS Setup** - Network storage configuration #medium #procedure
- [ ] **Claude MCP AI Integration** - Advanced automation setup #low #procedure
- [ ] **System Testing Procedures** - Comprehensive validation protocols #high #procedure
- [ ] **Backup and Recovery Procedures** - Disaster recovery protocols #medium #procedure
- [ ] **Maintenance Schedules** - Ongoing system care procedures #medium #procedure

## Ready

- [ ] **Network Infrastructure** - [[docs/prompts/01-network-infrastructure|OpenWrt VLAN Setup]] #critical
- [ ] **Hardware Procurement Phase 1** - [[bill-of-materials/hardware/parts-list|Safety Critical Components]] #critical #procurement
- [ ] **3D Printer Setup** - For PrintAirPipe components #high
- [ ] **Development Environment** - Git workflow and documentation standards #high
- [ ] **Home Assistant Installation** - Core automation platform setup #critical #procedure
- [ ] **Frigate NVR Setup** - Video surveillance system #high #procedure
- [ ] **OpenWrt Router Configuration** - Flash firmware and VLAN setup #critical #procedure
- [ ] **Proxmox Installation Guide** - Virtualization platform setup #critical #procedure
- [ ] **PrintAirPipe Assembly Tutorial** - Safety system construction #safety-critical #procedure
- [ ] **PrintAirPipe Electronics Bundle** - ESP32, sensors, servos from DigiKey #safety-critical #procurement
- [ ] **HEPA Filter Set** - H13 grade 125mm filters (2x) #safety-critical #procurement
- [ ] **Activated Carbon Filters** - 125mm VOC removal filters (2x) #safety-critical #procurement
- [ ] **Smart Emergency Plugs** - TP-Link Kasa HS105 (4x) for power cutoff #safety-critical #procurement

## In Progress

- [x] **Project Documentation** - Standardizing YAML frontmatter and linking #high ✅ 2025-09-18
- [x] **System Architecture Planning** - Network topology and VLAN design #high ✅ 2025-09-18
- [ ] **Safety Requirements Analysis** - PrintAirPipe ventilation specs #safety-critical
- [ ] **Interactive Dashboard Development** - Enhanced project tracking interface #medium
- [ ] **Fire Safety Logic Programming** - Emergency detection and response #safety-critical #procedure
- [ ] **Network Security Implementation** - Firewall rules and VLAN isolation #critical #procedure
- [ ] **3D Print PrintAirPipe Components** - Segments, housings, adapters #safety-critical #building
- [ ] **ESP32 Programming** - ESPHome configuration for sensors/controls #safety-critical #building
- [ ] **Servo Damper Assembly** - MG90S servo integration with valve housings #safety-critical #building

## Testing

- [ ] **Documentation Templates** - Session state and system documentation formats #medium
- [ ] **Dashboard Integration** - Dataview queries and interactive elements #medium
- [ ] **Parts List Interactive Checkboxes** - Procurement tracking system #high
- [ ] **ESPHome Controller Setup** - PrintAirPipe programming guide #safety-critical #procedure
- [ ] **Sensor Calibration** - Temperature, pressure, VOC baseline readings #safety-critical #testing
- [ ] **Emergency Shutoff Testing** - Smart plug response time verification #safety-critical #testing
- [ ] **Airflow Verification** - CFM measurements and pressure differential #high #safety-critical #testing

## Complete

- [x] **Initial Project Planning** - Repository setup and basic documentation structure #high
- [x] **Network Architecture Decision** - [[docs/decisions/01-network-architecture|4-VLAN Security Design]] #critical
- [x] **Hardware Requirements Analysis** - [[bill-of-materials/hardware/parts-list|Complete Parts List]] #high
- [x] **Session Management System** - Consistent documentation workflow #medium
- [x] **Project Dashboard Framework** - Base dashboard with dataview queries #high
- [x] **Project Planning Documentation** - Architecture and system design #high #procedure
- [x] **PrintAirPipe STL Files** - Complete 125mm actuator/sensor set #safety-critical £29 ✅ 2025-09-18
- [x] **Smoke Detection System** - MQ-2 sensors with Home Assistant integration #safety-critical #deployed

## Blocked

- [ ] **Proxmox Installation** - Waiting for MINIX mini PC delivery #critical
- [ ] **PoE Switch Selection** - Budget approval needed for 8-port managed switch #high #procurement
- [ ] **3D Printer Access** - Need reliable printer for PrintAirPipe components #critical
- [ ] **Frigate NVR Configuration** - Waiting for camera selection #high #procedure
- [ ] **VM Creation Procedures** - Needs Proxmox installation complete #high #procedure
- [ ] **Sensor Calibration Procedures** - Waiting for hardware procurement #safety-critical #procedure

---

## 📋 Board Settings

**Priority Legend:**

- 🔴 **Critical:** Safety systems, core infrastructure, blocking dependencies
- 🟠 **High:** Primary functionality, user features, major components
- 🟡 **Medium:** Enhancements, optimizations, quality improvements
- 🟢 **Low:** Nice-to-have features, future expansions

**Tag Legend:**

- `#safety-critical` - Safety system components and procedures
- `#procurement` - Hardware acquisition tasks
- `#procedure` - Technical procedures and tutorials
- `#testing` - Verification and validation tasks
- `#building` - Physical construction/assembly
- `#deployed` - Successfully installed and operational

**Column Limits:**

- **In Progress:** Max 4 items (focus constraint)
- **Testing:** Max 3 items (quality control)
- **Blocked:** Items reviewed weekly

**Board Rules:**

1. Safety-critical items bypass normal flow if urgent
2. Items move right only when acceptance criteria met
3. Blocked items must have clear resolution path
4. New items enter via Backlog unless urgent (Ready)
5. Complete items archived monthly to maintain board clarity

**Updated:** September 23, 2025