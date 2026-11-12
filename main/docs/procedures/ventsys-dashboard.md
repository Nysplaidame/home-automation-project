---
title: VentSys authenticated dashboard
created: 2026-10-18
modified: 2026-11-07
type: service-manual
status: live-under-testing
---

# VentSys authenticated dashboard

## Latest acceptance correction — owner-reported control failures

Current frontend is `20261107-8`, with the independent operating-mode package below.
The preceding `20261019-5` / command-repair-1 corrected the owner-reported faults.
Earlier UI/mock/probe acceptance did **not** establish physical responsiveness.
The owner then reported both 360 controls stopping, blocked modes and E2 never
responding. Identified software/connection faults were corrected below; physical
retest is still required. Do not describe the subsystem as physically accepted.

## Current deployment

Open `https://192.168.20.101:8123/dashboard-ventsys/0` through the existing
**Garage Dashboards** sidebar entry. Sign in to Home Assistant normally.
The old `/local/ventsys-dashboard.html` and wrapper URLs redirect there.

Homepage also has a **VentSys** card under Home â†’ Home & Security. Its **Open
tab** action uses `https://homepage.home.local:8188/dashboard-ventsys/0`, the
existing HA proxy used by local and scoped remote clients. That origin has its
own HA sign-in session. No token or embedded control preview is added. The
normal card style is retained and no reachability indicator is presented as
proof of ventilation health. See [[../install/services/homepage]] for its
two-file deployment checkpoint and verification.

Release `20261027-1` is a direct `custom:ventsys-dashboard-card`, deployed at
`/config/www/ventsys-v2/`. It receives HA state and service access from the
authenticated frontend. There is no iframe bridge, public token, separate
WebSocket client, or token passed to the dashboard. The old dedicated
**VentSys Dashboard** credential was revoked, and an independent API request
with it returned HTTP 401. The public config file is now an empty compatibility
object; the card never loads it.

The authenticated migration closed the previous live/canonical split. The
current live release additionally corrects the legacy-ID role
mapping; repository and deployed assets/package match.
The original arbitration revision compiled logical recipes into guarded execution
and reconciled the fire-response main-fan 100% command. The current independent
operating manager supersedes normal recipe execution, as specified below.

## Reading and using the dashboard

- **Clear alarms** opens the currently latched native VentSys board alarms.
  Each board has its own Acknowledge button. The button is disabled while that
  board reports an active CO/smoke/temperature alarm or sensor fault; firmware
  also rejects acknowledgment while an alarm is active. This does not calibrate
  sensors or erase Home Assistant history. The control is available on standard
  and touch layouts. Release `20261107-4` was verified on the live dashboard
  with the SLA pipe latch visible and acknowledgment disabled while its CO
  detection and sensor fault were active.

- Release `20261107-4` adds a live incident banner and source outlines. The
  currently latched SLA pipe alarm and CO sensor fault appear as two orange
  warnings; the generic aggregate fault is suppressed to avoid a duplicate.
  Active red conditions pulse, with text and symbol as well as colour. The
  dashboard session log highlights new red events. The SLA environment panel
  is labelled CO and uses the adopted board's BME680 readings. This is a live
  state display, not a durable incident history. All 42 dashboard browser
  regression tests passed and the live resource/version was verified.
- Release `20261107-6` adds a separate **Diagnostics** tab at
  `/dashboard-ventsys/diagnostics`. It inventories the 294 currently exposed
  VentSys/legacy HA entities in a read-only, searchable board-grouped view:
  reported values, units, entity IDs and time since HA last updated each state.
  This includes CO voltage, BME680 readings, faults, uptime, Wi-Fi, loop time,
  free heap, airflow pulse/wheel readings and valve controller reports where
  those entities exist. Values that have not changed can show an old HA update
  time even while a board remains online; use uptime/status as separate context.
  No actuator or baseline controls are exposed in this view, and a voltage
  absent from firmware cannot be measured by the dashboard. The live tab showed
  the SLA CO voltage near 3.33 V with its sensor fault on and CO detection off.
- Release `20261107-7` adds an orange SLA pipe board connection incident when
  its native status is off, unknown or unavailable, and a separate CO-voltage
  entity-unavailable incident while the board itself reports online. HA sends
  an ntfy warning after the board status has been lost for two minutes and a
  recovery after 30 seconds back online; the transitions are also logged.
  Config validation passed, the new automation loaded in `on` state, and the
  live dashboard version was verified. A real dropout/recovery and phone
  delivery have not been induced or verified. This rule covers the SLA pipe
  board only in that release.
- Release `20261107-8` adds a 12-board expected-online roster. Every adopted
  VentSys board is monitored by default. The Diagnostics tab has a maintenance
  switch for each board: **Start maintenance** pauses that board's dropout ntfy
  alerts; **End maintenance** restores them. Maintenance is shown in blue, and
  an offline board remains visible while its alerts are paused. The switches
  retain their previous state across Home Assistant restarts; new switches
  start off. Eleven boards use uptime availability for dropout and recovery
  notifications; the SLA pipe board retains its status-based rule. An offline
  board is warned after two minutes and recovery is announced after 30 seconds.
  Ending maintenance while a board remains offline warns after two minutes.
  Maintenance pauses board dropout alerts only: CO hardware fault and VentSys
  failsafe notifications remain active. HA config validation passed, all 12
  switches and the general automation loaded, and a live Main duct valve 1
  maintenance on/off cycle updated the dashboard. A real board outage and
  phone delivery remain untested.
- Home Assistant package `ventsys_incidents.yaml` publishes SLA CO hardware
  fault and VentSys failsafe state changes to the internal `monitoring` ntfy
  topic and records transitions in HA Logbook. The package passed HA config
  validation and both automations loaded. A labelled test publish returned
  HTTP 200 from ntfy. Phone delivery is unverified because its subscription
  remains disconnected. Other severity rules, deduplicated persistent incident
  records and bounded repeats remain to be commissioned.

- Select a controller using the duct schematic or the labelled controller
  buttons. The detail panel shows its reported position, source, timestamp and
  firmware range. Standard valves use the restored 0â€“100 scale. The 360 intakes
  intentionally use their correct 30â€“60 controller range; it is not a firmware fault.
- Native ESPHome reports take precedence. An adopted native entity becoming
  unavailable cannot be masked by a retained MQTT number. A number is a
  controller report, not mechanical feedback; physical position stays unverified.
- Committing a slider/number change opens one confirmation popup; Cancel sends
  nothing. There is no Review position/speed button or physical-position field.
  Controller reports remain explicitly labelled. Opening/reloading never sends.
- Grouped Enclosure, Print, Purge and Stop buttons replace the single mode
  dropdown. See the independent operating-mode contract below. Mode actions
  execute directly; Purge first opens its strength chooser. Required missing
  controllers block the complete request rather than silently skipping a path.
- Individual position/fan/speed requests use `script.ventsys_dashboard_command` from
  `configs/home-assistant/ventsys_dashboard_package.yaml`. It validates exact
  kind/target/value combinations and native controller availability/ranges,
  serializes dashboard requests with `mode: single`, uses non-retained MQTT and
  waits up to eight seconds for reports. The client has a twelve-second bound.
  The backend revision below also routes the named mode scripts and legacy valve
  helper through one shared dispatcher; arbitrary direct MQTT/native calls remain
  outside that boundary.
- Smoke alarms cannot be overwritten by a clear fallback. A previously observed
  alarm stays visible across loss of that card's connection until fresh primary
  clear state is available; this local latch is not a durable HA safety alarm.
- Sensors show Unavailable, Offline, Stale or Unit mismatch rather than demo or
  last-known values. The freshness bound is five minutes. A recent temperature
  report from the exact same native sensor prefix can maintain freshness for an
  unchanged binary/humidity/pressure reading; this is board heartbeat evidence,
  not a claim of independently timestamped sampling.
- Absolute pressure is hPa; differential pressure requires a distinct Pa source.
  Gas resistance is raw kÎ©, without a certified IAQ/GOOD rating. Flow wheels show
  individual RPM. No valve-derived CFM or sum of unrelated wheel RPM is displayed.
- Faults name missing/stale sources and include when the card first noticed
  them. This is a session observation time, not a historical failure timestamp.
  The phone layout scrolls through controls/sensors; the duct view remains an
  overview. Keyboard focus, input labels and reduced motion are supported.

## Partial setup and accepted 360 configuration

At acceptance, five of ten actuator report paths were available. Main-1 and
Main-2 native reports were 0; retained MQTT numbers had previously differed.
Two print-valve reports and both fans were unknown, and the adopted E2 native
report was unavailable. These are source observations, not a commissioning state.

The owner confirmed on October 19 that the **360 firmware is correct**, and the
FDM/SLA roles were already swapped in firmware/HA. Do not widen or reflash the
360 firmware for this dashboard correction. Missing sensors/controllers are
expected while setup is incomplete; show them as setup/status notes rather
than assuming hardware faults requiring repair.

The registry still retains pre-swap entity IDs. The corrected bindings are:

| Dashboard role | Board | Native read/confirmation entity | Existing command topic |
|---|---|---|---|
| FDM 360 | `.62`, MAC `a0:85:e3:ae:5b:c8` | `number.ventsys_sla_360_intake_valve_valve_position` | `ventsys/sla/360/control` |
| SLA 360 | `.61`, MAC `cc:ba:97:f0:e3:ec` | `number.ventsys_fdm_360_intake_valve_valve_position` | `ventsys/fdm/360/control` |

These are deliberate legacy-ID bindings, verified against device-registry MACs
and, after the owner-reported failure, actual running-firmware MQTT subscription
logs. The earlier Builder-based claim that command topics were already correct
was wrong: running firmware retains opposite-role topics as well as entity IDs. The dashboard command wrapper is generated from
the same bindings, so request validation and acknowledgement read the same board.
Release `20261019-1` applies this correction and uses the configured 30â€“60
range for intake controls/graphics. It was activated through normal HA sign-in;
the old public token remains revoked. See [[../reference/current-live-state]].

The accepted firmware clamps the existing HA mode payloads 0/100 to its 30/60
endpoints. The generated mode **reported-state** contract now accounts for
that translation, while the mode scripts/firmware stay unchanged. Closed 30
also counts as closed for exhaust-path checks, rather than as a 30% open path.

Release verification passed 22 model, 11 backend and 20 browser tests,
including distinct intake values and rejection of acknowledgement from the
wrong board. Prepared assets, previous assets/package and the candidate
manifest are outside the public directory at:
`/config/backups/ventsys-role-fix-20261019-085025Z/`.
Release activation is complete: HA configuration check passed, no running scripts
matched the state filter, Scripts were reloaded, all five assets were copied,
and the existing resource was updated to `?v=20261019-1`. The signed-in dashboard
showed HA connected, both intake ranges 30–60, standard range 0–100, setup/status
notes and no commands sent. Live files/package match the tested candidate.
The configuration check also reported an unrelated `llamacpp_conversation`
warning for missing `voluptuous_openapi`; no restart was performed.
Keep the private previous assets/package for rollback. No credential was created,
restored or made public.

## Source and verification

Source files are `dashboards/ventsys-card.js`, `ventsys-model.mjs`,
`ventsys-modes.mjs`, `ventsys-dashboard.css`, `ventsys-schematic.svg`, and the
two credential-free legacy launch pages. The SVG preserves the previous duct
layout while removing operational demo values and command handlers.

Run from the repository root:

```powershell
python main/tools/generate_ventsys_dashboard_contract.py
python main/tools/validate_ventsys_contract.py
python main/tools/test_ventsys_dashboard_package.py
node --test main/tools/playwright-smoke/tests/ventsys-model.test.mjs
```

From `main/tools/playwright-smoke`:

```powershell
node node_modules/@playwright/test/cli.js test tests/dashboard.spec.js tests/valve-range.spec.js tests/ventsys-card.spec.js tests/preview-security.spec.js
node tests/audit-behavior.cjs
```

Release acceptance: **20 model tests, 10 backend guard tests and 19 browser
tests passed**, plus the existing 13-mode contract validator and screensaver
behaviour checks. Generated mode expectations match canonical/manual live
scripts. HA validated the package and loaded the new wrapper idle. Its templates
were exercised through the live template API without issuing actuator commands.
Real HA desktop/phone acceptance verified the version, all ten schematic
selectors, native values, no horizontal phone overflow, zero JavaScript errors
and zero startup service calls. Physical movement was not tested.

## Release and recovery

The release tool is `tools/deploy_ventsys_dashboard.py`. It uses the existing
Samba session, verified HTTPS/WSS and the HA Lovelace API; it does not edit
`.storage` directly. Public asset bytes and resource/config read-back are checked.
The installed legacy CA requires Python X.509 strict-flag compatibility; chain
and hostname verification remain enabled.

For later releases, provide a management credential through the private process
environment `VENTSYS_HA_TOKEN`; never through `/config/www/`. The migration
fallback credential in the old backup is now revoked and cannot be reused.

```powershell
python main/tools/deploy_ventsys_dashboard.py stage
python main/tools/deploy_ventsys_dashboard.py activate --backup '<private backup path returned by stage>'
```

Bump the immutable version in the model, its import URLs and deployment tool
for each release. Regenerate the contract and run tests before deployment.
Verify the actual HA card after activation. `refresh --backup ...` updates tested
assets/resource version before repeating acceptance. `secure` is the completed
one-time credential migration, not a normal future deployment step.

The private migration checkpoint is:

`/config/backups/ventsys-dashboard-20261018-225534Z/`

It contains prior dashboard assets, dashboard/resource JSON and `release.json`
with served hashes and actual UI acceptance. The saved config contains the
revoked legacy credential and must remain outside public assets and Git.

Do **not** recover by restoring that credential or old public-token dashboard.
If a later card release fails, restore the last working authenticated assets
and resource version, or temporarily show a read-only/unavailable page while
repairing the card. The existing HA entities/automations remain accessible
independently. The new command package can be removed/restored separately after
checking no script is running and validating HA config before script reload.

## Remaining work

Continue installing hardware as planned. The 360 firmware/role swap and the
dashboard legacy-ID correction are accepted. Named script arbitration and
fire-mode fan-speed drift are resolved in the backend revision below. Physical
commissioning, actual fan/valve sequence acceptance and controls outside the
shared dispatcher remain separate.
No physical safety certification is implied by UI/software acceptance.

Historical findings: [[../audits/2026-10-18-ventsys-dashboard]].
HA custom-card lifecycle reference:
[Home Assistant custom cards](https://contributors.home-assistant.io/frontend/custom-ui/card/).

## Read-only source/runtime drift check

Run `python main/tools/validate_ventsys_contract.py --arbitrated --live-scripts
\\192.168.20.101\config\packages\ventsys_ha_scripts.yaml` from the repository
root (keep the command on one shell line). This only reads YAML; it never calls
HA or MQTT. It compares execution settings and ordered action data, ignoring
presentation/selector metadata. `python main/tools/test_ventsys_script_drift.py`
checks the comparator.

The initial October 19 comparison isolated the fire-response speed omission.
After the backend deployment below, the `--arbitrated` comparison passes against
the compiled runtime. Omitting that option compares against the recipe source,
which intentionally differs in structure from the deployed dispatcher wrappers.

## Shared command arbitration — backend 20261019-arbitration-1

The arbitration deployment initially used frontend `20261019-1`; current
frontend is `20261019-6`. Both backend package files changed together.
All 12 normal mode script IDs, the compatibility valve helper and direct reviewed
dashboard commands now call `script.ventsys_normal_command`. It accepts a bounded
batch of allowlisted VentSys topics and canonical values, validates the entire
batch before publishing, and uses `mode: single` with no queued stale commands.
Overlapping requests are rejected/logged by HA; the dashboard still requires
report confirmation and can time out if its request was rejected or superseded.
Normal-mode reports remain controller reports, not mechanical confirmation.

Before **every** normal publish, failsafe must be explicitly off and the
fire-response script explicitly idle. Unknown state blocks normal commands.
The fire-response script first stops the shared dispatcher, dashboard request,
normal mode wrappers and valve helper. It then directly publishes the canonical
fire recipe, including main fan on/100%, booth fan off and existing valve targets.
It bypasses the normal guard and does not queue behind a normal batch.
No firmware or accepted 30/60 intake endpoints changed. The later command repair
corrects legacy MQTT routing as documented below. A command already handed
to MQTT/device cannot be recalled. Direct MQTT, native number controls and other
unrouted consumers are not globally locked; broker/firmware enforcement is absent.

The canonical mode recipe remains
`ventsys/ventsys_bundle_updated/ventsys_ha_scripts.yaml`. Run:

```powershell
python main/tools/generate_ventsys_dashboard_contract.py
python main/tools/generate_ventsys_arbitration.py
python main/tools/test_ventsys_arbitration.py
python main/tools/test_ventsys_dashboard_package.py
python main/tools/test_ventsys_script_drift.py
python main/tools/validate_ventsys_contract.py --arbitrated --live-scripts '\\192.168.20.101\config\packages\ventsys_ha_scripts.yaml'
```

The selected runtime artifact is
`configs/home-assistant/ventsys_ha_scripts_arbitrated.yaml`. Deploy that as
`/config/packages/ventsys_ha_scripts.yaml`, together with the generated
`ventsys_dashboard_package.yaml`. **Replace** existing files; do not install
additional copies with duplicate script IDs. Do not copy the recipe file over
this runtime. The dashboard deployment tool verifies the matching arbitration
backend before staging future frontend releases.

Verification: eight policy/template/generation tests, 11 dashboard backend tests,
three drift tests and existing contract checks passed. A temporary isolated HA
probe loaded a namespaced copy of the dispatcher/wrappers/fire cancellation,
replaced every MQTT action with test-only text writes and delays, and passed
actual single-mode contention, fire preemption, active-failsafe rejection and
the legacy helper native-numeric-template path. Numeric payloads accept canonical
integer strings or native integers; booleans/floats and noncanonical strings fail.
The probe generator recursively allowlists service actions and test-only targets.
Its helpers/scripts were removed afterward. HA configuration validation passed
with only the pre-existing unrelated `llamacpp_conversation` dependency warning.
No script was running before production reload; the new dispatcher loaded off.
Live package hashes match the selected artifacts. No physical command was sent.

Private recovery checkpoint:
`/config/backups/ventsys-arbitration-20261019-153359Z/`, including previous/new
packages, isolated probe and acceptance manifest. To roll back, restore **both**
previous package files to their original names, validate configuration, and
reload Scripts only while idle. This removes the new arbitration protection
and restores the former fire-speed omission; do not treat rollback as equivalent
control behaviour. Frontend assets/resource version do not change.

Home Assistant lifecycle/mode reference:
[Scripts](https://www.home-assistant.io/integrations/script/).

## Command status display — frontend 20261019-2

The card now observes the shared dispatcher and fire-response script states.
Busy normal execution blocks review/send with a wait message. Missing/unknown
backend state blocks controls. Send rechecks the gate if state changed during
review. Busy execution alone does not interrupt confirmation of our own request.

Failsafe activation/loss, running fire response or backend loss interrupts a
pending request immediately with an explicit unverified outcome. This check runs
before matching reports can claim success. Late service replies/reports cannot
replace that interruption with success. Smoke alarm, active failsafe and running
fire response use explicit highlighted note headings even when collapsed.
This is display/confirmation behaviour; it does not cancel physical commands.

Four new browser regressions cover dispatcher contention, takeover with a matching
report, unknown failsafe and backend loss/send-time races. All 24 browser tests
passed; the final card rerun passed all 21 card tests. Contract/runtime drift
checks passed. Signed-in live HA showed version `20261019-2`, connected state,
backend available and Ready/no commands sent. No alarms or failsafes were triggered
on real hardware; takeover cases were tested with intercepted browser fixtures.

Assets/resource only changed; backend and firmware are unchanged. Recovery:
`/config/backups/ventsys-command-status-20261019-172101Z/` contains the previous
five assets and accepted release manifest. Restore those assets and set the
existing resource query back to `?v=20261019-1` to roll back the display update.

## Environment comparison and system log — frontend 20261019-3

The schematic's former Ambient panel is now **Environment**, with three data
columns in order Ambient, FDM, SLA. Shared row labels carry the units: temperature
°C, relative humidity %, barometric hPa, smoke and raw gas resistance kΩ. Each
column uses the same source precedence, conversion, freshness and alarm latch
as its detailed sensor section. Missing/stale/offline numbers show a dash, never
zero/demo data; accessible cell labels retain the exact reason/value and units.
Smoke shows Clear/ALARM or a dash when unverified.

The former Control notes panel is **System log**, showing up to six recent events
from this dashboard session with timestamps and shortened previews. Full messages
remain available in System log details and accessible text. It is not HA's global
log or a persistent audit trail. Initial state explicitly says no commands sent.

26 browser tests passed, including independent zone values, unknown/offline
clearing, smoke latch, log event updates, column bounds and mobile overflow.
Desktop/mobile schematic screenshots were visually checked. Signed-in HA showed
version `20261019-3`, new labels/three columns, connected state and no commands sent.
All five deployed asset hashes match local sources. Backend remains unchanged.
Private recovery checkpoint:
`/config/backups/ventsys-environment-20261019-172605Z/`. Restore its previous assets
and resource query `?v=20261019-2` to undo this display change.

## Seven-inch touch view — frontend 20261019-4

The standard dashboard remains the default `/dashboard-ventsys/0`, with its
existing layout/configuration. A second **Touch screen** view is available at
`https://homepage.home.local:8188/dashboard-ventsys/touch` (or the equivalent
existing native HA origin). Both views use the same authenticated card, state
sources, reviewed requests and backend guards. `layout: touch` explicitly opts
in; screen size alone never replaces the standard dashboard.

The touch view displays the same 1300×820 SVG with unchanged pipe/device/panel
coordinates and aspect ratio. Tap a valve/fan for its controller pop-up. The
Environment and System log panels open their detailed pop-ups; toolbar buttons
open Controllers, Modes, Sensors, Status and System log. Menus close using Close
or Escape. Confirmation remains a separate reviewed action; opening menus never
publishes. Full screen is user-activated and browser-dependent.

At the owner's request the touch view restores the original PrintAirPipe neon
title/header, live clock and connection/report badges, plus a bottom status bar.
Its FLOW is explicitly Unmeasured, MODE uses current reported configuration and
physical position stays unverified. The original demo airflow/fixed uptime and
misleading system-health claims were not restored. Known smoke/failsafe/fire
alerts highlight the persistent Status button even when menus are closed.

The two specular strips at the main duct's right end previously extended to
x1283 beyond the duct end x1252. Both now end at x1250. Nothing in the duct layout
moved. System log entries increase from SVG 15 to 20 units (timestamps 18), with
shorter previews; full messages remain in log details and accessible labels.
These two narrow artwork fixes apply to both views.

Source view config: `configs/home-assistant/ventsys_dashboard_views.yaml`.
The deployment helper preserves other views and installs these two named paths.
30 browser tests passed across normal/mobile and touch 800×480 / 1024×600,
including unchanged SVG geometry, fit, pop-up navigation, no startup/menu commands,
review/cancel/failsafe behaviour and highlight endpoints/log font sizes. Desktop
and touch screenshots were visually inspected. Real signed-in HA resource/version,
restored header/status and controller popup open/close were verified. The physical
seven-inch device/resolution is not yet verified; both target sizes are retained.

The private checkpoint is
`/config/backups/ventsys-touch-20261019-183437Z/`. It contains previous assets,
private previous-dashboard JSON, new view YAML and acceptance/hash manifest.
Recovery: restore the previous five authenticated assets, restore the old single
view through HA's dashboard configuration UI, and set resource query back to
`?v=20261019-3`. Do not edit `.storage` directly. Backend, firmware and Homepage's
standard link remain unchanged. No actuator commands were sent.

## Command repair after owner testing — frontend 20261019-5

**Running firmware, not Builder YAML, establishes command routing.** Read-only
network log sessions confirmed:

| Physical role | Address / verified MAC | Running firmware identity | Actual custom command topic |
|---|---|---|---|
| FDM intake | `.62` / `a0:85:e3:ae:5b:c8` | `ventsys-sla-360-valve` | `ventsys/sla/360/control` |
| SLA intake | `.61` / `cc:ba:97:f0:e3:ec` | `ventsys-fdm-360-valve` | `ventsys/fdm/360/control` |
| E2/SLA branch | `.52` / `ec:e3:34:b4:79:7c` | `ventsys-sla-branch-valve` | `ventsys/sla/branch/control` |

The Builder copies had corrected-looking names/topics which differed from the
running October 10 firmware. The previous dashboard readback fix correctly bound
native entity IDs by MAC, but wrongly retained command topics. This sent intake
requests to the opposite board, then waited for acknowledgement from the requested
board. Dashboard controls, all mode recipes, generated expected-state mappings
and compiled runtime now use the observed wire topics. No firmware or endpoints
were changed. Do not flash the differing Builder copies as routine maintenance.

E2's HA ESPHome entry incorrectly targeted `.51` (MAIN-1). HA's normal Reconfigure
flow accepted `.52`; its native entity recovered to numeric 0 and dashboard
coverage rose from five to six controllers. The running E2 MAC/name/custom topic
were independently read from its logs. This verifies connectivity, not movement.

Modes now offer **Available controllers only**, checked by default for partial
setup. Review lists skipped devices and explicitly says the complete mode is
unverified. The exact included report keys are frozen into the reviewed request;
backend validates they are an allowed subset and still available. It dispatches
only those targets through the shared guard. A new device appearing cannot be
silently added to the reviewed subset. Uncheck to require the complete mode;
missing controllers still block that full request. Failsafe/fire locks remain.

A requested target matching a controller report no longer suppresses sending.
The user may explicitly review/resend it, for example after a restart/stall.
The outcome says **Command sent — target already reported; physical position
unverified**, rather than claiming a fresh movement confirmation. Changed targets
still require newer matching controller reports and retain timeout/error handling.

Verification: 32 browser tests, 22 model tests, 13 dashboard backend tests, eight
arbitration tests, three drift tests and contract validation passed. Actual HA
read-only template rendering confirmed the frozen subset, correctly paired intake
wire topics and recovered E2 native value. HA configuration check passed (same
unrelated llama.cpp dependency warning); Scripts reloaded with no script running.
Signed-in touch UI showed six available controllers; mode review enabled with an
explicit skipped-device list and was cancelled without sending. No actuator
commands were sent, so owner-observed physical retest remains outstanding.

Private evidence/previous files:
`/config/backups/ventsys-command-repair-20261019-220857Z/`.
Previous files contain the known routing/strict-mode defects: do not blindly
restore them as a healthy rollback. Backend packages and frontend must remain
compatible; if withdrawing the repair, disable controls until routing is corrected.
Both standard/touch layouts remain. Firmware, credentials and network policy
are unchanged. Temporary diagnostic SSH tunnels were closed; forwarding was not
enabled or broadened.

## Diagram colour/alignment polish — frontend 20261019-6

Closed valve blades/rings/position labels now use saturated deep red `#e00000`,
fully open uses bright green `#00ff00`, intermediate uses amber `#ffb000`, and
unavailable remains grey. The 360 colour classification uses its accepted 30–60
range: 30 is closed/red and 60 open/green. Numeric controller reports are unchanged.
System log, enclosure 1, enclosure 2 and spray-booth frame bottoms all end at SVG
y800; shadow layers end at y801. Only frame/highlight heights changed; ductwork,
valves and control positions were retained. Both dashboard layouts use the fix.

34 browser tests passed, including endpoint colours, calibrated-intake colours,
unknown-state grey and the shared baseline. Touch screenshot visually reviewed.
No backend, transport, firmware or actuator commands changed. Private recovery:
`/config/backups/ventsys-diagram-polish-20261019-221623Z/`; restore its previous
five assets and resource query `?v=20261019-5` to undo this visual change only.
Physical acceptance after the preceding command repair remains a separate task.

## Frame glow/alignment — frontend 20261019-7 (October 20)

Live resource is now `?v=20261019-7`. Environment has a cyan drop-shadow and
outer glow; both enclosure frame tops are y263 and all four frame bottoms y800.
Six touch tests passed before deployment; authenticated live DOM verification
confirmed both tops, four bottoms and Environment glow. No actuator commands or
backend changes. Previous five assets are in
`/config/backups/ventsys-frame-glow-20261020-132325Z/previous-assets/`;
restore those assets and resource query `?v=20261019-6` for cosmetic rollback.

## Independent operating modes — frontend 20261020-3 (October 20)

Owner-confirmed semantics: FDM and SLA each have Off/Enclosure/Print/Purge;
Booth is independent. Both changes the two printer enclosures together.
Changing FDM preserves SLA and Booth intents. Stop is a normal ventilation
operation, not an emergency/fire action.

| Selection | 360 intake | Printer valve | Required extraction path |
|---|---|---|---|
| FDM enclosure | 60 | 0 | E1 open, main fan on |
| SLA enclosure | 60 | 0 | E2 and MAIN-1 open, main fan on |
| FDM print | 30 | 100 | E1 open, main fan on |
| SLA print | 30 | 100 | E2 and MAIN-1 open, main fan on |
| FDM/SLA purge | 60 | 100 | Same enclosure path, main fan on |
| Booth | unchanged | unchanged | MAIN-1 and MAIN-2 open, booth/main fans on |

Values are controller targets. The accepted 360 range remains 30–60; standard
valves remain 0–100. MAIN-1 is downstream of the FDM takeoff, so FDM alone does
not require it; SLA and Booth do. MAIN-2 is required by Booth. No duct or device
coordinates changed. Entity-button labels are now 14px and values 16px.

Purge has one strength popup: Low2, Moderate4, Medium6, High8, Max10. The owner
approved HA percentage requests 20/40/60/80/100 respectively pending physical
step calibration. Each enclosure owns its purge strength; the shared main fan
uses the highest active purge request. Reducing/stopping FDM cannot weaken an
active SLA Max purge. Outside purge, current fan speeds are retained. Starting
an ordinary mode requires nonzero reported fan speed; a purge supplies its own
main-fan percentage. Booth still needs its own nonzero reported fan speed.
Preset choices are disabled with reasons if required controllers are absent;
the popup itself can be inspected without issuing a command.

### Backend state and failure behaviour

`configs/home-assistant/ventsys_operating_modes.yaml` adds persistent intent and
result input_text helpers and `script.ventsys_set_operating_mode`. No initial
value or startup automation replays commands. A revision token rejects stale
cross-tab requests; the manager is single and rejects overlapping transitions.
The normal dispatcher rejects conflicting manual batches before any publish and
rechecks between publishes. Dashboard manual calls and ordinary legacy-helper batches are blocked while a
mode transition runs; only manager-owned phases can use the normal dispatcher. Direct native/MQTT controls remain outside this boundary.

Preflight checks the complete resulting active configuration and released
resources. No available-only partial mode is accepted. Transition phases stop
unneeded fans first, open new routes/inlets, wait for matching controller reports,
set/start required fans, then close obsolete paths. Each phase has an eight-second
report bound; missing reports stop subsequent phases. Desired intents remain for
an explicit retry/reconciliation; no automatic rollback or replay is claimed.
An interrupted/error result stays visible. Shared paths close only after their
last active owner releases them. Starting an enclosure does not close previously
unmanaged unrelated branches. Stop all explicitly requests the whole system
sealed and therefore requires all affected controllers; missing hardware can
block it. It is not a substitute for the separate fire-response action.

Named legacy mode scripts now delegate to this manager, so they cannot overwrite
unrelated active modes. Legacy purge wrappers default to Medium6 unless given a
strength; legacy global Purge now selects both printer enclosures and preserves
Booth. Old cached dashboard mode/partial requests are rejected with a refresh
message. Fire response stops the new manager as well as the existing normal
paths, and retains direct emergency MQTT commands without helper dependencies.

### Faults and ntfy follow-up

Dashboard mode-report warnings cover BOTH missing required openings and unwanted
open reports where a mode requires closure (including a print mode's closed 360
intake and an enclosure mode's closed printer valve). A report mismatch is not
proof of a mechanical jam. If a jammed-open valve still reports its commanded
closed value, these servos cannot establish that fault by position reporting.
Unexpected airflow/leakage/backflow in a supposedly closed route needs its own
commissioned measurements and baseline. No invented physical-feedback field is
shown. Booth-only extraction is now included in the reported-open-path check;
missing unused enclosure reports no longer produce that false blocked-path warning.

### Incident severity and remaining commissioning plan

| Level | Initial conditions | Display | Notification |
|---|---|---|---|
| Blue — information | Gas warm-up, planned board restart, normal mode transition, recovery | Steady blue marker and ordinary event row | Usually no push; optional digest |
| Orange — abnormal | Commissioned sensor fault or stale board, repeated command timeout, unexpected valve report, temperature rise warning, expected/open or closed-path airflow deviation after commissioned baseline | Orange outline on the source and persistent warning row; pulse only on a new event | Deduplicated ntfy warning after debounce; recovery notice |
| Red — alarm | CO/smoke detection from a commissioned, validated sensor, commissioned high-temperature limit, failsafe/fire response, confirmed hazardous flow loss during an active print | Red pulsing outline on the source, persistent top warning symbol, flashing new-event row; steady red after acknowledgment | Immediate high-priority ntfy incident and bounded repeat until acknowledged/resolved |

Keep **active**, **latched**, **acknowledged**, and **resolved** as separate
states. Acknowledgment silences repeats and marks the event read; it does not
erase the source state or history. A current red event remains red while active.
Use the same backend incident record for the dashboard and ntfy, with a stable
incident key, source entity, first/last seen times, expected/actual values and
resolution time. Browser session logs are insufficient for this record. Alarm
colors also need text, icon and shape for accessibility; reduce animation for
users requesting reduced motion. Never flash the whole screen or imply an
unavailable sensor is clear.

For the current SLA pipe CO board, the recurring near-3.3 V fault means the
channel is **uncommissioned**. Surface its active CO/fault state conspicuously
in the dashboard, but label the hardware reading unverified and do not use it
as a calibrated CO incident or capture a baseline. A certified CO alarm remains
the independent safety device. The dashboard's SLA sensor panel uses the
adopted `garage_ventsys_sla_pipe_air_sensor_*` entities and labels the channel
CO instead of smoke. Firmware should
classify an out-of-range CO voltage as a fault before CO detection, so a clipped
ADC does not appear to prove CO exposure; verify that behavior on a bench.

Beyond the deployed CO hardware fault and failsafe notifications, these ntfy
delivery rules remain proposed:

- Commissioned node offline/stale, explicit sensor/controller fault, reboot loop,
  command timeout or an interrupted transition; exclude uncommissioned nodes.
- Required path lacks expected flow/pressure after settling, OR an unwanted path
  has excessive flow/leakage while requested closed. Use the current valve
  combination and fan strength baseline; both failure directions matter.
- Smoke/failsafe activation and commissioned temperature limits/rate of rise.
  Numeric temperature/flow limits still need commissioning and owner agreement;
  raw BME gas resistance is not a certified danger threshold.
- Persist incident identity, debounce ordinary disconnects, deduplicate/rate-limit,
  include recovery, source, expected/actual readings and a dashboard link.
- Run alerts in HA/backend, independent of an open card. Monitor HA/MQTT/alert
  publisher availability externally. Repeat authenticated phone delivery with
  the app backgrounded: the ntfy manual records failed October11 phone acceptance.

Useful next work: show requested versus reported mode distinctly (implemented),
add commissioned-node heartbeat/reset/error details, persistent server event
history beyond this card's session log, and measured path/closed-path baselines.
Purge remains continuous until changed/stopped; a timer/overrun is a separate
operating choice, not silently introduced here.

### Verification, deployment and remaining hardware issue

38 Python planner/template/policy tests, 39 browser tests and 24 model tests
passed. The path planner exercises all480 base state/request combinations;
strength tests exercise shared-maximum ownership and exact percentage topics.
An actual HA Template editor dry-run confirmed FDM Low with SLA Max requests
100%; no mode was executed. `ha core check` passed after staging. Helpers and
scripts were reloaded through authenticated Developer Tools while VentSys scripts
were idle. Five frontend hashes and live scripts match canonical artifacts.
Resource query is `?v=20261020-3`. Live grouped menu, disabled preset explanations,
14px labels and one typed-value confirmation/cancel were verified without sending.
No actuator commands, firmware, credentials or network changes were made.

October20 targeted investigation: E2 native is unavailable again. Its current
ESPHome config entry still contains host `.51`, contrary to the prior recovery
claim; canonical E2 is `.52`, MAC `ec:e3:34:b4:79:7c`. Two HA-host pings to `.52`
received no replies. This does not establish whether it is powered off, disconnected
or has another network fault; no reconfiguration/firmware change was attempted.
Resolve board identity/reachability and persistent host binding before physical
acceptance. Other absent controllers remain expected during setup.

Recovery checkpoint: `/config/backups/ventsys-operating-modes-20261020-134406Z/`
contains the preceding five assets and two packages (frontend20261019-7). To
withdraw this feature, first ensure no normal scripts are running and review
current outputs/intents; restore both packages and five assets, remove only the
new `packages/ventsys_operating_modes.yaml`, reload scripts/helpers and restore
resource query `?v=20261019-7`. Removing these protections is not equivalent to
a healthy operating-state reconciliation. Do not restore known-bad pre-command-
repair routing or broadly edit `.storage`. Helpers can be retained for audit;
configuration rollback itself issues no actuator commands.

Rebuild locally in order:
`python main/tools/generate_ventsys_dashboard_contract.py`,
`python main/tools/generate_ventsys_arbitration.py`, then
`python main/tools/generate_ventsys_operating_modes.py`.
The third generator must run after both earlier generators; it integrates the
manager guards/wrappers and retires cached dashboard mode calls.


## E2 USB diagnosis and native connection recovery — October27

Owner plugged the expected E2 board into the Admin desktop and reported local
GPIO33 touch actuation working but no dashboard report. Windows identified it
as CP210x COM4 (not COM5). Serial logs confirmed MAC `ec:e3:34:b4:79:7c`, hostname
`ventsys-sla-branch-valve`, firmware built October10 10:11:23 BST with ESPHome
2026.4.5, and `ventsys/sla/branch/control`. Canonical and HA Builder YAML hashes
match (`28f2c1d6e254472ed14a6c51d0119c2f4a95731361ae6c612f308e2c34a0936e`).
No flash, valve command or firewall change was needed.

Router association and Mosquitto logs established Wi-Fi/TLS MQTT connectivity
at `192.168.50.52`. Ping from HA remained unanswered; this is not reliable
availability evidence under the scoped HA-to-IoT rules. The router's generic
`Block IoT Internet` log prefix can appear before a `reject_to_wan` jump that
only rejects WAN egress, followed by the MQTT allow rule. Do not infer an MQTT
block from that log prefix alone; broker TLS connection is stronger evidence.

HA's MAC-bound E2 entry `01M3CCTVYZP8Q14879S7C1K8CR` still stored `.51`.
Used ESPHome integration > E2 entry Menu > Reconfigure to set host `.52`, port6053.
HA reported success; a targeted read-only `.storage` check confirmed `.52`
persisted. The unchanged dashboard then showed SLA/E2 branch0%, Native controller
report, range0–100. Screenshot saved outside the vault. This resolves current
reporting, not a mechanical travel/remote-actuation acceptance test. No remote
valve command was sent. Serial was closed after diagnosis; its initial capture
included a boot sequence despite RTS/DTR being preconfigured inactive.

## Setup/test option — live October27, release20261027-1

Current live release `20261027-1` adds an explicit **Setup/test — available valves
only** toggle to Modes. It defaults off and does not persist across reloads.
Normal operating modes keep strict full-path checks. Setup opens one confirmation
listing exact available native valve targets and skipped valves; fans are never
commanded, and an unknown/uninstalled fan requires the operator to ensure no
powered fan is running. Purge in setup tests valve targets only, without fan
strength selection. No operating intent/result helper is changed and no
ventilation-established claim is made. Requested subsets are frozen at review;
loss of a selected controller or a revision change blocks the send.

`script.ventsys_test_valves` validates a valve-only subset against generated
fixed targets, rejects active operating intents and reported running fans,
checks native ranges/availability, and uses the shared dispatcher with a dedicated
test-owner flag. Ordinary commands cannot interleave; fire response cancels the
test. Test ownership, fan exclusion and active/failsafe locks are rechecked before
publishes. Report confirmation is bounded to eight seconds. Stopping in setup
only applies available valve closure targets; it does not stop fans.

39 Python policy/template tests,42 browser tests and24 model tests pass. The new
review flow also passed at800×480 with a saved fixture preview. No actuator
commands were sent. Initial deployment was blocked by a detached browser panel;
once the owner brought the signed-in panel into view, deployment completed.
`ha core check` passed, scripts reloaded while idle, and Setup/manager/dispatcher
were all verified off. Resource20261027-1 was saved through HA. Live Setup/test
selection enabled the available valve actions; SLA enclosure review showed branch
100/intake60 and explicitly skipped SLA print/MAIN-1. It was cancelled without
sending. The toggle was left enabled in the displayed menu; reloading defaults it
off. Five assets/three package hashes match canonical source. Current intents
were off for both enclosures and Booth; testing does not alter those intents.

Private release/previous copies:
`/config/backups/ventsys-setup-test-20261027-193629Z/` (prepared-assets,
prepared-packages,previous-assets,previous-packages and release.json).
Active resource is `?v=20261027-1`. Both dashboard views use the release.
Deployment used the three prepared packages, configuration check, authenticated
script reload, five prepared assets and authenticated resource update; no direct
`.storage` edits or credential/network changes were made. Restore the three previous
packages/five assets/resource20261020-3 if withdrawing this release while idle.

## November4 UI release and E2 address recurrence

Frontend20261104-2 is active in both standard/touch views. Intake opening is
`clamp((raw-30)*100/30,0,100)`; UI0/50/100 map to raw30/45/60. Manual UI requests
convert back to integer raw controller steps, and confirmation shows the resulting
opening. Backend/mode targets retain raw units and their safety checks. Reports
remain commanded/controller state, not measured physical angle. RPM and gas kOhm
readings round to integers; other sensor precision is preserved. Fresh positive
wheel readings animate bottom/centre/top arrows; zero, stale, unavailable and
offline readings stop animation. Reduced-motion preference gives static arrows.

MAC `CC:BA:97:F0:D0:C0` at `.32` is physically FDM, correcting its earlier SLA
label. Board firmware and HA integration/device/entity display names now say FDM.
HA renamed sensor IDs to `garage_fdm_enclosure_sensor_fdm_enclosure_sensor_*`;
model mapping includes the old retained IDs only as missing-entity fallback and
never uses that board for SLA. Installed BME0x77/SDA4/SCL5/ADC3/LED2 retained;
existing40C threshold unchanged pending commissioning. Source `ventsys_fdm_sensor.yaml`;
old `ventsys_sla_sensor.yaml` is a compatibility include. Physical allocation `.32`
still collides with the planned second FDM array and must be reconciled before
that additional board is installed.

E2 MAC `EC:E3:34:B4:79:7C` responded at `.52`, RSSI-72dBm, uptime382515s
(about4.4 days), raw report0. HA entry had again reverted to `.51`; reconfigured
through integration UI to `.52` and native reporting recovered. MAIN-1 at `.51`
was independently identified as `EC:E3:34:67:8C:9C` / ventsys-main-valve-1;
E2 identifies as ventsys-sla-branch-valve. Canonical E2 firmware specifies `.52`;
dashboard has no connection-entry/address writes. No firmware/HA/dashboard
mechanism rewriting the host was proven.

A concrete stale live-router reservation was found: dhcp.cfg0ffe63 named MAIN-1
and assigned `.51` but used E2's MAC. Corrected only that MAC to MAIN-1's and
added named `dhcp.ventsys_e2` for E2/.52; committed DHCP and reloaded dnsmasq.
DNS `ventsys-sla-branch-valve.home.local` now resolves `.52`; router pings and HA
saved host/native reports passed. This is a plausible discovery-confusion source,
not proof it caused the HA host rewrite. Backup `/root/ventsys-dhcp-20261104/dhcp.before`;
rollback: restore that DHCP file and reload dnsmasq (also restores the known bad
reservation). Broader router source was not deployed. Canonical inventory already
had both correct MAC/IP bindings. No firewall change: a misleading early log
prefix occurred alongside subsequently proven successful MQTT TLS.

Codex heartbeat `ventsys-e2-connection-monitor` was stopped and deleted at the
owner’s request on November4; no recurring checks are currently active. It had run every5min.
It compares saved HA host, router reservation/DNS, router-side reachability and
available native uptime/RSSI. It stays quiet when healthy/unchanged and reports
new incidents/recovery; no automatic repair, actuation, serial access or external
ntfy delivery. Separate paused historical Main-2 monitor is unrelated and unchanged.

Five prior UI assets: `/config/backups/ventsys-ui-20261104-1`. Restore them and
resource20261027-1 to roll back the UI. Current five asset hashes match canonical
source; resource saved through authenticated HA UI, never direct storage edits.
Private build/evidence directory: `K:/Documents/Codex-builds/ventsys-nov4`.

November4 release20261104-3: online zero-flow circles remain full opacity with red arrows; positive fresh flow animates blue arrows upward; unavailable entities are greyed. Stale values do not establish positive flow. Prior assets in `/config/backups/ventsys-ui-20261104-2`. Reload clients to activate.

## November4 operating-mode review — follow-up required

Source review confirmed independently owned enclosure intents and shared-path
planning: enclosure opens the branch and 360, closes print; print opens branch
and print, closes 360; purge opens all three; SLA/booth require MAIN-1, booth
also needs MAIN-2 and its fan. Starts open paths before starting fans; stops
release shared paths only after their final owner stops. These are controller
reports, not proof of physical airflow or valve position. Seven mode and eight
arbitration unit tests passed; physical topology and mode transitions remain
unverified.

Open design issue: when the last purge ends and another non-purge mode stays
active, no new fan speed is requested. The fan retains its prior purge speed,
which may remain at Max. Non-purge modes require a previously reported nonzero
speed. Do not invent a default or silently change fan speed; decide and test a
normal-mode speed policy with the owner. Failed transitions retain requested
intents and can leave partial physical changes; retry/reconcile is required and
there is no verified automatic rollback. Direct device touch/MQTT consumers can
bypass HA arbitration, so dashboard mode locks do not enforce exclusive control
at the device or broker.

Requested follow-up scope includes stale/offline handling, commissioned-node
alerts with ntfy delivery proof, an explicitly no-motion reference interface,
and pre/post firmware-update retention checks. These are not delivered merely
by this review. Flow/jam thresholds require commissioned baselines; unconfigured
nodes must not cause alert storms. ntfy phone delivery was previously unproven.

### Interrupted-release recovery candidate

The local candidate retains the previous ownership key and exact request with the
new desired intent, and saves persistent states before issuing transition phases.
After interruption or restart, repeat that same request and strength to reconstruct
its original release plan, including shared paths. Other normal commands and setup
tests are blocked until controller reports confirm the transition. Emergency
preemption remains available; there is no automatic replay. Controller reports do
not establish physical valve position. This candidate is not deployed; the live
release still has the interrupted-release gap described above.

November4 release20261104-4: enclosure air-sensor symbols derive availability from the configured group of temperature, humidity, pressure, gas and smoke entities; a missing individual reading does not grey an otherwise online device. No available entity greys that sensor. Flow arrows remain vivid red when no fresh positive flow is available and animate blue on fresh positive flow; the circle itself is dimmed for an unavailable wheel entity. Tests cover online/offline, partial measurements and colours. Prior assets are in `/config/backups/ventsys-ui-20261104-3`; restore them and resource20261104-3 to roll back.
