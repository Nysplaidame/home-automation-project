---
title: Home Automation Project - Documentation Index
description: Master index of all project documentation with comprehensive cross-references
tags:
  - index
  - navigation
  - documentation
  - home-automation
  - moc
aliases:
  - Project Index
  - Documentation Hub
  - Project MOC
created: 2025-09-16
modified: 2025-09-16
type: index
project_context: "[[main/home-automation-safety/README|Home Automation Project]]"
---

# 🏠 Home Automation Project - Documentation Index

> **Master Navigation Hub** | [[main/home-automation-safety/README|📋 Project Overview]] | [[main/README|🏠 Vault Home]]

## 🎯 Project Quick Start

### Essential Documents
- **📋 Project Overview:** [[main/home-automation-safety/README|Home Automation Project]] - Current status and roadmap
- **🏗️ Network Architecture:** [[001-network-architecture|Network Architecture Decision]] - 4-VLAN security design
- **📊 Current Sessions:** [[docs/session-states|📂 Session States]] - Latest development context
- **🔧 Next Steps:** [[01-network-infrastructure|Network Infrastructure]] - Immediate focus area

### Project Status at a Glance
- **Phase:** Network Implementation (47% complete)
- **Current Focus:** VLAN deployment and testing
- **Priority:** Complete network foundation (Phase 1: 90% complete)
- **Repository:** [home-automation-project](https://github.com/Nysplaidame/home-automation-project)
- **Risk Level:** Low (solid foundation, safety planning complete)

---

## 📚 Documentation Categories

### 🗂️ Session Management
Track development progress and maintain context across Claude sessions.

**Current Session Context:**
- **Latest Sessions:** [[docs/session-states|📂 Browse All Sessions]] - View all development sessions
- **Session Templates:** [[session-template-complete|📝 Complete Template]] | [[session-template-concise|📝 Concise Template]]
- **Archive:** [[docs/session-states/archive|📂 Completed Sessions]] - Historical development record

**Quick Links to Recent Work:**
- [[session_state_20250918-concise|File Structure & Kanban Creation (2025-09-18)]]
- [[session_state_20250917-concise|Strategic Planning & Analysis (2025-09-17)]]
- [[session_state_20250916-concise|Vault Enhancement & Documentation (2025-09-16)]]

### 🏛️ Architecture & Decisions
Key architectural decisions and their rationale.

**Decision Records:**
- [[001-network-architecture|🔒 001 - Network Architecture Decision]] - 4-VLAN security segmentation

### 🎯 Sub-Project Prompts
Focused implementation guides for each system component.

**Sub-Projects (Implementation Order):**
1. [[01-network-infrastructure|🌐 Network Infrastructure & Security]] - **CURRENT FOCUS**
2. [[02-core-infrastructure|💻 Core Infrastructure (Proxmox)]] - Virtualization platform
3. [[03-printairpipe-ventilation|🔥 PrintAirPipe Ventilation System]] - **SAFETY CRITICAL**
4. [[04-home-assistant-core|🏠 Home Assistant Core]] - Automation hub
5. [[05-cctv-surveillance|📹 CCTV & Surveillance]] - Security monitoring
6. [[06-pi-nas-storage|💾 Pi NAS Storage]] - Data storage
7. [[07-claude-mcp-ai|🤖 Claude MCP Integration]] - AI automation

### 📊 Visual Documentation
Network diagrams and system visualizations.

**Diagrams & Visuals:**
- [[network-diagram|🕸️ Network Topology Diagram]] - Visual network design
- Network Mermaid files in `/diagrams/mermaid/`

### 📋 Procedures & Guides
Step-by-step implementation procedures.

**Procedures:**
- [[git-repository-setup|📦 Git Repository Setup]] - Repository initialization
- [[claude-MCP-integration|🤖 MCP Claude Integration]] - AI setup guide

---

## 🏗️ System Architecture Overview

### 🔒 Network Design (4-VLAN Security Architecture)
Based on [[001-network-architecture|Network Architecture Decision]]:

- **🌐 VLAN 20:** Automation & Management (192.168.20.0/24) - Internet access
- **📹 VLAN 30:** CCTV (192.168.30.0/24) - No internet, HA bridge access
- **💾 VLAN 40:** Storage (192.168.40.0/24) - No internet, Frigate access  
- **🔧 VLAN 50:** IoT Sensors (192.168.50.0/24) - No internet, HA control only

### 🛡️ Safety-Critical Systems
**⚠️ PRIORITY 1 - Fire Safety:**
- [[03-printairpipe-ventilation|PrintAirPipe Ventilation System]]
- Isolated network (VLAN 50)
- Emergency power cutoff capability
- Multiple sensor types (temperature, smoke, VOC)

### 💻 Core Infrastructure Stack
- **Hardware:** MINIX Fanless Mini PC (NEO Z350-0dB)
- **Hypervisor:** [[02-core-infrastructure|Proxmox]] virtualization
- **Network:** [[01-network-infrastructure|GL.iNet GL-MT6000 (OpenWrt)]]
- **Automation:** [[04-home-assistant-core|Home Assistant]]
- **Monitoring:** [[05-cctv-surveillance|Frigate NVR]]

---

## 📁 Repository Structure

### 📂 Physical Structure in Vault
```
Main/
└── home-automation-safety/     # Project root
	├──	bill-of-materials/      # Parts lists
	│	├── 3d-printing/        # Printing parts
	│	└── hardware/           # Hardware parts
	├──	configs/                # System configurations
	│	├── openwrt/            # Router configurations
	│	├── home-assistant/     # HA configs and automations
	│	├── frigate/            # NVR configurations
	│	├── esphome/            # PrintAirPipe and sensor configs
	│	└── proxmox/            # VM configurations
	├──	dashboards/             # Project managemnt
	├──	docs/                   # Documentation and session states
	│	├── session-states/     # Claude session documentation
	│	├── diagrams/           # Visual representation
	│	├── decisions/          # Architecture decisions and rationale
	│	├── procedures/         # Step-by-step procedures
	│	├── prompts/            # Sub-project focused prompts
	│	└── troubleshooting/    # Known issues and solutions
	├──	hardware/               # Physical system documentation
	│	├── stl-files/          # 3D printing files
	│	├── wiring-diagrams/    # Circuit diagrams
	│	└── part-lists/         # Component specifications
	└──	scripts/                # Automation and setup scripts
		├── setup/              # Installation scripts
		├── backup/             # Backup procedures
		└── monitoring/         # Health check scripts
```

### 📂 Detailed Content in Vault
```
main/
├── README.md (vault overview)
└── home-automation-safety/
	├── PROJECT-INDEX.md (master navigation hub)
    ├── README.md (main project doc)
    ├── TO-DO.md (master task list)
    ├── bill-of-materials/
    │   ├── 3d-printing/ (STL files, print configs)
	│   │   └── parts-list.md (interactive shopping list)
    │   └── hardware/
    │       └── parts-list.md (interactive shopping list)
    ├── configs/ (system configurations)
    ├── dashboards/ (project dashboards)
    │	├── hardware-procurement-kanban.md (procurement board)
    │   ├── main-project-dashboard.md (dataview dashboard)
	│   ├── main-project-kanban.md (workflow board)
	│   ├── major-procedures-kanban.md (procedures board)
	│	└── safety-systems-kanban.md (safety board)
    ├── docs/
    │   ├── decisions/ (ADRs)
    │   │   └── 001-network-architecture.md
    │   ├── diagrams/ (network topology, visuals, wiring diagrams)
    │   │   ├── mind-map/
	│   │   │   └── excalibrain.md (mind map)
    │   │   ├── network/
	│   │   │   ├── network-diagram.md
	│	│   │   └── network-diagram-new.md
    │   │   └── wiring-diagrams/ (physical setup)
    │   ├── procedures/ (setup procedures)
    │   │   ├── claude-MCP-integration.md
    │   │   └── git-repository-setup.md
    │   ├── prompts/ (implementation guides)
    │   │   ├── 01-network-architecture.md
    │   │   ├── 02-core-infrastructure.md
    │   │   ├── 03-printairpipe-ventilation.md
    │   │   ├── 04-home-assistant-core.md
    │   │   ├── 05-cctv-surveillance.md
    │   │   ├── 06-pi-nas-storage.md
    │   │   └── 07-claude-mcp-ai.md
    │   └── session-states/ (conversation logs)
    │       ├── archive/ (completed sessions)
    │       │	├── session-state-20250909.md
    │       │	├── session-state-20250912.md
    │       │	├── session-state-20250916.md
    │       │	└── session-state-20250917.md
    │       ├── session-state-20250909-concise.md
    │       ├── session-state-20250912-concise.md
    │       ├── session-state-20250916-concise.md
    │       ├── session-state-20250917-concise.md
    │       ├── session-state-20250918-concise.md
    │       ├── session-template-complete.md
    │       └── session-template-concise.md
    └── scripts/ (automation scripts)
    	├── setup/
		├── backup/
		└── monitoring/
```

### 🔗 GitHub Repository
**Repository:** [Nysplaidame/home-automation-project](https://github.com/Nysplaidame/home-automation-project)
- **Status:** ✅ Active and synced
- **Branch:** main
- **Setup:** [[git-repository-setup|Complete]]

---

## 🚀 Implementation Progress

### ✅ Completed Phases
- [x] **Project Planning** - [[session_state_20250909|Initial Planning Session]]
- [x] **Documentation Structure** - [[session_state_20250912|Repository Setup Session]]
- [x] **Network Architecture Design** - [[001-network-architecture|Network Architecture Decision]]

### 🔄 Current Phase: Network Implementation
**Focus:** [[01-network-infrastructure|Network Infrastructure & Security]]

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
1. **Load Context:** Reference [[session_state_20250912|latest session state]]
2. **Use Template:** Copy [[session-template-complete|session template]]
3. **Focus Area:** Begin [[01-network-infrastructure|Network Infrastructure]] implementation
4. **Key Decision:** Implement [[001-network-architecture|Network Architecture Decision]]

### 🔑 Critical Context Points:
- Repository structure complete ✅
- GitHub integration active ✅  
- Network architecture designed ✅
- Ready for OpenWrt router configuration
- Safety systems have highest priority ⚠️

---

**📊 Project Status:** 47% Complete | **🎯 Current Focus:** VLAN Deployment | **⏭️ Next:** Network Testing & Validation  
**📅 Last Updated:** September 16, 2025 | **📋 Document Version:** 1.0