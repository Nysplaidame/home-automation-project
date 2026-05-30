---
title: "Monitoring VM"
category: entity
tags: [software, monitoring, grafana, proxmox, influxdb, uptime-kuma, telegraf]
created: 2026-04-07
updated: 2026-05-30
sources: [proxmox-setup-guide, project-readme, project-todo]
status: stable
---

# Monitoring VM

**Type:** integration — observability stack
**Status:** ✅ Live — VM 102 on VLAN 60 at `192.168.60.10`
**Related:** [[entities/proxmox]], [[entities/home-assistant]], [[entities/docker-host]], [[entities/gl-mt6000]]

## Overview

The monitoring VM is live as Proxmox VM 102 on VLAN 60. It runs the project
observability stack: Uptime Kuma for availability checks, InfluxDB for
metrics/history storage, Grafana for dashboards, and Telegraf for collection
including forwarded OpenWrt syslog.

Home Assistant has a storage-managed `Monitoring` dashboard/sidebar entry with
direct links to Grafana and Uptime Kuma. Direct UI access is the reliable path
for now; embedded Grafana/Kuma inside HA is intentionally parked until a
same-origin HTTPS/reverse-proxy path is designed and tested.

## Key Properties

- VM ID: 102 (`monitoring`)
- VLAN: 60 (Monitoring)
- IP: `192.168.60.10`
- OS: Debian 13
- Stack: Uptime Kuma, InfluxDB, Grafana, Telegraf
- Grafana: `http://192.168.60.10:3000`
- InfluxDB: `http://192.168.60.10:8086`
- Uptime Kuma: `http://192.168.60.10:3001`

## Live Integrations

- Uptime Kuma baseline monitors are green for router DNS, Proxmox UI, HA UI, docker-host SSH, docker-host APT cache, Bambuddy UI, Grafana, InfluxDB, and Uptime Kuma.
- OpenWrt forwards syslog to `192.168.60.10:514/udp`; Telegraf receives on container port `6514/udp` and writes `syslog` measurements to InfluxDB.
- Home Assistant exports state history to the `homeassistant` InfluxDB bucket using `source=HA`.
- Router policy includes scoped `HA to InfluxDB` access from `192.168.20.101` to `192.168.60.10:8086/tcp`.
- Grafana datasource: `InfluxDB - Home Automation` (`uid: influxdb-homeassistant`).
- Grafana dashboard: `Home Automation Overview` (`/d/home-automation-overview/home-automation-overview`).
- Proxmox native metrics write to bucket `proxmox` through metric server `proxmox-influx`.
- Docker-host Telegraf writes host/container metrics to bucket `dockerhost`.
- Uptime Kuma monitor snapshots are exported to bucket `uptimekuma`.
- Docker-host Fail2ban counters are exported to bucket `dockerhost`.
- Grafana dashboards now include `Proxmox Resource Overview`, `Service Availability`, `Network DNS`, and `Security Posture`.
- `NAS Resource Overview` exists as a planned shell only; do not treat NAS telemetry as live.

## Open Questions

- [x] Add an external health signal so monitoring-VM downtime is visible even when Uptime Kuma itself is down.
- [x] Park Grafana/Kuma embedding behind same-origin HTTPS/reverse-proxy approval instead of treating it as a current reliability target.
- [x] Deploy docker-host Fail2ban baseline and export counters.
- [ ] Apply the repo-side HA Lovelace direct-link snippet through the HA UI.
- [ ] Add NAS telemetry only after OMV/NAS exists.

## Change Log

- 2026-05-30: Added Proxmox/docker-host metrics, architecture dashboards, Uptime Kuma/Fail2ban exporters, external HA health state, and direct-link monitoring posture.
- 2026-05-18: Corrected stale planned-state page. VM 102 is live with Grafana, InfluxDB, Telegraf, and Uptime Kuma.
- 2026-05-08: Clarified — VM 102 never created at that point; docker-host is VM 103; monitoring still planned.
- 2026-04-07: Page created as stub from proxmox-setup-guide ingest.
