---
title: Project Documentation Index
description: Master navigation hub for all project documentation
tags: [index, navigation, home-automation]
aliases: [Project Index, Documentation Hub]
created: 2025-09-15
modified: 2025-09-23
type: index
status: active
---

# 📋 Project Documentation Index

**Master Navigation:** [[README|📋 Overview]] | [[docs/session-states|📂 Sessions]] | [[dashboards/main-project-dashboard|📊 Dashboard]]

## Quick Navigation

**Essential:** [[README|Project Overview]] | [[docs/decisions/01-network-architecture|Network Architecture]] | [[docs/prompts/01-network-infrastructure|Current Focus]]
**Status:** Network Implementation (47% complete) | **Repository:** [GitHub](https://github.com/Nysplaidame/home-automation-project)

## 📂 Documentation Structure

### Session States
- **Latest:** [[docs/session-states|All Sessions]]
- **Templates:** [[docs/session-states/session-template|Concise Template]]

### Implementation Guides  
1. [[docs/prompts/01-network-infrastructure|Network & Security]] - **Current Focus**
2. [[docs/prompts/02-core-infrastructure|Core Infrastructure]]
3. [[docs/prompts/03-printairpipe-ventilation|Safety Systems]]
4. [[docs/prompts/04-home-assistant-core|Home Assistant]]
5. [[docs/prompts/05-cctv-surveillance|CCTV System]]
6. [[docs/prompts/06-pi-nas-storage|Storage]]
7. [[docs/prompts/07-claude-mcp-ai|AI Integration]]

### Architecture & Procedures
- **Decisions:** [[docs/decisions/01-network-architecture|Network Architecture]]
- **Diagrams:** [[docs/diagrams/network|Network Topology]]
- **Procedures:** [[docs/procedures|Setup Guides]]

## 🗃️ System Overview

**Network:** 4-VLAN security architecture (VLANs 20/30/40/50)
**Safety:** PrintAirPipe ventilation with fire detection
**Hardware:** MINIX Z350-0dB + OpenWrt router + Pi NAS
**Software:** Proxmox → Home Assistant + Frigate + Claude MCP

## 📁 File Structure

**Core:** `README.md` (overview) | `TO-DO.md` (tasks) | `PROJECT-INDEX.md` (this file)
**Config:** `configs/` → openwrt, home-assistant, frigate, esphome, proxmox
**Docs:** `docs/` → session-states, procedures, prompts, diagrams, decisions  
**Management:** `dashboards/` → kanban boards, status tracking
**Hardware:** `bill-of-materials/` → parts lists for procurement

## 🚀 Current Progress

**Completed:** Planning, architecture design, documentation structure  
**Current:** [[docs/prompts/01-network-infrastructure|Network Implementation]] - VLAN deployment
**Next:** [[docs/prompts/03-printairpipe-ventilation|Safety Systems]] → [[docs/prompts/02-core-infrastructure|Infrastructure]] → CCTV/AI

## 🔗 Key Links

**Configs:** `configs/openwrt/` (router) | `configs/home-assistant/` (automation) | `configs/esphome/` (safety)
**Resources:** [PrintAirPipe STL](https://nerdiy.de/en/product-2/printairpipe-125-actuator-sensor-set-3d-printable-stl-files/) | [ESPHome Code](https://github.com/Nerdiyde/ESPHomeSnippets/tree/c0135795dc180c6ff4a1306b2f5982ef3db386c3/Snippets/PrintAirPipe)
**Repository:** [GitHub](https://github.com/Nysplaidame/home-automation-project)

## 📋 Next Session Guide

**Load:** [[docs/session-states|Latest Session]] | **Template:** [[docs/session-states/session-template|Concise]]
**Focus:** [[docs/prompts/01-network-infrastructure|Network Implementation]] - VLAN deployment
**Context:** 47% complete, network foundation nearly ready

---
**Updated:** September 23, 2025
