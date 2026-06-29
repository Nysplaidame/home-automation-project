# VentSys Week 1: Network Validation - Simple Execution Guide

<!--
=============================================================================
SUMMARY: Step-by-step guide for validating OpenWrt network infrastructure
PURPOSE: Ensures existing network configuration (Phases 1-8) supports
         VentSys real-time IoT control before certificate infrastructure

WHERE TO USE: Reference guide for VentSys Week 1 implementation on
              OpenWrt router with completed 8-phase network foundation
DURATION: 2-3 hours total implementation time
PREREQUISITES: SSH root access, completed network Phases 1-8
=============================================================================
-->

## Brief Explanation
Week 1 validates that your existing OpenWrt network configuration (8-phase foundation: Prerequisites through VentSys Readiness) meets VentSys requirements for real-time IoT control. Two focused scripts test critical network paths, discover devices, and update DHCP reservations as needed.

## Prerequisites
- OpenWrt router with 8-phase network foundation deployed (Phases 1-8)
- SSH root access to router
- VLANs 20 (automation) and 50 (iot_sensors) operational
- HomeIoT WiFi SSID broadcasting

## Implementation (2-3 Hours Total)

### Step 1: Deploy Scripts (15 minutes)

```bash
# Create directory and deploy validation script
mkdir -p /var/log
# [Copy ventsys_week1_validation.sh to /usr/local/bin/]
chmod +x /usr/local/bin/ventsys_week1_validation.sh

# Deploy MAC collection script
# [Copy ventsys_week1_mac_collection.sh to /usr/local/bin/]  
chmod +x /usr/local/bin/ventsys_week1_mac_collection.sh
```

### Step 2: Run Network Validation (30 minutes)

```bash
# Execute comprehensive validation
/usr/local/bin/ventsys_week1_validation.sh

# Expected output: Pass/Fail report with specific issues
# Log location: /var/log/ventsys_validation.log
# Results: /tmp/ventsys_week1_results.txt
```

**Critical Success Criteria:**
- VLAN 20 and 50 operational
- HA to IoT connectivity < 50ms latency
- IoT internet access blocked (security critical)
- HomeIoT SSID broadcasting

**If validation fails:** Fix issues before proceeding. Common fixes:
```bash
# Restart network if VLANs missing
/etc/init.d/network restart

# Check firewall rules if connectivity fails
uci show firewall | grep -E "(automation|iot_sensors)"

# Restart wireless if WiFi issues
/etc/init.d/network restart
wifi
```

### Step 3: Device Discovery and Registration (60-90 minutes)

```bash
# Scan for existing VentSys devices
/usr/local/bin/ventsys_week1_mac_collection.sh --scan

# Expected devices:
# - Home Assistant VM (192.168.20.101)
# - Fan Controller (192.168.50.21) - if deployed
# - SLA Valve (192.168.50.56) - if deployed
```

**Update DHCP reservations for found devices:**
```bash
# Example: If Home Assistant found
/usr/local/bin/ventsys_week1_mac_collection.sh --update home-assistant AA:BB:CC:DD:EE:FF

# Example: If fan controller found
/usr/local/bin/ventsys_week1_mac_collection.sh --update ventsys-main-fan 11:22:33:44:55:66

# Verify reservations
/usr/local/bin/ventsys_week1_mac_collection.sh --list
```

### Step 4: Final Validation (15 minutes)

```bash
# Test device connectivity
/usr/local/bin/ventsys_week1_mac_collection.sh --test home-assistant

# Re-run network validation to confirm
/usr/local/bin/ventsys_week1_validation.sh

# Should show: "NETWORK READY FOR VENTSYS IMPLEMENTATION"
```

## Success Criteria Validation

### ✅ Must Pass (Blocks Week 2):
- [ ] VLAN 20 operational (192.168.20.1)
- [ ] VLAN 50 operational (192.168.50.1)
- [ ] HA to IoT latency < 50ms
- [ ] IoT internet access blocked
- [ ] HomeIoT SSID broadcasting
- [ ] Home Assistant reachable at 192.168.20.101

### ⚠️ Warnings (Can Proceed):
- High latency (>50ms but <100ms)
- Some planned devices not yet deployed
- Minor firewall rule naming differences

### ❌ Failures (Must Fix):
- IoT internet isolation broken
- Critical VLANs not operational
- HA to IoT connectivity failed
- HomeIoT WiFi not broadcasting

## Validation Checklist

**Scope Check**: ✅ Validates existing network, doesn't build new infrastructure  
**Environment Check**: ✅ Uses UCI commands, standard OpenWrt tools  
**Network Integration**: ✅ References VLANs 20/50, correct IP ranges  
**Resource Check**: ✅ Minimal CPU/memory usage, basic logging  
**Big Picture Check**: ✅ Validates VentSys foundation requirements  
**Dependency Check**: ✅ Uses standard OpenWrt commands only  

## Integration Notes

This validation fits within the VentSys architecture by:
- Confirming the network foundation supports real-time IoT control
- Establishing device registry for certificate deployment in Week 2
- Validating security isolation critical for IoT device safety
- Ensuring performance meets requirements for valve/fan control

## Files Generated

- `/var/log/ventsys_validation.log` - Validation test log
- `/var/log/ventsys_mac_updates.log` - DHCP update log  
- `/tmp/ventsys_week1_results.txt` - Final validation report

## Common Issues and Solutions

**"VLAN interfaces not found"**
```bash
uci show network | grep interface
/etc/init.d/network restart
```

**"IoT internet not blocked"**  
```bash
uci show firewall | grep -i iot
# Check for reject rules blocking VLAN 50 to WAN
```

**"HomeIoT SSID not broadcasting"**
```bash
uci show wireless | grep HomeIoT
/etc/init.d/network restart
iwconfig
```

**"High latency between VLANs"**
```bash
# Check bridge/switch performance
cat /sys/class/net/br-lan/bridge/stp_state
# Consider disabling STP if causing delays
```

## Week 1 Completion Status

**Ready for Week 2 when:**
- Network validation shows "READY FOR VENTSYS IMPLEMENTATION"
- Critical devices discovered and registered in DHCP
- Performance meets real-time control requirements
- Security isolation validated

**Outputs for Week 2:**
- Validated network foundation
- Device registry with known IP assignments
- Performance baseline for real-time control
- Confirmed security isolation for IoT devices

This focused approach completes Week 1 network validation in 2-3 hours versus the original 5-day plan, providing exactly what's needed to proceed to Week 2 certificate infrastructure deployment.
