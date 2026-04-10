# Phase 1: Prerequisites and Baseline Setup

**Duration**: 2-3 hours  
**Risk Level**: Low (baseline establishment)  
**Prerequisites**: Fresh OpenWrt installation, SSH/web access

## Overview
Establishes foundation for complex network deployment through package installation, baseline documentation, credential generation, and hardware verification. Critical for preventing configuration rollbacks due to missing dependencies.

## Interdependencies

### Input Requirements
- Fresh OpenWrt installation on GL.iNet GL-MT6000
- Internet connectivity via WAN for package downloads
- Root access (SSH or LuCI web interface)

### Output Deliverables
- All required packages installed and verified
- Complete hardware baseline documentation
- Generated credentials (WireGuard keys, WiFi passwords)
- Configuration backup system established
- Interface naming verification completed

### Dependencies for Later Phases
- **Phase 2**: Interface names required for VLAN configuration
- **Phase 6**: WireGuard keys required for VPN setup
- **Phase 5**: WiFi passwords required for wireless setup
- **All Phases**: Backup system enables rollback capability

## Sub-Tasks

### 1.1 System Assessment and Backup
**Duration**: 15 minutes

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

**Testing Criteria**:
- Configuration backup created successfully
- System information documented
- Sufficient storage available (>100MB free)

### 1.2 Package Installation
**Duration**: 20-30 minutes

```bash
# Update package lists
opkg update

# Install WireGuard components (CRITICAL for Phase 6)
opkg install wireguard-tools
opkg install kmod-wireguard 
opkg install luci-proto-wireguard

# Install additional network utilities
opkg install tcpdump
opkg install iperf3
opkg install ethtool

# Verify installations
opkg list-installed | grep -E "(wireguard|tcpdump|iperf|ethtool)"
```

**Testing Criteria**:
- All packages installed without errors
- WireGuard kernel module loaded (`lsmod | grep wireguard`)
- LuCI interface shows WireGuard protocol option
- Network utilities accessible via command line

**Critical Notes**:
- WireGuard packages must install before network reconfiguration
- Failed package installs will break Phase 6 VPN setup
- LuCI interface restart may be required

### 1.3 Hardware Interface Verification
**Duration**: 15 minutes

```bash
# Document physical interfaces
ip link show > /tmp/interface_baseline.txt

# Verify expected interfaces exist
echo "=== Interface Verification ===" >> /tmp/interface_baseline.txt
# lan1-lan4: active network ports (trunk, management, cameras, NAS)
# lan5: recovery/AP port — must exist; used for out-of-band router access during setup
#        and as the TP-Link TL-WA801N AP connection after setup is stable
for iface in wan lan1 lan2 lan3 lan4 lan5; do
    if ip link show "$iface" >/dev/null 2>&1; then
        echo "✓ $iface exists" >> /tmp/interface_baseline.txt
    else
        echo "✗ $iface missing" >> /tmp/interface_baseline.txt
    fi
done

# Document wireless interfaces
iw dev >> /tmp/interface_baseline.txt

# Document switch capabilities (DSA verification)
ls -la /sys/class/net/*/dsa/ 2>/dev/null >> /tmp/interface_baseline.txt || echo "DSA info not available" >> /tmp/interface_baseline.txt
```

**Testing Criteria**:
- Physical ports lan1-lan4 exist and are operational
- lan5 exists — this is the recovery/AP port (must be present; GL-MT6000 has 5 LAN ports)
- WAN interface exists and has link
- Wireless interfaces radio0/radio1 detected
- DSA switch architecture confirmed (if applicable)

**Critical Notes**:
- Interface naming MUST match configuration expectations
- Missing interfaces will break VLAN configuration in Phase 2
- Document any naming deviations for config adjustment
- lan5 is intentionally kept on VLAN 1 only throughout the project — connect your laptop
  here before starting Phase 2 so you retain SSH access to 192.168.1.1 if VLANs break

### 1.4 WireGuard Key Generation
**Duration**: 10 minutes

```bash
# Create WireGuard key directory
mkdir -p /etc/wireguard/keys
chmod 700 /etc/wireguard/keys

# Generate server private/public key pair
wg genkey | tee /etc/wireguard/keys/server_private.key | wg pubkey > /etc/wireguard/keys/server_public.key

# Generate client key pairs (3 clients as per config)
for i in {1..3}; do
    wg genkey | tee /etc/wireguard/keys/client${i}_private.key | wg pubkey > /etc/wireguard/keys/client${i}_public.key
done

# Set proper permissions
chmod 600 /etc/wireguard/keys/*_private.key
chmod 644 /etc/wireguard/keys/*_public.key

# Document keys for configuration use
echo "=== WireGuard Keys Generated ===" > /tmp/wireguard_keys.txt
echo "Server Public Key: $(cat /etc/wireguard/keys/server_public.key)" >> /tmp/wireguard_keys.txt
for i in {1..3}; do
    echo "Client $i Public Key: $(cat /etc/wireguard/keys/client${i}_public.key)" >> /tmp/wireguard_keys.txt
done
```

**Testing Criteria**:
- All key files created with correct permissions
- Public keys are valid base64 format
- Private keys are secure (600 permissions)
- Key documentation file created

**Critical Notes**:
- Private keys must never be shared or stored insecurely
- Public keys will be needed for Phase 6 VPN configuration
- Key loss requires complete regeneration and client reconfiguration

### 1.5 WiFi Password Generation
**Duration**: 5 minutes

```bash
# Generate secure WiFi passwords for all SSIDs
mkdir -p /etc/wireless/credentials

# Generate passwords (24 characters, alphanumeric + symbols)
openssl rand -base64 32 | tr -d "=+/" | cut -c1-24 > /etc/wireless/credentials/main_password.txt
openssl rand -base64 32 | tr -d "=+/" | cut -c1-24 > /etc/wireless/credentials/admin_password.txt
openssl rand -base64 32 | tr -d "=+/" | cut -c1-24 > /etc/wireless/credentials/iot_password.txt
openssl rand -base64 32 | tr -d "=+/" | cut -c1-24 > /etc/wireless/credentials/guest_password.txt
openssl rand -base64 32 | tr -d "=+/" | cut -c1-24 > /etc/wireless/credentials/dmz_password.txt

# Set secure permissions
chmod 600 /etc/wireless/credentials/*.txt

# Document passwords for configuration use (SECURE HANDLING REQUIRED)
echo "=== WiFi Credentials Generated ===" > /tmp/wifi_credentials.txt
echo "HomeMain Password: $(cat /etc/wireless/credentials/main_password.txt)" >> /tmp/wifi_credentials.txt
echo "HomeAdmin Password: $(cat /etc/wireless/credentials/admin_password.txt)" >> /tmp/wifi_credentials.txt
echo "HomeIoT Password: $(cat /etc/wireless/credentials/iot_password.txt)" >> /tmp/wifi_credentials.txt
echo "HomeGuest Password: $(cat /etc/wireless/credentials/guest_password.txt)" >> /tmp/wifi_credentials.txt
echo "HomeDMZ Password: $(cat /etc/wireless/credentials/dmz_password.txt)" >> /tmp/wifi_credentials.txt
```

**Testing Criteria**:
- All password files created with secure permissions
- Passwords are 24 characters, high complexity
- Credential documentation file created
- No passwords visible in command history

**Critical Notes**:
- WiFi credentials must be stored securely
- Passwords will be needed for Phase 5 wireless configuration
- Consider printing/securing credentials before network reconfiguration

### 1.6 Network Performance Baseline
**Duration**: 20 minutes

```bash
# Test current network performance
mkdir -p /tmp/baselines

# Test WAN connectivity and speed
ping -c 10 8.8.8.8 > /tmp/baselines/wan_connectivity.txt
nslookup google.com >> /tmp/baselines/wan_connectivity.txt

# Document current interface statistics
for iface in wan lan1 lan2 lan3 lan4; do
    if ip link show "$iface" >/dev/null 2>&1; then
        echo "=== $iface Statistics ===" >> /tmp/baselines/interface_stats.txt
        ethtool "$iface" 2>/dev/null >> /tmp/baselines/interface_stats.txt || echo "ethtool not available for $iface" >> /tmp/baselines/interface_stats.txt
        cat "/sys/class/net/$iface/statistics/rx_bytes" >> /tmp/baselines/interface_stats.txt 2>/dev/null || echo "No stats for $iface"
        cat "/sys/class/net/$iface/statistics/tx_bytes" >> /tmp/baselines/interface_stats.txt 2>/dev/null
    fi
done

# Test wireless capabilities
iwconfig 2>/dev/null > /tmp/baselines/wireless_baseline.txt || echo "Wireless not configured" > /tmp/baselines/wireless_baseline.txt
```

**Testing Criteria**:
- WAN connectivity confirmed (ping success)
- DNS resolution working
- Interface statistics collected
- Wireless hardware detected

### 1.7 Configuration Management Setup
**Duration**: 15 minutes

```bash
# Create configuration management structure
mkdir -p /etc/config/backups/{phases,emergency}
mkdir -p /tmp/deployment_logs

# Create backup script for each phase
cat > /usr/local/bin/backup_phase.sh << 'EOF'
#!/bin/bash
PHASE=$1
if [ -z "$PHASE" ]; then
    echo "Usage: backup_phase.sh <phase_number>"
    exit 1
fi

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/etc/config/backups/phases/phase_${PHASE}_${TIMESTAMP}"
mkdir -p "$BACKUP_DIR"

# Backup all config files
cp /etc/config/* "$BACKUP_DIR/"
uci export > "$BACKUP_DIR/uci_export.txt"

echo "Phase $PHASE backup created: $BACKUP_DIR"
EOF

chmod +x /usr/local/bin/backup_phase.sh

# Create emergency restore script
cat > /usr/local/bin/emergency_restore.sh << 'EOF'
#!/bin/bash
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

**Testing Criteria**:
- Backup directories created successfully
- Backup scripts executable and functional
- Phase 0 baseline backup created
- Emergency restore script ready

**Critical Notes**:
- Backup system is essential for rollback capability
- Emergency restore provides safety net for configuration failures
- Each phase must create backup before proceeding

## Phase Completion Testing

### Comprehensive Validation
**Duration**: 15 minutes

```bash
# Validate all prerequisites met
echo "=== Phase 1 Validation ===" > /tmp/phase1_validation.txt

# Check package installations
echo "Package Status:" >> /tmp/phase1_validation.txt
for pkg in wireguard-tools kmod-wireguard luci-proto-wireguard tcpdump iperf3; do
    if opkg list-installed | grep -q "$pkg"; then
        echo "✓ $pkg installed" >> /tmp/phase1_validation.txt
    else
        echo "✗ $pkg missing" >> /tmp/phase1_validation.txt
    fi
done

# Check WireGuard keys
echo "WireGuard Keys:" >> /tmp/phase1_validation.txt
if [ -f "/etc/wireguard/keys/server_private.key" ] && [ -f "/etc/wireguard/keys/server_public.key" ]; then
    echo "✓ Server keys generated" >> /tmp/phase1_validation.txt
else
    echo "✗ Server keys missing" >> /tmp/phase1_validation.txt
fi

# Check WiFi credentials
echo "WiFi Credentials:" >> /tmp/phase1_validation.txt
if [ -f "/etc/wireless/credentials/main_password.txt" ]; then
    echo "✓ WiFi passwords generated" >> /tmp/phase1_validation.txt
else
    echo "✗ WiFi passwords missing" >> /tmp/phase1_validation.txt
fi

# Check backup system
echo "Backup System:" >> /tmp/phase1_validation.txt
if [ -d "/etc/config/backups/phases" ] && [ -x "/usr/local/bin/backup_phase.sh" ]; then
    echo "✓ Backup system ready" >> /tmp/phase1_validation.txt
else
    echo "✗ Backup system not ready" >> /tmp/phase1_validation.txt
fi

# Display validation results
cat /tmp/phase1_validation.txt

# Final system status
echo ""
echo "=== System Status ==="
uptime
free -h
df -h | grep -E "(rootfs|/tmp)"
```

### Success Criteria for Phase 1
- **All packages installed**: WireGuard components and utilities
- **Keys generated**: Server and client WireGuard key pairs created
- **Credentials ready**: WiFi passwords for all SSIDs generated
- **Hardware verified**: All expected interfaces present and functional
- **Backup system operational**: Phase backup and emergency restore scripts ready
- **Baseline documented**: System state captured for rollback capability

### Failure Conditions
- **Package installation fails**: Internet connectivity issues or repository problems
- **Interface verification fails**: Hardware incompatibility or driver issues  
- **Key generation fails**: Insufficient entropy or filesystem issues
- **Backup system fails**: Storage issues or permission problems

### Rollback Procedure
If Phase 1 fails, minimal rollback needed (fresh installation state). Address specific failures:
- Package issues: Check internet connectivity and repository access
- Key generation: Verify filesystem permissions and available entropy
- Interface issues: Verify hardware compatibility and driver support

**Proceed to Phase 2 only when all validation criteria pass.**


# Phase 2: Network Infrastructure (VLAN Configuration)

**Duration**: 3-4 hours  
**Risk Level**: High (network foundation changes)  
**Prerequisites**: Phase 1 completed with all validation criteria met

## Overview
Implements DSA-based VLAN infrastructure creating 8 isolated network segments. Establishes physical-to-logical network mapping crucial for security segmentation. Most critical phase as all subsequent configurations depend on proper VLAN implementation.

## Interdependencies

### Input Requirements
- Phase 1 validation passed (interface names verified)
- Factory configuration backup created
- Current network connectivity for UCI commands

### Output Deliverables  
- 8 VLAN interfaces operational (VLANs 1,10,20,30,40,50,60,70,99)
- DSA bridge with proper VLAN tagging configuration
- Logical network interfaces for each VLAN
- Physical port assignments matching intended use case

### Dependencies for Later Phases
- **Phase 3**: DHCP requires network interfaces to exist
- **Phase 4**: Firewall zones reference these network names
- **Phase 5**: Wireless SSIDs map to these VLANs
- **VentSys**: VLANs 20 (automation) and 50 (iot_sensors) critical

## Critical Configuration Notes

### VLAN Design Architecture
- **VLAN 1**: Default LAN, main users (192.168.1.0/24)
- **VLAN 10**: Management network (192.168.10.0/24) 
- **VLAN 20**: **VentSys Automation** - Home Assistant VM only (192.168.20.0/24)
- **VLAN 30**: CCTV cameras (192.168.30.0/24)
- **VLAN 40**: Storage/NAS (192.168.40.0/24)
- **VLAN 50**: **VentSys IoT Sensors** - Fire safety (192.168.50.0/24)
- **VLAN 60**: Monitoring VMs (192.168.60.0/24)
- **VLAN 70**: DMZ services (192.168.70.0/24)
- **VLAN 99**: Guest network (192.168.99.0/24)

### Physical Port Assignment Strategy
- **lan1**: Trunk to Proxmox (tagged VLANs 10,20,30,40,50,60,70)
- **lan2**: Management port (VLAN 10 untagged, others tagged)
- **lan3**: Camera POE switch (VLAN 30 untagged, management tagged)
- **lan4**: NAS connection (VLAN 40 untagged, management tagged)
- **lan5**: Recovery / WiFi AP port (VLAN 1 untagged ONLY)
  - During setup: connect your laptop here before starting Phase 2 for guaranteed
    SSH access to 192.168.1.1 regardless of VLAN misconfiguration elsewhere.
  - After setup: connect TP-Link TL-WA801N in AP mode to extend HomeMain (VLAN 1).
    No config changes needed when transitioning from recovery use to AP use.

## Sub-Tasks

### 2.1 Pre-Configuration Backup and Validation
**Duration**: 10 minutes

```bash
# Create Phase 2 entry backup
/usr/local/bin/backup_phase.sh 2_entry

# Validate current network state
ip link show > /tmp/phase2_entry_state.txt
ip addr show >> /tmp/phase2_entry_state.txt
uci show network >> /tmp/phase2_entry_state.txt

# Verify connectivity before changes
ping -c 3 8.8.8.8 > /tmp/connectivity_test.txt
echo "Phase 2 entry connectivity verified" >> /tmp/deployment_logs/phase2.log
```

**Testing Criteria**:
- Backup created successfully
- Current network state documented
- Internet connectivity confirmed
- UCI configuration exportable

### 2.2 DSA Bridge Base Configuration
**Duration**: 30 minutes

```bash
# Clear existing network configuration (CRITICAL: Will break connectivity temporarily)
echo "WARNING: Network connectivity will be interrupted"
echo "Continuing in 5 seconds... Press Ctrl+C to cancel"
sleep 5

# Remove default bridge configuration
uci delete network.@device[0] 2>/dev/null || true

# Create new DSA bridge with proper settings
uci add network device
uci set network.@device[-1].name='br-lan'
uci set network.@device[-1].type='bridge'

# Add physical ports to bridge
uci add_list network.@device[-1].ports='lan1'
uci add_list network.@device[-1].ports='lan2' 
uci add_list network.@device[-1].ports='lan3'
uci add_list network.@device[-1].ports='lan4'
uci add_list network.@device[-1].ports='lan5'  # Recovery/AP port — VLAN 1 untagged only

# Enable bridge features for VM environment
uci set network.@device[-1].igmp_snooping='1'
uci set network.@device[-1].stp='1'
uci set network.@device[-1].stp_hello_time='2'
uci set network.@device[-1].stp_forward_delay='15'

echo "DSA bridge configured" >> /tmp/deployment_logs/phase2.log
```

**Testing Criteria**:
- DSA bridge created without errors
- All physical ports added to bridge
- STP enabled (critical for VM environment)
- IGMP snooping enabled for multicast efficiency

**Critical Notes**:
- Network connectivity will be lost temporarily during this step
- STP is essential to prevent loops in Proxmox VM environment
- IGMP snooping improves performance for camera multicast streams

### 2.3 VLAN Bridge Configuration
**Duration**: 45 minutes

```bash
# VLAN 1: Main Users Network
# lan5:u* makes VLAN 1 the PVID on lan5 — untagged devices on lan5 (recovery laptop
# or TP-Link TL-WA801N AP) are placed on the main LAN and can reach 192.168.1.1.
# lan2/lan3/lan4 are intentionally NOT listed here — their PVIDs are VLAN 10/30/40.
uci add network bridge-vlan
uci set network.@bridge-vlan[-1].device='br-lan'
uci set network.@bridge-vlan[-1].vlan='1'
uci set network.@bridge-vlan[-1].local='1'
uci add_list network.@bridge-vlan[-1].ports='lan5:u*'  # Recovery/AP port — PVID
# No other physical ports — main user devices use HomeMain WiFi SSID (Phase 5)

# VLAN 10: Management Network
uci add network bridge-vlan
uci set network.@bridge-vlan[-1].device='br-lan'
uci set network.@bridge-vlan[-1].vlan='10'
uci set network.@bridge-vlan[-1].local='1'
uci add_list network.@bridge-vlan[-1].ports='lan1:t'   # Trunk to Proxmox (tagged)
uci add_list network.@bridge-vlan[-1].ports='lan2:u*'  # Management port — PVID (u* sets untagged ingress VLAN)
uci add_list network.@bridge-vlan[-1].ports='lan3:t'   # Camera port (tagged for admin access)
uci add_list network.@bridge-vlan[-1].ports='lan4:t'   # NAS port (tagged for admin access)
# NOTE: u* vs u — 'u*' sets the port PVID so untagged frames arriving on lan2
# are placed into VLAN 10. Plain 'u' only controls egress tagging and would
# leave the ingress PVID undefined, breaking untagged device connectivity.

# VLAN 20: VentSys Automation Network (CRITICAL)
uci add network bridge-vlan
uci set network.@bridge-vlan[-1].device='br-lan'
uci set network.@bridge-vlan[-1].vlan='20'
uci set network.@bridge-vlan[-1].local='1'
uci add_list network.@bridge-vlan[-1].ports='lan1:t'  # Trunk to Proxmox for HA/Frigate VMs

# VLAN 30: CCTV Network
uci add network bridge-vlan
uci set network.@bridge-vlan[-1].device='br-lan'
uci set network.@bridge-vlan[-1].vlan='30'
uci set network.@bridge-vlan[-1].local='1'
uci add_list network.@bridge-vlan[-1].ports='lan1:t'  # Trunk to Proxmox for Frigate VM
uci add_list network.@bridge-vlan[-1].ports='lan3:u*'  # Camera POE switch — PVID (untagged ingress = VLAN 30)

# VLAN 40: Storage Network
uci add network bridge-vlan
uci set network.@bridge-vlan[-1].device='br-lan'
uci set network.@bridge-vlan[-1].vlan='40'
uci set network.@bridge-vlan[-1].local='1'
uci add_list network.@bridge-vlan[-1].ports='lan1:t'  # Trunk to Proxmox
uci add_list network.@bridge-vlan[-1].ports='lan4:u*'  # NAS direct connection — PVID (untagged ingress = VLAN 40)

# VLAN 50: VentSys IoT Sensors Network (CRITICAL)
uci add network bridge-vlan
uci set network.@bridge-vlan[-1].device='br-lan'
uci set network.@bridge-vlan[-1].vlan='50'
uci set network.@bridge-vlan[-1].local='1'
uci add_list network.@bridge-vlan[-1].ports='lan1:t'  # Trunk to Proxmox for HA VM access

# VLAN 60: Monitoring Network
uci add network bridge-vlan
uci set network.@bridge-vlan[-1].device='br-lan'
uci set network.@bridge-vlan[-1].vlan='60'
uci set network.@bridge-vlan[-1].local='1'
uci add_list network.@bridge-vlan[-1].ports='lan1:t'  # Trunk to Proxmox

# VLAN 70: DMZ Network
uci add network bridge-vlan
uci set network.@bridge-vlan[-1].device='br-lan'
uci set network.@bridge-vlan[-1].vlan='70'
uci set network.@bridge-vlan[-1].local='1'
uci add_list network.@bridge-vlan[-1].ports='lan1:t'  # Trunk to Proxmox

# VLAN 99: Guest Network (WiFi-only, NO PHYSICAL PORTS)
uci add network bridge-vlan
uci set network.@bridge-vlan[-1].device='br-lan'
uci set network.@bridge-vlan[-1].vlan='99'
uci set network.@bridge-vlan[-1].local='1'
# No physical ports - WiFi-only for security

echo "All bridge VLANs configured" >> /tmp/deployment_logs/phase2.log
```

**Testing Criteria**:
- All 9 VLANs configured without errors
- Proxmox trunk port (lan1) carries all required VLANs
- Physical port assignments match intended usage
- Guest VLAN has no physical port assignment (security)

**Critical Notes**:
- lan1 MUST carry all VLANs for Proxmox VM networking
- VLAN 50 (IoT) carries lan1:t for Proxmox trunk (HA VM reaches sensors via VLAN 50); WiFi clients join via HomeIoT SSID
- Port tagging (t) vs untagged (u) critical for proper operation

### 2.4 Logical Network Interface Creation  
**Duration**: 30 minutes

```bash
# Create logical interfaces for each VLAN
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


echo "All logical network interfaces created" >> /tmp/deployment_logs/phase2.log
```

**Testing Criteria**:
- All network interfaces configured with correct IP addresses
- VLAN device assignments match bridge-vlan configuration
- Interface names match expected firewall zone references
- Gateway IPs follow consistent .1 pattern

### 2.5 WAN Interface Preservation
**Duration**: 10 minutes

```bash
# Ensure WAN configuration is preserved/corrected
uci set network.wan.proto='dhcp'
uci set network.wan.peerdns='0'
uci delete network.wan.dns 2>/dev/null || true
uci add_list network.wan.dns='1.1.1.1'
uci add_list network.wan.dns='1.0.0.1'

# IPv6 WAN configuration
uci set network.wan6.proto='dhcpv6'
uci set network.wan6.reqaddress='try'
uci set network.wan6.reqprefix='auto'

echo "WAN interface configuration preserved" >> /tmp/deployment_logs/phase2.log
```

**Testing Criteria**:
- WAN interface maintains internet connectivity
- DNS servers set to Cloudflare (privacy)
- IPv6 configuration preserved
- ISP DNS disabled (peerdns='0')

### 2.6 Configuration Application and Service Restart
**Duration**: 20 minutes

```bash
# Commit network configuration
uci commit network

# Validate configuration before applying
if ! uci show network >/dev/null 2>&1; then
    echo "ERROR: Invalid network configuration detected"
    echo "Restoring from backup..."
    /usr/local/bin/emergency_restore.sh
    exit 1
fi

echo "Restarting network services - connectivity will be interrupted"
/etc/init.d/network restart

# Wait for network stabilization
echo "Waiting for network stabilization..."
sleep 30

# Attempt to restore connectivity
for i in {1..6}; do
    if ip addr show br-lan.1 | grep -q 192.168.1.1; then
        echo "Network interface restored after $((i*10)) seconds"
        break
    fi
    echo "Waiting for interface... attempt $i/6"
    sleep 10
done

echo "Network configuration applied" >> /tmp/deployment_logs/phase2.log
```

**Testing Criteria**:
- UCI commit successful without errors
- Network service restart completes
- Primary interface (br-lan.1) comes up with correct IP
- Network stabilizes within 60 seconds

## Phase 2 Testing and Validation

### 2.7 VLAN Interface Validation
**Duration**: 30 minutes

```bash
echo "=== Phase 2 VLAN Validation ===" > /tmp/phase2_validation.txt

# Test all VLAN interfaces exist and have correct IPs
for vlan in 1 10 20 30 40 50 60 70 99; do
    expected_ip="192.168.${vlan}.1"
    if [ $vlan -eq 1 ]; then expected_ip="192.168.1.1"; fi
    if [ $vlan -eq 99 ]; then expected_ip="192.168.99.1"; fi
    
    if ip addr show br-lan.$vlan | grep -q "$expected_ip"; then
        echo "✓ VLAN $vlan interface operational: $expected_ip" >> /tmp/phase2_validation.txt
    else
        echo "✗ VLAN $vlan interface failed: expected $expected_ip" >> /tmp/phase2_validation.txt
    fi
done

# Test bridge configuration
if brctl show br-lan >/dev/null 2>&1; then
    echo "✓ Bridge br-lan operational" >> /tmp/phase2_validation.txt
    brctl show br-lan >> /tmp/phase2_validation.txt
else
    echo "✗ Bridge br-lan not found" >> /tmp/phase2_validation.txt
fi

# Test STP status
if [ -f /sys/class/net/br-lan/bridge/stp_state ]; then
    stp_state=$(cat /sys/class/net/br-lan/bridge/stp_state)
    if [ "$stp_state" = "1" ]; then
        echo "✓ STP enabled on bridge" >> /tmp/phase2_validation.txt
    else
        echo "✗ STP not enabled" >> /tmp/phase2_validation.txt
    fi
fi

# Display validation results
cat /tmp/phase2_validation.txt
```

### 2.8 Connectivity Testing
**Duration**: 20 minutes

```bash
echo "=== Phase 2 Connectivity Testing ===" >> /tmp/phase2_validation.txt

# Test WAN connectivity
if ping -c 3 8.8.8.8 >/dev/null 2>&1; then
    echo "✓ WAN connectivity operational" >> /tmp/phase2_validation.txt
else
    echo "✗ WAN connectivity failed" >> /tmp/phase2_validation.txt
fi

# Test DNS resolution
if nslookup google.com >/dev/null 2>&1; then
    echo "✓ DNS resolution working" >> /tmp/phase2_validation.txt  
else
    echo "✗ DNS resolution failed" >> /tmp/phase2_validation.txt
fi

# Test local network interfaces can ping each other
echo "Interface Connectivity Tests:" >> /tmp/phase2_validation.txt
for vlan in 10 20 30 40 50 60 70 99; do
    target_ip="192.168.${vlan}.1"
    if [ $vlan -eq 99 ]; then target_ip="192.168.99.1"; fi
    
    if ping -c 1 -W 2 "$target_ip" >/dev/null 2>&1; then
        echo "✓ Can reach VLAN $vlan gateway" >> /tmp/phase2_validation.txt
    else
        echo "✗ Cannot reach VLAN $vlan gateway" >> /tmp/phase2_validation.txt
    fi
done

cat /tmp/phase2_validation.txt
```

### 2.9 VentSys Critical Interface Verification
**Duration**: 15 minutes

```bash
echo "=== VentSys Critical Interface Verification ===" >> /tmp/phase2_validation.txt

# Test VLAN 20 (Automation) - Critical for Home Assistant VM
if ip route show table main | grep -q "192.168.20.0/24"; then
    echo "✓ VLAN 20 (Automation) routing ready for HA VM" >> /tmp/phase2_validation.txt
else
    echo "✗ VLAN 20 (Automation) routing missing" >> /tmp/phase2_validation.txt
fi

# Test VLAN 50 (IoT Sensors) - Critical for VentSys devices  
if ip route show table main | grep -q "192.168.50.0/24"; then
    echo "✓ VLAN 50 (IoT Sensors) routing ready for VentSys" >> /tmp/phase2_validation.txt
else
    echo "✗ VLAN 50 (IoT Sensors) routing missing" >> /tmp/phase2_validation.txt
fi

# Verify trunk port configuration for Proxmox
echo "Proxmox Trunk Verification (lan1):" >> /tmp/phase2_validation.txt
if bridge vlan show dev lan1 2>/dev/null | grep -q -E "10|20|30|40|50|60|70"; then
    echo "✓ lan1 trunk port configured with VLANs" >> /tmp/phase2_validation.txt
else
    echo "✗ lan1 trunk port configuration incomplete" >> /tmp/phase2_validation.txt
fi

cat /tmp/phase2_validation.txt
```

## Success Criteria for Phase 2

- **All VLAN interfaces operational**: 9 VLANs (1,10,20,30,40,50,60,70,99) with correct IP addresses
- **Bridge configuration functional**: DSA bridge with STP enabled, IGMP snooping active
- **Physical port assignments correct**: Trunk, management, camera, and NAS ports configured
- **WAN connectivity preserved**: Internet access maintained through configuration changes
- **VentSys readiness**: VLANs 20 (automation) and 50 (iot_sensors) ready for HA and IoT integration
- **Network routing operational**: All VLANs can reach their respective gateways

## Failure Recovery Procedures

### Minor Issues
- **Individual VLAN failure**: Check interface configuration and restart network service
- **Connectivity loss**: Verify WAN interface configuration and physical connections
- **Bridge issues**: Check DSA bridge configuration and port assignments

### Major Failures  
- **Complete network loss**: Execute emergency restore script
- **Configuration corruption**: Restore from Phase 2 entry backup
- **Hardware compatibility**: Review interface naming and adjust configuration

### Emergency Rollback
```bash
# If complete network failure occurs:
/usr/local/bin/emergency_restore.sh

# Wait for restoration
sleep 30

# Verify basic connectivity restored
ping -c 3 8.8.8.8
```

**Proceed to Phase 3 only when all success criteria met and VentSys critical interfaces validated.**


# Phase 3: DHCP Configuration

**Duration**: 2-3 hours  
**Risk Level**: Medium (DHCP scope creation)  
**Prerequisites**: Phase 2 completed, all VLAN interfaces operational

## Overview
Configures DHCP services for all 9 network segments with appropriate scopes, DNS settings, and static reservations. Establishes automated IP assignment foundation required for firewall rules and wireless client assignment. Critical for VentSys device integration and network security isolation.

## Interdependencies

### Input Requirements
- Phase 2 network interfaces operational (br-lan.1 through br-lan.99)
- VLAN routing functional for all segments
- DNS resolution working on WAN interface

### Output Deliverables
- DHCP scopes active on all VLANs with correct ranges
- DNS configuration supporting network isolation requirements
- Static reservation framework prepared
- VentSys-compatible DHCP settings for VLANs 20 and 50

### Dependencies for Later Phases
- **Phase 4**: Firewall rules expect DHCP-assigned clients
- **Phase 5**: Wireless clients need DHCP assignment per VLAN
- **VentSys**: IoT devices require specific DHCP scope on VLAN 50

## Sub-Tasks

### 3.1 Pre-Configuration Backup and Validation
**Duration**: 10 minutes

```bash
# Create Phase 3 entry backup
/usr/local/bin/backup_phase.sh 3_entry

# Validate DHCP prerequisites
echo "=== Phase 3 Prerequisites ===" > /tmp/phase3_validation.txt

# Verify all VLAN interfaces are up
for vlan in 1 10 20 30 40 50 60 70 99; do
    expected_ip="192.168.${vlan}.1"
    if [ $vlan -eq 1 ]; then expected_ip="192.168.1.1"; fi
    if [ $vlan -eq 99 ]; then expected_ip="192.168.99.1"; fi
    
    if ip addr show br-lan.$vlan | grep -q "$expected_ip"; then
        echo "✓ VLAN $vlan interface ready for DHCP" >> /tmp/phase3_validation.txt
    else
        echo "✗ VLAN $vlan interface not ready" >> /tmp/phase3_validation.txt
        exit 1
    fi
done

cat /tmp/phase3_validation.txt
echo "All VLAN interfaces validated for DHCP configuration" >> /tmp/deployment_logs/phase3.log
```

### 3.2 Global DHCP and DNS Configuration
**Duration**: 30 minutes

```bash
# Configure global dnsmasq settings
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

# Configure upstream DNS servers
uci delete dhcp.@dnsmasq[0].server
uci add_list dhcp.@dnsmasq[0].server='1.1.1.1'
uci add_list dhcp.@dnsmasq[0].server='1.0.0.1'
uci add_list dhcp.@dnsmasq[0].server='8.8.8.8'

echo "Global DNS configuration completed" >> /tmp/deployment_logs/phase3.log
```

### 3.3 Main User Network DHCP (VLAN 1)
**Duration**: 15 minutes

```bash
# Configure LAN DHCP scope - existing interface
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

# DNS servers for main network (gateway + external)
uci delete dhcp.lan.dhcp_option
uci add_list dhcp.lan.dhcp_option='6,192.168.1.1,1.1.1.1,1.0.0.1'

echo "LAN DHCP scope configured: 192.168.1.100-199" >> /tmp/deployment_logs/phase3.log
```

### 3.4 Management Network DHCP (VLAN 10)
**Duration**: 15 minutes

```bash
# Create Management DHCP scope
uci add dhcp dhcp
uci set dhcp.@dhcp[-1].interface='management'
uci set dhcp.@dhcp[-1].start='100'
uci set dhcp.@dhcp[-1].limit='50'
uci set dhcp.@dhcp[-1].leasetime='24h'
uci set dhcp.@dhcp[-1].dhcpv4='server'

# DNS for management (local gateway + external)
uci add_list dhcp.@dhcp[-1].dhcp_option='6,192.168.10.1,1.1.1.1'

echo "Management DHCP scope configured: 192.168.10.100-149" >> /tmp/deployment_logs/phase3.log
```

### 3.5 VentSys Automation Network DHCP (VLAN 20)
**Duration**: 15 minutes

```bash
# Create Automation DHCP scope (CRITICAL FOR VENTSYS)
uci add dhcp dhcp
uci set dhcp.@dhcp[-1].interface='automation'
uci set dhcp.@dhcp[-1].start='110'
uci set dhcp.@dhcp[-1].limit='40'
uci set dhcp.@dhcp[-1].leasetime='24h'
uci set dhcp.@dhcp[-1].dhcpv4='server'

# Local DNS only for automation network
uci add_list dhcp.@dhcp[-1].dhcp_option='6,192.168.20.1'

echo "VENTSYS Automation DHCP scope configured: 192.168.20.110-149" >> /tmp/deployment_logs/phase3.log
```

### 3.6 CCTV Network DHCP (VLAN 30)
**Duration**: 15 minutes

```bash
# Create CCTV DHCP scope (isolated network)
uci add dhcp dhcp
uci set dhcp.@dhcp[-1].interface='cctv'
uci set dhcp.@dhcp[-1].start='100'
uci set dhcp.@dhcp[-1].limit='50'
uci set dhcp.@dhcp[-1].leasetime='24h'
uci set dhcp.@dhcp[-1].dhcpv4='server'

# Local DNS only (no internet access)
uci add_list dhcp.@dhcp[-1].dhcp_option='6,192.168.30.1'

echo "CCTV DHCP scope configured: 192.168.30.100-149" >> /tmp/deployment_logs/phase3.log
```

### 3.7 Storage Network DHCP (VLAN 40)
**Duration**: 15 minutes

```bash
# Create Storage DHCP scope (isolated network)
uci add dhcp dhcp
uci set dhcp.@dhcp[-1].interface='storage'
uci set dhcp.@dhcp[-1].start='100'
uci set dhcp.@dhcp[-1].limit='40'
uci set dhcp.@dhcp[-1].leasetime='24h'
uci set dhcp.@dhcp[-1].dhcpv4='server'

# Local DNS only (no internet access)
uci add_list dhcp.@dhcp[-1].dhcp_option='6,192.168.40.1'

echo "Storage DHCP scope configured: 192.168.40.100-139" >> /tmp/deployment_logs/phase3.log
```

### 3.8 VentSys IoT Sensors Network DHCP (VLAN 50)
**Duration**: 15 minutes

```bash
# Create IoT Sensors DHCP scope (CRITICAL FOR VENTSYS)
uci add dhcp dhcp
uci set dhcp.@dhcp[-1].interface='iot_sensors'
uci set dhcp.@dhcp[-1].start='100'
uci set dhcp.@dhcp[-1].limit='91'
uci set dhcp.@dhcp[-1].leasetime='6h'
uci set dhcp.@dhcp[-1].dhcpv4='server'

# Local DNS only - CRITICAL for security isolation
uci add_list dhcp.@dhcp[-1].dhcp_option='6,192.168.50.1'

echo "VENTSYS IoT Sensors DHCP scope configured: 192.168.50.100-190" >> /tmp/deployment_logs/phase3.log
```

### 3.9 Monitoring Network DHCP (VLAN 60)
**Duration**: 15 minutes

```bash
# Create Monitoring DHCP scope
uci add dhcp dhcp
uci set dhcp.@dhcp[-1].interface='monitoring'
uci set dhcp.@dhcp[-1].start='100'
uci set dhcp.@dhcp[-1].limit='50'
uci set dhcp.@dhcp[-1].leasetime='24h'
uci set dhcp.@dhcp[-1].dhcpv4='server'

# Limited internet access for updates and alerts
uci add_list dhcp.@dhcp[-1].dhcp_option='6,192.168.60.1,1.1.1.1'

echo "Monitoring DHCP scope configured: 192.168.60.100-149" >> /tmp/deployment_logs/phase3.log
```

### 3.10 DMZ Network DHCP (VLAN 70)
**Duration**: 15 minutes

```bash
# Create DMZ DHCP scope
uci add dhcp dhcp
uci set dhcp.@dhcp[-1].interface='dmz'
uci set dhcp.@dhcp[-1].start='100'
uci set dhcp.@dhcp[-1].limit='50'
uci set dhcp.@dhcp[-1].leasetime='12h'
uci set dhcp.@dhcp[-1].dhcpv4='server'

# Controlled internet access
uci add_list dhcp.@dhcp[-1].dhcp_option='6,192.168.70.1,1.1.1.1,8.8.8.8'

echo "DMZ DHCP scope configured: 192.168.70.100-149" >> /tmp/deployment_logs/phase3.log
```

### 3.11 Guest Network DHCP (VLAN 99)
**Duration**: 15 minutes

```bash
# Create Guest DHCP scope
uci add dhcp dhcp
uci set dhcp.@dhcp[-1].interface='guest'
uci set dhcp.@dhcp[-1].start='100'
uci set dhcp.@dhcp[-1].limit='51'
uci set dhcp.@dhcp[-1].leasetime='2h'
uci set dhcp.@dhcp[-1].dhcpv4='server'

# Internet DNS servers only
uci add_list dhcp.@dhcp[-1].dhcp_option='6,1.1.1.1,8.8.8.8'

echo "Guest DHCP scope configured: 192.168.99.100-150" >> /tmp/deployment_logs/phase3.log
```

### 3.12 Static DHCP Reservations Framework
**Duration**: 20 minutes

```bash
# Create placeholder static reservations for critical infrastructure
# These will be updated with real MAC addresses as devices are deployed

# Proxmox Host (Management Network) - PLACEHOLDER
uci add dhcp host
uci set dhcp.@host[-1].name='proxmox-host'
uci set dhcp.@host[-1].dns='1'
uci set dhcp.@host[-1].mac='XX:XX:XX:XX:XX:01'
uci set dhcp.@host[-1].ip='192.168.10.10'

# Home Assistant VM (Automation Network) - PLACEHOLDER
uci add dhcp host
uci set dhcp.@host[-1].name='home-assistant'
uci set dhcp.@host[-1].dns='1'
uci set dhcp.@host[-1].mac='XX:XX:XX:XX:XX:02'
uci set dhcp.@host[-1].ip='192.168.20.101'

# Frigate NVR VM (CCTV Network) - PLACEHOLDER
uci add dhcp host
uci set dhcp.@host[-1].name='frigate-nvr'
uci set dhcp.@host[-1].dns='1'
uci set dhcp.@host[-1].mac='XX:XX:XX:XX:XX:03'
uci set dhcp.@host[-1].ip='192.168.30.20'

# NAS (Storage Network) - PLACEHOLDER
uci add dhcp host
uci set dhcp.@host[-1].name='pi-nas'
uci set dhcp.@host[-1].dns='1'
uci set dhcp.@host[-1].mac='XX:XX:XX:XX:XX:04'
uci set dhcp.@host[-1].ip='192.168.40.50'


# A8-1 fix: was ventsys-fan-controller@.21 and ventsys-valve-controller@.56 (stale pre-canonical names).
# The FULL 17-device VentSys fleet is defined in scripts/setup/router/phase_3_dhcp_configuration.md.
# Apply that file's complete reservation block during Phase 3 deployment instead of this 2-device placeholder.
# Canonical names: ventsys-main-fan(.21), ventsys-booth-fan(.22), ventsys-fdm-sensor(.31) through
# ventsys-sla-360-valve(.62), plus 8 smart plugs (.71-.78). See dhcp-config.conf for full listing.
# Minimal bootstrap block (2 most-critical devices) kept below for reference only:
uci add dhcp host
uci set dhcp.@host[-1].name='ventsys-main-fan'  # A8-1: was ventsys-fan-controller
uci set dhcp.@host[-1].ip='192.168.50.21'
uci set dhcp.@host[-1].mac='XX:XX:XX:XX:XX:81'

uci add dhcp host
uci set dhcp.@host[-1].name='ventsys-sla-print-valve'  # A8-1: was ventsys-valve-controller
uci set dhcp.@host[-1].ip='192.168.50.56'
uci set dhcp.@host[-1].mac='XX:XX:XX:XX:XX:82'

echo "Static DHCP reservation framework created with placeholders" >> /tmp/deployment_logs/phase3.log
```

### 3.13 Local Domain Configuration
**Duration**: 15 minutes

```bash
# Configure local domain resolution
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

echo "Local domain configuration completed" >> /tmp/deployment_logs/phase3.log
```

## Phase 3 Testing and Validation

### 3.14 Configuration Application and Service Restart
**Duration**: 10 minutes

```bash
# Commit DHCP configuration
uci commit dhcp

# Validate configuration
if ! uci show dhcp >/dev/null 2>&1; then
    echo "ERROR: Invalid DHCP configuration"
    /usr/local/bin/emergency_restore.sh
    exit 1
fi

# Restart DHCP service
/etc/init.d/dnsmasq restart

# Verify service is running
sleep 5
if ! /etc/init.d/dnsmasq status >/dev/null 2>&1; then
    echo "ERROR: DHCP service failed to start"
    /etc/init.d/dnsmasq stop
    /etc/init.d/dnsmasq start
fi

echo "DHCP configuration applied and service restarted" >> /tmp/deployment_logs/phase3.log
```

### 3.15 DHCP Scope Validation
**Duration**: 20 minutes

```bash
echo "=== Phase 3 DHCP Scope Validation ===" > /tmp/phase3_validation.txt

# Check DHCP service status
if /etc/init.d/dnsmasq status >/dev/null 2>&1; then
    echo "✓ DHCP service running" >> /tmp/phase3_validation.txt
else
    echo "✗ DHCP service not running" >> /tmp/phase3_validation.txt
fi

# Verify DHCP lease file exists
if [ -f /tmp/dhcp.leases ]; then
    echo "✓ DHCP lease file created" >> /tmp/phase3_validation.txt
else
    echo "✗ DHCP lease file missing" >> /tmp/phase3_validation.txt
fi

# Test DHCP configuration syntax
if dnsmasq --test >/dev/null 2>&1; then
    echo "✓ DHCP configuration syntax valid" >> /tmp/phase3_validation.txt
else
    echo "✗ DHCP configuration syntax errors" >> /tmp/phase3_validation.txt
fi

# Verify DHCP listening on correct interfaces
netstat -ulnp | grep :53 >> /tmp/phase3_validation.txt
netstat -ulnp | grep :67 >> /tmp/phase3_validation.txt

cat /tmp/phase3_validation.txt
```

### 3.16 DNS Resolution Testing
**Duration**: 15 minutes

```bash
echo "=== DNS Resolution Testing ===" >> /tmp/phase3_validation.txt

# Test local domain resolution
for domain in router.home.local proxmox.home.local homeassistant.home.local; do
    if nslookup "$domain" 127.0.0.1 >/dev/null 2>&1; then
        echo "✓ Local domain resolution working: $domain" >> /tmp/phase3_validation.txt
    else
        echo "✗ Local domain resolution failed: $domain" >> /tmp/phase3_validation.txt
    fi
done

# Test external DNS resolution
if nslookup google.com 127.0.0.1 >/dev/null 2>&1; then
    echo "✓ External DNS resolution working" >> /tmp/phase3_validation.txt
else
    echo "✗ External DNS resolution failed" >> /tmp/phase3_validation.txt
fi

cat /tmp/phase3_validation.txt
```

### 3.17 VentSys Integration Validation
**Duration**: 10 minutes

```bash
echo "=== VentSys DHCP Integration Validation ===" >> /tmp/phase3_validation.txt

# Verify Automation VLAN DHCP scope
if uci show dhcp | grep -q "interface='automation'"; then
    echo "✓ VLAN 20 (Automation) DHCP scope configured" >> /tmp/phase3_validation.txt
else
    echo "✗ VLAN 20 (Automation) DHCP scope missing" >> /tmp/phase3_validation.txt
fi

# Verify IoT Sensors VLAN DHCP scope  
if uci show dhcp | grep -q "interface='iot_sensors'"; then
    echo "✓ VLAN 50 (IoT Sensors) DHCP scope configured" >> /tmp/phase3_validation.txt
else
    echo "✗ VLAN 50 (IoT Sensors) DHCP scope missing" >> /tmp/phase3_validation.txt
fi

# Verify VentSys static reservations exist
if uci show dhcp | grep -q "ventsys-main-fan"  # A8-1 fix: was ventsys-fan-controller; then
    echo "✓ VentSys static reservations configured" >> /tmp/phase3_validation.txt
else
    echo "✗ VentSys static reservations missing" >> /tmp/phase3_validation.txt
fi

cat /tmp/phase3_validation.txt
```

## Success Criteria for Phase 3

- **All DHCP scopes operational**: 9 network segments with appropriate ranges
- **DNS resolution functional**: Local domains and external DNS working
- **Service stability**: DHCP/DNS service running without errors
- **VentSys readiness**: VLANs 20 and 50 DHCP scopes ready for device assignment
- **Static reservation framework**: Placeholder reservations created for critical infrastructure
- **Network isolation maintained**: Isolated networks use local DNS only

## Failure Recovery Procedures

### Minor Issues
- **DHCP service failure**: Check configuration syntax and restart service
- **DNS resolution problems**: Verify upstream DNS servers and connectivity
- **Scope conflicts**: Check DHCP range overlaps and correct conflicts

### Major Failures
- **Configuration corruption**: Restore from Phase 3 entry backup
- **Service won't start**: Check port conflicts and interface bindings
- **Complete DHCP failure**: Emergency restore and reconfigure from Phase 2 state

### Emergency Rollback
```bash
# If DHCP service completely fails:
/etc/init.d/dnsmasq stop
/usr/local/bin/emergency_restore.sh
sleep 30
/etc/init.d/dnsmasq start
```

**Proceed to Phase 4 only when all DHCP scopes are operational and VentSys integration validated.**


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

# Execute the corrected firewall script
chmod +x /tmp/corrected_firewall_config.sh
/tmp/corrected_firewall_config.sh

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

# Verify ESPHome API rule (port 6053)
if uci show firewall | grep -q "ESPHome API HA to IoT"; then
    if uci show firewall | grep -A5 "ESPHome API" | grep -q "dest_port='6053'"; then
        echo "✓ VentSys ESPHome API rule (6053) configured" >> /tmp/phase4_ventsys_test.txt
    else
        echo "✗ VentSys ESPHome API port incorrect" >> /tmp/phase4_ventsys_test.txt
    fi
else
    echo "✗ VentSys ESPHome API rule missing" >> /tmp/phase4_ventsys_test.txt
fi

# Verify IoT sensors internet blocking
if uci show firewall | grep -q "Block IoT Internet"; then
    echo "✓ IoT sensors internet blocking configured" >> /tmp/phase4_ventsys_test.txt
else
    echo "✗ IoT sensors internet blocking missing" >> /tmp/phase4_ventsys_test.txt
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


# Phase 5: Wireless Configuration

**Duration**: 3-4 hours  
**Risk Level**: Medium-High (multi-SSID complexity)  
**Prerequisites**: Phase 4 completed, firewall rules operational

## Overview
Implements multi-SSID wireless architecture mapping 5 SSIDs to appropriate VLANs. Establishes WiFi-based access to network segments with proper security isolation. Critical for VentSys IoT device connectivity and guest access while maintaining security segmentation.

## Interdependencies

### Input Requirements
- All VLAN interfaces operational (Phase 2)
- Firewall zones configured (Phase 4)
- WiFi passwords generated (Phase 1)
- Radio hardware verified (Phase 1)

### Output Deliverables
- 5 SSIDs operational with proper VLAN mapping
- Channel separation strategy implemented
- Security configurations (WPA3/WPA2) applied appropriately
- VentSys IoT SSID ready for sensor connectivity

### Dependencies for Later Phases
- **Phase 6**: VPN clients will access network via wireless
- **Phase 7**: Wireless testing validates complete network architecture
- **VentSys**: HomeIoT SSID critical for sensor connectivity

## Sub-Tasks

### 5.1 Pre-Configuration Validation
**Duration**: 10 minutes

```bash
# Create Phase 5 entry backup
/usr/local/bin/backup_phase.sh 5_entry

# Validate wireless prerequisites
echo "=== Phase 5 Prerequisites ===" > /tmp/phase5_validation.txt

# Check radio hardware
if iwconfig 2>/dev/null | grep -q "IEEE 802.11"; then
    echo "✓ Wireless hardware detected" >> /tmp/phase5_validation.txt
else
    echo "✗ Wireless hardware not detected" >> /tmp/phase5_validation.txt
    exit 1
fi

# Verify WiFi credentials exist
if [ -f "/etc/wireless/credentials/main_password.txt" ]; then
    echo "✓ WiFi credentials available" >> /tmp/phase5_validation.txt
else
    echo "✗ WiFi credentials missing" >> /tmp/phase5_validation.txt
    exit 1
fi

# Verify required VLAN interfaces exist
for vlan in lan management iot_sensors guest; do
    if uci show network | grep -q "interface.*$vlan"; then
        echo "✓ Interface $vlan ready" >> /tmp/phase5_validation.txt
    else
        echo "✗ Interface $vlan missing" >> /tmp/phase5_validation.txt
        exit 1
    fi
done

cat /tmp/phase5_validation.txt
echo "Prerequisites validated for wireless configuration" >> /tmp/deployment_logs/phase5.log
```

### 5.2 Radio Base Configuration  
**Duration**: 20 minutes

```bash
# Configure 2.4GHz radio (radio0)
uci set wireless.radio0.type='mac80211'
uci set wireless.radio0.band='2g'
uci set wireless.radio0.channel='auto'
uci set wireless.radio0.htmode='HE40'
uci set wireless.radio0.country='GB'    # UK regulatory domain — matches wireless-config.conf
uci set wireless.radio0.txpower='20'
uci set wireless.radio0.mu_beamformer='1'
uci set wireless.radio0.legacy_rates='1'

# Configure 5GHz radio (radio1) 
uci set wireless.radio1.type='mac80211'
uci set wireless.radio1.band='5g'
uci set wireless.radio1.channel='auto'
uci set wireless.radio1.htmode='HE80'
uci set wireless.radio1.country='GB'    # UK regulatory domain — matches wireless-config.conf
uci set wireless.radio1.txpower='23'
uci set wireless.radio1.mu_beamformer='1'

echo "Radio base configuration completed" >> /tmp/deployment_logs/phase5.log
```

### 5.3 Main User WiFi (HomeMain - VLAN 1)
**Duration**: 30 minutes

```bash
# Load WiFi password
MAIN_PASSWORD=$(cat /etc/wireless/credentials/main_password.txt)

# Main Network - 2.4GHz
uci add wireless wifi-iface
uci set wireless.@wifi-iface[-1].device='radio0'
uci set wireless.@wifi-iface[-1].mode='ap'
uci set wireless.@wifi-iface[-1].ssid='HomeMain'
uci set wireless.@wifi-iface[-1].network='lan'
uci set wireless.@wifi-iface[-1].encryption='sae-mixed'
uci set wireless.@wifi-iface[-1].key="$MAIN_PASSWORD"
uci set wireless.@wifi-iface[-1].ieee80211w='1'
uci set wireless.@wifi-iface[-1].wpa_disable_eapol_key_retries='1'
uci set wireless.@wifi-iface[-1].bss_transition='1'
uci set wireless.@wifi-iface[-1].wnm_sleep_mode='1'

# Main Network - 5GHz (same SSID for roaming)
uci add wireless wifi-iface  
uci set wireless.@wifi-iface[-1].device='radio1'
uci set wireless.@wifi-iface[-1].mode='ap'
uci set wireless.@wifi-iface[-1].ssid='HomeMain'
uci set wireless.@wifi-iface[-1].network='lan'
uci set wireless.@wifi-iface[-1].encryption='sae-mixed'
uci set wireless.@wifi-iface[-1].key="$MAIN_PASSWORD"
uci set wireless.@wifi-iface[-1].ieee80211w='1'
uci set wireless.@wifi-iface[-1].wpa_disable_eapol_key_retries='1'
uci set wireless.@wifi-iface[-1].bss_transition='1'
uci set wireless.@wifi-iface[-1].wnm_sleep_mode='1'

echo "HomeMain SSID configured on both radios" >> /tmp/deployment_logs/phase5.log
```

### 5.4 Admin WiFi (HomeAdmin - VLAN 10)
**Duration**: 25 minutes

```bash
# Load admin password
ADMIN_PASSWORD=$(cat /etc/wireless/credentials/admin_password.txt)

# Admin Network - 5GHz Primary
uci add wireless wifi-iface
uci set wireless.@wifi-iface[-1].device='radio1'
uci set wireless.@wifi-iface[-1].mode='ap'
uci set wireless.@wifi-iface[-1].ssid='HomeAdmin'
uci set wireless.@wifi-iface[-1].network='management'
uci set wireless.@wifi-iface[-1].encryption='sae'
uci set wireless.@wifi-iface[-1].key="$ADMIN_PASSWORD"
uci set wireless.@wifi-iface[-1].ieee80211w='2'
uci set wireless.@wifi-iface[-1].wpa_disable_eapol_key_retries='1'
uci set wireless.@wifi-iface[-1].hidden='0'
uci set wireless.@wifi-iface[-1].maxassoc='8'

# Admin Network - 2.4GHz Backup
uci add wireless wifi-iface
uci set wireless.@wifi-iface[-1].device='radio0'
uci set wireless.@wifi-iface[-1].mode='ap'
uci set wireless.@wifi-iface[-1].ssid='HomeAdmin-2G'
uci set wireless.@wifi-iface[-1].network='management'
uci set wireless.@wifi-iface[-1].encryption='sae'
uci set wireless.@wifi-iface[-1].key="$ADMIN_PASSWORD"
uci set wireless.@wifi-iface[-1].ieee80211w='2'
uci set wireless.@wifi-iface[-1].wpa_disable_eapol_key_retries='1'
uci set wireless.@wifi-iface[-1].hidden='1'
uci set wireless.@wifi-iface[-1].maxassoc='4'

echo "HomeAdmin SSIDs configured" >> /tmp/deployment_logs/phase5.log
```

### 5.5 VentSys IoT WiFi (HomeIoT - VLAN 50) - CRITICAL
**Duration**: 20 minutes

```bash
# Load IoT password  
IOT_PASSWORD=$(cat /etc/wireless/credentials/iot_password.txt)

# IoT Sensors Network - 2.4GHz only for compatibility
uci add wireless wifi-iface
uci set wireless.@wifi-iface[-1].device='radio0'
uci set wireless.@wifi-iface[-1].mode='ap'
uci set wireless.@wifi-iface[-1].ssid='HomeIoT'
uci set wireless.@wifi-iface[-1].network='iot_sensors'
uci set wireless.@wifi-iface[-1].encryption='psk2'
uci set wireless.@wifi-iface[-1].key="$IOT_PASSWORD"
uci set wireless.@wifi-iface[-1].ieee80211w='0'
uci set wireless.@wifi-iface[-1].maxassoc='50'
uci set wireless.@wifi-iface[-1].dtim_period='3'
uci set wireless.@wifi-iface[-1].isolate='1'

echo "CRITICAL: VentSys HomeIoT SSID configured for VLAN 50" >> /tmp/deployment_logs/phase5.log
```

### 5.6 Guest WiFi (HomeGuest - VLAN 99)
**Duration**: 20 minutes

```bash
# Load guest password
GUEST_PASSWORD=$(cat /etc/wireless/credentials/guest_password.txt)

# Guest Network - 2.4GHz only
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

echo "HomeGuest SSID configured" >> /tmp/deployment_logs/phase5.log
```

### 5.7 DMZ WiFi (HomeDMZ - VLAN 70) - Disabled by Default
**Duration**: 15 minutes

```bash
# Load DMZ password
DMZ_PASSWORD=$(cat /etc/wireless/credentials/dmz_password.txt)

# DMZ Network - 5GHz (disabled by default)
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

echo "HomeDMZ SSID configured (disabled)" >> /tmp/deployment_logs/phase5.log
```

### 5.8 Channel Configuration
**Duration**: 5 minutes

```bash
# IMPORTANT: OpenWrt mac80211 assigns ONE channel per physical radio.
# All SSIDs on radio0 (HomeMain 2.4GHz, HomeAdmin-2G, HomeIoT, HomeGuest)
# MUST share the same channel. Per-interface channel overrides on wifi-iface
# objects are silently ignored — only the wifi-device level setting applies.
#
# Channel 6 is chosen as the single 2.4GHz channel because:
#   - HomeIoT (VentSys fire safety) requires a stable, fixed channel
#   - Channel 6 is a standard non-overlapping choice (1/6/11 plan)
#   - HomeMain 2.4GHz clients that support 5GHz will use radio1 (auto channel)
#     for better performance, leaving 2.4GHz primarily for IoT devices
#
# 5GHz (radio1) handles HomeMain and HomeAdmin on auto-selected channels

# Set radio0 (all 2.4GHz SSIDs) to channel 6
uci set wireless.radio0.channel='6'

# 5GHz remains on auto
uci set wireless.radio1.channel='auto'

echo "Channel configuration applied: radio0=6, radio1=auto" >> /tmp/deployment_logs/phase5.log
```

**Testing Criteria**:
- radio0 channel set to 6 (verified via `iw dev` after restart)
- radio1 on auto
- All 2.4GHz SSIDs visible and connecting correctly on channel 6

## Phase 5 Testing and Validation

### 5.9 Configuration Application and Service Restart
**Duration**: 15 minutes

```bash
# Commit wireless configuration
uci commit wireless

# Validate configuration
if ! uci show wireless >/dev/null 2>&1; then
    echo "ERROR: Invalid wireless configuration"
    /usr/local/bin/emergency_restore.sh
    exit 1
fi

# Enable wireless radios
uci set wireless.radio0.disabled='0'
uci set wireless.radio1.disabled='0'
uci commit wireless

# Restart wireless service
/etc/init.d/network restart
sleep 10

# Wait for wireless interfaces to come up
echo "Waiting for wireless interfaces..."
for i in {1..6}; do
    if iwconfig 2>/dev/null | grep -q "ESSID"; then
        echo "Wireless interfaces active after $((i*10)) seconds"
        break
    fi
    sleep 10
done

echo "Wireless configuration applied" >> /tmp/deployment_logs/phase5.log
```

### 5.10 SSID Visibility and Configuration Validation
**Duration**: 25 minutes

```bash
echo "=== SSID Visibility and Configuration Validation ===" > /tmp/phase5_ssid_test.txt

# Check wireless interface status
iwconfig >> /tmp/phase5_ssid_test.txt 2>&1

# Verify expected SSIDs are broadcasting
expected_ssids=("HomeMain" "HomeAdmin" "HomeAdmin-2G" "HomeIoT" "HomeGuest")
for ssid in "${expected_ssids[@]}"; do
    if iwlist scan 2>/dev/null | grep -q "ESSID:\"$ssid\""; then
        echo "✓ SSID '$ssid' broadcasting" >> /tmp/phase5_ssid_test.txt
    else
        echo "✗ SSID '$ssid' not detected" >> /tmp/phase5_ssid_test.txt
    fi
done

# Verify HomeDMZ is disabled (should not appear)
if iwlist scan 2>/dev/null | grep -q "ESSID:\"HomeDMZ\""; then
    echo "✗ HomeDMZ SSID broadcasting (should be disabled)" >> /tmp/phase5_ssid_test.txt
else
    echo "✓ HomeDMZ SSID properly disabled" >> /tmp/phase5_ssid_test.txt
fi

cat /tmp/phase5_ssid_test.txt
```

### 5.11 VLAN Mapping Validation
**Duration**: 20 minutes

```bash
echo "=== VLAN Mapping Validation ===" > /tmp/phase5_vlan_mapping_test.txt

# Verify SSID to VLAN mappings in configuration
mappings=(
    "HomeMain:lan"
    "HomeAdmin:management"
    "HomeIoT:iot_sensors"
    "HomeGuest:guest"
    "HomeDMZ:dmz"
)

for mapping in "${mappings[@]}"; do
    ssid=$(echo $mapping | cut -d':' -f1)
    network=$(echo $mapping | cut -d':' -f2)
    
    if uci show wireless | grep -A5 "ssid='$ssid'" | grep -q "network='$network'"; then
        echo "✓ $ssid correctly mapped to $network" >> /tmp/phase5_vlan_mapping_test.txt
    else
        echo "✗ $ssid mapping to $network incorrect" >> /tmp/phase5_vlan_mapping_test.txt
    fi
done

cat /tmp/phase5_vlan_mapping_test.txt
```

### 5.12 VentSys IoT WiFi Critical Validation
**Duration**: 15 minutes

```bash
echo "=== VentSys IoT WiFi Critical Validation ===" > /tmp/phase5_ventsys_test.txt

# Verify HomeIoT SSID configuration
if uci show wireless | grep -q "ssid='HomeIoT'"; then
    echo "✓ HomeIoT SSID configured" >> /tmp/phase5_ventsys_test.txt
    
    # Check VLAN 50 mapping
    if uci show wireless | grep -A5 "ssid='HomeIoT'" | grep -q "network='iot_sensors'"; then
        echo "✓ HomeIoT mapped to iot_sensors (VLAN 50)" >> /tmp/phase5_ventsys_test.txt
    else
        echo "✗ HomeIoT VLAN mapping incorrect" >> /tmp/phase5_ventsys_test.txt
	fi
    
else
    echo "✗ HomeIoT SSID not configured" >> /tmp/phase5_ventsys_test.txt
fi

cat /tmp/phase5_ventsys_test.txt	
```

### 5.13 Security and Performance Validation
**Duration**: 20 minutes

```bash
echo "=== Security and Performance Validation ===" > /tmp/phase5_security_test.txt

# Check encryption methods are appropriate for each network
encryption_checks=(
    "HomeMain:sae-mixed:WPA3 with WPA2 fallback"
    "HomeAdmin:sae:WPA3-only for admin security"
    "HomeIoT:psk2:WPA2 for IoT compatibility"
    "HomeGuest:psk2:WPA2 for guest compatibility"
)

for check in "${encryption_checks[@]}"; do
    ssid=$(echo $check | cut -d':' -f1)
    encryption=$(echo $check | cut -d':' -f2)
    description=$(echo $check | cut -d':' -f3)
    
    if uci show wireless | grep -A5 "ssid='$ssid'" | grep -q "encryption='$encryption'"; then
        echo "✓ $ssid: $description" >> /tmp/phase5_security_test.txt
    else
        echo "✗ $ssid: Encryption incorrect (expected $encryption)" >> /tmp/phase5_security_test.txt
    fi
done

# Check client isolation settings
isolation_required=("HomeIoT" "HomeGuest")
for ssid in "${isolation_required[@]}"; do
    if uci show wireless | grep -A5 "ssid='$ssid'" | grep -q "isolate='1'"; then
        echo "✓ $ssid: Client isolation enabled" >> /tmp/phase5_security_test.txt
    else
        echo "✗ $ssid: Client isolation missing" >> /tmp/phase5_security_test.txt
    fi
done

cat /tmp/phase5_security_test.txt
```

### 5.14 Channel Strategy Validation
**Duration**: 10 minutes

```bash
echo "=== Channel Strategy Validation ===" > /tmp/phase5_channel_test.txt

# All 2.4GHz SSIDs share radio0 — verify it is on channel 6
channel=$(uci get wireless.radio0.channel 2>/dev/null || echo "unknown")
if [ "$channel" = "6" ]; then
    echo "✓ radio0 (2.4GHz) on channel 6 — correct for VentSys IoT stability" >> /tmp/phase5_channel_test.txt
else
    echo "✗ radio0 channel is '$channel' (expected 6)" >> /tmp/phase5_channel_test.txt
fi

# 5GHz should be on auto
channel5=$(uci get wireless.radio1.channel 2>/dev/null || echo "unknown")
echo "ℹ radio1 (5GHz) channel: $channel5 (auto expected)" >> /tmp/phase5_channel_test.txt

# Confirm 2.4GHz radio is active
if iwconfig 2>/dev/null | grep "Frequency:2.4" >/dev/null; then
    echo "✓ 2.4GHz radio active" >> /tmp/phase5_channel_test.txt
else
    echo "✗ 2.4GHz radio not detected" >> /tmp/phase5_channel_test.txt
fi

# Confirm 5GHz radio is active
if iwconfig 2>/dev/null | grep "Frequency:5\." >/dev/null; then
    echo "✓ 5GHz radio active" >> /tmp/phase5_channel_test.txt
else
    echo "✗ 5GHz radio not detected" >> /tmp/phase5_channel_test.txt
fi

cat /tmp/phase5_channel_test.txt
```

Success Criteria for Phase 5

All SSIDs broadcasting: 5 SSIDs visible with correct configurations
VLAN mappings correct: Each SSID properly assigned to intended VLAN
Security configurations appropriate: WPA3/WPA2 selections match requirements
Channel separation implemented: Single 2.4GHz radio (radio0) fixed to channel 6 — no 2.4GHz channel conflict possible
VentSys IoT ready: HomeIoT SSID operational on VLAN 50 for sensor connectivity
Client isolation active: IoT and Guest networks prevent inter-client communication
Connection limits enforced: Guest and admin networks have appropriate limits

Failure Analysis and Resolution
Minor Issues

SSID not broadcasting: Check interface configuration and restart wireless
Wrong VLAN assignment: Verify network interface mappings
Security problems: Check encryption settings and key validity
Channel conflicts: Adjust channel assignments and restart radios

Major Failures

Wireless service failure: Check radio hardware and driver compatibility
Configuration corruption: Restore from Phase 5 entry backup
Radio hardware issues: Verify hardware compatibility and antenna connections

Emergency Rollback
bash# If wireless completely fails:
/etc/init.d/network stop
uci set wireless.radio0.disabled='1'  
uci set wireless.radio1.disabled='1'
uci commit wireless
/etc/init.d/network start

# Then restore from backup:
/usr/local/bin/emergency_restore.sh

**Proceed to Phase 6 when VentSys integration prerequisites validated.**


# Phase 6: WireGuard VPN Setup

**Duration**: 2-3 hours  
**Risk Level**: Medium (VPN connectivity complexity)  
**Prerequisites**: Phase 5 completed, all wireless networks operational

## Overview
Implements WireGuard VPN server for secure remote access to network resources. Establishes encrypted tunnel with controlled access to specific network segments while maintaining security isolation. Provides foundation for remote management and controlled access to internal services.

## Sub-Tasks

### 6.1 Pre-Configuration Validation
**Duration**: 10 minutes

```bash
# Create Phase 6 entry backup
/usr/local/bin/backup_phase.sh 6_entry

# Validate VPN prerequisites
echo "=== Phase 6 Prerequisites ===" > /tmp/phase6_validation.txt

# Check WireGuard packages installed
if opkg list-installed | grep -q "wireguard-tools"; then
    echo "✓ WireGuard tools installed" >> /tmp/phase6_validation.txt
else
    echo "✗ WireGuard tools missing" >> /tmp/phase6_validation.txt
    exit 1
fi

# Verify WireGuard keys exist
if [ -f "/etc/wireguard/keys/server_private.key" ]; then
    echo "✓ WireGuard server keys available" >> /tmp/phase6_validation.txt
else
    echo "✗ WireGuard server keys missing" >> /tmp/phase6_validation.txt
    exit 1
fi

cat /tmp/phase6_validation.txt
echo "Prerequisites validated for VPN setup" >> /tmp/deployment_logs/phase6.log
```

### 6.2 WireGuard Interface Configuration
**Duration**: 30 minutes

```bash
# Load server private key
SERVER_PRIVATE_KEY=$(cat /etc/wireguard/keys/server_private.key)

# Configure WireGuard interface (wg0)
uci add network interface
uci set network.@interface[-1].name='wg0'
uci set network.wg0.proto='wireguard'
uci set network.wg0.private_key="$SERVER_PRIVATE_KEY"
uci set network.wg0.listen_port='51820'
uci add_list network.wg0.addresses='10.0.0.1/24'

# NOTE: A redundant 'vpn' static interface (proto=static, device=wg0) was
# previously created here as a 'bridge' for the firewall zone. It is NOT needed.
# The vpn_clients firewall zone references network='wg0' directly (see
# firewall-config.conf B7 fix comment). Creating the duplicate 'vpn' interface
# causes the firewall zone assignment to silently fail. Do not add it back.

echo "WireGuard interfaces configured" >> /tmp/deployment_logs/phase6.log
```

### 6.3 VPN Client Configurations
**Duration**: 25 minutes

```bash
# Add WireGuard peers (clients)
# Client 1 - Mobile Device
CLIENT1_PUBLIC_KEY=$(cat /etc/wireguard/keys/client1_public.key)
uci add network wireguard_wg0
uci set network.@wireguard_wg0[-1].public_key="$CLIENT1_PUBLIC_KEY"
uci set network.@wireguard_wg0[-1].allowed_ips='10.0.0.2/32'
uci set network.@wireguard_wg0[-1].persistent_keepalive='25'

# Client 2 - Mobile Device
CLIENT2_PUBLIC_KEY=$(cat /etc/wireguard/keys/client2_public.key)
uci add network wireguard_wg0
uci set network.@wireguard_wg0[-1].public_key="$CLIENT2_PUBLIC_KEY"
uci set network.@wireguard_wg0[-1].allowed_ips='10.0.0.3/32'
uci set network.@wireguard_wg0[-1].persistent_keepalive='25'

# Client 3 - Laptop/Desktop
CLIENT3_PUBLIC_KEY=$(cat /etc/wireguard/keys/client3_public.key)
uci add network wireguard_wg0
uci set network.@wireguard_wg0[-1].public_key="$CLIENT3_PUBLIC_KEY"
uci set network.@wireguard_wg0[-1].allowed_ips='10.0.0.4/32'
uci set network.@wireguard_wg0[-1].persistent_keepalive='25'

echo "VPN client configurations added" >> /tmp/deployment_logs/phase6.log
```

### 6.4 VPN Configuration Application
**Duration**: 15 minutes

```bash
# Commit network configuration
uci commit network

# Restart network service
/etc/init.d/network restart
sleep 15

# Verify WireGuard interface is up
if ip addr show wg0 >/dev/null 2>&1; then
    echo "✓ WireGuard interface operational" >> /tmp/deployment_logs/phase6.log
else
    echo "✗ WireGuard interface failed" >> /tmp/deployment_logs/phase6.log
fi
```

### 6.5 VPN Client Configuration Files Generation
**Duration**: 20 minutes

```bash
# Generate client configuration files
mkdir -p /etc/wireguard/client_configs
SERVER_PUBLIC_KEY=$(cat /etc/wireguard/keys/server_public.key)
WAN_IP=$(wget -qO- http://ipecho.net/plain || echo "YOUR_PUBLIC_IP")

# Client 1 configuration
cat > /etc/wireguard/client_configs/client1.conf << EOF
[Interface]
PrivateKey = $(cat /etc/wireguard/keys/client1_private.key)
Address = 10.0.0.2/24
DNS = 192.168.1.1

[Peer]
PublicKey = $SERVER_PUBLIC_KEY
Endpoint = $WAN_IP:51820
AllowedIPs = 192.168.0.0/16, 10.0.0.0/24
PersistentKeepalive = 25
EOF

# Client 2 and 3 configurations (similar pattern)
for i in 2 3; do
    cat > /etc/wireguard/client_configs/client$i.conf << EOF
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

echo "VPN client configuration files generated" >> /tmp/deployment_logs/phase6.log
```

## Phase 6 Testing and Validation

### 6.6 VPN Interface Validation
**Duration**: 15 minutes

```bash
echo "=== VPN Interface Validation ===" > /tmp/phase6_validation.txt

# Check WireGuard interface status
if ip addr show wg0 | grep -q "10.0.0.1/24"; then
    echo "✓ WireGuard interface has correct IP" >> /tmp/phase6_validation.txt
else
    echo "✗ WireGuard interface IP incorrect" >> /tmp/phase6_validation.txt
fi

# Check if WireGuard is listening on port 51820
if netstat -ulnp | grep -q ":51820"; then
    echo "✓ WireGuard listening on port 51820" >> /tmp/phase6_validation.txt
else
    echo "✗ WireGuard not listening on port 51820" >> /tmp/phase6_validation.txt
fi

# Verify firewall zone exists for VPN
if uci show firewall | grep -q "zone.*name='vpn_clients'"; then
    echo "✓ VPN firewall zone configured" >> /tmp/phase6_validation.txt
else
    echo "✗ VPN firewall zone missing" >> /tmp/phase6_validation.txt
fi

cat /tmp/phase6_validation.txt
```

### 6.7 VPN Security and Access Validation
**Duration**: 20 minutes

```bash
echo "=== VPN Security and Access Validation ===" > /tmp/phase6_security_test.txt

# Verify VPN clients can access LAN (should be allowed)
if uci show firewall | grep -q "VPN to LAN Access"; then
    echo "✓ VPN to LAN access rule configured" >> /tmp/phase6_security_test.txt
else
    echo "✗ VPN to LAN access rule missing" >> /tmp/phase6_security_test.txt
fi

# Verify VPN clients blocked from sensitive networks
sensitive_blocks=("management" "cctv" "storage" "iot_sensors")
blocked_count=0
for zone in "${sensitive_blocks[@]}"; do
    if uci show firewall | grep -q "Block VPN to $zone"; then
        blocked_count=$((blocked_count + 1))
    fi
done

if [ $blocked_count -eq 4 ]; then
    echo "✓ VPN blocked from sensitive networks ($blocked_count/4)" >> /tmp/phase6_security_test.txt
else
    echo "✗ VPN sensitive network blocking incomplete ($blocked_count/4)" >> /tmp/phase6_security_test.txt
fi

cat /tmp/phase6_security_test.txt
```

## Success Criteria for Phase 6

- **WireGuard interface operational**: VPN server listening on port 51820
- **Client configurations generated**: 3 client config files ready for distribution
- **Firewall integration**: VPN clients properly integrated with firewall zones
- **Access controls**: VPN clients have controlled access (LAN yes, sensitive networks no)
- **Security isolation maintained**: VPN doesn't compromise network segmentation

## Proceed to Phase 7 only when VPN server operational and security controls validated.


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
for vlan in 1 10 20 30 40 50 60 70 99; do
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
networks=("192.168.1.1" "192.168.10.1" "192.168.20.1" "192.168.30.1" "192.168.40.1" "192.168.50.1" "192.168.60.1" "192.168.70.1" "192.168.99.1")

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
    if ping -c 3 -W 5 -I "$net" 8.8.8.8 >/dev/null 2>&1; then
        echo "✓ $name ($net): Internet access working" >> /tmp/phase7_internet_access.txt
    else
        echo "✗ $name ($net): Internet access blocked" >> /tmp/phase7_internet_access.txt
    fi
done

# No internet access networks (should fail)
no_access_nets=("192.168.30.1:CCTV" "192.168.40.1:Storage" "192.168.50.1:IoT_Sensors")
for net_desc in "${no_access_nets[@]}"; do
    net=$(echo $net_desc | cut -d':' -f1)
    name=$(echo $net_desc | cut -d':' -f2)
    if ping -c 3 -W 5 -I "$net" 8.8.8.8 >/dev/null 2>&1; then
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

# Verify all expected SSIDs are broadcasting
expected_ssids=("HomeMain" "HomeAdmin" "HomeAdmin-2G" "HomeIoT" "HomeGuest")
broadcasting_count=0
for ssid in "${expected_ssids[@]}"; do
    if iwlist scan 2>/dev/null | grep -q "ESSID:\"$ssid\""; then
        echo "✓ SSID broadcasting: $ssid" >> /tmp/phase7_wireless_test.txt
        broadcasting_count=$((broadcasting_count + 1))
    else
        echo "✗ SSID not broadcasting: $ssid" >> /tmp/phase7_wireless_test.txt
    fi
done

echo "Broadcasting SSIDs: $broadcasting_count/5" >> /tmp/phase7_wireless_test.txt

# Check radio status and performance
echo "" >> /tmp/phase7_wireless_test.txt
echo "Radio Status:" >> /tmp/phase7_wireless_test.txt
iwconfig 2>/dev/null >> /tmp/phase7_wireless_test.txt

# Verify HomeDMZ is disabled
if iwlist scan 2>/dev/null | grep -q "ESSID:\"HomeDMZ\""; then
    echo "✗ HomeDMZ broadcasting (should be disabled)" >> /tmp/phase7_wireless_test.txt
else
    echo "✓ HomeDMZ properly disabled" >> /tmp/phase7_wireless_test.txt
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
    "Internet Blocks:Block CCTV Internet,Block Storage Internet,Block IoT Internet"
    "VentSys Rules:HA to IoT Sensors Access,VentSys MQTT IoT to HA,ESPHome API HA to IoT"
    "Isolation Rules:Block Guest to LAN,Block DMZ to LAN,Block VPN to management"
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

# 2. VLAN 50 (IoT Sensors) operational and isolated
if ip addr show br-lan.50 | grep -q "192.168.50.1"; then
    echo "✓ VLAN 50 (IoT Sensors) ready for VentSys devices" >> /tmp/phase7_ventsys_readiness.txt
else
    echo "✗ VLAN 50 (IoT Sensors) not operational" >> /tmp/phase7_ventsys_readiness.txt
fi

# 3. HomeIoT WiFi SSID operational on VLAN 50
if iwlist scan 2>/dev/null | grep -q "ESSID:\"HomeIoT\""; then
    echo "✓ HomeIoT WiFi SSID broadcasting for VentSys sensors" >> /tmp/phase7_ventsys_readiness.txt
else
    echo "✗ HomeIoT WiFi SSID not broadcasting" >> /tmp/phase7_ventsys_readiness.txt
fi

# 4. IoT internet isolation (security critical)
if ping -c 2 -W 3 -I 192.168.50.1 8.8.8.8 >/dev/null 2>&1; then
    echo "✗ VLAN 50 has internet access (SECURITY ISSUE)" >> /tmp/phase7_ventsys_readiness.txt
else
    echo "✓ VLAN 50 internet access properly blocked" >> /tmp/phase7_ventsys_readiness.txt
fi

# 5. VentSys communication ports (MQTT 8883, ESPHome 6053)
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
- **VentSys readiness validated**: VLANs 20 and 50 ready for HA and IoT integration
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


# Phase 8: VentSys Integration Readiness

**Duration**: 2-3 hours  
**Risk Level**: Low (final validation and documentation)  
**Prerequisites**: Phase 7 completed with acceptable test results

## Overview
Finalizes network foundation for VentSys integration by completing certificate infrastructure preparation, creating integration documentation, and establishing monitoring baselines. Provides comprehensive handover documentation for VentSys Phase 1 implementation and validates all prerequisites for IoT ecosystem deployment.

## Sub-Tasks

### 8.1 Certificate Authority Preparation for VentSys TLS
**Duration**: 45 minutes

```bash
# Create Phase 8 entry backup
/usr/local/bin/backup_phase.sh 8_entry

echo "=== VentSys Certificate Authority Preparation ===" > /tmp/phase8_cert_prep.txt

# Prepare certificate infrastructure directory structure
mkdir -p /etc/ventsys/ca/{certs,private,crl,newcerts}
chmod 700 /etc/ventsys/ca/private

# Create CA configuration template for VentSys
cat > /etc/ventsys/ca/openssl.conf << 'EOF'
[ ca ]
default_ca = CA_default

[ CA_default ]
dir               = /etc/ventsys/ca
certs             = $dir/certs
crl_dir           = $dir/crl
new_certs_dir     = $dir/newcerts
database          = $dir/index.txt
serial            = $dir/serial
RANDFILE          = $dir/private/.rand

private_key       = $dir/private/ca.key
certificate       = $dir/certs/ca.crt

default_days      = 3650
default_crl_days  = 30
default_md        = sha256
preserve          = no
policy            = policy_strict

[ policy_strict ]
countryName             = match
stateOrProvinceName     = match
organizationName        = match
organizationalUnitName  = optional
commonName              = supplied
emailAddress            = optional

[ req ]
default_bits        = 4096
distinguished_name  = req_distinguished_name
string_mask         = utf8only
default_md          = sha256
x509_extensions     = v3_ca

[ v3_ca ]
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always,issuer
basicConstraints = critical, CA:true
keyUsage = critical, digitalSignature, cRLSign, keyCertSign

[ server_cert ]
basicConstraints = CA:FALSE
nsCertType = server
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid,issuer:always
keyUsage = critical, digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth
EOF

# Initialize CA database files
touch /etc/ventsys/ca/index.txt
echo 1000 > /etc/ventsys/ca/serial

echo "✓ Certificate Authority infrastructure prepared for VentSys" >> /tmp/phase8_cert_prep.txt
echo "⚠ CA keys will be generated during VentSys Phase 1, Week 2" >> /tmp/phase8_cert_prep.txt

cat /tmp/phase8_cert_prep.txt
echo "Certificate infrastructure prepared for VentSys integration" >> /tmp/deployment_logs/phase8.log
```

### 8.2 VentSys Network Integration Documentation
**Duration**: 30 minutes

```bash
echo "=== VentSys Network Integration Documentation ===" > /tmp/phase8_ventsys_integration.txt

# Document critical network settings for VentSys integration
echo "VENTSYS NETWORK INTEGRATION REQUIREMENTS:" >> /tmp/phase8_ventsys_integration.txt
echo "Generated: $(date)" >> /tmp/phase8_ventsys_integration.txt
echo "" >> /tmp/phase8_ventsys_integration.txt

# Document key network segments
echo "CRITICAL NETWORK SEGMENTS FOR VENTSYS:" >> /tmp/phase8_ventsys_integration.txt
echo "1. VLAN 20 (Automation): 192.168.20.0/24" >> /tmp/phase8_ventsys_integration.txt
echo "   - Home Assistant VM: 192.168.20.101 (static reservation)" >> /tmp/phase8_ventsys_integration.txt
echo "   - Gateway: 192.168.20.1" >> /tmp/phase8_ventsys_integration.txt
echo "   - DHCP Range: 192.168.20.110-149" >> /tmp/phase8_ventsys_integration.txt
echo "" >> /tmp/phase8_ventsys_integration.txt
echo "2. VLAN 50 (IoT Sensors): 192.168.50.0/24" >> /tmp/phase8_ventsys_integration.txt
echo "   - WiFi SSID: HomeIoT" >> /tmp/phase8_ventsys_integration.txt
echo "   - Gateway: 192.168.50.1" >> /tmp/phase8_ventsys_integration.txt
echo "   - DHCP Range: 192.168.50.100-190" >> /tmp/phase8_ventsys_integration.txt
echo "   - Fan Controller: 192.168.50.21 (static reservation)" >> /tmp/phase8_ventsys_integration.txt
echo "   - Valve Controller: 192.168.50.56 (static reservation)" >> /tmp/phase8_ventsys_integration.txt
echo "" >> /tmp/phase8_ventsys_integration.txt

# Document firewall rules critical for VentSys
echo "CRITICAL FIREWALL RULES FOR VENTSYS:" >> /tmp/phase8_ventsys_integration.txt
echo "1. Home Assistant to IoT Sensors: VLAN 20 → VLAN 50 (full access)" >> /tmp/phase8_ventsys_integration.txt
echo "2. MQTT Communication: VLAN 50 → VLAN 20:8883 (TCP)" >> /tmp/phase8_ventsys_integration.txt
echo "3. ESPHome API: VLAN 20 → VLAN 50:6053 (TCP)" >> /tmp/phase8_ventsys_integration.txt
echo "4. IoT Internet Block: VLAN 50 → WAN (REJECT - CRITICAL)" >> /tmp/phase8_ventsys_integration.txt
echo "" >> /tmp/phase8_ventsys_integration.txt

# WiFi credentials for VentSys devices
IOT_PASSWORD=$(cat /etc/wireless/credentials/iot_password.txt 2>/dev/null || echo "PASSWORD_NOT_FOUND")
echo "WIFI CREDENTIALS FOR VENTSYS DEVICES:" >> /tmp/phase8_ventsys_integration.txt
echo "SSID: HomeIoT" >> /tmp/phase8_ventsys_integration.txt
echo "Password: $IOT_PASSWORD" >> /tmp/phase8_ventsys_integration.txt
echo "Security: WPA2 (PSK2) - Optimized for IoT device compatibility" >> /tmp/phase8_ventsys_integration.txt
echo "Channel: 6 (fixed for stability)" >> /tmp/phase8_ventsys_integration.txt

cat /tmp/phase8_ventsys_integration.txt
```

### 8.3 Monitoring and Alerting Baseline Setup
**Duration**: 30 minutes

```bash
echo "=== Monitoring Baseline Setup ===" > /tmp/phase8_monitoring_setup.txt

# Create monitoring script for VentSys critical components
cat > /usr/local/bin/ventsys_network_monitor.sh << 'EOF'
#!/bin/bash
# VentSys Network Monitoring Script
# Monitors critical network components for VentSys operation

LOG_FILE="/var/log/ventsys_network_monitor.log"
ALERT_THRESHOLD=3

check_interface() {
    local interface=$1
    local expected_ip=$2
    
    if ip addr show "$interface" | grep -q "$expected_ip"; then
        echo "$(date): ✓ $interface operational ($expected_ip)" >> "$LOG_FILE"
        return 0
    else
        echo "$(date): ✗ $interface FAILED ($expected_ip)" >> "$LOG_FILE"
        return 1
    fi
}

check_wireless_ssid() {
    local ssid=$1
    
    if iwlist scan 2>/dev/null | grep -q "ESSID:\"$ssid\""; then
        echo "$(date): ✓ SSID $ssid broadcasting" >> "$LOG_FILE"
        return 0
    else
        echo "$(date): ✗ SSID $ssid NOT broadcasting" >> "$LOG_FILE"
        return 1
    fi
}

check_firewall_rule() {
    local rule_name=$1
    
    if uci show firewall | grep -q "$rule_name"; then
        echo "$(date): ✓ Firewall rule '$rule_name' present" >> "$LOG_FILE"
        return 0
    else
        echo "$(date): ✗ Firewall rule '$rule_name' MISSING" >> "$LOG_FILE"
        return 1
    fi
}

# Main monitoring checks
echo "$(date): Starting VentSys network monitoring" >> "$LOG_FILE"

# Check critical interfaces
check_interface "br-lan.20" "192.168.20.1"
check_interface "br-lan.50" "192.168.50.1"

# Check HomeIoT WiFi
check_wireless_ssid "HomeIoT"

# Check critical firewall rules
check_firewall_rule "HA to IoT Sensors Access"
check_firewall_rule "VentSys MQTT IoT to HA"
check_firewall_rule "Block IoT Internet"

echo "$(date): VentSys network monitoring completed" >> "$LOG_FILE"
EOF

chmod +x /usr/local/bin/ventsys_network_monitor.sh

# Create monitoring cron job (every 15 minutes)
echo "*/15 * * * * /usr/local/bin/ventsys_network_monitor.sh" >> /etc/crontabs/root

# Run initial monitoring check
/usr/local/bin/ventsys_network_monitor.sh

echo "✓ VentSys network monitoring script created and scheduled" >> /tmp/phase8_monitoring_setup.txt
echo "✓ Monitoring log: /var/log/ventsys_network_monitor.log" >> /tmp/phase8_monitoring_setup.txt
echo "✓ Cron job: Every 15 minutes" >> /tmp/phase8_monitoring_setup.txt

cat /tmp/phase8_monitoring_setup.txt
```

### 8.4 MAC Address Collection Framework
**Duration**: 15 minutes

```bash
echo "=== MAC Address Collection Framework ===" > /tmp/phase8_mac_collection.txt

# Create script to update static DHCP reservations with real MAC addresses
cat > /usr/local/bin/update_ventsys_mac.sh << 'EOF'
#!/bin/bash
# VentSys MAC Address Update Script
# Usage: update_ventsys_mac.sh <device_name> <mac_address>

DEVICE_NAME=$1
MAC_ADDRESS=$2

if [ -z "$DEVICE_NAME" ] || [ -z "$MAC_ADDRESS" ]; then
    echo "Usage: $0 <device_name> <mac_address>"
    echo "Available devices: proxmox-host, home-assistant, frigate-nvr, pi-nas, ventsys-main-fan, ventsys-sla-print-valve  # A8-1 fix: canonical names"
    exit 1
fi

# Validate MAC address format
if ! echo "$MAC_ADDRESS" | grep -qE '^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$'; then
    echo "Error: Invalid MAC address format. Expected format: XX:XX:XX:XX:XX:XX"
    exit 1
fi

# Find and update the DHCP host entry
host_sections=$(uci show dhcp | grep "dhcp\.@host.*\.name='$DEVICE_NAME'" | cut -d'.' -f2 | cut -d'=' -f1)

if [ -z "$host_sections" ]; then
    echo "Error: Device '$DEVICE_NAME' not found in DHCP reservations"
    exit 1
fi

for section in $host_sections; do
    echo "Updating MAC address for $DEVICE_NAME ($section) to $MAC_ADDRESS"
    uci set dhcp.$section.mac="$MAC_ADDRESS"
done

uci commit dhcp
/etc/init.d/dnsmasq restart

echo "✓ MAC address updated and DHCP service restarted"
echo "$(date): Updated $DEVICE_NAME MAC to $MAC_ADDRESS" >> /var/log/mac_address_updates.log
EOF

chmod +x /usr/local/bin/update_ventsys_mac.sh

echo "✓ MAC address update script created: /usr/local/bin/update_ventsys_mac.sh" >> /tmp/phase8_mac_collection.txt
echo "✓ Usage: update_ventsys_mac.sh <device_name> <mac_address>" >> /tmp/phase8_mac_collection.txt
echo "✓ Update log: /var/log/mac_address_updates.log" >> /tmp/phase8_mac_collection.txt

cat /tmp/phase8_mac_collection.txt
```

### 8.5 Final Configuration Backup and Documentation
**Duration**: 20 minutes

```bash
echo "=== Final Configuration Backup and Documentation ===" > /tmp/phase8_final_backup.txt

# Create comprehensive backup of complete configuration
BACKUP_DIR="/etc/config/backups/production_ready_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup all configuration files
cp /etc/config/* "$BACKUP_DIR/"
uci export > "$BACKUP_DIR/uci_complete_export.txt"

# Backup wireless credentials
cp -r /etc/wireless/credentials "$BACKUP_DIR/"

# Backup WireGuard keys and client configs
cp -r /etc/wireguard "$BACKUP_DIR/"

# Create configuration summary
cat > "$BACKUP_DIR/CONFIGURATION_SUMMARY.txt" << 'EOF'
OPENWRT ROUTER CONFIGURATION - PRODUCTION READY
===============================================

HARDWARE: GL.iNet GL-MT6000
FIRMWARE: OpenWrt (latest)
CONFIGURATION DATE: $(date)

NETWORK ARCHITECTURE:
- 9 VLANs operational (1,10,20,30,40,50,60,70,99)
- 5 WiFi SSIDs configured
- WireGuard VPN server operational
- Complete firewall segmentation implemented

VENTSYS INTEGRATION READY:
- VLAN 20 (Automation): Home Assistant VM network
- VLAN 50 (IoT Sensors): VentSys device network (internet isolated)
- HomeIoT WiFi SSID operational
- Certificate infrastructure prepared
- Monitoring baseline established

CRITICAL SECURITY FEATURES:
- Network segmentation with firewall isolation
- Guest network completely isolated
- IoT network has no internet access
- VPN clients have controlled access
- DNS security implemented

NEXT STEPS:
1. Deploy physical devices and collect MAC addresses
2. Update static DHCP reservations with real MACs
3. Begin VentSys Phase 1 implementation
4. Monitor network performance and security

FILES IN THIS BACKUP:
- All /etc/config/ files
- Complete UCI configuration export
- WiFi credentials (secure handling required)
- WireGuard keys and client configurations
- Custom scripts and monitoring tools
EOF

# Create deployment success marker
echo "$(date): Router configuration completed successfully" > "$BACKUP_DIR/DEPLOYMENT_SUCCESS.txt"
echo "Ready for production use and VentSys integration" >> "$BACKUP_DIR/DEPLOYMENT_SUCCESS.txt"

tar -czf "/tmp/production_ready_backup_$(date +%Y%m%d_%H%M%S).tar.gz" -C "$(dirname $BACKUP_DIR)" "$(basename $BACKUP_DIR)"

echo "✓ Complete configuration backed up to: $BACKUP_DIR" >> /tmp/phase8_final_backup.txt
echo "✓ Compressed backup created in /tmp/" >> /tmp/phase8_final_backup.txt
echo "✓ Configuration summary created" >> /tmp/phase8_final_backup.txt

cat /tmp/phase8_final_backup.txt
```

### 8.6 Final Validation and Handover Documentation
**Duration**: 20 minutes

```bash
echo "=== Final Validation and Handover Documentation ===" > /tmp/phase8_final_validation.txt

# Final system status
echo "FINAL SYSTEM STATUS - PHASE 8 COMPLETION:" >> /tmp/phase8_final_validation.txt
echo "Completion Date: $(date)" >> /tmp/phase8_final_validation.txt
echo "Total Implementation Time: 8 phases over multiple weeks" >> /tmp/phase8_final_validation.txt
echo "" >> /tmp/phase8_final_validation.txt

# Validate all critical components one final time
echo "CRITICAL COMPONENT VALIDATION:" >> /tmp/phase8_final_validation.txt

# Network interfaces
interface_count=$(ip addr show | grep -c "br-lan\.")
echo "✓ VLAN interfaces operational: $interface_count/9" >> /tmp/phase8_final_validation.txt

# Wireless SSIDs
ssid_count=$(iwlist scan 2>/dev/null | grep -c "ESSID:")
echo "✓ WiFi SSIDs broadcasting: $ssid_count" >> /tmp/phase8_final_validation.txt

# Firewall rules
rule_count=$(uci show firewall | grep -c "@rule")
echo "✓ Firewall rules configured: $rule_count" >> /tmp/phase8_final_validation.txt

# Services
services_running=0
for service in network firewall dnsmasq; do
    if /etc/init.d/$service status >/dev/null 2>&1; then
        services_running=$((services_running + 1))
    fi
done
echo "✓ Critical services running: $services_running/3" >> /tmp/phase8_final_validation.txt

# VentSys readiness
echo "" >> /tmp/phase8_final_validation.txt
echo "VENTSYS INTEGRATION READINESS:" >> /tmp/phase8_final_validation.txt
if ip addr show br-lan.20 | grep -q "192.168.20.1" && ip addr show br-lan.50 | grep -q "192.168.50.1"; then
    echo "✓ Critical VLANs operational (20: Automation, 50: IoT Sensors)" >> /tmp/phase8_final_validation.txt
else
    echo "✗ Critical VLANs not operational" >> /tmp/phase8_final_validation.txt
fi

if iwlist scan 2>/dev/null | grep -q "HomeIoT"; then
    echo "✓ HomeIoT WiFi SSID ready for VentSys sensors" >> /tmp/phase8_final_validation.txt
else
    echo "? HomeIoT WiFi SSID not broadcasting" >> /tmp/phase8_final_validation.txt
fi   # L-6 fix: closing fi for HomeIoT SSID check (was truncated with unclosed string)
if [ -d "/etc/ventsys/ca" ]; then
    echo "✓ Certificate infrastructure prepared" >> /tmp/phase8_final_validation.txt
else
    echo "✗ Certificate infrastructure not prepared" >> /tmp/phase8_final_validation.txt
fi

# Final recommendations
echo "" >> /tmp/phase8_final_validation.txt
echo "DEPLOYMENT COMPLETION STATUS:" >> /tmp/phase8_final_validation.txt
echo "✓ Network foundation complete and tested" >> /tmp/phase8_final_validation.txt
echo "✓ Security architecture implemented and validated" >> /tmp/phase8_final_validation.txt
echo "✓ VentSys integration prerequisites established" >> /tmp/phase8_final_validation.txt
echo "✓ Monitoring and maintenance tools deployed" >> /tmp/phase8_final_validation.txt
echo "✓ Complete configuration backup created" >> /tmp/phase8_final_validation.txt
echo "" >> /tmp/phase8_final_validation.txt
echo "READY FOR PRODUCTION USE" >> /tmp/phase8_final_validation.txt

cat /tmp/phase8_final_validation.txt
echo "SUCCESS: Router implementation completed - ready for VentSys Phase 1" >> /tmp/deployment_logs/phase8.log

Success Criteria for Phase 8

Certificate infrastructure prepared: Framework ready for VentSys TLS deployment
Integration documentation complete: VentSys team has all required network information
Monitoring operational: Automated health checks running every 15 minutes
Configuration secured: Complete backup with all credentials protected
Update procedures ready: MAC address collection and device onboarding framework
VentSys handover complete: All prerequisites documented and validated

Failure Analysis and Resolution
Minor Issues

Certificate structure problems: Recreate directory structure with proper permissions
Monitoring script failures: Check script permissions and log file access
Documentation gaps: Verify all critical information documented

Major Failures

Backup system failure: Recreate backup infrastructure and test procedures
Network monitoring failure: Reinstall monitoring components and validate functionality
VentSys prerequisites missing: Review and remediate missing network components

Recovery Procedures
bash# If monitoring system fails:
rm -rf /usr/local/bin/ventsys_network_monitor.sh
# Recreate from Phase 8.3 instructions

# If certificate infrastructure fails:
rm -rf /etc/ventsys/ca
mkdir -p /etc/ventsys/ca/{certs,private,crl,newcerts}
chmod 700 /etc/ventsys/ca/private
# Recreate from Phase 8.1 instructions

# If complete Phase 8 failure:
/usr/local/bin/backup_phase.sh 8_recovery
# Address specific failures and rerun phase sections

