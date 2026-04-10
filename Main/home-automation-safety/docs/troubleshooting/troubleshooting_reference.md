# Troubleshooting Reference
# Cross-system quick-reference for the most common failure modes
# See per-system guides for deeper diagnostics

---

## MQTT / VentSys


> **Port note (A10-1):** Commands in this section use port 1883 (pre-TLS only).
> After MQTT TLS migration, use port 8883 --cafile /ssl/ca.crt instead.
> See entsys_tls_implementation_guide.md for the migration procedure.

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
# Test the RTSP stream directly
ffprobe rtsp://admin:<password>@192.168.30.21:554/stream1
```
- Connection refused: wrong RTSP path or camera credentials — check camera manufacturer docs
- Timeout: camera unreachable — check camera power and VLAN 30 connectivity

### Frigate can't reach MQTT (HA)

```bash
# From frigate-nvr VM
nc -zv 192.168.20.101 8883    # A6-6: post-TLS; use 1883 pre-TLS
```
- Fails: check the `Frigate MQTT to HA` firewall rule in `configs/openwrt/firewall-config.conf`.
- FIX #19: The original troubleshooting note here said "add if missing" and included
  manual `uci` commands to create the rule. That rule already exists in
  firewall-config.conf as a permanent entry (src: cctv, src_ip: 192.168.30.20,
  dest: automation, dest_port: 8883)  # A6-6: firewall uses 8883. Bambuddy runs with `network_mode: host`
  on the same VM (192.168.30.20), so the same rule covers Bambuddy's MQTT
  publishing too — no separate rule is needed. If `nc` fails, the router config
  hasn't been deployed yet, or was deployed without this rule. Re-apply the full
  firewall-config.conf via the router setup guide rather than adding ad-hoc rules.

### HA can't reach Frigate

```bash
# From HA Terminal
nc -zv 192.168.30.20 8971    # A6-6: Frigate 0.14+ uses port 8971; use 5000 for Frigate 0.13
```
- Fails: firewall rule `HA to CCTV Access` — verify src_ip is `192.168.20.101`
- Also check UFW on the frigate-nvr VM allows VLAN 20 -> port 8971 (Frigate 0.14+) or port 5000 (Frigate <0.14)  # A9-4 fix

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
# Connect monitor and keyboard to MINIX, or use console access
ip addr show    # confirm vmbr0.10 has 192.168.10.10
ping 192.168.10.1    # router reachable?
systemctl status pveproxy    # is web UI service running?
systemctl restart pveproxy
```

### VM 100 or 101 not starting at boot

```bash
# Check onboot and startup settings
qm config 100 | grep -E "onboot|startup"
# Should show: onboot: 1 and startup: order=1

# If missing, set it:
qm set 100 --onboot 1
qm set 100 --startup order=1
```

---

## Router / Network

### Can't reach router web UI after VLAN change

- Connect directly to lan2 with a laptop — VLAN 10 untagged. Your laptop should get 192.168.10.x.
- If not: the PVID on lan2 may not be set to VLAN 10 (`u*` vs `u` bug — see router_setup_complete.md fix #2)
- Emergency: connect via serial console (GL-MT6000 has a UART header) or reset with the hardware button

### Device on wrong VLAN

1. Check `bridge vlan show` on the router — which VLAN is the port PVID?
2. Check the device's MAC against DHCP leases to identify which VLAN it landed on
3. Verify the physical port assignment in `vlan-config.conf`

### Two devices have the same IP

Usually a DHCP static reservation conflict with the dynamic range.

```bash
# On router — check leases
cat /tmp/dhcp.leases

# Check static reservations
uci show dhcp | grep "\.ip="
```
Ensure static reservations use IPs outside the dynamic ranges (static IPs are below .100 for most VLANs).

### DNS not resolving local hostnames

```bash
# On router
nslookup homeassistant.home.local 127.0.0.1
```
- Fails: check `configs/openwrt/dhcp-config.conf` has the domain entries, and dnsmasq is running
- `local '/home.local/'` must be in the dnsmasq config block

---

## WireGuard VPN

### VPN won't connect

1. Confirm port 51820 UDP is reachable from outside: use an online UDP port checker
2. Confirm WireGuard is listening: on router, `netstat -ulnp | grep 51820`
3. Check the client config `Endpoint` IP matches current WAN IP (may have changed — use DDNS)
4. Check client timestamp: if clock is very wrong, handshake fails — VPN is time-sensitive

### VPN connects but can't reach HA

1. Confirm `AllowedIPs` in client config includes `192.168.20.101/32`
2. Confirm firewall rule `VPN to Home Assistant` exists: `uci show firewall | grep "VPN to Home Assistant"`
3. Check VPN client IP is in 10.0.0.0/24 range — wrong IP = no firewall match

### VPN connects but all traffic is broken

Usually a DNS issue. The client config sets `DNS = 192.168.1.1` (the main LAN gateway,
reachable via the VPN tunnel's AllowedIPs). If DNS is still broken, temporarily switch
to `DNS = 1.1.1.1` to confirm it's a DNS routing issue rather than something else.

---

## Bambuddy / P1S printer

### Bambuddy container not starting

```bash
cd /opt/frigate && docker compose logs bambuddy --tail=40
```
- Port 8000 already in use: check no other service is on 8000 (`ss -tlnp | grep 8000`)
- Volume permission error: `chown -R 1000:1000 /opt/frigate/bambuddy/`

### Bambuddy UI unreachable (http://192.168.30.20:8000)

```bash
docker ps | grep bambuddy      # is the container running?
ss -tlnp | grep 8000           # is the port bound?
```
- Container not running: `docker compose up -d bambuddy`
- Port not bound but container up: container crashed on startup, check logs

### P1S shows "Connection Failed" in Bambuddy

```bash
# From Frigate VM:
nc -zv 192.168.1.200 8883    # should say open
ping 192.168.1.200           # basic reachability
```
- Firewall rule missing: check 'Bambuddy to P1S' rule on router
- P1S not at 192.168.1.200: check DHCP lease table on router
- Developer Mode not enabled on printer: re-enable via touchscreen Settings > Network
- Wrong Access Code: regenerate via Settings > Network > Developer Mode on printer

### Bambuddy MQTT not publishing to HA

```bash
# From HA Terminal:
mosquitto_sub -h localhost -p 8883 --cafile /ssl/ca.crt -u mqtt -P <password> -t 'bambuddy/#' -v  # A6-6: post-TLS
# Start/stop printer — if no messages: problem is Bambuddy -> Mosquitto
```
- Check 'Bambuddy MQTT to HA' firewall rule on router
- From Frigate VM: `nc -zv 192.168.20.101 8883` -- should be open (post-TLS)  # A6-6
- Check Bambuddy Settings > Network > MQTT Publishing — dot should be green

### HA API connection fails in Bambuddy (smart plug control broken)

- Check 'Bambuddy to HA API' firewall rule on router
- From Frigate VM: `nc -zv 192.168.20.101 8123` — should be open
- Regenerate Long-Lived Token in HA > Profile > Long-Lived Access Tokens

### P1S HA entities unavailable after package deploy

- Confirm serial number placeholder replaced: grep `<P1S_SERIAL>` /config/packages/bambuddy_p1s_package.yaml (should return nothing)
- Check MQTT topics are arriving: `mosquitto_sub -t 'bambuddy/printers/+/status' -v`
- Check HA logs: Settings > System > Logs — filter for "mqtt"

### HA can't mount NAS backup share

```bash
# In HA Terminal
mount -t nfs 192.168.40.50:/mnt/nas/ha-backups /tmp/test-mount
```
- Permission denied: check `/etc/exports` on NAS allows `192.168.20.101`
- Timeout: check firewall allows VLAN 20 → VLAN 40:2049 (the `HA to Storage Access` rule covers this)

### Frigate can't mount NAS

Same approach from frigate-nvr VM. The `Frigate to NAS Access` firewall rule allows ports 2049 and 445.

### NAS drive failing

```bash
sudo smartctl -a /dev/sda | grep -E "PASSED|FAILED|Error"
```
Replace the drive if any attributes show `FAILING_NOW` or if the overall health is `FAILED`.
Restore from Proxmox VM backup — NAS data is backed up via HA backups and config rsync.
