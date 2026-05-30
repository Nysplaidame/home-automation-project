---
title: Monitoring and Logging Roadmap
description: Deployment order for health checks, uptime monitoring, metrics, alerts, and syslog
tags: [monitoring, logging, grafana, influxdb, telegraf, uptime-kuma]
created: 2026-05-08
modified: 2026-05-30
type: procedure
status: active
---

# Monitoring And Logging Roadmap

## Current live state

### Already live

- `scripts/monitoring/health_check.sh` as the immediate health probe
- selective OpenWrt firewall logging on key deny rules
- core services with stable addresses suitable for monitoring
- monitoring VM on VLAN 60 (`192.168.60.10`)
- `Uptime Kuma`
- `InfluxDB`
- `Grafana`
- `Telegraf`

### Planned but not yet deployed

- centralized alert routing

### Live monitoring VM notes

- VM ID: `102`
- Hostname: `monitoring`
- IP: `192.168.60.10`
- MAC: `BC:24:11:A6:94:95`
- Stack path: `/opt/monitoring`
- Credentials file: `/root/monitoring-stack-credentials.txt` on VM 102
- Uptime Kuma admin account has been created
- Baseline Uptime Kuma monitors are live and green for router DNS, Proxmox UI, HA UI, docker-host SSH, docker-host APT cache, Bambuddy UI port, Homepage UI, Dozzle UI, AdGuard DNS, AdGuard UI, Immich UI, Grafana, InfluxDB, and Uptime Kuma
- OpenWrt syslog is forwarding to Telegraf on UDP/514 and writing `syslog` measurements into InfluxDB
- Home Assistant is exporting state history into the `homeassistant` bucket with `source=HA`
- Grafana datasource `InfluxDB - Home Automation` is configured and tested
- Grafana dashboard `Home Automation Overview` is live with monitoring VM, Docker, HA write, and OpenWrt syslog panels
- Proxmox native metric export is live via metric server `proxmox-influx`, writing to InfluxDB bucket `proxmox`
- Grafana datasource `InfluxDB - Proxmox` and dashboard `Proxmox Resource Overview` are live
- Docker-host Telegraf is live under `/opt/stacks/telegraf`, writing host and container metrics to InfluxDB bucket `dockerhost`
- Grafana datasource `InfluxDB - Docker Host` is live, and `Proxmox Resource Overview` includes Docker-host/container panels
- Grafana dashboards `Service Availability`, `Network DNS`, and `Security Posture` are live for architecture-level monitoring
- Uptime Kuma monitor snapshots are exported to InfluxDB bucket `uptimekuma` by `uptime-kuma-influx-export.timer`
- docker-host Fail2ban counters are exported to InfluxDB bucket `dockerhost` by `fail2ban-influx-export.timer`
- Grafana dashboard shell `NAS Resource Overview` is present but planned only; do not treat NAS metrics as live until the NAS is built
- Home Assistant has a storage-managed `Monitoring` dashboard at `/monitoring/overview` with direct links to Grafana and Uptime Kuma
- Embedded Grafana and Uptime Kuma views in HA remain intentionally parked until a same-origin HTTPS/reverse-proxy path is implemented and validated
- Uptime Kuma direct iframe embedding is blocked by its `SAMEORIGIN` frame header; integrate it later through a same-origin reverse proxy/HTTPS route or use API/notification integration instead
- HA-side external monitoring health package is live at
  `/config/packages/monitoring_external_health_package.yaml`, with source in
  `configs/home-assistant/monitoring_external_health_package.yaml`. It creates
  command-line binary sensors for Grafana, InfluxDB, and Uptime Kuma reachability
  from HA plus the aggregate `Monitoring Stack Externally Healthy` template
  sensor. Router rule `HA to Monitoring Health` allows HA to reach Grafana and
  Kuma on `192.168.60.10:3000/3001`; the existing `HA to InfluxDB` rule covers
  `8086`.
- `scripts/monitoring/health_check.sh` defaults to staged core checks only. Use
  `--full` later when Frigate UI, NAS, P1S, VentSys boards, and smart plugs are
  expected to be online.

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

- router DNS
- Proxmox UI
- Home Assistant UI
- docker-host SSH
- docker-host APT cache
- Bambuddy UI port
- monitoring stack self-checks
- Frigate VM when Frigate is started
- NAS when built

### Phase 3 — add metrics with InfluxDB + Grafana

Use this when you want historical trends, not just “is it up”.

Primary targets:

- HA sensor history
- VentSys telemetry
- smart plug energy data
- Proxmox / VM resource usage
- docker-host resource usage

Live state:

- Telegraf writes monitoring VM host/container metrics to the `homeassistant` bucket.
- Home Assistant writes state history to the same bucket with `source=HA`.
- Grafana uses InfluxDB v2, organization `homelab`, and bucket `homeassistant`.
- Baseline dashboard URL: `http://192.168.60.10:3000/d/home-automation-overview/home-automation-overview`
- Proxmox dashboard URL: `http://192.168.60.10:3000/d/proxmox-resource-overview/proxmox-resource-overview`
- Service Availability URL: `http://192.168.60.10:3000/d/service-availability-overview/service-availability`
- Network DNS URL: `http://192.168.60.10:3000/d/network-dns-overview/network-dns`
- Security Posture URL: `http://192.168.60.10:3000/d/security-posture-overview/security-posture`
- NAS dashboard shell URL: `http://192.168.60.10:3000/d/nas-resource-overview/nas-resource-overview`
- Home Assistant monitoring dashboard: `http://192.168.20.101:8123/monitoring/overview`
- Docker-host/container metrics are folded into the Proxmox dashboard for now
  rather than creating a third dashboard, preserving the two-dashboard model:
  live infrastructure now, NAS-focused dashboard later.

## Monitoring posture consistency

- Day-to-day operator path is direct-link monitoring access (HA links out to Grafana and Uptime Kuma).
- HA-embedded Grafana/Kuma is not a current dependency and should not be treated as an in-scope reliability target.
- Do not widen anonymous access solely to force embedding; re-evaluate embedding only after same-origin HTTPS is in place.
- External monitoring health in HA (`binary_sensor.monitoring_stack_externally_healthy`) remains the backstop when the monitoring VM itself is degraded.

### Phase 4 — add Telegraf collection

Use Telegraf for:

- host metrics
- container metrics
- OpenWrt syslog ingestion
- later, NAS and other Linux host metrics

Live collectors:

- monitoring VM Telegraf: monitoring VM host/container metrics and OpenWrt syslog
- docker-host Telegraf: VM 103 host metrics plus Docker engine/container metrics
- monitoring VM Uptime Kuma exporter: monitor status/latency into bucket `uptimekuma`
- docker-host Fail2ban exporter: jail counters into bucket `dockerhost`

### Phase 5 — wire in alerting

Preferred progression:

1. Uptime Kuma notifications for core outages
2. Grafana alerts for thresholds / trends
3. optional `ntfy` for self-hosted push notifications

## Logging plan

### Router / firewall

- keep targeted deny logging where it adds security value
- forward OpenWrt syslog to the monitoring VM on `192.168.60.10:514/udp`
- Telegraf receives router syslog on container port `6514/udp` via Docker port mapping `192.168.60.10:514:6514/udp`

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

Reference plan: `docs/procedures/ids_ips_progression_plan.md`

### Now

- rely on segmentation, firewall policy, selective deny logging, and `health_check.sh`
- keep docker-host `Fail2ban` SSH baseline active and observed through the security dashboard
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

As of May 30, 2026:

- true IDS: not deployed
- true IPS: not deployed
- host-based banning: docker-host `Fail2ban` SSH baseline is deployed; Frigate and other Linux service hosts remain planned
- security foundations: segmentation, firewall rules, Tailscale daily access, dormant WireGuard fallback, selective logging, Grafana/Kuma visibility

## Success criteria

The monitoring stack is “good enough” when:

- service outages are visible quickly
- HA, Proxmox, docker-host, and Frigate have basic uptime checks
- historical metrics exist for HA / VentSys / core hosts
- router syslog reaches a central place
- alerts go somewhere you will actually notice
