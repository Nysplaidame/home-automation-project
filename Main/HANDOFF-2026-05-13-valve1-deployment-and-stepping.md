# HANDOFF — Main Valve 1 deployment & mode-stepping architecture rework

**Date:** 2026-05-13
**Scope:** Bring `ventsys-main-valve-1` from "not flashed, MAC unknown" to "fully integrated and controllable from the dashboard with smooth server-side ramping on mode changes." Refactor HA token storage out of the dashboard source. Set up dual-target display (garage Pi kiosk + HA UI iframe card).

---

## TL;DR for the next agent committing to git

This session touches **3 modified files** and adds **2 new files** to the repo. There are also **2 files on the HA host that must NEVER be committed** (live secrets). There is **1 live OpenWrt firewall rule** that is NOT yet reflected in `configs/openwrt/firewall-config.conf` and will be wiped by the next `deploy.ps1` run unless added to source or replaced by the TLS migration.

Suggested commit plan is at the bottom of this document under "GIT COMMIT GUIDANCE".

---

## CONTEXT: how the session started

User reported Windows could not access COM5 (the device that needed flashing was a Silicon Labs CP210x USB-UART bridge connected to an ESP32 dev board). User had a `Valve - Colours, PWM Stop, Temp Mon, Temp Alarm Working - copy.yaml` (the prototype YAML, not the production one) and bootloader logs. They wanted to identify the device (get its MAC) and flash the correct production YAML.

The "correct" YAML turned out to be `G:\home-automation-project\main\configs\esphome\ventsys_main_valve1.yaml` (production, VLAN 50 identity, pre-TLS MQTT). The G: copy was the authoritative source-of-truth, modified 2026-05-12; the D: copy was stale (last touched 2026-03-19).

---

## DEVICE IDENTITY (confirmed in this session)

| Field             | Value                            |
| ----------------- | -------------------------------- |
| Device name       | `ventsys-main-valve-1`           |
| Chip              | ESP32-D0WD-V3 rev v3.1            |
| MAC address       | `EC:E3:34:B4:79:7C`               |
| Static IP         | `192.168.50.51` (VLAN 50, HomeIoT) |
| ESPHome API port  | `6053` (noise-encrypted)         |
| OTA port          | `3232`                            |
| MQTT broker       | `192.168.20.101:1883` (plain, pre-TLS path) |
| Control topic     | `ventsys/main/valve1/control`    |
| State topic       | `ventsys/main/valve1/state`      |
| HA entity         | `number.main_duct_valve_1`       |

---
## CHRONOLOGICAL SUMMARY (what happened, in order)

### 1. COM5 lock investigation

- Windows reported `Access to the path 'COM5' is denied.` when trying to flash.
- Diagnosed: Brave browser running the web.esphome.io USB log viewer was holding the port via the Web Serial API (exclusive lock). Identified by the `[hh:mm:ss]` timestamp pattern in the user's saved logs (specific to that page's UI) and by finding a Brave window titled "Web - ESPHome - Brave" with PID 3260.
- User closed Brave; COM5 freed.
- **No repo changes from this step.**

### 2. Discovery: device had no firmware

- Reading the saved bootloader logs revealed the device was in a continuous restart loop:
  `E (197) esp_image: image at 0x1d0000 has invalid magic byte (nothing flashed here?)`
  `E (209) boot: No bootable app partitions in the partition table`
- Both OTA app partitions were empty. The user's belief that "the YAML can be verified as working via the LED being on" was incorrect — the LED on was either the board's red power LED or a stale WS2812 latched color from a previous flash. The YAML was never running.

### 3. MAC retrieval via esptool

- Python 3.13 was installed at `C:\Users\Administrator\AppData\Local\Programs\Python\Python313\` but `esptool` was not installed.
- Installed esptool 5.2.0 via `pip install --user esptool`.
- Added the user-site Scripts dir (`C:\Users\Administrator\AppData\Roaming\Python\Python313\Scripts`) to the user PATH via the .NET `[Environment]::SetEnvironmentVariable` API. Also cleaned up duplicate Python PATH entries (trailing-slash dedupe issue).
- Ran `esptool.exe --port COM5 read_mac`. MAC: **`ec:e3:34:b4:79:7c`**.
- **No repo changes from this step.** PATH change is on the user's Windows machine only.

### 4. First flash and `secrets.yaml` line-10 syntax error

- User flashed the production YAML via the ESPHome dashboard.
- HA-side compile failed with: `Invalid YAML syntax ... in "/config/esphome/secrets.yaml", line 10, column 65: expected <block end>, but found '<scalar>'`.
- Cause: in the user's pasted secrets, line 10 had two YAML keys concatenated with no newline between them: `printAirPipe_AirFlowSensor_web_server_password: "<redacted>"wifi_ssid: "HomeIoT"`. The closing `"` of the redacted web-server password was at column 64, `wifi_ssid` began at column 65 — exactly where the parser reported.
- There was also a trailing duplicate `wifi_ssid: "HomeIoT"` at the end of the file.
- **REPO CHANGE:** Rewrote `G:\home-automation-project\main\configs\esphome\secrets.yaml` with the line split and the duplicate removed. (File mtime: 2026-05-12 ~14:00.)

### 5. MQTT credential rotation

- User changed MQTT broker credentials. Old: `ventsys_esphome` / `<old MQTT password>`. New: `mqtt` / `<new MQTT password>`. Credential values are stored in Bitwarden and intentionally redacted here.
- **REPO CHANGE:** Updated `G:\home-automation-project\main\configs\esphome\secrets.yaml` with the new credentials. (Final mtime: 2026-05-12 16:14:14.)
- User did the equivalent edit on `/config/esphome/secrets.yaml` on HA.
- Note: this file is now out of sync with the HA-side version's superset of keys (the HA-side has the `printAirPipe_*` placeholder keys for not-yet-deployed devices; G: only has the keys main_valve_1 actually uses). This is fine — `!secret` lookup is lazy.

### 6. Cross-VLAN firewall block on MQTT

- After re-flash, device showed `socket errno: 104 (Connection reset by peer)` on `192.168.20.101:1883`. ESPHome dashboard (running inside HA on VLAN 20) connected to the same broker fine — proving the broker was up and the credentials valid.
- Diagnosed: VLAN 50 → VLAN 20 firewall on the OpenWrt router permits port 8883 (TLS) but blocks 1883. Confirmed by reading `G:\home-automation-project\main\configs\openwrt\firewall-config.conf` v3.0, which has a comment block in the "SAFETY & SECURITY RULES" section explicitly anticipating this: `# TEMP rule for first-flight before TLS: iot_sensors -> 192.168.20.101:1883`.
- User picked **option 1** (open 1883 temporarily) over **option 2** (finish TLS deployment).
- **LIVE-SYSTEM CHANGE (NOT IN REPO):** User added a UCI firewall rule on the router:
  ```
  uci add firewall rule
  uci set firewall.@rule[N].name='TEMP VentSys MQTT plain valve1 to HA'
  uci set firewall.@rule[N].src='iot_sensors'
  uci set firewall.@rule[N].src_ip='192.168.50.51'
  uci set firewall.@rule[N].dest='automation'
  uci set firewall.@rule[N].dest_ip='192.168.20.101'
  uci set firewall.@rule[N].proto='tcp'
  uci set firewall.@rule[N].dest_port='1883'
  uci set firewall.@rule[N].target='ACCEPT'
  uci commit firewall
  /etc/init.d/firewall restart
  ```
- First attempt: rule was at the bottom of the firewall list, AFTER the blanket `Block IoT to Automation` REJECT — so the REJECT fired first and the ACCEPT never matched. Fixed with `uci reorder firewall.@rule[TEMP_idx]=BLOCK_idx`.
- MQTT then connected successfully. Confirmed in valve log: `[I][mqtt:348]: Connected`.

### 7. ESPHome dashboard "offline" indicator

- After successful MQTT, the ESPHome dashboard still showed the device as offline (red dot) even though logs streamed.
- Diagnosed: the dashboard's "online" indicator uses MQTT-based discovery (publishes `esphome/ping/<name>`, listens for `esphome/discover/<name>`), not the API log connection. The discovery cache was stale from before MQTT was working.
- Fix: restart the ESPHome add-on, which clears the discovery cache. User confirmed this resolved it.
- **No repo changes from this step.**

### 8. Dashboard integration and double-actuation bug

- User added the valve to the main HA dashboard via `number.main_duct_valve_1`. Slider control worked smoothly.
- Verified the ventilation dashboard at `ventsys-dashboard.html` was already wired for valve 1: MQTT command topic `ventsys/main/valve1/control` matched between dashboard, HA package (`ventsys_ha_package.yaml`), and the valve firmware. HA entity binding to `number.main_duct_valve_1` was also already in place at L2331.
- User reported that clicking a mode button (e.g. PURGE) caused the valve to snap fully open, snap back, then ramp slowly to the new position. The slider drag continued to work fine.

### 9. Root cause: two parallel command paths

Clicking PURGE triggered both:

- **Path A:** `applyMode('purge')` → `haCallScript('script.ventsys_mode_purge')` → HA published the target value once to `ventsys/main/valve1/control`. Valve snapped to 100.
- **Path B:** `_origApplyMode('purge')` → `animateValveTo('valve-main-1', 100, 2000)` ran a 125-frame eased animation. The animation called `updateValveVisual` on each frame, which (post-override) called `haPublish`, publishing ~125 incremental MQTT commands over 2 seconds starting from near-0.

Visible result: snap to 100 (path A) → snap back to near-0 (first frames of path B) → slow ramp to 100 (rest of path B).

### 10. First fix attempt — REVERTED

- Initially I patched `animateValveTo` and `animateIntakeTo` to use `_origUpdateValveVisual` / `_origUpdateIntakeVisual` (the pre-override visual functions that do not publish), to stop the 125-publish-per-click flood. This left the HA script's single immediate publish as the sole command, which would have produced a snap-to-target with no ramp.
- User pushed back: the slow stepping IS the intended behaviour by design — the original "snap then slow ramp" was actually "unwanted snap, followed by intended slow ramp." Removing the stepping was wrong.
- **REVERTED both edits** before any backup was taken on my side (user already had their own backup).

### 11. Architecture fix: option 3 — move stepping to HA scripts

Moved the slow-ramp logic from client-side JS animation into HA's mode scripts, so:

- Stepping applies regardless of trigger source (dashboard click, automation, voice, REST API).
- Single source of truth for valve position commands.
- The dashboard animation becomes purely cosmetic — visual mirror of HA state coming back via WebSocket.

**REPO CHANGES (file-by-file):**

#### `G:\home-automation-project\main\ventsys\ventsys_bundle_updated\ventsys_ha_scripts.yaml`

Rewritten from scratch. Backup of the original is at `ventsys_ha_scripts.yaml.bak-20260512` in the same directory. The new file:

- Adds a reusable `ventsys_ramp_valve` helper script. Parameters: `topic`, `entity_id`, `target`, optional `duration_ms` (default 2000). Reads the entity's current state, then publishes a 40-step linear ramp from current to target over `duration_ms` milliseconds (50ms per step at default). Helper has `mode: parallel max: 16` so multiple valves can ramp simultaneously inside a `parallel:` block. Early-exits if `delta == 0` (already at target).
- Rewrites all 12 mode scripts (`ventsys_mode_sealed`, `ventsys_mode_fire_safe`, `ventsys_mode_purge`, `ventsys_mode_booth`, `ventsys_mode_booth_seal`, `ventsys_mode_fdm_print`, `ventsys_mode_fdm_enclosure`, `ventsys_mode_fdm_purge`, `ventsys_mode_fdm_seal`, `ventsys_mode_sla_print`, `ventsys_mode_sla_enclosure`, `ventsys_mode_sla_purge`, `ventsys_mode_sla_seal`) to call `script.ventsys_ramp_valve` from a `parallel:` block instead of issuing immediate `mqtt.publish` to the valve control topics.
- Fan commands (`ventsys/fan/control`, `ventsys/spray-fan/control`, `ventsys/fan/percent`) are still one-shot `mqtt.publish` — they don't need ramping.
- Mode semantics (which valves go where, fan states, fire-safe behavior) are unchanged from the backup. Only the per-valve command path changed.
- File grew from 13014 bytes / 13 scripts → 21097 bytes / 14 scripts (12 modes + helper + 1 historical script that was already there).
- Comment headers explain the architecture, including a note that `duration_ms` can be overridden per call if a future review decides some mode needs faster snap.

#### `G:\home-automation-project\main\ventsys\ventsys_bundle_updated\ventsys_ha_scripts.yaml.bak-20260512` (NEW FILE)

Exact byte copy of the pre-rewrite scripts file. Keep until the new version is verified stable in production for at least a week. Listed under "files that should NOT be committed" in some teams' practice but on this project the convention seems to be commit-everything — your call.

#### `G:\home-automation-project\main\dashboards\ventsys-dashboard.html`

Two narrow edits and a bigger refactor.

**Edits to `animateValveTo` and `animateIntakeTo`** (around L1685 and L1717 respectively):
- Replaced `updateValveVisual(valveId, currentPosition)` with `_origUpdateValveVisual(valveId, currentPosition)`.
- Replaced `updateIntakeVisual(enclosure, currentPosition)` with `_origUpdateIntakeVisual(enclosure, currentPosition)`.
- Effect: the visual animation no longer publishes MQTT commands. The HA mode script is the sole publisher. Slider drag still uses the overridden version (which publishes) — that's correct, manual drag should publish per frame.
- Both edits carry a `// 2026-05-12: ...` comment explaining the rationale.

**External config loader refactor** (token externalization):
- Added a `<script src="ventsys-config.js" onerror="..."></script>` tag immediately before the main inline `<script>` block (~L1342). Onerror handler logs a console warning if the file is missing.
- Added a merge block immediately after the `const HA_CONFIG = { ... };` closing brace (~L2390). It calls `Object.assign(HA_CONFIG, window.VENTSYS_CONFIG)` if `window.VENTSYS_CONFIG` exists.
- Comment block above HA_CONFIG warns: "Token MUST stay as the placeholder here. The real production token lives in /config/www/ventsys-config.js on the HA host (NOT in this repo)."
- Effect: the dashboard HTML in the repo always has `token: '__SET_HA_TOKEN__'` as a placeholder. The real token lives in a separate file (see below) on the HA host. Re-deploying the HTML can never clobber the production token again.
- Final file size: 148453 bytes (was 145453).

#### `G:\home-automation-project\main\dashboards\ventsys-config.js.example` (NEW FILE)

Template config file. Documents how to set up `ventsys-config.js` on the HA host. Includes:
- Step-by-step instructions for generating a long-lived token in HA.
- `window.VENTSYS_CONFIG = { token: 'PASTE_YOUR_LONG_LIVED_TOKEN_HERE' };` template.
- Optional override examples (wsUrl, entities, etc.).
- Security warning: do NOT commit the real `.js` (without `.example`) to source control.
- Suggested `chmod 600` if the HA host shares `/config/www`.

This file IS safe to commit. The actual `ventsys-config.js` (no `.example` suffix) only exists on the HA host and contains the real token — see "FILES ON HA HOST, NOT IN REPO" below.

#### `G:\home-automation-project\main\dashboards\ventsys-card-wrapper.html` (NEW FILE)

Auto-scaling wrapper that lets the same 1024×600-native dashboard be embedded in arbitrary-sized Lovelace iframe cards. Created in response to the user wanting two display targets:
- Garage 7" screen via Raspberry Pi 4 (1024×600 native, fullscreen) — uses `/local/ventsys-dashboard.html` directly.
- HA UI on a PC monitor (varied card sizes) — uses `/local/ventsys-card-wrapper.html`, which embeds the dashboard in a `<iframe>` with a CSS `transform: scale(...)` driven by JS.

Implementation: ResizeObserver watches the wrapper's outer box; on resize, JS computes `scale = min(boxW/1024, boxH/600)` and applies it to the inner iframe with `transform-origin: center`. Letterbox behaviour on aspect-ratio mismatch (preserves entire dashboard); switch to `Math.max` if fill-with-crop is preferred later.

### 12. Verification of stepped ramping

After both `ventsys_ha_scripts.yaml` and `ventsys-dashboard.html` were deployed to HA, user confirmed: "the valve actuates smoothly now via dashboard." Single ramp on mode click, no snap-and-revert.

Intermediate state (only YAML deployed, dashboard not yet) was diagnosed via a grep test: `grep -c "2026-05-12: animation is now purely cosmetic" /config/www/ventsys-dashboard.html` returns 1 if the dashboard is the new version, 0 if it's still the old one. (Note: I initially told the user it should return 2, but only the `animateValveTo` edit uses that exact phrase — `animateIntakeTo`'s comment says "cosmetic only" instead. The correct expected value is 1.)

### 13. Token clobbering side-issue and the externalization fix

When the user redeployed the new dashboard HTML to `/config/www/ventsys-dashboard.html`, it overwrote their production token (which had been pasted inline into the previous deployment's HA_CONFIG) with the repo placeholder `__SET_HA_TOKEN__`. DevTools console showed "no token setup, running in demo mode" and the dashboard couldn't connect to HA.

User picked **option B** (external config file, two-file split) over option A (localStorage). Implementation captured in the `ventsys-dashboard.html` and `ventsys-config.js.example` changes above. User re-generated a long-lived token, created `/config/www/ventsys-config.js` with it, hard-refreshed; dashboard came back online.

---

## FILES ON HA HOST, NOT IN REPO (do NOT commit)

These exist only on the Home Assistant filesystem and contain live secrets:

| Path on HA                            | Content                                                                  |
| ------------------------------------- | ------------------------------------------------------------------------ |
| `/config/esphome/secrets.yaml`        | ESPHome secrets — should mirror `G:\...\configs\esphome\secrets.yaml` but may have additional keys for other devices. Reference only; updates flow G: → HA. |
| `/config/www/ventsys-config.js`       | The long-lived HA token in `window.VENTSYS_CONFIG = { token: '...' }`. Created this session. Must be regenerated if HA auth store is reset. |
| `/config/packages/ventsys_ha_scripts.yaml`         | Live copy of the mode scripts. Mirror of `G:\...\ventsys\ventsys_bundle_updated\ventsys_ha_scripts.yaml`. Reload after every git pull. |
| `/config/www/ventsys-dashboard.html`  | Live copy of the dashboard. Mirror of G: copy. |
| `/config/www/ventsys-card-wrapper.html` | Live copy of the wrapper. Mirror of G: copy. NEW this session. |

The `.gitignore` should contain (if not already):
```
ventsys-config.js
```
(Without the `.example` suffix — the example template IS tracked.)

---

## LIVE-SYSTEM CHANGES NOT YET IN SOURCE-OF-TRUTH

### OpenWrt router firewall

UCI rule added manually this session:

```
firewall.@rule[N]:
  name='TEMP VentSys MQTT plain valve1 to HA'
  src='iot_sensors'
  src_ip='192.168.50.51'
  dest='automation'
  dest_ip='192.168.20.101'
  proto='tcp'
  dest_port='1883'
  target='ACCEPT'
```

Position: just BEFORE the `Block IoT to Automation` REJECT rule (achieved via `uci reorder`).

**This rule is NOT in `G:\...\configs\openwrt\firewall-config.conf`.** The source spec only has a *comment block* describing it. The next `tools\router-deploy\deploy.ps1` run will wipe this rule when the router gets re-flashed from source.

Three resolution paths:
1. Add the rule to `firewall-config.conf` under the `# TEMP rule for first-flight before TLS` comment, without the `TEMP` prefix in the name (the deploy toolkit's first-flight profile strips rules whose names start with `TEMP`).
2. Complete the TLS migration (see "OUTSTANDING WORK" below) which makes this rule unnecessary.
3. Live with the rule getting wiped on each redeploy and re-adding it manually each time. (Not recommended.)

### Windows host PATH

The agent's working host (the user's Windows PC) has these directories in user PATH (deduplicated to one entry each):
- `C:\Users\Administrator\AppData\Local\Programs\Python\Python313\`
- `C:\Users\Administrator\AppData\Local\Programs\Python\Python313\Scripts\`
- `C:\Users\Administrator\AppData\Roaming\Python\Python313\Scripts` (esptool lives here)

The third entry was added this session. Not in source-of-truth (host-local), but worth knowing if another agent inherits the same machine.

---

## REPO FILES MODIFIED OR ADDED THIS SESSION (definitive list)

All paths relative to `G:\home-automation-project\`.

### Modified (3)

```
main/configs/esphome/secrets.yaml
main/dashboards/ventsys-dashboard.html
main/ventsys/ventsys_bundle_updated/ventsys_ha_scripts.yaml
```

### Added (2)

```
main/dashboards/ventsys-config.js.example
main/dashboards/ventsys-card-wrapper.html
```

### Backup file present (optional commit)

```
main/ventsys/ventsys_bundle_updated/ventsys_ha_scripts.yaml.bak-20260512
```

Whether to commit `.bak-*` files is a project-style choice. If your repo convention is "no backup files in git," delete it before commit; the prior version is recoverable from history anyway. If your convention is "preserve operational backups inline," commit it.

### Handoff document (this file)

```
main/HANDOFF-2026-05-13-valve1-deployment-and-stepping.md
```

---

## VERIFICATION CHECKLIST (what's confirmed working)

- ✅ Device flashed and running production firmware (compile timestamp `2026-05-12 13:39:16 +0100`).
- ✅ WiFi connects: `192.168.50.51` on HomeIoT VLAN 50.
- ✅ MQTT connects: `192.168.20.101:1883`, authenticates as `mqtt`.
- ✅ ESPHome native API connects: HA shows the device, all entities populate.
- ✅ Slider drag on main HA dashboard publishes commands; valve responds.
- ✅ Mode click on ventilation dashboard triggers smooth 2-second ramp; no snap-back.
- ✅ Dashboard re-authenticates via external `ventsys-config.js` after restart.
- ✅ Card wrapper file exists and is syntactically valid HTML; NOT YET tested in an HA iframe card (deployment by user is the next step).
- ✅ Garage Pi 4 setup instructions provided to user; kiosk deployment NOT YET attempted.

---

## OUTSTANDING WORK FOR FUTURE SESSIONS

### High priority

1. **TLS migration for MQTT.** The broker has TLS live on `8883` per the handoff trail; only `ventsys_main_valve1.yaml` is configured for plain `1883`. The other 17 device YAMLs in `main/configs/esphome/` use `port: 8883` + `certificate_authority: !secret mqtt_ca_cert`, and `mqtt_ca_cert` is NOT present in either `secrets.yaml`. Until this is resolved, no other VentSys device can be deployed. Steps: (a) `cat /ssl/ca.crt` on HA, copy into both `secrets.yaml` files (G: and HA) as a YAML literal block scalar (`mqtt_ca_cert: |` then indented cert), (b) switch `ventsys_main_valve1.yaml` to `port: 8883` + `certificate_authority: !secret mqtt_ca_cert`, (c) re-flash main_valve_1 wirelessly to verify TLS works on the same device that's currently on 1883, (d) remove the TEMP firewall rule, (e) flash the remaining 17 devices.

2. **Either bake the TEMP firewall rule into source or remove it via TLS migration.** Doing the TLS migration first is preferred — it cleans up both issues in one go.

### Medium priority

3. **HA card wrapper deployment.** User wants the dashboard accessible in HA's UI as well as on the garage Pi. The card wrapper is ready; user needs to (a) copy `ventsys-card-wrapper.html` to `/config/www/`, (b) create a new dashboard via `Settings → Dashboards`, (c) add an iframe card pointing at `/local/ventsys-card-wrapper.html` (suggested aspect_ratio: `58%` for tight fit, or `panel: true` + `aspect_ratio: 0%` for fullscreen view). Spec was provided in the chat; not yet executed.

4. **Garage Pi 4 kiosk deployment.** Recipe was provided (Chromium kiosk flags + LXDE autostart entries). User has not yet stood up the Pi. URL target: `http://192.168.20.101:8123/local/ventsys-dashboard.html`. Pi needs no token-specific config since `ventsys-config.js` is served from HA.

### Low priority / future review

5. **Race protection on rapid mode clicks.** All 12 mode scripts currently use HA's default behavior (queue subsequent calls). If user clicks mode A then B quickly, two ramps race because `ventsys_ramp_valve` has `mode: parallel max: 16` — publishes interleave, valve oscillates briefly. Easy fix when wanted: add `mode: restart` to each of the 12 mode script definitions. Not done by default because it changes queue semantics that user may want to keep.

6. **Page-init `updateValveVisual(id, 0)` calls at L2187 of dashboard.** These work today by accident of declaration order (override is defined LATER in the file, so init runs against the pre-override pass-through). If anyone reorders the script, page-load will publish `0` to every valve topic on each refresh. Adding a comment and/or using `_origUpdateValveVisual` explicitly would harden this.

7. **`restore_value: no` on the valve number entity.** After power cycle, firmware thinks valve is at 0% but servo's physical position is wherever it was last commanded. First slider touch will jump the valve. Switch to `restore_value: yes` when scale-up makes this a real concern.

8. **D: tree is stale.** `D:\Other computers\NOT A COMPUTER\home-automation-project\` is an older copy of the same project (last touched 2026-03-19 on the YAMLs). Either delete it or sync from G: to avoid future confusion about which is canonical. G: is the active source-of-truth.

---

## GIT COMMIT GUIDANCE

Suggested split into logical commits. All paths under `main/`.

### Commit 1 — `valve1: bring online with corrected secrets`

```
main/configs/esphome/secrets.yaml
```

Message body:
> Fix line-10 syntax error (two YAML keys on one line, no separator) and remove
> trailing duplicate `wifi_ssid`. Rotate MQTT credentials from `ventsys_esphome` /
> `<old MQTT password>` to `mqtt` / `<new MQTT password>` to match the new
> broker config. Required for ventsys-main-valve-1 to authenticate to Mosquitto.

### Commit 2 — `ventsys: server-side stepped valve ramping via reusable helper`

```
main/ventsys/ventsys_bundle_updated/ventsys_ha_scripts.yaml
main/ventsys/ventsys_bundle_updated/ventsys_ha_scripts.yaml.bak-20260512  (optional)
```

Message body:
> Introduces script.ventsys_ramp_valve helper (40 steps over 2000ms by default,
> parallel mode max 16). Rewrites all 12 mode scripts to call the helper from a
> parallel: block instead of publishing immediate values per valve.
>
> Effect: valves now ramp smoothly from current → target over ~2 seconds regardless
> of trigger source (dashboard, automation, voice, REST). Replaces the previous
> snap behaviour with controlled motion. Fan commands remain one-shot.
>
> Mode semantics (target values, fan states, fire-safe routing) are unchanged.

### Commit 3 — `dashboard: extract HA token into deployment-local config + cosmetic-only animation`

```
main/dashboards/ventsys-dashboard.html
main/dashboards/ventsys-config.js.example
```

Message body:
> Two related changes:
>
> 1. animateValveTo and animateIntakeTo now use _origUpdateValveVisual / 
>    _origUpdateIntakeVisual (no MQTT publish). The HA mode script is the sole
>    publisher of valve positions. Slider drag is unchanged (still publishes per
>    pointer event via the override). Fixes oscillation seen when both client-side
>    animation and server-side ramp tried to drive the same valve.
>
> 2. Externalize HA_CONFIG.token to /config/www/ventsys-config.js on the HA host.
>    Inline placeholder stays in the repo; an external file (loaded via 
>    <script src=...>) sets window.VENTSYS_CONFIG which is merged into HA_CONFIG 
>    at runtime. Prevents the repo HTML from clobbering production tokens on 
>    redeploy. Template at ventsys-config.js.example.
>
> Reminder: add `ventsys-config.js` (without .example) to .gitignore.

### Commit 4 — `dashboard: add auto-scaling wrapper for HA UI embed`

```
main/dashboards/ventsys-card-wrapper.html
```

Message body:
> Adds a small HTML wrapper that embeds ventsys-dashboard.html in an iframe 
> with a ResizeObserver-driven CSS transform: scale() to fit arbitrary card
> sizes while preserving aspect ratio. Enables the same source HTML to drive
> both the garage Pi 4 kiosk (native 1024×600) and HA Lovelace iframe cards
> (any size). Deploy to /config/www/ alongside the dashboard.

### Commit 5 — `docs: handoff for valve1 deployment and stepping rework`

```
main/HANDOFF-2026-05-13-valve1-deployment-and-stepping.md
```

Message body:
> Session handoff documenting the deployment of ventsys-main-valve-1, the
> architecture rework that moved valve stepping from client-side animation
> to server-side HA scripts, and supporting changes (token externalization,
> card wrapper). Includes file inventory, live-system changes not yet in
> source, and outstanding work — most notably the TLS migration which 
> blocks deployment of the remaining 17 devices.

---

## NOTES ON THE WORKING ENVIRONMENT (for the next agent)

Two recurring gotchas that bit this session:

1. **Google Drive sync silently no-ops some writes.** The `create_file` and `str_replace` MCP primitives sometimes report success but the file on G: is unchanged. Verified workaround: write via PowerShell's `[System.IO.File]::WriteAllText` / `AppendAllText` with explicit `New-Object System.Text.UTF8Encoding $false` for no-BOM UTF-8. This bypasses whatever sync layer was eating the writes. Desktop Commander's `edit_block` also generally works on G:. After every G: write, verify with a `Get-Item` mtime check before assuming the edit landed.

2. **ssh.exe is blocked in the sandbox.** Spawning `ssh.exe` (any args, even `-V`) exits with code 255 producing zero bytes on stdout and stderr. This appears to be Microsoft Defender ASR rule on script-spawned binaries from the agent's account (which runs as `win-uqqr9jbf7a3\nameofuser`, not `Administrator`). Cannot SSH to the router or HA from this environment. Use the user as a human-in-the-loop for any router or HA-shell commands.

3. **MCP `write_file` can hang past 4 minutes on large content.** During the scripts file rewrite, one chunked write_file call hung. Recovery: kill the process, switch to PowerShell direct-write via [System.IO.File]::AppendAllText for the remainder. State was preserved correctly mid-write.

4. **Python invocations occasionally hang the agent's process slot.** `python.exe` startup got slow-scanned by AV during the session, causing two Python-based tool calls to time out (one for PyYAML, one for the spec check). Avoid Python for quick validation — PowerShell's `Select-String` and string ops are sufficient for most YAML/HTML structural checks.

---

## END OF HANDOFF
