---
title: Cursor AI Prompts for Home Automation Project
description: Comprehensive Cursor prompts for code generation across all home automation subsystems
tags:
  - cursor
  - ai-prompts
  - home-automation
  - code-generation
  - development
aliases:
  - Cursor Prompts
  - AI Code Generation
  - Development Prompts
created: 2025-09-19
modified: 2025-09-19
status: active
type: development-guide
project_context: "[[main/home-automation-safety/README|Home Automation Project]]"
related_docs:
  - "[[PROJECT-INDEX|Project Documentation Index]]"
  - "[[session_state_20250912|Latest Session State]]"
  - "[[001-network-architecture|Network Architecture Decision]]"
sub_projects:
  - "[[01-network-infrastructure|Network Infrastructure]]"
  - "[[02-core-infrastructure|Core Infrastructure]]"
  - "[[03-printairpipe-ventilation|PrintAirPipe Ventilation]]"
  - "[[04-home-assistant-core|Home Assistant Core]]"
  - "[[05-cctv-surveillance|CCTV & Surveillance]]"
  - "[[06-pi-nas-storage|Pi NAS Storage]]"
  - "[[07-claude-mcp-ai|Claude MCP Integration]]"
---

# Cursor AI Prompts for Home Automation Project

> **Development Guide** | [[main/home-automation-safety/README|📋 Project Overview]] | [[PROJECT-INDEX|🗂️ Documentation Index]]

## 🎯 Project Context Template 
> **Use at start of each Cursor session**

```
CONTEXT: Home Automation & Fire Safety Project
GitHub: https://github.com/Nysplaidame/home-automation-project

PROJECT OVERVIEW:
- Comprehensive home automation system with fire safety focus for 3D printing
- Safety-critical PrintAirPipe ventilation system with emergency shutoffs
- 4-VLAN security-segmented network (VLANs 20,30,40,50)
- Proxmox virtualization on MINIX NEO Z350-0dB (i3-N350, 32GB RAM)
- Home Assistant core, Frigate NVR, Pi NAS storage
- ESPHome sensors, OpenWrt router, Claude MCP integration

CRITICAL REQUIREMENTS:
- Safety-first approach: fail-safes, emergency shutoffs, redundancy
- Network isolation: CCTV and sensors have NO internet access
- Security: Strong firewall rules, VLAN segregation
- Scalability: Modular design for future expansion
- Documentation: Comprehensive inline comments and README files

CURRENT PHASE: Network implementation (OpenWrt configuration)
REPOSITORY STRUCTURE: /configs/[system]/, /docs/, /scripts/
```

---

## 🌐 1. Network Infrastructure Prompt (OpenWrt/Router)
> **Focus Area:** [[01-network-infrastructure|Network Infrastructure & Security]]

```
TASK: Generate OpenWrt configuration files for 4-VLAN home automation network

NETWORK ARCHITECTURE:
- Router: GL.iNet GL-MT6000 (MediaTek MT7986A, OpenWrt 23.05+)
- VLAN 20: Automation/Management (192.168.20.0/24) - Internet access
- VLAN 30: CCTV (192.168.30.0/24) - No internet, HA bridge only
- VLAN 40: Storage (192.168.40.0/24) - No internet, Frigate access only  
- VLAN 50: IoT Sensors (192.168.50.0/24) - No internet, HA control only

SPECIFIC REQUIREMENTS:
1. Complete /etc/config/network with VLAN interfaces and bridge configurations
2. Comprehensive /etc/config/firewall with:
   - Zone-based security (lan/iot_sensors/cctv/storage/wan)
   - Block all VLAN 30,40,50 to WAN (no internet)
   - Allow specific inter-VLAN communication (HA→sensors, Frigate→NAS)
   - Port forwarding for Home Assistant remote access (secure)
3. /etc/config/dhcp with separate DHCP pools per VLAN
4. /etc/config/wireless for secure WiFi networks per VLAN

SECURITY FOCUS:
- Fail-closed firewall rules
- Logging for security monitoring
- Rate limiting and DDoS protection
- Guest network isolation
- Management interface security

OUTPUT: Separate config files with extensive comments explaining each rule
```

---

## 🏠 2. Home Assistant Configuration Prompt
> **Focus Area:** [[04-home-assistant-core|Home Assistant Core]]

```
TASK: Generate comprehensive Home Assistant configuration for safety-critical automation

SYSTEM INTEGRATION:
- ESPHome PrintAirPipe controllers (VLAN 50: 192.168.50.x)
- Frigate NVR integration (VLAN 30: 192.168.30.102)
- Pi NAS storage (VLAN 40: 192.168.40.100)
- Network: VLAN 20 (192.168.20.101)
- Claude MCP integration for AI automation

CORE REQUIREMENTS:
1. configuration.yaml with:
   - Network configuration for multi-VLAN environment
   - ESPHome integration discovery
   - Frigate integration setup
   - File system access to Pi NAS
   - MQTT broker configuration
   - Recorder with selective entity inclusion

2. automations.yaml with SAFETY-CRITICAL automations:
   - Fire detection → immediate power cutoff
   - Temperature thresholds → ventilation activation
   - Smoke detection → emergency protocols
   - Sensor failure → fail-safe activation
   - System health monitoring

3. Dashboard configurations:
   - Safety system overview
   - Sensor monitoring (temp, humidity, VOC, smoke)
   - CCTV integration
   - System health status

SAFETY REQUIREMENTS:
- Redundant safety checks
- Fail-safe behaviors (sensor failure = emergency mode)
- Emergency shutoff sequences
- Notification systems (multiple channels)
- Backup automation triggers

OUTPUT: Production-ready configs with extensive safety documentation
```

---

## 🔥 3. ESPHome PrintAirPipe Controller Prompt
> **Focus Area:** [[03-printairpipe-ventilation|PrintAirPipe Ventilation System]] | **⚠️ SAFETY CRITICAL**

```
TASK: Generate ESPHome configuration for PrintAirPipe safety controllers

HARDWARE SETUP:
- ESP32 controllers (suggest specific model for reliability)
- Servo motors for damper control (specify servo model/specs)
- Sensor array per 3D printer enclosure:
  * DS18B20 temperature sensors
  * DHT22 humidity sensors  
  * MQ-2 smoke detectors
  * SGP30 VOC sensors
  * Pressure/differential sensors
- Emergency relay for power cutoff
- Status LEDs and buzzer for local feedback

CONTROLLER FUNCTIONS:
1. Multi-sensor monitoring with configurable thresholds
2. Servo-controlled ventilation dampers (0-180° positioning)
3. Emergency power cutoff relay activation
4. Local safety logic (independent of HA connectivity)
5. Fail-safe modes for sensor/communication failures
6. Status reporting to Home Assistant via API

SAFETY LOGIC:
- Independent operation during network failures
- Graduated response levels (warning → action → emergency)
- Sensor cross-validation and fault detection
- Emergency override capabilities
- Watchdog timers and system health monitoring

CODE REQUIREMENTS:
- Detailed sensor calibration procedures
- Comprehensive error handling
- Extensive logging for troubleshooting
- OTA update capability with safety lockouts
- Configuration validation and bounds checking

OUTPUT: Complete ESPHome YAML with safety-first design principles
```

---

## 📹 4. Frigate NVR Configuration Prompt
> **Focus Area:** [[05-cctv-surveillance|CCTV & Surveillance]]

```
TASK: Generate Frigate NVR configuration for home security monitoring

SYSTEM SPECS:
- Proxmox VM: 4 vCPU, 8GB RAM, hardware acceleration
- Network: VLAN 30 (192.168.30.102) - isolated from internet
- Storage: Pi NAS via VLAN 40 bridge (CIFS/NFS mounts)
- Cameras: 4-6 IP cameras (suggest PoE models for reliability)

CONFIGURATION REQUIREMENTS:
1. config.yml with:
   - Hardware-accelerated detection (Intel QuickSync/VAAPI)
   - Multi-camera setup with different zones
   - Motion detection with AI object classification
   - Recording policies (continuous + event-based)
   - Storage management with automatic cleanup

2. Integration setup:
   - Home Assistant HASS integration
   - MQTT for real-time events
   - Network storage mounting (Pi NAS)
   - Time synchronization (critical for events)

3. Performance optimization:
   - Stream configurations per camera type
   - Detection zones and masking
   - Resource allocation and limits
   - Storage efficiency settings

SECURITY FEATURES:
- Tamper detection
- Camera offline monitoring  
- Motion-triggered recording
- Privacy masking for family areas
- Secure access controls

OUTPUT: Production config with performance tuning and monitoring setup
```

---

## 💻 5. Proxmox Virtualization Setup Prompt
> **Focus Area:** [[02-core-infrastructure|Core Infrastructure (Proxmox)]]

```
TASK: Generate Proxmox configuration scripts and VM templates

HARDWARE PLATFORM:
- MINIX NEO Z350-0dB: Intel i3-N350, 32GB DDR4, 512GB M.2 NVMe
- Network: Multiple VLAN interfaces via GL.iNet router
- Storage: Local NVMe + Pi NAS for backups

VM ARCHITECTURE:
- VM 101: Home Assistant (Ubuntu 22.04 LTS, 4GB RAM, 2 vCPU)
- VM 102: Frigate NVR (Ubuntu 22.04 LTS, 8GB RAM, 4 vCPU) 
- VM 103: Development/Testing (Ubuntu 22.04 LTS, 4GB RAM, 2 vCPU)
- Future: Additional VMs for expansion

REQUIREMENTS:
1. Proxmox installation script with:
   - Network bridge configuration for VLANs
   - Storage setup (local + NAS backup)
   - User management and security
   - Backup automation configuration

2. VM creation scripts:
   - Automated VM deployment with cloud-init
   - Network interface assignments per VLAN
   - Resource allocation and limits
   - Snapshot and backup policies

3. Infrastructure monitoring:
   - Resource usage monitoring
   - Health checks and alerting
   - Automated backup verification
   - Update management procedures

AUTOMATION FEATURES:
- VM template creation and cloning
- Automated backups to Pi NAS
- Resource monitoring and alerting
- Update orchestration across VMs

OUTPUT: Complete infrastructure-as-code setup with monitoring
```

---

## 💾 6. Pi NAS Storage System Prompt
> **Focus Area:** [[06-pi-nas-storage|Pi NAS Storage]]

```
TASK: Generate Raspberry Pi NAS configuration for CCTV and project storage

HARDWARE SETUP:
- Raspberry Pi 4B (8GB) with external USB 3.0 drives
- Network: VLAN 40 (192.168.40.100) - isolated storage network
- Storage: Multiple drives with redundancy (suggest RAID setup)

STORAGE REQUIREMENTS:
1. CCTV footage storage:
   - High-throughput write capability
   - Automatic retention policies
   - Direct access from Frigate (VLAN 30 bridge)
   - Monitoring and health checks

2. General network storage:
   - Home Assistant backups
   - Configuration file versioning
   - Project documentation sync
   - System image backups

SERVICES CONFIGURATION:
1. File sharing services:
   - Samba/CIFS for Windows compatibility
   - NFS for Linux VM performance
   - SSH/SFTP for secure access

2. Storage management:
   - Automated backup scheduling
   - Disk health monitoring (SMART)
   - Storage usage alerting
   - Cleanup and archiving policies

SECURITY & RELIABILITY:
- User access controls and permissions
- Network access restrictions (VLAN-based)
- Data integrity monitoring
- Automated backup validation

OUTPUT: Complete NAS setup with monitoring and maintenance automation
```

---

## 🤖 7. Claude MCP Integration Prompt
> **Focus Area:** [[07-claude-mcp-ai|Claude MCP Integration]]

```
TASK: Develop Claude MCP (Model Context Protocol) integration for AI-driven automation

INTEGRATION ARCHITECTURE:
- MCP server running alongside Home Assistant
- Real-time sensor data access and control capabilities
- Natural language processing for complex automation logic
- Safety-aware AI decision making with override capabilities

CORE FUNCTIONS:
1. Natural language automation:
   - Voice/text commands for system control
   - Complex rule creation via conversation
   - System status inquiries and reporting
   - Troubleshooting assistance

2. Intelligent monitoring:
   - Anomaly detection across all sensors
   - Predictive maintenance recommendations
   - Pattern recognition for optimization
   - Emergency response coordination

3. Safety integration:
   - AI-assisted safety system monitoring
   - Intelligent emergency response protocols
   - Risk assessment and prevention
   - Safety system validation and testing

MCP IMPLEMENTATION:
1. Server setup with Home Assistant integration
2. Sensor data streaming and command interfaces
3. Safety-constrained AI decision boundaries
4. Logging and audit trail for AI actions

SAFETY CONSTRAINTS:
- AI cannot override manual safety systems
- All AI actions require human validation for critical systems
- Fail-safe behaviors when AI is unavailable
- Comprehensive logging of AI decisions and actions

OUTPUT: Production MCP implementation with safety guardrails
```

---

## 🛠️ General Cursor Usage Tips

### 🧠 Context Management
- Start each session with the project context template
- Reference specific config files from the repository structure
- Use `@filename` to include existing configs when modifying
- Leverage Cursor's codebase understanding with `@codebase` queries

### 🏗️ Code Quality Focus
- Request extensive inline documentation and comments
- Ask for error handling and input validation
- Include logging and monitoring capabilities
- Generate README files for each component

### ⚠️ Safety-Critical Development
- Always request fail-safe behaviors and redundancy
- Ask for configuration validation and bounds checking
- Include emergency override capabilities
- Generate comprehensive testing procedures

### 🔧 Integration Approach
- Request modular, loosely-coupled designs
- Include standard interfaces (MQTT, REST APIs, etc.)
- Generate docker-compose files where appropriate
- Ask for health check and monitoring endpoints

---

## 💡 Example Cursor Commands

```bash
# Generate network config
"Using the network infrastructure prompt, generate complete OpenWrt configs for the 4-VLAN setup"

# Extend existing config
"@configs/home-assistant/configuration.yaml - Add PrintAirPipe ESPHome integration using the HA prompt"

# Create new component
"Generate a new ESPHome configuration for bedroom air quality monitoring using similar patterns from @codebase"

# Safety review
"Review all emergency automation logic for fail-safe behaviors and add missing safety checks"
```

---

**📊 Document Status:** Active Development Guide | **🎯 Purpose:** Cursor AI Code Generation  
**📅 Last Updated:** September 19, 2025 | **📋 Document Version:** 1.0

**Related Documents:**
- [[PROJECT-INDEX|📚 Project Documentation Index]]
- [[main/home-automation-safety/README|📋 Project Overview]]
- [[session_state_20250912|📦 Latest Session State]]

**Safety Notice:**  
⚠️ When using these prompts for safety-critical systems, always prioritize fail-safe behaviors and comprehensive testing before deployment.
