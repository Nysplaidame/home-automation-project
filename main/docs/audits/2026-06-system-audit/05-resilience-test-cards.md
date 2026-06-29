---
title: Scheduled Resilience and Physical Test Cards
created: 2026-06-21
modified: 2026-06-21
type: audit-test-plan
status: pending-windows
---

# Scheduled Resilience and Physical Test Cards

Every card requires an operator, start/end time, current backup evidence, rollback owner, and confirmation that temporary policy is removed afterward.

| ID | Scenario | Preconditions | Expected result | Rollback trigger / maximum outage |
|---|---|---|---|---|
| R-01 | Restore one current guest archive into an isolated ID/network | F-002 fixed; free capacity; archive integrity pass | Guest boots isolated and application data is coherent | Storage pressure or accidental production network; 30 min |
| R-02 | Restart one noncritical monitored container | Alert route armed; service data backed up | Kuma/ntfy detect failure, recovery clears alert | Data/error state; 10 min |
| R-03 | Monitoring VM outage | HA external sensors confirmed | HA aggregate turns off and sends independent notification | HA instability; 10 min |
| R-04 | AdGuard upstream loss | Router fallback expectations documented | DNS follows intended strict/fallback policy without bypass | Household DNS outage; 5 min |
| R-05 | MQTT broker interruption using test clients | No physical VentSys subscribers; retained topics captured | HA/clients become unavailable safely; no stale command replay | Any physical output; immediate |
| R-06 | Tailscale route withdrawal | Local admin path confirmed | Off-LAN host routes fail; local services remain available | Loss of sole admin path; 10 min |
| R-07 | WireGuard fallback drill | Governance checklist, client and local recovery | Only documented fallback targets work; prohibited VLANs fail | Unexpected broad access; immediate |
| R-08 | Representative VLAN ACL matrix | Test client in each VLAN | Every allow and deny pair matches access matrix | Unexpected management/write access; immediate |
| R-09 | Concurrent Frigate/legacy local LLM runtime GPU load | Temperature/resource telemetry visible | Both workloads remain stable within defined latency/thermal limits | GPU reset, OOM, camera loss; 15 min |
| R-10 | HA restart with test MQTT namespace | F-003 reconciled; no real actuators attached | Startup publishes only approved fail-safe commands | Any production-topic write; immediate |
| P-01 | Sensor disconnect/implausible values | Bench hardware, simulated load, fire-safe observer | Unavailable and invalid values cannot produce unsafe normal state | Any uncommanded power/fan/valve action |
| P-02 | Valve feedback mismatch/stall | Calibrated bench fixture | Command stops/alarms according to accepted timeout | Mechanical stress/current limit |
| P-03 | Controller and broker power loss/recovery | Safe physical isolation | Outputs return to documented fail-safe state; retained messages are safe | Unexpected energization |
| P-04 | Emergency cutoff/manual override | Non-fire test load and observer | Cutoff dominates automation; manual recovery is deliberate | Failure to de-energize immediately |
| P-05 | Fire-safe timing and airflow | All hardware commissioned; safe test medium | Accepted valve/fan sequence and airflow achieved within measured limit | Any unsafe flow path |

No physical card may run while F-003 or F-004 is open.

