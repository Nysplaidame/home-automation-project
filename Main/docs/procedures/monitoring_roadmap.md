---
title: Monitoring and Logging Roadmap
description: Deployment order for health checks, uptime monitoring, metrics, alerts, and syslog
tags: [monitoring, logging, grafana, influxdb, telegraf, uptime-kuma]
created: 2026-05-08
type: procedure
status: active
---

# Monitoring And Logging Roadmap

## Current live state

### Already live

- `scripts/monitoring/health_check.sh` as the immediate health probe
- selective OpenWrt firewall logging on key deny rules
- core services with stable addresses suitable for monitoring

### Planned but not yet deployed

- monitoring VM on VLAN 60 (`192.168.60.10`)
- `Uptime Kuma`
- `InfluxDB`
- `Grafana`
- `Telegraf`
- OpenWrt remote syslog forwarding
- centralized alert routing

## Chosen deployment order

### Phase 1 — keep the lightweight probe

Use `health_check.sh` as the day-1 operational check from management or Proxmox.
This remains useful even after a fuller monitoring stack exists.

### Phase 2 — deploy Uptime Kuma first

Why first:

- fastest path to clear service-up/service-down visibility
- low complexity
- useful before cameras, NAS, and more sensors exist

Initial monitors should cover:

- router
- Proxmox
- Home Assistant
- docker-host
- Bambuddy UI
- Frigate VM
- NAS when built

### Phase 3 — add metrics with InfluxDB + Grafana

Use this when you want historical trends, not just “is it up”.

Primary targets:

- HA sensor history
- VentSys telemetry
- smart plug energy data
- Proxmox / VM resource usage
- docker-host resource usage

### Phase 4 — add Telegraf collection

Use Telegraf for:

- host metrics
- container metrics
- OpenWrt syslog ingestion
- later, NAS and other Linux host metrics

### Phase 5 — wire in alerting

Preferred progression:

1. Uptime Kuma notifications for core outages
2. Grafana alerts for thresholds / trends
3. optional `ntfy` for self-hosted push notifications

## Logging plan

### Router / firewall

- keep targeted deny logging where it adds security value
- forward OpenWrt syslog to the monitoring VM once VLAN 60 is live

### Linux VMs

- keep native journald / service logs locally
- add centralized visibility later via Telegraf-backed collection

### Docker-host

- use container logs locally first
- add `Dozzle` as the simplest internal log viewer if desired

## Recommended near-term stack choices

### Strong yes

- `Uptime Kuma`
- `Grafana`
- `InfluxDB`
- `Telegraf`

### Nice add-ons

- `ntfy`
- `Dozzle`

## IDS / IPS progression

### Now

- rely on segmentation, firewall policy, selective deny logging, and `health_check.sh`
- do **not** introduce a heavy IDS/IPS stack before basic monitoring is live

### Later

- add centralized log visibility first
- add `Fail2ban` on Frigate and other Linux-exposed services where it adds value
- evaluate `CrowdSec` if log-driven automated blocking becomes useful
- evaluate `Suricata` only on dedicated x86 hardware if true network IDS/IPS becomes a real goal

### Maybe never

- running heavyweight IDS/IPS directly on the GL-MT6000 router
- deploying enterprise-scale security stacks such as full Wazuh/ELK unless operational complexity is clearly worth it

## Current answer

As of May 8, 2026:

- true IDS: not deployed
- true IPS: not deployed
- host-based banning: not deployed yet (`Fail2ban` planned)
- security foundations: segmentation, firewall rules, WireGuard, selective logging

## Success criteria

The monitoring stack is “good enough” when:

- service outages are visible quickly
- HA, Proxmox, docker-host, and Frigate have basic uptime checks
- historical metrics exist for HA / VentSys / core hosts
- router syslog reaches a central place
- alerts go somewhere you will actually notice
