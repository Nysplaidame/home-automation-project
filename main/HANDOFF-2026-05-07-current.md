# Handoff - 2026-05-07 Current Live State

This handoff captures the current laptop/router/Proxmox/Home Assistant state so
the next session can continue without replaying the long troubleshooting thread.

## Recommended Model

Use the strongest available reasoning model for the next deployment/configuration
step. This is no longer simple command-following: we are coordinating live router
policy, VLAN reachability, Proxmox guests, HA packages, and security posture.

## Working Directory

Primary repo path:

```text
G:\home-automation-project\main
```

The prompt may still show an older `D:\Other computers\...` cwd. Prefer the `G:`
path; it contains the restored and current repo.

Git is not available in the current PowerShell PATH.

## Network Access

Current laptop working position:

- Laptop is on the management network.
- Laptop IP: `192.168.10.148`
- Gateway: `192.168.10.1`
- Router management IP: `192.168.10.1`
- Proxmox IP: `192.168.10.10`
- Home Assistant IP: `192.168.20.101`
- Docker host VM IP: `192.168.20.102`
- Bambuddy workload UI: `http://192.168.20.102:8000`
- APT cache endpoint: `http://192.168.20.102:3142`
- Monitoring VM IP: `192.168.60.10`

Router SSH:

```powershell
ssh -i G:\home-automation-project\main\tools\router-deploy\keys\router_deploy root@192.168.10.1 '<cmd>'
```

The local SSH config also has a `router` alias pointing at this key.

Proxmox SSH:

```powershell
ssh -i $env:USERPROFILE\.ssh\proxmox_admin_ed25519 root@192.168.10.10
```

Docker host VM SSH:

```powershell
ssh -i $env:USERPROFILE\.ssh\proxmox_admin_ed25519 root@192.168.20.102
```

## Router State

The GL.iNet/OpenWrt router is deployed and stable. It is still in staged mode
where its own internet path can piggy-back the existing home router via WiFi,
but the final architecture will eventually make this router the internet edge.

Physical port notes:

- `lan1`: trunk toward Proxmox.
- `lan2`: management VLAN 10, tested.
- `lan3`: NVR VLAN 30, DHCP tested; intended uplink for the future managed PoE camera switch; router UI/ping intentionally not broadly open.
- `lan4`: storage VLAN 40, DHCP tested; router UI/ping intentionally not broadly open.
- `lan5`: recovery/LAN VLAN 1, tested.
- Hive placement is parked for now; no separate router port has been committed to it.

Important live cleanup completed:

- The temporary router rule `TEMP Docker Host Update Access` was removed after
  Docker/Bambuddy pulls and apt-cache validation.
- Verified remaining relevant firewall output contains no temp rule.
- Relevant remaining source/destination mentions of `192.168.20.102` are the
  intended Docker host/Bambuddy workload policy rules.
- `apt-cacher-ng` is live on docker-host and reachable from `frigate-nvr`.
- Permanent router rule `Frigate to APT Cache` exists before the NVR-to-Automation
  block rule.
- `docker-host` and `frigate-nvr` both have `/etc/apt/apt.conf.d/01proxy`
  configured for the cache.
- Router-local NTP server is enabled, with UDP/123 input rules for restricted
  VLANs that need local time.

Verification from VM 103 after temp rule removal:

```text
curl -4I https://download.docker.com/ -> blocked / could not connect
HA_8123_OK
MQTT_1883_OK
```

## Proxmox State

Proxmox:

- Host: `proxmox`
- IP: `192.168.10.10`
- PVE: 9.1.9
- Kernel after update/reboot: `7.0.0-3-pve`
- Web UI: `https://192.168.10.10:8006`
- No-subscription repository configured.
- Enterprise/Ceph enterprise repos disabled.
- Subscription warning is expected.
- SSH root login is key-only/prohibit-password.
- Temporary local Proxmox backups are scheduled daily at `02:00` for VMs
  `100/101/102/103`, keep `2`, until the NAS backup target is live.
- Longer-term storage direction: keep fast local recovery on the MINIX for VM/system
  backups, move HA scheduled backups to the NAS when available, and keep Frigate
  "live" recordings local first with NAS archiving later.

VMs:

| ID | Name | State | IP | Notes |
|---|---|---|---|---|
| 100 | home-assistant | running | 192.168.20.101 | HAOS, core 2026.5.0 |
| 101 | frigate-nvr | running | 192.168.30.20 | Debian 13 VM, Docker installed, Frigate staged |
| 102 | monitoring | running | 192.168.60.10 | Debian 13 VM, Docker stack: InfluxDB/Grafana/Telegraf/Uptime Kuma |
| 103 | docker-host | running | 192.168.20.102 | Debian 13 VM, Docker host, Bambuddy/Homepage/Dozzle/AdGuard/Immich pre-flight running |

VM 102 monitoring live state:

- Uptime Kuma baseline monitors are configured and green for router DNS, Proxmox UI, HA UI, docker-host SSH, docker-host APT cache, Bambuddy UI port, Homepage UI, Dozzle UI, AdGuard DNS, AdGuard UI, Immich UI, Grafana, InfluxDB, and Uptime Kuma.
- OpenWrt forwards syslog to `192.168.60.10:514/udp`; Telegraf receives it on container port `6514/udp` and writes `syslog` measurements to InfluxDB.
- Home Assistant exports state history to the InfluxDB `homeassistant` bucket using `source=HA`.
- HA to InfluxDB is allowed by OpenWrt with the scoped rule `HA to InfluxDB` from `192.168.20.101` to `192.168.60.10:8086/tcp`.
- Grafana has datasource `InfluxDB - Home Automation` (`uid: influxdb-homeassistant`) and dashboard `Home Automation Overview` (`/d/home-automation-overview/home-automation-overview`) in folder `Home Automation`.
- Grafana iframe embedding is enabled.
- Grafana anonymous Viewer mode is enabled for HA embedding (`GF_AUTH_ANONYMOUS_ENABLED=true`), but the last observed HA-side behavior still included a login loop, so treat direct Grafana UI access as the reliable path for now.
- HA has a storage-managed `Monitoring` dashboard at `/monitoring/overview` in the sidebar with direct links to Grafana and Uptime Kuma; the embedded Grafana experience is staged but not yet considered stable.
- Uptime Kuma direct HA iframe is parked because Kuma currently sends `X-Frame-Options: SAMEORIGIN`; use direct UI access until a same-origin reverse proxy/HTTPS path exists.
- HA-side external monitoring health is live at
  `/config/packages/monitoring_external_health_package.yaml`. It adds
  command-line binary sensors for Grafana, InfluxDB, and Uptime Kuma reachability
  from HA plus the aggregate `binary_sensor.monitoring_stack_externally_healthy`.
- HA HTTPS pre-flight certificate files exist but are not enabled:
  `/ssl/ha_https_preflight_fullchain.pem` and
  `/ssl/ha_https_preflight_privkey.pem`. Do not switch HA to HTTPS without a
  maintenance window, because that affects browser trust, Companion App URLs,
  dashboard URLs, and token-using clients.
- Router firewall rule `HA to Monitoring Health` allows HA
  `192.168.20.101` to monitoring VM `192.168.60.10` on TCP `3000` and `3001`;
  the existing `HA to InfluxDB` rule covers TCP `8086`.

VM 101 config highlights:

- Debian 13 genericcloud image.
- q35, OVMF, pre-enrolled keys disabled.
- `local-lvm`, 64 GiB SCSI disk.
- `net0`: `virtio=BC:24:11:9C:25:87,bridge=vmbr0,tag=30`
- Static cloud-init IP: `192.168.30.20/24`, gateway/DNS `192.168.30.1`.
- `onboot: 1`, startup order 2.
- Management SSH from VLAN 10 is working.
- Docker and Docker Compose are installed.
- Image pulled: `ghcr.io/blakeblackshear/frigate:stable`
- Frigate config staged under `/opt/frigate/`.
- Frigate is not started yet; it still needs `/opt/frigate/.env`, camera RTSP
  details, and the MQTT TLS/cert path to be finalized.
- NVR internet access is blocked by design. The temporary update rule used for
  Docker/image installation was removed after staging.

VM 103 config highlights:

- Debian 13 genericcloud image.
- q35, OVMF, pre-enrolled keys disabled.
- `local-lvm`, 16 GiB SCSI disk.
- `net0`: `virtio=BC:24:11:BC:B8:1A,bridge=vmbr0,tag=20`
- Static cloud-init IP: `192.168.20.102/24`, gateway/DNS `192.168.20.1`.
- `qemu-guest-agent` installed and active.
- VM sizing is currently `2 cores / 4096 MiB`. It was increased on 2026-05-27
  after Immich pre-flight overwhelmed the earlier 1 core / 2048 MiB recovery
  sizing.
  The recovery restart used Proxmox's firm stop path because QGA did not respond
  to shutdown during the overload.
- `onboot: 1`, startup order 3.
- 2026-05-27: Homepage is live at `http://192.168.20.102:3001`.
- 2026-05-27: Dozzle is live at `http://192.168.20.102:8081` and restricted
  with `docker-host-firewall.service` / `DOCKER-USER` so LAN5 cannot reach it.
- 2026-05-27: Docker image-pull router egress was added only temporarily and
  removed after pulling Homepage and Dozzle images.
- 2026-05-27: Uptime Kuma monitors for Homepage UI and Dozzle UI were added and
  returned `200 OK`.
- 2026-05-27: Tailscale `1.98.3` is installed and `tailscaled` is active on
  docker-host. docker-host is authenticated as `100.94.122.18`, and only
  `192.168.20.101/32` and `192.168.40.50/32` are advertised/approved. Local
  forwarding to HA returned `200`; off-LAN mobile validation was confirmed.
- 2026-05-27: AdGuard Home is live at `/opt/stacks/adguard-home`, admin UI
  `http://192.168.20.102:8080`, DNS bound to `192.168.20.102:53`, with approved
  upstreams `9.9.9.9`, `1.1.1.1`, and `1.0.0.1`. Admin password is stored on
  docker-host at `/root/adguard-home-admin-password.txt`; copy it to Bitwarden.
- 2026-05-27: Uptime Kuma monitors for AdGuard DNS and AdGuard UI were added and
  are green.
- 2026-05-27: Immich skeleton is live at `/opt/stacks/immich`, UI
  `http://192.168.20.102:2283`, version `v2.7.5`, with local placeholder
  `./library` uploads and `./postgres` database storage. Database password is
  stored on docker-host at `/root/immich-db-password.txt`.
- 2026-05-27: Immich is pre-flight only. Do not import a real photo library until
  OMV-backed storage and backup/restore steps are documented and tested.
- 2026-05-27: `immich_machine_learning` is intentionally stopped to keep VM 103
  stable; `immich_server`, `immich_postgres`, and `immich_redis` are healthy.
- 2026-05-27: `vm.overcommit_memory=1` is persisted via
  `/etc/sysctl.d/98-immich-valkey.conf` for Valkey/Redis.
- 2026-05-27: UFW and `docker-host-firewall.service` / `DOCKER-USER` scope
  Immich UI `2283/tcp` to management, LAN, monitoring, and `tailscale0`.
- 2026-05-27: Uptime Kuma monitor `Immich UI` was added after backup
  `/opt/monitoring/uptime-kuma/kuma.db.backup-20260527-125113-before-immich-monitor`
  and returned `200 OK`.
- 2026-05-27: VM 103 disk was expanded online from 16 GiB to 32 GiB; root
  filesystem now has about 21 GiB free after resize.
- 2026-05-27: ntfy is live at `/opt/stacks/ntfy`, URL
  `http://192.168.20.102:8085` / `http://ntfy.home.local:8085`, with default
  anonymous access denied. Credentials are stored on docker-host at
  `/root/ntfy-credentials.txt`; copy them to Bitwarden.
- 2026-05-27: ntfy users are `admin` and `watchtower`; `watchtower` has
  write-only access to topic `watchtower`.
- 2026-05-27: UFW, OpenWrt, and `docker-host-firewall.service` scope ntfy
  `8085/tcp` to management, LAN, HA, monitoring, and `tailscale0`.
- 2026-05-27: Watchtower monitor-only is live at `/opt/stacks/watchtower`.
  It has `WATCHTOWER_MONITOR_ONLY=true`, `DOCKER_API_VERSION=1.40`, no exposed
  HTTP port, and shoutrrr notifications pointed at internal ntfy. Because
  docker-host's Tailscale rule allows TCP `443` for DERP/HTTPS fallback, generic
  HTTPS egress is technically possible; still treat Docker pulls and updates as
  maintenance-window work, not routine background updates.
- 2026-05-27: Uptime Kuma monitor `ntfy UI` was added after backup
  `/opt/monitoring/uptime-kuma/kuma.db.backup-20260527-162424-before-ntfy-monitor`
  and returned `200 OK`.
- 2026-05-27: Temporary router egress for docker-host image pulls was removed
  again after Immich image pulls; router connectivity validation returned
  `PASS=82 WARN=0 FAIL=0`.

## Home Assistant State

Home Assistant VM 100:

- IP: `192.168.20.101`
- HA Core: `2026.5.0`
- Supervisor: `2026.04.2`
- Terminal & SSH add-on exposed on port 22.
- MQTT/Mosquitto has TLS live on port `8883`, with port `1883` still open as
  the staged bootstrap path for existing clients.

Known good backup:

- Name: `post-ha-ventsys-staged-20260507-db-excluded`
- Slug: `5fdeaff7`
- File: `/backup/5fdeaff7.tar`
- Size: about 80 KB
- Database excluded: yes

Live HA config:

- `/config/configuration.yaml` is the fresh HAOS default plus:

```yaml
# Project packages
homeassistant:
  packages: !include_dir_named packages
```

Live packages:

- `/config/packages/ventsys_ha_package.yaml`
- `/config/packages/ventsys_ha_scripts.yaml`

External monitoring health:

- `configs/home-assistant/monitoring_external_health_package.yaml` is deployed
  live at `/config/packages/monitoring_external_health_package.yaml`.
- `ha core check` passed and HA Core was restarted successfully on 2026-05-27.
- HA-side curl probes to Grafana `3000`, InfluxDB `8086`, and Uptime Kuma `3001`
  all returned successfully after adding router rule `HA to Monitoring Health`.
- The package entities are registered in HA's entity registry. No HA API token
  was available to query live states from automation, so final validation used
  endpoint probes, HA config check, HA restart, and entity-registry presence.

`ha core check` passes.

VentSys entities are registered, including:

- `fan.inline_fan`
- `fan.spray_booth_fan`
- `number.fdm_valve`
- `number.sla_valve`
- `number.main_duct_valve_1`
- `sensor.fdm_temperature`
- `sensor.sla_temperature`
- `binary_sensor.mqtt_broker_online`
- `input_boolean.ventsys_failsafe`

Broad automations are staged but disabled with `initial_state: false`, including:

- fire emergency response
- FDM/SLA high temperature warnings
- FDM/SLA critical cut-power responses
- FDM/SLA poor air quality responses
- MQTT broker offline alert
- VentSys initialise-to-safe-state on HA start

Some HA logs contain older MQTT integration errors from before the package
migration. Those were historical; entities registered after the fixed restart.

Current HA follow-up note:

- HA reports the InfluxDB YAML deprecation warning. The connection/auth keys that
  were auto-imported into the UI should be removed from `/config/configuration.yaml`
  after confirming the UI-managed Influx connection and restarting HA.
- 2026-05-08 update: the deprecated InfluxDB YAML connection/auth cleanup is now
  reflected in the repo config. No active `influxdb:` YAML block remains in
  `configs/home-assistant/configuration.yaml`.

## Validation Snapshot - 2026-05-08

Router validation from the management laptop against `192.168.10.1`:

```text
test.ps1 -RouterIp 192.168.10.1 -Profile first-flight
PASS=62 WARN=0 FAIL=0

test-connectivity.ps1 -RouterIp 192.168.10.1 -Profile first-flight
PASS=74 WARN=0 FAIL=0
```

Core service baseline from Proxmox using the staged default health check:

```text
health_check.sh --json
summary: PASS=11 FAIL=0
```

The default health check now treats Frigate UI, NAS, P1S, VentSys boards, and
VentSys plugs as parked/future checks unless `--full` is passed. This matches
the current hardware state: those devices/services are not expected to be live
yet.

Additional spot checks:

- Proxmox UI `192.168.10.10:8006`: reachable from management laptop.
- Home Assistant UI `192.168.20.101:8123`: reachable.
- Mosquitto bootstrap MQTT `192.168.20.101:1883`: reachable.
- Mosquitto TLS MQTT `192.168.20.101:8883`: reachable; authenticated TLS
  publish/subscribe with `/ssl/ca.crt` verified.
- Grafana `192.168.60.10:3000`, InfluxDB `192.168.60.10:8086`, and Uptime Kuma
  `192.168.60.10:3001`: reachable.
- `frigate-nvr` can reach docker-host apt cache at `192.168.20.102:3142`
  (`HTTP/1.1 200 OK`).
- VMs `100/101/102/103` are all running.
- Bambuddy container is running and healthy.

## Docker Host VM State

VM 103:

- Proxmox name: `docker-host`
- Hostname: `docker-host`
- OS: Debian GNU/Linux 13, trixie
- Kernel: `6.12.85+deb13-cloud-amd64`
- Interface: `eth0`, `192.168.20.102/24`
- Docker: installed and active
- Docker Compose: installed
- Image pulled: `ghcr.io/maziggy/bambuddy:latest`
- Image ID: `debbfe09b1cf`
- Image size: about 1.57 GB

Files staged:

```text
/opt/stacks/bambuddy/data/
/opt/stacks/bambuddy/logs/
/opt/stacks/bambuddy/docker-compose.yml
/opt/stacks/bambuddy/.env.example
```

`/opt/stacks/bambuddy/docker-compose.yml`:

```yaml
services:
  bambuddy:
    container_name: bambuddy
    image: ghcr.io/maziggy/bambuddy:latest
    restart: unless-stopped
    network_mode: host
    environment:
      - TZ=Europe/London
      - PORT=8000
      - MQTT_HOST=${MQTT_HOST}
      - MQTT_PORT=${MQTT_PORT}
      - MQTT_USER=${MQTT_USER}
      - MQTT_PASSWORD=${MQTT_PASSWORD}
    volumes:
      - /opt/stacks/bambuddy/data:/app/data
      - /opt/stacks/bambuddy/logs:/app/logs
```

`/opt/stacks/bambuddy/.env.example`:

```env
MQTT_HOST=192.168.20.101
MQTT_PORT=1883
MQTT_USER=mqtt
MQTT_PASSWORD=<set-from-bitwarden>
```

Bambuddy container is running and healthy after creating real
`/opt/stacks/bambuddy/.env` with the MQTT password.

2026-05-08 MQTT TLS update:

- `/opt/stacks/bambuddy/.env` now uses `MQTT_PORT=8883`.
- Backups were created before the change:
  `/opt/stacks/bambuddy/.env.bak.20260508-224722` and
  `/opt/stacks/bambuddy/data/bambuddy.db.bak.20260508-224722`.
- Bambuddy application settings in `data/bambuddy.db` were updated:
  `mqtt_enabled=true`, `mqtt_broker=192.168.20.101`, `mqtt_port=8883`,
  `mqtt_username=mqtt`, `mqtt_use_tls=true`, `mqtt_topic_prefix=bambuddy`.
- Bambuddy logs confirm both MQTT relay and MQTT smart-plug service connected
  to `192.168.20.101:8883`.
- Mosquitto logs confirm Bambuddy negotiated TLSv1.3 from `192.168.20.102`.
- Retained `bambuddy/status` was verified over TLS on `8883`:
  `{"status": "online", ...}`.

Current VM firewall:

- Default incoming: deny
- Default outgoing: allow
- Default routed: deny
- Allow `192.168.10.0/24` to TCP 22.
- Allow `192.168.10.0/24` to TCP 8000.
- Allow `192.168.1.0/24` to TCP 8000.
- Allow `192.168.20.0/24` to TCP 8000.

## Repo Source Files Updated

These repo files have been updated to reflect the live work:

- `configs/home-assistant/configuration.yaml`
- `configs/home-assistant/automations.yaml`
- `ventsys/ventsys_bundle_updated/ventsys_ha_package.yaml`
- `ventsys/ventsys_bundle_updated/ventsys_ha_optional.yaml`
- `scripts/setup/proxmox/ha_vm_setup_guide.md`
- `scripts/setup/proxmox/docker_host_setup_guide.md`
- `scripts/setup/proxmox/bambuddy_vm_setup_guide.md`
- `HANDOFF-2026-05-07-current.md`

Important source-state notes:

- VentSys MQTT entity YAML was migrated to the HA 2026.5-compatible top-level
  `mqtt:` layout.
- `configs/home-assistant/automations.yaml` now has broad automations disabled
  initially with `initial_state: false`.
- `configs/home-assistant/bambuddy_p1s_package.yaml` already uses top-level
  `mqtt:` for entities, but still contains `<P1S_SERIAL>` placeholders and
  must not be deployed until the real serial and Bambuddy MQTT state exist.

## Next Plan

1. Keep P1S/Bambuddy integration parked until the printer is physically ready.
2. When ready, add Bambuddy application config in its UI:

- P1S IP: `192.168.35.200`
- P1S access code and serial when physically available
- Home Assistant URL: `http://192.168.20.101:8123`
- Home Assistant long-lived token

3. Do not deploy `configs/home-assistant/bambuddy_p1s_package.yaml` until:

- Bambuddy is running.
- P1S serial is known.
- MQTT topics/entities are confirmed.
- `<P1S_SERIAL>` placeholders are replaced.

4. Monitoring follow-up:

- Keep using direct Grafana and Kuma links from HA until the embedding/auth path
  is stable.
- Add an external health signal so monitoring-VM downtime is still visible when
  Kuma itself is down.

5. Frigate/CCTV follow-up:

- Leave Frigate staged until camera RTSP details and MQTT credentials are ready.
- Require HTTPS/SSL for the Frigate UI before regular use.
- Add WebRTC audio later.
- Lumen setup on an Apple device is a manual user step to do later, alongside
  the Android viewing path.

6. Later hardening:

- Move remaining MQTT clients from `1883` to `8883`.
- Bambuddy MQTT has been moved to `8883`; keep the HA package parked until
  P1S details and MQTT topics are confirmed.
- Re-test HA/MQTT/Bambuddy paths.
- Decide whether docker-host should have periodic, tightly controlled update access
  or remain fully blocked except for manual maintenance windows.
- Finish WireGuard/DDNS only after the current local infrastructure is stable.

## Cautions

- Do not re-enable `TEMP Docker Host Update Access` unless actively installing or
  pulling updates, and remove it immediately afterwards.
- Do not wholesale replace HAOS `/config/configuration.yaml`; only patch in
  project includes. The repo guide has been updated for this.
- Keep broad HA automations disabled until the physical devices/sensors they
  depend on are present and tested.
- Do not deploy the Bambuddy HA package while `<P1S_SERIAL>` placeholders remain.
- Do not treat Grafana/Kuma HA embedding as fully complete yet; the reliable path
  today is sidebar links/direct UI access.
