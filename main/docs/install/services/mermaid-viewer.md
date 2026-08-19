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

## Rebuildable template

```text
configs/docker-host/stacks/mermaid-viewer/
```

Live layout:

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
- `main/apps/mermaid-viewer/diagram-data.js`
- `main/apps/mermaid-viewer/package.json`
- `main/apps/mermaid-viewer/scripts/build.mjs`
- `main/apps/mermaid-viewer/Dockerfile`
- `main/apps/mermaid-viewer/nginx.conf`
- `main/apps/mermaid-viewer/packaging/docker-compose.yml`
- `main/configs/docker-host/stacks/mermaid-viewer/docker-compose.yml`
- `main/configs/docker-host/stacks/mermaid-viewer/nginx.conf`
- `main/configs/docker-host/stacks/mermaid-viewer/README.md`

## Build steps

```sh
cd main/apps/mermaid-viewer
npm install
npm run build
```

The build copies Mermaid into `vendor/` so the viewer does not need a CDN or
runtime internet access.

## Deployment

1. Build the app in `main/apps/mermaid-viewer`.
2. Copy `dist/` into `/opt/stacks/mermaid-viewer/`.
3. Start the container with `docker compose up -d` from the stack directory.

## Notes

- The viewer uses bundled diagram data for browser compatibility under `file://`
  and uses a local Mermaid bundle when deployed.
- No editing or file write-back is planned.
- The viewer should stay behind the same internal trust boundary as other
  docker-host apps.
