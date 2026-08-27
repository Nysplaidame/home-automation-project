# Network Post-Deployment Testing Guide
# Run these tests after router VLAN cutover to verify isolation and routing
# Prerequisite: management laptop plugged into lan2 (VLAN 10 untagged)

Current production status, reconciled on 2026-08-25, uses the managed switch:
- lan5 LAN/recovery: DHCP `192.168.1.x`, gateway/DNS `192.168.1.1`
- lan2 management: DHCP `192.168.10.x`, gateway/DNS `192.168.10.1`
- lan3 managed-switch trunk: tagged VLANs `1,10,30,40`
- lan4 storage recovery/access port: VLAN 40 untagged and normally unplugged
- GS1900 port 8: OMV NAS at `192.168.40.50` on VLAN 40
- GS1900 ports 2/3/4: Camera 1 `.21`, Patio `.23`, and Gate `.22` on VLAN 30
- lan1 is tagged-only trunk to Proxmox; direct untagged laptop DHCP is not expected
- first-flight WiFi interfaces are configured but disabled

---

## Test environment setup

You need a laptop on VLAN 10 (lan2) as your base. All tests run from there unless noted.

```bash
# Confirm you are on VLAN 10
ip addr     # should show 192.168.10.x
ping 192.168.10.1   # router management gateway
```

---

## Section 1 — VLAN interface validation (on router)

SSH into the router: `ssh root@192.168.10.1`

```bash
# Verify all VLAN interfaces are up with correct IPs
for vlan in 1 10 20 30 35 40 50 60 70 99; do
    ip=$(ip addr show br-lan.$vlan 2>/dev/null | awk '/inet /{print $2}')
    if [ -n "$ip" ]; then
        echo "✓ VLAN $vlan: $ip"
    else
        echo "✗ VLAN $vlan: interface missing"
    fi
done

# Expected output:
# ✓ VLAN 1:  192.168.1.1/24
# ✓ VLAN 10: 192.168.10.1/24
# ✓ VLAN 20: 192.168.20.1/24
# ✓ VLAN 30: 192.168.30.1/24
# ✓ VLAN 35: 192.168.35.1/24
# ✓ VLAN 40: 192.168.40.1/24
# ✓ VLAN 50: 192.168.50.1/24
# ✓ VLAN 60: 192.168.60.1/24
# ✓ VLAN 70: 192.168.70.1/24
# ✓ VLAN 99: 192.168.99.1/24
```

---

## Section 2 — Physical port VLAN tagging (on router)

```bash
# Verify bridge VLAN table from UCI.
# The GL-MT6000 image used during first-flight did not include the `bridge` tool.
uci show network | grep -E "network\.@bridge-vlan\[[0-9]+\]\.(vlan|ports)"

# Expected:
# VLAN 1:  lan3:t lan5:u*
# VLAN 10: lan1:t lan2:u* lan3:t
# VLAN 20: lan1:t
# VLAN 30: lan1:t lan3:t
# VLAN 35: lan1:t
# VLAN 40: lan1:t lan3:t lan4:u*
# VLAN 50: lan1:t
# VLAN 60: lan1:t
# VLAN 70: lan1:t
# VLAN 99: configured without a physical port in first-flight

# Verify VLAN 1 has lan3 tagged and lan5 untagged.
uci show network.@bridge-vlan[0].ports
```

Physical client smoke tests:

| Port | Expected client result |
|---|---|
| lan5 | Direct LAN/recovery DHCP `192.168.1.x`, DNS `192.168.1.1`, LuCI/browser reachable at `192.168.1.1` |
| lan2 | DHCP `192.168.10.x`, DNS `192.168.10.1`, Proxmox/admin clients live here |
| lan3 | Tagged trunk only; test with the managed switch, not plain laptop DHCP |
| lan4 | Unplugged storage recovery/access port on VLAN 40; a temporary test client may use `192.168.40.x` |
| lan1 | Tagged trunk only; test with Proxmox or VLAN-aware client, not plain DHCP |

Managed switch access-port smoke tests after the switch is installed:

| Switch port role | Expected client result |
|---|---|
| Switch management interface | `192.168.10.12` on VLAN 10, reachable from management only |
| Camera access ports 2/3/4 | Camera 1 `.21`, Patio `.23`, Gate `.22`; no broad WAN access |
| Future camera ports 5-7 | VLAN 30 access, disabled/PoE-off until a labelled camera is commissioned; `.24` reserved next |
| OMV NAS port 8 | OMV reachable at `192.168.40.50`, DNS `192.168.40.1`; no broad WAN access |
| TL-WA801N access port | No current free switch port; requires an explicit capacity/design decision |

For restricted zones, DNS is the better client smoke test than gateway ping:

```powershell
nslookup homeassistant.home.local 192.168.30.1
nslookup nas.home.local 192.168.40.1
```

---

## Section 3 — Internet access controls

Test from the router by source-interface pinging:

```bash
# These SHOULD reach the internet:
ping -I br-lan.1  -c 3 1.1.1.1  && echo "✓ VLAN 1 internet" || echo "✗ VLAN 1 internet FAILED"
ping -I br-lan.10 -c 3 1.1.1.1  && echo "✓ VLAN 10 internet" || echo "✗ VLAN 10 internet FAILED"

# These MUST NOT reach the internet:
ping -I br-lan.30 -c 3 1.1.1.1 2>/dev/null && echo "✗ VLAN 30 internet LEAKED" || echo "✓ VLAN 30 (NVR) blocked"
ping -I br-lan.35 -c 3 1.1.1.1 2>/dev/null && echo "✗ VLAN 35 internet LEAKED" || echo "✓ VLAN 35 (Printers) blocked"
ping -I br-lan.40 -c 3 1.1.1.1 2>/dev/null && echo "✗ VLAN 40 internet LEAKED" || echo "✓ VLAN 40 blocked"
ping -I br-lan.50 -c 3 1.1.1.1 2>/dev/null && echo "✗ VLAN 50 internet LEAKED" || echo "✓ VLAN 50 blocked"

# Note: VLAN 35 (Printers) allows port 443 TCP outbound for OTA updates only.
# The above ICMP test will correctly show blocked regardless — ICMP is not permitted.
```

---

## Section 4 — Inter-VLAN isolation

Test that VLANs that should be isolated cannot reach each other.
Run these from the router shell:

```bash
# Guest (99) MUST NOT reach internal VLANs
for dest in 192.168.1.1 192.168.10.1 192.168.20.1 192.168.30.1 192.168.50.1; do
    ping -I br-lan.99 -c 2 -W 2 $dest >/dev/null 2>&1 \
        && echo "✗ VLAN 99 → $dest REACHABLE (isolation failure)" \
        || echo "✓ VLAN 99 → $dest blocked"
done

# NVR (30) MUST NOT reach automation (20) directly
ping -I br-lan.30 -c 2 -W 2 192.168.20.1 >/dev/null 2>&1 \
    && echo "✗ VLAN 30 → VLAN 20 REACHABLE" \
    || echo "✓ VLAN 30 (NVR) → VLAN 20 blocked"

# Printers (35) MUST NOT reach automation (20) or LAN (1) directly
ping -I br-lan.35 -c 2 -W 2 192.168.20.1 >/dev/null 2>&1 \
    && echo "✗ VLAN 35 → VLAN 20 REACHABLE" \
    || echo "✓ VLAN 35 (Printers) → VLAN 20 blocked"

# IoT (50) MUST NOT reach management (10)
ping -I br-lan.50 -c 2 -W 2 192.168.10.1 >/dev/null 2>&1 \
    && echo "✗ VLAN 50 → VLAN 10 REACHABLE" \
    || echo "✓ VLAN 50 → VLAN 10 blocked"
```

---

## Section 5 — Management VLAN full access

Management (VLAN 10) should reach everything:

```bash
for dest in 192.168.1.1 192.168.20.1 192.168.30.1 192.168.35.1 192.168.40.1 192.168.50.1 192.168.60.1 192.168.70.1; do
    ping -I br-lan.10 -c 2 -W 2 $dest >/dev/null 2>&1 \
        && echo "✓ Management → $dest" \
        || echo "✗ Management → $dest BLOCKED"
done
```

---

## Section 6 — Critical inter-VLAN services (HA bridge rules)

Test from the management laptop (192.168.10.x), NOT the router:

```bash
# HA -> Frigate (VLAN 20 -> VLAN 30, port 8971)
# Run this from the HA VM terminal once HA and Frigate are up:
nc -zv 192.168.30.20 8971 && echo "V HA -> Frigate API" || echo "? HA -> Frigate blocked"

# IoT → HA MQTT (VLAN 50 → VLAN 20)
# From any device on VLAN 50:
nc -zv 192.168.20.101 8883 && echo "✓ IoT → MQTT 8883 (TLS)" || echo "✗ IoT → MQTT 8883 blocked"

# Plain MQTT should be closed unless a temporary recovery/bootstrap exception is
# deliberately installed and documented.
nc -zv 192.168.20.101 1883 && echo "✗ IoT → MQTT 1883 open; confirm this is a documented temporary exception" || echo "✓ MQTT 1883 closed"

# HA → IoT ESPHome API (VLAN 20 → VLAN 50, port 6053)
# From HA Terminal:
nc -zv 192.168.50.21 6053 && echo "✓ HA → ESPHome fan ctrl" || echo "✗ HA → ESPHome blocked"
nc -zv 192.168.50.56 6053 && echo "✓ HA → ESPHome valve ctrl" || echo "✗ HA → ESPHome blocked"

# Frigate → NAS (VLAN 30 → VLAN 40, NFS port 2049)
# From frigate-nvr:
nc -zv 192.168.40.50 2049 && echo "✓ Frigate → NAS NFS" || echo "✗ Frigate → NAS blocked"
```

---

## Section 7 — DHCP verification

Connect a test device to each physical port and verify it gets the right IP range:

| Port | Expected VLAN | Expected IP range |
|---|---|---|
| lan2 | 10 (Management) | 192.168.10.100–149 |
| lan3 | tagged trunk only | no untagged DHCP expected |
| lan4 | 40 (Storage) | Unplugged recovery/access port; OMV is on GS1900 port 8 |
| lan5 | 1 (LAN/recovery) | 192.168.1.100–199 |

Managed switch access ports:

| Switch role | Expected VLAN | Expected IP range |
|---|---|---|
| Camera ports | 30 (NVR) | cameras 192.168.30.21–24, DHCP bench clients 192.168.30.100–149 |
| NAS port | 40 (Storage) | OMV 192.168.40.50, DHCP bench clients 192.168.40.100–139 |
| Extender port | 1 (LAN) | TL-WA801N 192.168.1.203, clients 192.168.1.100–199 |

WiFi tests:

| SSID | Expected IP range |
|---|---|
| HomeMain | 192.168.1.100–199 |
| HomePrinters | 192.168.35.100–149 |
| HomeIoT | 192.168.50.100–190 |
| HomeAdmin | 192.168.10.100–149 |
| HomeGuest | 192.168.99.100–150 |

```bash
# On router: check current DHCP leases
cat /tmp/dhcp.leases
# Format: expiry  mac  ip  hostname  id
```

---

## Section 8 — DNS resolution

```bash
# From router or any client:
nslookup homeassistant.home.local 192.168.10.1
# Expected: 192.168.20.101

nslookup frigate.home.local 192.168.10.1
# Expected: 192.168.30.20

nslookup nas.home.local 192.168.10.1
# Expected: 192.168.40.50

nslookup proxmox.home.local 192.168.10.1
# Expected: 192.168.10.10

# External DNS should work from unrestricted VLANs:
nslookup google.com 1.1.1.1
```

---

## Section 9 — WiFi SSID verification

In first-flight, all client WiFi interfaces are intentionally disabled because
secrets/placeholders are not ready for a full profile. Use this section only
after compiling and deploying the `full` profile.

```bash
# From router shell:
iwlist scan 2>/dev/null | grep ESSID

# Full-profile expected visible SSIDs:
# HomeMain, HomeAdmin, HomePrinters, HomeIoT, HomeGuest
# Hidden configured SSID: HomeAdmin-2G
# NOT broadcasting: HomeDMZ (disabled by default)

# All 2.4GHz SSIDs (HomeMain, HomeAdmin-2G, HomePrinters, HomeIoT, HomeGuest) share
# radio0 and will be on channel 6. Per-interface channel overrides are
# not supported in OpenWrt mac80211 — see wireless-config.conf for rationale.
# HomeMain, HomeAdmin, and HomePrinters 5GHz are on radio1 (auto channel).
iw dev | grep -E "(Interface|channel)"
```

---

## Section 10 — Firewall rule hit counters

After running the tests above, check that rules fired as expected:

```bash
# On router:
nft list ruleset | grep -E "counter packets [1-9]"
# Rules with non-zero packet counts were exercised during testing

# Check reject/drop rules and inspect whether any unexpected block counters moved:
nft list ruleset | grep -Ei "reject|drop"
```

---

## Pass/fail criteria

All of these must be true before declaring the network ready:

- [ ] All 10 VLAN interfaces up with correct IPs
- [ ] VLAN 1 has `lan3:t` and `lan5:u*` in `uci show network.@bridge-vlan[0].ports`
- [ ] lan3 is tagged-only for VLANs 1,10,30,40
- [ ] lan2 has the VLAN 10 PVID, lan4 has the VLAN 40 PVID, and lan5 has the VLAN 1 PVID
- [ ] Managed switch access ports have correct PVIDs: cameras=30, NAS=40, extender=1, switch management=10
- [ ] VLAN 1, 10, 99 can reach internet; 30, 35, 40, 50 cannot (ICMP blocked)
- [ ] VLAN 35 (Printers) OTA: port 443 TCP reachable, all other internet blocked
- [ ] Guest (99) cannot reach any internal VLAN
- [ ] NVR (30) cannot reach automation (20) directly
- [ ] Printers (35) cannot reach automation (20) or LAN (1) directly
- [ ] IoT (50) cannot reach management (10)
- [ ] Management (10) can reach all VLANs
- [ ] MQTT port 8883 reachable from VLAN 50 → VLAN 20
- [ ] Plain MQTT port 1883 closed unless there is a documented temporary exception
- [ ] ESPHome port 6053 reachable from VLAN 20 → VLAN 50
- [ ] Frigate API reachable from VLAN 20 → VLAN 30 (port 8971)
- [ ] NAS NFS reachable from VLAN 30 and VLAN 20
- [ ] Bambuddy (20.102) → P1S (35.200) reachable on ports 8883 and 21
- [ ] DHCP assigning correct ranges per VLAN
- [ ] Local DNS resolving homeassistant.home.local, docker-host.home.local, bambuddy.home.local, frigate.home.local, nas.home.local, p1s.home.local
