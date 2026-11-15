# HANDOFF - Sensor array display / SDP810 / HA package / carriers

**Date:** 2026-11-14
**Scope:** OLED + LDR + SDP810 added to the sensor array (firmware, case, wiring), splice carriers, HA-side gap closure, first flash of FDM array 1.
**Status:** Follow-through completed in HA on November 14. Historical notes below are superseded by the current-state section immediately below.

## Current state / resume

FDM `.31` adopted natively; pressure around -0.03 Pa with no DP fault. Dashboard `20261114-6` live: new FDM source bindings, separate pressure equality/sign panel, full enclosure tint, corrected green FDM outlines, grey/green fan status, heartbeat-backed zero RPM. SLA stored latch acknowledged and remains clear; no active fault observed. Garage MQTT patch checked/reloaded. Native alarm sources added to existing enabled risk publishers and validated/reloaded. Canonical detail: [[docs/procedures/ventsys-dashboard]] and [[docs/reference/current-live-state]].

Carrier screen SCAD/preset/STL and bezel STL copied from K:/Download to `assets/3d-printing/Sensor Carrier/`; original source files preserved. Wiring HTML artifact remains uncaptured.

Remaining physical work: confirm tubing polarity and zero with both ports equalized; inspect SDP pins; capture new `.31` CO/smoke baseline in known clean air; print/measure/dry-fit bezel; fit/flash other arrays; supervised end-to-end alarm/plug/phone acceptance. Do not assume calibrated CO ppm, pressure accuracy, or commissioning. Existing `.32` and `.37` CO baselines are present; `.31` remains unset. BME680 baseline-change warning remains a separate design task.

Follow-on: sensor trends and Activity tabs live; widened five-source environment; pressure icons and per-board detail/history/ack/maintenance panels; persistent activity automation. See canonical dashboard manual and [[docs/audits/2026-11-14-ventsys-history-and-telemetry]]. Maintenance shutdown is implemented but was not exercised on real boards; reconnect power before reactivation. Fan RPM is an explicitly labelled off-report indicator without tachometry. Physical source placement, graph interaction, alarm/shutdown/reconnect and safety acceptance remain open.

## Historical session notes (superseded where stated above)

## 1. Live state right now

- **FDM array 1** (`ventsys-fdm-array-1`, 192.168.50.31, prefix `ventsys/fdm/array_1`) flashed over USB (COM7) with `ventsys_fdm_array_1.yaml` with `dp:` and `display:` packages **enabled** (repo file edited).
  - Wi-Fi ("HomeIoT") and MQTT connect. OLED works after rewiring.
  - SDP810: boot log shows `sdp3x: Soft Reset failed`. That is only a warning in the driver (setup continues; it marks FAILED only if the ID read or start-measurement fails, and neither was logged). **No pressure value has been seen yet.**
  - Status LED not connected (intentional). Bent SDP810 pins (pitch narrower than the connector) - check for bridges.
- **HA**: the board is NOT in the ESPHome integration (registry has no entity for it; the old "garage_sla_enclosure_sensor_array_1" device is different/older firmware). Native entities (`differential_pressure`, `dp_sensor_fault`, display switches) will not exist until it is added (host 192.168.50.31, port 6053, key = `api_key` in ESPHome `secrets.yaml`). mDNS may not cross VLAN 50 -> 20, so add by IP.
- **HA packages**: `ventsys_array_mqtt.yaml` copied to `\\192.168.20.101\config\packages\` (auto-loaded by `!include_dir_named packages`). **HA config check / reload NOT done.** Both risk-publisher automations ship `initial_state: false`.

## 2. What was built (repo paths under `main/`)

- `configs/esphome/ventsys_air_sensor_base.yaml` - globals `dp_pa`, `dp_fault_active`, i2c 400 kHz, ids `wifi_rssi`/`uptime_s`/`ip_addr`; `any_fault` includes the dp fault.
- `configs/esphome/ventsys_air_sensor_dp.yaml` (new) - sdp3x, `dp_zero_offset`, `dp_capture_zero` button, `dp_sensor_fault`, MQTT `<prefix>/diff_pressure` (Pa).
- `configs/esphome/ventsys_air_sensor_display.yaml` (new) - SSD1306 0x3C, status bar + 3x2 grid (DP, TEMP, RISE, SMOKE, CO, RH), alarm takeover, diagnostics page, 1 px burn-in shift, LDR (GPIO0) auto-brightness. Needs the `co:` package.
- `configs/esphome/ventsys_{fdm,sla}_array_{1,2}.yaml` - `display_title` + `# dp:` / `# display:` include lines. **Only fdm_array_1 has them enabled.**
- `docs/diagrams/wiring-diagrams/ventsys_wiring_reference.md` - splice, SDP810, OLED/LDR wiring, GPIO map (GPIO2 CO, 3 smoke, 4 SDA, 5 SCL, 0 LDR, 8 WS2812, 1 spare).
- `assets/3d-printing/Splice Carrier/` - original `ventsys_i2c_power_splice.*` plus **v2** `ventsys_i2c_power_splice_v2.scad/.stl/_preview.png`: feedback-carrier dimensions (plate 1.8, recess 0.8, 100nF pocket 4.8x5.9, 10k pocket 6.3x2.2), 3V3 / GND / LDR rails 1.5 wide, every feature has its own labelled position/size parameters (one decimal), 27.1 x 18.6 mm. README has a v2 section.
- `ventsys/ventsys_bundle_updated/ventsys_array_mqtt.yaml` (new) - MQTT entities for both arrays of FDM and SLA: CO, diff pressure, humidity, alarm latched, fault, high temp (+ temp/IAQ/smoke for array 2), and risk publishers `ventsys_{fdm,sla}_risk_publish` -> `ventsys/{fdm,sla}/risk/state` (retained; FIRE_RISK if any array has latched alarm, smoke, CO or high temp).
- `ventsys/ventsys_bundle_updated/ventsys_ha_package.yaml` - garage topics changed to `ventsys/garage/air/...`, F-28 note updated. `ventsys_ha_optional.yaml` (draft, not loaded) - baro topics now `ventsys/{fdm,sla}/array_1/baro_pressure` and `ventsys/garage/air/baro_pressure`.

## 3. NOT in the repo (user holds these)

- **Carrier case**: `ventsys_sensor_carrier-screen.scad` (latest, with OLED surround, LDR pocket, bezel group 19, insert shift settings), its JSON (preset **"New set 2"** is the real defaults), STLs. Recommend saving them under `assets/3d-printing/` (suggest a `Sensor Carrier/` folder). Keep CRLF line endings. A preset's `part_to_generate` overrides `-D`.
- **Wiring diagram HTML** (artifact https://claude.ai/artifact/UZMJUdugzsLHWEZFsVXU4M, version 2) - not saved in the repo.
- Bezel plate STL (`ventsys_oled_bezel.stl`) built from the above.

## 4. Case details worth knowing

- OLED sits on top of the lid in a surround on 4 standoffs; only the 4-pin header goes through a lid slot. OLED module 27 x 27.9, holes 2.1 dia at 1.6 from both edges.
- **Bezel plate** (`part_to_generate = oled_bezel`): window 4.1 mm from the header-end edge to 8.5 mm from the cable-end edge, 24 wide; recess for the 2.5 mm solder tips; recess for the 11.5 mm flex cable; glass recess covering the lower black bezel strip; plate is 4.1 mm thick. Settings are in group 19. New heat-set-insert shift/spacing settings are in the BME680 and smoke/CO groups (the smoke group applies to CO as well).
- Recommended SDP810 ports pointing down, drip loop on L.

## 5. Open items / next steps (rough priority)

1. **HA**: Developer tools > YAML > check configuration, reload; add the ESPHome device (see section 1); confirm the new MQTT entities appear.
2. **Verify SDP810**: `dp_sensor_fault` off; ~0 Pa idle with both ports open; blow into H = positive, L = negative; press `dp_capture_zero` with ports open.
3. Merge the garage-topic fix into the **live** `/config/packages/ventsys_ha_package.yaml` (lines ~690-750 still `ventsys/garage/<x>`). **The live file is an OLDER version than the repo bundle** (e.g. `ventsys/fdm/temperature`, not `.../array_1/...`) - do not overwrite it with the repo copy. Back it up first.
4. After the array is stable (no latched alarm/CO/smoke; CO baseline captured), **enable the two risk-publisher automations** - they feed `ventsys_fire_risk_cutoff` (printer plugs off + fail-safe on). Booth still has no publisher / board.
5. Enable `dp:`/`display:` in the other array configs as hardware is fitted; flash them.
6. Print the bezel plate and dry-fit; measure and update the guessed values below.
7. Save carrier SCAD/JSON and the wiring diagram into the repo; redraw the wiring diagram/doc for the v2 splice (circuit unchanged); update `TO-DO.md`, `PROJECT-INDEX.md` and `main/README.md` status table.

**Values still assumed - measure**: glass top edge 3.5 mm from the header-end edge; glass bottom edge 5.4 mm from the cable-end edge; flex cable height 1.5 mm; window width 24; glass width 26.6; OLED PCB 1.6 / glass 1.5 / header plastic 2.5 / header row 2.0 from edge; I2C address 0x3C; 10uF ceramic pocket (uses 4.8 x 5.9 - radial 10uF is often ~5 x 6). Glass recess leaves only ~0.25 mm wall beside it - may print poorly (try `oled_bezel_fit` 0.1).

## 6. Gotchas for the next session

- **Flashing**: the PC's ESPHome (Pinokio miniconda, 2025.7.5) is too old - esp32 `board` is required, while the config uses `variant: esp32c6` only. A venv with ESPHome 2026.9.1 was created at `%TEMP%\esphome_venv` (may be gone). Command used: `esphome run ventsys_fdm_array_1.yaml --device COM7 --no-logs`.
- **Secrets**: no `secrets.yaml` in the repo (gitignored). The build copied `\\192.168.20.101\config\esphome\secrets.yaml` into a temp build folder with the configs and deleted it afterwards. Never write secrets or the Samba password into tracked files.
- Full compile only works with internet (PlatformIO, fonts); the cloud sandbox cannot compile. `esphome config` validation works there.
- A built-in-browser load of the HA UI failed (private address approval); HA files are readable/writable through the Samba share.
- OpenSCAD nightly: `K:\Documents\3D Design\OpenSCAD (Nightly)\openscad.exe`. The `device_bash` tool was unavailable; Desktop Commander `start_process` (PowerShell) works.
- Use `expectedMtimeMs` guards when writing repo files via the device bridge; repo files may be CRLF.

### FDM array reconnect and LDR test — November 14, 23:23 UTC

FDM array1 `.31` returned online. BME680 readings, SDP810 and both gas ADC channels reported data, and the gas warm-up timer completed. At the final check CO and smoke detection, combined sensor fault and latch were off. CO/smoke Rs/R0 readings were unknown because clean-air baselines remain unset. No functional gas challenge or calibrated measurements were established.

During owner-directed LDR cover/light checks, ambient_light varied rapidly from approximately 3–64%, during the test, including after the light was applied. Single readings were 4.5% covered and 4.6% immediately after lit, then 53.6% shortly afterward. A stable directional response was not demonstrated. Check the GPIO0 LDR divider and supply/ground connections before relying on automatic display brightness. The board briefly reconnected around 23:20 and uptime reset; owner said power lead may have been disturbed. Temperature 23.5 C, humidity 43%, barometric pressure 992.8 hPa, differential pressure -0.047 Pa and Wi-Fi -62 dBm were observed. Pressure tubing orientation and equalized zero remain unverified.

### November14 23:34 UTC — reboot and LDR/OLED retest

Owner rebooted `.31`. LDR remained erratic, varying roughly 0–58% during cover/shine testing. OLED remained physically dark with `display_enabled` on, dark-off temporarily disabled and minimum brightness temporarily increased to 100%. Both temporary settings were restored to original dark-off on and minimum 5% afterward. SDP810 differential pressure was unknown with `dp_sensor_fault` and combined fault on after reboot. BME680 temperature and barometric pressure updated, fault off, but humidity stayed at 100% since reboot, unlike ~43% before reboot. CO and smoke fault/detection and latch flags were off after warm-up. No active gas challenge or baseline calibration was performed.

Physical checks remain: with power disconnected inspect 3V3/GND/SDA/SCL branches and individual connectors for OLED and SDP810 (the BME working shows the whole bus is not necessarily down); confirm LDR divider 3V3 -> LDR -> GPIO0 -> 10k -> GND and check humidity reading after wiring is stable. Verify display module pin labels. Do not infer a failed part from these observations alone. See wiring reference.

### November14 23:43 UTC — FDM array power-on follow-up

Owner powered `.31` back on and confirmed OLED shows a picture. SDP810 recovered with differential pressure around -0.044 Pa and its fault off. BME680 humidity returned to ~41% with temperature/pressure updating. Gas warm-up completed, CO/smoke detection, combined fault and alarm latch off, CO ~1.28 V and smoke ~0.37 V. R0 baselines remain unset, and no gas challenge was performed.

LDR remains unstable after power cycle. Owner reported covered for 20 seconds, readings fluctuated about 8–34% around that interval. After owner reported direct light, recent readings ranged about 6–31%; the two ranges overlap and a reproducible directional response was not demonstrated. Continue divider/connection checks and controlled retesting. Pressure zero/tubing orientation remain unverified.
