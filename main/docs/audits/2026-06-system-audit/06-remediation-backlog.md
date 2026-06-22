---
title: Risk-Ranked Remediation Backlog
created: 2026-06-21
modified: 2026-06-21
type: audit-backlog
status: open
---

# Risk-Ranked Remediation Backlog

Discovery and remediation remain separate. Work in this order because later tests depend on earlier trust and recovery controls.

| Order | Findings | Corrective work | Exit gate |
|---:|---|---|---|
| 1 | F-001 | Rotate/revoke exposed REST API material, remove tracked settings, purge history, audit copies/access | Old material rejected; current/history scans clean |
| 2 | F-002, F-006 | Recover CT 114 lock/snapshot using supported procedure; increase/move backup capacity; rerun backup | Fresh 114 backup, integrity pass, no lock, safe free-space margin |
| 3 | F-003, F-005 | Freeze VentSys adoption; decide calibration/timing; reconcile HA source/live and deploy once | Source/live hashes equal; config check and MQTT dry tests pass |
| 4 | F-004, F-015, F-017 | Redesign ESP8266 TLS path or hardware; fix future ESPHome errors and misleading file | Every intended firmware config validates and compiles |
| 5 | F-008, F-009 | Replace `_verify.ps1`; make health probe platform/profile/VM/LXC aware | Same green result from Proxmox and supported management host |
| 6 | F-007, F-011, F-014 | Repair canonical links, DNS/status contradictions, wiki drift | Link checker clean except explicit examples; matrices resolve live |
| 7 | F-010 | Pin image policy, add meaningful health checks, minimize/proxy Docker socket access | Compose validation and controlled restart tests pass |
| 8 | F-012 | Add dashboard tests for init safety, unavailable entities, connection loss, mobile view and console errors | Browser suite passes with no production MQTT writes |
| 9 | F-016 | Resolve or document Frigate RPC mount failure before NAS/NFS cutover | No unexplained failed units |
| 10 | F-013 | Re-run official vendor compatibility review | URLs, versions and dated decisions recorded |
| 11 | R/P cards | Execute scheduled resilience, restore and physical acceptance tests | Each card has evidence and normal-state restoration proof |

After remediation, update canonical docs and TODOs from evidence; do not merely mark this backlog complete.

