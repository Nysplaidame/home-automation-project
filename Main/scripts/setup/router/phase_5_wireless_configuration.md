# Phase 5: Wireless Configuration

**Duration**: 3-4 hours  
**Risk Level**: Medium-High (multi-SSID complexity)  
**Prerequisites**: Phase 4 completed, firewall rules operational

## Overview
Implements multi-SSID wireless architecture mapping 6 SSIDs to appropriate VLANs. Establishes WiFi-based access to network segments with proper security isolation. Critical for VentSys IoT device connectivity and guest access while maintaining security segmentation.

## Interdependencies

### Input Requirements
- All VLAN interfaces operational (Phase 2)
- Firewall zones configured (Phase 4)
- WiFi passwords generated (Phase 1)
- Radio hardware verified (Phase 1)

### Output Deliverables
- 6 SSIDs operational with proper VLAN mapping
- Channel separation strategy implemented
- Security configurations (WPA3/WPA2) applied appropriately
- VentSys IoT SSID ready for sensor connectivity
- HomePrinters SSID ready for printer VLAN connectivity

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

# Generate printers password if not already created in Phase 1
if [ ! -f "/etc/wireless/credentials/printers_password.txt" ]; then
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-24 > /etc/wireless/credentials/printers_password.txt
    chmod 600 /etc/wireless/credentials/printers_password.txt
    echo "✓ HomePrinters WiFi password generated" >> /tmp/phase5_validation.txt
else
    echo "✓ HomePrinters WiFi credentials available" >> /tmp/phase5_validation.txt
fi

# Verify required VLAN interfaces exist
for vlan in lan management printers iot_sensors guest; do
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
# CRITICAL: In OpenWrt mac80211, ALL SSIDs on a radio share ONE channel.
# Per-interface channel settings are silently ignored — only this radio-level
# setting takes effect. Channel 6 is chosen because:
#   - HomeIoT (VentSys fire safety) requires a fixed, stable channel
#   - Channel 6 is a standard non-overlapping 2.4GHz channel (1/6/11)
#   - All 2.4GHz SSIDs (HomeMain-2G, HomeAdmin-2G, HomeIoT, HomeGuest) share it
uci set wireless.radio0.channel='6'
uci set wireless.radio0.htmode='HE40'
uci set wireless.radio0.country='GB'      # UK regulatory domain — CRITICAL: do not use 'US'
uci set wireless.radio0.txpower='20'
uci set wireless.radio0.mu_beamformer='1'
uci set wireless.radio0.legacy_rates='1'

# Configure 5GHz radio (radio1) 
uci set wireless.radio1.type='mac80211'
uci set wireless.radio1.band='5g'
uci set wireless.radio1.channel='auto'
uci set wireless.radio1.htmode='HE80'
uci set wireless.radio1.country='GB'      # UK regulatory domain — CRITICAL: do not use 'US'
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

### 5.6b Printers WiFi (HomePrinters - VLAN 35)
**Duration**: 15 minutes

```bash
# Load printers password
PRINTERS_PASSWORD=$(cat /etc/wireless/credentials/printers_password.txt)

# Printers Network — 5GHz only (keeps 2.4GHz free for safety-critical HomeIoT)
# P1S supports 802.11ac — 5GHz fully compatible.
uci add wireless wifi-iface
uci set wireless.@wifi-iface[-1].device='radio1'
uci set wireless.@wifi-iface[-1].mode='ap'
uci set wireless.@wifi-iface[-1].ssid='HomePrinters'
uci set wireless.@wifi-iface[-1].network='printers'
uci set wireless.@wifi-iface[-1].encryption='psk2'
uci set wireless.@wifi-iface[-1].key="$PRINTERS_PASSWORD"
uci set wireless.@wifi-iface[-1].ieee80211w='0'
uci set wireless.@wifi-iface[-1].isolate='1'
uci set wireless.@wifi-iface[-1].maxassoc='10'

echo "HomePrinters SSID configured on radio1 (5GHz, VLAN 35)" >> /tmp/deployment_logs/phase5.log
``` (HomeDMZ - VLAN 70) - Disabled by Default
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

### 5.8 Channel Strategy Note
**Duration**: 5 minutes

```bash
# IMPORTANT: Per-interface channel overrides DO NOT WORK in OpenWrt mac80211.
# All SSIDs on a radio share a single channel set at the radio level (step 5.2).
# No UCI commands are needed here — channel 6 is already set on radio0 in step 5.2.
#
# 2.4GHz (radio0): ALL SSIDs (HomeMain-2G, HomeAdmin-2G, HomeIoT, HomeGuest) use channel 6.
# 5GHz (radio1): auto channel selection (HomeMain-5G, HomeAdmin-5G).
#
# If you need strict channel separation between SSIDs (e.g., IoT on ch6 vs Main on ch1),
# the only option is a second physical access point on a separate radio.
#
# Channel 6 was chosen for radio0 because HomeIoT (fire safety) requires a fixed,
# stable channel, and 6 is a standard non-overlapping 2.4GHz channel.

echo "Channel strategy: radio0 fixed channel 6 (set in step 5.2), radio1 auto (set in step 5.2)" >> /tmp/deployment_logs/phase5.log
echo "No per-interface channel overrides possible — mac80211 architecture" >> /tmp/deployment_logs/phase5.log
```

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
expected_ssids=("HomeMain" "HomeAdmin" "HomeAdmin-2G" "HomePrinters" "HomeIoT" "HomeGuest")
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
    "HomePrinters:printers"
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
isolation_required=("HomePrinters" "HomeIoT" "HomeGuest")
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
**Duration**: 5 minutes

```bash
echo "=== Channel Strategy Validation ===" > /tmp/phase5_channel_test.txt

# Verify radio0 is on channel 6 (the only channel that matters for 2.4GHz)
radio0_channel=$(uci get wireless.radio0.channel 2>/dev/null)
if [ "$radio0_channel" = "6" ]; then
    echo "✓ radio0 channel 6 confirmed (all 2.4GHz SSIDs share this)" >> /tmp/phase5_channel_test.txt
else
    echo "✗ radio0 channel is '$radio0_channel' — expected '6'" >> /tmp/phase5_channel_test.txt
fi

# Verify radio0 country code is GB
radio0_country=$(uci get wireless.radio0.country 2>/dev/null)
if [ "$radio0_country" = "GB" ]; then
    echo "✓ radio0 country code: GB" >> /tmp/phase5_channel_test.txt
else
    echo "✗ radio0 country code is '$radio0_country' — expected 'GB'" >> /tmp/phase5_channel_test.txt
fi

# Verify radio1 country code is GB
radio1_country=$(uci get wireless.radio1.country 2>/dev/null)
if [ "$radio1_country" = "GB" ]; then
    echo "✓ radio1 country code: GB" >> /tmp/phase5_channel_test.txt
else
    echo "✗ radio1 country code is '$radio1_country' — expected 'GB'" >> /tmp/phase5_channel_test.txt
fi

# Verify 5GHz auto channel
radio1_channel=$(uci get wireless.radio1.channel 2>/dev/null)
if [ "$radio1_channel" = "auto" ]; then
    echo "✓ radio1 auto channel selection active" >> /tmp/phase5_channel_test.txt
else
    echo "✗ radio1 channel is '$radio1_channel' — expected 'auto'" >> /tmp/phase5_channel_test.txt
fi

cat /tmp/phase5_channel_test.txt
```

Success Criteria for Phase 5

All SSIDs broadcasting: 5 SSIDs visible with correct configurations
VLAN mappings correct: Each SSID properly assigned to intended VLAN
Security configurations appropriate: WPA3/WPA2 selections match requirements
Channel configuration correct: radio0 fixed on channel 6 (all 2.4GHz SSIDs share this — mac80211 architecture, per-interface overrides silently ignored); radio1 on auto
VentSys IoT ready: HomeIoT SSID operational on VLAN 50 for sensor connectivity
Client isolation active: IoT and Guest networks prevent inter-client communication
Connection limits enforced: Guest and admin networks have appropriate limits

Failure Analysis and Resolution
Minor Issues

SSID not broadcasting: Check interface configuration and restart wireless
Wrong VLAN assignment: Verify network interface mappings
Security problems: Check encryption settings and key validity
Channel conflicts: Not applicable — all 2.4GHz SSIDs share a single channel
  (set at radio0 level, not per-SSID). If interference is a problem, change
  radio0.channel in UCI (step 5.2). Per-SSID channel separation is not
  possible in OpenWrt mac80211 — see step 5.8 Channel Strategy Note.

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