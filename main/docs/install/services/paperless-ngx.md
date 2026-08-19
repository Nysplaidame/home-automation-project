---
title: Paperless-ngx Install Manual
description: Decision-gated Paperless-ngx install, OCR ingest, backup, restore, update, and rollback
tags: [install, docker-host, paperless-ngx]
created: 2026-05-24
modified: 2026-08-09
type: install-guide
status: draft-installable
---

# Paperless-ngx Install Manual

## Purpose

Evaluate Paperless-ngx for searchable household documents. Documents, metadata,
correspondents, tags, and OCR output are sensitive. The service may be installed
with harmless test data, but it must not receive real identity, medical, tax, or
financial documents until authentication, narrow access, backup, and isolated
import recovery all pass.

## Runs on

- docker-host over SSH at `192.168.20.102`;
- trusted HomeAdmin/Tailscale browser for first login and document workflow;
- scanner/import client only after a separately approved source-scoped ingest
  path exists.

## Deployment gate

Record approval for all of these before running the installer:

- PostgreSQL-backed Docker Compose layout (upstream recommendation for new installs);
- exact upstream installer revision/hash reviewed that day;
- local port `8001` and approved internal HTTPS/access path;
- local consume directory for the first evaluation; no scanner share yet;
- OCR language `eng`, time zone `Europe/London`, UID/GID ownership;
- document retention/trash policy and whether originals may ever be deleted;
- exporter plus off-host OMV backup and isolated importer restore;
- named admin/daily-user model; no permanent use of a bootstrap superuser.

Stop if Redis or the database would be externally published, the consume path
is a network filesystem without polling, or a generated secret/env file would
enter Git.

## Inputs

- `<PAPERLESS_ADMIN_USER>`
- `<PAPERLESS_ADMIN_PASSWORD>`

Resolve these from the password manager only in the interactive installer/UI.
Do not put them on a command line.

## 1. Download, hash, and review the official installer

Run on: docker-host over SSH after the deployment gate is approved.

```bash
install -d -m 0750 /opt/stacks/paperless-ngx
cd /opt/stacks/paperless-ngx
curl --fail --location --silent --show-error \
  https://raw.githubusercontent.com/paperless-ngx/paperless-ngx/main/install-paperless-ngx.sh \
  -o install-paperless-ngx.sh
chmod 0750 install-paperless-ngx.sh
sha256sum install-paperless-ngx.sh
less install-paperless-ngx.sh
```

Expected result: download succeeds, SHA-256 prints, and review shows the official
interactive Compose installer rather than unexpected credential upload,
privileged device, or broad host changes. Record the hash/date in the deployment
log. If review is not accepted, remove only the downloaded script and leave the
candidate parked.

## 2. Run the interactive install with evaluation choices

Run on: docker-host over SSH only after reviewing the downloaded script.

```bash
cd /opt/stacks/paperless-ngx
bash ./install-paperless-ngx.sh
```

Choose the PostgreSQL Compose option, local port `8001`, time zone
`Europe/London`, OCR language `eng`, and host UID/GID that owns the stack paths.
Keep `consume`, `data`, `media`, and `export` persistent under the approved stack
layout. Do not publish PostgreSQL/Redis ports. Enter admin credentials only at
the installer prompt.

The upstream script can change; its current prompts are authoritative. If it
does not offer the recorded choices, cancel instead of improvising a live
layout, update this manual, and repeat review.

Expected result: generated Compose/env files exist, containers start, and the
installer reports the local Paperless URL. Restrict generated secret files to
the administrative owner before continuing.

Run on: docker-host over SSH.

```bash
cd /opt/stacks/paperless-ngx
find . -maxdepth 1 -type f -printf '%M %u:%g %f\n' | sort
chmod 0600 .env docker-compose.env 2>/dev/null || true
docker compose config --quiet
docker compose ps
curl -fsS -o /dev/null -w 'HTTP %{http_code}\n' http://127.0.0.1:8001/
```

Expected output: Compose validation exits `0`, database/broker/web/worker
services are `Up` (and healthy where defined), and local HTTP returns `200` or
the documented login redirect. A missing optional env filename is harmless;
the actual generated secret-bearing files must be mode `0600` and untracked.

## 3. Prove a harmless OCR/consume workflow

Use a one-page test PDF containing no personal information. Upload it through
the trusted browser first. If a consume directory is later approved, copy only
that test file into the exact host directory mapped to
`/usr/src/paperless/consume`.

Run on: docker-host over SSH after submitting the test PDF.

```bash
cd /opt/stacks/paperless-ngx
docker compose logs --since=10m 2>&1 | tail -n 120
find consume -maxdepth 1 -type f -printf '%f\n' 2>/dev/null || true
```

Expected result: logs show successful consumption/OCR/indexing with no
permission or broker error, the UI can search a known word, and the source file
has been consumed according to the configured workflow. Paperless normally
moves files out of the consume directory; do not treat disappearance as backup.

For a future NFS-backed consume directory, set the upstream polling option and
prove a newly copied test file is detected without a container restart. Prefer
a local consume directory plus controlled scanner transfer to avoid inotify and
partial-write surprises.

## 4. Configure identities and exposure

From a trusted browser:

1. replace/secure the bootstrap superuser and store it in Bitwarden;
2. create a non-superuser daily account if the service will be shared;
3. disable unneeded registration and test that an unauthenticated browser cannot
   enumerate documents or download media;
4. expose only through the approved internal HTTPS/Tailscale path;
5. add a Uptime Kuma login-page health check that contains no credentials or
   document identifiers.

Do not use scanner SMB credentials as Paperless admin credentials.

## 5. Export and copy a consistent backup off-host

Run on: docker-host over SSH after the harmless test document is indexed.

```bash
cd /opt/stacks/paperless-ngx
test -d export
docker compose exec -T webserver document_exporter ../export
find export -maxdepth 2 -type f -printf '%s %p\n' | sort | tail -n 20
findmnt -T /mnt/omv/docker-host-backups
systemctl start docker-host-app-data-backup.service
systemctl --no-pager --full status docker-host-app-data-backup.service
```

Expected result: exporter completes without error, export contains non-zero
manifest/data/document files, `findmnt` shows the OMV NFS source, and the backup
job exits successfully. Confirm the backup job explicitly includes the
Paperless export and required Compose/env reference without logging secrets.

An exporter artifact is the preferred portable recovery set. A file-level
database/media copy is additional protection and must be made with database
consistency understood; do not copy a live PostgreSQL data directory and call it
a tested backup.

## 6. Isolated restore proof

Restore the export into a disposable Paperless stack/project on loopback-only
ports and a separate database/data directory. Do not point it at production
volumes or start workers against the production consume directory.

Run on: docker-host over SSH after the disposable stack is configured and down.

```bash
cd /opt/stacks/paperless-ngx-restore-test
docker compose config --quiet
docker compose up -d
docker compose exec -T webserver document_importer ../export
docker compose ps
docker compose logs --tail=100
```

Expected result: importer completes, disposable services remain healthy, and a
trusted browser can find/open the harmless test document through the disposable
loopback/approved test endpoint. Record export ID/date and result.

Run on: docker-host over SSH after recording the successful proof.

```bash
cd /opt/stacks/paperless-ngx-restore-test
docker compose down --remove-orphans
```

Expected result: only disposable containers/networks stop. Preserve or remove
the disposable files according to the recorded cleanup decision; never use
`down -v` unless the exact disposable volumes have been listed and approved.

## Updates

During an approved maintenance window, create a fresh exporter backup, review
upstream release/migration notes, capture current image digests, pull the chosen
release, run `docker compose config`, then recreate and repeat OCR/search/export
checks. Do not use automatic updates for this data-bearing service.

## Failure recovery

| Failure | Safe response | Proof before continuing |
|---|---|---|
| Installer creates unexpected layout | Stop generated stack; preserve/move it aside; do not delete volumes. | Reviewed Compose/env paths and ports match the gate. |
| Consume file is ignored | Verify bind path, ownership, broker/worker, and enable polling for NFS. | New harmless file indexes without restart. |
| OCR language fails | Confirm installed OCR language/options; keep original. | Known test text is searchable and original opens. |
| Upgrade/migration fails | Restore prior Compose/image and known exporter into isolated stack first. | Prior version and test document work. |
| Login lost | Use the documented application admin recovery from local shell; keep exposure narrow. | Named admin works; anonymous access remains denied. |
| Export/import fails | Preserve live service and failed artifact; generate a new export. | Fresh isolated import and document open pass. |

## Completion checklist

- [ ] Gate records installer hash, PostgreSQL layout, OCR, access, retention, backup, restore, and rollback.
- [ ] Generated secrets are mode `0600`, ignored by Git, and stored in Bitwarden.
- [ ] Harmless PDF consumes, OCRs, searches, and opens successfully.
- [ ] Bootstrap/default access is removed and unauthenticated document access fails.
- [ ] Export is copied to real OMV storage and imports into a disposable stack.
- [ ] Monitoring and update/rollback procedures are proven.
- [ ] No sensitive household document is imported before every prior item passes.
