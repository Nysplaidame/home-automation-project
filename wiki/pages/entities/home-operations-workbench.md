---
title: "Home Operations Workbench"
category: entity
tags: [software, household, diagnostics, recovery, meals, ventsys]
created: 2026-09-06
updated: 2026-09-07
sources: [project-todo]
status: active
---

# Home Operations Workbench

**Type:** local static proof-of-concept application
**Status:** Not deployed; fixture and saved health-snapshot imports only
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

- 2026-09-06: model tests passed for schema rejection, unsafe link/detail
  filtering, dependency grouping, recovery evidence and meal availability.
- 2026-09-06: browser smoke test passed at desktop and mobile dimensions with
  no console errors or horizontal overflow.

## Open Questions

- [ ] Decide whether a live successor belongs in Household Hub or a separately
  placed service.
- [x] Define offline Windows/Proxmox adapters with a 36-hour freshness window, explicit legacy timezone and unknown missing evidence.
- [ ] Define least-privilege authenticated collection for any future live adapter.
- [ ] Complete the existing Troubleshooting Dashboard Proxmox snapshot gate
  before reusing live diagnostic evidence.
- [ ] Keep VentSys interaction visual-only until hardware and safety acceptance
  have independently completed.

## Change Log

- 2026-09-06: Created as a verified local proof of concept for the selected
  roadmap workflows; no service or home-automation state changed.

- 2026-09-07: Added offline health imports and non-overwriting CLI conversion; raw collector details are discarded and backup freshness cannot imply integrity or restore proof. Desktop/mobile smoke passes. See [[project-todo]].
