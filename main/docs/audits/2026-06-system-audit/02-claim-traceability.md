---
title: Claim Traceability Matrix
created: 2026-06-21
modified: 2026-06-21
type: audit-evidence
status: complete
---

# Claim Traceability Matrix

| ID | Claim | Evidence | Status | Gap / next proof |
|---|---|---|---|---|
| C-001 | The project provides a correct fire-safety automation system | Hardware is mostly absent; source/live scripts disagree | `unverifiable` | Physical safety acceptance suite required |
| C-002 | Ten routed network segments are deployed | Router interface, DHCP, nftables, and self-ping checks passed for VLANs 1/10/20/30/35/40/50/60/70/99 | `verified` | Add source-VLAN client tests |
| C-003 | Router full-profile policy is live and internally consistent | Full test 87 PASS; active connectivity 85 PASS; static lint passed | `verified` | Resolve DNS alias drift and record test profile guidance |
| C-004 | Proxmox host and documented guests are live | `qm list`, `pct list`, storage and version observed over SSH | `verified` | Clear CT 114 backup lock and capacity defect |
| C-005 | Retired VMs 101/104 are stopped while CTs 111/114 run | Live guest inventory | `verified` | Health script must stop treating VM 101 as failed |
| C-006 | HAOS 2026.6.3 is live | `.HA_VERSION`, HTTP 200, registry/database evidence | `verified` | None for liveness |
| C-007 | Repository HA configuration represents live HA | Live `configuration.yaml` differs materially; automations are line-equivalent | `contradicted` | Choose canonical live/source shape and check it before deploy |
| C-008 | Home Assistant configuration check passes | HA is running and logs are empty, but an explicit current `ha core check` was not invoked | `unverifiable` | Run supported HA config check and preserve result |
| C-009 | VentSys dashboard is deployed from source | Local/live hashes match | `verified` | Browser and no-publish-on-init tests remain blocked |
| C-010 | VentSys HA package/scripts are deployed from source | Package has small comment drift; script has functional 0–100 ramp versus source 0–50 direct-target behaviour | `contradicted` | Block adoption; reconcile then retest |
| C-011 | Frigate CT 111 baseline is healthy | Container reports healthy and UI port responds; one failed RPC mount unit exists | `verified` | Explain/clear failed unit; cameras remain planned |
| C-012 | Frigate and legacy local LLM runtime share the iGPU successfully | legacy local LLM runtime reports 100% GPU; devices exist in CT 114; Frigate config/container healthy | `unverifiable` | Capture simultaneous GPU/process telemetry under load |
| C-013 | Docker-host live workload list is accurate | Containers and documented HTTP endpoints observed | `verified` | Add health checks/version controls across stacks |
| C-014 | Monitoring stack and HA external-health backstop are live | Four containers live; HA database shows all four health entities `on` | `verified` | Alert/recovery test requires window |
| C-015 | ntfy alert dispatch is operational | Historical TODO evidence only; no outage/notification generated in this audit | `unverifiable` | Scheduled alert-path test |
| C-016 | Local backup policy protects all active guests | Jobs exist; latest 100/102/103/111 and prior 114 archives pass `zstd -t`; current 114 job failed for no space | `contradicted` | Repair lock/capacity, rerun, then sandbox restore |
| C-017 | Tailscale advertises only three host routes | Live preferences show HA `/32`, OMV `/32`, monitoring `/32`; node online | `verified` | Off-LAN ACL-negative tests require client |
| C-018 | OMV/NAS is planned, not live | Host `192.168.40.50` unreachable; docs label planned | `verified` | Procurement/build prerequisite |
| C-019 | Cameras/production Frigate inputs are planned | Baseline has no production camera evidence; docs label pending | `planned` | Hardware and credentials required |
| C-020 | ESPHome configurations are written and ready | 24 configurations validate, four ESP8266 plug configs fail, and one `.yaml` is documentation-only | `contradicted` | Correct TLS/platform design and file semantics |
| C-021 | Secrets stay outside Git | Tracked Obsidian REST settings contain an API key and private key across history | `contradicted` | Rotate, purge, prevent recurrence |
| C-022 | Rebuild manuals are operator-complete | 136 checklist items remain extant and 45 blocked; health script is context-sensitive | `contradicted` | Finish dry run, expected output, rollback and stopping gates |
| C-023 | Canonical DNS/service matrix matches live DNS | `router.home.local` documents `.10.1` but resolves `.1.1` | `contradicted` | Decide intended address and reconcile |
| C-024 | Lightweight health probe is reliable from its documented locations | Passes core network checks from Proxmox but falsely fails retired VM 101; management-laptop Git Bash run falsely failed five checks | `contradicted` | Make platform-aware and CT-aware |
| C-025 | Wiki navigation is intact | Multiple unresolved entity/concept links remain | `contradicted` | Repair links or label intentionally absent concepts |
| C-026 | Backup archives are at least compression-integrity valid | Latest available archives for 100/102/103/111/114 pass `zstd -t` | `verified` | Compression integrity is not restore proof |
| C-027 | AI cannot directly replace safety-critical logic | Current HA architecture separates conversation entities from YAML/MQTT safety logic | `verified` | Preserve as an explicit change-control invariant |

