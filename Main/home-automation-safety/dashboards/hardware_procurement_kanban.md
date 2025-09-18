---
title: Hardware Procurement Kanban Board  
description: Hardware acquisition and installation tracking with cost management
tags:
  - kanban
  - hardware
  - procurement
  - parts-list
  - budget-tracking
aliases:
  - Hardware Board
  - Procurement Tracker
  - Shopping Board
created: 2025-09-18
modified: 2025-09-18
type: kanban-board
project_context: "[[main/home-automation-safety/README|Home Automation Project]]"
status: active
total_budget: £1360
---

## Research

- [ ] **Security Camera Comparison** - 4MP PoE options, night vision quality #medium ~£240
- [ ] **NAS Drive Selection** - 4TB USB 3.0 reliability comparison #medium ~£160  
- [ ] **Backup Power Solutions** - UPS sizing for critical systems #medium ~£200

## Ordered

- [ ] **MINIX Fanless Mini PC** - NEO Z350-0dB, Intel i3, 32GB RAM, 512GB #critical ~£320
  - **Supplier:** Amazon Business
  - **Order Date:** TBD
  - **Expected:** 3-5 days
  - **Tracking:** [Order number]

## Shipped

- [x] **PrintAirPipe STL Files** - Complete 125mm actuator/sensor set #critical €29 ✅ 2025-09-18
  - **Supplier:** nerdiy.de  
  - **Order Date:** TBD
  - **Status:** Digital download
  - **Files:** Ready for 3D printing

## Received

- [ ] **Sample Item** - Example of received status #placeholder
  - **Delivery Date:** TBD
  - **Condition:** New/Damaged/Returned
  - **Next Action:** Unpack/Inspect/Install

## Installed

- [x] **Example Completed Item** - Shows completed installation #example
  - **Install Date:** 2025-09-17
  - **Status:** Operational
  - **Documentation:** [[link-to-setup-guide]]

***

## 🔧 Installation Queue

### **Ready to Install** 
*Items received and ready for installation*

### **Installation Dependencies**
- [ ] **Mini PC Setup** - Requires: desk space, power outlet, network cable
- [ ] **Router Configuration** - Requires: internet downtime window, backup connection
- [ ] **Camera Installation** - Requires: cable routing, mounting hardware, weather check

### **Installation Schedule**
- **Weekend Projects:** Major installations requiring downtime
- **Weekday Tasks:** Small component additions, software setup
- **Weather Dependent:** Outdoor cable routing, camera mounting

***

## 📋 Procurement Checklist

### **Before Ordering**
- [ ] **Compatibility Check** - Verify component compatibility  
- [ ] **Supplier Research** - Compare prices and reviews
- [ ] **Delivery Planning** - Ensure someone available for delivery
- [ ] **Installation Readiness** - Tools and time available

### **After Delivery**
- [ ] **Immediate Inspection** - Check for damage or missing items
- [ ] **Inventory Update** - Mark as received in parts list
- [ ] **Installation Planning** - Schedule setup and configuration
- [ ] **Documentation** - File warranties and manuals
- [ ] **Supplier Feedback** - Rate delivery and product quality

***

## 🚨 Critical Hardware Alerts

### **Safety Critical Items** 
These items block safety system deployment:
- **ESP32 Controllers** - Required for PrintAirPipe automation
- **Emergency Sensors** - Smoke, VOC, temperature monitoring  
- **Smart Plugs** - Emergency power cutoff capability
- **Ventilation Components** - HEPA filters, fans, ducting

### **Project Blocking Items**
These items block major project phases:
- **Mini PC** - Required for Proxmox/Home Assistant deployment
- **Router** - Required for network segmentation and VLANs
- **3D Printer Access** - Required for PrintAirPipe fabrication

***

**Board Rules:**
1. **Safety First** - Safety-critical items get procurement priority
2. **Budget Limits** - No orders without confirmed budget allocation  
3. **Quality Focus** - Research phase required for major purchases
4. **Delivery Coordination** - Ensure availability for deliveries
5. **Documentation** - All purchases documented with receipts and warranties