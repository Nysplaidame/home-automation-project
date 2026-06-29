#!/bin/bash

# =============================================================================
# VentSys Week 1: Network Infrastructure Validation Script
# =============================================================================
# PURPOSE: Validates existing OpenWrt network configuration meets VentSys 
#          real-time control requirements. Tests critical VLANs, connectivity,
#          security isolation, and WiFi infrastructure.
#
# WHERE TO RUN: OpenWrt router (GL.iNet GL-MT6000) via SSH as root
# EXECUTION: /usr/local/bin/ventsys_week1_validation.sh
# DURATION: ~30 minutes
# OUTPUT: Pass/fail report with specific remediation guidance
# =============================================================================

# VentSys Week 1: Network Infrastructure Validation
# Purpose: Validate existing OpenWrt network configuration supports VentSys requirements
# Environment: GL.iNet GL-MT6000 OpenWrt router with Phases 1-7 configuration

set -euo pipefail

SCRIPT_VERSION="1.0.0"
LOG_FILE="/var/log/ventsys_validation.log"
RESULT_FILE="/tmp/ventsys_week1_results.txt"

# VentSys network requirements from Phase documentation
AUTOMATION_VLAN="20"
IOT_VLAN="50"
HA_IP="192.168.20.101"
IOT_GATEWAY="192.168.50.1"
IOT_SSID="HomeIoT"

# Performance requirements for real-time control
MAX_LATENCY_MS="50"
MAX_PACKET_LOSS="1"

# Logging function
log() {
    local level="$1"
    local message="$2"
    echo "$(date '+%Y-%m-%d %H:%M:%S') [$level] $message" | tee -a "$LOG_FILE"
}

# Initialize validation environment
init_validation() {
    mkdir -p "$(dirname "$LOG_FILE")"
    log "INFO" "Starting VentSys Week 1 validation (v$SCRIPT_VERSION)"
    
    # Check required commands
    local missing_cmds=()
    for cmd in ping ip uci iwconfig; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            missing_cmds+=("$cmd")
        fi
    done
    
    if [ ${#missing_cmds[@]} -gt 0 ]; then
        log "ERROR" "Missing required commands: ${missing_cmds[*]}"
        exit 1
    fi
    
    if [ "$EUID" -ne 0 ]; then
        log "ERROR" "Must run as root for network testing"
        exit 1
    fi
    
    echo "VentSys Week 1 Network Validation Results" > "$RESULT_FILE"
    echo "=========================================" >> "$RESULT_FILE"
    echo "Generated: $(date)" >> "$RESULT_FILE"
    echo "" >> "$RESULT_FILE"
}

# Test critical VLAN interfaces
test_vlan_interfaces() {
    log "INFO" "Testing critical VLAN interfaces"
    local failed=0
    
    # Test VLAN 20 (Automation) - Critical for Home Assistant
    if ip addr show "br-lan.$AUTOMATION_VLAN" | grep -q "192.168.${AUTOMATION_VLAN}.1"; then
        log "INFO" "VLAN $AUTOMATION_VLAN operational"
        echo "✓ VLAN $AUTOMATION_VLAN (Automation): OK" >> "$RESULT_FILE"
    else
        log "ERROR" "VLAN $AUTOMATION_VLAN failed"
        echo "✗ VLAN $AUTOMATION_VLAN (Automation): FAILED" >> "$RESULT_FILE"
        failed=$((failed + 1))
    fi
    
    # Test VLAN 50 (IoT Sensors) - Critical for VentSys devices
    if ip addr show "br-lan.$IOT_VLAN" | grep -q "192.168.${IOT_VLAN}.1"; then
        log "INFO" "VLAN $IOT_VLAN operational"
        echo "✓ VLAN $IOT_VLAN (IoT Sensors): OK" >> "$RESULT_FILE"
    else
        log "ERROR" "VLAN $IOT_VLAN failed"
        echo "✗ VLAN $IOT_VLAN (IoT Sensors): FAILED" >> "$RESULT_FILE"
        failed=$((failed + 1))
    fi
    
    return $failed
}

# Test inter-VLAN connectivity for VentSys
test_ventsys_connectivity() {
    log "INFO" "Testing VentSys inter-VLAN connectivity"
    
    # Test HA to IoT gateway path (critical for device control)
    if ping -I "br-lan.$AUTOMATION_VLAN" -c 5 -W 2 "$IOT_GATEWAY" >/dev/null 2>&1; then
        # Measure latency
        local latency
        latency=$(ping -I "br-lan.$AUTOMATION_VLAN" -c 10 -W 2 "$IOT_GATEWAY" 2>/dev/null | 
                 grep "rtt min/avg/max" | cut -d'/' -f5)
        
        if [ -n "$latency" ]; then
            log "INFO" "HA to IoT latency: ${latency}ms"
            
            # Check if latency meets real-time requirements
            if (( $(echo "$latency < $MAX_LATENCY_MS" | bc 2>/dev/null || echo "1") )); then
                echo "✓ HA to IoT connectivity: ${latency}ms (< ${MAX_LATENCY_MS}ms)" >> "$RESULT_FILE"
                return 0
            else
                log "WARN" "High latency: ${latency}ms (> ${MAX_LATENCY_MS}ms)"
                echo "⚠ HA to IoT connectivity: ${latency}ms (HIGH LATENCY)" >> "$RESULT_FILE"
                return 1
            fi
        else
            echo "✓ HA to IoT connectivity: OK (latency unknown)" >> "$RESULT_FILE"
            return 0
        fi
    else
        log "ERROR" "HA to IoT connectivity failed"
        echo "✗ HA to IoT connectivity: FAILED" >> "$RESULT_FILE"
        return 1
    fi
}

# Test IoT internet isolation (security critical)
test_iot_isolation() {
    log "INFO" "Testing IoT internet isolation"
    
    # IoT devices MUST NOT reach internet (security requirement)
    if ping -I "br-lan.$IOT_VLAN" -c 3 -W 2 9.9.9.9 >/dev/null 2>&1; then
        log "ERROR" "IoT internet isolation BROKEN - SECURITY RISK"
        echo "✗ IoT internet isolation: BROKEN (SECURITY RISK)" >> "$RESULT_FILE"
        return 1
    else
        log "INFO" "IoT internet access properly blocked"
        echo "✓ IoT internet isolation: OK" >> "$RESULT_FILE"
        return 0
    fi
}

# Test HomeIoT WiFi SSID
test_homeiot_wifi() {
    log "INFO" "Testing HomeIoT WiFi SSID"
    
    if iwconfig 2>/dev/null | grep -q "IEEE 802.11"; then
        if iwlist scan 2>/dev/null | grep -q "ESSID:\"$IOT_SSID\""; then
            log "INFO" "HomeIoT SSID broadcasting"
            echo "✓ HomeIoT WiFi SSID: Broadcasting" >> "$RESULT_FILE"
            
            # Check VLAN mapping
            if uci show wireless | grep -A3 "ssid='$IOT_SSID'" | grep -q "network='iot_sensors'"; then
                echo "✓ HomeIoT VLAN mapping: Correct (VLAN $IOT_VLAN)" >> "$RESULT_FILE"
                return 0
            else
                log "WARN" "HomeIoT VLAN mapping incorrect"
                echo "⚠ HomeIoT VLAN mapping: Check configuration" >> "$RESULT_FILE"
                return 1
            fi
        else
            log "ERROR" "HomeIoT SSID not broadcasting"
            echo "✗ HomeIoT WiFi SSID: Not broadcasting" >> "$RESULT_FILE"
            return 1
        fi
    else
        log "ERROR" "WiFi hardware not detected"
        echo "✗ WiFi hardware: Not detected" >> "$RESULT_FILE"
        return 1
    fi
}

# Discover VentSys devices
discover_devices() {
    log "INFO" "Discovering VentSys devices"
    echo "" >> "$RESULT_FILE"
    echo "Device Discovery:" >> "$RESULT_FILE"
    echo "=================" >> "$RESULT_FILE"
    
    local found_devices=0
    
    # Expected devices from VentSys plan
    local -A ventsys_devices=(
        ["192.168.20.101"]="Home Assistant VM"
    ["192.168.50.21"]="Main Fan (ventsys-main-fan)"
    ["192.168.50.56"]="SLA Print Valve (ventsys-sla-print-valve)"
    )
    
    for ip in "${!ventsys_devices[@]}"; do
        local device="${ventsys_devices[$ip]}"
        if ping -c 2 -W 1 "$ip" >/dev/null 2>&1; then
            local mac
            mac=$(arp -n "$ip" 2>/dev/null | awk '{print $3}' | head -1)
            log "INFO" "Found device: $device at $ip"
            echo "✓ $device: $ip${mac:+ ($mac)}" >> "$RESULT_FILE"
            found_devices=$((found_devices + 1))
        else
            echo "- $device: $ip (not responding)" >> "$RESULT_FILE"
        fi
    done
    
    log "INFO" "Found $found_devices VentSys devices"
    return 0
}

# Check firewall rules for VentSys
test_firewall_rules() {
    log "INFO" "Testing VentSys firewall rules"
    
    local rules_ok=0
    local total_rules=3
    
    # Check for HA to IoT access rule
    if uci show firewall 2>/dev/null | grep -q "HA to IoT Sensors Access\|automation.*iot_sensors"; then
        echo "✓ HA to IoT access rule: Present" >> "$RESULT_FILE"
        rules_ok=$((rules_ok + 1))
    else
        echo "⚠ HA to IoT access rule: Check firewall config" >> "$RESULT_FILE"
    fi
    
    # Check for IoT internet block rule  
    if uci show firewall 2>/dev/null | grep -q "Block.*IoT.*Internet\|iot_sensors.*wan.*REJECT"; then
        echo "✓ IoT internet block rule: Present" >> "$RESULT_FILE"
        rules_ok=$((rules_ok + 1))
    else
        echo "⚠ IoT internet block rule: Check firewall config" >> "$RESULT_FILE"
    fi
    
    # Check for MQTT rule (port 8883)
    if uci show firewall 2>/dev/null | grep -q "8883\|MQTT"; then
        echo "✓ MQTT access rule: Present" >> "$RESULT_FILE"
        rules_ok=$((rules_ok + 1))
    else
        echo "⚠ MQTT access rule: May need configuration" >> "$RESULT_FILE"
    fi
    
    log "INFO" "Firewall rules check: $rules_ok/$total_rules present"
    return 0
}

# Generate final report
generate_report() {
    log "INFO" "Generating validation report"
    
    echo "" >> "$RESULT_FILE"
    echo "Summary:" >> "$RESULT_FILE"
    echo "========" >> "$RESULT_FILE"
    
    # Count results
    local passed failed warnings
    passed=$(grep -c "✓" "$RESULT_FILE" || echo "0")
    failed=$(grep -c "✗" "$RESULT_FILE" || echo "0")
    warnings=$(grep -c "⚠" "$RESULT_FILE" || echo "0")
    
    echo "Passed: $passed" >> "$RESULT_FILE"
    echo "Failed: $failed" >> "$RESULT_FILE"
    echo "Warnings: $warnings" >> "$RESULT_FILE"
    echo "" >> "$RESULT_FILE"
    
    # Overall assessment
    if [ "$failed" -eq 0 ]; then
        if [ "$warnings" -eq 0 ]; then
            echo "✓ NETWORK READY FOR VENTSYS IMPLEMENTATION" >> "$RESULT_FILE"
            log "INFO" "Validation passed - ready for VentSys"
            return 0
        else
            echo "⚠ NETWORK READY WITH WARNINGS - Review and proceed" >> "$RESULT_FILE"
            log "WARN" "Validation passed with warnings"
            return 0
        fi
    else
        echo "✗ NETWORK NOT READY - Fix critical issues before proceeding" >> "$RESULT_FILE"
        log "ERROR" "Validation failed - $failed critical issues"
        return 1
    fi
}

# Troubleshooting suggestions
provide_troubleshooting() {
    local exit_code="$1"
    
    if [ "$exit_code" -ne 0 ]; then
        echo "" >> "$RESULT_FILE"
        echo "Troubleshooting:" >> "$RESULT_FILE"
        echo "================" >> "$RESULT_FILE"
        
        # Check what failed and provide specific guidance
        if grep -q "VLAN.*FAILED" "$RESULT_FILE"; then
            echo "• VLAN issues: Check 'uci show network' and restart network service" >> "$RESULT_FILE"
        fi
        
        if grep -q "connectivity.*FAILED" "$RESULT_FILE"; then
            echo "• Connectivity: Verify firewall allows VLAN 20 to VLAN 50 traffic" >> "$RESULT_FILE"
        fi
        
        if grep -q "isolation.*BROKEN" "$RESULT_FILE"; then
            echo "• SECURITY: IoT internet access must be blocked - check firewall rules" >> "$RESULT_FILE"
        fi
        
        if grep -q "WiFi.*Not broadcasting" "$RESULT_FILE"; then
            echo "• WiFi: Check wireless configuration and restart network service" >> "$RESULT_FILE"
        fi
        
        echo "" >> "$RESULT_FILE"
        echo "Commands to check:" >> "$RESULT_FILE"
        echo "  uci show network | grep interface" >> "$RESULT_FILE"
        echo "  uci show wireless | grep HomeIoT" >> "$RESULT_FILE"
        echo "  uci show firewall | grep -E '(iot|IoT)'" >> "$RESULT_FILE"
        echo "  /etc/init.d/network restart" >> "$RESULT_FILE"
    fi
}

# Main execution
main() {
    local total_errors=0
    
    init_validation
    
    log "INFO" "Running VentSys Week 1 validation tests"
    
    # Run validation tests
    test_vlan_interfaces || total_errors=$((total_errors + $?))
    test_ventsys_connectivity || total_errors=$((total_errors + $?))
    test_iot_isolation || total_errors=$((total_errors + $?))
    test_homeiot_wifi || total_errors=$((total_errors + $?))
    
    # Information gathering (non-blocking)
    discover_devices
    test_firewall_rules
    
    # Generate final report
    generate_report
    local report_result=$?
    
    # Provide troubleshooting if needed
    provide_troubleshooting $report_result
    
    # Display results
    echo ""
    echo "=== VentSys Week 1 Validation Complete ==="
    cat "$RESULT_FILE"
    echo ""
    echo "Detailed log: $LOG_FILE"
    echo "Results file: $RESULT_FILE"
    
    log "INFO" "Validation completed with exit code: $report_result"
    exit $report_result
}

# Execute main function
main "$@"
