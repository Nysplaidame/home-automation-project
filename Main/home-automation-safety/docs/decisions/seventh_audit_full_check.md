# HOME AUTOMATION SAFETY VAULT
# Seventh Audit — Full Vault Check
# March 2026

---

## Scope

Every file in the vault was read for this audit:
configs/esphome/* (all 25 YAMLs), configs/home-assistant/* (automations, configuration, bambuddy package),
configs/openwrt/* (vlan, dhcp, firewall, wireless), configs/frigate/* (config.yml, docker-compose.yml),
configs/proxmox/* (vm-setup.sh, vm-configs.conf), ventsys/ventsys_bundle_updated/* (ha_package, ha_scripts,
ha_optional, fan/valve controllers), scripts/monitoring/health_check.sh, docs/secrets_reference.md,
and supporting files including the combined audit report.

---

## Part 1 — Status of Prior Audit Findings

### Fixed since last audit

| Prior ID | Item | How verified |
|---|---|---|
| A8 | printairpipe-controller.yaml backwards TLS comment | Comment now correct: Stage 1 = 1883, Stage 2 = 8883 |
| B5/G5 | Wireless channel description corrected | wireless-config.conf CHANNEL ALLOCATION section correct |
| B6 | Redundant duplicate VPN interface in vlan-config.conf | Removed; wg0 is the only WireGuard interface |
| B7 | VPN zone assignment missing from firewall | firewall-config.conf VPN zone references wg0; fix comment present |
| C7 | ventsys_ha_optional.yaml no header warning | File now has DO NOT LOAD header and full prerequisites list |
| C8 | health_check.sh only monitored 2 boards | Now monitors all 17 ESP32 boards + 8 smart plugs |
| C9 | P1S health check used TCP to port 8883 | Now uses ping; fix comment explains why |
| D4 | No startup safe state for VentSys | ventsys_startup_safe_state automation added to automations.yaml |
| F9 | 8 missing ESPHome firmware YAMLs | All now present in configs/esphome/ |
| F11 | No master secrets reference | docs/secrets_reference.md created with all 10 sections |
| G3 | Router-only DNS domain entries | dhcp-config.conf now has per-VLAN domain entries |
| H1 | DNS/DHCP rules used src='*' including WAN | Firewall rules removed; comment explains zone-default approach |
| H2 | SSH exposed to WAN | SSH WAN rule removed; fix comment explains VPN-only access model |
| H3 | HA brute-force protection disabled | ip_ban_enabled: true, login_attempts_threshold: 5 in configuration.yaml |

### Still open from prior audits (summary)

The following findings from the combined report remain unresolved. Detailed descriptions are in combined_audit_report.md. Listed here for tracking:

A1, A2, A3, A4, A5, A6, A7, A9 — MQTT port documentation in setup guides and package comments
B1 — phase_3 DHCP guide has wrong device count and wrong names
B3 — phase_4 firewall guide references /tmp path
B4, B8, B9, B10 — phase_4, phase_7, phase_8 guide issues
B13, B14, B15, B16, B17 — Proxmox guide and VLAN 60 planning
C1 — phase_3 uses hostname 'ventsys-sla-valve' instead of 'ventsys-valve-controller'
C2, C3 — frigate_vm_setup_guide inline compose errors
C4 — p1s_ventsys_fdm automations referenced but unimplemented
C5, C6 — Booth Valve and Booth Risk entities not marked UNIMPLEMENTED
C10 — HA VM setup guide Next Steps omits Bambuddy
C11 — bambuddy package header comment references port 1883 as permanent
C12 — Docker images unpinned (Frigate stable, Bambuddy latest)
C13 — Humidity data published by firmware but no HA sensor subscribed
D1 — Fire emergency calls purge (activates spray booth fan)
D2 — Mode scripts not atomic (don't reset prior paths)
D3 — booth_seal doesn't close main-1
D5 — FIRE_RISK topic has no publisher anywhere
D6 — mqtt_reconnect_alert targets binary_sensor.mqtt_broker_online, entity is binary_sensor.mqtt_broker
D7 — Smart plug entity IDs assumed; deployment note added but not validated
F1 — No dedicated fire-safe emergency ventilation script
F2 — No FDM+SLA simultaneous mode script
F3 — Sensor board adoption procedure not documented
F5 — Frigate MQTT TLS steps missing from TLS guide
F7 — Backup runbook cross-reference wrong
F8 — P1S serial placeholder: deployment blocker documented but serial not yet substituted
F10 — No unified MQTT TLS migration checklist
G1 — unit_of_measurement: "C" should be "°C" (ventsys_ha_package.yaml)
G6 — No git history warning in backup_strategy.md
G7 — Obsidian wikilinks in UCI config comment blocks
G8 — ESPHome device names partially mismatched with DHCP hostnames (main fan)

---

## Part 2 — New Findings

Severity scale: CRITICAL / HIGH / MEDIUM / LOW

| ID | Sev | File | Summary |
|---|---|---|---|
| ~~N-1~~ | ~~HIGH~~ | ~~bambuddy_p1s_package.yaml~~ | ~~p1s_print_failed notification broken by YAML duplicate key~~ — **RETRACTED**: `title`, `message`, and `data` are three distinct keys under the outer `data:` mapping. Not a YAML duplicate key. `data.data.priority` is valid HA notification extras syntax. Notification fires correctly. |
| N-2 | HIGH | printairpipe-controller.yaml | SLA temperature threshold hardcoded, not parameterisable |
| N-3 | HIGH | configs/frigate/docker-compose.yml | RTSP and MQTT passwords explicitly set to empty, overriding .env |
| N-4 | MEDIUM | automations.yaml | pressure_diff_fault threshold `below: 5` always true — sensors measure in hPa (range ±0.1), so fires continuously once optional package is loaded |
| N-5 | LOW | configs/esphome/ | No `ventsys_main_fan.yaml` in `configs/esphome/` — canonical file lives only in the bundle as `ventsys_fan_controller.yaml`. IP is correct (.21). Organisational inconsistency only. |
| ~~N-6~~ | ~~HIGH~~ | ~~automations.yaml~~ | ~~esphome_device_offline_fdm targets non-existent entity ID~~ — **RETRACTED**: `ventsys_fan_controller.yaml` has `friendly_name: VentSys Main Fan` and `binary_sensor: name: "Status"`, generating exactly `binary_sensor.ventsys_main_fan_status`. The YAML even documents this match in a comment. Entity ID is correct. |
| ~~N-7~~ | ~~HIGH~~ | ~~ventsys_ha_package.yaml~~ | ~~Booth smoke sensor entity missing; booth absent from fire detection chain~~ — **RETRACTED**: by design, fire detection is limited to FDM and SLA enclosures only. The booth has no smoke sensor and no fire detection requirement. |
| ~~N-8~~ | ~~HIGH~~ | ~~automations.yaml~~ | ~~No high-temperature automations for spray booth enclosure~~ — **RETRACTED**: by design, temperature-based safety automations are only required for the FDM and SLA enclosures. |
| N-9 | MEDIUM | ventsys_ha_package.yaml | IAQ unit "IAQ" incorrect — firmware publishes ohms (Ω) |
| N-10 | MEDIUM | health_check.sh | ESPHome plug boards (.73-.76) checked by ping instead of port 6053 |
| N-11 | LOW | wireless-config.conf | Duplicate/stale channel comments in main_2g and admin_2g interfaces |
| N-12 | MEDIUM | configs/esphome/ sensor wrappers | Sensor YAML wrappers are incomplete — cannot be flashed as-is |
| N-13 | LOW | configs/esphome/ sensor wrappers | Sensor wrapper quick-reference list omits garage sensor |
| N-14 | MEDIUM | all valve YAMLs | Servo level mapping uses only half range; mounting orientation undocumented |
| N-15 | MEDIUM | ESPHome plug YAMLs | MQTT TLS + API encryption on ESP8266 1MB flash — known RAM risk |

---

## Detailed Findings

### N-1 — RETRACTED

`title`, `message`, and `data` are three distinct keys inside the outer `data:` mapping — not a YAML duplicate key. The nested `data.data.priority` is HA's standard pattern for passing service-specific notification extras. PyYAML parses this correctly and the notification fires as expected. No action required.

---

### N-2 [HIGH] printairpipe-controller.yaml — SLA temperature threshold hardcoded, not parameterisable

The `high_temp_alarm` binary sensor uses a hardcoded lambda threshold:
```yaml
lambda: 'return id(enclosure_temperature).state > 55.0f;'
```

The comment says: 'Change to 40 in the SLA board substitution.' However, there is no `high_temp_threshold` substitution variable in the file. The four substitutions defined (`device_name`, `friendly_name`, `device_ip`, `mqtt_topic_prefix`) do not include a temperature threshold. The per-device sensor wrapper files (`ventsys_sla_sensor.yaml`) also do not include a threshold substitution.

Any operator deploying the SLA sensor board using the wrapper will get the FDM threshold of 55°C on a board where 40°C is the safety limit. An SLA enclosure reaching 55°C without triggering an alarm is a significant safety gap — resin is typically stored and cured below 40°C to prevent spontaneous polymerisation.

Suggested fix: Add a substitution variable `high_temp_threshold: "55.0"` to printairpipe-controller.yaml and use `${high_temp_threshold}` in the lambda. Set it to `"40.0"` in ventsys_sla_sensor.yaml and ventsys_booth_sensor.yaml substitutions.

---

### N-3 [HIGH] configs/frigate/docker-compose.yml — RTSP and MQTT passwords set to empty, overriding .env

The docker-compose.yml environment section contains:
```yaml
environment:
  - FRIGATE_RTSP_PASSWORD=
  - FRIGATE_MQTT_PASSWORD=
```

In Docker Compose, the syntax `VARIABLE=` explicitly sets the variable to an empty string, which OVERRIDES any value defined in .env. The notes section instructs operators to set these in .env, but as written, both will always be empty. The result:
- Camera streams will fail to authenticate (cameras reject empty RTSP password)
- Mosquitto will reject Bambuddy's MQTT connection (empty password fails authentication)

The correct syntax to allow .env to supply the value is `VARIABLE` without an equals sign:
```yaml
  - FRIGATE_RTSP_PASSWORD
  - FRIGATE_MQTT_PASSWORD
```

This is a deployment blocker that will cause silent authentication failures without an obvious error message.

---

### N-4 [MEDIUM] automations.yaml — pressure_diff_fault threshold always true

The `pressure_diff_fault` automation triggers `below: 5` on `sensor.fdm_pressure_differential` and `sensor.sla_pressure_differential`. These are template sensors defined in `ventsys_ha_optional.yaml` that compute `enclosure_pressure − garage_pressure` in hPa. Normal operating values when the fan is extracting are approximately −0.01 to −0.10 hPa. That is always below 5. The automation therefore fires continuously for 5 minutes after the fan starts (the `for: minutes: 5` delay), then re-triggers repeatedly while the fan runs.

The intent is to detect a blocked valve or fan fault — a situation where the fan is running but no pressure differential is building. The correct trigger direction is the opposite: `above: -0.01` (differential is not negative enough, meaning extraction is not happening). The current `below: 5` direction is wrong.

Note: if the optional package is not loaded, these entities don't exist and the automation silently never fires. It only becomes a problem once the optional package is activated.

Suggested fix: Change `below: 5` to `above: -0.01` (or calibrate the threshold against measured values during commissioning). The `for: minutes: 5` delay is appropriate and should be kept.

---

### N-5 [LOW] configs/esphome/ — ventsys_main_fan.yaml missing from configs/esphome/

The canonical per-device fan firmware lives in `ventsys/ventsys_bundle_updated/ventsys_fan_controller.yaml` with the correct IP (192.168.50.21, updated by F-23 fix) and correct name (`ventsys-main-fan`). Every other device in the fleet has a corresponding file in `configs/esphome/` (e.g. `ventsys_booth_fan.yaml`, `ventsys_fdm_sensor.yaml`). The main fan has no such file there, creating an inconsistency in where an operator would look for it.

This is an organisational issue only — the firmware is correct and complete in the bundle location.

Suggested fix: Either create `configs/esphome/ventsys_main_fan.yaml` pointing to (or copying) the bundle YAML, or add a note in `configs/esphome/` documenting that the main fan firmware lives in the bundle.

---

### N-6 — RETRACTED

`ventsys_fan_controller.yaml` has `friendly_name: VentSys Main Fan` and `binary_sensor: platform: status, name: "Status"`. HA's native API integration generates `binary_sensor.ventsys_main_fan_status` from these — and the YAML even documents this explicitly in an H-1 fix comment. The automation's target entity ID is correct. No action required.

---

### N-7 — RETRACTED

By design. Fire detection (smoke sensors, temperature alarms) is limited to the FDM and SLA enclosures. The spray booth has no smoke sensor and no fire safety automation requirement. ventsys_booth_sensor.yaml publishes environmental data (temperature, humidity, IAQ) for ambient reference only. No action required.

---

### N-8 — RETRACTED

By design. High-temperature safety automations are only required for the FDM and SLA enclosures. No temperature-based automation is needed for the spray booth. No action required.

---

### N-9 [MEDIUM] ventsys_ha_package.yaml — IAQ unit is "IAQ" but sensor publishes ohms

```yaml
  - platform: mqtt
    name: FDM IAQ
    unit_of_measurement: "IAQ"
```

The printairpipe-controller.yaml firmware publishes BME680 gas resistance in ohms (Ω). The automations `poor_air_quality_fdm` and `poor_air_quality_sla` correctly use ohm-based thresholds (5000 Ω and 8000 Ω). However, the HA entity displays "IAQ" as the unit, which will confuse anyone reading the sensor history, energy dashboard, or graphs — they will see values like "4200 IAQ" rather than "4200 Ω".

This also means HA will not apply the correct sensor device class for gas resistance (there is no "IAQ" device class; the correct one would be `volatile_organic_compounds` or just omit device_class and use "Ω" as unit).

Suggested fix: Change `unit_of_measurement: "IAQ"` to `unit_of_measurement: "Ω"` on both FDM and SLA IAQ entities. Remove or omit the `device_class` field, or use `device_class: volatile_organic_compounds` if the HA version supports it.

---

### N-10 [MEDIUM] health_check.sh — ESPHome plug boards (.73-.76) checked by ping instead of ESPHome API port

The VENTSYS_PLUGS array (checked by ping) includes:
```
192.168.50.73  plug_uv_1       (ventsys-plug-uv-1)
192.168.50.74  plug_uv_2       (ventsys-plug-uv-2)
192.168.50.75  plug_wash_cure  (ventsys-plug-wash-cure)
192.168.50.76  plug_ultrasonic (ventsys-plug-ultrasonic)
```

The comment says "no ESPHome API port — commercial units." However, these are NOT commercial units — they are Avatar AWP02L2 plugs running ESPHome firmware (ventsys_plug_uv1.yaml etc.), which includes the native API on port 6053. Ping only confirms the device is powered on; port 6053 would confirm the ESPHome firmware and native API are running.

The truly commercial Tapo P110 units (plug-fdm-printer .71 and plug-sla-printer .72) are correctly checked by ping since they don't run ESPHome.

Suggested fix: Move the four ESPHome plug entries (.73-.76) from VENTSYS_PLUGS to VENTSYS_BOARDS so they are checked via port 6053. Leave .71 and .72 in VENTSYS_PLUGS (ping only, commercial units).

---

### N-11 [LOW] wireless-config.conf — Duplicate stale comments in two interface blocks

In `main_2g`:
```
# NOTE: channel is set at radio0 level (channel 6) — no per-interface override possible.
```
This comment appears twice in that block (lines are identical).

In `admin_2g`:
```
# NOTE: channel 11 annotation below is informational only — actual channel...
```
followed by:
```
# NOTE: channel annotation below is stale — actual channel is set at radio0...
```
These are two slightly different versions of the same note, both present, which creates confusion about which is authoritative.

Suggested fix: Remove the duplicate in main_2g. Merge the two admin_2g notes into one clear statement.

---

### N-12 [MEDIUM] Sensor YAML wrapper files are incomplete — cannot be flashed as-is

`configs/esphome/ventsys_fdm_sensor.yaml`, `ventsys_sla_sensor.yaml`, and `ventsys_booth_sensor.yaml` contain only a substitutions block plus a comment instructing the operator to copy printairpipe-controller.yaml content manually:

```yaml
# All remaining configuration is inherited from the shared firmware:
# Copy the full printairpipe-controller.yaml content below this header...
```

These files cannot be compiled or flashed by ESPHome in their current state — the ESPHome compiler will error immediately due to missing required components (esphome:, esp32:, wifi:, etc.).

The wrapper pattern (substitutions only) is useful documentation, but creates deployment risk — an operator following the deployment guide may try to flash these files directly and get confusing errors. The ventsys_garage_sensor.yaml is complete and standalone, making the inconsistency more surprising.

Suggested fix: Either complete each wrapper file by inlining the full printairpipe-controller.yaml content (with substitutions pre-filled), or use ESPHome's `packages:` feature to include the shared YAML. The `!include` approach would keep the codebase DRY:
```yaml
packages:
  shared: !include printairpipe-controller.yaml
substitutions:
  device_name: enc-fdm-sensors
  ...
```

---

### N-13 [LOW] Sensor wrapper quick-reference omits garage sensor

All three sensor wrapper files include this quick-reference at the bottom:
```
# Quick reference - change ONLY these four substitution lines per board:
#   FDM board:   device_name: enc-fdm-sensors | ...
#   SLA board:   device_name: enc-sla-sensors | ...
#   Booth board: device_name: enc-booth-sensors | ...
```

The garage sensor (ventsys-garage-sensor at 192.168.50.34, using `ventsys/garage` prefix) is absent from this list. An operator using this reference to create a new sensor board would not know the garage sensor variant exists or what its substitution values should be.

Suggested fix: Add a fourth line: `Garage board: device_name: ventsys-garage-sensor | device_ip: 192.168.50.34 | mqtt_topic_prefix: ventsys/garage` and note that the garage sensor uses a different base YAML (ventsys_garage_sensor.yaml, not printairpipe-controller.yaml).

---

### N-14 [MEDIUM] All valve YAMLs — Servo level mapping uses only half range; orientation undocumented

All valve controllers compute servo position as:
```yaml
servo.write:
  id: valve_servo
  level: !lambda 'return x / 100.0;'
```

In ESPHome, `servo.write` accepts `level` from −1.0 to +1.0. Without `min_level`/`max_level` override, this maps to full servo range (0°–180° on MG90S). The formula `x/100.0` produces levels 0.0–1.0 (only the upper half: 90°–180°). This means:
- At 0% (valve closed): servo at 90° (center position)
- At 100% (valve open): servo at 180° (full right)

For a quarter-turn (90°) butterfly valve this is mechanically correct IF the valve mechanism is mounted so that 90° = fully closed and 180° = fully open. However, if the valve is mounted so 0° = closed and 90° = open, the formula is wrong — the valve would never fully close (it can only reach 90°, which is the physical "closed" position if mounted the other way).

There is no documentation in any wiring reference, build guide, or ESPHome YAML comment specifying which physical orientation is required for this formula to produce correct open/closed positions. Without this, hardware builders may mount the servo either way and get a valve that either never fully closes or never fully opens.

Suggested fix: Add a comment to each valve YAML stating the required mounting orientation. The safest fix is to change the formula to `(x / 100.0) * 2.0 - 1.0` (mapping 0%→−1.0, 50%→0.0, 100%→+1.0, full 180° range) and document the corresponding physical mounting. The `valve_opened_position` and `valve_closed_position` calibration numbers then allow per-valve tuning.

---

### N-15 [MEDIUM] ESP8266 plug YAMLs — MQTT TLS + API encryption on 1MB flash is RAM-critical

`ventsys_plug_uv1.yaml`, `ventsys_plug_uv2.yaml`, `ventsys_plug_ultrasonic.yaml`, and `ventsys_plug_wash_cure.yaml` all configure:
- `mqtt: ca_certificate: !secret mqtt_ca_cert` (MBEDTLS for MQTT TLS)
- `api: encryption: key: !secret api_key` (additional TLS for native API)
- Hardware: ESP8266 `esp01_1m` (1MB flash, ~80KB heap)

MBEDTLS on ESP8266 requires approximately 30–50KB of heap for TLS context. Running two simultaneous TLS connections (MQTT + native API) on an 80KB heap device is likely to cause heap exhaustion, random reboots, or failed connections. The esp01_1m is particularly constrained — it has no PSRAM and the 1MB flash leaves minimal OTA headroom too.

This is a post-TLS-migration concern: in Stage 1 (pre-TLS), these plugs will work fine. After TLS migration, the plugs are at risk.

Suggested fix: Consider one of:
(a) Disable the native API on these plugs (`api:` block commented out) — they only need MQTT for control, and the native API is primarily used for ESPHome dashboard integration and OTA. OTA can still work via MQTT.
(b) Switch to MQTT-only (no TLS) for these low-security plug devices, using a separate Mosquitto listener on 1883 scoped only to plug topics behind the firewall.
(c) Replace the esp01_1m plugs with ESP32-based alternatives that have adequate RAM.

---

## Part 3 — Cross-File Consistency Checks (new this audit)

### MQTT topic consistency across all files

All valve firmware topics match ventsys_ha_package.yaml and ventsys_ha_scripts.yaml:

| Valve | Firmware topic | HA package topic | Scripts topic |
|---|---|---|---|
| Main valve 1 | ventsys/main/valve1/control | ventsys/main/valve1/control | ✓ |
| Main valve 2 | ventsys/main/valve2/control | ventsys/main/valve2/control | ✓ |
| FDM branch | ventsys/fdm/branch/control | ventsys/fdm/branch/control | ✓ |
| FDM print | ventsys/fdm/valve/control | ventsys/fdm/valve/control | ✓ |
| FDM 360 | ventsys/fdm/360/control | ventsys/fdm/360/control | ✓ |
| SLA branch | ventsys/sla/branch/control | ventsys/sla/branch/control | ✓ |
| SLA print | ventsys/sla/valve/control | ventsys/sla/valve/control | ✓ |
| SLA 360 | ventsys/sla/360/control | ventsys/sla/360/control | ✓ |
| Main fan | ventsys/fan/control | ventsys/fan/control | ✓ |
| Spray fan | ventsys/spray-fan/control | ventsys/spray-fan/control | ✓ |

All topic paths are consistent. Dashboard (ventilation_v9k.html) HA_CONFIG.topics matches all of the above.

### IP address consistency

| Device | dhcp-config | ESPHome firmware | health_check | MISMATCH? |
|---|---|---|---|---|
| Main fan | .21 | .81 (ventsys_fan_controller.yaml) | .21 | ⚠️ YES — N-5 |
| Booth fan | .22 | .22 | .22 | ✓ |
| FDM sensor | .31 | .31 | .31 | ✓ |
| SLA sensor | .32 | .32 | .32 | ✓ |
| Booth sensor | .33 | .33 | .33 | ✓ |
| Garage sensor | .34 | .34 | .34 | ✓ |
| FDM airflow | .41 | .41 | .41 | ✓ |
| SLA airflow | .42 | .42 | .42 | ✓ |
| Booth airflow | .43 | .43 | .43 | ✓ |
| Main valve 1 | .51 | .51 | .51 | ✓ |
| Main valve 2 | .52 | .52 | .52 | ✓ |
| FDM branch | .53 | .53 | .53 | ✓ |
| SLA branch | .54 | .54 | .54 | ✓ |
| FDM print | .55 | .55 | .55 | ✓ |
| SLA print | .56 | .56 | .56 | ✓ |
| FDM 360 | .61 | .61 | .61 | ✓ |
| SLA 360 | .62 | .62 | .62 | ✓ |

14 of 17 boards are consistent. Only the main fan controller has an IP mismatch (N-5 above).

### HA entity ID / ESPHome friendly_name consistency

The ESPHome native API `binary_sensor.status` entity ID is derived from the device friendly_name. A mismatch between expected and actual entity ID means the automation target doesn't exist.

| Device | Friendly name | Expected entity ID | Automation uses | Match? |
|---|---|---|---|---|
| Main fan | "VentSys Fan Controller" | binary_sensor.ventsys_fan_controller_status | binary_sensor.ventsys_main_fan_status | ⚠️ NO — N-6 |
| SLA print valve | "VentSys SLA Print Valve" | binary_sensor.ventsys_sla_print_valve_status | binary_sensor.ventsys_sla_print_valve_status | ✓ |
| MQTT broker | friendly_name "MQTT Broker" | binary_sensor.mqtt_broker | binary_sensor.mqtt_broker_online | ⚠️ NO — D6, still open |

---

## Summary by severity

| Severity | New findings | Prior findings still open |
|---|---|---|
| CRITICAL | 0 | D1, D5, F1, F8 |
| HIGH | 2 confirmed (N-2, N-3) — N-1, N-6, N-7, N-8 retracted | D2, D3, D6, F3 |
| MEDIUM | 4 confirmed (N-4, N-9, N-10, N-12, N-14, N-15) | Multiple (see Part 1 list) |
| LOW | 3 confirmed (N-5, N-11, N-13) | G1, G6, G7, G8 |

The confirmed new findings in priority order:
1. N-3 [HIGH] — docker-compose passwords explicitly empty — deployment blocker before first Frigate/Bambuddy start
2. N-2 [HIGH] — SLA (and booth) sensor boards will alarm at 55°C instead of 40°C — no substitution variable for threshold
3. N-4 [MEDIUM] — pressure_diff_fault triggers continuously once optional package loaded — wrong threshold direction
4. N-9 [MEDIUM] — IAQ sensors display unit "IAQ" but firmware publishes ohms (Ω)
5. N-10 [MEDIUM] — ESPHome plug boards .73–.76 checked by ping instead of port 6053
6. N-12 [MEDIUM] — Sensor YAML wrapper files incomplete — cannot be flashed as-is
7. N-14 [MEDIUM] — Servo level mapping underdocumented; mounting orientation required for correct open/close
8. N-15 [MEDIUM] — MQTT TLS + API encryption on ESP8266 1MB flash is RAM-critical post-TLS migration
9. N-5 [LOW] — ventsys_main_fan.yaml absent from configs/esphome/ (organisational only, firmware is correct)
10. N-11, N-13 [LOW] — Duplicate wireless comments; sensor wrapper quick-reference omits garage board
