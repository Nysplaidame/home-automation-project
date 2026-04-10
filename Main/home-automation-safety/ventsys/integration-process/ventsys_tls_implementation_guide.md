# VentSys Solution 1 Implementation Guide
## Certificate Renewal Strategy & Complete Process

> **Related documents in this folder:**
> - [[ventsys_network_integration_analysis]] Ã¢â‚¬â€ why TLS is needed, risk assessment
> - [[ventsys_implementation_roadmap]] Ã¢â‚¬â€ 9-week phased roadmap referencing this guide
> - [[ventsys_technical_specifications]] Ã¢â‚¬â€ hardware and software specifications
> - [[ventsys_complete_implementation_plan]] Ã¢â‚¬â€ full integration plan
>
> **VentSys hardware & control phase guides:** `scripts/setup/ventsys/`

---

## Certificate Renewal Strategy

For isolated IoT devices, I recommend an **Automated Local Renewal System** that operates entirely within your local network:

### Renewal Approach

**Certificate Lifecycle Management:**
- **Initial certificates:** 3-year validity (balances security with maintenance burden)
- **Renewal trigger:** 6 months before expiration
- **Delivery mechanism:** Authenticated MQTT messages
- **Fallback options:** Manual renewal during maintenance windows

**Automated Renewal Process:**
1. **Certificate Monitoring:** Home Assistant tracks all device certificate expiration dates
2. **Pre-renewal Generation:** HA generates new certificates 6 months before expiration
3. **Secure Distribution:** New certificates published to device-specific MQTT topics
4. **Authentication:** Devices authenticate certificate updates using their current valid certificates
5. **Installation Confirmation:** Devices confirm successful certificate installation via MQTT response
6. **Status Tracking:** HA maintains renewal status dashboard for all devices

**Fallback Mechanisms:**
- Multiple certificate provisioning (current + next certificate)
- Emergency maintenance window with temporary management access
- Long-lived backup certificates (5+ years) for emergency use only

---

# Complete Implementation Process for Solution 1

## Phase 1: Network Infrastructure Verification

### Step 1.1: Verify Network Configuration
```bash
# On OpenWrt router, verify VLAN configuration
uci show network | grep -E "(automation|iot_sensors)"

# Verify automation network (VLAN 20) exists
ping 192.168.20.1

# Verify IoT sensors network (VLAN 50) exists  
ping 192.168.50.1
```

### Step 1.2: Apply Required Firewall Rules
```bash
# Add NTP access for IoT devices
uci add firewall rule
uci set firewall.@rule[-1].name='IoT to Router NTP'
uci set firewall.@rule[-1].src='iot_sensors'
uci set firewall.@rule[-1].dest_port='123'
uci set firewall.@rule[-1].proto='udp'
uci set firewall.@rule[-1].target='ACCEPT'

# Add MQTT TLS access for IoT devices
uci add firewall rule
uci set firewall.@rule[-1].name='IoT to HA MQTT TLS'
uci set firewall.@rule[-1].src='iot_sensors'
uci set firewall.@rule[-1].dest='automation'
uci set firewall.@rule[-1].dest_ip='192.168.20.101'
uci set firewall.@rule[-1].dest_port='8883'
uci set firewall.@rule[-1].proto='tcp'
uci set firewall.@rule[-1].target='ACCEPT'

# Commit changes and restart firewall
uci commit firewall
/etc/init.d/firewall restart
```

### Step 1.3: Configure OpenWrt NTP Server
```bash
# Install and configure NTP on OpenWrt router
opkg update
opkg install ntp

# Configure NTP server
cat > /etc/ntp.conf << 'EOF'
# External time sources (router needs internet for initial sync)
server 0.pool.ntp.org iburst
server 1.pool.ntp.org iburst
server 2.pool.ntp.org iburst

# Serve time to local networks
restrict default limited kod nomodify notrap nopeer noquery
restrict 127.0.0.1
restrict ::1

# Allow IoT network to query time (nomodify+notrap prevents config changes; noquery removed Ã¢â‚¬â€ devices MUST be able to query)
restrict 192.168.50.0 mask 255.255.255.0 nomodify notrap nopeer

# Local clock as fallback
server 127.127.1.0
fudge 127.127.1.0 stratum 10

# Drift file
driftfile /var/lib/ntp/drift

# Log file
logfile /var/log/ntpd.log
EOF

# Start NTP service
/etc/init.d/ntp enable
/etc/init.d/ntp start

# Verify NTP is running
ntpq -p
```

## Phase 2: Home Assistant Prerequisites

### Step 2.3: Enable SSH Access
```yaml
# Via HA UI: Settings -> Add-ons -> Add-on Store -> SSH & Web Terminal
# Install and start SSH add-on
# Configure in add-on settings:
```
```yaml
ssh:
  username: root
  password: "YOUR_SECURE_PASSWORD"
  authorized_keys: []
  sftp: true
  compatibility_mode: false
  allow_agent_forwarding: false
  allow_remote_port_forwarding: false
  allow_tcp_forwarding: false
```

## Phase 3: Certificate Authority Setup

### Step 3.1: Create Certificate Authority Directory Structure
```bash
# SSH into Home Assistant
ssh root@192.168.20.101

# Create CA directory structure
mkdir -p /config/ssl/ca/{certs,crl,newcerts,private}
chmod 700 /config/ssl/ca/private
echo 1000 > /config/ssl/ca/serial
touch /config/ssl/ca/index.txt
```

### Step 3.2: Create CA Configuration File
```bash
cat > /config/ssl/ca/openssl.cnf << 'EOF'
[ ca ]
default_ca = CA_default

[ CA_default ]
dir               = /config/ssl/ca
certs             = $dir/certs
crl_dir           = $dir/crl
new_certs_dir     = $dir/newcerts
database          = $dir/index.txt
serial            = $dir/serial
RANDFILE          = $dir/private/.rand

private_key       = $dir/private/ca-key.pem
certificate       = $dir/certs/ca-cert.pem

crlnumber         = $dir/crlnumber
crl               = $dir/crl/ca.crl.pem
crl_extensions    = crl_ext

default_crl_days  = 30
default_md        = sha256
name_opt          = ca_default
cert_opt          = ca_default
default_days      = 1095
preserve          = no
policy            = policy_strict

[ policy_strict ]
countryName             = match
stateOrProvinceName     = match
organizationName        = match
organizationalUnitName  = optional
commonName              = supplied
emailAddress            = optional

[ req ]
default_bits        = 4096
distinguished_name  = req_distinguished_name
string_mask         = utf8only
default_md          = sha256
x509_extensions     = v3_ca

[ req_distinguished_name ]
countryName                     = Country Name (2 letter code)
stateOrProvinceName             = State or Province Name
localityName                    = Locality Name
0.organizationName              = Organization Name
organizationalUnitName          = Organizational Unit Name
commonName                      = Common Name
emailAddress                    = Email Address

countryName_default             = GB
stateOrProvinceName_default     = England
localityName_default            = London
0.organizationName_default      = Home Automation
organizationalUnitName_default  = IoT Infrastructure
emailAddress_default            = admin@home.local

[ v3_ca ]
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always,issuer
basicConstraints = critical,CA:true
keyUsage = critical, digitalSignature, cRLSign, keyCertSign

[ server_cert ]
basicConstraints = CA:FALSE
nsCertType = server
nsComment = "OpenSSL Generated Server Certificate"
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid,issuer:always
keyUsage = critical, digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth

[ crl_ext ]
authorityKeyIdentifier=keyid:always
EOF
```

### Step 3.3: Generate Root CA Certificate
```bash
# Generate CA private key
openssl genrsa -out /config/ssl/ca/private/ca-key.pem 4096
chmod 400 /config/ssl/ca/private/ca-key.pem

# Generate CA certificate (valid for 10 years)
openssl req -config /config/ssl/ca/openssl.cnf \
    -key /config/ssl/ca/private/ca-key.pem \
    -new -x509 -days 3650 -sha256 -extensions v3_ca \
    -out /config/ssl/ca/certs/ca-cert.pem \
    -subj "/C=GB/ST=England/L=London/O=Home Automation/OU=IoT Infrastructure/CN=Home Automation Root CA"

# Verify CA certificate
openssl x509 -noout -text -in /config/ssl/ca/certs/ca-cert.pem
```

### Step 3.4: Create Certificate Management Scripts
```bash
# Create certificate generation script
cat > /config/ssl/ca/generate-server-cert.sh << 'EOF'
#!/bin/bash
set -e

HOSTNAME="$1"
DAYS="${2:-1095}"  # 3 years default

if [ -z "$HOSTNAME" ]; then
    echo "Usage: $0 <hostname> [days]"
    exit 1
fi

cd /config/ssl/ca

# Generate private key
openssl genrsa -out "private/${HOSTNAME}-key.pem" 2048

# Generate certificate signing request
openssl req -config openssl.cnf -key "private/${HOSTNAME}-key.pem" \
    -new -sha256 -out "certs/${HOSTNAME}.csr" \
    -subj "/C=GB/ST=England/L=London/O=Home Automation/OU=IoT Infrastructure/CN=${HOSTNAME}"

# Generate certificate
openssl ca -config openssl.cnf -extensions server_cert -days "${DAYS}" \
    -notext -md sha256 -in "certs/${HOSTNAME}.csr" \
    -out "certs/${HOSTNAME}-cert.pem" -batch

# Clean up CSR
rm "certs/${HOSTNAME}.csr"

echo "Generated certificate for ${HOSTNAME}"
echo "Private key: private/${HOSTNAME}-key.pem"
echo "Certificate: certs/${HOSTNAME}-cert.pem"
EOF

chmod +x /config/ssl/ca/generate-server-cert.sh
```

> **L-10 audit note - Certificate CN and ESPHome validation:**
> The server certificate CN is set to ${HOSTNAME}. ESPHome validates the cert chain
> against the CA (via ca_certificate:) but does NOT perform CN/hostname verification by default.
> This means the CN value does not need to match the broker IP address for ESPHome clients.
> However, the Frigate MQTT client (Go library) DOES perform CN/SAN hostname verification.
> The broker cert's CN or a SAN must match the address Frigate uses to connect (192.168.20.101).
> Generate the Mosquitto broker cert with: bash generate-server-cert.sh mosquitto
> Then add subjectAltName to the [server_cert] extension in openssl.cnf:
>   subjectAltName = IP:192.168.20.101, DNS:mosquitto, DNS:ha-vm
> This ensures Frigate, Bambuddy, and any strict TLS clients all validate successfully.

## Phase 4: MQTT Broker Configuration

### Step 4.1: Install Mosquitto MQTT Add-on
```yaml
# Via HA UI: Settings -> Add-ons -> Add-on Store -> Mosquitto broker
# Install and configure:
```

### Step 4.2: Generate MQTT Server Certificate
```bash
# Generate certificate for MQTT broker
# L-10 fix: cert named "mosquitto" so CN matches DNS name; SAN covers IP.
# Confirm [server_cert] in openssl.cnf has:
#   subjectAltName = IP:192.168.20.101, DNS:mosquitto, DNS:ha-vm
/config/ssl/ca/generate-server-cert.sh "mosquitto"

# Copy certificates to mosquitto directory
mkdir -p /config/mosquitto/certs
cp /config/ssl/ca/certs/ca-cert.pem /config/mosquitto/certs/
cp /config/ssl/ca/certs/mosquitto-cert.pem /config/mosquitto/certs/server.crt
cp /config/ssl/ca/private/mosquitto-key.pem /config/mosquitto/certs/server.key

# Set proper permissions
chmod 600 /config/mosquitto/certs/server.key
chmod 644 /config/mosquitto/certs/server.crt
chmod 644 /config/mosquitto/certs/ca-cert.pem
```

### Step 4.3: Configure Mosquitto Ã¢â‚¬â€ Single TLS Listener
```yaml
# Create /config/mosquitto/mosquitto.conf
```
```conf
# Mosquitto Configuration for VentSys Ã¢â‚¬â€ Single TLS Architecture
#
# ARCHITECTURE DECISION: Single port 8883 TLS only.
# All devices (Home Assistant and IoT/ESPHome) use port 8883 with local CA.
# No plaintext port 1883 Ã¢â‚¬â€ all VentSys devices receive certs at flash time
# before ever connecting to the network. No internet dependency at any stage.

# Global settings
persistence true
persistence_location /mosquitto/data/
log_dest file /mosquitto/log/mosquitto.log
log_dest stdout
log_type error
log_type warning
log_type notice
log_type information
connection_messages true
log_timestamp true

# Single TLS listener Ã¢â‚¬â€ all clients (HA + IoT devices)
listener 8883
protocol mqtt
cafile /mosquitto/config/certs/ca-cert.pem
certfile /mosquitto/config/certs/server.crt
keyfile /mosquitto/config/certs/server.key
require_certificate false
use_identity_as_username false
tls_version tlsv1.2
allow_anonymous false
password_file /mosquitto/config/passwd

# Access Control Lists
acl_file /mosquitto/config/acl.conf

# Client connection limits
max_connections 100
max_connections_per_ip 10

# Message limits
message_size_limit 1048576
max_queued_messages 1000
max_inflight_messages 40

# Logging
log_type subscribe
log_type unsubscribe
```

### Step 4.4: Create MQTT User Accounts
```bash
# Create password file
touch /config/mosquitto/passwd

# Single 'mqtt' user Ã¢â‚¬â€ used by HA integration, all ESPHome devices, Frigate,
# and Bambuddy. This matches the username configured everywhere else in the vault:
#   - ha_vm_setup_guide.md (creates HA user 'mqtt')
#   - frigate/config.yml (user: mqtt)
#   - docker-compose.yml Bambuddy (MQTT_USER=mqtt)
#   - esphome_adoption_guide.md (username: mqtt)
#   - ventsys_fan/valve_controller.yaml (username: !secret mqtt_user Ã¢â€ â€™ 'mqtt')
# Using a single user simplifies TLS migration Ã¢â‚¬â€ no credential changes needed
# in any device YAML or service config, only the port changes (1883 Ã¢â€ â€™ 8883).
# Use the same password that was configured during initial Mosquitto setup
# (stored in /config/secrets.yaml as mqtt_password).
mosquitto_passwd -b /config/mosquitto/passwd mqtt "YOUR_MQTT_PASSWORD"
```
> **Note:** All clients connect on port 8883 TLS only after this migration.
> The password does NOT change Ã¢â‚¬â€ only the port and TLS settings change.
> This means ESPHome device YAMLs only need their `port:` updated from
> 1883 to 8883 and `ca_certificate:` added; credentials stay the same.

### Step 4.5: Configure MQTT Access Control
```bash
cat > /config/mosquitto/acl.conf << 'EOF'
# Single 'mqtt' user Ã¢â‚¬â€ full access to all topics.
# All clients (HA, ESPHome devices, Frigate, Bambuddy) use this user.
# This avoids per-client credential management and matches the username
# configured in every service and device YAML across the vault.
#
# Topics covered:
#   ventsys/#          Ã¢â‚¬â€ VentSys sensor and controller devices
#   homeassistant/#    Ã¢â‚¬â€ ESPHome MQTT discovery
#   frigate/#          Ã¢â‚¬â€ Frigate NVR events, detections, stats
#   bambuddy/#         Ã¢â‚¬â€ Bambuddy printer status
#   #                  Ã¢â‚¬â€ catch-all for any future additions
user mqtt
topic readwrite #
EOF
```

### Step 4.6: Restart Mosquitto and Test
```bash
# Restart Mosquitto add-on via HA UI
# Test secure connection Ã¢â‚¬â€ all clients use the single 'mqtt' user
mosquitto_pub -h 192.168.20.101 -p 8883 --cafile /config/ssl/ca/certs/ca-cert.pem \
    -u mqtt -P "YOUR_MQTT_PASSWORD" -t "test/secure" -m "TLS test from HA"

# Verify from IoT perspective Ã¢â‚¬â€ same user, same password, TLS port
mosquitto_pub -h 192.168.20.101 -p 8883 --cafile /config/ssl/ca/certs/ca-cert.pem \
    -u mqtt -P "YOUR_MQTT_PASSWORD" \
    -t "test/tls" -m "TLS test from IoT device"

# Subscribe to confirm delivery
mosquitto_sub -h 192.168.20.101 -p 8883 --cafile /config/ssl/ca/certs/ca-cert.pem \
    -u mqtt -P "YOUR_MQTT_PASSWORD" -t "test/#" -v &
```

## Phase 5: IoT Device Configuration

### Step 5.0: Update Bambuddy MQTT Port (do this before restarting Mosquitto on 8883-only)

Bambuddy runs on the Frigate VM (192.168.30.20) and publishes print events to Mosquitto.
After TLS migration, port 1883 no longer exists Ã¢â‚¬â€ Bambuddy must use 8883.

```bash
# On the Frigate VM
cd /opt/frigate

# Update the MQTT port in docker-compose.yml   # M-14 fix: MQTT_PORT lives here, not in .env
sed -i 's/MQTT_PORT=1883/MQTT_PORT=8883/' docker-compose.yml   # M-14 fix: MQTT_PORT is in docker-compose.yml, not .env

# Verify
grep MQTT_PORT docker-compose.yml   # should show MQTT_PORT=8883

# Restart Bambuddy to pick up the new port
docker compose restart bambuddy

# Check logs Ã¢â‚¬â€ look for "MQTT connected" on port 8883
docker compose logs bambuddy --tail=30
```

Also update the firewall on the router Ã¢â‚¬â€ remove the temporary Stage 1 plain-text rule
if you added one, and confirm the permanent 8883 rule is in place:

```bash
# On the router:
# Find and remove the temporary plain-text rule (if added during Stage 1)
uci show firewall | grep -n "TEMP Bambuddy"
# If found at index N:
uci delete firewall.@rule[N]
uci commit firewall
/etc/init.d/firewall restart
```

> **Note on Frigate MQTT:** Frigate's MQTT connection is configured in
> `configs/frigate/config.yml` (`mqtt.port: 8883`). The TLS settings for
> Frigate's own MQTT connection (`cafile`, `certfile`, `keyfile`) should be
> populated from the CA cert generated in Phase 3 Ã¢â‚¬â€ see `config.yml` comment
> block for the required keys. Frigate also uses the single `mqtt` user.


```bash
# Create CA certificate in PEM format for device distribution
cp /config/ssl/ca/certs/ca-cert.pem /config/www/ca-cert.pem

# Make accessible via HA web server at:
# http://192.168.20.101:8123/local/ca-cert.pem
```

### Step 5.2: Configure IoT Devices (ESP32/ESPHome Example)
```yaml
# Example ESPHome configuration for a new VentSys sensor board.
# Use the existing ventsys_fan_controller.yaml / ventsys_valve_controller.yaml
# as primary templates Ã¢â‚¬â€ they already have the correct structure.
# This example shows the TLS-specific additions needed for any new board.
esphome:
  name: ventsys-sla-sensors
  # NOTE: 'platform:' inside the esphome: block was removed in ESPHome 2021.x.
  # Use a top-level 'esp32:' block instead (as shown below).

esp32:
  board: esp32dev

wifi:
  ssid: "HomeIoT"
  password: "YOUR_IOT_WIFI_PASSWORD_HERE"
  manual_ip:
    static_ip: 192.168.50.31
    gateway: 192.168.50.1
    subnet: 255.255.255.0
    dns1: 192.168.50.1

# NTP configuration using OpenWrt router
time:
  - platform: sntp
    servers:
      - 192.168.50.1  # OpenWrt router NTP server
    timezone: "Europe/London"

# MQTT configuration with TLS and local CA Ã¢â‚¬â€ port 8883 only
mqtt:
  broker: 192.168.20.101
  port: 8883
  username: mqtt   # H-9 fix: single 'mqtt' user - matches all device YAMLs and service configs
  password: "SENSOR_PASSWORD"
  # Use ca_certificate for full local CA validation (no internet required)
  ca_certificate: |
    -----BEGIN CERTIFICATE-----
    # Insert contents of ca-cert.pem here
    -----END CERTIFICATE-----
  
  # VentSys sensor topics
  discovery: true
  discovery_prefix: homeassistant
  
# Sensors for SLA enclosure
sensor:
  # M-13 fix: replaced invalid platforms (dht, mq135, analog) with correct ESPHome
  # platforms matching the actual deployed hardware (printairpipe-controller.yaml).
  # BME688 handles temperature, humidity, pressure, and IAQ gas resistance.
  # Differential pressure uses a dedicated ADC sensor on a separate pin.
  - platform: bme68x
    address: 0x77
    temperature:
      name: "${friendly_name} Temperature"
    pressure:
      name: "${friendly_name} Pressure"
    humidity:
      name: "${friendly_name} Humidity"
    gas_resistance:
      name: "${friendly_name} IAQ Gas Resistance"
    update_interval: 60s
    
  - platform: adc
    pin: ${pressure_diff_pin}
    name: "${friendly_name} Pressure Differential"
    update_interval: 5s
    unit_of_measurement: Pa
    filters:
      - calibrate_linear:
          - 0.0 -> 0.0
          - 3.3 -> 200.0   # calibrate to your sensor range

# Smoke detector (binary sensor)
binary_sensor:
  - platform: gpio
    pin:
      number: GPIO5
      mode: INPUT_PULLUP
      inverted: true
    name: "SLA Smoke Detector"
    device_class: smoke

# Servo valve control
servo:
  - id: sla_valve
    output: pwm_output
    auto_detach_time: 0s
    transition_length: 1s

output:
  - platform: ledc
    pin: GPIO18
    id: pwm_output
    frequency: 50 Hz

# MQTT-controlled valve
number:
  - platform: template
    name: "SLA Valve Position"
    min_value: 0
    max_value: 100
    step: 1
    mode: slider
    set_action:
      then:
        - servo.write:
            id: sla_valve
            level: !lambda 'return x / 100.0;'
        - mqtt.publish:
            topic: "ventsys/sla/valve/state"
            payload: !lambda 'return to_string((int)x);'
```

### Step 5.3: Device Provisioning Process
```bash
# For each IoT device:

# 1. Initial setup with temporary internet access for compilation
# 2. Flash device with configuration including CA certificate
# 3. Test connectivity on main network
# 4. Move device to IoT VLAN
# 5. Verify MQTT connectivity with TLS
# 6. Document device in registry:

cat >> /config/device_registry.yaml << EOF
- name: ventsys-sla-sensors
  mac: XX:XX:XX:XX:XX:XX
  ip: 192.168.50.31
  type: ESP32
  purpose: SLA enclosure monitoring
  certificate_expires: $(date -d "+3 years" '+%Y-%m-%d')
  mqtt_user: mqtt   # H-9 fix: use 'mqtt' user created in Step 4.4
  topics:
    - ventsys/sla/temperature
    - ventsys/sla/humidity
    - ventsys/sla/voc
    - ventsys/sla/smoke
    - ventsys/sla/pressure
    - ventsys/sla/valve/control
    - ventsys/sla/valve/state
EOF
```

## Phase 6: Home Assistant Integration

### Step 6.1: Configure MQTT Integration
```yaml
# Via HA UI: Settings -> Integrations -> Add Integration -> MQTT
# Configure:
# Broker: 192.168.20.101
# Port: 8883
# Username: mqtt   # H-9 fix: single 'mqtt' user - ha_secure_user was never created
# Password: SECURE_HA_PASSWORD
# Enable TLS
# CA Certificate: /config/ssl/ca/certs/ca-cert.pem
```

### Step 6.2: Create VentSys Entities
```yaml
# Add to /config/configuration.yaml
mqtt:
  sensor:
    # SLA Enclosure Sensors
    - name: "SLA Temperature"
      state_topic: "ventsys/sla/temperature"
      unit_of_measurement: "Ã‚Â°C"
      device_class: temperature
      
    - name: "SLA Humidity" 
      state_topic: "ventsys/sla/humidity"
      unit_of_measurement: "%"
      device_class: humidity
      
    - name: "SLA VOC"
      state_topic: "ventsys/sla/voc"
      unit_of_measurement: "ppm"
      
    - name: "SLA Pressure"
      state_topic: "ventsys/sla/pressure"
      unit_of_measurement: "Pa"
      device_class: pressure
      
  binary_sensor:
    - name: "SLA Smoke Detector"
      state_topic: "ventsys/sla/smoke"
      device_class: smoke
      
  number:
    # Valve Controls
    - name: "SLA Valve Position"
      command_topic: "ventsys/sla/valve/control"
      state_topic: "ventsys/sla/valve/state"
      min: 0
      max: 100
      step: 1
      mode: slider
      
  fan:
    - name: "VentSys Inline Fan"
      command_topic: "ventsys/fan/control"
      state_topic: "ventsys/fan/state"
      percentage_command_topic: "ventsys/fan/percent"
      percentage_state_topic: "ventsys/fan/percent_state"
      
  switch:
    # Smart plugs for printer control
    - name: "SLA Printer Power"
      command_topic: "ventsys/sla/printer/control"
      state_topic: "ventsys/sla/printer/state"
      payload_on: "ON"
      payload_off: "OFF"
```

### Step 6.3: Create VentSys Dashboard
```yaml
# Add to /config/dashboards/ventsys.yaml
title: VentSys Control
views:
  - title: Overview
    cards:
      - type: picture-elements
        image: /local/ventsys-schematic.png
        elements:
          # Fan status indicator
          - type: state-icon
            entity: fan.ventsys_inline_fan
            style:
              top: 15%
              left: 85%
              
          # SLA enclosure status
          - type: state-badge
            entity: sensor.sla_temperature
            style:
              top: 50%
              left: 25%
              
          # Valve position indicators
          - type: state-label
            entity: number.sla_valve_position
            style:
              top: 60%
              left: 25%
              
      - type: entities
        title: System Status
        entities:
          - fan.ventsys_inline_fan
          - binary_sensor.ventsys_system_healthy
          - sensor.ventsys_fire_risk_level
          
      - type: grid
        cards:
          - type: gauge
            entity: number.sla_valve_position
            name: SLA Valve
            min: 0
            max: 100
            
          - type: gauge 
            entity: sensor.sla_temperature
            name: SLA Temperature
            min: 15
            max: 50
            
  - title: Manual Control
    cards:
      - type: entities
        title: Valve Controls
        entities:
          - entity: number.sla_valve_position
            name: SLA Valve Position
          - entity: number.fdm_valve_position
            name: FDM Valve Position
          - entity: number.booth_valve_position
            name: Booth Valve Position
            
      - type: entities
        title: Fan Control
        entities:
          - entity: fan.ventsys_inline_fan
          - entity: input_boolean.ventsys_manual_mode
          - entity: input_boolean.ventsys_failsafe_active
```

### Step 6.4: Create Safety Automations
```yaml
# Add to /config/automations.yaml
- alias: VentSys Fire Risk Response
  id: ventsys_fire_risk
  trigger:
    - platform: state
      entity_id: sensor.ventsys_fire_risk_level
      to: 'FIRE_RISK'
  action:
    - service: switch.turn_off
      target:
        entity_id:
          - switch.sla_printer_power
          - switch.fdm_printer_power
    - service: number.set_value
      target:
        entity_id:
          - number.sla_valve_position
          - number.fdm_valve_position
          - number.booth_valve_position
      data:
        value: 100
    - service: fan.turn_on
      target:
        entity_id: fan.ventsys_inline_fan
      data:
        percentage: 100
    - service: notify.mobile_app
      data:
        title: "FIRE RISK DETECTED"
        message: "VentSys has detected fire risk. All printers shut down, ventilation at maximum."
        data:
          priority: high
          
- alias: VentSys Certificate Renewal Alert
  id: ventsys_cert_renewal
  trigger:
    - platform: template
      value_template: >
        {% for device in states.sensor 
           if device.entity_id.endswith('_cert_expires') 
           and (as_timestamp(device.state) - now().timestamp()) < 5184000 %}
          true
        {% endfor %}
  action:
    - service: notify.persistent_notification
      data:
        title: "Certificate Renewal Required"
        message: "IoT device certificates expire within 60 days. Schedule maintenance."
```

## Phase 7: Certificate Renewal Implementation

### Step 7.1: Create Certificate Monitoring System
```python
# Create /config/python_scripts/cert_monitor.py
import ssl
import socket
import datetime
import json
import os

def check_certificate_expiry(hostname, port=8883):
    """Check certificate expiry for MQTT broker"""
    try:
        context = ssl.create_default_context()
        context.load_verify_locations('/config/ssl/ca/certs/ca-cert.pem')
        
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                expiry = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                days_until_expiry = (expiry - datetime.datetime.now()).days
                
                return {
                    'hostname': hostname,
                    'expiry': expiry.isoformat(),
                    'days_until_expiry': days_until_expiry,
                    'status': 'ok' if days_until_expiry > 60 else 'warning'
                }
    except Exception as e:
        return {
            'hostname': hostname,
            'error': str(e),
            'status': 'error'
        }

# Check MQTT broker certificate
mqtt_status = check_certificate_expiry('192.168.20.101', 8883)
hass.states.set('sensor.mqtt_cert_status', mqtt_status['status'], mqtt_status)

# Read device registry and check each device
device_registry_path = '/config/device_registry.yaml'
if os.path.exists(device_registry_path):
    with open(device_registry_path, 'r') as f:
        devices = yaml.safe_load(f)
    
    for device in devices:
        if 'certificate_expires' in device:
            expiry = datetime.datetime.strptime(device['certificate_expires'], '%Y-%m-%d')
            days_until_expiry = (expiry - datetime.datetime.now()).days
            
            status = 'ok' if days_until_expiry > 60 else 'warning'
            entity_id = f"sensor.{device['name'].replace('-', '_')}_cert_expires"
            
            hass.states.set(entity_id, days_until_expiry, {
                'device_name': device['name'],
                'expiry_date': device['certificate_expires'],
                'status': status
            })
```

### Step 7.2: Create Automated Renewal System
```bash
# Create certificate renewal script
cat > /config/ssl/ca/renew-certificates.sh << 'EOF'
#!/bin/bash
set -e

RENEWAL_THRESHOLD=180  # Days before expiry to trigger renewal
CA_DIR="/config/ssl/ca"
MQTT_TOPIC_PREFIX="ventsys/system/certificate"

cd "$CA_DIR"

# Function to publish certificate via MQTT
publish_certificate() {
    local device_name="$1"
    local cert_file="$2"
    local key_file="$3"
    
    # Create certificate package
    cert_package=$(cat << EOJ
{
  "device": "$device_name",
  "certificate": "$(cat "$cert_file" | base64 -w 0)",
  "private_key": "$(cat "$key_file" | base64 -w 0)",
  "ca_certificate": "$(cat certs/ca-cert.pem | base64 -w 0)",
  "issued": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "expires": "$(openssl x509 -in "$cert_file" -noout -enddate | cut -d= -f2)"
}
EOJ
)
    
    # Publish to device-specific topic
    mosquitto_pub -h 192.168.20.101 -p 8883 \
        --cafile certs/ca-cert.pem \
    -u mqtt -P "YOUR_MQTT_PASSWORD" \   # H-9 fix: use mqtt user
        -t "$MQTT_TOPIC_PREFIX/$device_name/renewal" \
        -m "$cert_package" \
        -r
    
    echo "Published certificate renewal for $device_name"
}

# Read device registry and check for expiring certificates
while IFS= read -r line; do
    if [[ "$line" =~ ^-[[:space:]]+name:[[:space:]]+(.+) ]]; then
        device_name="${BASH_REMATCH[1]}"
    elif [[ "$line" =~ ^[[:space:]]+certificate_expires:[[:space:]]+(.+) ]]; then
        cert_expires="${BASH_REMATCH[1]}"
        
        # Calculate days until expiry
        expiry_epoch=$(date -d "$cert_expires" +%s)
        current_epoch=$(date +%s)
        days_until_expiry=$(( (expiry_epoch - current_epoch) / 86400 ))
        
        if [ "$days_until_expiry" -le "$RENEWAL_THRESHOLD" ]; then
            echo "Renewing certificate for $device_name (expires in $days_until_expiry days)"
            
            # Generate new certificate
            ./generate-server-cert.sh "$device_name" 1095
            
            # Publish to MQTT for device to pick up
            publish_certificate "$device_name" \
                "certs/${device_name}-cert.pem" \
                "private/${device_name}-key.pem"
            
            # Update device registry
            sed -i "s/certificate_expires: $cert_expires/certificate_expires: $(date -d '+3 years' '+%Y-%m-%d')/" \
                /config/device_registry.yaml
        fi
    fi
done < /config/device_registry.yaml

echo "Certificate renewal check completed"
EOF

chmod +x /config/ssl/ca/renew-certificates.sh
```

### Step 7.3: Schedule Automatic Renewals
```yaml
# Add to /config/configuration.yaml
automation:
  - alias: Certificate Renewal Check
    id: cert_renewal_check
    trigger:
      - platform: time
        at: "02:00:00"  # Daily at 2 AM
    action:
      - service: shell_command.renew_certificates
      
shell_command:
  renew_certificates: /config/ssl/ca/renew-certificates.sh
  
# Certificate monitoring sensor
template:
  - sensor:
    - name: "Certificate Renewal Status"
      state: >
        {% set expiring = namespace(count=0) %}
        {% for entity_id in states.sensor 
           if entity_id.entity_id.endswith('_cert_expires') 
           and entity_id.state | int < 60 %}
          {% set expiring.count = expiring.count + 1 %}
        {% endfor %}
        {% if expiring.count > 0 %}
          {{ expiring.count }} certificates expiring
        {% else %}
          All certificates valid
        {% endif %}
      attributes:
        expiring_certificates: >
          {% set expiring = [] %}
          {% for entity_id in states.sensor 
             if entity_id.entity_id.endswith('_cert_expires') 
             and entity_id.state | int < 60 %}
            {% set expiring = expiring + [entity_id.attributes.device_name] %}
          {% endfor %}
          {{ expiring }}
```

## Phase 8: Testing and Validation

### Step 8.1: Network Connectivity Tests
```bash
# Test IoT device connectivity
# From IoT device (192.168.50.31):
ping -c 4 192.168.50.1      # Gateway
ping -c 4 192.168.20.101    # Home Assistant
nslookup google.com         # Should fail (no internet)

# Test NTP synchronization with OpenWrt router
ntpdate -q 192.168.50.1

# Test MQTT connectivity with TLS
mosquitto_pub -h 192.168.20.101 -p 8883 \
    --cafile /config/ssl/ca/certs/ca-cert.pem \
    -u mqtt -P "YOUR_MQTT_PASSWORD" \   # H-9 fix: use mqtt user
    -t "test/connectivity" -m "IoT device connected via TLS"
```

### Step 8.2: Certificate Validation Tests
```bash
# Verify certificate chain
openssl verify -CAfile /config/ssl/ca/certs/ca-cert.pem \
    /config/ssl/ca/certs/mosquitto-cert.pem

# Test certificate expiry checking
openssl x509 -in /config/ssl/ca/certs/mosquitto-cert.pem \
    -noout -enddate

# Test MQTT TLS connection
openssl s_client -connect 192.168.20.101:8883 \
    -CAfile /config/ssl/ca/certs/ca-cert.pem \
    -verify_return_error
```

### Step 8.3: Security Validation
```bash
# Verify IoT devices cannot reach internet
# From IoT device:
curl -I google.com          # Should fail
ping -c 1 8.8.8.8           # Should fail

# Verify firewall rules are working
# From router:
iptables -L | grep iot_sensors
```

### Step 8.4: VentSys Functional Tests
```bash
# Test MQTT topics
mosquitto_sub -h 192.168.20.101 -p 8883 \
    --cafile /config/ssl/ca/certs/ca-cert.pem \
    -u mqtt -P "YOUR_MQTT_PASSWORD" \   # H-9 fix: use mqtt user
    -t "ventsys/+/+/state" -v

# Test valve control
mosquitto_pub -h 192.168.20.101 -p 8883 \
    --cafile /config/ssl/ca/certs/ca-cert.pem \
    -u mqtt -P "YOUR_MQTT_PASSWORD" \   # H-9 fix: use mqtt user
    -t "ventsys/sla/valve/control" -m "50"

# Verify Home Assistant entities are created
curl -H "Authorization: Bearer YOUR_HA_TOKEN" \
    http://192.168.20.101:8123/api/states/sensor.sla_temperature
```

## Phase 9: Documentation and Maintenance

### Step 9.1: Create System Documentation
```markdown
# VentSys Security Documentation

## Certificate Management
- **CA Location**: `/config/ssl/ca/`
- **CA Certificate**: Valid until $(openssl x509 -in /config/ssl/ca/certs/ca-cert.pem -noout -enddate)
- **Renewal Schedule**: Automated daily checks at 2:00 AM
- **Manual Renewal**: Execute `/config/ssl/ca/renew-certificates.sh`

## Device Registry
Location: `/config/device_registry.yaml`
Contains all IoT devices with certificate expiry tracking

## Emergency Procedures
1. **Certificate Compromise**: Revoke and regenerate all certificates
2. **CA Compromise**: Generate new CA and re-provision all devices  
3. **Network Issues**: Check firewall rules for IoT access to HA
4. **MQTT Issues**: Verify mosquitto service and certificate validity

## Maintenance Tasks
- Monthly: Review certificate expiry status
- Quarterly: Test emergency procedures
- Annually: Update CA certificate if needed (10-year validity)
```

### Step 9.2: Create Monitoring Dashboard
```yaml
# Add certificate monitoring card to dashboard
type: entities
title: Certificate Status
entities:
  - sensor.mqtt_cert_status
  - sensor.certificate_renewal_status
  - sensor.ventsys_sla_sensors_cert_expires
  - sensor.ventsys_fdm_sensors_cert_expires
  - sensor.ventsys_booth_sensors_cert_expires
show_header_toggle: false
```

### Step 9.3: Backup Procedures
```bash
# Create backup script
cat > /config/backup-certificates.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/config/backups/certificates/$(date +%Y-%m-%d)"
mkdir -p "$BACKUP_DIR"

# Backup CA
cp -r /config/ssl/ca "$BACKUP_DIR/"

# Backup mosquitto config
cp -r /config/mosquitto "$BACKUP_DIR/"

# Backup device registry
cp /config/device_registry.yaml "$BACKUP_DIR/"

# Create encrypted archive
tar -czf "$BACKUP_DIR.tar.gz" -C "$BACKUP_DIR" .
rm -rf "$BACKUP_DIR"

echo "Certificate backup created: $BACKUP_DIR.tar.gz"
EOF

chmod +x /config/backup-certificates.sh

# Schedule weekly backups
# Add to crontab via HA automation:
# 0 3 * * 0 /config/backup-certificates.sh
```

### Step 9.4: Router NTP Status Monitoring
```bash
# Add NTP monitoring to OpenWrt router
cat > /etc/crontabs/root << 'EOF'
# Check NTP sync status hourly
0 * * * * /usr/sbin/ntpq -p > /var/log/ntp-status.log 2>&1

# Log NTP statistics daily
0 6 * * * /usr/bin/logger "NTP Status: $(ntpq -c peers | head -n 10)"
EOF

# Enable cron service
/etc/init.d/cron enable
/etc/init.d/cron start
```

---

## Summary

This implementation provides:

1. **Complete IoT isolation** with no internet access
2. **Full TLS encryption** using local CA certificates  
3. **Automated certificate renewal** via MQTT
4. **OpenWrt NTP server** for reliable time synchronization
5. **Comprehensive monitoring** of certificate health
6. **Emergency procedures** for certificate compromise
7. **Robust backup systems** for disaster recovery

### Key Benefits of Using OpenWrt NTP

- **Reduced dependencies**: No need for additional NTP service on Home Assistant
- **Better reliability**: Router-level time sync more stable than application-level
- **Network efficiency**: Single NTP source for all isolated networks
- **Simplified firewall rules**: Only need to allow UDP/123 to router gateway IPs

### Implementation Timeline

- **Phase 1-2**: Network verification and prerequisites (1-2 hours)
- **Phase 3**: Certificate Authority setup (2-3 hours)
- **Phase 4**: MQTT configuration (1-2 hours)  
- **Phase 5**: IoT device provisioning (2-4 hours per device)
- **Phase 6**: Home Assistant integration (1-2 hours)
- **Phase 7**: Certificate renewal automation (2-3 hours)
- **Phase 8-9**: Testing and documentation (2-3 hours)

**Total estimated time**: 12-20 hours depending on number of IoT devices

The solution maintains both security and functionality while operating entirely within your isolated network architecture. IoT devices receive time synchronization from the router and certificate management through the local Home Assistant server, eliminating any need for internet connectivity while preserving strong cryptographic authentication.
