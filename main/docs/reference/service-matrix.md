---
title: Service Matrix
description: Central service, port, DNS, backup, monitoring, and runbook reference
tags: [reference, services, ports, dns, docker-host]
created: 2026-05-23
modified: 2026-07-16
type: reference
status: active
---

# Service Matrix

This matrix is the canonical place to track service placement, ports, URLs,
remote exposure, backup expectations, monitoring, and runbook coverage.

## Core infrastructure

| Service | Host | IP / VLAN | Port(s) | Local URL / DNS | Tailscale exposure | Backup / data | Monitoring | Runbook |
|---|---|---:|---|---|---|---|---|---|
| OpenWrt router | GL-MT6000 | `192.168.10.1` / VLAN 10 mgmt; `192.168.1.1` / LAN | 80/443, 22 | `router.home.local` resolves to `192.168.1.1`; management uses `192.168.10.1` directly | No daily exposure; WireGuard fallback endpoint on WAN | router-deploy source + generated artifacts | ping, DNS, firewall tests | `docs/troubleshooting/troubleshooting_reference.md` |
| Proxmox | MINISFORUM M1 Pro-125H | `192.168.10.10` / VLAN 10 | 8006, 22 | `proxmox.home.local` | Not advertised | NFS storage `omv-backups` -> md0 `backups/proxmox`; VMs 100/102/103 daily 02:00, CTs 111/114 daily 04:00; keep 7 daily + 6 monthly | Uptime Kuma plus five-minute host health timer | `scripts/setup/proxmox/proxmox_setup_guide.md` |
| Home Assistant | VM 100 | `192.168.20.101` / VLAN 20 | 8123, 8883 MQTT | `homeassistant.home.local` | `192.168.20.101/32` via docker-host | HA backup mount `nas_backups` -> md0 `backups/home-assistant`; default backup mount active | Uptime Kuma, HA checks | `scripts/setup/proxmox/ha_vm_setup_guide.md` |
| Frigate | CT 111 (unprivileged LXC) | `192.168.30.20` / VLAN 30 | 8971, 5000, 8554, 8555 | `frigate.home.local` | Not advertised | local baseline; OMV archive later | container/API baseline; camera monitors after hardware | `scripts/setup/proxmox/frigate_vm_setup_guide.md` |
| Monitoring stack | VM 102 | `192.168.60.10` / VLAN 60 | 3000 Grafana, 3001 Uptime Kuma, 8086 InfluxDB | `grafana.home.local:3000`, `uptime-kuma.home.local:3001`, `influxdb.home.local:8086` | Host route `192.168.60.10/32` advertised via docker-host for Grafana/Kuma only; do not expose InfluxDB | stack config + Influx backups | Uptime Kuma self-monitor plus HA-side external health sensors | `scripts/setup/proxmox/monitoring_vm_setup_guide.md` |
| Docker host | VM 103 | `192.168.20.102` / VLAN 20 | 22 plus service ports | `docker-host.home.local` | Tailscale node identity / MagicDNS | `/opt/stacks/<service>/`; app-data backup timer copies selected household app data to OMV `backups/docker-host` daily at `03:45` | Uptime Kuma, Dozzle | `scripts/setup/proxmox/docker_host_setup_guide.md` |
| Local AI inference | CT 114 (unprivileged LXC) | `192.168.20.104` / VLAN 20 | 8081, 8082, 3002, 10200, 10300, 10400 | `llm-host.home.local`, `openwebui.home.local` | Not advertised by default; source-scoped host and Docker firewall rules | `/opt/stacks/local-ai/`; `Qwen3-14B-128K-Q4_K_M.gguf` served as `home-assistant-llm`, `bge-small-en-v1.5-q8_0.gguf`, and voice data local to CT 114 | Uptime Kuma should check llama.cpp chat, Open WebUI, Piper, Whisper and OpenWakeWord; embedding endpoint is currently source-scoped to docker-host | `scripts/setup/proxmox/llm_host_setup_guide.md`, `docs/procedures/local_ai_performance_testing.md` |
| OMV NAS | NAS hardware | `192.168.40.50` / VLAN 40 storage | 80, 22, 445, 2049, NFS helper ports 111/20048/32765-32767 | `OMVNAS`; web UI at `http://192.168.40.50/`, `omv.home.local`, `nas.home.local` | not advertised as a broad storage route | md0 `backups/` hierarchy, md0 `CCTV/` Frigate recording share, Immich media NFS, SMART, OMV config backup | ping, web UI, SMART, NFS checks; docker-host Telegraf sees `/mnt/omv/immich` | `scripts/setup/nas/omv_nas_setup_guide.md` |
| OMV Transfer Portal | OMVNAS native service | `192.168.40.50` / VLAN 40 storage | 8088 | `transferportal.home.local:8088` | none in v1 | `/var/lib/transferportal/jobs.sqlite`, `/etc/transferportal/config.yaml`, `/var/log/transferportal/` | systemd status, audit log, job log tail | `docs/install/services/transferportal.md` |

## Docker-host Tier 1

| Service | Stack path | Port(s) | Local URL / DNS | Tailscale exposure | Data / backup | Monitoring | Runbook |
|---|---|---|---|---|---|---|---|
| Tailscale | host service | 41641/udp outbound, 443 outbound | docker-host MagicDNS | Node identity; advertises `192.168.20.101/32`, `192.168.40.50/32`, `192.168.60.10/32` | no auth keys in repo | `tailscale status`, route approval | `docs/install/phases/05-docker-host.md` |
| AdGuard Home | `/opt/stacks/adguard-home/` | 53/tcp+udp, 3000 initial, 8080 admin target | `adguard.home.local` | Admin via docker-host Tailscale identity only if ACL allows | config/work dir under stack path | DNS query test + UI | `docs/install/services/adguard-home.md` |
| Immich | `/opt/stacks/immich/` | 2283/tcp | `immich.home.local` | Via docker-host Tailscale identity / MagicDNS | uploads/library on OMV NFS mount `/mnt/omv/immich`; database local at `/opt/stacks/immich/postgres` | Uptime Kuma HTTP check; docker-host Telegraf disk metric for OMV mount | `docs/install/services/immich.md` |
| Homepage | `/opt/stacks/homepage/` | 3001/tcp | `homepage.home.local` | Via docker-host Tailscale identity / MagicDNS | config directory | HTTP check | `docs/install/services/homepage.md` |
| Dozzle | `/opt/stacks/dozzle/` | 8081/tcp | `dozzle.home.local` | Admin only via Tailscale/Mgmt/LAN policy | no critical data | HTTP check | `docs/install/services/dozzle.md` |
| Bambuddy | `/opt/stacks/bambuddy/` | 8000/tcp | `bambuddy.home.local` | Via docker-host Tailscale identity / MagicDNS if needed | app data/logs under stack path | HTTP + MQTT status | `scripts/setup/proxmox/bambuddy_vm_setup_guide.md` |
| ntfy | `/opt/stacks/ntfy/` | 8085/tcp | `ntfy.home.local` | Via docker-host Tailscale identity / MagicDNS | config/auth DB under stack path; credentials in Bitwarden | Uptime Kuma HTTP check | `docs/install/services/ntfy.md` |
| Mealie | `/opt/stacks/mealie/` | 9925/tcp | `mealie.home.local:9925` | Via docker-host Tailscale identity | SQLite data under `/opt/stacks/mealie/data`; include in docker-host app-data backup to OMV `backups/docker-host` | Uptime Kuma HTTP check | `docs/install/services/mealie.md` |
| Grocy | `/opt/stacks/grocy/` | 9283/tcp | `grocy.home.local:9283` | Via docker-host Tailscale identity | config/database under `/opt/stacks/grocy/config`; base household model seeded; HA Assist has add/list shopping-list API access through dedicated Grocy key; docker-host app-data backup copies it to OMV `backups/docker-host` | Uptime Kuma HTTP check | `docs/install/services/grocy.md` |
| Obsidian LiveSync | `/opt/stacks/obsidian-livesync/` | 5984/tcp; Tailscale HTTPS 8443 | `obsidian-sync.home.local:5984` | `docker-host.tail7012a0.ts.net:8443` after Serve approval | CouchDB data under `/opt/stacks/obsidian-livesync/data`; Git remains version history; backend/CORS/local plugin ready; docker-host app-data backup copies data to OMV | Uptime Kuma HTTP auth check | `docs/install/services/obsidian-livesync.md` |
| GardenKeeper | `/opt/stacks/gardenkeeper/` | 8091/tcp UI, 8090/tcp API | `gardenkeeper.home.local:8091` | Via docker-host Tailscale identity | Local Postgres dump timer writes `/opt/stacks/gardenkeeper/backups`; docker-host app-data backup copies dumps to OMV `backups/docker-host` | Uptime Kuma HTTP checks for UI and `/health` | `docs/install/services/gardenkeeper.md` |
| Household Hub | `/opt/stacks/household-hub/` | 8100/tcp workbench and reverse-proxied API | `household-hub.home.local:8100` | Via docker-host Tailscale identity after ACL approval | PostgreSQL, Redis, and Qdrant volumes; scoped HA read-only credential | API status plus authenticated HA assistant probes | Household Hub repository deployment docs |
| Mermaid Viewer | `/opt/stacks/mermaid-viewer/` | 8092/tcp | `mermaid-viewer.home.local:8092` | Via docker-host Tailscale identity after ACL approval | stateless utility | HTTP check | `apps/mermaid-viewer/README.md` |
| Gridfinity Layout Tool | `/opt/stacks/gridfinity-layout-tool/` | 8093/tcp | `http://192.168.20.102:8093` (DNS source staged for `gridfinity.home.local:8093`) | Management, LAN, and docker-host Tailscale identity | stateless browser-local utility; no server-side data | container health and HTTP `/healthz` check | `docs/install/services/gridfinity-layout-tool.md` |
| SearXNG | `/opt/stacks/searxng/` | 8087/tcp | `searxng.home.local:8087` | Via docker-host Tailscale identity after ACL approval | stack config | HTTP/search API check | `docs/install/services/searxng.md` |
| Whoogle | `/opt/stacks/whoogle/` | 8088/tcp | `whoogle.home.local:8088` | Via docker-host Tailscale identity after ACL approval | stack config | HTTP check | `docs/install/services/whoogle.md` |
| Watchtower monitor-only | `/opt/stacks/watchtower/` | none | no DNS alias; no user-facing listener | none | no critical data | container state/logs | stack config |
| apt-cacher-ng | host service | 3142/tcp | `apt-cacher-ng.home.local:3142` | none | package cache | service/listener check | `docs/procedures/apt_cacher_ng_design.md` |

## Docker-host roadmap

| Tier | Service | Suggested stack path | Default / planned port | Notes |
|---|---|---|---|---|
| Tier 2 | Paperless-ngx | `/opt/stacks/paperless-ngx/` | 8001 | `docs/install/services/paperless-ngx.md` |
| Tier 2 | ntfy | `/opt/stacks/ntfy/` | 8085 | Pre-flight live internal-only; `docs/install/services/ntfy.md` |
| Tier 2 | Actual Budget | `/opt/stacks/actual-budget/` | 5006 | `docs/install/services/actual-budget.md`; sensitive data gate |
| Tier 2 | Scrypted | `/opt/stacks/scrypted/` | 10443 / 11080 | `docs/install/services/scrypted.md`; placement gate |
| Tier 3 | Vaultwarden | `/opt/stacks/vaultwarden/` | 8082 | `docs/install/services/vaultwarden.md`; security gate |
| Tier 3 | Portainer | `/opt/stacks/portainer/` | 9443 | `docs/install/services/portainer.md`; socket exposure gate |
| Tier 3 | local registry mirror | `/opt/stacks/registry-mirror/` | 5000 | `docs/install/services/local-registry-mirror.md`; daemon rollback gate |
| Tier 3 | Node-RED | `/opt/stacks/node-red/` | 1880 | `docs/install/services/node-red.md`; HA-native automation gate |
| Future | AI-adjacent query apps | `/opt/stacks/<service>/` | TBD | VM 103 is the expected target for future containerized query apps; define app-specific API, egress, storage, monitoring, and firewall rules before deployment |

## DNS aliases

OpenWrt dnsmasq is authoritative for `home.local`; AdGuard is an upstream
filtering resolver and intentionally has no local rewrites. Service aliases map
to hosts, so URLs must retain the listed non-default port. Internal-only
Compose services such as PostgreSQL, Redis, Qdrant, machine-learning helpers,
workers, and databases use Compose DNS only and do not receive LAN aliases.

| Name | IP | Notes |
|---|---:|---|
| `lan.home.local` | `192.168.1.1` | LAN gateway |
| `management.home.local` | `192.168.10.1` | Management gateway |
| `automation.home.local` | `192.168.20.1` | Automation gateway |
| `nvr.home.local` | `192.168.30.1` | NVR gateway |
| `printers.home.local` | `192.168.35.1` | Printers gateway |
| `storage.home.local` | `192.168.40.1` | Storage gateway |
| `iot.home.local` | `192.168.50.1` | IoT gateway |
| `monitoring.home.local` | `192.168.60.1` | Monitoring gateway; not the monitoring VM |
| `dmz.home.local` | `192.168.70.1` | DMZ gateway |
| `guest.home.local` | `192.168.99.1` | Guest gateway |
| `router.home.local` | `192.168.1.1` | OpenWrt router user-facing alias |
| `proxmox.home.local` | `192.168.10.10` | Proxmox UI on 8006 |
| `docker-host.home.local` | `192.168.20.102` | VM 103 |
| `homeassistant.home.local` | `192.168.20.101` | HA HTTPS UI on 8123 |
| `mqtt.home.local` | `192.168.20.101` | Mosquitto TLS on 8883 |
| `adguard.home.local` | `192.168.20.102` | AdGuard Home UI/DNS host |
| `immich.home.local` | `192.168.20.102` | Immich UI |
| `homepage.home.local` | `192.168.20.102` | Homepage UI |
| `dozzle.home.local` | `192.168.20.102` | Dozzle UI |
| `bambuddy.home.local` | `192.168.20.102` | Bambuddy UI |
| `ntfy.home.local` | `192.168.20.102` | ntfy UI/API |
| `apt-cacher-ng.home.local` | `192.168.20.102` | apt-cacher-ng on 3142 |
| `searxng.home.local` | `192.168.20.102` | Live SearXNG UI/API on 8087 |
| `whoogle.home.local` | `192.168.20.102` | Live Whoogle UI on 8088 |
| `mealie.home.local` | `192.168.20.102` | Mealie recipe and meal-planning UI |
| `grocy.home.local` | `192.168.20.102` | Grocy food-stock UI |
| `obsidian-sync.home.local` | `192.168.20.102` | CouchDB backend for Obsidian LiveSync |
| `gardenkeeper.home.local` | `192.168.20.102` | GardenKeeper garden care app |
| `household-hub.home.local` | `192.168.20.102` | Household Hub workbench/API proxy on 8100 |
| `mermaid-viewer.home.local` | `192.168.20.102` | Mermaid Viewer on 8092 |
| `gridfinity.home.local` | `192.168.20.102` | DNS source staged; Gridfinity Layout Tool on 8093 after router DNS deployment |
| `llm-host.home.local` | `192.168.20.104` | CT 114 local AI host |
| `openwebui.home.local` | `192.168.20.104` | Open WebUI host |
| `llama.home.local` | `192.168.20.104` | llama.cpp chat endpoint on 8081 |
| `embeddings.home.local` | `192.168.20.104` | llama.cpp embedding endpoint on 8082 |
| `piper.home.local` | `192.168.20.104` | Wyoming Piper on 10200 |
| `whisper.home.local` | `192.168.20.104` | Wyoming Whisper on 10300 |
| `openwakeword.home.local` | `192.168.20.104` | Wyoming OpenWakeWord on 10400 |
| `frigate.home.local` | `192.168.30.20` | Frigate HTTPS UI on 8971 |
| `p1s.home.local` | `192.168.35.200` | Bambu Lab P1S printer |
| `athena2.home.local` | `192.168.35.201` | Athena 2 printer |
| `omv-nas.home.local` | `192.168.40.50` | OMV hostname |
| `omv.home.local` | `192.168.40.50` | OMV convenience alias |
| `nas.home.local` | `192.168.40.50` | Storage convenience alias |
| `transferportal.home.local` | `192.168.40.50` | Transfer Portal on 8088 |
| `grafana.home.local` | `192.168.60.10` | Grafana on 3000 |
| `uptime-kuma.home.local` | `192.168.60.10` | Uptime Kuma on 3001 |
| `influxdb.home.local` | `192.168.60.10` | InfluxDB on 8086; not remotely exposed |
