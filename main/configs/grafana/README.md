---
title: Grafana Source Dashboards
description: Rebuildable source exports for Grafana dashboards
tags: [grafana, dashboards, monitoring]
created: 2026-05-29
modified: 2026-05-29
type: config-reference
status: active
---

# Grafana Source Dashboards

These files are source exports for live Grafana dashboards on the monitoring VM
at `192.168.60.10`.

Live dashboards may have different internal Grafana `id` or `version` values.
The durable identity is the dashboard `uid`.

Current source exports:

- `dashboards/service-availability-overview.json`
- `dashboards/network-dns-overview.json`
- `dashboards/security-posture-overview.json`

Operational notes:

- `Service Availability` depends on the local Uptime Kuma SQLite-to-Influx
  exporter on the monitoring VM.
- `Security Posture` depends on the docker-host Fail2ban-to-Influx exporter.
- `Network DNS` currently uses OpenWrt syslog plus AdGuard container metrics;
  AdGuard query-level analytics are not exported yet.
