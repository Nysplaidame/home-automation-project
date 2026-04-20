# OpenWrt GL-MT6000 Deployment Script - Comprehensive Analysis

## Executive Summary

**CRITICAL: This script is NOT production-ready and is NOT idempotent.** Running it multiple times will create hundreds of duplicate configuration entries, regenerate all security credentials (breaking existing VPN/WiFi connections), and potentially corrupt the router configuration.

**Overall Assessment:**
- Network topology design: ✅ Excellent
- Security architecture: ✅ Very good
- Idempotency: ❌ CRITICAL FAILURES (100+ issues)
- Error handling: ⚠️  Insufficient
- OpenWrt compatibility: ⚠️  Minor issues
- Missing configurations: ❌ Critical firewall rule missing

---

## CRITICAL ISSUES (Must Fix Before Deployment)

### 1. WireGuard VPN Completely Non-Functional
**Severity: CRITICAL** | **Location: Phase 4** | **Impact: VPN will not work**

The script creates a WireGuard VPN server but **never adds a firewall rule to allow incoming VPN connections from the internet**.

```bash
# MISSING from Phase 4:
uci add firewall rule
uci set firewall.@rule[-1].name='Allow-WireGuard-WAN'
uci set firewall.@rule[-1].src='wan'
uci set firewall.@rule[-1].dest_port='51820'
uci set firewall.@rule[-1].proto='udp'
uci set firewall.@rule[-1].target='ACCEPT'
```

**Impact:** All VPN connection attempts from external networks will be blocked by the firewall.

---

### 2. Credential Regeneration Breaks Existing Connections
**Severity: CRITICAL** | **Location: Phase 1, Lines 66-100** | **Impact: All clients disconnected**

The script **always** regenerates:
- WireGuard keys (5 sets)
- WiFi passwords (5 passwords)

**Current code:**
```bash
wg genkey | tee /etc/wireguard/keys/server_private.key | wg pubkey > /etc/wireguard/keys/server_public.key
openssl rand -base64 32 | tr -d "=+/" | cut -c1-24 > /etc/wireless/credentials/main_password.txt
```

**Required fix:**
```bash
if [ ! -f /etc/wireguard/keys/server_private.key ]; then
    wg genkey | tee /etc/wireguard/keys/server_private.key | wg pubkey > /etc/wireguard/keys/server_public.key
fi

if [ ! -f /etc/wireless/credentials/main_password.txt ]; then
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-24 > /etc/wireless/credentials/main_password.txt
fi
```

**Impact:** Running the script a second time disconnects all WiFi devices and breaks all VPN connections.

---

### 3. Firewall Configuration Accumulates Exponentially
**Severity: CRITICAL** | **Location: Phase 4** | **Impact: 100+ duplicate rules on re-run**

**Non-idempotent sections:**
- 10 firewall zones (lines 584-642): Each re-run adds 10 duplicate zones
- ~20 forwarding rules (lines 650-715): Duplicates on each run
- ~30 firewall rules (lines 675-778): Guest isolation loop adds 8 rules per run, DMZ adds 5 rules per run

**Example problematic code:**
```bash
# Lines 745-754 - Guest isolation
for zone in lan management automation cctv storage iot_sensors monitoring dmz; do
    uci add firewall rule  # Creates 8 rules each time
    uci set firewall.@rule[-1].name="Block Guest to $zone"
    # ...
done
```

**After 3 runs:** 3 zone definitions, 60 forwarding rules, 90+ firewall rules
**After 10 runs:** 10 zone definitions, 200 forwarding rules, 300+ firewall rules

**Required approach:**
```bash
# Delete all existing zones first
while uci -q delete firewall.@zone[0]; do :; done

# Delete all forwardings
while uci -q delete firewall.@forwarding[0]; do :; done

# Delete all rules
while uci -q delete firewall.@rule[0]; do :; done

# Then add fresh configuration
```

---

### 4. VLAN Configuration Creates Duplicates
**Severity: CRITICAL** | **Location: Phase 2, Lines 216-318** | **Impact: Multiple VLAN definitions**

Every VLAN uses `uci add network bridge-vlan`, creating duplicates on each run.

**Example:**
```bash
# Checkpoint 2 - VLAN 1
uci add network bridge-vlan  # Creates NEW entry every time
uci set network.@bridge-vlan[-1].vlan='1'
```

**After 5 runs:** 5 definitions of each VLAN (45 total bridge-vlan entries instead of 9)

**Required fix:**
```bash
# At start of Phase 2, after bridge creation:
while uci -q delete network.@bridge-vlan[0]; do :; done

# Then add all VLANs fresh
```

---

### 5. DHCP Static Hosts Accumulate
**Severity: HIGH** | **Location: Phase 3, Lines 486-522** | **Impact: Duplicate reservations**

**Current code:**
```bash
uci add dhcp host
uci set dhcp.@host[-1].name='proxmox-host'
uci set dhcp.@host[-1].mac='XX:XX:XX:XX:XX:01'
uci set dhcp.@host[-1].ip='192.168.10.10'
```

**After 3 runs:** 3 reservations for same device (18 total host entries instead of 6)

**Required fix:**
```bash
# Clear all static hosts first
while uci -q delete dhcp.@host[0]; do :; done

# Or use named sections:
uci set dhcp.proxmox_host=host
uci set dhcp.proxmox_host.name='proxmox-host'
uci set dhcp.proxmox_host.mac='XX:XX:XX:XX:XX:01'
uci set dhcp.proxmox_host.ip='192.168.10.10'
```

---

### 6. WiFi Interface Duplication
**Severity: HIGH** | **Location: Phase 5, Lines 811-876** | **Impact: Duplicate SSIDs**

**Current code:**
```bash
uci add wireless wifi-iface
uci set wireless.@wifi-iface[-1].device='radio0'
uci set wireless.@wifi-iface[-1].ssid='HomeMain'
```

**After 3 runs:** 3 instances of each SSID (18 WiFi interfaces instead of 6)

**Required fix:**
```bash
# Delete all wifi-iface entries first
while uci -q delete wireless.@wifi-iface[0]; do :; done
```

---

### 7. Cron Job Multiplication
**Severity: MEDIUM** | **Location: Phase 8, Lines 1085-1087** | **Impact: Multiple monitoring processes**

**Current code:**
```bash
echo "*/15 * * * * /usr/local/bin/ventsys_network_monitor.sh" >> /etc/crontabs/root
```

**After 5 runs:** Script runs 5 times every 15 minutes (75 executions per hour instead of 4)

**Required fix:**
```bash
# Remove existing entry first
sed -i '/ventsys_network_monitor/d' /etc/crontabs/root
echo "*/15 * * * * /usr/local/bin/ventsys_network_monitor.sh" >> /etc/crontabs/root
```

---

## HIGH PRIORITY ISSUES

### 8. Bridge Device Deletion is Dangerous
**Severity: HIGH** | **Location: Phase 2, Line 195** | **Impact: Could delete wrong device**

**Current code:**
```bash
uci delete network.@device[0] 2>/dev/null || true
```

This blindly deletes the first device without knowing what it is. On a second run, devices might be in a different order.

**Required fix:**
```bash
# Delete specific device by name
uci -q delete network.br_lan || true
```

---

### 9. Shell Compatibility Issue
**Severity: HIGH** | **Location: Line 1** | **Impact: May not run on OpenWrt**

**Current shebang:**
```bash
#!/bin/bash
```

OpenWrt typically uses BusyBox ash, not bash. While most commands are compatible, bash may not be installed by default.

**Required fix:**
```bash
#!/bin/sh

# Or add to prerequisites:
opkg install bash
```

---

### 10. Placeholder MAC Addresses
**Severity: HIGH** | **Location: Phase 3, Lines 490-520** | **Impact: DHCP won't work**

All static DHCP reservations use placeholder MACs:
```bash
uci set dhcp.@host[-1].mac='XX:XX:XX:XX:XX:01'
```

**Impact:** These must be updated with real MAC addresses before deployment or DHCP reservations will fail.

---

## MEDIUM PRIORITY ISSUES

### 11. Missing Error Handling
**Severity: MEDIUM** | **Location: Throughout** | **Impact: Failures may go unnoticed**

The script uses `set -e` but then defeats it with `|| true` in many places. There's no consistent error handling strategy.

**Recommendations:**
- Remove `set -e` and add proper error checking
- Or use `set -e` consistently and remove all `|| true` except where truly optional
- Add verification after critical operations

---

### 12. Public IP Retrieval Can Fail
**Severity: MEDIUM** | **Location: Phase 6, Line 951** | **Impact: Client configs have placeholder**

**Current code:**
```bash
WAN_IP=$(wget -qO- http://ipecho.net/plain 2>/dev/null || echo "YOUR_PUBLIC_IP")
```

**Issues:**
- Uses unencrypted HTTP
- External service might be unreachable
- No notification if retrieval fails

**Better approach:**
```bash
WAN_IP=$(wget -qO- https://api.ipify.org 2>/dev/null)
if [ -z "$WAN_IP" ]; then
    echo "WARNING: Could not retrieve public IP address"
    echo "Please manually update WireGuard client configs"
    WAN_IP="YOUR_PUBLIC_IP_HERE"
fi
```

---

### 13. Excessive Network Restarts
**Severity: MEDIUM** | **Location: Throughout** | **Impact: Long execution time, connection drops**

The script restarts network services 15+ times with 30-second waits (7-8 minutes of waiting).

**Recommendations:**
- Batch UCI changes where possible
- Reduce sleep times where safe
- Add actual connectivity verification instead of fixed waits

---

### 14. Backup Strategy Flaw
**Severity: MEDIUM** | **Location: Phase 1, Line 41** | **Impact: Backups lost on failure**

All backups are stored on the router itself in `/etc/config/backups/` and `/tmp/`.

**Impact:** If the router fails or needs factory reset, all backups are lost.

**Required:** Document that backups should be copied off-router before proceeding.

---

### 15. Permissions Too Restrictive
**Severity: MEDIUM** | **Location: Phase 1, Lines 129-130** | **Impact: System scripts inaccessible**

**Current code:**
```bash
mkdir -p /usr/local/bin
chmod 700 /usr/local/bin/
```

Setting `/usr/local/bin` to 700 prevents non-root users from accessing system utilities.

**Required fix:**
```bash
chmod 755 /usr/local/bin/  # Standard for system directories
```

---

### 16. WireGuard Peer Accumulation
**Severity: MEDIUM** | **Location: Phase 6, Lines 920-937** | **Impact: Duplicate peer entries**

**Current code:**
```bash
uci add network wireguard_wg0
uci set network.@wireguard_wg0[-1].public_key="$CLIENT1_PUBLIC_KEY"
```

**After 3 runs:** 9 peer entries instead of 3

**Required fix:**
```bash
# Delete all existing wireguard peers first
while uci -q delete network.@wireguard_wg0[0]; do :; done
```

---

### 17. DNS Domain Accumulation
**Severity: MEDIUM** | **Location: Phase 3, Lines 524-542** | **Impact: Duplicate DNS entries**

**Current code:**
```bash
uci add dhcp domain
uci set dhcp.@domain[-1].name='router.home.local'
```

**After 5 runs:** 25 domain entries instead of 5

**Required fix:**
```bash
# Clear existing domains first
while uci -q delete dhcp.@domain[0]; do :; done
```

---

## LOW PRIORITY ISSUES & OBSERVATIONS

### 18. No Package Installation Check
**Severity: LOW** | **Location: Phase 1, Lines 44-51** | **Impact: Unnecessary reinstalls**

Packages are installed without checking if they already exist. While harmless, it's inefficient.

**Better approach:**
```bash
opkg list-installed | grep -q wireguard-tools || opkg install wireguard-tools
```

---

### 19. Unicode Characters May Not Display
**Severity: LOW** | **Location: Throughout** | **Impact: Cosmetic**

The script uses Unicode checkmarks (✓/✗) which may not render correctly in all terminals.

**Safer alternatives:**
```bash
echo "[ OK ] Service running"
echo "[FAIL] Service not running"
```

---

### 20. Verification Command Inconsistency
**Severity: LOW** | **Location: Phase 2, Line 214** | **Impact: Command doesn't exist**

The verification step suggests: `brctl show br-lan`

However, DSA systems don't use `brctl`. The correct command is:
```bash
bridge link show  # Shows bridge port configuration
```

---

### 21. Missing System Validation
**Severity: LOW** | **Location: Phase 1** | **Impact: May run on wrong hardware**

The script doesn't verify:
- Router model (should be GL-MT6000)
- OpenWrt version compatibility
- Available flash storage
- Current configuration state

**Recommendation:** Add at start:
```bash
# Verify hardware
MODEL=$(cat /tmp/sysinfo/model 2>/dev/null)
if [[ "$MODEL" != *"GL-MT6000"* ]]; then
    echo "WARNING: This script is designed for GL-MT6000"
    echo "Current model: $MODEL"
    read -p "Continue anyway? (yes/no): " CONFIRM
    [ "$CONFIRM" != "yes" ] && exit 1
fi
```

---

### 22. Temporary Files in /tmp
**Severity: LOW** | **Location: Throughout** | **Impact: Lost on reboot**

Many important files are stored in `/tmp/`:
- Baseline backups
- Validation reports
- WiFi credentials summary
- WireGuard keys summary

**Impact:** All lost on reboot. These should be in `/etc/` or explicitly documented as temporary.

---

### 23. No IPv6 Firewall Rules
**Severity: LOW** | **Location: Phase 4** | **Impact: IPv6 traffic may not be properly filtered**

The script enables IPv6 (wan6, DHCPv6, RA) but doesn't create corresponding firewall rules for IPv6 traffic between zones.

**Note:** OpenWrt typically handles basic IPv6 firewall automatically, but explicit rules may be needed for VentSys security.

---

### 24. VPN Zone Created Before VPN Interface
**Severity: LOW** | **Location: Phase 4 vs Phase 6** | **Impact: Confusing order**

Phase 4 (line 638) creates firewall zone for `wg0`, but Phase 6 (line 908) creates the `wg0` interface.

**Impact:** Should still work (zones can reference non-existent interfaces), but it's confusing and poor design.

**Recommendation:** Either reorder phases or add a note explaining this dependency.

---

## CONFIGURATION CORRECTNESS

### Network Topology - VALIDATED ✓

The VLAN topology is **correctly designed and internally consistent**:

| VLAN | Physical Ports | Subnet | Purpose | Internet |
|------|---------------|---------|---------|----------|
| 1 | lan5 (untagged), lan1 (tagged) | 192.168.1.0/24 | Rescue/Admin | Yes |
| 10 | lan2 (untagged), lan1 (tagged), lan4 (tagged) | 192.168.10.0/24 | Management | Yes |
| 20 | lan1 (tagged) | 192.168.20.0/24 | Automation/HA | Yes |
| 30 | lan3 (untagged), lan1 (tagged) | 192.168.30.0/24 | CCTV | No |
| 40 | lan4 (untagged), lan1 (tagged) | 192.168.40.0/24 | Storage | No |
| 50 | lan1 (tagged) | 192.168.50.0/24 | IoT Sensors | No |
| 60 | lan1 (tagged) | 192.168.60.0/24 | Monitoring | Yes |
| 70 | lan1 (tagged) | 192.168.70.0/24 | DMZ | Yes |
| 99 | None (WiFi only) | 192.168.99.0/24 | Guest | Yes |

**Port Strategy:**
- **lan5 (1Gb):** Rescue port - always accessible on VLAN 1
- **lan1 (2.5Gb):** High-speed trunk — ideal for Proxmox carrying all VLANs
- **lan4 (1Gb):** NAS direct connection — VLAN 40 untagged
- **lan2 (1Gb):** Dedicated management
- **lan3 (1Gb):** Dedicated CCTV

---

### Security Design - EXCELLENT ✓

The security architecture is **well-designed**:

**Zone Isolation:**
- IoT sensors cannot reach internet (prevents phoning home)
- CCTV cameras isolated from internet
- Storage isolated from internet
- Guest network isolated from all internal networks
- DMZ properly restricted

**VentSys-Specific Rules (EXCELLENT):**
```
✓ Home Assistant can access IoT sensors
✓ IoT sensors can send MQTT to HA (port 8883)
✓ ESPHome API enabled (port 6053)
✓ IoT blocked from internet
✓ IoT devices isolated from each other (WiFi client isolation)
```

This is **exactly the right security model** for ESP32-based sensors.

---

### DHCP & IP Allocation - VALIDATED ✓

All IP ranges are properly configured with no conflicts:

| Network | Gateway | DHCP Range | Static IPs | Lease Time |
|---------|---------|------------|------------|------------|
| VLAN 1 | .1 | .100-.200 | - | 12h |
| VLAN 10 | .1 | .100-.150 | .10 (Proxmox) | 24h |
| VLAN 20 | .1 | .110-.150 | .101 (HA) | 24h |
| VLAN 30 | .1 | .100-.150 | .20 (Frigate) | 24h |
| VLAN 40 | .1 | .100-.140 | .50 (NAS) | 24h |
| VLAN 50 | .1 | .100-.191 | .81-.82 (VentSys) | 6h |
| VLAN 60 | .1 | .100-.150 | - | 24h |
| VLAN 70 | .1 | .100-.150 | - | 12h |
| VLAN 99 | .1 | .100-.151 | - | 2h |

**Observations:**
- No overlaps between DHCP ranges and static assignments ✓
- Guest network has short lease time (2h) - appropriate ✓
- IoT sensors have shorter lease (6h) - reasonable for sensors ✓

---

### WiFi Configuration - VALIDATED ✓

| SSID | Radio | VLAN | Encryption | PMF | Isolation | Purpose |
|------|-------|------|------------|-----|-----------|---------|
| HomeMain | 2.4+5GHz | 1 | WPA3/WPA2 | Optional | No | Primary |
| HomeAdmin | 5GHz | 10 | WPA3 | Required | No | Admin |
| HomeIoT | 2.4GHz | 50 | WPA2 | Disabled | Yes | ESP32 |
| HomeGuest | 2.4GHz | 99 | WPA2 | Disabled | Yes | Guests |
| HomeDMZ | 5GHz | 70 | WPA3 | Required | No | DMZ (disabled) |

**Security choices are appropriate:**
- WPA3 with WPA2 fallback for main network ✓
- WPA2-only for IoT (ESP32 compatibility) ✓
- Client isolation enabled for IoT and Guest ✓
- PMF disabled for IoT (required for many ESP devices) ✓
- 5GHz-only for admin access (less congested) ✓

---

## MISSING CONFIGURATIONS

### Critical Missing Items

1. **WireGuard WAN firewall rule** (see Critical Issue #1)
2. **Router web interface access rules** - Many zones can't reach router web UI
3. **SSH access rules** - No explicit SSH rules defined
4. **NTP configuration** - Time sync not configured
5. **System logging** - Remote syslog not configured

### Recommended Additions

```bash
# Allow router web interface from trusted zones
uci add firewall rule
uci set firewall.@rule[-1].name='Allow-WebUI-Management'
uci set firewall.@rule[-1].src='management'
uci set firewall.@rule[-1].dest_port='80 443'
uci set firewall.@rule[-1].proto='tcp'
uci set firewall.@rule[-1].target='ACCEPT'

# Allow SSH from management
uci add firewall rule
uci set firewall.@rule[-1].name='Allow-SSH-Management'
uci set firewall.@rule[-1].src='management'
uci set firewall.@rule[-1].dest_port='22'
uci set firewall.@rule[-1].proto='tcp'
uci set firewall.@rule[-1].target='ACCEPT'

# Configure NTP
uci set system.ntp.enabled='1'
uci set system.ntp.enable_server='1'
uci add_list system.ntp.server='0.openwrt.pool.ntp.org'
uci add_list system.ntp.server='1.openwrt.pool.ntp.org'
uci commit system
```

---

## SYNTAX VALIDATION

### Shell Script Syntax: ✓ VALID
- Shebang present
- Heredocs properly formatted
- Variable expansion correct
- Loop syntax valid
- Conditional statements proper

### UCI Command Syntax: ✓ VALID
- All `uci set` commands properly formatted
- `uci add` and `uci add_list` correct
- `uci commit` called after each section
- No syntax errors detected

### OpenWrt Compatibility: ⚠️ MINOR ISSUES
- Uses `#!/bin/bash` instead of `#!/bin/sh`
- References `brctl` command (deprecated)
- Otherwise fully compatible

---

## IDEMPOTENCY SUMMARY

### Complete List of Non-Idempotent Operations

| Phase | Operation | Count | Impact on Re-run |
|-------|-----------|-------|------------------|
| 1 | Key generation | 5 | Breaks VPN |
| 1 | Password generation | 5 | Disconnects WiFi |
| 2 | Bridge device | 1 | May delete wrong device |
| 2 | Bridge VLANs | 9 | Creates duplicates |
| 3 | DHCP hosts | 6 | Accumulates entries |
| 3 | DNS domains | 5 | Accumulates entries |
| 4 | Firewall zones | 10 | Multiplies zones |
| 4 | Forwarding rules | ~20 | Accumulates rules |
| 4 | Firewall rules | ~30 | Exponential growth |
| 5 | WiFi interfaces | 6 | Duplicate SSIDs |
| 6 | WireGuard peers | 3 | Duplicate peers |
| 8 | Cron jobs | 1 | Multiple instances |

**Total:** ~100 non-idempotent operations

**After 5 runs:**
- 25 WiFi interfaces (should be 6)
- 50 firewall zones (should be 10)
- 100+ forwarding rules (should be ~20)
- 150+ firewall rules (should be ~30)
- 30 DHCP host entries (should be 6)
- 25 DNS domains (should be 5)
- All VPN connections broken
- All WiFi connections broken

---

## RECOMMENDATIONS

### Immediate Actions (Before Any Deployment)

1. **Fix WireGuard firewall rule** - VPN won't work without this
2. **Fix all idempotency issues** - Script will corrupt configuration on re-run
3. **Update placeholder MAC addresses** - DHCP won't work without real MACs
4. **Change shebang to #!/bin/sh** - Or install bash
5. **Copy all backups off-router** - Before starting deployment
6. **Test in VM first** - Use Proxmox to test before deploying to production

### Script Restructuring Recommendations

1. **Separate credential generation** - Run once, store securely
2. **Use named UCI sections** - Where possible instead of indexed
3. **Add cleanup functions** - Clear existing config before adding new
4. **Implement proper error handling** - Don't rely on `set -e`
5. **Add rollback capability** - Restore from specific checkpoint
6. **Break into modules** - Separate script per phase
7. **Add validation suite** - Comprehensive post-deployment checks

### Example Idempotent Pattern

```bash
#!/bin/sh

# Function to clear all firewall zones
clear_firewall_zones() {
    while uci -q delete firewall.@zone[0]; do :; done
}

# Function to create firewall zones idempotently
create_firewall_zones() {
    clear_firewall_zones
    
    # WAN zone
    uci set firewall.wan=zone
    uci set firewall.wan.name='wan'
    # ... rest of config
    
    # LAN zone  
    uci set firewall.lan=zone
    uci set firewall.lan.name='lan'
    # ... rest of config
    
    uci commit firewall
}
```

---

## DEPLOYMENT RISK ASSESSMENT

**Current State: HIGH RISK** ❌

| Risk Factor | Severity | Mitigation |
|-------------|----------|------------|
| VPN won't function | CRITICAL | Add firewall rule |
| Re-run corrupts config | CRITICAL | Fix idempotency |
| Connection loss during deployment | HIGH | Use rescue port |
| Backup loss on failure | MEDIUM | Copy backups off-router |
| Wrong hardware | LOW | Add model check |

**After Fixes: MEDIUM RISK** ⚠️

The network design itself is excellent, but the script implementation has critical flaws that must be fixed before production use.

---

## POSITIVE ASPECTS

Despite the critical issues, the script demonstrates:

✓ **Excellent network segmentation** - Well-designed VLAN topology  
✓ **Strong security architecture** - Proper zone isolation  
✓ **VentSys-optimized** - Perfect firewall rules for ESP32 sensors  
✓ **Good documentation** - Comprehensive comments and checkpoints  
✓ **Safety-conscious** - Interactive verification at each step  
✓ **Comprehensive scope** - Covers all aspects of router configuration  
✓ **Professional practices** - Backup strategy, emergency restore  

The underlying network design is **production-quality**. The script just needs idempotency fixes before deployment.

---

## FINAL VERDICT

**Network Design: A+**  
**Script Implementation: D** (Critical failures)  
**After Idempotency Fixes: B+**  

**Recommendation:** Fix all CRITICAL issues before any deployment. Consider this a solid architecture blueprint that needs implementation refinement.
