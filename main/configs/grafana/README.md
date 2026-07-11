---
title: Grafana Source Dashboards
description: Rebuildable source exports for Grafana dashboards
tags: [grafana, dashboards, monitoring]
created: 2026-05-29
modified: 2026-07-10
type: config-reference
status: active
---

# Grafana Source Dashboards

These files are source exports for live Grafana dashboards on the monitoring VM
at `192.168.60.10`.

Live dashboards may have different internal Grafana `id` or `version` values.
The durable identity is the dashboard `uid`.

Current source exports:

- `dashboards/proxmox-resource-overview.json`
- `dashboards/service-availability-overview.json`
- `dashboards/network-dns-overview.json`
- `dashboards/security-posture-overview.json`

Known missing source exports:

- `Home Automation Overview`
- `NAS Resource Overview`

Re-export these after Grafana admin access is available. Keep resource
dashboards labelled by metric type, such as `CPU`, `Guest RAM`, `RAM Pressure`,
or `Root Disk`, rather than showing bare percentages.

Operational notes:

- `Service Availability` depends on the local Uptime Kuma SQLite-to-Influx
  exporter on the monitoring VM.
- `Security Posture` depends on the docker-host Fail2ban-to-Influx exporter.
- `Network DNS` currently uses OpenWrt syslog plus AdGuard container metrics;
  AdGuard query-level analytics are not exported yet.
- `system/monitoring-docker-firewall.sh` and its systemd unit are the
  rebuildable VM 102 policy for Docker-published Grafana, Uptime Kuma,
  InfluxDB, and Telegraf syslog ports.
