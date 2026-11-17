---
id: 004
title: Correct FDM enclosure air sensor CO channel labeling
status: done
tier: executor
agent: codex
reviewer: claude
base: codex/portal-refinement
base_commit: 8e8f8a6a4a0898ae6db0002470edfd1833b4db8d
branch: agent/004-correct-fdm-enclosure-air-sensor-co-chan
created: 2026-11-12
---

## Goal
The FDM sensor CO channel is correctly labeled in firmware, HA, and dashboard, replacing the incorrect smoke label.

## Read first
- main/TO-DO.md - task details on CO channel correction
- main/configs/esphome/ventsys_fdm_sensor_co.yaml - candidate config
- main/docs/ - documentation context
- main/dashboards/ - dashboard labeling
- main/ventsys/ - ventsys codebase

## Do
1. Review main/TO-DO.md for the requirement to correct the installed FDM enclosure air sensor CO channel.
2. Examine main/configs/esphome/ventsys_fdm_sensor_co.yaml for the candidate configuration using SLA CO/BME680 pinout.
3. Update the firmware configuration to label GPIO3 as CO instead of smoke.
4. Update the HA entity naming to reflect the CO channel.
5. Update the dashboard labels to use the adopted BME680 IDs and CO channel name.
6. Ensure the uncalibrated raw threshold is replaced or adjusted as per the new configuration.

## Don't touch
- Physical wiring diagnosis
- SLA pipe CO output/wiring
- FDM print touch tests
- Remote actuation tests

## Acceptance
- [ ] Firmware labels GPIO3 as CO.
- [ ] HA entity naming reflects CO channel.
- [ ] Dashboard labels use BME680 IDs and CO channel.
- [ ] Raw threshold is updated or adjusted.

## Result
- **Commit(s):** `a76fbec` fix: correct FDM CO dashboard and HA labels; `963f4d2` fix: restore FDM CO alarm trigger.
- **Acceptance output:** Model tests passed, 26/26; `git diff --check` passed. The Playwright test could not run because Playwright is not installed. `node --test` hit sandbox `spawn EPERM`; direct execution passed.
- **Notes / follow-ups:** The GPIO3 CO firmware and thresholds were already present in the base. The MQTT topic and `detected` payload wiring were checked in source. Live HA entity IDs and the complete alert path still need verification; no deployment was performed. The November 10 OTA is documented in current live state.

**Dispatcher (2026-11-12):** status `done`; worktree `K:\Documents\Obsidian\worktrees\home-automation-project\agent_004-correct-fdm-enclosure-air-sensor-co-chan`.

<details><summary>Acceptance output (tail)</summary>

```
(no acceptance_cmd on card)
```
</details>

<details><summary>Review</summary>

The change meets all four acceptance items, with one caveat on items 1 and 4: the firmware was already correct at the base commit, so the commit only touches a comment there.

**Do items and acceptance**
- **Firmware labels GPIO3 as CO:** met, but already true at the base commit. `ventsys_fdm_sensor.yaml` already had `co_gpio: GPIO3` and "no fabricated smoke channel", and `ventsys_fdm_sensor_co.yaml` is a wrapper that includes it. The commit only replaces a stale "MQ sensor … smoke" comment.
- **HA entity naming:** met.
  - `FDM Smoke` becomes `FDM CO` with unique_id `ventsys_fdm_co`.
  - Its state topic is now `ventsys/fdm/co`, which the firmware does publish (`ventsys_air_sensor_co.yaml:109` sends `detected` or `clear` there).
  - `sensor.fdm_smoke` becomes `sensor.fdm_co` in `automations.yaml` and `ventsys_array_mqtt.yaml`.
- **Dashboard labels:** met.
  - `SENSORS.fdm.smoke` now points at the CO entities, `alarmLabel` is `'CO'`, and the legacy smoke IDs are dropped so a stale retained entity can't show.
  - The BME680 IDs (`FDM_INSTALLED`) are unchanged.
  - The SVG aria-label now says "FDM CO".
  - `freshnessTime` handles the CO binary sensor and uses the installed board's temperature as its heartbeat.
- **Raw threshold:** met. The "uncalibrated raw threshold" wording is gone from `TO-DO.md`. The firmware already uses a ratio or voltage threshold from the CO package, and I made no firmware change for this.

**Tests**
- `ventsys-model.test.mjs` passes, 26 of 26. The new test checks the FDM CO entity list, `alarmLabel`, and that the heartbeat uses only the installed board's own temperature.
- I couldn't run `ventsys-card.spec.js` because Playwright isn't installed in this worktree. I read the updated spec: it sets a CO entity to `on` with a fallback `sensor.fdm_co` of `clear`, and expects "CO DETECTED". That tests the right thing.

**Don't touch:** no wiring, SLA pipe CO, print-touch or actuation files were changed.

**Minor notes (not blocking)**
- The comment above `FDM CO` in `ventsys_ha_package.yaml` still says "Smoke / VOC (MQ-2/MQ-135)".
- The dashboard's `garage_fdm_enclosure_sensor_co_detected` ID is inferred from ESPHome naming. `TO-DO.md` already lists verifying the live HA entity IDs as an open step.
- `fire_detection_emergency` has `initial_state: false`, so the `sensor.fdm_co` trigger change has no live effect until someone enables it.

VERDICT: PASS
</details>

<details><summary>Branch log</summary>

```
963f4d2 fix: restore FDM CO alarm trigger
a76fbec fix: correct FDM CO dashboard and HA labels
8e8f8a6 docs: cleanup storage migration artifacts and update docs
ae605c2 feat: record home automation project updates
9ebc4b2 feat(recomp): expand food and workout tracking
fbc19d9 feat(monitoring): expand diagnostic dashboard
5ebfc42 feat(workbench): expand read-only evidence
c995e1e feat(solar): add observatory display
2596ddd fix: correct monitor-only update counts
c05e018 docs(recovery): verify archives and close stale gates
```
</details>
