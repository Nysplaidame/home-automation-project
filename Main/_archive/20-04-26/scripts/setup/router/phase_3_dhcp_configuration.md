# Phase 3: DHCP Configuration

**Duration**: 2-3 hours  
**Risk Level**: Medium (DHCP scope creation)  
**Prerequisites**: Phase 2 completed, all VLAN interfaces operational

## Overview
Configures DHCP services for all 10 network segments with appropriate scopes with appropriate scopes, DNS settings, and static reservations. Establishes automated IP assignment foundation required for firewall rules and wireless client assignment. Critical for VentSys device integration and network security isolation.

## Interdependencies

### Input Requirements
- Phase 2 network interfaces operational (br-lan.1 through br-lan.99)
- VLAN routing functional for all segments
- DNS resolution working on WAN interface

### Output Deliverables
- DHCP scopes active on all 10 VLANs with correct ranges
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
for vlan in 1 10 20 30 35 40 50 60 70 99; do
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

### 3.6 NVR Network DHCP (VLAN 30)
**Duration**: 15 minutes

```bash
# Create NVR DHCP scope (renamed from cctv — isolated network)
uci add dhcp dhcp
uci set dhcp.@dhcp[-1].interface='nvr'
uci set dhcp.@dhcp[-1].start='100'
uci set dhcp.@dhcp[-1].limit='50'
uci set dhcp.@dhcp[-1].leasetime='24h'
uci set dhcp.@dhcp[-1].dhcpv4='server'

# Local DNS only (no internet access)
uci add_list dhcp.@dhcp[-1].dhcp_option='6,192.168.30.1'

echo "NVR DHCP scope configured: 192.168.30.100-149" >> /tmp/deployment_logs/phase3.log
```

### 3.6b Printers Network DHCP (VLAN 35)
**Duration**: 15 minutes

```bash
# Create Printers DHCP scope (Bambu P1S + Concepts3D Athena 2)
uci add dhcp dhcp
uci set dhcp.@dhcp[-1].interface='printers'
uci set dhcp.@dhcp[-1].start='100'
uci set dhcp.@dhcp[-1].limit='50'
uci set dhcp.@dhcp[-1].leasetime='24h'
uci set dhcp.@dhcp[-1].dhcpv4='server'

# Local DNS only — OTA resolves via dnsmasq forwarding to 1.1.1.1 for port 443 only
uci add_list dhcp.@dhcp[-1].dhcp_option='6,192.168.35.1'

echo "Printers DHCP scope configured: 192.168.35.100-149" >> /tmp/deployment_logs/phase3.log
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

# Home Assistant VM (Automation Network)
uci add dhcp host
uci set dhcp.@host[-1].name='home-assistant'
uci set dhcp.@host[-1].dns='1'
uci set dhcp.@host[-1].mac='XX:XX:XX:XX:XX:02'
uci set dhcp.@host[-1].ip='192.168.20.101'

# Bambuddy VM (Automation Network) — VM 103, 192.168.20.102
uci add dhcp host
uci set dhcp.@host[-1].name='bambuddy'
uci set dhcp.@host[-1].dns='1'
uci set dhcp.@host[-1].mac='XX:XX:XX:XX:XX:XX'
uci set dhcp.@host[-1].ip='192.168.20.102'

# Frigate NVR VM (NVR Network — renamed from CCTV)
uci add dhcp host
uci set dhcp.@host[-1].name='frigate-nvr'
uci set dhcp.@host[-1].dns='1'
uci set dhcp.@host[-1].mac='XX:XX:XX:XX:XX:03'
uci set dhcp.@host[-1].ip='192.168.30.20'

# Bambu P1S (Printers Network — moved from VLAN 1 192.168.1.200)
uci add dhcp host
uci set dhcp.@host[-1].name='bambu-p1s'
uci set dhcp.@host[-1].dns='1'
uci set dhcp.@host[-1].mac='XX:XX:XX:XX:XX:XX'
uci set dhcp.@host[-1].ip='192.168.35.200'

# Concepts3D Athena 2 (Printers Network)
uci add dhcp host
uci set dhcp.@host[-1].name='athena-2'
uci set dhcp.@host[-1].dns='1'
uci set dhcp.@host[-1].mac='XX:XX:XX:XX:XX:XX'
uci set dhcp.@host[-1].ip='192.168.35.201'

# NAS (Storage Network) - PLACEHOLDER
uci add dhcp host
uci set dhcp.@host[-1].name='pi-nas'
uci set dhcp.@host[-1].dns='1'
uci set dhcp.@host[-1].mac='XX:XX:XX:XX:XX:04'
uci set dhcp.@host[-1].ip='192.168.40.50'

# VentSys Controllers (CRITICAL FOR VENTSYS)
# F-D fix: Updated to match canonical dhcp-config.conf - full 17-device fleet.
# Previous placeholder had wrong device names (ventsys-fdm-valve, ventsys-booth-valve)
# and wrong IPs (.83, .84). Canonical allocations from dhcp-config.conf used below.

# Fans
uci add dhcp host
uci set dhcp.@host[-1].name='ventsys-main-fan'
uci set dhcp.@host[-1].ip='192.168.50.21'
uci set dhcp.@host[-1].mac='XX:XX:XX:XX:XX:XX'
uci set dhcp.@host[-1].dns='1'

uci add dhcp host
uci set dhcp.@host[-1].name='ventsys-booth-fan'
uci set dhcp.@host[-1].ip='192.168.50.22'
uci set dhcp.@host[-1].mac='XX:XX:XX:XX:XX:XX'
uci set dhcp.@host[-1].dns='1'

# Sensor arrays
uci add dhcp host
uci set dhcp.@host[-1].name='ventsys-fdm-sensor'
uci set dhcp.@host[-1].ip='192.168.50.31'
uci set dhcp.@host[-1].mac='XX:XX:XX:XX:XX:XX'
uci set dhcp.@host[-1].dns='1'

uci add dhcp host
uci set dhcp.@host[-1].name='ventsys-sla-sensor'
uci set dhcp.@host[-1].ip='192.168.50.32'
uci set dhcp.@host[-1].mac='XX:XX:XX:XX:XX:XX'
uci set dhcp.@host[-1].dns='1'

uci add dhcp host
uci set dhcp.@host[-1].name='ventsys-booth-sensor'
uci set dhcp.@host[-1].ip='192.168.50.33'
uci set dhcp.@host[-1].mac='XX:XX:XX:XX:XX:XX'
uci set dhcp.@host[-1].dns='1'

uci add dhcp host
uci set dhcp.@host[-1].name='ventsys-garage-sensor'
uci set dhcp.@host[-1].ip='192.168.50.34'
uci set dhcp.@host[-1].mac='XX:XX:XX:XX:XX:XX'
uci set dhcp.@host[-1].dns='1'

# Airflow sensors
uci add dhcp host
uci set dhcp.@host[-1].name='ventsys-fdm-airflow'
uci set dhcp.@host[-1].ip='192.168.50.41'
uci set dhcp.@host[-1].mac='XX:XX:XX:XX:XX:XX'
uci set dhcp.@host[-1].dns='1'

uci add dhcp host
uci set dhcp.@host[-1].name='ventsys-sla-airflow'
uci set dhcp.@host[-1].ip='192.168.50.42'
uci set dhcp.@host[-1].mac='XX:XX:XX:XX:XX:XX'
uci set dhcp.@host[-1].dns='1'

uci add dhcp host
uci set dhcp.@host[-1].name='ventsys-booth-airflow'
uci set dhcp.@host[-1].ip='192.168.50.43'
uci set dhcp.@host[-1].mac='XX:XX:XX:XX:XX:XX'
uci set dhcp.@host[-1].dns='1'

# Butterfly valves
uci add dhcp host
uci set dhcp.@host[-1].name='ventsys-main-valve-1'
uci set dhcp.@host[-1].ip='192.168.50.51'
uci set dhcp.@host[-1].mac='XX:XX:XX:XX:XX:XX'
uci set dhcp.@host[-1].dns='1'

uci add dhcp host
uci set dhcp.@host[-1].name='ventsys-main-valve-2'
uci set dhcp.@host[-1].ip='192.168.50.52'
uci set dhcp.@host[-1].mac='XX:XX:XX:XX:XX:XX'
uci set dhcp.@host[-1].dns='1'

uci add dhcp host
uci set dhcp.@host[-1].name='ventsys-fdm-branch-valve'
uci set dhcp.@host[-1].ip='192.168.50.53'
uci set dhcp.@host[-1].mac='XX:XX:XX:XX:XX:XX'
uci set dhcp.@host[-1].dns='1'

uci add dhcp host
uci set dhcp.@host[-1].name='ventsys-sla-branch-valve'
uci set dhcp.@host[-1].ip='192.168.50.54'
uci set dhcp.@host[-1].mac='XX:XX:XX:XX:XX:XX'
uci set dhcp.@host[-1].dns='1'

uci add dhcp host
uci set dhcp.@host[-1].name='ventsys-fdm-print-valve'
uci set dhcp.@host[-1].ip='192.168.50.55'
uci set dhcp.@host[-1].mac='XX:XX:XX:XX:XX:XX'
uci set dhcp.@host[-1].dns='1'

uci add dhcp host
uci set dhcp.@host[-1].name='ventsys-sla-print-valve'
uci set dhcp.@host[-1].ip='192.168.50.56'
uci set dhcp.@host[-1].mac='XX:XX:XX:XX:XX:XX'
uci set dhcp.@host[-1].dns='1'

# 360-degree intake valves
uci add dhcp host
uci set dhcp.@host[-1].name='ventsys-fdm-360-valve'
uci set dhcp.@host[-1].ip='192.168.50.61'
uci set dhcp.@host[-1].mac='XX:XX:XX:XX:XX:XX'
uci set dhcp.@host[-1].dns='1'

uci add dhcp host
uci set dhcp.@host[-1].name='ventsys-sla-360-valve'
uci set dhcp.@host[-1].ip='192.168.50.62'
uci set dhcp.@host[-1].mac='XX:XX:XX:XX:XX:XX'
uci set dhcp.@host[-1].dns='1'

# Bambu Lab P1S Printer (LAN — VLAN 1)
# Stays on VLAN 1 so Bambu Studio on user laptop can reach it directly.
# Bambuddy (Frigate VM, 192.168.30.20) reaches it via 'Bambuddy to P1S' firewall rule.
uci add dhcp host
uci set dhcp.@host[-1].name='bambu-p1s'
uci set dhcp.@host[-1].ip='192.168.1.200'
uci set dhcp.@host[-1].mac='XX:XX:XX:XX:XX:XX'
uci set dhcp.@host[-1].dns='1'

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
uci set dhcp.@domain[-1].name='bambuddy.home.local'
uci set dhcp.@domain[-1].ip='192.168.20.102'

uci add dhcp domain
uci set dhcp.@domain[-1].name='frigate.home.local'
uci set dhcp.@domain[-1].ip='192.168.30.20'

uci add dhcp domain
uci set dhcp.@domain[-1].name='nvr.home.local'
uci set dhcp.@domain[-1].ip='192.168.30.1'

uci add dhcp domain
uci set dhcp.@domain[-1].name='printers.home.local'
uci set dhcp.@domain[-1].ip='192.168.35.1'

uci add dhcp domain
uci set dhcp.@domain[-1].name='p1s.home.local'
uci set dhcp.@domain[-1].ip='192.168.35.200'

uci add dhcp domain
uci set dhcp.@domain[-1].name='athena2.home.local'
uci set dhcp.@domain[-1].ip='192.168.35.201'

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
if uci show dhcp | grep -q "ventsys-main-fan"; then  # A9-5 fix: was ventsys-fan-controller (stale name)
    echo "✓ VentSys static reservations configured" >> /tmp/phase3_validation.txt
else
    echo "✗ VentSys static reservations missing" >> /tmp/phase3_validation.txt
fi

cat /tmp/phase3_validation.txt
```

## Success Criteria for Phase 3

- **All DHCP scopes operational**: 10 network segments with appropriate ranges
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
