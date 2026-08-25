---
title: "Docker Host (VM 103)"
category: entity
tags: [software, docker, proxmox, bambuddy, apt-cache, tailscale, monitoring, fail2ban, mullvad, qbittorrent]
created: 2026-05-08
updated: 2026-08-25
sources: [project-readme, project-todo]
status: stable
---

# Docker Host (VM 103)

**Type:** integration - trusted Docker host
**Status:** Live - trusted Docker app host, Tailscale node, metrics collector, and Fail2ban baseline
**Related:** [[entities/proxmox]], [[entities/bambuddy]], [[entities/home-assistant]], [[concepts/tailscale-remote-access]], [[entities/adguard-home]], [[entities/immich]], [[entities/homepage]], [[entities/dozzle]], [[entities/household-hub]], [[entities/qbittorrent]]

## Overview

VM 103 is the central trusted Docker host on VLAN 20. It runs internal services
that need to communicate with Home Assistant, the automation network, or the
operator's daily remote-access path. Household apps, media services, ntfy,
search, the Mullvad download gateway, Watchtower monitor-only, docker-host
Telegraf, Homepage's fixed HTTPS proxy and the Fail2ban SSH baseline are live.

Internet access is blocked by router policy except for narrowly documented
Tailscale, Mullvad WireGuard, AdGuard, docker-host-to-InfluxDB, and approved
service egress. General package/container updates still go through a controlled
maintenance window.

## Key Properties

- VM ID: 103 (`docker-host`)
- VLAN: 20 (Automation)
- IP: `192.168.20.102`
- MAC: `BC:24:11:BC:B8:1A`
- OS: Debian GNU/Linux 13
- Docker `29.7.1`, containerd `2.2.6`, Buildx `0.36.0`, Compose `5.3.1`
- Tailscale `1.98.10`; Python `3.13.5-2+deb13u4`
- Stack path convention: `/opt/stacks/<service>/`
- Docker networks: every project bridge uses an explicit, non-overlapping CIDR
  and canonical name; Bambuddy's empty `10.240.23.0/24` bridge is prepared but
  its container remains in host mode until P1S connectivity returns
- Tailscale routes: exactly `192.168.20.101/32`, `192.168.30.20/32`,
  `192.168.40.50/32`, and `192.168.60.10/32`; Frigate remote routing is HTTPS
  `8971` only and its API `5000` remains denied
- Metrics: Docker-host Telegraf writes to InfluxDB bucket `dockerhost`
- Host hardening: Fail2ban `sshd` jail at `/etc/fail2ban/jail.d/docker-host-sshd.local`

## Running Workloads

| Stack | Path | Port | Status |
|---|---|---|---|
| Bambuddy | `/opt/stacks/bambuddy/` | 8000 | Running |
| apt-cacher-ng | system service | 3142 | Running |
| [[entities/adguard-home]] | `/opt/stacks/adguard-home/` | 53, 8080 | DNS filtering |
| [[entities/immich]] | `/opt/stacks/immich/` | 2283 | Live with approved OMV-backed media storage |
| [[entities/homepage]] | `/opt/stacks/homepage/` | 443, 3001 rollback, 8180-8209 | Home Operations portal and fixed HTTPS proxy |
| [[entities/dozzle]] | `/opt/stacks/dozzle/` | 8081 | Docker logs, management/internal only |
| [[entities/household-hub]] | `/opt/stacks/household-hub/` | 8100 | Knowledge/RAG, recipe research, read-only Grocy and Markdown/ICS exports |
| ntfy | `/opt/stacks/ntfy/` | 8085 | Internal alert relay |
| SearXNG | `/opt/stacks/searxng/` | 8087 | Live metasearch and bounded local-agent search API |
| Whoogle | `/opt/stacks/whoogle/` | 8088 | Live search proxy |
| Mealie / Grocy | `/opt/stacks/mealie/`, `/opt/stacks/grocy/` | 9925, 9283 | Live recipes, meal planning, stock and shopping |
| Jellyfin / Calibre-Web / Atsumeru | respective `/opt/stacks/` paths | 8096, 8083, 31337 | Live OMV-backed media services |
| Recomp Tracker | `/opt/stacks/recomp-tracker/` | 8420 | Live habits/workout tracker; fixed proxy 8209 |
| Vaultwarden | `/opt/stacks/vaultwarden/` | loopback 8222, HTTPS SNI proxy | Live; owner onboarding remains gated |
| Watchtower | `/opt/stacks/watchtower/` | none | Monitor-only; no automatic updates |
| Telegraf | `/opt/stacks/telegraf/` | none | Host/container metrics to InfluxDB |
| [[entities/qbittorrent]] | `/opt/stacks/download-gateway/` | 8084 | Mullvad-isolated downloader; fail-closed proof passed |
| Fail2ban | host service | none | SSH jail baseline |

## Tailscale Role

docker-host is the live Tailscale daily-access node. It advertises host routes
only:

- `192.168.20.101/32` for Home Assistant
- `192.168.30.20/32` for authenticated Frigate HTTPS `8971` only
- `192.168.40.50/32` for OMV
- `192.168.60.10/32` for Grafana and Uptime Kuma only

Docker-host services should be reached by docker-host Tailscale identity/MagicDNS.
Grafana and Uptime Kuma should use routed access to the monitoring VM on ports
`3000` and `3001`; InfluxDB `8086` should remain off the daily mobile path.

For the approved OnePlus mobile identity, Homepage is the app-access boundary:
the node permits split DNS, `tcp:443`, and fixed Homepage proxy ports
`tcp:8180-8209` only. The proxies target a fixed allow-list of services and do
not create a general route into VLAN 20 or other private subnets.

## Monitoring and Hardening

- Router policy allows docker-host `192.168.20.102` to write metrics to
  monitoring VM `192.168.60.10:8086`.
- Rebuildable Telegraf templates live in `main/configs/docker-host/stacks/telegraf/`.
- Rebuildable Fail2ban jail source lives in
  `main/configs/docker-host/system/docker-host-fail2ban-sshd.local`.
- Rebuildable routed UFW allowances for monitoring mobile access live at
  `main/configs/docker-host/system/docker-host-ufw-route-monitoring-tailscale.sh`.
- Watchtower remains monitor-only; update notifications are candidates for a
  planned patch window, not automatic approval.
- ntfy has a read-only `mobile-monitoring` identity for household phone
  subscriptions. Its credential is held outside the repository.
- The live app-data backup job uses SQLite's online backup API for ntfy
  `user.db` and `cache.db`; a fresh NAS backup and temporary restore smoke passed
  on 2026-07-29.
- The app-data backup service sends Kuma monitor 36's host-only-token heartbeat
  in `ExecStartPost`, meaning backup freshness is reported only after a
  successful backup. Its first live heartbeat was accepted on 2026-08-01.

## Open Questions

- [ ] Restore the P1S/VLAN-35 path, migrate Bambuddy from host mode to its
  prepared bridge, and obtain a zero-exit docker-host security audit.
- [ ] Continue weekly update review and schedule the next controlled window only
  when new candidates justify it.
- [ ] Decide whether one tightly allow-listed Autobrr source/category is useful.

## Change Log

- 2026-08-25: Reconciled the four-route Tailscale set and current live workload
  inventory with the canonical service/network references.
- 2026-08-21: Recreated all project Docker bridges at explicit canonical
  allocations, including Household Hub's shared dependency networks and
  `local-alerting`; all live checks passed except Bambuddy bridge attachment,
  which remains blocked by the unreachable P1S path.
- 2026-08-21: Added the fixed Homepage proxy route for Recomp Tracker and the
  narrow OnePlus grant for all Homepage card proxy ports (`8180`-`8209`).
- 2026-08-09: Added the live Household Hub workload and its persisted,
  confirmation-gated recipe/Mealie workflow.
- 2026-08-09: Connected Household Hub read-only to Grocy and added its persistent
  Obsidian Markdown outbox; Nextcloud remains export-only because it is absent.
- 2026-08-01: Completed the controlled package window with no reboot required;
  activated and acceptance-proved the Mullvad/qBittorrent gateway and its NAS
  backup/restore path.
- 2026-08-01: Added the post-success Uptime Kuma backup-freshness heartbeat to
  the live app-data backup service and acceptance-tested its first delivery.
- 2026-05-30: Synced live service state: Tier 1 apps, ntfy, Watchtower monitor-only, Telegraf metrics, Tailscale routes, and Fail2ban baseline are live.
- 2026-05-31: Applied monitoring VM Tailscale host route on docker-host and added routed UFW source artifact for Grafana/Kuma mobile access; route may still need Tailscale admin approval before mobile clients can use it.
- 2026-07-29: Added the read-only ntfy phone subscriber and deployed/validated
  SQLite-consistent ntfy backups to OMV.
- 2026-05-23: Added Tailscale host-route role and Tier 1 service roadmap.
- 2026-05-08: Page created - VM 103 live with Bambuddy and apt-cache.
