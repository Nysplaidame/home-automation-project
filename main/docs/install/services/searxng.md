---
title: SearXNG Install Manual
description: Tier 2 internal metasearch candidate on docker-host
tags: [install, docker-host, searxng, search, privacy]
created: 2026-05-27
modified: 2026-09-14
type: install-guide
status: preflight-live
---

# SearXNG Install Manual

## Purpose

Provide an internal metasearch service for household/private search experiments.

## Runs on

docker-host over SSH at `192.168.20.102`.

## Prerequisites

- docker-host phase complete.
- Egress and rate-limit gate reviewed. SearXNG queries external search engines,
  so deployment changes docker-host's outbound traffic profile.
- Internal-only exposure accepted; no public exposure without a separate review.
- Check current upstream SearXNG deployment docs before live deployment.

## Inputs

- `SEARXNG_SECRET` in the protected stack `.env`; the effective application
  secret and engine/limiter settings must also be recovered and checked.

## Current pre-flight live state

As of 2026-05-27:

- Stack path: `/opt/stacks/searxng`.
- Direct URL: `http://192.168.20.102:8087/` /
  `http://searxng.home.local:8087/`.
- These are historical direct listeners. Current Homepage HTTPS proxy access
  is documented in the service matrix below; the old no-proxy claim is obsolete.
- `SEARXNG_SECRET` is stored live-only in `/opt/stacks/searxng/.env` and
  `/root/searxng-secret.txt`.
- UFW and `docker-host-firewall.service` scope `8087/tcp` to management, LAN,
  monitoring, `tailscale0`, Home Assistant (`192.168.20.101`), and local AI
  (`192.168.20.104`). Keep these automation exceptions before the terminal
  `8087/tcp` drop in the `DOCKER-USER` chain.
- Uptime Kuma monitor `SearXNG UI` is live and returned `200 OK`.
- The temporary WiFi WAN dependency is obsolete. The September baseline uses
  PPPoE on untagged `eth1`; search still depends on permitted host/router egress.

## Commands

Run on: docker-host over SSH, for installation or an agreed maintenance change.
Transfer the tracked Compose from the canonical checkout to a staging directory
on this host, compare it with the live file, then install the reviewed file at
`/opt/stacks/searxng/docker-compose.yml`. Do not regenerate a `latest` example.
The tracked bridge is `searxng` with subnet `10.240.8.0/24`; verify it does not
conflict with existing networks and retain the current firewall scope.

Recover the protected `.env` and settings on an existing installation. For a
blank install, copy [env.example](../../../configs/docker-host/stacks/searxng/env.example)
to `.env`, supply a unique secret, and copy the
[sanitized reviewed settings](../../../configs/docker-host/stacks/searxng/settings.reviewed.yml)
to `searxng/settings.yml`. The September12 snapshot matches the installed image;
review it again before changing image releases. Environment overrides supply
the real secret and advertised base URL. Never use the placeholder as a secret.
The source Compose now rejects an empty `SEARXNG_SECRET`.

Once these prerequisites are satisfied, run on docker-host:

```sh
cd /opt/stacks/searxng
docker compose config --quiet
```

Continue only when validation exits zero and the intended settings/image have
been reviewed. Pulling requires permitted registry egress:

```sh
cd /opt/stacks/searxng
docker compose pull searxng && docker compose up -d searxng
docker compose ps
```

Expected result: the pinned service stays running with only the intended
listener. Container startup alone does not establish working external search.

## Expected result

After approval and start, SearXNG loads internally at
`http://searxng.home.local:8087/`.

## Validation

Run on: Admin laptop, from a permitted network.

```powershell
Test-NetConnection 192.168.20.102 -Port 8087
```

This proves TCP reachability only. Open the approved URL from the service matrix
and verify the UI. During an approved search-egress window, issue one harmless
query and inspect returned results, elapsed time and service logs. A UI HTTP200
with blocked engines, a challenge page or no usable results is not search
acceptance. Record endpoint, image digest, time and outcome; do not archive
sensitive queries. Review bounded logs on docker-host:

```sh
cd /opt/stacks/searxng
docker compose logs --tail 80 searxng
```

## Backup

Back up Compose, protected `.env`, and the complete `searxng/` settings tree
with numeric ownership and permissions. Store the checkpoint outside VM103,
including its date, image digest and restored-file inventory. Quiesce the service
while taking a manual configuration checkpoint if settings are being edited.
The central docker-host app-data script does **not** include SearXNG. A VM backup
is a separate recovery layer whose current success must be verified.

Do not assume the secret ledger or Compose alone reconstructs effective settings.
Capture a sanitized settings template in source after recovering and reviewing
the real configuration; never commit the instance secret. Search results are
not a promised durable archive.

## Update and rollback

1. Record the deployed image ID/digest, Compose and configuration checkpoint.
   Retain the previous image; review the candidate release's configuration and
   upstream-search compatibility before changing the tracked digest.
2. Test the candidate using the isolated recovery procedure below. Review the
   source diff and validate Compose quietly; do not dump resolved secrets.
3. In a maintenance window, install the reviewed Compose and configuration,
   pull the selected image, then recreate only `searxng` using the commands
   above. Verify UI, a bounded query and any configured consumer integration.
4. If acceptance fails, stop `searxng`, preserve failed logs/settings separately,
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
port. Set `restart: "no"`. For SearXNG, point the bind mount at the copied settings
and adjust the test base URL. Keep consumers and production proxy/DNS disconnected.

Run `docker compose -p searxng-restore config --quiet` and then
`docker compose -p searxng-restore up -d` from that test directory. Confirm the
UI and effective configuration locally, using an SSH tunnel if the test VM is
remote. Only enable approved outbound search for the separate one-query check;
offline startup cannot prove upstream availability. Record the backup identity,
image, settings checks and query outcome. Stop the test with
`docker compose -p searxng-restore down` from the same directory. Retain evidence
and dispose of protected copied settings according to the backup policy.

A production recovery uses the verified checkpoint in the stopped production
stack, restores its original endpoints/network settings and ownership, then
passes the same UI/search checks before consumers resume.

## Failure recovery

For timeouts, separate DNS, TCP, UI and upstream-engine failures using the
[written diagnostic walkthroughs](../../troubleshooting/diagnostic-walkthroughs.md).
Inspect logs and current access policy before restarting or changing egress.
If queries cause repeated rate limits or challenges, pause automated consumers;
stop the service if necessary with `docker compose stop searxng` from
`/opt/stacks/searxng` on docker-host. Do not broaden firewall access to bypass an
upstream block. Resume only after a bounded query passes.

## Completion checklist

- [x] Upstream deployment docs checked for the historical May pre-flight.
- [ ] Recheck release-specific configuration before the next upgrade.
- [x] `secret_key` generated and stored outside git.
- [x] Egress/rate-limit policy accepted for pre-flight.
- [x] Internal-only access confirmed.
- [x] Uptime Kuma monitor added.

## Source and diagrams

Reviewed against the tracked configuration on 2026-09-11; this is a source
review, not a new live acceptance test. Use the
[tracked Compose](../../../configs/docker-host/stacks/searxng/docker-compose.yml)
for the exact image digest and network settings, and the
[service matrix](../../reference/service-matrix.md) for access policy.
The [diagram library](../../diagrams/README.md) links rendered views; Mermaid
sources show [service placement](../../diagrams/infrastructure/docker-host-service-placement.mermaid),
[remote access](../../diagrams/network/remote-access-flow.mermaid), and
[backup dependencies](../../diagrams/storage/storage-and-backup-flow.mermaid).

## September 11 settings recovery evidence

The live settings file exists at `/opt/stacks/searxng/searxng/settings.yml`.
A protected off-host copy is at
`C:/Users/Admin/home-automation-recovery/source-20260911-224938/searxng-settings.yml`.
Its remote/local SHA-256 matched:
`f38119af0322ac7c50fd07a07b16958f65b65a667646a5bf040916bc1480c181`.
It contains a secret assignment; do not copy this file into Git or print it.
The directory has restricted Windows ACLs as recorded in the current handoff.

A text-only inspection found `limiter: false` and 280 engine-name entries.
These are file observations, not parsed effective runtime configuration or
280 proven working engines. The attempted YAML parser was unavailable, so
secret/environment precedence, effective server URL and enabled-engine policy
remain unverified. Do not enable the limiter, replace the secret or generate a
sanitized production template from a regex alone. Complete semantic review
against the installed release before making that template authoritative.

## September 12 semantic verification

The earlier parser gap is closed: the installed interpreter is
`/usr/local/searxng/.venv/bin/python`. Its YAML parser and SearXNG settings loader
verified the sanitized snapshot without restarting the service. All280 engine
entries retain their enablement state (110 enabled); the limiter remains false.
These are configuration counts, not proof of successful searches through every
engine. The effective base URL is `http://searxng.home.local:8087/`, and the
effective secret equals the protected `SEARXNG_SECRET` environment value.
The secret embedded in the historical settings file differs, but is overridden
by the installed loader. Neither secret appears in the reviewed template.

The reviewed file was also loaded via a test-only `SEARXNG_SETTINGS_PATH` in a
separate Python process, confirming the protected environment supplies its real
secret. The source Compose passed a valid-input check and rejected an empty
secret. The production settings, limiter and container were unchanged.
Keep the existing protected settings checkpoint for recovery; schedule periodic
configuration capture separately if settings begin changing regularly.
