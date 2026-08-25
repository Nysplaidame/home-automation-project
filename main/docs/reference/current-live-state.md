---
title: Current Live State
description: Canonical inventory of deployed hosts, services, and deliberately deferred components
tags: [reference, current-state, infrastructure]
created: 2026-06-20
modified: 2026-08-25
type: reference
status: active
---

# Current Live State

This is the canonical current-state inventory. Rebuild manuals describe how to
build from blank and must link here rather than duplicating live-status claims.

Full state verification: **2026-08-09**. Core endpoint reachability, including
Recomp Tracker, was rechecked on **2026-08-19**; this does not replace the
recorded functional acceptance checks. Homepage's fixed mobile proxy routes and
their Tailscale grant were server-side rechecked on **2026-08-21**. The
canonical architecture references, diagrams, active setup guides and generated
Mermaid Viewer source were reconciled against that evidence and the tracked
configuration on **2026-08-25**. A management-workstation endpoint spot check
that day passed router, Frigate, docker-host, Bambuddy, MQTT TLS, Grafana, Kuma,
llama.cpp, OMV NFS and Frigate HTTPS; Home Assistant returned HTTPS `200` via
`curl -k`. The PowerShell health-check HTTP implementation was corrected after
it misreported that trusted-local-CA response as `HTTP 0`.

The Household admin workstation joined Tailscale on 2026-07-13 as
`household-admin-workstation` (`100.95.209.14`). Tailnet peer discovery and
WireGuard connectivity to docker-host pass, but the current tailnet ACL denies
service and SSH connections from the new device. Management-VLAN access remains
available through the explicit `192.168.20.0/24` route while ACL approval is
completed in the Tailscale admin console.

The canonical OpenWrt and service-matrix inventories contain 48 authoritative
`home.local` aliases. They were deployed to live OpenWrt on 2026-07-29 and
dnsmasq restarted successfully. The full
`scripts/validation/validate-home-local-dns.ps1 -DnsServer 192.168.10.1` run
passed all 48 aliases after temporarily disconnecting Mullvad's DNS leak
protection; Mullvad was reconnected immediately afterward. The now-redundant
workstation hosts entry for `homeassistant.home.local` was removed with an
elevated edit on 2026-07-29 and the Windows DNS cache was flushed.

## Compute

| ID | Kind | Name | Address | State | Role |
|---:|---|---|---|---|---|
| 100 | QEMU VM | home-assistant | `192.168.20.101` | Live | HAOS 2026.7.1, native HTTPS, MQTT, ESPHome and Assist |
| 101 | QEMU VM | frigate-nvr | offline | Rollback only | Pre-LXC snapshot; `onboot=0` |
| 102 | QEMU VM | monitoring | `192.168.60.10` | Live | Uptime Kuma, InfluxDB, Grafana and Telegraf |
| 103 | QEMU VM | docker-host | `192.168.20.102` | Live | Trusted Compose workloads and Tailscale routing |
| 104 | QEMU VM | llm-host | offline | Rollback only | Pre-LXC snapshot; `onboot=0` |
| 111 | unprivileged LXC | frigate-nvr | `192.168.30.20` | Live | Frigate 0.17.1, OpenVINO and VA-API on shared iGPU |
| 114 | unprivileged LXC | llm-host | `192.168.20.104` | Live | llama.cpp, Open WebUI and Wyoming voice services on shared iGPU |

VM 101 and VM 104 are retained temporarily as rollback points. Production DNS
and static addresses belong to CT 111 and CT 114. Never start either retired VM
while its replacement LXC is running.

## Home Assistant

- Configuration check passes on HAOS 2026.7.1.
- Native HA HTTPS is live at `https://192.168.20.101:8123` using
  `/ssl/fullchain.pem` and `/ssl/privkey.pem`, signed by local
  `/ssl/ca.crt` (`Home Local CA`). HTTP on port `8123` is no longer the active
  HA UI.
- `homeassistant.internal_url` is set to `https://192.168.20.101:8123`;
  `external_url` is intentionally unset.
- Mosquitto, File Editor, Terminal & SSH and ESPHome Device Builder are live.
- The Home Assist pipeline uses Home Assistant's built-in conversation agent.
- The Overwatch Assist pipeline points at `llamacpp_conversation`, a local
  Home Assistant custom conversation agent for llama.cpp's OpenAI-compatible API.
- The bounded read-only SearXNG search tool, Mealie recipe tools, and Grocy
  add/list shopping-list tools are enabled for local LLM conversation agents
  through the `llamacpp_conversation` config.
  On 2026-07-07, docker-host firewall scope was updated so HA's Supervisor
  network `172.30.32.0/23` can reach SearXNG `8087/tcp`, Grocy `9283/tcp`, and
  Mealie `9925/tcp`; HA-side API proofs returned success for those backend
  paths. The Grocy voice path is intentionally limited to adding/listing
  shopping-list items, and a live Assist spoken prompt is still required before
  certifying the conversational path end to end.
- GardenKeeper and Household Hub LLM tool integrations are live. GardenKeeper
  owns deterministic garden-state and task operations with confirmation tokens;
  Household Hub exposes authenticated read-only knowledge and recipe research.
  Both use separate HA credentials, and authenticated backend probes passed on
  2026-07-13. A spoken Assist prompt is still required to certify model tool
  selection and speech output end to end.
- Mealie is live; Overwatch-to-Mealie recipe saving is not yet implemented.
- VentSys dashboard is deployed; most physical VentSys entities remain gated on
  hardware installation.
- Repository and live HA core files, VentSys packages, mode scripts and dashboard
  have matching SHA-256 hashes. The valve contract is direct `0`/`50`, HA
  configuration validation passes, and HA restarted successfully on that source.
- Frigate integration in Home Assistant is live using Frigate API URL
  `http://192.168.30.20:5000`; all three cameras have Frigate entities and
  Advanced Camera Card CCTV views in HA.

## Frigate

- CT 111 runs Frigate 0.17.1 live on the shared Intel iGPU.
- OpenVINO detector process uses the shared Intel iGPU.
- VA-API is configured and active for camera decoding.
- Three cameras are live on VLAN 30: Camera 1 at `192.168.30.21` on switch
  port 2, Gate at `192.168.30.22` on port 4, and Patio at `192.168.30.23` on
  port 3. All three are ANNKE C500 cameras (`I51HJ`, firmware
  `v5.8.10 build 250917`), use verified RTSP main/substream paths, and sustain
  approximately `10 fps`.
- Camera RTSP auth required switching the camera from RTSP `Digest` to
  `Digest/Basic`; after that change, Frigate confirmed live ingest at roughly
  `10 fps` on the first bench camera using substream detect and mainstream
  record roles.
- Live CT 111 carries the accepted three-camera config and live
  `/opt/frigate/.env`; repository source now mirrors the three-camera layout
  with RTSP and MQTT secrets represented only as environment placeholders.
  `configs/frigate/config-baseline.yml` remains the no-camera migration-safe
  fallback.
- HA validates Frigate API version/stats and sees all three cameras through the
  Frigate integration. `/config/packages/frigate_camera_health_package.yaml`
  adds MQTT FPS sensors plus three-minute camera-offline and recovery alerts;
  alerts use persistent notifications and the tested operator mobile service.
- Frigate HTTPS UI is live on `https://192.168.30.20:8971`; auth is enabled.
  Plain HTTP to port `8971` is rejected, while HA continues to use the internal
  unauthenticated API on `http://192.168.30.20:5000`.
- On 2026-08-01, the Frigate `admin` password was recovered with the supported
  one-time `auth.reset_admin_password` flag, then changed and the flag removed
  before a final verified restart. The credential is not recorded in the
  repository. Live API checks confirmed MQTT enabled, all three camera streams
  healthy at about 8 fps, and detection enabled for the Gate and Patio cameras
  (Camera 1 detection remains disabled).
- Frigate HTTPS now uses a `Home Local CA` signed certificate mounted from
  `/opt/frigate/tls` into `/etc/letsencrypt/live/frigate`. The certificate SANs
  include `192.168.30.20`, `frigate.home.local`, `frigate-nvr`, and `frigate`.
  This replaced Frigate's generated `FRIGATE DEFAULT CERT` so trusted Android
  and Apple browsers should not show the local certificate as untrusted.
- Direct Frigate PWA access off-WiFi is live through docker-host Tailscale as a
  narrow approved `192.168.30.20/32` route with firewall access only to
  authenticated HTTPS port `8971`. A routed workstation validation on
  2026-07-29 received the expected `401` challenge from `8971`, while the
  unauthenticated API on port `5000` remained unreachable.
- Recordings now write to OMV NFS storage. Proxmox mounts
  `192.168.40.50:/export/frigate` at `/mnt/omv/frigate`, CT 111 has
  `mp0: /mnt/omv/frigate,mp=/mnt/nas/frigate`, and Frigate maps
  `/mnt/nas/frigate:/media/frigate/recordings`. The cutover was validated on
  2026-07-07 with fresh MP4 segments under
  `/mnt/nas/frigate/2026-07-07/13/cam_01_annke_c500/`.
- CT-local `/opt/frigate/storage` remains the local media root/fallback for
  non-recording data. The OMV export has an ACL for host UID `100000`, which is
  CT 111's unprivileged root mapping; without that ACL Frigate could mount the
  export but could not create dated recording folders.
- Dormant NFS client/RPC units remain disabled inside CT 111 because the CT
  does not mount NFS directly.

## Local AI

- CT 114 runs llama.cpp `server-vulkan`, a dedicated llama.cpp embedding
  service, Open WebUI, Wyoming Whisper, Piper and OpenWakeWord.
- llama.cpp serves `home-assistant-llm` from
  `Qwen3-14B-128K-Q4_K_M.gguf` at `192.168.20.104:8081/v1`; it runs with a
  `65536` token context, Q8 KV cache, reasoning disabled for normal assistant
  output, and Vulkan on Intel Meteor Lake graphics.
- The Qwen3 model file SHA-256 is
  `e6ad1ba102ef53dbc88aa59bd1bf1b10aaff298fea8f1a91f99e4312f1194c81`.
- A dedicated llama.cpp embeddings service serves `home-assistant-embedding`
  from `bge-small-en-v1.5-q8_0.gguf` at `192.168.20.104:8082/v1`; it returns
  384-dimensional embeddings and is source-scoped to docker-host for Household
  Hub.
- Live llama.cpp image digest:
  `ghcr.io/ggml-org/llama.cpp@sha256:4e784358f638549d95bd22fb814c1afeed1af71fbd4b70c25f23eae01caaa6af`.
- Whisper starts offline from persistent model/tokenizer data.
- HA can reach ports 8081, 10200, 10300 and 10400 through source-scoped
  host and Docker firewall policy. HA uses `192.168.20.104:8081/v1` for the
  llama.cpp conversation agent.
- Docker-host can reach CT 114 ports 8081, 8082 and 3002 for Household Hub
  assistant integration. Household Hub production RAG uses CT 114 chat on 8081,
  embeddings on 8082, and local Qdrant on VM 103.
- SearXNG web search is reachable at docker-host port 8087, including from Home
  Assistant after the 2026-07-07 HA Supervisor-network docker-host firewall
  update.

## Docker host

Live workloads: Bambuddy, AdGuard Home, Immich, Homepage, Dozzle,
ntfy, SearXNG, Whoogle, Mealie, Grocy, Obsidian LiveSync/CouchDB, Watchtower
monitor-only, GardenKeeper, Household Hub, Gridfinity Layout Tool, Recomp
Tracker and Telegraf.
Homepage is the central `Home Operations` navigation portal at
`https://192.168.20.102/`, using a `Home Local CA` certificate. The former
`http://192.168.20.102:3001/` endpoint remains live for rollback. Its Home,
Tools, Infrastructure, Monitoring,
Storage, Media and Operations tabs cover every user-facing portal and every
live docker-host container; Docker-backed cards expose container health and
expandable resource statistics. The header aligns the Home Operations title,
search, Portal runtime resources (the Homepage container, not host-wide CPU or
memory) and date/time, while Home starts with the reference links. Portal cards
use 50% translucent, elevated glass surfaces.
Each card also exposes a visible Preview action that opens an inline embedded
workspace below the active tab's portal cards, with working Reload, Close and
normal-link `Open tab` controls. Every configured service is attempted in the
iframe; Open tab remains the safe fallback if a target declines framing. The
workspace is a sibling immediately after the complete card grid, closes before
tab changes, is margin-bounded and acts as a splitter/work area rather than a
popup. On 2026-07-26 its responsive desktop and mobile heights were doubled,
allowing page scroll so embedded applications have substantially more working
space. Header and card surfaces use a 50% translucent dark-teal/light-teal visual system with
restrained outline shadows; the header's adaptive search fills remaining space
between the title, runtime resource widget and date/time.
On 2026-07-29 the responsive header, navigation, service-card and background
rules were repaired and visually verified at `320`, `350`, `375`, `390`,
`430`, `480`, `768`, `900`, and `1280` px. The header no longer overlaps,
narrow navigation and cards keep consistent gaps/padding, and the expanding
mobile glow was removed without removing the dark network artwork. The 390 px
embedded-workspace controls were exercised successfully.
Follow-up checks against the reported edge cases passed at exactly `956` px and
`489` px: header controls now reflow below `1230` px without search/title
encroachment, and stacked service cards have a measured `10.4` px row gap.
On 2026-07-29, Tailscale split DNS was added so the canonical
`https://homepage.home.local/` name can be used locally and remotely: OpenWrt
returns `192.168.20.102` on home WiFi, while the OnePlus tailnet client is sent
to the identity-gated AdGuard listener at `100.94.122.18`, which returns the
docker-host Tailscale address. On 2026-08-21, every user-facing Homepage card
was changed from a private-address direct link to its named fixed HTTPS proxy
(`443` or `8180`-`8209`; qBittorrent remains the fixed same-origin
`/portal-preview/qbittorrent/` route). The OnePlus grant is limited to DNS,
`tcp/443`, and `tcp/8180`-`8209` on that node; it is not a broad VLAN route.
The same card links work on home WiFi with Tailscale off because DNS resolves
the canonical name to the LAN address and the proxies are LAN-allowed.
The preview loading veil is pointer-transparent and becomes a delayed-preview
notice after six seconds, so it cannot trap the embedded UI when a service
blocks or delays iframe loading. Desktop service groups consume a single row
where space permits. Cards at 330 px or narrower grow vertically and reserve a
bottom action row; wider cards keep Preview equally inset from the top and
bottom. Hover no longer moves the action over the status indicator. Navigation
tabs now have visually distinct raised default, hover/focus and selected states.
The dock placement routine changes its parent only when Homepage replaces the
active layout. This prevents the former mutation/re-append loop that repeatedly
detached the iframe, blanked otherwise valid previews and moved controls during
pointer clicks. Household Hub and Mermaid Viewer were visibly rendered in the
live embedded workspace after the 2026-07-26 correction; Reload and Close were
also exercised successfully.
On 2026-08-09, Household Hub's workbench search authentication was repaired.
The browser no longer stores or submits the production API token; the web
container's Nginx proxy injects the existing bearer credential server-side for
same-origin `/api/` requests. Direct container-to-API requests remain protected
and returned `401`, while live recipe and YouTube searches each returned six
candidates without a browser token. The production web image build and
`nginx -t` both passed before the container was recreated.
The same 2026-08-09 maintenance updated only the frontend lockfile resolutions
for transitive `nanoid` (`3.3.18`) and `postcss` (`8.5.26`). A fresh production
build reported zero npm vulnerabilities; live health and recipe-search probes
returned `200`, and direct unauthenticated API access continued to return `401`.
Household Hub recipe review and Mealie handoff are now confirmation-gated and
durable. Reviews persist a UUID plus candidate/search provenance; imports require
that UUID and the matching source URL, reject duplicate/in-progress handoffs,
and record imported or retryable failed state. Search candidates and
assistant-extracted drafts use the same two-step workbench flow. Alembic revision
`20260809_0002` is live with an empty `recipe_workflows` table after deployment;
no live Mealie import was performed during verification.
Household Hub now also has a live read-only Grocy overview at
`GET /api/integrations/grocy/overview`. It uses a separate
`household-hub-read-only` Grocy API key and an application-enforced GET-only
client; Grocy does not provide per-key endpoint scopes, so all mutation routes
remain absent from Household Hub. The live probe returned the five seeded
locations and correctly reported empty stock and shopping lists.
The Obsidian Markdown exporter is configured at container path
`/exports/obsidian`, backed by the persistent host outbox
`/opt/stacks/household-hub/data/obsidian-exports`. This does not write directly
to Self-hosted LiveSync's plugin-managed CouchDB. A disposable recipe export
created valid Markdown and was removed after verification. The API now requires
a persisted confirmation UUID whose candidate title and source URL match the
draft; an unconfirmed live probe returned `404` and left the outbox unchanged.
Nextcloud is not
deployed and has no CalDAV credential; the workbench now exposes its valid
dry-run `VTODO`/`VEVENT` payload as a downloadable `.ics` file without claiming
live upload.
The integration deployment passed 62 backend tests, Ruff with the pre-existing
`TRY004`/`ISC004` baseline exclusions, production API/web builds, live API
smokes, desktop interaction and a 390 px mobile layout check. The mobile check
also caught and repaired a pre-existing dark-on-dark button-label override;
the final browser console had no warnings or errors.
The docker-host app-data job now includes the Household Hub Markdown outbox.
Its dry-run passed and real NAS run `20260809T130054Z` completed successfully,
capturing the new Grocy key state and creating
`latest/household-hub-exports`.
A fixed-target `homepage-preview-proxy` Nginx sidecar is live on docker-host.
It terminates HTTPS on the LAN and Tailscale addresses at `443`; HTTPS preview
ports `8180`-`8209` are
host-firewall scoped to the established management,
LAN, automation and Tailscale sources; it cannot proxy arbitrary destinations.
GardenKeeper, Bambuddy and Whoogle visibly load through it after their upstream
frame-denial headers are replaced with portal-scoped CSP. On 2026-07-26, the
source- and port-scoped OpenWrt rules were deployed and Proxmox, OpenWrt, Zyxel
and OMV proxy listeners were verified from docker-host (`200`). Router LuCI
requires a separate INPUT rule because traffic addressed to OpenWrt itself is
not an inter-zone forward. The OpenWrt `3000/3001` forwarding rule is live.
The monitoring VM now permits only docker-host `192.168.20.102` to its Grafana
`3000/tcp` and Uptime Kuma `3001/tcp` published ports. Matching `DOCKER-USER`
returns are applied by the enabled `monitoring-firewall.service`, so Docker's
forwarding path remains restricted after reboot.
Home Assistant now loads its login UI through HTTPS preview `8188`, with the
upstream local-CA certificate verified and WebSocket upgrade preserved. The
direct `8123` login cookie is not shared with this distinct origin, so the first
embedded visit requires a normal one-time HA login. GardenKeeper and Mermaid
Viewer were also visibly rendered through the HTTPS portal, and Reload/Close
were exercised successfully.
Frigate, Proxmox, OpenWrt, Zyxel, Grafana, Uptime Kuma, OMV and Transfer Portal
all have Homepage health sources and render a status dot. Frigate, OpenWrt,
Zyxel, OMV and Transfer Portal were visibly healthy after revalidation;
Proxmox uses the fixed-target proxy health endpoint because ICMP from the
Homepage container was not reliable. Docker-host UFW permits the Homepage
bridge `172.18.0.0/16` to reach only gateway port `8299/tcp` for this check;
the rebuild rule is tracked in `docker-host-ufw-homepage-previews.sh`. Grafana
and Uptime Kuma return through HTTPS preview proxy ports `8202` and `8186`
respectively; their Homepage status dots are healthy.
Its local network SVG now has a slow background and ambient-glow drift; both
animations are disabled for `prefers-reduced-motion`.
Mermaid Viewer is live at `http://192.168.20.102:8092/` and is generated from
the 11 canonical project diagrams. It supports search, deep links, pan, zoom,
fit, 100% view, fullscreen, source inspection and an adaptive full-width
layout in both direct and embedded views. Its dark canvas, controls and panels
use elevated glass surfaces over a subtle technical grid and network glow.
GardenKeeper and Household Hub have matching subject-specific backgrounds and
the same raised-glass card/button treatment; their reusable source layers are
in `apps/custom-site-themes/`. The Transfer Portal source has the matching
style prepared but is not deployed until OMV management access is restored.
The portal uses only non-secret configuration and remains an internal/Tailscale
surface rather than an authentication boundary.
Gridfinity Layout Tool (`gridfinity-layout-tool-v4.342.0`) is live at
`http://192.168.20.102:8093`; its
`gridfinity.home.local` DNS source is staged but not yet router-deployed. It
serves a pinned externally built static release through Nginx on the fixed
`172.32.0.0/24` Docker subnet, avoiding the prior overlapping automatic bridge
allocation. A Windows per-user 09:00 daily autodeploy checks the locally
recorded release, builds a newer upstream tag externally, and uses the atomic
health-checked deployment/rollback workflow in
`docs/install/services/gridfinity-layout-tool.md`.
Recomp Tracker is live at `http://192.168.20.102:8420` for personal habits and
workout tracking, with the fixed Homepage HTTPS proxy at
`https://homepage.home.local:8209/` for portal navigation. Its source is tracked in
`configs/docker-host/stacks/recomp-tracker/`, its Docker bridge is explicitly
allocated as `10.240.31.0/24`, and its firewall permits only management, LAN
and Tailscale sources. Its HTTP endpoint returned `200` during the 2026-08-19
reachability recheck.
VM 103 has a 64 GiB virtual disk and 6 GiB RAM. On 2026-07-13 both app stacks were rebuilt from verified source,
their scoped HA credentials were rotated, the Hub database was baselined at
Alembic revision `20260617_0001`, and authenticated assistant probes passed.

2026-07-05 docker-host guest-agent check:

- Root filesystem: `63G` total, `37G` used, `24G` available (`62%`).
- Immich OMV mount is present at `/mnt/omv/immich`
  (`192.168.40.50:/export/immich`, NFSv3).
- Mealie returned `HTTP/1.1 200 OK` on `127.0.0.1:9925`.
- Grocy returned `HTTP/1.1 302 Found` on `127.0.0.1:9283`; its local API
  returned HTTP `200` with the dedicated HA voice key on 2026-07-07.
- Obsidian LiveSync/CouchDB returned `HTTP/1.1 401 Unauthorized` on
  `127.0.0.1:5984`.

Immich now uses the OMV-backed NFS mount at `/mnt/omv/immich` for uploads and
library storage. Its database remains local under `/opt/stacks/immich/postgres`.
Mealie, Grocy, Obsidian LiveSync, and GardenKeeper now have documented
app-data or dump backup source paths targeting OMV `backups/docker-host`. A
read-only docker-host check on 2026-07-06 confirmed the source directories
exist: Mealie `15M`, Grocy `4.2M`, LiveSync `152K`, and GardenKeeper local
dumps `36K`. Proxmox confirmed OMV exports `backups/docker-host` to
`192.168.20.102`.

On 2026-07-07, the live OpenWrt `Docker Host to OMV NFS` rule was deployed,
docker-host mounted the OMV export at `/mnt/omv/docker-host-backups` using
NFSv3, and the first real app-data backup run `20260706T231304Z` wrote `20M`
under `runs/` while updating `latest/`. Restore smoke copied `latest/` to a
temporary directory, verified Mealie `mealie.db`, Grocy `grocy.db`, LiveSync
shards, and a GardenKeeper compressed SQL dump, then removed the temp copy.
`docker-host-app-data-backup.timer` is enabled and active for daily `03:45`
local runs. After the Grocy voice API key was added, backup run
`20260707T132647Z` completed and updated `latest/` to `22M`.

On 2026-07-29 OMV gained a dedicated `media` export for the populated
`14tb/Media` tree, restricted to docker-host `192.168.20.102`. Docker-host
mounts it at `/mnt/omv/media` with a persistent systemd automount. The dedicated
`media-service` identity (`1007:100`) passed create/read/delete validation in
the new isolated library and staging roots; no legacy media path was changed.

The first media foundation is live on docker-host:

- Jellyfin `10.11.11` on `8096/tcp`, with films, series, music and the future
  `immich-curated` export mounted read-only; hardware transcoding is disabled.
- Calibre-Web on `8083/tcp`, with write access only to
  `books/calibre-library`.
- Atsumeru on `31337/tcp`, with write access only to
  `comics/atsumeru-library` and local application state.

Each stack has a source-scoped UFW/`DOCKER-USER` policy, a restart proof and a
non-overlapping explicit Docker subnet (`10.240.10.0/24` through
`10.240.12.0/24`). This is mandatory: the first Jellyfin Compose attempt
automatically chose `192.168.0.0/20`, overlapping the management VLAN and
temporarily removing VM 103 management reachability. The stack was stopped,
routes recovered and every new stack was assigned explicit `10.240.x.0/24`
IPAM before deployment resumed.

Controlled remediation on 2026-08-21 recreated every project bridge at its
canonical explicit allocation and name, including Household Hub's shared
SearXNG/Mealie/Grocy dependencies and the four-consumer `local-alerting`
network. All application, storage, dependency, VPN-egress and firewall checks
passed. The persistent firewall covers Bambuddy port `8000` on IPv4 and IPv6,
and the Bambuddy routed-UFW policy and empty `10.240.23.0/24` bridge are ready;
the Bambuddy container itself remains on host networking because the P1S ports
are currently unreachable from VM 103. This is the sole failing assertion in
the live security audit and the only remaining remediation step.

Vaultwarden `1.36.0` is live with its raw HTTP listener bound only to
`127.0.0.1:8222`. Production access is through the fixed Nginx proxy at
`https://vault.home.local` using a dedicated local-CA certificate, HSTS and a
no-framing policy. Sign-ups and the admin endpoint remain disabled. A
SQLite-consistent NAS backup passed two isolated restore exercises, including a
disposable registered account restored into a second temporary container with
database integrity, exact-account-count and HTTP health checks. Owner onboarding,
2FA/recovery and emergency-access policy remain gated on live local DNS.
Backup run `20260729T160804Z` added Jellyfin, Calibre-Web, Atsumeru, ntfy and
Vaultwarden application state to the existing NAS job; the restored Vaultwarden
database passed `PRAGMA integrity_check` before the disposable proof was removed.

The Mullvad/Gluetun + qBittorrent gateway is live on `8084/tcp` with explicit
Docker subnet `10.240.20.0/24`. qBittorrent shares Gluetun's network namespace,
uses NAS-backed `/downloads/incomplete` and `/downloads/complete`, and cannot see
quarantine or any final media/book/document library. Mullvad recognized the
tunnel and its public route differed from the host. Dropping Gluetun's `tun0`
interface blocked qBittorrent public egress while the Web UI and host egress
remained available; automatic tunnel recovery then passed. The stronger full
provider-stop test also failed closed while host and unrelated-container egress
continued. Its permanent Web UI credential is in Windows Credential Manager as
`home-automation/qbittorrent`. NAS backup run `20260801T144643Z` passed an
isolated restore proof for the credential hash and both download paths.

The controlled docker-host package window completed on 2026-08-01: Docker CE
and CLI `29.7.1`, containerd `2.2.6`, Buildx `0.36.0`, Compose `5.3.1`, Python
`3.13.5-2+deb13u4`, and Tailscale `1.98.10` were installed. No reboot was
required, no package remained upgradable, `dpkg --audit` was clean, all 33
pre-existing containers remained running, both OMV mounts were present and all
tested local/monitoring endpoints passed.

The 2026-07-29 VM reboot exposed an AdGuard/Tailscale boot race: Docker tried to
bind `100.94.122.18:53` before `tailscale0` owned the address, leaving AdGuard
half-created without port bindings. The enabled
`adguard-home-compose.service` now waits for the Tailscale address and force-
recreates the Compose stack. Local and Tailscale DNS listeners plus the UI were
revalidated after installation.

Paperless-ngx, Actual Budget, Scrypted, Portainer, a local
registry mirror and Node-RED remain decision-gated candidates.

## Monitoring

- Uptime Kuma, InfluxDB, Grafana and Telegraf are live on VM 102.
- Proxmox, HA, docker-host, DNS, core apps and local-AI endpoints are monitored.
- Alert routing through ntfy exists for configured Kuma monitors. Grafana also
  uses an authenticated `ntfy Monitoring` webhook as its default notification
  policy; a live Grafana test notification succeeded on 2026-07-29.
- On 2026-07-29, stale Kuma checks were repaired for HA native HTTPS and the
  llama.cpp models API. New ntfy-enabled checks for OMV web, OMV NFS, and all
  three camera hosts are live and `Up`.
- OpenWrt now permits only monitoring VM `192.168.60.10` to Frigate API TCP
  `5000`, OMV TCP `80`/`2049`, and ICMP for camera hosts `.21`-.23. The OMV and
  camera checks pass. CT 111 now also allows the monitoring VM to Frigate API
  TCP `5000`; a direct monitoring-VM probe and Kuma monitor 28 both returned
  HTTP `200` on 2026-08-01.
- Kuma monitor 34 and the OMV `smartctl -H` heartbeat service/timer are live for
  aggregate disk-health reporting. The 30-minute timer uses a host-only token
  file and narrow OMV-to-Kuma network path; the first accepted heartbeat on
  2026-07-29 reported `All 5 physical disks report healthy`.
- Kuma monitor 36 tracks docker-host app-data backup freshness with a 25-hour
  push window. The existing backup service invokes its host-only-token producer
  in `ExecStartPost`, so a heartbeat is sent only after a successful backup;
  the first `Docker-host app-data backup completed` heartbeat was accepted on
  2026-08-01.
- Grafana 13.0.1 has two initial metric alerts in `Infrastructure health`:
  docker-host root disk and Proxmox root storage, each warning above 85% for
  10 minutes. Both evaluated `Normal` after creation. The reset Grafana admin
  credential is stored in Windows Credential Manager under
  `home-automation/grafana`; it is not stored in this repository.
- ntfy has a separate read-only `mobile-monitoring` account for the `monitoring`
  and `watchtower` topics. Its generated credential is stored in Windows
  Credential Manager under `home-automation/ntfy-mobile`. Mobile access is
  Tailscale Serve HTTPS at `https://docker-host.tail7012a0.ts.net`; the
  Homepage proxy binds both its LAN and Tailscale address on port 443; Tailscale
  Serve continues to own its separate MagicDNS endpoint.
- The live docker-host app-data job now snapshots ntfy's `user.db` and
  `cache.db` through SQLite's backup API. A fresh NAS run and temporary restore
  smoke on 2026-07-29 passed integrity checks for both databases.
- OMV NFS TCP 2049 and Proxmox storage pressure are checked by
  `home-automation-health-check.timer`. Backup storage is intentionally on md0;
  the old 86-87% high-water warning was cleared by the 2026-07-05 Proxmox
  check showing `omv-backups` active at 54.21% used.
- OMV SMART monitoring is globally enabled with a 1,800-second check interval,
  a 5 C change threshold and a 55 C maximum alert. Monitoring is enabled on all
  five physical disks (`/dev/sda` through `/dev/sde`); all reported `Good` on
  2026-07-29 at 33-44 C. No new SMART self-test schedule was added.

## Backup storage

- OMV is live on Storage VLAN 40 at `192.168.40.50`.
- Final backup storage lives on md0 at
  `/srv/dev-disk-by-uuid-fdb92af7-371c-4793-8d98-ff47e961498d/backups/`.
- Frigate/NVR recordings target md0 at
  `/srv/dev-disk-by-uuid-fdb92af7-371c-4793-8d98-ff47e961498d/CCTV/`.
- OMV exports NFS paths for Proxmox backups, HA backups, docker-host backups,
  config backups, Immich DB backups, Immich media, and Frigate/NVR recordings.
- `scripts/backup/backup_vault_to_nas.ps1` provides a guarded, additive
  robocopy helper for the project vault. Its default dry run against
  `\\192.168.40.50\NAS\configs\home-automation-project` enumerated about 11,700
  files (229 MB) successfully on 2026-07-29. No scheduled vault-backup task has
  been created; first execution and restore proof remain approval-gated.
- The Frigate export is mounted on the Proxmox host and bind-mounted into CT
  111 for recordings. CT 111 remains unprivileged and must not mount NFS
  directly.
- Home Assistant previously had Supervisor backup mount `nas_backups` pointing
  at `192.168.40.50:/srv/dev-disk-by-uuid-fdb92af7-371c-4793-8d98-ff47e961498d/backups/home-assistant`;
  manual backup `manual-nfs-md0-test-20260626` (`8294da47.tar`, 69 MiB) wrote
  successfully to OMV. During the 2026-07-02 HA native HTTPS cutover,
  `ha mounts info` reported no active mounts; this was resolved on 2026-07-03
  by restoring `nas_backups` and proving fresh writes. The pre-TLS HA backup was
  created locally as `pre-ha-native-tls-20260702-db-excluded`, slug `04da1c7d`.
- On 2026-07-03, the Zyxel GS1900-8HP was moved from the temporary VLAN 30
  bench posture to the intended managed-switch layout: router `lan3` is a
  tagged trunk for VLANs 1/10/30/40, switch management is on VLAN 10 at
  `192.168.10.12`, the first camera is on untagged VLAN 30 port 2, and OMV is
  on untagged VLAN 40 port 8. Router ARP confirmed OMV at
  `a8:b8:e0:0a:93:7d` on VLAN 40. The GS1900 Save action was invoked after
  the cutover and the switch remained reachable at `192.168.10.12`.
- On 2026-07-28, switch ports 2-7 were standardized as PoE CCTV access ports:
  VLAN 30 untagged, PVID 30, and excluded from VLANs 1/10/40. Port 1 remains
  the tagged router trunk and port 8 remains the NAS access port with PVID 40.
  The change was saved to switch startup configuration. Live validation showed
  cameras on ports 2-4 at approximately 10 fps, including recovery of the gate
  camera at `192.168.30.22` after correcting port 4 and cycling only its PoE.
- HA Supervisor mount `nas_backups` is active again and set as the default
  backup mount. Manual backup
  `post-switch-trunk-nas-backups-20260703-db-excluded`, slug `3e3b1ecb`,
  wrote successfully to `nas_backups` (102.01 MiB).
- Fresh post-cutover proof on 2026-07-03 confirmed `nas_backups` still active,
  writable, and default. Manual backup
  `post-cutover-nas-backups-proof2-20260703-db-excluded`, slug `db7946c4`,
  wrote to `nas_backups` with `homeassistant_exclude_database: true`
  (81.51 MiB).
- HA automatic backups are configured for daily `03:00`, retained by count
  with `14` copies, and targeted only at `nas_backups`
  (`hassio.nas_backups`). The backup manager storage file was copied to
  `/config/.storage/backup.pre-auto-schedule-20260703-145639` before the
  direct storage edit and HA Core restart.
- Proxmox storage `omv-backups` uses NFSv3 to
  `/srv/dev-disk-by-uuid-fdb92af7-371c-4793-8d98-ff47e961498d/backups/proxmox`.
  It was active on 2026-07-05: `pvesm status` reported total
  `15501464576 KiB`, used `8403021824 KiB`, available `7098426368 KiB`
  (`54.21%`), and `df -h /mnt/pve/omv-backups` showed about `15T` total,
  `7.9T` used and `6.7T` available.
- Daily jobs cover VMs 100/102/103 at 02:00 and CTs 111/114 at 04:00, snapshot
  mode, ZSTD, `keep-daily=7`, and `keep-monthly=6`.
- A manual VM 102 backup to `omv-backups` completed on 2026-06-26. Scheduled
  VM backups for 100, 102 and 103 completed again on 2026-07-05.
- The 2026-07-05 scheduled CT 111/114 backups initially failed because the
  unprivileged LXC backup process could not enter the NFS-backed temporary dump
  directory. The CT backup job
  `a8c84d38-2a73-4d9d-bf34-111114000001` now has `tmpdir: /var/tmp`; a manual
  CT 111 backup using that setting produced
  `vzdump-lxc-111-2026_07_05-23_11_08.tar.zst` (`23G`) on `omv-backups`.
  A manual CT 114 backup using the same setting then completed on 2026-07-06:
  `vzdump-lxc-114-2026_07_06-00_13_59.tar.zst`, archive size `15.30GB`,
  finished in `00:23:30`, with the temporary snapshot removed successfully.
  Proxmox warned that thin-pool autoextend protection is not enabled and that
  summed thin volume sizes exceed pool capacity; keep watching `local-lvm`
  pressure before large guest growth.
- Fresh VM 102 and CT 114 archives passed `zstd -t` on 2026-06-22. VM 102 also
  passed an isolated no-NIC restore/boot/guest-agent drill under temporary ID
  9102, which was purged after validation.
- Existing local archives remain retained during the transition.

## Not built or not production-ready

- Frigate expansion beyond the three live ANNKE cameras, including any fourth
  camera, remaining motion/zone tuning, and later AI-rule decisions.
- Most VentSys physical hardware, remaining ESPHome adoption and full safety
  acceptance testing.
- P1S details and HA Bambuddy package deployment.
- Same-origin HTTPS/reverse proxy for embedded monitoring views. HA native
  HTTPS is live, but Grafana/Kuma remain direct HTTP links rather than embedded
  iframes.
- Overwatch-to-Mealie recipe ingestion live prompt validation and remaining
  Grocy pilot product workflow testing.
- Obsidian LiveSync client wizard and second-device rollout; backend database,
  CORS preflight, local plugin install, backup proof, and Tailscale Serve
  mapping are live, but the admin laptop did not resolve the tailnet hostname
  during the 2026-07-07 check.

## Rollback and backup warning

Migration snapshots named `pre-lxc-migration-20260620` exist for retired VM 101
and VM 104. Daily Proxmox jobs now retain 7 daily and 6 monthly generations on
`omv-backups`; projected retention fits the current md0-backed storage after
the 2026-07-05 capacity check, and both CT 111 and CT 114 have manual successful
proof after the `tmpdir=/var/tmp` change. Consult
`scripts/backup/backup_strategy.md`.
