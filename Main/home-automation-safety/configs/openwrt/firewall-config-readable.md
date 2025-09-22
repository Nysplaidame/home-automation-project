#!/bin/bash

# ============================================================================
# Home Automation Project - OpenWrt Firewall Configuration
# 4-VLAN Security Architecture Implementation
# Version: 1.1
# Date: 2025-09-20
# Repository: https://github.com/Nysplaidame/home-automation-project
# ============================================================================

set -e  # Exit on any error
set -u  # Exit on undefined variables

echo "Starting Home Automation Firewall Configuration..."
echo "Implementing 4-VLAN security architecture"

# ============================================================================
# BACKUP EXISTING CONFIGURATION
# ============================================================================

# Create backup of existing firewall config
echo "Creating backup of existing configuration..."
cp /etc/config/firewall "/etc/config/firewall.backup.$(date +%Y%m%d_%H%M%S)" || echo "Warning: Could not create backup"

# ============================================================================
# CLEAR EXISTING CONFIGURATION
# ============================================================================

echo "Clearing existing firewall configuration..."
> /etc/config/firewall

# ============================================================================
# BASIC FIREWALL DEFAULTS
# ============================================================================

echo "Setting up basic firewall defaults..."
cat >> /etc/config/firewall << 'EOF'

config defaults
    option syn_flood    1
    option input        REJECT
    option output       ACCEPT
    option forward      REJECT

EOF

# ============================================================================
# ZONE DEFINITIONS
# ============================================================================

echo "Creating firewall zones..."

# Zone: WAN (Internet)
uci add firewall zone
uci set firewall.@zone[-1].name='wan'
uci set firewall.@zone[-1].input='REJECT'
uci set firewall.@zone[-1].output='ACCEPT'
uci set firewall.@zone[-1].forward='REJECT'
uci set firewall.@zone[-1].masq='1'
uci set firewall.@zone[-1].mtu_fix='1'
uci add_list firewall.@zone[-1].network='wan'
uci add_list firewall.@zone[-1].network='wan6'

# Zone: LAN/MANAGEMENT (VLAN 10) - Default OpenWrt management
uci add firewall zone
uci set firewall.@zone[-1].name='management'
uci set firewall.@zone[-1].input='ACCEPT'
uci set firewall.@zone[-1].output='ACCEPT'
uci set firewall.@zone[-1].forward='ACCEPT'
uci add_list firewall.@zone[-1].network='lan'

# Zone: AUTOMATION (VLAN 20) - Home Assistant and services
uci add firewall zone
uci set firewall.@zone[-1].name='automation'
uci set firewall.@zone[-1].input='ACCEPT'
uci set firewall.@zone[-1].output='REJECT'
uci set firewall.@zone[-1].forward='REJECT'
uci add_list firewall.@zone[-1].network='automation'

# Zone: CCTV (VLAN 30) - No Internet Access
uci add firewall zone
uci set firewall.@zone[-1].name='cctv'
uci set firewall.@zone[-1].input='ACCEPT'
uci set firewall.@zone[-1].output='REJECT'
uci set firewall.@zone[-1].forward='REJECT'
uci add_list firewall.@zone[-1].network='cctv'

# Zone: STORAGE (VLAN 40) - No Internet Access
uci add firewall zone
uci set firewall.@zone[-1].name='storage'
uci set firewall.@zone[-1].input='ACCEPT'
uci set firewall.@zone[-1].output='REJECT'
uci set firewall.@zone[-1].forward='REJECT'
uci add_list firewall.@zone[-1].network='storage'

# Zone: IOT_SENSORS (VLAN 50) - No Internet Access (CRITICAL SAFETY)
uci add firewall zone
uci set firewall.@zone[-1].name='iot_sensors'
uci set firewall.@zone[-1].input='ACCEPT'
uci set firewall.@zone[-1].output='REJECT'
uci set firewall.@zone[-1].forward='REJECT'
uci add_list firewall.@zone[-1].network='iot_sensors'

# Zone: VPN_CLIENTS - For remote access
uci add firewall zone
uci set firewall.@zone[-1].name='vpn_clients'
uci set firewall.@zone[-1].input='ACCEPT'
uci set firewall.@zone[-1].output='REJECT'
uci set firewall.@zone[-1].forward='REJECT'
uci add_list firewall.@zone[-1].network='vpn'

echo "Firewall zones created successfully"

# ============================================================================
# INTERNET ACCESS RULES
# ============================================================================

echo "Configuring internet access rules..."

# Management to WAN - Full Internet Access
uci add firewall rule
uci set firewall.@rule[-1].name='Management to Internet'
uci set firewall.@rule[-1].src='management'
uci set firewall.@rule[-1].dest='wan'
uci set firewall.@rule[-1].target='ACCEPT'

# Home Assistant to WAN - Limited Internet Access
uci add firewall rule
uci set firewall.@rule[-1].name='Home Assistant Internet Access'
uci set firewall.@rule[-1].src='automation'
uci set firewall.@rule[-1].src_ip='192.168.20.101'
uci set firewall.@rule[-1].dest='wan'
uci set firewall.@rule[-1].target='ACCEPT'

# Frigate to WAN - For updates only
uci add firewall rule
uci set firewall.@rule[-1].name='Frigate Internet Access'
uci set firewall.@rule[-1].src='automation'
uci set firewall.@rule[-1].src_ip='192.168.20.102'
uci set firewall.@rule[-1].dest='wan'
uci set firewall.@rule[-1].dest_port='80,443'
uci set firewall.@rule[-1].proto='tcp'
uci set firewall.@rule[-1].target='ACCEPT'

# Block all other automation devices from internet
uci add firewall rule
uci set firewall.@rule[-1].name='Block Other Automation Internet'
uci set firewall.@rule[-1].src='automation'
uci set firewall.@rule[-1].dest='wan'
uci set firewall.@rule[-1].target='REJECT'

# Explicit blocks for isolated networks
uci add firewall rule
uci set firewall.@rule[-1].name='Block CCTV Internet'
uci set firewall.@rule[-1].src='cctv'
uci set firewall.@rule[-1].dest='wan'
uci set firewall.@rule[-1].target='REJECT'

uci add firewall rule
uci set firewall.@rule[-1].name='Block Storage Internet'
uci set firewall.@rule[-1].src='storage'
uci set firewall.@rule[-1].dest='wan'
uci set firewall.@rule[-1].target='REJECT'

uci add firewall rule
uci set firewall.@rule[-1].name='Block IoT Internet'
uci set firewall.@rule[-1].src='iot_sensors'
uci set firewall.@rule[-1].dest='wan'
uci set firewall.@rule[-1].target='REJECT'

echo "Internet access rules configured"

# ============================================================================
# INTER-VLAN COMMUNICATION RULES
# ============================================================================

echo "Configuring inter-VLAN communication rules..."

# Home Assistant access to CCTV network
uci add firewall rule
uci set firewall.@rule[-1].name='HA to CCTV Access'
uci set firewall.@rule[-1].src='automation'
uci set firewall.@rule[-1].src_ip='192.168.20.101'
uci set firewall.@rule[-1].dest='cctv'
uci set firewall.@rule[-1].target='ACCEPT'

# Home Assistant access to Storage network
uci add firewall rule
uci set firewall.@rule[-1].name='HA to Storage Access'
uci set firewall.@rule[-1].src='automation'
uci set firewall.@rule[-1].src_ip='192.168.20.101'
uci set firewall.@rule[-1].dest='storage'
uci set firewall.@rule[-1].target='ACCEPT'

# Home Assistant access to IoT Sensors network
uci add firewall rule
uci set firewall.@rule[-1].name='HA to IoT Sensors Access'
uci set firewall.@rule[-1].src='automation'
uci set firewall.@rule[-1].src_ip='192.168.20.101'
uci set firewall.@rule[-1].dest='iot_sensors'
uci set firewall.@rule[-1].target='ACCEPT'

# Frigate access to NAS for footage storage
uci add firewall rule
uci set firewall.@rule[-1].name='Frigate to NAS Access'
uci set firewall.@rule[-1].src='automation'
uci set firewall.@rule[-1].src_ip='192.168.20.102'
uci set firewall.@rule[-1].dest='storage'
uci set firewall.@rule[-1].dest_ip='192.168.40.50'
uci set firewall.@rule[-1].dest_port='22,445,2049'
uci set firewall.@rule[-1].proto='tcp'
uci set firewall.@rule[-1].target='ACCEPT'

# Management access to all networks (for administration)
uci add firewall rule
uci set firewall.@rule[-1].name='Management Full Access - Automation'
uci set firewall.@rule[-1].src='management'
uci set firewall.@rule[-1].dest='automation'
uci set firewall.@rule[-1].target='ACCEPT'

uci add firewall rule
uci set firewall.@rule[-1].name='Management Full Access - CCTV'
uci set firewall.@rule[-1].src='management'
uci set firewall.@rule[-1].dest='cctv'
uci set firewall.@rule[-1].target='ACCEPT'

uci add firewall rule
uci set firewall.@rule[-1].name='Management Full Access - Storage'
uci set firewall.@rule[-1].src='management'
uci set firewall.@rule[-1].dest='storage'
uci set firewall.@rule[-1].target='ACCEPT'

uci add firewall rule
uci set firewall.@rule[-1].name='Management Full Access - IoT'
uci set firewall.@rule[-1].src='management'
uci set firewall.@rule[-1].dest='iot_sensors'
uci set firewall.@rule[-1].target='ACCEPT'

echo "Inter-VLAN communication rules configured"

# ============================================================================
# SAFETY & SECURITY RULES
# ============================================================================

echo "Configuring safety and security rules..."

# Emergency: Allow IoT sensors to communicate with each other (sensor mesh)
uci add firewall rule
uci set firewall.@rule[-1].name='IoT Sensor Mesh Communication'
uci set firewall.@rule[-1].src='iot_sensors'
uci set firewall.@rule[-1].dest='iot_sensors'
uci set firewall.@rule[-1].target='ACCEPT'

# Block all other inter-VLAN communication by default
uci add firewall rule
uci set firewall.@rule[-1].name='Block CCTV to Automation'
uci set firewall.@rule[-1].src='cctv'
uci set firewall.@rule[-1].dest='automation'
uci set firewall.@rule[-1].target='REJECT'

uci add firewall rule
uci set firewall.@rule[-1].name='Block Storage to Automation'
uci set firewall.@rule[-1].src='storage'
uci set firewall.@rule[-1].dest='automation'
uci set firewall.@rule[-1].target='REJECT'

uci add firewall rule
uci set firewall.@rule[-1].name='Block IoT to Automation'
uci set firewall.@rule[-1].src='iot_sensors'
uci set firewall.@rule[-1].dest='automation'
uci set firewall.@rule[-1].target='REJECT'

echo "Safety and security rules configured"

# ============================================================================
# VPN ACCESS CONFIGURATION
# ============================================================================

echo "Configuring VPN access rules..."

# Allow WireGuard VPN traffic
uci add firewall rule
uci set firewall.@rule[-1].name='Allow WireGuard'
uci set firewall.@rule[-1].src='wan'
uci set firewall.@rule[-1].dest_port='51820'
uci set firewall.@rule[-1].proto='udp'
uci set firewall.@rule[-1].target='ACCEPT'

# VPN clients access to Home Assistant only
uci add firewall rule
uci set firewall.@rule[-1].name='VPN to Home Assistant'
uci set firewall.@rule[-1].src='vpn_clients'
uci set firewall.@rule[-1].dest='automation'
uci set firewall.@rule[-1].dest_ip='192.168.20.101'
uci set firewall.@rule[-1].dest_port='8123'
uci set firewall.@rule[-1].proto='tcp'
uci set firewall.@rule[-1].target='ACCEPT'

echo "VPN access rules configured"

# ============================================================================
# INTRUSION DETECTION & LOGGING
# ============================================================================

echo "Configuring logging and intrusion detection..."

# Log dropped packets for security monitoring
uci add firewall rule
uci set firewall.@rule[-1].name='Log Blocked CCTV Internet'
uci set firewall.@rule[-1].src='cctv'
uci set firewall.@rule[-1].dest='wan'
uci set firewall.@rule[-1].target='REJECT'
uci set firewall.@rule[-1].extra='-j LOG --log-prefix "CCTV-INET-BLOCK: " --log-level 4'

uci add firewall rule
uci set firewall.@rule[-1].name='Log Blocked IoT Internet'
uci set firewall.@rule[-1].src='iot_sensors'
uci set firewall.@rule[-1].dest='wan'
uci set firewall.@rule[-1].target='REJECT'
uci set firewall.@rule[-1].extra='-j LOG --log-prefix "IOT-INET-BLOCK: " --log-level 4'

echo "Logging rules configured"

# ============================================================================
# EMERGENCY PROTOCOLS
# ============================================================================

echo "Configuring emergency protocols..."

# Critical: Emergency access for fire safety override
# This rule allows admin direct access to smart plugs in emergency
uci add firewall rule
uci set firewall.@rule[-1].name='Emergency Smart Plug Access'
uci set firewall.@rule[-1].src='management'
uci set firewall.@rule[-1].src_ip='192.168.10.10'
uci set firewall.@rule[-1].dest='iot_sensors'
uci set firewall.@rule[-1].dest_ip='192.168.50.71'
uci set firewall.@rule[-1].dest_port='80,443'
uci set firewall.@rule[-1].proto='tcp'
uci set firewall.@rule[-1].target='ACCEPT'
uci set firewall.@rule[-1].enabled='0'  # Disabled by default, enable in emergency

uci add firewall rule
uci set firewall.@rule[-1].name='Emergency Smart Plug Access 2'
uci set firewall.@rule[-1].src='management'
uci set firewall.@rule[-1].src_ip='192.168.10.10'
uci set firewall.@rule[-1].dest='iot_sensors'
uci set firewall.@rule[-1].dest_ip='192.168.50.72'
uci set firewall.@rule[-1].dest_port='80,443'
uci set firewall.@rule[-1].proto='tcp'
uci set firewall.@rule[-1].target='ACCEPT'
uci set firewall.@rule[-1].enabled='0'

uci add firewall rule
uci set firewall.@rule[-1].name='Emergency Smart Plug Access 3'
uci set firewall.@rule[-1].src='management'
uci set firewall.@rule[-1].src_ip='192.168.10.10'
uci set firewall.@rule[-1].dest='iot_sensors'
uci set firewall.@rule[-1].dest_ip='192.168.50.73'
uci set firewall.@rule[-1].dest_port='80,443'
uci set firewall.@rule[-1].proto='tcp'
uci set firewall.@rule[-1].target='ACCEPT'
uci set firewall.@rule[-1].enabled='0'

echo "Emergency protocols configured (disabled by default)"

# ============================================================================
# ADDITIONAL SECURITY HARDENING
# ============================================================================

echo "Configuring additional security hardening..."

# Rate limiting for SSH access
uci add firewall rule
uci set firewall.@rule[-1].name='SSH Rate Limit'
uci set firewall.@rule[-1].src='wan'
uci set firewall.@rule[-1].dest_port='22'
uci set firewall.@rule[-1].proto='tcp'
uci set firewall.@rule[-1].extra='-m limit --limit 3/min --limit-burst 3'
uci set firewall.@rule[-1].target='ACCEPT'

# Block common attack ports
uci add firewall rule
uci set firewall.@rule[-1].name='Block Telnet'
uci set firewall.@rule[-1].src='wan'
uci set firewall.@rule[-1].dest_port='23'
uci set firewall.@rule[-1].proto='tcp'
uci set firewall.@rule[-1].target='REJECT'

uci add firewall rule
uci set firewall.@rule[-1].name='Block FTP'
uci set firewall.@rule[-1].src='wan'
uci set firewall.@rule[-1].dest_port='21'
uci set firewall.@rule[-1].proto='tcp'
uci set firewall.@rule[-1].target='REJECT'

# Allow ping for network diagnostics
uci add firewall rule
uci set firewall.@rule[-1].name='Allow Ping'
uci set firewall.@rule[-1].src='wan'
uci set firewall.@rule[-1].proto='icmp'
uci set firewall.@rule[-1].icmp_type='echo-request'
uci set firewall.@rule[-1].target='ACCEPT'
uci set firewall.@rule[-1].limit='1000/sec'

echo "Security hardening configured"

# ============================================================================
# APPLY CONFIGURATION
# ============================================================================

echo "Applying firewall configuration..."

# Commit all firewall changes
uci commit firewall

# Validate configuration before restart
if ! uci show firewall > /dev/null 2>&1; then
    echo "ERROR: Invalid UCI configuration detected. Restoring backup..."
    # Restore backup if available
    if [ -f "/etc/config/firewall.backup.*" ]; then
        cp /etc/config/firewall.backup.* /etc/config/firewall
        echo "Configuration restored from backup"
    fi
    exit 1
fi

# Restart firewall service
echo "Restarting firewall service..."
/etc/init.d/firewall restart

# Verify firewall is running
if /etc/init.d/firewall status > /dev/null 2>&1; then
    echo "✅ Firewall configuration applied successfully!"
else
    echo "❌ ERROR: Firewall failed to start properly"
    exit 1
fi

# ============================================================================
# POST-CONFIGURATION VERIFICATION
# ============================================================================

echo ""
echo "============================================================================"
echo "FIREWALL CONFIGURATION COMPLETE"
echo "============================================================================"
echo ""
echo "✅ 4-VLAN security architecture implemented:"
echo "   - VLAN 10 (Management): 192.168.10.0/24 - Full internet access"
echo "   - VLAN 20 (Automation): 192.168.20.0/24 - Limited internet access"  
echo "   - VLAN 30 (CCTV): 192.168.30.0/24 - No internet, HA bridge only"
echo "   - VLAN 40 (Storage): 192.168.40.0/24 - No internet, Frigate access"
echo "   - VLAN 50 (IoT): 192.168.50.0/24 - No internet, HA control only"
echo ""
echo "🔐 Security features enabled:"
echo "   - Network segmentation and isolation"
echo "   - SSH rate limiting"
echo "   - Attack port blocking"
echo "   - Comprehensive logging"
echo "   - Emergency access protocols (disabled)"
echo ""
echo "⚠️  CRITICAL POST-DEPLOYMENT TASKS:"
echo "   1. Verify Home Assistant can communicate with all VLANs"
echo "   2. Test emergency smart plug cutoff functionality"
echo "   3. Confirm isolated networks cannot access internet"
echo "   4. Validate VPN access to Home Assistant only"
echo "   5. Monitor logs for blocked connection attempts"
echo ""
echo "📝 Configuration files:"
echo "   - Active: /etc/config/firewall"
echo "   - Backup: /etc/config/firewall.backup.*"
echo ""
echo "🚨 Emergency procedures:"
echo "   - To enable emergency smart plug access:"
echo "     uci set firewall.@rule[N].enabled='1' && uci commit && /etc/init.d/firewall restart"
echo "   - To restore from backup:"
echo "     cp /etc/config/firewall.backup.* /etc/config/firewall && /etc/init.d/firewall restart"
echo ""
echo "Configuration completed at: $(date)"
echo "============================================================================"