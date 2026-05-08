---
title: Eighth Audit - Router Configuration Deep Dive
description: Comprehensive audit of router configuration files and setup guides for consistency with v3.0 architecture
tags: [audit, router, openwrt, vlan, consistency-check]
created: 2026-04-20
modified: 2026-04-20
type: audit
status: resolved
audit-number: 8
scope: router-configuration
---

# Eighth Audit — Router Configuration Deep Dive

**Audit date:** 2026-04-20
**Scope:** All files in `scripts/setup/router/` and `configs/openwrt/`
**Trigger:** User request for deep-dive consistency check
**Architectural context:** v3.0 (10-VLAN architecture per `02-printer-vlan-architecture.md`, dated 2026-04-10)

---

## Summary

The authoritative OpenWrt config files (`vlan-config.conf`, `firewall-config.conf`,
`dhcp-config.conf`, `wireless-config.conf`) have all been correctly updated to v3.0
with the 10-VLAN architecture: VLAN 30 renamed cctv → nvr, new VLAN 35 for printers,
Bambuddy moved to dedicated VM 103 on VLAN 20, P1S moved to 192.168.35.200.

**However, none of the phase guides have been updated to match.** All eight phase
guides (`phase_1_prerequisites.md` through `phase_8_ventsys_readiness.md`) and the
supporting `network_testing_guide.md` still document the old 9-VLAN architecture
with the `cctv` interface name and no reference to VLAN 35 or the printers zone.

This creates a serious risk: following the phase guides as written produces a router
configuration that is incompatible with the v3.0 canonical configs. The phase guides
reference an interface (`cctv`) that the firewall config no longer uses, omit an
entire VLAN (35) that the DHCP config expects, and reference rule names that do not
exist in the current `firewall-config.conf`.

## Role of the canonical `.conf` files

The four files in `configs/openwrt/` are the source of truth for router state.
Three of them (`vlan-config.conf`, `dhcp-config.conf`, `wireless-config.conf`) are
UCI-format specifications mirroring `/etc/config/network`, `/etc/config/dhcp`, and
`/etc/config/wireless` respectively — they describe the target state but are not
loaded directly; the phase guides translate them into `uci set` commands applied
over SSH. The fourth (`firewall-config.conf`) is an executable bash script that is
copied to the router and run directly (per `phase_4_firewall_implementation.md`
section 4.2).

Their roles in the project lifecycle:

1. **Single source of truth** — when phase guides drift, the `.conf` files remain
   canonical. Any mismatch means the phase guide is wrong, not the conf file.
2. **Audit and review target** — reading a single `firewall-config.conf` shows
   every rule without scrolling through 8 phase guides. Same pattern for DHCP,
   VLANs, wireless.
3. **Fast rebuild / migration** — for re-imaging the router or moving to new
   hardware, these files let you reconstruct the config without re-reading setup
   docs. `firewall-config.conf` runs end-to-end as-is; the other three are used
   as copy-paste reference for `uci` batch commands or as input to a future
   deployment script.

---

## Findings

### Severity summary

| Severity | Count | Description |
|---|---|---|
| **HIGH** | 5 | Phase guides inconsistent with v3.0 architecture — will produce broken config |
| **MEDIUM** | 3 | Documentation drift, stale references, missing validation |
| **LOW** | 1 | Cosmetic/cleanup issue |

### HIGH severity

#### R8-H1 — phase_2 documents 9-VLAN architecture, missing VLAN 35

**File:** `scripts/setup/router/phase_2_network_infrastructure_complete.md`

**Problem:** The Overview states "9 isolated network segments" and the VLAN Design
Architecture section lists VLANs 1, 10, 20, 30, 40, 50, 60, 70, 99 — missing VLAN 35.
The Output Deliverables says "8 VLAN interfaces operational (VLANs 1,10,20,30,40,50,60,70,99)"
which is doubly wrong (9 listed, claims 8, missing 35 and 99 count).

The script section 2.3 "VLAN Bridge Configuration" has no VLAN 35 block. Section 2.4
"Logical Network Interface Creation" has no `network.printers` interface. The trunk
description on lan1 says "tagged VLANs 10,20,30,40,50,60,70" missing VLAN 35.

**Impact:** Running the Phase 2 script produces a router with no VLAN 35 interface.
DHCP won't start on VLAN 35 in Phase 3 (no interface to attach to). Firewall rules
referencing the `printers` zone won't deploy in Phase 4. The P1S at 192.168.35.200
has no network to join. Complete failure of printer VLAN integration.

**Fix required:** Add VLAN 35 bridge-vlan block, logical interface block, update
trunk documentation, update Overview/Output Deliverables counts to 10 VLANs.

**Reference fix:** `configs/openwrt/vlan-config.conf` has the correct v3.0 blocks —
copy the VLAN 35 bridge-vlan and the `config interface 'printers'` block verbatim.

---

#### R8-H2 — phase_3 uses obsolete `cctv` interface name, no VLAN 35 DHCP scope

**File:** `scripts/setup/router/phase_3_dhcp_configuration.md`

**Problem:** Section 3.6 creates DHCP scope with `uci set dhcp.@dhcp[-1].interface='cctv'`.
The v3.0 canonical config uses `interface='nvr'` (rename per 02-printer-vlan-architecture.md).

No section exists for VLAN 35 DHCP scope. No static reservations for Bambu P1S at
192.168.35.200 or Athena 2 at 192.168.35.201. No reservation for VM 103 (Bambuddy)
at 192.168.20.102. P1S reservation in section 3.12 still shows `192.168.1.200`
(old VLAN 1 placement).

Local domain config section 3.13 has `frigate.home.local → 192.168.30.20` and
`bambuddy.home.local → 192.168.30.20` (both pointing at the Frigate VM IP, and
Bambuddy at the wrong IP). Missing `printers.home.local`, `nvr.home.local`,
`athena2.home.local`. P1S domain points at `192.168.1.200` (old IP).

**Impact:** Phase 3 creates a DHCP configuration that doesn't match the authoritative
`dhcp-config.conf`. Printers won't get static IPs. Interface name mismatch (`cctv`
vs `nvr`) means Phase 4 firewall rules will fail because they reference a zone that
was created against an interface that doesn't exist.

**Fix required:** Section 3.6 rename `cctv` → `nvr`. Add new section for VLAN 35
(printers) DHCP scope. Add static reservations for P1S (35.200), Athena 2 (35.201),
Bambuddy VM (20.102). Update P1S reservation from 192.168.1.200 → 192.168.35.200.
Update local domain entries.

---

#### R8-H3 — phase_4 firewall validation uses obsolete zone names and rule names

**File:** `scripts/setup/router/phase_4_firewall_implementation.md`

**Problem:** Multiple issues in validation sections:

Section 4.1 prerequisite check:
```bash
for interface in lan management automation cctv storage iot_sensors monitoring dmz guest; do
```
This list uses `cctv` (obsolete) and does not include `printers` (VLAN 35).

Section 4.4 expected_zones:
```bash
expected_zones="wan lan management automation cctv storage iot_sensors monitoring dmz guest vpn_clients"
```
Should be `nvr printers` instead of `cctv` and add `printers`. Also checks
`zone.*name='automation'` for network='automation' mapping but doesn't verify the
v3.0 nvr/printers zone mappings exist.

Section 4.5 VentSys validation references these rule names:
- `"HA to IoT Sensors Access"` — does NOT exist in v3.0 firewall-config.conf.
  The actual rule in v3.0 is `"ESPHome API HA to IoT"` (with dest_port `6053,3232`).
  No rule named "HA to IoT Sensors Access" exists at all.
- `"Bambuddy to P1S"` — does NOT exist in v3.0. The v3.0 rules are
  `"Bambuddy to Printer MQTT"` and `"Bambuddy to Printer FTPS"` (different names,
  also now crossing automation→printers zones, not cctv→lan).
- `"Block CCTV to Automation"` — renamed to `"Block NVR to Automation"` in v3.0.

Section 4.6 DMZ isolation check:
```bash
for zone in lan automation cctv storage iot_sensors; do
```
Uses obsolete `cctv` and omits `printers`. The "expected 5 rules" comparison is
hardcoded to 5 — v3.0 firewall-config.conf has 5 DMZ block rules (lan, automation,
nvr, storage, iot_sensors) so the count is coincidentally still correct, but
`Block DMZ to cctv` won't match `Block DMZ to NVR` and the check will fail.

**Impact:** Running Phase 4's validation steps will report numerous spurious
failures on a correctly-configured v3.0 router, and may mask real missing rules
because the test is looking for rules by the wrong names.

**Fix required:** Global find-and-replace `cctv` → `nvr` in validation scripts.
Add `printers` to all zone lists. Update rule name checks:
- `"HA to IoT Sensors Access"` → `"ESPHome API HA to IoT"`
- `"Bambuddy to P1S"` → `"Bambuddy to Printer MQTT"` + `"Bambuddy to Printer FTPS"`
  (with note that they now cross automation→printers zones)
- `"Block CCTV to Automation"` → `"Block NVR to Automation"`

Add validation for new rules: `"Printers OTA Internet"`, `"LAN to Printers"`,
`"Bambuddy MQTT to HA"` (now intra-automation), `"Bambuddy to HA API"`.

---

#### R8-H4 — phase_5 wireless validation missing HomePrinters SSID

**File:** `scripts/setup/router/phase_5_wireless_configuration.md`

**Problem:** Section 5.10 expected_ssids:
```bash
expected_ssids=("HomeMain" "HomeAdmin" "HomeAdmin-2G" "HomeIoT" "HomeGuest")
```
Missing `HomePrinters` (5GHz, VLAN 35, added in wireless-config.conf v2.1).

Section 5.11 mappings:
```bash
mappings=(
    "HomeMain:lan"
    "HomeAdmin:management"
    "HomeIoT:iot_sensors"
    "HomeGuest:guest"
    "HomeDMZ:dmz"
)
```
Missing `"HomePrinters:printers"` mapping. No config step in the phase to actually
create the HomePrinters SSID either — only HomeMain, HomeAdmin, HomeIoT, HomeGuest,
HomeDMZ are configured.

**Impact:** Following Phase 5 produces a router with no HomePrinters SSID. The P1S
(WiFi-only device) cannot connect to its designated VLAN. Athena 2 cannot use WiFi.
The printer VLAN infrastructure is entirely unreachable for wireless devices.

**Fix required:** Add new section 5.X creating HomePrinters SSID on radio1 matching
`configs/openwrt/wireless-config.conf` v2.1. Update validation arrays to include
HomePrinters.

---

#### R8-H5 — phase_7 connectivity matrix missing VLAN 35

**File:** `scripts/setup/router/phase_7_integration_testing.md`

**Problem:** Section 7.1 final validation loops:
```bash
for vlan in 1 10 20 30 40 50 60 70 99; do
```
Missing VLAN 35.

Section 7.2 networks array:
```bash
networks=("192.168.1.1" "192.168.10.1" "192.168.20.1" "192.168.30.1" "192.168.40.1" "192.168.50.1" "192.168.60.1" "192.168.70.1" "192.168.99.1")
```
Missing `"192.168.35.1"`.

Section 7.3 internet access matrix: `no_access_nets` array includes CCTV (by
obsolete name) but not Printers. Printers should have internet access blocked
except port 443 — but the test uses ICMP which is blocked entirely, so this would
test correctly if the array entry were added.

Section 7.6 firewall rule verification references old rule names:
- `Internet Blocks:Block CCTV Internet,Block Storage Internet,Block IoT Internet`
  — v3.0 has `Block NVR Internet` (not `Block CCTV Internet`)
- `VentSys Rules:HA to IoT Sensors Access,...` — doesn't exist (see R8-H3)
- `Isolation Rules:...Block VPN to management` — v3.0 uses `Block VPN to Management`
  (capitalised "Management") — case-sensitive `grep` may miss this.

**Impact:** Phase 7 integration testing will miss VLAN 35 entirely — never verifies
it's operational, never tests printers zone isolation. False-negative results on
v3.0 rule names make the final "PASS" determination unreliable.

**Fix required:** Add VLAN 35 to every test loop and every IP address array.
Add Printers-specific isolation tests. Update all rule name references.

---

### MEDIUM severity

#### R8-M4 — network_testing_guide.md references 9-VLAN architecture throughout

**File:** `scripts/setup/router/network_testing_guide.md`

**Problem:**
- Section 1 validation loop: `for vlan in 1 10 20 30 40 50 60 70 99` — missing 35.
- Section 1 expected output block: 9 entries, missing VLAN 35.
- Section 2 `bridge vlan show` expected output: missing VLAN 35 on lan1 trunk.
- Section 3 internet access tests: no VLAN 35 tests. Printers should block internet
  except port 443 — the test needs a positive test for port 443 and a negative test
  for general internet.
- Section 4 CCTV isolation test: uses "CCTV" label but checks VLAN 30 to VLAN 20 —
  the logic is still right since VLAN 30 is now NVR, but the comment is wrong.
- Section 7 DHCP table: missing VLAN 35 row, still calls VLAN 30 "CCTV".
- Section 9 SSID verification: missing `HomePrinters` in expected SSID list.
- Pass/fail criteria: no criterion for VLAN 35, uses "CCTV" terminology.

**Impact:** Following this testing guide after a v3.0 deployment would miss all
printer VLAN verification and label NVR as CCTV in reports.

**Fix required:** Full update to reflect 10-VLAN architecture. Add printers test
section covering OTA port 443 positive test and general internet negative test.

---

#### R8-M5 — phase_6 references obsolete zone names in VPN security validation

**File:** `scripts/setup/router/phase_6_vpn_setup.md`

**Problem:** Section 6.7 "VPN Security and Access Validation":
```bash
sensitive_blocks=("management" "cctv" "storage" "iot_sensors")
```
Uses obsolete `cctv` and omits `printers`. The v3.0 firewall-config.conf has
`Block VPN to Printers` as well.

Also: `[ $blocked_count -eq 4 ]` — the check is hardcoded to 4, but v3.0 has
5 VPN block rules (management, nvr, storage, iot, printers). Updating the list
requires also updating this magic number.

**Impact:** Phase 6 validation will miss the `Block VPN to Printers` rule check
and will incorrectly report success when the count is 4 (missing the printers
block would go undetected).

**Fix required:** Add `printers` to the array and update the magic number to 5.
Also verify `cctv` → `nvr` rename.

---

#### R8-M6 — phase_8 VentSys handover documentation uses outdated naming

**File:** `scripts/setup/router/phase_8_ventsys_readiness.md`

**Problem:** Section 8.2 VentSys network integration documentation. While most
core references are correct, some leakage:
- DHCP range for VLAN 20 shown as `192.168.20.110-149` — correct, but should note
  that .101 (HA) and .102 (Bambuddy) are static reservations outside this range.
- No mention of VLAN 35 printers in the VentSys-adjacent context (Bambuddy is now
  on VLAN 20 and bridges to printers on VLAN 35).

Section 8.6 final validation:
```bash
if ip addr show br-lan.20 | grep -q "192.168.20.1" && ip addr show br-lan.50 | grep -q "192.168.50.1"; then
    echo "✓ Critical VLANs operational (20: Automation, 50: IoT Sensors)" >> ...
```
Still reporting 9-VLAN mindset. Should also verify VLAN 35 since Bambuddy's
printer bridge depends on it being operational.

**Impact:** Lower than H1-H5 because this is documentation/validation rather than
configuration generation. Final readiness check won't catch a broken VLAN 35.

**Fix required:** Add VLAN 35 to the critical VLAN check. Add Bambuddy → Printers
flow to the critical firewall rules list.

---

### LOW severity

#### R8-L1 — phase_5 typo in section 5.12

**File:** `scripts/setup/router/phase_5_wireless_configuration.md`, section 5.12

**Problem:**
```bash
    else
        echo "✗ HomeIoT VLAN mapping incorrect" >> /tmp/phase5_vents
	fi
```
The redirect target is truncated mid-word (`/tmp/phase5_vents` should be
`/tmp/phase5_ventsys_test.txt`). Also the `fi` is preceded by a hard tab instead
of spaces, which is cosmetic but inconsistent with the rest of the file.

**Impact:** Running section 5.12 as-is will fail — the truncated filename will be
created as a new file (if the shell accepts it) rather than appending to the
existing test log. The validation output will be split between two files.

**Fix required:** Complete the filename. Fix indentation.

---

#### R8-L2 — Multiple files reference "9 VLANs" count in comments/labels

Throughout phase guides and some headers still describe "9 VLANs" or "9 network
segments". Easy to miss during updates. After R8-H1 through R8-H5 fixes, a final
sweep should catch all remaining "9 VLAN" mentions.

**Affected files:**
- `phase_2_network_infrastructure_complete.md` (Overview, several locations)
- `phase_3_dhcp_configuration.md` (Overview: "all 9 network segments")
- `phase_5_wireless_configuration.md` (minor)
- `phase_7_integration_testing.md` (summary sections)
- `phase_8_ventsys_readiness.md` (CONFIGURATION_SUMMARY template: "9 VLANs operational")

**Fix required:** Sweep for "9 VLAN", "9 network", "9 isolated" after main fixes.

---

## Verified-correct items (no action needed)

The following were checked and confirmed correct for v3.0 — no changes needed:

- **vlan-config.conf** — v3.0 dated 2026-04-10, all 10 VLANs present, VLAN 35
  configured, NVR rename applied, lan5 recovery/AP port documented.
- **firewall-config.conf** — v3.0 dated 2026-04-10, all zones correct (including
  `printers` and `nvr`), Bambuddy intra-automation rules present, printer zone
  rules present including OTA exception and LAN slicer access.
- **dhcp-config.conf** — v2.0 dated 2026-04-10, 10 VLAN scopes, VLAN 35 scope
  correct, P1S at 192.168.35.200, Athena 2 at 192.168.35.201, Bambuddy at
  192.168.20.102, homeextender at 192.168.1.203 (lan5 AP).
- **wireless-config.conf** — v2.1 dated 2026-04-10, HomePrinters SSID on radio1,
  all existing SSIDs unchanged, country code GB, channel 6 fixed for radio0.
- **tplink_wa801n_ap_setup.md** — correct and current; lan5 dual-purpose
  documented, AP config instructions accurate.
- **wireguard_vpn_guide.md** — R-5 and R-6 fixes applied correctly, client
  configs include DMZ in AllowedIPs, DNS corrected to 192.168.1.1, WAN IP lookup
  no longer uses external service.
- **phase_1_prerequisites.md** — lan5 documented in interface verification loop;
  package installation and key generation sections are architecture-independent
  and remain correct.

---

## Recommended remediation order

1. **R8-H1 first** (phase_2) — all other phase validation depends on VLAN 35
   existing. Without the interface, downstream DHCP/firewall/wireless changes are
   untestable.
2. **R8-H2 second** (phase_3) — DHCP must provision the new interface before
   firewall rules can be validated against live clients.
3. **R8-H3 third** (phase_4) — firewall changes complete the network segmentation.
4. **R8-H4 fourth** (phase_5) — wireless completes the printer VLAN access path.
5. **R8-H5 fifth** (phase_7) — integration tests now cover all of the above.
6. **R8-M4** (network_testing_guide.md) — align post-deployment testing to 10-VLAN.
7. **R8-M5/M6** (phase_6, phase_8 validation) — small test array updates.
8. **R8-L1/L2** — cleanup pass at the end.

---

## Related documents

- [[docs/decisions/02-printer-vlan-architecture|02 - Printer VLAN Architecture]]
  — The architectural decision driving all v3.0 changes
- [[docs/decisions/combined_audit_report|Sixth Audit — Combined Report]]
- [[docs/decisions/seventh_audit_full_check|Seventh Audit — Full Check]]
- [[configs/openwrt/vlan-config|vlan-config.conf v3.0]]
- [[configs/openwrt/firewall-config|firewall-config.conf v3.0]]
- [[configs/openwrt/dhcp-config|dhcp-config.conf v3.0]]
- [[configs/openwrt/wireless-config|wireless-config.conf v2.1]]
