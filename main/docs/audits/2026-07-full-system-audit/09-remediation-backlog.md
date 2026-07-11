---
title: July 2026 Risk-Ranked Remediation Backlog
created: 2026-07-10
modified: 2026-07-10
type: audit-remediation-plan
status: proposed-not-authorized
---

# Risk-Ranked Remediation Backlog

Discovery is frozen before remediation. Each wave needs separate scope and
approval; production changes are not implied by this document.

## Wave 0 — Immediate containment and data-loss prevention

1. F-001: scope and rotate the tracked Obsidian REST credential/key; establish
   the history-rewrite decision.
2. F-004: protect CT 111 from exhaustion without deleting footage until backup
   and retention approval exist.
3. F-002: prepare a mount-safe Immich recovery and backup proof; restore service
   only in an approved window.
4. F-008: stop the Transfer Portal restart storm or repair the bind only after
   job/mount proof and approval.

Exit gate: no live secret remains valid in Git, capacity has safe headroom,
Immich/Transfer Portal have objective health state, and all containment
rollbacks are documented.

## Wave 1 — Trust and access controls

1. F-010/F-011: reconcile every router, UFW, `DOCKER-USER`, Docker publish and
   NFS identity rule; run positive/negative tests.
2. F-012: obtain owner-supervised switch and tailnet evidence; verify saved
   config, `/32` approvals, grants/ACLs, accounts and recovery ownership.
3. F-016/F-017/F-028/F-029: unify PKI/client trust, retire redundant HA SSH
   exposure, rotate/harden host and workstation secrets, and constrain backup
   and local filesystem ACLs.
4. Reconcile Fail2ban/service-auth coverage and dormant WireGuard intent.

Exit gate: every intended flow has source and destination enforcement, all
representative denies pass, and no unexplained privileged path remains.

## Wave 2 — Backup and recovery

1. F-006/F-007: define achievable RPO/RTO, include required HA apps, and add
   app-native Household Hub/Bambuddy/Immich/monitoring backups. F-005's
   independent-copy and isolated-restore gates are owner-accepted residual risk.
2. F-009: retain OMV config/export evidence and reconstruct router/switch/OMV
   configs in a clean, isolated workflow.
3. F-025: remove unintended schedule overlap and prove application consistency.
4. Keep local archive-stream verification and rebuild documentation current.
   RC-08 and RC-09 are retained but not scheduled due unavailable resources.

Exit gate for this constrained estate: every achievable local backup has an
owner, freshness monitor and documented rebuild path. This wave cannot satisfy
the original full-certification restore/failure-domain gate.

## Wave 3 — Source/live reconciliation

1. F-003: design and execute the HomeIoT internal-identifier migration or
   revert source to the durable live identifier.
2. F-019: make Frigate detection phase explicit and reconcile the OMV path.
3. Canonicalize live Immich/ntfy/Watchtower/Bambuddy/Household Hub/GardenKeeper
   source and remove unexplained drift.
4. Decide Sonarr placement and retire or onboard it.

Exit gate: semantic source/live comparison has no unexplained difference and a
clean checkout reconstructs every service without live-file archaeology.

## Wave 4 — Service reproducibility and observability

1. F-014/F-015: regenerate monitoring from the service matrix; add backup-age,
   guest-disk, mount and dependency checks; remove retired probes.
2. Pin supported images/models/digests; add health checks, limits and rollback
   manifests; minimize Docker socket exposure.
3. F-020/F-024: run controlled update and shared-resource campaigns with staged
   rollback.
4. F-027: validate and govern the Mermaid Viewer overlay before deployment.

Exit gate: false-green tests fail correctly, alerts reach an independent path,
and clean builds use reviewed immutable artifacts.

## Wave 5 — AI/voice safety and privacy

1. F-013: reduce log sensitivity, enforce non-model tool authorization and
   write confirmation, and add prompt-injection/cross-tool tests.
2. Prove no AI-accessible tool can directly control emergency, ventilation,
   alarm, access, or other safety-critical logic.
3. Establish data-retention and model/prompt provenance policy.

Exit gate: valid tools are deterministic, ambiguous/adversarial requests cannot
write, private payloads do not appear in normal logs, and safety paths are
structurally inaccessible.

## Wave 6 — Documentation and wiki

1. F-023: repair README, current-live-state, matrices, START-HERE, backup
   strategy, decisions, TODOs, handoffs and install paths from retest evidence.
2. Preserve old audits/handoffs as historical records; mark supersession rather
   than rewriting history.
3. Repair wiki conflicts after canonical docs are correct; add link, placeholder,
   claim and `Run on:` verification.

Exit gate: every claim has a disposition/evidence owner, all active links and
paths pass, and the rebuild sequence can be dry-read by a second operator.

## Wave 7 — Physical acceptance and resilience

1. F-022: document the absence of UPS protection plus manual recovery and boot
   order; UPS-runtime testing is not planned.
2. Keep VentSys at design review only. RC-16 remains deferred until the system
   is mature enough for physical acceptance.
3. Execute camera outage, storage loss and six-camera/GPU capacity cards.

Exit gate: signed physical evidence proves fail-safe states, persistence,
recovery order, capacity and independent alerting.

## Final reissue

After approved waves, do not edit the discovery decision below. Re-run the
exact gates and issue a new dated correctness report that references this pack
and states `certified`, `conditionally certified`, or `not certified`.
