---
title: ntfy Install Manual
description: Notification service installation, backup, update and recovery
tags: [install, docker-host, ntfy, notifications]
created: 2026-05-24
modified: 2026-09-11
type: install-guide
status: preflight-live
---

# ntfy Install Manual

## Purpose

Provide self-hosted notifications for monitoring and automation alerts.

## Runs on

docker-host over SSH at `192.168.20.102`.

## Prerequisites

- docker-host phase complete.
- Internal-only versus public relay decision gate reviewed.

## Inputs

- `<NTFY_ADMIN_PASSWORD>`
- `<NTFY_WATCHTOWER_PASSWORD>`
- `<NTFY_MONITORING_PASSWORD>`
- `<NTFY_MOBILE_SUBSCRIBER_PASSWORD>`

## Commands

Run on: docker-host over SSH. Transfer the
[tracked Compose](../../../configs/docker-host/stacks/ntfy/docker-compose.yml)
and [server template](../../../configs/docker-host/stacks/ntfy/etc/server.yml)
from the canonical checkout to a staging directory. Compare with live settings
before installing reviewed copies at `/opt/stacks/ntfy/docker-compose.yml` and
`/opt/stacks/ntfy/etc/server.yml`. Preserve existing databases and credentials;
do not overwrite an installed stack with a generated example.

On a blank host, create the `etc/` and `cache/` directories first and restore
protected data when recovering. The pinned image serves internal port80 on
host8085 and owns `local-alerting` (`10.240.15.0/24`); Watchtower joins this
network after ntfy exists. Check network conflicts, firewall scope and the
HTTPS/Tailscale terminators separately before advertising the endpoint.

```sh
cd /opt/stacks/ntfy
docker compose config --quiet
```

Continue only after validation succeeds and configuration is reviewed. During
permitted registry egress:

```sh
cd /opt/stacks/ntfy
docker compose pull ntfy && docker compose up -d ntfy
docker compose ps
```

For a new instance, provision the approved admin, publisher and subscriber
identities interactively and verify the topic ACLs below. A restored instance
must retain its existing users; do not recreate or rotate them just to test it.

## Current pre-flight live state

As of 2026-05-27:

- Stack path: `/opt/stacks/ntfy`.
- Primary browser URL: `https://192.168.20.102:8193/`, terminated by the
  Homepage local-CA HTTPS proxy. This is the required secure context for the
  browser Notifications API.
- Raw `http://192.168.20.102:8085/` remains an internal service listener only;
  do not use it in a browser or as ntfy's advertised base URL.
- Mobile Tailscale URL: `https://docker-host.tail7012a0.ts.net:8444/`, served
  privately by Tailscale Serve with a Tailscale-issued certificate.
- DNS alias `ntfy.home.local` points to `192.168.20.102`.
- Credentials are stored on docker-host at `/root/ntfy-credentials.txt`.
- `auth-default-access: "deny-all"` is live.
- Users:
  - `admin`: admin role.
  - `watchtower`: write-only access to topic `watchtower`.
  - `monitoring`: write-only access to topic `monitoring`.
  - `mobile-monitoring`: read-only access to topics `monitoring` and
    `watchtower`; generated credential stored outside the repository in Windows
    Credential Manager target `home-automation/ntfy-mobile`.
- UFW and `docker-host-firewall.service` scope `8085/tcp` to management, LAN,
  HA, monitoring, and `tailscale0`.
- Uptime Kuma monitor `ntfy UI` is live.
- Uptime Kuma notification `ntfy Monitoring` is active/default and mapped to all
  active monitors; database backup before enabling it:
  `/opt/monitoring/uptime-kuma/kuma.db.backup-20260527-172349-before-ntfy-notification`.

## Explanation

The default policy denies access until users/topics are configured. This avoids
accidentally creating an unauthenticated notification relay.

## Expected result

ntfy's browser-facing base URL is `https://192.168.20.102:8193/`; it listens
internally on HTTP `8085` only behind the HTTPS/Tailscale terminators.

## Validation

Run on: docker-host over SSH.

```sh
cd /opt/stacks/ntfy && docker compose ps
curl -fsS -o /dev/null -w '%{http_code}\n' https://192.168.20.102:8193/
```

Use a client that trusts the Homepage local CA for the HTTPS check; install the
approved CA or select the trusted Tailscale endpoint if trust is absent. Do not
count a certificate-bypassing probe as HTTPS acceptance. UI reachability does
not prove authenticated publish/subscribe or phone delivery.

## Mobile subscriber rollout

The read-only phone identity already exists in the recorded live state. Inspect
`ntfy user list` and `ntfy access` first. The following creation/grant commands
are only for a blank instance where that identity is absent; on restore, verify
the existing grants instead of adding the account again:

Run on: docker-host over SSH.

```sh
docker exec -it ntfy ntfy user add mobile-monitoring
docker exec ntfy ntfy access mobile-monitoring monitoring ro
docker exec ntfy ntfy access mobile-monitoring watchtower ro
docker exec ntfy ntfy user list
docker exec ntfy ntfy access
```

Store the generated password in a credential manager; do not add it to this
repository. The live account was created on 2026-07-29 and its credential is in
Windows Credential Manager under `home-automation/ntfy-mobile`.
On the phone, connect Tailscale and add a custom ntfy server using:

- server: `https://docker-host.tail7012a0.ts.net:8444`
- topic: `monitoring`
- user: `mobile-monitoring`
- password: the approved Windows Credential Manager value for
  `home-automation/ntfy-mobile`

This must be entered manually rather than through the old `ntfy://` deep link.
The mobile endpoint uses a Tailscale-issued HTTPS certificate; do not expose
port `8085` publicly.

After subscribing, publish one labelled test message and confirm it appears on
the phone before relying on ntfy for incident delivery.

## Backup

VM 103's configured Proxmox backup is the whole-stack recovery layer; confirm
its latest successful evidence before relying on it. The live docker-host
app-data backup job also stages a consistent SQLite snapshot of `etc/user.db`
and `cache/cache.db` using Python's SQLite backup API, plus the remaining files
under `etc/`. On 2026-07-29 a fresh NAS run completed and temporary restored
copies of both databases passed SQLite integrity checks.

The [app-data backup source](../../../configs/docker-host/system/docker-host-app-data-backup.sh)
writes `ntfy/etc/` and `ntfy/cache/` beneath
`/mnt/omv/docker-host-backups/runs/<UTC timestamp>/` and `latest/`. Select a
verified dated run; the existence of `latest` alone is not completion evidence.
Retain Compose/image digest and protected credential recovery separately: the
app-data snapshot does not include the stack Compose, `/root` credential files,
or HTTPS/Tailscale configuration. No attachment store is configured or covered.
Protect these backups as credentials and notification content. Its `--dry-run`
still creates staging/directories and snapshots SQLite; it is not read-only.

## Update and rollback

1. Record the running digest and a verified pre-change database/configuration
   checkpoint. If users or ACLs may change during backup, pause those changes
   so the checkpoint represents a known policy. Retain the old image.
2. Review the candidate's database/configuration migration requirements and test
   copied data in isolation. Change the tracked digest only after review.
3. During maintenance, stop publishers/consumers as needed, install the reviewed
   Compose, pull and recreate ntfy. Verify HTTPS, deny-all and each account's
   ACLs before an agreed labelled notification test. Resume integrations only
   when publish/subscribe works; phone receipt is a separate acceptance check.
4. On failure, stop ntfy, preserve failed data/logs separately, and restore both
   the old image/Compose and matching pre-change databases/configuration.
   Do not run an older binary on a potentially migrated live database. Restore
   ownership/permissions, recreate ntfy, verify ACLs and resume publishers.
   Restoring a checkpoint can lose newer messages or account changes; record
   that recovery point explicitly.

## Isolated restore rehearsal

Use a disposable Docker VM without production connectivity. Copy a dated
`ntfy/` snapshot to protected storage there, retaining ownership/permissions;
never bind-mount the NAS backup or live stack writable into the test.
Check each copied SQLite database before starting. Run on the test VM from the
copied snapshot directory; Python opens existing files read-only:

```sh
python3 - <<'PY'
import sqlite3
from pathlib import Path
for name in ('etc/user.db', 'cache/cache.db'):
    path = Path(name).resolve(strict=True)
    with sqlite3.connect(path.as_uri() + '?mode=ro', uri=True) as db:
        result = db.execute('PRAGMA integrity_check').fetchall()
        if result != [('ok',)]:
            raise SystemExit(f'{name}: integrity check failed')
        print(f'{name}: ok')
PY
```

Prepare a test-only Compose using the saved digest and copied `etc/`/`cache/`:
remove `container_name`, replace explicit `local-alerting` name/subnet with a
project-local network, set `restart: "no"`, and bind port80 only to loopback
on a verified unused test port. Adjust only the copied server base URL for the
test endpoint. Attach no production publishers, phones, proxy or Tailscale Serve.

From the test directory, run `docker compose -p ntfy-restore config --quiet`,
then `docker compose -p ntfy-restore up -d`. Inspect users/ACLs with
`docker compose -p ntfy-restore exec ntfy ntfy user list` and
`docker compose -p ntfy-restore exec ntfy ntfy access`. Confirm expected policy
without printing database rows or secrets. An agreed test using isolated
credentials/topics must prove unauthenticated denial, publisher write-only and
subscriber read-only access; SQLite integrity alone does not prove these.
Record the backup ID, digest and outcomes. Stop with
`docker compose -p ntfy-restore down` from that directory.

For production recovery, pause publishers and stop ntfy, preserve failed files,
restore the verified copies into the existing mount paths, and restore the
production endpoint configuration and permissions. Start the saved image and
validate before resuming publishers. Do not tear down the shared alerting
network while Watchtower uses it.

## Failure recovery

If auth blocks expected messages, inspect `server.yml` and user configuration
before changing firewall exposure.

## Completion checklist

- [x] Internal/public decision recorded.
- [x] Default access is not open.
- [x] Topic users created for Watchtower and Uptime Kuma monitoring.
- [x] Config is backed up by stack path and Proxmox VM backup.
- [x] Create the read-only `mobile-monitoring` subscriber and validate its
  authenticated subscription; phone-side notification acceptance is pending.
- [x] Deploy and restore-smoke the granular ntfy app-data backup template.
- [x] HTTPS browser and private Tailscale endpoints documented; public exposure
  is outside the accepted scope.
- [ ] Record phone-side delivery acceptance.
- [ ] Resolve Watchtower error40014 and record a separately agreed delivery test.
- [ ] Record a full isolated account/ACL restore rehearsal for the current image.

## Source and diagrams

Reviewed against the tracked configuration on 2026-09-11; this is a source
review, not a new live acceptance test. Use the
[tracked Compose](../../../configs/docker-host/stacks/ntfy/docker-compose.yml)
for the exact image digest and network settings, and the
[service matrix](../../reference/service-matrix.md) for access policy.
The [diagram library](../../diagrams/README.md) links rendered views; Mermaid
sources show [service placement](../../diagrams/infrastructure/docker-host-service-placement.mermaid),
[remote access](../../diagrams/network/remote-access-flow.mermaid), and
[backup dependencies](../../diagrams/storage/storage-and-backup-flow.mermaid).
