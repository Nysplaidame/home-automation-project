---
title: Monitoring and Logging Roadmap
description: Deployment order for health checks, uptime monitoring, metrics, alerts, and syslog
tags: [monitoring, logging, grafana, influxdb, telegraf, uptime-kuma]
created: 2026-05-08
modified: 2026-10-10
type: procedure
status: active
---

# Monitoring And Logging Roadmap

October10: [[resource_pressure_monitor]] is live on Proxmox every minute,
independent of VM102. It covers actual host/guest usable memory, cgroup limits,
new OOMs, CPU, disk/memory PSI, blocked tasks, capacity and kernel hang warnings
with authenticated ntfy alerts. VM102 now6GiB; VM103 root now128GiB. An hourly
Codex watchdog checks collector freshness/failure; handset presentation remains
an acceptance item. Existing Grafana/Kuma checks remain in place.

## Current live state

Status wording reconciled against [[../reference/current-live-state|Current Live
State]] and [[../../README|Project Overview]] on October4. Historical green
checks below describe their dated acceptance, not fresh uptime certification.
The Zyxel switch and three installed cameras are disconnected pending owner
reconnection/acceptance; Frigate's reachable baseline does not certify streams.

### Already live

- `scripts/monitoring/health_check.sh` as the immediate health probe
- selective OpenWrt firewall logging on key deny rules
- core services with stable addresses suitable for monitoring
- monitoring VM on VLAN 60 (`192.168.60.10`)
- `Uptime Kuma`
- `InfluxDB`
- `Grafana`
- `Telegraf`
- `Loki` for centrally retained application and container logs
- `Alloy` on docker-host for mTLS-protected log shipping

### Alert routing

- Centralized ntfy routing is deployed for configured Uptime Kuma monitors.
- Grafana's authenticated ntfy contact point and default notification policy
  are live, with initial docker-host disk and Proxmox storage alerts.

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
- Grafana dashboard shell `NAS Resource Overview` is present but remains a
  dashboard follow-up; OMV itself is live and monitored by web, NFS and SMART
  checks plus docker-host mount metrics.
- CT 114 `llm-host` is live. Uptime Kuma checks cover llama.cpp, Open WebUI,
  Wyoming Whisper, Piper and OpenWakeWord and are exported to InfluxDB.
- CT 111 Frigate retains its reachable API/UI baseline. Direct Kuma checks and
  HA offline/recovery alerts are configured for three installed cameras, which
  remain disconnected pending reconnection and acceptance. Do not label those
  camera streams healthy based on historical checks.
- OMV SMART and docker-host app-data backup freshness report through Kuma push
  monitors; both paths have accepted live heartbeats.
- Home Assistant has a storage-managed `Monitoring` dashboard at `/monitoring/overview` with direct links to Grafana and Uptime Kuma
- Homepage exposes one **Grafana** entry, which opens
  `/login?disableAutoLogin=true` through the same HTTPS proxy. An authenticated
  session persists in Homepage's embedded preview through Grafana's HTTPS-only
  `SameSite=None` session cookie. Grafana anonymous access is disabled, so an
  absent or expired session returns to the login form rather than silently
  opening an anonymous Viewer dashboard.
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
- `scripts/monitoring/health_check.sh` defaults to its maintained core checks.
  `--full` adds parked hardware/service expectations; use it only when those
  targets are intentionally online. OMV and Frigate baseline availability are
  live service facts. P1S integration is live; disconnected cameras and VentSys
  commissioning remain separate from service reachability.

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
- Frigate CT 111 baseline now; camera streams later
- NAS web/NFS and existing SMART push checks — live; host-local resource
  collection and dashboard delivery remain prepared/unaccepted
- llm-host CT 114 services: llama.cpp `8081`, Open WebUI `3002`, Piper
  `10200`, Whisper `10300`, and OpenWakeWord `10400`

### Phase 3 — add metrics with InfluxDB + Grafana

Use this when you want historical trends, not just “is it up”.

Primary targets:

- HA sensor history
- VentSys telemetry
- smart plug energy data
- Proxmox / VM resource usage
- docker-host resource usage
- llm-host resource usage, GPU use and local AI container memory

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
- Home Assistant monitoring dashboard: `https://192.168.20.101:8123/monitoring/overview`
- Docker-host/container metrics are folded into the Proxmox dashboard for now
  rather than creating a third dashboard, preserving the two-dashboard model:
  live infrastructure now, NAS-focused dashboard later.

## Monitoring posture consistency

- HA's Monitoring dashboard links directly to Grafana and Uptime Kuma.
  Homepage's authenticated Grafana HTTPS embedded preview is also live; its
  session/cookie behavior is distinct from embedding monitoring inside HA.
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
- llm-host CT metrics via Proxmox; add container-level collection if operationally useful
- monitoring VM Uptime Kuma exporter: monitor status/latency into bucket `uptimekuma`
- docker-host Fail2ban exporter: jail counters into bucket `dockerhost`

### Phase 5 — wire in alerting

Preferred progression:

1. Uptime Kuma notifications for core outages — live
2. Grafana alerts for selected thresholds / trends — initial rules live
3. authenticated self-hosted `ntfy` delivery — live; expand only with an
   explicit severity and routing policy

## Logging plan

### Router / firewall

- keep targeted deny logging where it adds security value
- forward OpenWrt syslog to the monitoring VM on `192.168.60.10:514/udp`
- Telegraf receives router syslog on container port `6514/udp` via Docker port mapping `192.168.60.10:514:6514/udp`

### Linux VMs

- keep native journald / service logs locally
- add centralized visibility later via Telegraf-backed collection

### Docker-host

- Docker and Bambuddy application logs are sent automatically to Loki on the
  monitoring VM by Alloy. Transport is TLS 1.3 with mutual certificate
  authentication and is firewall-scoped to docker-host (`192.168.20.102`) to
  Loki (`192.168.60.10:3100`).
- Use Grafana **Explore** with the `Loki` datasource for normal browser-based
  reading; Dozzle remains useful as a live, docker-host-only fallback.
- Grafana reaches Loki through an internal-only query proxy which is itself an
  mTLS client. The Grafana datasource therefore contains no private key.
- Grafana's provisioned **Central Logs** dashboard includes focused Bambuddy
  error output, focused docker-host error output, OpenWrt warning/error syslog,
  and the unfiltered Bambuddy and docker-host log tables. Use a panel's
  **Explore** action for surrounding context and arbitrary Loki queries.
- Grafana's provisioned **Infrastructure Fleet** dashboard provides a concise
  current view of the five running Proxmox guests, Proxmox CPU, docker-host root
  disk usage, active guest state, and guest CPU history. It links to the deeper
  `Proxmox Resource Overview`; no in-guest collector was installed for this
  view.

### Next central collection stages

Keep collection least-privilege and host-local. Do not make Grafana poll a
guest's service ports or grant it general SSH access.

1. Proxmox: ship task, backup, replication, and host journal events through a
   dedicated read-only collector/API token; retain guest resource metrics from
   the existing native Proxmox metric server.
2. Home Assistant and Frigate: collect their local application/service logs
   with a supported host-local mechanism, preserving the current VLAN rules and
   without copying secrets or camera stream URLs into Loki.
3. LLM host: collect systemd/service logs for llama.cpp, Open WebUI, Piper,
   Whisper, and OpenWakeWord from CT 114.
4. OMV: existing desktop key administration access was verified October2;
   keep that access separate from collection. Accept and install a
   dedicated Telegraf/Alloy collector for host, filesystem, RAID, SMART,
   SMB/NFS, backup, and Transfer Portal logs. Only then replace the intentional
   NAS dashboard shell with a live NAS resource overview.

October4 OMV preparation supplies the host-local `omv-health/1.0` collector,
atomic publisher, stdout conversion, dedicated consumer input fragments and
three guarded current-state/unit Flux queries. Eighteen Linux tests, five
Telegraf parser cases and19 synthetic Flux cases (32 executions) pass. October2's
one-off read-only observation remains historical, not current health. No
scheduled collector or metric shipping is deployed; real consumer permissions,
delivery, alert/rendering and NAS panel acceptance remain open. Log/backup
coverage is a separate contract.
See [[omv-health-collector-preparation|contract, live evidence and deployment boundaries]].

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

- expand the already-live docker-host Loki/Alloy visibility to the remaining
  host/application sources before adding log-driven blocking
- add `Fail2ban` on Frigate and other Linux-exposed services where it adds value
- evaluate `CrowdSec` if log-driven automated blocking becomes useful
- evaluate `Suricata` only on dedicated x86 hardware if true network IDS/IPS becomes a real goal

### Maybe never

- running heavyweight IDS/IPS directly on the GL-MT6000 router
- deploying enterprise-scale security stacks such as full Wazuh/ELK unless operational complexity is clearly worth it

## Current answer

As of August 25, 2026:

- true IDS: not deployed
- true IPS: not deployed
- host-based banning: docker-host and CT 111 Frigate SSH baselines are deployed;
  October4 read-only CT114 inspection still finds Fail2ban absent, no HTTP APT
  proxy and blocked/unavailable cache paths. Prepared repair remains
  maintenance-gated under [[ct114-package-path-repair]].
- security foundations: segmentation, OpenWrt/host/Docker firewall rules,
  explicit Compose bridge allocations, scoped Tailscale access, dormant
  WireGuard fallback, selective logging, Grafana/Kuma visibility and ntfy alert
  delivery

## Success criteria

The monitoring stack is “good enough” when:

- service outages are visible quickly
- HA, Proxmox, docker-host, and Frigate have basic uptime checks
- historical metrics exist for HA / VentSys / core hosts
- router syslog reaches a central place
- alerts go somewhere you will actually notice

## November10 identity monitor and access review

VentSys identity checks and continuous MQTT evidence capture now run on VM102 via enabled `ventsys-monitor.service`; the desktop heartbeat is paused and collector stopped. See [[ventsys-temporary-mqtt-logging]] for service paths, credentials, validation, incident-only ntfy notifications and temporary logging rollback.

[[../audits/2026-11-10-monitoring-network-access|Monitoring network audit]] found missing VM102 router access to MQTT8883, ntfyHTTPS8193, HomepageHTTPS443, Hub8100 and four already monitoring-approved media/download endpoints. No router rules were changed. Additional health checks for newer services are absent from Kuma. OMV SMART heartbeat was repaired by preserving its existing allowance in the full Docker firewall rebuild and ordering the augmentation unit after it; sender and Kuma recovery verified.

November10 follow-up: confirmed MQTT/HTTPS/Hub/media/download access gaps are now closed with VM102-specific router rules and HTTPS host rules. Both VentSys functions moved from interim VM103 to VM102; old dedicated installation and key were removed. Additional Kuma service checks and Homepage metric integration remain tasks.


## November11 Kuma coverage and Homepage work

Kuma monitors37–44 were created for Jellyfin Health, Calibre-Web, Household
Hub, qBittorrent UI, Homepage HTTPS, ntfy HTTPS, Atsumeru and HA MQTT TLS Port.
Latest checks all pass. Atsumeru accepts its HTTP401 authentication challenge.
The MQTT Kuma check tests TCP8883 reachability. The independent VentSys service
continues to validate an authenticated TLS MQTT subscription.

Kuma now mounts the existing Home Local CA at `/etc/ssl/home-local-ca.crt`
and sets `NODE_EXTRA_CA_CERTS`. Its two new HTTPS checks pass with TLS
verification enabled. Compose source is current. Protected rollback checkpoint
on VM102 is `/root/kuma-homepage-20261111/` with SQLite backup and prior Compose.

Only Jellyfin37 and Calibre38 currently have ntfy Monitoring enabled and two
retries. The remaining six notification routes and retry settings require the
owner's signed-in browser. Owner requested doing browser actions themselves.

Homepage source now contains a Service Health group on the Home tab using the
native uptimekuma widget with slug `home-operations`, fields up/down/uptime/
incident, and a status-page link through8186. YAML validates. This source
change is prepared and has not been deployed. Kuma has no saved status page
at this checkpoint. Owner needs to create Home Operations / home-operations,
add all monitors in a group, and save with monitor URLs hidden. Then deploy
the narrow Homepage additions, revalidate and verify the widget response.


November11 follow-up: the owner saved status page `home-operations`, with all
43 monitors in its Services group and monitor URLs hidden. The prepared native
widget was deployed to the Homepage Home tab in Service Health, with a backup at
`/opt/backups/homepage-kuma-20261111/`. YAML and Homepage revalidation passed;
Homepage services API includes the widget and Kuma heartbeat API returns all
43 monitors. Browser display verification remains pending. At verification,
monitors39–44 still had no ntfy route and zero retries; owner was asked to
complete those six through Kuma. Do not claim notification setup complete.

November11 final verification: owner completed ntfy and retry settings for
monitors39–44 and checked Homepage. All eight monitors37–44 have ntfy route1,
two retries and latest status Up. Home Operations status API reports40 Up and
3 Down, the latter the known disconnected cameras. Homepage services API
contains the deployed widget. Notification server delivery and phone display
remain separate acceptance checks. Roll back the card by restoring the backed-up
services.yaml and settings.yaml in `/opt/backups/homepage-kuma-20261111/`, then
call Homepage `/api/revalidate` with an allowed Host header.
