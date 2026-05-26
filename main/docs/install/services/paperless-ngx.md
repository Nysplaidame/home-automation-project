---
title: Paperless-ngx Install Manual
description: Tier 2 document management draft install
tags: [install, docker-host, paperless-ngx]
created: 2026-05-24
modified: 2026-05-24
type: install-guide
status: draft-installable
---

# Paperless-ngx Install Manual

## Purpose

Store and OCR household documents. This contains sensitive records, so backups
and access controls are mandatory before live use.

## Runs on

docker-host over SSH at `192.168.20.102`.

## Prerequisites

- docker-host phase complete.
- Backup destination selected.
- Document ingest path decided.

## Inputs

- `<PAPERLESS_ADMIN_USER>`
- `<PAPERLESS_ADMIN_PASSWORD>`

## Commands

Run on: docker-host over SSH.

```sh
mkdir -p /opt/stacks/paperless-ngx
cd /opt/stacks/paperless-ngx
curl --location --silent --show-error \
  https://raw.githubusercontent.com/paperless-ngx/paperless-ngx/main/install-paperless-ngx.sh \
  -o install-paperless-ngx.sh
less install-paperless-ngx.sh
```

Run on: docker-host over SSH only after reading the script.

```sh
bash install-paperless-ngx.sh
```

## Explanation

The official project provides an interactive Docker Compose installer. This
manual downloads it first for review instead of piping directly to a shell.

## Expected result

Paperless runs internally, usually on a configured HTTP port such as 8001.

## Validation

Run on: docker-host over SSH.

```sh
docker ps | grep -i paperless
```

## Backup

Back up media, export, consume, database, and Compose/env files before scanning
real documents.

## Failure recovery

If the interactive script creates an unwanted layout, stop the containers and
move the generated directory aside before retrying.

## Completion checklist

- [ ] Installer script reviewed.
- [ ] Admin account stored.
- [ ] Backup path defined.
- [ ] Service is not exposed publicly.
