# Bambuddy + P1S Setup Guide
# Bambu Lab P1S — local network integration via Bambuddy
# Bambuddy host: Frigate VM (192.168.30.20, VLAN 30)
# P1S network: VLAN 1 (LAN) — 192.168.1.200 (static)
# HA integration: MQTT publish to Mosquitto on 192.168.20.101
# Bambuddy repo: https://github.com/maziggy/bambuddy

---

## Architecture overview

```
P1S Printer (192.168.1.200, VLAN 1)
    MQTT TLS :8883  +  explicit FTPS :21
         |
Bambuddy (192.168.30.20:8000, VLAN 30 - Frigate VM)
    MQTT publish :8883  +  REST API :8123  # A6-5 fix: was :1883; docker-compose.yml MQTT_PORT=8883, firewall rule uses 8883
         |
Home Assistant (192.168.20.101, VLAN 20)
    sensors, automations, VentSys triggers
         |
VentSys FDM mode auto-activates when P1S starts printing
```

Bambuddy translates Bambu Lab proprietary MQTT into clean JSON events
published to your existing Mosquitto broker on HA.

---

## Phase 1 - Printer preparation

### 1.1 Enable Developer Mode on the P1S

On the printer touchscreen:
1. Settings > Network > LAN Only Mode > Enable
2. Settings > Network > Developer Mode > Enable (appears after LAN Mode)
3. Note the Access Code (you will enter this in Bambuddy)
4. About This Machine > note the Serial Number (format: 01P09C41xxxxxxx)

LAN Only Mode disables Bambu Cloud sync. You keep full local control.
You can still use Bambu Studio / OrcaSlicer directly to the printer.

### 1.2 Enable "Store sent files on external storage"

In Bambu Studio or OrcaSlicer, on the Device tab for your printer:
Print Options > Store Sent Files on External Storage > Enable

Bambuddy needs 3MF files on the SD card for thumbnails and model previews.

### 1.3 Set the P1S to a static IP

Find the P1S MAC address from the router DHCP table after it connects:

```bash
cat /tmp/dhcp.leases | grep -i bambu
```

Update configs/openwrt/dhcp-config.conf - the reservation is templated:
```
config host
    option name 'bambu-p1s'
    option dns '1'
    option mac 'XX:XX:XX:XX:XX:XX'   # replace with P1S MAC
    option ip '192.168.1.200'
```

Apply config, then reboot printer so it picks up 192.168.1.200.

---

## Phase 2 - Firewall rules

> **FIX #32:** A previous version of this guide reproduced the three firewall
> rules verbatim as `uci` commands to run here. That created two sources of
> truth that drift independently. The rules are now maintained exclusively in
> `configs/openwrt/firewall-config.conf` (the Bambuddy section, labelled
> `── BAMBUDDY (P1S PRINTER INTEGRATION) ──`). Running the full firewall
> config script is the only supported way to apply them.

Three rules in `configs/openwrt/firewall-config.conf` must be deployed before
Bambuddy can reach the printer or publish to HA:

| Rule name | From | To | Ports | Purpose |
|---|---|---|---|---|
| `Bambuddy to P1S` | VLAN 30 (192.168.30.20) | VLAN 1 (192.168.1.200) | 8883, 21 | Printer MQTT + explicit FTPS |
| `Bambuddy MQTT to HA` | VLAN 30 (192.168.30.20) | VLAN 20 (192.168.20.101) | 8883 | Publish events to Mosquitto (TLS)  # A6-5 fix: was 1883; firewall-config.conf and docker-compose both use 8883 |
| `Bambuddy to HA API` | VLAN 30 (192.168.30.20) | VLAN 20 (192.168.20.101) | 8123 | Smart plug + token control |

If the router config is already deployed, apply only the Bambuddy section:

```bash
# On the router shell — paste the three Bambuddy uci blocks from
# firewall-config.conf (search for "BAMBUDDY") then:
uci commit firewall && /etc/init.d/firewall restart
```

Verify from Frigate VM after applying:
```bash
nc -zv 192.168.1.200 8883     # P1S MQTT
nc -zv 192.168.20.101 8883    # Mosquitto TLS  # A6-5 fix: was 1883
nc -zv 192.168.20.101 8123    # HA API
```
## Phase 3 - Deploy Bambuddy on the Frigate VM

Bambuddy runs as a second container on the Frigate VM alongside Frigate NVR.
The updated configs/frigate/docker-compose.yml includes both services.

### 3.1 Copy updated docker-compose to VM

```bash
scp configs/frigate/docker-compose.yml admin@192.168.30.20:/opt/frigate/docker-compose.yml
```

### 3.2 Create data directories

```bash
ssh admin@192.168.30.20
# FIX: correct dirs are data/ and logs/ (not db/ archive/ — see docker-compose.yml FIX #4)
mkdir -p /opt/frigate/bambuddy/{data,logs}
```

### 3.3 Start Bambuddy

```bash
cd /opt/frigate
docker compose pull bambuddy
docker compose up -d bambuddy
docker compose logs bambuddy --tail=30
```

Bambuddy UI: http://192.168.30.20:8000

---

## Phase 4 - Add P1S to Bambuddy

Bambuddy UI > Printers > Add Printer

| Field | Value |
|---|---|
| IP Address | 192.168.1.200 |
| Serial Number | 01P09C41xxxxxxx |
| Access Code | from Developer Mode screen |
| Model | P1S |

Click Test Connection - should be green. Save.

SSDP auto-discovery does not work across VLANs. Always add by IP manually.

Printer card should show green dot, temperatures, and live camera stream.

---

## Phase 5 - Bambuddy MQTT publishing to Mosquitto

Bambuddy > Settings > Network > MQTT Publishing

| Setting | Value |
|---|---|
| Enable MQTT | On |
| Broker Hostname | 192.168.20.101 |
| Port | 8883 |  # A6-5 fix: was 1883; docker-compose MQTT_PORT=8883
| Username | mqtt |
| Password | your Mosquitto password |
| Topic Prefix | bambuddy |
| Use TLS | Off |

Save. Dot turns green.

Test from HA Terminal:
```bash
mosquitto_sub -h localhost -p 8883 --cafile /ssl/ca.crt -u mqtt -P <password> -t 'bambuddy/#' -v  # A6-5 fix: was -p 1883; system uses TLS on 8883
```

Jog the printer head or start a print - JSON payloads appear.

---

## Phase 6 - Bambuddy to HA connection

### 6.1 Create a Long-Lived Token in HA

HA > Profile > Long-Lived Access Tokens > Create Token
Name: Bambuddy
Copy immediately.

### 6.2 Configure in Bambuddy

Bambuddy > Settings > Network > Home Assistant

| Setting | Value |
|---|---|
| HA URL | http://192.168.20.101:8123 |
| Long-Lived Token | (paste token) |

Test Connection > green. Enable toggle.

### 6.3 Add printer power smart plug

Bambuddy > Settings > Smart Plugs > Add Smart Plug > Home Assistant tab

| Field | Value |
|---|---|
| Name | P1S Power |
| Entity | switch.fdm_printer_plug |
| Printer | Bambu P1S |

Enable Auto Power Off > Cooldown Temperature: 40C.

Add energy sensors if your plug exposes them (power W, energy kWh).

### 6.4 Link VentSys to print start/stop via HA automations

> FIX #25: A previous version of this guide described adding VentSys scripts as
> "Smart Plug" entries in Bambuddy. Bambuddy smart plug triggers fire on PLUG
> SWITCH state change, not on print state change -- so this would fire when the
> plug is toggled for power control, not when a print starts or finishes.
>
> The correct approach is HA automations responding to binary_sensor.p1s_printing
> directly. These automations live in configs/home-assistant/automations.yaml
> (NOT in bambuddy_p1s_package.yaml — the package handles notifications and
> failed-print purge only).

The following automations must be present in `/config/automations.yaml` on the HA VM:

- `p1s_ventsys_fdm_start` — triggers when `binary_sensor.p1s_printing` turns ON
  → calls `script.ventsys_mode_fdm_print` → FDM ventilation mode activates

- `p1s_ventsys_fdm_stop` — triggers when `binary_sensor.p1s_printing` turns OFF
  → calls `script.ventsys_mode_fdm_purge` → post-print fume clearance runs

These are included in `configs/home-assistant/automations.yaml` in the vault.
The bambuddy_p1s_package.yaml package handles notifications and print/failed purge
separately — both files must be deployed for complete integration.

Verify automations fired:
Settings → Automations → p1s_ventsys_fdm_start / p1s_ventsys_fdm_stop → Traces

---

## Phase 7 - HA package deployment

The file configs/home-assistant/bambuddy_p1s_package.yaml must be copied
to /config/packages/ on the HA VM.

Before copying: replace all instances of <P1S_SERIAL> with your actual
serial number (e.g. 01P09C411500579).

```bash
# In HA File Editor: create /config/packages/bambuddy_p1s_package.yaml
# Paste the contents, save, then restart HA:
Settings > System > Restart
```

After restart these entities appear:
- sensor.p1s_print_progress (percent)
- sensor.p1s_state (IDLE / PRINTING / FAILED)
- sensor.p1s_bed_temperature
- sensor.p1s_nozzle_temperature
- sensor.p1s_chamber_temperature
- sensor.p1s_layer (current / total)
- sensor.p1s_remaining_time (minutes)
- sensor.p1s_current_print (filename)
- binary_sensor.p1s_printing

---

## Phase 8 - Dashboard card

Add Bambuddy as an iframe in HA dashboard:
Settings > Dashboards > Edit > Add Card > Webpage
URL: http://192.168.30.20:8000
Title: Bambuddy P1S

---

## Phase 9 - Notifications

Bambuddy native (recommended for print events):
Settings > Notifications > add Telegram/Discord/email
Enable: Print Completed, Print Failed, HMS Errors, Bed Cooled

HA automations in bambuddy_p1s_package.yaml fire on:
- print/completed -> HA notification + log
- print/failed -> urgent HA notification + VentSys purge

---

## Completion checklist

- [ ] Developer Mode on P1S - Access Code and Serial noted
- [ ] Store sent files enabled in slicer
- [ ] P1S MAC noted, dhcp-config.conf updated, 192.168.1.200 confirmed
- [ ] Three firewall rules applied on router
- [ ] nc checks pass: 192.168.1.200:8883 (P1S MQTT) and 192.168.20.101:8883 (Mosquitto TLS) open  # A6-5 fix: was :1883 for Mosquitto
- [ ] /opt/frigate/docker-compose.yml updated on Frigate VM
- [ ] Bambuddy data dirs created: /opt/frigate/bambuddy/{data,logs}
- [ ] Bambuddy container up: docker compose up -d bambuddy
- [ ] Bambuddy UI accessible at http://192.168.30.20:8000
- [ ] P1S added to Bambuddy, connection test green
- [ ] Printer card shows temperatures and camera
- [ ] MQTT publishing configured, mosquitto_sub shows events
- [ ] HA API connection configured, test green
- [ ] Smart plug added (switch.fdm_printer_plug)
- [ ] VentSys FDM scripts linked as on/off triggers
- [ ] bambuddy_p1s_package.yaml serial updated, deployed to /config/packages/
- [ ] HA entities visible: p1s_state, p1s_print_progress, temperatures
- [ ] Dashboard iframe card added
- [ ] Notifications configured

---

## Quick reference

| Item | Value |
|---|---|
| P1S IP | 192.168.1.200 (VLAN 1) |
| Bambuddy UI | http://192.168.30.20:8000 |
| Bambuddy data | /opt/frigate/bambuddy/ |
| MQTT status topic | bambuddy/printers/<serial>/status |
| HA Token name | Bambuddy |
| VentSys FDM on | script.ventsys_mode_fdm_print |
| VentSys FDM purge | script.ventsys_mode_fdm_purge |
| P1S MQTT port | 8883 (TLS, Bambuddy handles natively) |
| P1S FTP ports | 21 (explicit FTPS — port 990 removed per FIX #34) |
| Firewall rule 1 | Bambuddy to P1S (cctv to lan:192.168.1.200) |
| Firewall rule 2 | Bambuddy MQTT to HA (cctv to automation:8883  # A6-5 fix: was 1883) |
| Firewall rule 3 | Bambuddy to HA API (cctv to automation:8123) |
