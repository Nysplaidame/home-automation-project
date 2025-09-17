---
title: "Home Automation Project - Documentation Index"
description: "Master index of all project documentation with comprehensive cross-references"
tags:
  - index
  - navigation
  - documentation
  - home-automation
  - moc
aliases:
  - "Project Index"
  - "Documentation Hub"
  - "Project MOC"
created: 2025-09-16
modified: 2025-09-16
type: index
project_context: "[[Main/home-automation-safety/README|Home Automation Project]]"
---

# 🏠 Home Automation Project - Documentation Index

> **Master Navigation Hub** | [[Main/home-automation-safety/README|📋 Project Overview]] | [[Main/README|🏠 Vault Home]]

## 🎯 Project Quick Start

### Essential Documents
- **📋 Project Overview:** [[Main/home-automation-safety/README|Home Automation Project]] - Current status and roadmap
- **🏗️ Network Architecture:** [[Main/home-automation-safety/docs/decisions/001-network-architecture|Network Architecture Decision]] - 4-VLAN security design
- **📊 Latest Session:** [[Main/home-automation-safety/docs/session-states/session_state_20250912|Repository Setup Session]] - Current development context
- **🔧 Next Steps:** [[Main/home-automation-safety/docs/prompts/01-network-infrastructure-UPDATED|Network Infrastructure]] - Immediate focus area

### Project Status at a Glance
- **Phase:** Network Architecture & Planning (25% complete)
- **Priority:** Network foundation setup
- **Repository:** [home-automation-project](https://github.com/Nysplaidame/home-automation-project)
- **Risk Level:** Low (solid foundation established)

---

## 📚 Documentation Categories

### 🗂️ Session Management
Track development progress and maintain context across Claude sessions.

**Session States:**
- [[Main/home-automation-safety/docs/session-states/session_state_20250912|📦 Repository Setup Complete (2025-09-12)]] - Latest ✅
- [[Main/home-automation-safety/docs/session-states/session_state_20250909|🎯 Initial Planning Session (2025-09-09)]] - Foundation
- [[Main/home-automation-safety/docs/session-states/session-template|📝 Session Template]] - For new sessions

### 🏛️ Architecture & Decisions
Key architectural decisions and their rationale.

**Decision Records:**
- [[Main/home-automation-safety/docs/decisions/001-network-architecture|🔒 001 - Network Architecture Decision]] - 4-VLAN security segmentation

### 🎯 Sub-Project Prompts
Focused implementation guides for each system component.

**Sub-Projects (Implementation Order):**
1. [[Main/home-automation-safety/docs/prompts/01-network-infrastructure-UPDATED|🌐 Network Infrastructure & Security]] - **CURRENT FOCUS**
2. [[Main/home-automation-safety/docs/prompts/02-core-infrastructure|💻 Core Infrastructure (Proxmox)]] - Virtualization platform
3. [[Main/home-automation-safety/docs/prompts/03-printairpipe-ventilation|🔥 PrintAirPipe Ventilation System]] - **SAFETY CRITICAL**
4. [[Main/home-automation-safety/docs/prompts/04-home-assistant-core|🏠 Home Assistant Core]] - Automation hub
5. [[Main/home-automation-safety/docs/prompts/05-cctv-surveillance|📹 CCTV & Surveillance]] - Security monitoring
6. [[Main/home-automation-safety/docs/prompts/06-pi-nas-storage|💾 Pi NAS Storage]] - Data storage
7. [[Main/home-automation-safety/docs/prompts/07-claude-mcp-ai|🤖 Claude MCP Integration]] - AI automation

### 📊 Visual Documentation
Network diagrams and system visualizations.

**Diagrams & Visuals:**
- [[Main/home-automation-safety/docs/diagrams/Network Diagram|🕸️ Network Topology Diagram]] - Visual network design
- Network Mermaid files in `/diagrams/mermaid/`

### 📋 Procedures & Guides
Step-by-step implementation procedures.

**Procedures:**
- [[Main/home-automation-safety/docs/procedures/Git Repository - Setup Procedure|📦 Git Repository Setup]] - Repository initialization
- [[Main/home-automation-safety/docs/procedures/MCP - Claude Integration|🤖 MCP Claude Integration]] - AI setup guide

---

## 🏗️ System Architecture Overview

### 🔒 Network Design (4-VLAN Security Architecture)
Based on [[Main/home-automation-safety/docs/decisions/001-network-architecture|Network Architecture Decision]]:

- **🌐 VLAN 20:** Automation & Management (192.168.20.0/24) - Internet access
- **📹 VLAN 30:** CCTV (192.168.30.0/24) - No internet, HA bridge access
- **💾 VLAN 40:** Storage (192.168.40.0/24) - No internet, Frigate access  
- **🔧 VLAN 50:** IoT Sensors (192.168.50.0/24) - No internet, HA control only

### 🛡️ Safety-Critical Systems
**⚠️ PRIORITY 1 - Fire Safety:**
- [[Main/home-automation-safety/docs/prompts/03-printairpipe-ventilation|PrintAirPipe Ventilation System]]
- Isolated network (VLAN 50)
- Emergency power cutoff capability
- Multiple sensor types (temperature, smoke, VOC)

### 💻 Core Infrastructure Stack
- **Hardware:** MINIX Fanless Mini PC (NEO Z350-0dB)
- **Hypervisor:** [[Main/home-automation-safety/docs/prompts/02-core-infrastructure|Proxmox]] virtualization
- **Network:** [[Main/home-automation-safety/docs/prompts/01-network-infrastructure-UPDATED|GL.iNet GL-MT6000 (OpenWrt)]]
- **Automation:** [[Main/home-automation-safety/docs/prompts/04-home-assistant-core|Home Assistant]]
- **Monitoring:** [[Main/home-automation-safety/docs/prompts/05-cctv-surveillance|Frigate NVR]]

---

## 📁 Repository Structure

### 📂 Physical Structure in Vault
```
Main/
└── home-automation-safety/          # Project root
    ├── README.md                    # Project overview
    ├── docs/                        # Documentation
    │   ├── session-states/          # Claude sessions
    │   ├── decisions/              # Architecture decisions
    │   ├── procedures/             # Step-by-step guides
    │   ├── prompts/               # Sub-project prompts
    │   └── diagrams/              # Visual documentation
    ├── configs/                    # System configurations
    │   ├── openwrt/               # Router configs
    │   ├── home-assistant/        # HA configs
    │   ├── frigate/               # NVR configs
    │   ├── esphome/              # Sensor configs
    │   └── proxmox/              # VM configs
    └── scripts/                   # Automation scripts
```

### 🔗 GitHub Repository
**Repository:** [Nysplaidame/home-automation-project](https://github.com/Nysplaidame/home-automation-project)
- **Status:** ✅ Active and synced
- **Branch:** main
- **Setup:** [[Main/home-automation-safety/docs/procedures/Git Repository - Setup Procedure|Complete]]

---

## 🚀 Implementation Progress

### ✅ Completed Phases
- [x] **Project Planning** - [[Main/home-automation-safety/docs/session-states/session_state_20250909|Initial Planning Session]]
- [x] **Documentation Structure** - [[Main/home-automation-safety/docs/session-states/session_state_20250912|Repository Setup Session]]
- [x] **Network Architecture Design** - [[Main/home-automation-safety/docs/decisions/001-network-architecture|Network Architecture Decision]]

### 🔄 Current Phase: Network Implementation
**Focus:** [[Main/home-automation-safety/docs/prompts/01-network-infrastructure-UPDATED|Network Infrastructure & Security]]

**Immediate Tasks:**
1. Configure OpenWrt VLAN interfaces
2. Implement firewall rules for security segmentation  
3. Set up remote access for Home Assistant
4. Test network isolation and connectivity

### 📅 Upcoming Phases
1. **Core Infrastructure** - Proxmox virtualization setup
2. **Safety Systems** - PrintAirPipe implementation ⚠️ **CRITICAL**
3. **Automation Platform** - Home Assistant deployment
4. **Monitoring Systems** - CCTV and surveillance setup
5. **AI Integration** - Claude MCP connectivity

---

## 🔍 Quick Reference Links

### 🔧 Configuration Files
- **Router:** `configs/openwrt/` - Network and security configs
- **Automation:** `configs/home-assistant/` - HA configurations  
- **Safety:** `configs/esphome/` - PrintAirPipe sensor configs
- **Monitoring:** `configs/frigate/` - NVR configurations
- **Virtualization:** `configs/proxmox/` - VM configurations

### 🌐 External Resources
- **PrintAirPipe Hardware:** [STL Files](https://nerdiy.de/en/product-2/printairpipe-125-actuator-sensor-set-3d-printable-stl-files/)
- **ESPHome Integration:** [Code Repository](https://github.com/Nerdiyde/ESPHomeSnippets/tree/c0135795dc180c6ff4a1306b2f5982ef3db386c3/Snippets/PrintAirPipe)
- **Project Repository:** [GitHub](https://github.com/Nysplaidame/home-automation-project)

### 🏷️ Tag Navigation
Use these tags to find related content:
- `#home-automation` - All project content
- `#session-state` - Development sessions  
- `#architecture-decision` - Design decisions
- `#sub-project` - Implementation prompts
- `#network-security` - Network-related content
- `#fire-safety` - Safety-critical systems
- `#configuration` - Config files and setup

---

## 📋 Next Session Preparation

### 🎯 When Starting Next Claude Session:
1. **Load Context:** Reference [[Main/home-automation-safety/docs/session-states/session_state_20250912|latest session state]]
2. **Use Template:** Copy [[Main/home-automation-safety/docs/session-states/session-template|session template]]
3. **Focus Area:** Begin [[Main/home-automation-safety/docs/prompts/01-network-infrastructure-UPDATED|Network Infrastructure]] implementation
4. **Key Decision:** Implement [[Main/home-automation-safety/docs/decisions/001-network-architecture|Network Architecture Decision]]

### 🔑 Critical Context Points:
- Repository structure complete ✅
- GitHub integration active ✅  
- Network architecture designed ✅
- Ready for OpenWrt router configuration
- Safety systems have highest priority ⚠️

---

**📊 Project Status:** 25% Complete | **🎯 Current Focus:** Network Foundation | **⏭️ Next:** OpenWrt Configuration  
**📅 Last Updated:** September 16, 2025 | **📋 Document Version:** 1.0