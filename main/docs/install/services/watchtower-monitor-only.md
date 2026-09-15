---
title: Watchtower Monitor-only Install Manual
description: Tier 3 update notification candidate without automatic updates
tags: [install, docker-host, watchtower, tier3]
created: 2026-05-24
modified: 2026-09-15
type: install-guide
status: preflight-live
---

# Watchtower Monitor-only Install Manual

## Purpose

Monitor for container image updates without applying automatic updates.

## Runs on

docker-host over SSH at `192.168.20.102`.

## Prerequisites

- Monitor-only gate approved.
- Notification target chosen if desired.

## Inputs

- `<WATCHTOWER_NTFY_PASSWORD>`

## Commands

Transfer the [tracked Compose](../../../configs/docker-host/stacks/watchtower/docker-compose.yml)
from the canonical checkout to a staging directory on docker-host. Compare it
with the live file before installing the reviewed copy at
`/opt/stacks/watchtower/docker-compose.yml`. It pins version1.7.1 by digest;
retain `WATCHTOWER_MONITOR_ONLY=true`, Docker API1.40 and no published API port.

Preserve the existing protected `.env`. For a blank installation, create it with
mode0600 using a protected editor and the approved `WATCHTOWER_NTFY_PASSWORD`;
use Compose-compatible quoting for the actual value. This is the existing
ntfy `watchtower` publisher password, not a new independent credential. Avoid
shell-history entry or printing resolved Compose, which includes the secret.
Start ntfy first: Watchtower joins its external `local-alerting` network.

Run on: docker-host over SSH, after these prerequisites are met.

```bash
cd /opt/stacks/watchtower
docker compose config --quiet && \
  docker compose config --format json \
  | jq -e '.services.watchtower.environment.WATCHTOWER_MONITOR_ONLY == "true"' >/dev/null
```

Stop if validation fails. Once the reviewed pinned image is available through
approved registry egress:

```sh
cd /opt/stacks/watchtower
docker compose pull watchtower && docker compose up -d watchtower
docker compose ps
```

Expected result: Watchtower stays running without a published port or target
container recreation. Its schedule is `0 0 4 * * *` (04:00 container time);
the template has no `TZ`, so verify the actual timezone before assigning a
Europe/London wall-clock interpretation.

## Current pre-flight live state

As of 2026-05-27:

- Stack path: `/opt/stacks/watchtower`.
- Watchtower `1.7.1` is running in monitor-only mode.
- `DOCKER_API_VERSION=1.40` is set because the docker-host daemon rejects the
  older default client API version.
- Notifications target internal ntfy topic `watchtower` over the shared
  `local-alerting` Docker network.
- No Watchtower HTTP/API port is exposed.
- Docker-host remains blocked from general internet access outside maintenance
  windows, so Watchtower update checks are meaningful only during an approved
  registry egress window unless a future decision allows narrow permanent
  registry access.

September6/7 evidence supersedes any assumption that configured notifications
are delivered: scans succeed, but ntfy rejects notifications with attachment-policy
error40014. Repair and acceptance remain open; retain the no-attachments policy.

## Explanation

`WATCHTOWER_MONITOR_ONLY=true` is the central safety setting. Do not remove it
without a new decision. The Docker socket mount permits privileged daemon
operations; monitor-only is an application setting, not a security boundary.
Do not attach a production socket during a recovery rehearsal.

## Expected result

Watchtower runs and reports updates, but does not recreate containers.

## Validation

Run on: docker-host over SSH.

```bash
docker inspect watchtower --format '{{range .Config.Env}}{{println .}}{{end}}' | grep WATCHTOWER_MONITOR_ONLY
docker logs --tail 80 watchtower
```

Expected output contains exactly `WATCHTOWER_MONITOR_ONLY=true`; logs may report
available images but must not report stopping, recreating, or updating a target
container. During an approved registry-egress window, record target container
IDs/start times before and after a scan and prove they are unchanged.

## Backup

Preserve Compose, image digest, protected `.env`, schedule/API settings and the
ntfy publisher account/ACL recovery reference. There is no application database
in the tracked Watchtower template; the central app-data job does not capture
its Compose or `.env`. Store the protected checkpoint outside VM103 and retain
the previous image if registry availability is a recovery dependency.

## Update and rollback

1. Record the current digest, protected configuration and target container
   IDs/start times. Review the candidate's monitor-only, Docker API and
   notification compatibility. Keep the existing image and checkpoint.
2. Rehearse on a disposable Docker VM as below, then change the tracked image
   digest and validate the monitor-only assertion before production recreation.
3. During permitted registry egress, pull and recreate only Watchtower. Observe
   a scheduled scan; confirm target IDs/start times are unchanged, no update
   actions occur, and distinguish scan success from notification acceptance.
4. On failure, stop Watchtower, preserve logs, restore its old Compose/image
   and protected environment, validate monitor-only and recreate it. If another
   container changed, its own image/data rollback is required; rolling back
   Watchtower cannot undo another application's migration.

## Isolated restore rehearsal

On a disposable Docker VM with only disposable target containers, restore a copy
of Compose using the saved image. Remove `container_name`, set `restart: "no"`,
remove the production `local-alerting` network and notification credentials,
and remove the notification settings for the initial scan-only test. Confirm
that the socket path belongs to this disposable VM, never the production host;
only then mount its local Docker socket. Keep monitor-only/API settings intact.

From the isolated directory run `docker compose -p watchtower-restore config --quiet` and apply the same JSON monitor-only assertion shown
above. Start with `docker compose -p watchtower-restore up -d`, record disposable
target IDs/start times, and observe one scheduled scan during permitted registry
egress. For a shorter test, edit only the test schedule to an explicit bounded
window; do not remove monitor-only. Confirm target containers remain unchanged.

Notification formatting requires a separate isolated ntfy with no-attachments
policy and test-only publisher/subscriber accounts. Test the repaired payload
there before any agreed production delivery test. An error40014 is failure,
not evidence that the subscriber is offline. Preserve the real production
credentials solely for eventual recovery; never insert them into this test.

Record saved digest, scan result, unchanged targets and any isolated notification
outcome, then stop with `docker compose -p watchtower-restore down` from the
test directory. Restore production using its protected configuration and the
original network only after ntfy/account recovery and monitor-only validation.

## Failure recovery

If automatic update behavior is observed, stop Watchtower immediately, capture
logs and target container IDs, restore any affected service using its own pinned
image/data rollback, then repair the tracked/runtime monitor-only setting before
another notification test.

## Completion checklist

- [x] Monitor-only setting present.
- [x] No auto-update policy accepted.
- [x] Notification path documented.
- [x] Repair error40014 and prove server acceptance (September15).
- [ ] Confirm phone receipt and next scheduled scan delivery.
- [ ] Record an isolated monitor-only restore and next-upgrade acceptance.

## Source and diagrams

Reviewed against the tracked configuration on 2026-09-11; this is a source
review, not a new live acceptance test. Use the
[tracked Compose](../../../configs/docker-host/stacks/watchtower/docker-compose.yml)
for the exact image digest and network settings, and the
[service matrix](../../reference/service-matrix.md) for access policy.
The [diagram library](../../diagrams/README.md) links rendered views; Mermaid
sources show [service placement](../../diagrams/infrastructure/docker-host-service-placement.mermaid),
[remote access](../../diagrams/network/remote-access-flow.mermaid), and
[backup dependencies](../../diagrams/storage/storage-and-backup-flow.mermaid).

## September 15 notification repair

The existing `watchtower` publisher has write-only access to its topic, and
`mobile-monitoring` has read-only access. No account or ACL change was required.
An isolated ntfy instance reproduced error40014 with a 5,000-byte text body.
The real pinned Watchtower image then completed a scan against a fake Docker
API with no production socket and delivered the bounded report successfully.

The tracked Compose now uses a compact report template with counts and a log
reference. It was deployed by recreating only Watchtower, retaining monitor-only,
image pin, schedule, network and protected credentials. The startup service-event
message was accepted and found in ntfy's cache at15:23 BST. Phone receipt and the
next scheduled real scan remain separate acceptance checks. A service-event
message directs the operator to logs; it does not certify a successful scan.

The current schedule is04:00 UTC (05:00 BST). Detailed scan warnings remain in
`docker logs watchtower`; ntfy attachment support remains disabled. Report count
`Updated` represents updates available in this monitor-only configuration.
Rollback configuration is protected at
`/root/recovery-verification-20260915/watchtower-compose-before.yml`.

References: [Watchtower report templates](https://containrrr.dev/watchtower/notifications/)
and [ntfy message-size behavior](https://docs.ntfy.sh/publish/#attachments).
