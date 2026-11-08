---
title: Homepage Install Manual
description: Tier 1 internal dashboard for service links
tags: [install, docker-host, homepage]
created: 2026-05-24
modified: 2026-10-19
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

- `<DOCKER_HOST_TAILSCALE_IP>` from `tailscale ip -4`; this is not secret.
- A `Home Local CA` signed leaf certificate. Generate and keep its private key
  on docker-host.

Do not place tokens or passwords in visible Homepage config.

## Current live state

- October 19: **VentSys** is in Home → Home & Security beside Home Assistant.
  Its matching **Open tab** action opens the authenticated dashboard at
  `https://homepage.home.local:8188/dashboard-ventsys/0`, using the existing
  source-scoped HA proxy and normal HA sign-in. It does not add a Preview frame,
  token, port, firewall rule or synthetic ventilation-health status. Desktop
  navigation and 390 px mobile action bounds passed, and the proxy served the
  tested card byte-for-byte. Existing Voice Mixer and other live services were
  preserved by a narrow two-file patch. This viewport/server proof is not a new
  phone-on-mobile-data acceptance claim. See [[../../procedures/ventsys-dashboard]].
  Rollback: `/opt/backups/homepage-ventsys-20261019-082312Z/{services.yaml,custom.js}`;
  restore those two files to `/opt/stacks/homepage/config/` and call
  `/api/revalidate`. The config revalidation returned `{"revalidated":true}`.

- October18: Pocketry1.5.1 added beside Gridfinity in Tools → Workshop &
  Knowledge with the shared card, status, Preview and Open tab style, at
  `https://homepage.home.local:8211/` (loopback8098 backend). Browser checks
  passed; mobile-data8211 remains unverified. Preserve live Voice Mixer8210.
  See [[pocketry|Pocketry]] for rebuild and browser-project backups.

- Live at `/opt/stacks/homepage` on docker-host.
- Canonical local and remote bookmark: `https://homepage.home.local/`, using a
  `Home Local CA` certificate and split DNS. Local DNS returns
  `192.168.20.102`; the approved OnePlus tailnet client receives the
  docker-host Tailscale address. Direct local `https://192.168.20.102/` also
  works, and `http://192.168.20.102:3001/` remains the rollback endpoint.
- Uptime Kuma monitor `Homepage UI` is live.
- Rebuildable template: `configs/docker-host/stacks/homepage/`.
- Seven tabs are live: Home, Tools, Infrastructure, Monitoring, Storage, Media
  and Operations.
- Tailscale is available in Home's Reference Links; the duplicate Infrastructure card was removed on 2026-10-11.
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
  desktop and mobile behaviour. User-facing card links use their named fixed
  HTTPS proxy URLs, so the same links work locally and through the scoped
  OnePlus tailnet grant.
- A fixed-target Nginx sidecar terminates Homepage HTTPS on `443` and provides
  HTTPS portal-scoped preview routes on `8180`-`8209`. It has no dynamic
  target input, preserves service-specific CSP directives, replaces only the
  framing policy, and is host-firewall scoped to the existing LAN and Tailscale
  clients. qBittorrent remains the deliberate same-origin
  `/portal-preview/qbittorrent/` exception.
- The approved OnePlus mobile grant permits only split-DNS traffic, `tcp/443`
  and `tcp/8180-8209` to docker-host. Phone-side acceptance passed from mobile
  data across every Homepage tab; no broad VLAN route is part of this path.
- Home Assistant is framed through `8188` with its upstream local-CA
  certificate verified and WebSocket upgrade preserved. Because `8188` is a
  distinct browser origin, the first embedded visit requires its own HA login;
  the direct `8123` session cookie is not shared. GardenKeeper, Bambuddy,
  Whoogle, Proxmox, OpenWrt, Zyxel, Frigate, Grafana, Uptime Kuma and OMV proxy
  previews are live.
  OpenWrt has source- and port-scoped rules for the Docker
  host, including a separate INPUT rule for LuCI because traffic addressed to
  the router is not inter-zone forwarded traffic. The monitoring VM permits only
  docker-host `192.168.20.102` to Grafana `3000/tcp` and Uptime Kuma `3001/tcp`;
  matching `DOCKER-USER` returns are rebuilt by `monitoring-firewall.service`
  after Docker starts.
- Proxmox status uses the fixed-target local proxy health endpoint rather than
  ICMP. The explicit Homepage bridge subnet `10.240.1.0/24` is allowed only to proxy port
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
- Narrow/intermediate layout repair is live: the header becomes a bounded grid,
  resource metrics reflow without overlap, navigation uses gapped one/two/four
  column layouts, narrow service cards reserve a full-width Preview row, and
  the mobile-only ambient glow layer is removed while the dark network artwork
  remains. Visual checks passed at `320`, `350`, `375`, `390`, `430`, `480`,
  `768`, `900`, and `1280` px; the 390 px embedded workspace remained bounded
  and its Reload, Open tab, and Close controls remained operable.
- The reported intermediate-width regression was rechecked at exactly `956` px:
  header controls reflow below `1230` px and the search no longer encroaches on
  the title. At exactly `489` px, stacked service cards have a computed `10.4`
  px row gap rather than touching vertically.

## Commands

Run on: docker-host over SSH.

Copy the tracked `configs/docker-host/stacks/homepage/` directory to
`/opt/stacks/homepage/`, then run:

Run on: docker-host over SSH.

```sh
cd /opt/stacks/homepage
DOCKER_HOST_TAILSCALE_IP=$(tailscale ip -4)
test -n "$DOCKER_HOST_TAILSCALE_IP"
printf 'DOCKER_HOST_TAILSCALE_IP=%s\n' "$DOCKER_HOST_TAILSCALE_IP" >.env
chmod 600 .env
test -s tls/homepage.key
test -s tls/homepage.crt
test -s tls/ca.crt
openssl verify -CAfile tls/ca.crt tls/homepage.crt
docker compose config
docker compose up -d
```

Install and apply the tracked host-firewall rules after confirming the
Homepage Compose subnet is `10.240.1.0/24`:

Run on: docker-host over SSH.

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
`/opt/stacks/homepage/docker-compose.yml`. Include `preview-proxy/` (especially
activated `optional.d/*.conf`) and protect the live-only `tls/` directory as
secret-bearing recovery material. Never commit private keys.

Vaultwarden requires the existing `preview-proxy/vaultwarden.conf.example`
activated as `preview-proxy/optional.d/vaultwarden.conf` after its documented
certificate/backend prerequisites. September 11 found this directory empty:
Homepage still worked while vault.home.local received the wrong certificate.
After recovery, test each SNI hostname with normal certificate validation,
not just an IP-based HTTP200. A successful `nginx -t` cannot detect a missing
optional file matched by an empty wildcard.

## Failure recovery

### September 30 access repair and release contract

`Direct` means standalone navigation through the same fixed HTTPS proxy as
`Preview`. It must not substitute a backend LAN IP or HTTP port. The September
25 action did exactly that: Homepage and previews remained reachable while
mobile-data standalone navigation tried destinations outside the phone's
scoped Tailscale grant. Paths, queries and fragments remain preserved, and
port-based destinations inherit the outer Homepage hostname to preserve HA's
same-site ingress behavior. Raw backend URLs belong in management runbooks.

Bambuddy browser/PWA access now uses `https://homepage.home.local:8207/`.
Native Bambuddy Mobile retains `https://docker-host.tail7012a0.ts.net:8181/`.
Nginx retains `192.168.20.102:8181` only as a legacy LAN bookmark; it must never
bind wildcard or tailnet `8181`, which belongs to Tailscale Serve. Before this
repair, both services claimed it: tailscaled repeatedly reported `address
already in use`, and phone TLS handshakes reported `no webserver configured
for name/port`. Which listener starts first can change the symptom.

Before deploying navigation or proxy changes, run:

```powershell
node main/configs/docker-host/stacks/homepage/tests/access-contract.cjs
node --check main/configs/docker-host/stacks/homepage/config/custom.js
```

This gate checks standalone/preview parity, paths/query/fragments, LAN/name/
tailnet origins, scoped card URLs and separate native/browser port ownership.
Then run Compose validation, Nginx validation, `/api/revalidate`, inspect live
card destinations, and test both browser `8207` and native `8181` with normal
certificate validation. A green Homepage monitor or `nginx -t` alone does not
prove that individual cards work over the phone's access policy.

September 30 server checks: split DNS answered `100.94.122.18`; certificate-
verified Homepage and proxy ports `8180`, `8188`, `8195`, `8207`, `8209` returned
200, as did native Bambuddy `8181`. These server-origin probes do not prove
phone ACL acceptance. The phone was connected via London DERP; relay use is
not the cause of this raw-IP navigation regression. Final phone acceptance
requires refreshing Homepage on mobile data and opening standalone links.

Rollback files are on docker-host at
`/opt/backups/homepage-access-20260930/{custom.js,services.yaml,nginx.conf}`.
Copy each to its original config/preview-proxy path, recreate only
`preview-proxy`, and revalidate Homepage. That rollback restores the known
mobile-link and port-conflict defects, so use it only for a new regression.

For the historical failure picture, see the access guide. Preserve the narrow
phone grants; widening VLAN routes would conceal a navigation defect.

The owner confirmed mobile-data navigation now works across apps, with Grocy
as the remaining exception. Grocy's proxy was then corrected to preserve the
external Host and port: its old redirect escaped to raw LAN HTTPS `:9283`.
The regression gate covers this distinct header policy. Phone confirmation
of the Grocy follow-up also passed; the owner confirmed it works.

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
