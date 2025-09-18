---
title: Home Automation Project - Master Dashboard
description: Macro-level project tracking dashboard showing system status and task completion
tags:
  - project-dashboard
  - dataview
  - project-management
  - overview
aliases:
  - Project Dashboard
  - Master Status
  - Project Overview
created: 2025-09-18
modified: 2025-09-18
type: dashboard
project_context: "[[main/home-automation-safety/README|Home Automation Project]]"
status: active
phase: Multi-Phase Implementation
---
---

title: Home Automation Project - Interactive Dashboard description: Comprehensive interactive project tracking with Kanban boards, task management, and progress visualization tags:

- project-dashboard
- dataview
- kanban
- tasks
- project-management
- overview
- interactive aliases:
- Project Dashboard
- Master Dashboard
- Interactive Tracker
- Project Control Center created: 2025-09-18 modified: 2025-09-18 type: dashboard status: active phase: Multi-Phase Implementation project_context: "[[main/home-automation-safety/README|Home Automation Project]]" cssclasses: dashboard

---

# 🏠 Home Automation Project - Interactive Dashboard

> **Live Project Tracking** | **Auto-Updated:** `=date(now)` | **Phase:** Multi-System Implementation
> 
> **Quick Links:** [[main/home-automation-safety/README|📋 Project Overview]] | [[PROJECT-INDEX|🗂️ Master Index]] | [[main/home-automation-safety/bill-of-materials/hardware/parts-list|🛒 Shopping List]]

---

## 🚨 Critical Safety Systems Status

> **⚠️ SAFETY FIRST** - These systems have safety implications and require priority monitoring

```dataview
TABLE WITHOUT ID
  file.link as "System",
  choice(status = "completed", "✅", choice(status = "in-progress", "🔄", choice(status = "blocked", "🚫", choice(status = "planning", "📝", "⏸️")))) as "Status",
  choice(priority = "CRITICAL", "🔴", choice(priority = "HIGH", "🟡", "🟢")) as "Priority",
  started as "Started",
  completed as "Completed"
FROM #home-automation AND #safety-critical
WHERE status != "completed"
SORT priority DESC, file.name ASC
```

### Safety System Quick Actions

- [ ] **PrintAirPipe Ventilation** - Emergency shutoff capability implemented
- [ ] **Fire Detection** - Smoke/VOC sensors operational
- [ ] **Temperature Monitoring** - Critical temperature thresholds configured
- [ ] **Emergency Communications** - Alert system tested and functional

---

## 📊 Project Health Overview

### Phase Progress Summary

```dataview
TABLE WITHOUT ID
  phase as "Phase",
  length(filter(rows, (r) => r.status = "completed")) as "✅ Complete",
  length(filter(rows, (r) => r.status = "in-progress")) as "🔄 Active", 
  length(filter(rows, (r) => r.status = "planning")) as "📝 Planned",
  length(filter(rows, (r) => r.status = "blocked")) as "🚫 Blocked",
  round(length(filter(rows, (r) => r.status = "completed")) / length(rows) * 100, 1) + "%" as "% Done"
FROM #home-automation
WHERE type != "template" AND type != "dashboard"
GROUP BY phase
SORT phase ASC
```

### System Status Distribution

```dataview
TABLE WITHOUT ID
  status as "Status",
  length(rows) as "Count",
  round(length(rows) / length(filter(dv.pages("#home-automation"), (p) => p.type != "template" AND p.type != "dashboard")) * 100, 1) + "%" as "Percentage"
FROM #home-automation
WHERE type != "template" AND type != "dashboard"
GROUP BY status
SORT length(rows) DESC
```

---

## 📋 Interactive Task Management

### 🎯 Current Sprint Tasks

```tasks
not done
heading includes Current Sprint
sort by priority
group by heading
```

### 🔥 Priority Actions Needed

```dataview
TASK
FROM #home-automation
WHERE status = "blocked" OR status = "waiting" OR contains(lower(description), "urgent")
SORT priority DESC, due ASC
```

### 📅 Recently Completed (Last 7 Days)

```dataview
TABLE WITHOUT ID
  file.link as "System",
  completed as "Completed Date",
  description as "Achievement"
FROM #home-automation
WHERE completed >= date(today) - dur(7 days)
SORT completed DESC
LIMIT 10
```

---

## 🏗️ System Implementation Status

### 🚀 Ready to Start

```dataview
TABLE WITHOUT ID
  file.link as "System",
  choice(priority = "CRITICAL", "🔴", choice(priority = "HIGH", "🟡", "🟢")) as "Priority",
  phase as "Phase",
  description as "Next Actions"
FROM #home-automation
WHERE status = "ready" OR status = "planned"
SORT priority DESC, phase ASC
LIMIT 5
```

### 🔄 Currently In Progress

```dataview
TABLE WITHOUT ID
  file.link as "System", 
  started as "Started",
  choice(priority = "CRITICAL", "🔴", choice(priority = "HIGH", "🟡", "🟢")) as "Priority",
  description as "Current Focus"
FROM #home-automation
WHERE status = "in-progress" OR status = "implementing"
SORT started ASC
```

### 🚫 Blocked Systems

```dataview
TABLE WITHOUT ID
  file.link as "System",
  choice(priority = "CRITICAL", "🔴", choice(priority = "HIGH", "🟡", "🟢")) as "Priority",
  description as "Blocking Issue",
  file.mtime as "Last Updated"
FROM #home-automation
WHERE status = "blocked" OR status = "waiting"
SORT priority DESC, file.mtime ASC
```

---

## 🛒 Procurement & Hardware Status

### Hardware Acquisition Progress

```dataview
TABLE WITHOUT ID
  file.link as "Component Category",
  choice(status = "ordered", "📦 Ordered", choice(status = "delivered", "✅ Received", choice(status = "installed", "🔧 Installed", "📝 Needed"))) as "Status",
  estimated_cost as "Est. Cost",
  supplier as "Supplier"
FROM #hardware OR #parts-list
SORT status ASC, estimated_cost DESC
```

### Procurement Checklist

- [ ] **Phase 1 (Safety Critical)** - £240 budget allocated
- [ ] **PrintAirPipe Electronics** - ESP32, sensors, servos
- [ ] **3D Printing Materials** - PLA+, PLA-HT filaments
- [ ] **Network Equipment** - Router, PoE switch, cables
- [ ] **Tools & Consumables** - Crimping tools, multimeter

---

## 📡 Network & Infrastructure

### VLAN Implementation Status

```dataview
TABLE WITHOUT ID
  file.link as "VLAN",
  vlan_id as "ID",
  ip_range as "IP Range",
  choice(status = "configured", "✅", choice(status = "testing", "🧪", choice(status = "planning", "📝", "❌"))) as "Status",
  purpose as "Purpose"
FROM #network AND #vlan
SORT vlan_id ASC
```

### Infrastructure Systems

```dataview
TABLE WITHOUT ID
  file.link as "System",
  choice(status = "online", "🟢 Online", choice(status = "configuring", "🟡 Config", choice(status = "offline", "🔴 Offline", "⚪ Pending"))) as "Status",
  ip_address as "IP Address",
  last_checked as "Last Check"
FROM #infrastructure OR #network-device
SORT status DESC, file.name ASC
```

---

## 💾 Storage & Backup Status

### Storage Systems Health

```dataview
TABLE WITHOUT ID
  file.link as "Storage System",
  capacity as "Capacity",
  used_space as "Used",
  choice(status = "healthy", "🟢 Healthy", choice(status = "warning", "🟡 Warning", choice(status = "critical", "🔴 Critical", "⚪ Unknown"))) as "Health",
  last_backup as "Last Backup"
FROM #storage OR #nas OR #backup
SORT status ASC, capacity DESC
```

---

## 🎮 Interactive Controls

### Quick Actions

```button
name Add New System
type command
action QuickAdd: New Home Automation System
```

```button
name Weekly Review
type command
action Templater: Weekly Project Review
```

```button
name Update Dashboard
type command
action Dataview: Refresh All Views
```

### Project Maintenance Checklist

- [ ] **Weekly:** Update system status in individual files
- [ ] **Weekly:** Review blocked items and resolve dependencies
- [ ] **Monthly:** Archive completed systems documentation
- [ ] **Monthly:** Update procurement status and costs
- [ ] **Quarterly:** Review project priorities and phase planning

---

## 📈 Progress Analytics

### Completion Trends (Last 30 Days)

```dataview
TABLE WITHOUT ID
  date(completed) as "Date",
  count(rows) as "Systems Completed"
FROM #home-automation
WHERE completed >= date(today) - dur(30 days)
GROUP BY date(completed)
SORT date(completed) DESC
```

### Time Investment by Phase

```dataview
TABLE WITHOUT ID
  phase as "Phase",
  sum(rows.time_invested) as "Hours Invested",
  count(filter(rows, (r) => r.status = "completed")) as "Systems Done",
  round(sum(rows.time_invested) / count(filter(rows, (r) => r.status = "completed")), 1) + "h" as "Avg Time/System"
FROM #home-automation
WHERE time_invested AND time_invested > 0
GROUP BY phase
SORT sum(rows.time_invested) DESC
```

---

## 🔧 Kanban Board Integration

> **Note:** Create dedicated Kanban boards for each major system using the Kanban plugin:

### Main Project Board

- **File:** `kanban-main-project.md`
- **Columns:** Backlog | Ready | In Progress | Testing | Complete | Blocked
- **Auto-sync:** Link to system status fields

### Safety Systems Board

- **File:** `kanban-safety-systems.md`
- **Columns:** Planning | Parts Ordered | Building | Testing | Deployed | Monitoring
- **Priority:** Safety-critical items always visible

### Hardware Procurement Board

- **File:** `kanban-hardware.md`
- **Columns:** Research | Budget Approval | Ordered | Shipped | Received | Installed
- **Integration:** Link to parts list checkboxes

---

## 🎯 Goals & Milestones

### Current Sprint Goals

- [ ] **Network Foundation** - Complete VLAN setup and router configuration
- [ ] **Safety Priority** - Implement PrintAirPipe ventilation monitoring
- [ ] **Hardware Acquisition** - Order Phase 1 critical components
- [ ] **Documentation** - Standardize all system documentation formats

### Monthly Milestones

```dataview
TABLE WITHOUT ID
  milestone as "Milestone",
  target_date as "Target",
  choice(status = "completed", "✅", choice(status = "on-track", "🟢", choice(status = "at-risk", "🟡", "🔴"))) as "Status",
  systems_involved as "Systems Count"
FROM #milestone
WHERE target_date >= date(today) - dur(30 days)
SORT target_date ASC
```

---

## 🔗 System Interconnections

### Dependency Visualization

```dataview
TABLE WITHOUT ID
  file.link as "System",
  dependencies as "Depends On",
  dependents as "Enables"
FROM #home-automation
WHERE dependencies OR dependents
SORT length(dependents) DESC
```

---

## 🏷️ Tag Management for Dashboard

### Required Tags for Dashboard Inclusion

For **system tracking**, ensure YAML frontmatter includes:

```yaml
tags:
  - home-automation
  - [specific-system-tag]
status: [planning|ready|in-progress|testing|completed|blocked|waiting]
priority: [CRITICAL|HIGH|MEDIUM|LOW]
phase: [Phase 1|Phase 2|etc.]
started: [YYYY-MM-DD]
completed: [YYYY-MM-DD] 
```

For **safety-critical systems**, add:

```yaml
tags:
  - safety-critical
emergency_procedures: [link-to-procedures]
```

For **hardware/procurement**, add:

```yaml
tags:
  - hardware|parts-list
estimated_cost: [£amount]
supplier: [supplier-name]
```

---

## 🔄 Auto-Refresh Settings

```dataview
TABLE WITHOUT ID
  "Dashboard auto-refreshes every 5 minutes" as "Status",
  "Last updated: " + string(date(now)) as "Timestamp"
FROM ""
WHERE file.name = this.file.name
LIMIT 1
```

---

**Dashboard Version:** 2.0  
**Interactive Features:** Kanban integration, task management, real-time updates  
**Update Frequency:** Automatic based on file changes + manual refresh buttons  
**Optimization:** Designed for ad-hoc project workflow without rigid deadlines

> **💡 Usage Tips:**
> 
> - Update individual system files - dashboard reflects changes automatically
> - Use Quick Actions buttons for common tasks
> - Leverage Kanban boards for visual project management
> - Focus on 'started' and 'completed' dates rather than deadlines
> - Mark safety-critical items with appropriate tags for priority visibility