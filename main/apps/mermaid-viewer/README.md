# Mermaid Viewer

Internal read-only viewer generated from the canonical sources under
`main/docs/diagrams/`.

This directory is the only repository source for the service:

- `src/` contains editable frontend source;
- `scripts/build.mjs` generates the release;
- `dist/` is the single checked-in release artifact;
- `docker-compose.yml` and `nginx.conf` define the deployed stack;
- `scripts/release.ps1` is the only packaging/deployment entrypoint.

Do not recreate a mirror under `configs/docker-host/stacks/`. Other docker-host
documentation should link here.

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
4. emits a static Nginx-ready `dist/` directory;
5. writes deterministic content hashes to `dist/SHA256SUMS`.

The UI uses the full available viewport and adapts its sidebar and diagram
canvas across desktop, embedded and mobile layouts. It supports full-text
filtering, deep links, fit, 100% view, zoom, pan, fullscreen, and optional
source display.

## Package, verify and deploy

Run the deterministic local release gate from the app directory:

```powershell
npm run release
```

That single command installs the locked dependency set, rebuilds `dist/`, writes
and displays its hashes, and runs the complete browser verification. It does not
contact the live host.

To run the same gate and deploy the exact verified artifact through the existing
SSH alias:

```powershell
npm run release -- -DeployHost docker-host-lan
```

The deploy path is fixed at `/opt/stacks/mermaid-viewer`. The command uploads to
a content-addressed temporary directory, validates every `dist/` hash and the
Compose model on docker-host, checkpoints the previous complete stack under
`/opt/backups/`, replaces the directory, and starts the new release. A failed
start restores the prior stack. No project secrets are required or included.

Follow the [operating manual](../../docs/install/services/mermaid-viewer.md) for
post-deploy acceptance and rollback boundaries.

## Verification

The release command runs this automatically. To run verification separately,
install the existing smoke-test dependencies with
`npm ci --prefix main/tools/playwright-smoke` from the repository root if
needed, then run `npm run verify` from this app directory.
The check serves the local build on loopback, compares all embedded sources
with canonical files, renders every diagram, checks browser errors, and
exercises mobile zoom, 100% and Fit on the three largest overview views.
Screenshots and dimensions go to the temporary `mermaid-diagram-review`
directory, or the path supplied by `DIAGRAM_SCREENSHOTS`.

The live stack bind-mounts `dist/` read-only. Use the complete release command
for routine changes so source, generated data, runtime and hashes remain one
coherent artifact. Emergency diagram-only replacement remains a documented
recovery technique, not the normal release path.
