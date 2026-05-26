---
title: Actual Budget Install Manual
description: Tier 2 financial data service draft install
tags: [install, docker-host, actual-budget]
created: 2026-05-24
modified: 2026-05-24
type: install-guide
status: draft-installable
---

# Actual Budget Install Manual

## Purpose

Host Actual Budget for household finance data. Treat it as sensitive.

## Runs on

docker-host over SSH at `192.168.20.102`.

## Prerequisites

- docker-host phase complete.
- Backup and access review completed.

## Inputs

- `<ACTUAL_PASSWORD>`

## Commands

Run on: docker-host over SSH.

```sh
mkdir -p /opt/stacks/actual-budget/data
cd /opt/stacks/actual-budget
cat > docker-compose.yml <<'COMPOSE'
services:
  actual:
    image: actualbudget/actual-server:latest
    container_name: actual-budget
    restart: unless-stopped
    ports:
      - "5006:5006"
    volumes:
      - ./data:/data
COMPOSE
docker compose config
docker compose up -d
```

## Explanation

Actual stores sensitive financial data. Do not expose it beyond approved
internal/Tailscale access.

## Expected result

Actual loads at `http://192.168.20.102:5006/`.

## Validation

Run on: docker-host over SSH.

```sh
cd /opt/stacks/actual-budget && docker compose ps
```

## Backup

Back up `/opt/stacks/actual-budget/data` before importing real budgets.

## Failure recovery

If login or sync behaves unexpectedly, stop the stack and preserve the data
directory before retrying.

## Completion checklist

- [ ] UI loads.
- [ ] Access restricted.
- [ ] Backup path tested before real import.
