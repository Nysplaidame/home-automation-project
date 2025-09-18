 segments (10x)
   - [ ] Basic adapters & connectors (6x)
   
2. **Phase 2: Control Systems**
   - [ ] Servo valve housings (4x)
   - [ ] Sensor housings (8x)
   
3. **Phase 3: Filtration**
   - [ ] Filter housings (2x) - **PLA-HT Required**
   - [ ] Air sensor segments (2x)

### Estimated Print Times
- **Total Print Time:** ~48-60 hours
- **Material Usage:** ~2.5kg total filament
- **Printer Utilization:** 3-4 weeks (part-time printing)

---
## 🔥 PrintAirPipe Ventilation & Safety System ⚠️ **SAFETY CRITICAL**

> **System Focus:** [[03-printairpipe-ventilation|PrintAirPipe Ventilation System]]

### PrintAirPipe Hardware Components

#### Electronics & Control

|Component|Model|Qty|Purpose|Source|
|---|---|---|---|---|
|**ESP32 Development Board**|ESP32-WROOM-32|2x|Controller for each enclosure|Generic supplier|
|**MG90S Servo Motor**|9g Metal Gear Servo|4x|Damper control (2 per enclosure)|Electronics supplier|
|**USB-C Power Adapter**|5V 3A USB-C PSU|2x|Power for ESP32 + servos|Electronics supplier|
|**Temperature Sensor**|DS18B20 Waterproof|4x|Temperature monitoring|Electronics supplier|
|**Humidity Sensor**|DHT22/AM2302|2x|Humidity monitoring|Electronics supplier|
|**Pressure Sensor**|BMP280|2x|Differential pressure measurement|Electronics supplier|
|**Smoke Detector**|MQ-2 Gas Sensor|2x|Fire/smoke detection|Electronics supplier|
|**VOC Sensor**|SGP30 or CCS811|2x|Volatile organic compound detection|Electronics supplier|
|**Smart Plugs**|TP-Link Kasa HS105|4x|Emergency power cutoff for printers|Electronics retailer|

### PrintAirPipe Electronics Checklist:

- [ ] ESP32 Development Board (ESP32-WROOM-32) - 2x
- [ ] MG90S Servo Motor (9g Metal Gear) - 4x
- [ ] USB-C Power Adapter (5V 3A) - 2x
- [ ] DS18B20 Waterproof Temperature Sensor - 4x
- [ ] DHT22/AM2302 Humidity Sensor - 2x
- [ ] BMP280 Pressure Sensor - 2x
- [ ] MQ-2 Gas Sensor for smoke detection - 2x
- [ ] SGP30 or CCS811 VOC Sensor - 2x
- [ ] TP-Link Kasa HS105 Smart Plugs - 4x

#### 3D Printed Components (STL Files Required)

Source: nerdiy.de STL files

|Component|Description|Quantity|Print Material|
|---|---|---|---|
|**PrintAirPipe Segments**|125mm pipe segments|10x|PLA+/PLA-HT|
|**Servo Valve Housing**|Servo mount + damper assembly|4x|PLA+/PLA-HT|
|**Sensor Housings**|Temperature/pressure sensor mounts|8x|PLA+/PLA-HT|
|**Air Sensor Segments**|Sensor integration segments|2x|PLA+/PLA-HT|
|**Filter Housings**|HEPA/carbon filter mounts|2x|PLA-HT|
|**Adapters & Connectors**|Various pipe connections|6x|PLA+|

### 3D Printed Components Checklist:

- [ ] PrintAirPipe Segments (125mm pipe segments) - 10x
- [ ] Servo Valve Housing (servo mount + damper assembly) - 4x
- [ ] Sensor Housings (temperature/pressure sensor mounts) - 8x
- [ ] Air Sensor Segments (sensor integration segments) - 2x
- [ ] Filter Housings (HEPA/carbon filter mounts) - 2x
- [ ] Adapters & Connectors (various pipe connections) - 6x


### PrintAirPipe-Specific Resources

- **STL Files:** nerdiy.de (€29.00 for complete set)
- **Documentation:** GitHub ESPHome snippets (free)
- **Community:** PrintAirPipe Discord/forums for troubleshooting
#### Filtration System

|Component|Specification|Quantity|Purpose|Source|
|---|---|---|---|---|
|**HEPA Filters**|125mm diameter, H13 grade|2x|Particle filtration|HVAC supplier|
|**Activated Carbon Filter**|125mm diameter|2x|VOC/odor removal|HVAC supplier|
|**120mm Axial Fan**|12V brushless, 2000 RPM|2x|Air movement|Electronics supplier|

### Filtration System Checklist:

- [ ] HEPA Filters (125mm diameter, H13 grade) - 2x
- [ ] Activated Carbon Filter (125mm diameter) - 2x
- [ ] 120mm Axial Fan (12V brushless, 2000 RPM) - 2x

#### Enclosure Integration

|Component|Specification|Quantity|Purpose|Source|
|---|---|---|---|---|
|**Printer Enclosure**|Acrylic/aluminum frame|2x|SLA + FDM printer housing|DIY fabrication|
|**125mm Ducting**|Flexible aluminum duct|10m|Connect enclosures to ventilation|HVAC supplier|
|**Duct Clamps**|125mm hose clamps|10x|Secure duct connections|Hardware store|

### Enclosure Integration Checklist:

- [ ] Printer Enclosure frames (acrylic/aluminum) - 2x
- [ ] 125mm Flexible aluminum duct - 10m
- [ ] 125mm Duct Clamps (hose clamps) - 10x

**PrintAirPipe Resources:**

- **STL Files:** https://nerdiy.de/en/product-2/printairpipe-125-actuator-sensor-set-3d-printable-stl-files/
- **ESPHome Code:** https://github.com/Nerdiyde/ESPHomeSnippets/tree/c0135795dc180c6ff4a1306b2f5982ef3db386c3/Snippets/PrintAirPipe

---

## 🔧 3D Printing Materials & Supplies

### Filament Requirements

|Material|Specification|Quantity|Purpose|Key Properties|
|---|---|---|---|---|
|**PLA+ Filament**|1.75mm, enhanced strength|2kg|PrintAirPipe structural components|High strength, dimensional stability|
|**PLA-HT Filament**|1.75mm, fire-retardant|1kg|Safety-critical high-temp components|Fire retardancy, temperature resistance|

### 3D Printing Materials Checklist:

- [ ] PLA+ Filament (1.75mm, enhanced strength) - 2kg
- [ ] PLA-HT Filament (1.75mm, fire-retardant) - 1kg

### Print Quality Requirements

- **Layer Height:** 0.2mm for structural components
- **Infill:** 40%+ for pipe segments, 20% for housings
- **Support:** Required for overhangs >45°

## 🔍 Quality Assurance

### Pre-Print Checklist
- [ ] STL files downloaded and verified
- [ ] Slicer settings configured per material
- [ ] Printer calibrated and tested
- [ ] Filament quality verified

### Post-Print Inspection
- [ ] Dimensional accuracy within ±0.2mm
- [ ] Surface quality acceptable for assembly
- [ ] No structural defects or weak layers
- [ ] Threading (if applicable) clean and functional

---

## 📚 Related Documentation

### Implementation References
- **Hardware List:** [[main/home-automation-safety/bill-of-materials/hardware/parts-list|Complete Hardware Parts List]]
- **System Design:** [[03-printairpipe-ventilation|PrintAirPipe Ventilation System]]
- **Assembly Guide:** *To be created after STL acquisition*

### Configuration Files
- **Print Profiles:** *To be stored in configs folder*
- **Slicer Settings:** *To be documented after testing*

---

## ⚠️ Safety & Manufacturing Notes

### Fire Safety Requirements
- **PLA-HT Mandatory** for filter housings and high-temperature exposure
- **Fire-rated filament** certificates should be retained
- **Print environment** should be well-ventilated

### Assembly Considerations
- **Test fit all components** before final installation
- **Check clearances** for servo movement and sensor access
- **Verify airflow paths** are unobstructed

---

**Document Version:** 1.0  
**Created:** September 17, 2025  
**Last Updated:** September 17, 2025  
**Status:** Active - Pre-Production Phase  
**Related Project:** [[main/home-automation-safety/README|Home Automation Project]]

## Next Actions
1. **Purchase STL files** from nerdiy.de (€29.00)
2. **Acquire filament materials** (PLA+ 2kg, PLA-HT 1kg)  
3. **Configure slicer profiles** for optimal print quality
4. **Begin Phase 1 printing** with pipe segments