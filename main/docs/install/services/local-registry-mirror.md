---
title: Local Registry Mirror Install Manual
description: Tier 3 Docker Hub pull-through cache candidate
tags: [install, docker-host, registry, tier3]
created: 2026-05-24
modified: 2026-05-24
type: install-guide
status: draft-installable
---

# Local Registry Mirror Install Manual

## Purpose

Evaluate a local Docker Hub pull-through cache to reduce repeated external image
pulls across hosts.

## Runs on

docker-host over SSH at `192.168.20.102`.

## Prerequisites

- Registry mirror gate approved.
- Disk quota/location selected.
- Docker daemon rollback path documented.

## Inputs

No secrets for anonymous Docker Hub pull-through cache.

## Commands

Run on: docker-host over SSH.

```sh
mkdir -p /opt/stacks/registry-mirror/{data,config}
cd /opt/stacks/registry-mirror
cat > config/config.yml <<'YAML'
version: 0.1
log:
  fields:
    service: registry
storage:
  filesystem:
    rootdirectory: /var/lib/registry
proxy:
  remoteurl: https://registry-1.docker.io
http:
  addr: :5000
YAML
cat > docker-compose.yml <<'COMPOSE'
services:
  registry:
    image: registry:2
    container_name: registry-mirror
    restart: unless-stopped
    ports:
      - "5000:5000"
    volumes:
      - ./data:/var/lib/registry
      - ./config/config.yml:/etc/docker/registry/config.yml:ro
COMPOSE
docker compose config
docker compose up -d
```

## Explanation

The registry image can act as a pull-through cache. Client Docker daemons must be
configured separately to use it.

## Expected result

Registry mirror listens on `192.168.20.102:5000`.

## Validation

Run on: docker-host over SSH.

```sh
curl -I http://127.0.0.1:5000/v2/
```

## Backup

Cache data is disposable. Back up config only unless you intentionally store
private images later.

## Failure recovery

Remove the client daemon `registry-mirrors` setting and restart Docker if pulls fail.

## Completion checklist

- [ ] Disk location approved.
- [ ] Client rollback path documented.
- [ ] Config backed up.
