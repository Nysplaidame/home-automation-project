# VentSys ESPHome Direct-TLS Rollout Guide

This is the working procedure for adding further VentSys ESPHome devices after
the 2026-05-15 TLS validation work. It is intentionally opinionated: follow
this path unless there is a documented reason not to.

## What this guide assumes

- Home Assistant is at `192.168.20.101`.
- VentSys ESPHome devices live on VLAN 50 / `192.168.50.0/24`.
- Mosquitto TLS is live on `8883`.
- The permanent router rule allowing IoT sensors to HA MQTT TLS is already in
  place.
- New devices should be introduced directly on TLS. Plain MQTT `1883` is now a
  recovery/bootstrap exception only, not the normal path.

## Source-of-truth files

- Device YAMLs: `main/configs/esphome/`
- HA mode scripts: `main/ventsys/ventsys_bundle_updated/ventsys_ha_scripts.yaml`
- Device allocation reference:
  `main/scripts/setup/ventsys/esphome_adoption_guide.md`
- TLS background and certificate setup:
  `main/docs/procedures/ssl_tls_guide.md`

## Before touching hardware

1. Confirm the physical board label and choose the matching YAML.
2. Confirm the target IP, device name, and MQTT topics in the YAML match the
   allocation table.
3. Confirm `main/configs/esphome/secrets.yaml` contains:

```yaml
wifi_ssid: "HomeIoT"
wifi_pass: "..."
mqtt_user: "mqtt"
mqtt_pass: "..."
mqtt_ca_cert: |-
  -----BEGIN CERTIFICATE-----
  ...
  -----END CERTIFICATE-----
api_key: "..."
ota_password: "..."
```

4. Visually inspect the exact component type, not only the package shape.
   The airflow-sensor troubleshooting proved that an analog 49E Hall sensor can
   look compatible with the original design while behaving completely
   differently from the intended digital latching Hall sensor.
5. Check power before assuming firmware trouble. During airflow bring-up the
   device repeatedly disappeared and reappeared until the USB connection was
   moved to a stronger laptop USB-C charging port.

## Standard YAML baseline

Every new TLS-first VentSys ESPHome device should include this network baseline:

```yaml
api:
  encryption:
    key: !secret api_key
  reboot_timeout: 0s

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_pass
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

Why these details matter:

- `certificate_authority` is required for the ESPHome client to trust the local
  Mosquitto certificate.
- `use_address` keeps OTA targeting the known static IP instead of relying on
  discovery.
- `dns1` avoids needless name-resolution ambiguity on the IoT VLAN.
- `discover_ip: false` avoids the ESPHome MQTT discovery path when the native API
  is already used for logs and HA integration.
- `api.reboot_timeout: 0s` prevents a healthy MQTT-only or temporarily
  unadopted node from rebooting itself every 15 minutes just because no API
  client is attached.

## First flash procedure

1. Connect the board by USB.
2. If flashing fails because the port is busy, close any browser tab using Web
   Serial first. Brave/web.esphome.io previously held COM5 open and blocked
   flashing.
3. If the board is unstable or not entering flash mode, use the known manual
   sequence:
   - hold `BOOT`
   - press and release `RESET`
   - release `BOOT`
4. Flash the canonical YAML for that device over USB.
5. Watch the first boot log until all of these are true:

```text
WiFi connected
MQTT:
  Server Address: 192.168.20.101:8883
Connected
```

6. On the Mosquitto side, confirm the device appears on port `8883` and that the
   log records a negotiated TLS cipher.
7. Do not count a device as validated merely because it boots. Exercise its real
   hardware path:
   - valve: command closed/open and confirm actual movement
   - airflow sensor: produce real pulses at the sensor, not only at a floating
     wire junction
   - LED device: confirm the intended GPIO and LED chain behavior

## Device bring-up checklist

### Connectivity

- Correct static IP in the boot log
- Correct hostname
- Correct MQTT broker port: `8883`
- TLS connection visible in Mosquitto logs
- HA API connects without repeated reboot cycling
- Expected entities appear in HA

### Home Assistant

- New devices do not automatically appear on the Overview dashboard just because
  entities exist. Add the desired entities/cards manually or include them in the
  relevant VentSys dashboard configuration.
- If an ESPHome device is healthy but the ESPHome dashboard does not show the
  old discovery-style status you expected, trust the actual evidence first:
  boot log, API connection, and broker log. The airflow sensor was online and
  functional even while the UI presentation differed from earlier VM testing.

### Hardware

- Verify the GPIOs in the YAML match the board you actually built, not the
  board used by the original upstream project.
- Verify the component class, value, and pinout against the actual part you
  bought.
- Treat “works only when I touch the wire” as a hardware/electrical clue, not a
  firmware success. In the airflow test that behavior was consistent with the
  wrong sensor type/floating input path, not a valid Hall-trigger path.

## Valve-specific rules

### Butterfly valves

All current butterfly valves are physically fully open at `50`, not `100`.

Required consequences:

- `Valve Open Position` should default to `50`.
- The valve status LED should compare against `id(valve_opened_position).state`,
  not hard-code `100`.
- HA mode scripts must command butterfly valves to `50` for “open”.
  Sending `100` from the mode scripts overrides the calibration even if the HA
  Overview slider behaves correctly.

The canonical scripts now follow that rule in
`main/ventsys/ventsys_bundle_updated/ventsys_ha_scripts.yaml`.

### Die-temperature monitoring

The butterfly-valve firmware keeps the original ESP32 die-temperature monitor,
alert states, test button, and flashing LED behavior. ESPHome may log ignored
invalid readings on some ESP32 variants; that does not stop valid readings from
being useful as an internal diagnostic.

To keep the normal HA surface tidy, the die-temperature sensor, alert-level text
sensor, alert binary sensors, and test-alert button are `disabled_by_default`.
Enable them in HA only where you want to inspect or expose them.

The valve YAMLs also lower the `internal_temperature.esp32` logger tag to
`INFO`, which keeps the useful feature while suppressing the repeated debug-only
invalid-reading chatter in normal logs.

## Airflow-specific lessons

- The validated TLS/network path for `ventsys-fdm-airflow` is good.
- The hardware issue was separate: the purchased 49E/OH49E/SS49E devices are
  linear analog Hall sensors, while the original design expects a digital
  latching Hall switch behavior.
- The tested ESP32-C6 wiring used:
  - Hall input: `GPIO0`
  - LED signal: `GPIO1`
- For pulse-meter debugging, add a total counter as well as the instantaneous
  rate. It makes false triggering and burst behavior much easier to see.
- Clamp derived animation percentages to the number entity range so bursty noise
  cannot exceed the configured `0..100` limit.

## Router and firewall lessons

- The permanent design is IoT VLAN to HA MQTT TLS on `8883`.
- Plain `1883` was used only as a temporary valve1 bootstrap path earlier in the
  project and has now been removed.
- Rule order matters on OpenWrt: an allow rule placed after the broad IoT-to-HA
  reject rule will never match.
- Before blaming MQTT credentials, compare:
  - ESPHome device log
  - Mosquitto listener/port in broker logs
  - router firewall rule order

## Common failure patterns

| Symptom | Most likely check |
|---|---|
| COM port access denied | Browser/Web Serial still owns the port |
| Device appears/disappears rapidly on USB | Power/cable/port quality |
| Reboots every ~15 minutes despite WiFi/MQTT working | Missing `api.reboot_timeout: 0s` |
| YAML compiles fail around secrets | Look for concatenated YAML keys or duplicate keys |
| Device boots but MQTT never connects | Verify port `8883`, CA secret, and router rule |
| HA Overview slider works but VentSys mode changes over-travel | HA mode script still sending raw `100` |
| Sensor only “works” when touching wiring | Floating input or wrong component type |
| Device entities exist but not on Overview | Dashboard card not added yet |

## Recommended rollout order for each next device

1. Copy the closest known-good YAML.
2. Set device identity, IP, topics, board type, and GPIOs.
3. Apply the direct-TLS baseline.
4. Remove copied features that are not valid on that hardware.
5. Flash by USB.
6. Confirm WiFi, API, MQTT TLS, and broker-side TLS evidence.
7. Validate the actual physical function.
8. Add or update HA entities/cards/scripts only after the hardware behavior is
   proven.
9. Record any device-specific exception in the YAML header or this guide before
   moving on.

## Final acceptance checklist

- [ ] Correct YAML for the physical board
- [ ] Direct TLS configured on `8883`
- [ ] CA trust present
- [ ] Static IP and `use_address` correct
- [ ] `api.reboot_timeout: 0s` present when appropriate
- [ ] MQTT state publishing verified
- [ ] HA entity visible
- [ ] Physical behavior verified
- [ ] Butterfly-valve 50% calibration reflected in HA scripts as well as firmware
- [ ] No temporary plain-MQTT firewall exception left behind
