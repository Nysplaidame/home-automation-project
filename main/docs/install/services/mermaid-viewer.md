---
title: Mermaid Diagram Viewer
description: Internal read-only web viewer for canonical Mermaid diagrams
tags: [install, docker-host, diagrams, mermaid]
created: 2026-07-09
modified: 2026-09-11
type: install-guide
status: active
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

- `main/apps/mermaid-viewer/dist/` (HTML, CSS, JS, diagram data and vendor runtime)
- `main/configs/docker-host/stacks/mermaid-viewer/docker-compose.yml`
- `main/configs/docker-host/stacks/mermaid-viewer/nginx.conf`

Editable frontend sources are in `main/apps/mermaid-viewer/src/`; diagram
sources are in `main/docs/diagrams/`. See the app README for verification and
atomic diagram-only updates to the existing bind-mounted live stack.

## Build steps

Run on: admin workstation in the canonical repository checkout.

```sh
cd main/apps/mermaid-viewer
npm ci
npm run build
```

The build copies Mermaid into `dist/vendor/` so the viewer does not need a CDN or
runtime internet access.

## Deployment

1. Build the app in `main/apps/mermaid-viewer`.
2. Copy `dist/` into `/opt/stacks/mermaid-viewer/`.
3. Start the container with `docker compose up -d` from the stack directory.

## Notes

- Serve the static build over HTTP; ES-module diagram data requires a server.
  The deployed viewer uses a local Mermaid bundle.
- No editing or file write-back is planned.
- The viewer should stay behind the same internal trust boundary as other
  docker-host apps.

## Versioned recovery and update acceptance

Keep the source commit, lockfile, complete built `dist/` directory, Compose,
Nginx configuration and deployed image digest together outside VM103. The
viewer has no authoritative server database: canonical diagram sources in the
vault are the recovery source, while a retained build permits offline recovery.
Do not save just HTML and omit `diagram-data.js` or the local vendor runtime.

Use the [app verification procedure](../../../apps/mermaid-viewer/README.md)
on a fresh build: compare embedded sources against every canonical `.mermaid`
file, render the entire set and exercise mobile navigation. For a saved-build
restore, serve a copied `dist` on loopback in a disposable container with unique
name/network and no production proxy. Confirm diagram count, representative
deep links, source text and offline rendering without CDN access.

For diagram-only changes follow the app README's hash-checked single-file
replacement. For a full build, keep the old complete `dist` checkpoint and stop
the serving container during the reviewed directory replacement; recreate it
so its bind mount resolves the intended directory. Validate LAN and fixed HTTPS
proxy content plus a browser render. On failure restore the previous complete
build/config and image, recreate, and repeat those checks. Do not combine assets
from different builds. Record source/build hashes and acceptance date.

Diagrams: [library](../../diagrams/README.md) and
[placement](../../diagrams/infrastructure/docker-host-service-placement.mermaid).
