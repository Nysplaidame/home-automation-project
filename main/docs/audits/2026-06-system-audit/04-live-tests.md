---
title: Live and Static Test Record
created: 2026-06-21
modified: 2026-06-21
type: audit-evidence
status: complete-with-blockers
---

# Live and Static Test Record

## Static validation

| Test | Result |
|---|---|
| Git worktree before audit | Clean |
| Tracked artefact inventory | 448 recorded |
| JSON/YAML/Python syntax | 19 JSON, 66 YAML/YML and 6 Python files parsed; no base syntax failures |
| PowerShell parse | Zero parser errors |
| Router source lint | Pass |
| Router compile | First-flight pass; full preview pass with documented placeholders allowed |
| Active documentation links | Stale wrapper/index targets plus unresolved wiki concepts; see F-007 |
| Secret scan | Critical tracked REST API credential/key found; see F-001 |
| ESPHome | 24 device files pass; 4 plug files fail; one documentation-only YAML fails; warnings recorded |
| Compose static review | Syntax passes; widespread floating tags/missing health checks/socket mounts |
| Dashboard browser test | Blocked: browser runtime and Node/npm unavailable |

## Network and endpoint tests

| Test | Result |
|---|---|
| Router full post-deploy validation | 87 PASS, 0 WARN, 0 FAIL |
| Router active connectivity/nftables | 85 PASS, 0 WARN, 0 FAIL |
| First-flight router profile against current live router | 8 expected Wi-Fi-state failures; wrong profile for full deployment |
| Management-origin TCP | Proxmox, HA, docker-host, llm-host, Frigate, Grafana, Kuma and InfluxDB reachable |
| Management-origin HTTP | Core and documented application endpoints returned 200/302 as appropriate |
| OMV | Unreachable as documented/planned |
| DNS | Core host aliases resolve; router alias mismatch recorded |
| Tailscale | Node online; only HA, OMV and monitoring `/32` routes advertised |

ICMP failure for HA/docker/NVR/monitoring targets was not treated as outage because TCP/HTTP succeeded and firewall policy is restrictive.

## Host and service tests

| Component | Result |
|---|---|
| Proxmox guest state | Matches current-live-state |
| Docker host | Debian 13, UFW active/default deny, no failed units, documented workloads live |
| Monitoring VM | Four expected containers live; no failed units; 21% root use |
| Frigate CT | Container healthy, 24% root use; RPC mount unit failed |
| llm-host CT | Five expected containers live; 29% root use; legacy local LLM runtime model 100% GPU |
| HA | 2026.6.3, UI live, source/live hashes compared, registry and read-only state DB sampled |
| HA monitoring entities | Grafana, InfluxDB, Kuma and aggregate health states all `on` in latest recorded state |

## Backup tests

Latest available archives for VM 100, VM 102, VM 103, CT 111 and CT 114 passed low-priority `zstd -t`. CT 114’s latest *scheduled attempt* failed for no space; its passing archive is the previous day’s file. No restore was attempted.

## Tests deliberately not run

- Firewall changes, service stops/restarts, broker/DNS outages, route withdrawal or Tailscale ACL mutation.
- HA service calls or MQTT publications that could actuate VentSys entities.
- Sensor disconnection, power cutoff, fan/valve movement, emergency response or manual override.
- Production or sandbox restore.
- Camera and NAS tests for absent hardware.

