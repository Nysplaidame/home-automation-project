---
title: Network Architecture Decision - Printer VLAN, Bambuddy VM Separation, VLAN 30 Rename
description: Adds VLAN 35 for printer isolation, moves Bambuddy to a dedicated VM on VLAN 20, and renames VLAN 30 from CCTV to NVR
tags: [architecture-decision, network-security, vlan, printers, bambuddy]
created: 2026-04-10
modified: 2026-04-10
type: decision
status: accepted
---

# Decision: Printer VLAN, Bambuddy VM Separation, and VLAN 30 Rename

**Date:** 2026-04-10
**Status:** Accepted
**Context:** Adding a second printer (Concepts3D Athena 2) to the system, reviewing
placement of the Bambu P1S, and resolving a semantic mismatch between VLAN 30's
"CCTV" label and its actual contents after Bambuddy was added to VM 101.

---

## Problems addressed

### 1 — P1S had no internet restriction
The P1S was planned on VLAN 1 (LAN) with a blanket `LAN to Internet → ACCEPT` rule.
This gives Bambu Lab unrestricted outbound access to their cloud infrastructure, which
conflicts with the goal of running the printer in LAN/Developer mode and retaining
control over its network behaviour if future firmware changes restrict functionality.

### 2 — No appropriate VLAN for printers
VLAN 50 (IoT Sensors) was considered but rejected: the P1S and Athena 2 are complex
multi-service devices, not simple ESPHome sensor boards. Mixing them into the
safety-critical sensor VLAN would dilute a tightly scoped isolation boundary. A
dedicated printer VLAN gives the right posture without compromising VLAN 50.

### 3 — Bambuddy collocated with Frigate on VM 101
Bambuddy was added to VM 101 as a convenience (Docker sidecar on the same host).
This colocation means Bambuddy shares Frigate's VLAN 30 network identity, despite
having no functional relationship to CCTV. Separating it produces cleaner
responsibility boundaries and allows VM 101 to return to a single-purpose NVR role.

### 4 — VLAN 30 label no longer accurate
"CCTV" stopped being an accurate description once Bambuddy was added. With Bambuddy
removed, the zone contains Frigate NVR and IP cameras only. Renaming it "NVR" is
accurate and prevents future confusion when reading firewall rules.

---

## Decisions

### Decision A — Add VLAN 35 "Printers" (192.168.35.0/24)

**Chosen option:** Dedicated VLAN between Storage (40) and CCTV/NVR (30).

**Rationale:**
- Clean separation from VLAN 50 (safety sensors) and VLAN 1 (users)
- No internet by default; single OTA exception (port 443 TCP → WAN) covers both
  printers — P1S uses HTTPS for firmware, Athena 2 (NanoDLP on Linux) uses HTTPS
  for OS/firmware updates
- Wired-only: both P1S and Athena 2 have Gigabit Ethernet; no WiFi SSID required,
  keeping the wireless config unchanged
- Lan4 currently carries VLAN 40 untagged (NAS). VLAN 35 is VM-accessible only via
  the Proxmox trunk on lan1 — no new physical port assignment is needed
- LAN → printers firewall rule allows Bambu Studio (laptop on VLAN 1) to reach the
  P1S on ports 8883 and 21. Manual IP entry in Bambu Studio required (mDNS does not
  cross VLANs — acceptable, one-off configuration)
- NanoDLP (Athena 2) exposes a web UI and REST API on HTTP port 80 (Raspberry Pi
  default, configurable). LAN → printers rule also allows port 80 and 8080 for
  browser/slicer access from user laptops
- Odyssey (Open Resin Alliance) exposes a REST API on port 12357 by default.
  Dragonfruit slicer integration requirements are not yet confirmed — a placeholder
  comment is left in the firewall config pending confirmation from ORA Discord.
  Add port 12357 to the LAN → printers rule when confirmed.
- Future printers join VLAN 35 without requiring firewall or VLAN changes beyond a
  DHCP reservation

**P1S moves from:** 192.168.1.200 (VLAN 1) → 192.168.35.200 (VLAN 35)
**Athena 2 planned at:** 192.168.35.201 (VLAN 35)

### Decision B — Move Bambuddy to dedicated VM 103 on VLAN 20

**Chosen option:** New VM 103 "bambuddy" on VLAN 20 (Automation), 192.168.20.102.

**Rationale:**
- Bambuddy is an automation integration service, not a CCTV/NVR component. It
  subscribes to printer state and publishes to Mosquitto — the same data-inward,
  event-upward pattern as ESPHome devices. VLAN 20 (Automation) is the correct
  semantic home.
- Placing Bambuddy on VLAN 20 rather than VLAN 35 (Printers) enforces a one-way
  trust boundary: Bambuddy initiates connections *to* the printer VLAN; the printer
  cannot initiate connections back to Bambuddy. If P1S firmware were ever compromised
  it cannot reach Bambuddy or HA via unsolicited inbound connections.
- VM 101 returns to single-purpose NVR use. docker-compose.yml loses the Bambuddy
  service block entirely.
- Hardware headroom is sufficient: MINIX has 16GB RAM. VM 103 requires only 1GB RAM
  and 1 core. Current VM allocation (HA 4GB + Frigate 4GB + Monitoring 2GB) = 10GB,
  leaving 6GB. VM 103 uses 1GB, leaving 5GB headroom.

**VM 103 spec:**
| Field | Value |
|---|---|
| VM ID | 103 |
| Name | bambuddy |
| VLAN tag | 20 |
| IP | 192.168.20.102 |
| RAM | 1024 MiB |
| Cores | 1 |
| Disk | 16 GiB |
| OS | Debian 12 minimal + Docker |
| Startup order | 3 (after HA VM 100) |

### Decision C — Rename VLAN 30 from "CCTV" to "NVR"

**Chosen option:** Rename zone label and all references. No IP, subnet, or firewall
logic changes — purely a naming correction.

**Rationale:** With Bambuddy removed, VLAN 30 contains only Frigate NVR (VM 101) and
IP cameras. "NVR" accurately describes the zone. "CCTV" implied the zone was only for
cameras, which caused confusion about why a print management service was also there.

---

## Firewall rules summary

### Removed rules (no longer valid after Bambuddy leaves VLAN 30)
| Rule name | Was |
|---|---|
| `Bambuddy to P1S` | cctv → lan, 192.168.30.20 → 192.168.1.200, ports 8883/21 |
| `Bambuddy MQTT to HA` | cctv → automation, 192.168.30.20 → 192.168.20.101, port 8883 |
| `Bambuddy to HA API` | cctv → automation, 192.168.30.20 → 192.168.20.101, port 8123 |

### Added rules
| Rule name | Src → Dest | Ports | Purpose |
|---|---|---|---|
| `Printers OTA Internet` | printers → wan | 443/tcp | Firmware updates (both printers) |
| `Block Printers Internet` | printers → wan | — | REJECT + log; catch-all |
| `Bambuddy to Printer MQTT` | automation (20.102) → printers (35.200) | 8883/tcp | P1S local MQTT |
| `Bambuddy to Printer FTPS` | automation (20.102) → printers (35.200) | 21/tcp | P1S file transfer |
| `Bambuddy MQTT to HA` | automation (20.102) → automation (20.101) | 8883/tcp | Publish print events |
| `Bambuddy to HA API` | automation (20.102) → automation (20.101) | 8123/tcp | Smart plug control |
| `LAN to Bambuddy UI` | lan → automation (20.102) | 8000/tcp | Browser access |
| `LAN to Printers` | lan → printers | 8883,21,80,8080/tcp | Bambu Studio + NanoDLP browser |
| `Management to Printers` | management → printers | all | Admin access |

Note: Bambuddy→HA rules (MQTT and API) are intra-zone (both on VLAN 20). OpenWrt
firewall zones apply to inter-zone traffic by default; intra-zone traffic on VLAN 20
is governed by the automation zone's `input/output` policy. The automation zone has
`output=REJECT` to prevent devices from arbitrarily initiating outbound connections.
Explicit intra-zone rules are added to permit Bambuddy (20.102) → HA (20.101) on the
required ports, consistent with the existing scoped approach used elsewhere.

---

## Athena 2 — NanoDLP protocol notes

The Athena 2 runs a custom NanoDLP Linux OS on a Raspberry Pi CM5 mainboard.
NanoDLP exposes a web UI and REST API over HTTP (port 80 on RPi-based systems,
configurable). No cloud dependency for local operation — fully LAN-accessible.

The Open Resin Alliance Odyssey engine (REST API, port 12357 by default) may be
required for Dragonfruit slicer integration. Dragonfruit is in active development
as of April 2026. Confirm required ports via ORA Discord before adding to the
`LAN to Printers` firewall rule. A placeholder comment marks this in
`firewall-config.conf`.

OTA firmware updates use HTTPS (port 443) — same allow rule as the P1S.

---

## Files changed

| File | Change |
|---|---|
| `configs/openwrt/vlan-config.conf` | Add VLAN 35 bridge-vlan + logical interface; rename VLAN 30 comments |
| `configs/openwrt/firewall-config.conf` | Rename cctv zone to nvr; remove 3 Bambuddy rules; add all new rules |
| `configs/openwrt/dhcp-config.conf` | Add VLAN 35 DHCP scope; move P1S to 192.168.35.200; add VM 103 reservation |
| `configs/frigate/docker-compose.yml` | Remove Bambuddy service, volumes, and .env entries |
| `docs/decisions/01-network-architecture.md` | Add VLAN 35 row; rename VLAN 30 entry |
| `scripts/setup/proxmox/bambuddy_vm_setup_guide.md` | New — VM 103 creation and Bambuddy deployment |
| `README.md` | Update VLAN table, system components, hardware, key file locations |
| `PROJECT-INDEX.md` | Update VLAN table reference |
| `TO-DO.md` | Add Phase 2.5 Bambuddy VM and Phase 5 Printer VLAN tasks |
| `docs/secrets_reference.md` | Update P1S IP; add Bambuddy VM section |
| `docs/troubleshooting/troubleshooting_reference.md` | Update Bambuddy firewall troubleshooting IPs |

---

## Implementation sequence

Deploy these changes in this order to avoid a broken intermediate state:

1. Apply updated `vlan-config.conf` (adds VLAN 35 interface)
2. Apply updated `firewall-config.conf` (new rules reference the new zone)
3. Apply updated `dhcp-config.conf` (VLAN 35 scope + reservations)
4. Move P1S to wired Ethernet on the Proxmox trunk (or a switch on VLAN 35)
5. Confirm P1S gets 192.168.35.200 and Bambu Studio reaches it from VLAN 1
6. Create VM 103 per `bambuddy_vm_setup_guide.md`
7. Remove Bambuddy from VM 101 (`docker compose down bambuddy && docker compose up -d`)
8. Confirm HA P1S entities remain available after Bambuddy moves to new IP

---

## Related documents

- [[docs/decisions/01-network-architecture|01 - Network Architecture]] — original 9-VLAN design
- [[scripts/setup/proxmox/bambuddy_vm_setup_guide|Bambuddy VM Setup Guide]] — VM 103 deployment
- [[configs/openwrt/firewall-config.conf|Firewall Config]] — full rule set
- [[docs/troubleshooting/troubleshooting_reference|Troubleshooting Reference]] — updated Bambuddy section
