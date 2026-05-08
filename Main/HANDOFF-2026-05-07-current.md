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
- `lan3`: NVR VLAN 30, DHCP tested; router UI/ping intentionally not broadly open.
- `lan4`: storage VLAN 40, DHCP tested; router UI/ping intentionally not broadly open.
- `lan5`: recovery/LAN VLAN 1, tested.

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

VMs:

| ID | Name | State | IP | Notes |
|---|---|---|---|---|
| 100 | home-assistant | running | 192.168.20.101 | HAOS, core 2026.5.0 |
| 101 | frigate-nvr | running | 192.168.30.20 | Debian 13 VM, Docker installed, Frigate staged |
| 103 | docker-host | running | 192.168.20.102 | Debian 13 VM, Docker host, Bambuddy running |

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
- `onboot: 1`, startup order 3.

## Home Assistant State

Home Assistant VM 100:

- IP: `192.168.20.101`
- HA Core: `2026.5.0`
- Supervisor: `2026.04.2`
- Terminal & SSH add-on exposed on port 22.
- MQTT/Mosquitto is currently pre-TLS on port `1883`.

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

1. Create `/opt/stacks/bambuddy/.env` from `.env.example` on VM 103.
2. Add the real MQTT password from Bitwarden.
3. Start Bambuddy:

```bash
cd /opt/stacks/bambuddy
docker compose up -d
docker compose logs bambuddy -f
```

4. Confirm the UI is reachable from the laptop:

```text
http://192.168.20.102:8000
```

5. Add Bambuddy application config in its UI:

- P1S IP: `192.168.35.200`
- P1S access code and serial when physically available
- Home Assistant URL: `http://192.168.20.101:8123`
- Home Assistant long-lived token

6. Do not deploy `configs/home-assistant/bambuddy_p1s_package.yaml` until:

- Bambuddy is running.
- P1S serial is known.
- MQTT topics/entities are confirmed.
- `<P1S_SERIAL>` placeholders are replaced.

7. Later hardening:

- Configure Mosquitto TLS.
- Move Bambuddy MQTT from `1883` to `8883`.
- Re-test HA/MQTT/Bambuddy paths.
- Decide whether docker-host should have periodic, tightly controlled update access
  or remain fully blocked except for manual maintenance windows.

## Cautions

- Do not re-enable `TEMP Docker Host Update Access` unless actively installing or
  pulling updates, and remove it immediately afterwards.
- Do not wholesale replace HAOS `/config/configuration.yaml`; only patch in
  project includes. The repo guide has been updated for this.
- Keep broad HA automations disabled until the physical devices/sensors they
  depend on are present and tested.
- Do not deploy the Bambuddy HA package while `<P1S_SERIAL>` placeholders remain.
