# Homepage portal (VM 103 `/opt/stacks/homepage`)

Rebuildable copy of the live portal, synced from docker-host on 2026-10-10.

| Path | Live location | Notes |
|---|---|---|
| `docker-compose.yml` | `/opt/stacks/homepage/` | Homepage on `3001`, `homepage-preview-proxy` (nginx, host network) |
| `.env.example` | `.env` (mode 600) | only `DOCKER_HOST_TAILSCALE_IP` |
| `config/*.yaml`, `custom.css`, `custom.js` | `config/` | services, settings, widgets, bookmarks, docker socket |
| `preview-proxy/` | `preview-proxy/` | TLS ports `8180`–`8210` proxying each app to `https://homepage.home.local:<port>/` (`8181` is bound to `192.168.20.102` only; Tailscale Serve owns tailnet `:8181`) |
| `assets/` | `assets/` | portal background |

Not tracked: `tls/` (local-CA certificates and private keys), `.env`,
`config/logs/`, `state/`, and the `*.bak*` / `*.pre-*` backups.

Docker-host UFW admits the portal ports from management `192.168.10.0/24`,
LAN `192.168.1.0/24`, automation `192.168.20.0/24` and `tailscale0`: one rule
set for the range `8180:8209`, plus individual `8210/tcp` rules (Voice Mixer,
2026-10-11).

Adding an app:

1. Back up, then add `server { listen <next port> ssl; ... proxy_pass ...; }`
   to `preview-proxy/nginx.conf` and an item in `config/services.yaml` pointing
   at `https://homepage.home.local:<port>/` (with `siteMonitor` or
   `server`/`container`). `config/` is a directory mount, so Homepage picks up
   `services.yaml` immediately.
2. `nginx.conf` is a single-file bind mount rendered from a template at
   container start. Editors that replace the file (`sed -i`, most editors) leave
   the container on the old inode, so apply it with
   `docker restart homepage-preview-proxy` (1–2 s portal blip), then check
   `docker exec homepage-preview-proxy grep -c "listen <port>" /etc/nginx/nginx.conf`.
3. Add UFW rules for the port with the four sources above if it is outside the range.

Edit live and repo together; re-sync this folder after any live change.
