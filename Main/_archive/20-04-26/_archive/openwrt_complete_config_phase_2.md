# OpenWrt Router Complete Configuration Guide
## GL.iNet GL-MT6000 - 8 Phase Deployment

**Hardware Configuration:**
- WAN (2.5Gb): Internet
- lan1 (2.5Gb): Proxmox trunk - Tagged VLANs
- lan2 (1Gb): Management - VLAN 10 untagged
- lan3 (1Gb): CCTV - VLAN 30 untagged
- lan4 (1Gb): Storage/NAS - VLAN 40 untagged
- lan5 (1Gb): Admin/Rescue - VLAN 1 untagged

---

# Phase 1: Prerequisites and Baseline Setup

**Duration**: 2-3 hours  
**Risk Level**: Low

## 1.1 System Assessment and Backup

```bash
# Document current system state
uname -a > /tmp/system_baseline.txt
cat /etc/openwrt_release >> /tmp/system_baseline.txt
df -h >> /tmp/system_baseline.txt

# Create baseline configuration backup
mkdir -p /etc/config/backups/baseline
cp /etc/config/* /etc/config/backups/baseline/
tar -czf /tmp/factory_baseline_$(date +%Y%m%d_%H%M%S).tar.gz -C /etc/config/backups baseline/

# Document available storage
free -h
```

## 1.2 Package Installation

```bash
# Update package lists
opkg update

# Install WireGuard components
opkg install wireguard-tools
opkg install kmod-wireguard 
opkg install luci-proto-wireguard

# Install additional network utilities
opkg install tcpdump
opkg install iperf3
opkg install ethtool

# Verify installations
opkg list-installed | grep -E "(wireguard|tcpdump|iperf|ethtool)"

# Verify WireGuard kernel module
lsmod | grep wireguard
```

## 1.3 Hardware Interface Verification

```bash
# Document physical interfaces
ip link show > /tmp/interface_baseline.txt

# Verify expected interfaces exist
echo "=== Interface Verification ===" >> /tmp/interface_baseline.txt
for iface in wan lan1 lan2 lan3 lan4 lan5; do
    if ip link show "$iface" >/dev/null 2>&1; then
        echo "✓ $iface exists" >> /tmp/interface_baseline.txt
    else
        echo "✗ $iface missing" >> /tmp/interface_baseline.txt
    fi
done

# Document wireless interfaces
iw dev >> /tmp/interface_baseline.txt
```

## 1.4 WireGuard Key Generation

```bash
# Create WireGuard key directory
mkdir -p /etc/wireguard/keys
chmod 700 /etc/wireguard/keys

# Generate server private/public key pair
wg genkey | tee /etc/wireguard/keys/server_private.key | wg pubkey > /etc/wireguard/keys/server_public.key

# Generate client key pairs (3 clients)
for i in 1 2 3; do
    wg genkey | tee /etc/wireguard/keys/client${i}_private.key | wg pubkey > /etc/wireguard/keys/client${i}_public.key
done

# Set proper permissions
chmod 600 /etc/wireguard/keys/*_private.key
chmod 644 /etc/wireguard/keys/*_public.key

# Document keys
echo "=== WireGuard Keys Generated ===" > /tmp/wireguard_keys.txt
echo "Server Public Key: $(cat /etc/wireguard/keys/server_public.key)" >> /tmp/wireguard_keys.txt
for i in 1 2 3; do
    echo "Client $i Public Key: $(cat /etc/wireguard/keys/client${i}_public.key)" >> /tmp/wireguard_keys.txt
done
```

## 1.5 WiFi Password Generation

```bash
# Generate secure WiFi passwords
mkdir -p /etc/wireless/credentials

# Generate passwords (24 characters)
openssl rand -base64 32 | tr -d "=+/" | cut -c1-24 > /etc/wireless/credentials/main_password.txt
openssl rand -base64 32 | tr -d "=+/" | cut -c1-24 > /etc/wireless/credentials/admin_password.txt
openssl rand -base64 32 | tr -d "=+/" | cut -c1-24 > /etc/wireless/credentials/iot_password.txt
openssl rand -base64 32 | tr -d "=+/" | cut -c1-24 > /etc/wireless/credentials/guest_password.txt
openssl rand -base64 32 | tr -d "=+/" | cut -c1-24 > /etc/wireless/credentials/dmz_password.txt

# Set secure permissions
chmod 600 /etc/wireless/credentials/*.txt

# Document passwords
echo "=== WiFi Credentials Generated ===" > /tmp/wifi_credentials.txt
echo "HomeMain Password: $(cat /etc/wireless/credentials/main_password.txt)" >> /tmp/wifi_credentials.txt
echo "HomeAdmin Password: $(cat /etc/wireless/credentials/admin_password.txt)" >> /tmp/wifi_credentials.txt
echo "HomeIoT Password: $(cat /etc/wireless/credentials/iot_password.txt)" >> /tmp/wifi_credentials.txt
echo "HomeGuest Password: $(cat /etc/wireless/credentials/guest_password.txt)" >> /tmp/wifi_credentials.txt
echo "HomeDMZ Password: $(cat /etc/wireless/credentials/dmz_password.txt)" >> /tmp/wifi_credentials.txt
```

## 1.6 Network Performance Baseline

```bash
# Test current network performance
mkdir -p /tmp/baselines

# Test WAN connectivity
ping -c 10 8.8.8.8 > /tmp/baselines/wan_connectivity.txt
nslookup google.com >> /tmp/baselines/wan_connectivity.txt

# Document interface statistics
for iface in wan lan1 lan2 lan3 lan4 lan5; do
    if ip link show "$iface" >/dev/null 2>&1; then
        echo "=== $iface Statistics ===" >> /tmp/baselines/interface_stats.txt
        ethtool "$iface" 2>/dev/null >> /tmp/baselines/interface_stats.txt || echo "ethtool not available for $iface" >> /tmp/baselines/interface_stats.txt
    fi
done
```

## 1.7 Configuration Management Setup

```bash
# Create configuration management structure
mkdir -p /etc/config/backups/{phases,emergency}
mkdir -p /tmp/deployment_logs

# Create backup script
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

# Create emergency restore script
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

chmod +x /usr/local/bin/emergency_restore.sh

# Test backup system
/usr/local/bin/backup_phase.sh 0_baseline
```

## Phase 1 Validation

```bash
echo "=== Phase 1 Validation ===" > /tmp/phase1_validation.txt

# Check packages
for pkg in wireguard-tools kmod-wireguard luci-proto-wireguard tcpdump iperf3; do
    if opkg list-installed | grep -q "$pkg"; then
        echo "✓ $pkg installed" >> /tmp/phase1_validation.txt
    else
        echo "✗ $pkg missing" >> /tmp/phase1_validation.txt
    fi
done

# Check WireGuard keys
if [ -f "/etc/wireguard/keys/server_private.key" ] && [ -f "/etc/wireguard/keys/server_public.key" ]; then
    echo "✓ Server keys generated" >> /tmp/phase1_validation.txt
else
    echo "✗ Server keys missing" >> /tmp/phase1_validation.txt
fi

# Check WiFi credentials
if [ -f "/etc/wireless/credentials/main_password.txt" ]; then
    echo "✓ WiFi passwords generated" >> /tmp/phase1_validation.txt
else
    echo "✗ WiFi passwords missing" >> /tmp/phase1_validation.txt
fi

# Check backup system
if [ -d "/etc/config/backups/phases" ] && [ -x "/usr/local/bin/backup_phase.sh" ]; then
    echo "✓ Backup system ready" >> /tmp/phase1_validation.txt
else
    echo "✗ Backup system not ready" >> /tmp/phase1_validation.txt
fi

cat /tmp/phase1_validation.txt
```

---

# Phase 2: Network Infrastructure (VLAN Configuration)

**Duration**: 4-5 hours  
**Risk Level**: High  
**CRITICAL**: Incremental deployment with checkpoints

## Checkpoint 0: Establish Rescue Port (lan5)

```bash
# Create Phase 2 entry backup
/usr/local/bin/backup_phase.sh 2_entry

# Document current state
ip link show > /tmp/phase2_checkpoint0_entry.txt
ip addr show >> /tmp/phase2_checkpoint0_entry.txt
uci show network >> /tmp/phase2_checkpoint0_entry.txt

echo "=== CHECKPOINT 0: Establishing Rescue Port lan5 ===" | tee -a /tmp/deployment_logs/phase2.log

# Check if lan5 exists
ip link show lan5

# Ensure default LAN interface configuration
uci set network.lan.device='br-lan'
uci set network.lan.proto='static'
uci set network.lan.ipaddr='192.168.1.1'
uci set network.lan.netmask='255.255.255.0'
uci commit network

# Apply changes
/etc/init.d/network restart

echo "Waiting 30 seconds for network to stabilize..."
sleep 30
```

**MANUAL VERIFICATION - CHECKPOINT 0:**
From your machine at 192.168.1.10:
```bash
ping -c 3 192.168.1.1
ssh root@192.168.1.1
bridge link show | grep lan5
```

**If all tests pass:**
```bash
echo "CHECKPOINT 0 PASSED: lan5 rescue port operational" >> /tmp/deployment_logs/phase2.log
/usr/local/bin/backup_phase.sh 2_checkpoint0
```

## Checkpoint 1: Create DSA Bridge Base

```bash
echo "=== CHECKPOINT 1: Creating DSA Bridge Base ===" | tee -a /tmp/deployment_logs/phase2.log

# Remove existing device config
uci delete network.@device[0] 2>/dev/null || true

# Create new DSA bridge
uci add network device
uci set network.@device[-1].name='br-lan'
uci set network.@device[-1].type='bridge'

# Add ALL physical ports to bridge
uci add_list network.@device[-1].ports='lan1'
uci add_list network.@device[-1].ports='lan2'
uci add_list network.@device[-1].ports='lan3'
uci add_list network.@device[-1].ports='lan4'
uci add_list network.@device[-1].ports='lan5'

# Enable bridge features
uci set network.@device[-1].igmp_snooping='1'
uci set network.@device[-1].stp='1'
uci set network.@device[-1].stp_hello_time='2'
uci set network.@device[-1].stp_forward_delay='15'

# Commit
uci commit network

echo "DSA bridge configured with all 5 ports" >> /tmp/deployment_logs/phase2.log

# Apply changes
echo "WARNING: Network will restart."
/etc/init.d/network restart

echo "Waiting 30 seconds for network stabilization..."
sleep 30
```

**MANUAL VERIFICATION - CHECKPOINT 1:**
```bash
ping -c 3 192.168.1.1
ssh root@192.168.1.1
brctl show br-lan
cat /sys/class/net/br-lan/bridge/stp_state  # Should return: 1
ip addr show br-lan | grep 192.168.1.1
```

**If all tests pass:**
```bash
echo "CHECKPOINT 1 PASSED: DSA bridge operational" >> /tmp/deployment_logs/phase2.log
/usr/local/bin/backup_phase.sh 2_checkpoint1
```

## Checkpoint 2: Add VLAN 1 (Rescue Port Protection)

```bash
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

uci commit network

echo "VLAN 1 configured with lan5 as untagged rescue port" >> /tmp/deployment_logs/phase2.log

# Apply changes
/etc/init.d/network restart
sleep 30
```

**MANUAL VERIFICATION - CHECKPOINT 2:**
```bash
ping -c 3 192.168.1.1
bridge vlan show dev lan5  # Should show: VLAN 1 untagged (PVID)
ip addr show br-lan.1
ssh root@192.168.1.1
```

**If all tests pass:**
```bash
echo "CHECKPOINT 2 PASSED: VLAN 1 operational" >> /tmp/deployment_logs/phase2.log
/usr/local/bin/backup_phase.sh 2_checkpoint2
```

## Checkpoint 3A: Add Management VLAN 10

```bash
echo "=== CHECKPOINT 3A: Adding VLAN 10 (Management) ===" | tee -a /tmp/deployment_logs/phase2.log

# VLAN 10: Management Network
uci add network bridge-vlan
uci set network.@bridge-vlan[-1].device='br-lan'
uci set network.@bridge-vlan[-1].vlan='10'
uci set network.@bridge-vlan[-1].local='1'
uci add_list network.@bridge-vlan[-1].ports='lan1:t'
uci add_list network.@bridge-vlan[-1].ports='lan2:u'
uci add_list network.@bridge-vlan[-1].ports='lan3:t'
uci add_list network.@bridge-vlan[-1].ports='lan4:t'

uci commit network
/etc/init.d/network restart
sleep 30
```

**MANUAL VERIFICATION:**
```bash
ping -c 3 192.168.1.1
bridge vlan show | grep "vlan 10"
ssh root@192.168.1.1
```

**If tests pass:**
```bash
echo "CHECKPOINT 3A PASSED: VLAN 10 added" >> /tmp/deployment_logs/phase2.log
/usr/local/bin/backup_phase.sh 2_checkpoint3a
```

## Checkpoint 3B: Add Automation VLAN 20

```bash
echo "=== CHECKPOINT 3B: Adding VLAN 20 (Automation) ===" | tee -a /tmp/deployment_logs/phase2.log

# VLAN 20: VentSys Automation Network
uci add network bridge-vlan
uci set network.@bridge-vlan[-1].device='br-lan'
uci set network.@bridge-vlan[-1].vlan='20'
uci set network.@bridge-vlan[-1].local='1'
uci add_list network.@bridge-vlan[-1].ports='lan1:t'

uci commit network
/etc/init.d/network restart
sleep 30
```

**MANUAL VERIFICATION:**
```bash
ping -c 3 192.168.1.1
bridge vlan show | grep "vlan 20"
ssh root@192.168.1.1
```

**If tests pass:**
```bash
echo "CHECKPOINT 3B PASSED: VLAN 20 added" >> /tmp/deployment_logs/phase2.log
/usr/local/bin/backup_phase.sh 2_checkpoint3b
```

## Checkpoint 3C: Add CCTV VLAN 30

```bash
echo "=== CHECKPOINT 3C: Adding VLAN 30 (CCTV) ===" | tee -a /tmp/deployment_logs/phase2.log

# VLAN 30: CCTV Network
uci add network bridge-vlan
uci set network.@bridge-vlan[-1].device='br-lan'
uci set network.@bridge-vlan[-1].vlan='30'
uci set network.@bridge-vlan[-1].local='1'
uci add_list network.@bridge-vlan[-1].ports='lan1:t'
uci add_list network.@bridge-vlan[-1].ports='lan3:u'

uci commit network
/etc/init.d/network restart
sleep 30
```

**MANUAL VERIFICATION:**
```bash
ping -c 3 192.168.1.1
bridge vlan show | grep "vlan 30"
ssh root@192.168.1.1
```

**If tests pass:**
```bash
echo "CHECKPOINT 3C PASSED: VLAN 30 added" >> /tmp/deployment_logs/phase2.log
/usr/local/bin/backup_phase.sh 2_checkpoint3c
```

## Checkpoint 3D: Add Storage VLAN 40

```bash
echo "=== CHECKPOINT 3D: Adding VLAN 40 (Storage) ===" | tee -a /tmp/deployment_logs/phase2.log

# VLAN 40: Storage Network
uci add network bridge-vlan
uci set network.@bridge-vlan[-1].device='br-lan'
uci set network.@bridge-vlan[-1].vlan='40'
uci set network.@bridge-vlan[-1].local='1'
uci add_list network.@bridge-vlan[-1].ports='lan1:t'
uci add_list network.@bridge-vlan[-1].ports='lan4:u*'

uci commit network
/etc/init.d/network restart
sleep 30
```

**MANUAL VERIFICATION:**
```bash
ping -c 3 192.168.1.1
bridge vlan show | grep "vlan 40"
bridge vlan show dev lan4  # Should show VLAN 40 untagged
ssh root@192.168.1.1
```

**If tests pass:**
```bash
echo "CHECKPOINT 3D PASSED: VLAN 40 added on lan4 (NAS port)" >> /tmp/deployment_logs/phase2.log
/usr/local/bin/backup_phase.sh 2_checkpoint3d
```

## Checkpoint 3E: Add IoT Sensors VLAN 50

```bash
echo "=== CHECKPOINT 3E: Adding VLAN 50 (IoT Sensors) ===" | tee -a /tmp/deployment_logs/phase2.log

# VLAN 50: VentSys IoT Sensors Network
uci add network bridge-vlan
uci set network.@bridge-vlan[-1].device='br-lan'
uci set network.@bridge-vlan[-1].vlan='50'
uci set network.@bridge-vlan[-1].local='1'
uci add_list network.@bridge-vlan[-1].ports='lan1:t'

uci commit network
/etc/init.d/network restart
sleep 30
```

**MANUAL VERIFICATION:**
```bash
ping -c 3 192.168.1.1
bridge vlan show | grep "vlan 50"
ssh root@192.168.1.1
```

**If tests pass:**
```bash
echo "CHECKPOINT 3E PASSED: VLAN 50 added" >> /tmp/deployment_logs/phase2.log
/usr/local/bin/backup_phase.sh 2_checkpoint3e
```

## Checkpoint 3F: Add Remaining VLANs (60, 70, 99)

```bash
echo "=== CHECKPOINT 3F: Adding VLANs 60, 70, 99 ===" | tee -a /tmp/deployment_logs/phase2.log

# VLAN 60: Monitoring Network
uci add network bridge-vlan
uci set network.@bridge-vlan[-1].device='br-lan'
uci set network.@bridge-vlan[-1].vlan='60'
uci set network.@bridge-vlan[-1].local='1'
uci add_list network.@bridge-vlan[-1].ports='lan1:t'

# VLAN 70: DMZ Network
uci add network bridge-vlan
uci set network.@bridge-vlan[-1].device='br-lan'
uci set network.@bridge-vlan[-1].vlan='70'
uci set network.@bridge-vlan[-1].local='1'
uci add_list network.@bridge-vlan[-1].ports='lan1:t'

# VLAN 99: Guest Network (WiFi-only)
uci add network bridge-vlan
uci set network.@bridge-vlan[-1].device='br-lan'
uci set network.@bridge-vlan[-1].vlan='99'
uci set network.@bridge-vlan[-1].local='1'

uci commit network
/etc/init.d/network restart
sleep 30
```

**MANUAL VERIFICATION:**
```bash
ping -c 3 192.168.1.1
bridge vlan show | grep -E "vlan (60|70|99)"
ssh root@192.168.1.1
```

**If tests pass:**
```bash
echo "CHECKPOINT 3F PASSED: All VLANs configured" >> /tmp/deployment_logs/phase2.log
/usr/local/bin/backup_phase.sh 2_checkpoint3f
```

## Checkpoint 4: Create Logical Network Interfaces

```bash
echo "=== CHECKPOINT 4: Creating Logical Network Interfaces ===" | tee -a /tmp/deployment_logs/phase2.log

# Management VLAN 10
uci set network.management=interface
uci set network.management.proto='static'
uci set network.management.device='br-lan.10'
uci set network.management.ipaddr='192.168.10.1'
uci set network.management.netmask='255.255.255.0'

# Automation VLAN 20
uci set network.automation=interface
uci set network.automation.proto='static'
uci set network.automation.device='br-lan.20'
uci set network.automation.ipaddr='192.168.20.1'
uci set network.automation.netmask='255.255.255.0'

# CCTV VLAN 30
uci set network.cctv=interface
uci set network.cctv.proto='static'
uci set network.cctv.device='br-lan.30'
uci set network.cctv.ipaddr='192.168.30.1'
uci set network.cctv.netmask='255.255.255.0'

# Storage VLAN 40
uci set network.storage=interface
uci set network.storage.proto='static'
uci set network.storage.device='br-lan.40'
uci set network.storage.ipaddr='192.168.40.1'
uci set network.storage.netmask='255.255.255.0'

# IoT Sensors VLAN 50
uci set network.iot_sensors=interface
uci set network.iot_sensors.proto='static'
uci set network.iot_sensors.device='br-lan.50'
uci set network.iot_sensors.ipaddr='192.168.50.1'
uci set network.iot_sensors.netmask='255.255.255.0'

# Monitoring VLAN 60
uci set network.monitoring=interface
uci set network.monitoring.proto='static'
uci set network.monitoring.device='br-lan.60'
uci set network.monitoring.ipaddr='192.168.60.1'
uci set network.monitoring.netmask='255.255.255.0'

# DMZ VLAN 70
uci set network.dmz=interface
uci set network.dmz.proto='static'
uci set network.dmz.device='br-lan.70'
uci set network.dmz.ipaddr='192.168.70.1'
uci set network.dmz.netmask='255.255.255.0'

# Guest VLAN 99
uci set network.guest=interface
uci set network.guest.proto='static'
uci set network.guest.device='br-lan.99'
uci set network.guest.ipaddr='192.168.99.1'
uci set network.guest.netmask='255.255.255.0'

uci commit network
/etc/init.d/network restart
sleep 30
```

**MANUAL VERIFICATION:**
```bash
ping -c 3 192.168.1.1
ip addr show | grep "br-lan\."
ping -c 1 192.168.10.1
ping -c 1 192.168.20.1
ping -c 1 192.168.30.1
ping -c 1 192.168.40.1
ping -c 1 192.168.50.1
ssh root@192.168.1.1
```

**If tests pass:**
```bash
echo "CHECKPOINT 4 PASSED: All logical interfaces operational" >> /tmp/deployment_logs/phase2.log
/usr/local/bin/backup_phase.sh 2_checkpoint4
```

## Checkpoint 5: Final WAN Configuration

```bash
echo "=== CHECKPOINT 5: WAN Configuration ===" | tee -a /tmp/deployment_logs/phase2.log

# WAN configuration
uci set network.wan.proto='dhcp'
uci set network.wan.peerdns='0'
uci delete network.wan.dns 2>/dev/null || true
uci add_list network.wan.dns='1.1.1.1'
uci add_list network.wan.dns='1.0.0.1'

# IPv6 WAN
uci set network.wan6.proto='dhcpv6'
uci set network.wan6.reqaddress='try'
uci set network.wan6.reqprefix='auto'

uci commit network
/etc/init.d/network restart
sleep 30
```

**MANUAL VERIFICATION:**
```bash
ping -c 3 192.168.1.1
ping -c 3 8.8.8.8
ssh root@192.168.1.1
```

## Phase 2 Final Validation

```bash
echo "=== Phase 2 Final Validation ===" > /tmp/phase2_final_validation.txt

# Test all VLAN interfaces
for vlan in 1 10 20 30 40 50 60 70 99; do
    if [ $vlan -eq 1 ]; then expected_ip="192.168.1.1"
    elif [ $vlan -eq 99 ]; then expected_ip="192.168.99.1"
    else expected_ip="192.168.${vlan}.1"; fi
    
    if ip addr show br-lan.$vlan 2>/dev/null | grep -q "$expected_ip"; then
        echo "✓ VLAN $vlan operational: $expected_ip" >> /tmp/phase2_final_validation.txt
    else
        echo "✗ VLAN $vlan FAILED" >> /tmp/phase2_final_validation.txt
    fi
done

# Verify port assignments
echo "" >> /tmp/phase2_final_validation.txt
echo "Port Assignment Verification:" >> /tmp/phase2_final_validation.txt
bridge vlan show >> /tmp/phase2_final_validation.txt

cat /tmp/phase2_final_validation.txt

echo "✓ PHASE 2 COMPLETE" >> /tmp/deployment_logs/phase2.log
/usr/local/bin/backup_phase.sh 2_complete
```

---

# Phase 3: DHCP Configuration

**Duration**: 2-3 hours  
**Risk Level**: Medium

## 3.1 Pre-Configuration Backup

```bash
/usr/local/bin/backup_phase.sh 3_entry

echo "=== Phase 3 Prerequisites ===" > /tmp/phase3_validation.txt

# Verify all VLAN interfaces
for vlan in 1 10 20 30 40 50 60 70 99; do
    if [ $vlan -eq 1 ]; then expected_ip="192.168.1.
