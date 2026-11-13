---
title: "Home Operations Workbench"
category: entity
tags: [software, household, diagnostics, recovery, meals, ventsys]
created: 2026-09-06
updated: 2026-10-04
sources: [project-todo]
status: active
---

# Home Operations Workbench

**Type:** local static proof-of-concept application
**Status:** Not deployed; fixture, saved health/Grocy/GardenKeeper/Mealie/Recomp selections and curated historical recovery imports only
**Related:** [[entities/household-hub]], [[entities/troubleshooting-dashboard]],
[[entities/ventsys]], [[analyses/household-workshop-operations-roadmap-2026-09]]

## Overview

The Home Operations Workbench is a local, import-only interface for the first
selected household-operations roadmap workflows. It presents daily household
evidence, possible shared dependencies, recovery readiness, meal availability,
and a command-free VentSys commissioning checklist from a versioned JSON model.
It is intentionally separate from the deployed household applications while a
live integration contract has not been selected.

## Key Properties

- Source path: `main/apps/home-operations-workbench/`.
- Schema: versioned `1.0` JSON; unsupported versions are rejected.
- Safety boundary: no live API connection, browser persistence, credentials,
  shell execution, MQTT publish, or source-system mutation.
- Evidence model: source and timestamp plus `healthy`, `failed`, `warning`,
  `stale`, `unknown`, or `planned_offline` status.
- Recovery model: backup, integrity and restore exercise stay separate;
  completed backup evidence cannot imply a tested restore.
- Export: local incident reports and emergency evidence packs only.

## Verification

- 2026-10-04: saved GardenKeeper pending-task selections import locally with
  observation freshness, explicit UTC due times and bounded display. Private
  notes/identifiers are omitted; empty selections cannot imply garden coverage.
  Twenty-five unit tests and all three desktop/320px browser suites pass.
  Only the live API schema was read; no real task records or live integration
  were accepted. See [[../../../main/docs/procedures/read-only-product-release-plan]].

- 2026-10-02: portable selected-runbook bundle includes seven systems and13
  documents with clickable index, link manifest and17 checksummed files.
  Twenty unit tests and independent checksum verification pass. Fifty-four
  omitted references remain explicit; this is offline reading coverage, not
  full-estate executable/data recovery. Generated output remains outside the vault.

- 2026-10-02: saved Hub Grocy overview converter verified with sixteen total
  Workbench unit tests and desktop/320px fresh/stale/unavailable imports. Shopping
  notes/unknown fields are excluded; best-before dates retain their meaning.
  Synthetic rows are not household evidence; real-data and live acceptance remain open.
  The file picker also accepts the saved Grocy envelope directly, calculating
  freshness on import. BOM, invalid/oversized file errors, preserved previous
  evidence and Clear pass desktop/320px checks.

- 2026-10-02: twelve unit tests plus desktop/320px historical recovery import
  checks pass. Seven scoped records preserve stale backup evidence and unknown
  complete-system restore status; a local exporter adds validated vault-relative
  source/runbook paths without overwriting output. Partial VM102 boot and
  Hub/GardenKeeper component proof remain labelled; no fresh backup inferred.
- 2026-09-06: model tests passed for schema rejection, unsafe link/detail
  filtering, dependency grouping, recovery evidence and meal availability.
- 2026-09-06: browser smoke test passed at desktop and mobile dimensions with
  no console errors or horizontal overflow.

## Open Questions

- [ ] Decide whether a live successor belongs in Household Hub or a separately
  placed service.
- [x] Define offline Windows/Proxmox adapters with a 36-hour freshness window, explicit legacy timezone and unknown missing evidence.
- [ ] Define least-privilege authenticated collection for any future live adapter.
- [x] September14–15 existing Troubleshooting Dashboard Proxmox snapshot
  acceptance; future freshness and full application restores remain separate.
- [ ] Keep VentSys interaction visual-only until hardware and safety acceptance
  have independently completed.

## Change Log

- 2026-09-06: Created as a verified local proof of concept for the selected
  roadmap workflows; no service or home-automation state changed.

- 2026-09-07: Added offline health imports and non-overwriting CLI conversion; raw collector details are discarded and backup freshness cannot imply integrity or restore proof. Desktop/mobile smoke passes. See [[project-todo]].

- 2026-10-04: added saved GardenKeeper task import, credential-fragment URL
  rejection and corrected list spacing; local browser regressions pass.

- 2026-10-04: pending imports cannot undo Clear, demonstration or a newer
  selection; obsolete errors are suppressed. Controlled delayed-read checks
  pass at desktop/320px. Summary counters explicitly describe dependencies,
  independently of household task rows. No live application changed.

- 2026-10-04: all three saved-source adapters share strict timestamp validation;
  rolled-over clocks and any future observation cannot imply health or backup
  freshness. Source microseconds are accepted at millisecond display precision.
  All28 unit tests and three desktop/mobile browser suites pass; no live changes.

- 2026-10-04: saved Mealie paginated plan import adds an explicit calendar-date
  selection, preserving freshness and unknown ingredient availability. Private
  recipe/notes/identifiers are omitted; no complete-plan coverage is inferred.
  All33 unit tests and three browser suites pass. Only public schema metadata
  was read; household pilot, source combination and live release remain open.

- 2026-10-04: a combined saved household bundle shows GardenKeeper, Grocy and
  Mealie together while retaining independent observations and unavailable
  isolation. Malformed bundles are rejected atomically; source summaries survive
  operation caps. All38 unit tests and three browser suites pass. Real-data pilot,
  Recomp, diagnostic/recovery composition and live release remain open.

- 2026-10-04: saved Recomp routine projection follows weekday and one-off move
  semantics without health/session history or completion/readiness inference.
  Versioned four-source Today composition retains the three-source contract.
  All45 unit tests and three browser suites pass. Programme coverage, genuine
  household pilot, diagnostic/recovery composition and live release remain open.
