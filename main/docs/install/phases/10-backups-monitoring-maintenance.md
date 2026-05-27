---
title: Phase 10 - Backups Monitoring Maintenance
description: Backup layers, monitoring checks, update workflow, and restore drills
tags: [install, backup, monitoring, maintenance]
created: 2026-05-24
modified: 2026-05-24
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

- Proxmox has local and NAS-backed backup plan.
- HA has a backup schedule.
- docker-host stack data paths are known.
- OMV storage health is visible.
- Monitoring has an external failure signal or a documented gap.
- HA-side external monitoring health package is deployed at
  `/config/packages/monitoring_external_health_package.yaml`, with source in
  `configs/home-assistant/monitoring_external_health_package.yaml`.

## Current pre-NAS backup readiness

As of 2026-05-27, Proxmox has an enabled daily `02:00` snapshot job for VMs
`100,101,102,103` to local storage with `keep-last=2`. The latest backup logs
for all four VMs finished successfully on 2026-05-27. This is still a local
pre-NAS safety net, not long-term disaster recovery.

## Validation

Run on: Admin laptop.

```powershell
Test-Connection 192.168.10.10 -Count 2
Test-Connection 192.168.20.101 -Count 2
Test-Connection 192.168.20.102 -Count 2
Test-Connection 192.168.40.50 -Count 2
```

## Failure recovery

- If a backup restore is untested, do not call the service live.
- If monitoring depends only on itself, record the visibility gap in `TO-DO.md`
  and stage or deploy the HA-side external health package.
- If updates fail, roll back one service stack at a time; do not mass-update.

## Completion checklist

- [ ] Backup strategy read.
- [ ] Restore drill scheduled.
- [x] Monitoring health checks documented.
- [ ] Update maintenance playbook read.
