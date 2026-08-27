---
title: Actual Budget Install Manual
description: Decision-gated Actual Budget install with HTTPS, export, isolated restore, and password recovery
tags: [install, docker-host, actual-budget]
created: 2026-05-24
modified: 2026-08-09
type: install-guide
status: draft-installable
---

# Actual Budget Install Manual

## Purpose

Evaluate Actual Budget for household finance data. Keep the raw server
loopback-only, require an approved HTTPS path for remote browsers, and prove
export plus isolated recovery before importing bank or real budget data.

## Runs on

- docker-host over SSH at `192.168.20.102`;
- trusted Tailscale/HomeAdmin browser through the approved HTTPS endpoint.

## Deployment gate

Record approval for:

- whether Actual adds enough value to store financial data locally;
- exact stable image digest recorded on deployment day;
- loopback raw listener `127.0.0.1:5006` and HTTPS proxy/Tailscale endpoint;
- server password, optional separate E2EE password, and recovery ownership;
- no bank-sync provider until its credential/egress/privacy gate is separate;
- `/opt/stacks/actual-budget/data` consistent backup to OMV;
- UI export, isolated restore, password reset, update, and rollback proofs.

Do not deploy with `0.0.0.0:5006`, public exposure, header authentication, or
real financial data during the evaluation.

## Inputs

- `<ACTUAL_PASSWORD>` entered only in the trusted web UI or interactive reset.

If E2EE is enabled, create a separate password-manager secret; do not reuse the
server password or store either value in Compose.

## 1. Pull the current stable image and pin its digest

Run on: docker-host over SSH after gate approval and during a maintenance window.

```bash
install -d -m 0750 /opt/stacks/actual-budget/data
cd /opt/stacks/actual-budget
docker pull actualbudget/actual-server:latest
actual_image="$(docker image inspect actualbudget/actual-server:latest --format '{{index .RepoDigests 0}}')"
test -n "$actual_image"
printf 'ACTUAL_IMAGE=%s\n' "$actual_image" >.env
chmod 0600 .env
printf '%s\n' "$actual_image"
```

Expected result: pull succeeds and output is a repository reference ending in a
`sha256:` digest. `.env` contains only the immutable image reference, not the
Actual password. Record the upstream release corresponding to the digest.

## 2. Create and validate the loopback-only Compose stack

Run on: docker-host over SSH.

```bash
cd /opt/stacks/actual-budget
install -d -m 0750 data
cat >docker-compose.yml <<'COMPOSE'
services:
  actual:
    image: ${ACTUAL_IMAGE:?Set ACTUAL_IMAGE in .env}
    container_name: actual-budget
    restart: unless-stopped
    ports:
      - "127.0.0.1:5006:5006"
    volumes:
      - ./data:/data
    healthcheck:
      test: ["CMD-SHELL", "node src/scripts/health-check.js"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s
COMPOSE
docker compose config --quiet
docker compose up -d
docker compose ps
curl -fsS -o /dev/null -w 'HTTP %{http_code}\n' http://127.0.0.1:5006/
ss -lntp | grep '127.0.0.1:5006'
```

Expected result: `actual-budget` is `Up`/healthy, local HTTP returns `200`, and
`ss` shows only `127.0.0.1:5006`, never `0.0.0.0:5006` or `[::]:5006`.

If the upstream health-check path changes, leave the candidate stopped, verify
the current official Compose example, and update this manual; do not remove the
health check merely to make `ps` look green.

## 3. Add the approved HTTPS path

Actual requires HTTPS for safe/full remote browser functionality. The project
preference is a unique Tailscale Serve HTTPS port or the established local-CA
proxy; do not replace another service's existing Serve configuration.

Run on: docker-host over SSH only after confirming port `8445` is unallocated and Tailscale exposure is approved.

```bash
tailscale serve status
tailscale serve --bg --https=8445 http://127.0.0.1:5006
tailscale serve status
```

Expected result: existing Serve handlers remain present and a new HTTPS handler
on `8445` proxies only to loopback `5006`. From a trusted Tailscale client, open
`https://docker-host.tail7012a0.ts.net:8445/`, set `<ACTUAL_PASSWORD>`, then
create only a disposable evaluation budget.

If the current Tailscale CLI proposes replacing existing handlers, cancel and
use the documented proxy configuration method for that installed version.

## 4. Prove authentication and denied access

From a trusted browser, sign out/in with the stored server password. If E2EE is
selected, enable it only on the disposable budget, store the distinct secret,
and prove a second trusted client can decrypt after sync.

Run on: docker-host over SSH.

```bash
curl -fsS -o /dev/null -w 'loopback HTTP %{http_code}\n' http://127.0.0.1:5006/
docker compose -f /opt/stacks/actual-budget/docker-compose.yml ps
```

Expected result: loopback remains healthy, the container is healthy, and no raw
LAN listener exists. From an unapproved/non-Tailscale client, the HTTPS endpoint
must be unreachable; from the trusted client, an incorrect password must fail.

## 5. Export, back up, and restore disposable data

In the Actual UI, open the disposable budget and use **Settings -> Export** to
download an Actual export. Store the export in the approved encrypted backup
location; do not put it in the repository.

Run on: docker-host over SSH after completing the UI export.

```bash
cd /opt/stacks/actual-budget
find data -maxdepth 2 -type f -printf '%s %p\n' | sort | tail -n 20
findmnt -T /mnt/omv/docker-host-backups
docker compose stop actual
systemctl start docker-host-app-data-backup.service
systemctl --no-pager --full status docker-host-app-data-backup.service
docker compose up -d
docker compose ps
```

Expected result: non-zero server/user data files exist, backup target is the
OMV NFS mount, the stopped-file backup succeeds, and Actual returns healthy.
Confirm the backup job includes `actual-budget/data` before trusting it.

For the restore proof, copy the selected backup into a disposable directory,
create a temporary Compose override with a separate project/container name and
loopback port such as `15006`, then start it without mounting production data.
Open it only through a temporary approved HTTPS/localhost tunnel, authenticate,
and verify the disposable budget contents. Also import the UI export into a new
disposable budget and compare representative accounts/categories/transactions.

Cleanup must stop only the disposable project. Do not use `down -v` against the
production project.

## 6. Prove password-reset recovery

Run on: docker-host over SSH with the disposable restore container, not production.

```bash
docker exec -it actual-budget-restore-test /bin/sh
```

Run on: disposable Actual restore-test container.

```bash
node /app/src/scripts/reset-password.js
```

Expected result: the interactive command accepts a new disposable password and
the restored test server accepts it without losing the test budget. Exit the
container, record proof, and clean up the disposable project.

Use this on production only during an approved recovery; it invalidates the old
password and must be followed by password-manager/client updates.

## Updates

Export a budget, stop Actual for a consistent data backup, record the current
digest, pull the current stable release, update only `ACTUAL_IMAGE` in `.env`,
run `docker compose config`, recreate, and repeat HTTPS/login/sync/export checks.
Rollback by restoring the previous digest and compatible data checkpoint. Never
use nightly or automatic updates for real household finance data.

## Failure recovery

| Failure | Safe response | Proof before continuing |
|---|---|---|
| Raw listener exposed to LAN | Stop stack; restore loopback port mapping. | `ss` shows only `127.0.0.1:5006`. |
| HTTPS secure context fails | Keep raw listener loopback-only; repair trust/proxy. | Trusted browser loads approved HTTPS with no warning. |
| Password lost | Run official reset interactively after a backup. | New password works and data remains. |
| E2EE secret lost | Preserve encrypted files; recover from password manager/offline record. | Disposable client decrypts before further changes. |
| Upgrade fails | Restore previous digest and compatible stopped-data checkpoint. | Login, budget open, and sync/export pass. |
| Restore differs from source | Preserve both copies and compare the UI export plus server data backup. | Representative budget records agree. |

## Completion checklist

- [ ] Gate and immutable image digest are recorded.
- [ ] Raw listener is loopback-only and approved HTTPS works.
- [ ] Password and optional distinct E2EE secret are stored outside Git.
- [ ] Incorrect password and unapproved-source tests fail as intended.
- [ ] Disposable budget has both UI export and stopped-data OMV backup.
- [ ] UI import, isolated data restore, and password reset are proven.
- [ ] Update and digest rollback are documented and no automatic updates exist.
- [ ] No real financial data or bank-sync credential is imported before all prior items pass.
