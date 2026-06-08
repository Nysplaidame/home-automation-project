# Handoff - Router Automation Deployment (Hardened)

**Source session:** Claude on web (claude.ai), audit + planning + spec fixes complete  
**Target session:** Claude Desktop on Windows laptop, with Desktop Commander  
**Created:** 2026-04-30  
**Updated:** 2026-05-07 (first-flight deployed, physical ports validated, HAOS live)  
**Purpose:** Build `tools/router-deploy` from scratch, then run safe router deployment + validation.

> Current status: `tools/router-deploy` exists and first-flight has been applied
> to the GL-MT6000. Use this handoff as historical implementation context, not
> as an instruction to rebuild the toolkit from scratch.
>
> Current staging note: Proxmox is live on the `lan1` trunk at `192.168.10.10`;
> Home Assistant OS VM 100 is live on VLAN 20 at `192.168.20.101`; router
> validation is clean (`test-connectivity`: PASS=72/WARN=0/FAIL=0,
> `test.ps1`: PASS=60/WARN=0/FAIL=0). The optional WiFi uplink remains an
> explicit temporary staging path for internet downloads only.

---

## What is already done (do not redo)

The four canonical OpenWrt files in `main/configs/openwrt/` are source-of-truth design specs:

| File | Status |
|---|---|
| `vlan-config.conf` | v3.0, VLANs 1/10/20/30/35/40/50/60/70/99, lan5 recovery/AP documented |
| `firewall-config.conf` | v3.0, 12 zones, `nvr` rename complete, printer and Bambuddy rules included |
| `dhcp-config.conf` | v2.0, all 10 scopes, printer/Bambuddy/static reservations present |
| `wireless-config.conf` | v2.1, 6 SSIDs including HomePrinters |

Phase guides under `scripts/setup/router/` are reference docs only.  
The `wiki/` directory is stale and out of scope.

---

## Operating assumptions

- Path B: live troubleshooting with Claude Desktop.
- Wipe-and-rebuild model was used to create the toolkit; do not redo it unless
  the repo is lost.
- Soft rollback on failure is mandatory.
- lan5 is physical recovery path and must stay VLAN 1 untagged.
- Router-only scope (no Proxmox/HA/NAS orchestration in this toolkit).

---

## Stage 0 - prerequisite checks (must pass before coding or deployment)

```powershell
# 1) PowerShell available
powershell -NoProfile -Command "$PSVersionTable.PSVersion"

# 2) Python 3.10+
python --version

# 3) OpenSSH client
ssh -V

# 4) Vault path reachable
Test-Path "<repo-root>\main\configs\openwrt\vlan-config.conf"

# 5) Laptop has recovery-path lease (lan5 expected 192.168.1.x)
ipconfig | Select-String "IPv4"

# 6) SSH password login currently works
ssh root@192.168.1.1 "echo OK; exit"
```

If 5 fails, reconnect to physical `lan5` and restore DHCP/SSH before continuing.
Do not use `lan1` as an untagged recovery path; it is the Proxmox trunk.
If 6 fails, set root password in LuCI first.

---

## Stage 1 - build toolkit from scratch

Working directory: `<repo-root>\main\tools\router-deploy\`

```
tools/router-deploy/
|- README.md
|- .gitignore
|- lint.py
|- compile.py
|- deploy.ps1
|- test.ps1
|- uplink.ps1
|- generated/
|- snapshots/
|- logs/
|- lib/
|  |- parse_uci.py
|  `- ssh_session.ps1
`- keys/
   |- .gitkeep
   `- uplink_wifi.example.json
```

### Why this structure matters

Deploy must run from deterministic artifacts in `generated/`, not directly from source specs.  
This removes parser/deployer mismatch risk and gives auditable payloads.

---

## lint.py requirements (safety gate)

Reads the four source specs and exits nonzero on any failure with `file:line` diagnostics.

Required checks:

1. Structural
- Merge marker detection.
- Parse validity.
- Required section presence.

2. Cross-file consistency
- Firewall zone `network` values map to vlan-config interfaces.
- DHCP scope `interface` values map to vlan-config interfaces.
- Wireless `network` values map to vlan-config interfaces.
- VLAN set consistency.
- No duplicate PVID per physical port.

3. Address sanity
- DHCP dynamic ranges fit subnet.
- Static reservations inside valid subnet.
- Static reservations do not overlap dynamic ranges.
- Duplicate static IP detection.

4. Critical firewall reachability
- For each `input=REJECT` zone that relies on router DHCP/DNS, required DHCP/DNS input rules must exist.

### Parser hardening note

`firewall-config.conf` is an executable shell script that may use loops and variable expansion.  
Parser must support:
- double-quoted values
- shell-loop-generated rule names (`${ZONE}`)

If this is not supported, lint must validate *compiled artifacts* instead of raw source script for those checks.

---

## compile.py requirements (mandatory build step)

`compile.py` takes source specs and emits deploy-ready artifacts:

- `generated/network.uci`
- `generated/dhcp.uci`
- `generated/wireless.uci`
- `generated/firewall.sh` (or normalized equivalent)
- `generated/summary.json`

`summary.json` must include:
- VLAN/interface/zone counts
- critical invariants
- intended target IP/identity hints

Critical invariants to assert:
- lan5 appears as VLAN 1 untagged (`lan5:u*`)
- `lan` remains on `br-lan.1`
- expected LAN recovery address remains valid (`192.168.1.1`)

---

## deploy.ps1 requirements (hardened workflow)

1. Pre-flight + identity gate
- Check `keys/router_deploy` exists.
- Verify key-based SSH to `root@192.168.1.1`.
- Verify target router identity (board/model/OpenWrt release) matches expected GL-MT6000.
- Run `python lint.py` and profile-targeted `python compile.py`; abort on any failure.
- Print compiled summary (`generated/summary.json`).
- Require explicit confirmation phrase: `DEPLOY ROUTER` (unless `-Force`).

Profile policy:
- `first-flight` (default): minimum safe boot while placeholders may still exist.
- `first-flight` is bring-up only; client WiFi remains disabled until full profile is deployed with real secrets.
- `full`: strict mode that blocks on placeholders.

2. Snapshot (two-tier)
- Router snapshot: `/tmp/router-deploy-snapshots/<timestamp>/etc-config-*`
- Laptop snapshot copy: `tools/router-deploy/snapshots/<timestamp>/`
- Laptop snapshot copy failure is fatal before any router changes.
- A router-side rollback watchdog is armed before applying changes.

3. Apply generated payload
- Copy `network.uci`, `dhcp.uci`, and `wireless.uci` into `/etc/config/network`, `/etc/config/dhcp`, and `/etc/config/wireless`.
- Apply `firewall.sh` (or normalized firewall payload), which rebuilds and commits `/etc/config/firewall`.
- Parse-check all touched UCI packages before service restarts.
- In `first-flight`, strip temporary Bambuddy/Frigate WAN exception rules during compile so generated `firewall.sh` is already hardened.

4. Controlled restart order
- Restart network, then dnsmasq, then firewall.
- Wait for stabilization.

5. Staged post-checks
- SSH reachability within timeout.
- `ifstatus lan` shows expected LAN.
- `uci show network.@bridge-vlan[0].ports` confirms the lan5 recovery invariant.
- dnsmasq and firewall are healthy.

6. Soft rollback on any failed stage
- Restore `/etc/config/*` from router snapshot.
- Restart relevant services.
- Re-check connectivity.
- Report explicit rollback result.
- If SSH unreachable: print manual lan5 recovery instructions + laptop snapshot restore path.
- Cancel the router-side rollback watchdog only after health checks pass.

---

## test.ps1 requirements (post-deploy verification)

Translate `scripts/setup/router/network_testing_guide.md` into structured PASS/FAIL/WARN checks:

- VLAN interfaces and IPs (1,10,20,30,35,40,50,60,70,99)
- DHCP scope behavior
- DNS local + external
- SSID config via `uci show wireless` (not `iwlist scan`)
- Internet access matrix per VLAN policy
- Inter-VLAN isolation matrix (router-level caveats called out)
- Critical firewall rule-name presence (case-sensitive)

Produce summary counts and clear failing test details.

---

## .gitignore baseline

```
keys/router_deploy
keys/router_deploy.pub
snapshots/
generated/
logs/
*.bak
__pycache__/
```

---

## README.md must include

- Toolkit purpose and file map
- Stage 0 prerequisites
- First-run flow (Stages 2-5)
- Dry-run process (`lint.py` + `compile.py`)
- Deployment + rollback behavior
- Snapshot locations and manual restore
- Troubleshooting checklist

---

## Stage 2 - create and install deploy key

```powershell
cd <repo-root>\main\tools\router-deploy
ssh-keygen -t ed25519 -f .\keys\router_deploy -N '""' -C "router-deploy@laptop"
```

Install `keys/router_deploy.pub` via LuCI SSH-Keys page and verify:

```powershell
ssh -i .\keys\router_deploy root@192.168.1.1 "echo SSH_KEY_OK"
```

---

## Stage 3 - dry-run gates

```powershell
python <repo-root>\main\tools\router-deploy\lint.py
python <repo-root>\main\tools\router-deploy\compile.py --profile first-flight
```

`first-flight` applies minimum-safe transforms automatically:
- rewrites `wg0` as an inert stub and removes `wireguard_wg0` peer sections from generated network payload
- removes host reservations with placeholder MACs from generated DHCP payload
- disables SSIDs whose keys are still placeholders

```powershell
python <repo-root>\main\tools\router-deploy\compile.py --profile full
```

`--profile full` intentionally fails while WiFi passwords, WireGuard keys, or DHCP MAC addresses still contain placeholders.

---

## Stage 4 - first deployment

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <repo-root>\main\tools\router-deploy\deploy.ps1 -Profile first-flight
```

Watch live output and keep interactive troubleshooting ready (`ssh`, `uci show`, `ifstatus`, `logread`). The first-flight GL-MT6000 image did not include the `bridge` tool.

---

## Stage 5 - post-deploy test run

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <repo-root>\main\tools\router-deploy\test.ps1 -Profile first-flight
```

Investigate FAILs live before calling them test-harness issues.

---

## Stage 6 - optional temporary internet uplink (WiFi client WAN)

Use only if internet is needed for post-first-flight tasks (updates, package pulls, etc.).
This is temporary and should be removed when no longer needed.
The GL-MT6000 is intended to replace the existing home router later; do not
shape permanent routing policy around the current WiFi piggyback uplink.

1. Create local secret file (gitignored):

```powershell
Copy-Item <repo-root>\main\tools\router-deploy\keys\uplink_wifi.example.json <repo-root>\main\tools\router-deploy\keys\uplink_wifi.json
```

2. Populate `ssid` and `psk` in `keys\uplink_wifi.json`.

3. Enable uplink:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <repo-root>\main\tools\router-deploy\uplink.ps1 -Action enable
```

4. Verify status:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <repo-root>\main\tools\router-deploy\uplink.ps1 -Action status
```

5. Disable when finished:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <repo-root>\main\tools\router-deploy\uplink.ps1 -Action disable
```

---

## Architectural facts

### Hardware
- Router: GL.iNet GL-MT6000 (OpenWrt), lan1-lan5
- Server: MINISFORUM M1 Pro-125H (Proxmox, wired mgmt `enp86s0`)
- NAS: OMV at `192.168.40.50` via lan4 (VLAN 40)

### VLAN architecture

| VLAN | Name | Subnet |
|---|---|---|
| 1 | lan | 192.168.1.0/24 |
| 10 | management | 192.168.10.0/24 |
| 20 | automation | 192.168.20.0/24 |
| 30 | nvr | 192.168.30.0/24 |
| 35 | printers | 192.168.35.0/24 |
| 40 | storage | 192.168.40.0/24 |
| 50 | iot_sensors | 192.168.50.0/24 |
| 60 | monitoring | 192.168.60.0/24 |
| 70 | dmz | 192.168.70.0/24 |
| 99 | guest | 192.168.99.0/24 |

### Physical ports
- lan1: tagged trunk to Proxmox (VLANs 10,20,30,35,40,50,60,70)
- lan2: management untagged (VLAN 10), physically validated
- lan3: camera/NVR network untagged (VLAN 30), DHCP/DNS physically validated
- lan4: storage untagged (VLAN 40), DHCP/DNS physically validated
- lan5: recovery/AP untagged (VLAN 1), DHCP/DNS/LuCI physically validated

### Firewall local-service rule

Restricted zones keep `input='REJECT'` and `forward='REJECT'`, but their
zone `output` policy must be `ACCEPT`. Otherwise dnsmasq can receive DHCP
requests and create offers but the firewall blocks router-originated DHCP
replies with `Operation not permitted`.

### Critical safety rule

lan5 recovery mapping must never be lost during deployment.

---

## Out of scope

- Firmware install/upgrade
- Secret management overhaul
- CI/CD
- Multi-router support
- Non-router stack automation (Proxmox/HA/NAS/etc.)
- Diff-based idempotent deploy model

---

## Open questions

None currently. If user constraints change, update this handoff and README before continuing.

---

## Pick-up checklist

Before writing code:

1. Confirm the 4 canonical `main/configs/openwrt/*.conf` files still match expected versions.
2. Confirm lan5 recovery assumptions still hold in the design specs.
3. Confirm toolkit is being rebuilt intentionally from scratch.
4. Confirm Stage 0 prerequisites pass in the active laptop shell session.

If any mismatch appears, stop and align with user before build or deploy.
