---
title: "Docker Host (VM 103)"
category: entity
tags: [software, docker, proxmox, bambuddy, apt-cache]
created: 2026-05-08
updated: 2026-05-08
sources: [project-readme]
status: stable
---

# Docker Host (VM 103)

**Type:** integration — trusted Docker host
**Status:** ✅ Live — Debian 13, Docker installed, Bambuddy running
**Related:** [[entities/proxmox]], [[entities/bambuddy]], [[entities/frigate]], [[entities/home-assistant]]

## Overview

VM 103 is the central trusted Docker host on VLAN 20. It runs workloads that need to communicate with Home Assistant or the automation network. Bambuddy is its first Compose workload. It also hosts `apt-cacher-ng` for package caching across VMs.

Internet access is blocked by router policy. Updates must go through a controlled maintenance window using the temporary firewall rule `TEMP Docker Host Update Access` (always remove this rule after use).

## Key Properties

- VM ID: 103 (`docker-host`)
- VLAN: 20 (Automation)
- IP: `192.168.20.102`
- MAC: `BC:24:11:BC:B8:1A`
- OS: Debian GNU/Linux 13 (trixie), kernel `6.12.85+deb13-cloud-amd64`
- Docker: installed and active
- Docker Compose: installed
- `qemu-guest-agent`: installed and active
- Startup: `onboot: 1`, order 3

## Running Workloads

| Stack | Path | Port | Status |
|---|---|---|---|
| Bambuddy | `/opt/stacks/bambuddy/` | 8000 | ✅ Running |
| apt-cacher-ng | (system service) | 3142 | ✅ Running |

## apt-cacher-ng

Package cache for VMs that have limited or no internet access.
- Endpoint: `http://192.168.20.102:3142`
- `frigate-nvr` (VM 101) configured via `/etc/apt/apt.conf.d/01proxy`
- Permanent router rule: `Frigate to APT Cache` (VLAN 30 → VLAN 20, port 3142)

## Setup Guide

`scripts/setup/proxmox/docker_host_setup_guide.md` — VM creation, Docker install, Bambuddy workload, apt-cache setup.

## Firewall (VM-level)

- Incoming default: deny
- Allow `192.168.10.0/24` → TCP 22 (management SSH)
- Allow `192.168.10.0/24` + `192.168.1.0/24` + `192.168.20.0/24` → TCP 8000 (Bambuddy UI)

## Open Questions

- [ ] Decide whether docker-host should have periodic controlled update access or remain fully blocked
- [ ] Decide whether a Docker registry mirror is justified as more Compose workloads are added

## Change Log

- 2026-05-08: Page created — VM 103 live with Bambuddy and apt-cache
