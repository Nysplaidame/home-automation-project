---
title: SearXNG docker-host Template
description: Non-secret direct-access pre-flight template for SearXNG
tags: [docker-host, searxng, search]
created: 2026-05-27
modified: 2026-09-14
type: config-note
status: active
---

# SearXNG docker-host Template

This is the direct-access pre-flight template for
`http://searxng.home.local:8087/`.

Before starting live:

- Copy `env.example` only for a blank setup, then supply a generated secret;
  preserve the existing protected `.env` on recovery.
- Recover the existing `SEARXNG_SECRET`, or generate one only for a new instance.
- Use `settings.reviewed.yml` as the September12 sanitized settings snapshot,
  installed as `searxng/settings.yml` only after release/configuration review.
  Environment supplies the real secret and base URL. Limiter remains disabled
  and the recorded 110 enabled engines are preserved; this is not new policy.
- Keep `.env` out of git.
- Review egress/rate-limit policy before household use.

See the [operating manual](../../../../docs/install/services/searxng.md) for
backup, isolated restore, updates, rollback and Mermaid links.

September12: parsed the snapshot with the installed SearXNG interpreter and
loaded it through the application settings loader with the protected environment.
Engine enablement and limiter match the live file; the real secret is absent
from this template. Compose now rejects an empty secret. No live stack was restarted.
