---
title: Scrypted Install Manual
description: Placement-gated Scrypted evaluation with camera isolation, backup, restore, and rollback
tags: [install, docker-host, proxmox, scrypted, cameras]
created: 2026-05-24
modified: 2026-08-09
type: install-guide
status: draft-installable
---

# Scrypted Install Manual

## Purpose

Evaluate Scrypted only for a camera function that Frigate plus Home Assistant do
not already provide. Upstream recommends Proxmox for dedicated Intel/AMD servers
and prefers it over Docker because Scrypted uses host networking and may need
GPU/storage integration. The project default is **parked**.

## Runs on

- planning/review from the admin laptop;
- Proxmox host shell if the preferred dedicated-guest path is approved;
- docker-host over SSH only if an exception explicitly approves host-network
  collision risk and resource/device boundaries;
- Scrypted UI from a trusted management client.

## Mandatory placement and overlap gate

Do not download or run an installer until the decision record answers:

- required feature and why Frigate/HA cannot meet it;
- bridge-only versus Scrypted NVR/recording role;
- dedicated Proxmox LXC/VM versus docker-host exception;
- CT/VM ID, address/VLAN, CPU, memory, storage, iGPU/Coral ownership;
- exact camera source/destination flows and discovery requirement;
- whether any camera credentials must be duplicated;
- recording ownership/retention so two NVRs do not fill storage;
- ports `10443`/`11080` and host-network collision check;
- Scrypted-native backup, Proxmox backup, isolated restore, and exit plan.

For the current shared-iGPU design, Frigate CT 111 and local-AI CT 114 already
use `/dev/dri`. Do not assume another workload can safely share decode capacity;
measure it with the existing camera/AI workloads active.

## Inputs

- `<SCRYPTED_ADMIN_PASSWORD>` entered only in the first-run UI.

Store camera credentials separately and use a least-privilege camera account if
the hardware supports it.

## 1. Reconfirm that the candidate is still parked

Run on: Proxmox host shell.

```bash
pct list
qm list
ss -lntp | grep -E ':(10443|11080)\b' || true
```

Run on: docker-host over SSH.

```bash
docker ps --format 'table {{.Names}}\t{{.NetworkSettings.Networks}}\t{{.Ports}}'
ss -lntp | grep -E ':(10443|11080)\b' || true
test ! -e /opt/stacks/scrypted && echo 'scrypted candidate absent'
```

Expected result before approval: no Scrypted guest/container/listener exists and
the candidate directory is absent. If artifacts exist, stop and identify their
origin before choosing a path; do not run another installer on top.

## 2A. Preferred path: dedicated Proxmox guest

The official Proxmox installer creates/restores a Scrypted container and prompts
for accelerator choices. Review it before execution and keep a copy/hash in the
deployment record, not in tracked source.

Run on: Proxmox host shell after the dedicated-guest gate is approved.

```bash
install -d -m 0700 /root/scrypted-install-review
cd /root/scrypted-install-review
curl --fail --silent --show-error --location \
  https://raw.githubusercontent.com/koush/scrypted/main/install/proxmox/install-scrypted-proxmox.sh \
  -o install-scrypted-proxmox.sh
chmod 0700 install-scrypted-proxmox.sh
sha256sum install-scrypted-proxmox.sh
less install-scrypted-proxmox.sh
```

Expected result: an official Proxmox installer is downloaded, hash/date are
recorded, and review identifies guest creation, download sources, defaults,
device mounts, networking, and restore behavior. Stop if it would reuse an
existing VM/CT ID, bridge/VLAN, address, storage, or device assignment.

Run on: Proxmox host shell only after script review and final resource approval.

```bash
cd /root/scrypted-install-review
bash ./install-scrypted-proxmox.sh
```

Choose a unique CT/VM ID and project-approved VLAN/address. Decline NVR storage
and accelerator passthrough unless those were explicitly selected. Change the
installer's default root credential immediately at the guest console.

Expected result: the installer completes, reports the created guest and
`https://<scrypted-address>:10443/`, and no existing guest/device assignment is
changed. Record the actual ID/address/resources because upstream defaults can
change.

The upstream Compose currently includes a Scrypted-scoped Watchtower updater
and public DNS defaults. Before adding cameras, disable the updater by default
and set the guest's router-local DNS. The guest address determines the router
DNS value; a VLAN 30 guest uses `192.168.30.1`.

Run on: dedicated Scrypted LXC console before camera onboarding.

```bash
cd /root/.scrypted
docker compose stop watchtower
cat >docker-compose.override.yml <<'COMPOSE'
services:
  watchtower:
    profiles: [manual-update-only]
COMPOSE
grep -q '^SCRYPTED_DNS_SERVER_0=' .env || printf '%s\n' 'SCRYPTED_DNS_SERVER_0=192.168.30.1' >>.env
grep -q '^SCRYPTED_DNS_SERVER_1=' .env || printf '%s\n' 'SCRYPTED_DNS_SERVER_1=192.168.30.1' >>.env
chmod 0600 .env
docker compose config --quiet
docker compose up -d
docker compose ps --all
```

Expected result: Scrypted is `Up`; `scrypted-watchtower` is stopped/absent from
the default profile, and DNS uses the VLAN router rather than the upstream
public defaults. Recheck this override after any upstream reset/install script.

Run on: Proxmox host shell.

```bash
pct list
read -r -p 'Recorded Scrypted CT ID: ' scrypted_ct_id
[[ "$scrypted_ct_id" =~ ^[0-9]+$ ]]
pct config "$scrypted_ct_id"
```

Expected output shows the recorded dedicated guest, approved
bridge/VLAN/resources, and only the
approved device/storage mappings. This is an operational value, not a secret.

## 2B. Exception path: Linux Docker on docker-host

Use this only when the decision explicitly accepts upstream's host-network
requirements and proves no conflict with existing docker-host services. This
project-controlled exception stores the reviewed upstream Compose file under
`/opt/stacks/scrypted`; update the backup job for its `volume` directory and
native backup before treating it as persistent.

Download the upstream Compose file directly so automatic-update and public-DNS
defaults can be overridden before any container starts. Do not run the upstream
Docker installer unchanged: it enables a Watchtower updater by default.

Run on: docker-host over SSH after the Docker exception gate is approved.

```bash
install -d -m 0700 /opt/stacks/scrypted
cd /opt/stacks/scrypted
curl --fail --silent --show-error --location \
  https://raw.githubusercontent.com/koush/scrypted/main/install/docker/docker-compose.yml \
  -o docker-compose.yml
sha256sum docker-compose.yml
less docker-compose.yml
```

Expected result: official Linux Docker Compose hash/review is recorded. Review
must confirm host networking, runtime path, devices, update helper, DNS, and
storage do not violate the gate.

Run on: docker-host over SSH only after Compose review.

```bash
cd /opt/stacks/scrypted
watchtower_token="$(openssl rand -hex 16)"
umask 077
cat >.env <<ENV
WATCHTOWER_HTTP_API_TOKEN=${watchtower_token}
SCRYPTED_DNS_SERVER_0=192.168.20.1
SCRYPTED_DNS_SERVER_1=192.168.20.1
ENV
unset watchtower_token
cat >docker-compose.override.yml <<'COMPOSE'
services:
  watchtower:
    profiles: [manual-update-only]
COMPOSE
docker compose config --quiet
docker compose up -d
docker compose ps --all
ss -lntp | grep -E ':(10443|11080)\b'
```

Expected result: Scrypted starts from `/opt/stacks/scrypted`, the Watchtower
service is stopped/absent from the default profile, router-local DNS is used,
and only approved Scrypted listeners appear. If existing services disappear or
ports collide, stop Scrypted and restore the pre-install docker-host baseline.

Never run both paths.

## 3. First-run security and one-camera pilot

From a trusted management browser:

1. open the exact recorded HTTPS address/port and inspect the certificate warning
   only on the intended local host;
2. create the named admin with `<SCRYPTED_ADMIN_PASSWORD>` and store it;
3. disable/uninstall unused plugins and cloud integrations;
4. add one non-critical camera with least-privilege credentials;
5. keep Frigate as recording/system-of-record unless the NVR gate explicitly
   says otherwise;
6. validate view/stream latency while Frigate recording and CT 114 inference are
   active;
7. prove an unapproved VLAN/source cannot open the admin UI or camera feed.

Expected result: one camera works without duplicate recordings, camera lockout,
Frigate interruption, iGPU errors, or a broad camera-VLAN route.

## 4. Capture native and infrastructure backups

Create a Scrypted-native backup from its UI before and after the camera pilot.
Store it in the approved protected backup location. Do not commit the archive;
it may contain credentials, server address, and plugin configuration.

For the dedicated Proxmox path, also back up the guest only after stopping or
quiescing it as the selected method requires.

Run on: Proxmox host shell for the dedicated-guest path.

```bash
read -r -p 'Recorded Scrypted CT ID: ' scrypted_ct_id
[[ "$scrypted_ct_id" =~ ^[0-9]+$ ]]
vzdump "$scrypted_ct_id" --storage omv-backups --mode stop --compress zstd --tmpdir /var/tmp
pvesm list omv-backups --content backup | grep -- "-${scrypted_ct_id}-"
```

Expected result: `vzdump` ends successfully and a new non-zero guest archive is
listed. Record the exact volume ID.

For docker-host placement, confirm the backup job captures the upstream runtime
data path plus the native backup while the service is stopped/consistent.

## 5. Isolated restore and rollback proof

Restore the native backup or Proxmox archive to a disposable guest/project with
its NIC disconnected or placed on an isolated test bridge. Do not let the clone
start with the production Scrypted address, camera access, or server identity.
After booting in isolation, import the native backup and verify plugins/camera
configuration exist without actually connecting to production cameras.

Scrypted backups can restore the saved server address. Change it before attaching
any network. Record proof, shut down the disposable target, then remove it only
after explicit target-ID/path confirmation.

Rollback from a failed pilot:

1. remove/disable only the Scrypted camera/plugin;
2. stop the Scrypted guest/Compose stack;
3. remove temporary Scrypted firewall routes and device mappings;
4. verify Frigate streams, recording path, HA entities, and CT 114 inference;
5. retain backup/config until the evaluation decision is closed.

## Updates

Create a native backup plus infrastructure checkpoint, review upstream release
notes and installer changes, update during a camera maintenance window, then
repeat admin/camera/Frigate/GPU/storage tests. Do not enable automatic updates.
Use upstream's documented LXC/host reset only after reading the current script,
capturing a backup, and confirming the exact guest context.

## Failure recovery matrix

| Failure | Safe response | Proof before continuing |
|---|---|---|
| Installer wants existing guest ID/storage | Cancel before execution or at prompt. | Unique approved target recorded. |
| Docker host-network collision | Stop Docker Scrypted and restore prior listeners/firewall. | Existing services and ports return. |
| Camera locks out or drops | Remove duplicate Scrypted session and preserve Frigate path. | Camera and Frigate stabilize. |
| GPU contention/error | Remove Scrypted device mapping or stop workload. | Frigate and CT 114 performance return to baseline. |
| Duplicate recording fills storage | Stop Scrypted NVR; preserve Frigate retention. | One approved recorder and expected capacity trend. |
| Native restore changes address | Keep clone isolated and edit address before network. | No duplicate identity/connection occurs. |
| Evaluation rejected | Stop service, remove approved temporary rules, preserve backup briefly. | Existing camera/HA/NVR acceptance suite passes. |

## Completion checklist

- [ ] Feature need, placement, resources, network, device, storage, and overlap gate accepted.
- [ ] Official installer hash/review and actual guest/runtime path recorded.
- [ ] Named admin exists; unused plugins/cloud paths are disabled.
- [ ] One-camera pilot passes with Frigate and local AI active.
- [ ] Unapproved-source access is denied and no broad camera route exists.
- [ ] Native backup plus placement-specific backup restore in isolation.
- [ ] Rollback restores Frigate, HA, storage, and GPU baselines.
- [ ] Automatic updates remain disabled.
