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

SearXNG scrapes public result pages, so engines break when sites add CAPTCHAs, rate limits or
JavaScript-only pages. On 2026-11-05 voice search returned 0 results (Brave rate-limited,
DuckDuckGo/Startpage CAPTCHA, Google empty) on the pinned 2026-08-10 image. Egress is the home IP,
not the VPN.

Fix applied:

- Image updated and re-pinned to `2026.11.5-3e95f6cd2` (digest in `docker-compose.yml`); backups
  `docker-compose.yml.bak-20261105`, `searxng/settings.yml.bak-20261105-pre-update` (plus earlier
  `settings.yml.bak-20261105`, `.bak-20261105-pre-yandex`).
- Live `settings.yml` (not tracked here) general engines: **enabled** brave, bing, yandex, yahoo,
  mojeek, mwmbl (+ wikipedia/wikidata); **disabled** google, duckduckgo, startpage, qwant (blocked;
  they only add timeouts and suspensions). Typical query: 60-90 results from 5-6 engines.
- `Cannot load engine "adobe_stock"/"aol"/...` start-up errors are engines removed upstream that the
  old settings file still lists as disabled; harmless.
- Optional robust tier: `braveapi` (Brave Search API) and `google_cse` (Programmable Search) engines
  exist in this image and need an API key kept only in the live `settings.yml`.

Probe one engine with `/search?q=test&format=json&engines=<name>` and check `unresponsive_engines`.
After any image update, re-probe and adjust `disabled:` flags.
