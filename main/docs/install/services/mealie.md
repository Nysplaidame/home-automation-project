---
title: Mealie Install Manual
description: Live internal recipe and meal-planning service
tags: [install, docker-host, mealie]
created: 2026-05-24
modified: 2026-06-21
type: install-guide
status: live
---

# Mealie Install Manual

## Purpose

Host household recipes and meal planning.

## Runs on

docker-host over SSH at `192.168.20.102`.

## Prerequisites

- docker-host phase complete.
- Internal-only access chosen.

## Inputs

- An operator ready to replace the bootstrap administrator credentials on first login.

## Commands

Run on: docker-host over SSH.

```sh
mkdir -p /opt/stacks/mealie/data
cp /path/to/repo/main/configs/docker-host/stacks/mealie/docker-compose.yml \
  /opt/stacks/mealie/docker-compose.yml
cd /opt/stacks/mealie
docker compose config
docker compose up -d
```

## Explanation

The SQLite deployment is appropriate for this household. The image is pinned to
`v3.19.2`, open signup is disabled, and `mealie.home.local` is the canonical
internal name. Image pulls use the temporary Docker-host maintenance window in
`docs/procedures/update_maintenance_playbook.md`.

## Expected result

Mealie loads at `http://mealie.home.local:9925/`.

## Validation

Run on: docker-host over SSH.

```sh
cd /opt/stacks/mealie && docker compose ps
curl -fsS -o /dev/null http://127.0.0.1:9925/
```

## Home Assistant recipe tools

The repo includes a Home Assistant custom component at
`configs/home-assistant/custom_components/mealie_llm/`. It exposes narrow LLM
tools for importing a chosen recipe URL, searching saved recipes, and reading a
saved recipe back from Mealie.

To activate it on HA, add a Mealie bearer token to `secrets.yaml`:

```yaml
mealie_api_token: <MEALIE_API_TOKEN>
```

Then add the `mealie_llm` block from `configs/home-assistant/configuration.yaml`
to the live HA config, restart Home Assistant, and enable the `mealie_recipes`
LLM API on the local llama.cpp conversation agent.

Use `http://192.168.20.102:9925` in Home Assistant config so the tool does not
depend on HA resolving the internal `mealie.home.local` hostname.

## Backup

Back up `/opt/stacks/mealie/data`.

## Failure recovery

If the web UI does not load, inspect `docker compose logs --tail=80`.

## Completion checklist

- [x] UI loads.
- [x] Signup disabled.
- [ ] Data directory backed up.
- [ ] Bootstrap administrator credentials replaced and stored in Bitwarden.
