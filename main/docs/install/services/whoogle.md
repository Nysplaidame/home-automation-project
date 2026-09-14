---
title: Whoogle Install Manual
description: Tier 2 internal Google-search proxy candidate on docker-host
tags: [install, docker-host, whoogle, search, privacy]
created: 2026-05-27
modified: 2026-09-11
type: install-guide
status: preflight-live
---

# Whoogle Install Manual

## Purpose

Provide an internal, lightweight Google-search proxy candidate for private search
experiments.

## Runs on

docker-host over SSH at `192.168.20.102`.

## Prerequisites

- docker-host phase complete.
- Egress and rate-limit gate reviewed. Whoogle queries Google and may be blocked
  or rate-limited.
- Internal-only exposure accepted; no public exposure without a separate review.
- Check current upstream Whoogle deployment docs before live deployment.

## Inputs

No required project secrets for a basic internal evaluation.

## Current pre-flight live state

As of 2026-05-27:

- Stack path: `/opt/stacks/whoogle`.
- Direct URL: `http://192.168.20.102:8088/` /
  `http://whoogle.home.local:8088/`.
- These are historical direct listeners. Current Homepage HTTPS proxy access
  is documented in the service matrix below; the old no-proxy claim is obsolete.
- UFW and `docker-host-firewall.service` scope `8088/tcp` to management, LAN,
  monitoring, and `tailscale0`.
- Uptime Kuma monitor `Whoogle UI` is live and returned `200 OK`.
- The temporary WiFi WAN dependency is obsolete. The September baseline uses
  PPPoE on untagged `eth1`; search still depends on permitted host/router egress.

## Commands

Run on: docker-host over SSH, for installation or an agreed maintenance change.
Transfer the tracked Compose from the canonical checkout to a staging directory
on this host, compare it with the live file, then install the reviewed file at
`/opt/stacks/whoogle/docker-compose.yml`. Do not regenerate a `latest` example.
The tracked bridge is `whoogle` with subnet `10.240.9.0/24`; verify it does not
conflict with existing networks and retain the current firewall scope.

The tracked template has no persistent volume or required secret. Preserve any
intentional live overrides before replacing its Compose file; browser preferences
are outside this server-side recovery contract.

Once these prerequisites are satisfied, run on docker-host:

```sh
cd /opt/stacks/whoogle
docker compose config --quiet
```

Continue only when validation exits zero and the intended settings/image have
been reviewed. Pulling requires permitted registry egress:

```sh
cd /opt/stacks/whoogle
docker compose pull whoogle && docker compose up -d whoogle
docker compose ps
```

Expected result: the pinned service stays running with only the intended
listener. Container startup alone does not establish working external search.

## Expected result

After approval and start, Whoogle loads internally at
`http://whoogle.home.local:8088/`.

## Validation

Run on: Admin laptop, from a permitted network.

```powershell
Test-NetConnection 192.168.20.102 -Port 8088
```

This proves TCP reachability only. Open the approved URL from the service matrix
and verify the UI. During an approved search-egress window, issue one harmless
query and inspect returned results, elapsed time and service logs. A UI HTTP200
with blocked engines, a challenge page or no usable results is not search
acceptance. Record endpoint, image digest, time and outcome; do not archive
sensitive queries. Review bounded logs on docker-host:

```sh
cd /opt/stacks/whoogle
docker compose logs --tail 80 whoogle
```

## Backup

Preserve Compose, the exact image digest and any deliberate live overrides in a
protected checkpoint outside VM103. The tracked template has no mounted server
data, so recovery recreates the service; it does not restore browser preferences
or guarantee saved searches. If persistence or secrets were added live, inventory
and back them up before using this procedure.

The central docker-host app-data job does not include Whoogle. Repository
history preserves the template, but retaining the old image locally or in an
approved image archive is needed if its registry becomes unavailable.

## Update and rollback

1. Record the deployed image ID/digest, Compose and configuration checkpoint.
   Retain the previous image; review the candidate release's configuration and
   upstream-search compatibility before changing the tracked digest.
2. Test the candidate using the isolated recovery procedure below. Review the
   source diff and validate Compose quietly; do not dump resolved secrets.
3. In a maintenance window, install the reviewed Compose and configuration,
   pull the selected image, then recreate only `whoogle` using the commands
   above. Verify UI, a bounded query and any configured consumer integration.
4. If acceptance fails, stop `whoogle`, preserve failed logs/settings separately,
   restore the previous Compose and matching pre-update settings, and recreate
   the previous pinned image. Verify again before resuming consumers. Do not
   prune the old image or discard the checkpoint until acceptance is recorded.

## Isolated restore rehearsal

Use a disposable Docker VM without production access and a protected copy of
the checkpoint. Load the retained pinned image or use approved registry egress.
Never mount the original configuration directory into the test container.

Edit a test-only copy of Compose: remove `container_name`, use a unique project
name, replace the explicit network name/subnet with a project-local network,
and bind the container's HTTP port only to `127.0.0.1` on a verified unused test
port. Set `restart: "no"`. Keep consumers and production proxy/DNS disconnected.

Run `docker compose -p whoogle-restore config --quiet` and then
`docker compose -p whoogle-restore up -d` from that test directory. Confirm the
UI and effective configuration locally, using an SSH tunnel if the test VM is
remote. Only enable approved outbound search for the separate one-query check;
offline startup cannot prove upstream availability. Record the backup identity,
image, settings checks and query outcome. Stop the test with
`docker compose -p whoogle-restore down` from the same directory. Retain evidence
and dispose of protected copied settings according to the backup policy.

A production recovery uses the verified checkpoint in the stopped production
stack, restores its original endpoints/network settings and ownership, then
passes the same UI/search checks before consumers resume.

## Failure recovery

For timeouts, separate DNS, TCP, UI and upstream-engine failures using the
[written diagnostic walkthroughs](../../troubleshooting/diagnostic-walkthroughs.md).
Inspect logs and current access policy before restarting or changing egress.
If queries cause repeated rate limits or challenges, pause automated consumers;
stop the service if necessary with `docker compose stop whoogle` from
`/opt/stacks/whoogle` on docker-host. Do not broaden firewall access to bypass an
upstream block. Resume only after a bounded query passes.

## Completion checklist

- [x] Upstream deployment docs checked for the historical May pre-flight.
- [ ] Recheck release-specific configuration before the next upgrade.
- [x] Egress/rate-limit policy accepted for pre-flight.
- [x] Internal-only access confirmed.
- [x] Uptime Kuma monitor added.

## Source and diagrams

Reviewed against the tracked configuration on 2026-09-11; this is a source
review, not a new live acceptance test. Use the
[tracked Compose](../../../configs/docker-host/stacks/whoogle/docker-compose.yml)
for the exact image digest and network settings, and the
[service matrix](../../reference/service-matrix.md) for access policy.
The [diagram library](../../diagrams/README.md) links rendered views; Mermaid
sources show [service placement](../../diagrams/infrastructure/docker-host-service-placement.mermaid),
[remote access](../../diagrams/network/remote-access-flow.mermaid), and
[backup dependencies](../../diagrams/storage/storage-and-backup-flow.mermaid).
