---
title: VentSys board shutdown and restart controls
type: procedure
status: active
created: 2026-10-10
modified: 2026-11-04
tags: [ventsys, esphome, maintenance, safety]
---

# VentSys board shutdown and restart controls

**November4 owner correction:** Standard print, enclosure/branch and main
valves have 0–100% physical and displayed travel. Older uncalibrated or pending
endpoint notes below describe historical bench state and are superseded by this
owner confirmation. The 360 intakes separately map raw30–60 to displayed0–100.
No mechanical position feedback is fitted.

Production VentSys ESPHome firmware includes two native Home Assistant buttons
through `configs/esphome/ventsys_board_management.yaml`:

- **Power Off Board** invokes ESPHome shutdown and places the ESP in deep sleep.
- **Restart Board** reboots an awake ESP while it is reachable.

Shutdown is not a switched power supply. While asleep, the ESP has no Wi-Fi,
Home Assistant, MQTT, telemetry, sensing, or actuator control. The Restart
button cannot wake it. Resume it using the board's physical reset button or by
cycling its power. An external power switch would be needed for remote power
cycling.

## Safety boundary

Do not shut down a board while relying on it for active fire, smoke, temperature,
air-quality, airflow, or valve control. Before any maintenance shutdown, stop
the related printer/process and ensure required ventilation and monitoring are
maintained independently. Do not assume a valve or relay stays in a safe
physical state when its controller sleeps; that depends on the board, wiring,
servo/relay supply, and mechanism. Software-reported position is not proof of
physical position.

Shutting down a VentSys smart-plug controller also does not provide a guaranteed
way to switch its connected load off. Verify load state separately before
maintenance.

## Deployment status

### Valve position persistence

All eleven top-level valve firmware variants under `configs/esphome/` now
persist Valve Position, Valve Open Position and Valve Closed Position using
`restore_value: true` and `flash_write_interval: 1ms`. The bundled TLS/pre-TLS
valve templates also retain their commanded-position global, checking changes
every 1ms. All production standalone firmware and sensor wrappers include the
shared shutdown/restart package; bundled controller templates include it too.
Development-only calibration/prototype images under `_dev/` are not rollout
targets and retain their documented special-purpose behaviour.

Position means the last software command, not measured shaft position. Servo
restore remains explicitly disabled: startup restores number states without
calling the motor action. Intermediate PWM holding ends at a reboot/shutdown;
the mechanism is not automatically driven back to its saved command. A later
explicit position command enables PWM. First installation falls back to the
configured initial value if the previous firmware never saved a command.
There is still a small save/power-loss race; the 1ms interval is a scheduling
interval, not a guaranteed flash completion deadline. Writes occur when values
change. Avoid continuous high-frequency command streams because of flash wear.

The v2 intake MQTT and Open/Close buttons now use `number.set` so these paths
save the command as well as native number control. Calling `publish_state`
alone does not save ESPHome TemplateNumber preferences.

Offline regression gate: `py -3.12 main/tools/validate_ventsys_firmware.py`.
ESPHome 2026.9.1 configuration validation covers every production entry point
and all four bundled controller templates; online targets additionally require
a successful build, authenticated OTA upload and native API identity/build check.

The shared controls are present in canonical firmware source. VentSys remains
under testing and has not been commissioned; commissioning status will be
updated only when the owner specifies that it has occurred.

### Online OTA rollout — 2026-10-10

All six reachable devices received authenticated OTA updates, with native API
identity, build timestamp and board controls verified afterward. ESPHome
2026.4.5 built the five valve/airflow targets; 2026.9.1 built the installed SLA
sensor (encrypted OTA). HA Builder YAMLs were synchronized with canonical source.

| Address | Device | Final build (BST) |
|---|---|---|
| .61 | SLA 360 (`CC:BA:97:F0:E3:EC`) | 10:07:55 |
| .62 | FDM 360 (`A0:85:E3:AE:5B:C8`) | 10:09:39 |
| .52 | E2/SLA branch | 10:11:23 |
| .41 | FDM airflow | 10:13:58 |
| .57 | MAIN-2, including reset/heap/loop diagnostics | 10:25:40 |
| .32 | Installed legacy SLA enclosure sensor | 10:32:58 |

The owner later corrected the FDM/SLA 360 identity mapping. HA had the old
labels `.61`/MAC `CC:BA:97:F0:E3:EC` as FDM and `.62`/MAC
`A0:85:E3:AE:5B:C8` as SLA. Target roles swap while each IP/MAC pair stays with
its board: SLA `.61`/MAC `CC:BA:97:F0:E3:EC`, FDM `.62`/MAC
`A0:85:E3:AE:5B:C8`. DHCP and firmware sources now match; live firmware still
needs an in-place OTA at each board's existing IP, followed by HA identity and
MQTT-topic verification. The 2026-10-10 builds did not command valve movement
or Power Off.
Physical direction and endpoint acceptance remain pending. Offline boards still
require deployment and acceptance.

**October 19 owner correction:** the 360 firmware is correct and its FDM/SLA
role swap was already completed in firmware/HA. The earlier pending-OTA note
above is historical, not the current next step. Registry entity IDs retain
their old FDM/SLA prefixes; see [[ventsys-dashboard]] for MAC-based bindings.
The dashboard correction changes neither firmware nor physical calibration.

The installed FDM sensor (previously identified as SLA) is ESP32-C6 MAC `cc:ba:97:f0:d0:c0`, name
`ventsys-fdm-sensor` since November4. Its archived June firmware is the hardware authority:
SDA GPIO4, SCL GPIO5, BME680 **0x77**, analog gas ADC GPIO3, status LED GPIO2.
Archived firmware calls the GPIO3 input smoke, but the owner identified the
fitted component as a CO detector on 2026-11-08. The flashed smoke naming and
fixed raw threshold are not validated for that CO module. Confirm its model and
interface before revising firmware or dashboard labels. The first maintenance
upload incorrectly used the modern
carrier's 0x76 default and produced a BME read fault. The final standalone
`ventsys_sla_sensor.yaml` restores the installed wiring/address, adds management
and BME validity diagnostics, and preserves its legacy topics. Native readings
confirmed temperature 22.88°C, valid pressure/humidity/gas and `sensor_fault=false`.
Do not use the new-carrier configuration for this installed board. Its .32
address conflicts with the planned FDM array 2 inventory; resolve before that
board is deployed. CO channel identification, alarm calibration and full safety
acceptance remain open.

### MAIN-2 reset investigation

MAIN-2's initial OTA handshake failed before firmware transfer while the board
was unreachable. COM4 serial access later showed a power-on boot and successful
network setup; OTA then completed. Historical bench work documents PC USB
RTS/DTR holding a controller in reset and standalone supply resolving similar
symptoms. This is a candidate explanation, not a proven diagnosis for MAIN-2.
Router logs showed inactivity/disconnection and retries, but no MQTT firewall
block was established; firewall and Wi-Fi settings were left unchanged.

With the owner moving MAIN-2 to independent power, uptime advanced beyond five
minutes, heap was about 192 kB, loop time 17 ms, and reset reason matched the
preceding OTA software restart. A single native Restart Board command recovered
within 7.7 seconds including state verification: reset reason `Reboot request
from api`, saved command 0/open 75/closed 0, PWM inactive. Reset/heap/loop entities
are now available for future failures. This demonstrates successful software
restart on independent power, not repeated loaded cold-start reliability.
Before duct installation, test repeated independent-supply cold starts and
sustained operation with the actual servo load; check supply/EN wiring if failure
recurs. Firmware cannot release an externally held reset pin.

Pre-rollout Builder YAML backup: `\\192.168.20.101\config\backups\ventsys-persistence-20261010`.
Build logs and binaries are outside the vault in the local temporary
`ventsys-persistence-20261010` workspace (valve build workspaces retain their
previous names); rebuild from canonical YAML with the stated ESPHome version.

MAIN-2 reports the ESP32 internal die temperature, not valve or enclosure
temperature. Its configured LED alert levels begin at 60°C, 70°C, and 80°C.
The owner's 2026-10-10 report of a sustained reading at or above 57°C is not
diagnosed by this source change. Keep the board's temperature entity visible
and investigate board placement, supply, and airflow if the reading rises or
persists near the notice threshold.


October 19 command repair: running API log handshakes/subscriptions confirm FDM
`.62` retains `ventsys-sla-360-valve` / `ventsys/sla/360/control`, SLA `.61`
retains `ventsys-fdm-360-valve` / `ventsys/fdm/360/control`. Builder copies differ;
do not infer deployed topics or flash from those copies without reconciling them.
Firmware remains owner-accepted. E2 native HA host corrected `.51`→`.52` and
recovered; no power/restart/actuation command was sent. See the dashboard manual.

## FDM print normal valve — October28 USB installation

MAC `EC:E3:34:B4:76:A4` verified before erase/upload on COM4; ESP32-D0WD-V3,
4MB. Canonical `configs/esphome/ventsys_fdm_print_valve.yaml` now uses the
current normal three-wire profile: GPIO16 servo, GPIO33 touch, no feedback ADC.
Static IP `192.168.50.55`, MQTT `ventsys/fdm/valve/control` and `/state`.
Provisional pulse range940–2000us; logical endpoints0/100 require physical
calibration. No movement command was sent.

Firmware validator passed. ESPHome2026.4.5 on Python3.12 compiled successfully;
esptool erase followed by ESPHome USB upload returned four verified write hashes.
Factory SHA256: `d55b62471a0e37fcfe4851ee00e4b2ee59c51e897532d8265ab9fd7de210e9db`.
Canonical source SHA256: `83bb95ad3bdabae16302a58fe935b9b5de9bf38de06e2a03be6c615d24db12fb`.
Canonical, staged and new live Builder YAML were byte-identical.

Private evidence/builds: `C:/Users/Admin/.codex/tmp/ventsys-fdm-print-20261028`.
Commands used Python at `C:/Users/Admin/.codex/tmp/ventsys-esphome312/Scripts/python.exe`:
`-m esphome compile <staged-yaml>` then
`-m esphome upload <staged-yaml> --device COM4 --upload_speed 115200`.
Old partition table and NVS region were backed up; whole-flash backup stalled
and was cancelled. These partial backups cannot restore the previous firmware.
Rebuild this role from canonical YAML and private HA secrets for recovery.

MQTT TLS connected and HA adoption in Garage succeeded. Dashboard/native API
reported display50%, open100%, closed0%, PWM off, None since boot; this does not
verify physical angle. October29 owner reports the board unplugged. Repower,
then verify calibration, touch/remote motion and loaded stability before use.

## SLA print normal valve — October29 USB installation

Normal three-wire ESP32-D0WD-V3 board MAC `EC:E3:34:1B:DB:2C` identified on
COM4 and rechecked before erase/upload. Target `ventsys-sla-print-valve`, static
`192.168.50.56`, MQTT `ventsys/sla/valve/control` and `/state`; GPIO16 servo,
GPIO33 touch, no feedback ADC. Physical touch installation remains unverified.
The current normal FDM print profile was adapted for SLA; provisional940–2000us
pulse window and logical0/100 endpoints require this valve's physical calibration.

ESPHome2026.4.5/Python3.12 compilation and firmware validator passed. Original
4MB flash read completed before erase (SHA256
`b197f5b7ab4737cf2c06331c94d95f888eb8b2bef927e047c8478c94e2f63795`).
Private recovery image/evidence: `C:/Users/Admin/.codex/tmp/ventsys-sla-print-20261029`.
Use the same explicit Python runtime and compile/upload commands as FDM above,
substituting `ventsys_sla_print_valve.yaml`; USB upload115200 returned four
verified write hashes. Factory SHA256:
`7126b8f6d02d113ba8fc7bda633d16751c4c6feecd5204d8e7fe633fb56931b4`.
Source SHA256:
`cb33a339a6f1eef2fb9bed5e295d9039db20df8bba64175b4efda08d17a757d7`.
Canonical, staged and new Builder YAML match; shared management package matches.
No prior SLA print Builder file existed. DHCP source inventory updated only;
firmware uses the planned static address, no router deployment required.

MQTT TLS and HA adoption in Garage verified. Native startup reports seed50%,
open100/closed0, PWM off, None since boot, physical position unknown. No movement
command was sent. Touch, remote travel, endpoints and sustained load remain pending.
For rollback, verify this MAC, then write the private full flash image at address0;
it contains the previous role/preferences and must not be used on another board.

Possible future calibration UI: separate manual observed-position acknowledgement
from movement commands; acknowledgement must not enable PWM or imply feedback.
Correct future travel still requires measured/jogged pulse endpoints or mechanical
horn alignment. No manual-reference feature was implemented in this installation.

## November4 intake touch and retention acceptance

Both installed ESP32-C6 intakes now use external digital touch input GPIO2,
with pulldown so a disconnected input stays inactive,50ms debounce and a3s
startup guard. GPIO1 remains the LED, GPIO0 the servo. C6 has no native touch
peripheral: this requires an external touch module's digital output, not a bare
capacitive pad. Physical touch response remains owner acceptance work. Each press
toggles configured30/60 endpoints. Firmware retains deployed identities/topics:
physical SLA `.61`/CC:BA:97:F0:E3:EC uses `ventsys-fdm-360-valve` and fdm/360;
physical FDM `.62`/A0:85:E3:AE:5B:C8 uses `ventsys-sla-360-valve` and sla/360.
Canonical v2_nerdiy files represent physical roles; preserve these legacy wire
identities. Both MACs were verified before OTA. ESPHome2026.4.5 builds and uploads
passed. Old misleading hyphenated Builder YAMLs were retained in
`/config/backups/ventsys-ui-20261104-1/legacy-builder-*`; active Builder files now
match canonical underscore profiles. Legacy ESP32/non-C6 templates are explicitly
marked unsuitable for these installed C6 boards.

SLA raw report changed from60 before the first touch update to30 afterwards.
Restore flags alone had not proved migration of the old saved value. Exact cause
of that initial loss remains unproven. A later deliberate restart test ran before
the new OTA image's default60s acceptance window and rolled back to the previous
image (compilation time09:19:21, missing new diagnostic/action). That failed test
is not persistence acceptance and is distinct from the initial value loss.

Both C6 profiles now expose read-only PWM Commanded Active and a bounded API
maintenance action `record_known_command(position)` (raw30–60 only). It rejects
nonfinite/out-of-range values or active PWM, saves through the number's native
entity-preference key, synchronizes flash, then publishes state. It never invokes
number.set, servo.write or drive_valve_to. This records a previously known command,
not measured angle or mechanical calibration. It is not connected to ordinary
UI position controls, which continue to require confirmation and drive normally.

Used the known pre-update SLA60 as the reference with PWM off. After waiting75s
for the image to be accepted, native Restart Board recovered the SAME firmware
image and raw60, endpoints60/30, PWM false, touch false. Final input-pulldown OTA
also compared pre/post native command and both endpoints: SLA60/60/30 and
FDM30/60/30 retained with PWM false. No servo/fan command or mechanical test was
sent. Private JSON evidence/builds: `K:/Documents/Codex-builds/ventsys-nov4`.

Required future update gate for every valve: capture MAC, running identity/build,
native command, both endpoints and PWM status before upload; verify intended
profile against running firmware (Builder filename alone is not authority).
After upload, wait beyond OTA acceptance and compare all saved values before
claiming success; test restart only after the image is accepted and verify the
same image returns. If a value differs, stop acceptance and investigate; never
issue a motion command merely to correct the displayed state. All11 canonical
valve variants pass persistence/no-boot-drive source gates, but only the stated
installed boards have this session's runtime proof. Loaded cold starts and all
physical positions remain unverified.

Installed sensor MAC CC:BA:97:F0:D0:C0 at `.32` is FDM (owner correction), now
`ventsys_fdm_sensor.yaml` / ventsys-fdm-sensor, ESPHome2026.9.1 encrypted OTA.
HA reconfiguration and entry/device/entity display labels updated. Its BME0x77,
SDA4/SCL5, ADC3 and LED2 were preserved; retained old40C threshold is deliberately
unchanged pending commissioning. Former `ventsys_sla_sensor.yaml` includes the
new source for compatibility and must not be treated as a separate SLA device.

C: filled during compilation before any upload. Only generated task build/cache
files were moved to `K:/Documents/Codex-builds`; the interrupted toolchain was
preserved as an incomplete folder and reinstalled there. Future sensor9.1 builds
use process-local ESPHOME_ESP_IDF_PREFIX=`K:/Documents/Codex-builds/idf` and TEMP/TMP
under the same outside-vault build root. No private secrets or build caches were
added to the vault. Use explicit private Python runtimes listed in build evidence.

### Offline firmware report comparator

`main/tools/ventsys_firmware_check.py BEFORE.json AFTER.json` compares two
independently acquired native reports without connecting to or controlling a board.
Each JSON object requires `mac`, numeric `position`, `open`, `closed`,
`pwm_active: false`, and `accepted_image: true`. Capture the actual values and
confirm the image acceptance window independently; this tool does not acquire
reports or verify timestamps, board authenticity, physical position, or build
identity. Exit0 means values/identity match, exit1 means a difference, exit2
means invalid or insufficient evidence. Private report files should stay outside
the vault. Three unit tests cover match, mismatch and invalid evidence.

November4 capture improvement: `main/tools/ventsys_capture_valve_report.py`
can collect a native API snapshot without issuing commands. It verifies the
expected MAC, requires position/endpoints and PWM inactive, records firmware
build and requires uptime >=90s plus explicit independent image-acceptance
confirmation. Supply the API key only in private process environment variable
`VENTSYS_ESPHOME_API_KEY`; specify the route/tunnel host/port, expected MAC and
an output file outside the vault. Compare two snapshots with
`ventsys_firmware_check.py`. It does not establish physical valve position or
prove bootloader acceptance from uptime alone. Mocked identity/missing-evidence
tests and a read-only E2 `.52` native capture passed. Older boards without a
PWM diagnostic fail indeterminate rather than claiming success. OTA upload and
post-update comparison are not yet automatically coupled.

## FDM CO firmware — November 10

The FDM `.32` board (MAC `CC:BA:97:F0:D0:C0`) now runs the CO-capable `ventsys_fdm_sensor.yaml` after encrypted OTA. It retains GPIO2 plain status LED, GPIO3 CO input, GPIO4/5 BME680 at `0x77`, device identity and 40 C threshold. ESPHome 2026.9.1 build `11:02:34 +0000`, config hash `0x1585cc4c`; the HA Builder source matches. The former smoke-labelled channel was removed. Allow 180 seconds after boot, check CO fault is off and voltage stable, then use the CO clean-air baseline button; verify the resulting Rs/R0 ratio and full notification path. No smoke sensor or calibrated ppm measurement is implied.
