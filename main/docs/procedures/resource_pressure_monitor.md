---
title: Resource Pressure Monitor
description: Always-on Proxmox and guest pressure alerts with ntfy delivery
tags: [proxmox, monitoring, memory, oom, ntfy]
created: 2026-10-10
modified: 2026-10-11
type: procedure
status: active
---

# Resource Pressure Monitor

## Live deployment

October12: at the owner's request, the hourly chat watchdog automation
`proxmox-resource-monitor-watchdog` is paused. The enabled Proxmox collector
and publisher timers and VM103 Troubleshooting API remain active independently.
The final check had fresh six-system coverage, no queued alerts/delivery errors,
and readable CA/event history. Phone subscription repair/receipt acceptance
remains open in the ntfy manual; pausing chat checks does not establish phone
delivery. Resume this automation explicitly if external chat supervision is wanted.

Proxmox runs `resource-pressure-monitor.timer` every minute independently of
VM102, Grafana, InfluxDB and the Windows workstation. It samples the host and
every running VM/CT, and expects production guests100/102/103/111/114 to stay up.
Stopped rollback VMs101/104 and restore VM9102 consume no CPU/RAM and do not
generate stopped-guest alerts. Any additional running guest is discovered;
unsupported/missing guest telemetry generates a coverage alert.

The Python collector is `/usr/local/sbin/resource-pressure-monitor.py`.
Source: [[../../scripts/monitoring/resource_pressure_monitor.py]]. Systemd units
live under [[../../configs/proxmox/]]. No automatic remediation is performed.

- Host: `/proc` memory, pressure, OOM/load/blocked tasks; root filesystem,
  LVM thin data/metadata capacity and recent kernel disk/hang warnings.
- CTs: cgroup-v2 memory/pressure/OOM counters plus Proxmox root-disk metrics.
  Reclaimable inactive file pages count toward estimated usable headroom.
  Shared memory counts as non-cache use, important for CT114's AI allocation.
- VM102/103: fixed read-only `/proc` and root-filesystem commands through QGA.
- VM100 HA: the same fixed command through a dedicated SSH key, restricted
  with `restrict,command=...`; no general shell or forwarding. The key is in
  the SSH add-on's Supervisor-managed authorized-key options as well as its
  live authorized_keys. Proxmox uses the pre-existing verified HA host key.
- Native Proxmox CPU fractions are checked for every running guest. VM RAM
  `mem/maxmem` remains cache-inclusive and is **not** the memory alert input.

## Resource Health viewer

Homepage Monitoring links to
`https://homepage.home.local/portal-preview/troubleshooting/#resource-health`.
This viewer shares the troubleshooting app on VM103; no additional guest is used.
Proxmox's independent `troubleshooting-publish.timer` exports sanitized latest
metrics and status every minute through source-restricted forced-command SSH to
VM103. The viewer uses a local Unix-socket API and marks samples older than five
minutes stale. Publication/API failure cannot stop this primary alert timer.
The viewer now retains up to30days /1,000 bounded event summaries on VM103:
monitor-state transitions, accepted-notification timestamps, viewer freshness
and requested diagnostics. It returns the newest100 and links to existing
Grafana resource/log dashboards around each event. History begins at deployment;
previous incidents are not reconstructed. History failure cannot reject fresh
metrics publication or stop primary alerts. No credentials or arbitrary Proxmox
shell access are exposed. Grafana and ntfy
links are navigation, not a new historical metrics pipeline. Source, runtime,
validation and selected rollback:
[[../../apps/troubleshooting-dashboard/README|Troubleshooting Dashboard manual]].

## Alert policy

Authenticated notifications go to the existing ntfy `monitoring` topic on
VM103, consumed by `mobile-monitoring`. The dedicated token has monitoring
user's existing write-only access to this topic. URL/token/config stay in
`/etc/resource-pressure-monitor.json` mode0600, never in Git or tool output.
The dedicated HA private key is `/etc/resource-pressure-monitor-key` mode0600;
trusted hosts are `/etc/resource-pressure-monitor-known-hosts`.

| Condition | Threshold |
|---|---|
| Usable memory | below10% **or** below256MiB |
| CT non-cache memory | anon + shared memory at least85% of limit |
| CT hard-limit risk | at least95% total usage and below10% usable headroom |
| Memory stalls | PSI some avg60 at least10% |
| Disk stalls | PSI some avg60 at least20% |
| Host blocked tasks | at least8 |
| Host load | at least2 × logical CPU count |
| Guest CPU | at least95% of assigned CPU capacity |
| Root filesystem | at least85% used |
| Thin data / metadata | at least80% / 70% allocated |
| Guest coverage | expected stopped/missing or sample unavailable |

Threshold alerts require three bad samples spanning at least120seconds.
Recovery needs three good samples. Active alerts repeat at most hourly.
New OOM-counter increments and new kernel disk/hang warnings notify on the
next sample; historical OOMs and boot counter resets do not count as new events.
Kernel matching covers blocked/hung tasks, I/O errors and NVMe timeout/reset.

Durable state and queued resource/event delivery live in
`/var/lib/resource-pressure-monitor/state.json`; latest evidence is `latest.json`.
Writes are atomic, notification timeouts are5seconds, and at most four pending
notifications are attempted per run. Failed delivery remains pending for retry.
The unit has a55second execution limit and cannot overlap itself. Expected
collection errors are retained in `collector-health.json`: three failed runs
spanning120seconds trigger failure notification; successful collection sends
recovery if the incident was notified. Unexpected service exits still invoke
`resource-pressure-monitor-failure.service` immediately. Its cooldown is
durable application state (at most one accepted failure notification per hour),
not systemd's start-rate limiter; the notifier no longer latches `start-limit-hit`.
Failed sends remain queued, including incidents that recover before delivery.
Successful sends are checkpointed individually to reduce duplicate retries.
Transport failure is recorded as delivery failure, not collector failure.
If ntfy or the host itself is unreachable, immediate push
delivery cannot succeed; queued resource messages retry when connectivity returns.

A Proxmox inventory timeout does not abort host/guest collection. Last-known
guest identities permit fresh cgroup/QGA/SSH reads, while inventory coverage
is explicitly degraded (`collector:inventory`). Cached guest CPU and CT disk
percentages are not evaluated as fresh; new guests cannot be discovered until
inventory recovers. The normal coverage debounce/recovery applies. Completely
failed collections leave `latest.json` untouched so freshness cannot look healthy.
OOM baselines survive temporary gaps in guest telemetry.

An hourly Codex heartbeat, **Proxmox resource monitor watchdog**, checks service
health, sample freshness (5minutes), lost coverage and pending delivery. It stays
quiet when healthy and does not duplicate resource notifications. This secondary
check requires Codex's local scheduler/workstation; the Proxmox timer does not.

## Verification and operations

2026-10-10: six systems sampled with zero missing coverage, four unit tests
passed, systemd unit validation passed, timer enabled and recurring runs passed.
ntfy accepted the labelled test. A deployment bug treating journalctl's empty
grep result as failure was fixed; its failure notification also proved the
OnFailure route. No new infrastructure incident caused that deployment alert.
Phone presentation has not been independently verified in this session.

October11 error-handling deployment: ten tests pass, including inventory timeout
with continued host coverage, full collection failure/stale sample preservation,
failure debounce/cooldown/recovery, offline notification then incident recovery,
resource-alert delivery after the condition clears, and OOM across missing
samples. Systemd validation and live six-system collection pass. The old failed
notifier state was cleared; its result is success. No guest was restarted.
The hourly watchdog now uses the supported read-only `--status` endpoint,
including collector health and pending delivery, instead of a temporary helper.

```sh
systemctl list-timers resource-pressure-monitor.timer
journalctl -u resource-pressure-monitor.service -n 30 --no-pager
cat /var/lib/resource-pressure-monitor/latest.json
python3 /usr/local/sbin/resource-pressure-monitor.py --status
python3 /usr/local/sbin/resource-pressure-monitor.py --test-notification
```

To update, upload the source, `install -m0755` into `/usr/local/sbin`, upload
the units into `/etc/systemd/system`, run `systemd-analyze verify`, reload and
start the service, then verify fresh six-system coverage before leaving it.
Do not recreate the token or key for an ordinary code update.

October11 rollback copies of the prior collector and notifier unit are under
`/var/lib/resource-pressure-monitor/errorhandling-20261011/` (host-only). To
roll back, stop only the monitor timer/service, restore those two files to
their original locations, reload systemd and restart the timer; preserve
state/config/token/key. The older code will reintroduce the rate-limit latch
and weaker retry behavior. Forward-added JSON fields are ignored by old code.

To disable: `systemctl disable --now resource-pressure-monitor.timer` and
pause the Codex watchdog. Retain state for diagnosis. To retire, revoke the
labelled `proxmox-resource-pressure` ntfy token and remove the restricted HA
authorized key from Supervisor options before deleting the private key.

## October10 resource audit

| Guest | Allocation after audit | Usable RAM / root used observed |
|---|---|---|
| VM100 HA | 2CPU / 6GiB / 32GiB disk | 4.47GiB / 58% |
| VM102 monitoring | 2CPU / **6GiB** / 32GiB disk | ~4.3GiB after shutdown/start / 37% |
| VM103 Docker | 4CPU / 10GiB / **128GiB** disk | ~4.9GiB / **44%**, down from88% |
| CT111 Frigate | 2CPU / **6GiB** after lifecycle repair / 32GiB root | several GiB cache/working margin / 22% |
| CT114 AI | 6CPU / 28GiB / 100GiB root | ~12.1GiB estimated / 42% |
| VM101 /104 /9102 | stopped, retained disks | zero CPU/RAM |

VM102's Grafana had a historical OOM kill on September17; increasing3→6GiB
required a graceful QEMU shutdown/start, not merely an in-guest OS reboot.
Grafana API/database, Influx health and healthy Kuma passed after startup.
VM103's disk grew64→128GiB online using `qm resize`, `growpart`, `resize2fs`;
the mounted ext4 filesystem reports126GiB total and69GiB available.

The host has62GiB usable RAM, ~25GiB available after changes, negligible current
memory pressure and no persistent blocked tasks. Root is81% with18GiB available;
64GiB is local backup files, not unexplained application growth. No backups were
deleted. Thin pool is~26.7% allocated with~1.1% metadata; virtual allocations are
overcommitted, so the physical-pool alert remains necessary. Host swap contains
old pages; swap occupancy alone is not evidence of active pressure.

Frigate's local owner-thread lifecycle repair now passes reconnect and synthetic
three-camera validation; CT111 was reassessed12→6GiB. Cameras remain
disconnected/disabled pending physical real-stream and sustained acceptance:
[[../install/phases/04-frigate]].
