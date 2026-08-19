---
title: "Household Knowledge Hub"
category: entity
tags: [software, knowledge, rag, recipes, mealie, searxng, grocy, obsidian, nextcloud]
created: 2026-08-09
updated: 2026-08-09
sources: [project-readme, project-todo]
status: active
---

# Household Knowledge Hub

**Type:** service — household knowledge and recipe-research application
**Status:** Operational on [[entities/docker-host]]
**Related:** [[entities/docker-host]], [[entities/home-assistant]], [[entities/llm-host]], [[entities/homepage]]

## Overview

Household Hub runs under `/opt/stacks/household-hub` on VM 103. Its workbench
is exposed on port `8100`; PostgreSQL stores relational records, Qdrant stores
transcript vectors, Redis supports future background jobs, SearXNG supplies web
discovery, and [[entities/llm-host]] supplies local chat and embeddings. The app
owns household knowledge indexing, transcript RAG, recipe research and
provenance, without replacing Mealie, Grocy, GardenKeeper or Home Assistant as
their domains' systems of record.

## Key Properties

- Production API authentication is injected server-side by the web Nginx proxy;
  the bearer token is not stored in browser JavaScript or session storage.
- Home Assistant uses a separate read-only credential for household knowledge
  and recipe-research tools.
- Recipe review persists a UUID workflow record containing candidate and search
  provenance, normalized tags, notes, timestamps and current status.
- Mealie import requires the persisted confirmation UUID and matching source
  URL. Duplicate or in-progress handoffs are rejected.
- Import success records the Mealie slug and timestamp; failure records a
  retryable failed state without losing provenance.
- Search candidates and assistant-extracted drafts both use the same explicit
  review-before-import rule.
- Alembic revision `20260809_0002` owns the `recipe_workflows` table.
- A distinct Grocy key backs an application-enforced read-only overview of the
  five household locations, current stock/expiry and unchecked shopping list.
- Obsidian exports write to a persistent Markdown staging outbox, not directly
  into the LiveSync-owned CouchDB database. Writes require a persisted review
  UUID matching the draft's title and source URL.
- Nextcloud calendar projections remain dry-run-only while no Nextcloud service
  exists; the generated iCalendar object can be downloaded as `.ics`.

## Notes & Observations

- The recipe deployment passed 59 backend tests, Ruff, production builds,
  SQLite and PostgreSQL migration round trips, and live browser/API checks.
- Automated production verification did not create a Mealie recipe; a deliberate
  owner-driven import remains the final external-state acceptance check.
- The frontend dependency audit reports zero known vulnerabilities after the
  transitive Nano ID and PostCSS lockfile remediation.
- The integration deployment passed 62 backend tests, production builds, live
  Grocy/Obsidian/CalDAV probes, desktop/mobile checks and a clean browser console.
- NAS app-data run `20260809T130054Z` captured the Grocy key state and added the
  persistent Markdown outbox to `latest/household-hub-exports`.

## Open Questions

- [ ] Move YouTube transcript import and indexing into durable Redis-backed jobs
  with progress, retries and visible failure state.
- [ ] Connect a supported Obsidian vault filesystem path if automatic outbox
  ingestion is later required; do not write raw LiveSync CouchDB documents.
- [ ] Deploy Nextcloud and create a dedicated app credential before enabling
  non-dry-run CalDAV uploads.

## Change Log

- 2026-08-09: Page created after persisted recipe confirmation/import workflow,
  production migration and browser-authentication repairs went live.
- 2026-08-09: Added live read-only Grocy, persistent Obsidian Markdown outbox and
  downloadable Nextcloud-compatible `.ics` projections.
