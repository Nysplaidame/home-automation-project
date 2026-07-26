---
title: Homepage Install Manual
description: Tier 1 internal dashboard for service links
tags: [install, docker-host, homepage]
created: 2026-05-24
modified: 2026-07-26
type: install-guide
status: live
---

# Homepage Install Manual

## Purpose

Provide the central `Home Operations` portal for household apps,
infrastructure, monitoring and docker-host workload status.

## Runs on

docker-host over SSH at `192.168.20.102`.

## Prerequisites

- docker-host phase complete.
- Service matrix available.

## Inputs

No required secrets. Do not place tokens or passwords in visible Homepage config.

## Current live state

- Live at `/opt/stacks/homepage` on docker-host.
- Primary local URL: `https://192.168.20.102/`, using a `Home Local CA`
  certificate. The former `http://192.168.20.102:3001/` remains available as
  a rollback endpoint.
- Planned friendly URL: `https://homepage.home.local/`; use the IP until
  the canonical `home.local` router records are deployed.
- Uptime Kuma monitor `Homepage UI` is live.
- Rebuildable template: `configs/docker-host/stacks/homepage/`.
- Seven tabs are live: Home, Tools, Infrastructure, Monitoring, Storage, Media
  and Operations.
- User-facing portals and all running docker-host containers are represented.
- Docker-backed cards expose state and expandable CPU, memory and network
  statistics.
- Each portal card keeps its normal link and has a visible `Preview` control
  that opens the service in an inline workspace immediately after the active
  tab's complete card grid. The workspace closes before a different tab is
  selected and remains within a margin-bounded split/work area rather than
  becoming a popup or touching the viewport edges. Its desktop and mobile
  heights are twice the original work-area dimensions, deliberately allowing
  page scrolling in exchange for a substantially larger embedded application.
- The preview toolbar provides working Reload, Open tab and Close controls.
  `Open tab` is a normal browser link rather than a scripted popup, for reliable
  desktop and mobile behaviour.
- A fixed-target Nginx sidecar terminates Homepage HTTPS on `443` and provides
  HTTPS portal-scoped preview routes on `8180`-`8204`. It has no dynamic
  target input, preserves service-specific CSP directives, replaces only the
  framing policy, and is host-firewall scoped to the existing LAN and Tailscale
  clients. Open tab always uses the original service URL.
- Home Assistant is framed through `8188` with its upstream local-CA
  certificate verified and WebSocket upgrade preserved. Because `8188` is a
  distinct browser origin, the first embedded visit requires its own HA login;
  the direct `8123` session cookie is not shared. GardenKeeper, Bambuddy,
  Whoogle, Proxmox, OpenWrt, Zyxel, Frigate and OMV proxy previews are live.
  OpenWrt has source- and port-scoped rules for the Docker
  host, including a separate INPUT rule for LuCI because traffic addressed to
  the router is not inter-zone forwarded traffic. Uptime Kuma remains blocked
  by the monitoring VM's host firewall even though its OpenWrt forwarding rule
  is live; `3000/tcp` and `3001/tcp` still need a monitoring-host allowance
  from `192.168.20.102`.
- Proxmox status uses the fixed-target local proxy health endpoint rather than
  ICMP. The Homepage bridge subnet `172.18.0.0/16` is allowed only to proxy port
  `8299/tcp`, so the health check reflects the real upstream without granting
  the container general host-service access.
- Preview loading is deliberately fail-safe: cross-origin frame failures do not
  emit a dependable browser error, so a delayed-preview notice replaces the
  loading veil after six seconds and never captures pointer input.
- The preview dock is appended only when its Homepage layout parent actually
  changes. Never re-append it on every observed DOM mutation: detaching an
  iframe reloads it, and the resulting mutation can otherwise create a loop
  that blanks previews and moves toolbar controls during clicks.
- The header is a responsive full-width control bar: title, adaptive search,
  portal-runtime resources and date/time use the same raised translucent teal
  surface treatment. Service cards are 50% translucent dark teal with light
  teal copy and restrained outline shadows; the local network artwork remains
  unchanged apart from its gentle reduced-motion-aware drift.
- At desktop widths, a service group's cards use the available row before
  wrapping, so small groups such as two to five applications remain together.
  Cards at 250 px or narrower grow vertically and give Preview its own bottom
  action row; wider cards keep the action inset by equal top and bottom margins.
  Preview hover/focus no longer shifts the control or exposes the status dot.
- Navigation tabs use distinct raised teal-glass default, hover/focus and
  selected states.

## Commands

Run on: docker-host over SSH.

Copy the tracked `configs/docker-host/stacks/homepage/` directory to
`/opt/stacks/homepage/`, then run:

```sh
cd /opt/stacks/homepage
docker compose config
docker compose up -d
```

Install and apply the tracked host-firewall rules after confirming the
Homepage Compose subnet remains `172.18.0.0/16`:

```sh
install -m 0755 docker-host-ufw-homepage-previews.sh \
  /usr/local/sbin/docker-host-ufw-homepage-previews.sh
/usr/local/sbin/docker-host-ufw-homepage-previews.sh
```

The tracked stack includes:

- `config/services.yaml` — portals and Docker workload cards.
- `config/settings.yaml` — tabs, responsive layout, theme and PWA shortcuts.
- `config/docker.yaml` — local read-only Docker socket integration.
- `config/widgets.yaml` — search and British date/time header.
- `config/bookmarks.yaml` — project and administration references.
- `config/custom.js` — accessible preview buttons and inline iframe work-area
  placement below the active card grid.
- `config/custom.css` — shared teal glass surfaces, restrained card elevation,
  responsive header/workspace styling and accessible low-motion background drift.
- `assets/portal-background.svg` — local, non-tracking visual background.
- `preview-proxy/` — fixed-upstream Nginx framing adapter; listeners are hosted
  directly on docker-host so existing inter-VLAN policy remains authoritative.
- `tls/` — live-only certificate, CA certificate and private key. This
  directory is never copied into version control; the private key remains on
  docker-host and only its CSR is signed by the HA-hosted local CA.

## Explanation

Homepage is internal navigation, not an authentication layer. It may read Docker
metadata through a read-only socket mount. The Docker socket is powerful even
when mounted read-only, so Homepage must remain internal and access-controlled
by the existing network policy.
`HOMEPAGE_ALLOWED_HOSTS` is required by current Homepage releases. Keep it
limited to the local, DNS and Tailscale names actually used to open the portal;
do not replace it with `*`.

Do not place API keys or service credentials in visible Homepage configuration.
Add authenticated service widgets only after their secrets can be injected
outside tracked YAML.

## Expected result

Homepage loads at `https://192.168.20.102/` with Home, Tools,
Infrastructure, Monitoring, Storage, Media and Operations tabs. Docker-backed
cards show a green status dot when their mapped container is running or healthy.

## Validation

Run on: Admin laptop.

```powershell
Test-NetConnection 192.168.20.102 -Port 443
Invoke-WebRequest https://192.168.20.102/api/services -UseBasicParsing
Invoke-WebRequest https://192.168.20.102/images/portal-background.svg -UseBasicParsing
```

Also check one desktop and one mobile viewport, each tab, browser console
errors, normal card navigation, the Mermaid Viewer and Household Hub embedded
previews, the Home Assistant/GardenKeeper/Bambuddy/Whoogle/Proxmox/OpenWrt/
Zyxel/Frigate/OMV proxy
previews, automatic close on tab change, placement after `#layout-groups`, all
three workspace toolbar controls, and that the number of mapped Docker
workloads matches `docker ps`.

## Backup

Back up `/opt/stacks/homepage/config`, `/opt/stacks/homepage/assets`, and
`/opt/stacks/homepage/docker-compose.yml`.

## Failure recovery

- If config breaks the page, move the changed YAML aside and restart.
- Homepage renders its navigation as a generated static page. After changing
  `services.yaml` or `settings.yaml`, use the portal's bottom-right refresh
  control or run `curl http://192.168.20.102:3001/api/revalidate` once to
  regenerate that page. Restarting the container alone can leave the previous
  generated page visible until it is revalidated.
- If Docker socket exposure is undesired, remove the socket mount.
- If the HTTPS sidecar must be rolled back, stop `preview-proxy` and use
  `http://192.168.20.102:3001/`. Portal links and Open tab remain usable.

## Completion checklist

- [x] UI loads.
- [x] No secrets visible in config.
- [x] Config template is stored in repo.
- [x] All user-facing portals are represented.
- [x] All live docker-host workloads are represented.
- [x] Desktop and mobile layouts are verified.
