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
candidates, and live SearXNG/Whoogle pre-flight deployment.

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
ssh -i $env:USERPROFILE\.ssh\proxmox_admin_ed25519 root@192.168.20.102
```

HAOS SSH using the Proxmox key previously failed with `Permission denied
(publickey)`, so Home Assistant live validation may need the HA UI, Terminal &
SSH add-on, or user-provided access.

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

Docker host:

- VM 103 is live at `192.168.20.102`.
- VM size is currently 2 cores, 4096 MiB RAM, 32 GiB disk.
- Rebuildable non-secret templates live under `main/configs/docker-host/`.
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
- Tailscale still advertises only `192.168.20.101/32` and `192.168.40.50/32`.
- Router WireGuard remains dormant (`network.wg0.auto='0'`, interface down).
- Monitoring endpoints are directly reachable from management:
  - Grafana `http://192.168.60.10:3000/api/health` -> `200`
  - InfluxDB `http://192.168.60.10:8086/health` -> `200`
  - Uptime Kuma `http://192.168.60.10:3001/` -> `302`
- HA-side entity-state confirmation for
  `monitoring_external_health_package.yaml` is still a manual HA UI task when
  operator access is available.
- Controlled outage test: Whoogle was stopped and Uptime Kuma logged repeated
  failures, then Whoogle was restored (`HTTP 200`). No ntfy publish was observed
  during this test window, so notification dispatch requires follow-up.
- Frigate pre-flight status on VM 101:
  - `/opt/frigate/.env` missing (expected pre-start blocker)
  - `/opt/frigate/certs/ca-cert.pem` missing (expected TLS blocker)
  - MQTT TLS path reachable: `192.168.20.101:8883` open
  - Plain MQTT path not reachable: `192.168.20.101:1883` closed
- Proxmox backup preflight:
  - Job enabled daily at `02:00`, `keep-last=2`, VMs `100,101,102,103`
  - Latest 2026-05-28 artifacts present for all four VMs in `/var/lib/vz/dump`
  - Integrity spot-check passed: `zstd -t` on latest VM 100 backup

SearXNG direct search and Whoogle UI/search tests returned HTTP `200`.

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

The next conversation should probably avoid starting another big service first.
The highest-value work is to remove drift and make the pre-flight state more
rebuildable.

Recommended order:

1. Validate Uptime Kuma -> ntfy dispatch path (monitor failure was detected, but ntfy publish was not observed in the controlled Whoogle outage test).
2. Stage Frigate startup prerequisites without starting Frigate:
   `.env` secrets and MQTT CA cert at `/opt/frigate/certs/ca-cert.pem`.
3. Keep Grafana/Kuma embedding parked behind direct-link usage until HTTPS/same-origin path is intentionally implemented.
4. Prepare OMV storage cutover execution using
   `main/docs/procedures/omv_storage_cutover_checklist.md`.
5. Keep WireGuard dormant fallback posture unless there is a deliberate decision
   to roll out fallback clients.

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
```
