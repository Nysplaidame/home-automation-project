---
title: Service Matrix
description: Central service, port, DNS, backup, monitoring, and runbook reference
tags: [reference, services, ports, dns, docker-host]
created: 2026-05-23
modified: 2026-05-31
type: reference
status: active
---

# Service Matrix

This matrix is the canonical place to track service placement, ports, URLs,
remote exposure, backup expectations, monitoring, and runbook coverage.

## Core infrastructure

| Service | Host | IP / VLAN | Port(s) | Local URL / DNS | Tailscale exposure | Backup / data | Monitoring | Runbook |
|---|---|---:|---|---|---|---|---|---|
| OpenWrt router | GL-MT6000 | `192.168.10.1` / VLAN 10 mgmt | 80/443, 22 | `router.home.local` | No daily exposure; WireGuard fallback endpoint on WAN | router-deploy source + generated artifacts | ping, DNS, firewall tests | `docs/troubleshooting/troubleshooting_reference.md` |
| Proxmox | MINIX | `192.168.10.10` / VLAN 10 | 8006, 22 | `proxmox.home.local` | Not advertised | local Proxmox backups, later NAS copy | Uptime Kuma | `scripts/setup/proxmox/proxmox_setup_guide.md` |
| Home Assistant | VM 100 | `192.168.20.101` / VLAN 20 | 8123, 8883 MQTT | `homeassistant.home.local` | `192.168.20.101/32` via docker-host | HA backups to OMV | Uptime Kuma, HA checks | `scripts/setup/proxmox/ha_vm_setup_guide.md` |
| Frigate | VM 101 | `192.168.30.20` / VLAN 30 | 8971, 8554, 8555 | `frigate.home.local` | Not advertised | local first, OMV archive later | parked until cameras live | `scripts/setup/proxmox/frigate_vm_setup_guide.md` |
| Monitoring stack | VM 102 | `192.168.60.10` / VLAN 60 | 3000, 3001, 8086 | monitoring dashboard links in HA | Planned host route `192.168.60.10/32` via docker-host for Grafana/Kuma only; do not expose InfluxDB | stack config + Influx backups | Uptime Kuma self-monitor plus HA-side external health sensors | `scripts/setup/proxmox/monitoring_vm_setup_guide.md` |
| Docker host | VM 103 | `192.168.20.102` / VLAN 20 | 22 plus service ports | `docker-host.home.local` | Tailscale node identity / MagicDNS | `/opt/stacks/<service>/` | Uptime Kuma, Dozzle | `scripts/setup/proxmox/docker_host_setup_guide.md` |
| OMV NAS | NAS hardware | `192.168.40.50` / VLAN 40 | 80/443, 22, 445, 2049 | `omv.home.local`, `nas.home.local` | `192.168.40.50/32` via docker-host | shared folders, SMART, OMV config backup | ping, web UI, SMART, NFS checks | `scripts/setup/nas/omv_nas_setup_guide.md` |

## Docker-host Tier 1

| Service | Stack path | Port(s) | Local URL / DNS | Tailscale exposure | Data / backup | Monitoring | Runbook |
|---|---|---|---|---|---|---|---|
| Tailscale | host service | 41641/udp outbound, 443 outbound | docker-host MagicDNS | Node identity; advertises `192.168.20.101/32`, `192.168.40.50/32`; add `192.168.60.10/32` for Grafana/Kuma mobile access | no auth keys in repo | `tailscale status`, route approval | `docs/install/phases/05-docker-host.md` |
| AdGuard Home | `/opt/stacks/adguard-home/` | 53/tcp+udp, 3000 initial, 8080 admin target | `adguard.home.local` | Admin via docker-host Tailscale identity only if ACL allows | config/work dir under stack path | DNS query test + UI | `docs/install/services/adguard-home.md` |
| Immich | `/opt/stacks/immich/` | 2283/tcp | `immich.home.local` | Via docker-host Tailscale identity / MagicDNS | pre-flight local placeholder; OMV-backed library required before real import | Uptime Kuma HTTP check | `docs/install/services/immich.md` |
| Homepage | `/opt/stacks/homepage/` | 3001/tcp | `homepage.home.local` | Via docker-host Tailscale identity / MagicDNS | config directory | HTTP check | `docs/install/services/homepage.md` |
| Dozzle | `/opt/stacks/dozzle/` | 8081/tcp | `dozzle.home.local` | Admin only via Tailscale/Mgmt/LAN policy | no critical data | HTTP check | `docs/install/services/dozzle.md` |
| Bambuddy | `/opt/stacks/bambuddy/` | 8000/tcp | `bambuddy.home.local` | Via docker-host Tailscale identity / MagicDNS if needed | app data/logs under stack path | HTTP + MQTT status | `scripts/setup/proxmox/bambuddy_vm_setup_guide.md` |
| ntfy | `/opt/stacks/ntfy/` | 8085/tcp | `ntfy.home.local` | Via docker-host Tailscale identity / MagicDNS | config/auth DB under stack path; credentials in Bitwarden | Uptime Kuma HTTP check | `docs/install/services/ntfy.md` |

## Docker-host roadmap

| Tier | Service | Suggested stack path | Default / planned port | Notes |
|---|---|---|---|---|
| Tier 2 | Paperless-ngx | `/opt/stacks/paperless-ngx/` | 8001 | `docs/install/services/paperless-ngx.md` |
| Tier 2 | Mealie | `/opt/stacks/mealie/` | 9925 | `docs/install/services/mealie.md` |
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
| `omv-nas.home.local` | `192.168.40.50` | OMV hostname |
| `omv.home.local` | `192.168.40.50` | OMV convenience alias |
| `nas.home.local` | `192.168.40.50` | Storage convenience alias |
