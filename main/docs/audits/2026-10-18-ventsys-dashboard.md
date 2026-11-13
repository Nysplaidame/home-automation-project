---
title: VentSys dashboard range restoration and audit
created: 2026-10-18
type: audit
status: findings-open
---

# VentSys dashboard range restoration and audit

## Owner test correction — October 19, command repair

Owner testing found intake commands stopped/failed, modes blocked, and E2 never
responded. Prior "accepted" checks were UI/mocks and did not prove physical
response. Runtime log inspection exposed the incorrect topic assumption: FDM
`.62` actually subscribes to the SLA wire topic, SLA `.61` to the FDM wire topic.
Builder copies differed from running firmware. Readback was correct; sends were
crossed. E2 HA host was `.51` instead of `.52`. These were corrected in frontend
`20261019-5` / backend `20261019-command-repair-1`. Partial modes now explicitly
review/freeze available targets and skipped devices; same-target resend is allowed.
HA/source/software checks passed without actuation; physical retest remains open.
This correction supersedes earlier "command topics already correct" claims.
Current evidence, exact topics and recovery notes are in the dashboard manual.

## Remediation disposition — October 18–19

**Latest owner correction (October 19):** the 360 firmware and firmware/HA role
swap are already correct. The 30–60 controller range is intentional. Missing
hardware is expected during setup. The remaining mapping defect is in the
dashboard: the old SLA native entity prefix belongs to the current FDM board
and vice versa. Live release `20261019-1` corrects those bindings and their command
acknowledgements, without changing the correct command topics or firmware.
Normal HA sign-in activated it; 53 tests and live range checks passed. The public token stays revoked.
This supersedes the earlier recommendations to revisit/reflash 360 firmware.

The authenticated replacement is now live as release `20261019-1`. The direct
HA card supersedes both the older token dashboard and the offline candidate;
the previous source/runtime split is closed. Current operating and release
instructions are in [[../procedures/ventsys-dashboard]]. The original findings
below are retained as the evidence that drove this change.

- Closed: public credential exposure (file sanitized, dedicated token revoked,
  old credential independently rejected with HTTP 401); optimistic/offline state;
  missing/stale display values; smoke precedence; pressure quantities/units;
  demo airflow and IAQ claims; unrelated node counts; phone clipping and input
  labels/keyboard/reduced motion; contradictory release status.
- Dashboard command requests now use one exact-schema HA wrapper with native
  availability/range/failsafe checks, serialized execution and bounded report
  confirmation. Named mode/helper arbitration is now covered by the shared backend below;
  direct MQTT/native consumers remain outside it.
- Remaining: installation as planned, physical commissioning when requested,
  physical sequence acceptance and controls outside the named script dispatcher.
  The owner accepts the 360 firmware, endpoints and firmware/HA role swap;
  those are no longer dashboard remediation tasks.
- Evidence: current release passed 22 model, 11 backend and 20 browser tests;
  signed-in HA showed both intake ranges 30–60, standard valves 0–100,
  setup/status notes and no commands sent. Physical travel was not tested.
- The private authenticated-release checkpoint is
  `/config/backups/ventsys-dashboard-20261018-225534Z/`; its `release.json` records
  served hashes, real UI acceptance and successful revocation. Old credential
  backups must stay private and must not be restored as public authentication.

## Backend follow-up — October 19

Backend `20261019-arbitration-1` is now deployed. The 12 normal modes, legacy valve
helper and dashboard share one dispatcher, with whole-batch topic/value validation
and failsafe/fire-idle checks before each publish. Fire response stops normal
execution first and publishes directly, including the canonical main fan 100%.
The original speed drift and named-script overlap findings are resolved.
Eight arbitration, 11 backend and three drift tests passed. An isolated real HA
copy using text writes instead of MQTT passed contention/preemption/failsafe tests;
the temporary probe was removed. HA schema validation and idle reload passed,
new dispatcher loaded off, and deployed hashes match generated source. No physical
commands were sent. See the runbook for selected runtime artifacts and paired
rollback. Direct MQTT/native controls are still outside this arbitration boundary.

## Follow-up execution audit — October 19

A read-only semantic comparison of canonical and Samba-deployed mode scripts
found **only `ventsys_mode_fire_safe` differs**. All 12 manual dashboard mode
scripts and the valve helper match execution settings and ordered action data.
The live fire-response script omits the canonical `ventsys/fan/percent: 100`
publish. No fire response or other actuator command was executed for this audit.
That initial discrepancy is resolved by the backend follow-up above; this audit
does not establish the correct physical fire response.

`tools/validate_ventsys_contract.py --live-scripts <deployed YAML>` now compares
execution settings and complete ordered sequences while ignoring top-level
presentation/selector metadata. It exits nonzero on drift and names scripts
without dumping file contents. The three comparator tests cover omitted speed,
changed sequence order, missing/extra scripts and concurrency settings.
Running against `/config/packages/ventsys_ha_scripts.yaml` produced the expected
failure for `ventsys_mode_fire_safe` only; local mode/dashboard/topic checks passed.

Dashboard `mode: single` serializes dashboard requests only. The independent
mode scripts and parallel valve helper do not share that dispatcher, so this
is not a global lock or an emergency-preemption guarantee. This initial limitation is superseded for named script entry points by the
backend follow-up above. Unrouted direct consumers remain outside arbitration.

The sections below describe the original October 18 evidence. Current accepted
360 ranges and current release instructions above supersede historical claims
that every intake should expose 0–100 or that legacy HTML/token rollback is valid.
Never restore the old public credential-based control path.

## Delivered

The owner requested removal of the historical 50-as-fully-open convention.
Dashboard slider limits, colour/rotation normalization, command clamping,
the invalid-setting fallback and all mode-script open targets now use 100.
The live `ventsys-config.js` override was also changed from 50 to 100.
All eight valve/intake controls cover 0–100; 50 is half travel.
Fan speed percentages, firmware pulse calibration and saved per-device
Open/Closed button targets were not changed. This restores the software
command range; it does not establish physical endpoint calibration.

Canonical changes: `dashboards/ventsys-dashboard.html`, public config example,
`ventsys/ventsys_bundle_updated/ventsys_ha_scripts.yaml`, contract validator,
and `tools/playwright-smoke/tests/valve-range.spec.js`.

The live dashboard is an older authenticated, optimistic-control variant.
The canonical dashboard is an offline candidate with several subsequent fixes.
They were already different before this work. **Do not copy the canonical HTML
over production as a routine range deployment:** it would disable live control.
The deployed HTML and script package received only the targeted range edits.
The local script's separate main-fan-100 fire-mode change was not included.

## Evidence and scope

- Nine canonical Playwright tests passed: existing dashboard tests plus four
  range tests. The four range tests also passed against the staged live HTML,
  with every HTTP request intercepted and command sends captured in memory.
- All eight sliders preserved 0, 25, 50, 75 and 100 telemetry; all eight distinct
  command topics sent non-retained `100`. Half/full colours differ and invalid
  configuration falls back to 100.
- `python main/tools/validate_ventsys_contract.py`: 13 mode scripts and existing
  command-free initialization/topic checks passed. Validator open target is 100.
- Live YAML before/after semantic comparison allowed only valve targets,
  selector maximum/example and range description changes; fan settings match.
- HA `/api/config/core/check_config` returned `valid`; `/api/services/script/reload`
  succeeded. No HA script was running before reload. Samba bytes matched the
  staged files and HTTPS returned the patched HTML exactly.
- Mock browser review at 1280×800, 800×480 and 390×844; kiosk/mobile screenshots
  inspected. Live-variant page produced no startup JavaScript exception.
- Read-only HA state inspection found two print-valve numbers unknown. No
  physical movement, calibration, firmware flash or mode activation was tested.
- TLS certificate/hostname verification remained enabled. Python's strict X.509
  flag needed legacy-CA compatibility because the local CA lacks key usage.

## Findings, in priority order

| Priority | Finding and evidence | Recommended change |
|---|---|---|
| P1 | **Credential publicly downloadable.** An unauthenticated HTTPS GET of `/local/ventsys-config.js` returned the same credential used successfully for the read-only HA state request. No credential was logged or committed. | Complete and validate an authenticated card integration, remove the public credential, then revoke/replace it. Audit other consumers before revocation. Existing draft card is not ready for promotion. |
| P1 | **Offline/failed operations look successful in production.** Mock offline startup reports `SEALED`; `toggleFan()` changes local running state with no HA connection. Live `applyMode` animates desired state before acknowledgement. | Port the candidate's confirmed-state controls and unknown startup semantics while preserving working authenticated access. Add failed-service, timeout and disconnect tests. Never interpret an echoed command as measured mechanical position. |
| P1 | **Unavailable sensors retain old values.** Humidity 42 followed by `unavailable` still displays 42. Most sensors/actuators return early on unknown/removal; disconnect also retains old display values. | Explicit unknown/stale state for every field, clear trust on disconnect, disable unavailable actuator controls, and show freshness. Keep a confirmed alarm distinct from an unknown sensor. |
| P1 | **Fallback smoke can clear an alarm.** Feeding primary `on`, then fallback `clear`, changes `SMOKE` to `CLEAR`; both sources directly write the same field. | Define source precedence and alarm aggregation explicitly. Add conflicting-state and unavailable-primary tests. IAQ also currently uses whichever source reports last. |
| P1 | **Wrong pressure quantity/unit.** Config binds `*_baro_pressure` to the `D. PSR` / `Pa` field. Mock 1013 hPa displays `1013.0` under that label. | Separate absolute pressure (hPa) from actual differential pressure (Pa); require an appropriate sensor for the latter, otherwise show unavailable. |
| P2 | **Demonstration values are presented as telemetry.** Static temperature/humidity/clear-smoke/uptime survive startup; random temperature trends run offline. `updateFlowRates` synthesizes CFM from valve sliders if flow readings are absent. Missing wheel channels become zero and wheel RPMs are summed as a total. | Remove demo data from operational mode. Label calibrated estimates, distinguish missing from zero, and show per-wheel RPM rather than a physically ambiguous total. |
| P2 | **Node health includes unrelated HA devices.** `nodeSlugFromDiagnosticEntity('sensor.unrelated_printer_uptime')` returns a node. Discovery scans every HA diagnostic suffix and refreshes during each initial state, with repeated full-map scans. | Restrict inventory to identified VentSys devices, batch initial updates and cache membership. Do not label the system nominal solely from diagnostic uptime counts. |
| P2 | **Modes can overlap or drop requests.** Mode scripts have independent executions and no shared arbitration; the valve helper runs in parallel; dashboard sends every click and every slider input. No request timeout exists in `haSend`. Local candidate only derives SEALED/PURGE, not the complete mode set. | Serialize mode changes centrally, expose pending/failed state and bounded timeouts, coalesce slider changes. Test rapid mode changes, disconnect and rejected commands. |
| P2 | **Fire-mode source/runtime drift.** Canonical fire-safe script explicitly sets main fan speed to 100; deployed script does not. The range patch preserves the live behavior. | Reconcile as a separately tested control change; verify the complete intended fan/valve sequence before commissioning. |
| P2 | **Phone layout and accessibility.** At 390×844 the header clips, the schematic shrinks to an unreadable centre band, and hidden overflow prevents normal recovery. All ten range inputs lack programmatic labels. | Provide a narrow-screen control/sensor layout, labelled inputs, keyboard-operable schematic controls, focus handling and reduced-motion support. Preserve the 800×480 kiosk layout. |
| P2 | **Release documentation contradicted deployment.** Earlier card status/bridge docs describe an offline accepted page, while production still uses public-token WebSocket auth. The example encouraged adding that token. | Maintain explicit live/candidate status and a reproducible deployment diff. The example and status docs are corrected by this audit. |

These are code/browser findings, not a physical safety certification. VentSys
remains under testing. Physical commissioning gates in the current live-state record still apply.
The owner-accepted 360 identity/firmware correction above supersedes the earlier
identity recommendations.

## Deployment and rollback

Deployment used the existing Windows-authenticated Samba share and existing
HA API access; no secret was written into the repository. Backups are outside
the public web directory at:

`/config/backups/ventsys-full-range-20261018-202453/`

That directory contains `ventsys-dashboard.html`, `ventsys-config.js` and
`ventsys_ha_scripts.yaml`. Treat the config backup as credential-bearing.
To roll back, restore the first two files to `/config/www/` and the scripts file
to `/config/packages/`, run the HA configuration check, reload scripts only when
none is running, then refresh dashboard clients. Restoring the config and HTML
together is necessary because the override takes precedence over the default.

Current resume: dashboard software remediation is complete; use the authenticated
release/manual above. The following useful work is installation as planned and the remaining
independent control gates. Physical travel
acceptance requires observation of the devices.
