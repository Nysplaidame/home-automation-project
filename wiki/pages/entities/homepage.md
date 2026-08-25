---
title: "Homepage"
category: entity
tags: [dashboard, docker, docker-host]
created: 2026-05-23
updated: 2026-08-25
sources: [project-readme, project-todo]
status: active
---

# Homepage

**Type:** service - internal dashboard
**Status:** Live Tier 1 docker-host service
**Related:** [[entities/docker-host]], [[entities/qbittorrent]]

## Overview

Homepage is the live `Home Operations` dashboard for docker-host and core
home-automation links. It provides seven task-oriented tabs, fixed-target
embedded previews, container status, portal-runtime metrics, and a responsive
teal-glass interface.

## Key Properties

- Stack path: `/opt/stacks/homepage/`
- Canonical URL: `https://homepage.home.local/` locally and remotely through
  split DNS; direct local `https://192.168.20.102/` also works
- Rollback URL: `http://192.168.20.102:3001/`
- DNS name: `homepage.home.local`
- The canonical HTTPS name is used locally and remotely through split DNS:
  OpenWrt returns the LAN address and Tailscale/AdGuard returns docker-host's
  tailnet address for the approved phone.
- Every user-facing card uses a fixed proxy URL under `homepage.home.local`
  (`443` or `8180`-`8209`) rather than a private direct address; qBittorrent
  uses its fixed same-origin `/portal-preview/qbittorrent/` route. This makes
  the same cards work on home WiFi with Tailscale off and on mobile data with
  Tailscale on, without a broad subnet route.
- Responsive verification: exact checks from 320-1280 px; at 956 px the header
  reflows without title/search overlap, and at 489 px stacked cards retain a
  measured 10.4 px row gap
- Security: internal/Tailscale surface; preview proxy uses fixed targets and
  source-scoped firewall listeners
- Media tab includes the live qBittorrent Web UI/status card; no VPN or Web UI
  secret is stored in Homepage configuration

## Change Log

- 2026-08-25: Reconfirmed the canonical named URL and aligned the wiki with the
  reconciled architecture references.
- 2026-08-21: Moved all user-facing card navigation to fixed HTTPS proxy routes,
  added Recomp Tracker proxy `8209`, and granted the approved OnePlus identity
  only `tcp:8180-8209` in addition to its DNS and `tcp:443` access.
- 2026-08-01: Added the live qBittorrent Media card after tunnel, credential,
  firewall and backup acceptance passed.
- 2026-07-29: Added split-horizon DNS so one canonical bookmark works on WiFi and Tailscale.
- 2026-07-29: Synced live HTTPS, preview, responsive-layout and exact-width verification state.
- 2026-05-30: Updated from planned to live docker-host Tier 1 service.
- 2026-05-23: Page created from self-hosted services roadmap.
