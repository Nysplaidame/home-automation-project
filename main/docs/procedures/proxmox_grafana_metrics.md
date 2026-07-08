---
title: Proxmox Grafana Metrics
description: Native Proxmox metric export into InfluxDB v2 and Grafana dashboard state
tags: [proxmox, grafana, influxdb, monitoring, metrics]
created: 2026-05-29
modified: 2026-05-31
type: procedure
status: active
---

# Proxmox Grafana Metrics

Proxmox exports native host, guest, and storage metrics directly to InfluxDB v2.
Grafana reads those metrics through a dedicated datasource.

## Live state

- Proxmox metric server ID: `proxmox-influx`
- Proxmox config: `/etc/pve/status.cfg`
- Proxmox token storage: `/etc/pve/priv/metricserver/proxmox-influx.pw`
- InfluxDB organization: `homelab`
- InfluxDB bucket: `proxmox`
- Bucket retention: `90d`
- Grafana datasource: `InfluxDB - Proxmox`
- Grafana datasource UID: `influxdb-proxmox`
- Docker-host InfluxDB bucket: `dockerhost`
- Docker-host Grafana datasource: `InfluxDB - Docker Host`
- Docker-host Grafana datasource UID: `influxdb-dockerhost`
- Grafana dashboard: `Proxmox Resource Overview`
- Grafana dashboard URL: `http://192.168.60.10:3000/d/proxmox-resource-overview/proxmox-resource-overview`
- Grafana paired NAS dashboard shell: `NAS Resource Overview`
- Grafana NAS dashboard URL: `http://192.168.60.10:3000/d/nas-resource-overview/nas-resource-overview`

Validation note, 2026-05-31:

- Grafana anonymous dashboard search did not list `Proxmox Resource Overview`,
  although the datasource and InfluxDB bucket remain queryable through Grafana.
- Grafana admin API access confirmed the dashboard is live and saveable.
- Source export now lives at
  `configs/grafana/dashboards/proxmox-resource-overview.json`.
- Live dashboard version `6` labels the formerly ambiguous percentage panels as
  `Guest RAM`, `RAM Pressure`, and `Root Disk`.
- The ambiguous high VM percentages currently read as Proxmox guest memory
  usage (`mem / maxmem`), not CPU or disk. Current samples were:
  Home Assistant about `98%`, docker-host about `91%`, monitoring about `85%`,
  and Frigate about `18%`.
- Proxmox host CPU was about `0.5%`, Proxmox RAM pressure was about `37%`, root
  storage was about `45%`, and `local-lvm` was about `6%`.
- Docker-host in-guest Telegraf reported memory `used_percent` about `59%` and
  root filesystem about `52%`, so the docker-host Proxmox `91%` guest-memory
  card is cache-inclusive and not an immediate capacity concern by itself.

## Validation

Run on: Proxmox host.

```sh
pvesh get /cluster/metrics/server/proxmox-influx
curl -sS http://192.168.60.10:8086/health
```

Run on: monitoring VM.

```sh
cd /opt/monitoring
set -a
. ./.env
set +a
docker exec -e INFLUX_TOKEN="$INFLUXDB_TOKEN" influxdb influx query \
  'from(bucket: "proxmox") |> range(start: -10m) |> limit(n: 5)' \
  --org homelab
```

Run on: docker-host VM.

```sh
cd /opt/stacks/telegraf
docker compose ps
```

Run on: monitoring VM.

```sh
cd /opt/monitoring
set -a
. ./.env
set +a
docker exec -e INFLUX_TOKEN="$INFLUXDB_TOKEN" influxdb influx query \
  'import "influxdata/influxdb/schema" schema.measurements(bucket: "dockerhost")' \
  --org homelab
```

## Dashboard scope

The Proxmox dashboard uses the shared wallboard visual style and focuses on
live infrastructure only:

- Proxmox node CPU
- Proxmox RAM pressure (`(memtotal - memavailable) / memtotal`)
- reporting VM count
- root storage usage (`local`)
- VM storage usage (`local-lvm`)
- per-VM CPU
- per-VM guest memory (`mem / maxmem`; label this explicitly, because it can
  appear high when the guest is using RAM for cache)
- per-VM network throughput
- per-VM disk throughput
- current VM status table
- docker-host CPU, RAM, root filesystem use, Docker container counts, and image counts
- docker-host host CPU/RAM history
- docker-host per-container CPU, RAM, network throughput, and status table
- CT 114 `llm-host` CPU, RAM, disk, and container memory after Phase 05A is
  deployed and local AI performance testing passes

The paired `NAS Resource Overview` dashboard is a planned shell only. It exists
to reserve the second dashboard entry and visual direction, not to imply that
OMV/NAS metrics are live.

Future NAS telemetry should prefer the existing monitoring pattern first:

- Telegraf on the NAS writing to InfluxDB.
- Existing InfluxDB/Grafana stack for storage, disk, network, and service panels.
- Additional containers only when a specific metric cannot be collected cleanly
  through Telegraf or a native host exporter.

## Docker-host collector state

Docker-host telemetry is collected by a Telegraf container at
`/opt/stacks/telegraf` on VM 103. Rebuildable non-secret templates live under
`configs/docker-host/stacks/telegraf/`.

Live secret material:

- Docker-host Telegraf write token: `/opt/stacks/telegraf/.env` on VM 103
- Grafana Docker-host read token: stored in Grafana datasource secure storage
- Token source files on monitoring VM: `/root/dockerhost-telegraf-write.token`
  and `/root/grafana-dockerhost-read.token`

The first deployment used offline Docker image transfer:

```sh
ssh root@192.168.60.10 'docker save telegraf:latest' | \
  ssh root@192.168.20.102 'docker load'
```

This avoided opening broad docker-host registry access just to deploy the
collector.

Current baseline as of 2026-07-06:

- OMV is live on VLAN 40, `omv-backups` is active, and the old 86-87% capacity
  warning has been cleared by the 2026-07-05 Proxmox check.
- Frigate is live on CT 111 with one ANNKE bench camera, HA integration and
  HTTPS UI; broader camera rollout remains near-term hardware follow-up.
- CT 114 local AI runtime is live and monitored.
- VentSys physical entities remain unbuilt until hardware is adopted and
  explicitly revalidated.

## Memory interpretation

The Proxmox host currently has about `31 GiB` RAM (`33,107,255,296` bytes).
Linux may use free memory for cache, so the dashboard uses available memory to
show pressure rather than treating cache as unavailable. A `RAM Pressure` value
around one third means the hypervisor is not maxed out.

For VM cards and rows, do not display a bare percent without a metric label.
Use labels such as `CPU`, `Guest RAM`, `Root Disk`, or `Storage` so high
guest-memory values are not mistaken for host CPU or disk saturation.

## Prometheus note

Prometheus is an alternative scrape-based metrics database. It is useful when
many services expose `/metrics` endpoints or when exporter ecosystems become
important. It is not required for the current Proxmox dashboard because Proxmox
already exports native metrics directly to InfluxDB.
