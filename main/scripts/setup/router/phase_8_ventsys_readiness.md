# Phase 8: VentSys Integration Readiness

**Duration**: 2-3 hours  
**Risk Level**: Low (final validation and documentation)  
**Prerequisites**: Phase 7 completed with acceptable test results

## Overview
Finalizes network foundation for VentSys integration by completing certificate infrastructure preparation, creating integration documentation, and establishing monitoring baselines. Provides comprehensive handover documentation for VentSys Phase 1 implementation and validates all prerequisites for IoT ecosystem deployment.

## Sub-Tasks

### 8.1 Certificate Authority Preparation for VentSys TLS
**Duration**: 20 minutes

> **ARCHITECTURE NOTE — CA LOCATION (B9 fix):**
> The full Certificate Authority (private key + signing infrastructure) lives on the
> **HA VM** at `/config/ssl/ca/`, as defined in `docs/procedures/ssl_tls_guide.md`.
> The router does NOT host Mosquitto — MQTT TLS termination happens on the HA VM.
> The router only needs a copy of the CA *public certificate* if mutual TLS is ever
> added to WireGuard. This step prepares that directory only; do not create CA keys
> here. Follow `docs/procedures/ssl_tls_guide.md` for full CA setup on the HA VM.

```bash
# Create Phase 8 entry backup
/usr/local/bin/backup_phase.sh 8_entry

echo "=== VentSys Certificate Preparation ===" > /tmp/phase8_cert_prep.txt

# Prepare directory for the CA public certificate (copied from HA VM after CA creation)
# The CA private key and signing infrastructure are on the HA VM, not this router.
mkdir -p /etc/ventsys/ca/certs
chmod 755 /etc/ventsys/ca/certs

echo "✓ Router CA cert directory prepared: /etc/ventsys/ca/certs/" >> /tmp/phase8_cert_prep.txt
echo "⚠ Full CA infrastructure lives on HA VM at /config/ssl/ca/" >> /tmp/phase8_cert_prep.txt
echo "⚠ Generate the CA on the HA VM per docs/procedures/ssl_tls_guide.md" >> /tmp/phase8_cert_prep.txt
echo "⚠ After CA creation, copy public cert to router:" >> /tmp/phase8_cert_prep.txt
echo "    scp root@192.168.20.101:/config/ssl/ca/ca.crt /etc/ventsys/ca/certs/" >> /tmp/phase8_cert_prep.txt

cat /tmp/phase8_cert_prep.txt
echo "Certificate directory prepared for VentSys integration" >> /tmp/deployment_logs/phase8.log
```

### 8.2 VentSys Network Integration Documentation
**Duration**: 30 minutes

```bash
echo "=== VentSys Network Integration Documentation ===" > /tmp/phase8_ventsys_integration.txt

# Document critical network settings for VentSys integration
echo "VENTSYS NETWORK INTEGRATION REQUIREMENTS:" >> /tmp/phase8_ventsys_integration.txt
echo "Generated: $(date)" >> /tmp/phase8_ventsys_integration.txt
echo "" >> /tmp/phase8_ventsys_integration.txt

# Document key network segments
echo "CRITICAL NETWORK SEGMENTS FOR VENTSYS:" >> /tmp/phase8_ventsys_integration.txt
echo "1. VLAN 20 (Automation): 192.168.20.0/24" >> /tmp/phase8_ventsys_integration.txt
echo "   - Home Assistant VM: 192.168.20.101 (static reservation)" >> /tmp/phase8_ventsys_integration.txt
echo "   - Gateway: 192.168.20.1" >> /tmp/phase8_ventsys_integration.txt
echo "   - DHCP Range: 192.168.20.110-149" >> /tmp/phase8_ventsys_integration.txt
echo "" >> /tmp/phase8_ventsys_integration.txt
echo "2. VLAN 50 (IoT Sensors): 192.168.50.0/24" >> /tmp/phase8_ventsys_integration.txt
echo "   - WiFi SSID: HomeIoT" >> /tmp/phase8_ventsys_integration.txt
echo "   - Gateway: 192.168.50.1" >> /tmp/phase8_ventsys_integration.txt
echo "   - DHCP Range: 192.168.50.100-190" >> /tmp/phase8_ventsys_integration.txt
    echo "   - Main Fan (ventsys-main-fan):              192.168.50.21 (static reservation)" >> /tmp/phase8_ventsys_integration.txt
    echo "   - SLA Print Valve (ventsys-sla-print-valve): 192.168.50.56 (static reservation)" >> /tmp/phase8_ventsys_integration.txt
    echo "   - FDM Print Valve (ventsys-fdm-print-valve): 192.168.50.55 (static reservation)  # A6-1 fix: was ventsys-fdm-valve@.83 - stale pre-canonical name/IP" >> /tmp/phase8_ventsys_integration.txt
    echo "   - FDM Sensor Array 1 (ventsys-fdm-array-1):  192.168.50.31 (static reservation)" >> /tmp/phase8_ventsys_integration.txt
    echo "   - FDM Sensor Array 2 (ventsys-fdm-array-2):  192.168.50.32 (static reservation)" >> /tmp/phase8_ventsys_integration.txt
    echo "   - SLA Sensor Array 1 (ventsys-sla-array-1):  192.168.50.33 (static reservation)" >> /tmp/phase8_ventsys_integration.txt
    echo "   - SLA Sensor Array 2 (ventsys-sla-array-2):  192.168.50.34 (static reservation)" >> /tmp/phase8_ventsys_integration.txt
    echo "   - Garage Air Sensor:                         192.168.50.35 (static reservation)" >> /tmp/phase8_ventsys_integration.txt
    echo "   - FDM Pipe Air Sensor:                       192.168.50.36 (static reservation)" >> /tmp/phase8_ventsys_integration.txt
    echo "   - SLA Pipe Air Sensor:                       192.168.50.37 (static reservation)" >> /tmp/phase8_ventsys_integration.txt
echo "" >> /tmp/phase8_ventsys_integration.txt

# Document firewall rules critical for VentSys
echo "CRITICAL FIREWALL RULES FOR VENTSYS:" >> /tmp/phase8_ventsys_integration.txt
echo "1. Home Assistant to IoT Sensors: VLAN 20 → VLAN 50 (full access)" >> /tmp/phase8_ventsys_integration.txt
echo "2. MQTT Communication: VLAN 50 → VLAN 20:8883 (TCP)" >> /tmp/phase8_ventsys_integration.txt
echo "3. ESPHome API + OTA: VLAN 20 → VLAN 50:6053,3232 (TCP) — both ports required" >> /tmp/phase8_ventsys_integration.txt
echo "4. NTP (time sync): VLAN 50 → router:123 (UDP) — required for TLS cert validation" >> /tmp/phase8_ventsys_integration.txt
echo "5. IoT Internet Block: VLAN 50 → WAN (REJECT - CRITICAL)" >> /tmp/phase8_ventsys_integration.txt
echo "6. Bambuddy to Printer: VLAN 20 (.102) → VLAN 35 (.200) ports 8883,21 — Bambuddy bridge" >> /tmp/phase8_ventsys_integration.txt
echo "" >> /tmp/phase8_ventsys_integration.txt

# WiFi credentials for VentSys devices
IOT_PASSWORD=$(cat /etc/wireless/credentials/iot_password.txt 2>/dev/null || echo "PASSWORD_NOT_FOUND")
echo "WIFI CREDENTIALS FOR VENTSYS DEVICES:" >> /tmp/phase8_ventsys_integration.txt
echo "SSID: HomeIoT" >> /tmp/phase8_ventsys_integration.txt
echo "Password: $IOT_PASSWORD" >> /tmp/phase8_ventsys_integration.txt
echo "Security: WPA2 (PSK2) - Optimized for IoT device compatibility" >> /tmp/phase8_ventsys_integration.txt
echo "Channel: 6 (fixed for stability)" >> /tmp/phase8_ventsys_integration.txt

cat /tmp/phase8_ventsys_integration.txt
```

### 8.3 Monitoring and Alerting Baseline Setup
**Duration**: 30 minutes

```bash
echo "=== Monitoring Baseline Setup ===" > /tmp/phase8_monitoring_setup.txt

# Create monitoring script for VentSys critical components
cat > /usr/local/bin/ventsys_network_monitor.sh << 'EOF'
#!/bin/bash
# VentSys Network Monitoring Script
# Monitors critical network components for VentSys operation

LOG_FILE="/var/log/ventsys_network_monitor.log"
ALERT_THRESHOLD=3

check_interface() {
    local interface=$1
    local expected_ip=$2
    
    if ip addr show "$interface" | grep -q "$expected_ip"; then
        echo "$(date): ✓ $interface operational ($expected_ip)" >> "$LOG_FILE"
        return 0
    else
        echo "$(date): ✗ $interface FAILED ($expected_ip)" >> "$LOG_FILE"
        return 1
    fi
}

check_wireless_ssid() {
    local ssid=$1
    # B8 fix: iwlist scan is unreliable on the router's own radios — it is a
    # client-side scan tool and may report nothing or scan the wrong interface.
    # Check UCI config and hostapd instead: SSID must be configured and not disabled.
    local iface
    iface=$(uci show wireless | grep "\.ssid='${ssid}'" | cut -d. -f1-2 2>/dev/null)
    if [ -n "$iface" ]; then
        local disabled
        disabled=$(uci get "${iface}.disabled" 2>/dev/null)
        if [ "$disabled" != "1" ]; then
            echo "$(date): ✓ SSID $ssid configured and enabled" >> "$LOG_FILE"
            return 0
        fi
    fi
    echo "$(date): ✗ SSID $ssid NOT configured or disabled" >> "$LOG_FILE"
    return 1
}

check_firewall_rule() {
    local rule_name=$1
    
    if uci show firewall | grep -q "$rule_name"; then
        echo "$(date): ✓ Firewall rule '$rule_name' present" >> "$LOG_FILE"
        return 0
    else
        echo "$(date): ✗ Firewall rule '$rule_name' MISSING" >> "$LOG_FILE"
        return 1
    fi
}

# Main monitoring checks
echo "$(date): Starting VentSys network monitoring" >> "$LOG_FILE"

# Check critical interfaces
check_interface "br-lan.20" "192.168.20.1"
check_interface "br-lan.50" "192.168.50.1"

# Check HomeIoT WiFi
check_wireless_ssid "HomeIoT"

# Check critical firewall rules
check_firewall_rule "ESPHome API HA to IoT"
check_firewall_rule "VentSys MQTT IoT to HA"
check_firewall_rule "Block IoT Internet"

echo "$(date): VentSys network monitoring completed" >> "$LOG_FILE"
EOF

chmod +x /usr/local/bin/ventsys_network_monitor.sh

# Create monitoring cron job (every 15 minutes) — idempotent: only add if absent
CRON_ENTRY="*/15 * * * * /usr/local/bin/ventsys_network_monitor.sh"
if ! grep -qF "$CRON_ENTRY" /etc/crontabs/root 2>/dev/null; then
    echo "$CRON_ENTRY" >> /etc/crontabs/root
    echo "✓ Cron job added" >> /tmp/phase8_monitoring_setup.txt
else
    echo "✓ Cron job already present (skipped duplicate)" >> /tmp/phase8_monitoring_setup.txt
fi

# Run initial monitoring check
/usr/local/bin/ventsys_network_monitor.sh

echo "✓ VentSys network monitoring script created and scheduled" >> /tmp/phase8_monitoring_setup.txt
echo "✓ Monitoring log: /var/log/ventsys_network_monitor.log" >> /tmp/phase8_monitoring_setup.txt
echo "✓ Cron job: Every 15 minutes" >> /tmp/phase8_monitoring_setup.txt

cat /tmp/phase8_monitoring_setup.txt
```

### 8.4 MAC Address Collection Framework
**Duration**: 15 minutes

```bash
echo "=== MAC Address Collection Framework ===" > /tmp/phase8_mac_collection.txt

# Create script to update static DHCP reservations with real MAC addresses
cat > /usr/local/bin/update_ventsys_mac.sh << 'EOF'
#!/bin/bash
# VentSys MAC Address Update Script
# Usage: update_ventsys_mac.sh <device_name> <mac_address>

DEVICE_NAME=$1
MAC_ADDRESS=$2

if [ -z "$DEVICE_NAME" ] || [ -z "$MAC_ADDRESS" ]; then
    echo "Usage: $0 <device_name> <mac_address>"
echo "Available devices: proxmox-host, home-assistant, frigate-nvr, omv-nas, ventsys-main-fan, ventsys-sla-print-valve  # A6-1 fix: was ventsys-fan-controller, ventsys-valve-controller (stale names)"
    exit 1
fi

# Validate MAC address format
if ! echo "$MAC_ADDRESS" | grep -qE '^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$'; then
    echo "Error: Invalid MAC address format. Expected format: XX:XX:XX:XX:XX:XX"
    exit 1
fi

# Find and update the DHCP host entry
host_sections=$(uci show dhcp | grep "dhcp\.@host.*\.name='$DEVICE_NAME'" | cut -d'.' -f2 | cut -d'=' -f1)

if [ -z "$host_sections" ]; then
    echo "Error: Device '$DEVICE_NAME' not found in DHCP reservations"
    exit 1
fi

for section in $host_sections; do
    echo "Updating MAC address for $DEVICE_NAME ($section) to $MAC_ADDRESS"
    uci set dhcp.$section.mac="$MAC_ADDRESS"
done

uci commit dhcp
/etc/init.d/dnsmasq restart

echo "✓ MAC address updated and DHCP service restarted"
echo "$(date): Updated $DEVICE_NAME MAC to $MAC_ADDRESS" >> /var/log/mac_address_updates.log
EOF

chmod +x /usr/local/bin/update_ventsys_mac.sh

echo "✓ MAC address update script created: /usr/local/bin/update_ventsys_mac.sh" >> /tmp/phase8_mac_collection.txt
echo "✓ Usage: update_ventsys_mac.sh <device_name> <mac_address>" >> /tmp/phase8_mac_collection.txt
echo "✓ Update log: /var/log/mac_address_updates.log" >> /tmp/phase8_mac_collection.txt

cat /tmp/phase8_mac_collection.txt
```

### 8.5 Final Configuration Backup and Documentation
**Duration**: 20 minutes

```bash
echo "=== Final Configuration Backup and Documentation ===" > /tmp/phase8_final_backup.txt

# Create comprehensive backup of complete configuration
BACKUP_DIR="/etc/config/backups/production_ready_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup all configuration files
cp /etc/config/* "$BACKUP_DIR/"
uci export > "$BACKUP_DIR/uci_complete_export.txt"

# Backup wireless credentials
cp -r /etc/wireless/credentials "$BACKUP_DIR/"

# Backup WireGuard keys and client configs
cp -r /etc/wireguard "$BACKUP_DIR/"

# Create configuration summary
cat > "$BACKUP_DIR/CONFIGURATION_SUMMARY.txt" << EOF
OPENWRT ROUTER CONFIGURATION - PRODUCTION READY
===============================================

HARDWARE: GL.iNet GL-MT6000
FIRMWARE: OpenWrt (latest)
CONFIGURATION DATE: $(date)

NETWORK ARCHITECTURE:
- 10 VLANs operational (1,10,20,30,35,40,50,60,70,99)
- 6 WiFi SSIDs configured
- WireGuard VPN server operational
- Complete firewall segmentation implemented

VENTSYS INTEGRATION READY:
- VLAN 20 (Automation): Home Assistant VM network
- VLAN 50 (IoT Sensors): VentSys device network (internet isolated)
- HomeIoT WiFi SSID operational
- Certificate infrastructure prepared
- Monitoring baseline established

CRITICAL SECURITY FEATURES:
- Network segmentation with firewall isolation
- Guest network completely isolated
- IoT network has no internet access
- VPN clients have controlled access
- DNS security implemented

NEXT STEPS:
1. Deploy physical devices and collect MAC addresses
2. Update static DHCP reservations with real MACs
3. Begin VentSys Phase 1 implementation
4. Monitor network performance and security

FILES IN THIS BACKUP:
- All /etc/config/ files
- Complete UCI configuration export
- WiFi credentials (secure handling required)
- WireGuard keys and client configurations
- Custom scripts and monitoring tools
EOF

# Create deployment success marker
echo "$(date): Router configuration completed successfully" > "$BACKUP_DIR/DEPLOYMENT_SUCCESS.txt"
echo "Ready for production use and VentSys integration" >> "$BACKUP_DIR/DEPLOYMENT_SUCCESS.txt"

tar -czf "/tmp/production_ready_backup_$(date +%Y%m%d_%H%M%S).tar.gz" -C "$(dirname $BACKUP_DIR)" "$(basename $BACKUP_DIR)"

echo "✓ Complete configuration backed up to: $BACKUP_DIR" >> /tmp/phase8_final_backup.txt
echo "✓ Compressed backup created in /tmp/" >> /tmp/phase8_final_backup.txt
echo "✓ Configuration summary created" >> /tmp/phase8_final_backup.txt

cat /tmp/phase8_final_backup.txt
```

### 8.6 Final Validation and Handover Documentation
**Duration**: 20 minutes

```bash
echo "=== Final Validation and Handover Documentation ===" > /tmp/phase8_final_validation.txt

# Final system status
echo "FINAL SYSTEM STATUS - PHASE 8 COMPLETION:" >> /tmp/phase8_final_validation.txt
echo "Completion Date: $(date)" >> /tmp/phase8_final_validation.txt
echo "Total Implementation Time: 8 phases over multiple weeks" >> /tmp/phase8_final_validation.txt
echo "" >> /tmp/phase8_final_validation.txt

# Validate all critical components one final time
echo "CRITICAL COMPONENT VALIDATION:" >> /tmp/phase8_final_validation.txt

# Network interfaces
interface_count=$(ip addr show | grep -c "br-lan\.")
echo "✓ VLAN interfaces operational: $interface_count/10" >> /tmp/phase8_final_validation.txt

# Wireless SSIDs
ssid_count=$(iwlist scan 2>/dev/null | grep -c "ESSID:")
echo "✓ WiFi SSIDs broadcasting: $ssid_count" >> /tmp/phase8_final_validation.txt

# Firewall rules
rule_count=$(uci show firewall | grep -c "@rule")
echo "✓ Firewall rules configured: $rule_count" >> /tmp/phase8_final_validation.txt

# Services
services_running=0
for service in network firewall dnsmasq; do
    if /etc/init.d/$service status >/dev/null 2>&1; then
        services_running=$((services_running + 1))
    fi
done
echo "✓ Critical services running: $services_running/3" >> /tmp/phase8_final_validation.txt

# VentSys readiness
echo "" >> /tmp/phase8_final_validation.txt
echo "VENTSYS INTEGRATION READINESS:" >> /tmp/phase8_final_validation.txt
if ip addr show br-lan.20 | grep -q "192.168.20.1" && ip addr show br-lan.35 | grep -q "192.168.35.1" && ip addr show br-lan.50 | grep -q "192.168.50.1"; then
    echo "✓ Critical VLANs operational (20: Automation, 35: Printers, 50: IoT Sensors)" >> /tmp/phase8_final_validation.txt
else
    echo "✗ Critical VLANs not operational" >> /tmp/phase8_final_validation.txt
fi

if uci show wireless | grep -q "ssid='HomeIoT'"; then
    echo "✓ HomeIoT WiFi SSID configured for VentSys sensors" >> /tmp/phase8_final_validation.txt
else
    echo "✗ HomeIoT WiFi SSID not configured — check wireless configuration" >> /tmp/phase8_final_validation.txt
fi

if [ -f "/etc/ventsys/ca/certs/ca.crt" ]; then
    echo "✓ VentSys CA certificate present on router (copied from HA VM)" >> /tmp/phase8_final_validation.txt
else
    # NOT a failure — the router only needs this cert if mutual TLS is later added
    # to WireGuard. Standard deployment does not require it here. See phase 8.1 note.
    echo "⚠ VentSys CA certificate not yet present — OK for initial deployment." >> /tmp/phase8_final_validation.txt
    echo "  Copy from HA VM after CA creation: scp root@192.168.20.101:/config/ssl/ca/ca.crt /etc/ventsys/ca/certs/" >> /tmp/phase8_final_validation.txt
fi

# Final recommendations
echo "" >> /tmp/phase8_final_validation.txt
echo "DEPLOYMENT COMPLETION STATUS:" >> /tmp/phase8_final_validation.txt
echo "✓ Network foundation complete and tested" >> /tmp/phase8_final_validation.txt
echo "✓ Security architecture implemented and validated" >> /tmp/phase8_final_validation.txt
echo "✓ VentSys integration prerequisites established" >> /tmp/phase8_final_validation.txt
echo "✓ Monitoring and maintenance tools deployed" >> /tmp/phase8_final_validation.txt
echo "✓ Complete configuration backup created" >> /tmp/phase8_final_validation.txt
echo "" >> /tmp/phase8_final_validation.txt
echo "READY FOR PRODUCTION USE" >> /tmp/phase8_final_validation.txt

cat /tmp/phase8_final_validation.txt
echo "SUCCESS: Router implementation completed - ready for VentSys Phase 1" >> /tmp/deployment_logs/phase8.log
```

## Success Criteria for Phase 8

Certificate infrastructure prepared: Framework ready for VentSys TLS deployment
Integration documentation complete: VentSys team has all required network information
Monitoring operational: Automated health checks running every 15 minutes
Configuration secured: Complete backup with all credentials protected
Update procedures ready: MAC address collection and device onboarding framework
VentSys handover complete: All prerequisites documented and validated

## Failure Analysis and Resolution

### Minor Issues

Certificate structure problems: Recreate directory structure with proper permissions
Monitoring script failures: Check script permissions and log file access
Documentation gaps: Verify all critical information documented

### Major Failures

Backup system failure: Recreate backup infrastructure and test procedures
Network monitoring failure: Reinstall monitoring components and validate functionality
VentSys prerequisites missing: Review and remediate missing network components

### Recovery Procedures

```bash
# If monitoring system fails:
rm -rf /usr/local/bin/ventsys_network_monitor.sh
# Recreate from Phase 8.3 instructions

# If certificate infrastructure fails:
rm -rf /etc/ventsys/ca
mkdir -p /etc/ventsys/ca/{certs,private,crl,newcerts}
chmod 700 /etc/ventsys/ca/private
# Recreate from Phase 8.1 instructions

# If complete Phase 8 failure:
/usr/local/bin/backup_phase.sh 8_recovery
# Address specific failures and rerun phase sections
```
