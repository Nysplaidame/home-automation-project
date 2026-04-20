# Troubleshooting Reference
# Cross-system quick-reference for the most common failure modes
# See per-system guides for deeper diagnostics
#
# Updated 2026-04-10: VLAN 30 renamed cctv→nvr, Bambuddy moved to VM 103
# (192.168.20.102, VLAN 20). P1S moved to 192.168.35.200 (VLAN 35).

---

## MQTT / VentSys

> **Port note (A10-1):** Commands in this section use port 1883 (pre-TLS only).
> After MQTT TLS migration, use port 8883 --cafile /ssl/ca.crt instead.
> See ventsys_tls_implementation_guide.md for the migration procedure.

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
mosquitto_pub -h localhost -p 1883 -u mqtt -P <password> -t test -m hello
mosquitto_sub -h localhost -p 1883 -u mqtt -P <password> -t test
```
- If both commands hang: Mosquitto add-on is not running → Settings → Add-ons → Mosquitto → Start
- If auth fails: check MQTT username/password in Settings → Devices & Services → MQTT → Configure

### VentSys device not publishing MQTT topics

```bash
# Subscribe from HA Terminal, then power-cycle the ESP device
mosquitto_sub -h localhost -p 1883 -u mqtt -P <password> -t 'ventsys/#' -v
```
- No output: check ESPHome device logs for "MQTT connected"
- Check MQTT credentials in the ESPHome YAML match the Mosquitto add-on user

### Dashboard shows `○ HA OFFLINE`

- Open browser console (F12) — look for WebSocket errors
- Confirm the Long-Lived Token in `HA_CONFIG.token` is still valid (tokens can be revoked)
- Create a new token: Settings → Profile → Security → Long-Lived Access Tokens
- Confirm HA is at `http://192.168.20.101:8123` (not HTTPS yet)

---

## Home Assistant

### HA web UI not loading

```bash
# From management laptop
ping 192.168.20.101           # is the VM reachable?
nc -zv 192.168.20.101 8123    # is port 8123 open?
```
- No ping: check Proxmox VM 100 is running, check VLAN 20 is up on the router
- Ping OK, port closed: HA is still booting (wait 2 min after VM start) or check VM console in Proxmox

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
# From frigate-nvr VM
ffprobe rtsp://admin:<password>@192.168.30.21:554/stream1
```
- Connection refused: wrong RTSP path or camera credentials — check camera manufacturer docs
- Timeout: camera unreachable — check camera power and VLAN 30 connectivity

### Frigate can't reach MQTT (HA)

```bash
# From frigate-nvr VM (192.168.30.20)
nc -zv 192.168.20.101 8883    # post-TLS; use 1883 pre-TLS
```
- Fails: check the `Frigate MQTT to HA` rule in firewall-config.conf
  (src: nvr, src_ip: 192.168.30.20, dest: automation, dest_port: 8883)
- If the rule is present but nc still fails, the router config hasn't been
  deployed yet — re-apply firewall-config.conf rather than adding ad-hoc rules.

### HA can't reach Frigate

```bash
# From HA Terminal
nc -zv 192.168.30.20 8971    # Frigate 0.14+ port; use 5000 for <0.14
```
- Fails: check `HA to NVR Access` rule — verify src_ip is 192.168.20.101
- Also check UFW on the frigate-nvr VM allows 192.168.20.0/24 → port 8971

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

---

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

---

## Bambuddy / P1S printer

> **Architecture note:** Bambuddy runs on VM 103 (192.168.20.102, VLAN 20).
> The P1S is at 192.168.35.200 (VLAN 35 — Printers, HomePrinters WiFi SSID).
> The P1S runs its own MQTT broker on port 8883 — Bambuddy connects TO the
> printer, not the other way around.

### Bambuddy container not starting

```bash
# On VM 103 (bambuddy):
cd /opt/bambuddy && docker compose logs bambuddy --tail=40
```
- Port 8000 already in use: `ss -tlnp | grep 8000`
- Volume permission error: `chown -R 1000:1000 /opt/bambuddy/`

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
# From VM 103 (bambuddy):
nc -zv 192.168.35.200 8883    # should say open
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
- Check `Bambuddy MQTT to HA` firewall rule (src: automation/20.102, dest: automation/20.101, port 8883)
- From VM 103: `nc -zv 192.168.20.101 8883` — should be open
- Check Bambuddy Settings → Network → MQTT Publishing — dot should be green

### HA API connection fails in Bambuddy (smart plug control broken)

- Check `Bambuddy to HA API` firewall rule (src: automation/20.102, dest: automation/20.101, port 8123)
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

### HA can't mount NAS backup share

```bash
# In HA Terminal
mount -t nfs 192.168.40.50:/mnt/nas/ha-backups /tmp/test-mount
```
- Permission denied: check `/etc/exports` on NAS allows `192.168.20.101`
- Timeout: `HA to Storage Access` firewall rule covers VLAN 20 → VLAN 40:2049

### Frigate can't mount NAS

Same approach from frigate-nvr VM. `Frigate to NAS Access` rule allows ports 2049 and 445.

### NAS drive failing

```bash
sudo smartctl -a /dev/sda | grep -E "PASSED|FAILED|Error"
```
Replace drive if any attribute shows `FAILING_NOW` or overall health is `FAILED`.
