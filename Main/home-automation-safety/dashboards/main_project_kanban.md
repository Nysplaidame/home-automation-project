---
title: Main Project Kanban Board
description: Visual workflow management for all home automation systems
tags:
  - kanban
  - project-management
  - workflow
  - home-automation
aliases:
  - Main Project Board
  - System Workflow
created: 2025-09-18
modified: 2025-09-18
type: kanban-board
project_context: "[[main/home-automation-safety/README|Home Automation Project]]"
status: active
---

## Backlog

- [ ] **Additional CCTV Cameras** - Expand surveillance coverage #medium
- [ ] **Voice Control Integration** - Amazon Alexa/Google Home setup #low
- [ ] **Advanced Analytics Dashboard** - Grafana with custom metrics #low
- [ ] **Mobile App Development** - Custom control interface #low
- [ ] **Backup Power System** - UPS for critical components #medium
- [ ] **Smart Lighting Integration** - Philips Hue/LIFX automation #medium
- [ ] **Climate Control** - Smart thermostats and environmental monitoring #medium
- [ ] **Security System Expansion** - Door/window sensors, motion detectors #high

## Ready

- [ ] **Network Infrastructure** - [[main/home-automation-safety/docs/prompts/01-network-infrastructure-UPDATED|OpenWrt VLAN Setup]] #critical
- [ ] **Hardware Procurement Phase 1** - [[main/home-automation-safety/bill-of-materials/hardware/parts-list|Safety Critical Components]] #critical
- [ ] **3D Printer Setup** - For PrintAirPipe components #high
- [ ] **Development Environment** - Git workflow and documentation standards #high
- [ ] **Home Assistant Installation** - Core automation platform setup #critical
- [ ] **Frigate NVR Setup** - Video surveillance system #high

## In Progress

- [ ] **Project Documentation** - Standardizing YAML frontmatter and linking #high
- [ ] **System Architecture Planning** - Network topology and VLAN design #high
- [ ] **Safety Requirements Analysis** - PrintAirPipe ventilation specs #critical
- [ ] **Interactive Dashboard Development** - Enhanced project tracking interface #medium

## Testing

- [ ] **Documentation Templates** - Session state and system documentation formats #medium
- [ ] **Dashboard Integration** - Dataview queries and interactive elements #medium
- [ ] **Parts List Interactive Checkboxes** - Procurement tracking system #high

## Complete

- [x] **Initial Project Planning** - Repository setup and basic documentation structure #high
- [x] **Network Architecture Decision** - [[001-network-architecture|4-VLAN Security Design]] #critical
- [x] **Hardware Requirements Analysis** - [[main/home-automation-safety/bill-of-materials/hardware/parts-list|Complete Parts List]] #high
- [x] **Session Management System** - Consistent documentation workflow #medium
- [x] **Project Dashboard Framework** - Base dashboard with dataview queries #high

## Blocked

- [ ] **Proxmox Installation** - Waiting for MINIX mini PC delivery #critical
- [ ] **PrintAirPipe STL Files** - Need to purchase from nerdiy.de (€29) #critical
- [ ] **PoE Switch Selection** - Budget approval needed for 8-port managed switch #high
- [ ] **3D Printer Access** - Need reliable printer for PrintAirPipe components #critical

***

## Board Settings

**Auto-sync Status:** Enabled  
**Update Frequency:** On file changes  
**Priority Legend:**
- 🔴 **Critical:** Safety systems, core infrastructure, blocking dependencies
- 🟡 **High:** Primary functionality, user features, major components  
- 🟢 **Medium:** Enhancements, optimizations, quality improvements
- ⚪ **Low:** Nice-to-have features, future expansions

**Column Limits:**
- **In Progress:** Max 4 items (focus constraint)
- **Testing:** Max 3 items (quality control)
- **Blocked:** Items reviewed weekly

**Board Rules:**
1. Safety-critical items bypass normal flow if urgent
2. Items move right only when acceptance criteria met
3. Blocked items must have clear resolution path
4. Complete items archived monthly to maintain board clarity
5. New items enter via Backlog unless urgent (Ready)