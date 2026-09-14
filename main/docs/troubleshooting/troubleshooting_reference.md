---
title: Troubleshooting Reference
description: Cross-system quick diagnosis for the current deployed architecture
tags: [troubleshooting, diagnostics, recovery, architecture]
created: 2026-05-08
modified: 2026-09-10
type: reference
status: active
---

# Troubleshooting Reference

This reference follows the [September recorded baseline](../reference/current-live-state.md):
HA uses native HTTPS, Frigate runs in CT 111 with three configured but
deliberately disconnected cameras, local AI runs in CT 114, OMV is directly
on router LAN4/VLAN40, and Hive uses LAN2/VLAN55. P1S is uncommissioned.
Docker-host uses explicit Compose bridges with documented host-network
exceptions; remote Homepage cards use fixed HTTPS proxy ports.

The [written diagnostic walkthroughs](diagnostic-walkthroughs.md) cover all five
troubleshooting app investigations, including commands, expected results,
evidence freshness and recovery links. The app complements these documents;
it does not replace them. Its September 10 improvements are deployed and
live-tested; the Proxmox collector update and fresh backup evidence remain open. See its [deployment record](../../apps/troubleshooting-dashboard/README.md).

## Diagrams for diagnosis

| Investigating | Mermaid source |
|---|---|
| Physical connection or wrong VLAN | [Cabling](../diagrams/network/physical-port-and-cabling.mermaid), [VLAN inventory](../diagrams/network/vlan_architecture_clean.mermaid) |
| DNS, NTP or remote access | [DNS/NTP](../diagrams/network/dns-ntp-flow.mermaid), [Tailscale/proxies](../diagrams/network/remote-access-flow.mermaid) |
| Firewall or source-specific failure | [Access policy](../diagrams/network/security-access-flow.mermaid) |
| Guest or container failure | [Proxmox guests](../diagrams/infrastructure/proxmox-guests-and-backups.mermaid), [Docker services](../diagrams/infrastructure/docker-host-service-placement.mermaid) |
| Missing recordings or backups | [Storage and backup flow](../diagrams/storage/storage-and-backup-flow.mermaid) |
| VentSys control or commissioning | [Control and safety flow](../diagrams/ventsys/ventsys-control-and-safety-flow.mermaid) |

The [diagram library](../diagrams/README.md) also links the rendered viewer.

## Start here

1. Record the symptom and time; do not restart several systems at once.
2. Check the path from the operator inward: client/DNS/TLS, router/firewall,
   host or guest, container/service, dependency, then storage or physical device.
3. Run `scripts/monitoring/health_check.ps1 -Full` from Windows, or
   `scripts/monitoring/health_check.sh --json` from Proxmox.
4. Compare the result with `docs/reference/current-live-state.md`,
   `docs/reference/service-matrix.md`, and `docs/reference/access-matrix.md`.
5. Preserve the exact error, HTTP status, timestamp and relevant logs before a
   change. Prefer one reversible action followed by the same validation.

Historical audits and handoffs may describe earlier states. They are evidence,
not the current operating instructions.

---

## MQTT / VentSys

> **Port note:** MQTT TLS on port 8883 is the normal path. Plaintext 1883 is
> not an existing router exception for valve 1. Do not assume 1883 is allowed
> because an uncommissioned source file still uses it. See the
> [TLS guide](../procedures/ssl_tls_guide.md).

### ESPHome device shows offline in HA

First confirm the device was adopted and its actual IP and transport are
recorded. Hardware-dependent entities may be unavailable because the device
is not commissioned. Ping loss alone does not prove Wi-Fi failure; ICMP policy,
address changes and routing can produce the same symptom.

Run on: Home Assistant Terminal & SSH add-on, for the verified example device.

```sh
ping -c 3 192.168.50.21
nc -zv 192.168.50.21 6053
```

Expected: reachability and native API only if that device actually enables it.
For an MQTT-only build, native API port6053 is not an acceptance criterion.
Inspect ESPHome logs, DHCP/SSID and the configured transport before restarting
or reflashing. A closed port can mean a disabled listener or filtering, not
necessarily broken firmware.

### MQTT broker not connecting (in HA)

Run on: Home Assistant Terminal & SSH add-on.

```sh
nc -zv 192.168.20.101 8883
```

Expected: broker TCP listener reachable. Use the HA MQTT integration's
configured authenticated listen tool for an approved diagnostic topic, or the
[TLS procedure](../procedures/ssl_tls_guide.md) from a client with the correct
CA and credentials. Use the recorded broker address covered by its certificate;
`localhost` in an add-on is not a substitute for the HA broker address.

Separate timeout/refusal, certificate validation and authentication errors.
A subscriber waiting without messages is normal; it does not prove a stopped
broker. Inspect Mosquitto add-on logs and the actual listener before a restart.
Do not paste passwords into shell examples, history or the incident report.

### VentSys device not publishing MQTT topics

Use HA's configured MQTT integration to listen to `ventsys/#` and inspect
that device's ESPHome logs. A quiet topic can mean no event was emitted, an
incorrect topic, missing subscription permission or an uncommissioned device.
Check connection/authentication and the exact source YAML before power-cycling.
Do not publish actuator or emergency topics as an ordinary connectivity test.

### Dashboard shows `○ HA OFFLINE`

Open the dashboard through its authenticated Lovelace card bridge while
signed into Home Assistant. Inspect browser WebSocket/bridge errors and confirm
HA's native HTTPS endpoint responds. The dashboard source explicitly ignores
tokens supplied by public `ventsys-config.js`; do not put a long-lived token in
public HTML/JavaScript or recreate that older deployment pattern. A separately
opened static page may lack the authenticated bridge even while HA is healthy.
Use the [dashboard source](../../dashboards/ventsys-dashboard.html) and current
HA card configuration to trace the bridge before changing credentials.

---

## Home Assistant

### HA web UI not loading

Run on: Windows management workstation in PowerShell.

```powershell
Test-NetConnection 192.168.20.101 -Port 8123
Invoke-WebRequest https://192.168.20.101:8123/ -UseBasicParsing
```

Expected: TCP and trusted HTTPS succeed. For failed TCP, check VM100 and its
console, VLAN20 and listener; ping alone cannot establish the failed layer.
For a certificate error, check Home Local CA trust and hostname/address coverage.
Do not change the documented service to HTTP to hide a trust failure. See the
[HA walkthrough](diagnostic-walkthroughs.md#2-home-assistant-unavailable).

### HA restarting repeatedly after config change

Use the Proxmox VM100 console to observe startup errors. If the Terminal &
SSH add-on is reachable, inspect and validate there:

Run on: Home Assistant Terminal & SSH add-on.

```sh
ha core logs
ha core check
```

Expected: configuration check succeeds; preserve the first named error when
it does not. Back up and repair the exact package through HA's file editor or
an established recovery path. The Proxmox host and HAOS console are different
contexts from the add-on filesystem. Renaming a whole package can remove
safety entities, so review its effect rather than disabling one generically.
Restart HA only after validation and a bounded recovery plan.

### Entity missing after HA restart

- Check Settings → System → Logs for YAML errors
- Search for the entity in Settings → Devices & Services → Entities (include disabled)
- If from a package: run `ha core check` in the HA Terminal add-on; YAML syntax alone does not validate HA schemas

### Automations not firing

1. Check Settings → Automations → select automation → Traces (shows last 10 runs and why they did/didn't trigger)
2. Check mode: if `mode: single` the automation won't re-trigger while already running
3. Check condition block — conditions silently block execution

---

## Frigate

### Camera shows grey / offline in Frigate UI

Check the dated disconnected-camera baseline first. For a connected camera,
use the [camera walkthrough](diagnostic-walkthroughs.md#3-camera-unavailable-or-recordings-missing).

Run on: Frigate CT111 shell.

```sh
nc -zv 192.168.30.21 554
```

Expected for commissioned camera1: the RTSP listener is reachable. Connection
refused is a listener/rejection symptom, not proof of a wrong RTSP path or
password. If TCP works, inspect Frigate's stream/authentication logs and the
recorded `/Streaming/Channels/101` and `/102` paths. Keep authenticated RTSP
URLs out of command history and reports.

### Frigate can't reach MQTT (HA)

Run on: Frigate CT111 shell.

```bash
# From frigate-nvr CT (192.168.30.20)
nc -zv 192.168.20.101 8883
```
- Fails: check the `Frigate MQTT to HA` rule in firewall-config.conf
  (src: nvr, src_ip: 192.168.30.20, dest: automation, dest_port: 8883)
- If source contains the rule but the probe fails, inspect live rule counters,
  the CT source address, HA listener and host firewall. Source presence alone
  cannot establish deployment or identify the failed layer. Use router-deploy
  validation before considering a rule change.

### HA can't reach Frigate

Run on: Home Assistant Terminal & SSH add-on.

```bash
# From HA Terminal
nc -zv 192.168.30.20 5000    # HA integration API
nc -zv 192.168.30.20 8971    # authenticated browser UI
```
- Fails: check `HA to NVR Access` rule — verify src_ip is 192.168.20.101
- Also check the CT firewall allows the HA source to the required API/stream
  ports. Do not expose API port `5000` through the remote Frigate host route.

### Frigate container not starting

Run on: Frigate CT111 shell.

```bash
cd /opt/frigate && docker compose logs frigate
```
- `shared memory` error: compare actual limits and workload with the Frigate manual before a scoped resource change
- `camera ... connection refused`: inspect listener, address and rejection; verify path/auth only after TCP works
- `MQTT connection refused`: see MQTT section above

---

## Proxmox / VMs

### VM not getting its IP

1. Check VM is started: `qm status 100`
2. Check VM console (VM → Console) — HAOS shows its IP on screen
3. Check DHCP lease: on router, `cat /tmp/dhcp.leases | grep 192.168.20`
4. If no lease: establish whether the guest uses DHCP or a static address; then compare MAC, VLAN and DHCP logs
5. Check VM network: `qm config 100 | grep net0` — confirm `tag=20`

### Proxmox web UI not accessible after reboot

Run on: Proxmox host local console or established SSH session.

```bash
ip addr show    # confirm vmbr0.10 has 192.168.10.10
ping -c 3 192.168.10.1    # router reachable?
systemctl --no-pager status pveproxy
journalctl -u pveproxy -n 40 --no-pager
```

### VM not starting at boot

Run on: Proxmox host shell.

```sh
qm config 100 | grep -E 'onboot|startup'
```

Compare boot policy and order with the guest inventory before changing it.
Retired rollback VMs101/104 must remain off while CT111/114 own their addresses.
A missing boot setting does not justify assigning every guest the same order.

---

## Router / Network

### Can't reach router web UI after VLAN change

- Use HomeAdmin for management at `192.168.10.1`; LAN2 is Hive/cloud IoT,
  not a management port.
- For wired recovery, use LAN5, DHCP `192.168.1.x` and router `192.168.1.1`.
  If DHCP fails, the router phase documents temporary `192.168.1.10/24`.
- Allow an active router-deploy watchdog rollback to finish before intervening.
  Follow the [LAN5 recovery drill](../install/phases/01-router-openwrt.md#10-rehearse-physical-lan5-recovery-before-full-deployment)
  and select an explicit known-good snapshot. A factory reset is not the first
  diagnostic step.

### Internet or Hive fails after the fibre change

The recorded WAN is untagged Zen PPPoE on `eth1`; the retired Zyxel Wi-Fi
uplink is disabled. Check WAN session, default route and DNS separately using
the [router guide](../install/phases/01-router-openwrt.md) and
[physical map](../reference/physical-port-and-cabling.md). Do not dump PPPoE
credentials into reports. IPv4 recovery does not establish IPv6 acceptance:
Zen returned `NoAddrsAvail` / `NoPrefixAvail` in the September investigation.

Hive has a recorded lease at `192.168.55.10`, router DNS/NTP and WAN-only
forwarding; its app still reported offline despite observed internet traffic.
Separate network evidence from owner-side account/app acceptance. Do not add
internal forwarding to resolve an unexplained vendor-app status.

### Device on wrong VLAN

1. Check `bridge vlan show` on the router
2. Check MAC against DHCP leases to identify which VLAN it landed on
3. Verify the physical port assignment in `vlan-config.conf`

### Two devices have the same IP

Run on: OpenWrt router shell.

```bash
cat /tmp/dhcp.leases
uci show dhcp | grep "\.ip="
```
Compare reservations with each interface's actual DHCP range in
`configs/openwrt/dhcp-config.conf`. There is no universal below-`.100` rule:
HA uses `.101`, docker-host `.102`, and the planned P1S `.200`.

### DNS not resolving local hostnames

Run on: OpenWrt router shell.

```bash
nslookup homeassistant.home.local 127.0.0.1
```
- Fails: check dhcp-config.conf has the domain entries and dnsmasq is running
- `local '/home.local/'` must be in the dnsmasq config block

### AdGuard filtering not working

Run on: Windows management workstation in PowerShell.

```powershell
nslookup example.com 192.168.10.1
```

Run on: OpenWrt router shell.

```sh
nslookup example.com 192.168.20.102
```

- Router query to docker-host fails: check AdGuard container, docker-host UFW, and `adguard.home.local`.
- Client query works but ads are not blocked: confirm router dnsmasq has `192.168.20.102#53` first.
- Household DNS down: router should fall back to `9.9.9.9`, `1.1.1.1`, then `1.0.0.1`; check dnsmasq logs.

### Clients bypass AdGuard

- DHCP clients should receive only their local router gateway as DNS.
- Direct WAN DNS on ports 53/853 should be blocked for ordinary client zones.
- Management VLAN remains the emergency/admin exception path.

---

## Tailscale Remote Access

### Tailscale client cannot reach HA

Run on: an approved admin Tailscale client with a POSIX shell and the named host-route grants.

```bash
tailscale status
ping -c 3 192.168.20.101
curl -I https://192.168.20.101:8123
```

- Confirm docker-host is online in the tailnet.
- Confirm `192.168.20.101/32` is advertised and approved.
- Confirm Tailscale ACLs allow the client to reach HA on 8123.

This direct host route is an admin path. The approved OnePlus daily portal
identity normally opens `https://homepage.home.local/` and its fixed proxy
ports rather than browsing routed private addresses.

### Tailscale client cannot reach OMV

Run on: an approved admin Tailscale client with a POSIX shell and the named host-route grants.

```bash
ping -c 3 192.168.40.50
curl -I http://192.168.40.50/
```

- Confirm `192.168.40.50/32` is advertised and approved.
- Confirm OpenWrt allows docker-host routed access only to the OMV host where required.
- Do not widen this to the whole storage VLAN.

### Homepage cards fail on mobile data

```text
https://homepage.home.local/
https://homepage.home.local:8180/ ... :8209/
```

- Confirm Tailscale is connected and split DNS resolves `homepage.home.local`
  to docker-host's tailnet address `100.94.122.18`.
- Confirm the device identity is the approved OnePlus client and its grant
  permits DNS, `tcp/443`, and `tcp/8180-8209` only.
- If Homepage opens but one card fails, test that card's fixed proxy port and
  then its fixed upstream from docker-host. Do not add a broad VLAN route.
- qBittorrent is the deliberate same-origin
  `/portal-preview/qbittorrent/` exception rather than a separate proxy port.

### Docker-host services unreachable over Tailscale

- Connect to docker-host's Tailscale name/IP, not the VLAN IP unless a route is intended.
- Check docker-host UFW for `tailscale0` allowances.
- Check the service is bound to the expected port from `docs/reference/service-matrix.md`.

### Grafana or Uptime Kuma unreachable over Tailscale

Run on: an approved admin Tailscale client with a POSIX shell and the named host-route grants.

```bash
ping -c 3 192.168.60.10
curl -I http://192.168.60.10:3000/
curl -I http://192.168.60.10:3001/
```

- Confirm docker-host advertises `192.168.60.10/32` and that the route is
  approved in the Tailscale admin console.
- Confirm docker-host has UFW route rules from `tailscale0` to
  `192.168.60.10` ports `3000` and `3001`.
- Keep InfluxDB port `8086` off the daily mobile route unless an admin-only
  exception is explicitly documented.

## WireGuard VPN

WireGuard is a dormant fallback. Confirm intentional activation through the
[governance procedure](../procedures/wireguard_fallback_governance.md) before
treating an absent listener or handshake as an outage.

### VPN won't connect

1. Confirm port 51820 UDP is reachable from outside
2. On router: `netstat -ulnp | grep 51820`
3. Check `Endpoint` IP in client config matches current WAN IP — use DDNS if IP changes
4. Check client clock — VPN handshake fails if clock is significantly wrong

### VPN connects but can't reach HA

1. Confirm `AllowedIPs` includes `192.168.20.101/32`
2. Confirm `VPN to Home Assistant` rule exists: `uci show firewall | grep "VPN to Home Assistant"`
3. Check VPN client IP is in 10.0.0.0/24 range

### VPN connects but all traffic is broken

Compare an allowed private IP/port test with a local-name lookup from the same
client. Confirm the configured DNS server itself is included in the permitted
route/access policy. Public DNS cannot resolve `home.local`; replacing it with
a public resolver is not a local-service recovery. Follow the
[WireGuard fallback governance](../procedures/wireguard_fallback_governance.md)
before activating or changing the dormant fallback.

### VPN fallback cannot reach OMV

1. Confirm `AllowedIPs` includes `192.168.40.50/32`, not `192.168.40.0/24`.
2. Confirm `VPN to OMV NAS` exists before `Block VPN to Storage`.
3. Test only the required OMV ports: 80/443 for UI, 445 for SMB, 2049 for NFS, 22 for admin.

---

## Docker-host Compose Services

### Compose stack will not start

Replace `<service>` with the exact stack directory from the service matrix.

Run on: docker-host shell.

```bash
cd "/opt/stacks/<service>" || exit 1
docker compose config --quiet
docker compose logs --tail=80
```

- Invalid config: fix the Compose or `.env` file.
- Port already in use: inspect `ss -tlnp` on docker-host for the exact port from the service matrix.
- Permission issue: check ownership under `/opt/stacks/<service>/`.
- Network overlap or wrong Compose label: compare the stack with
  `configs/docker-host/NETWORK-ALLOCATION.md`; every project bridge must use its
  explicit CIDR and a Compose network key matching the explicit network name.
- Run `/usr/local/sbin/docker-host-security-audit.sh --verify` after any network
  or firewall change. The current expected exception is Bambuddy's bridge
  attachment only, until the P1S network path is restored.

### Docker-host cannot reach the internet

- General image pulls should still use temporary maintenance access.
- Tailscale has a narrow permanent egress rule.
- AdGuard has a narrow upstream DNS egress rule.
- Do not re-add broad docker-host internet permanently just to make pulls easy.

## Immich

### Immich UI unreachable

Run on: docker-host VM103 shell.

```bash
# On docker-host
cd /opt/stacks/immich
docker compose ps
ss -tlnp | grep 2283
```

- If port 2283 is not listening, inspect `docker compose logs`.
- If LAN works but Tailscale fails, check docker-host UFW `tailscale0` rules.
- If uploads fail, check the OMV-backed library mount and disk space.

## Homepage

### Homepage UI unreachable

Run on: docker-host VM103 shell.

```bash
cd /opt/stacks/homepage
docker compose ps
ss -tlnp | grep -E ':443|:3001|:81[89][0-9]|:820[0-9]'
docker compose exec -T preview-proxy nginx -t
```

- Confirm `homepage.home.local` resolves to `192.168.20.102`.
- Use `https://homepage.home.local/` as the normal local and remote bookmark;
  `http://192.168.20.102:3001/` is the rollback path.
- Check config syntax in `/opt/stacks/homepage/config/`.
- If only previews fail, validate the fixed-target proxy sidecar, its source-
  scoped UFW rules and the exact `8180-8209` mapping in `services.yaml`.

## Dozzle

### Dozzle shows no containers or is unreachable

Run on: docker-host VM103 shell.

```bash
cd /opt/stacks/dozzle
docker compose logs --tail=80
docker ps
```

- Confirm Dozzle can access the Docker socket if configured that way.
- Keep Dozzle admin/internal only; do not expose it to Guest or DMZ.

## Bambuddy / P1S printer

> **Architecture note:** Bambuddy runs as a workload on docker-host,
> VM 103 (192.168.20.102, VLAN 20).
> P1S is not commissioned in the September baseline; its intended address is
> 192.168.35.200 (VLAN 35 — Printers, HomePrinters WiFi SSID).
> The P1S runs its own MQTT broker on port 8883 — Bambuddy connects TO the
> printer, not the other way around.
> Bambuddy currently remains on host networking. Its explicit
> `10.240.23.0/24` bridge and routed UFW rules are prepared, but migration is
> blocked until VM 103 itself can reach P1S ports `21` and `8883`.

### Bambuddy container not starting

Run on: docker-host VM103 shell.

```bash
# On VM 103 (docker-host):
cd /opt/stacks/bambuddy && docker compose logs bambuddy --tail=40
```
- Port 8000 already in use: `ss -tlnp | grep 8000`
- Volume permission error: compare the named failing path, actual mount and
  runtime UID/GID with the stack configuration before changing ownership.
  Do not recursively change the whole stack directory.

### Bambuddy UI unreachable (http://192.168.20.102:8000)

Run on: docker-host VM103 shell.

```bash
# On VM 103:
docker ps | grep bambuddy
ss -tlnp | grep 8000
```
- Container not running: `docker compose up -d bambuddy`
- Port not bound but container up: check logs

### P1S shows "Connection Failed" in Bambuddy

Run on: docker-host VM103 shell.

```bash
# From VM 103 (docker-host):
nc -zv 192.168.35.200 8883    # should say open
nc -zv 192.168.35.200 21      # FTP/control path used by the integration
ping 192.168.35.200            # basic reachability
```
- Printer not at 192.168.35.200: check DHCP leases on router, confirm P1S is on HomePrinters SSID
- `Bambuddy to Printer MQTT` firewall rule missing — check firewall-config.conf
- Developer Mode not enabled on printer: re-enable via touchscreen Settings → Network
- Wrong Access Code: regenerate via Settings → Network → Developer Mode on printer
- If connections drop only while another integration is connected, compare
  the printer and client logs and retry with that client disconnected. Record
  the installed firmware behavior rather than assuming a universal client limit.

### Bambuddy MQTT not publishing to HA

Use HA's configured MQTT integration to listen to `bambuddy/#`; inspect
Bambuddy's publishing settings and logs. Do not start a real print just to
produce diagnostic traffic. Check a normal observed state update after P1S
commissioning and confirm the serial/topic match.

Run on: docker-host VM103 shell.

```sh
nc -zv 192.168.20.101 8883
```

Expected: HA broker listener reachable. This VLAN20-local path is not enforced
by the router's inter-VLAN firewall. A successful TCP check still needs TLS,
authentication and topic acceptance.

### HA API connection fails in Bambuddy (smart plug control broken)

- VLAN 20 is the HA+Docker host trust boundary; this path is not router-firewall enforced.
- From VM 103: `nc -zv 192.168.20.101 8123` — should be open
- Check the actual HTTPS/authentication error and configured token first. Rotate only if needed, updating the protected credential and dependent service together.

### P1S HA entities unavailable after package deploy

- Confirm serial number placeholder replaced:
  `grep '<P1S_SERIAL>' /config/packages/bambuddy_p1s_package.yaml` → should return nothing
- Listen to `bambuddy/printers/+/status` through HA's configured MQTT integration.
- Check HA logs: Settings → System → Logs, filter for "mqtt"

### P1S not getting IP on HomePrinters SSID

- Confirm HomePrinters SSID is broadcasting (check wireless-config.conf is deployed)
- Confirm P1S is set to LAN mode: printer touchscreen Settings → Network
- Check DHCP lease for 192.168.35.200 on the router: `cat /tmp/dhcp.leases | grep 192.168.35`
- If the address differs from planned `.200`, compare the actual MAC/reservation and renew state; do not infer the cause from its final octet alone.

## OMV NAS

### HA can't mount NAS backup share

Check **Settings → System → Storage** and the Supervisor logs for the
configured network storage. The HA Terminal add-on is not the HAOS host;
an arbitrary mount inside it does not validate HA-managed backup storage.
Compare the share/export and authorized client with the
[OMV contract](../../configs/omv/README.md).

- Permission denied: verify the exact export, HA client `192.168.20.101`, and
  export permissions using the [OMV guide](../../scripts/setup/nas/omv_nas_setup_guide.md).
- Timeout: check OMV's direct LAN4/VLAN40 attachment, NFS listener and the
  scoped HA-to-storage rule. Do not widen the entire storage VLAN.

### Backup or monitoring evidence is incomplete

Use the [backup walkthrough](diagnostic-walkthroughs.md#5-backup-freshness-uncertain)
to distinguish VM/CT archive freshness, VM103 application job success, and
isolated restore proof. September's direct Proxmox/OMV SSH denial leaves new
guest-backup/SMART evidence open; it does not prove those services failed.

Monitoring has separate known gaps: CT114 Fail2ban is inactive, its package
access is unresolved, and Watchtower's ntfy delivery failed with error `40014`.
Use the [update review log](../procedures/update_review_log.md) and
[host hardening guide](../procedures/fail2ban_host_rollout.md); a healthy
container or monitor does not prove alert delivery or patch freshness.

### Frigate recordings are not reaching OMV

CT 111 does not mount NFS directly. Proxmox mounts
`192.168.40.50:/export/frigate` at `/mnt/omv/frigate`, then bind-mounts it into
CT 111 at `/mnt/nas/frigate`.

1. On Proxmox, confirm the NFS mount source and free space.
2. Confirm `pct config 111` contains the expected `mp0` bind mount.
3. In CT 111, confirm `/mnt/nas/frigate` is writable by the unprivileged UID
   mapping and new recording segments appear.
4. If mounted but unwritable, verify the OMV ACL for host UID `100000`; do not
   enable dormant NFS client units inside CT 111.

### Immich can't write media to OMV

- On docker-host, verify the OMV-backed mount is present before starting Immich.
- Check the OMV service user has write access to the `immich` shared folder.
- Check disk free space and SMART status before retrying bulk imports.

### NAS drive failing

Use OMV's disk inventory to match model and serial to the actual device
before interpreting SMART. `/dev/sda` is not a durable drive identity. Review
the complete SMART health/error/self-test information in OMV or through the
[storage guide](../../scripts/setup/nas/omv_nas_setup_guide.md).

A passing overall flag does not rule out I/O or filesystem trouble. Preserve
errors, verify backup/array state and identify the exact physical drive before
a replacement plan. Do not pull a disk solely because a filtered output line
contains the word `Error`.
