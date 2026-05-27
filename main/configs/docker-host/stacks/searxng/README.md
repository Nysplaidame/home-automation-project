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
