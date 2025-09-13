# OpenWrt Firewall Configuration for Home Automation Safety System
# Router: GL.iNet GL-MT6000 with OpenWrt

# ============================================================================
# NETWORK ZONES CONFIGURATION
# ============================================================================

# Zone: WAN (Internet)
uci set firewall.@zone[0]=zone
uci set firewall.@zone[0].name='wan'
uci set firewall.@zone[0].input='REJECT'
uci set firewall.@zone[0].output='ACCEPT'
uci set firewall.@zone[0].forward='REJECT'
uci set firewall.@zone[0].masq='1'
uci set firewall.@zone[0].mtu_fix='1'
uci add_list firewall.@zone[0].network='wan'
uci add_list firewall.@zone[0].network='wan6'

# Zone: MANAGEMENT (VLAN 10) - Full Internet Access
uci add firewall zone
uci set firewall.@zone[-1].name='management'
uci set firewall.@zone[-1].input='ACCEPT'
uci set firewall.@zone[-1].output='ACCEPT'
uci set firewall.@zone[-1].forward='ACCEPT'
uci add_list firewall.@zone[-1].network='management'

# Zone: AUTOMATION (VLAN 20) - Controlled Internet Access
uci add firewall zone
uci set firewall.@zone[-1].name='automation'
uci set firewall.@zone[-1].input='ACCEPT'
uci set firewall.@zone[-1].output='ACCEPT'
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

# ============================================================================
# INTERNET ACCESS RULES
# ============================================================================

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

# Block all other automation devices from internet
uci add firewall rule
uci set firewall.@rule[-1].name='Block Other Automation Internet'
uci set firewall.@rule[-1].src='automation'
uci set firewall.@rule[-1].dest='wan'
uci set firewall.@rule[-1].target='REJECT'

# ============================================================================
# INTER-VLAN COMMUNICATION RULES
# ============================================================================

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
uci set firewall.@rule[-1].name='Management Full Access'
uci set firewall.@rule[-1].src='management'
uci set firewall.@rule[-1].dest='automation'
uci set firewall.@rule[-1].target='ACCEPT'

uci add firewall rule
uci set firewall.@rule[-1].name='Management to CCTV'
uci set firewall.@rule[-1].src='management'
uci set firewall.@rule[-1].dest='cctv'
uci set firewall.@rule[-1].target='ACCEPT'

uci add firewall rule
uci set firewall.@rule[-1].name='Management to Storage'
uci set firewall.@rule[-1].src='management'
uci set firewall.@rule[-1].dest='storage'
uci set firewall.@rule[-1].target='ACCEPT'

uci add firewall rule
uci set firewall.@rule[-1].name='Management to IoT'
uci set firewall.@rule[-1].src='management'
uci set firewall.@rule[-1].dest='iot_sensors'
uci set firewall.@rule[-1].target='ACCEPT'

# ============================================================================
# SAFETY & SECURITY RULES
# ============================================================================

# Emergency: Allow IoT sensors to communicate with each other (sensor mesh)
uci add firewall rule
uci set firewall.@rule[-1].name='IoT Sensor Mesh Communication'
uci set firewall.@rule[-1].src='iot_sensors'
uci set firewall.@rule[-1].dest='iot_sensors'
uci set firewall.@rule[-1].target='ACCEPT'

# Block all other inter-VLAN communication by default
uci add firewall rule
uci set firewall.@rule[-1].name='Block CCTV to Others'
uci set firewall.@rule[-1].src='cctv'
uci set firewall.@rule[-1].dest='automation'
uci set firewall.@rule[-1].target='REJECT'

uci add firewall rule
uci set firewall.@rule[-1].name='Block Storage to Others'
uci set firewall.@rule[-1].src='storage'
uci set firewall.@rule[-1].dest='automation'
uci set firewall.@rule[-1].target='REJECT'

uci add firewall rule
uci set firewall.@rule[-1].name='Block IoT to Others'
uci set firewall.@rule[-1].src='iot_sensors'
uci set firewall.@rule[-1].dest='automation'
uci set firewall.@rule[-1].target='REJECT'

# ============================================================================
# VPN ACCESS CONFIGURATION
# ============================================================================

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

# ============================================================================
# INTRUSION DETECTION & LOGGING
# ============================================================================

# Log dropped packets for security monitoring
uci add firewall rule
uci set firewall.@rule[-1].name='Log Blocked Internet Attempts'
uci set firewall.@rule[-1].src='cctv'
uci set firewall.@rule[-1].dest='wan'
uci set firewall.@rule[-1].target='REJECT'
uci set firewall.@rule[-1].extra='-j LOG --log-prefix "CCTV-INET-BLOCK: "'

uci add firewall rule
uci set firewall.@rule[-1].name='Log Blocked IoT Internet'
uci set firewall.@rule[-1].src='iot_sensors'
uci set firewall.@rule[-1].dest='wan'
uci set firewall.@rule[-1].target='REJECT'
uci set firewall.@rule[-1].extra='-j LOG --log-prefix "IOT-INET-BLOCK: "'

# ============================================================================
# EMERGENCY PROTOCOLS
# ============================================================================

# Critical: Emergency access for fire safety override
# This rule allows admin direct access to smart plugs in emergency
uci add firewall rule
uci set firewall.@rule[-1].name='Emergency Smart Plug Access'
uci set firewall.@rule[-1].src='automation_mgmt'
uci set firewall.@rule[-1].src_ip='192.168.20.10'
uci set firewall.@rule[-1].dest='iot_sensors'
uci set firewall.@rule[-1].dest_ip='192.168.50.71,192.168.50.72,192.168.50.73'
uci set firewall.@rule[-1].target='ACCEPT'
uci set firewall.@rule[-1].enabled='0'  # Disabled by default, enable in emergency

# ============================================================================
# ADDITIONAL SECURITY HARDENING
# ============================================================================

# Rate limiting for SSH access
uci add firewall rule
uci set firewall.@rule[-1].name='SSH Rate Limit'
uci set firewall.@rule[-1].src='wan'
uci set firewall.@rule[-1].dest_port='22'
uci set firewall.@rule[-1].proto='tcp'
uci set firewall.@rule[-1].extra='--limit 3/min --limit-burst 3'
uci set firewall.@rule[-1].target='ACCEPT'

# Block common attack ports
uci add firewall rule
uci set firewall.@rule[-1].name='Block Telnet'
uci set firewall.@rule[-1].src='wan'
uci set firewall.@rule[-1].dest_port='23'
uci set firewall.@rule[-1].proto='tcp'
uci set firewall.@rule[-1].target='REJECT'

# ============================================================================
# APPLY CONFIGURATION
# ============================================================================

# Commit all firewall changes
uci commit firewall

# Restart firewall service
/etc/init.d/firewall restart

echo "Firewall configuration applied successfully!"
echo "CRITICAL: Verify all safety systems can communicate with Home Assistant"
echo "CRITICAL: Test emergency smart plug cutoff functionality"
echo "Security: Verify isolated networks cannot access internet"