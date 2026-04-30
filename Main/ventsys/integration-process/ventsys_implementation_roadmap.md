# VentSys TLS Implementation Roadmap

## Required Reference Documents
- **Master Implementation Guide**: `VentSys Solution 1 Implementation Guide` - Complete step-by-step process
- **Network Architecture**: `vlan-config.conf`, `firewall-config.conf`, `dhcp-config.conf`, `wireless-config.conf`
- **Current VentSys**: All existing VentSys YAML and JSON configuration files
- **Integration Analysis**: `ventsys_network_integration_analysis.md`

## Implementation Overview

This roadmap follows the TLS Certificate Authority approach detailed in the master implementation guide. Each phase references specific steps from that document to avoid duplication while providing project-specific context.

## Phase 1: Network Foundation & Certificate Authority (Week 1-2)
*Establish secure infrastructure foundation*

### Week 1: Network Infrastructure Setup
**References**: Master Guide Phases 1-2 (Steps 1.1-2.3)

**VentSys-Specific Tasks**:
- Verify VLAN 50 (IoT) and VLAN 20 (Automation) connectivity
- Apply firewall rules for IoT→Router NTP and IoT→HA MQTT TLS access
- Configure OpenWrt NTP server to serve VLAN 50 devices
- Enable SSH access to Home Assistant for CA operations

**Key Deliverables**:
- OpenWrt NTP server operational on router (192.168.50.1, 192.168.20.1)
- Firewall rules allowing UDP/123 (NTP) and TCP/8883 (MQTT TLS) from VLAN 50
- Home Assistant SSH access configured for certificate management
- Network connectivity validated between all VentSys components

**Validation Criteria**:
```bash
# From IoT device IP range (192.168.50.x):
ntpdate -q 192.168.50.1        # NTP sync works
ping -c 1 192.168.20.101       # HA accessible
ping -c 1 8.8.8.8              # Should fail (internet blocked)
```

### Week 2: Certificate Authority Deployment  
**References**: Master Guide Phase 3 (Steps 3.1-3.4)

**VentSys-Specific Modifications**:
- Create CA with 10-year validity for long-term VentSys operation
- Generate certificates with 3-year validity to balance security and maintenance
- Configure certificate generation script for VentSys device naming convention
- Set up certificate monitoring for VentSys device registry

**Certificate Naming Strategy**:
```bash
# A8-3 fix: stale pre-canonical device names corrected. Certificate CN MUST match
# the ESPHome device_name (= mDNS hostname) or TLS validation will fail.
# Canonical names from dhcp-config.conf and ESPHome YAMLs in configs/esphome/:
ventsys-main-fan         (192.168.50.21)   # was ventsys-fan-controller
ventsys-sla-print-valve  (192.168.50.56)   # was ventsys-sla-valve
ventsys-fdm-print-valve  (192.168.50.55)   # was ventsys-fdm-valve@.83 (device/IP did not exist)
ventsys-booth-sensor     (192.168.50.33)   # was ventsys-booth-valve@.84 (device/IP did not exist)
ventsys-fdm-sensor       (192.168.50.31)   # canonical sensor-board mDNS/DHCP name
ventsys-sla-sensor       (192.168.50.32)   # canonical sensor-board mDNS/DHCP name
ventsys-booth-sensor     (192.168.50.33)   # canonical sensor-board mDNS/DHCP name
```

**Validation Criteria**:
- Certificate Authority operational with 10-year root certificate
- Device certificate generation script functional
- Certificate validation chain working
- CA certificate accessible for device distribution

---

## Phase 2: MQTT TLS Infrastructure (Week 3)
*Deploy encrypted MQTT with local CA authentication*

### Week 3: Mosquitto TLS Configuration
**References**: Master Guide Phase 4 (Steps 4.1-4.6)

**VentSys MQTT Architecture**:
- **Single TLS Port (8883)**: All devices (HA and IoT/ESPHome) use encrypted connection with local CA
- **No plaintext port**: Certs are generated on HA and embedded in ESPHome firmware at flash time — no internet dependency at any stage
- **Device Authentication**: Certificate-based authentication for IoT devices
- **Access Control**: Granular topic permissions for VentSys device classes (ventsys_controllers, ventsys_sensors, ventsys_nodered)

**VentSys-Specific ACL Configuration**:
```conf
# VentSys MQTT Access Control (/config/mosquitto/acl.conf)
# Home Assistant - full access
user ha_secure_user
topic readwrite #

# VentSys Controllers (fan, valves) — connect on 8883 TLS
user ventsys_controllers
topic readwrite ventsys/fan/+
topic readwrite ventsys/+/valve/+
topic readwrite ventsys/devices/+/+

# VentSys Sensors — connect on 8883 TLS
user ventsys_sensors
topic readwrite ventsys/+/temperature
topic readwrite ventsys/+/humidity
topic readwrite ventsys/+/pressure
topic readwrite ventsys/+/voc
topic readwrite ventsys/+/smoke
topic readwrite homeassistant/sensor/ventsys/+

# Node-RED flows - bridge user
user ventsys_nodered
topic readwrite ventsys/#
topic readwrite homeassistant/#
```

**Key Deliverables**:
- Mosquitto configured with TLS listener on port 8883
- Local CA certificate integrated for device authentication
- VentSys-specific user accounts and ACL permissions configured
- MQTT broker certificate generated and installed

**Validation Criteria**:
```bash
# Test TLS connection with local CA
mosquitto_pub -h 192.168.20.101 -p 8883 \
    --cafile /config/ssl/ca/certs/ca-cert.pem \
    -u ventsys_controllers -P "CONTROLLER_PASSWORD" \
    -t "ventsys/test" -m "TLS working"

# Verify certificate validation
openssl s_client -connect 192.168.20.101:8883 \
    -CAfile /config/ssl/ca/certs/ca-cert.pem -verify_return_error
```

---

## Phase 3: VentSys Device TLS Integration (Week 4-5)
*Convert existing devices to use local CA and TLS*

### Week 4: ESPHome Device Certificate Provisioning
**References**: Master Guide Phase 5 (Steps 5.1-5.3)

**Device Update Strategy**:
1. Generate certificates for existing VentSys devices
2. Update ESPHome configurations with TLS and local CA
3. Flash devices with new TLS-enabled configurations
4. Validate TLS connectivity and certificate authentication

**VentSys ESPHome Base Configuration**:
```yaml
# ventsys_base_tls_config.yaml
substitutions:
  device_name: ${device_name}
  device_ip: ${device_ip}
  device_cert_name: ${device_cert_name}

esphome:
  name: ${device_name}
  friendly_name: ${friendly_name}

esp32:
  board: esp32dev

wifi:
  ssid: !secret iot_wifi_ssid        # "HomeIoT" - Channel 6, VLAN 50
  password: !secret iot_wifi_pass
  manual_ip:
    static_ip: ${device_ip}
    gateway: 192.168.50.1
    subnet: 255.255.255.0
    dns1: 192.168.50.1

time:
  - platform: sntp
    id: sntp_time
    servers:
      - 192.168.50.1                 # OpenWrt NTP server
    timezone: "America/New_York"

mqtt:
  broker: 192.168.20.101
  port: 8883
  username: !secret mqtt_device_user  # ventsys_controllers or ventsys_sensors
  password: !secret mqtt_device_pass
  discovery: false
  
  # Local CA certificate for TLS validation
  ca_certificate: |
    -----BEGIN CERTIFICATE-----
    # Content of ca-cert.pem inserted during provisioning
    -----END CERTIFICATE-----
  
  # Device lifecycle messages  
  birth_message:
    topic: ventsys/devices/${device_name}/birth
    payload: !lambda |-
      char buf[256];
      snprintf(buf, sizeof(buf), 
               "{\"ts\":%u,\"device\":\"%s\",\"ip\":\"%s\",\"cert\":\"%s\"}", 
               (unsigned)id(sntp_time).timestamp, "${device_name}", 
               "${device_ip}", "${device_cert_name}");
      return std::string(buf);
    retain: true
```

**Device-Specific Updates**:
- **Main Fan** (ventsys-main-fan, 192.168.50.21): Update with TLS, keep existing MQTT topics  # A8-3
- **SLA Print Valve** (ventsys-sla-print-valve, 192.168.50.56): Add TLS  # A8-3: was SLA Valve Controller
- **FDM Print Valve** (ventsys-fdm-print-valve, 192.168.50.55): Deploy with TLS from start  # A8-3: was ventsys-fdm-valve@.83 (stale)
- **Booth Sensor** (ventsys-booth-sensor, 192.168.50.33): Deploy with TLS from start  # A8-3: was ventsys-booth-valve@.84 (device does not exist)

### Week 5: Hardware Expansion with TLS
**New Hardware Deployment**:
- Deploy FDM valve controller with TLS configuration
- Deploy Booth valve controller with TLS configuration  
- Test multi-valve coordination through TLS MQTT
- Validate certificate-based device authentication

**Key Deliverables**:
- All existing VentSys devices converted to TLS with local CA
- Two additional valve controllers deployed with TLS
- Device certificates generated and provisioned
- VentSys device registry updated with certificate expiry tracking

**Validation Criteria**:
- All devices connect successfully via TLS to MQTT broker
- Certificate validation working for all devices
- Existing VentSys functionality preserved
- Multi-zone valve control operational

---

## Phase 4: Home Assistant Integration & Node-RED Updates (Week 6)
*Integrate TLS infrastructure with VentSys control systems*

### Week 6: Control System Integration
**References**: Master Guide Phase 6 (Steps 6.1-6.4)

**Home Assistant MQTT Integration**:
- Configure HA MQTT integration with TLS and local CA
- Update VentSys entity definitions for new device structure
- Create certificate monitoring sensors for all VentSys devices
- Deploy VentSys dashboard with certificate status visibility

**Node-RED MQTT Broker Updates**:
```javascript
// Updated Node-RED MQTT broker configuration
{
  "id": "ventsys-mqtt-tls",
  "type": "mqtt-broker",
  "name": "VentSys MQTT TLS",
  "broker": "192.168.20.101",
  "port": "8883",
  "tls": "ventsys-tls-config",
  "credentials": {
    "user": "ventsys_nodered",
    "password": "NODERED_TLS_PASSWORD"
  }
}

// TLS configuration node
{
  "id": "ventsys-tls-config",
  "type": "tls-config", 
  "name": "VentSys Local CA",
  "ca": "/config/ssl/ca/certs/ca-cert.pem",
  "verifyservercert": true
}
```

**VentSys Safety Automations with Certificate Monitoring**:
```yaml
# Certificate expiry alerts for VentSys devices
- alias: VentSys Certificate Expiry Alert
  id: ventsys_cert_expiry
  trigger:
    - platform: numeric_state
      entity_id:
        - sensor.ventsys_fan_controller_cert_expires
        - sensor.ventsys_sla_valve_cert_expires
        - sensor.ventsys_fdm_valve_cert_expires
        - sensor.ventsys_booth_valve_cert_expires
      below: 60  # 60 days before expiry
  action:
    - service: notify.mobile_app
      data:
        title: "VentSys Certificate Renewal Required"
        message: "Device {{ trigger.to_state.attributes.device_name }} certificate expires in {{ trigger.to_state.state }} days"
        data:
          priority: high
```

**Key Deliverables**:
- Home Assistant MQTT integration using TLS with local CA
- All VentSys entities functional with TLS connectivity
- Node-RED flows updated to use TLS MQTT broker
- Certificate monitoring integrated into VentSys dashboard
- Safety automations operational with enhanced certificate monitoring

---

## Phase 5: Certificate Lifecycle Management (Week 7-8)
*Deploy automated certificate renewal and monitoring*

### Week 7-8: Automated Certificate Management
**References**: Master Guide Phase 7 (Steps 7.1-7.3)

**VentSys Certificate Registry**:
```yaml
# /config/ventsys_device_registry.yaml
ventsys_devices:
  - name: ventsys-main-fan  # A8-3 fix: was ventsys-fan-controller
    mac: "XX:XX:XX:XX:XX:XX"
    ip: 192.168.50.21
    type: ESP32_Controller
    purpose: Inline fan control
    certificate_expires: "2027-12-01"
    mqtt_user: ventsys_controllers
    mqtt_topics:
      - ventsys/fan/control
      - ventsys/fan/percent
      - ventsys/fan/state
    
  - name: ventsys-sla-print-valve  # A8-3 fix: was ventsys-sla-valve
    mac: "XX:XX:XX:XX:XX:XX" 
    ip: 192.168.50.56
    type: ESP32_Valve
    purpose: SLA enclosure valve control
    certificate_expires: "2027-12-01"
    mqtt_user: ventsys_controllers
    mqtt_topics:
      - ventsys/sla/valve/control
      - ventsys/sla/valve/state
```

**VentSys Certificate Renewal Integration**:
- Modify renewal script to handle VentSys device registry format
- Add VentSys-specific MQTT topics for certificate distribution
- Configure renewal notifications through VentSys safety system
- Test certificate renewal process with VentSys devices

**Automated Certificate Distribution**:
```bash
# VentSys certificate renewal process
publish_ventsys_certificate() {
    local device_name="$1"
    local cert_file="$2"
    local key_file="$3"
    
    # Create VentSys certificate package
    cert_package=$(cat << EOJ
{
  "device": "$device_name",
  "certificate": "$(cat "$cert_file" | base64 -w 0)",
  "ca_certificate": "$(cat certs/ca-cert.pem | base64 -w 0)",
  "issued": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "expires": "$(openssl x509 -in "$cert_file" -noout -enddate | cut -d= -f2)",
  "renewal_id": "$(uuidgen)"
}
EOJ
)
    
    # Publish to VentSys certificate renewal topic
    mosquitto_pub -h 192.168.20.101 -p 8883 \
        --cafile certs/ca-cert.pem \
        -u ha_secure_user -P "SECURE_HA_PASSWORD" \
        -t "ventsys/system/certificate/$device_name/renewal" \
        -m "$cert_package" \
        -r
}
```

**Key Deliverables**:
- VentSys-specific device registry with certificate tracking
- Automated certificate renewal process for VentSys devices
- Certificate distribution via MQTT for VentSys devices
- Certificate monitoring integrated with VentSys safety systems
- Automated renewal testing and validation

---

## Phase 6: Testing, Validation & Documentation (Week 9)
*Complete system testing and documentation*

### Week 9: System Validation & Documentation
**References**: Master Guide Phases 8-9 (Steps 8.1-9.4)

**VentSys-Specific Testing**:
```bash
# VentSys functional testing with TLS
# Test all valve controllers respond via TLS
for valve in sla fdm booth; do
    mosquitto_pub -h 192.168.20.101 -p 8883 \
        --cafile /config/ssl/ca/certs/ca-cert.pem \
        -u ventsys_controllers -P "CONTROLLER_PASSWORD" \
        -t "ventsys/$valve/valve/control" -m "50"
done

# Test fan control via TLS
mosquitto_pub -h 192.168.20.101 -p 8883 \
    --cafile /config/ssl/ca/certs/ca-cert.pem \
    -u ventsys_controllers -P "CONTROLLER_PASSWORD" \
    -t "ventsys/fan/percent" -m "75"

# Validate internet isolation maintained
# From each VentSys device:
ping -c 1 8.8.8.8              # Should fail
curl -I google.com             # Should fail
```

**VentSys Safety System Validation**:
- Test fire risk detection and response with TLS connectivity
- Validate printer cutoff functionality through TLS MQTT
- Test failsafe modes operate correctly with TLS authentication
- Verify Node-RED flows function with TLS MQTT broker

**Documentation Deliverables**:
- VentSys certificate management procedures
- Device certificate renewal schedules
- TLS troubleshooting guide for VentSys devices
- Emergency certificate replacement procedures
- VentSys device registry maintenance procedures

---

## Implementation Success Metrics

### Technical Success Criteria
- **Zero Internet Dependencies**: All VentSys devices function during internet outage
- **TLS Encryption**: 100% of MQTT traffic encrypted with local CA validation
- **Certificate Health**: All device certificates >6 months from expiry
- **Functional Preservation**: All existing VentSys features operational
- **Performance**: TLS adds <200ms latency to MQTT operations

### Security Success Criteria
- **Authentication**: All devices authenticate via certificates, no plaintext passwords
- **Authorization**: Device access limited to appropriate MQTT topics via ACL
- **Network Isolation**: IoT devices cannot access internet, confirmed by firewall logs
- **Certificate Validation**: All TLS connections validate against local CA only
- **Monitoring**: Certificate expiry monitoring operational with alerting

### Operational Success Criteria
- **Automated Renewal**: Certificate renewal system tested and operational
- **Emergency Procedures**: Certificate replacement procedures documented and tested
- **Monitoring Integration**: Certificate status visible in VentSys dashboard
- **Documentation**: Complete operational documentation for certificate management
- **Backup Systems**: Certificate authority and device registry backups automated

## Resource Requirements

### Time Investment (Following Implementation Guide)
- **Phase 1**: 8-12 hours (network setup + CA deployment)
- **Phase 2**: 4-6 hours (MQTT TLS configuration)
- **Phase 3**: 12-16 hours (device certificate provisioning + hardware expansion)
- **Phase 4**: 6-8 hours (HA integration + Node-RED updates)
- **Phase 5**: 8-10 hours (certificate lifecycle management)
- **Phase 6**: 4-6 hours (testing and documentation)
- **Total**: 42-58 hours over 9 weeks

### Hardware Requirements (Additional)
- **2x ESP32 DevKit boards** - FDM and Booth valve controllers
- **2x Servo motors** - Valve actuation hardware
- **Mounting hardware** - Physical installation components
- **No network infrastructure changes required**

### Skills Development
- **OpenWrt administration** - NTP server configuration, firewall management
- **PKI certificate management** - CA operations, certificate lifecycle
- **ESPHome TLS configuration** - Certificate integration, TLS troubleshooting
- **MQTT TLS operations** - Encrypted broker management, certificate authentication

This roadmap provides a complete path to implementing enterprise-grade TLS security for VentSys while maintaining complete network isolation and preserving all existing functionality. The approach eliminates internet dependencies while providing strong cryptographic protection for all VentSys communications.
