---
title: "Docker Host (VM 103)"
category: entity
tags: [software, docker, proxmox, bambuddy, apt-cache, tailscale, monitoring, fail2ban]
created: 2026-05-08
updated: 2026-07-10
sources: [project-readme, project-todo]
status: stable
---

# Docker Host (VM 103)

**Type:** integration - trusted Docker host
**Status:** Live - trusted Docker app host, Tailscale node, metrics collector, and Fail2ban baseline
**Related:** [[entities/proxmox]], [[entities/bambuddy]], [[entities/home-assistant]], [[concepts/tailscale-remote-access]], [[entities/adguard-home]], [[entities/immich]], [[entities/homepage]], [[entities/dozzle]]

## Overview

VM 103 is the central trusted Docker host on VLAN 20. It runs internal services
that need to communicate with Home Assistant, the automation network, or the
operator's daily remote-access path. Bambuddy, Tier 1 app services, ntfy,
search-service pre-flight stacks, Watchtower monitor-only, docker-host
Telegraf, and the Fail2ban SSH baseline are live.

Internet access is blocked by router policy except for narrowly documented
Tailscale, AdGuard, docker-host-to-InfluxDB, and approved pre-flight search
egress. General package/container updates still go through a controlled
maintenance window.

## Key Properties

- VM ID: 103 (`docker-host`)
- VLAN: 20 (Automation)
- IP: `192.168.20.102`
- MAC: `BC:24:11:BC:B8:1A`
- OS: Debian GNU/Linux 13
- Docker and Docker Compose: installed
- Stack path convention: `/opt/stacks/<service>/`
- Tailscale routes: live `192.168.20.101/32`, `192.168.40.50/32`,
  `192.168.60.10/32` for Grafana/Kuma mobile access only
- Metrics: Docker-host Telegraf writes to InfluxDB bucket `dockerhost`
- Host hardening: Fail2ban `sshd` jail at `/etc/fail2ban/jail.d/docker-host-sshd.local`

## Running Workloads

| Stack | Path | Port | Status |
|---|---|---|---|
| Bambuddy | `/opt/stacks/bambuddy/` | 8000 | Running |
| apt-cacher-ng | system service | 3142 | Running |
| [[entities/adguard-home]] | `/opt/stacks/adguard-home/` | 53, 8080 | DNS filtering |
| [[entities/immich]] | `/opt/stacks/immich/` | 2283 | Skeleton/pre-flight only until OMV-backed storage exists |
| [[entities/homepage]] | `/opt/stacks/homepage/` | 3001 | Internal dashboard |
| [[entities/dozzle]] | `/opt/stacks/dozzle/` | 8081 | Docker logs, management/internal only |
| ntfy | `/opt/stacks/ntfy/` | 8085 | Internal alert relay |
| SearXNG | `/opt/stacks/searxng/` | 8087 | Direct-access search pre-flight |
| Whoogle | `/opt/stacks/whoogle/` | 8088 | Direct-access search pre-flight |
| Watchtower | `/opt/stacks/watchtower/` | none | Monitor-only; no automatic updates |
| Telegraf | `/opt/stacks/telegraf/` | none | Host/container metrics to InfluxDB |
| Fail2ban | host service | none | SSH jail baseline |

## Tailscale Role

docker-host is the live Tailscale daily-access node. It advertises host routes
only:

- `192.168.20.101/32` for Home Assistant
- `192.168.40.50/32` for OMV
- `192.168.60.10/32` for monitoring VM UIs; approve in Tailscale admin if
  still pending

Docker-host services should be reached by docker-host Tailscale identity/MagicDNS.
Grafana and Uptime Kuma should use routed access to the monitoring VM on ports
`3000` and `3001`; InfluxDB `8086` should remain off the daily mobile path.

## Monitoring and Hardening

- Router policy allows docker-host `192.168.20.102` to write metrics to
  monitoring VM `192.168.60.10:8086`.
- Rebuildable Telegraf templates live in `main/configs/docker-host/stacks/telegraf/`.
- Rebuildable Fail2ban jail source lives in
  `main/configs/docker-host/system/docker-host-fail2ban-sshd.local`.
- Rebuildable routed UFW allowances for monitoring mobile access live at
  `main/configs/docker-host/system/docker-host-ufw-route-monitoring-tailscale.sh`.
- `docker-host-firewall.service` enforces source-scoped `DOCKER-USER` rules
  for every currently published Docker port. IPv6-published services are
  Tailscale-only; TCP/53 and UDP/53 remain IPv4-only.
- Watchtower remains monitor-only; update notifications are candidates for a
  planned patch window, not automatic approval.

## Open Questions

- [ ] Run the planned docker-host package patch window and post-check sequence.
- [ ] Keep Mullvad egress hardening for search services parked until storage and
  backup priorities are clear.

## Change Log

- 2026-07-10: Reconciled Docker published-port enforcement with declared UFW
  policy; unapproved HA access to Homepage, Mermaid Viewer, and Household Hub
  UI is now denied while approved APIs remain reachable.
- 2026-05-30: Synced live service state: Tier 1 apps, ntfy, Watchtower monitor-only, Telegraf metrics, Tailscale routes, and Fail2ban baseline are live.
- 2026-05-31: Applied monitoring VM Tailscale host route on docker-host and added routed UFW source artifact for Grafana/Kuma mobile access; route may still need Tailscale admin approval before mobile clients can use it.
- 2026-05-23: Added Tailscale host-route role and Tier 1 service roadmap.
- 2026-05-08: Page created - VM 103 live with Bambuddy and apt-cache.
