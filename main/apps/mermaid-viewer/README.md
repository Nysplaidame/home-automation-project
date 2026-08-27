# Mermaid Viewer

Internal read-only viewer generated from the canonical sources under
`main/docs/diagrams/`.

## Build

```powershell
cd main/apps/mermaid-viewer
npm install
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

Copy this directory to `/opt/stacks/mermaid-viewer/` on docker-host and run:

```sh
cd /opt/stacks/mermaid-viewer
docker compose config
docker compose up -d
```

No project secrets are required or included.
