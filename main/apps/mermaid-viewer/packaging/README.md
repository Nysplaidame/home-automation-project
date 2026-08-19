# Mermaid Viewer Packaging

Build and serve the static viewer from docker-host:

```sh
cd E:/home-automation-project/main/apps/mermaid-viewer
npm install
npm run build
docker compose -f packaging/docker-compose.yml up -d --build
```

This packaging directory is a draft; the final deployment path can be adjusted
to the actual docker-host stack location.
