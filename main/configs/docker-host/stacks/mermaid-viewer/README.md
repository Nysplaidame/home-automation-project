# Mermaid Viewer Docker-Host Stack

Template for the internal read-only Mermaid diagram browser.

Expected live layout:

```text
/opt/stacks/mermaid-viewer/
  docker-compose.yml
  nginx.conf
  dist/
    index.html
    styles.css
    app.js
    diagram-data.js
    vendor/
      mermaid.esm.min.mjs
```

Deployment flow:

```sh
cd /opt/stacks/mermaid-viewer
docker compose up -d
```

Build `dist/` from the repo app directory before starting the container:

```sh
cd main/apps/mermaid-viewer
npm install
npm run build
```

Then copy the resulting `dist/` tree to `/opt/stacks/mermaid-viewer/dist/`.

The service is internal-only and read-only.

