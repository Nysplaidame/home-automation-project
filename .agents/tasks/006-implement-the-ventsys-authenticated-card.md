---
id: 006
title: Implement the VentSys authenticated card-to-page bridge
status: blocked
tier: executor
agent: codex
reviewer: claude
base: codex/portal-refinement
base_commit: 8e8f8a6a4a0898ae6db0002470edfd1833b4db8d
branch: agent/006-implement-the-ventsys-authenticated-card
created: 2026-11-12
---

## Goal
The local VentSys card and page communicate through the authenticated bridge defined by the existing contract. Contract behavior is covered by automated tests.

## Read first
- main/TO-DO.md - current bridge status and deployment constraint
- docs/procedures/ventsys-card-page-bridge-contract.md - required authentication and communication behavior

## Do
1. Inspect the bridge contract and the existing card, page, and browser tests.
2. Implement the contract’s authenticated communication between the card and page.
3. Add or update tests for authorized and unauthorized communication and contract-defined failure cases.
4. Run the relevant local tests, including the existing browser tests, and document any unresolved limitations.

## Don't touch
- Live dashboard deployment
- Public credentials
- Physical controllers and firmware

## Acceptance
- [ ] The card and page communicate locally according to the bridge contract.
- [ ] Automated tests cover successful authentication and rejected unauthorized requests.
- [ ] Relevant local tests pass, including the existing browser tests.
- [ ] The page remains offline and no public credentials are introduced.

## Result
- Commit(s): `7a8fd51` docs: record VentSys bridge acceptance gates
- Acceptance output: **Fail** — Node receiver test passed. `npm ci` and `npx playwright install chromium` failed with `ENOTCACHED`; `npm test` could not find Playwright, so the browser suite remains unverified.
- Notes / follow-ups: Run the dependency and Chromium installs, then the full browser suite in an environment with access to the required packages. The contract now documents the candidate and open gates. An untracked `.npm-cache` directory remains under `main/tools/playwright-smoke`; automatic approval review rejected its removal.

**Dispatcher (2026-11-13):** status `blocked`; worktree `K:\Documents\Obsidian\worktrees\home-automation-project\agent_006-implement-the-ventsys-authenticated-card`.
- Notes: review FAIL after one fix round

<details><summary>Acceptance output (tail)</summary>

```
(no acceptance_cmd on card)
```
</details>

<details><summary>Review</summary>

The bridge is implemented as the card asks, but the browser tests, which the card requires, never ran, so this fails.

**Do items**
- **Implementation (done):** `ventsys-bridge-card.js`, `-page.html` and `-page.js` follow the contract's envelope.
  - Each message carries a version, type, random per-frame session ID, a monotonic sequence, issued and expiry times (15 s validity), and an exact-key schema.
  - The page rejects a wrong origin, wrong source window, wrong session, replay, expiry, unknown type (including `command`) and malformed payloads. It clears to "Offline" on failure, `pagehide` or expiry.
  - The card posts only to `location.origin`, never `'*'`, and sends only the allowlisted `input_boolean.ventsys_failsafe` field. No token, `hass` object or service proxy reaches the page.
- **Tests (partly done):** a Node receiver test (`ventsys-bridge.test.cjs`) and a Playwright spec (`ventsys-bridge.spec.js`) were added. The Node test passes when I run it. The Playwright spec has never run.
- **Limitations (documented):** the TO-DO and contract doc say the browser and HA lifecycle gates remain open.

**Don't touch:** the diff has no changes to live deployment, credentials or firmware/controllers. The page is offline, and no public credentials are introduced.

**Acceptance**
- **Local communication per contract:** met by code review. It has not been exercised in a browser.
- **Tests cover successful authentication and rejected requests:** the unit test covers both well. The browser spec covers a wrong origin, reload and disconnect, but has never executed, so its correctness is unverified.
- **Relevant local tests pass, including existing browser tests:** not met.
  - `@playwright` is not in `node_modules`; only `pngjs` and `three` are there.
  - The executor reports that `npm ci` and Chromium installation failed. None of the existing browser specs (dashboard, screensaver, `ventsys-card`, `ventsys-touch`) nor the new one ran.
  - The TO-DO entry admits this.
- **Offline, no public credentials:** met.

**Minor, non-blocking**
- The unit test doesn't cover `pagehide`, a missing session attribute, or an expiry timer set to the right delay.
- The browser spec only tests a wrong origin, not a wrong source window. The unit test does cover wrong source.

1. `main/tools/playwright-smoke` (environment): `@playwright/test` and Chromium are not installed. Fix: install them with network access or a populated cache, then run `npm test` or `npx playwright test` for the full suite. This must include the existing specs and `ventsys-bridge.spec.js`.
2. `main/tools/playwright-smoke/tests/ventsys-bridge.spec.js`: it is unverified. Fix: run it, correct any failures, and confirm the order-dependent steps (post-reload session change, then `Connected`) pass without flakiness.
3. `main/TO-DO.md` and the contract doc: both say browser acceptance is open. Fix: after the suite passes, record the actual pass counts and mark that gate closed.

Plan mode was active, so I made no edits and wrote no plan file.

VERDICT: FAIL
</details>

<details><summary>Branch log</summary>

```
7a8fd51 docs: record VentSys bridge acceptance gates
86c43dc feat: add local read-only VentSys bridge
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
