---
title: Troubleshooting Reference
description: Cross-system quick diagnosis for the current deployed architecture
tags: [troubleshooting, diagnostics, recovery, architecture]
created: 2026-05-08
modified: 2026-08-25
type: reference
status: active
---

# Troubleshooting Reference

This reference follows the current architecture: HA uses native HTTPS, Frigate
runs in CT 111 with three cameras, local AI runs in CT 114, OMV is on GS1900
port 8, docker-host uses explicit Compose bridges except for the documented
Bambuddy exception, and remote Homepage cards use fixed HTTPS proxy ports.

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
> only for deliberate bootstrap exceptions while flashing or recovering devices.
> See `docs/procedures/ssl_tls_guide.md`.

### ESPHome device shows offline in HA

1. Ping the device: `ping 192.168.50.21` (from HA Terminal — should work if firewall is correct)
2. If ping fails: device lost WiFi — power cycle, check HomeIoT SSID is broadcasting
3. If ping works but ESPHome shows offline: ESPHome native API may be stuck
   ```bash
   nc -zv 192.168.50.21 6053   # should say "open"
   ```
4. If port 6053 closed: device needs a reboot or re-flash
5. Check ESPHome add-on logs: Settings → Add-ons → ESPHome → device → Logs

### MQTT broker not connecting (in HA)

```bash
# In HA Terminal
mosquitto_pub -h localhost -p 8883 --cafile /ssl/ca.crt -u mqtt -P <password> -t test -m hello
mosquitto_sub -h localhost -p 8883 --cafile /ssl/ca.crt -u mqtt -P <password> -t test
```
- If both commands hang: Mosquitto add-on is not running → Settings → Add-ons → Mosquitto → Start
- If auth fails: check MQTT username/password in Settings → Devices & Services → MQTT → Configure

### VentSys device not publishing MQTT topics

```bash
# Subscribe from HA Terminal, then power-cycle the ESP device
mosquitto_sub -h localhost -p 8883 --cafile /ssl/ca.crt -u mqtt -P <password> -t 'ventsys/#' -v
```
- No output: check ESPHome device logs for "MQTT connected"
- Check MQTT credentials in the ESPHome YAML match the Mosquitto add-on user

### Dashboard shows `○ HA OFFLINE`

- Open browser console (F12) — look for WebSocket errors
- Confirm the Long-Lived Token in `HA_CONFIG.token` is still valid (tokens can be revoked)
- Create a new token: Settings → Profile → Security → Long-Lived Access Tokens
- Confirm HA is at `https://192.168.20.101:8123`; HTTP is no longer the live UI.

---

## Home Assistant

### HA web UI not loading

```bash
# From management laptop
ping 192.168.20.101           # is the VM reachable?
nc -zv 192.168.20.101 8123    # is port 8123 open?
curl -k -I https://192.168.20.101:8123/
```
- No ping: check Proxmox VM 100 is running, check VLAN 20 is up on the router
- Ping OK, port closed: HA is still booting (wait 2 min after VM start) or check VM console in Proxmox
- Port open but browser warns about trust: install/trust the Home Local CA; do
  not switch the documented URL back to HTTP.

### HA restarting repeatedly after config change

1. Open Proxmox console (VM 100 → Console)
2. Watch for error lines — usually a YAML syntax error in a package file
3. Common: wrong indentation, missing quotes, duplicate keys
4. Fix via the console terminal or temporarily rename the broken package file:
   ```bash
   mv /config/packages/broken_file.yaml /config/packages/broken_file.yaml.bak
   ha core restart
   ```

### Entity missing after HA restart

- Check Settings → System → Logs for YAML errors
- Search for the entity in Settings → Devices & Services → Entities (include disabled)
- If from a package: confirm the package file has no syntax errors (`yamllint /config/packages/`)

### Automations not firing

1. Check Settings → Automations → select automation → Traces (shows last 10 runs and why they did/didn't trigger)
2. Check mode: if `mode: single` the automation won't re-trigger while already running
3. Check condition block — conditions silently block execution

---

## Frigate

### Camera shows grey / offline in Frigate UI

```bash
# From frigate-nvr CT
ffprobe 'rtsp://admin:<password>@192.168.30.21:554/Streaming/Channels/102'
```
- Connection refused: wrong RTSP path or camera credentials — check camera manufacturer docs
- Timeout: camera unreachable — check camera power and VLAN 30 connectivity

### Frigate can't reach MQTT (HA)

```bash
# From frigate-nvr CT (192.168.30.20)
nc -zv 192.168.20.101 8883
```
- Fails: check the `Frigate MQTT to HA` rule in firewall-config.conf
  (src: nvr, src_ip: 192.168.30.20, dest: automation, dest_port: 8883)
- If the rule is present but nc still fails, the router config hasn't been
  deployed yet — re-apply firewall-config.conf rather than adding ad-hoc rules.

### HA can't reach Frigate

```bash
# From HA Terminal
nc -zv 192.168.30.20 5000    # HA integration API
nc -zv 192.168.30.20 8971    # authenticated browser UI
```
- Fails: check `HA to NVR Access` rule — verify src_ip is 192.168.20.101
- Also check the CT firewall allows the HA source to the required API/stream
  ports. Do not expose API port `5000` through the remote Frigate host route.

### Frigate container not starting

```bash
cd /opt/frigate && docker compose logs frigate
```
- `shared memory` error: increase `shm_size` in docker-compose.yml
- `camera ... connection refused`: RTSP URL wrong or camera offline
- `MQTT connection refused`: see MQTT section above

---

## Proxmox / VMs

### VM not getting its IP

1. Check VM is started: `qm status 100`
2. Check VM console (VM → Console) — HAOS shows its IP on screen
3. Check DHCP lease: on router, `cat /tmp/dhcp.leases | grep 192.168.20`
4. If no lease: VM MAC not in DHCP reservation, or VLAN tag wrong on VM network interface
5. Check VM network: `qm config 100 | grep net0` — confirm `tag=20`

### Proxmox web UI not accessible after reboot

```bash
ip addr show    # confirm vmbr0.10 has 192.168.10.10
ping 192.168.10.1    # router reachable?
systemctl status pveproxy
systemctl restart pveproxy
```

### VM not starting at boot

```bash
qm config 100 | grep -E "onboot|startup"
# Should show: onboot: 1 and startup: order=N
# If missing:
qm set 100 --onboot 1
qm set 100 --startup order=1
```

---

## Router / Network

### Can't reach router web UI after VLAN change

- Connect directly to lan2 with a laptop — VLAN 10 untagged. Should get 192.168.10.x.
- If not: the PVID on lan2 may not be set to VLAN 10 (`u*` vs `u` bug)
- Emergency: serial console (GL-MT6000 has a UART header) or hardware reset button

### Device on wrong VLAN

1. Check `bridge vlan show` on the router
2. Check MAC against DHCP leases to identify which VLAN it landed on
3. Verify the physical port assignment in `vlan-config.conf`

### Two devices have the same IP

```bash
cat /tmp/dhcp.leases
uci show dhcp | grep "\.ip="
```
Ensure static reservations use IPs outside the dynamic ranges (statics are below .100).

### DNS not resolving local hostnames

```bash
nslookup homeassistant.home.local 127.0.0.1
```
- Fails: check dhcp-config.conf has the domain entries and dnsmasq is running
- `local '/home.local/'` must be in the dnsmasq config block

### AdGuard filtering not working

```bash
# From a management client
nslookup example.com 192.168.10.1

# From router
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

```bash
tailscale status
ping 192.168.20.101
curl -k -I https://192.168.20.101:8123
```

- Confirm docker-host is online in the tailnet.
- Confirm `192.168.20.101/32` is advertised and approved.
- Confirm Tailscale ACLs allow the client to reach HA on 8123.

This direct host route is an admin path. The approved OnePlus daily portal
identity normally opens `https://homepage.home.local/` and its fixed proxy
ports rather than browsing routed private addresses.

### Tailscale client cannot reach OMV

```bash
ping 192.168.40.50
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

```bash
ping 192.168.60.10
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

DNS issue. Client config sets `DNS = 192.168.1.1`. Temporarily switch to
`DNS = 1.1.1.1` to confirm it's a DNS routing issue.

### VPN fallback cannot reach OMV

1. Confirm `AllowedIPs` includes `192.168.40.50/32`, not `192.168.40.0/24`.
2. Confirm `VPN to OMV NAS` exists before `Block VPN to Storage`.
3. Test only the required OMV ports: 80/443 for UI, 445 for SMB, 2049 for NFS, 22 for admin.

---

## Docker-host Compose Services

### Compose stack will not start

```bash
cd /opt/stacks/<service>
docker compose config
docker compose logs --tail=80
```

- Invalid config: fix the Compose or `.env` file.
- Port already in use: `ss -tlnp | grep <port>`.
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

```bash
cd /opt/stacks/homepage
docker compose ps
ss -tlnp | grep -E ':443|:3001|:81[89][0-9]|:820[0-9]'
nginx -t
```

- Confirm `homepage.home.local` resolves to `192.168.20.102`.
- Use `https://homepage.home.local/` as the normal local and remote bookmark;
  `http://192.168.20.102:3001/` is the rollback path.
- Check config syntax in `/opt/stacks/homepage/config/`.
- If only previews fail, validate the fixed-target proxy sidecar, its source-
  scoped UFW rules and the exact `8180-8209` mapping in `services.yaml`.

## Dozzle

### Dozzle shows no containers or is unreachable

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
> The P1S is at 192.168.35.200 (VLAN 35 — Printers, HomePrinters WiFi SSID).
> The P1S runs its own MQTT broker on port 8883 — Bambuddy connects TO the
> printer, not the other way around.
> Bambuddy currently remains on host networking. Its explicit
> `10.240.23.0/24` bridge and routed UFW rules are prepared, but migration is
> blocked until VM 103 itself can reach P1S ports `21` and `8883`.

### Bambuddy container not starting

```bash
# On VM 103 (docker-host):
cd /opt/stacks/bambuddy && docker compose logs bambuddy --tail=40
```
- Port 8000 already in use: `ss -tlnp | grep 8000`
- Volume permission error: `chown -R 1000:1000 /opt/stacks/bambuddy/`

### Bambuddy UI unreachable (http://192.168.20.102:8000)

```bash
# On VM 103:
docker ps | grep bambuddy
ss -tlnp | grep 8000
```
- Container not running: `docker compose up -d bambuddy`
- Port not bound but container up: check logs

### P1S shows "Connection Failed" in Bambuddy

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
- Single client limit: the P1S only supports one simultaneous local MQTT client.
  If Bambu Studio is open and connected, close it — Bambuddy cannot connect while
  another client is already holding the connection.

### Bambuddy MQTT not publishing to HA

```bash
# From HA Terminal:
mosquitto_sub -h localhost -p 8883 --cafile /ssl/ca.crt \
    -u mqtt -P <password> -t 'bambuddy/#' -v
# Start/stop a print — if no messages arrive, problem is Bambuddy → Mosquitto
```
- VLAN 20 is the HA+Docker host trust boundary; this path is not router-firewall enforced.
- From VM 103: `nc -zv 192.168.20.101 8883` — should be open
- Check Bambuddy Settings → Network → MQTT Publishing — dot should be green

### HA API connection fails in Bambuddy (smart plug control broken)

- VLAN 20 is the HA+Docker host trust boundary; this path is not router-firewall enforced.
- From VM 103: `nc -zv 192.168.20.101 8123` — should be open
- Regenerate Long-Lived Token: HA → Settings → Profile → Long-Lived Access Tokens → save in Bitwarden

### P1S HA entities unavailable after package deploy

- Confirm serial number placeholder replaced:
  `grep '<P1S_SERIAL>' /config/packages/bambuddy_p1s_package.yaml` → should return nothing
- Check MQTT topics arriving: `mosquitto_sub -t 'bambuddy/printers/+/status' -v`
- Check HA logs: Settings → System → Logs, filter for "mqtt"

### P1S not getting IP on HomePrinters SSID

- Confirm HomePrinters SSID is broadcasting (check wireless-config.conf is deployed)
- Confirm P1S is set to LAN mode: printer touchscreen Settings → Network
- Check DHCP lease for 192.168.35.200 on the router: `cat /tmp/dhcp.leases | grep 192.168.35`
- If P1S got a dynamic .100+ IP instead of .200: MAC not yet in dhcp-config.conf reservation

## OMV NAS

### HA can't mount NAS backup share

```bash
# In HA Terminal
mount -t nfs 192.168.40.50:/export/ha-backups /tmp/test-mount
```
- Permission denied: check the OMV NFS export allows `192.168.20.101`
- Timeout: `HA to Storage Access` firewall rule covers VLAN 20 → VLAN 40:2049

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

```bash
sudo smartctl -a /dev/sda | grep -E "PASSED|FAILED|Error"
```
Replace drive if any attribute shows `FAILING_NOW` or overall health is `FAILED`.
