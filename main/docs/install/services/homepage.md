---
title: Homepage Install Manual
description: Tier 1 internal dashboard for service links
tags: [install, docker-host, homepage]
created: 2026-05-24
modified: 2026-07-24
type: install-guide
status: live
---

# Homepage Install Manual

## Purpose

Provide the central `Home Operations` portal for household apps,
infrastructure, monitoring and docker-host workload status.

## Runs on

docker-host over SSH at `192.168.20.102`.

## Prerequisites

- docker-host phase complete.
- Service matrix available.

## Inputs

No required secrets. Do not place tokens or passwords in visible Homepage config.

## Current live state

- Live at `/opt/stacks/homepage` on docker-host.
- Reliable local URL: `http://192.168.20.102:3001/`.
- Planned friendly URL: `http://homepage.home.local:3001/`; use the IP until
  the canonical `home.local` router records are deployed.
- Uptime Kuma monitor `Homepage UI` is live.
- Rebuildable template: `configs/docker-host/stacks/homepage/`.
- Seven tabs are live: Home, Tools, Infrastructure, Monitoring, Storage, Media
  and Operations.
- User-facing portals and all running docker-host containers are represented.
- Docker-backed cards expose state and expandable CPU, memory and network
  statistics.
- Each portal card keeps its normal link and has a visible `Preview` control
  that opens the service in an inline workspace below the active tab's portal
  cards. The workspace remains within a margin-bounded split/work area rather
  than becoming a popup or touching the viewport edges.
- The preview toolbar always retains an `Open tab` fallback because individual
  services may prohibit framing with their own browser security headers.
- Preview loading is deliberately fail-safe: cross-origin frame failures do not
  emit a dependable browser error, so the loading veil clears after a short
  interval and never captures pointer input. A blocked service can therefore
  still be closed or opened normally.
- The header is a responsive full-width control bar: title, adaptive search,
  portal-runtime resources and date/time use the same raised translucent teal
  surface treatment. Service cards are 50% translucent dark teal with light
  teal copy and restrained outline shadows; the local network artwork remains
  unchanged apart from its gentle reduced-motion-aware drift.
- At desktop widths, a service group's cards use the available row before
  wrapping, so small groups such as two to five applications remain together.

## Commands

Run on: docker-host over SSH.

Copy the tracked `configs/docker-host/stacks/homepage/` directory to
`/opt/stacks/homepage/`, then run:

```sh
cd /opt/stacks/homepage
docker compose config
docker compose up -d
```

The tracked stack includes:

- `config/services.yaml` — portals and Docker workload cards.
- `config/settings.yaml` — tabs, responsive layout, theme and PWA shortcuts.
- `config/docker.yaml` — local read-only Docker socket integration.
- `config/widgets.yaml` — search and British date/time header.
- `config/bookmarks.yaml` — project and administration references.
- `config/custom.js` — accessible preview buttons and inline iframe work-area
  placement below the active card grid.
- `config/custom.css` — shared teal glass surfaces, restrained card elevation,
  responsive header/workspace styling and accessible low-motion background drift.
- `assets/portal-background.svg` — local, non-tracking visual background.

## Explanation

Homepage is internal navigation, not an authentication layer. It may read Docker
metadata through a read-only socket mount. The Docker socket is powerful even
when mounted read-only, so Homepage must remain internal and access-controlled
by the existing network policy.
`HOMEPAGE_ALLOWED_HOSTS` is required by current Homepage releases. Keep it
limited to the local, DNS and Tailscale names actually used to open the portal;
do not replace it with `*`.

Do not place API keys or service credentials in visible Homepage configuration.
Add authenticated service widgets only after their secrets can be injected
outside tracked YAML.

## Expected result

Homepage loads at `http://192.168.20.102:3001/` with Home, Tools,
Infrastructure, Monitoring, Storage, Media and Operations tabs. Docker-backed
cards show a green status dot when their mapped container is running or healthy.

## Validation

Run on: Admin laptop.

```powershell
Test-NetConnection 192.168.20.102 -Port 3001
Invoke-WebRequest http://192.168.20.102:3001/api/services -UseBasicParsing
Invoke-WebRequest http://192.168.20.102:3001/images/portal-background.svg -UseBasicParsing
```

Also check one desktop and one mobile viewport, each tab, browser console
errors, normal card navigation, the Mermaid Viewer embedded preview, its
`Open tab` fallback, and that the number of mapped Docker workloads matches
`docker ps`.

## Backup

Back up `/opt/stacks/homepage/config`, `/opt/stacks/homepage/assets`, and
`/opt/stacks/homepage/docker-compose.yml`.

## Failure recovery

- If config breaks the page, move the changed YAML aside and restart.
- Homepage renders its navigation as a generated static page. After changing
  `services.yaml` or `settings.yaml`, use the portal's bottom-right refresh
  control or run `curl http://192.168.20.102:3001/api/revalidate` once to
  regenerate that page. Restarting the container alone can leave the previous
  generated page visible until it is revalidated.
- If Docker socket exposure is undesired, remove the socket mount.

## Completion checklist

- [x] UI loads.
- [x] No secrets visible in config.
- [x] Config template is stored in repo.
- [x] All user-facing portals are represented.
- [x] All live docker-host workloads are represented.
- [x] Desktop and mobile layouts are verified.
