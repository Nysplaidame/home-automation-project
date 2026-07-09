---
title: Mermaid Diagram Viewer
description: Internal read-only web viewer for canonical Mermaid diagrams
tags: [install, docker-host, diagrams, mermaid]
created: 2026-07-09
modified: 2026-07-09
type: install-guide
status: draft
---

# Mermaid Diagram Viewer

## Purpose

Provide a small internal web UI for browsing the canonical Mermaid diagram
sources under `docs/diagrams/`.

## Placement

- Runs on `docker-host`.
- Internal-only.
- Read-only.
- No public exposure.

## Suggested stack path

```text
/opt/stacks/mermaid-viewer/
```

## Minimal architecture

- Static HTML/CSS/JS frontend.
- Manifest of canonical `.mermaid` files.
- Browser-side Mermaid renderer.
- Copy-link and search helpers.

## Files to deploy

- `main/apps/mermaid-viewer/index.html`
- `main/apps/mermaid-viewer/styles.css`
- `main/apps/mermaid-viewer/app.js`
- `main/apps/mermaid-viewer/diagram-index.json`

## Notes

- The viewer should serve the source files from `docs/diagrams/`.
- No editing or file write-back is planned.
- The viewer should stay behind the same internal trust boundary as other
  docker-host apps.
