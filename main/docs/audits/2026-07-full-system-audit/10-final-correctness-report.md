---
title: July 2026 Final Correctness Decision
created: 2026-07-10
modified: 2026-07-10
type: audit-decision
status: discovery-frozen
---

# Final Correctness Decision

## Decision: `not certified`

The audit is complete enough to make a negative correctness decision, but the
estate is not certified. Audit completion is not system correctness.

Any one of the following prevents certification; all are currently present:

- a live credential and private key are retained in current Git and history;
- ignored automation secret files are locally readable/modifiable beyond their
  required operator identities;
- Immich and Transfer Portal are actively failed;
- current router source is unsafe to deploy over the live VLAN 50 identifiers;
- Frigate's CT is at critical thin/root capacity;
- automatic HA recovery omits apps and representative restores are unproved;
- critical data lacks a proved independent/off-site failure domain;
- Docker/monitoring negative ACL enforcement, Tailscale policy, and managed
  switch configuration/persistence are unverified;
- physical power/UPS and VentSys safety acceptance are absent.

## What is working

The negative decision does not mean the entire estate is down. HA, one-camera
Frigate recording to OMV, MQTT TLS, core VM/CT backups, most Docker apps,
monitoring dashboards, local AI/voice containers, md0 RAID1 and the live
HomeIoT isolation path are operating. Static router previews, repository
verification, Transfer Portal unit tests, VentSys source contracts and intended
ESPHome YAML validation pass.

Those successes are narrower than the correctness contract: they do not prove
least privilege, restoreability, safe redeployment, physical fail-safe
behaviour, or independent recovery.

## Certification blockers by domain

| Domain | Decision | Principal blockers |
|---|---|---|
| Repository and secrets | Fail | F-001, F-015, F-023, F-027 |
| Network and trust | Fail | F-003, F-010, F-011, F-012, F-016 |
| Home Assistant | Conditional service health / estate fail | F-006, F-013, F-017, F-018 |
| Frigate/CCTV | Fail | F-004, F-019, blocked outage/capacity tests |
| Docker applications | Fail | F-002, F-007, F-015, F-028 |
| OMV/storage | Fail | F-009, F-011, no independent copy |
| Monitoring/operations | Fail | F-014, F-024 |
| Local AI/voice | Fail | F-013, F-020, blocked adversarial/load tests |
| Backup/recovery | Fail | F-005, F-006, F-007, F-025 |
| Physical/VentSys | Blocked and therefore fail | F-021, F-022 |

## Evidence limitations

The decision is based on read-only observation and static validation. Switch
and Tailscale administrative state, password-manager contents, upstream router,
physical hardware, and disruptive negative/resilience tests were not available
or authorized. They are recorded as blockers, never treated as passes.

The operator subsequently confirmed that off-site/independent copies and
isolated restores are not feasible, no UPS exists or is planned, and VentSys is
not mature enough for physical acceptance. These are explicit accepted or
deferred residual risks in `12-owner-decisions.md`; they preserve the
`not certified` decision but are removed from the actionable remediation queue.

## Reissue gate

A later report may improve the decision only after the approved remediation
waves and exact retest gates in the findings and resilience cards. Critical and
high findings may be accepted/deferred by an owner, but an accepted active
secret, unproved critical restore, unexplained ACL, or unverified physical
safety path cannot receive full certification.
