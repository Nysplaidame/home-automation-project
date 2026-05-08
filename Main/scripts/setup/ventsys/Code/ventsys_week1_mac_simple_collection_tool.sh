#!/bin/bash

# =============================================================================
# VentSys Week 1: Simple MAC Address Collection and DHCP Management Tool
# =============================================================================
# PURPOSE: Discovers VentSys devices on network and updates DHCP reservations
#          with collected MAC addresses for static IP assignments.
#
# WHERE TO RUN: OpenWrt router (GL.iNet GL-MT6000) via SSH as root
# EXECUTION: /usr/local/bin/ventsys_mac_collection.sh --scan
#           /usr/local/bin/ventsys_mac_collection.sh --update <device> <mac>
# DURATION: ~15 minutes for discovery, ~5 minutes per MAC update
# OUTPUT: Device discovery results and DHCP reservation updates
# =============================================================================

# VentSys Week 1: Simple MAC Address Collection and DHCP Management
# Purpose: Discover VentSys devices and update DHCP reservations
# Environment: OpenWrt router with existing Phase 3 DHCP configuration

set -euo pipefail

LOG_FILE="/var/log/ventsys_mac_updates.log"

# VentSys device definitions (from device registry)
declare -A VENTSYS_DEVICES=(
    ["home-assistant"]="192.168.20.101:Home Assistant VM"
    ["ventsys-main-fan"]="192.168.50.21:Main Fan Controller"  # A7-1 fix: was ventsys-fan-controller (stale name)
    ["ventsys-sla-print-valve"]="192.168.50.56:SLA Print Valve Controller"  # A7-1 fix: was ventsys-sla-valve (stale name)
    ["ventsys-fdm-print-valve"]="192.168.50.55:FDM Print Valve Controller"  # A7-1 fix: was ventsys-fdm-valve@.83 - device does not exist; canonical is ventsys-fdm-print-valve@.55
    ["ventsys-booth-sensor"]="192.168.50.33:Booth Sensor Board"  # A7-1 fix: was ventsys-booth-valve@.84 - device does not exist; closest is ventsys-booth-sensor@.33
)

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $*" | tee -a "$LOG_FILE"
}

# Validate MAC address format
validate_mac() {
    local mac="$1"
    if [[ $mac =~ ^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$ ]]; then
        return 0
    else
        return 1
    fi
}

# Update device MAC address in DHCP
update_device_mac() {
    local device_name="$1"
    local mac_address="$2"
    
    # Validate inputs
    if [[ ! -v VENTSYS_DEVICES["$device_name"] ]]; then
        echo "ERROR: Unknown device '$device_name'"
        echo "Available devices:"
        for dev in "${!VENTSYS_DEVICES[@]}"; do
            echo "  $dev (${VENTSYS_DEVICES[$dev]%:*})"
        done
        return 1
    fi
    
    if ! validate_mac "$mac_address"; then
        echo "ERROR: Invalid MAC address format: $mac_address"
        echo "Expected format: XX:XX:XX:XX:XX:XX"
        return 1
    fi
    
    local device_info="${VENTSYS_DEVICES[$device_name]}"
    local ip_address="${device_info%:*}"
    
    log "Updating $device_name: $ip_address -> $mac_address"
    
    # Find existing DHCP host entry
    local host_sections
    host_sections=$(uci show dhcp | grep "name='$device_name'" | cut -d'.' -f2 | cut -d'=' -f1 || true)
    
    if [ -n "$host_sections" ]; then
        # Update existing entry
        for section in $host_sections; do
            uci set "dhcp.$section.mac=$mac_address"
        done
        log "Updated existing DHCP reservation"
    else
        # Create new entry
        uci add dhcp host
        uci set "dhcp.@host[-1].name=$device_name"
        uci set "dhcp.@host[-1].dns=1"
        uci set "dhcp.@host[-1].mac=$mac_address"
        uci set "dhcp.@host[-1].ip=$ip_address"
        log "Created new DHCP reservation"
    fi
    
    # Apply changes
    if uci commit dhcp && /etc/init.d/dnsmasq restart; then
        echo "SUCCESS: Updated $device_name MAC address"
        return 0
    else
        echo "ERROR: Failed to update DHCP configuration"
        return 1
    fi
}

# Scan networks for VentSys devices
scan_devices() {
    echo "Scanning for VentSys devices..."
    echo ""
    
    for device_name in "${!VENTSYS_DEVICES[@]}"; do
        local device_info="${VENTSYS_DEVICES[$device_name]}"
        local ip_address="${device_info%:*}"
        local description="${device_info#*:}"
        
        echo -n "Checking $description ($ip_address)... "
        
        if ping -c 2 -W 1 "$ip_address" >/dev/null 2>&1; then
            local mac
            mac=$(arp -n "$ip_address" 2>/dev/null | awk 'NR==1{print $3}')
            
            if [ -n "$mac" ] && validate_mac "$mac"; then
                echo "FOUND: $mac"
                echo "  Command: $0 --update $device_name $mac"
            else
                echo "FOUND: (MAC not in ARP table yet)"
            fi
        else
            echo "Not responding"
        fi
    done
    
    echo ""
    echo "Note: Devices may need to be powered on and connected to appear in scan"
}

# List current DHCP reservations
list_reservations() {
    echo "Current VentSys DHCP Reservations:"
    echo "=================================="
    
    for device_name in "${!VENTSYS_DEVICES[@]}"; do
        local device_info="${VENTSYS_DEVICES[$device_name]}"
        local expected_ip="${device_info%:*}"
        
        local host_sections
        host_sections=$(uci show dhcp | grep "name='$device_name'" | cut -d'.' -f2 | cut -d'=' -f1 || true)
        
        if [ -n "$host_sections" ]; then
            for section in $host_sections; do
                local mac ip
                mac=$(uci get "dhcp.$section.mac" 2>/dev/null || echo "NOT_SET")
                ip=$(uci get "dhcp.$section.ip" 2>/dev/null || echo "NOT_SET")
                echo "$device_name: $ip ($mac)"
            done
        else
            echo "$device_name: No reservation (expected $expected_ip)"
        fi
    done
}

# Test device connectivity
test_device() {
    local device_name="$1"
    
    if [[ ! -v VENTSYS_DEVICES["$device_name"] ]]; then
        echo "ERROR: Unknown device '$device_name'"
        return 1
    fi
    
    local device_info="${VENTSYS_DEVICES[$device_name]}"
    local ip_address="${device_info%:*}"
    
    echo "Testing connectivity to $device_name ($ip_address)..."
    
    if ping -c 3 -W 2 "$ip_address"; then
        local mac
        mac=$(arp -n "$ip_address" 2>/dev/null | awk 'NR==1{print $3}')
        [ -n "$mac" ] && echo "MAC Address: $mac"
        return 0
    else
        echo "Device not reachable"
        return 1
    fi
}

# Show usage
show_usage() {
    echo "VentSys MAC Address Collection Tool"
    echo ""
    echo "USAGE:"
    echo "  $0 --scan                           Scan for VentSys devices"
    echo "  $0 --update <device> <mac>          Update device MAC address"
    echo "  $0 --list                           List current reservations"
    echo "  $0 --test <device>                  Test device connectivity"
    echo ""
    echo "EXAMPLES:"
    echo "  $0 --scan"
    echo "  $0 --update home-assistant AA:BB:CC:DD:EE:FF"
    echo "  $0 --list"
    echo ""
    echo "AVAILABLE DEVICES:"
    for device in "${!VENTSYS_DEVICES[@]}"; do
        echo "  $device (${VENTSYS_DEVICES[$device]})"
    done
}

# Main execution
main() {
    # Check if running as root
    if [ "$EUID" -ne 0 ]; then
        echo "ERROR: Must run as root for UCI and network operations"
        exit 1
    fi
    
    # Parse arguments
    case "${1:-}" in
        --scan)
            scan_devices
            ;;
        --update)
            if [ $# -ne 3 ]; then
                echo "ERROR: --update requires device name and MAC address"
                exit 1
            fi
            update_device_mac "$2" "$3"
            ;;
        --list)
            list_reservations
            ;;
        --test)
            if [ $# -ne 2 ]; then
                echo "ERROR: --test requires device name"
                exit 1
            fi
            test_device "$2"
            ;;
        --help|"")
            show_usage
            ;;
        *)
            echo "ERROR: Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
}

main "$@"
