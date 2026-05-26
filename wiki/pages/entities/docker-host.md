---
title: "Docker Host (VM 103)"
category: entity
tags: [software, docker, proxmox, bambuddy, apt-cache, tailscale]
created: 2026-05-08
updated: 2026-05-23
sources: [project-readme]
status: stable
---

# Docker Host (VM 103)

**Type:** integration - trusted Docker host
**Status:** Live - Debian 13, Docker installed, Bambuddy running
**Related:** [[entities/proxmox]], [[entities/bambuddy]], [[entities/home-assistant]], [[concepts/tailscale-remote-access]], [[entities/adguard-home]], [[entities/immich]], [[entities/homepage]], [[entities/dozzle]]

## Overview

VM 103 is the central trusted Docker host on VLAN 20. It runs internal services
that need to communicate with Home Assistant or the automation network. Bambuddy
is the first live Compose workload. It also hosts `apt-cacher-ng` for package
caching across VMs.

Internet access is blocked by router policy except for narrowly documented
Tailscale and AdGuard egress. General updates still go through a controlled
maintenance window using the temporary firewall rule `TEMP Docker Host Update
Access`.

## Key Properties

- VM ID: 103 (`docker-host`)
- VLAN: 20 (Automation)
- IP: `192.168.20.102`
- MAC: `BC:24:11:BC:B8:1A`
- OS: Debian GNU/Linux 13
- Docker and Docker Compose: installed
- Stack path convention: `/opt/stacks/<service>/`

## Running Workloads

| Stack | Path | Port | Status |
|---|---|---|---|
| Bambuddy | `/opt/stacks/bambuddy/` | 8000 | Running |
| apt-cacher-ng | system service | 3142 | Running |

## Tier 1 Planned Workloads

| Service | Path | Port | Notes |
|---|---|---|---|
| [[entities/adguard-home]] | `/opt/stacks/adguard-home/` | 53, 8080 | DNS filtering; router remains DNS/DHCP authority |
| [[entities/immich]] | `/opt/stacks/immich/` | 2283 | Gallery/photos; OMV-backed storage |
| [[entities/homepage]] | `/opt/stacks/homepage/` | 3001 | Internal dashboard |
| [[entities/dozzle]] | `/opt/stacks/dozzle/` | 8081 | Docker logs; admin/internal only |

## Tailscale Role

docker-host is the planned Tailscale subnet router. It should advertise host
routes only:

- `192.168.20.101/32` for Home Assistant
- `192.168.40.50/32` for OMV

Docker-host services should be reached by docker-host Tailscale identity/MagicDNS.

## Change Log

- 2026-05-23: Added Tailscale host-route role and Tier 1 service roadmap.
- 2026-05-08: Page created - VM 103 live with Bambuddy and apt-cache.
