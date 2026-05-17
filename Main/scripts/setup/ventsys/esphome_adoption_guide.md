# ESPHome Device Adoption Guide
# FIX #23: A reference to update_ventsys_mac.sh was here. That script does not exist in the vault.

> **L-9 audit note — Board identification safeguard:** Before flashing any board,
> verify you have the correct YAML for the correct physical board using the table below.
> Flashing the wrong firmware installs the wrong device name, wrong MQTT topics, and wrong
> GPIO pin assignments. Recovery requires a full USB re-flash.
>
> # A5-2 fix: Entire IP column was wrong (13 of 16 entries). Previous table used
> # a pre-canonical allocation scheme. All IPs now match dhcp-config.conf.
> # Also: sensor boards now have per-device YAMLs (A4-4); UV plug names updated (A4-5).
> | Board label | YAML file | Expected device_name | IP reservation |
> |---|---|---|---|
> | Main fan controller | ventsys_fan_controller.yaml | ventsys-main-fan | 192.168.50.21 |
> | Booth fan controller | ventsys_booth_fan.yaml | ventsys-booth-fan | 192.168.50.22 |
> | FDM sensor board | ventsys_fdm_sensor.yaml | ventsys-fdm-sensor | 192.168.50.31 |
> | SLA sensor board | ventsys_sla_sensor.yaml | ventsys-sla-sensor | 192.168.50.32 |
> | Booth sensor board | ventsys_booth_sensor.yaml | ventsys-booth-sensor | 192.168.50.33 |
> | Garage sensor | ventsys_garage_sensor.yaml | ventsys-garage-sensor | 192.168.50.34 |
> | FDM airflow sensor | ventsys_fdm_airflow.yaml | ventsys-fdm-airflow | 192.168.50.41 |
> | SLA airflow sensor | ventsys_sla_airflow.yaml | ventsys-sla-airflow | 192.168.50.42 |
> | Booth airflow sensor | ventsys_booth_airflow.yaml | ventsys-booth-airflow | 192.168.50.43 |
> | Main duct valve 1 | ventsys_main_valve1.yaml | ventsys-main-valve-1 | 192.168.50.51 |
> | Main duct valve 2 | ventsys_main_valve2.yaml | ventsys-main-valve-2 | 192.168.50.52 |
> | FDM branch valve | ventsys_fdm_branch_valve.yaml | ventsys-fdm-branch-valve | 192.168.50.53 |
> | SLA branch valve | ventsys_sla_branch_valve.yaml | ventsys-sla-branch-valve | 192.168.50.54 |
> | FDM print valve | ventsys_fdm_print_valve.yaml | ventsys-fdm-print-valve | 192.168.50.55 |
> | SLA print valve | ventsys_sla_print_valve.yaml | ventsys-sla-print-valve | 192.168.50.56 |
> | FDM 360 intake valve | ventsys_fdm_360_valve.yaml | ventsys-fdm-360-valve | 192.168.50.61 |
> | SLA 360 intake valve | ventsys_sla_360_valve.yaml | ventsys-sla-360-valve | 192.168.50.62 |
> | UV station 1 plug | ventsys_plug_uv1.yaml | ventsys-plug-uv-1 | 192.168.50.73 |
> | UV station 2 plug | ventsys_plug_uv2.yaml | ventsys-plug-uv-2 | 192.168.50.74 |
> | Wash/cure plug | ventsys_plug_wash_cure.yaml | ventsys-plug-wash-cure | 192.168.50.75 |
> | Ultrasonic plug | ventsys_plug_ultrasonic.yaml | ventsys-plug-ultrasonic | 192.168.50.76 |
>
> **Before each flash:** confirm the connected board's label, then run
> `esphome config <yaml>` to verify `device_name` matches the table above before flashing.
# Network: VLAN 50 (IoT Sensors) — 192.168.50.0/24
# WiFi SSID: HomeIoT
# Managed via: ESPHome add-on on HA (192.168.20.101)
#
# Covers: All VentSys ESPHome boards — fan controllers, valve controllers,
#         and sensor arrays (FDM, SLA, booth, garage)
# Canonical IP allocations: configs/openwrt/dhcp-config.conf
# ESPHome configs: ventsys/ventsys_bundle_updated/ and configs/esphome/

---

## Overview

ESPHome devices go through three stages:
1. **First flash** — USB serial (one-time, before the device has WiFi)
2. **Adoption** — HA discovers the device and it appears in ESPHome add-on
3. **OTA updates** — all future flashes happen over WiFi from the ESPHome add-on

---

## Before you start — secrets.yaml

ESPHome reads credentials from a `secrets.yaml` file in the same folder as
the YAML config. Create this file before flashing anything.
See `docs/secrets_reference.md` Section 4 for the full template.
Minimum required for direct-TLS flashing:

```yaml
# secrets.yaml — DO NOT COMMIT TO GITHUB
wifi_ssid: "HomeIoT"
wifi_pass: "your-homeiot-password"    # Bitwarden: wifi-homeiot
mqtt_user: "mqtt"
mqtt_pass: "your-mqtt-password"       # Bitwarden: mqtt-credentials
mqtt_ca_cert: |-
  -----BEGIN CERTIFICATE-----
  ...
  -----END CERTIFICATE-----
api_key: "your-32-byte-base64-key"    # openssl rand -base64 32
ota_password: "your-ota-password"
```

Place `secrets.yaml` in both:
- `ventsys/ventsys_bundle_updated/` (fan and valve controllers)
- `configs/esphome/` (sensor arrays and garage sensor)

---

## Phase 1 — First flash via USB

### 1.1 — Install ESPHome on your laptop

> **FIX #33:** `pip install esphome` on Windows has known path-length and
> venv issues that cause silent failures. Preferred options:

**Option A — pipx (recommended)**
```powershell
winget install python.python.3    # if Python not already installed
pip install pipx
pipx install esphome
esphome version
```

**Option B — WSL (cleanest on Windows)**
```bash
pip3 install esphome
esphome version
```

**Option C — pip directly**
```powershell
pip install esphome
# If "esphome is not recognised": python -m esphome
```

### 1.2 — Flash fan and valve controllers

Config files: `ventsys/ventsys_bundle_updated/`

Use the pre-TLS variants for stage-1 (before TLS migration):
- `ventsys_fan_controller_pretls.yaml`   → target IP 192.168.50.21
- `../configs/esphome/ventsys_sla_print_valve.yaml` (canonical) → target IP 192.168.50.56

```bash
cd "\\VBoxSvr\home-automation-safety\ventsys\ventsys_bundle_updated"

esphome run ventsys_fan_controller_pretls.yaml
# swap USB to the valve board, then:
esphome run ../../../configs/esphome/ventsys_sla_print_valve.yaml
```

If the COM port isn't detected automatically:
```bash
# Windows — check Device Manager for the COM port number
esphome run ventsys_fan_controller_pretls.yaml --device COM3
# Linux/WSL
esphome run ventsys_fan_controller_pretls.yaml --device /dev/ttyUSB0
```

Watch for in the serial output:
```
WiFi connected! IP: 192.168.50.21
MQTT connected
```

### 1.3 — Flash sensor arrays (FDM, SLA, booth)

Config files: `configs/esphome/`
Use: `printairpipe-controller_pretls.yaml`
Targets: 192.168.50.31 (FDM) / 192.168.50.32 (SLA) / 192.168.50.33 (booth)

Each board needs its own IP and hostname. Set the substitution variables at the
top of the config before flashing each board:

```yaml
# printairpipe-controller_pretls.yaml — edit these per board before flashing:
substitutions:
  device_name: "ventsys-fdm-sensor"     # ventsys-fdm-sensor / ventsys-sla-sensor / ventsys-booth-sensor
  device_ip: "192.168.50.31"            # .31 FDM  /  .32 SLA  /  .33 booth
  device_description: "FDM sensor array"
```

Flash each board one at a time:
```bash
cd "\\VBoxSvr\home-automation-safety\configs\esphome"

# Set substitutions for FDM (.31), flash, then repeat for SLA (.32) and booth (.33)
esphome run printairpipe-controller_pretls.yaml
```

### 1.4 — Flash garage ambient sensor

Config: `configs/esphome/ventsys_garage_sensor_pretls.yaml`
Target IP: 192.168.50.34

```bash
cd "\\VBoxSvr\home-automation-safety\configs\esphome"
esphome run ventsys_garage_sensor_pretls.yaml
```

### 1.5 — Find the DS18B20 one-wire address (sensor boards only)

The DS18B20 address in `printairpipe-controller.yaml` is a placeholder
(`0x0000000000000000`) — it must be replaced with the real address of the
physical sensor soldered to each board. After first flash, read it from logs:

```bash
esphome logs printairpipe-controller_pretls.yaml
# Look for:
# Found 1 sensors on the 1-Wire bus.
# Sensor address: 0x28FF6D5A92180342
```

Or from the ESPHome add-on after adoption: open the device → Logs on first boot.

Once you have the address for each board, update the production config:
- Open `configs/esphome/printairpipe-controller.yaml`
- Replace `0x0000000000000000` with the real address for that board
- Each board has a different address — update separately per device

### 1.6 — Verify BME680 I2C address

BME680 defaults to I2C address `0x76`. If the SDO pin is soldered high it will
be `0x77`. The ESPHome log shows which was found:

```
[I2C] Found device at 0x76
```

If your board shows `0x77`, update the `address:` field in the YAML config
before flashing the production (non-pretls) version.

---

## Phase 2 — Adoption in Home Assistant

### 2.1 — Verify devices are reachable

From HA Terminal add-on (HA on VLAN 20; firewall allows HA → VLAN 50):

```bash
# ESPHome native API port 6053
nc -zv 192.168.50.21 6053   # fan controller
nc -zv 192.168.50.56 6053   # valve controller
nc -zv 192.168.50.31 6053   # FDM sensor
nc -zv 192.168.50.32 6053   # SLA sensor
nc -zv 192.168.50.33 6053   # booth sensor
nc -zv 192.168.50.34 6053   # garage sensor
```

If any fail: confirm the device got its static IP (`ping 192.168.50.xx` from
router), check `ESPHome API HA to IoT` firewall rule, verify DHCP reservation
MAC in `configs/openwrt/dhcp-config.conf`.

### 2.2 — Note each device MAC address

After first flash, MAC addresses are needed for DHCP static reservations.
Get them from the router DHCP leases table, or from serial output during
flash (look for `WiFi connected! MAC: XX:XX:XX:XX:XX:XX`).

Update each placeholder in `configs/openwrt/dhcp-config.conf`:
```
config host
    option name 'ventsys-fdm-sensor'
    option mac 'XX:XX:XX:XX:XX:XX'    <- replace with real MAC
    option ip '192.168.50.31'
```

Re-apply DHCP config to router (`scripts/setup/router/phase_3_dhcp_configuration.md`) and
power-cycle each device so it picks up its static reservation.

### 2.3 — Adopt in ESPHome add-on

Settings → Add-ons → ESPHome → Open Web UI.

Devices appear with a **"Discovered"** badge. Click **Adopt** on each.
ESPHome prompts for the encryption key (from `api_key` in secrets.yaml).
After adoption each device shows its IP, firmware version, and online status.

### 2.4 — Accept in HA Integrations

`Settings → Devices & Services → Notifications`

A new ESPHome device notification appears for each board. Click **Configure**
and accept. This creates entities for all declared components.

---

## Phase 3 — Verify MQTT topics

From HA Terminal:
```bash
mosquitto_sub -h localhost -p 1883 \
    -u mqtt -P your-mqtt-password \
    -t 'ventsys/#' -v
```

> **TLS note (A9-2):** The command above uses port 1883 (Stage 1 pre-TLS, for initial device bring-up).
> Phase 1.2 of this guide explains the two-stage approach. After TLS migration, switch to:
> mosquitto_sub -h localhost -p 8883 --cafile /ssl/ca.crt -u mqtt -P <password> -t ventsys/# -v

Power-cycle a sensor board. You should see:
```
ventsys/fdm/temperature 24.3
ventsys/fdm/humidity 45.1
ventsys/fdm/iaq 18500
ventsys/fdm/smoke_alarm OFF
ventsys/fan/state on
ventsys/fan/percent_state 50
```

If nothing appears: check ESPHome device logs in the add-on, verify MQTT
credentials in the YAML match Mosquitto config, confirm HA MQTT integration
is connected (Settings → Devices & Services → MQTT → Configure).

---

## Phase 4 — OTA updates (all future updates)

Once adopted, USB is never needed again:
1. Edit the YAML in the ESPHome add-on (or update vault file and re-upload)
2. Click **Install** on the device
3. Choose **Wirelessly** — ESPHome compiles and flashes over the air

Device reboots and reconnects within ~30 seconds.

---

## Phase 5 — MQTT TLS baseline

New VentSys devices should be deployed directly onto TLS now that the broker
listener and CA trust path are proven.

Each production YAML should include:

```yaml
wifi:
  use_address: ${device_ip}
  manual_ip:
    static_ip: ${device_ip}
    gateway: 192.168.50.1
    subnet: 255.255.255.0
    dns1: 192.168.50.1

mqtt:
  broker: 192.168.20.101
  port: 8883
  username: !secret mqtt_user
  password: !secret mqtt_pass
  discovery: false
  discover_ip: false
  certificate_authority: !secret mqtt_ca_cert
```

`certificate_authority` is the current ESPHome key for trusting the broker CA.
`discover_ip: false` avoids the ESPHome MQTT IP-discovery path when the native
API is already enabled for logs and OTA. `use_address` keeps OTA targeting the
static VLAN 50 address directly.

---

## Phase 6 — Adding new ESPHome devices in future

1. Determine the device IP from `configs/openwrt/dhcp-config.conf`
2. Create or copy a YAML config; set `static_ip`, hostname, and sensor pins
3. Place `secrets.yaml` in the config directory if not already there
4. Flash once via USB (Phase 1 above)
5. Note the MAC; update dhcp-config.conf; re-apply DHCP to router
6. Adopt in ESPHome add-on (Phase 2)
7. Verify entities appear in HA

**Canonical VLAN 50 IP blocks:**

| Range | Device type |
|---|---|
| .21–.22 | Fan controllers |
| .31–.34 | Sensor arrays (FDM / SLA / booth / garage) |
| .41–.43 | Airflow sensors |
| .51–.56 | Butterfly valves |
| .61–.62 | 360° intake valves |
| .71–.78 | Smart plugs |
| .79–.89 | Reserved for future devices |
| .100–.190 | Dynamic DHCP pool |

---

## Troubleshooting

| Symptom | Check |
|---|---|
| Device not in ESPHome | `ping 192.168.50.xx` from router — confirm it got its static IP |
| `nc -zv ... 6053` fails | Check firewall rule `ESPHome API HA to IoT`; device on VLAN 50? |
| MQTT not publishing | ESPHome add-on logs → look for "MQTT connected" |
| OTA flash fails | Device must be reachable on port 3232 (ESPHome OTA port) |
| Wrong IP address | MAC in dhcp-config.conf doesn't match physical device |
| WiFi not connecting | HomeIoT SSID broadcasting? WPA2 password correct in secrets.yaml? |
| DS18B20 shows 0°C | Address mismatch — re-scan logs, update `address:` field in YAML |
| BME680 not found | Check I2C address: 0x76 (default) or 0x77 (SDO pin high) |

### Find device MAC after unexpected DHCP assignment

```bash
# From router shell
cat /tmp/dhcp.leases | grep "192.168.50"
```

Note the MAC for the unexpected IP, update dhcp-config.conf, re-apply DHCP
config (`scripts/setup/router/phase_3_dhcp_configuration.md`), then power-cycle the device.

# FIX #23: A reference to update_ventsys_mac.sh was here. That script does not exist in the vault.
