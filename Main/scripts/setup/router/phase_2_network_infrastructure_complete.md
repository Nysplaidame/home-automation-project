# Phase 2: Network Infrastructure (VLAN Configuration)

**Duration**: 3-4 hours  
**Risk Level**: High (network foundation changes)  
**Prerequisites**: Phase 1 completed with all validation criteria met

## Overview
Implements DSA-based VLAN infrastructure creating 10 isolated network segments. Establishes physical-to-logical network mapping crucial for security segmentation. Most critical phase as all subsequent configurations depend on proper VLAN implementation.

## Interdependencies

### Input Requirements
- Phase 1 validation passed (interface names verified)
- Factory configuration backup created
- Current network connectivity for UCI commands

### Output Deliverables  
- 10 VLAN interfaces operational (VLANs 1,10,20,30,35,40,50,60,70,99)
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
- **VLAN 20**: **VentSys Automation** - HA/Frigate VMs (192.168.20.0/24)
- **VLAN 30**: NVR cameras (192.168.30.0/24) — renamed from CCTV
- **VLAN 35**: Printers (192.168.35.0/24) — Bambu P1S, Concepts3D Athena 2
- **VLAN 40**: Storage/NAS (192.168.40.0/24)
- **VLAN 50**: **VentSys IoT Sensors** - Fire safety (192.168.50.0/24)
- **VLAN 60**: Monitoring VMs (192.168.60.0/24)
- **VLAN 70**: DMZ services (192.168.70.0/24)
- **VLAN 99**: Guest network (192.168.99.0/24)

### Physical Port Assignment Strategy
- **lan1**: Trunk to Proxmox (tagged VLANs 10,20,30,35,40,50,60,70)
- **lan2**: Management port (VLAN 10 untagged, others tagged)
- **lan3**: Camera POE switch (VLAN 30 untagged, management tagged)
- **lan4**: NAS connection (VLAN 40 untagged, management tagged)
- **lan5**: Recovery / WiFi AP port (VLAN 1 untagged ONLY)
  - During setup: connect your laptop here before starting Phase 2. You will always
    be able to SSH to 192.168.1.1 from this port regardless of VLAN misconfiguration
    elsewhere — lan5 only carries VLAN 1 which is the simplest possible config.
  - After setup: connect TP-Link TL-WA801N in AP mode to extend HomeMain (VLAN 1).
    No config changes are needed when switching from recovery use to AP use.

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

# VLAN 10: Management Network
uci add network bridge-vlan
uci set network.@bridge-vlan[-1].device='br-lan'
uci set network.@bridge-vlan[-1].vlan='10'
uci set network.@bridge-vlan[-1].local='1'
uci add_list network.@bridge-vlan[-1].ports='lan1:t'  # Trunk to Proxmox
# B12 fix: lan2:u* sets VLAN 10 as the PVID (untagged ingress VLAN) for lan2.
# lan2:u without * marks the port for untagged egress only — incoming untagged
# frames on lan2 would NOT be assigned to VLAN 10, breaking management access.
uci add_list network.@bridge-vlan[-1].ports='lan2:u*' # Management port — PVID
uci add_list network.@bridge-vlan[-1].ports='lan3:t'  # Tagged for admin access
uci add_list network.@bridge-vlan[-1].ports='lan4:t'  # Tagged for admin access

# VLAN 20: VentSys Automation Network (CRITICAL)
uci add network bridge-vlan
uci set network.@bridge-vlan[-1].device='br-lan'
uci set network.@bridge-vlan[-1].vlan='20'
uci set network.@bridge-vlan[-1].local='1'
uci add_list network.@bridge-vlan[-1].ports='lan1:t'  # Trunk to Proxmox for HA/Frigate VMs

# VLAN 30: NVR Network (renamed from CCTV — see docs/decisions/02-printer-vlan-architecture.md)
uci add network bridge-vlan
uci set network.@bridge-vlan[-1].device='br-lan'
uci set network.@bridge-vlan[-1].vlan='30'
uci set network.@bridge-vlan[-1].local='1'
uci add_list network.@bridge-vlan[-1].ports='lan1:t'  # Trunk to Proxmox for Frigate VM
# B12 fix: u* sets PVID so untagged ingress on lan3 is assigned to VLAN 30.
uci add_list network.@bridge-vlan[-1].ports='lan3:u*' # Camera POE switch — PVID

# VLAN 35: Printers Network (Bambu P1S + Concepts3D Athena 2)
# No physical port PVID needed — P1S is WiFi-only (HomePrinters SSID, radio0/2.4GHz).
# lan1:t is tagged so Proxmox trunk carries VLAN 35 for future wired use.
uci add network bridge-vlan
uci set network.@bridge-vlan[-1].device='br-lan'
uci set network.@bridge-vlan[-1].vlan='35'
uci set network.@bridge-vlan[-1].local='1'
uci add_list network.@bridge-vlan[-1].ports='lan1:t'  # Trunk to Proxmox (tagged)

# VLAN 40: Storage Network
uci add network bridge-vlan
uci set network.@bridge-vlan[-1].device='br-lan'
uci set network.@bridge-vlan[-1].vlan='40'
uci set network.@bridge-vlan[-1].local='1'
uci add_list network.@bridge-vlan[-1].ports='lan1:t'  # Trunk to Proxmox
# B12 fix: u* sets PVID so untagged ingress on lan4 is assigned to VLAN 40.
uci add_list network.@bridge-vlan[-1].ports='lan4:u*' # NAS direct connection — PVID

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
- All 10 VLANs configured without errors
- Proxmox trunk port (lan1) carries all required VLANs
- Physical port assignments match intended usage
- VLAN 1 has lan5:u* assigned (recovery/AP port) — no other physical ports
- Guest VLAN 99 has no physical port assignment (security)

**Critical Notes**:
- lan1 MUST carry all non-VLAN-1 VLANs for Proxmox VM networking
- VLAN 1 is otherwise WiFi-only; main users reach it via HomeMain SSID (Phase 5)
- lan5 carries ONLY VLAN 1 untagged — this is intentional. It is the recovery port
  (SSH to 192.168.1.1 if other VLANs break) and later the WiFi AP port (TL-WA801N)
- VLAN 50 (IoT) carries lan1:t so HA VM on Proxmox can reach sensor devices
- Port tagging (t) vs untagged (u*) critical for proper operation
- Each physical port can have only ONE untagged PVID: lan2=VLAN10, lan3=VLAN30, lan4=VLAN40, lan5=VLAN1

### 2.4 Logical Network Interface Creation  
**Duration**: 30 minutes

```bash
# Create logical interfaces for each VLAN

# LAN VLAN 1 — CRITICAL: must be explicitly pointed at br-lan.1 after bridge rebuild.
# Without this the lan UCI section retains its factory device ('br-lan' undivided),
# which no longer exists once the DSA bridge is created. Consequences of omission:
#   - lan5 recovery port gets no DHCP/IP — SSH safety net is broken
#   - HomeMain WiFi SSIDs (network='lan') broadcast but pass no traffic
#   - Phase 3 dhcp.lan scope attaches to a non-functional interface
uci set network.lan=interface
uci set network.lan.proto='static'
uci set network.lan.device='br-lan.1'
uci set network.lan.ipaddr='192.168.1.1'
uci set network.lan.netmask='255.255.255.0'
uci set network.lan.ip6assign='60'

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

# NVR VLAN 30 (renamed from cctv)
uci set network.nvr=interface
uci set network.nvr.proto='static'
uci set network.nvr.device='br-lan.30'
uci set network.nvr.ipaddr='192.168.30.1'
uci set network.nvr.netmask='255.255.255.0'

# Printers VLAN 35
uci set network.printers=interface
uci set network.printers.proto='static'
uci set network.printers.device='br-lan.35'
uci set network.printers.ipaddr='192.168.35.1'
uci set network.printers.netmask='255.255.255.0'

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
for vlan in 1 10 20 30 35 40 50 60 70 99; do
    expected_ip="192.168.${vlan}.1"
    if [ $vlan -eq 1 ]; then expected_ip="192.168.1.1"; fi
    if [ $vlan -eq 99 ]; then expected_ip="192.168.99.1"; fi
    
    if ip addr show br-lan.$vlan | grep -q "$expected_ip"; then
        echo "✓ VLAN $vlan interface operational: $expected_ip" >> /tmp/phase2_validation.txt
    else
        echo "✗ VLAN $vlan interface failed: expected $expected_ip" >> /tmp/phase2_validation.txt
    fi
done

# B12/E4 fix: brctl is deprecated on DSA-based OpenWrt and not installed by default.
# Use 'bridge vlan show' to inspect VLAN membership and 'ip link show' for bridge state.
if bridge link show | grep -q "br-lan"; then
    echo "✓ Bridge br-lan operational" >> /tmp/phase2_validation.txt
    bridge vlan show dev br-lan >> /tmp/phase2_validation.txt
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

- **All VLAN interfaces operational**: 10 VLANs (1,10,20,30,35,40,50,60,70,99) with correct IP addresses
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
