---
title: Grafana Architecture Dashboards
description: Full-architecture Grafana dashboard set, exporters, and Home Assistant link posture
tags: [grafana, monitoring, dashboards, home-assistant, uptime-kuma, fail2ban]
created: 2026-05-29
modified: 2026-05-31
type: procedure
status: active
---

# Grafana Architecture Dashboards

This document tracks the architecture-level Grafana dashboards on the monitoring
VM and the small exporters that feed them.

## Live dashboards

| Dashboard | URL | Scope |
|---|---|---|
| Home Automation Overview | `http://192.168.60.10:3000/d/home-automation-overview/home-automation-overview` | Baseline monitoring VM / HA / router syslog view |
| Proxmox Resource Overview | `http://192.168.60.10:3000/d/proxmox-resource-overview/proxmox-resource-overview` | Proxmox, VMs, docker-host, and containers |
| Service Availability | `http://192.168.60.10:3000/d/service-availability-overview/service-availability` | Uptime Kuma monitor status and latency |
| Network DNS | `http://192.168.60.10:3000/d/network-dns-overview/network-dns` | OpenWrt syslog, DNS-rebind warnings, AdGuard container health |
| Security Posture | `http://192.168.60.10:3000/d/security-posture-overview/security-posture` | docker-host Fail2ban counters and router warning logs |
| NAS Resource Overview | `http://192.168.60.10:3000/d/nas-resource-overview/nas-resource-overview` | Planned shell only until OMV/NAS exists |

Current validation, 2026-05-31:

- Grafana anonymous search lists Home Automation Overview, NAS Resource
  Overview, Service Availability, Network DNS, and Security Posture.
- Grafana admin API access confirmed `Proxmox Resource Overview` is live and
  saveable; the dashboard was re-exported to source and its ambiguous resource
  percentage panels were relabelled.

## Source exports

Dashboard source exports live in:

```text
configs/grafana/dashboards/
```

Current exported dashboards:

- `proxmox-resource-overview.json`
- `service-availability-overview.json`
- `network-dns-overview.json`
- `security-posture-overview.json`

Missing source exports:

- `home-automation-overview.json`
- `nas-resource-overview.json`

## Exporters

### Uptime Kuma to InfluxDB

Live path:

- Script: `/usr/local/sbin/export_uptime_kuma_to_influx.py` on monitoring VM
- Env file: `/etc/uptime-kuma-influx-export.env`
- Systemd timer: `uptime-kuma-influx-export.timer`
- InfluxDB bucket: `uptimekuma`
- Grafana datasource: `InfluxDB - Uptime Kuma`

Source path:

```text
scripts/monitoring/export_uptime_kuma_to_influx.py
```

Validation:

```sh
systemctl status uptime-kuma-influx-export.timer
cd /opt/monitoring
set -a
. ./.env
set +a
docker exec -e INFLUX_TOKEN="$INFLUXDB_TOKEN" influxdb influx query \
  'from(bucket: "uptimekuma") |> range(start: -10m) |> filter(fn: (r) => r._measurement == "uptime_kuma_monitor") |> limit(n: 5)' \
  --org homelab
```

### Fail2ban to InfluxDB

Live path:

- Script: `/usr/local/sbin/export_fail2ban_to_influx.sh` on docker-host
- Env file: `/etc/fail2ban-influx-export.env`
- Systemd timer: `fail2ban-influx-export.timer`
- InfluxDB bucket: `dockerhost`
- Grafana datasource: `InfluxDB - Docker Host`

Source path:

```text
scripts/monitoring/export_fail2ban_to_influx.sh
```

Validation:

```sh
systemctl status fail2ban-influx-export.timer
```

Run on monitoring VM:

```sh
cd /opt/monitoring
set -a
. ./.env
set +a
docker exec -e INFLUX_TOKEN="$INFLUXDB_TOKEN" influxdb influx query \
  'from(bucket: "dockerhost") |> range(start: -10m) |> filter(fn: (r) => r._measurement == "fail2ban") |> last()' \
  --org homelab
```

## Home Assistant availability

Current safe posture is direct links from Home Assistant, not embedded Grafana
iframes. The repo-side Lovelace snippet is:

```text
configs/home-assistant/lovelace/monitoring-grafana-links.yaml
```

Live HA dashboard update was not applied from this session because:

- HA API is reachable but requires authentication.
- HA VM has no QEMU guest agent configured.
- The existing HA Monitoring dashboard is storage-managed, so changing it
  safely requires either HA UI access or a deliberate HA dashboard deployment
  workflow.

Use the snippet in the HA UI Raw Configuration Editor or recreate the same
Markdown card manually on the existing Monitoring dashboard.

Do not make Grafana embedding a reliability dependency until same-origin HTTPS
and auth/cookie behavior are intentionally tested.

## Scope guardrails

- OMV/NAS metrics remain planned only until OMV exists.
- Frigate app telemetry remains planned only until cameras, RTSP, HTTPS, and
  audio requirements are ready.
- VentSys entity dashboards remain hardware-dependent until the devices are
  built, adopted, and explicitly revalidated.
