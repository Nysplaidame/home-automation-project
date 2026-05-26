# OpenWrt WiFi Configuration - Multi-SSID VLAN Setup

**File:** `/etc/config/wireless`  
**Hardware:** GL.iNet GL-MT6000 dual-band WiFi 6  
**Version:** 1.0  
**Date:** 2025-09-24

## SSID Architecture

| SSID | VLAN | Bands | Security | Purpose |
|------|------|-------|----------|---------|
| **HomeMain** | VLAN 1 | 2.4GHz + 5GHz | WPA3 | Main user network |
| **HomeAdmin** | VLAN 10 | 5GHz + hidden 2.4GHz backup | WPA3 | Admin devices |
| **HomePrinters** | VLAN 35 | 2.4GHz + 5GHz | WPA2 | Bambu P1S + printer VLAN |
| **HomeIoT** | VLAN 50 | 2.4GHz only | WPA2 | IoT sensors |
| **HomeGuest** | Isolated | 2.4GHz only | WPA2 | Guest access |

## Configuration File

```bash
# File equivalent: /etc/config/wireless
# GL.iNet GL-MT6000 WiFi Configuration - Multi-SSID VLAN Setup

# ============================================================================
# RADIO CONFIGURATION
# ============================================================================

# 2.4GHz Radio Configuration
config wifi-device 'radio0'
    option type 'mac80211'
    option path 'platform/18000000.wmac'
    option band '2g'
    option channel 'auto'
    option htmode 'HE40'
    option country 'US'
    option txpower '20'
    option mu_beamformer '1'
    option legacy_rates '1'
    
# 5GHz Radio Configuration  
config wifi-device 'radio1'
    option type 'mac80211'
    option path 'pci0000:00/0000:00:01.0/0000:01:00.0'
    option band '5g'
    option channel 'auto'
    option htmode 'HE80'
    option country 'US'
    option txpower '23'
    option mu_beamformer '1'

# ============================================================================
# MAIN USER NETWORK - VLAN 1 (2.4GHz + 5GHz)
# Primary WiFi for phones, laptops, tablets, smart TVs
# ============================================================================

# Main Network - 2.4GHz
config wifi-iface 'main_2g'
    option device 'radio0'
    option mode 'ap'
    option ssid 'HomeMain'
    option network 'lan'
    option encryption 'sae-mixed'
    option key 'YOUR_MAIN_WIFI_PASSWORD_HERE'
    option ieee80211w '1'
    option wpa_disable_eapol_key_retries '1'
    option bss_transition '1'
    option wnm_sleep_mode '1'
    
# Main Network - 5GHz
config wifi-iface 'main_5g'
    option device 'radio1'
    option mode 'ap'
    option ssid 'HomeMain'
    option network 'lan'
    option encryption 'sae-mixed'
    option key 'YOUR_MAIN_WIFI_PASSWORD_HERE'
    option ieee80211w '1'
    option wpa_disable_eapol_key_retries '1'
    option bss_transition '1'
    option wnm_sleep_mode '1'

# ============================================================================
# ADMIN NETWORK - VLAN 10 (2.4GHz only)
# Administrative devices, management laptops, admin tablets
# ============================================================================

config wifi-iface 'admin_2g'
    option device 'radio0'
    option mode 'ap'
    option ssid 'HomeAdmin'
    option network 'management'
    option encryption 'sae'
    option key 'YOUR_ADMIN_WIFI_PASSWORD_HERE'
    option ieee80211w '2'
    option wpa_disable_eapol_key_retries '1'
    option hidden '0'
    option maxassoc '8'
    # Optional: Set hidden '1' for additional security through obscurity

# ============================================================================
# IOT SENSORS NETWORK - VLAN 50 (2.4GHz only)
# Fire safety sensors, environmental monitors, smart switches
# ============================================================================

config wifi-iface 'iot_2g'
    option device 'radio0'
    option mode 'ap'
    option ssid 'HomeIoT'
    option network 'iot_sensors'
    option encryption 'psk2'
    option key 'YOUR_IOT_WIFI_PASSWORD_HERE'
    option ieee80211w '0'
    option maxassoc '20'
    option dtim_period '3'
    # Optimized for low-power IoT devices

# ============================================================================
# GUEST NETWORK - Isolated (2.4GHz only)
# Visitor access with internet only, no local network access
# ============================================================================

config wifi-iface 'guest_2g'
    option device 'radio0'
    option mode 'ap'
    option ssid 'HomeGuest'
    option network 'guest'
    option encryption 'psk2'
    option key 'YOUR_GUEST_WIFI_PASSWORD_HERE'
    option ieee80211w '0'
    option isolate '1'
    option maxassoc '10'
    # Note: Guest network interface needs to be created in /etc/config/network

# ============================================================================
# ADVANCED WIFI SETTINGS
# ============================================================================

# WiFi optimization for mixed device environment
config wifi-device 'radio0'
    # Additional 2.4GHz optimization
    option beacon_int '100'
    option rts '2346'
    option frag '2346'
    
config wifi-device 'radio1'  
    # Additional 5GHz optimization
    option beacon_int '100'
    option rts '2346'
    option frag '2346'
```

## Security Configuration

### Password Requirements
- **Main Network:** Strong WPA3 password (12+ characters, mixed case, numbers, symbols)
- **Admin Network:** Very strong password (16+ characters, complex)
- **IoT Network:** Moderate password (devices may have input limitations)
- **Guest Network:** Simple but secure password (easy for visitors to type)

### Security Features Enabled
- **WPA3 (SAE)** for main and admin networks
- **Management Frame Protection** (IEEE 802.11w)
- **BSS Transition support** for seamless roaming
- **Connection limits** per SSID to prevent abuse
- **Guest isolation** to prevent inter-device communication

### Network Binding
- **HomeMain** → `lan` network (VLAN 1: 192.168.1.0/24)
- **HomeAdmin** → `management` network (VLAN 10: 192.168.10.0/24)  
- **HomeIoT** → `iot_sensors` network (VLAN 50: 192.168.50.0/24)
- **HomeGuest** → `guest` network (isolated, needs creation)

## Deployment Checklist

### Before Applying Configuration
1. **Replace passwords:** Change all `YOUR_*_PASSWORD_HERE` with actual strong passwords
2. **Verify hardware paths:** Confirm radio paths match your GL-MT6000
3. **Create guest network:** Add guest network interface in `/etc/config/network`
4. **Test SSID mapping:** Verify each SSID connects to correct VLAN
5. **Check firewall rules:** Ensure rules allow appropriate access per network

### Post-Deployment Testing
1. **IP assignment:** Connect to each SSID and verify correct IP range
2. **Internet access:** Test access per network security policies
3. **VLAN isolation:** Verify IoT can't reach internet, etc.
4. **Admin access:** Test administrative functions from HomeAdmin SSID
5. **Guest isolation:** Confirm guests can't see local devices

### Performance Monitoring
- Monitor WiFi client distribution across bands
- Check for 2.4GHz interference with multiple SSIDs
- Verify adequate throughput for main network users
- Monitor IoT device connectivity and power consumption

## Emergency Access
- Keep wired admin access available (lan2 port)
- Document SSID passwords securely  
- Consider USB recovery access for GL-MT6000

## Notes
- **WPA3 mixed mode** (`sae-mixed`) provides backward compatibility
- **IoT devices** often require WPA2 for compatibility
- **Guest network** requires additional firewall configuration
- **Radio paths** may vary by hardware revision
