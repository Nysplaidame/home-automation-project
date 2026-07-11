---
title: July 2026 Full Home-Automation Estate Audit
description: Evidence pack for repository, live infrastructure, security, recovery, documentation, and physical-system review
created: 2026-07-09
modified: 2026-07-10
type: audit
status: discovery-frozen-not-certified
---

# July 2026 Full Home-Automation Estate Audit

This directory is the evidence-first discovery pack for the full estate audit.
Discovery does not authorize production remediation. Live checks are read-only
unless a later test card is individually approved by the operator.

## Evidence precedence

1. Current observed live behaviour and configuration.
2. Canonical active records and source configuration.
3. Durable decisions and procedures.
4. Wiki material.
5. Historical and archived material.

A reachable endpoint proves reachability, not functional correctness. A parse
pass proves syntax, not safe behaviour. A checked task proves only that the
project record asserts completion until independently corroborated.

## Generated ledgers

- `artifact-inventory.csv`: tracked and relevant untracked source validation.
- `worktree-file-inventory.csv`: path, state, size, and SHA-256 for every
  non-`.git` file, including ignored ESPHome build output and vendor material.
- `live-component-inventory.csv`: every observed guest, container, HA app,
  control plane, client class, and pending physical component.
- `todo-disposition.md`: all checklist rows from the canonical task files.
- `roadmap-disposition.md`: open roadmap candidates awaiting evidence review.

## Evidence and decisions

- `01-scope-baseline.md`: immutable baseline, tools, scope, and safety limits.
- `02-static-test-record.md`: repository validation and static findings.
- `03-live-evidence.md`: sanitized read-only live observations.
- `04-dependency-matrix.csv` and `04-architecture.mmd`: producer/consumer and
  failure-domain model.
- `05-backup-recovery-matrix.md`: dataset-level protection and restore gaps.
- `06-claim-traceability.md`: material current claims and dispositions.
- `07-findings.md`: risk-ranked findings with correction and retest gates.
- `08-resilience-test-cards.md`: individually approval-gated negative tests.
- `09-remediation-backlog.md`: proposed waves; no wave is authorized here.
- `10-final-correctness-report.md`: frozen `not certified` decision.
- `11-vendor-compatibility.md`: point-in-time primary-source review.
- `12-owner-decisions.md`: accepted recovery/power constraints and deferred
  physical testing recorded after discovery.
- `HANDOFF.md`: safe restart point for an approved remediation session.

The discovery decision is frozen. Later remediation must issue a new dated
correctness report rather than editing this decision into a pass.
