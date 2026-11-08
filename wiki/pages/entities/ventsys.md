---
title: "VentSys — Fire Safety Ventilation System"
category: entity
tags: [ventsys, esphome, mqtt, safety, ventilation, 3d-printing]
created: 2026-04-07
updated: 2026-11-07
sources: [project-readme, ventsys-technical-specs, ventsys-implementation-roadmap, troubleshooting-reference]
status: active
---

# VentSys — Fire Safety Ventilation System

**Type:** integration — custom fire safety ventilation subsystem
**Status:** 🧪 Under testing, not commissioned — E1, E2, MAIN-1, MAIN-2, and both 360 intake controller boards are adopted; 360 firmware/HA roles accepted; dashboard legacy-ID correction deployed; physical commissioning separate
**Related:** [[entities/esphome]], [[entities/home-assistant]], [[entities/mosquitto-mqtt]], [[concepts/ventsys-architecture]], [[concepts/printairpipe]], [[concepts/mqtt-tls]]

## Current dashboard controls

November 7 frontend `20261107-8` includes a Clear alarms popup in standard and touch
views. It lists live native board latches and offers per-board acknowledgment
only while the board reports no active alarm or sensor fault. The SLA pipe CO
reading returned to about 3.3 V with a sensor fault and stored latch, so its
latch cannot currently be acknowledged. The latest API check did not report
CO detection. The dashboard shows the latch and fault as orange live incidents,
and HA sends CO hardware fault and failsafe transitions to internal ntfy.
The ntfy server accepted a test publish; phone reception and the full
persistent incident system remain pending. See the canonical dashboard manual.
The separate read-only Diagnostics tab inventories searchable HA entity values,
including CO voltage, faults, BME680 data and board/controller statistics where
firmware exposes them. It showed about 3.33 V on the faulted CO channel.
All 12 adopted boards are expected online by default. Diagnostics provides a
per-board maintenance switch that pauses that board's dropout ntfy alerts while
showing maintenance in blue; an offline board remains visible. Eleven boards
use uptime availability for dropout/recovery alerts, and SLA pipe uses its
separate status rule. Maintenance does not pause CO hardware fault or failsafe
alerts. Live switch operation was verified; induced dropout and phone delivery
are still unverified.

Frontend `20261027-1` uses grouped independent FDM/SLA Enclosure/Print/Purge
intents, with separate Booth. Shared paths retain every active owner; stale
requests and conflicting manual commands are blocked in the HA backend. Purge
strength2/4/6/8/10 requests20/40/60/80/100 percent, with the highest active purge
request winning. The owner accepted that requested mapping pending physical
calibration. Values open one confirmation on commit; review buttons and the
physical-position field are removed. Standard and seven-inch touch views remain.
38 Python,39 browser and24 model tests passed, together with live HA config,
read-only template and UI checks. No actuator commands were issued in this update.

Running-firmware logs establish physical FDM `.62` uses legacy
`ventsys/sla/360/control`, and physical SLA `.61` uses `ventsys/fdm/360/control`.
Those corrected topics remain; firmware was not changed. Historical October20 E2 finding:
October20 live config still contains `.51`, whereas canonical E2 is `.52` / MAC
`ec:e3:34:b4:79:7c`. Two HA-host pings to `.52` failed. The earlier `.52` recovery
claim is not current availability or physical acceptance. Investigate identity,
reachability and persistent binding before commissioning.

Mode-report warnings cover missing required openings and unwanted open reports.
Mechanical jams with matching command echoes remain unobservable without suitable
feedback/commissioned flow evidence. ntfy incident rules and open/closed-path
baselines remain proposed; phone delivery is not yet accepted. Canonical details:
[[../../../main/docs/procedures/ventsys-dashboard]].

## Overview

On October 18–19, the dashboard and HA mode scripts returned to 0–100 software
commands, then the authenticated direct HA card was deployed as release
`20261018-3`. It has reviewed requests, native controller reports, explicit
missing/stale values, corrected sensor quantities/units and a phone layout.
The public credential was removed and its dedicated token revoked; independent
verification returned HTTP 401. Real HA desktop/phone startup sent no commands.
The owner confirmed October 19 that the 30–60 firmware and firmware/HA role
swap are correct. Legacy entity IDs retained the old opposite role prefixes,
causing a dashboard-only read/confirmation mismatch. Live release `20261019-1`
corrects those bindings and recognizes 30/60 endpoints, with 53 tests passed;
activation and range checks passed through normal HA sign-in. Uninstalled hardware is expected during setup.
No firmware/calibration was changed; system commissioning is still separate.
Backend `20261019-arbitration-1` adds a shared normal dispatcher for named modes,
legacy helper and dashboard commands, with per-publish failsafe gates and fire
preemption. The fire-response main-fan 100% omission is reconciled. Eight policy
tests, 11 backend tests, three drift tests and an isolated real HA no-MQTT probe
passed. No physical command was sent; direct MQTT/native controls bypass this
boundary and physical commissioning remains separate.
Frontend `20261019-4` adds a separate `/dashboard-ventsys/touch` view for the
seven-inch display, retaining the standard view and diagram geometry. Touch
pop-ups reuse authenticated controls/guards; the original-style PrintAirPipe
header/clock and bottom status strip show current/unmeasured status. Duct
highlight overruns are fixed and log entries enlarged. 30 browser tests and
live configuration/popup acceptance passed without commands; the physical
screen still needs checking.
Homepage now links to the signed-in dashboard through its existing HA proxy
under Home & Security, using a standalone Open tab action.
Current source and operating authority:
[[../../../main/docs/procedures/ventsys-dashboard]] and
[[../../../main/docs/reference/current-live-state]].

VentSys is a bespoke fire safety and ventilation system built around ESP32 microcontrollers, ESPHome firmware, MQTT, and Home Assistant automations. It manages airflow across two 3D printer enclosures (FDM and SLA) and a spray booth using servo-controlled butterfly valves and inline duct fans. Sensors monitor temperature, humidity, smoke, VOC, and differential pressure. Emergency power cutoff is handled via smart plugs.

The authenticated dashboard and HA integration are deployed; hardware-dependent
entities must not be treated as commissioned until
the ESPHome devices are built, adopted, and explicitly revalidated. Historical
main-valve-1 work should be resumed only on the MQTT TLS path.

The owner confirmed on 2026-10-10 that the VentSys system remains under testing
and has not been commissioned. Record commissioning only when the owner says
it has occurred. On 2026-10-10 all six reachable boards (.61/.62/.52/.57/.41/.32) received OTA maintenance firmware with restart/shutdown controls. Production valve source now persists commands and endpoints without boot motion. The 360 SLA-profile raw-LEDC fix is flashed on the board now assigned to SLA; physical acceptance remains open. Installed legacy FDM .32 uses C6 SDA4/SCL5, BME680 0x77, analog gas ADC3 and status LED2. The owner identified its fitted gas component as CO on 2026-11-08; flashed firmware and dashboard still call it smoke and use an uncalibrated threshold. Confirm module model and correct that channel before relying on its alarm. The final firmware restored the archived wiring and cleared its BME fault. MAIN-2 passed one software restart on independent power within 7.7 seconds with saved settings and PWM inactive; earlier USB reset/power failures are still not definitively diagnosed. Repeated loaded cold starts remain pending. See [[../../../main/docs/procedures/ventsys-board-power-controls]]. No valve movement was commanded.
Power Off and physical reset/power-cycle wake acceptance remain open; see
[[main/docs/procedures/ventsys-board-power-controls]].

On 2026-11-08, the owner confirmed the FDM enclosure board uses CO GPIO3 and
BME680 GPIO4/5 like the SLA pipe board. A CO-only replacement source compiled,
but the FDM board was offline and no USB serial device was present, so the
smoke-labelled image was not replaced. Physical status LED wiring still needs
verification because the legacy record says GPIO2 plain LED while the new
shared source assumes GPIO8 WS2812. See the canonical live-state record.

## Solar Observatory Display Rebuild

The 7-inch screensaver replacement has local TypeScript foundations for
authoritative ephemeris ingestion, common moon/path coordinates, camera
framing, expiring read-only display state and validated cache publication.
It now has a tested local Three.js geometry preview for Earth/Moon, Jupiter/Io
and Saturn, plus a mock-tested read-only host with expiring state and latched
failsafe interruption. Simulated connectivity is not physical monitoring health.
The first local visual pass uses NASA Earth/Moon maps and a muted ESO Milky Way
photograph, with visible attribution. Earth/Moon surfaces follow an approximate
IAU text-PCK attitude model verified against SPICE; it is not precision EOP or
binary lunar libration, and leap-second coverage ends July1 2027 pending review.
Other bodies still use proof geometry. There is no accepted HA integration. The existing
dashboard/card and live deployments were not changed by this work.
Canonical status: [[main/docs/procedures/ventsys_solar_screensaver]].

## Physical Setup

- **Ducting:** PrintAirPipe 125mm with servo-controlled butterfly valves.
- **Enclosures:** FDM printer, SLA printer, spray booth.
- **Fan:** inline duct fan plus spray booth fan control in HA entities/scripts.
- **Valves:** multiple servo-driven butterfly valves per zone.
- **Device baseline:** all hardware-dependent devices remain pending or require
  explicit revalidation before use.

## ESP32 Device Fleet (21 YAML/device entries)

> Full canonical table from `esphome_adoption_guide.md` and current handoff state. All YAMLs exist in `configs/esphome/`. Treat all hardware-dependent devices as pending or needing explicit TLS-path revalidation. **Flash wrong YAML = wrong GPIO/MQTT topics; requires full USB re-flash to fix.**

| Role | device_name | IP / MAC | YAML | State |
|---|---|---|---|---|
| Main fan | ventsys-main-fan | 192.168.50.21 | ventsys_fan_controller.yaml | pending |
| Booth fan | ventsys-booth-fan | 192.168.50.22 | ventsys_booth_fan.yaml | pending |
| FDM sensor | enc-fdm-sensors | 192.168.50.31 | ventsys_fdm_sensor.yaml | pending |
| FDM sensor | ventsys-fdm-sensor | 192.168.50.32 / CC:BA:97:F0:D0:C0 | ventsys_fdm_sensor.yaml | online, renamed November4 |
| Booth sensor | enc-booth-sensors | 192.168.50.33 | ventsys_booth_sensor.yaml | pending |
| Garage sensor | ventsys-garage-sensor | 192.168.50.34 | ventsys_garage_sensor.yaml | pending |
| SLA pipe air | ventsys-sla-pipe-air-sensor | 192.168.50.37 / CC:BA:97:F0:C3:0C | ventsys_sla_pipe_air_sensor.yaml | Flashed/adopted November 6; BME680 on GPIO4/5 at 0x77 works; CO on GPIO3 again faulted near 3.3 V with detection and latch active November 7, hardware check pending |
| FDM airflow | ventsys-fdm-airflow | 192.168.50.41 / CC:BA:97:F0:E3:DC | ventsys_fdm_airflow.yaml | USB flash and encrypted API verified October21; HA adoption and physical pulse checks pending |
| SLA airflow | ventsys-sla-airflow | 192.168.50.42 / CC:BA:97:F0:D3:10 | ventsys_sla_airflow.yaml | Flashed and adopted in HA Garage 2026-10-19; physical airflow/pulse response untested |
| Booth airflow | ventsys-booth-airflow | 192.168.50.43 / CC:BA:97:F0:D0:A0 | ventsys_booth_airflow.yaml | Reassigned from FDM by MAC-verified OTA October21; GPIO0 pulse/GPIO1 LED retained; API verified, HA adoption and physical checks pending |
| Main valve 1 | ventsys-main-valve-1 | 192.168.50.51 / EC:E3:34:67:8C:9C | ventsys_main_valve1.yaml | New normal three-wire servo board flashed and adopted in HA on 2026-10-12; owner confirms physical/display travel0–100%; no feedback entities |
| Main valve 2 | ventsys-main-valve-2 | 192.168.50.57 | ventsys_main_valve2.yaml | ESPHome/HA and MQTT online; normal servo; owner confirms physical/display travel0–100% |
| E1 / FDM branch valve | ventsys-fdm-branch-valve | 192.168.50.53 / EC:E3:34:67:0D:28 | ventsys_fdm_branch_valve.yaml | Normal three-wire servo board flashed and adopted in HA on 2026-10-11; owner confirms physical/display travel0–100% |
| E2 / SLA branch valve | ventsys-sla-branch-valve | 192.168.50.52 | ventsys_sla_branch_valve.yaml | Board adopted; normal servo linked, range accepted for bench state |
| FDM print valve | ventsys-fdm-print-valve | 192.168.50.55 | ventsys_fdm_print_valve.yaml | flashed/adopted October28; owner confirms physical/display travel0–100% |
| SLA print valve | ventsys-sla-print-valve | 192.168.50.56 / EC:E3:34:1B:DB:2C | ventsys_sla_print_valve.yaml | Flashed/adopted October29; owner confirms physical/display travel0–100% |
| FDM 360 intake | ventsys-fdm-360-valve | `192.168.50.62` / `A0:85:E3:AE:5B:C8` | `ventsys_fdm_360_valve_v2_nerdiy.yaml` | Formerly labeled SLA; firmware reassignment pending |
| SLA 360 intake | ventsys-sla-360-valve | `192.168.50.61` / `CC:BA:97:F0:E3:EC` | `ventsys_sla_360_valve_v2_nerdiy.yaml` | Board flashed over COM8 on 2026-10-10 while labeled FDM; firmware reassignment pending |
| UV plug 1 | ventsys-plug-uv-1 | 192.168.50.73 | ventsys_plug_uv1.yaml | pending |
| UV plug 2 | ventsys-plug-uv-2 | 192.168.50.74 | ventsys_plug_uv2.yaml | pending |
| Wash/cure plug | ventsys-plug-wash-cure | 192.168.50.75 | ventsys_plug_wash_cure.yaml | pending |
| Ultrasonic plug | ventsys-plug-ultrasonic | 192.168.50.76 | ventsys_plug_ultrasonic.yaml | pending |

## 360 Intake Identity Correction — 2026-10-10

The owner requested swapping the FDM/SLA 360-intake identities. HA device info
verified MAC `CC:BA:97:F0:E3:EC` at `.61` and MAC `A0:85:E3:AE:5B:C8` at `.62`
under the old labels. Corrected target mapping swaps FDM/SLA roles while keeping
the observed IP/MAC pairs together: FDM = `.62` / `A0:85:E3:AE:5B:C8`; SLA =
`.61` / `CC:BA:97:F0:E3:EC`. DHCP and firmware sources now match that target.
Live boards still run their old static-IP names/topics; OTA each profile at its
existing IP and verify HA identity/topics before using either valve. The `.61`
COM8 board history therefore refers to the board now assigned to SLA.

## Main Valve 1 Current Bench State

- MAC `EC:E3:34:67:8C:9C` is MAIN-1 at `.51`. Its normal three-wire servo
  uses GPIO16, with GPIO21 LED and enabled GPIO33 touch toggle. HA adopted it
  on 2026-10-12 with no feedback entities. Its horn is free, the copied
  940–2000 µs window is provisional, and physical stops remain uncalibrated.
- No physical MAIN-1 board was verified in the earlier 2026-10-06 session;
  the board formerly used for Valve 1 testing is now MAIN-2.
- Canonical current state: `main/docs/reference/current-live-state.md`.

## E2 and Main Valve 2 Current Bench State

- MAC `EC:E3:34:B4:79:7C` is E2/SLA branch at `.52`, not MAIN-2. Its normal
  servo retains the accepted E2 940–2000 µs endpoints. The linked valve still
  needs loaded-system acceptance.
- MAC `EC:E3:34:67:A0:18` is MAIN-2 at `.57`. It runs a normal three-wire
  servo on GPIO16, an LED on GPIO21, and enabled GPIO33 touch control. The
  940–2000 µs range is copied from E2; neither stop is calibrated for MAIN-2.
- HA's native MAIN-2 device and 21 entity IDs now use Valve 2 identity. The
  separate MQTT `number.main_duct_valve_2` shows restored command 50. PWM was
  inactive after boot. The commanded value is not physical position feedback.
- Canonical current state: `main/docs/reference/current-live-state.md`.

## Main Valve 1 Historical Facts

- Device name: `ventsys-main-valve-1`.
- Previous board MAC: `EC:E3:34:B4:79:7C` (not the current Valve 1 board).
- Static IP: `192.168.50.51` (VLAN 50 / HomeIoT).
- ESPHome API: port `6053` with noise encryption.
- OTA: port `3232`.
- MQTT broker target: `192.168.20.101:8883` with CA validation before current use.
- Control topic: `ventsys/main/valve1/control`.
- State topic: `ventsys/main/valve1/state`.
- HA entity: `number.main_duct_valve_1`.

These historical facts describe an earlier board assignment. No present
Valve 1 controller was verified in the 2026-10-06 session.

## MQTT Architecture

- **Current state:** broker TLS on `8883` is live; plain MQTT `1883` should not be reintroduced through router policy for VentSys.
- **Required next migration:** add `mqtt_ca_cert` to repo and HA-side ESPHome `secrets.yaml`, then keep VentSys device YAMLs on `8883` with `certificate_authority` before adoption/revalidation.
- **Topic structure:** `ventsys/<zone>/<sensor|control>/<type>`.
- **WiFi:** HomeIoT SSID (VLAN 50, 2.4GHz, channel 6, WPA2).

## HA Integration Files

- `/config/packages/ventsys_ha_package.yaml` — entities + automations.
- `/config/packages/ventsys_ha_scripts.yaml` — 12 mode scripts plus `script.ventsys_ramp_valve` helper; mode changes now ramp valves server-side.
- `/config/www/ventsys-dashboard.html` — live dashboard.
- `/config/www/ventsys-config.js` - public display configuration only; no HA tokens.
  The authenticated card/page bridge remains a draft acceptance dependency;
  see [[main/docs/procedures/ventsys-card-page-bridge-contract]].
- `/config/www/ventsys-card-wrapper.html` — iframe/card wrapper for HA UI embedding.

## Safety Notes

- Software failsafe via `input_boolean.ventsys_failsafe` in HA.
- Broad safety automations remain disabled until the physical sensors/devices they depend on are present and tested.
- Production ESPHome source includes **Power Off Board** (deep sleep) and
  **Restart Board** buttons. Shutdown disables telemetry, sensing, and actuator
  control; restarting requires the physical reset button or a power cycle.
  These controls are source-only until each board is built/flashed. Follow
  [[main/docs/procedures/ventsys-board-power-controls]] and do not shut down a
  board while relying on its safety monitoring or control.
- ⚠️ Hardware failsafe relay recommended (normally-closed, keeps fan ON if ESP32 loses power).
- MQ sensors require 24–48h burn-in before calibration.
- DS18B20 one-wire addresses must be discovered after first flash and added to YAML.

## Open Questions

- [ ] Finish MQTT TLS migration/revalidation for valve 1 without reintroducing plain-MQTT router access.
- [ ] Purchase/build/flash/adopt the remaining VentSys devices.
- [ ] Record DS18B20 addresses after first flash; update YAMLs.
- [x] Replace the old iframe bridge with the authenticated direct HA card; public token revoked.
- [ ] Stand up the garage Pi 4 kiosk once display hardware is ready.
- [x] Serialize mode transitions with a single manager and reject overlapping/stale requests; do not restart an in-flight transition.
- [x] Verify authenticated-card startup/hydration never sends actuator commands.
- [ ] Verify Valve 2's saved position after a deliberately commanded non-100 value and power cycle, once physical travel is calibrated.

## Change Log

- 2026-10-20: Synced independent operating intents, purge strengths and backend guards; recorded E2 host/reachability discrepancy, bidirectional report faults and outstanding ntfy/physical acceptance.


- 2026-10-10: Added shared board shutdown/restart controls across the
  production firmware set and flashed the FDM C6 test target over COM8. HA
  showed fresh Wi-Fi telemetry; Power Off and physical wake acceptance remain
  open. VentSys remains under testing and uncommissioned.
- 2026-10-04: Corrected the Valve 1/Valve 2 physical MAC assignment; recorded
  Valve 2's three-wire servo firmware and restored commanded-position display.
- 2026-05-30: Synced to canonical planning baseline: VentSys packages/dashboard are staged, hardware-dependent entities require revalidation, and plain-MQTT router access should not be reintroduced.
- 2026-05-18: Updated for live main-valve-1, dashboard token externalization, HA-side ramp helper, mixed MQTT state, and current TLS migration blockers.
- 2026-04-07: Page created; full device fleet, MQTT architecture, and safety notes from ingest.


## October27 E2 reporting recovery

The USB board is COM4 / MAC `ec:e3:34:b4:79:7c`, running its correct October10
E2 firmware. Router association and broker TLS confirm `.52` online; ICMP was
not a valid offline proof. The stale HA `.51` entry was reconfigured to `.52`
through HA; persisted host and dashboard native E2 branch0% verified. No flash,
firewall change or remote valve command. Owner reports local touch actuation;
remote control and physical travel acceptance remain separate. Canonical detail:
[[../../../main/docs/procedures/ventsys-dashboard]].


## Explicit valve setup testing — October27

Live frontend20261027-1 adds an opt-in Setup/test toggle. It reviews an exact
available native valve subset and skipped controllers, commands no fans, changes
no operating intents and makes no ventilation-established claim. Active modes,
reported running fans, failsafe/fire, lost reviewed controllers and concurrent
requests block tests. Normal operating modes retain complete-path checks.
39 Python,42 browser and24 model tests passed; live config/script/resource/hash
and review/cancel checks passed without actuator commands. Canonical semantics
and rollback: [[../../../main/docs/procedures/ventsys-dashboard]].

## FDM print board — October28/29

Canonical [[../../../main/docs/reference/current-live-state|current live state]] and
[[../../../main/docs/procedures/ventsys-board-power-controls|board procedure]]
record normal three-wire MAC `EC:E3:34:B4:76:A4`, `.55`, USB COM4 installation
and HA adoption. GPIO16 servo/GPIO33 touch, no position feedback. MQTT TLS and
native display50% verified with PWM off and no command since boot; physical
travel remains unverified. Owner unplugged board October29; repower and endpoint,
touch, remote and loaded tests remain pending. System remains uncommissioned.

### SLA print installation — October29

The same canonical board procedure records normal three-wire SLA print `.56`,
MAC `EC:E3:34:1B:DB:2C`, COM4 flash and Garage adoption. Original4MB backup saved;
MQTT TLS/native seed50% verified, PWM off, no command since boot. GPIO16/GPIO33,
no feedback; calibration, touch/remote travel and loaded stability remain pending.

## November4 update

FDM sensor identity and E2 router/HA reservations corrected; E2 was temporarily monitored; the owner stopped that monitor. Both 360 intake GPIO2 digital touch inputs were deployed. SLA raw60 survived an accepted-image restart and both intakes retained reports through final OTA with PWM off. Dashboard normalizes30–60 to0–100 and shows red arrows for zero flow, blue moving arrows for detected flow, grey for offline. Physical touch and position remain unverified. See [[../../../main/docs/procedures/ventsys-dashboard|dashboard manual]] and [[../../../main/docs/procedures/ventsys-board-power-controls|board procedure]].

**November4 owner correction:** Standard print, enclosure/branch and main valves have physical and displayed endpoints of 0–100%. Earlier uncalibrated statements describe historical bench state. The 360 intakes separately map raw30–60 to displayed0–100%. No physical position feedback is fitted.
