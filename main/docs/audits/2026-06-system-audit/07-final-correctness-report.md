---
title: Final Correctness Report
created: 2026-06-21
modified: 2026-06-21
type: audit-report
status: not-certified
---

# Final Correctness Report

## Decision

**The home automation system is not certified correct.**

The deployed network, core compute, HA, Docker-host services, Frigate baseline, local AI and monitoring are substantially operational. Router source/live validation is unusually strong. Those successes do not outweigh the unresolved trust, recovery, and safety-control failures.

## Goal status

| Goal | Assessment |
|---|---|
| Secure segmented network | Met for router structural/live policy; representative source-VLAN tests remain |
| Rebuildable core infrastructure | Partially met; source/live HA drift and incomplete manuals prevent certification |
| Reliable monitoring | Operational baseline met; independent alert/recovery testing remains |
| Recoverable system | Not met; CT 114 backup failed and no sandbox restore was performed |
| Production NVR/storage | Planned; hardware and OMV storage absent |
| Fire-safe VentSys | Not met/unverifiable; hardware incomplete and safety scripts drift |
| Secret management | Not met; active private material is committed |
| Roadmap feasibility | Mostly feasible with prerequisites; three AI/tooling concepts require redesign |

## Acceptance criteria review

- Every tracked artefact has an inventory result: **met**.
- Every TODO has a disposition: **met**, with checked operational claims still subordinate to claim evidence.
- Every roadmap candidate has a feasibility path: **met locally**, external vendor verification blocked.
- Every active factual/completion claim is represented: **met for canonical system-level claims**, not every prose sentence.
- Every critical service has positive, negative, failure, recovery, observability and backup proof: **not met**; disruptive tests are pending.
- No unexplained canonical/config/live contradictions: **not met**.
- Safety is not certified from configuration alone: **met**.
- Temporary policy restored after tests: **met**; no policy mutation occurred.
- Findings include evidence, action and retest gates: **met**.

## Residual risk

Critical credential exposure may allow unauthorized local REST API access until rotation and history cleanup finish. Backup failure means the newest llm-host state is not protected by the scheduled job and local backup capacity is fragile. VentSys source/live divergence could produce wrong valve range and response timing when hardware is adopted. Four intended plug firmwares cannot implement the documented TLS configuration on their selected platform. No physical fire-safety or restoration claim is proven.

## Certification gate

Do not declare the system correct, adopt remaining VentSys hardware, or rely on unattended safety automation until F-001 through F-004 are closed, HA source/live parity is proven, a fresh CT 114 backup is restored in isolation, and the applicable R/P test cards pass. Reissue this report after remediation rather than editing the decision in place.

