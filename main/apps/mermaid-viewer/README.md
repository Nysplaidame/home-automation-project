# Mermaid Viewer

Internal read-only viewer generated from the canonical sources under
`main/docs/diagrams/`.

## Build

```powershell
cd main/apps/mermaid-viewer
npm ci
npm run build
```

The build:

1. discovers every canonical `.mermaid` file;
2. embeds the complete source in `dist/diagram-data.js`;
3. copies the local Mermaid runtime;
4. emits a static Nginx-ready `dist/` directory.

The UI uses the full available viewport and adapts its sidebar and diagram
canvas across desktop, embedded and mobile layouts. It supports full-text
filtering, deep links, fit, 100% view, zoom, pan, fullscreen, and optional
source display.

## Deploy

Build on the workstation, then stage the complete `dist/` together with
`main/configs/docker-host/stacks/mermaid-viewer/docker-compose.yml` and
`nginx.conf` at `/opt/stacks/mermaid-viewer/` on docker-host. The application
source directory alone is not the deployment stack. Follow the
[operating manual](../../docs/install/services/mermaid-viewer.md) for checkpoint,
atomic diagram-only updates and full-build rollback.

Run on: docker-host over SSH after staging and configuration review:

```sh
cd /opt/stacks/mermaid-viewer
docker compose config --quiet && docker compose up -d
```

No project secrets are required or included.

## Verification

After building, install the existing smoke-test dependencies with
`npm ci --prefix main/tools/playwright-smoke` from the repository root if
needed, then run `node main/apps/mermaid-viewer/scripts/verify-diagrams.mjs`.
The check serves the local build on loopback, compares all embedded sources
with canonical files, renders every diagram, checks browser errors, and
exercises mobile zoom, 100% and Fit on the three largest overview views.
Screenshots and dimensions go to the temporary `mermaid-diagram-review`
directory, or the path supplied by `DIAGRAM_SCREENSHOTS`.

The current live stack bind-mounts `dist/` read-only. For diagram-only updates,
back up the deployed `dist/diagram-data.js`, upload its replacement to a
sibling temporary file, verify its hash, then rename it into place. No
container restart is needed. Verify both the LAN endpoint and fixed HTTPS
proxy return the expected data, then inspect a live render.
