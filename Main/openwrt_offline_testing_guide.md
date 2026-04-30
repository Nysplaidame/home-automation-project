# OpenWrt Configuration Offline Testing Guide

**Project:** Home Automation Safety - Network Infrastructure Validation  
**Router:** GL.iNet GL-MT6000 with OpenWrt  
**Architecture:** 10-VLAN Security Network + WireGuard VPN

## 🚨 **PRE-TEST SAFETY CHECKLIST**

### **⚠️ CRITICAL SAFETY MEASURES**
- [ ] **Console Access**: Ensure serial/console access as backup
- [ ] **Configuration Backup**: Save current working config
- [ ] **Rollback Plan**: Know how to restore previous config
- [ ] **Physical Access**: Maintain physical access to router
- [ ] **Test Incrementally**: Don't test everything at once

### **📋 PREPARATION COMMANDS**
```bash
# Create configuration backup
cp /etc/config/network /etc/config/network.backup
cp /etc/config/firewall /etc/config/firewall.backup  
cp /etc/config/dhcp /etc/config/dhcp.backup
cp /etc/config/wireless /etc/config/wireless.backup

# Document current status
uci show network > /tmp/network-before.txt
uci show firewall > /tmp/firewall-before.txt
ip addr show > /tmp/interfaces-before.txt
```

---

## 📱 **REQUIRED TEST EQUIPMENT**

### **MINIMUM SETUP** (Essential Tests)
- Admin laptop/device with ethernet cable
- One additional WiFi-capable device
- SSH client or console access

### **RECOMMENDED SETUP** (Comprehensive Tests)
- Admin laptop (ethernet + WiFi capable)
- Mobile device or tablet
- Additional laptop/desktop
- IoT device or smartphone for IoT network testing
- 4x Ethernet cables (to test each physical port)

### **OPTIONAL EQUIPMENT** (Full Validation)
- Multiple client devices for each network
- Network scanner/analyzer
- Raspberry Pi or similar for automated testing

---

## 🔧 **PHASE 1: BASIC INFRASTRUCTURE VERIFICATION**

### **Test 1.1: Network Interface Creation**

**Objective:** Verify all network interfaces are created and configured

**Commands:**
```bash
# Check all network interfaces
ip addr show

# Check UCI network configuration
uci show network | grep interface

# Check interface status
/etc/init.d/network status
```

**Expected Output:**
```
br-lan.1    (192.168.1.1/24)    # User network
br-lan.10   (192.168.10.1/24)   # Management  
br-lan.20   (192.168.20.1/24)   # Automation
br-lan.30   (192.168.30.1/24)   # NVR
br-lan.35   (192.168.35.1/24)   # Printers
br-lan.40   (192.168.40.1/24)   # Storage
br-lan.50   (192.168.50.1/24)   # IoT Sensors
br-lan.60   (192.168.60.1/24)   # Monitoring
br-lan.70   (192.168.70.1/24)   # DMZ
br-lan      (192.168.99.1/24)   # Guest
wg0         (10.0.0.1/24)       # VPN
```

**✅ SUCCESS CRITERIA:**
- [ ] All 10 VLAN gateway interfaces plus `wg0` present with correct IPs
- [ ] All interfaces in "UP" state
- [ ] No error messages in logs

**❌ TROUBLESHOOTING:**
```bash
# If interfaces missing:
uci commit network && /etc/init.d/network restart

# Check for errors:
logread | grep -i "network\|interface\|vlan"

# Manual interface creation test:
ip link add link br-lan name br-lan.10 type vlan id 10
```

---

### **Test 1.2: Bridge and VLAN Configuration**

**Objective:** Verify bridge setup and VLAN tagging

**Commands:**
```bash
# Check bridge configuration (new DSA style)
bridge vlan show

# Check bridge interfaces
brctl show br-lan

# Verify VLAN interface mapping
ls -la /sys/class/net/br-lan.*
```

**Expected Output:**
```bash
# bridge vlan show should show:
br-lan	 1 PVID Egress Untagged
	 10 Egress Untagged (lan2)
	 10 (lan1)
	 20 (lan1) 
	 30 Egress Untagged (lan3)
	 30 (lan1)
	 35 (lan1)
	 40 Egress Untagged (lan4)
	 40 (lan1)
	 50 (lan1)
	 60 (lan1)
	 70 (lan1)
```

**✅ SUCCESS CRITERIA:**
- [ ] All VLANs present on bridge
- [ ] Trunk port (lan1) carries all VLANs tagged
- [ ] Access ports have correct untagged VLANs
- [ ] VLAN interface files exist

---

### **Test 1.3: Physical Port Assignment**

**Objective:** Verify physical port mapping to VLANs

**Test Setup:** Connect ethernet cable to each port and check VLAN assignment

**Commands:**
```bash
# Check port status and link
ethtool lan1  # Should show link if connected
ethtool lan2
ethtool lan3  
ethtool lan4

# Check which VLAN each port maps to
bridge vlan show dev lan1
bridge vlan show dev lan2  
bridge vlan show dev lan3
bridge vlan show dev lan4
```

**Expected Port Mapping:**
- **lan1:** Trunk port (VLANs 10,20,30,35,40,50,60,70 tagged) → Proxmox
- **lan2:** VLAN 10 untagged → Management devices
- **lan3:** VLAN 30 untagged → Camera POE switch  
- **lan4:** VLAN 40 untagged → NAS

**✅ SUCCESS CRITERIA:**
- [ ] Each port shows correct VLAN assignment
- [ ] Trunk port (lan1) shows all VLANs
- [ ] Access ports show single untagged VLAN

---

## 🌐 **PHASE 2: DHCP AND DNS SERVICES**

### **Test 2.1: DHCP Server Configuration**

**Objective:** Verify DHCP servers are running for all networks

**Commands:**
```bash
# Check DHCP configuration
uci show dhcp | grep "dhcp\."

# Check DHCP service status
/etc/init.d/dnsmasq status

# Check active DHCP leases
cat /tmp/dhcp.leases

# Check DHCP listening interfaces
netstat -ulnp | grep :67
```

**Expected Output:**
```bash
# Should show DHCP server configs for:
dhcp.lan, dhcp.management, dhcp.automation,
dhcp.nvr, dhcp.printers, dhcp.storage, dhcp.iot_sensors,
dhcp.monitoring, dhcp.dmz, dhcp.guest
```

**✅ SUCCESS CRITERIA:**
- [ ] DHCP service running (PID shown)
- [ ] Listening on port 67 for all interfaces
- [ ] No configuration errors in logs

---

### **Test 2.2: DHCP IP Assignment Test**

**Objective:** Test DHCP assignment on different networks

**Test Method:** Connect device to different networks and verify IP assignment

**Management Network Test (via lan2 port):**
```bash
# Connect ethernet to lan2, should get 192.168.10.100-149
# On client device:
ipconfig /all  # Windows
ifconfig       # Linux/Mac

# Expected: IP in range 192.168.10.100-149
```

**User Network Test (via WiFi HomeMain):**
```bash
# Connect to HomeMain WiFi
# Expected: IP in range 192.168.1.100-199
```

**IoT Network Test (via WiFi HomeIoT):**
```bash  
# Connect to HomeIoT WiFi
# Expected: IP in range 192.168.50.100-190
```

**✅ SUCCESS CRITERIA:**
- [ ] Each network assigns IP from correct range
- [ ] Correct gateway IP (.1 on each network)
- [ ] Proper DNS server assignment
- [ ] Lease appears in `/tmp/dhcp.leases`

---

### **Test 2.3: Static IP Reservations**

**Objective:** Verify static IP reservations work correctly

**Commands:**
```bash
# Check static reservations
uci show dhcp | grep "host\."

# Check if static IPs are excluded from DHCP ranges
uci show dhcp | grep -E "(start|limit)"
```

**Expected Static IPs:**
- Proxmox: 192.168.10.10 (outside DHCP range 100-149)
- Home Assistant: 192.168.20.101 (outside DHCP range 110-149)
- Bambuddy: 192.168.20.102 (outside DHCP range 110-149)
- Frigate: 192.168.30.20 (outside DHCP range 100-149)
- Bambu P1S: 192.168.35.200 (outside DHCP range 100-149)
- Athena 2: 192.168.35.201 (outside DHCP range 100-149)
- NAS: 192.168.40.50 (outside DHCP range 100-139)

**✅ SUCCESS CRITERIA:**
- [ ] All static IPs outside their network's DHCP range
- [ ] MAC addresses configured (or placeholder present)
- [ ] No IP conflicts between static and dynamic ranges

---

### **Test 2.4: Local DNS Resolution**

**Objective:** Test local DNS resolution for home.local domain

**Commands:**
```bash
# From router, test DNS resolution
nslookup router.home.local 192.168.1.1
nslookup proxmox.home.local 192.168.10.1
nslookup homeassistant.home.local 192.168.20.1

# Check DNS configuration
uci show dhcp | grep domain
```

**From Client Device:**
```bash
nslookup router.home.local
nslookup nas.home.local  
ping router.home.local
```

**✅ SUCCESS CRITERIA:**
- [ ] Local hostnames resolve to correct IPs
- [ ] Each network can resolve local domains
- [ ] No DNS resolution errors

---

## 📶 **PHASE 3: WIFI FUNCTIONALITY**

### **Test 3.1: WiFi Radio and SSID Broadcasting**

**Objective:** Verify all WiFi SSIDs are broadcasting correctly

**Commands:**
```bash
# Check WiFi service status
/etc/init.d/network status

# Check radio configuration
iwinfo

# Check all configured SSIDs
uci show wireless | grep ssid

# Scan for broadcast SSIDs (from client device)
iwlist scan | grep ESSID
```

**Expected SSIDs:**
- **HomeMain** (2.4GHz + 5GHz) → VLAN 1
- **HomeAdmin** (5GHz) → VLAN 10  
- **HomeAdmin-2G** (2.4GHz, hidden) → VLAN 10
- **HomePrinters** (2.4GHz + 5GHz) → VLAN 35
- **HomeIoT** (2.4GHz) → VLAN 50
- **HomeGuest** (2.4GHz) → Guest network

**✅ SUCCESS CRITERIA:**
- [ ] All expected visible SSIDs visible; HomeAdmin-2G configured as hidden
- [ ] Both 2.4GHz and 5GHz radios active
- [ ] Signal strength reasonable for coverage area
- [ ] No WiFi errors in system logs

---

### **Test 3.2: WiFi Security and Authentication**

**Objective:** Test WiFi connection and security settings

**Authentication Tests:**

**HomeMain (WPA3-Mixed):**
```bash
# Test connection with WPA3 capable device
# Should connect with WPA3 (SAE)
# Fallback to WPA2 if WPA3 not supported
```

**HomeAdmin (WPA3-Only):**
```bash
# Should require WPA3 capable device
# Should reject WPA2-only devices
# Hidden SSID requires manual SSID entry
```

**HomeIoT (WPA2):**
```bash
# Should accept WPA2 devices
# Should isolate clients (no device-to-device communication)
```

**✅ SUCCESS CRITERIA:**
- [ ] Each SSID uses correct security protocol
- [ ] PMF settings work as configured
- [ ] Client isolation works where enabled
- [ ] Hidden SSIDs require manual configuration

---

### **Test 3.3: WiFi VLAN Mapping**

**Objective:** Verify WiFi clients get assigned to correct VLANs

**Test Method:** Connect to each SSID and verify IP assignment

**HomeMain → VLAN 1 Test:**
```bash
# Connect to HomeMain
# Expected IP: 192.168.1.100-199
# Gateway: 192.168.1.1
```

**HomeAdmin → VLAN 10 Test:**
```bash
# Connect to HomeAdmin
# Expected IP: 192.168.10.100-149  
# Gateway: 192.168.10.1
```

**HomeIoT → VLAN 50 Test:**
```bash
# Connect to HomeIoT
# Expected IP: 192.168.50.100-190
# Gateway: 192.168.50.1
```

**✅ SUCCESS CRITERIA:**
- [ ] Each WiFi network assigns correct IP range
- [ ] Gateway matches expected VLAN
- [ ] DNS server assignment correct
- [ ] Network isolation working (test ping between networks)

---

## 🛡️ **PHASE 4: FIREWALL STRUCTURE**

### **Test 4.1: Firewall Zone Configuration**

**Objective:** Verify firewall zones are created and bound to networks

**Commands:**
```bash
# Check firewall service
/etc/init.d/firewall status

# Show configured zones
uci show firewall | grep zone

# Check zone-to-network binding
uci show firewall | grep network

# Check actual iptables rules
iptables -L -n -v
```

**Expected Zones:**
- wan, lan, management, automation, nvr, printers, storage, iot_sensors
- monitoring, dmz, guest, vpn_clients

**✅ SUCCESS CRITERIA:**
- [ ] All 12 zones present
- [ ] Each zone bound to correct network interface
- [ ] Default policies set correctly (ACCEPT/REJECT)
- [ ] No firewall configuration errors

---

### **Test 4.2: Basic Firewall Rule Structure**

**Objective:** Verify firewall rules are loaded correctly

**Commands:**
```bash
# Check number of configured rules
uci show firewall | grep "rule\." | wc -l

# Check for critical rules
uci show firewall | grep -E "(Internet Access|Block.*Internet|HA to.*Access)"

# Check iptables chain structure
iptables -L FORWARD -n | head -20
```

**✅ SUCCESS CRITERIA:**
- [ ] Expected number of rules loaded
- [ ] Critical security rules present
- [ ] No duplicate or conflicting rules
- [ ] Chain structure looks correct

---

### **Test 4.3: Firewall Logging Test**

**Objective:** Verify firewall logging is working

**Commands:**
```bash
# Check if logging rules are active
iptables -L -n -v | grep LOG

# Generate test traffic and check logs
# (This will be limited offline, but can test structure)
logread | grep -E "(BLOCK|REJECT|DROP)"

# Check log rotation and storage
ls -la /var/log/
```

**✅ SUCCESS CRITERIA:**
- [ ] Logging rules present in iptables
- [ ] Log format includes prefixes for identification
- [ ] Logs are being written to expected location

---

## 🔄 **PHASE 5: INTER-NETWORK COMMUNICATION**

### **Test 5.1: Management Network Access**

**Objective:** Verify management network can access all other networks

**Test Setup:** Connect admin device to management network (lan2 or HomeAdmin WiFi)

**Test Commands:**
```bash
# From management device, test connectivity to each network:
ping 192.168.1.1      # User network
ping 192.168.20.1     # Automation  
ping 192.168.30.1     # NVR
ping 192.168.35.1     # Printers
ping 192.168.40.1     # Storage
ping 192.168.50.1     # IoT Sensors
ping 192.168.60.1     # Monitoring
ping 192.168.70.1     # DMZ
ping 192.168.99.1     # Guest

# Test specific service access
telnet 192.168.20.101 8123  # Home Assistant (if running)
ssh 192.168.30.20           # Frigate (if accessible)
```

**✅ SUCCESS CRITERIA:**
- [ ] Can ping all network gateways
- [ ] Can access services where configured
- [ ] No blocked connections from management

---

### **Test 5.2: Network Isolation Test**

**Objective:** Verify restricted networks cannot access inappropriate targets

**Test Setup:** Connect device to restricted network (IoT, NVR, Printers, Storage)

**IoT Network Isolation Test:**
```bash
# From IoT device (192.168.50.x):
ping 192.168.1.1      # Should FAIL (blocked)
ping 192.168.30.1     # Should FAIL (blocked NVR)
ping 192.168.35.1     # Should FAIL (blocked Printers)
ping 192.168.20.1     # Should SUCCEED (HA control)
ping 8.8.8.8          # Should FAIL (no internet)
```

**Guest Network Isolation Test:**
```bash
# From guest device (192.168.99.x):
ping 192.168.1.1      # Should FAIL (blocked)
ping 192.168.10.1     # Should FAIL (blocked)
ping 192.168.20.1     # Should FAIL (blocked)
# Note: Internet test not possible offline
```

**✅ SUCCESS CRITERIA:**
- [ ] Blocked connections properly rejected
- [ ] Allowed connections work correctly
- [ ] Isolation rules enforced as designed

---

### **Test 5.3: Home Assistant Integration Paths**

**Objective:** Verify HA can access required networks

**Test Setup:** From automation network (or simulate HA IP)

**Commands:**
```bash
# Simulate traffic from HA IP to test firewall rules
# (Limited without actual HA running, but can test basic connectivity)

# From automation network:
ping 192.168.30.1     # NVR network (Frigate)
ping 192.168.35.1     # Printers network
ping 192.168.40.1     # Storage network (NAS)
ping 192.168.50.1     # IoT network (sensors)
```

**Expected Results:**
- HA → NVR: ALLOWED (for Frigate control)
- HA → Printers: TRUST-BOUNDARY NOTE (Bambuddy and HA are same-subnet on VLAN 20)
- HA → Storage: ALLOWED (for backups)
- HA → IoT: ALLOWED (for sensor control)

**✅ SUCCESS CRITERIA:**
- [ ] HA can reach required networks
- [ ] Connections allowed by firewall rules
- [ ] No unexpected access granted

---

## 🔧 **PHASE 6: ADVANCED FEATURES**

### **Test 6.1: VPN Interface Configuration**

**Objective:** Verify WireGuard VPN interface is configured

**Commands:**
```bash
# Check WireGuard interface
ip addr show wg0

# Check WireGuard configuration
wg show

# Check VPN network interface
uci show network.vpn
uci show network.wg0

# Check if VPN zone is bound
uci show firewall | grep vpn
```

**✅ SUCCESS CRITERIA:**
- [ ] WireGuard interface exists with correct IP (10.0.0.1/24)
- [ ] Private key configured (or placeholder present)
- [ ] Listening on port 51820
- [ ] VPN zone properly configured

**Note:** Full VPN testing requires external client, not possible offline.

---

### **Test 6.2: Emergency Access Protocols**

**Objective:** Verify emergency rules exist but are disabled

**Commands:**
```bash
# Check for emergency rules
uci show firewall | grep -i emergency

# Verify emergency rules are disabled
uci show firewall | grep "enabled='0'"

# Check smart plug emergency access
uci show firewall | grep "192.168.50.71"
```

**✅ SUCCESS CRITERIA:**
- [ ] Emergency rules present in configuration
- [ ] All emergency rules disabled by default
- [ ] Rules target correct IP addresses
- [ ] Can be enabled if needed

---

### **Test 6.3: Configuration Backup and Restore**

**Objective:** Test configuration backup/restore functionality

**Commands:**
```bash
# Create system backup
sysupgrade -b /tmp/backup.tar.gz

# List backup contents
tar -tzf /tmp/backup.tar.gz | head -20

# Test configuration export
uci export > /tmp/config-export.txt

# Verify critical configs in backup
tar -xzf /tmp/backup.tar.gz -O etc/config/network | head -10
```

**✅ SUCCESS CRITERIA:**
- [ ] Backup created successfully
- [ ] All critical config files included
- [ ] Backup size reasonable (not empty)
- [ ] Export function works

---

## 📊 **COMPREHENSIVE TEST RESULTS MATRIX**

### **Test Results Summary**
Copy this matrix to track your test results:

| Test Category | Test Name | Status | Notes |
|---------------|-----------|--------|-------|
| **Phase 1: Infrastructure** | | | |
| 1.1 | Network Interface Creation | ⏳ | |
| 1.2 | Bridge and VLAN Config | ⏳ | |
| 1.3 | Physical Port Assignment | ⏳ | |
| **Phase 2: DHCP/DNS** | | | |
| 2.1 | DHCP Server Config | ⏳ | |
| 2.2 | DHCP IP Assignment | ⏳ | |
| 2.3 | Static IP Reservations | ⏳ | |
| 2.4 | Local DNS Resolution | ⏳ | |
| **Phase 3: WiFi** | | | |
| 3.1 | WiFi Radio & SSID Broadcasting | ⏳ | |
| 3.2 | WiFi Security & Authentication | ⏳ | |
| 3.3 | WiFi VLAN Mapping | ⏳ | |
| **Phase 4: Firewall** | | | |
| 4.1 | Firewall Zone Configuration | ⏳ | |
| 4.2 | Basic Firewall Rule Structure | ⏳ | |
| 4.3 | Firewall Logging Test | ⏳ | |
| **Phase 5: Inter-Network** | | | |
| 5.1 | Management Network Access | ⏳ | |
| 5.2 | Network Isolation Test | ⏳ | |
| 5.3 | HA Integration Paths | ⏳ | |
| **Phase 6: Advanced** | | | |
| 6.1 | VPN Interface Configuration | ⏳ | |
| 6.2 | Emergency Access Protocols | ⏳ | |
| 6.3 | Configuration Backup/Restore | ⏳ | |

**Legend:** ✅ Pass | ❌ Fail | ⏳ Pending | ⚠️ Issues Found

---

## 🚨 **CRITICAL FAILURE RESPONSES**

### **If Phase 1 Tests Fail:**
```bash
# Network interface issues:
uci commit network
/etc/init.d/network restart
ip addr show

# VLAN issues:
bridge vlan del dev br-lan vid 1 self
bridge vlan add dev br-lan vid 1 pvid untagged self
```

### **If Phase 2 Tests Fail:**
```bash
# DHCP issues:
/etc/init.d/dnsmasq restart
cat /var/log/messages | grep dnsmasq

# IP conflicts:
cat /tmp/dhcp.leases
uci show dhcp | grep -E "(start|limit|ip)"
```

###
