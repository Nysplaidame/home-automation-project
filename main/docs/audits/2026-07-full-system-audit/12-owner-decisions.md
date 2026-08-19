---
title: July 2026 Audit Owner Decisions
created: 2026-07-10
modified: 2026-07-10
type: audit-decision
status: accepted-risk-and-deferral
---

# Owner Decisions

These decisions were supplied after discovery and do not rewrite the observed
findings or turn blocked tests into passes.

## Recovery scope

- No off-site/independent backup copy will be implemented because the operator
  does not have the required resources.
- No isolated VM, CT, application, or database restore campaign will be run for
  the same reason.
- The operator accepts the resulting common-mode loss and unproved-restore
  risks. Current local backups, archive-stream checks, repository source, and
  rebuild documentation remain the achievable protection boundary.
- This prevents full certification under the original completion contract but
  does not prevent remediation of the other findings.

## Frigate footage and CT capacity

- Existing pre-OMV recordings on CT 111 are disposable.
- CCTV footage is currently retained for motion-detection tuning and later AI
  detection work, not as security evidence.
- Deleting the old local recordings is the selected remediation for CT 111
  capacity. The deletion is deliberately deferred to the remediation chat so
  the exact local path, current NFS target, active writers, before/after usage,
  and rollback limitations can be verified immediately before execution.
- Current OMV recordings and the Frigate database/config are outside that
  deletion scope.

## Power resilience

- There is no UPS and none is currently planned.
- The operator accepts outage, unclean-shutdown, and same-site power risks.
- Documentation should describe safe manual recovery and boot ordering, but the
  audit must not imply power continuity or graceful automated shutdown.

## VentSys maturity

- VentSys is not mature enough for formal physical acceptance testing.
- Source contracts, ESPHome validation, wiring/BOM review, and explicit
  design-stage hazards remain useful; physical certification is deferred until
  hardware and design maturity justify it.
- VentSys remains `planned/design-only`, never `verified` or `certified`.

## Audit consequence

The frozen correctness decision remains `not certified`. Remediation should
prioritize active secrets, failed services, router source/live drift, Frigate
capacity cleanup, trust/ACL defects, monitoring, and documentation. Accepted
resource constraints are retained as known residual risks in any later report.
