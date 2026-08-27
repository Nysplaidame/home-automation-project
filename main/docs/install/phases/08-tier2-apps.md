---
title: Phase 08 - Tier 2 Apps
description: Decision-gated installation, recovery, and household rollout for Tier 2 services
tags: [install, docker-host, tier2]
created: 2026-05-24
modified: 2026-08-09
type: install-guide
status: active
---

# Phase 08 - Tier 2 Apps

## Purpose

Rebuild useful household services one at a time without turning a candidate into
a trusted or Internet-exposed service by accident. A container being `Up` is
only installation evidence; each service must also pass authentication,
exposure, backup, isolated restore, monitoring, and rollback gates before real
household data or client dependency is added.

## Current-state callout

[current-live-state.md](../../reference/current-live-state.md) is authoritative
for deployment state. Mealie, Grocy, ntfy, SearXNG, Whoogle, GardenKeeper, and
Gridfinity Layout Tool are live. The Obsidian LiveSync backend is live but its
client rollout is parked. Paperless-ngx, Actual Budget, and Scrypted remain
evaluation candidates and must not be deployed merely because this rebuild
manual contains commands.

This phase remains the blank-to-live path. Current-state evidence never replaces
the service's fresh validation and recovery proof.

## Runs on

- docker-host over SSH at `192.168.20.102` for Compose and local HTTP checks;
- a trusted HomeAdmin/Tailscale browser for first-run identities and user flows;
- OMV/destination storage only through the Phase 06 approved backup path;
- Proxmox host shell only if the Scrypted placement gate selects a dedicated
  Proxmox workload.

## Prerequisites

- Phase 05 docker-host and Phase 06 OMV storage are validated.
- Tier 1 monitoring/logging is available.
- `/opt/stacks/` permissions and the Docker maintenance-window procedure are in
  place.
- Required values exist in the password manager; no secret is pasted into Git,
  shell history, screenshots, or Compose files tracked by this repository.
- [decision-gates.md](../reference/decision-gates.md) and
  [version-policy.md](../reference/version-policy.md) have been reviewed.

## Mandatory per-service deployment record

Before running a candidate's deploy command, record:

| Decision | Required answer |
|---|---|
| Owner/use case | Who needs it and what existing service does not meet the need? |
| Placement | docker-host, dedicated Proxmox guest, or remain parked |
| Version | Exact image digest/tag or upstream installer revision reviewed that day |
| Authentication | Bootstrap removal, named admin, 2FA/E2EE if supported |
| Exposure | Exact source CIDRs/Tailscale identity and HTTPS endpoint; never “LAN-wide by default” |
| Data | Persistent paths, sensitivity, retention, and import source |
| Backup | Consistent capture method, OMV destination, encryption if required |
| Restore | Disposable target, success condition, and cleanup |
| Monitoring | Health check that does not leak credentials or private data |
| Rollback | Previous image/config/data checkpoint and maximum acceptable outage |

Paperless-ngx and Actual Budget contain sensitive documents/financial records;
do not import real data until their restore and access-denial tests pass.
Scrypted must pass its placement/camera-overlap gate before any installer runs.

## 1. Capture the docker-host baseline

Run on: docker-host over SSH.

```bash
date -Is
hostnamectl --static
docker version --format 'server={{.Server.Version}}'
docker compose version
df -hT /opt /mnt/omv/docker-host-backups
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'
ss -lntp
systemctl is-active docker-host-app-data-backup.timer
```

Expected result: hostname is the docker host, Docker/Compose versions print,
`/opt` and the OMV backup mount have safe headroom, existing containers/ports
are recorded, and the backup timer is active. Stop if a requested port is
already owned or the OMV path is an unmounted local directory.

## 2. Recreate only approved stack directories

Do not bulk-create candidate directories: an absent candidate path is useful
evidence that it remains parked. Recreate the currently approved/live paths.

Run on: docker-host over SSH.

```bash
install -d -m 0750 \
  /opt/stacks/mealie \
  /opt/stacks/grocy \
  /opt/stacks/obsidian-livesync \
  /opt/stacks/ntfy \
  /opt/stacks/searxng \
  /opt/stacks/whoogle \
  /opt/stacks/gardenkeeper \
  /opt/stacks/gridfinity-layout-tool
```

Expected result: only approved stack roots exist; no container starts and no
candidate becomes live. Copy the matching source-controlled templates using the
individual manuals, then run `docker compose config` before every `up -d`.

## 3. Rebuild live services sequentially

Use this order so notification and search/household dependencies are observable:

1. [ntfy](../services/ntfy.md) — authentication/topic policy, local-CA and
   Tailscale HTTPS, then notification delivery and restore proof.
2. [SearXNG](../services/searxng.md) and
   [Whoogle](../services/whoogle.md) — internal-only egress/abuse controls, then
   bounded search checks.
3. [Mealie](../services/mealie.md) and [Grocy](../services/grocy.md) — replace
   bootstrap credentials before recipe/inventory data; prove API scope and
   SQLite-consistent recovery.
4. [GardenKeeper](../services/gardenkeeper.md) — restore database/config before
   enabling its HA/LLM consumer.
5. [Gridfinity Layout Tool](../services/gridfinity-layout-tool.md) — rebuild the
   stateless app and confirm exports/downloads.
6. [Obsidian LiveSync](../services/obsidian-livesync.md) — rebuild the CouchDB
   backend, but keep client rollout parked unless explicitly resumed with one
   authoritative vault and a clean Git checkpoint.

For each service, stop and resolve failures before continuing to the next. Do
not use a phase-wide `docker compose up` or prune command.

Run on: docker-host over SSH after the relevant live stacks are rebuilt.

```bash
for stack in ntfy searxng whoogle mealie grocy gardenkeeper gridfinity-layout-tool obsidian-livesync; do
  if test -f "/opt/stacks/${stack}/docker-compose.yml"; then
    printf '\n== %s ==\n' "$stack"
    docker compose -f "/opt/stacks/${stack}/docker-compose.yml" ps
  else
    printf '%s: compose file absent\n' "$stack"
  fi
done
```

Expected output has a named section for every approved service. Rebuilt stacks
show their expected containers as `Up`/healthy; an absent file is explicit and
must be reconciled with current-live-state rather than silently skipped.

## 4. Finish live-service operator gates

The remaining household-completion work is deliberately interactive:

- Mealie: replace bootstrap admin, store the Bitwarden item, export recipes,
  and restore into a disposable path/container.
- Grocy: complete purchase/consume/correction/expiry for a disposable pilot
  product, then remove it and perform the documented rollback drill.
- Obsidian LiveSync: only if unparked, store CouchDB/E2EE/setup-URI secrets,
  upload one authoritative vault, then enroll one clean second device.
- ntfy: prove authenticated delivery and a denied anonymous/incorrect-topic
  request from the intended client paths.
- SearXNG/Whoogle: prove allowed internal requests and denied unapproved source
  access without broadening egress.
- GardenKeeper/Gridfinity: follow their manuals' state/export/restore checks.

Record the exact backup ID/path used for each restore. Testing against live data
in place is not an isolated restore proof.

## 5. Evaluate Paperless-ngx only after approval

Use [paperless-ngx.md](../services/paperless-ngx.md). Its gate must select the
scanner/import path, PostgreSQL layout, OCR languages, internal HTTPS/access,
retention, exporter/importer recovery, and protected document backup. First
consume only a harmless test PDF; do not scan identity, tax, medical, or finance
records during evaluation.

## 6. Evaluate Actual Budget only after approval

Use [actual-budget.md](../services/actual-budget.md). Remote browser use requires
the approved HTTPS path; the raw HTTP listener should remain loopback-only.
Create a disposable budget, export it, restore it into an isolated test target,
and prove password-reset recovery before importing financial data.

## 7. Evaluate Scrypted only after placement approval

Use [scrypted.md](../services/scrypted.md). The default decision is **parked**.
The gate must document why Frigate plus Home Assistant do not already meet the
camera need, whether Scrypted requires NVR recording, and whether a dedicated
Proxmox guest is selected. Do not give docker-host host networking, camera VLAN
access, `/dev/dri`, or recording storage until those exact boundaries are
approved and collision-tested.

## 8. Prove backup and isolated recovery coverage

Run on: docker-host over SSH.

```bash
findmnt -T /mnt/omv/docker-host-backups
systemctl start docker-host-app-data-backup.service
systemctl --no-pager --full status docker-host-app-data-backup.service
journalctl -u docker-host-app-data-backup.service -n 80 --no-pager
```

Expected result: the target is the exact OMV NFS mount, the job exits
successfully, and logs identify captured services without secrets. For a newly
approved candidate, update the backup job only after its consistency method is
known, then restore the resulting artifact to a disposable directory/container
and validate application-level data.

Recovery if the mount is absent: stop the backup job and affected services,
restore the Phase 06 NFS mount, prove `findmnt` shows the remote source, then run
a manual backup. Never accept a successful copy into an ordinary local
`/mnt/omv/docker-host-backups` directory.

## End-of-phase validation

Run on: docker-host over SSH.

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
docker ps --filter health=unhealthy --format '{{.Names}}'
ss -lntp
findmnt -T /mnt/omv/docker-host-backups
systemctl is-active docker-host-app-data-backup.timer
```

Expected result: every approved service is present and healthy, the unhealthy
query prints nothing, listeners match the service/access matrix, the backup
path is remote, and the timer is active. Candidate services not approved for
deployment remain absent.

Run on: docker-host over SSH.

```bash
for candidate in paperless-ngx actual-budget scrypted; do
  if test -e "/opt/stacks/${candidate}"; then
    printf '%s: candidate path exists; reconcile approval record\n' "$candidate"
  else
    printf '%s: parked/absent\n' "$candidate"
  fi
done
```

Expected output is `parked/absent` for each unapproved candidate. An existing
path is not automatically a failure, but it requires an approval/status review
before the phase can pass.

## Failure recovery matrix

| Failure | Safe response | Proof before continuing |
|---|---|---|
| Image pull or migration fails | Stop that stack, preserve data, restore prior Compose/env and pinned image. | Prior version starts and application data opens. |
| Port collision | Leave the new stack down; identify the owner with `ss`/`docker ps`. | Service matrix and firewall use one approved owner/port. |
| Bootstrap/default login remains | Keep access source-scoped and import no real data. | Default login fails; named credential is stored. |
| Backup target is local fallback | Stop jobs/services that write there; restore NFS first. | `findmnt` shows exact OMV source and fresh off-host artifact exists. |
| Restore test fails | Preserve live data and retry a known backup in a new disposable target. | App-level record/document/budget query succeeds in isolation. |
| Browser requires secure context | Do not weaken browser flags or publish raw HTTP. | Approved HTTPS endpoint and trust path work. |
| Candidate appears without approval | Stop it without deleting volumes and reconcile provenance. | Gate record is approved or stack remains stopped/parked. |
| Scrypted conflicts with camera/NVR paths | Stop Scrypted; restore prior Frigate/HA network/device state. | Existing camera streams, recording, and HA entities pass again. |

## Completion checklist

- [ ] Baseline ports, capacity, Docker versions, and OMV mount are recorded.
- [ ] Every live Tier 2 service rebuilds individually with expected health.
- [ ] Live services have named auth, narrow exposure, monitoring, consistent
  backup, isolated restore, and documented rollback evidence.
- [ ] Mealie operator credential/export/restore gates are complete.
- [ ] Grocy pilot workflow and rollback drill are complete.
- [ ] Obsidian LiveSync remains parked or completes controlled two-device rollout.
- [ ] Paperless-ngx remains absent or passes its sensitive-document gate.
- [ ] Actual Budget remains absent or passes HTTPS/export/restore/reset gates.
- [ ] Scrypted remains absent or has an approved placement and non-overlap proof.
- [ ] No automatic-update, broad firewall, public exposure, or destructive prune
  action was introduced.

Continue to [Phase 09 - Tier 3 / Evaluate Apps](09-tier3-evaluate.md) only after all
unapproved Tier 2 candidates are confirmed stopped/absent and every live Tier 2
dependency has recovery evidence.
