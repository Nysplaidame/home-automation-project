# VentSys TLS Technical Specifications

## Required Reference Documents  
- **Master Implementation**: `VentSys Solution 1 Implementation Guide` - Complete TLS deployment process
- **Network Architecture**: `vlan-config.conf`, `firewall-config.conf`, `dhcp-config.conf`, `wireless-config.conf`
- **Current VentSys Files**: `ventsys_fan_controller.yaml`, `ventsys_valve_controller.yaml`, `ventsys_combined.json`
- **Integration Analysis**: `ventsys_network_integration_analysis.md`
- **Implementation Roadmap**: `ventsys_implementation_roadmap.md`

## Network Integration with TLS Architecture

### VLAN Assignments (From Network Configs)
**VLAN 50 (IoT Sensors) - 192.168.50.0/24**
```
# VentSys Controllers (Certificate-authenticated)
192.168.50.21 - ventsys-main-fan (existing, TLS upgrade)  # A9-6: was ventsys-fan-controller
192.168.50.56 - ventsys-sla-print-valve (existing, TLS upgrade  # A9-6: was ventsys-sla-valve + topic fix)  
192.168.50.55 - ventsys-fdm-print-valve (canonical IP per dhcp-config.conf)  # R-2 fix: was .83
# R-2 fix: ventsys-booth-valve at .84 does not exist in current fleet.
  # Booth valve function handled by ventsys-fdm-branch-valve (.53) and ventsys-sla-branch-valve (.54).

# Future Sensor Nodes (TLS-ready)
192.168.50.31-39 - Environmental sensors (BME680, temperature/humidity/pressure/IAQ)
192.168.50.41-49 - Fire detection sensors (optical smoke, MQ-2)
192.168.50.51-59 - Air quality sensors (SGP30 VOC detection)
192.168.50.61-69 - Pressure differential sensors (SDP610)
192.168.50.71-79 - Smart plugs (printer emergency cutoff)
```

**VLAN 20 (Automation) - 192.168.20.0/24**
```
192.168.20.101 - Home Assistant (MQTT TLS broker + Local CA + NTP relay optional)
```

### WiFi Network Mapping (From wireless-config.conf)
**HomeIoT SSID Configuration**:
- **SSID**: "HomeIoT" (2.4GHz only, Channel 6)
- **Security**: WPA2-PSK (no PMF for IoT compatibility)
- **VLAN**: 50 (iot_sensors network)
- **Features**: Client isolation enabled, reduced power (15dBm)
- **Channel Strategy**: Fixed channel 6 (isolated from main networks on 1/11)

## TLS Infrastructure Architecture

### Local Certificate Authority Structure
**Implementation Reference**: Master Guide Phase 3 (Steps 3.1-3.4)

**CA Directory Structure**:
```bash
/config/ssl/ca/
├── certs/                    # CA and device certificates
│   ├── ca-cert.pem          # Root CA certificate (10-year)
│   ├── 192.168.20.101-cert.pem  # MQTT broker certificate
│   ├── ventsys-main-fan-cert.pem  # A9-6
│   ├── ventsys-sla-valve-cert.pem
│   └── ...
├── private/                  # Private keys (chmod 700)
│   ├── ca-key.pem           # Root CA private key
│   ├── 192.168.20.101-key.pem
│   └── ...
├── newcerts/                # Certificate database
├── index.txt                # Certificate index
├── serial                   # Certificate serial numbers
└── openssl.cnf             # CA configuration
```

**Certificate Lifecycle**:
- **Root CA**: 10-year validity (low maintenance)
- **Device Certificates**: 3-year validity (security balance)
- **Renewal Trigger**: 6 months before expiry (180 days)
- **Distribution**: Automated via MQTT

### MQTT TLS Configuration
**Implementation Reference**: Master Guide Phase 4 (Steps 4.1-4.6)

**Mosquitto TLS Setup** (`/config/mosquitto/mosquitto.conf`):
```conf
# Single TLS listener for all VentSys devices
listener 8883
protocol mqtt
cafile /mosquitto/config/certs/ca-cert.pem
certfile /mosquitto/config/certs/server.crt
keyfile /mosquitto/config/certs/server.key
require_certificate false          # Use username/password + TLS
use_identity_as_username false
tls_version tlsv1.2

# Security settings
allow_anonymous false
password_file /mosquitto/config/passwd
acl_file /mosquitto/config/acl.conf
max_connections 100
max_connections_per_ip 10
```

**VentSys MQTT Access Control** (`/config/mosquitto/acl.conf`):
```conf
# Home Assistant - full system access
user ha_secure_user
topic readwrite #

# VentSys Controllers - device control only
user ventsys_controllers
topic readwrite ventsys/fan/+
topic readwrite ventsys/+/valve/+
topic readwrite ventsys/devices/+/+
topic read ventsys/system/certificate/+/renewal

# VentSys Sensors - environmental data only
user ventsys_sensors  
topic readwrite ventsys/+/temperature
topic readwrite ventsys/+/humidity
topic readwrite ventsys/+/pressure
topic readwrite ventsys/+/voc
topic readwrite ventsys/+/smoke
topic readwrite homeassistant/sensor/ventsys/+
topic read ventsys/system/certificate/+/renewal

# Node-RED flows - system orchestration
user ventsys_nodered
topic readwrite ventsys/#
topic readwrite homeassistant/sensor/ventsys/#
topic read ventsys/system/certificate/+/renewal
```

**MQTT User Account Setup**:
```bash
# Create VentSys user accounts with strong passwords
mosquitto_passwd -b /config/mosquitto/passwd ha_secure_user "$(openssl rand -base64 32)"
mosquitto_passwd -b /config/mosquitto/passwd ventsys_controllers "$(openssl rand -base64 24)"
mosquitto_passwd -b /config/mosquitto/passwd ventsys_sensors "$(openssl rand -base64 24)"
mosquitto_passwd -b /config/mosquitto/passwd ventsys_nodered "$(openssl rand -base64 24)"
```

## Updated Firewall Rules

### Required Firewall Modifications (From firewall-config.conf)
**Implementation Reference**: Master Guide Phase 1 (Steps 1.1-1.2)

```bash
# Replace existing IoT rules with TLS-specific rules
# Allow IoT devices access to OpenWrt NTP server
uci add firewall rule
uci set firewall.@rule[-1].name='IoT NTP to Router'
uci set firewall.@rule[-1].src='iot_sensors'
uci set firewall.@rule[-1].dest_port='123'
uci set firewall.@rule[-1].proto='udp'
uci set firewall.@rule[-1].extra='-m limit --limit 5/minute --limit-burst 3'
uci set firewall.@rule[-1].target='ACCEPT'

# Allow IoT devices TLS MQTT access to Home Assistant
uci add firewall rule
uci set firewall.@rule[-1].name='IoT MQTT TLS to HA'
uci set firewall.@rule[-1].src='iot_sensors'
uci set firewall.@rule[-1].dest='automation'
uci set firewall.@rule[-1].dest_ip='192.168.20.101'
uci set firewall.@rule[-1].dest_port='8883'
uci set firewall.@rule[-1].proto='tcp'
uci set firewall.@rule[-1].extra='-m limit --limit 10/minute --limit-burst 5'
uci set firewall.@rule[-1].target='ACCEPT'

# Explicit block of non-TLS MQTT (security enforcement)
uci add firewall rule
uci set firewall.@rule[-1].name='Block IoT Plain MQTT'
uci set firewall.@rule[-1].src='iot_sensors'
uci set firewall.@rule[-1].dest='automation'
uci set firewall.@rule[-1].dest_port='1883'
uci set firewall.@rule[-1].proto='tcp'
uci set firewall.@rule[-1].target='REJECT'

# Log any internet access attempts (security monitoring)
uci add firewall rule
uci set firewall.@rule[-1].name='Log IoT Internet Attempts'
uci set firewall.@rule[-1].src='iot_sensors'
uci set firewall.@rule[-1].dest='wan'
uci set firewall.@rule[-1].target='REJECT'
uci set firewall.@rule[-1].extra='-j LOG --log-prefix "VENTSYS-INET-BLOCK: " --log-level 4'

# Commit changes
uci commit firewall
/etc/init.d/firewall restart
```

## ESPHome TLS Device Configurations

### Base TLS Configuration Template
**Implementation Reference**: Master Guide Phase 5 (Steps 5.1-5.3)

```yaml
# ventsys_base_tls_config.yaml - Shared by all VentSys devices
substitutions:
  device_name: ${device_name}           # e.g., "ventsys-main-fan"  # A9-6  
  device_ip: ${device_ip}               # e.g., "192.168.50.21"
  friendly_name: ${friendly_name}       # e.g., "VentSys Fan Controller"
  mqtt_user_type: ${mqtt_user_type}     # "ventsys_controllers" or "ventsys_sensors"

esphome:
  name: ${device_name}
  friendly_name: ${friendly_name}
  project:
    name: "ventsys.controller"
    version: "2.0-tls"

esp32:
  board: esp32dev
  framework:
    type: arduino

# WiFi connects to HomeIoT network (VLAN 50)
wifi:
  ssid: !secret iot_wifi_ssid           # "HomeIoT"
  password: !secret iot_wifi_pass
  manual_ip:
    static_ip: ${device_ip}
    gateway: 192.168.50.1               # VLAN 50 gateway
    subnet: 255.255.255.0
    dns1: 192.168.50.1                  # Use gateway DNS

# Time sync from OpenWrt NTP server
time:
  - platform: sntp
    id: sntp_time
    servers:
      - 192.168.50.1                    # OpenWrt router NTP
    timezone: "Europe/London"  # R-7 fix: was America/New_York; system is UK-based (Europe/London)
    update_interval: 6h

# TLS MQTT with local CA authentication
mqtt:
  broker: 192.168.20.101
  port: 8883
  username: !secret mqtt_user_${mqtt_user_type}
  password: !secret mqtt_pass_${mqtt_user_type}
  discovery: false
  keepalive: 60s
  reboot_timeout: 15min
  
  # Local CA certificate (inserted during provisioning)
  ca_certificate: |
    -----BEGIN CERTIFICATE-----
    # CA certificate content inserted by provisioning script
    # This validates the MQTT broker's TLS certificate
    -----END CERTIFICATE-----
  
  # Device lifecycle messages
  birth_message:
    topic: ventsys/devices/${device_name}/birth
    payload: !lambda |-
      char buf[300];
      snprintf(buf, sizeof(buf), 
               "{\"ts\":%u,\"device\":\"%s\",\"ip\":\"%s\",\"type\":\"%s\",\"fw\":\"%s\"}", 
               (unsigned)id(sntp_time).timestamp, "${device_name}", 
               "${device_ip}", "${mqtt_user_type}", ESPHOME_VERSION);
      return std::string(buf);
    retain: true
    
  will_message:
    topic: ventsys/devices/${device_name}/status
    payload: "offline"
    retain: true

# ESPHome API for Home Assistant (with encryption)
api:
  encryption:
    key: !secret api_encryption_key_${device_name}
  reboot_timeout: 15min

# OTA updates through Home Assistant
ota:
  safe_mode: true
  reboot_timeout: 10min
  num_attempts: 5

logger:
  level: INFO
  baud_rate: 0                          # Disable serial for production

# Device monitoring and certificate status
interval:
  - interval: 60s
    then:
      - mqtt.publish_json:
          topic: ventsys/devices/${device_name}/heartbeat
          payload: |-
            root["ts"] = id(sntp_time).timestamp;
            root["uptime_s"] = millis() / 1000;
            root["rssi"] = id(wifi_signal_sensor).state;
            root["free_heap"] = ESP.getFreeHeap();
            root["tls_connected"] = id(mqtt_client).is_connected();

sensor:
  - platform: wifi_signal
    name: "${friendly_name} WiFi Signal"
    id: wifi_signal_sensor
    update_interval: 60s
    internal: true
    
  - platform: uptime
    name: "${friendly_name} Uptime"
    id: uptime_sensor
    update_interval: 300s
    internal: true

# Certificate renewal handling
mqtt_subscribe:
  - topic: ventsys/system/certificate/${device_name}/renewal
    qos: 1
    id: cert_renewal_sub
    on_message:
      then:
        - logger.log:
            format: "Certificate renewal received for %s"
            args: [ '${device_name}' ]
        # Certificate installation logic would go here
        # For now, log and alert for manual intervention
        - mqtt.publish:
            topic: ventsys/devices/${device_name}/cert_renewal_received
            payload: !lambda 'return id(cert_renewal_sub).state;'
```

### Fan Controller TLS Configuration
```yaml
# ventsys_fan_controller_tls.yaml
substitutions:
  device_name: "ventsys-main-fan"  # A9-6
  device_ip: "192.168.50.21" 
  friendly_name: "VentSys Fan Controller"
  mqtt_user_type: "controllers"

packages:
  base_config: !include ventsys_base_tls_config.yaml

output:
  - platform: ledc
    id: fan_pwm
    pin: GPIO23
    frequency: 25000 Hz

fan:
  - platform: speed
    output: fan_pwm
    name: "Inline Fan"
    id: inline_fan_local
    speed_count: 100
    restore_mode: RESTORE_DEFAULT_OFF

# MQTT control subscriptions (unchanged topics for compatibility)
mqtt_subscribe:
  - topic: ventsys/fan/percent
    qos: 1
    id: fan_pct_sub
    on_message:
      then:
        - lambda: |-
            int pct = atoi(id(fan_pct_sub).state.c_str());
            if (pct < 0) pct = 0; 
            if (pct > 100) pct = 100;
            if (pct > 0) {
              id(inline_fan_local).turn_on();
              id(inline_fan_local).set_speed(pct);
            } else {
              id(inline_fan_local).turn_off();
            }
        - mqtt.publish:
            topic: ventsys/fan/percent_state
            payload: !lambda 'return id(fan_pct_sub).state;'
            retain: true
            
  - topic: ventsys/fan/control
    qos: 1
    id: fan_onoff_sub
    on_message:
      then:
        - lambda: |-
            std::string s = id(fan_onoff_sub).state;
            if (s == "on" || s == "ON") {
              id(inline_fan_local).turn_on();
            } else if (s == "off" || s == "OFF") {
              id(inline_fan_local).turn_off();
            }
        - mqtt.publish:
            topic: ventsys/fan/state
            payload: !lambda |-
              return id(inline_fan_local).state ? "ON" : "OFF";
            retain: true

# Publish fan state changes
fan:
  - platform: speed
    # ... (same as above)
    on_state:
      then:
        - mqtt.publish:
            topic: ventsys/fan/state  
            payload: !lambda |-
              return id(inline_fan_local).state ? "ON" : "OFF";
            retain: true
        - mqtt.publish:
            topic: ventsys/fan/percent_state
            payload: !lambda |-
              return to_string((int)(id(inline_fan_local).speed * 100));
            retain: true
```

### Valve Controller TLS Template
```yaml
# ventsys_valve_controller_tls_template.yaml
substitutions:
  device_name: ${valve_device_name}      # e.g., "ventsys-sla-print-valve"  # A9-6
  device_ip: ${valve_device_ip}          # e.g., "192.168.50.56"
  friendly_name: ${valve_friendly_name}  # e.g., "VentSys SLA Valve"
  valve_zone: ${valve_zone}              # e.g., "sla", "fdm", "booth"
  mqtt_user_type: "controllers"

packages:
  base_config: !include ventsys_base_tls_config.yaml

output:
  - platform: ledc
    id: servo_pwm
    pin: GPIO18
    frequency: 50 Hz

servo:
  - id: valve_servo
    output: servo_pwm
    min_angle: 0deg
    max_angle: 180deg
    restore: true
    auto_detach_time: 2s

globals:
  - id: current_valve_pct
    type: int
    restore_value: true
    initial_value: "0"

script:
  - id: set_valve_position
    parameters:
      pct: int
    then:
      - lambda: |-
          int c = pct; 
          if (c < 0) c = 0; 
          if (c > 100) c = 100;
          id(current_valve_pct) = c;
          float angle = (c / 100.0f) * 180.0f;
          id(valve_servo).write(angle);
          ESP_LOGI("valve", "Set ${valve_zone} valve to %d%% (%.1f degrees)", c, angle);

# MQTT valve control subscription
mqtt_subscribe:
  - topic: ventsys/${valve_zone}/valve/control
    qos: 1
    id: valve_control_sub
    on_message:
      then:
        - lambda: |-
            int pct = atoi(id(valve_control_sub).state.c_str());
            id(set_valve_position)->execute(pct);
        - mqtt.publish:
            topic: ventsys/${valve_zone}/valve/state
            payload: !lambda 'return id(valve_control_sub).state;'
            retain: true

# Publish valve position changes
number:
  - platform: template
    name: "${friendly_name} Position"
    id: valve_position
    min_value: 0
    max_value: 100
    step: 1
    mode: slider
    optimistic: true
    restore_value: true
    initial_value: 0
    set_action:
      then:
        - script.execute:
            id: set_valve_position
            pct: !lambda 'return (int)x;'
        - mqtt.publish:
            topic: ventsys/${valve_zone}/valve/state
            payload: !lambda 'return to_string((int)x);'
            retain: true
```

### Specific Device Configurations
```yaml
# ventsys_sla_valve_tls.yaml (Fix existing device topics)
substitutions:
  valve_device_name: "ventsys-sla-print-valve"  # A9-6
  valve_device_ip: "192.168.50.56"
  valve_friendly_name: "VentSys SLA Valve Controller"
  valve_zone: "sla"

packages:
  valve_template: !include ventsys_valve_controller_tls_template.yaml

# ventsys_fdm_valve_tls.yaml (New device)
substitutions:
  valve_device_name: "ventsys-fdm-print-valve"  # A9-6
  valve_device_ip: "192.168.50.55"  # R-2 fix: was .83; canonical is fdm-print-valve at .55
  valve_friendly_name: "VentSys FDM Valve Controller"
  valve_zone: "fdm"

packages:
  valve_template: !include ventsys_valve_controller_tls_template.yaml

# ventsys_booth_valve_tls.yaml (New device)  
substitutions:
  valve_device_name: "ventsys-booth-sensor"  # A9-6
  valve_device_ip: "192.168.50.54"  # R-2 fix: was .84; canonical is sla-branch-valve at .54
  valve_friendly_name: "VentSys Booth Valve Controller"
  valve_zone: "booth"

packages:
  valve_template: !include ventsys_valve_controller_tls_template.yaml
```

## Certificate Management System

### VentSys Device Registry
**Implementation Reference**: Master Guide Phase 7 (Steps 7.1-7.3)

```yaml
# /config/ventsys_device_registry.yaml
ventsys_infrastructure:
  ca_expires: "2034-12-01"              # 10-year CA certificate
  mqtt_broker_cert_expires: "2027-12-01" # 3-year MQTT broker cert
  
ventsys_devices:
    - name: ventsys-main-fan  # A9-6 fix: was ventsys-fan-controller
    mac: "XX:XX:XX:XX:XX:XX"           # Update with actual MAC
    ip: 192.168.50.21
    type: ESP32_Controller
    purpose: "Inline exhaust fan control"
    certificate_expires: "2027-12-01"
    mqtt_user: ventsys_controllers
    esphome_config: ventsys_fan_controller_tls.yaml
    topics:
      subscribe:
        - ventsys/fan/control
        - ventsys/fan/percent
        - ventsys/system/certificate/ventsys-main-fan/renewal  # A9-6
      publish:
        - ventsys/fan/state
        - ventsys/fan/percent_state
        - ventsys/devices/ventsys-main-fan/+  # A9-6
    
    - name: ventsys-sla-print-valve  # A9-6 fix: was ventsys-sla-valve
    mac: "XX:XX:XX:XX:XX:XX"           # Update with actual MAC
    ip: 192.168.50.56
    type: ESP32_Valve
    purpose: "SLA enclosure airflow control"
    certificate_expires: "2027-12-01"
    mqtt_user: ventsys_controllers
    esphome_config: ventsys_sla_valve_tls.yaml
    topics:
      subscribe:
        - ventsys/sla/valve/control
        - ventsys/system/certificate/ventsys-sla-print-valve/renewal  # A9-6
      publish:
        - ventsys/sla/valve/state
        - ventsys/devices/ventsys-sla-print-valve/+  # A9-6
        
  - name: ventsys-fdm-valve
    mac: "XX:XX:XX:XX:XX:XX"           # Update with actual MAC
    ip: 192.168.50.55  # R-2 fix: was .83; canonical fdm-print-valve
    type: ESP32_Valve
    purpose: "FDM print valve control (fdm-print-valve)"
    certificate_expires: "2027-12-01"
    mqtt_user: ventsys_controllers
    esphome_config: ventsys_fdm_valve_tls.yaml
    topics:
      subscribe:
        - ventsys/fdm/valve/control
        - ventsys/system/certificate/ventsys-fdm-print-valve/renewal  # A9-6
      publish:
        - ventsys/fdm/valve/state
        - ventsys/devices/ventsys-fdm-print-valve/+  # A9-6
        
    - name: ventsys-booth-sensor  # A9-6 fix: was ventsys-booth-valve (device does not exist)
    mac: "XX:XX:XX:XX:XX:XX"           # Update with actual MAC  
    ip: 192.168.50.54  # R-2 fix: was .84; canonical sla-branch-valve
    type: ESP32_Valve
    purpose: "SLA branch valve control (sla-branch-valve)"
    certificate_expires: "2027-12-01"
    mqtt_user: ventsys_controllers
    esphome_config: ventsys_booth_valve_tls.yaml
    topics:
      subscribe:
        - ventsys/booth/valve/control
        - ventsys/system/certificate/ventsys-booth-sensor/renewal  # A9-6
      publish:
        - ventsys/booth/valve/state
        - ventsys/devices/ventsys-booth-sensor/+  # A9-6

# Future sensor nodes
ventsys_future_sensors:
  - name: ventsys-sla-sensors
    ip: 192.168.50.31
    purpose: "SLA enclosure environmental monitoring"
    sensors: ["temperature", "humidity", "voc", "smoke", "pressure"]
  - name: ventsys-fdm-sensors  
    ip: 192.168.50.32
    purpose: "FDM enclosure environmental monitoring"
    sensors: ["temperature", "humidity", "voc", "smoke", "pressure"]
  - name: ventsys-booth-sensors
    ip: 192.168.50.33
    purpose: "Spray booth environmental monitoring" 
    sensors: ["temperature", "humidity", "voc", "smoke", "pressure"]
```

### Home Assistant Certificate Monitoring
**Implementation Reference**: Master Guide Phase 6 (Steps 6.1-6.4)

```yaml
# Add to /config/configuration.yaml
template:
  - sensor:
    - name: "VentSys Certificate Status"
      state: >
        {% set expiring = namespace(count=0) %}
        {% set devices = [
          'ventsys_fan_controller',
          'ventsys_sla_valve', 
          'ventsys_fdm_valve',
          'ventsys_booth_valve'
        ] %}
        {% for device in devices %}
          {% set entity = 'sensor.' + device + '_cert_expires' %}
          {% if states(entity) | int < 60 %}
            {% set expiring.count = expiring.count + 1 %}
          {% endif %}
        {% endfor %}
        {% if expiring.count > 0 %}
          {{ expiring.count }} certificates expiring soon
        {% else %}
          All certificates valid
        {% endif %}
      attributes:
        total_devices: 4
        expiring_devices: >
          {% set expiring = [] %}
          {% set devices = [
            'ventsys_fan_controller',
            'ventsys_sla_valve',
            'ventsys_fdm_valve', 
            'ventsys_booth_valve'
          ] %}
          {% for device in devices %}
            {% set entity = 'sensor.' + device + '_cert_expires' %}
            {% if states(entity) | int < 60 %}
              {% set expiring = expiring + [device] %}
            {% endif %}
          {% endfor %}
          {{ expiring }}

# Certificate expiry sensors for each device
mqtt:
  sensor:
    - name: "VentSys Fan Controller Cert Expires"
      state_topic: "ventsys/devices/ventsys-main-fan/cert_status"  # A9-6
      value_template: "{{ value_json.days_until_expiry }}"
      json_attributes_topic: "ventsys/devices/ventsys-main-fan/cert_status"  # A9-6
      unit_of_measurement: "days"
      device_class: duration
      
    - name: "VentSys SLA Valve Cert Expires"
      state_topic: "ventsys/devices/ventsys-sla-print-valve/cert_status"  # A9-6
      value_template: "{{ value_json.days_until_expiry }}"
      json_attributes_topic: "ventsys/devices/ventsys-sla-print-valve/cert_status"  # A9-6
      unit_of_measurement: "days"
      device_class: duration
      
    # Additional cert status sensors for FDM and Booth valves...
```

## Node-RED TLS Integration

### Updated Node-RED MQTT Broker Configuration
```javascript
// Single TLS MQTT broker for all VentSys flows
{
  "id": "ventsys-mqtt-tls",
  "type": "mqtt-broker",
  "name": "VentSys MQTT TLS",
  "broker": "192.168.20.101",
  "port": "8883",
  "tls": "ventsys-tls-config",
  "credentials": {
    "user": "ventsys_nodered",
    "password": "NODE_RED_TLS_PASSWORD"
  },
  "usetls": true,
  "verifyservercert": true,
  "compatmode": false,
  "protocolversion": "4",
  "keepalive": "60",
  "cleansession": true
}

// TLS configuration referencing local CA
{
  "id": "ventsys-tls-config",
  "type": "tls-config",
  "name": "VentSys Local CA TLS",
  "ca": "/config/ssl/ca/certs/ca-cert.pem",
  "verifyservercert": true,
  "servername": "192.168.20.101"
}
```

### Enhanced VentSys Flow with Certificate Monitoring
```javascript
// Certificate status monitoring function
{
  "id": "ventsys-cert-monitor",
  "type": "function",
  "name": "VentSys Certificate Monitor",
  "func": "const devices = ['ventsys-main-fan'  # A9-6, 'ventsys-sla-valve', 'ventsys-fdm-print-valve'  # A9-6, 'ventsys-booth-sensor'  # A9-6]; const warnings = []; for (const device of devices) { const daysLeft = flow.get(`${device}_cert_days`) || 365; if (daysLeft < 60) { warnings.push({ device: device, days: daysLeft, status: daysLeft < 30 ? 'critical' : 'warning' }); } } if (warnings.length > 0) { msg.payload = { alert: 'certificate_expiry', devices: warnings, timestamp: Date.now() }; return msg; } return null;",
  "outputs": 1,
  "wires": [["ventsys-cert-alert"]]
}

// Enhanced failsafe with certificate validation
{
  "id": "ventsys-failsafe-enhanced",
  "type": "function", 
  "name": "Enhanced Failsafe with TLS",
  "func": "// Check certificate status first const certStatus = flow.get('ventsys_cert_status') || 'unknown'; if (certStatus === 'critical') { msg.cert_alert = true; } // Original failsafe logic msg.payload = 100; const fanMsg = {...msg, payload: 'on'}; return [msg, msg, msg, fanMsg, msg.cert_alert ? {payload: certStatus} : null];",
  "outputs": 5,
  "wires": [
    ["ventsys-sla-valve-tls"],
    ["ventsys-fdm-valve-tls"], 
            ["ventsys-booth-sensor-tls"],  # A9-6 fix: was ventsys-booth-valve-tls
    ["ventsys-fan-tls"],
    ["ventsys-cert-emergency-alert"]
  ]
}
```

## Testing and Validation Procedures

### TLS Connectivity Testing
**Implementation Reference**: Master Guide Phase 8 (Steps 8.1-8.4)

```bash
# Test certificate chain validation
openssl verify -CAfile /config/ssl/ca/certs/ca-cert.pem \
    /config/ssl/ca/certs/192.168.20.101-cert.pem

# Test MQTT TLS connectivity
mosquitto_pub -h 192.168.20.101 -p 8883 \
    --cafile /config/ssl/ca/certs/ca-cert.pem \
    -u ventsys_controllers -P "CONTROLLER_TLS_PASSWORD" \
    -t "ventsys/test/tls" -m "TLS connectivity verified" -d

# Test device-specific valve control via TLS
for zone in sla fdm booth; do
    echo "Testing $zone valve via TLS..."
    mosquitto_pub -h 192.168.20.101 -p 8883 \
        --cafile /config/ssl/ca/certs/ca-cert.pem \
        -u ventsys_controllers -P "CONTROLLER_TLS_PASSWORD" \
        -t "ventsys/$zone/valve/control" -m "25" -d
    sleep 2
done

# Test fan control via TLS
mosquitto_pub -h 192.168.20.101 -p 8883 \
    --cafile /config/ssl/ca/certs/ca-cert.pem \
    -u ventsys_controllers -P "CONTROLLER_TLS_PASSWORD" \
    -t "ventsys/fan/percent" -m "60" -d

# Verify internet isolation maintained
# Should fail from IoT devices:
ping -c 1 8.8.8.8
curl -I google.com
nslookup github.com
```

### Security Validation Checklist
```bash
# 1. Certificate validation
✓ All device certificates signed by local CA
✓ MQTT broker certificate validates against CA
✓ Certificate expiry dates > 6 months
✓ Private keys secured with proper permissions

# 2. Network isolation  
✓ IoT devices cannot access internet
✓ IoT devices can reach OpenWrt NTP (UDP/123)
✓ IoT devices can reach HA MQTT TLS (TCP/8883)
✓ IoT devices blocked from plain MQTT (TCP/1883)

# 3. TLS connectivity
✓ All MQTT connections use TLS encryption
✓ Certificate-based server validation working
✓ No plaintext MQTT traffic detected
✓ TLS version 1.2 or higher enforced

# 4. Functional validation
✓ All VentSys devices responsive via TLS MQTT
✓ Fan control operational through TLS
✓ All valve controllers operational through TLS  
✓ Node-RED flows functional with TLS broker
✓ Home Assistant entities updated via TLS
```

## Deployment Timeline and Resources

### Implementation Time Estimates
- **Phase 1**: 8-10 hours (OpenWrt NTP + CA setup)
- **Phase 2**: 4-6 hours (MQTT TLS configuration)  
- **Phase 3**: 14-18 hours (device cert provisioning + hardware expansion)
- **Phase 4**: 6-8 hours (HA integration + Node-RED updates)
- **Phase 5**: 8-10 hours (certificate lifecycle automation)
- **Phase 6**: 4-6 hours (testing and documentation)
- **Total**: 44-58 hours over 9 weeks

### Required Additional Hardware
- **2x ESP32 DevKit boards** - FDM and Booth valve controllers ($12-15 each)
- **2x SG90 Servo motors** - Valve actuation ($5-8 each)  
- **Breadboards/perfboards** - Prototyping and final assembly ($10-15)
- **Jumper wires and connectors** - Wiring ($10-15)
- **Mounting hardware** - Physical installation ($15-25)
- **Total hardware cost**: ~$70-100

### Skills and Knowledge Requirements  
- **OpenWrt Administration**: NTP configuration, firewall rule management
- **PKI Certificate Management**: CA operations, certificate lifecycle, renewal automation
- **ESPHome Advanced Configuration**: TLS integration, certificate embedding, troubleshooting
- **MQTT TLS Operations**: Broker configuration, certificate authentication, access control
- **Home Assistant Integration**: MQTT TLS setup, certificate monitoring, automation development

This TLS-based approach provides enterprise-grade security while maintaining complete isolation from the internet and preserving all existing VentSys functionality. The comprehensive certificate management system ensures long-term operational security with minimal maintenance overhead through automated renewal processes.
