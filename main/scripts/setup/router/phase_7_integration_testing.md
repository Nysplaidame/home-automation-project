# Phase 7: Integration Testing

**Duration**: 4-6 hours  
**Risk Level**: Low-Medium (comprehensive validation)  
**Prerequisites**: Phase 6 completed, VPN operational

## Overview
Conducts comprehensive end-to-end testing of complete network architecture. Validates all network segments, security isolation, internet access controls, and inter-VLAN communication rules. Establishes performance baselines and confirms readiness for production deployment and VentSys integration.

## Sub-Tasks

### 7.1 Complete System Status Validation
**Duration**: 30 minutes

```bash
# Create Phase 7 entry backup
/usr/local/bin/backup_phase.sh 7_entry

echo "=== Complete System Status Validation ===" > /tmp/phase7_system_status.txt

# Validate all services are running
services=("network" "firewall" "dnsmasq" "wireless")
for service in "${services[@]}"; do
    if /etc/init.d/$service status >/dev/null 2>&1; then
        echo "✓ $service running" >> /tmp/phase7_system_status.txt
    else
        echo "✗ $service not running" >> /tmp/phase7_system_status.txt
    fi
done

# Check all VLAN interfaces
for vlan in 1 10 20 30 35 40 50 60 70 99; do
    if ip addr show br-lan.$vlan >/dev/null 2>&1; then
        ip_addr=$(ip addr show br-lan.$vlan | grep 'inet ' | awk '{print $2}')
        echo "✓ VLAN $vlan: $ip_addr" >> /tmp/phase7_system_status.txt
    else
        echo "✗ VLAN $vlan interface missing" >> /tmp/phase7_system_status.txt
    fi
done

# Check WireGuard
if ip addr show wg0 >/dev/null 2>&1; then
    wg_addr=$(ip addr show wg0 | grep 'inet ' | awk '{print $2}')
    echo "✓ WireGuard interface: $wg_addr" >> /tmp/phase7_system_status.txt
else
    echo "✗ WireGuard interface missing" >> /tmp/phase7_system_status.txt
fi

cat /tmp/phase7_system_status.txt
```

### 7.2 Network Connectivity Matrix Testing
**Duration**: 45 minutes

```bash
echo "=== Network Connectivity Matrix Testing ===" > /tmp/phase7_connectivity_matrix.txt

# Test connectivity between gateway interfaces (router-level testing)
# NOTE ON SCOPE: These ping -I tests probe whether the *router itself* can
# forward traffic between its own gateway IPs. They validate the routing table
# and zone forwarding rules, but they do NOT prove client-to-client isolation.
# Forwarded traffic from a client traverses nftables/iptables in a different
# path than router-originated traffic. Full isolation validation requires
# physical test devices on each VLAN running pings across zone boundaries.
# Treat these tests as a sanity check only — not a security proof.
networks=("192.168.1.1" "192.168.10.1" "192.168.20.1" "192.168.30.1" "192.168.35.1" "192.168.40.1" "192.168.50.1" "192.168.60.1" "192.168.70.1" "192.168.99.1")

echo "Testing inter-network gateway connectivity:" >> /tmp/phase7_connectivity_matrix.txt
for source in "${networks[@]}"; do
    for dest in "${networks[@]}"; do
        if [ "$source" != "$dest" ]; then
            if ping -c 1 -W 2 -I "$source" "$dest" >/dev/null 2>&1; then
                echo "✓ $source → $dest" >> /tmp/phase7_connectivity_matrix.txt
            else
                echo "✗ $source → $dest" >> /tmp/phase7_connectivity_matrix.txt
            fi
        fi
    done
done

cat /tmp/phase7_connectivity_matrix.txt
```

### 7.3 Internet Access Validation by Network Segment
**Duration**: 30 minutes

```bash
echo "=== Internet Access Validation ===" > /tmp/phase7_internet_access.txt

# Test internet access from different network gateways
# Full internet access networks
full_access_nets=("192.168.1.1:LAN" "192.168.10.1:Management" "192.168.99.1:Guest")
for net_desc in "${full_access_nets[@]}"; do
    net=$(echo $net_desc | cut -d':' -f1)
    name=$(echo $net_desc | cut -d':' -f2)
    if ping -c 3 -W 5 -I "$net" 1.1.1.1 >/dev/null 2>&1; then
        echo "✓ $name ($net): Internet access working" >> /tmp/phase7_internet_access.txt
    else
        echo "✗ $name ($net): Internet access blocked" >> /tmp/phase7_internet_access.txt
    fi
done

# No internet access networks (should fail)
no_access_nets=("192.168.30.1:NVR" "192.168.35.1:Printers" "192.168.40.1:Storage" "192.168.50.1:IoT_Sensors")
for net_desc in "${no_access_nets[@]}"; do
    net=$(echo $net_desc | cut -d':' -f1)
    name=$(echo $net_desc | cut -d':' -f2)
    if ping -c 3 -W 5 -I "$net" 1.1.1.1 >/dev/null 2>&1; then
        echo "✗ $name ($net): Internet access not blocked (SECURITY ISSUE)" >> /tmp/phase7_internet_access.txt
    else
        echo "✓ $name ($net): Internet access properly blocked" >> /tmp/phase7_internet_access.txt
    fi
done

cat /tmp/phase7_internet_access.txt
```

### 7.4 DHCP and DNS Functionality Testing  
**Duration**: 25 minutes

```bash
echo "=== DHCP and DNS Testing ===" > /tmp/phase7_dhcp_dns_test.txt

# Test DHCP lease file exists and is being updated
if [ -f /tmp/dhcp.leases ]; then
    lease_count=$(wc -l < /tmp/dhcp.leases)
    echo "✓ DHCP lease file exists with $lease_count entries" >> /tmp/phase7_dhcp_dns_test.txt
else
    echo "✗ DHCP lease file missing" >> /tmp/phase7_dhcp_dns_test.txt
fi

# Test local DNS resolution
local_domains=("router.home.local" "proxmox.home.local" "homeassistant.home.local" "frigate.home.local" "nas.home.local")
for domain in "${local_domains[@]}"; do
    if nslookup "$domain" 127.0.0.1 >/dev/null 2>&1; then
        echo "✓ Local DNS resolution: $domain" >> /tmp/phase7_dhcp_dns_test.txt
    else
        echo "✗ Local DNS resolution failed: $domain" >> /tmp/phase7_dhcp_dns_test.txt
    fi
done

# Test external DNS resolution
if nslookup google.com 127.0.0.1 >/dev/null 2>&1; then
    echo "✓ External DNS resolution working" >> /tmp/phase7_dhcp_dns_test.txt
else
    echo "✗ External DNS resolution failed" >> /tmp/phase7_dhcp_dns_test.txt
fi

cat /tmp/phase7_dhcp_dns_test.txt
```

### 7.5 Wireless Network Comprehensive Testing
**Duration**: 35 minutes

```bash
echo "=== Wireless Network Testing ===" > /tmp/phase7_wireless_test.txt

# Verify all expected SSIDs are configured and not disabled
# iwlist is a client-side scan tool — it scans for external APs and
# is not a reliable way to verify your own router's SSIDs. On OpenWrt it may
# report nothing or scan the wrong interface. The correct method is to check
# the UCI wireless config (for configuration) and hostapd (for live broadcast).
expected_ssids=("HomeMain" "HomeAdmin" "HomePrinters" "HomeIoT" "HomeGuest")
broadcasting_count=0
for ssid in "${expected_ssids[@]}"; do
    # Check UCI: SSID must be configured and not explicitly disabled
    if uci show wireless | grep -q "\.ssid='$ssid'"; then
        # Confirm the wifi-iface containing this SSID is not disabled
        iface=$(uci show wireless | grep "\.ssid='$ssid'" | cut -d. -f1-2)
        disabled=$(uci get ${iface}.disabled 2>/dev/null)
        if [ "$disabled" != "1" ]; then
            echo "✓ SSID configured and enabled: $ssid" >> /tmp/phase7_wireless_test.txt
            broadcasting_count=$((broadcasting_count + 1))
        else
            echo "✗ SSID configured but disabled: $ssid" >> /tmp/phase7_wireless_test.txt
        fi
    else
        echo "✗ SSID not configured: $ssid" >> /tmp/phase7_wireless_test.txt
    fi
done

echo "Active visible SSIDs: $broadcasting_count/5" >> /tmp/phase7_wireless_test.txt

# HomeAdmin-2G is intentionally hidden; verify config state via UCI
if uci show wireless | grep -A8 "ssid='HomeAdmin-2G'" | grep -q "hidden='1'"; then
    echo "✓ HomeAdmin-2G configured as hidden backup SSID" >> /tmp/phase7_wireless_test.txt
else
    echo "✗ HomeAdmin-2G hidden backup SSID not configured correctly" >> /tmp/phase7_wireless_test.txt
fi

# Check radio status
echo "" >> /tmp/phase7_wireless_test.txt
echo "Radio Status:" >> /tmp/phase7_wireless_test.txt
wifi status 2>/dev/null | jsonfilter -e '@.*.up' >> /tmp/phase7_wireless_test.txt

# Verify HomeDMZ is disabled (should not be broadcasting)
if uci show wireless | grep -q "\.ssid='HomeDMZ'"; then
    iface=$(uci show wireless | grep "\.ssid='HomeDMZ'" | cut -d. -f1-2)
    disabled=$(uci get ${iface}.disabled 2>/dev/null)
    if [ "$disabled" = "1" ]; then
        echo "✓ HomeDMZ properly disabled in UCI config" >> /tmp/phase7_wireless_test.txt
    else
        echo "✗ HomeDMZ is configured and NOT disabled (should be disabled)" >> /tmp/phase7_wireless_test.txt
    fi
else
    echo "✓ HomeDMZ not configured (not broadcasting)" >> /tmp/phase7_wireless_test.txt
fi

cat /tmp/phase7_wireless_test.txt
```

### 7.6 Security Isolation Comprehensive Testing
**Duration**: 40 minutes

```bash
echo "=== Security Isolation Testing ===" > /tmp/phase7_security_isolation.txt

# Test firewall rule effectiveness
echo "Firewall Rule Validation:" >> /tmp/phase7_security_isolation.txt

# Count and verify critical firewall rules
rule_categories=(
    "Internet Access:LAN to Internet,Management to Internet,Guest Internet Access"
    "Internet Blocks:Block NVR Internet,Block Storage Internet,Block IoT Internet,Block Printers Internet"
    "VentSys Rules:ESPHome API HA to IoT,VentSys MQTT IoT to HA,Block IoT Internet"
    "Isolation Rules:Block Guest to LAN,Block DMZ to LAN,Block VPN to Management"
)

for category in "${rule_categories[@]}"; do
    category_name=$(echo $category | cut -d':' -f1)
    rules=$(echo $category | cut -d':' -f2 | tr ',' ' ')
    
    echo "" >> /tmp/phase7_security_isolation.txt
    echo "$category_name:" >> /tmp/phase7_security_isolation.txt
    
    for rule in $rules; do
        if uci show firewall | grep -q "$rule"; then
            echo "  ✓ $rule" >> /tmp/phase7_security_isolation.txt
        else
            echo "  ✗ $rule" >> /tmp/phase7_security_isolation.txt
        fi
    done
done

cat /tmp/phase7_security_isolation.txt
```

### 7.7 VentSys Integration Readiness Testing
**Duration**: 30 minutes

```bash
echo "=== VentSys Integration Readiness Testing ===" > /tmp/phase7_ventsys_readiness.txt

# Critical VentSys network requirements
echo "VentSys Critical Network Requirements:" >> /tmp/phase7_ventsys_readiness.txt

# 1. VLAN 20 (Automation) operational for Home Assistant VM
if ip addr show br-lan.20 | grep -q "192.168.20.1"; then
    echo "✓ VLAN 20 (Automation) ready for Home Assistant VM" >> /tmp/phase7_ventsys_readiness.txt
else
    echo "✗ VLAN 20 (Automation) not operational" >> /tmp/phase7_ventsys_readiness.txt
fi

# 2. VLAN 35 (Printers) operational — required for Bambuddy → printer path
if ip addr show br-lan.35 | grep -q "192.168.35.1"; then
    echo "✓ VLAN 35 (Printers) operational" >> /tmp/phase7_ventsys_readiness.txt
else
    echo "✗ VLAN 35 (Printers) not operational" >> /tmp/phase7_ventsys_readiness.txt
fi

# 3. VLAN 50 (IoT Sensors) operational and isolated
if ip addr show br-lan.50 | grep -q "192.168.50.1"; then
    echo "✓ VLAN 50 (IoT Sensors) ready for VentSys devices" >> /tmp/phase7_ventsys_readiness.txt
else
    echo "✗ VLAN 50 (IoT Sensors) not operational" >> /tmp/phase7_ventsys_readiness.txt
fi

# 4. HomeIoT WiFi SSID
# Check UCI config rather than scanning as a client with iwlist.
homeiot_iface=$(uci show wireless | grep "\.ssid='HomeIoT'" | cut -d. -f1-2 2>/dev/null)
if [ -n "$homeiot_iface" ]; then
    disabled=$(uci get ${homeiot_iface}.disabled 2>/dev/null)
    network=$(uci get ${homeiot_iface}.network 2>/dev/null)
    if [ "$disabled" != "1" ] && [ "$network" = "HomeIoT" ]; then
        echo "✓ HomeIoT SSID enabled and mapped to HomeIoT (VLAN 50)" >> /tmp/phase7_ventsys_readiness.txt
    elif [ "$disabled" = "1" ]; then
        echo "✗ HomeIoT SSID is disabled" >> /tmp/phase7_ventsys_readiness.txt
    else
        echo "✗ HomeIoT SSID network mapping incorrect (expected: HomeIoT, got: $network)" >> /tmp/phase7_ventsys_readiness.txt
    fi
else
    echo "✗ HomeIoT WiFi SSID not configured" >> /tmp/phase7_ventsys_readiness.txt
fi

# 5. IoT internet isolation (security critical)
if ping -c 2 -W 3 -I 192.168.50.1 1.1.1.1 >/dev/null 2>&1; then
    echo "✗ VLAN 50 has internet access (SECURITY ISSUE)" >> /tmp/phase7_ventsys_readiness.txt
else
    echo "✓ VLAN 50 internet access properly blocked" >> /tmp/phase7_ventsys_readiness.txt
fi

# 6. VentSys communication ports
ventsys_ports=("8883:MQTT" "6053:ESPHome")
for port_desc in "${ventsys_ports[@]}"; do
    port=$(echo $port_desc | cut -d':' -f1)
    service=$(echo $port_desc | cut -d':' -f2)
    if uci show firewall | grep -q "dest_port.*$port"; then
        echo "✓ Firewall rule exists for $service port $port" >> /tmp/phase7_ventsys_readiness.txt
    else
        echo "✗ Firewall rule missing for $service port $port" >> /tmp/phase7_ventsys_readiness.txt
    fi
done

cat /tmp/phase7_ventsys_readiness.txt
```

### 7.8 Performance Baseline Establishment
**Duration**: 25 minutes

```bash
echo "=== Performance Baseline Establishment ===" > /tmp/phase7_performance_baseline.txt

# Network interface throughput capabilities
echo "Network Interface Performance:" >> /tmp/phase7_performance_baseline.txt
for iface in wan lan1 lan2 lan3 lan4; do
    if ethtool "$iface" 2>/dev/null | grep -q "Speed"; then
        speed=$(ethtool "$iface" 2>/dev/null | grep "Speed" | awk '{print $2}')
        echo "✓ $iface: $speed" >> /tmp/phase7_performance_baseline.txt
    else
        echo "⚠ $iface: Speed information not available" >> /tmp/phase7_performance_baseline.txt
    fi
done

# Memory and CPU utilization baseline
echo "" >> /tmp/phase7_performance_baseline.txt
echo "System Resource Utilization:" >> /tmp/phase7_performance_baseline.txt
echo "Memory:" >> /tmp/phase7_performance_baseline.txt
free -h >> /tmp/phase7_performance_baseline.txt
echo "" >> /tmp/phase7_performance_baseline.txt
echo "CPU Load:" >> /tmp/phase7_performance_baseline.txt
uptime >> /tmp/phase7_performance_baseline.txt

# Firewall rule count and performance impact
rule_count=$(iptables -L | wc -l)
echo "" >> /tmp/phase7_performance_baseline.txt
echo "Firewall Performance:" >> /tmp/phase7_performance_baseline.txt
echo "Total iptables rules: $rule_count" >> /tmp/phase7_performance_baseline.txt
if [ $rule_count -lt 500 ]; then
    echo "✓ Firewall rule count optimal" >> /tmp/phase7_performance_baseline.txt
elif [ $rule_count -lt 1000 ]; then
    echo "⚠ Firewall rule count moderate - monitor performance" >> /tmp/phase7_performance_baseline.txt
else
    echo "⚠ High firewall rule count - may impact performance" >> /tmp/phase7_performance_baseline.txt
fi

cat /tmp/phase7_performance_baseline.txt
```

### 7.9 Comprehensive System Health Check
**Duration**: 20 minutes

```bash
echo "=== Comprehensive System Health Check ===" > /tmp/phase7_health_check.txt

# Check system logs for errors
echo "System Log Analysis (last 50 lines):" >> /tmp/phase7_health_check.txt
if dmesg | tail -50 | grep -i "error\|fail\|warn" | wc -l; then
    error_count=$(dmesg | tail -50 | grep -i "error\|fail\|warn" | wc -l)
    echo "System errors/warnings in last 50 log entries: $error_count" >> /tmp/phase7_health_check.txt
    if [ $error_count -gt 10 ]; then
        echo "⚠ High error count - investigate system logs" >> /tmp/phase7_health_check.txt
    else
        echo "✓ System error count acceptable" >> /tmp/phase7_health_check.txt
    fi
fi

# Check filesystem usage
echo "" >> /tmp/phase7_health_check.txt
echo "Filesystem Usage:" >> /tmp/phase7_health_check.txt
df -h >> /tmp/phase7_health_check.txt

# Network service status
echo "" >> /tmp/phase7_health_check.txt
echo "Critical Service Status:" >> /tmp/phase7_health_check.txt
critical_services=("network" "firewall" "dnsmasq")
for service in "${critical_services[@]}"; do
    if /etc/init.d/$service status >/dev/null 2>&1; then
        echo "✓ $service: Running" >> /tmp/phase7_health_check.txt
    else
        echo "✗ $service: Not running" >> /tmp/phase7_health_check.txt
    fi
done

cat /tmp/phase7_health_check.txt
```

### 7.10 Final Integration Test Summary
**Duration**: 15 minutes

```bash
echo "=== Phase 7 Final Integration Test Summary ===" > /tmp/phase7_final_summary.txt

# Compile all test results
echo "PHASE 7 INTEGRATION TESTING SUMMARY:" >> /tmp/phase7_final_summary.txt
echo "Date: $(date)" >> /tmp/phase7_final_summary.txt
echo "Test Duration: Approximately $(( ($(date +%s) - $(stat -c %Y /tmp/phase7_system_status.txt)) / 60 )) minutes" >> /tmp/phase7_final_summary.txt
echo "" >> /tmp/phase7_final_summary.txt

# Analyze all test files for failures
test_files=(
    "/tmp/phase7_system_status.txt:System Status"
    "/tmp/phase7_connectivity_matrix.txt:Network Connectivity" 
    "/tmp/phase7_internet_access.txt:Internet Access Controls"
    "/tmp/phase7_dhcp_dns_test.txt:DHCP and DNS Services"
    "/tmp/phase7_wireless_test.txt:Wireless Networks"
    "/tmp/phase7_security_isolation.txt:Security Isolation"
    "/tmp/phase7_ventsys_readiness.txt:VentSys Readiness"
    "/tmp/phase7_performance_baseline.txt:Performance Baseline"
    "/tmp/phase7_health_check.txt:System Health"
)

total_failures=0
critical_failures=0

for test_desc in "${test_files[@]}"; do
    file=$(echo $test_desc | cut -d':' -f1)
    name=$(echo $test_desc | cut -d':' -f2)
    
    if [ -f "$file" ]; then
        failures=$(grep -c "✗" "$file" 2>/dev/null || echo 0)
        total_failures=$((total_failures + failures))
        
        if [ $failures -eq 0 ]; then
            echo "✓ $name: All tests passed" >> /tmp/phase7_final_summary.txt
        else
            echo "✗ $name: $failures failures detected" >> /tmp/phase7_final_summary.txt
            
            # Mark as critical if it's VentSys or security related
            if echo "$name" | grep -q -E "(VentSys|Security|Internet Access)"; then
                critical_failures=$((critical_failures + failures))
            fi
        fi
    else
        echo "⚠ $name: Test file missing" >> /tmp/phase7_final_summary.txt
        total_failures=$((total_failures + 1))
    fi
done

echo "" >> /tmp/phase7_final_summary.txt
echo "SUMMARY STATISTICS:" >> /tmp/phase7_final_summary.txt
echo "Total test failures: $total_failures" >> /tmp/phase7_final_summary.txt
echo "Critical failures: $critical_failures" >> /tmp/phase7_final_summary.txt

if [ $critical_failures -eq 0 ] && [ $total_failures -lt 5 ]; then
    echo "" >> /tmp/phase7_final_summary.txt
    echo "✓ PHASE 7 INTEGRATION TESTING PASSED" >> /tmp/phase7_final_summary.txt
    echo "✓ Network architecture ready for production deployment" >> /tmp/phase7_final_summary.txt
    echo "✓ VentSys integration prerequisites validated" >> /tmp/phase7_final_summary.txt
    echo "SUCCESS: Integration testing completed successfully" >> /tmp/deployment_logs/phase7.log
else
    echo "" >> /tmp/phase7_final_summary.txt
    echo "✗ PHASE 7 INTEGRATION TESTING FAILED" >> /tmp/phase7_final_summary.txt
    echo "✗ Critical failures: $critical_failures, Total failures: $total_failures" >> /tmp/phase7_final_summary.txt
    echo "⚠ Address failures before proceeding to production" >> /tmp/phase7_final_summary.txt
    echo "FAILURE: Integration testing found issues" >> /tmp/deployment_logs/phase7.log
fi

cat /tmp/phase7_final_summary.txt
```

## Success Criteria for Phase 7

- **All network services operational**: Network, firewall, DHCP, wireless, VPN services running
- **Network connectivity validated**: All VLAN segments communicating as designed
- **Security isolation confirmed**: Internet access controls and network segmentation working
- **Wireless networks functional**: All SSIDs broadcasting with proper VLAN assignments
- **VentSys readiness validated**: VLANs 20, 35, and 50 ready for HA, printer, and IoT integration
- **Performance baseline established**: System resources adequate for operational load
- **No critical security failures**: Security isolation and access controls functioning properly

## Failure Analysis and Resolution

### Critical Failures (Block progression)
- **Security isolation failures**: Fix firewall rules before proceeding
- **VentSys readiness failures**: Network foundation must be solid for IoT integration  
- **Service failures**: All core services must be operational

### Minor Issues (Can proceed with monitoring)
- **Performance warnings**: Monitor during operation
- **Non-critical connectivity issues**: Address during optimization
- **Log warnings**: Investigate but don't block progression

**Proceed to Phase 8 only when critical failures resolved and VentSys integration prerequisites validated.**
