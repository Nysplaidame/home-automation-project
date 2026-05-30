---
title: Weekly Update Review Log
description: Execution log for weekly update-candidate review and post-check outcomes
tags: [operations, updates, maintenance, watchtower, docker-host]
created: 2026-05-28
modified: 2026-05-28
type: procedure
status: active
---

# Weekly Update Review Log

Use this log for recurring update-candidate review runs.

Current planning baseline:

- Treat OMV as unbuilt.
- Treat Frigate as unbuilt.
- Treat VentSys entities as unbuilt.

Do not log tasks here that assume those systems are live unless baseline is
explicitly updated first.

## Entry template

```text
Date:
Operator:
Scope:
Maintenance window:

Host package candidates:
- ...

Container image candidates (Watchtower monitor-only):
- ...

Security-relevant items:
- ...

Actions taken:
- ...

Actions deferred:
- ...

Post-check:
- health_check result:
- key endpoint checks:

Follow-up window:
- ...
```

## 2026-05-28 — Initial weekly review baseline

Date:

- 2026-05-28

Operator:

- Codex session

Scope:

- docker-host only (`192.168.20.102`)

Maintenance window:

- review-only window; no package/container updates applied

Host package candidates:

- `containerd.io` upgradable (`2.2.3` -> `2.2.4`)
- `docker-buildx-plugin` upgradable (`0.33.0` -> `0.34.1`)
- `docker-ce-cli` upgradable (`29.4.3` -> `29.5.2`)
- `docker-ce-rootless-extras` upgradable (`29.4.3` -> `29.5.2`)
- `docker-ce` upgradable (`29.4.3` -> `29.5.2`)
- `docker-compose-plugin` upgradable (`5.1.3` -> `5.1.4`)
- `linux-image-cloud-amd64` upgradable (`6.12.90-1` -> `6.12.90-2`)

Container image candidates (Watchtower monitor-only):

- watchtower reported `Found new ghcr.io/maziggy/bambuddy:latest image`
- session summary: `Failed=0 Scanned=11 Updated=1 notify=no`

Security-relevant items:

- Docker engine/component upgrades available; schedule controlled patch window
- kernel metapackage upgrade available; requires reboot planning

Actions taken:

- collected `apt list --upgradable` snapshot
- reviewed watchtower logs and container health status

Actions deferred:

- all package upgrades deferred to planned patch window
- all container image refresh deferred to planned patch window

Post-check:

- health_check result: not run from this Windows session (shell compatibility)
- key endpoint checks: docker-host containers currently `Up`; watchtower `healthy`

Follow-up window:

- next scheduled patch window should include docker-host package upgrades and
  explicit restart/reboot validation plan

## 2026-05-29 — Docker-host metrics preflight and patch-window planning

Date:

- 2026-05-29

Operator:

- Codex session

Scope:

- docker-host metrics deployment
- monitoring VM Grafana/Influx integration
- router source/live drift check for docker-host-to-InfluxDB access

Maintenance window:

- metrics-only preflight; no host package upgrades or application image updates applied

Host package candidates:

- carry forward 2026-05-28 docker-host package candidates
- schedule a controlled docker-host patch window for Docker engine/component updates and kernel metapackage update

Container image candidates:

- no routine application image updates applied
- Telegraf image was transferred from monitoring VM via `docker save/load`, avoiding a new broad registry egress window

Security-relevant items:

- added narrow router allowance from docker-host `192.168.20.102` to monitoring VM `192.168.60.10:8086`
- created scoped InfluxDB bucket/token path for docker-host metrics
- kept Watchtower monitor-only posture unchanged

Actions taken:

- deployed docker-host Telegraf collector under `/opt/stacks/telegraf`
- created InfluxDB bucket `dockerhost`
- created Grafana datasource `InfluxDB - Docker Host`
- added Docker-host/container panels to `Proxmox Resource Overview`
- fixed `health_check.sh` Proxmox storage column parsing

Actions deferred:

- docker-host package upgrades deferred to planned patch window
- routine container updates deferred to planned patch window
- registry mirror remains parked until recurring image-pull friction justifies it

Post-check:

- router connectivity validation: `PASS=85 WARN=0 FAIL=0`
- `health_check.sh`: `11/11` checks passed after storage parsing fix
- docker-host `fail2ban` sshd jail: `0` failed, `0` banned
- docker-host Telegraf: running and writing `dockerhost` measurements

Follow-up window:

- perform docker-host package patching with explicit pre-check, snapshot/rollback
  note, package upgrade, reboot if kernel changes, and post-check validation
