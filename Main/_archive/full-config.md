
#!/bin/bash
################################################################################
# OpenWrt Router Complete Deployment Script - All 8 Phases
# GL.iNet GL-MT6000 Configuration
# 
# WARNING: This script will reconfigure your entire network
# Execute sections manually with verification checkpoints
#
# Port Configuration:
#   - WAN (2.5Gb): Internet
#   - lan5 (1Gb): Admin/Rescue - VLAN 1 untagged (192.168.1.1)
#   - lan1 (2.5Gb): Proxmox trunk - Tagged VLANs
#   - lan4 (1Gb): Storage/NAS - VLAN 40 untagged
#   - lan2 (1Gb): Management - VLAN 10 untagged
#   - lan3 (1Gb): CCTV - VLAN 30 untagged
################################################################################

set -e  # Exit on error

################################################################################
# PHASE 1: Prerequisites and Baseline Setup
################################################################################

echo "==================================="
echo "PHASE 1: Prerequisites and Baseline"
echo "==================================="

# 1.1 System Assessment and Backup
echo "Creating baseline backup..."
uname -a > /tmp/system_baseline.txt
cat /etc/openwrt_release >> /tmp/system_baseline.txt
df -h >> /tmp/system_baseline.txt

mkdir -p /etc/config/backups/baseline
cp /etc/config/* /etc/config/backups/baseline/
tar -czf /tmp/factory_baseline_$(date +%Y%m%d_%H%M%S).tar.gz -C /etc/config/backups baseline/
free -h

# 1.2 Package Installation
echo "Installing required packages..."
opkg update
opkg install wireguard-tools
opkg install kmod-wireguard 
opkg install luci-proto-wireguard
opkg install tcpdump
opkg install iperf3
opkg install ethtool

# Verify installations
opkg list-installed | grep -E "(wireguard|tcpdump|iperf|ethtool)"
lsmod | grep wireguard

# 1.3 Hardware Interface Verification
echo "Verifying hardware interfaces..."
ip link show > /tmp/interface_baseline.txt

for iface in wan lan1 lan2 lan3 lan4 lan5; do
    if ip link show "$iface" >/dev/null 2>&1; then
        echo "✓ $iface exists"
    else
        echo "✗ $iface missing"
    fi
done

iw dev >> /tmp/interface_baseline.txt

# 1.4 WireGuard Key Generation
echo "Generating WireGuard keys..."
mkdir -p /etc/wireguard/keys
chmod 700 /etc/wireguard/keys

wg genkey | tee /etc/wireguard/keys/server_private.key | wg pubkey > /etc/wireguard/keys/server_public.key

for i in 1 2 3; do
    wg genkey | tee /etc/wireguard/keys/client${i}_private.key | wg pubkey > /etc/wireguard/keys/client${i}_public.key
done

chmod 600 /etc/wireguard/keys/*_private.key
chmod 644 /etc/wireguard/keys/*_public.key

echo "=== WireGuard Keys Generated ===" > /tmp/wireguard_keys.txt
echo "Server Public Key: $(cat /etc/wireguard/keys/server_public.key)" >> /tmp/wireguard_keys.txt
for i in 1 2 3; do
    echo "Client $i Public Key: $(cat /etc/wireguard/keys/client${i}_public.key)" >> /tmp/wireguard_keys.txt
done

# 1.5 WiFi Password Generation
echo "Generating WiFi passwords..."
mkdir -p /etc/wireless/credentials

openssl rand -base64 32 | tr -d "=+/" | cut -c1-24 > /etc/wireless/credentials/main_password.txt
openssl rand -base64 32 | tr -d "=+/" | cut -c1-24 > /etc/wireless/credentials/admin_password.txt
openssl rand -base64 32 | tr -d "=+/" | cut -c1-24 > /etc/wireless/credentials/iot_password.txt
openssl rand -base64 32 | tr -d "=+/" | cut -c1-24 > /etc/wireless/credentials/guest_password.txt
openssl rand -base64 32 | tr -d "=+/" | cut -c1-24 > /etc/wireless/credentials/dmz_password.txt

chmod 600 /etc/wireless/credentials/*.txt

echo "=== WiFi Credentials Generated ===" > /tmp/wifi_credentials.txt
echo "HomeMain: $(cat /etc/wireless/credentials/main_password.txt)" >> /tmp/wifi_credentials.txt
echo "HomeAdmin: $(cat /etc/wireless/credentials/admin_password.txt)" >> /tmp/wifi_credentials.txt
echo "HomeIoT: $(cat /etc/wireless/credentials/iot_password.txt)" >> /tmp/wifi_credentials.txt
echo "HomeGuest: $(cat /etc/wireless/credentials/guest_password.txt)" >> /tmp/wifi_credentials.txt
echo "HomeDMZ: $(cat /etc/wireless/credentials/dmz_password.txt)" >> /tmp/wifi_credentials.txt

# 1.6 Network Performance Baseline
echo "Establishing network baseline..."
mkdir -p /tmp/baselines

ping -c 10 8.8.8.8 > /tmp/baselines/wan_connectivity.txt
nslookup google.com >> /tmp/baselines/wan_connectivity.txt

for iface in wan lan1 lan2 lan3 lan4 lan5; do
    if ip link show "$iface" >/dev/null 2>&1; then
        echo "=== $iface Statistics ===" >> /tmp/baselines/interface_stats.txt
        ethtool "$iface" 2>/dev/null >> /tmp/baselines/interface_stats.txt || echo "ethtool not available for $iface" >> /tmp/baselines/interface_stats.txt
    fi
done

# 1.7 Configuration Management Setup
echo "Setting up configuration management..."
mkdir -p /etc/config/backups/{phases,emergency}
mkdir -p /tmp/deployment_logs

mkdir -p /usr/local/
mkdir -p /usr/local/bin
chmod 750 /usr/local/
chmod 750 /usr/local/bin/

cat > /usr/local/bin/backup_phase.sh << 'EOF'
#!/bin/sh
PHASE=$1
if [ -z "$PHASE" ]; then
    echo "Usage: backup_phase.sh <phase_number>"
    exit 1
fi

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/etc/config/backups/phases/phase_${PHASE}_${TIMESTAMP}"
mkdir -p "$BACKUP_DIR"

cp /etc/config/* "$BACKUP_DIR/"
uci export > "$BACKUP_DIR/uci_export.txt"

echo "Phase $PHASE backup created: $BACKUP_DIR"
EOF

chmod +x /usr/local/bin/backup_phase.sh

cat > /usr/local/bin/emergency_restore.sh << 'EOF'
#!/bin/sh
echo "WARNING: This will restore factory configuration"
echo "Press Ctrl+C to cancel, or wait 10 seconds to continue..."
sleep 10

if [ -d "/etc/config/backups/baseline" ]; then
    cp /etc/config/backups/baseline/* /etc/config/
    echo "Factory configuration restored"
    echo "Restarting network services..."
    /etc/init.d/network restart
    /etc/init.d/firewall restart
    /etc/init.d/dnsmasq restart
else
    echo "ERROR: No baseline backup found"
    exit 1
fi
EOF

##### DON'T RUN CHMOD BEFORE FINISHING CAT -> EOF ######

chmod +x /usr/local/bin/emergency_restore.sh

/usr/local/bin/backup_phase.sh 0_baseline

echo "✓ PHASE 1 COMPLETE"
echo ""
echo "Press Enter to continue to Phase 2..."
read

################################################################################
# PHASE 2: Network Infrastructure (VLAN Configuration)
################################################################################

echo "==================================="
echo "PHASE 2: Network Infrastructure"
echo "==================================="
echo "WARNING: This phase has multiple checkpoints"
echo "You will be prompted to verify connectivity after each step"
echo ""

# Checkpoint 0: Establish Rescue Port
echo "=== CHECKPOINT 0: Establishing Rescue Port lan5 ==="
/usr/local/bin/backup_phase.sh 2_entry

ip link show > /tmp/phase2_checkpoint0_entry.txt
ip addr show >> /tmp/phase2_checkpoint0_entry.txt
uci show network >> /tmp/phase2_checkpoint0_entry.txt

ip link show lan5

uci set network.lan.device='br-lan'
uci set network.lan.proto='static'
uci set network.lan.ipaddr='192.168.1.1'
uci set network.lan.netmask='255.255.255.0'
uci commit network

/etc/init.d/network restart
echo "Waiting 30 seconds..."
sleep 30

echo ""
echo "VERIFY CHECKPOINT 0:"
echo "1. Can you ping 192.168.1.1?"
echo "2. Can you SSH to the router?"
echo "Press Enter when verified..."
read

/usr/local/bin/backup_phase.sh 2_checkpoint0

# Checkpoint 1: DSA Bridge Base
echo "=== CHECKPOINT 1: Creating DSA Bridge ==="

uci delete network.@device[0] 2>/dev/null || true

uci add network device
uci set network.@device[-1].name='br-lan'
uci set network.@device[-1].type='bridge'

uci add_list network.@device[-1].ports='lan1'
uci add_list network.@device[-1].ports='lan2'
uci add_list network.@device[-1].ports='lan3'
uci add_list network.@device[-1].ports='lan4'
uci add_list network.@device[-1].ports='lan5'

uci set network.@device[-1].igmp_snooping='1'
uci set network.@device[-1].stp='1'
uci set network.@device[-1].stp_hello_time='2'
uci set network.@device[-1].stp_forward_delay='15'

uci commit network

echo "WARNING: Network will restart"
/etc/init.d/network restart
echo "Waiting 30 seconds..."
sleep 30

echo ""
echo "VERIFY CHECKPOINT 1:"
echo "1. Can you ping 192.168.1.1?"
echo "2. Run: brctl show br-lan (should show all 5 ports)"
echo "Press Enter when verified..."
read

/usr/local/bin/backup_phase.sh 2_checkpoint1

# Checkpoint 2: VLAN 1
echo "=== CHECKPOINT 2: Adding VLAN 1 (Rescue Port) ==="

echo "=== CHECKPOINT 2: Configuring VLAN 1 for Rescue Port ===" | tee -a /tmp/deployment_logs/phase2.log

# VLAN 1: Default/Rescue Network
uci add network bridge-vlan
uci set network.@bridge-vlan[-1].device='br-lan'
uci set network.@bridge-vlan[-1].vlan='1'
uci set network.@bridge-vlan[-1].local='1'

# lan5 MUST be untagged on VLAN 1 (rescue port)
uci add_list network.@bridge-vlan[-1].ports='lan5:u*'

# Other ports get VLAN 1 tagged temporarily
uci add_list network.@bridge-vlan[-1].ports='lan1:t'
uci add_list network.@bridge-vlan[-1].ports='lan2:t'
uci add_list network.@bridge-vlan[-1].ports='lan3:t'
uci add_list network.@bridge-vlan[-1].ports='lan4:t'

# Bind the LAN interface itself to br-lan.1 so the router stays reachable
uci set network.lan.device='br-lan.1'
uci set network.lan.proto='static'
uci set network.lan.ipaddr='192.168.1.1'
uci set network.lan.netmask='255.255.255.0'

uci commit network

echo "VLAN 1 configured with lan5 as untagged rescue port" >> /tmp/deployment_logs/phase2.log

# Apply changes
/etc/init.d/network restart
sleep 30

echo ""
echo "VERIFY CHECKPOINT 2:"
echo "1. Can you ping 192.168.1.1?"
echo "2. Run: bridge vlan show dev lan5"
echo "Press Enter when verified..."
read

/usr/local/bin/backup_phase.sh 2_checkpoint2

# Checkpoint 3A: VLAN 10
echo "=== CHECKPOINT 3A: Adding VLAN 10 (Management) ==="

uci add network bridge-vlan
uci set network.@bridge-vlan[-1].device='br-lan'
uci set network.@bridge-vlan[-1].vlan='10'
uci set network.@bridge-vlan[-1].local='1'
uci add_list network.@bridge-vlan[-1].ports='lan1:t'
uci add_list network.@bridge-vlan[-1].ports='lan2:u*'
uci add_list network.@bridge-vlan[-1].ports='lan3:t'
uci add_list network.@bridge-vlan[-1].ports='lan4:t'

uci commit network
/etc/init.d/network restart
sleep 30

echo "VERIFY: Can you still ping 192.168.1.1? Press Enter..."
read
/usr/local/bin/backup_phase.sh 2_checkpoint3a

# Checkpoint 3B: VLAN 20
echo "=== CHECKPOINT 3B: Adding VLAN 20 (Automation) ==="

uci add network bridge-vlan
uci set network.@bridge-vlan[-1].device='br-lan'
uci set network.@bridge-vlan[-1].vlan='20'
uci set network.@bridge-vlan[-1].local='1'
uci add_list network.@bridge-vlan[-1].ports='lan1:t'

uci commit network
/etc/init.d/network restart
sleep 30

echo "VERIFY: Can you still ping 192.168.1.1? Press Enter..."
read
/usr/local/bin/backup_phase.sh 2_checkpoint3b

# Checkpoint 3C: VLAN 30
echo "=== CHECKPOINT 3C: Adding VLAN 30 (CCTV) ==="

uci add network bridge-vlan
uci set network.@bridge-vlan[-1].device='br-lan'
uci set network.@bridge-vlan[-1].vlan='30'
uci set network.@bridge-vlan[-1].local='1'
uci add_list network.@bridge-vlan[-1].ports='lan1:t'
uci add_list network.@bridge-vlan[-1].ports='lan3:u*'

uci commit network
/etc/init.d/network restart
sleep 30

echo "VERIFY: Can you still ping 192.168.1.1? Press Enter..."
read
/usr/local/bin/backup_phase.sh 2_checkpoint3c

# Checkpoint 3D: VLAN 40
echo "=== CHECKPOINT 3D: Adding VLAN 40 (Storage) ==="

uci add network bridge-vlan
uci set network.@bridge-vlan[-1].device='br-lan'
uci set network.@bridge-vlan[-1].vlan='40'
uci set network.@bridge-vlan[-1].local='1'
uci add_list network.@bridge-vlan[-1].ports='lan1:t'
uci add_list network.@bridge-vlan[-1].ports='lan4:u*'

uci commit network
/etc/init.d/network restart
sleep 30

echo "VERIFY: Can you still ping 192.168.1.1? Press Enter..."
read
/usr/local/bin/backup_phase.sh 2_checkpoint3d

# Checkpoint 3E: VLAN 50
echo "=== CHECKPOINT 3E: Adding VLAN 50 (IoT Sensors) ==="

uci add network bridge-vlan
uci set network.@bridge-vlan[-1].device='br-lan'
uci set network.@bridge-vlan[-1].vlan='50'
uci set network.@bridge-vlan[-1].local='1'
uci add_list network.@bridge-vlan[-1].ports='lan1:t'

uci commit network
/etc/init.d/network restart
sleep 30

echo "VERIFY: Can you still ping 192.168.1.1? Press Enter..."
read
/usr/local/bin/backup_phase.sh 2_checkpoint3e

# Checkpoint 3F: VLANs 60, 70, 99
echo "=== CHECKPOINT 3F: Adding VLANs 60, 70, 99 ==="

uci add network bridge-vlan
uci set network.@bridge-vlan[-1].device='br-lan'
uci set network.@bridge-vlan[-1].vlan='60'
uci set network.@bridge-vlan[-1].local='1'
uci add_list network.@bridge-vlan[-1].ports='lan1:t'

uci add network bridge-vlan
uci set network.@bridge-vlan[-1].device='br-lan'
uci set network.@bridge-vlan[-1].vlan='70'
uci set network.@bridge-vlan[-1].local='1'
uci add_list network.@bridge-vlan[-1].ports='lan1:t'

uci add network bridge-vlan
uci set network.@bridge-vlan[-1].device='br-lan'
uci set network.@bridge-vlan[-1].vlan='99'
uci set network.@bridge-vlan[-1].local='1'

uci commit network
/etc/init.d/network restart
sleep 30

echo "VERIFY: Can you still ping 192.168.1.1? Press Enter..."
read
/usr/local/bin/backup_phase.sh 2_checkpoint3f

# Checkpoint 4: Logical Interfaces
echo "=== CHECKPOINT 4: Creating Logical Interfaces ==="

uci set network.management=interface
uci set network.management.proto='static'
uci set network.management.device='br-lan.10'
uci set network.management.ipaddr='192.168.10.1'
uci set network.management.netmask='255.255.255.0'

uci set network.automation=interface
uci set network.automation.proto='static'
uci set network.automation.device='br-lan.20'
uci set network.automation.ipaddr='192.168.20.1'
uci set network.automation.netmask='255.255.255.0'

uci set network.cctv=interface
uci set network.cctv.proto='static'
uci set network.cctv.device='br-lan.30'
uci set network.cctv.ipaddr='192.168.30.1'
uci set network.cctv.netmask='255.255.255.0'

uci set network.storage=interface
uci set network.storage.proto='static'
uci set network.storage.device='br-lan.40'
uci set network.storage.ipaddr='192.168.40.1'
uci set network.storage.netmask='255.255.255.0'

uci set network.iot_sensors=interface
uci set network.iot_sensors.proto='static'
uci set network.iot_sensors.device='br-lan.50'
uci set network.iot_sensors.ipaddr='192.168.50.1'
uci set network.iot_sensors.netmask='255.255.255.0'

uci set network.monitoring=interface
uci set network.monitoring.proto='static'
uci set network.monitoring.device='br-lan.60'
uci set network.monitoring.ipaddr='192.168.60.1'
uci set network.monitoring.netmask='255.255.255.0'

uci set network.dmz=interface
uci set network.dmz.proto='static'
uci set network.dmz.device='br-lan.70'
uci set network.dmz.ipaddr='192.168.70.1'
uci set network.dmz.netmask='255.255.255.0'

uci set network.guest=interface
uci set network.guest.proto='static'
uci set network.guest.device='br-lan.99'
uci set network.guest.ipaddr='192.168.99.1'
uci set network.guest.netmask='255.255.255.0'

uci commit network
/etc/init.d/network restart
sleep 30

echo ""
echo "VERIFY CHECKPOINT 4:"
echo "1. Can you ping 192.168.1.1?"
echo "2. Run: ip addr show | grep br-lan"
echo "3. Try pinging: 192.168.10.1, 192.168.20.1, etc."
echo "Press Enter when verified..."
read

/usr/local/bin/backup_phase.sh 2_checkpoint4

# Checkpoint 5: WAN Config
echo "=== CHECKPOINT 5: WAN Configuration ==="

uci set network.wan.proto='dhcp'
uci set network.wan.peerdns='0'
uci delete network.wan.dns 2>/dev/null || true
uci add_list network.wan.dns='1.1.1.1'
uci add_list network.wan.dns='1.0.0.1'

uci set network.wan6.proto='dhcpv6'
uci set network.wan6.reqaddress='try'
uci set network.wan6.reqprefix='auto'

uci commit network
/etc/init.d/network restart
sleep 30

echo "VERIFY: Can you ping 8.8.8.8 (internet)? Press Enter..."
read

echo "✓ PHASE 2 COMPLETE"
/usr/local/bin/backup_phase.sh 2_complete

echo ""
echo "Press Enter to continue to Phase 3..."
read

################################################################################
# PHASE 3: DHCP Configuration
################################################################################

echo "==================================="
echo "PHASE 3: DHCP Configuration"
echo "==================================="

/usr/local/bin/backup_phase.sh 3_entry

# Global DHCP Settings
uci set dhcp.@dnsmasq[0].domainneeded='1'
uci set dhcp.@dnsmasq[0].boguspriv='1'
uci set dhcp.@dnsmasq[0].filterwin2k='0'
uci set dhcp.@dnsmasq[0].localise_queries='1'
uci set dhcp.@dnsmasq[0].rebind_protection='1'
uci set dhcp.@dnsmasq[0].rebind_localhost='1'
uci set dhcp.@dnsmasq[0].local='/home.local/'
uci set dhcp.@dnsmasq[0].domain='home.local'
uci set dhcp.@dnsmasq[0].expandhosts='1'
uci set dhcp.@dnsmasq[0].nonegcache='0'
uci set dhcp.@dnsmasq[0].cachesize='1000'
uci set dhcp.@dnsmasq[0].authoritative='1'
uci set dhcp.@dnsmasq[0].readethers='1'
uci set dhcp.@dnsmasq[0].leasefile='/tmp/dhcp.leases'
uci set dhcp.@dnsmasq[0].resolvfile='/tmp/resolv.conf.d/resolv.conf.auto'

uci delete dhcp.@dnsmasq[0].server 2>/dev/null || true
uci add_list dhcp.@dnsmasq[0].server='1.1.1.1'
uci add_list dhcp.@dnsmasq[0].server='1.0.0.1'
uci add_list dhcp.@dnsmasq[0].server='8.8.8.8'

# VLAN 1 - LAN
uci set dhcp.lan.interface='lan'
uci set dhcp.lan.start='100'
uci set dhcp.lan.limit='100'
uci set dhcp.lan.leasetime='12h'
uci set dhcp.lan.dhcpv4='server'
uci set dhcp.lan.dhcpv6='server'
uci set dhcp.lan.ra='server'
uci set dhcp.lan.ra_slaac='1'
uci add_list dhcp.lan.ra_flags='managed-config'
uci add_list dhcp.lan.ra_flags='other-config'
uci delete dhcp.lan.dhcp_option 2>/dev/null || true
uci add_list dhcp.lan.dhcp_option='6,192.168.1.1,1.1.1.1,1.0.0.1'

# VLAN 10 - Management
uci set dhcp.management=dhcp
uci set dhcp.management.interface='management'
uci set dhcp.management.start='100'
uci set dhcp.management.limit='50'
uci set dhcp.management.leasetime='24h'
uci set dhcp.management.dhcpv4='server'
uci add_list dhcp.management.dhcp_option='6,192.168.10.1,1.1.1.1'

# VLAN 20 - Automation
uci set dhcp.automation=dhcp
uci set dhcp.automation.interface='automation'
uci set dhcp.automation.start='110'
uci set dhcp.automation.limit='40'
uci set dhcp.automation.leasetime='24h'
uci set dhcp.automation.dhcpv4='server'
uci add_list dhcp.automation.dhcp_option='6,192.168.20.1'

# VLAN 30 - CCTV
uci set dhcp.cctv=dhcp
uci set dhcp.cctv.interface='cctv'
uci set dhcp.cctv.start='100'
uci set dhcp.cctv.limit='50'
uci set dhcp.cctv.leasetime='24h'
uci set dhcp.cctv.dhcpv4='server'
uci add_list dhcp.cctv.dhcp_option='6,192.168.30.1'

# VLAN 40 - Storage
uci set dhcp.storage=dhcp
uci set dhcp.storage.interface='storage'
uci set dhcp.storage.start='100'
uci set dhcp.storage.limit='40'
uci set dhcp.storage.leasetime='24h'
uci set dhcp.storage.dhcpv4='server'
uci add_list dhcp.storage.dhcp_option='6,192.168.40.1'

# VLAN 50 - IoT Sensors
uci set dhcp.iot_sensors=dhcp
uci set dhcp.iot_sensors.interface='iot_sensors'
uci set dhcp.iot_sensors.start='100'
uci set dhcp.iot_sensors.limit='91'
uci set dhcp.iot_sensors.leasetime='6h'
uci set dhcp.iot_sensors.dhcpv4='server'
uci add_list dhcp.iot_sensors.dhcp_option='6,192.168.50.1'

# VLAN 60 - Monitoring
uci set dhcp.monitoring=dhcp
uci set dhcp.monitoring.interface='monitoring'
uci set dhcp.monitoring.start='100'
uci set dhcp.monitoring.limit='50'
uci set dhcp.monitoring.leasetime='24h'
uci set dhcp.monitoring.dhcpv4='server'
uci add_list dhcp.monitoring.dhcp_option='6,192.168.60.1,1.1.1.1'

# VLAN 70 - DMZ
uci set dhcp.dmz=dhcp
uci set dhcp.dmz.interface='dmz'
uci set dhcp.dmz.start='100'
uci set dhcp.dmz.limit='50'
uci set dhcp.dmz.leasetime='12h'
uci set dhcp.dmz.dhcpv4='server'
uci add_list dhcp.dmz.dhcp_option='6,192.168.70.1,1.1.1.1,8.8.8.8'

# VLAN 99 - Guest
uci set dhcp.guest=dhcp
uci set dhcp.guest.interface='guest'
uci set dhcp.guest.start='100'
uci set dhcp.guest.limit='51'
uci set dhcp.guest.leasetime='2h'
uci set dhcp.guest.dhcpv4='server'
uci add_list dhcp.guest.dhcp_option='6,1.1.1.1,8.8.8.8'

# Static Reservations (Placeholders)
uci add dhcp host
uci set dhcp.@host[-1].name='proxmox-host'
uci set dhcp.@host[-1].dns='1'
uci set dhcp.@host[-1].mac='XX:XX:XX:XX:XX:01'
uci set dhcp.@host[-1].ip='192.168.10.10'

uci add dhcp host
uci set dhcp.@host[-1].name='home-assistant'
uci set dhcp.@host[-1].dns='1'
uci set dhcp.@host[-1].mac='XX:XX:XX:XX:XX:02'
uci set dhcp.@host[-1].ip='192.168.20.101'

uci add dhcp host
uci set dhcp.@host[-1].name='frigate-nvr'
uci set dhcp.@host[-1].dns='1'
uci set dhcp.@host[-1].mac='XX:XX:XX:XX:XX:03'
uci set dhcp.@host[-1].ip='192.168.30.20'

uci add dhcp host
uci set dhcp.@host[-1].name='pi-nas'
uci set dhcp.@host[-1].dns='1'
uci set dhcp.@host[-1].mac='XX:XX:XX:XX:XX:04'
uci set dhcp.@host[-1].ip='192.168.40.50'

uci add dhcp host
uci set dhcp.@host[-1].name='ventsys-fan-controller'
uci set dhcp.@host[-1].ip='192.168.50.21'
uci set dhcp.@host[-1].mac='XX:XX:XX:XX:XX:81'

uci add dhcp host
uci set dhcp.@host[-1].name='ventsys-valve-controller'
uci set dhcp.@host[-1].ip='192.168.50.56'
uci set dhcp.@host[-1].mac='XX:XX:XX:XX:XX:82'

# Local Domains
uci add dhcp domain
uci set dhcp.@domain[-1].name='router.home.local'
uci set dhcp.@domain[-1].ip='192.168.1.1'

uci add dhcp domain
uci set dhcp.@domain[-1].name='proxmox.home.local'
uci set dhcp.@domain[-1].ip='192.168.10.10'

uci add dhcp domain
uci set dhcp.@domain[-1].name='homeassistant.home.local'
uci set dhcp.@domain[-1].ip='192.168.20.101'

uci add dhcp domain
uci set dhcp.@domain[-1].name='frigate.home.local'
uci set dhcp.@domain[-1].ip='192.168.30.20'

uci add dhcp domain
uci set dhcp.@domain[-1].name='nas.home.local'
uci set dhcp.@domain[-1].ip='192.168.40.50'

uci commit dhcp
/etc/init.d/dnsmasq restart
sleep 5

echo "✓ PHASE 3 COMPLETE"
/usr/local/bin/backup_phase.sh 3_complete

echo ""
echo "Press Enter to continue to Phase 4..."
read

################################################################################
# PHASE 4: Firewall Implementation
################################################################################

echo "==================================="
echo "PHASE 4: Firewall Implementation"
echo "==================================="

/usr/local/bin/backup_phase.sh 4_entry

# Firewall Defaults
uci set firewall.@defaults[0]=defaults
uci set firewall.@defaults[0].input='REJECT'
uci set firewall.@defaults[0].output='ACCEPT'
uci set firewall.@defaults[0].forward='REJECT'
uci set firewall.@defaults[0].synflood_protect='1'
uci set firewall.@defaults[0].drop_invalid='1'

# WAN Zone
uci set firewall.wan=zone
uci set firewall.wan.name='wan'
uci add_list firewall.wan.network='wan'
uci add_list firewall.wan.network='wan6'
uci set firewall.wan.input='REJECT'
uci set firewall.wan.output='ACCEPT'
uci set firewall.wan.forward='REJECT'
uci set firewall.wan.masq='1'
uci set firewall.wan.mtu_fix='1'

# LAN Zone
uci set firewall.lan=zone
uci set firewall.lan.name='lan'
uci add_list firewall.lan.network='lan'
uci set firewall.lan.input='ACCEPT'
uci set firewall.lan.output='ACCEPT'
uci set firewall.lan.forward='ACCEPT'

# Management Zone
uci add firewall zone
uci set firewall.@zone[-1].name='management'
uci add_list firewall.@zone[-1].network='management'
uci set firewall.@zone[-1].input='ACCEPT'
uci set firewall.@zone[-1].output='ACCEPT'
uci set firewall.@zone[-1].forward='ACCEPT'

# Automation Zone
uci add firewall zone
uci set firewall.@zone[-1].name='automation'
uci add_list firewall.@zone[-1].network='automation'
uci set firewall.@zone[-1].input='ACCEPT'
uci set firewall.@zone[-1].output='ACCEPT'
uci set firewall.@zone[-1].forward='REJECT'

# CCTV Zone
uci add firewall zone
uci set firewall.@zone[-1].name='cctv'
uci add_list firewall.@zone[-1].network='cctv'
uci set firewall.@zone[-1].input='REJECT'
uci set firewall.@zone[-1].output='ACCEPT'
uci set firewall.@zone[-1].forward='REJECT'

# Storage Zone
uci add firewall zone
uci set firewall.@zone[-1].name='storage'
uci add_list firewall.@zone[-1].network='storage'
uci set firewall.@zone[-1].input='ACCEPT'
uci set firewall.@zone[-1].output='ACCEPT'
uci set firewall.@zone[-1].forward='REJECT'

# IoT Sensors Zone
uci add firewall zone
uci set firewall.@zone[-1].name='iot_sensors'
uci add_list firewall.@zone[-1].network='iot_sensors'
uci set firewall.@zone[-1].input='REJECT'
uci set firewall.@zone[-1].output='ACCEPT'
uci set firewall.@zone[-1].forward='REJECT'

# Monitoring Zone
uci add firewall zone
uci set firewall.@zone[-1].name='monitoring'
uci add_list firewall.@zone[-1].network='monitoring'
uci set firewall.@zone[-1].input='ACCEPT'
uci set firewall.@zone[-1].output='ACCEPT'
uci set firewall.@zone[-1].forward='REJECT'

# DMZ Zone
uci add firewall zone
uci set firewall.@zone[-1].name='dmz'
uci add_list firewall.@zone[-1].network='dmz'
uci set firewall.@zone[-1].input='REJECT'
uci set firewall.@zone[-1].output='ACCEPT'
uci set firewall.@zone[-1].forward='REJECT'

# Guest Zone
uci add firewall zone
uci set firewall.@zone[-1].name='guest'
uci add_list firewall.@zone[-1].network='guest'
uci set firewall.@zone[-1].input='REJECT'
uci set firewall.@zone[-1].output='ACCEPT'
uci set firewall.@zone[-1].forward='REJECT'

# VPN Zone
uci add firewall zone
uci set firewall.@zone[-1].name='vpn_clients'
uci add_list firewall.@zone[-1].network='wg0'
uci set firewall.@zone[-1].input='ACCEPT'
uci set firewall.@zone[-1].output='ACCEPT'
uci set firewall.@zone[-1].forward='REJECT'

# Internet Access Forwardings
uci add firewall forwarding
uci set firewall.@forwarding[-1].src='lan'
uci set firewall.@forwarding[-1].dest='wan'

uci add firewall forwarding
uci set firewall.@forwarding[-1].src='management'
uci set firewall.@forwarding[-1].dest='wan'

uci add firewall forwarding
uci set firewall.@forwarding[-1].src='automation'
uci set firewall.@forwarding[-1].dest='wan'

uci add firewall forwarding
uci set firewall.@forwarding[-1].src='guest'
uci set firewall.@forwarding[-1].dest='wan'

uci add firewall forwarding
uci set firewall.@forwarding[-1].src='dmz'
uci set firewall.@forwarding[-1].dest='wan'

uci add firewall forwarding
uci set firewall.@forwarding[-1].src='monitoring'
uci set firewall.@forwarding[-1].dest='wan'

# VentSys Critical Rules
uci add firewall rule
uci set firewall.@rule[-1].name='HA to IoT Sensors Access'
uci set firewall.@rule[-1].src='automation'
uci set firewall.@rule[-1].src_ip='192.168.20.101'
uci set firewall.@rule[-1].dest='iot_sensors'
uci set firewall.@rule[-1].target='ACCEPT'

uci add firewall rule
uci set firewall.@rule[-1].name='VentSys MQTT IoT to HA'
uci set firewall.@rule[-1].src='iot_sensors'
uci set firewall.@rule[-1].dest='automation'
uci set firewall.@rule[-1].dest_ip='192.168.20.101'
uci set firewall.@rule[-1].proto='tcp'
uci set firewall.@rule[-1].dest_port='8883'
uci set firewall.@rule[-1].target='ACCEPT'

uci add firewall rule
uci set firewall.@rule[-1].name='ESPHome API HA to IoT'
uci set firewall.@rule[-1].src='automation'
uci set firewall.@rule[-1].src_ip='192.168.20.101'
uci set firewall.@rule[-1].dest='iot_sensors'
uci set firewall.@rule[-1].proto='tcp'
uci set firewall.@rule[-1].dest_port='6053'
uci set firewall.@rule[-1].target='ACCEPT'

uci add firewall rule
uci set firewall.@rule[-1].name='Block IoT Internet'
uci set firewall.@rule[-1].src='iot_sensors'
uci set firewall.@rule[-1].dest='wan'
uci set firewall.@rule[-1].target='REJECT'

# Management Access
for zone in lan automation cctv storage iot_sensors monitoring dmz; do
    uci add firewall forwarding
    uci set firewall.@forwarding[-1].src='management'
    uci set firewall.@forwarding[-1].dest="$zone"
done

# Automation Zone Access
uci add firewall forwarding
uci set firewall.@forwarding[-1].src='automation'
uci set firewall.@forwarding[-1].dest='cctv'

uci add firewall forwarding
uci set firewall.@forwarding[-1].src='automation'
uci set firewall.@forwarding[-1].dest='storage'

# CCTV Zone Access
uci add firewall forwarding
uci set firewall.@forwarding[-1].src='cctv'
uci set firewall.@forwarding[-1].dest='storage'

uci add firewall forwarding
uci set firewall.@forwarding[-1].src='cctv'
uci set firewall.@forwarding[-1].dest='automation'

uci add firewall rule
uci set firewall.@rule[-1].name='Block CCTV Internet'
uci set firewall.@rule[-1].src='cctv'
uci set firewall.@rule[-1].dest='wan'
uci set firewall.@rule[-1].target='REJECT'

# Storage Block Internet
uci add firewall rule
uci set firewall.@rule[-1].name='Block Storage Internet'
uci set firewall.@rule[-1].src='storage'
uci set firewall.@rule[-1].dest='wan'
uci set firewall.@rule[-1].target='REJECT'

# Guest Isolation
for zone in lan management automation cctv storage iot_sensors monitoring dmz; do
    uci add firewall rule
    uci set firewall.@rule[-1].name="Block Guest to $zone"
    uci set firewall.@rule[-1].src='guest'
    uci set firewall.@rule[-1].dest="$zone"
    uci set firewall.@rule[-1].target='REJECT'
done

# DMZ Isolation
for zone in lan automation cctv storage iot_sensors; do
    uci add firewall rule
    uci set firewall.@rule[-1].name="Block DMZ to $zone"
    uci set firewall.@rule[-1].src='dmz'
    uci set firewall.@rule[-1].dest="$zone"
    uci set firewall.@rule[-1].target='REJECT'
done

# VPN Access
uci add firewall forwarding
uci set firewall.@forwarding[-1].src='vpn_clients'
uci set firewall.@forwarding[-1].dest='lan'

uci add firewall forwarding
uci set firewall.@forwarding[-1].src='vpn_clients'
uci set firewall.@forwarding[-1].dest='wan'

for zone in management cctv storage iot_sensors; do
    uci add firewall rule
    uci set firewall.@rule[-1].name="Block VPN to $zone"
    uci set firewall.@rule[-1].src='vpn_clients'
    uci set firewall.@rule[-1].dest="$zone"
    uci set firewall.@rule[-1].target='REJECT'
done

uci commit firewall
/etc/init.d/firewall restart
sleep 10

echo "✓ PHASE 4 COMPLETE"
/usr/local/bin/backup_phase.sh 4_complete

echo ""
echo "Press Enter to continue to Phase 5..."
read

################################################################################
# PHASE 5: Wireless Configuration
################################################################################

echo "==================================="
echo "PHASE 5: Wireless Configuration"
echo "==================================="

/usr/local/bin/backup_phase.sh 5_entry

# Radio Configuration
uci set wireless.radio0.type='mac80211'
uci set wireless.radio0.band='2g'
uci set wireless.radio0.channel='6'
uci set wireless.radio0.htmode='HE40'
uci set wireless.radio0.country='US'
uci set wireless.radio0.txpower='20'
uci set wireless.radio0.mu_beamformer='1'
uci set wireless.radio0.legacy_rates='1'

uci set wireless.radio1.type='mac80211'
uci set wireless.radio1.band='5g'
uci set wireless.radio1.channel='auto'
uci set wireless.radio1.htmode='HE80'
uci set wireless.radio1.country='US'
uci set wireless.radio1.txpower='23'
uci set wireless.radio1.mu_beamformer='1'

# HomeMain SSID (VLAN 1)
MAIN_PASSWORD=$(cat /etc/wireless/credentials/main_password.txt)

uci add wireless wifi-iface
uci set wireless.@wifi-iface[-1].device='radio0'
uci set wireless.@wifi-iface[-1].mode='ap'
uci set wireless.@wifi-iface[-1].ssid='HomeMain'
uci set wireless.@wifi-iface[-1].network='lan'
uci set wireless.@wifi-iface[-1].encryption='sae-mixed'
uci set wireless.@wifi-iface[-1].key="$MAIN_PASSWORD"
uci set wireless.@wifi-iface[-1].ieee80211w='1'

uci add wireless wifi-iface
uci set wireless.@wifi-iface[-1].device='radio1'
uci set wireless.@wifi-iface[-1].mode='ap'
uci set wireless.@wifi-iface[-1].ssid='HomeMain'
uci set wireless.@wifi-iface[-1].network='lan'
uci set wireless.@wifi-iface[-1].encryption='sae-mixed'
uci set wireless.@wifi-iface[-1].key="$MAIN_PASSWORD"
uci set wireless.@wifi-iface[-1].ieee80211w='1'

# HomeAdmin SSID (VLAN 10)
ADMIN_PASSWORD=$(cat /etc/wireless/credentials/admin_password.txt)

uci add wireless wifi-iface
uci set wireless.@wifi-iface[-1].device='radio1'
uci set wireless.@wifi-iface[-1].mode='ap'
uci set wireless.@wifi-iface[-1].ssid='HomeAdmin'
uci set wireless.@wifi-iface[-1].network='management'
uci set wireless.@wifi-iface[-1].encryption='sae'
uci set wireless.@wifi-iface[-1].key="$ADMIN_PASSWORD"
uci set wireless.@wifi-iface[-1].ieee80211w='2'
uci set wireless.@wifi-iface[-1].maxassoc='8'

# HomeIoT SSID (VLAN 50) - VentSys Critical
IOT_PASSWORD=$(cat /etc/wireless/credentials/iot_password.txt)

uci add wireless wifi-iface
uci set wireless.@wifi-iface[-1].device='radio0'
uci set wireless.@wifi-iface[-1].mode='ap'
uci set wireless.@wifi-iface[-1].ssid='HomeIoT'
uci set wireless.@wifi-iface[-1].network='iot_sensors'
uci set wireless.@wifi-iface[-1].encryption='psk2'
uci set wireless.@wifi-iface[-1].key="$IOT_PASSWORD"
uci set wireless.@wifi-iface[-1].ieee80211w='0'
uci set wireless.@wifi-iface[-1].maxassoc='50'
uci set wireless.@wifi-iface[-1].isolate='1'

# HomeGuest SSID (VLAN 99)
GUEST_PASSWORD=$(cat /etc/wireless/credentials/guest_password.txt)

uci add wireless wifi-iface
uci set wireless.@wifi-iface[-1].device='radio0'
uci set wireless.@wifi-iface[-1].mode='ap'
uci set wireless.@wifi-iface[-1].ssid='HomeGuest'
uci set wireless.@wifi-iface[-1].network='guest'
uci set wireless.@wifi-iface[-1].encryption='psk2'
uci set wireless.@wifi-iface[-1].key="$GUEST_PASSWORD"
uci set wireless.@wifi-iface[-1].ieee80211w='0'
uci set wireless.@wifi-iface[-1].isolate='1'
uci set wireless.@wifi-iface[-1].maxassoc='10'

# HomeDMZ SSID (VLAN 70) - Disabled
DMZ_PASSWORD=$(cat /etc/wireless/credentials/dmz_password.txt)

uci add wireless wifi-iface
uci set wireless.@wifi-iface[-1].device='radio1'
uci set wireless.@wifi-iface[-1].mode='ap'
uci set wireless.@wifi-iface[-1].ssid='HomeDMZ'
uci set wireless.@wifi-iface[-1].network='dmz'
uci set wireless.@wifi-iface[-1].encryption='sae'
uci set wireless.@wifi-iface[-1].key="$DMZ_PASSWORD"
uci set wireless.@wifi-iface[-1].ieee80211w='2'
uci set wireless.@wifi-iface[-1].maxassoc='5'
uci set wireless.@wifi-iface[-1].disabled='1'

# Enable radios
uci set wireless.radio0.disabled='0'
uci set wireless.radio1.disabled='0'

uci commit wireless
/etc/init.d/network restart
sleep 15

echo "✓ PHASE 5 COMPLETE"
/usr/local/bin/backup_phase.sh 5_complete

echo ""
echo "Press Enter to continue to Phase 6..."
read

################################################################################
# PHASE 6: WireGuard VPN Setup
################################################################################

echo "==================================="
echo "PHASE 6: WireGuard VPN Setup"
echo "==================================="

/usr/local/bin/backup_phase.sh 6_entry

SERVER_PRIVATE_KEY=$(cat /etc/wireguard/keys/server_private.key)

# WireGuard Interface
uci set network.wg0=interface
uci set network.wg0.proto='wireguard'
uci set network.wg0.private_key="$SERVER_PRIVATE_KEY"
uci set network.wg0.listen_port='51820'
uci add_list network.wg0.addresses='10.0.0.1/24'

# WireGuard Peers
CLIENT1_PUBLIC_KEY=$(cat /etc/wireguard/keys/client1_public.key)
CLIENT2_PUBLIC_KEY=$(cat /etc/wireguard/keys/client2_public.key)
CLIENT3_PUBLIC_KEY=$(cat /etc/wireguard/keys/client3_public.key)

uci add network wireguard_wg0
uci set network.@wireguard_wg0[-1].public_key="$CLIENT1_PUBLIC_KEY"
uci set network.@wireguard_wg0[-1].allowed_ips='10.0.0.2/32'
uci set network.@wireguard_wg0[-1].persistent_keepalive='25'

uci add network wireguard_wg0
uci set network.@wireguard_wg0[-1].public_key="$CLIENT2_PUBLIC_KEY"
uci set network.@wireguard_wg0[-1].allowed_ips='10.0.0.3/32'
uci set network.@wireguard_wg0[-1].persistent_keepalive='25'

uci add network wireguard_wg0
uci set network.@wireguard_wg0[-1].public_key="$CLIENT3_PUBLIC_KEY"
uci set network.@wireguard_wg0[-1].allowed_ips='10.0.0.4/32'
uci set network.@wireguard_wg0[-1].persistent_keepalive='25'

uci commit network
/etc/init.d/network restart
sleep 15

# Generate Client Configs
mkdir -p /etc/wireguard/client_configs
SERVER_PUBLIC_KEY=$(cat /etc/wireguard/keys/server_public.key)
WAN_IP=$(wget -qO- http://ipecho.net/plain 2>/dev/null || echo "YOUR_PUBLIC_IP")

for i in 1 2 3; do
    cat > /etc/wireguard/client_configs/client${i}.conf << EOF
[Interface]
PrivateKey = $(cat /etc/wireguard/keys/client${i}_private.key)
Address = 10.0.0.$((i+1))/24
DNS = 192.168.1.1

[Peer]
PublicKey = $SERVER_PUBLIC_KEY
Endpoint = $WAN_IP:51820
AllowedIPs = 192.168.0.0/16, 10.0.0.0/24
PersistentKeepalive = 25
EOF
done

echo "✓ PHASE 6 COMPLETE"
/usr/local/bin/backup_phase.sh 6_complete

echo ""
echo "Press Enter to continue to Phase 7..."
read

################################################################################
# PHASE 7: Integration Testing
################################################################################

echo "==================================="
echo "PHASE 7: Integration Testing"
echo "==================================="

/usr/local/bin/backup_phase.sh 7_entry

# System Status
echo "=== System Status ===" > /tmp/phase7_validation.txt

for service in network firewall dnsmasq; do
    if /etc/init.d/$service status >/dev/null 2>&1; then
        echo "✓ $service running" >> /tmp/phase7_validation.txt
    else
        echo "✗ $service not running" >> /tmp/phase7_validation.txt
    fi
done

# VLAN Interfaces
for vlan in 1 10 20 30 40 50 60 70 99; do
    if ip addr show br-lan.$vlan >/dev/null 2>&1; then
        echo "✓ VLAN $vlan operational" >> /tmp/phase7_validation.txt
    else
        echo "✗ VLAN $vlan missing" >> /tmp/phase7_validation.txt
    fi
done

# Port Verification
if bridge vlan show dev lan5 2>/dev/null | grep -q "1.*PVID.*Egress Untagged"; then
    echo "✓ lan5: Rescue port configured correctly" >> /tmp/phase7_validation.txt
else
    echo "✗ lan5: Configuration incorrect" >> /tmp/phase7_validation.txt
fi

if bridge vlan show dev lan1 2>/dev/null | grep -q -E "10|20|30|40|50|60|70"; then
    echo "V lan1: Proxmox trunk port (2.5Gb) configured correctly" >> /tmp/phase7_validation.txt
else
    echo "? lan1: Trunk port configuration incorrect" >> /tmp/phase7_validation.txt
fi

if bridge vlan show dev lan4 2>/dev/null | grep -q "40.*PVID.*Egress Untagged"; then
    echo "V lan4: NAS storage port configured correctly (VLAN 40 untagged)" >> /tmp/phase7_validation.txt

# VentSys Readiness
if ip addr show br-lan.20 2>/dev/null | grep -q "192.168.20.1"; then
    echo "✓ VLAN 20 (Automation): Ready for Home Assistant" >> /tmp/phase7_validation.txt
else
    echo "✗ VLAN 20: Not operational" >> /tmp/phase7_validation.txt
fi

if ip addr show br-lan.50 2>/dev/null | grep -q "192.168.50.1"; then
    echo "✓ VLAN 50 (IoT): Ready for VentSys" >> /tmp/phase7_validation.txt
else
    echo "✗ VLAN 50: Not operational" >> /tmp/phase7_validation.txt
fi

cat /tmp/phase7_validation.txt

echo "✓ PHASE 7 COMPLETE"
/usr/local/bin/backup_phase.sh 7_complete

echo ""
echo "Press Enter to continue to Phase 8..."
read

################################################################################
# PHASE 8: VentSys Integration Readiness
################################################################################

echo "==================================="
echo "PHASE 8: VentSys Integration"
echo "==================================="

/usr/local/bin/backup_phase.sh 8_entry

# Certificate Infrastructure
mkdir -p /etc/ventsys/ca/{certs,private,crl,newcerts}
chmod 700 /etc/ventsys/ca/private
touch /etc/ventsys/ca/index.txt
echo 1000 > /etc/ventsys/ca/serial

# Monitoring Script
cat > /usr/local/bin/ventsys_network_monitor.sh << 'EOF'
#!/bin/sh
LOG_FILE="/var/log/ventsys_network_monitor.log"
echo "$(date): Starting monitoring" >> "$LOG_FILE"

if ip addr show br-lan.20 | grep -q "192.168.20.1"; then
    echo "$(date): ✓ VLAN 20 operational" >> "$LOG_FILE"
else
    echo "$(date): ✗ VLAN 20 FAILED" >> "$LOG_FILE"
fi

if ip addr show br-lan.50 | grep -q "192.168.50.1"; then
    echo "$(date): ✓ VLAN 50 operational" >> "$LOG_FILE"
else
    echo "$(date): ✗ VLAN 50 FAILED" >> "$LOG_FILE"
fi

echo "$(date): Complete" >> "$LOG_FILE"
EOF

chmod +x /usr/local/bin/ventsys_network_monitor.sh
echo "*/15 * * * * /usr/local/bin/ventsys_network_monitor.sh" >> /etc/crontabs/root
/etc/init.d/cron restart

# MAC Address Update Script
cat > /usr/local/bin/update_ventsys_mac.sh << 'EOF'
#!/bin/sh
DEVICE_NAME=$1
MAC_ADDRESS=$2

if [ -z "$DEVICE_NAME" ] || [ -z "$MAC_ADDRESS" ]; then
    echo "Usage: $0 <device_name> <mac_address>"
    exit 1
fi

if ! echo "$MAC_ADDRESS" | grep -qE '^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$'; then
    echo "Error: Invalid MAC address format"
    exit 1
fi

host_section=$(uci show dhcp | grep "name='$DEVICE_NAME'" | cut -d'.' -f2 | cut -d'=' -f1)
if [ -z "$host_section" ]; then
    echo "Error: Device not found"
    exit 1
fi

uci set dhcp.$host_section.mac="$MAC_ADDRESS"
uci commit dhcp
/etc/init.d/dnsmasq restart

echo "✓ Updated $DEVICE_NAME MAC to $MAC_ADDRESS"
EOF

chmod +x /usr/local/bin/update_ventsys_mac.sh

# Final Backup
BACKUP_DIR="/etc/config/backups/production_ready_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp /etc/config/* "$BACKUP_DIR/"
uci export > "$BACKUP_DIR/uci_complete_export.txt"
cp -r /etc/wireless/credentials "$BACKUP_DIR/"
cp -r /etc/wireguard "$BACKUP_DIR/"
tar -czf "/tmp/production_ready_backup_$(date +%Y%m%d_%H%M%S).tar.gz" -C "$(dirname $BACKUP_DIR)" "$(basename $BACKUP_DIR)"

echo "✓ PHASE 8 COMPLETE"
/usr/local/bin/backup_phase.sh 8_complete

################################################################################
# DEPLOYMENT COMPLETE
################################################################################

echo ""
echo "========================================"
echo "DEPLOYMENT COMPLETE!"
echo "========================================"
echo ""
echo "Configuration Summary:"
echo "  - 9 VLANs operational"
echo "  - 5 WiFi SSIDs configured"
echo "  - WireGuard VPN operational"
echo "  - Complete firewall segmentation"
echo "  - VentSys integration ready"
echo ""
echo "Port Assignments:"
echo "  - lan5 (1Gb): Rescue/admin - 192.168.1.1"
  echo "  - lan1 (2.5Gb): Proxmox trunk"
  echo "  - lan4 (1Gb): NAS storage - VLAN 40"
echo "  - lan2 (1Gb): Management - VLAN 10"
echo "  - lan3 (1Gb): CCTV - VLAN 30"
echo ""
echo "Next Steps:"
echo "  1. Connect physical devices"
echo "  2. Update MAC addresses: /usr/local/bin/update_ventsys_mac.sh"
echo "  3. Begin VentSys Phase 1"
echo "  4. Monitor: /var/log/ventsys_network_monitor.log"
echo ""
echo "Backups: /etc/config/backups/"
echo "Emergency restore: /usr/local/bin/emergency_restore.sh"
echo ""
</parameter>
</invoke>
