---
title: Phase 11 - Physical Integrations
description: Labelled bench bring-up for cameras, P1S/Bambuddy, ESPHome, and VentSys safety acceptance
tags: [install, physical, ventsys, cameras, printers]
created: 2026-05-24
modified: 2026-08-09
type: install-guide
status: active
---

# Phase 11 - Physical Integrations

## Purpose

Bring physical devices online one at a time with a reversible chain from label
and wiring to network identity, firmware, service integration, monitoring, and
safe failure behavior. Software success never overrides an unsafe electrical or
mechanical result.

## Current-state callout

[current-live-state.md](../../reference/current-live-state.md) records three
ANNKE C500 cameras live through Frigate, Bambuddy live on docker-host, and most
VentSys physical hardware/adoption/full safety acceptance still pending. P1S
serial/access details and the HA Bambuddy package remain operator work. This
manual covers both a fresh build and the remaining-device path without claiming
that repository configuration equals installed hardware.

## Canonical guides

- [VentSys wiring reference](../../diagrams/wiring-diagrams/ventsys_wiring_reference.md)
- [ESPHome adoption guide](../../../scripts/setup/ventsys/esphome_adoption_guide.md)
- [ESPHome TLS rollout](../../procedures/ventsys_esphome_tls_rollout_guide.md)
- [camera/PoE pre-flight](../../procedures/frigate_camera_preflight_checklist.md)
- [docker-host/Bambuddy deployment](../../../scripts/setup/proxmox/docker_host_setup_guide.md)
- [printer VLAN decision](../../decisions/02-printer-vlan-architecture.md)

If a device-specific YAML and the wiring reference disagree, stop. Inspect the
physical board and correct canonical documentation/configuration before power.

## Runs on

- unpowered physical bench for inspection/continuity;
- current-limited low-voltage bench supply for first power where applicable;
- admin laptop for USB flashing and repository validation;
- OpenWrt/router-deploy workflow for DHCP reservations/firewall;
- HA UI/ESPHome add-on for adoption and MQTT/entity tests;
- CT 111 for camera restream/Frigate checks;
- docker-host for Bambuddy/P1S reachability.

## Electrical and mechanical stop conditions

Disconnect power and stop if:

- board, voltage, polarity, pinout, load current, conductor gauge, fuse, or PSU
  rating is unknown;
- a 5 V analog signal could reach an ESP32 3.3 V ADC directly;
- a servo/fan/motor is powered from the ESP 3.3 V rail;
- grounds, motor suppression/driver, strain relief, enclosure, or protective
  earth/mains isolation are unresolved;
- an actuator is mechanically coupled before its safe direction/endpoints are
  calibrated at low power;
- a camera location exposes a person/private area outside the approved field of
  view or permanent mounting prevents safe reset/service;
- PoE voltage/class/budget or cable termination is uncertain;
- a physical safety claim depends on a DIY gas/VOC sensor, AI, dashboard, Wi-Fi,
  MQTT, or Home Assistant alone.

Use certified smoke/fire protection independently. Mains work and permanent
fan supplies require a competent person and applicable local electrical rules.
Do not create smoke, flame, solvent vapour, or dangerous heat for testing; use
electrical/simulation test inputs defined for the hardware.

## 1. Build the physical-device ledger

Before connection, record for every item:

| Field | Required evidence |
|---|---|
| Physical label/location | photo plus durable label matching canonical name |
| Model/revision/serial | label/photo; board MCU and flash variant |
| MAC/IP/VLAN | unique MAC, planned reservation, switch/SSID/port |
| Power | voltage, max/current budget, connector/polarity, fuse/PoE class |
| Firmware/config | exact repository path and Git commit/hash |
| I/O | GPIO/pin, voltage level, active state, safe boot state |
| Secrets | password-manager item names only |
| Recovery | USB/reset access, power isolation, last-known-good firmware |
| Acceptance | bench, network, integration, fail-safe results and operator/date |

Do not reuse a board label or MAC reservation. Candidate/development YAML under
`_dev` or marked original/test must never be flashed to a production-labelled
board.

## 2. De-energized wiring and first-power inspection

For VentSys boards, work through the wiring-reference checklist with power
removed:

1. identify ESP board and voltage rails from the actual schematic/data sheet;
2. continuity-check power-to-ground for an unintended short;
3. verify polarity and that ADC/I2C/GPIO never exceed 3.3 V logic limits;
4. power servos/fans from the approved separate rail/driver with common signal
   ground only as designed;
5. disconnect actuator load/mechanical linkage for first firmware boot;
6. set a current limit appropriate to the board alone, then energize;
7. watch current, temperature, smell/noise, and reset/brownout behavior;
8. remove power immediately on unexpected behavior.

Expected result: board boots at expected current with no hot component,
brownout loop, motion, fan start, relay chatter, or energised unsafe output.

Recovery: remove power, photograph/measure the fault, disconnect loads, return
to a known USB-only board configuration, and correct wiring/config before a new
first-power attempt. Never “fix” a wiring fault by changing random GPIOs live.

## 3. Validate and first-flash one ESPHome board over USB

Keep the actuator/motor output physically disconnected. Use the production TLS
YAML matching the label; the garage air-sensor example is sensor-only.

Run on: Admin laptop from the repository checkout.

```powershell
$config = (Resolve-Path -LiteralPath '.\main\configs\esphome\ventsys_garage_air_sensor.yaml').Path
esphome version
esphome config $config
esphome compile $config
$serialPort = Read-Host 'Verified USB serial port (for example COM3)'
if ($serialPort -notmatch '^COM\d+$') { throw 'Expected a Windows COM port.' }
esphome run $config --device $serialPort
```

Expected result: config/compile succeed, the selected MCU/framework matches the
physical board, upload completes, and serial logs show the canonical device
name, HomeIoT connection, expected VLAN 50 address, router-derived time, native
API, and MQTT TLS connection. Record the MAC from serial/router evidence.

For another board, replace only `$config` after cross-checking the adoption
table, label, MCU, GPIOs, and IP. Never flash all boards in a loop. If upload or
boot fails, stay on USB, capture logs, and reflash the last-known-good matching
YAML; do not fall back to a plaintext-MQTT image without the documented bounded
exception and removal plan.

## 4. Add the DHCP reservation through canonical router source

Update `main/configs/openwrt/dhcp-config.conf` with the observed MAC and planned
IP, then use Phase 01 lint/compile/deploy/recovery. Do not add a conflicting live
`uci` reservation that is absent from source.

Run on: OpenWrt router over SSH after the reviewed router-deploy change.

```bash
uci show dhcp | grep 'ventsys-garage-air-sensor'
cat /tmp/dhcp.leases | grep -E 'ventsys-garage-air-sensor|192\.168\.50\.35'
ping -c 3 192.168.50.35
```

Expected output shows one reservation, the exact observed MAC/address, and
successful local reachability. A duplicate MAC/IP/name is a rollback condition.

Power-cycle only that device and prove it returns to the reservation. If it does
not, keep it on the bench, compare serial MAC, router lease, SSID/VLAN, and
static-IP YAML before reflashing.

## 5. Adopt in ESPHome and Home Assistant

In the ESPHome add-on:

1. confirm the discovered name matches the physical label;
2. adopt using the device's stored API encryption key;
3. verify logs, firmware version, IP, Wi-Fi signal, time, and update status;
4. accept the matching HA ESPHome integration notification;
5. rename only friendly UI labels, not canonical device/API identities;
6. test OTA only after USB recovery access and the first-flash artifact remain.

Run on: Home Assistant Terminal & SSH app.

```bash
nc -zvw5 192.168.50.35 6053
ping -c 3 192.168.50.35
ha core check
```

Expected result: native API port is reachable only from the approved HA path,
device responds, and HA configuration passes. A different source VLAN must not
gain editor/API access merely to simplify adoption.

Use **Settings -> Devices & Services -> MQTT -> Configure -> Listen to a topic**
for `ventsys/#`; this avoids putting the MQTT password in a process list. Power
cycle the single device and confirm expected availability/telemetry topics,
reasonable values, and recovery after reconnect.

## 6. Bench-calibrate sensors and actuators safely

### Sensors

- Compare temperature/humidity/pressure with a trusted reference at stable room
  conditions; record offset and warm-up period.
- Confirm BME680 address from logs (`0x76` versus `0x77`) matches SDO wiring.
- Validate analog input with a safe, measured voltage source across the expected
  range; never expose people to smoke/VOC/heat to force thresholds.
- Disconnect each sensor on the bench and prove unavailable/stale detection and
  notification without commanding an unsafe output.

### Servos/valves

- Keep linkage disconnected; command small increments from the local ESPHome
  control first.
- Determine direction, closed/open positions, stall limits, and PWM-detach
  behavior; never assume copied values fit a new printed mechanism.
- Attach the mechanism unpowered, move it by hand, then repeat at current limit.
- Verify power removal/manual movement leaves the duct in the documented safe
  state and does not trap a person/process.

### Fans/relays/smart plugs

- Validate only low-voltage control on the bench; use the approved driver.
- Confirm boot/off/failure default before connecting the real load.
- For a mains smart plug, use the exact device flashing/safety procedure and
  enclosure; do not open or energize exposed mains hardware.
- Confirm a physical/manual cutoff works with HA, Wi-Fi, and MQTT unavailable.

Expected result: calibrated ranges/endpoints and failure defaults are recorded
per physical unit. A mechanically “working” actuator without current/stall and
manual-cutoff evidence does not pass.

## 7. Add one PoE camera at a time

Follow the camera pre-flight guide. Before mounting:

1. photograph label/MAC/firmware and confirm switch PoE budget;
2. connect one bench port configured untagged/PVID VLAN 30;
3. change admin credentials, create least-privilege viewer if supported, disable
   cloud/P2P/UPnP, set router DNS/NTP, and update firmware only from trusted local
   media/process;
4. reserve `.21`-`.24` only after the observed MAC is known;
5. validate main/sub RTSP from CT 111, FOV/privacy mask, time, reconnect, and PoE
   port-cycle recovery;
6. add one camera to Frigate, validate, then proceed to the next;
7. mount only after a day of stable bench ingest and acceptable field of view.

After Frigate holds credentials, validate through its local restream so secrets
do not appear in the command line.

Run on: Frigate CT 111.

```bash
for stream in cam_01_annke_c500 cam_01_annke_c500_sub cam_02_gate cam_02_gate_sub cam_03_patio cam_03_patio_sub; do
  printf '\n== %s ==\n' "$stream"
  ffprobe -v error -rtsp_transport tcp \
    -show_entries stream=codec_name,width,height,r_frame_rate \
    -of default=noprint_wrappers=1 "rtsp://127.0.0.1:8554/${stream}"
done
docker compose -f /opt/frigate/docker-compose.yml config --quiet
docker compose -f /opt/frigate/docker-compose.yml ps
docker compose -f /opt/frigate/docker-compose.yml logs --tail=120 frigate
```

Expected result: each configured stream prints codec/resolution/frame rate;
Compose validates; Frigate stays healthy with no repeated decode/auth errors.
For a fresh build, run only names already added and approved; absent future
camera names are not failures.

Verify a newly created OMV-backed recording segment is non-zero and playable,
then temporarily disconnect/cycle one non-critical camera port and prove HA
offline/recovery alerts. Restore it before proceeding. Do not combine first
camera enablement, OMV cutover, detection tuning, and permanent mounting.

Rollback: restore `config-baseline.yml`/last-known-good camera set, keep `.env`
protected, restart Frigate, and prove existing cameras/recording before retrying.

## 8. Add the P1S to Printer VLAN 35 and Bambuddy

Keep printer control separated from general IoT. Record the printer Wi-Fi MAC,
serial, LAN access-code custody, firmware, and physical location. Use the
canonical router source to reserve `192.168.35.200`; do not commit the serial or
access code.

From the P1S UI/app, enable the approved LAN connectivity mode and record the
access code directly into Bitwarden/Bambuddy UI. Decide cloud access separately;
do not weaken VLAN policy as a troubleshooting shortcut.

Run on: docker-host over SSH.

```bash
nc -zvw5 192.168.35.200 8883
nc -zvw5 192.168.35.200 21
nc -zvw5 192.168.20.101 8883
docker compose -f /opt/stacks/bambuddy/docker-compose.yml ps
docker compose -f /opt/stacks/bambuddy/docker-compose.yml logs --tail=100
```

Expected result: only approved printer/Bambuddy/HA paths answer, Bambuddy is
healthy, and logs show successful printer/MQTT integration without printing
credentials. A denied workstation/VLAN path should remain denied.

Copy `main/configs/home-assistant/bambuddy_p1s_package.yaml` to HA live
`/config/packages/`, substitute `<P1S_SERIAL>` only in the live untracked copy,
then validate before restart.

Run on: Home Assistant Terminal & SSH app after the live-only serial substitution.

```bash
ha core check
grep -R '<P1S_SERIAL>' /config/packages/bambuddy_p1s_package.yaml && exit 1 || true
```

Expected result: HA configuration passes and no unresolved serial placeholder
remains in the live package. Confirm printer status changes appear in Bambuddy
and HA using a harmless idle/ready observation; do not start an unattended print
as an integration test.

## 9. VentSys safety acceptance sequence

Test one chain at a time with the physical load made harmless:

1. sensor input/telemetry and plausible range;
2. stale/unavailable detection;
3. HA entity and automation trace;
4. notification delivery and acknowledgement;
5. command arbitration/manual override;
6. actuator response at disconnected/low-energy bench state;
7. loss of HA, MQTT, Wi-Fi, sensor, and controller power;
8. physical cutoff/manual safe-state recovery;
9. restart/reconnect without an unexpected output pulse;
10. only then connect the real non-mains load and repeat under supervision.

Use simulated/test entities or electrically safe test inputs. Never heat a
printer/enclosure, create smoke/vapour, obstruct live extraction, or defeat a
certified alarm to prove automation. AI remains advisory and must not issue
safety-critical actuator commands.

Run on: Home Assistant Terminal & SSH app after deploying the live packages.

```bash
ha core check
ha core logs --lines 200 | grep -Ei 'ventsys|esphome|mqtt|error|failed' || true
```

Expected result: config passes and no unresolved VentSys/ESPHome/MQTT error is
present. Use HA automation traces plus physical observation for each harmless
test; a clean log alone is not proof.

## End-of-phase validation

Run on: OpenWrt router over SSH.

```bash
uci show dhcp | grep -E 'ventsys|camera|cam-|p1s|bambu'
logread | grep -E 'DHCPACK.*192\.168\.(30|35|50)\.' | tail -n 80
```

Expected result: only recorded device reservations/leases appear in their
planned camera, printer, and IoT subnets; unknown MACs remain unapproved.

Run on: Home Assistant Terminal & SSH app.

```bash
ha core check
ha core info
```

Expected result: configuration is valid and Core reports `running` without a
restart loop.

Run on: Frigate CT 111.

```bash
docker compose -f /opt/frigate/docker-compose.yml ps
findmnt -T /mnt/nas/frigate
find /mnt/nas/frigate -type f -name '*.mp4' -printf '%T@ %s %p\n' \
  | sort -nr | head -n 3
```

Expected result: device reservations/leasing match labels, HA config and
integrations are healthy, Frigate is up, recording storage is the OMV bind, and
recent non-zero segments exist. Final acceptance additionally requires the
physical ledger and harmless failure tests—not just these commands.

## Failure recovery matrix

| Failure | Safe response | Proof before continuing |
|---|---|---|
| Unexpected current/heat/motion | Cut power; disconnect load; inspect wiring/firmware. | Board-only current and boot state normal. |
| Wrong board identity/GPIO | Stay on USB; flash matching last-known-good YAML. | Serial name, MCU, IP and pins match label. |
| Device gets wrong IP | Keep on bench; reconcile MAC, reservation and YAML. | One MAC/name/IP mapping after power cycle. |
| API/MQTT unavailable | Check time, CA, VLAN, firewall and credentials without plaintext fallback. | Native API and MQTT TLS recover. |
| Sensor implausible/stale | Mark unavailable; inhibit dependent automation; inspect wiring/calibration. | Trusted-reference and disconnect tests pass. |
| Servo stalls/reverses | Remove power/linkage; reduce range and recalibrate. | Incremental no-load then loaded travel passes. |
| Camera auth/decode fails | Keep camera on bench; test supported auth/stream; preserve existing set. | Restream/Frigate logs stable. |
| Camera/PoE drops | Cycle only affected port; inspect cable/budget/firmware. | Sustained stream plus recovery alert pass. |
| P1S/Bambuddy fails | Preserve printer VLAN; recheck LAN mode/code/firewall. | Idle status reaches Bambuddy/HA; no broad rule. |
| Safety chain test fails | Keep physical load disconnected and automation disabled. | Independent cutoff plus each failure mode passes. |

## Completion checklist

- [ ] Every physical item has a unique label, ledger row, recovery access, and photo.
- [ ] De-energized wiring, voltage, polarity, current, fuse/PoE, and safe boot checks pass.
- [ ] Each ESPHome board compiles/flashes individually with matching production TLS YAML.
- [ ] MAC reservation, adoption, API, MQTT TLS, telemetry, OTA, and offline recovery pass per board.
- [ ] Sensors and actuators have recorded calibration, stall/current, manual cutoff, and failure defaults.
- [ ] Each camera passes bench, hardening, RTSP/restream, PoE recovery, Frigate, recording, privacy, and alert tests before mounting.
- [ ] P1S reservation/LAN mode/Bambuddy/HA package work without committing serial or access code.
- [ ] Harmless VentSys failure-mode tests and independent certified/manual protections pass.
- [ ] AI/dashboard/Wi-Fi/MQTT/HA are not sole safety controls.

Continue to [Phase 12 - Validation and Troubleshooting](12-validation-troubleshooting.md)
only after all connected physical devices have explicit pass/fail records.
