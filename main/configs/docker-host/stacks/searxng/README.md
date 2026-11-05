---
title: SearXNG docker-host Template
description: Non-secret direct-access pre-flight template for SearXNG
tags: [docker-host, searxng, search]
created: 2026-05-27
modified: 2026-05-27
type: config-note
status: active
---

# SearXNG docker-host Template

This is the direct-access pre-flight template for
`http://searxng.home.local:8087/`.

Before starting live:

- Copy `.env.example` to `.env`.
- Generate a real `SEARXNG_SECRET`.
- Keep `.env` out of git.
- Review egress/rate-limit policy before household use.

## Engine health (2026-11-05)

Voice-assistant search returned 0 results: Brave was rate-limited ("too many requests") and
DuckDuckGo/Startpage were CAPTCHA-blocked, while Google returned nothing. Bing (and Yandex) still
answered, so `bing` and `yandex` (backup) were enabled in the live `/opt/stacks/searxng/searxng/settings.yml`
(`disabled: false`; backups `settings.yml.bak-20261105`, `.bak-20261105-pre-yandex`). Probe an engine with
`/search?q=test&format=json&engines=<name>` and check `unresponsive_engines`.
