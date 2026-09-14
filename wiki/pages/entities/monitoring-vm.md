---
title: "Monitoring VM"
category: entity
tags: [software, monitoring, grafana, proxmox, influxdb, uptime-kuma, telegraf]
created: 2026-04-07
updated: 2026-08-01
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
- Uptime Kuma also checks OMV web/NFS and direct reachability of all three CCTV
  hosts; the checks are ntfy-enabled and were `Up` after host-scoped OpenWrt
  rules were deployed on 2026-07-29.
- CT 111 permits the monitoring VM to Frigate API TCP `5000`; Kuma's Frigate
  API check returned `200 - OK` after the host exception was applied on
  2026-08-01.
- Grafana now routes through the authenticated `ntfy Monitoring` contact point
  and default policy. Its live delivery test passed. Initial docker-host root
  disk and Proxmox root-storage alerts both evaluate `Normal` and warn above
  85% for 10 minutes.
- Aggregate OMV SMART push monitor 34 and its 30-minute OMV producer are live;
  the first accepted heartbeat reported all five physical disks healthy.
- Uptime Kuma monitor 36 receives a 25-hour docker-host app-data
  backup-freshness heartbeat only after the backup service succeeds; its first
  live delivery was accepted on 2026-08-01.
- ntfy has a dedicated read-only `mobile-monitoring` subscriber. Authenticated
  polling passed; a real Android notification is the remaining acceptance step.
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
- docker-host now advertises mobile Tailscale access for Grafana/Kuma through
  `192.168.60.10/32` and allows only routed ports `3000` and `3001`; route
  approval and mobile-data retest may still be required.
- A 2026-05-31 datasource check found the high unlabeled VM percentages on the
  Proxmox dashboard are Proxmox guest-memory values, not CPU or disk saturation.
  Current samples were about `98%` for Home Assistant, `91%` for docker-host,
  and `85%` for monitoring; Proxmox host CPU and RAM pressure were low.

## Open Questions

- [x] Add an external health signal so monitoring-VM downtime is visible even when Uptime Kuma itself is down.
- [x] Park Grafana/Kuma embedding behind same-origin HTTPS/reverse-proxy approval instead of treating it as a current reliability target.
- [x] Deploy docker-host Fail2ban baseline and export counters.
- [ ] Apply the repo-side HA Lovelace direct-link snippet through the HA UI.
- [x] Re-export `Proxmox Resource Overview` into repo source.
- [x] Add explicit metric labels to Proxmox dashboard percentage panels.
- [x] Add authenticated Grafana alerting and the dedicated ntfy mobile subscriber.
- [x] Add a backup-freshness push heartbeat.
- [x] Repair CT 111's Frigate API exception.

## Change Log

- 2026-07-29: Repaired stale Kuma checks, added OMV NFS/web and three camera
  monitors, and recorded remaining Frigate-host, Grafana, and ntfy gaps.
- 2026-07-29: Activated the OMV SMART heartbeat, added and tested authenticated
  Grafana-to-ntfy delivery with two initial disk alerts, and created the
  read-only ntfy mobile subscriber.
- 2026-08-01: Added monitor 36 and acceptance-tested docker-host's
  post-success app-data backup-freshness heartbeat.
- 2026-08-01: Re-enabled Kuma monitor 28 after CT 111's narrow Frigate API
  firewall exception; the monitoring VM and monitor both returned HTTP 200.
- 2026-05-30: Added Proxmox/docker-host metrics, architecture dashboards, Uptime Kuma/Fail2ban exporters, external HA health state, and direct-link monitoring posture.
- 2026-05-31: Applied docker-host route/firewall side for mobile Grafana/Kuma access, re-exported `Proxmox Resource Overview`, and clarified that high Proxmox VM percentages are guest-memory values.
- 2026-05-18: Corrected stale planned-state page. VM 102 is live with Grafana, InfluxDB, Telegraf, and Uptime Kuma.
- 2026-05-08: Clarified — VM 102 never created at that point; docker-host is VM 103; monitoring still planned.
- 2026-04-07: Page created as stub from proxmox-setup-guide ingest.
