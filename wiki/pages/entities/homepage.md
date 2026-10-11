---
title: "Homepage"
category: entity
tags: [dashboard, docker, docker-host, portal, nginx]
created: 2026-05-23
updated: 2026-10-11
sources: [project-readme, project-todo]
status: active
---

# Homepage

**Type:** service - internal dashboard / portal
**Status:** Live Tier 1 docker-host service
**Related:** [[entities/docker-host]], [[entities/voice-mixer]], [[entities/llm-host]]

## Overview

Homepage is the internal portal for docker-host apps and core home-automation
links. A companion nginx container (`homepage-preview-proxy`, host network)
fronts each app on its own TLS port at `https://homepage.home.local:<port>/`
using the local CA.

## Key Properties

- Stack path: `/opt/stacks/homepage/`; repo source
  `configs/docker-host/stacks/homepage/` (re-synced with live 2026-10-11).
- Homepage UI: `3001/tcp`; DNS name `homepage.home.local`.
- Portal ports `8180`–`8210`; docker-host UFW allows them from management,
  LAN, automation VLAN and `tailscale0` (range `8180:8209` plus `8210` rules).
- Remote-host apps use `siteMonitor` health checks, e.g. Open WebUI `8200` →
  CT 114 `3002`, Voice Mixer `8210` → CT 114 `7860`.

## Notes & Observations

- `nginx.conf` is a single-file bind mount rendered from a template at
  container start. In-place replacements (`sed -i`, editors) leave the
  container on the old file, so portal changes need
  `docker restart homepage-preview-proxy`; a reload alone is not enough.
- `services.yaml` lives in the mounted `config/` folder and is picked up live.

## Change Log

- 2026-10-11: Portal model documented; Voice Mixer added on `8210`; repo copy
  re-synced from live (it had predated the TLS portal on `main`).
- 2026-05-30: Updated from planned to live docker-host Tier 1 service.
- 2026-05-23: Page created from self-hosted services roadmap.
