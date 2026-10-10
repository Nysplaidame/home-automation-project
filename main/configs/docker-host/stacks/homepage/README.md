# Homepage portal (VM 103 `/opt/stacks/homepage`)

Rebuildable copy of the live portal, synced from docker-host on 2026-10-10.

| Path | Live location | Notes |
|---|---|---|
| `docker-compose.yml` | `/opt/stacks/homepage/` | Homepage on `3001`, `homepage-preview-proxy` (nginx, host network) |
| `.env.example` | `.env` (mode 600) | only `DOCKER_HOST_TAILSCALE_IP` |
| `config/*.yaml`, `custom.css`, `custom.js` | `config/` | services, settings, widgets, bookmarks, docker socket |
| `preview-proxy/` | `preview-proxy/` | TLS ports `8180`–`8210` proxying each app to `https://homepage.home.local:<port>/` |
| `assets/` | `assets/` | portal background |

Not tracked: `tls/` (local-CA certificates and private keys), `.env`,
`config/logs/`, `state/`, and the `*.bak*` / `*.pre-*` backups.

Adding an app: add a `server { listen <next port> ssl; ... proxy_pass ...; }`
line to `preview-proxy/nginx.conf`, an item in `config/services.yaml` pointing
at `https://homepage.home.local:<port>/` (with `siteMonitor` or
`server`/`container`), make sure the docker-host firewall admits the port, then
`docker exec homepage-preview-proxy nginx -t && docker exec homepage-preview-proxy nginx -s reload`.
Edit live and repo together; re-sync this folder after any live change.
