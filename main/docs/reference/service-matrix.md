---
title: Service Matrix
description: Central service, port, DNS, backup, monitoring, and runbook reference
tags: [reference, services, ports, dns, docker-host]
created: 2026-05-23
modified: 2026-06-26
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
| Monitoring stack | VM 102 | `192.168.60.10` / VLAN 60 | 3000, 3001, 8086 | monitoring dashboard links in HA | Host route `192.168.60.10/32` advertised via docker-host for Grafana/Kuma only; do not expose InfluxDB | stack config + Influx backups | Uptime Kuma self-monitor plus HA-side external health sensors | `scripts/setup/proxmox/monitoring_vm_setup_guide.md` |
| Docker host | VM 103 | `192.168.20.102` / VLAN 20 | 22 plus service ports | `docker-host.home.local` | Tailscale node identity / MagicDNS | `/opt/stacks/<service>/` | Uptime Kuma, Dozzle | `scripts/setup/proxmox/docker_host_setup_guide.md` |
| Local AI inference | CT 114 (unprivileged LXC) | `192.168.20.104` / VLAN 20 | 8081, 3002, 10200, 10300, 10400 | `llm-host.home.local`, `openwebui.home.local` | Not advertised by default; source-scoped host and Docker firewall rules | `/opt/stacks/local-ai/`; model/voice data local to CT 114 | Uptime Kuma should check llama.cpp, Open WebUI, Piper, Whisper and OpenWakeWord | `scripts/setup/proxmox/llm_host_setup_guide.md`, `docs/procedures/local_ai_performance_testing.md` |
| OMV NAS | NAS hardware | `192.168.40.50` / VLAN 40 storage | 80, 22, 445, 2049, NFS helper ports 111/20048/32765-32767 | `OMVNAS`; web UI at `http://192.168.40.50/`, `omv.home.local`, `nas.home.local` | not advertised as a broad storage route | md0 `backups/` hierarchy, md0 `CCTV/` Frigate recording share, Immich media NFS, SMART, OMV config backup | ping, web UI, SMART, NFS checks; docker-host Telegraf sees `/mnt/omv/immich` | `scripts/setup/nas/omv_nas_setup_guide.md` |
| OMV Transfer Portal | OMVNAS native service | `192.168.40.50` / VLAN 40 storage | 8088 | `http://192.168.40.50:8088/` | none in v1 | `/var/lib/transferportal/jobs.sqlite`, `/etc/transferportal/config.yaml`, `/var/log/transferportal/` | systemd status, audit log, job log tail | `docs/install/services/transferportal.md` |

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
| Mealie | `/opt/stacks/mealie/` | 9925/tcp | `mealie.home.local:9925` | Via docker-host Tailscale identity | SQLite data under stack path; OMV backup pending | Uptime Kuma HTTP check | `docs/install/services/mealie.md` |
| Grocy | `/opt/stacks/grocy/` | 9283/tcp | `grocy.home.local:9283` | Via docker-host Tailscale identity | config/database under stack path; OMV backup pending | Uptime Kuma HTTP check | `docs/install/services/grocy.md` |
| Obsidian LiveSync | `/opt/stacks/obsidian-livesync/` | 5984/tcp; Tailscale HTTPS 8443 | `obsidian-sync.home.local:5984` | `docker-host.tail7012a0.ts.net:8443` after Serve approval | CouchDB data under stack path; Git remains version history | Uptime Kuma HTTP auth check | `docs/install/services/obsidian-livesync.md` |

## Docker-host roadmap

| Tier | Service | Suggested stack path | Default / planned port | Notes |
|---|---|---|---|---|
| Tier 2 | Paperless-ngx | `/opt/stacks/paperless-ngx/` | 8001 | `docs/install/services/paperless-ngx.md` |
| Tier 2 | ntfy | `/opt/stacks/ntfy/` | 8085 | Pre-flight live internal-only; `docs/install/services/ntfy.md` |
| Tier 2 | Actual Budget | `/opt/stacks/actual-budget/` | 5006 | `docs/install/services/actual-budget.md`; sensitive data gate |
| Tier 2 | Scrypted | `/opt/stacks/scrypted/` | 10443 / 11080 | `docs/install/services/scrypted.md`; placement gate |
| Tier 2 | SearXNG | `/opt/stacks/searxng/` | 8087 | Pre-flight live direct-access; `docs/install/services/searxng.md`; egress/rate-limit gate |
| Tier 2 | Whoogle | `/opt/stacks/whoogle/` | 8088 | Pre-flight live direct-access; `docs/install/services/whoogle.md`; egress/rate-limit gate |
| Tier 3 | Vaultwarden | `/opt/stacks/vaultwarden/` | 8082 | `docs/install/services/vaultwarden.md`; security gate |
| Tier 3 | Portainer | `/opt/stacks/portainer/` | 9443 | `docs/install/services/portainer.md`; socket exposure gate |
| Tier 3 | Watchtower monitor-only | `/opt/stacks/watchtower/` | none | Pre-flight live monitor-only; useful during approved registry egress windows |
| Tier 3 | local registry mirror | `/opt/stacks/registry-mirror/` | 5000 | `docs/install/services/local-registry-mirror.md`; daemon rollback gate |
| Tier 3 | Node-RED | `/opt/stacks/node-red/` | 1880 | `docs/install/services/node-red.md`; HA-native automation gate |
| Future | AI-adjacent query apps | `/opt/stacks/<service>/` | TBD | VM 103 is the expected target for future containerized query apps; define app-specific API, egress, storage, monitoring, and firewall rules before deployment |

## DNS aliases

| Name | IP | Notes |
|---|---:|---|
| `docker-host.home.local` | `192.168.20.102` | VM 103 |
| `adguard.home.local` | `192.168.20.102` | AdGuard Home UI/DNS host |
| `immich.home.local` | `192.168.20.102` | Immich UI |
| `homepage.home.local` | `192.168.20.102` | Homepage UI |
| `dozzle.home.local` | `192.168.20.102` | Dozzle UI |
| `bambuddy.home.local` | `192.168.20.102` | Bambuddy UI |
| `ntfy.home.local` | `192.168.20.102` | ntfy UI/API |
| `searxng.home.local` | `192.168.20.102` | Future SearXNG UI |
| `whoogle.home.local` | `192.168.20.102` | Future Whoogle UI |
| `mealie.home.local` | `192.168.20.102` | Mealie recipe and meal-planning UI |
| `grocy.home.local` | `192.168.20.102` | Grocy food-stock UI |
| `obsidian-sync.home.local` | `192.168.20.102` | CouchDB backend for Obsidian LiveSync |
| `llm-host.home.local` | `192.168.20.104` | CT 114 local AI host |
| `openwebui.home.local` | `192.168.20.104` | Open WebUI host |
| `omv-nas.home.local` | `192.168.40.50` | OMV hostname |
| `omv.home.local` | `192.168.40.50` | OMV convenience alias |
| `nas.home.local` | `192.168.40.50` | Storage convenience alias |
