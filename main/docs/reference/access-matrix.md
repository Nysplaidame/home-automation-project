---
title: ACL And Access Matrix
description: Canonical OpenWrt, Tailscale, host firewall, and service-auth access intent
tags: [reference, acl, firewall, tailscale, access-control]
created: 2026-05-23
modified: 2026-07-24
type: reference
status: active
---

# ACL And Access Matrix

This document records intended access paths. OpenWrt rules remain the canonical
local firewall policy. Tailscale ACLs are desired policy only until implemented
in the tailnet admin console.

## Remote access policy

| Path | Allowed target | Denied target | Enforcement |
|---|---|---|---|
| Tailscale daily access | docker-host node services, HA `192.168.20.101/32`, Frigate `192.168.30.20/32` on authenticated HTTPS `8971`, OMV `192.168.40.50/32`, Grafana/Kuma host `192.168.60.10/32` on ports `3000`/`3001` | broad VLAN routes, Frigate internal API `5000`, monitoring InfluxDB `8086` | Tailscale route approval + ACLs + docker-host UFW + narrow OpenWrt allow rules |
| WireGuard dormant fallback | LAN, HA host, OMV host, DMZ fallback | Management, NVR, Printers, IoT, broad Storage VLAN | OpenWrt `vpn_clients` firewall zone |
| Management VLAN | all local admin targets | WAN-exposed admin | OpenWrt + service auth |
| Guest VLAN | internet only through router DNS | all internal VLANs | OpenWrt |

Planned managed-switch administration belongs on VLAN 10. The Zyxel GS1900-8HP
management interface should use `192.168.10.12` once its MAC address is known.

## Tailscale ACL intent

| User/group | Source | Destination | Ports | Notes |
|---|---|---|---|---|
| Admin devices | tailnet admin group | docker-host Tailscale IP / MagicDNS | 22, service UI ports | Admin only |
| Admin devices | tailnet admin group | `192.168.20.101/32` | 8123 | Home Assistant |
| Admin devices | tailnet admin group | `192.168.30.20/32` | 8971 | Frigate authenticated HTTPS only; internal API `5000` remains denied |
| Admin devices | tailnet admin group | `192.168.40.50/32` | 80, 443, 445, 2049, 22 | OMV admin/shares as needed |
| Admin devices | tailnet admin group | `192.168.60.10/32` | 3000, 3001 | Grafana and Uptime Kuma only |
| Household mobile devices | approved user/device tags | docker-host service UI ports | 443, 3001 rollback, 8180-8208 previews, 2283, selected apps | No Management/NVR/IoT/Printers |
| Household mobile devices | approved user/device tags | `192.168.60.10/32` | 3000, 3001 | Monitoring dashboards only if desired for daily mobile use |
| Admin devices | tailnet admin group | `192.168.20.104/32` | 3002, 8081, 10200, 10300, 10400 | Local AI admin/testing only if explicitly approved; embedding port 8082 is source-scoped to docker-host |
| Unknown devices | any | any routed subnet | none | Require explicit approval |

Do not advertise or allow `192.168.10.0/24`, `192.168.30.0/24`,
`192.168.35.0/24`, `192.168.50.0/24`, or the broad monitoring VLAN
`192.168.60.0/24` through Tailscale.

WireGuard fallback activation/deactivation governance is defined in
`docs/procedures/wireguard_fallback_governance.md`.

## OpenWrt access intent

| Source | Destination | Allowed | Notes |
|---|---|---|---|
| LAN | Home Assistant | 8123/tcp | HA UI |
| LAN / Management | docker-host app UIs | 443, 5984, 8000, 2283, 3001, 8080, 8081, 8085, 8087, 8088, 8091, 8092, 8093, 8100, 8180-8208, 9283, 9925/tcp | Homepage HTTPS and fixed previews, Obsidian LiveSync, Bambuddy, Immich, HTTP rollback, AdGuard admin, Dozzle, ntfy, SearXNG, Whoogle, GardenKeeper, Mermaid Viewer, Gridfinity Layout Tool, Household Hub, Grocy, Mealie |
| LAN | Printers | 8883, 21, 80, 8080/tcp | Slicer/local printer access |
| HA | Frigate | 8971, 5000, 8554, 8555/tcp | HA integration |
| HA | OMV | 22, 445, 2049/tcp | Backup/storage |
| HA | IoT | 6053, 3232/tcp | ESPHome API/OTA |
| docker-host | P1S | 8883, 21/tcp | Bambuddy |
| HA | llm-host | 8081, 10200, 10300/tcp | llama.cpp/OpenAI-compatible LLM endpoint and Wyoming STT/TTS integrations |
| HA | docker-host | 8090, 8100, 9283/tcp | GardenKeeper operations, Household Hub read-only knowledge/research, and Grocy voice shopping-list APIs |
| HA Supervisor network `172.30.32.0/23` | docker-host | 8087, 8090, 8100, 9283, 9925/tcp | SearXNG, GardenKeeper, Household Hub, Grocy, and Mealie tools used by Overwatch/Assist |
| docker-host | llm-host | 8081, 8082, 3002/tcp | Household Hub assistant/API integration path and dedicated embedding endpoint |
| LAN / Management | llm-host | 3002/tcp; 8081/tcp for local LLM testing | Open WebUI and local LLM test access |
| Monitoring | llm-host | 8081, 3002, 10200, 10300, 10400/tcp | Uptime Kuma checks and service health |
| llm-host | docker-host | future approved query-app ports only | Pattern reserved for future containerized query apps; no app-specific rule exists yet |
| docker-host | Monitoring VM | 8086/tcp | Telegraf metrics export to InfluxDB bucket `dockerhost` |
| docker-host | Monitoring VM | 3000, 3001/tcp | Tailscale-routed mobile access to Grafana and Uptime Kuma only |
| docker-host | WAN | Tailscale, AdGuard upstream, and approved pre-flight search egress only | No general Docker pulls outside maintenance |
| Frigate | OMV | 22, 445, 2049/tcp | Recording/archive storage |
| Frigate | HA | 8883/tcp | MQTT TLS |
| Frigate | docker-host | 3142/tcp | apt-cacher-ng |
| Monitoring | selected infra | monitoring/admin ports | No broad write path |
| VPN clients | HA | 8123/tcp | Dormant fallback |
| VPN clients | OMV | 80, 443, 445, 2049, 22/tcp | Host-only fallback |
| VPN clients | Management/NVR/Printers/IoT | none | Blocked |

## Host firewall intent

| Host | Firewall intent |
|---|---|
| docker-host | default deny incoming; allow Management/LAN/Tailscale to approved service ports; allow Tailscale interface; avoid broad routed forwarding except approved host routes |
| llm-host | default deny incoming; allow HA to llama.cpp/Wyoming ports; allow Management/LAN to Open WebUI and approved LLM testing; allow Monitoring checks; block Guest, DMZ, NVR, Printers, and IoT |
| OMV | allow Management, HA, Frigate, docker-host, and Tailscale-routed admin/device access only to required ports |
| Frigate | allow HA and Management; no user/LAN direct path until cameras are configured |
| Home Assistant | allow LAN, Management, Tailscale-routed admin/mobile, and required service integrations |

## Service auth intent

| Service | Auth requirement |
|---|---|
| Home Assistant | strong admin password + 2FA; long-lived tokens stored in Bitwarden |
| AdGuard Home | admin password in Bitwarden; no unauthenticated admin UI |
| Immich | app accounts and library backup before import |
| Homepage | internal-only; avoid secrets in visible config |
| Dozzle | admin/internal-only; do not expose to Guest/DMZ |
| ntfy | internal-only; default anonymous access denied; topic users stored in Bitwarden |
| SearXNG | internal-only pre-flight; direct HTTP until reverse proxy/HTTPS pass |
| Whoogle | internal-only pre-flight; direct HTTP until reverse proxy/HTTPS pass |
| Watchtower | monitor-only; no automatic updates |
| Local AI / Open WebUI | internal-only; admin account required; HA exposes only approved entities; no safety-critical direct control by default |
| GardenKeeper | dedicated HA secret; deterministic garden operations only; ambiguous or destructive task changes require confirmation |
| Household Hub | dedicated HA secret; voice surface is read-only knowledge and recipe research; no garden-state or downstream writes |
| Hermes Agent candidate | advisory/tooling-only until separate sandbox, credentials, logging, and tool allowlist are approved |
| OMV | unique admin and service-user credentials |
| Jellyfin | household account authentication; libraries are read-only in the container; no iGPU passthrough in the first phase |
| Calibre-Web | household account authentication; only the dedicated Calibre library is writable |
| Atsumeru | administrator/client authentication; generated credentials never enter Git or chat logs |
| qBittorrent | strong Web UI credential; management/monitoring/Tailscale sources only; all public egress must fail closed through Gluetun |
| Vaultwarden | HTTPS-only through `vault.home.local`; raw listener is loopback-only; sign-ups/admin endpoint disabled outside bounded owner onboarding; 2FA/recovery required before real credentials |
