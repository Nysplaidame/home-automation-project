---
title: Phase 09 - Tier 3 Evaluate Apps
description: Security-gated rebuild and evaluation for Vaultwarden, Portainer, Watchtower, registry mirror, and Node-RED
tags: [install, docker-host, tier3, evaluate]
created: 2026-05-24
modified: 2026-08-09
type: install-guide
status: active
---

# Phase 09 - Tier 3 Evaluate Apps

## Purpose

Rebuild already approved Tier 3 services while keeping powerful candidates
stopped and absent until their security, backup, restore, exposure, and rollback
gates pass. A directory or Compose file is not deployment approval.

## Current-state callout

[current-live-state.md](../../reference/current-live-state.md) records
Vaultwarden as live but owner-onboarding gated, and Watchtower as live in strict
monitor-only mode. Portainer, the local registry mirror, and Node-RED remain
parked candidates. This manual does not change those decisions.

## Runs on

- repository/admin laptop for tracked configuration transfer;
- docker-host over SSH at `192.168.20.102` for Compose/runtime validation;
- trusted management/Tailscale browser only for explicitly approved admin UIs.

## Non-negotiable invariants

- Vaultwarden imports no primary credentials until HTTPS, owner 2FA, recovery
  codes, emergency access, and isolated restore remain proven.
- Watchtower must retain `WATCHTOWER_MONITOR_ONLY=true`; no update engine may
  recreate containers automatically.
- Portainer's Docker socket is root-equivalent; the candidate remains absent
  unless that blast radius is explicitly accepted.
- A registry mirror may cache only Docker Hub public pulls unless a new
  authenticated-private-content gate is approved; no insecure client registry.
- Node-RED starts in safe mode with editor authentication and no production HA
  token, MQTT command, or safety-critical flow during evaluation.
- Do not bulk-create candidate directories or run `docker system prune`.

## 1. Capture the admin-surface baseline

Run on: docker-host over SSH.

```bash
date -Is
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'
ss -lntp
find /var/run/docker.sock -maxdepth 0 -printf '%M %u:%g %p\n'
findmnt -T /mnt/omv/docker-host-backups
systemctl is-active docker-host-app-data-backup.timer
tailscale serve status
```

Expected result: existing listeners/Serve handlers are recorded, Docker socket
ownership is explicit, the backup path is the OMV NFS mount, and the timer is
active. Stop if backup storage is local fallback or an intended candidate port
already has an unknown owner.

## 2. Rebuild only the approved live services

Follow, one at a time:

1. [Vaultwarden](../services/vaultwarden.md) — preserve live `.env` and data,
   loopback raw listener, fixed HTTPS proxy, backup, restore, and onboarding gate.
2. [Watchtower monitor-only](../services/watchtower-monitor-only.md) — verify the
   monitor flag in rendered config and runtime before starting it.

Run on: docker-host over SSH after both approved stacks are reconciled.

```bash
for stack in vaultwarden watchtower; do
  printf '\n== %s ==\n' "$stack"
  docker compose -f "/opt/stacks/${stack}/docker-compose.yml" config --quiet
  docker compose -f "/opt/stacks/${stack}/docker-compose.yml" ps
done

docker inspect watchtower --format '{{range .Config.Env}}{{println .}}{{end}}' \
  | grep -Fx 'WATCHTOWER_MONITOR_ONLY=true'
ss -lntp | grep '127.0.0.1:8222'
```

Expected result: both Compose files validate; live containers are healthy/up;
runtime Watchtower prints exactly the monitor-only flag; Vaultwarden raw HTTP
is bound to loopback. Any missing monitor flag is a stop condition.

## 3. Confirm candidates remain parked

Run on: docker-host over SSH.

```bash
for candidate in portainer registry-mirror node-red; do
  if test -e "/opt/stacks/${candidate}"; then
    printf '%s: path exists; reconcile approval and runtime state\n' "$candidate"
  else
    printf '%s: parked/absent\n' "$candidate"
  fi
done

docker ps --format '{{.Names}}' | grep -E '^(portainer|registry-mirror|node-red)$' && exit 1 || true
```

Expected result: each candidate is `parked/absent` and no matching container is
running. An existing path must be inspected and preserved if it contains user
data; do not delete it as part of this check.

## 4. Portainer evaluation gate

Use [portainer.md](../services/portainer.md) only if the operator accepts that a
web-session compromise becomes Docker-host root control. Require loopback-only
Portainer HTTPS behind approved Tailscale access, no optional Edge tunnel,
immutable image digest, named admin, encrypted configuration backup, a fresh
no-socket restore test, and immediate shutdown/route removal on rejection.

## 5. Registry mirror evaluation gate

Use [local-registry-mirror.md](../services/local-registry-mirror.md) only after
measuring repeated Docker Hub pull cost. Require a quota/capacity alert, cache
TTL/deletion, HTTPS with trusted CA, source scope, no upstream private account,
client `daemon.json` backup/validation, one-client canary, and client rollback.
Cache data is disposable; configuration and client rollback evidence are not.

## 6. Node-RED evaluation gate

Use [node-red.md](../services/node-red.md) only for a concrete workflow that HA
cannot express safely. Require loopback-only editor behind HTTPS, `adminAuth`, a
stored credential secret, safe-mode first boot, no production credentials,
flow/credential backup together, isolated safe-mode restore, and a rule that
fire/smoke/ventilation interlocks remain in HA/firmware.

## 7. Prove live-service backup and recovery state

Run on: docker-host over SSH.

```bash
findmnt -T /mnt/omv/docker-host-backups
systemctl start docker-host-app-data-backup.service
systemctl --no-pager --full status docker-host-app-data-backup.service
journalctl -u docker-host-app-data-backup.service -n 100 --no-pager
```

Expected result: the destination is OMV, the job succeeds, and its log identifies
Vaultwarden's SQLite-consistent staging and Watchtower configuration coverage
without printing secrets. Retain the documented two isolated Vaultwarden
restore proofs; configuration-only Watchtower recovery must reproduce
monitor-only behavior before notification checks.

## End-of-phase validation

Run on: docker-host over SSH.

```bash
docker ps --filter health=unhealthy --format '{{.Names}}'
docker inspect watchtower --format '{{range .Config.Env}}{{println .}}{{end}}' \
  | grep -Fx 'WATCHTOWER_MONITOR_ONLY=true'
docker inspect vaultwarden --format '{{json .HostConfig.PortBindings}}'
docker ps --format '{{.Names}}' | grep -E '^(portainer|registry-mirror|node-red)$' && exit 1 || true
findmnt -T /mnt/omv/docker-host-backups
```

Expected result: no unhealthy container names print, Watchtower remains
monitor-only, Vaultwarden's raw binding is loopback-only, parked candidates do
not run, and backups target OMV.

## Failure recovery matrix

| Failure | Safe response | Proof before continuing |
|---|---|---|
| Watchtower lacks monitor-only flag | Stop Watchtower immediately; repair Compose/env. | Rendered config and runtime env both show `true`; no container was recreated. |
| Vaultwarden HTTPS/restore gate fails | Stop onboarding/imports; preserve data and proxy state. | HTTPS, SQLite integrity and isolated login restore pass. |
| Candidate starts without approval | Stop with `docker compose down` but keep data; remove temporary route. | Container absent and previous services healthy. |
| Docker socket admin UI exposed broadly | Stop Portainer and remove Serve/firewall rule. | No listener/route remains; Docker workloads unchanged. |
| Mirror breaks pulls | Restore client `daemon.json`, validate, restart Docker in window. | Direct upstream pull succeeds and workloads return. |
| Node-RED flow triggers unexpectedly | Stop Node-RED; keep HA/firmware authoritative. | HA automations and safety paths pass independently. |
| Backup mount is local fallback | Stop backup/service writes; restore NFS first. | Exact OMV source and fresh off-host artifact proven. |

## Completion checklist

- [ ] Vaultwarden rebuild retains HTTPS, loopback, backup/restore, and onboarding gates.
- [ ] Watchtower rendered/runtime state is monitor-only and notification-only.
- [ ] Portainer, registry mirror, and Node-RED are absent/stopped unless each
  individual gate and recovery drill is approved.
- [ ] No candidate introduced public exposure, an insecure registry, automatic
  updates, or safety-critical duplicate automation.
- [ ] OMV backup target and live-service recovery evidence pass.

Continue to [Phase 10 - Backups, Monitoring, and Maintenance](10-backups-monitoring-maintenance.md)
only after the parked/live distinction is recorded.
