# VentSys Phase 1: Network and Security Foundation (Weeks 1-3)

## Phase Overview
Establish secure network infrastructure and certificate authority system that will support all subsequent VentSys components. This phase creates the foundation for TLS-encrypted device communication while maintaining complete IoT network isolation.

## Reference Documents
- **Network Configs**: `vlan-config.conf`, `firewall-config.conf`, `dhcp-config.conf`, `wireless-config.conf` (existing, no changes)
- **TLS Implementation**: `docs/procedures/ssl_tls_guide.md` (canonical active workflow)
- **Network Integration Analysis**: [[ventsys/integration-process/ventsys_network_integration_analysis|Network Integration Analysis]]
- **Implementation Roadmap**: [[ventsys/integration-process/ventsys_implementation_roadmap|9-Week Roadmap]]
- **Current VentSys**: All existing configuration files (preserved during foundation setup)

## Backup and Recovery Strategy
**Daily Backup Schedule**: Automated backup of all configurations at 2:00 AM
**Pre-Change Backups**: Manual backup before any major configuration change
**Backup Components**: Network configs, certificates, MQTT configs, Home Assistant configs, device registry

---

## Week 1: Network Infrastructure Validation

### 1.1 Network Connectivity Verification
**Objective**: Confirm existing network architecture supports VentSys requirements without modification

**Sub-tasks**:
- **VLAN Connectivity Test**: Verify communication between VLAN 50 (IoT) and VLAN 20 (Automation) through existing firewall rules
- **WiFi Assignment Validation**: Confirm HomeIoT SSID correctly assigns devices to VLAN 50 with proper IP allocation from DHCP range 192.168.50.100-190
- **Internet Isolation Verification**: Test that devices on VLAN 50 cannot reach external networks while maintaining access to gateway services
- **Performance Baseline**: Document network latency, throughput, and reliability metrics between critical network segments

**Code Requirements**:
- Create network validation script that tests all required connectivity paths and documents results in structured format
- Update device registry template to track MAC addresses, IP assignments, and network performance metrics

**Interdependencies**: 
- Requires existing network configuration files to be functional
- Depends on proper VLAN and firewall configuration from uploaded configs
- Prerequisites for all subsequent certificate and device deployment phases

**Testing Procedures**:
- Connect test device to HomeIoT WiFi and verify VLAN 50 assignment
- Attempt internet access from test device (should fail)
- Verify test device can reach Home Assistant on 192.168.20.101
- Document response times and connection reliability

**Success Criteria**:
- All required network paths functional with <50ms latency
- IoT devices properly isolated from internet
- DHCP assignments working correctly on all VLANs
- Network performance meets baseline requirements for real-time control

### 1.2 Static IP Assignment and Device Registry
**Objective**: Establish consistent IP addressing for all VentSys components and create comprehensive device tracking

**Sub-tasks**:
- **VentSys IP Allocation**: Reserve static IP addresses for all VentSys devices per the canonical allocation table in `configs/openwrt/dhcp-config.conf` (fans .21–.22, sensor arrays .31–.34, airflow sensors .41–.43, butterfly valves .51–.56, 360° intake valves .61–.62, smart plugs .71–.78; reserved future .79–.89)
- **Device Registry Creation**: Create comprehensive registry tracking all VentSys devices with MAC addresses, IP assignments, device types, and deployment status
- **DHCP Reservation Setup**: Configure DHCP reservations for all VentSys devices to ensure consistent IP addressing
- **Network Documentation Update**: Document all VentSys network assignments and update network topology diagrams

**Code Requirements**:
- Create VentSys device registry YAML file with comprehensive device tracking including certificate status, deployment dates, and hardware specifications
- Update DHCP configuration to include static reservations for all planned VentSys devices

**Interdependencies**:
- Depends on network connectivity validation (1.1)
- Required before certificate generation (Week 2)
- Prerequisites for device deployment in subsequent phases

**Testing Procedures**:
- Verify static IP assignments work correctly for test devices
- Confirm DHCP reservations prevent IP conflicts
- Validate device registry accurately tracks all planned components

**Success Criteria**:
- All VentSys IP addresses reserved and functional
- Device registry comprehensive and accurate
- No IP conflicts detected during testing
- Network topology documentation complete and current

### 1.3 Firewall Rule Validation and Optimization
**Objective**: Verify existing firewall rules support VentSys requirements and optimize for security and performance

**Sub-tasks**:
- **VentSys Traffic Analysis**: Analyze existing firewall rules to confirm they support required VentSys communication patterns
- **Rule Performance Testing**: Test firewall rule performance under expected VentSys traffic loads
- **Security Validation**: Verify firewall properly blocks unauthorized traffic while allowing required VentSys communications
- **Logging Configuration**: Configure firewall logging to track VentSys-related traffic for security monitoring and troubleshooting

**Code Requirements**:
- Create firewall validation script that tests all required VentSys communication paths and logs results
- Update firewall logging configuration to capture VentSys-specific traffic patterns for monitoring

**Interdependencies**:
- Depends on network connectivity verification (1.1)
- Required before TLS deployment (Week 2)
- Foundation for security monitoring throughout project

**Testing Procedures**:
- Test all planned VentSys communication paths through firewall
- Verify unauthorized access attempts are properly blocked
- Confirm firewall performance under simulated VentSys traffic loads

**Success Criteria**:
- All required VentSys communications pass firewall rules
- Unauthorized access properly blocked and logged
- Firewall performance adequate for VentSys traffic loads
- Security logging captures relevant events without overwhelming system

---

## Week 2: Certificate Authority and TLS Infrastructure

### 2.1 OpenWrt NTP Server Configuration
**Reference**: `VentSys Solution 1 Implementation Guide` Phase 1 (Steps 1.1-1.3)

**Objective**: Deploy local NTP server on router to provide time synchronization for IoT devices without internet access

**Sub-tasks**:
- **NTP Server Installation**: Install and configure NTP server on OpenWrt router with multiple upstream time sources for reliability
- **Local Network Configuration**: Configure NTP server to serve time to VLAN 50 devices while maintaining security isolation
- **Firewall Rule Application**: Apply firewall rules allowing IoT devices UDP/123 access to router NTP service
- **Time Sync Validation**: Test NTP synchronization from IoT VLAN and verify accuracy and reliability

**Code Requirements**:
- Configure OpenWrt NTP service with upstream servers and local network serving capability
- Update firewall rules to allow UDP/123 traffic from VLAN 50 to router gateway addresses

**Interdependencies**:
- Depends on network validation (Week 1)
- Required before device TLS configuration (Week 3)
- Foundation for all device time synchronization

**Testing Procedures**:
- Test NTP queries from devices on VLAN 50 to router
- Verify time accuracy within 1 second of internet time sources
- Confirm NTP service continues working during internet outages

**Success Criteria**:
- NTP server operational on router serving VLAN 50
- Time synchronization accuracy within ±1 second
- Service maintains operation during internet disruptions
- Firewall properly allows required NTP traffic

### 2.2 Certificate Authority Deployment
**Reference**: `VentSys Solution 1 Implementation Guide` Phase 3 (Steps 3.1-3.4)

**Objective**: Create local certificate authority for VentSys device authentication with 10-year operational lifetime

**Sub-tasks**:
- **CA Directory Structure**: Create secure certificate authority directory structure on Home Assistant with proper permissions and organization
- **Root CA Generation**: Generate 10-year root CA certificate with strong cryptographic parameters suitable for long-term IoT device authentication
- **Certificate Generation Scripts**: Create scripts for generating device certificates with VentSys-specific naming conventions and 3-year validity periods
- **CA Security Configuration**: Implement proper security measures for CA private key protection and certificate signing operations

**Code Requirements**:
- Create CA directory structure with secure permissions and proper organization for certificate management
- Generate root CA certificate and private key with appropriate OpenSSL configuration for 10-year validity
- Create certificate generation script template for VentSys devices with standardized naming and validity periods

**Interdependencies**:
- Depends on Home Assistant SSH access configuration
- Required before MQTT TLS configuration (2.3)
- Foundation for all device certificate provisioning

**Testing Procedures**:
- Verify CA certificate validates properly with OpenSSL tools
- Test certificate generation script with sample device names
- Confirm CA directory structure has proper security permissions

**Success Criteria**:
- Root CA operational with 10-year validity
- Certificate generation process functional and documented
- CA security properly implemented and tested
- Certificate validation chain working correctly

### 2.3 MQTT Broker TLS Configuration  
**Reference**: `VentSys Solution 1 Implementation Guide` Phase 4 (Steps 4.1-4.6)

**Objective**: Configure Mosquitto MQTT broker with TLS encryption using local CA for device authentication

**Sub-tasks**:
- **MQTT Broker Certificate**: Generate and install TLS certificate for MQTT broker using local CA with proper hostname validation
- **TLS Listener Configuration**: Configure Mosquitto with TLS listener on port 8883 using local CA for certificate validation
- **User Account Management**: Create MQTT user accounts for different VentSys device classes with appropriate permissions
- **Access Control Implementation**: Configure MQTT ACL to restrict device access to appropriate topics based on device type and function

**Code Requirements**:
- Generate MQTT broker certificate signed by local CA and configure Mosquitto TLS listener with proper security settings
- Create MQTT user accounts for ventsys_controllers, ventsys_sensors, and ventsys_nodered with strong passwords
- Configure MQTT ACL file to restrict topic access based on device type and security requirements

**Interdependencies**:
- Depends on CA deployment (2.2)
- Required before device TLS configuration (Week 3)
- Foundation for all secure MQTT communication

**Testing Procedures**:
- Test TLS connection to MQTT broker with local CA validation
- Verify user authentication and topic access restrictions
- Confirm certificate validation rejects invalid certificates

**Success Criteria**:
- MQTT broker serving TLS on port 8883 with local CA validation
- User accounts functional with appropriate access restrictions
- Certificate authentication working properly
- Access control enforced according to security requirements

### 2.4 Certificate Management System
**Reference**: `VentSys Solution 1 Implementation Guide` Phase 7 (Steps 7.1-7.3)

**Objective**: Implement certificate lifecycle management with monitoring and renewal procedures

**Sub-tasks**:
- **Certificate Monitoring**: Create system to track certificate expiry dates for all VentSys devices and alert 6 months before expiration
- **Renewal Procedures**: Develop manual certificate renewal procedures with clear step-by-step instructions for generating and distributing new certificates
- **Device Registry Integration**: Integrate certificate tracking with VentSys device registry to maintain comprehensive device and certificate status
- **Backup and Recovery**: Implement secure backup procedures for CA and device certificates with recovery testing

**Code Requirements**:
- Create certificate monitoring script that checks expiry dates and generates alerts through Home Assistant notification system
- Develop certificate renewal procedure documentation with scripts for certificate generation and device registry updates
- Integrate certificate tracking into VentSys device registry with automated status updates

**Interdependencies**:
- Depends on CA deployment (2.2) and device registry (1.2)
- Required before large-scale device deployment
- Foundation for long-term certificate maintenance

**Testing Procedures**:
- Test certificate expiry monitoring with test certificates
- Validate certificate renewal procedures with sample devices
- Verify backup and recovery procedures work correctly

**Success Criteria**:
- Certificate expiry monitoring operational with alerting
- Renewal procedures documented and tested
- Device registry tracks certificate status accurately  
- Backup and recovery procedures validated

---

## Week 3: Basic Device Connectivity with TLS

### 3.1 ESPHome Base TLS Configuration
**Reference**: `VentSys Solution 1 Implementation Guide` Phase 5 (Steps 5.1-5.3)

**Objective**: Create standardized TLS configuration template for all VentSys ESPHome devices

**Sub-tasks**:
- **Base Configuration Template**: Create comprehensive ESPHome base configuration with TLS MQTT, local NTP, WiFi, and common device functionality
- **Device Certificate Integration**: Develop procedure for embedding CA certificate into ESPHome configurations during device provisioning
- **Device Authentication Setup**: Configure device authentication using MQTT username/password with TLS encryption for secure communication
- **Device Lifecycle Management**: Implement device birth/will messages and heartbeat reporting for comprehensive device monitoring

**Code Requirements**:
- Create ventsys_base_tls.yaml template with WiFi (HomeIoT SSID), NTP (router), MQTT TLS (port 8883), and device monitoring functionality
- Develop device provisioning procedure that embeds CA certificate and device-specific credentials into ESPHome configurations
- Implement device lifecycle MQTT messages for birth, will, and heartbeat reporting with structured JSON payloads

**Interdependencies**:
- Depends on MQTT TLS configuration (2.3) and NTP deployment (2.1)
- Required before device certificate generation (3.2)
- Template for all VentSys device configurations

**Testing Procedures**:
- Test base configuration with sample ESP32 device
- Verify TLS MQTT connectivity and certificate validation
- Confirm device lifecycle messages work correctly

**Success Criteria**:
- Base TLS configuration template functional
- Device authentication working with TLS encryption
- CA certificate integration process documented
- Device lifecycle monitoring operational

### 3.2 Existing Device Certificate Provisioning
**Objective**: Generate certificates for initial VentSys devices and update configurations for TLS

**Sub-tasks**:
- **Initial Device Certificates**: Generate certificates for the first devices being deployed (e.g., main fan controller at .21, FDM sensor array at .31) using the CA certificate generation script from Week 2
- **Device Configuration Updates**: Update ESPHome YAML files to use base TLS template while preserving existing MQTT topic structure (see `ventsys_fan_controller.yaml` and `ventsys_valve_controller.yaml` as starting points)
- **Full Device Registry**: Once all 17 ESP32 boards and 8 smart plugs are assembled, generate certificates for all devices per the canonical IP allocation table in `dhcp-config.conf`
- **Certificate Distribution**: Implement secure procedure for distributing CA certificate and device credentials to ESP32 devices during flashing

**Code Requirements**:
- Generate device certificates for `ventsys-main-fan` and `ventsys-sla-print-valve` using the CA certificate generation script
- Update ventsys_fan_controller.yaml and ventsys_valve_controller.yaml to use base TLS template while maintaining existing MQTT topic structure
- Create device flashing procedure that securely integrates certificates and credentials into device firmware

**Interdependencies**:
- Depends on base TLS configuration (3.1) and certificate management (2.4)
- Required before device TLS testing (3.3)
- Foundation for existing device TLS migration

**Testing Procedures**:
- Generate certificates for existing devices and validate against CA
- Flash updated configurations and verify TLS connectivity
- Confirm existing device functionality preserved

**Success Criteria**:
- Certificates generated for existing devices
- Device configurations updated with TLS
- Existing functionality preserved during TLS migration
- Certificate distribution process documented

### 3.3 TLS Connectivity Testing and Validation
**Objective**: Validate TLS MQTT connectivity for all updated devices and verify system functionality

**Sub-tasks**:
- **Device TLS Testing**: Test TLS MQTT connectivity for all updated devices and verify certificate authentication
- **Functionality Preservation**: Validate that existing VentSys functionality continues working with TLS encryption
- **Network Isolation Confirmation**: Verify that TLS devices maintain network isolation while communicating securely
- **Performance Impact Assessment**: Measure TLS performance impact and confirm acceptable latency for real-time control

**Code Requirements**:
- Create TLS connectivity testing script that validates certificate authentication and MQTT communication for all devices
- Develop functionality testing procedures that verify existing VentSys operations work correctly with TLS encryption
- Implement performance monitoring to measure TLS impact on communication latency and system responsiveness

**Interdependencies**:
- Depends on device certificate provisioning (3.2)
- Required before Phase 2 hardware expansion
- Validates TLS foundation for all future development

**Testing Procedures**:
- Test TLS MQTT connectivity from all updated devices
- Verify existing fan and valve control functions work correctly
- Confirm network isolation maintained with TLS communication

**Success Criteria**:
- All devices communicate via TLS MQTT with certificate validation
- Existing VentSys functionality preserved and operational
- Network isolation maintained with TLS communication
- TLS performance impact acceptable for real-time control

### 3.4 System Integration and Documentation
**Objective**: Integrate TLS devices with Home Assistant and complete Phase 1 documentation

**Sub-tasks**:
- **Home Assistant MQTT Integration**: Configure Home Assistant MQTT integration with TLS and local CA for secure device communication
- **Entity Preservation**: Ensure existing Home Assistant entities continue working with TLS-enabled devices
- **Certificate Monitoring Integration**: Add certificate status monitoring for all VentSys devices to Home Assistant dashboard
- **Phase 1 Documentation**: Complete comprehensive documentation of TLS infrastructure, procedures, and device configurations

**Code Requirements**:
- Configure Home Assistant MQTT integration with TLS client certificate and CA validation for secure communication
- Update Home Assistant entity configurations to work with TLS-enabled devices while preserving existing functionality
- Create certificate monitoring entities in Home Assistant that track expiry dates and certificate health for all VentSys devices

**Interdependencies**:
- Depends on TLS testing (3.3) and certificate management (2.4)
- Completes Phase 1 foundation for Phase 2 development
- Required for comprehensive system monitoring

**Testing Procedures**:
- Verify Home Assistant MQTT integration works with TLS
- Confirm existing entities update correctly with TLS devices
- Test certificate monitoring displays accurate information

**Success Criteria**:
- Home Assistant integrated with TLS MQTT broker
- All existing entities functional with TLS devices
- Certificate monitoring operational in Home Assistant
- Phase 1 documentation complete and accurate

---

## Phase 1 Success Criteria

### Network Foundation
- All VLANs operational with proper isolation and performance
- Static IP assignments functional for all planned VentSys devices
- Network documentation complete and accurate
- Firewall rules validated for VentSys communication requirements

### Security Infrastructure  
- Local Certificate Authority operational with 10-year root certificate
- MQTT broker serving TLS on port 8883 with local CA validation
- Certificate management system operational with monitoring and renewal procedures
- All security measures tested and documented

### Device Integration
- Existing VentSys devices converted to TLS authentication
- Device connectivity validated with certificate authentication
- Home Assistant integration functional with TLS devices
- Device registry tracking all components and certificate status

### Operational Readiness
- Backup and recovery procedures implemented and tested
- Network time synchronization operational for IoT devices
- System monitoring and alerting functional
- Comprehensive documentation completed

## Phase 1 Deliverables
- Fully operational TLS infrastructure with local CA
- Existing VentSys devices converted to secure TLS communication
- Comprehensive device registry and certificate management system
- Network foundation validated and documented for Phase 2 expansion
