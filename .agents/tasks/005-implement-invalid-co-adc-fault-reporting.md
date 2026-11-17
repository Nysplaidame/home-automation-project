---
id: 005
title: Implement invalid CO ADC fault reporting in firmware
status: done
tier: executor
agent: codex
reviewer: claude
base: codex/portal-refinement
base_commit: 8e8f8a6a4a0898ae6db0002470edfd1833b4db8d
branch: agent/005-implement-invalid-co-adc-fault-reporting
created: 2026-11-12
---

## Goal
Invalid CO ADC readings report a fault before detection in the firmware.

## Read first
- main/TO-DO.md - task on invalid CO ADC readings
- main/configs/esphome/ventsys_fdm_sensor_co.yaml - sensor config
- main/ventsys/ - ventsys codebase
- main/docs/ - documentation
- main/dashboards/ - dashboard fault display

## Do
1. Review main/TO-DO.md for the requirement to make invalid CO ADC readings report fault before detection.
2. Analyze main/configs/esphome/ventsys_fdm_sensor_co.yaml to understand the current ADC reading logic.
3. Implement logic in main/ventsys/ to detect invalid CO ADC readings.
4. Ensure invalid readings trigger a fault state before any detection logic is applied.
5. Verify that the dashboard displays the fault state correctly.
6. Update any relevant documentation in main/docs/ to reflect the new fault reporting behavior.

## Don't touch
- Physical bench-verification
- SLA pipe CO output/wiring
- FDM print touch tests
- Remote actuation tests

## Acceptance
- [ ] Invalid CO ADC readings trigger a fault state.
- [ ] Fault state is reported before detection logic.
- [ ] Dashboard displays the fault state correctly.
- [ ] Documentation is updated to reflect the new behavior.

## Result
- Commit(s): `b79a989` — `fix: report invalid CO readings as faults`
- Acceptance output: **Partial** — dashboard model checks passed 26/26, including CO fault display and concurrent detection labeling. `git diff --check` passed. ESPHome configuration validation failed because the available executable exited with code 1 and Python has no `esphome` module.
- Notes / follow-ups: The firmware change is in the shared ESPHome package under `main/configs/esphome/`, which the listed wrapper includes; `main/ventsys/` does not contain that firmware. The candidate remains uncompiled, undeployed, and not bench-verified. The card specified no acceptance command.

**Dispatcher (2026-11-12):** status `done`; worktree `K:\Documents\Obsidian\worktrees\home-automation-project\agent_005-implement-invalid-co-adc-fault-reporting`.

<details><summary>Acceptance output (tail)</summary>

```
(no acceptance_cmd on card)
```
</details>

<details><summary>Review</summary>

The change meets the card, and I'm passing it. The 26 model tests pass, but I could not compile the ESPHome YAML here, because `esphome config` printed nothing and there is no `secrets.yaml`.

**What changed**
- The card names `ventsys_fdm_sensor_co.yaml`, but the edit is in `ventsys_air_sensor_co.yaml`. That file is the shared CO package: `ventsys_fdm_sensor_co.yaml` pulls it in through `ventsys_fdm_sensor.yaml`, so the FDM board gets the fix.
- Nothing in "Don't touch" changed. The only files edited are one firmware package, `main/dashboards/ventsys-model.mjs`, one docs page and one test file.

**Do items**
- **Moving average and fault delay removed:** the five-reading moving average on `co_voltage` and the 15 s `delayed_on` on `co_sensor_fault` are gone. A bad sample is no longer smoothed away or held back.
- **Warm-up gate removed from the fault:** `co_sensor_fault` no longer waits for `gas_sensors_ready`, so it can report during warm-up.
- **Detection checks the sample itself:**
  - `co_detected` re-checks `isfinite` and the low and high voltage limits on the sample it reads. It also recomputes the ratio from that sample rather than reading the template `co_ratio` sensor, so the fault classification applies before detection.
  - The ratio sensor and the baseline-capture button use the same limits.
- **Dashboard regex fix:** `ventsys-model.mjs` changes the capture to lazy (`+?`). The greedy version matched `..._co_sensor_fault` as prefix `x_co` plus kind `sensor_fault`. The test checks the CO fault is reported as `co sensor fault`.
- **Docs:** `ventsys-dashboard.md` describes the new behavior. It says the change is not deployed or bench-verified, and that an alarm can briefly outlast a fault because of the existing 5 s on and 15 s off detection delays.

**Acceptance**
- **Fault on invalid reading:** met. NaN, below 0.02 V or above 3.25 V now faults.
- **Fault before detection:** met, as described above.
- **Dashboard display:** met. The new test checks an orange fault incident and the "unverified signal" red label when detection and fault are both on.
- **Docs:** met.
- **Firmware tests:** none exist. There is no firmware test harness, and bench verification is out of scope for this card.

**Non-blocking notes**
- `co_sensor_fault` and `co_detected` are template binary sensors with no `update_interval`, so they poll every 60 s. This was already true before the change. Dropping the 15 s delay does not make the fault itself faster, because it still updates only on the 60 s poll.
- With the warm-up gate removed, a boot-time NaN reading may raise a brief fault until the next poll. The docs describe this as including warm-up, so it looks deliberate.
- `main/TO-DO.md` still shows the item unchecked. That is right while bench verification is pending, but a short "firmware candidate done" note would help.

VERDICT: PASS
</details>

<details><summary>Branch log</summary>

```
b79a989 fix: report invalid CO readings as faults
8e8f8a6 docs: cleanup storage migration artifacts and update docs
ae605c2 feat: record home automation project updates
9ebc4b2 feat(recomp): expand food and workout tracking
fbc19d9 feat(monitoring): expand diagnostic dashboard
5ebfc42 feat(workbench): expand read-only evidence
c995e1e feat(solar): add observatory display
2596ddd fix: correct monitor-only update counts
c05e018 docs(recovery): verify archives and close stale gates
5741785 fix: bound alerts and document recovery proof
```
</details>
