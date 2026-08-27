---
title: Phase 10 - Backups Monitoring Maintenance
description: Backup contracts, isolated restore drills, alert proofs, maintenance windows, updates, and rollback
tags: [install, backup, monitoring, maintenance]
created: 2026-05-24
modified: 2026-08-09
type: install-guide
status: active
---

# Phase 10 - Backups Monitoring Maintenance

## Purpose

Make the rebuilt system recoverable and observable before treating it as
dependable. A successful backup job is only archive-creation evidence. Recovery
requires an isolated restore, application-level validation, and safe cleanup.

## Current-state callout

[current-live-state.md](../../reference/current-live-state.md) and the
[backup strategy](../../../scripts/backup/backup_strategy.md) record the deployed
state: Proxmox guest archives and HA native backups target OMV; docker-host has a
daily app-data job with SQLite-consistent handling for ntfy/Vaultwarden; VM 102,
multiple app datasets, and Vaultwarden have restore evidence; HA-side external
monitoring and Uptime Kuma/ntfy alert paths exist. This manual is still the
blank-to-operational path and does not claim a fresh rebuild passed.

## Runs on

- Proxmox host shell for VM/LXC archives and isolated guest restores;
- Home Assistant UI and Terminal & SSH app for HA backups;
- docker-host over SSH for application backup, service updates, and timers;
- CT 111/114 or their service UIs for Frigate/local-AI checks;
- OMV UI/shell for capacity, SMART, and export health;
- admin laptop for project-vault copy/restore and cross-host alert checks.

## Stop conditions

Stop a backup, restore, or update if:

- OMV backup paths are not mounted from the exact remote source;
- free space is below policy or Proxmox thin-pool warnings are unexplained;
- a restore target ID/path/name already exists;
- a restored clone still has its production NIC, address, hostname, MQTT,
  camera, automation, or external-integration identity;
- the only backup is being overwritten or restored over live data;
- a maintenance window lacks a named rollback checkpoint and observer;
- alerts are muted without a timed re-enable owner;
- a package/image update would cross multiple hosts or services at once.

Never use `qmrestore --force` or restore an LXC to its production ID as a drill.
Never clear a Proxmox lock until active backup/snapshot processes are disproven.

## Backup and drill contract

| Layer | Schedule / retention | Minimum proof | Drill cadence |
|---|---|---|---|
| Proxmox VMs 100/102/103 | daily 02:00; 7 daily + 6 monthly | fresh archive, `zstd -t`, isolated no-NIC boot/app check | one representative VM quarterly; every VM annually |
| Proxmox CTs 111/114 | daily 04:00; same retention; `tmpdir=/var/tmp` | archive, integrity, isolated no-NIC config/boot where safe | one CT quarterly; every CT annually |
| HA native `nas_backups` | daily 03:00; 14 copies/current policy | OMV file plus isolated disposable HAOS restore | quarterly and before major HA upgrade |
| docker-host app data | daily 03:45; 14 runs + `latest` | exact OMV mount, consistent artifacts, service-specific isolated restore | one rotating stateful service monthly; all annually |
| Frigate recordings/config | continuous retention + CT archive/config | fresh playable MP4, DB/config backup, isolated CT/config restore | monthly sample playback; quarterly recovery |
| OMV configuration reference | after material change | restricted config/package/disk inventory copied off-host | quarterly tabletop; OS reinstall drill when spare media exists |
| Project vault/configs | daily additive copy + Git checkpoints | temporary-folder restore and representative hashes/diff | monthly |

Record date, source backup ID/path, restore target, isolation method, checks,
cleanup, operator, and result. Failed drills remain open work; do not relabel
them as “tabletop complete.”

## 1. Verify clocks, targets, schedules, and capacity

Run on: Proxmox host shell.

```bash
date -Is
pvesm status | awk 'NR == 1 || $1 == "omv-backups"'
df -hT /mnt/pve/omv-backups
pvesh get /cluster/backup --output-format yaml
lvs -a -o lv_name,vg_name,lv_size,data_percent,metadata_percent
systemctl list-timers home-automation-health-check.timer
```

Expected result: clock is correct, `omv-backups` is active with policy headroom,
jobs show VM and CT schedules/retention plus LXC `tmpdir=/var/tmp`, thin-pool
usage is accepted, and the health timer is scheduled.

Run on: docker-host over SSH.

```bash
date -Is
findmnt -T /mnt/omv/docker-host-backups
df -hT /mnt/omv/docker-host-backups
systemctl list-timers docker-host-app-data-backup.timer
systemctl --failed
```

Expected result: exact OMV NFS source is mounted, capacity is safe, next backup
time is visible, and no unexplained failed service exists.

Run on: Home Assistant Terminal & SSH app.

```bash
ha mounts info
ha backups list
ha core info
```

Expected result: `nas_backups` is active/writable/default as intended, recent
backups list without error, and HA is healthy. Confirm the corresponding latest
backup is non-zero on OMV; catalog presence alone is insufficient.

## 2. Prove current Proxmox archives without restoring

Run on: Proxmox host shell.

```bash
pvesm list omv-backups --content backup
for guest in 100 102 103 111 114; do
  latest="$(find /mnt/pve/omv-backups/dump -maxdepth 1 -type f \
    \( -name "vzdump-qemu-${guest}-*.vma.zst" -o -name "vzdump-lxc-${guest}-*.tar.zst" \) \
    -printf '%T@ %p\n' | sort -nr | head -n1 | cut -d' ' -f2-)"
  test -n "$latest" && test -s "$latest"
  printf '%s %s\n' "$guest" "$latest"
  zstd -t "$latest"
done
```

Expected result: every guest prints one non-zero latest archive and each
`zstd -t` reports success. This proves compression integrity, not guest boot or
application integrity.

If a CT backup failed, run the guard read-only first.

Run on: Proxmox host shell from the repository checkout.

```bash
sh main/scripts/backup/proxmox-lxc-backup-guard.sh
```

Expected result: the guard reports active processes, lock values, and snapshot
markers without changing them. Use `--apply` only for the exact affected CT
after the output proves no `vzdump`, snapshot, restore, or delete task is active.
Then create a fresh manual CT backup and repeat integrity checks.

## 3. Isolated Proxmox VM restore drill

Select an unused high temporary ID. The example prompts and refuses an existing
ID; it restores stopped, removes all restored NIC entries before boot, and does
not replace production.

Run on: Proxmox host shell during the approved restore window.

```bash
read -r -p 'Unused temporary VM ID (for example 9102): ' restore_vmid
[[ "$restore_vmid" =~ ^[0-9]+$ ]]
! qm status "$restore_vmid" >/dev/null 2>&1
archive="$(find /mnt/pve/omv-backups/dump -maxdepth 1 -type f \
  -name 'vzdump-qemu-102-*.vma.zst' -printf '%T@ %p\n' \
  | sort -nr | head -n1 | cut -d' ' -f2-)"
test -n "$archive" && test -s "$archive"
qmrestore "$archive" "$restore_vmid" --storage local-lvm
while qm config "$restore_vmid" | grep -q '^net[0-9]:'; do
  nic="$(qm config "$restore_vmid" | awk -F: '/^net[0-9]+:/{print $1; exit}')"
  qm set "$restore_vmid" --delete "$nic"
done
qm config "$restore_vmid"
```

Expected result: restore succeeds to the new ID and final config has no `netN`
entry. Review disks, boot order, cloud-init, mounts, and USB/device passthrough.
Do not boot if any production-connected device/path remains.

Boot only after the no-NIC review. Use console/QEMU Guest Agent to prove OS and
application data without attaching a production network. Shut down after checks.

Run on: Proxmox host shell after the isolated checks.

```bash
qm shutdown "$restore_vmid" --timeout 120 || qm stop "$restore_vmid"
qm status "$restore_vmid"
```

Expected result: temporary VM is `stopped`. Record proof. Destroy it only after
re-reading its config and confirming the exact temporary ID with the operator;
cleanup is deliberately not automated here.

## 4. Isolated Proxmox LXC restore drill

Use a new temporary CT ID and remove `net0` before any start. Do not copy CT 111
GPU/NFS bind mounts or CT 114 GPU/model mounts into the drill unless an isolated
equivalent is explicitly prepared.

Run on: Proxmox host shell during the approved restore window.

```bash
read -r -p 'Unused temporary CT ID (for example 9114): ' restore_ctid
[[ "$restore_ctid" =~ ^[0-9]+$ ]]
! pct status "$restore_ctid" >/dev/null 2>&1
archive="$(find /mnt/pve/omv-backups/dump -maxdepth 1 -type f \
  -name 'vzdump-lxc-114-*.tar.zst' -printf '%T@ %p\n' \
  | sort -nr | head -n1 | cut -d' ' -f2-)"
test -n "$archive" && test -s "$archive"
pct restore "$restore_ctid" "$archive" --storage local-lvm
pct set "$restore_ctid" --delete net0 2>/dev/null || true
pct config "$restore_ctid"
```

Expected result: new CT is stopped, has no network, and has no production
device/bind mount that was not explicitly reviewed. Console-start only when
isolation is proven; validate files/database/config, then stop and manually
clean up the confirmed temporary ID.

## 5. Isolated Home Assistant restore drill

1. Create a disposable HAOS VM with a unique ID and no NIC, or an isolated test
   bridge with no path to MQTT, IoT, cameras, notification services, or devices.
2. Upload/select a specific `nas_backups` archive through the HA recovery flow.
3. Restore and boot isolated.
4. Confirm configuration loads, dashboards/entities exist, add-ons are present,
   and recorder/config checks pass without sending automations.
5. Record backup slug/date and stop the disposable VM.
6. Manually remove it only after confirming its temporary ID.

If the restore requires network temporarily, use an isolated NAT/update segment
with no routes to production. Never allow a cloned HA instance to share the
production address, MQTT client identity, or automation outputs.

## 6. Rotate docker-host application restore drills

Run a fresh consistent backup first.

Run on: docker-host over SSH.

```bash
findmnt -T /mnt/omv/docker-host-backups
systemctl start docker-host-app-data-backup.service
systemctl --no-pager --full status docker-host-app-data-backup.service
latest_target="$(readlink -f /mnt/omv/docker-host-backups/latest)"
test -d "$latest_target"
find "$latest_target" -maxdepth 3 -type f -printf '%s %p\n' | sort | tail -n 80
```

Expected result: backup succeeds to OMV, `latest` resolves inside the mounted
backup tree, and expected non-zero artifacts are visible. If `latest` is a real
directory rather than a symlink in the installed script, record that layout and
validate the directory instead of forcing a symlink.

Restore one stateful service per month using its manual. Minimum app-level proof:

| Service type | Isolated proof |
|---|---|
| SQLite (Mealie/Grocy/ntfy/Vaultwarden) | `PRAGMA integrity_check` returns `ok`, disposable app starts, representative record/account count matches |
| PostgreSQL/GardenKeeper | dump decompresses/imports into disposable DB and a representative query succeeds |
| CouchDB/LiveSync | restored shards/native replication open in isolated CouchDB; database/doc count is plausible |
| Media app config | disposable app opens restored config/database without writing to media library |
| qBittorrent config | syntax/settings load in a network-disabled disposable container; no torrent starts |

Use distinct container names, loopback test ports, isolated networks, and copied
data. Never mount a disposable test over production paths or expose it through
existing Tailscale/Homepage routes.

## 7. Restore the project vault to a temporary folder

The tracked helper defaults to an additive dry run; do not substitute `/MIR`.

Run on: Admin laptop from the repository checkout.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File `
  .\main\scripts\backup\backup_vault_to_nas.ps1
```

Expected result: dry-run log identifies the intended local source and NAS
destination without writing. Use `-Execute` only after reviewing both paths.

For restore proof, copy one selected NAS backup to a newly created local
temporary directory, never the active vault. Compare representative files and
hashes, open the restored Markdown read-only, then remove the temporary copy
only after proof is recorded.

## 8. Prove monitoring and notification paths

Run on: docker-host over SSH.

```bash
docker ps --filter health=unhealthy --format '{{.Names}}'
systemctl --failed
systemctl list-timers docker-host-app-data-backup.timer
curl -fsS -o /dev/null http://127.0.0.1:3001/
curl -fsS -o /dev/null http://127.0.0.1:8085/v1/health
```

Expected result: no unhealthy names or unexplained failed units print, timers
are scheduled, Uptime Kuma responds, and ntfy health returns success.

Run on: Home Assistant Terminal & SSH app.

```bash
ha core check
ha core logs --lines 100 | grep -Ei 'monitoring_external_health|error|failed' || true
```

Expected result: HA config check succeeds and no unresolved external-health
package error appears. Verify the external-health entities update even when the
monitored docker-host service is unavailable; otherwise monitoring depends on
the thing it is meant to observe.

Perform a bounded alert test quarterly: choose a non-critical canary monitor,
record its container/service state, stop it briefly, confirm Kuma detects Down
and ntfy receives the named notification, restart it, then confirm Up/recovery.
Do not use HA, MQTT, DNS, storage, camera recording, or a safety service as the
canary.

## 9. Maintenance windows and update policy

| Frequency | Work |
|---|---|
| Daily automated | Proxmox/HA/docker-host backups, health/SMART timers, alerts |
| Weekly review | Failed jobs, capacity trend, certificate/update notices, unresolved alerts |
| Monthly attended | OS/container review, one app restore rotation, LXC guard audit, SMART/thin-pool review |
| Quarterly | VM or CT restore, HA restore, alert outage proof, access/firewall review |
| Annual | Every workload restored, hardware/NAS recovery tabletop or spare-media drill |

Use [update_maintenance_playbook.md](../../procedures/update_maintenance_playbook.md)
and [docker_host_patch_window_runbook.md](../../procedures/docker_host_patch_window_runbook.md).
Automatic application/container updates remain disabled.

Pre-window record:

- scope and one owner/observer;
- start/end time and household impact;
- current versions/digests/config diff;
- fresh matching backup plus known restore proof;
- exact health checks and rollback trigger;
- only one host/service change at a time.

Run on: docker-host over SSH before an approved single-stack update.

```bash
date -Is
findmnt -T /mnt/omv/docker-host-backups
systemctl start docker-host-app-data-backup.service
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'
read -r -p 'Approved single stack name: ' service
[[ "$service" =~ ^[a-z0-9][a-z0-9-]*$ ]]
test -f "/opt/stacks/${service}/docker-compose.yml"
docker compose -f "/opt/stacks/${service}/docker-compose.yml" config --quiet
```

Expected result: backup succeeds, current images/states are recorded, and the
approved stack's Compose file validates. Pull only
the reviewed version/digest, recreate that stack, then test authentication,
data, dependencies, monitoring, and logs before proceeding.

Rollback uses the recorded prior Compose/env/image digest and compatible data
checkpoint. If rollback fails, keep the affected service stopped and preserve
both pre/post data for recovery; do not update another service to “match.”

## End-of-phase validation

Run on: Proxmox host shell.

```bash
pvesm status | awk 'NR == 1 || $1 == "omv-backups"'
pvesh get /cluster/backup --output-format yaml
systemctl --failed
```

Expected result: `omv-backups` is active, configured backup jobs print with the
intended schedule/storage, and no unexplained Proxmox unit is failed.

Run on: docker-host over SSH.

```bash
findmnt -T /mnt/omv/docker-host-backups
systemctl list-timers docker-host-app-data-backup.timer
docker ps --filter health=unhealthy --format '{{.Names}}'
systemctl --failed
```

Expected result: the backup target is remote, the timer has a next/last run,
the unhealthy-container query is empty, and no unexplained host unit is failed.

Run on: Admin laptop.

```powershell
Test-Connection 192.168.10.10 -Count 2
Test-Connection 192.168.20.101 -Count 2
Test-Connection 192.168.20.102 -Count 2
Test-Connection 192.168.20.104 -Count 2
Test-Connection 192.168.40.50 -Count 2
```

Expected result: storage/jobs/timers are healthy, unhealthy/failed queries are
empty or explained, and all intended hosts answer. Reachability is not service
health; the restore and alert evidence above remains required.

## Failure recovery matrix

| Failure | Safe response | Proof before continuing |
|---|---|---|
| Archive missing/corrupt | Preserve logs; create fresh backup after fixing storage/capacity. | New archive passes integrity and isolated restore. |
| Restore ID/path collision | Abort; select a verified unused temporary target. | Production config/data untouched. |
| Clone has production identity | Keep powered off; remove NIC/routes/integrations. | Isolation reviewed before boot. |
| CT remains backup-locked | Run guard read-only; inspect active tasks. | No active task; targeted cleanup then fresh backup succeeds. |
| App backup wrote locally | Stop job/services; restore NFS and create fresh off-host backup. | Exact remote source plus isolated restore. |
| Alert did not fire/recover | Restore canary; inspect Kuma/ntfy routing and credentials. | Both Down and Up messages arrive. |
| Update health check fails | Stop rollout; restore prior digest/config/data checkpoint. | Previous version and monitoring return. |
| Monitoring self-dependency | Preserve HA-side/external check and document gap. | Observer detects target outage independently. |

## Completion checklist

- [ ] Backup schedules, retention, mounts, capacity, clocks, and timers pass.
- [ ] Every current guest archive is non-zero and compression-valid.
- [ ] Quarterly VM/CT and HA isolated restore records exist.
- [ ] Monthly rotating docker-host service restore passes application-level checks.
- [ ] Project vault restores to a temporary folder without overwriting active work.
- [ ] LXC guard read-only workflow is understood; no blind unlock is used.
- [ ] Monitoring is externally observable and bounded Down/Up notification test passes.
- [ ] Maintenance calendar, one-service update policy, and rollback triggers are recorded.
- [ ] Automatic updates remain disabled and failed drills remain explicit.

Continue to [Phase 11 - Physical Integrations](11-physical-integrations.md) only
after recovery evidence and maintenance ownership are accepted.
