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