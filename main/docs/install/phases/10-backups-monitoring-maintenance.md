---
title: Phase 10 - Backups Monitoring Maintenance
description: Backup layers, monitoring checks, update workflow, and restore drills
tags: [install, backup, monitoring, maintenance]
created: 2026-05-24
modified: 2026-07-06
type: install-guide
status: active
---

# Phase 10 - Backups Monitoring Maintenance

## Purpose

Make the rebuilt system recoverable and maintainable before relying on it.

## Runs on

- Proxmox host shell.
- Home Assistant UI.
- docker-host over SSH.
- llm-host over SSH if Phase 05A is deployed.
- OMV web UI.
- Admin laptop.

## Prerequisites

- Core hosts installed.
- OMV or temporary backup target available.
- Service matrix updated with backup notes.

## Inputs

Secrets are service-specific; see the placeholder ledger.

## Commands

Run on: docker-host over SSH.

```sh
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
du -sh /opt/stacks/* 2>/dev/null || true
```

Run on: Proxmox host shell.

```sh
vzdump --help >/dev/null && echo VZDUMP_AVAILABLE
qm list
```

## Explanation

Backups and monitoring are not optional finishing touches. They define whether
the system can be safely maintained after installation.

## Expected result

- Proxmox uses OMV-backed `omv-backups` NFS storage for VM and LXC backups.
- HA has an OMV-backed `nas_backups` schedule.
- docker-host stack data paths are known, and app-data backup templates exist
  for Mealie, Grocy, Obsidian LiveSync, and GardenKeeper dumps.
- OMV storage health is visible.
- Monitoring has an external failure signal or a documented gap.
- CT 114 AI services have uptime checks and the local
  AI performance test procedure has a recorded pass.
- HA-side external monitoring health package is deployed at
  `/config/packages/monitoring_external_health_package.yaml`, with source in
  `configs/home-assistant/monitoring_external_health_package.yaml`.
- Failed CT backup cleanup is handled by an audit-first Proxmox guard instead
  of blind `pct unlock` commands.

## Current backup readiness

As of 2026-07-06:

- Proxmox storage `omv-backups` is active over NFSv3 to OMV md0
  `backups/proxmox`.
- Scheduled Proxmox jobs cover VMs `100`, `102`, and `103` at `02:00`, and
  CTs `111` and `114` at `04:00`, with `keep-daily=7` and
  `keep-monthly=6`.
- The CT 111/114 job uses `tmpdir=/var/tmp` so unprivileged LXC temporary files
  stay on Proxmox local storage instead of the NFS dump directory.
- Manual CT 111 and CT 114 backup proofs passed on 2026-07-05/06 after the
  `tmpdir` fix.
- `scripts/backup/proxmox-lxc-backup-guard.sh` exists as the recovery guard for
  stale CT backup locks and leftover `vzdump` snapshot markers.
- HA automatic backups target `nas_backups` daily at `03:00`.
- docker-host app-data backup templates exist under `configs/docker-host/system/`
  for Mealie, Grocy, Obsidian LiveSync, and GardenKeeper dump copies. The live
  `backups/docker-host` NFS mount, first backup run, restore smoke, and daily
  `03:45` systemd timer were proven on 2026-07-07.

## Validation

Run on: Admin laptop.

```powershell
Test-Connection 192.168.10.10 -Count 2
Test-Connection 192.168.20.101 -Count 2
Test-Connection 192.168.20.102 -Count 2
Test-Connection 192.168.20.104 -Count 2
Test-Connection 192.168.40.50 -Count 2
```

## Failure recovery

- If a backup restore is untested, do not call the service live.
- If a CT backup fails and Proxmox reports `CT is locked`, run the LXC backup
  guard in read-only mode first. Clear locks only after proving no real
  backup/snapshot process is active.
- If monitoring depends only on itself, record the visibility gap in `TO-DO.md`
  and stage or deploy the HA-side external health package.
- If updates fail, roll back one service stack at a time; do not mass-update.

## Completion checklist

- [ ] Backup strategy read.
- [ ] Restore drill scheduled.
- [ ] Proxmox LXC backup guard reviewed after any failed CT backup.
- [x] Monitoring health checks documented.
- [x] CT 114 local AI checks documented; OpenWakeWord monitor added 2026-06-20.
- [ ] Update maintenance playbook read.
- [x] docker-host app-data backup mount/timer installed and restore-smoked.
