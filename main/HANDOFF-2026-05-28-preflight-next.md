# Handoff - 2026-05-28 Pre-flight Next Steps

Use this handoff to start a new conversation without replaying the recent router,
Proxmox, Home Assistant, docker-host, monitoring, and search-service setup work.

## Start Here

Repository root:

```text
G:\home-automation-project
```

Active project tree:

```text
G:\home-automation-project\main
```

Read these first in the new conversation:

1. `README.md`
2. `main/README.md`
3. `main/PROJECT-INDEX.md`
4. `main/TO-DO.md`
5. This file
6. `main/HANDOFF-2026-05-07-current.md` only if deeper live-state detail is needed

Do not bulk-read the repository. Use `main/PROJECT-INDEX.md` to navigate.

## Current Git State

As of this handoff, the local branch was clean and aligned with origin:

```text
## main...origin/main
```

Recent pushed commits include the docker-host rebuild templates, router-only
deployment documentation, Home Assistant Companion App validation, search-service
candidates, live SearXNG/Whoogle pre-flight deployment, Grafana dashboard
source exports, docker-host/Frigate Fail2ban hardening, mobile monitoring route
prep, and VentSys dashboard/valve actuation fixes.

## Human-Input Sprint - Start Here Next

The next work target is to clear every currently-known item that needs the
operator's hands, phone, UI session, hardware choice, or approval. Do these
before opening another broad service deployment thread.

1. Approve and test the new Tailscale monitoring route.
   - docker-host already advertises `192.168.60.10/32`.
   - docker-host already has routed UFW allowances for Grafana `3000` and Uptime
     Kuma `3001`.
   - User action: in the Tailscale admin console, approve `192.168.60.10/32` if
     it is pending for `docker-host`, then test from mobile data:
     `http://192.168.60.10:3000` and `http://192.168.60.10:3001`.
   - Context docs:
     - `main/docs/procedures/tailscale_remote_access_guide.md`
     - `main/docs/troubleshooting/troubleshooting_reference.md`
     - `main/docs/reference/access-matrix.md`
     - `main/docs/reference/service-matrix.md`

2. Apply the HA Monitoring dashboard direct-link snippet.
   - User action: use the Home Assistant UI to apply
     `main/configs/home-assistant/lovelace/monitoring-grafana-links.yaml` to the
     live Monitoring dashboard, or recreate the same Markdown card manually.
   - HA embedding remains parked; this is direct links only.
   - Context docs:
     - `main/docs/procedures/grafana_architecture_dashboards.md`
     - `main/configs/home-assistant/lovelace/monitoring-grafana-links.yaml`
     - `main/docs/procedures/home_assistant_companion_app_guide.md`

3. Decide whether to run the docker-host patch window now.
   - User action: approve timing for a controlled maintenance window.
   - Codex can execute the runbook over SSH once approved.
   - Context docs:
     - `main/docs/procedures/docker_host_patch_window_runbook.md`
     - `main/docs/procedures/update_review_log.md`
     - `main/docs/procedures/update_maintenance_playbook.md`

4. VentSys physical checks that still need the user.
   - User action: check whether the HA live copies match the repo/source copies,
     then report back.
   - User action: inspect main valve 2 wiring/power; logs suggested the device
     was not powering or actuating, not merely a dashboard/control bug.
   - Context docs:
     - `main/docs/procedures/ventsys_esphome_tls_rollout_guide.md`
     - `main/docs/procedures/ssl_tls_guide.md`
     - `main/ventsys/ventsys_bundle_updated/ventsys_ha_scripts.yaml`
     - `main/dashboards/ventsys-dashboard.html`

5. Hardware-dependent gates to keep visible but not force.
   - NAS/OMV: still unbuilt; do not configure HA backups, Immich real library, or
     Frigate NAS archive until OMV hardware/storage exists.
   - Frigate app: do not start for regular use until camera models, RTSP URLs,
     HTTPS/SSL, and WebRTC audio decisions are ready.
   - Camera/Lumen/kiosk/mobile hardware items remain user-selection or
     hardware-arrival tasks.
   - Context docs:
     - `main/docs/procedures/omv_storage_cutover_checklist.md`
     - `main/docs/procedures/omv_cutover_execution_runbook.md`
     - `main/scripts/setup/proxmox/frigate_vm_setup_guide.md`
     - `main/TO-DO.md`

## Network Position

The laptop is expected to be on the GL-MT6000 management side, normally through
`lan2` or another management-access path.

Known infrastructure addresses:

- Router management: `192.168.10.1`
- Proxmox: `192.168.10.10`
- Home Assistant: `192.168.20.101`
- Docker host: `192.168.20.102`
- Monitoring VM: `192.168.60.10`
- Frigate VM: `192.168.30.20`

Router SSH:

```powershell
ssh -i G:\home-automation-project\main\tools\router-deploy\keys\router_deploy root@192.168.10.1 '<cmd>'
```

Proxmox SSH:

```powershell
ssh -i $env:USERPROFILE\.ssh\proxmox_admin_ed25519 root@192.168.10.10
```

Docker host SSH:

```powershell
ssh -i $env:USERPROFILE\.ssh\id_ed25519_codex_ha -o IdentitiesOnly=yes root@192.168.20.102
```

Monitoring VM SSH:

```powershell
ssh -i $env:USERPROFILE\.ssh\id_ed25519_codex_ha -o IdentitiesOnly=yes root@192.168.60.10
```

HAOS SSH using the Proxmox key previously failed with `Permission denied
(publickey)`, so Home Assistant live validation may need the HA UI, Terminal &
SSH add-on, or user-provided access.

Note, 2026-05-31: Proxmox root SSH works from this laptop, and QEMU guest agents
were alive on VMs `102` and `103`. The Codex laptop key was injected into both
VMs through Proxmox guest-agent, so direct root SSH to docker-host and monitoring
now works with `id_ed25519_codex_ha`.

## Important Live State

The GL-MT6000/OpenWrt router is live and stable on `192.168.10.1`, but it is
still staged behind the existing home router rather than acting as the final
internet edge.

Temporary router WiFi uplink:

- `wwan_uplink` is enabled.
- It connects to `ZyXEL_F1E9`.
- Router-side DHCP address was recorded as `192.168.1.143`.
- Upstream gateway is `192.168.1.254`.
- SearXNG and Whoogle pre-flight search depend on this uplink while the GL-MT6000
  is not the final internet edge.

Physical router port intent:

- `lan1`: trunk to Proxmox
- `lan2`: management VLAN 10
- `lan3`: NVR VLAN 30, future managed PoE camera switch
- `lan4`: storage VLAN 40
- `lan5`: recovery/LAN VLAN 1

## Live Services

Proxmox:

- Host is live at `https://192.168.10.10:8006`.
- VMs `100`, `101`, `102`, and `103` are expected to be running.
- Temporary local Proxmox backups are scheduled daily at `02:00`, keep `2`, until
  NAS storage exists.

Home Assistant:

- HAOS VM 100 is live at `192.168.20.101:8123`.
- Mosquitto MQTT is live with TLS listener on `8883`.
- Plain MQTT `1883` should be treated as deprecated; 2026-05-28 Frigate-path
  probe to `192.168.20.101:1883` returned closed/refused.
- VentSys packages and dashboard are staged.
- Companion App service `notify.mobile_app_mai_foenn` is registered.
- Basic push notification and actionable notification acknowledgement were
  tested successfully.

Monitoring:

- Monitoring VM 102 is live at `192.168.60.10`.
- Uptime Kuma, Grafana, InfluxDB, and Telegraf are running.
- Uptime Kuma has green monitors for core infrastructure and docker-host services.
- Uptime Kuma notification `ntfy Monitoring` is active and mapped to active
  monitors.
- Grafana/Influx are usable directly; HA embedding remains not fully stable.
- Proxmox native metric export is live through metric server `proxmox-influx`,
  writing to InfluxDB bucket `proxmox`.
- Grafana datasource `InfluxDB - Proxmox` and dashboard `Proxmox Resource
  Overview` are live at
  `http://192.168.60.10:3000/d/proxmox-resource-overview/proxmox-resource-overview`.
- `Proxmox Resource Overview` now uses the shared wallboard visual style.
- `Proxmox Resource Overview` live dashboard version `6` now labels formerly
  ambiguous percentage panels as `Guest RAM`, `RAM Pressure`, and `Root Disk`.
- Source export now exists at
  `main/configs/grafana/dashboards/proxmox-resource-overview.json`.
- Docker-host Telegraf is live under `/opt/stacks/telegraf` on VM 103, writing
  host/container metrics to InfluxDB bucket `dockerhost`.
- Grafana datasource `InfluxDB - Docker Host` is live, and Docker-host/container
  panels are folded into `Proxmox Resource Overview`.
- Grafana datasource `InfluxDB - Uptime Kuma` is live, backed by InfluxDB bucket
  `uptimekuma`.
- Architecture dashboards are live:
  - `Service Availability`:
    `http://192.168.60.10:3000/d/service-availability-overview/service-availability`
  - `Network DNS`:
    `http://192.168.60.10:3000/d/network-dns-overview/network-dns`
  - `Security Posture`:
    `http://192.168.60.10:3000/d/security-posture-overview/security-posture`
- `NAS Resource Overview` exists as a planned Grafana dashboard shell at
  `http://192.168.60.10:3000/d/nas-resource-overview/nas-resource-overview`;
  it should not be treated as live NAS telemetry until the NAS is built.

Docker host:

- VM 103 is live at `192.168.20.102`.
- VM size is currently 2 cores, 4096 MiB RAM, 32 GiB disk.
- Rebuildable non-secret templates live under `main/configs/docker-host/`.
- `fail2ban` is installed/enabled with active `sshd` jail and baseline config at
  `/etc/fail2ban/jail.d/docker-host-sshd.local` (template:
  `main/configs/docker-host/system/docker-host-fail2ban-sshd.local`).
- Docker-host Telegraf runs as `docker-host-telegraf` from `/opt/stacks/telegraf`.
- Rebuildable Docker-host Telegraf templates are in
  `main/configs/docker-host/stacks/telegraf/`.
- docker-host Fail2ban counters export through `fail2ban-influx-export.timer`
  into InfluxDB bucket `dockerhost`.
- Tailscale currently advertises `192.168.20.101/32`, `192.168.40.50/32`, and
  `192.168.60.10/32`.
- UFW routed rules allow Tailscale clients to reach only monitoring VM Grafana
  `3000` and Uptime Kuma `3001`; InfluxDB `8086` is intentionally not exposed
  over this daily mobile route.
- Rebuildable source for those monitoring route rules:
  `main/configs/docker-host/system/docker-host-ufw-route-monitoring-tailscale.sh`.
- Secrets, app databases, ntfy auth DB, AdGuard password hash, and generated
  service secrets remain live-only and must not be committed.

Live docker-host services:

- Bambuddy UI: `http://192.168.20.102:8000`
- Homepage: `http://192.168.20.102:3001`
- Dozzle: `http://192.168.20.102:8081`
- AdGuard Home UI: `http://192.168.20.102:8080`
- AdGuard DNS: `192.168.20.102:53`
- Immich skeleton: `http://192.168.20.102:2283`
- ntfy: `http://192.168.20.102:8085` and `http://ntfy.home.local:8085`
- SearXNG: `http://192.168.20.102:8087` and `http://searxng.home.local:8087`
- Whoogle: `http://192.168.20.102:8088` and `http://whoogle.home.local:8088`
- Watchtower is monitor-only with no exposed HTTP UI.
- Docker-host Telegraf has no exposed HTTP UI; it writes metrics to
  `192.168.60.10:8086`.
- Uptime Kuma state exports through `uptime-kuma-influx-export.timer` on the
  monitoring VM; this feeds the `Service Availability` Grafana dashboard.

Search-service state:

- SearXNG and Whoogle are direct-access pre-flight deployments.
- They are not yet behind a reverse proxy.
- Reverse proxy/HTTPS is intentionally deferred; direct access is acceptable for
  internal pre-flight.
- Both have Uptime Kuma monitors and Homepage links.

## Recent Validations

Router deployment after search-service DNS/firewall additions succeeded.

Connectivity validation:

```text
test-connectivity.ps1 -RouterIp 192.168.10.1
PASS=85 WARN=0 FAIL=0
```

Validation snapshot run on 2026-05-28 after uplink-policy documentation update:

```text
python main\tools\router-deploy\lint.py -> PASSED: all checks clean
python main\tools\router-deploy\compile.py --profile first-flight -> OK artifacts generated
main\tools\router-deploy\test-connectivity.ps1 -RouterIp 192.168.10.1 -> PASS=85 WARN=0 FAIL=0
```

Pre-flight sweep run on 2026-05-28 (steps 1-4 and 6-8, excluding MQTT migration planning):

- Router/source parity rechecked: `lint` clean, `compile --profile first-flight`
  produced artifacts, `test-connectivity` remained `PASS=85/WARN=0/FAIL=0`.
- `wwan_uplink` confirmed enabled/up with staged upstream DHCP (`192.168.1.143`)
  and gateway (`192.168.1.254`).
- Live firewall remains TLS-oriented for MQTT (`8883` rules active for Bambuddy,
  Frigate, and VentSys IoT-to-HA path; no valve-specific plain `1883` exception).
- docker-host UFW routed DNS rules were normalized to subnet-based entries for
  `172.20.0.0/16 -> 53/udp,53/tcp,853/tcp`; duplicate interface-scoped entries
  were removed.
- At the time of the 2026-05-28 sweep, Tailscale advertised only
  `192.168.20.101/32` and `192.168.40.50/32`; this was superseded on
  2026-05-31 when `192.168.60.10/32` was added for Grafana/Kuma mobile access.
- Router WireGuard remains dormant (`network.wg0.auto='0'`, interface down).
- Monitoring endpoints are directly reachable from management:
  - Grafana `http://192.168.60.10:3000/api/health` -> `200`
  - InfluxDB `http://192.168.60.10:8086/health` -> `200`
  - Uptime Kuma `http://192.168.60.10:3001/` -> `302`
- HA-side entity-state confirmation is complete via Home Assistant UI:
  - `binary_sensor.monitoring_stack_externally_healthy` = `on`
  - `binary_sensor.monitoring_vm_grafana_reachable` = `on`
  - `binary_sensor.monitoring_vm_influxdb_reachable` = `on`
  - `binary_sensor.uptime_kuma_reachable_from_ha` = `on`
- Controlled outage test: Whoogle was stopped and Uptime Kuma logged repeated
  failures, then Whoogle was restored (`HTTP 200`).
- Uptime Kuma -> ntfy dispatch was validated in a follow-up outage test:
  ntfy `messages_published` increased from `14` to `15` during the monitor-17
  failure window.
- Frigate pre-flight status on VM 101:
  - `/opt/frigate/.env` is staged with MQTT secret set; RTSP password remains
    a placeholder until camera selection
  - `/opt/frigate/certs/ca-cert.pem` is staged and validates against
    `192.168.20.101:8883` (`Verify return code: 0`)
  - MQTT TLS path reachable: `192.168.20.101:8883` open
  - Plain MQTT path not reachable: `192.168.20.101:1883` closed
  - Fail2ban is installed/enabled with active `sshd` jail at
    `/etc/fail2ban/jail.d/frigate-nvr-sshd.local`; status on 2026-05-30 was
    `0` failed and `0` banned
- Proxmox backup preflight:
  - Job enabled daily at `02:00`, `keep-last=2`, VMs `100,101,102,103`
  - Latest 2026-05-28 artifacts present for all four VMs in `/var/lib/vz/dump`
  - Restore-readiness drill passed on latest VM `100/101/102/103` backups:
    each archive passed `zstd -t`, and each matching `2026-05-28` backup log
    contains `Finished Backup`

SearXNG direct search and Whoogle UI/search tests returned HTTP `200`.

Pre-flight metrics pass on 2026-05-29:

- Router source updated with narrow `Docker Host to InfluxDB` rule
  (`192.168.20.102` -> `192.168.60.10:8086`) and live rule confirmed.
- Router deploy validation stayed green:
  `test-connectivity.ps1 -RouterIp 192.168.10.1 -> PASS=85/WARN=0/FAIL=0`.
- Docker-host Telegraf deployed by transferring `telegraf:latest` from the
  monitoring VM with `docker save/load`, avoiding broad registry egress.
- InfluxDB bucket `dockerhost` and scoped tokens created.
- Grafana datasource `InfluxDB - Docker Host` created.
- `Proxmox Resource Overview` now includes Docker-host CPU/RAM/root disk,
  Docker container/image counts, per-container CPU/RAM/network, and container
  status panels.
- `health_check.sh` storage parsing fixed; final run reported `ALL OK 11/11`
  with Proxmox storage `local 41%` and `local-lvm 5%`.
- docker-host Fail2ban sshd jail remained quiet: `0` failed, `0` banned.

Architecture dashboard pass on 2026-05-29:

- Created `Service Availability`, `Network DNS`, and `Security Posture`
  dashboards in Grafana.
- Added source exports under `main/configs/grafana/dashboards/`.
- Added Uptime Kuma SQLite-to-Influx exporter:
  `scripts/monitoring/export_uptime_kuma_to_influx.py`.
- Added docker-host Fail2ban-to-Influx exporter:
  `scripts/monitoring/export_fail2ban_to_influx.sh`.
- Added HA Lovelace direct-link snippet:
  `configs/home-assistant/lovelace/monitoring-grafana-links.yaml`.
- Live HA dashboard update was not applied from the session because HA API
  required auth and VM 100 has no QEMU guest agent; apply the Lovelace snippet
  via the HA UI Monitoring dashboard when convenient.

Documentation/wiki audit on 2026-05-30:

- Canonical docs were audited against the current monitoring/Grafana/exporter,
  docker-host Fail2ban, Tailscale/WireGuard, Frigate, OMV, and VentSys planning
  state.
- The wiki was updated to match project docs, including docker-host Tier 1 live
  state, direct-link monitoring posture, MQTT TLS posture, Frigate staging
  guardrails, and VentSys hardware revalidation guardrails.
- Filed the wiki lint report at `wiki/pages/analyses/lint-2026-05-30.md`.
- Validation after edits:
  - `python main\tools\router-deploy\lint.py` -> PASSED
  - `python main\tools\router-deploy\compile.py --profile first-flight` -> OK
  - `python -m py_compile main\scripts\monitoring\export_uptime_kuma_to_influx.py` -> OK
  - active `main/` wikilinks -> 0 unresolved after excluding code blocks/examples

Frigate Fail2ban hardening on 2026-05-30:

- Added docker-host patch-window runbook at
  `docs/procedures/docker_host_patch_window_runbook.md`.
- Added Frigate Fail2ban template at
  `configs/frigate/system/frigate-nvr-fail2ban-sshd.local`.
- Installed Fail2ban on VM 101 and deployed the template to
  `/etc/fail2ban/jail.d/frigate-nvr-sshd.local`.
- Validation: `systemctl is-active fail2ban` -> `active`;
  `fail2ban-client status sshd` -> `0` failed, `0` banned.
- Temporary router update rules used during package install were removed.
- Note: the first `apt-cacher-ng` package fetch attempt failed under the current
  staged-uplink posture; cached `.deb` packages were copied from docker-host as
  a fallback and the install then completed successfully.

Monitoring/mobile route and Grafana label pass on 2026-05-31:

- Proxmox guest-agent was used to grant this laptop direct root SSH to
  docker-host and monitoring VM with `id_ed25519_codex_ha`.
- docker-host Tailscale route advertisement updated to include
  `192.168.60.10/32`.
- docker-host UFW route rules added:
  - `tailscale0 -> eth0 -> 192.168.60.10:3000/tcp`
  - `tailscale0 -> eth0 -> 192.168.60.10:3001/tcp`
- Tailscale admin console approval may still be required for the new route.
- Grafana admin credentials were read locally on the monitoring VM from
  `/root/monitoring-stack-credentials.txt` without exposing secrets in chat.
- Grafana API confirmed `Proxmox Resource Overview`, `Home Automation Overview`,
  and `NAS Resource Overview` are saveable with admin credentials.
- `Proxmox Resource Overview` panels were relabelled live/source:
  - `Home Assistant Guest RAM`
  - `Monitoring Guest RAM`
  - `docker-host Guest RAM`
  - `Frigate Guest RAM`
  - `RAM Pressure`
  - `Docker Host Root Disk`
- Validation:
  - dashboard JSON parses
  - YAML/frontmatter parses
  - live UFW helper script passes `bash -n`
  - worktree was clean after commit/push

VentSys/dashboard pass on 2026-05-31:

- Dashboard node live counter now uses configured node list/diagnostic status
  instead of counting all HA entities for configured nodes.
- Valve visual/control logic now treats configured open position (`50`, i.e.
  90 degrees) as fully open for main valve 1.
- Mode animations still step visually, but HA script publishing now sends direct
  target commands instead of stepped actuation.
- Source docs/configs updated:
  - `main/dashboards/ventsys-dashboard.html`
  - `main/dashboards/ventsys-config.js.example`
  - `main/ventsys/ventsys_bundle_updated/ventsys_ha_scripts.yaml`
  - `main/docs/procedures/ventsys_esphome_tls_rollout_guide.md`

HA Companion App:

- `notify.mobile_app_mai_foenn` received a test notification.
- Actionable notification acknowledgement event worked.
- If testing events in the HA UI, the listener stops when navigating away from
  Developer Tools -> Events.

## Cautions

Router deploy tooling is intended for router configuration only. Do not use
`main/tools/router-deploy/` as a general deployment mechanism for Proxmox,
Home Assistant, docker-host, or monitoring services.

Do not remove or disable the temporary `wwan_uplink` unless the effect on
SearXNG/Whoogle internet search and image/package pulls is understood.

Do not switch HA to HTTPS casually. Certificate files are staged, but enabling
HTTPS affects browser trust, Companion App URLs, dashboards, and token-using
clients.

Do not deploy `configs/home-assistant/bambuddy_p1s_package.yaml` yet. It still
depends on real P1S details, confirmed MQTT topics, and placeholder replacement.

Do not import a real photo library into Immich until OMV-backed storage and
backup/restore procedures are ready.

Do not start Frigate for regular use until camera RTSP details, `.env`, MQTT
credentials/certs, HTTPS/SSL, and WebRTC audio requirements are resolved.

## Best Next Tasks

The next conversation should complete the human-input sprint above before
starting another big service. Keep the work narrow and close tasks as soon as
the user provides the necessary UI approval, mobile test result, timing approval,
or hardware observation.

Recommended order:

1. Tailscale admin route approval and mobile test for Grafana/Kuma.
2. HA UI application of the Monitoring dashboard direct-link snippet.
3. Decide/execute docker-host patch window if the user approves timing.
4. Record user-reported VentSys HA-copy and valve-2 wiring findings, then act on
   any software/docs follow-up.
5. Keep Grafana/Kuma embedding parked behind direct-link usage until HTTPS/same-origin path is intentionally implemented.
6. Keep WireGuard dormant fallback posture unless there is a deliberate decision
   to roll out fallback clients.
7. Keep Mullvad egress hardening for SearXNG/Whoogle parked until storage and
   backup priorities are complete.

## Possible App Candidates After Tightening

Once the drift/operational items above are handled, likely next docker-host app
candidates are:

- Paperless-ngx: useful, but needs storage/backup thinking before real documents.
- Mealie: easy internal app candidate, lower risk than document/password services.
- Actual Budget: useful, but finance data means backup/auth review first.
- Scrypted: camera-adjacent; probably wait until camera hardware decisions.

Vaultwarden should remain gated behind a serious backup/security review.
Portainer should remain optional because it adds an admin surface.

## One-Line Continuation Prompt

Use this if starting a new chat:

```text
Read AGENTS.md, main/README.md, main/PROJECT-INDEX.md, main/TO-DO.md, and main/HANDOFF-2026-05-28-preflight-next.md. Then reassess the best next infrastructure task. Prefer resolving live/source drift before deploying new apps.
Current aim: complete every task that requires my input first. Start with Tailscale route approval/mobile Grafana-Kuma test, then HA Monitoring dashboard snippet, then docker-host patch-window timing, then VentSys live-copy/valve-2 physical findings.
```
