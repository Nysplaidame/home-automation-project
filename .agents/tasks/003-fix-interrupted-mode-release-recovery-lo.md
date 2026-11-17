---
id: 003
title: Fix interrupted mode-release recovery logic
status: done
tier: executor
agent: codex
reviewer: claude
base: codex/portal-refinement
base_commit: 8e8f8a6a4a0898ae6db0002470edfd1833b4db8d
branch: agent/003-fix-interrupted-mode-release-recovery-lo
created: 2026-11-12
---

## Goal
The system saves desired intent before valve closures and retries omit released valves and shared paths.

## Read first
- main/TO-DO.md - current task definition
- main/ventsys/ - relevant codebase
- main/configs/esphome/ - ESPHome configuration
- main/dashboards/ - dashboard components
- main/docs/ - documentation

## Do
1. Review main/TO-DO.md for the specific requirement to save desired intent before valve closures.
2. Analyze main/ventsys/ to locate the current mode-release and retry logic.
3. Modify the code to persist the desired intent state durably before initiating valve closures.
4. Update the retry mechanism to check the saved intent and omit valves/paths that have already been released.
5. Replace any misleading retry guidance in the code or comments with accurate logic.
6. Verify that pending ownership is preserved durably through the restart/retry cycle.

## Don't touch
- Physical hardware tests
- Camera reconnection
- SMB capture tooling
- Fan speed decisions

## Acceptance
- [ ] Code saves intent before valve closure actions.
- [ ] Retry logic correctly omits released valves.
- [ ] Retry logic correctly omits shared paths.
- [ ] Pending ownership is preserved in the state.

## Result
- Commit(s): `0f2231a` — `fix: preserve pending mode release ownership`
- Acceptance output: Pass — 10 operating-package tests passed; dashboard JavaScript syntax and `git diff --check` passed. The card specified no acceptance command.
- Notes / follow-ups: Changes are local and have not been deployed. Home Assistant restart acceptance remains outstanding. The existing generator could not run against the already-generated dashboard package; the generated files were updated directly. Git emitted a `packed-refs.lock` permission warning, but the commit succeeded.

**Dispatcher (2026-11-12):** status `done`; worktree `K:\Documents\Obsidian\worktrees\home-automation-project\agent_003-fix-interrupted-mode-release-recovery-lo`.

<details><summary>Acceptance output (tail)</summary>

```
(no acceptance_cmd on card)
```
</details>

<details><summary>Review</summary>

I checked the diff against the card and found nothing that blocks it, so this is a PASS. The Python tests pass, but the dashboard JS changes and the dispatcher guard have no test coverage. I did not run the live Home Assistant or the dashboard.

**Do items**
1. **TO-DO reviewed:** `main/TO-DO.md` carries the requirement and is annotated "local candidate; deployment and HA restart acceptance outstanding", which is honest.
2. **Logic located:** the change is in the generator `main/tools/generate_ventsys_operating_modes.py` and the generated `ventsys_operating_modes.yaml`. The drift test passes, so the generated YAML matches the generator.
3. **Intent saved before closures:** the helper write now includes `pending_key`, `pending_request` and `pending_strength`, followed by `homeassistant.save_persistent_states`. Both come before the phase loop. A success write after the loop clears the pending fields and saves again.
4. **Retry omits released valves and shared paths:**
   - `current_key` now prefers `pending_key`, so a retry rebuilds the original plan from the pre-transition ownership key. That plan includes the SLA branch, print, 360 and `main1` valves.
   - The guard only accepts a retry of the same request and strength.
   - Setup tests, reference recording and the normal-command dispatcher are blocked while a transition is pending. The dispatcher is still unblocked for the owning script.
5. **Misleading guidance replaced:** the timeout message now says "retry the same request to reconcile". The doc section is rewritten, and the dashboard shows the new text when `pending_key` is set.
6. **Ownership preserved across restart:** the persistent-state save is in place, and the worst-case JSON is about 211 characters against the 255 limit.

**Don't touch:** none of the excluded areas changed. There are no changes to firmware, ESPHome config, camera, SMB or fan-speed logic. Fan speeds are only carried along unchanged in the saved state.

**Acceptance**
- **Intent saved before closures, and pending ownership in state:** `test_interrupted_release_retains_ownership_and_retries_original_plan` checks these.
- **Retry omits released valves and shared paths:** the same test asserts the retry plan equals the original plan and includes `sla_branch`, `sla_print`, `sla_360` and `main1` (closed). It also asserts that a different request (`fdm:off`) is rejected while pending.
- **Tests run:** 10 operating-package tests and 37 related tests pass (operating-modes, script-drift, arbitration, dashboard-package, reference-controls). The two phase-index tests were updated for the extra step.

**Non-blocking notes**
- There is no test for the dispatcher's new `pending_key and not owner` guard in `ventsys_ha_scripts_arbitrated.yaml` or for the `ventsys-card.js` changes.
- If the same request can never succeed (for example a board stays offline), every other normal command is blocked until it does. Only fire and failsafe bypass this. Worth confirming that is intended.
- The pending write and the final write both use revision `current.revision + 1`, so the revision is unchanged across pending to complete. This is harmless because the pending fields differ.

VERDICT: PASS
</details>

<details><summary>Branch log</summary>

```
0f2231a fix: preserve pending mode release ownership
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
