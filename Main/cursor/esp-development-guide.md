---
title: Cursor ESPHome Development Guide
description: Comprehensive guide for using Cursor AI to develop ESPHome configurations for home automation sensors and controllers
tags:
  - cursor
  - esphome
  - esp32
  - sensors
  - development-guide
  - home-automation
  - AI-assisted-development
  - prompt-engineering
  - safety-systems
aliases:
  - ESPHome Cursor Guide
  - ESP32 Development
  - Sensor Programming Guide
  - cursor-esphome
  - ai-iot-development
created: 2025-09-19
modified: 2025-09-19
status: active
type: development-guide
difficulty: intermediate
project_scope: safety-critical-sensor-systems
estimated_setup_time: 2-4 hours
development_approach: bottom-up
project_context: "[[main/home-automation-safety/README|Home Automation Project]]"
related_docs:
  - "[[03-printairpipe-ventilation|PrintAirPipe Ventilation System]]"
  - "[[ai-prompts-for-home-automation-project|Cursor AI Prompts]]"
  - "[[04-home-assistant-core|Home Assistant Core]]"
  - "[[PROJECT-INDEX|Project Documentation Index]]"
  - "[[session_state_20250912|Latest Session State]]"
  - "[[001-network-architecture|Network Architecture Decision]]"
dependencies:
  - Cursor IDE
  - Home Assistant
  - ESPHome addon
  - Git
focus_systems:
  - PrintAirPipe ventilation
  - Fire safety sensors
  - Environmental monitoring
related_projects:
  - home-automation-safety
  - smart-home-integration
parent_guide: "[[ai-prompts-for-home-automation-project|Main Cursor Development Guide]]"
focus_area: ESPHome sensor development and safety systems
---

# Cursor ESPHome Development Guide

> **ESPHome Specialist Guide** | [[ai-prompts-for-home-automation-project|🤖 Main Cursor Guide]] | [[03-printairpipe-ventilation|🔥 PrintAirPipe System]]

## 🎯 Overview

This specialized guide provides comprehensive prompts and strategies for using Cursor AI to develop ESPHome configurations for home automation sensors, with special focus on safety-critical applications like the PrintAirPipe ventilation system. Users report completing complex 1,500-2,000+ line ESPHome applications in weeks instead of months using Cursor's AI assistance.

**Goal**: Build a complex interdependent sensor-actuator system for ventilation control with electrical safety cutoffs using Cursor's AI-powered development workflow.

### 🔗 Guide Relationship
- **Parent Guide:** [[ai-prompts-for-home-automation-project|Cursor AI Prompts for Home Automation]] - Complete system development
- **This Guide:** ESPHome sensor and controller specialization
- **Focus Systems:** [[03-printairpipe-ventilation|PrintAirPipe Ventilation]] + general sensor development
- **Integration:** [[04-home-assistant-core|Home Assistant Core]] connectivity and automation

## 🗏️ ESPHome Architecture Context

### 📊 Hardware Platform Standards
- **Primary Controller:** ESP32-S3 (recommended for reliability and GPIO count)
- **Alternative:** ESP32-C3 (for simpler sensor nodes)
- **Power:** 5V supply with 3.3V logic (industrial reliability)
- **Communication:** WiFi 802.11n with strong signal requirements
- **Programming:** ESPHome YAML configuration with OTA updates

### 🌐 Network Integration
- **Network:** VLAN 50 (IoT Sensors) - 192.168.50.0/24 (per [[001-network-architecture|Network Architecture]])
- **Isolation:** No internet access, Home Assistant communication only
- **Discovery:** ESPHome native API with encryption
- **Backup:** MQTT integration for redundancy
- **Monitoring:** Built-in diagnostics and health reporting
- **Security:** WPA3 WiFi encryption, API authentication, network isolation compliance

### 📊 Project Integration Context  
- **PrintAirPipe System:** [[03-printairpipe-ventilation|Primary safety-critical application]]
- **Home Assistant:** [[04-home-assistant-core|Central automation hub integration]]
- **Repository Location:** `configs/esphome/` - Configuration storage
- **Development Phase:** Safety systems implementation (high priority)
- **Network Security:** [[001-network-architecture|4-VLAN security architecture]] compliance

---

## 🛠️ Cursor IDE Setup for ESPHome Development

### Initial Configuration

1. **Install Cursor IDE**
   - Download from cursor.com
   - Works seamlessly on Mac and Ubuntu systems

2. **Essential Extensions**
   ```
   - ESPHome Language Support
   - ESPHome Snippets
   - Home Assistant Config Helper
   - YAML Support
   - Run In Terminal
   - PlatformIO IDE (for advanced debugging)
   ```

3. **Project Structure Setup**
   ```
   esp-ventilation-project/
   ├── .cursorrules          # AI behavior configuration
   ├── esphome/
   │   ├── main-controller.yaml
   │   ├── sensors.yaml
   │   └── secrets.yaml
   ├── home-assistant/
   │   ├── automations.yaml
   │   └── scripts.yaml
   ├── docs/
   │   ├── requirements.md
   │   └── architecture.md
   └── README.md
   ```

## 📈 Development Approach: Bottom-Up Strategy

### Why Bottom-Up for ESP/HA Projects

**Start with individual components → Build subsystems → Integrate full system**

1. **Sensor Layer First**
   - Individual sensor configurations
   - Test each sensor independently
   - Validate data accuracy

2. **Actuator Layer Second**
   - Basic switch/relay controls
   - PWM fan controls
   - Safety cutoff mechanisms

3. **Logic Layer Third**
   - Automation rules
   - Emergency procedures
   - System orchestration

4. **Integration Layer Last**
   - Home Assistant dashboard
   - Notifications
   - Remote monitoring

### Bottom-Up Advantages
- Easier debugging of individual components
- Incremental testing and validation
- Reduced complexity in AI prompts
- Better error isolation

---

## 🔥 PrintAirPipe-Specific Development
> **Primary Application:** [[03-printairpipe-ventilation|PrintAirPipe Ventilation System]]

### 🚀 PrintAirPipe Hardware Resources
- **STL Files:** [PrintAirPipe 125 Hardware](https://nerdiy.de/en/product-2/printairpipe-125-actuator-sensor-set-3d-printable-stl-files/)
- **ESPHome Code:** [Nerdiyde ESPHome Snippets](https://github.com/Nerdiyde/ESPHomeSnippets/tree/c0135795dc180c6ff4a1306b2f5982ef3db386c3/Snippets/PrintAirPipe)
- **Target Config:** `configs/esphome/printairpipe-controller.yaml`

### 🎡 PrintAirPipe Cursor Development Prompt

```
TASK: Generate PrintAirPipe ESPHome configuration for 3D printing safety ventilation

PROJECT CONTEXT:
- Based on Nerdiyde PrintAirPipe 125 system design
- Integrate with existing STL hardware and ESPHome code base
- Safety-critical fire prevention system for 3D printer enclosures
- Network: VLAN 50 isolation, Home Assistant integration only

HARDWARE INTEGRATION:
- Servo-controlled dampers (125mm ducting system)
- Multi-point temperature monitoring (DS18B20)
- Air quality sensors (SGP30 VOC detection)
- Smoke detection (MQ-2 sensors)
- Emergency power cutoff relays
- Status indicators (LED arrays, buzzer)

SAFETY REQUIREMENTS:
- Independent fire detection and response
- Graduated emergency protocols (warning → action → cutoff)
- Fail-safe operation during network failures
- Manual emergency override capability
- Comprehensive logging and diagnostics
- Multi-sensor validation and redundancy

INTEGRATION SPECS:
- Base existing code from Nerdiyde repository
- Adapt for dual-enclosure setup (SLA + FDM printers)
- Home Assistant dashboard integration
- Emergency automation sequences
- Predictive maintenance monitoring

OUTPUT: Production-ready PrintAirPipe controller configuration
```

---

## 🔥 General Safety-Critical ESPHome Template

```
CONTEXT: Safety-Critical ESPHome Controller Development
Project: Home Automation with Fire Safety Focus
Target: ESP32-based sensor controllers for 3D printing safety

SAFETY REQUIREMENTS:
- Independent operation during network failures
- Fail-safe behavior when sensors malfunction
- Emergency shutdown capabilities with redundancy
- Comprehensive logging and diagnostics
- Watchdog timers and system health monitoring
- Local decision-making without cloud dependencies

HARDWARE SPECIFICATIONS:
- Controller: ESP32-S3-DevKitC-1 (or equivalent)
- Power: 5V/2A regulated supply with backup
- Sensors: [Specify sensor array for current project]
- Actuators: Servo motors, relays, status indicators
- Communication: WiFi only (no Bluetooth for security)

DEVELOPMENT STANDARDS:
- Extensive inline documentation and comments
- Modular component design for maintainability
- Comprehensive error handling and recovery
- Configuration validation and bounds checking
- OTA update capability with rollback protection
- Real-time diagnostics and health reporting

INTEGRATION REQUIREMENTS:
- Home Assistant native API integration
- MQTT backup communication protocol
- Sensor data validation and filtering
- Actuator safety interlocks and limits
- Emergency override and manual control
- Network isolation compliance (VLAN 50)
```

---

## 🚀 Cursor Prompt Engineering for ESP Development

### Essential Prompt Structure

Maximize Cursor effectiveness through systematic planning and advanced prompting techniques:

```
Context: [Project overview]
Current State: [What's already built]
Goal: [Specific task]
Constraints: [Hardware/software limitations]
Expected Output: [File format, structure]
```

### Best Prompting Practices

#### 1. **Component-Specific Prompts**
```
// Example: Sensor Configuration
"Create an ESPHome YAML configuration for:
- DHT22 on GPIO 4 (temperature/humidity)
- BMP280 on I2C (pressure)  
- MQ-2 on ADC pin A0 (smoke detection)

Include proper filtering, calibration, and Home Assistant integration.
Use descriptive entity names and appropriate update intervals."
```

#### 2. **Chain-of-Thought Prompting**
```
"Step by step, create a ventilation automation system:

1. First, analyze sensor thresholds for safety
2. Then, design the logic flow for normal operation
3. Next, implement emergency procedures
4. Finally, add fail-safes and manual overrides

For each step, explain the reasoning and potential failure modes."
```

#### 3. **Few-Shot Learning with Examples**
```
"Based on this working temperature sensor config:
[paste existing working config]

Create a similar configuration for:
- Pressure sensor with the same filtering approach
- Include emergency thresholds above 1013.25 hPa
- Add Home Assistant notifications"
```

### Advanced Cursor Features for ESP Development

#### 4. **Using .cursorrules for Project Consistency**

Create `.cursorrules` file:
```yaml
# ESPHome Development Rules
- Always validate YAML syntax before suggesting
- Use consistent naming: snake_case for entities, PascalCase for friendly names
- Include safety considerations in all actuator configurations
- Suggest appropriate update intervals based on sensor type
- Always include Home Assistant integration patterns
- Consider power consumption in battery-powered designs
- Include error handling and fallback states
- Use semantic versioning for configuration comments
```

#### 5. **Context-Aware Development**
- Use `@` references to include relevant files
- Reference documentation: `@docs/esphome-sensors.md`
- Include existing configs: `@esphome/working-sensor.yaml`
- Label different references appropriately so AI understands context

---

## ⚡ Efficient Cursor Workflows

### 1. **Rapid Prototyping Cycle**

```bash
# Cursor hotkey workflow
Ctrl+L     # Chat with AI about next component
Ctrl+K     # Inline code generation/editing
Ctrl+R     # Compile and upload (custom setup)
Ctrl+`     # Terminal for ESPHome commands
```

### 2. **AI-Assisted Debugging**

When encountering errors:
```
Prompt: "I'm getting this ESPHome compilation error:
[paste error]

Current configuration:
[paste relevant YAML section]

Analyze the issue and provide a corrected configuration with explanation."
```

### 3. **Documentation Generation**
```
Prompt: "Generate comprehensive documentation for this ESP configuration including:
- Hardware connections diagram
- Configuration explanation
- Troubleshooting steps
- Home Assistant integration instructions"
```

---

## 🔧 Component-Specific Development Prompts

### 🌡️ Temperature Monitoring System

```
TASK: Generate ESPHome configuration for multi-point temperature monitoring

SENSOR ARRAY:
- Primary: DS18B20 digital sensors (high accuracy, addressable)
- Secondary: DHT22 for humidity correlation
- Quantity: 4-6 sensors per enclosure
- Placement: Intake, exhaust, internal air, heated bed proximity

SAFETY LOGIC:
- Temperature thresholds: Warning (45°C), Action (55°C), Emergency (70°C)
- Gradient monitoring: Rapid temperature rise detection
- Sensor validation: Cross-reference multiple sensors
- Fail-safe: Assume emergency if sensor fails or gives impossible readings

REQUIREMENTS:
1. Individual sensor addressing and calibration
2. Gradient calculation and trend analysis
3. Configurable threshold alerts with hysteresis
4. Sensor failure detection and reporting
5. Emergency action integration (relay control)
6. Data logging with timestamp correlation

OUTPUT: Complete ESPHome YAML with safety-first design
```

### 💨 Air Quality and Ventilation Control

```
TASK: Generate ESPHome configuration for air quality monitoring and ventilation control

SENSOR INTEGRATION:
- VOC Detection: SGP30 or equivalent for 3D printing fumes
- Particulate Matter: PMS7003 for resin/filament particles  
- Pressure Differential: For ventilation effectiveness monitoring
- Air Flow: For fan speed validation and duct monitoring

ACTUATOR CONTROL:
- Servo Motors: PrintAirPipe damper positioning (0-180°)
- Fan Control: PWM speed control with RPM feedback
- Emergency Valves: Fail-open dampers for emergency ventilation

CONTROL LOGIC:
1. Graduated response based on air quality readings
2. Coordinated ventilation system operation
3. Emergency protocols for high contamination
4. Manual override capabilities
5. System performance monitoring and optimization

SAFETY FEATURES:
- Independent air quality assessment
- Fail-safe ventilation activation
- Contamination level emergency thresholds
- System performance validation
- Manual emergency controls
```

### 🚨 Fire Detection and Emergency Response

```
TASK: Generate ESPHome configuration for fire detection and emergency response

DETECTION ARRAY:
- Smoke Detectors: MQ-2 gas sensors for combustion detection
- Temperature Monitoring: Rapid rise and absolute temperature limits
- Visual Detection: Optional camera integration for flame detection
- Air Quality: VOC spikes indicating combustion

EMERGENCY RESPONSE:
- Power Cutoff: Relay control for 3D printer power disconnection
- Ventilation Override: Maximum ventilation activation
- Alert Systems: Local alarms, network notifications
- Status Indication: LED arrays and audible alerts

SAFETY PROTOCOLS:
1. Multi-sensor confirmation for fire detection
2. Graduated response levels (alert → action → emergency)
3. Manual emergency activation (physical button)
4. System self-testing and validation
5. Backup power consideration for critical functions
6. Network-independent emergency operation

CRITICAL REQUIREMENTS:
- Sub-second emergency response times
- Redundant detection methods
- Fail-safe emergency activation
- Independent operation capability
- Comprehensive event logging
- Manual override and testing procedures
```

---

## 🛠️ Cursor Development Workflows

### 🚀 Initial Controller Setup Workflow

```
Step 1: Hardware Definition
"Generate ESPHome base configuration for ESP32-S3 controller with the following GPIO assignments: [provide pin mapping]. Include comprehensive pin documentation and validation."

Step 2: Network Configuration  
"Add secure WiFi and Home Assistant API integration for VLAN 50 network (192.168.50.x). Include connection monitoring and reconnection logic."

Step 3: Sensor Integration
"@existing_config - Add [sensor type] integration with calibration, error handling, and safety thresholds. Include diagnostic capabilities."

Step 4: Safety Logic
"@updated_config - Implement safety monitoring logic with graduated response levels and emergency protocols. Add comprehensive logging."

Step 5: Testing Framework
"Generate testing procedures and validation scripts for all safety functions and emergency responses."
```

### 🔄 Iterative Development Process

```
Enhancement Workflow:
1. "Review @current_config for potential safety improvements and edge cases"
2. "Add sensor redundancy and cross-validation logic to existing temperature monitoring"
3. "Implement advanced filtering and noise reduction for air quality sensors"
4. "Add predictive maintenance indicators based on sensor trends"
5. "Generate comprehensive documentation and troubleshooting guide"

Performance Optimization:
1. "Analyze @config for resource usage and optimize polling frequencies"
2. "Implement adaptive sampling rates based on current conditions" 
3. "Add data compression and efficient logging mechanisms"
4. "Optimize network communication and reduce bandwidth usage"
```

---

## 📈 Complex System Development Strategy

### Phase 1: Individual Components (Week 1)
```yaml
# Prompt sequence for each sensor:
1. "Create basic [sensor] configuration"
2. "Add filtering and calibration"  
3. "Integrate with Home Assistant"
4. "Add error handling and diagnostics"
```

### Phase 2: Sensor Integration (Week 2)
```yaml
# System integration prompts:
1. "Combine all sensors in single ESP configuration"
2. "Create sensor validation logic"
3. "Add system health monitoring"
4. "Implement data backup strategies"
```

### Phase 3: Actuator Control (Week 3)
```yaml
# Actuator development:
1. "Design safe actuator control logic"
2. "Add manual override capabilities"
3. "Create emergency shutdown procedures"
4. "Implement progressive fan control"
```

### Phase 4: Home Assistant Integration (Week 4)
```yaml
# HA automation development:
1. "Create responsive automation rules"
2. "Add notification systems"
3. "Build diagnostic dashboards"
4. "Implement data logging"
```

---

## 🚀 Beginner Tips for Cursor with ESP Development

- **Start small**: Begin with single sensors before complex systems
- **Use templates**: Train Cursor like a junior engineer - the better you train it, the better it performs
- **Validate everything**: Always test AI-generated configs before deployment

### 💡 Prompt Efficiency Tips
- **Be specific about hardware**: "ESP32 DevKit v1 with GPIO 2 LED" vs "ESP with LED"
- **Include constraints**: Power limitations, physical space, environmental conditions
- **Request explanations**: "Explain why you chose this pin configuration"

### 🔧 Development Workflow
- **Version control everything**: Commit after each working component
- **Use branches**: `feature/smoke-sensor`, `feature/fan-control`
- **Test incrementally**: Don't integrate until individual components work

### 🛠️ Debugging with AI
- **Share complete context**: Include hardware setup, existing config, error messages
- **Ask for alternatives**: "What are 3 different approaches to solve this?"
- **Validation prompts**: "Review this configuration for potential issues"

---

## 💡 Advanced Cursor Techniques

### **Multi-File Code Generation**
```
Prompt: "Generate a complete ESP ventilation system with:
- Main controller YAML
- Sensor definitions file
- Actuator control file  
- Home Assistant automation package
- Installation documentation

Structure as separate files with proper imports."
```

### **Configuration Validation**
```
Prompt: "Review this complete system configuration for:
- Hardware compatibility issues
- Pin conflicts
- Performance bottlenecks
- Safety vulnerabilities
- Home Assistant integration problems

Provide a checklist of potential issues."
```

### **System Optimization**
```
Prompt: "Optimize this ESP configuration for:
- Reduced power consumption
- Faster sensor response times
- More reliable WiFi connectivity
- Better Home Assistant integration
- Enhanced safety features"
```

---

## ⚠️ Common Pitfalls & Solutions

### ❌ **Avoid These Mistakes**
- **Vague prompts**: "Make it work" → "Fix GPIO pin conflict between DHT22 and relay"
- **No context**: Include hardware specs, existing code, error messages
- **Ignoring constraints**: Mention power, memory, pin limitations
- **All-at-once approach**: Build incrementally, not everything simultaneously

### ✅ **Success Patterns**  
- **Iterative development**: Build → Test → Refine → Integrate
- **Comprehensive prompts**: Context + Goal + Constraints + Expected Output
- **Validation focus**: Ask Cursor to review and critique its own suggestions
- **Documentation parallel**: Generate docs alongside code

---

## 🧪 Testing and Validation Prompts

### 🔍 Safety System Testing

```
TASK: Generate comprehensive testing procedures for safety-critical ESPHome controllers

TEST CATEGORIES:
1. Sensor Accuracy and Calibration
   - Individual sensor validation against known standards
   - Cross-sensor correlation and validation
   - Drift detection and long-term stability
   - Environmental condition testing

2. Emergency Response Testing
   - Simulated fire condition response times
   - Power cutoff sequence validation
   - Ventilation emergency activation
   - Communication failure recovery

3. System Integration Testing
   - Home Assistant connectivity and control
   - Network isolation compliance
   - Multi-controller coordination
   - Backup system activation

AUTOMATED TEST SUITES:
- Unit tests for individual sensor functions
- Integration tests for system interactions
- Stress tests for extreme conditions
- Security tests for network isolation
- Performance tests for response times

OUTPUT: Complete testing framework with pass/fail criteria
```

### 📊 Performance Monitoring

```
TASK: Generate ESPHome configuration for comprehensive system monitoring

MONITORING METRICS:
- System Performance: CPU usage, memory consumption, network latency
- Sensor Health: Accuracy drift, response times, failure rates
- Actuator Performance: Servo positioning accuracy, relay cycle counts
- Network Status: Connection stability, packet loss, encryption status
- Safety System Status: Emergency readiness, test cycle compliance

DIAGNOSTIC FEATURES:
1. Real-time dashboard integration
2. Historical trend analysis
3. Predictive maintenance alerts
4. Performance optimization recommendations
5. System health scoring
6. Automated reporting and alerts

IMPLEMENTATION:
- Built-in ESPHome diagnostic sensors
- Custom monitoring components
- Home Assistant integration
- Automated alert generation
- Performance trending and analysis
```

---

## 🏭 Production Deployment Guidelines

### 🔒 Security and Hardening

```
SECURITY CHECKLIST for ESPHome Controllers:

1. Network Security:
   - WiFi WPA3 encryption with strong passwords
   - Home Assistant API encryption enabled
   - MQTT authentication and TLS (if used)
   - MAC address filtering and access control
   - Network isolation compliance (VLAN 50)

2. Firmware Security:
   - OTA password protection
   - Firmware signing and verification
   - Rollback capability for failed updates
   - Boot security and tamper detection
   - Debug interface disabling in production

3. Operational Security:
   - Configuration backup and versioning
   - Access logging and monitoring
   - Regular security updates
   - Penetration testing procedures
   - Incident response planning
```

### 📚 Documentation Standards

```
DOCUMENTATION REQUIREMENTS for each ESPHome controller:

1. Hardware Documentation:
   - GPIO pin assignments and functions
   - Sensor specifications and calibration data
   - Power requirements and consumption
   - Physical installation procedures
   - Troubleshooting and maintenance guides

2. Software Documentation:
   - Configuration file with extensive comments
   - API endpoints and integration guide
   - Safety procedures and emergency protocols
   - Update and maintenance procedures
   - Testing and validation procedures

3. Operations Documentation:
   - Installation and commissioning checklist
   - Routine maintenance schedules
   - Performance monitoring procedures
   - Emergency response procedures
   - Decommissioning and replacement guide
```

---

## 🚨 Emergency Development Scenarios

### ⚡ Rapid Response Development

```
EMERGENCY SCENARIO: Critical sensor failure requiring immediate replacement

RAPID DEVELOPMENT PROMPT:
"Generate emergency ESPHome configuration for immediate deployment replacing failed [sensor type] in safety-critical environment. Prioritize rapid deployment with basic functionality, comprehensive logging, and fail-safe operation. Include minimal testing procedures for immediate validation."

REQUIREMENTS:
- Minimal viable configuration for immediate deployment
- Enhanced logging for troubleshooting
- Conservative safety thresholds
- Manual override capabilities
- Quick validation procedures
```

### 🔧 Field Troubleshooting

```
FIELD SUPPORT PROMPT:
"Generate diagnostic ESPHome configuration to troubleshoot [specific issue] in deployed controller. Include enhanced debugging output, sensor raw data logging, and network connectivity diagnostics."

DIAGNOSTIC FEATURES:
- Verbose logging and debug output
- Sensor raw data exposure
- Network performance metrics
- System resource monitoring
- Remote diagnostic capabilities
```

---

## 🔗 Multi-File Development

```
# Working with related files
"@esphome/common.yaml - Create shared library of common sensor configurations for reuse across multiple controllers"

"@esphome/safety-common.yaml - Extract common safety logic into shared include file"

"Generate controller-specific config that imports @common.yaml and adds local sensors and actuators"
```

### 🧩 Component Libraries

```
# Building reusable components
"Create ESPHome custom component for PrintAirPipe servo control with position feedback and safety limits"

"Generate lambda functions for complex sensor fusion and validation logic"

"@components/air-quality.h - Create advanced air quality assessment algorithm with multi-sensor input"
```

### 🔄 Version Management

```
# Configuration evolution
"@current-config.yaml - Upgrade sensor integration from DHT22 to SHT30 while maintaining compatibility"

"Generate migration procedure for upgrading ESP32 controllers to ESP32-S3 with minimal downtime"

"Create rollback configuration for emergency recovery from failed updates"
```

---

## 📝 Project Management with Cursor

### **Daily Development Routine**
1. **Morning**: Review overnight sensor data, plan day's development
2. **Development**: Use Cursor for 2-3 component iterations  
3. **Testing**: Physical validation of AI-generated configurations
4. **Documentation**: AI-assisted documentation updates
5. **Planning**: Next day's development scope with AI input

### **Quality Assurance Prompts**
```
"Perform a comprehensive code review of this ESP configuration:
- Check for security vulnerabilities
- Verify Home Assistant best practices  
- Identify potential failure points
- Suggest performance improvements
- Validate safety procedures"
```

---

## 🔗 Integration with Main Development Guide

### 🎆 Workflow Integration
**Primary Workflow:** Use [[ai-prompts-for-home-automation-project|main Cursor guide]] for system-wide development, then this guide for ESPHome specialization.

**Development Sequence:**
1. **System Context:** Start with main guide's project context template
2. **ESPHome Focus:** Switch to this guide for sensor development
3. **Integration Testing:** Return to main guide for system integration
4. **Safety Validation:** Use this guide's testing procedures

### 🗂️ File Organization
```
configs/esphome/
├── printairpipe-controller.yaml    # Primary safety system
├── common/
│   ├── common-sensors.yaml      # Shared sensor configs
│   └── safety-common.yaml       # Shared safety logic
└── controllers/
    ├── bedroom-air-quality.yaml # Room monitoring
    └── workshop-sensors.yaml   # General monitoring
```

### 🔄 Cross-Guide References
- **Network Setup:** [[ai-prompts-for-home-automation-project#🌐-1-network-infrastructure-prompt-openwrtrouter|Network Infrastructure Prompt]]
- **HA Integration:** [[ai-prompts-for-home-automation-project#🏠-2-home-assistant-configuration-prompt|Home Assistant Prompt]]  
- **System Testing:** [[ai-prompts-for-home-automation-project#🛠️-general-cursor-usage-tips|General Testing Approach]]
- **This Guide Focus:** ESPHome-specific sensor development and safety systems

---

## Resources & References

- [Cursor Official Documentation](https://cursor.com/docs)
- Community guide for transitioning from ESPHome Builder to Cursor/VSCode
- [ESPHome Documentation](https://esphome.io/)
- [Home Assistant Automation Guide](https://www.home-assistant.io/docs/automation/)

---

**📊 Document Status:** Active Development Guide | **🎯 Focus:** ESPHome Safety Systems  
**📅 Last Updated:** September 19, 2025 | **📋 Document Version:** 1.2

**Related Documents:**
- [[ai-prompts-for-home-automation-project|🤖 Main Cursor Development Guide]]
- [[03-printairpipe-ventilation|🔥 PrintAirPipe Ventilation System]]  
- [[04-home-assistant-core|🏠 Home Assistant Integration]]
- [[PROJECT-INDEX|📂 Project Documentation Index]]
- [[001-network-architecture|🔒 Network Architecture Decision]]

**Safety Notice:**  
⚠️ All ESPHome configurations generated using these prompts must undergo thorough testing before deployment in safety-critical applications. Never deploy untested code to fire safety systems.

**Guide Relationship:**  
🔗 This guide specializes the [[ai-prompts-for-home-automation-project|main Cursor development guide]] for ESPHome sensor development, with primary focus on the [[03-printairpipe-ventilation|PrintAirPipe safety system]].