# Phase 4: Firewall Implementation

**Duration**: 3-4 hours  
**Risk Level**: High (security rule implementation)  
**Prerequisites**: Phase 3 completed, all DHCP scopes operational

## Overview
Implements comprehensive firewall security architecture using corrected UCI commands. Establishes network segmentation, internet access controls, and VentSys-specific communication rules. Most security-critical phase requiring extensive validation to ensure proper isolation without breaking legitimate communications.

## Interdependencies

### Input Requirements
- All network interfaces operational from Phase 2
- DHCP services running from Phase 3
- Corrected firewall configuration script (pure UCI format)
- Network connectivity for rule testing

### Output Deliverables
- Complete firewall rule set with proper network segmentation
- Internet access controls per network segment
- VentSys communication rules (MQTT 8883, ESPHome 6053)
- Guest and DMZ isolation implemented
- Security logging and monitoring rules active

### Dependencies for Later Phases
- **Phase 5**: Wireless clients must pass through firewall rules
- **Phase 6**: VPN zone rules must be operational
- **VentSys Phase 1**: IoT isolation and HA bridge rules required

## Sub-Tasks

### 4.1 Pre-Implementation Validation
**Duration**: 15 minutes

```bash
# Create Phase 4 entry backup
/usr/local/bin/backup_phase.sh 4_entry

# Validate prerequisites
echo "=== Phase 4 Prerequisites ===" > /tmp/phase4_validation.txt

# Verify all network interfaces exist
for interface in lan management automation cctv storage iot_sensors monitoring dmz guest; do
    if uci show network | grep -q "interface.*$interface"; then
        echo "✓ Interface $interface exists" >> /tmp/phase4_validation.txt
    else
        echo "✗ Interface $interface missing" >> /tmp/phase4_validation.txt
        exit 1
    fi
done

# Verify DHCP service is running
if /etc/init.d/dnsmasq status >/dev/null 2>&1; then
    echo "✓ DHCP service operational" >> /tmp/phase4_validation.txt
else
    echo "✗ DHCP service not running" >> /tmp/phase4_validation.txt
    exit 1
fi

cat /tmp/phase4_validation.txt
echo "Prerequisites validated for firewall implementation" >> /tmp/deployment_logs/phase4.log
```

### 4.2 Firewall Configuration Deployment
**Duration**: 30 minutes

```bash
# Deploy corrected firewall configuration
echo "Deploying corrected firewall configuration..."
echo "WARNING: Network access will be restricted during deployment"

# The authoritative firewall configuration lives in the vault at:
#   configs/openwrt/firewall-config.conf
# Transfer it to the router from your workstation BEFORE running this step.
# From a machine that can reach the router on the management network:
#   scp /path/to/vault/configs/openwrt/firewall-config.conf root@192.168.10.1:/tmp/firewall-config.sh
# Or paste the contents manually on the router via the LuCI terminal or SSH:
#   vi /tmp/firewall-config.sh  (paste contents, :wq to save)

# Execute the firewall configuration script
chmod +x /tmp/firewall-config.sh
/tmp/firewall-config.sh

# Verify firewall deployment succeeded
if [ $? -eq 0 ]; then
    echo "✓ Firewall deployment successful" >> /tmp/deployment_logs/phase4.log
else
    echo "✗ Firewall deployment failed - restoring backup" >> /tmp/deployment_logs/phase4.log
    /usr/local/bin/emergency_restore.sh
    exit 1
fi
```

**Testing Criteria**:
- Firewall script executes without errors
- All UCI commands succeed
- Firewall service restarts successfully
- Basic connectivity preserved

### 4.3 Internet Access Validation
**Duration**: 45 minutes

```bash
echo "=== Internet Access Validation ===" > /tmp/phase4_internet_test.txt

# Test internet access from different VLANs
# NOTE: Physical devices not available, testing via router interfaces

# LAN network (should have full internet)
if ping -I br-lan.1 -c 3 8.8.8.8 >/dev/null 2>&1; then
    echo "✓ LAN internet access working" >> /tmp/phase4_internet_test.txt
else
    echo "✗ LAN internet access blocked" >> /tmp/phase4_internet_test.txt
fi

# Management network (should have full internet)
if ping -I br-lan.10 -c 3 8.8.8.8 >/dev/null 2>&1; then
    echo "✓ Management internet access working" >> /tmp/phase4_internet_test.txt
else
    echo "✗ Management internet access blocked" >> /tmp/phase4_internet_test.txt
fi

# Automation network (limited access - only HA should have internet)
# This will be validated with actual devices later
echo "⚠ Automation network access requires device testing" >> /tmp/phase4_internet_test.txt

# Test DNS resolution on allowed networks
if nslookup google.com >/dev/null 2>&1; then
    echo "✓ DNS resolution working" >> /tmp/phase4_internet_test.txt
else
    echo "✗ DNS resolution failed" >> /tmp/phase4_internet_test.txt
fi

cat /tmp/phase4_internet_test.txt
```

### 4.4 Firewall Zone Validation
**Duration**: 30 minutes

```bash
echo "=== Firewall Zone Validation ===" > /tmp/phase4_zones_test.txt

# Verify all firewall zones exist
expected_zones="wan lan management automation cctv storage iot_sensors monitoring dmz guest vpn_clients"
for zone in $expected_zones; do
    if uci show firewall | grep -q "zone.*name='$zone'"; then
        echo "✓ Zone $zone configured" >> /tmp/phase4_zones_test.txt
    else
        echo "✗ Zone $zone missing" >> /tmp/phase4_zones_test.txt
    fi
done

# Check zone-to-network mappings
if uci show firewall | grep -A5 "zone.*name='automation'" | grep -q "network='automation'"; then
    echo "✓ Automation zone properly mapped to network" >> /tmp/phase4_zones_test.txt
else
    echo "✗ Automation zone mapping incorrect" >> /tmp/phase4_zones_test.txt
fi

if uci show firewall | grep -A5 "zone.*name='iot_sensors'" | grep -q "network='iot_sensors'"; then
    echo "✓ IoT sensors zone properly mapped to network" >> /tmp/phase4_zones_test.txt
else
    echo "✗ IoT sensors zone mapping incorrect" >> /tmp/phase4_zones_test.txt
fi

cat /tmp/phase4_zones_test.txt
```

### 4.5 VentSys Critical Rule Validation
**Duration**: 30 minutes

```bash
echo "=== VentSys Critical Rule Validation ===" > /tmp/phase4_ventsys_test.txt

# Verify Home Assistant to IoT Sensors access rule
if uci show firewall | grep -q "HA to IoT Sensors Access"; then
    echo "✓ HA to IoT Sensors rule configured" >> /tmp/phase4_ventsys_test.txt
else
    echo "✗ HA to IoT Sensors rule missing" >> /tmp/phase4_ventsys_test.txt
fi

# Verify MQTT rule (port 8883)
if uci show firewall | grep -q "VentSys MQTT IoT to HA"; then
    if uci show firewall | grep -A5 "VentSys MQTT" | grep -q "dest_port='8883'"; then
        echo "✓ VentSys MQTT rule (8883) configured" >> /tmp/phase4_ventsys_test.txt
    else
        echo "✗ VentSys MQTT port incorrect" >> /tmp/phase4_ventsys_test.txt
    fi
else
    echo "✗ VentSys MQTT rule missing" >> /tmp/phase4_ventsys_test.txt
fi

# Verify ESPHome API rule (ports 6053 + 3232)
# FIX: Both ports are required. 6053 = native API, 3232 = OTA firmware updates.
if uci show firewall | grep -q "ESPHome API HA to IoT"; then
    if uci show firewall | grep -A5 "ESPHome API" | grep -q "dest_port='6053,3232'"; then
        echo "✓ VentSys ESPHome API rules (6053,3232) configured" >> /tmp/phase4_ventsys_test.txt
    else
        echo "✗ VentSys ESPHome API ports incorrect (expected '6053,3232' — OTA port 3232 is required)" >> /tmp/phase4_ventsys_test.txt
    fi
else
    echo "✗ VentSys ESPHome API rule missing (expected: 'ESPHome API HA to IoT')" >> /tmp/phase4_ventsys_test.txt
fi

# Verify IoT sensors internet blocking
if uci show firewall | grep -q "Block IoT Internet"; then
    echo "✓ IoT sensors internet blocking configured" >> /tmp/phase4_ventsys_test.txt
else
    echo "✗ IoT sensors internet blocking missing" >> /tmp/phase4_ventsys_test.txt
fi

# Verify NTP rule for IoT devices (required for TLS certificate validation)
if uci show firewall | grep -q "IoT to Router NTP"; then
    echo "✓ IoT NTP rule configured (required for TLS cert validation)" >> /tmp/phase4_ventsys_test.txt
else
    echo "✗ IoT NTP rule missing (ESPHome TLS will fail without accurate time)" >> /tmp/phase4_ventsys_test.txt
fi

# Verify Bambuddy integration rules (must exist before 'Block CCTV to Automation')
for rule in "Bambuddy to P1S" "Bambuddy MQTT to HA" "Bambuddy to HA API"; do
    if uci show firewall | grep -q "$rule"; then
        echo "✓ Bambuddy rule configured: $rule" >> /tmp/phase4_ventsys_test.txt
    else
        echo "✗ Bambuddy rule missing: $rule" >> /tmp/phase4_ventsys_test.txt
    fi
done

# Verify 'Block CCTV to Automation' exists (must come AFTER Bambuddy rules)
if uci show firewall | grep -q "Block CCTV to Automation"; then
    echo "✓ Block CCTV to Automation (catch-all) configured" >> /tmp/phase4_ventsys_test.txt
else
    echo "✗ Block CCTV to Automation rule missing" >> /tmp/phase4_ventsys_test.txt
fi

cat /tmp/phase4_ventsys_test.txt
```

### 4.6 Network Isolation Testing
**Duration**: 30 minutes

```bash
echo "=== Network Isolation Testing ===" > /tmp/phase4_isolation_test.txt

# Test guest network isolation rules
guest_isolation_rules=0
for zone in lan management automation cctv storage iot_sensors monitoring dmz; do
    if uci show firewall | grep -q "Block Guest to $zone"; then
        guest_isolation_rules=$((guest_isolation_rules + 1))
    fi
done

if [ $guest_isolation_rules -eq 8 ]; then
    echo "✓ Guest isolation rules complete ($guest_isolation_rules/8)" >> /tmp/phase4_isolation_test.txt
else
    echo "✗ Guest isolation incomplete ($guest_isolation_rules/8)" >> /tmp/phase4_isolation_test.txt
fi

# Test DMZ isolation rules
dmz_isolation_rules=0
for zone in lan automation cctv storage iot_sensors; do
    if uci show firewall | grep -q "Block DMZ to $zone"; then
        dmz_isolation_rules=$((dmz_isolation_rules + 1))
    fi
done

if [ $dmz_isolation_rules -eq 5 ]; then
    echo "✓ DMZ isolation rules complete ($dmz_isolation_rules/5)" >> /tmp/phase4_isolation_test.txt
else
    echo "✗ DMZ isolation incomplete ($dmz_isolation_rules/5)" >> /tmp/phase4_isolation_test.txt
fi

cat /tmp/phase4_isolation_test.txt
```


## Success Criteria for Phase 4

- **All firewall zones operational**: 11 zones configured with proper network mappings
- **Internet access controls**: Graduated access (full/limited/none) per network segment
- **VentSys rules active**: MQTT (8883) and ESPHome (6053) communication rules functional
- **Network isolation complete**: Guest and DMZ properly isolated from internal networks
- **Management access functional**: Admin network can reach all segments
- **DNS security implemented**: Isolated networks blocked from external DNS
- **Service stability**: Firewall service running without errors

## Failure Analysis and Resolution

### Minor Issues
- **Individual rule failures**: Check UCI syntax and rule dependencies
- **Service restart problems**: Verify configuration syntax and restart services
- **Access problems**: Review rule order and conflicting rules

### Major Failures
- **Firewall service failure**: Emergency restore and reconfigure from backup
- **Complete network lockout**: Physical console access required for recovery
- **Rule conflicts**: Systematic rule review and conflict resolution

### Emergency Rollback
```bash
# If firewall completely blocks access:
# 1. Physical console access required
# 2. Stop firewall service
/etc/init.d/firewall stop
# 3. Restore from backup
/usr/local/bin/emergency_restore.sh
# 4. Restart services
/etc/init.d/network restart
/etc/init.d/firewall restart
```

**Proceed to Phase 5 when VentSys integration prerequisites validated.**