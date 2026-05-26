# VentSys Phase 1 Week 1: Network Infrastructure Validation
## Complete Implementation Guide

### Overview
This week validates the existing OpenWrt network configuration from Phases 1-7 to ensure it meets VentSys requirements. No network changes are made - this is pure validation and baseline establishment.

### Prerequisites Checklist
- [ ] OpenWrt router fully deployed with Phases 1-7 configuration
- [ ] All VLANs (1,10,20,30,40,50,60,70,99) operational
- [ ] WiFi SSIDs broadcasting (especially HomeIoT)
- [ ] Firewall rules applied from Phase 4
- [ ] SSH access to router as root
- [ ] Internet connectivity for package validation

---

## Day 1: Environment Setup and Initial Validation

### Step 1.1: Deploy Scripts and Initialize Environment
```bash
# Create VentSys directories
mkdir -p /etc/ventsys
mkdir -p /var/log/ventsys
mkdir -p /tmp/ventsys_reports

# Deploy main validation script
# [Copy ventsys_week1_network_validation.sh to /usr/local/bin/]
chmod +x /usr/local/bin/ventsys_week1_network_validation.sh

# Deploy device registry
# [Copy device_registry.yaml to /etc/ventsys/]

# Deploy MAC collection script  
# [Copy ventsys_week1_mac_collection.sh to /usr/local/bin/]
chmod +x /usr/local/bin/ventsys_week1_mac_collection.sh

# Deploy performance monitoring
# [Copy ventsys_week1_performance_monitoring.sh to /usr/local/bin/]
chmod +x /usr/local/bin/ventsys_week1_performance_monitoring.sh
```

### Step 1.2: Run Initial Network Validation
```bash
# Execute comprehensive network validation
/usr/local/bin/ventsys_week1_network_validation.sh

# Expected output: Comprehensive JSON report
# Location: /tmp/ventsys_reports/week1_validation_results.json
# Log: /var/log/ventsys/network_validation_[timestamp].log
```

**Critical Success Criteria:**
- All VLAN interfaces operational (9/9)
- HomeIoT SSID broadcasting
- IoT internet access blocked (security critical)
- VLAN 20 to VLAN 50 routing functional
- Overall status: PASSED or WARNING (not FAILED)

### Step 1.3: Initial Health Check
```bash
# Run quick health assessment
/usr/local/bin/ventsys_week1_performance_monitoring.sh --health

# Should show:
# - ✓ VLAN 20 operational (192.168.20.1)
# - ✓ VLAN 50 operational (192.168.50.1)  
# - ✓ HA to IoT gateway reachable
# - ✓ IoT internet access properly blocked
# - ✓ HomeIoT SSID broadcasting
```

**If Health Check Fails:** Stop and resolve network issues before proceeding. VentSys requires a fully functional network foundation.

---

## Day 2: Device Discovery and IP Assignment

### Step 2.1: Discover Existing Devices
```bash
# Scan networks for devices
/usr/local/bin/ventsys_week1_mac_collection.sh --discover

# This will:
# - Scan VLAN 20 (192.168.20.100-149) for Home Assistant
# - Scan VLAN 50 (192.168.50.30-39, 80-99) for VentSys devices
# - Show suggested MAC address assignments
```

### Step 2.2: Update Existing Device MAC Addresses
Based on discovery results, update known devices:

```bash
# Example: If Home Assistant found at 192.168.20.101
/usr/local/bin/ventsys_week1_mac_collection.sh --update home-assistant AA:BB:CC:DD:EE:FF

# Example: If existing fan controller found
/usr/local/bin/ventsys_week1_mac_collection.sh --update ventsys-fan-controller 11:22:33:44:55:66

# Example: If existing SLA valve found  
/usr/local/bin/ventsys_week1_mac_collection.sh --update ventsys-sla-valve 77:88:99:AA:BB:CC
```

### Step 2.3: Verify DHCP Reservations
```bash
# List all current reservations
/usr/local/bin/ventsys_week1_mac_collection.sh --list

# Test connectivity to updated devices
/usr/local/bin/ventsys_week1_mac_collection.sh --test home-assistant
/usr/local/bin/ventsys_week1_mac_collection.sh --test ventsys-fan-controller
```

---

## Day 3: Performance Baseline Establishment

### Step 3.1: Comprehensive Baseline Testing
```bash
# Run full baseline test suite
/usr/local/bin/ventsys_week1_performance_monitoring.sh --baseline

# This measures:
# - Inter-VLAN latency (HA to IoT gateway)
# - All critical path performance
# - WiFi signal strength and quality
# - System resource utilization
# - Firewall rule validation
```

### Step 3.2: Start Continuous Monitoring
```bash
# Start monitoring with 15-minute intervals
/usr/local/bin/ventsys_week1_performance_monitoring.sh --monitor 900 &

# Monitor will run in background and log:
# - Network latency every 15 minutes
# - Performance degradation alerts
# - System resource warnings
# - Firewall status checks
```

### Step 3.3: Network Stress Testing
```bash
# Run stress test to validate performance under load
/usr/local/bin/ventsys_week1_performance_monitoring.sh --stress

# This simulates:
# - Multiple device connections
# - High-frequency heartbeat traffic
# - Concurrent MQTT messaging load
```

---

## Day 4: Validation Analysis and Documentation

### Step 4.1: Generate Performance Report
```bash
# Generate comprehensive performance report
/usr/local/bin/ventsys_week1_performance_monitoring.sh --report

# Report location: /tmp/ventsys_performance_report_[timestamp].txt
# Includes:
# - 24-hour performance summary
# - VentSys readiness assessment
# - Critical event analysis
# - Performance trend data
```

### Step 4.2: Validate Critical Requirements

#### Network Connectivity Requirements:
```bash
# Test specific VentSys requirements
ping -I br-lan.20 -c 10 192.168.50.1    # HA to IoT gateway < 50ms
ping -I br-lan.20 -c 10 192.168.50.21   # HA to fan controller < 50ms
ping -I br-lan.20 -c 10 192.168.50.56   # HA to SLA valve < 50ms

# Verify results show:
# - Average latency < 50ms
# - Packet loss < 1%  
# - Jitter < 10ms
```

#### Security Isolation Requirements:
```bash
# Critical: IoT devices MUST NOT reach internet
ping -I br-lan.50 -c 3 8.8.8.8          # Should FAIL
ping -I br-lan.50 -c 3 1.1.1.1          # Should FAIL

# Automation network should reach internet
ping -I br-lan.20 -c 3 8.8.8.8          # Should SUCCEED
```

#### WiFi Infrastructure Requirements:
```bash
# HomeIoT SSID must broadcast on 2.4GHz channel 6
iwlist scan | grep -A5 "HomeIoT"

# Should show:
# - ESSID: "HomeIoT"
# - Channel: 6
# - Security: WPA2 PSK
```

### Step 4.3: Document Network Architecture
Create comprehensive documentation:

```bash
# Generate device config templates
/usr/local/bin/ventsys_week1_mac_collection.sh --config ventsys-fan-controller
/usr/local/bin/ventsys_week1_mac_collection.sh --config ventsys-sla-valve

# Document network topology
ip route show table main | grep 192.168 > /tmp/ventsys_routing_table.txt
uci show network | grep interface > /tmp/ventsys_interfaces.txt
uci show wireless | grep ssid > /tmp/ventsys_wifi_ssids.txt
```

---

## Day 5: Week 1 Completion and Handover

### Step 5.1: Final Validation Run
```bash
# Execute final comprehensive validation
/usr/local/bin/ventsys_week1_network_validation.sh

# Must achieve:
# - Overall status: PASSED
# - All critical failures: 0
# - VentSys readiness: CONFIRMED
```

### Step 5.2: Create Week 1 Summary Report

**Network Infrastructure Status:**
- [ ] All 9 VLANs operational with correct IP assignments
- [ ] HomeIoT WiFi SSID broadcasting on VLAN 50
- [ ] IoT internet isolation confirmed (security critical)
- [ ] Inter-VLAN routing functional (VLAN 20 ↔ VLAN 50)
- [ ] Network latency < 50ms for real-time control

**Device Registry Status:**
- [ ] Home Assistant IP assignment: 192.168.20.101
- [ ] Fan controller IP assignment: 192.168.50.21
- [ ] SLA valve IP assignment: 192.168.50.56
- [ ] MAC addresses collected and DHCP reservations updated
- [ ] Device connectivity validated

**Performance Baseline Status:**
- [ ] 24+ hours of monitoring data collected
- [ ] Performance thresholds established
- [ ] Stress testing completed successfully
- [ ] System resource utilization within limits
- [ ] Network ready for real-time IoT control

### Step 5.3: Prepare for Week 2
```bash
# Stop monitoring (if needed for Week 2 changes)
pkill -f "ventsys_week1_performance_monitoring"

# Create Week 1 completion backup
/usr/local/bin/backup_phase.sh week1_completion

# Prepare certificate infrastructure directories
mkdir -p /etc/ventsys/ca/{certs,private,crl,newcerts}
chmod 700 /etc/ventsys/ca/private
```

---

## Success Criteria Summary

### Week 1 Must Pass All:
1. **Network Connectivity**: All VLANs operational, inter-VLAN routing functional
2. **Security Isolation**: IoT devices cannot reach internet, automation can
3. **WiFi Infrastructure**: HomeIoT SSID broadcasting and mapped to VLAN 50  
4. **Performance Requirements**: Latency < 50ms, packet loss < 1%
5. **Device Discovery**: Existing devices identified and registered
6. **Baseline Establishment**: 24+ hours monitoring data collected

### Critical Failure Conditions (Block Week 2):
- IoT internet isolation broken (security risk)
- HomeIoT SSID not broadcasting (devices can't connect)
- VLAN 20 to VLAN 50 routing failed (HA can't control devices)
- Network latency > 50ms (real-time control impossible)
- DHCP not assigning IoT devices to VLAN 50

### Warning Conditions (Proceed with Monitoring):
- High system resource usage (monitor during Week 2)
- WiFi signal strength issues (optimize during implementation)
- DNS resolution problems on automation network

---

## Troubleshooting Guide

### Issue: Network Validation Fails
```bash
# Check VLAN interface status
ip addr show | grep "br-lan\."

# Verify VLAN configuration
uci show network | grep bridge-vlan

# Test basic connectivity
ping 192.168.20.1
ping 192.168.50.1
```

### Issue: IoT Internet Isolation Broken
```bash
# Check firewall rules
uci show firewall | grep "Block IoT Internet"

# Verify iptables rules
iptables -L FORWARD -v | grep 192.168.50

# Test isolation
ping -I br-lan.50 -c 1 8.8.8.8  # Should fail
```

### Issue: HomeIoT SSID Not Broadcasting
```bash
# Check wireless configuration
uci show wireless | grep -A5 "HomeIoT"

# Verify WiFi service status
/etc/init.d/network restart
iwconfig

# Check radio status
wifi status
```

### Issue: High Latency Between VLANs
```bash
# Check switch/bridge performance
bridge fdb show | head -10

# Verify STP status
cat /sys/class/net/br-lan/bridge/stp_state

# Test different packet sizes
ping -s 64 -c 5 192.168.50.1
ping -s 1024 -c 5 192.168.50.1
```

---

## Files Generated During Week 1

### Log Files:
- `/var/log/ventsys/network_validation_[timestamp].log` - Validation results
- `/var/log/ventsys_network_monitor.log` - Continuous monitoring data  
- `/var/log/mac_address_updates.log` - Device registration changes
- `/var/log/ventsys_alerts.log` - Performance alerts and warnings

### Data Files:
- `/tmp/ventsys_reports/week1_validation_results.json` - Structured validation results
- `/var/log/ventsys_performance_baseline.json` - Performance baseline data
- `/etc/ventsys/device_registry.yaml` - VentSys device registry
- `/tmp/ventsys_performance_report_[timestamp].txt` - Weekly performance report

### Backup Files:
- `/etc/config/backups/ventsys/dhcp_backup_[timestamp].conf` - DHCP config backups
- `/etc/config/backups/phases/phase_week1_completion_[timestamp]/` - Complete config backup

---

## Week 1 Completion Checklist

- [ ] Network validation script executed successfully (PASSED status)
- [ ] All critical VLANs operational (20, 50 minimum)
- [ ] HomeIoT WiFi SSID broadcasting and mapped to VLAN 50
- [ ] IoT internet isolation confirmed working
- [ ] Performance baseline established (24+ hours data)
- [ ] Existing devices discovered and registered
- [ ] MAC addresses collected and DHCP reservations updated
- [ ] System resource utilization within acceptable limits
- [ ] Network latency meets real-time control requirements (< 50ms)
- [ ] Security isolation validated (IoT blocked, automation allowed)
- [ ] Documentation generated and filed
- [ ] Week 1 completion backup created
- [ ] Ready to proceed to Week 2 (Certificate Infrastructure)

**Week 1 Status: READY FOR WEEK 2** ✅