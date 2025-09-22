---
title: Project Documentation Index
description: Master navigation hub for all project documentation
tags: [index, navigation, home-automation]
aliases: [Project Index, Documentation Hub]
type: index
---

# ðŸ“‹ Project Documentation Index

**Master Navigation:** [[README|ðŸ“‹ Overview]] | [[docs/session-states|ðŸ“‚ Sessions]] | [[dashboards/main-project-dashboard|ðŸ“Š Dashboard]]

## Quick Navigation

**Essential:** [[README|Project Overview]] | [[01-network-architecture|Network Architecture]] | [[01-network-infrastructure|Current Focus]]
**Status:** Network Implementation (47% complete) | **Repository:** [GitHub](https://github.com/Nysplaidame/home-automation-project)

## ðŸ“‚ Documentation Structure

### Session States
- **Latest:** [[docs/session-states|All Sessions]]
- **Templates:** [[session-state-template|Concise Template]]

### Implementation Guides  
1. [[01-network-infrastructure|Network & Security]] - **Current Focus**
2. [[02-core-infrastructure|Core Infrastructure]]
3. [[03-printairpipe-ventilation|Safety Systems]] 
4. [[04-home-assistant-core|Home Assistant]]
5. [[05-cctv-surveillance|CCTV System]]
6. [[06-pi-nas-storage|Storage]]
7. [[07-claude-mcp-ai|AI Integration]]

### Architecture & Procedures
- **Decisions:** [[01-network-architecture|Network Architecture]]
- **Diagrams:** [[docs/diagrams/network|Network Topology]]
- **Procedures:** [[docs/procedures|Setup Guides]]

## ðŸ—ï¸ System Overview

**Network:** 4-VLAN security architecture (VLANs 20/30/40/50)
**Safety:** PrintAirPipe ventilation with fire detection
**Hardware:** MINIX Z350-0dB + OpenWrt router + Pi NAS
**Software:** Proxmox â†’ Home Assistant + Frigate + Claude MCP

## ðŸ“ File Structure

**Core:** `README.md` (overview) | `TO-DO.md` (tasks) | `PROJECT-INDEX.md` (this file)
**Config:** `configs/` â†’ openwrt, home-assistant, frigate, esphome, proxmox
**Docs:** `docs/` â†’ session-states, procedures, prompts, diagrams, decisions  
**Management:** `dashboards/` â†’ kanban boards, status tracking
**Hardware:** `bill-of-materials/` â†’ parts lists for procurement

## ðŸš€ Current Progress

**Completed:** Planning, architecture design, documentation structure  
**Current:** [[01-network-infrastructure|Network Implementation]] - VLAN deployment
**Next:** [[03-printairpipe-ventilation|Safety Systems]] â†’ [[02-core-infrastructure|Infrastructure]] â†’ CCTV/AI

## ðŸ”— Key Links

**Configs:** `configs/openwrt/` (router) | `configs/home-assistant/` (automation) | `configs/esphome/` (safety)
**Resources:** [PrintAirPipe STL](https://nerdiy.de/en/product-2/printairpipe-125-actuator-sensor-set-3d-printable-stl-files/) | [ESPHome Code](https://github.com/Nerdiyde/ESPHomeSnippets/tree/c0135795dc180c6ff4a1306b2f5982ef3db386c3/Snippets/PrintAirPipe)
**Repository:** [GitHub](https://github.com/Nysplaidame/home-automation-project)

## ðŸ“‹ Next Session Guide

**Load:** [[docs/session-states|Latest Session]] | **Template:** [[session-state-template|Concise]]
**Focus:** [[01-network-infrastructure|Network Implementation]] - VLAN deployment
**Context:** 47% complete, network foundation nearly ready

---
**Updated:** September 21, 2025
