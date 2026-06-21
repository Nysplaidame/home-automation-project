---
title: ACL And Access Matrix
description: Canonical OpenWrt, Tailscale, host firewall, and service-auth access intent
tags: [reference, acl, firewall, tailscale, access-control]
created: 2026-05-23
modified: 2026-05-31
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
| Tailscale daily access | docker-host node services, HA `192.168.20.101/32`, OMV `192.168.40.50/32`, Grafana/Kuma host `192.168.60.10/32` on ports `3000`/`3001` | broad VLAN routes, monitoring InfluxDB `8086` | Tailscale route approval + ACLs + docker-host UFW + narrow OpenWrt allow rules |
| WireGuard dormant fallback | LAN, HA host, OMV host, DMZ fallback | Management, NVR, Printers, IoT, broad Storage VLAN | OpenWrt `vpn_clients` firewall zone |
| Management VLAN | all local admin targets | WAN-exposed admin | OpenWrt + service auth |
| Guest VLAN | internet only through router DNS | all internal VLANs | OpenWrt |

## Tailscale ACL intent

| User/group | Source | Destination | Ports | Notes |
|---|---|---|---|---|
| Admin devices | tailnet admin group | docker-host Tailscale IP / MagicDNS | 22, service UI ports | Admin only |
| Admin devices | tailnet admin group | `192.168.20.101/32` | 8123 | Home Assistant |
| Admin devices | tailnet admin group | `192.168.40.50/32` | 80, 443, 445, 2049, 22 | OMV admin/shares as needed |
| Admin devices | tailnet admin group | `192.168.60.10/32` | 3000, 3001 | Grafana and Uptime Kuma only |
| Household mobile devices | approved user/device tags | docker-host service UI ports | 2283, 3001, selected apps | No Management/NVR/IoT/Printers |
| Household mobile devices | approved user/device tags | `192.168.60.10/32` | 3000, 3001 | Monitoring dashboards only if desired for daily mobile use |
| Admin devices | tailnet admin group | `192.168.20.104/32` | 3002, 11434, 10200, 10300, 10400 | Local AI admin/testing only if explicitly approved |
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
| LAN | docker-host app UIs | 8000, 2283, 3001, 8080, 8081, 8085, 8087, 8088/tcp | Bambuddy, Immich, Homepage, AdGuard admin, Dozzle, ntfy, SearXNG, Whoogle |
| LAN | Printers | 8883, 21, 80, 8080/tcp | Slicer/local printer access |
| HA | Frigate | 8971, 5000, 8554, 8555/tcp | HA integration |
| HA | OMV | 22, 445, 2049/tcp | Backup/storage |
| HA | IoT | 6053, 3232/tcp | ESPHome API/OTA |
| docker-host | P1S | 8883, 21/tcp | Bambuddy |
| HA | llm-host | 11434, 10200, 10300/tcp | Ollama and Wyoming STT/TTS integrations |
| LAN / Management | llm-host | 3002/tcp; 11434/tcp only if testing requires it | Open WebUI and local LLM test access |
| Monitoring | llm-host | 11434, 3002, 10200, 10300/tcp | Uptime Kuma checks and service health |
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
| llm-host | default deny incoming; allow HA to Ollama/Wyoming ports; allow Management/LAN to Open WebUI if approved; allow Monitoring checks; block Guest, DMZ, NVR, Printers, and IoT |
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
| Hermes Agent candidate | advisory/tooling-only until separate sandbox, credentials, logging, and tool allowlist are approved |
| OMV | unique admin and service-user credentials |
| Vaultwarden candidate | separate security review before deployment |
