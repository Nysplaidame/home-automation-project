# Router Deploy Toolkit

This toolkit builds and deploys OpenWrt router configuration from canonical source specs in:

- `main/configs/openwrt/vlan-config.conf`
- `main/configs/openwrt/dhcp-config.conf`
- `main/configs/openwrt/wireless-config.conf`
- `main/configs/openwrt/firewall-config.conf`
- `main/configs/openwrt/system-config.conf`

It uses a compile-first model:

1. `lint.py` validates source specs.
2. `compile.py` emits deterministic deployment artifacts to `generated/`.
3. `deploy.ps1` applies only router-owned generated state to the router (`network/dhcp/wireless` copied to `/etc/config`, `firewall.sh` executed, and narrow system/NTP UCI settings applied).
4. `test.ps1` performs post-deploy validation.

## Ownership Boundary

Router-deploy is deliberately router-only. It owns generated OpenWrt state for:

- VLAN bridge/interface configuration.
- DHCP scopes, static reservations, and local DNS names.
- Router firewall zones, forwarding policy, and narrow host/port rules.
- Wireless SSID definitions.
- Dormant WireGuard fallback config.
- Router-local NTP intent.
- Validation artifacts and router snapshots.

Router-deploy does not deploy or configure:

- Docker containers, Compose stacks, or docker-host host services.
- Proxmox VMs, HAOS add-ons, Frigate, OMV, Tailscale auth, or app databases.
- ntfy users/topics, Uptime Kuma monitors/notifications, or service credentials.
- Live app state under `/opt/stacks/`, `/config`, `/opt/monitoring`, or NAS paths.

If a task changes a non-router endpoint, use that endpoint's manual and keep the
router-deploy side limited to DNS, DHCP, firewall, NTP, and validation support.

## Current First-Flight State

As of 2026-05-07, first-flight has been applied to the GL-MT6000 and the
physical recovery/access ports have been smoke-tested:

| Port | Role | Verified client behavior |
|---|---|---|
| `lan5` | Recovery/AP, VLAN 1 untagged | DHCP `192.168.1.x`, gateway/DNS `192.168.1.1`, LuCI reachable |
| `lan2` | Management, VLAN 10 untagged | DHCP `192.168.10.x`, gateway/DNS `192.168.10.1` |
| `lan3` | NVR, VLAN 30 untagged | DHCP `192.168.30.x`, DNS `192.168.30.1`; router admin blocked by policy |
| `lan4` | Storage, VLAN 40 untagged | DHCP `192.168.40.x`, DNS `192.168.40.1`; router admin blocked by policy |
| `lan1` | Proxmox trunk | Tagged VLANs only; test with Proxmox/VLAN-aware client |

Restricted client zones use `input='REJECT'` and explicit DHCP/DNS/NTP input rules.
Their firewall zone `output` policy must stay `ACCEPT` so the router can send
DHCP, DNS, NTP, and other explicitly allowed local-service replies back to
clients. `test-connectivity.ps1` checks this regression.

Router-deploy also owns the router-local NTP server intent. It enables
`system.ntp.enable_server='1'` without replacing the whole OpenWrt
`/etc/config/system` file, so board-specific system sections remain intact.

Current staging internet: `uplink.ps1` may be used to attach the GL-MT6000 to
the existing home router over WiFi while Proxmox/Home Assistant need package
downloads. This is not the final WAN architecture: the GL-MT6000 is intended to
replace the existing home router later. Keep this uplink as an explicit
temporary staging path, and disable it when testing isolated local behavior.

## Files

- `lint.py`: static safety checks for source specs.
- `compile.py`: compiler for deploy artifacts + `summary.json`.
- `deploy.ps1`: hardened deploy workflow with identity gate, rollback, and router-local NTP application.
- `test.ps1`: post-deploy checks against UCI config, DNS policy, service aliases, firewall rule intent, and NTP intent (PASS/FAIL/WARN).
- `test-connectivity.ps1`: post-deploy active-state checks — per-VLAN L3 probes, dnsmasq health, sysntpd health, live nft ruleset, zone forwarding policy.
- `uplink.ps1`: optional temporary WAN-over-WiFi helper for post-first-flight testing.
- `lib/parse_uci.py`: parser helpers for UCI source formats.
- `lib/ssh_session.ps1`: SSH/SCP helper functions.

## Stage 0 Prerequisites

Run on the deployment laptop:

```powershell
powershell -NoProfile -Command "$PSVersionTable.PSVersion"
python --version
ssh -V
Test-Path "<repo-root>\main\configs\openwrt\vlan-config.conf"
ipconfig | Select-String "IPv4"
ssh root@192.168.1.1 "echo OK; exit"
```

Expected recovery network path: laptop has `192.168.1.x`, router is `192.168.1.1`.

## First Run

1. Generate deploy key:

```powershell
cd <repo-root>\main\tools\router-deploy
ssh-keygen -t ed25519 -f .\keys\router_deploy -N '""' -C "router-deploy@laptop"
```

2. Add public key in LuCI (`System -> Administration -> SSH-Keys`).

3. Verify key auth:

```powershell
ssh -i .\keys\router_deploy root@192.168.1.1 "echo SSH_KEY_OK"
```

4. Dry run:

```powershell
python .\lint.py
python .\compile.py --profile first-flight
```

For controlled first flight, `--profile first-flight` is the intended path.
It is the safe bring-up profile: placeholders are contained, WiFi with
placeholder keys is disabled, WireGuard peers are removed, and temporary
maintenance egress rules are stripped from generated output.
Strict full deploy still requires:

```powershell
python .\compile.py --profile full
```

`--profile full` is the final populated profile. It blocks if WiFi passwords,
WireGuard keys, or DHCP MAC addresses still contain placeholders, and it is the
profile to use only after secrets and real hardware identities are ready.

Expected `lint.py` success shape:

```text
Router Config Lint
============================================================
PASSED: all checks clean.
```

Expected `compile.py --profile first-flight` success shape:

```text
[INFO] Stripped 2 TEMP firewall rule(s).
[INFO] First-flight adjustments applied:
  - wg0_stubbed: 1
  - removed_wg_peer_sections: 3
  - removed_placeholder_hosts: <count>
  - disabled_wifi_ifaces: <count>
[OK] Artifacts written:
  - ...\generated\network.uci
  - ...\generated\dhcp.uci
  - ...\generated\wireless.uci
  - ...\generated\system.uci
  - ...\generated\firewall.sh
  - ...\generated\summary.json
```

5. Deploy:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\deploy.ps1 -Profile first-flight
```

Expected deploy success shape:

```text
[OK] Router identity verified.
[OK] Router snapshots created.
[OK] Generated configs copied.
[OK] Services restarted and health checks passed.
[OK] Watchdog cancelled.
```

For a later fully populated rollout:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\deploy.ps1 -Profile full
```

6. Validate:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\test.ps1 -Profile first-flight
powershell -NoProfile -ExecutionPolicy Bypass -File .\test-connectivity.ps1 -Profile first-flight
```

Expected `test.ps1` success shape is a PASS-only summary, for example:

```text
Summary: PASS=<count> WARN=0 FAIL=0
```

Expected `test-connectivity.ps1` success shape after the current first-flight
deployment is:

```text
Summary: PASS=83 WARN=0 FAIL=0
```

`test.ps1` checks that the deployed UCI config matches expectations, including
AdGuard-first DNS, Quad9 public fallback, no Google DNS fallback, service
aliases, router-local NTP enablement, and the host-only OMV remote-access rule.
`test-connectivity.ps1` complements it by inspecting actual kernel state — VLAN
interfaces are up, dnsmasq is serving DNS, sysntpd is running, the loaded
nftables ruleset matches the firewall config, and zone-pair forwarding policy is
enforced as expected.
It also verifies that restricted zones allow router-originated output, which is
required for DHCP/DNS replies even when zone input and forwarding remain locked
down.
On first run of `test-connectivity.ps1`, manually verify that `nft list chain
inet fw4 forward_lan` on your router shows `accept_to_<zone>` helper-chain
jumps; the Section 4 zone-pair checks depend on this firewall4 render.

## Rollback and Snapshots

- Router snapshots are created in `/tmp/router-deploy-snapshots/<timestamp>/`.
- Laptop pullback copies are stored in `snapshots/<timestamp>/`.
- On failure, `deploy.ps1` attempts automatic restore + service restarts.
- A router-side watchdog is armed before applying changes and cancelled only after health checks pass.
- In `first-flight`, `wg0` is rewritten as an inert stub, WireGuard peer sections are removed from generated `network.uci`, host reservations with placeholder MACs are removed from `dhcp.uci`, and SSIDs with placeholder keys are forced `disabled '1'`.
- In `first-flight`, temporary Docker-host/Frigate WAN exception rules are stripped during compile so generated `firewall.sh` is already hardened.
- First-flight is bring-up only: expect no client-usable WiFi until secrets are populated and full profile is deployed.
- If router becomes unreachable, use physical lan5 recovery path and restore `/etc/config/*` manually.

## Physical lan5 Recovery Drill

Use this path when deploy connectivity is lost and the watchdog did not restore
access automatically.

1. Move the laptop Ethernet cable to router `lan5`.
2. Set the laptop adapter to DHCP, or use static `192.168.1.10/24` with gateway
   `192.168.1.1`.
3. Confirm the router answers:

```powershell
ping 192.168.1.1
ssh -i .\keys\router_deploy root@192.168.1.1 "echo RECOVERY_OK"
```

4. Inspect the latest router-side snapshot:

```sh
ls -1 /tmp/router-deploy-snapshots
```

5. Restore the newest known-good snapshot, then restart services:

```sh
SNAP=/tmp/router-deploy-snapshots/<timestamp>
cp "$SNAP"/network /etc/config/network
cp "$SNAP"/dhcp /etc/config/dhcp
cp "$SNAP"/wireless /etc/config/wireless
cp "$SNAP"/firewall /etc/config/firewall
/etc/init.d/network restart
/etc/init.d/dnsmasq restart
/etc/init.d/firewall restart
```

6. Return to management access on `lan2` / `192.168.10.1` and rerun both test
   scripts before attempting another deploy.

## Optional Temporary Uplink Phase

Use this only after first-flight succeeds and only as a temporary staging path.
The current upstream home router also uses `192.168.1.0/24`, so this helper is
intentionally a short-term convenience for downloads/updates, not a permanent
WAN design.

1. Create local secret file (gitignored):

```powershell
Copy-Item .\keys\uplink_wifi.example.json .\keys\uplink_wifi.json
```

2. Fill `ssid` / `psk` in `keys\uplink_wifi.json`.

3. Enable temporary uplink:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\uplink.ps1 -Action enable
```

4. Check status:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\uplink.ps1 -Action status
```

5. Disable when done:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\uplink.ps1 -Action disable
```

## Troubleshooting

- `lint.py` fails with DHCP/DNS input rule errors:
  - Verify parser supports firewall loop-generated rules and double-quoted values.
- Deploy aborts at identity gate:
  - Confirm target is the intended GL-MT6000 at `192.168.1.1`.
- SSH key auth fails:
  - Reinstall `keys/router_deploy.pub` in LuCI and retry with `ssh -i`.
- Connectivity lost after restart:
  - Wait full timeout; rollback should trigger.
  - If not reachable, recover via lan5 and restore latest snapshot.

## Scope Summary

- Router config only.
- Wipe-and-rebuild deployment model for router-owned UCI state.
- No firmware install/upgrade orchestration.
- No Proxmox, HA, Docker, NAS, Tailscale, monitoring, or app orchestration in
  this toolkit.
