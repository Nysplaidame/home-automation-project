---
title: Pocketry
description: Local photo tracing and Gridfinity cutout bins
modified: 2026-10-18
type: runbook
status: live
---

# Pocketry

Pocketry 1.5.1 is live on VM103 at **https://homepage.home.local:8211/**.
Homepage → Tools → Workshop & Knowledge includes its shared card, container
status, Preview and Open tab actions beside Gridfinity Layout Tool.

## Deployment

- Upstream: https://github.com/wcscr/pocketry
- Pinned unmodified source: `bed5852df30593fd8f2f511980640ade12c110d7`, AGPL-3.0-only.
- Workstation Ubuntu WSL build with Node22/npm: `npm ci && npm run build`.
  Deploy only the contents of `dist/public`, including LICENSE.txt/NOTICE.txt.
- Stack `/opt/stacks/pocketry`; templates in `main/configs/docker-host/stacks/pocketry/`.
- Container `pocketry`: unprivileged read-only Nginx, dropped capabilities,
  pinned existing runtime digest, explicit checked bridge `10.240.33.0/24`.
- Backend `127.0.0.1:8098`; host-network Homepage proxy serves HTTPS8211 using
  the existing Home Local CA certificate. No new DNS alias or VM103 WAN access.
- UFW8211 permits existing management/LAN/automation source networks and
  tailscale0; rebuild rule is in `docker-host-ufw-homepage-previews.sh`.
- Preserve the live Voice Mixer listener/card on8210.
- Phone policy documented through8209: mobile-data8211 remains unverified and
  may need a narrow Tailscale ACL addition. No broad subnet route was added.

## Rebuild/update

Build outside the vault and shared application VM, in Ubuntu WSL:

```sh
git clone https://github.com/wcscr/pocketry.git ~/builds/pocketry
cd ~/builds/pocketry
git checkout bed5852df30593fd8f2f511980640ade12c110d7
npm ci
npm run build
tar -czf /tmp/pocketry-1.5.1-dist.tar.gz -C dist/public .
```

Transfer the archive and tracked Compose/Nginx files to `/opt/stacks/pocketry`.
Extract to `dist/`, run `docker compose config -q`, then
`docker compose up -d --pull never`. Stage a missing runtime image from the
workstation. Retain the complete prior build/config before updating; export
browser projects first. No scheduled updater was created.

## Validation/rollback

October18 passed: production build; upstream self-hosting smoke test for app
routes, API/missing asset404s, caching, workers/WASM/OpenCV and legal notices;
Compose/Nginx validation; healthy container; certificate-verified HTTPS health;
Homepage access-contract and JavaScript syntax. Browser checks confirmed Tools
card, embedded welcome, standalone Bin controls and a drawn rectangle pocket
rendered in3D. Real-tool photos/physical fit and phone access remain untested.

Run upstream smoke test from the build checkout with the public CA supplied:
`NODE_EXTRA_CA_CERTS=/path/to/ca.crt npx tsx scripts/test-self-hosting.ts https://homepage.home.local:8211`.

Homepage snapshots: `/opt/backups/pocketry-install-20261018/` contains
`services.yaml`, `custom.js`, `nginx.conf`. Remove only Pocketry's card,8098→8211
mapping and8211 server block, or restore snapshots if no later edits exist.
Recreate `preview-proxy`, run `nginx -t`, and request `/api/revalidate` on3001
with `Host: homepage.home.local`. Stop the app with `docker compose down` in
its stack; remove only8211 UFW rules when retiring it.

## Data and backups

Photos, processing, geometry and projects remain in each browser. No server
database or shared library exists. Keep the canonical URL because storage is
bound to scheme/hostname/port. Export project/library `.pocketry.json` backups
to backed-up documents; keep original photos separately. STL/3MF and container
backups do not replace editable projects. Preview/standalone use the same origin.
