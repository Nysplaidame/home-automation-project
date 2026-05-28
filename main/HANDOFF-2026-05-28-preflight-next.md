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
- Plain MQTT `1883` remains open as a staged/bootstrap path until remaining
  clients are migrated.
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

1. Validate and maintain VentSys MQTT TLS-only firewall posture (do not reintroduce plain `1883` valve exceptions).
2. Canonicalize docker-host UFW route rules.
3. Review Home Assistant Companion App sensors.
4. Document the temporary router WiFi uplink operating policy.
5. Only then consider the next app candidate.

### 1. Keep valve-1 MQTT on TLS-only firewall posture

Live/source checks on 2026-05-28 found no valve-specific temporary plain-MQTT
`1883` firewall exception, while VentSys MQTT firewall policy is `8883` TLS-only.
Do not add a valve-1 plain-MQTT exception unless a verified rollback scenario
explicitly requires it.

Suggested first checks:

```powershell
Get-Content main\configs\openwrt\firewall-config.conf | Select-Object -Skip 650 -First 100
```

```powershell
ssh -i main\tools\router-deploy\keys\router_deploy root@192.168.10.1 "uci show firewall | grep -Ei 'VentSys|valve|MQTT|1883|8883'"
```

If a live temporary valve-1 `1883` rule ever appears again, treat it as
time-boxed drift and document the rollback rationale before copying it into
source.

Router validation commands:

```powershell
python main\tools\router-deploy\lint.py
python main\tools\router-deploy\compile.py --profile first-flight
main\tools\router-deploy\test-connectivity.ps1 -RouterIp 192.168.10.1
```

Only redeploy if source changes need to be applied:

```powershell
main\tools\router-deploy\deploy.ps1 -RouterIp 192.168.10.1 -Profile first-flight -Force
```

### 2. Canonicalize docker-host UFW route rules

Live UFW route rules were added on docker-host so AdGuard's Docker bridge subnet
can reach upstream DNS despite `ufw default deny routed`.

Current live intent:

- Allow `172.20.0.0/16` to any `53/udp`
- Allow `172.20.0.0/16` to any `53/tcp`
- Allow `172.20.0.0/16` to any `853/tcp`

This is now backed by rebuildable source at
`main/configs/docker-host/system/docker-host-ufw-route-dns.sh`. Keep this script
deployed on docker-host as `/usr/local/sbin/docker-host-ufw-route-dns.sh` and
run it after UFW baseline policy is enabled on rebuilds.

Be careful not to conflate this with `docker-host-firewall.service`, which owns
the Docker `DOCKER-USER` chain for published-port scoping. UFW host/routed rules
and Docker published-port guard rules are related but distinct.

### 3. Review HA Companion App sensors

The app is installed and notification/action testing works. Remaining work is
sensor hygiene:

- Enable useful presence, battery, network, and notification sensors.
- Avoid enabling noisy or privacy-heavy sensors unless there is a specific use.
- Update `main/docs/procedures/home_assistant_companion_app_guide.md` and
  `main/TO-DO.md` after the review.

This is partly a manual phone/UI task.

### 4. Document temporary router WiFi uplink policy

The temporary uplink exists because the GL-MT6000 is staged behind the current
home router. It should be documented as an explicit operating mode:

- Keep enabled while SearXNG/Whoogle need upstream internet search.
- Keep enabled when router-side package/image access is needed during pre-flight.
- Disable only when testing final-edge behavior or when another upstream path is
  intentionally provided.
- Confirm after changes that laptop management access and internet access still
  coexist.

Useful command if the uplink needs to be restored:

```powershell
main\tools\router-deploy\uplink.ps1 -Action enable -RouterIp 192.168.10.1
```

Canonical policy doc:

- `main/docs/procedures/router_temporary_uplink_policy.md`

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
