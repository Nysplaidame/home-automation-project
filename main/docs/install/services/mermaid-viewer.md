---
title: Mermaid Diagram Viewer
description: Internal read-only web viewer for canonical Mermaid diagrams
tags: [install, docker-host, diagrams, mermaid]
created: 2026-07-09
modified: 2026-09-25
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

## Canonical source and release artifact

```text
main/apps/mermaid-viewer/
```

This is the only repository tree for the service. Editable frontend files live
in `src/`. The generated `dist/` directory is the single checked-in release
artifact. Compose, Nginx configuration and release tooling live beside it.
There is intentionally no mirror under `configs/docker-host/stacks/`.

Live layout remains:

```text
/opt/stacks/mermaid-viewer/
```

## Minimal architecture

- Static HTML/CSS/JS frontend.
- Manifest of canonical `.mermaid` files.
- Browser-side Mermaid renderer.
- Copy-link and search helpers.

## Release contents

- `main/apps/mermaid-viewer/dist/` (HTML, CSS, JS, diagram data and vendor runtime)
- `main/apps/mermaid-viewer/docker-compose.yml`
- `main/apps/mermaid-viewer/nginx.conf`

Editable frontend sources are in `main/apps/mermaid-viewer/src/`; diagram
sources are in `main/docs/diagrams/`. `dist/SHA256SUMS` binds the generated
files into one verifiable release.

## Package and verification

Run on: admin workstation in the canonical repository checkout.

```sh
cd main/apps/mermaid-viewer
npm run release
```

The command performs `npm ci`, rebuilds from canonical diagram and frontend
sources, writes deterministic content hashes, and runs the browser verification.
The build copies Mermaid into `dist/vendor/`, so the viewer needs no CDN or
runtime internet access.

## Deployment

Run on the canonical Windows workstation:

```powershell
cd main/apps/mermaid-viewer
npm run release -- -DeployHost docker-host-lan
```

This is the sole routine packaging/deployment command. It deploys only after
the local browser gate passes, uploads the verified release to a
content-addressed staging directory, verifies hashes and Compose remotely,
checkpoints the previous complete stack, and swaps the release. A failed start
restores the previous stack. After success, verify the LAN endpoint, Homepage
proxy and representative desktop/mobile diagram renders.

## Notes

- Serve the static build over HTTP; ES-module diagram data requires a server.
  The deployed viewer uses a local Mermaid bundle.
- No editing or file write-back is planned.
- The viewer should stay behind the same internal trust boundary as other
  docker-host apps.

## Versioned recovery and update acceptance

Keep the source commit, lockfile, complete checked-in `dist/` release, Compose,
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

Use the app README's release command for routine diagram and frontend changes.
The deploy helper retains a complete timestamped backup under `/opt/backups/`
and rolls back automatically when the replacement stack does not start. Validate
LAN and fixed HTTPS proxy content plus a browser render. Do not combine assets
from different builds. Record source/build hashes and acceptance date.

Diagrams: [library](../../diagrams/README.md) and
[placement](../../diagrams/infrastructure/docker-host-service-placement.mermaid).
