---
title: Safety Systems Kanban Board
description: Critical safety system implementation tracking with emergency protocols
tags:
  - kanban
  - safety-critical
  - printairpipe
  - fire-safety
  - emergency-systems
aliases:
  - Safety Board
  - Critical Systems
  - Emergency Systems Board
created: 2025-09-18
modified: 2025-09-18
type: kanban-board
project_context: "[[main/home-automation-safety/README|Home Automation Project]]"
status: active
priority: CRITICAL
---

## Planning

- [ ] **Fire Suppression System** - Automatic sprinklers for workshop area #critical
- [ ] **Emergency Power Backup** - UPS for safety systems during outages #critical
- [ ] **Remote Monitoring Alerts** - SMS/email notifications for safety events #high
- [ ] **Backup Ventilation** - Secondary extraction system for redundancy #medium
- [ ] **Emergency Communication** - Two-way radio system for workshop #medium

## Parts Ordered

- [ ] **PrintAirPipe Electronics Bundle** - ESP32, sensors, servos from DigiKey #critical
- [ ] **HEPA Filter Set** - H13 grade 125mm filters (2x) #critical
- [ ] **Activated Carbon Filters** - 125mm VOC removal filters (2x) #critical
- [ ] **Smart Emergency Plugs** - TP-Link Kasa HS105 (4x) for power cutoff #critical

## Building

- [ ] **3D Print PrintAirPipe Components** - Segments, housings, adapters #critical
- [ ] **ESP32 Programming** - ESPHome configuration for sensors/controls #critical
- [ ] **Servo Damper Assembly** - MG90S servo integration with valve housings #critical

## Testing

- [ ] **Sensor Calibration** - Temperature, pressure, VOC baseline readings #critical
- [ ] **Emergency Shutoff Testing** - Smart plug response time verification #critical
- [ ] **Airflow Verification** - CFM measurements and pressure differential #high

## Deployed

- [ ] **Smoke Detection System** - MQ-2 sensors with Home Assistant integration #critical

## Monitoring

*Items move here after successful deployment and verification*

***

## 🚨 Emergency Protocols

### **Fire Detection Response**
1. **Immediate:** Cut power to all printers via smart plugs
2. **Alert:** Sound local alarm + send mobile notifications  
3. **Ventilation:** Activate emergency extraction at maximum speed
4. **Response:** Auto-dial emergency services if threshold exceeded

### **Toxic Gas Detection**
1. **Immediate:** Shut down all printing operations
2. **Evacuation:** Clear workshop area immediately
3. **Ventilation:** Full extraction + fresh air intake
4. **Assessment:** VOC sensor readings logged for analysis

### **System Failure Response** 
1. **Power Loss:** Safety systems on UPS backup power
2. **Sensor Failure:** Fail-safe shutdown of printing operations
3. **Communication Loss:** Local alarms activate independently
4. **Ventilation Failure:** Backup extraction system engages

***

## 📋 Safety Checklist (Pre-Operation)

- [ ] **Sensor Status** - All temperature/pressure/VOC sensors responding
- [ ] **Ventilation Test** - Airflow verified, filters clean
- [ ] **Emergency Cutoff** - Smart plugs tested and responsive
- [ ] **Communication Check** - Home Assistant alerts functional
- [ ] **Manual Override** - Physical emergency stops accessible
- [ ] **Fire Suppression** - Extinguisher charged and accessible

***

## 📊 Safety Metrics Tracking

### **Critical Measurements**
- **VOC Levels:** < 100 ppb baseline, alert at >500 ppb
- **Temperature:** Workshop <30°C, printer enclosure <60°C  
- **Pressure:** Negative pressure maintained in printer enclosures
- **Airflow:** Minimum 200 CFM extraction rate verified

### **Response Times**
- **Emergency Shutoff:** <2 seconds from detection to power cut
- **Alert Delivery:** <30 seconds to mobile notification
- **Ventilation Activation:** <5 seconds to full extraction

***

## 🔧 Maintenance Schedule

### **Weekly Checks**
- [ ] Visual inspection of all sensor housings
- [ ] Test emergency cutoff functions
- [ ] Verify ventilation system operation
- [ ] Check filter condition and airflow

### **Monthly Maintenance** 
- [ ] Sensor calibration verification
- [ ] Filter replacement assessment
- [ ] Emergency protocol drill
- [ ] System response time testing

### **Quarterly Reviews**
- [ ] Complete system safety audit
- [ ] Update emergency contact procedures  
- [ ] Review and update safety thresholds
- [ ] Professional ventilation system inspection

***

## ⚠️ Board Rules - SAFETY CRITICAL

1. **No Bypassing:** Safety items cannot skip testing phase
2. **Dual Verification:** All safety systems require two-person verification
3. **Immediate Escalation:** Any safety concerns stop all other work
4. **Documentation Required:** Every safety system change must be documented
5. **Regular Testing:** Deployed systems tested monthly minimum
6. **Backup Systems:** No single points of failure in safety chains

**Emergency Contact:** [Your emergency contact information]
**Workshop Safety Officer:** [Designated safety person]
**Last Safety Audit:** [Date of last professional review]