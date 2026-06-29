---
title: June 2026 Remediation Execution and Replacement Correctness Report
description: Evidence and certification decision after the 2026-06-22 remediation pass
created: 2026-06-22
modified: 2026-06-22
type: audit
status: complete-with-blockers
---

# Remediation execution and replacement correctness report

## Decision

The system is materially safer and recoverable, but it is **not certified
correct**. Backup recovery, HA/VentSys source parity, ESPHome validation and the
Frigate failed-unit defect are remediated. Certification remains withheld for
the explicitly deferred credential/history finding F-001, OMV capacity above
the 80% gate, blocked browser/physical tests, and remaining container/vendor
review work.

## Production evidence

| Area | Result | Evidence |
|---|---|---|
| SMB transport | pass | OMV `New` requires encryption; Proxmox mount reports SMB 3.1.1 and `seal` |
| Access isolation | pass | Dedicated `proxmox-backup` identity and mode `2700` subdirectory; credential retained only in secure stores |
| Proxmox storage | pass-with-risk | `smb-backup-new` active; measured daily set is 45,175,709,568 bytes and seven generations project to 294.51 GiB, well below 80% of the 2.12 TB target; shared filesystem is already 87.34% used |
| Backup schedules | pass | VMs 100/102/103 at 02:00 and CTs 111/114 at 04:00; snapshot, ZSTD, `keep-last=7` |
| CT 114 recovery | pass | Confirmed no active task; supported `pct unlock` and `pct delsnapshot`; no remaining lock or `vzdump` snapshot |
| Fresh archives | pass | Fresh archives created for every active guest: 100, 102, 103, 111 and 114 |
| Archive integrity | pass | All five fresh archives passed `zstd -t` from the SMB mount |
| Restore | pass | VM 102 restored as 9102, NIC removed before boot, guest agent returned hostname `monitoring`, then guest was shut down and purged |
| Local retention | pass | Existing local archives were not removed |
| HA deployment | pass | Timestamped live backup created; canonical core files, VentSys packages/scripts and dashboard deployed |
| HA validation | pass | `ha core check` passed before/after deployment and again on HAOS 2026.6.4; HA restarted and port 8123 recovered |
| Source/live parity | pass | SHA-256 matched for configuration, automations, scripts, scenes, two VentSys packages and dashboard |
| VentSys command contract | pass | Mock executor checked 13 modes: valve helper emits one publish and each topic receives at most one direct `0` or `50` target |
| Dashboard init safety | pass-static | Startup uses pure renderers; initialization/render functions contain no publish path |
| ESPHome | pass | All 27 production YAML files validate; four ESP8266 native-API plug configurations compile |
| Router source | pass-with-prerequisites | Lint passes and preview compilation succeeds; strict deployment compilation correctly blocks unresolved device placeholders |
| Core reachability | pass | Router, HA, Frigate SSH, docker-host, Bambuddy, MQTT TLS, Grafana, Kuma, legacy local LLM runtime and OMV SMB checks pass |
| Frigate failed unit | pass | Dormant NFS/RPC units disabled in CT 111; `systemctl --failed` reports zero units |
| Monitoring | active-alert | Five-minute Proxmox timer checks core services, TCP 445 and storage; conservative shared-filesystem high-water policy currently alerts on OMV's 87.34% usage |

No password, generated account secret, private key or token is included in this
evidence pack.

## Repository remediation

- Replaced the stale-path `_verify.ps1` with a checkout-relative validator.
- Added a Windows health checker and made the Proxmox checker VM/LXC-aware,
  excluding intentionally stopped rollback VMs 101/104.
- Added repository-owned systemd service/timer definitions for recurring health
  checks and made storage threshold breaches affect exit status.
- Moved the four ESP8266 plugs from unsupported MQTT CA settings to encrypted
  native API control with `RESTORE_DEFAULT_OFF` and WPA2-only Wi-Fi.
- Converted the documentation-only main-fan YAML to Markdown and repaired its
  references; fixed ESPHome naming warnings.
- Hardened dashboard initialization and added Playwright/static contract tests.
- Reconciled HA configuration to the live baseline and deployed canonical
  direct-target VentSys scripts.
- Repaired the root handoff, project index, DNS/status and monitoring roadmap
  contradictions sampled by the audit.
- Updated current-live-state, service matrix and backup procedures for OMV and
  the seven-generation policy.

## Finding disposition

| Finding | Disposition |
|---|---|
| F-001 credential/private-key history | deferred by owner; unresolved critical certification blocker |
| F-002 CT 114 lock/backup | remediated and retested |
| F-003/F-005 VentSys and HA drift | remediated and source/live hashes verified |
| F-004/F-015/F-017 ESPHome defects | remediated; validation and compile gates pass |
| F-006 backup feasibility | storage moved and restore-proven; seven-generation projection passes, with shared-filesystem high-water risk retained |
| F-007/F-011/F-014 documentation contradictions | targeted defects remediated; full regenerated inventory remains the coverage record |
| F-008/F-009 validation tooling | remediated |
| F-010 container reproducibility | unresolved; requires a separately controlled service-by-service restart pass |
| F-012 dashboard coverage | static safety gate passes; real browser reload/reconnect/mobile/console suite blocked because the browser runtime is unavailable |
| F-013 vendor compatibility review | unresolved |
| F-016 Frigate RPC mount | remediated; zero failed CT units |

## Residual risk and blocked gates

1. F-001 remains unresolved by explicit decision. Rotate/revoke and purge Git
   history before any full certification.
2. Seven generations project to 294.51 GiB and pass the 2.12 TB target gate,
   but the larger shared filesystem backing `New` is already 87.34% used.
   Reclaim/expand it or explicitly approve a different high-water policy before
   treating the five-minute storage monitor as green.
3. Physical VentSys actuation, emergency cutoff, feedback mismatch and power-loss
   cards remain blocked by incomplete hardware. They are not passes.
4. Browser reload/reconnect, mobile layout and console-error testing remains
   blocked. The static no-publish invariant is not a substitute for that suite.
5. Container pinning/health/restart policy, vendor-version review and the wider
   approved-window resilience cards remain open.
6. The router's strict production compile still requires real MAC/device values;
   preview artefacts are not deployable configuration.

Temporary restore ID 9102 was purged. No temporary snapshot, guest lock, test
NIC, firewall rule, uplink, bypass or maintenance policy was left enabled by
this remediation pass.
