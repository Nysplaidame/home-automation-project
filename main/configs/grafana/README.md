---
title: Grafana Source Dashboards
description: Rebuildable source exports for Grafana dashboards
tags: [grafana, dashboards, monitoring]
created: 2026-05-29
modified: 2026-07-29
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
- `alerting/infrastructure-health.yaml`
- `alerting/ntfy-notifications.example.yaml`

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
- The live `Infrastructure health` group warns when docker-host root disk or
  Proxmox root storage remains above 85% for 10 minutes.
- The live `ntfy Monitoring` webhook is authenticated and is the default
  notification policy. Its test delivery passed on 2026-07-29. The example
  provisioning file deliberately references `NTFY_MONITORING_PASSWORD`; keep
  that value in a runtime secret store and never commit it.
