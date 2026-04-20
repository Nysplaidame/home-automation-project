---
title: 3D Printing Parts List - Home Automation Project
description: Comprehensive 3D printing requirements for PrintAirPipe ventilation system and safety components
tags: [3d-printing, parts-list, printairpipe, ventilation, safety-critical]
aliases: [3D Printing Parts List, PrintAirPipe Components, 3D Manufacturing List]
created: 2025-09-17
modified: 2025-09-23
type: manufacturing-specification
status: active
---

# 🖨️ 3D Printing Parts List - Home Automation Project

> **Project Context:** [[README|Home Automation Project]] | **Master Index:** [[PROJECT-INDEX|Documentation Hub]]

## 📋 3D Printing Summary by System

| System | Component Count | Estimated Print Time | Material Usage |
|---|---|---|---|
| **PrintAirPipe Ventilation** | 32 components | ~48-60 hours | ~2.5kg filament |
| **Safety Critical Components** | 6 components | ~12-15 hours | ~0.5kg PLA-HT |
| **Support & Integration** | 6 components | ~8-10 hours | ~0.3kg PLA+ |

### System Status Checklist:

- [ ] PrintAirPipe Ventilation
- [ ] Safety Critical Components  
- [ ] Support & Integration

**Total Manufacturing Time:** ~68-85 hours  
**Total Material Usage:** ~3.3kg filament

---

## 🔥 PrintAirPipe Ventilation & Safety System ⚠️ **SAFETY CRITICAL**

> **System Focus:** [[docs/prompts/03-printairpipe-ventilation|PrintAirPipe Ventilation System]]

### PrintAirPipe 3D Printed Components

|Component|Model/Specification|Quantity|Purpose|Print Material|
|---|---|---|---|---|
|**PrintAirPipe Segments**|125mm diameter pipe segments|10x|Main air distribution|PLA+/PLA-HT|
|**Servo Valve Housing**|MG90S servo mount + damper assembly|4x|Automated airflow control|PLA+/PLA-HT|
|**Sensor Housings**|Temperature/pressure sensor mounts|8x|Environmental monitoring|PLA+/PLA-HT|
|**Air Sensor Segments**|Sensor integration pipe segments|2x|Sensor placement integration|PLA+/PLA-HT|
|**Filter Housings**|HEPA/carbon filter mounting|2x|Filtration system support|PLA-HT|
|**Basic Adapters & Connectors**|Various pipe connections|6x|System interconnection|PLA+|

### PrintAirPipe Components Checklist:

- [ ] PrintAirPipe Segments (125mm pipe segments) - 10x
- [ ] Servo Valve Housing (servo mount + damper assembly) - 4x
- [ ] Sensor Housings (temperature/pressure sensor mounts) - 8x
- [ ] Air Sensor Segments (sensor integration segments) - 2x
- [ ] Filter Housings (HEPA/carbon filter mounts) - 2x ⚠️ **PLA-HT Required**
- [ ] Basic Adapters & Connectors (various pipe connections) - 6x

**STL Source:** nerdiy.de PrintAirPipe 125 Actuator & Sensor Set (€29.00)

---

## 📐 Manufacturing Specifications

### Print Quality Requirements

|Parameter|Specification|Purpose|Critical For|
|---|---|---|---|
|**Layer Height**|0.2mm|Structural integrity|Pipe segments, housings|
|**Infill Density**|40%+ structural, 20% housings|Strength vs material efficiency|Load-bearing components|
|**Support Material**|Required for overhangs >45°|Surface quality|Complex geometries|
|**Print Speed**|50mm/s maximum|Quality assurance|All safety-critical parts|

### Print Quality Checklist:

- [ ] Layer Height: 0.2mm configured
- [ ] Infill: 40%+ for structural, 20% for housings
- [ ] Support: Enabled for overhangs >45°
- [ ] Print Speed: Limited to 50mm/s max

---

## 🧵 3D Printing Materials & Supplies

### Filament Requirements

|Material|Specification|Quantity|Purpose|Key Properties|
|---|---|---|---|---|
|**PLA+ Filament**|1.75mm, enhanced strength|2.0kg|PrintAirPipe structural components|High strength, dimensional stability|
|**PLA-HT Filament**|1.75mm, fire-retardant|1.0kg|Safety-critical high-temp components|Fire retardancy, temperature resistance|
|**Support Material**|PVA or HIPS|0.3kg|Complex geometry support|Water soluble or breakaway|

### 3D Printing Materials Checklist:

- [ ] PLA+ Filament (1.75mm, enhanced strength) - 2.0kg
- [ ] PLA-HT Filament (1.75mm, fire-retardant) - 1.0kg ⚠️ **Safety Critical**
- [ ] Support Material (PVA or HIPS) - 0.3kg

**Material Certification:** Fire-rated filament certificates must be retained for safety compliance

---

## 📅 Production Schedule by Phase

### Phase 1: Core Infrastructure (Week 1-2)
- [ ] PrintAirPipe Segments (125mm pipe segments) - 10x
- [ ] Basic Adapters & Connectors (various connections) - 6x

**Phase 1 Totals:** 16 components, ~24 hours print time

### Phase 2: Control Systems (Week 2-3)
- [ ] Servo Valve Housings (servo mount assemblies) - 4x
- [ ] Sensor Housings (temperature/pressure mounts) - 8x

**Phase 2 Totals:** 12 components, ~20 hours print time

### Phase 3: Filtration (Week 3-4) ⚠️ **Safety Critical**
- [ ] Filter Housings (HEPA/carbon filter mounts) - 2x ⚠️ **PLA-HT Required**
- [ ] Air Sensor Segments (sensor integration) - 2x

**Phase 3 Totals:** 4 components, ~14 hours print time

---

## 🎯 Quality Assurance & Testing

### Pre-Print Verification

|Check|Requirement|Purpose|
|---|---|---|
|**STL File Integrity**|Mesh analysis passed|Prevent print failures|
|**Slicer Configuration**|Material profiles loaded|Optimal print settings|
|**Printer Calibration**|Bed leveling, extrusion verified|Dimensional accuracy|
|**Filament Quality**|Diameter consistency ±0.02mm|Reliable feeding|

### Pre-Print Checklist:

- [ ] STL files downloaded and verified from nerdiy.de
- [ ] Slicer settings configured per material type
- [ ] Printer calibrated and test prints successful
- [ ] Filament quality verified (diameter, moisture)

### Post-Print Inspection

|Inspection|Tolerance|Critical For|
|---|---|---|
|**Dimensional Accuracy**|±0.2mm|Assembly fit|
|**Surface Quality**|Layer adhesion intact|Structural integrity|
|**Threading Quality**|Clean, functional|Connections|
|**Structural Defects**|Zero tolerance|Safety components|

### Post-Print Quality Checklist:

- [ ] Dimensional accuracy within ±0.2mm
- [ ] Surface quality acceptable for assembly
- [ ] No structural defects or weak layers
- [ ] Threading (if applicable) clean and functional

---

## 💰 Cost Analysis

### Material Costs

| Material Type | Cost per kg | Quantity | Total Cost |
|---|---|---|---|
| **PLA+ Filament** | £25 | 2.0kg | £50 |
| **PLA-HT Filament** | £35 | 1.0kg | £35 |
| **Support Material** | £30 | 0.3kg | £9 |
| **STL Files** | - | 1 set | €29 (~£25) |

### Cost Breakdown Checklist:

- [ ] **Material Costs:** £94 total filament
- [ ] **STL License:** €29 (~£25) nerdiy.de
- [ ] **Electricity:** ~£15 estimated
- [ ] **Total Project Cost:** ~£134

**Cost per Component:** ~£4.18 average

---

## 🏭 Equipment & Infrastructure

### 3D Printer Requirements

|Specification|Minimum Requirement|Recommended|Purpose|
|---|---|---|---|
|**Build Volume**|200x200x200mm|250x250x250mm|Large pipe segments|
|**Heated Bed**|60°C minimum|80°C|PLA-HT adhesion|
|**Enclosed Chamber**|Not required|Recommended|Temperature stability|
|**Extruder Type**|Direct drive or Bowden|Direct drive preferred|Filament reliability|

### Equipment Checklist:

- [ ] 3D Printer (build volume ≥200x200x200mm)
- [ ] Heated bed capability (≥60°C)
- [ ] Print surface (PEI, glass, or buildtak)
- [ ] Filament storage (dry, temperature controlled)

---

## 📦 Supplier Information

### STL Files & Documentation

| Source | Product | Cost | Purpose |
|---|---|---|---|
| **nerdiy.de** | PrintAirPipe 125 Actuator & Sensor Set | €29.00 | Complete STL collection |
| **GitHub** | ESPHome configuration snippets | Free | Software integration |
| **Discord/Forums** | Community support | Free | Troubleshooting |

### Filament Suppliers

| Category | Supplier | Advantages |
|---|---|---|
| **Premium Materials** | Prusa Research, SUNLU | Quality consistency, certifications |
| **Budget Options** | SUNLU, TECBEARS | Cost-effective, good quality |
| **Specialty Filaments** | Proto-pasta, Polymaker | Advanced materials, fire-rated |

---

## ⚠️ Safety & Manufacturing Notes

### Fire Safety Requirements

|Component Type|Material Requirement|Justification|
|---|---|---|
|**Filter Housings**|PLA-HT Mandatory|High temperature exposure|
|**Sensor Housings**|PLA+ Minimum|Moderate heat exposure|
|**Pipe Segments**|PLA+ Acceptable|Ambient temperature operation|

### Fire Safety Checklist:

- [ ] **PLA-HT Mandatory** for filter housings and high-temperature exposure
- [ ] **Fire-rated filament** certificates retained for compliance
- [ ] **Print environment** well-ventilated during production
- [ ] **Emergency procedures** established for print failures

### Assembly Considerations

- [ ] **Test fit all components** before final installation
- [ ] **Check clearances** for servo movement and sensor access  
- [ ] **Verify airflow paths** are unobstructed
- [ ] **Inspect threaded connections** for proper engagement

---

## 📚 Related Documentation

### Implementation References
- **Hardware List:** [[bill-of-materials/hardware/parts-list|Complete Hardware Parts List]]
- **System Design:** [[docs/prompts/03-printairpipe-ventilation|PrintAirPipe Ventilation System]]
- **Assembly Guide:** *To be created after STL acquisition*

### Configuration Files
- **Print Profiles:** *To be created in configs directory*
- **Quality Standards:** *To be created in docs directory*
- **Session History:** [[docs/session-states/session-template|Development Sessions]]

---

**Document Version:** 1.0  
**Created:** September 17, 2025  
**Last Updated:** September 18, 2025  
**Status:** Active - Pre-Production Phase  
**Related Project:** [[README|Home Automation Project]]

## Next Actions

1. [ ] **Purchase STL files** from nerdiy.de (€29.00)
2. [ ] **Acquire filament materials** (PLA+ 2kg, PLA-HT 1kg)  
3. [ ] **Configure slicer profiles** for optimal print quality
4. [ ] **Begin Phase 1 printing** with pipe segments
5. [ ] **Set up quality control procedures** for safety-critical components