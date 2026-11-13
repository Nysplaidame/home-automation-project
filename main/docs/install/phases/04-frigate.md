---
title: Phase 04 - Frigate
description: CT 111 creation, Docker, shared iGPU, migration-safe Frigate baseline, cameras, MQTT, HTTPS, storage, HA, and recovery
tags: [install, frigate, nvr]
created: 2026-05-24
modified: 2026-09-10
type: install-guide
status: active
---

# Phase 04 - Frigate

## Purpose

Create unprivileged CT 111, map the shared Intel DRM devices, install Docker and
Frigate, prove the no-camera recovery baseline, then add MQTT, HTTPS, storage,
Home Assistant, and one bench-validated camera at a time.

The safe order is deliberate:

1. empty Debian LXC;
2. shared-iGPU proof;
3. Frigate with cameras and MQTT disabled;
4. authenticated HTTPS UI and internal API policy;
5. MQTT TLS;
6. OMV recording bind mount;
7. one camera and its HA entities;
8. detection/recording tuning.

## Current-state callout

[current-live-state.md](../../reference/current-live-state.md) records the
production state: CT111 retains three ANNKE C500 configurations; cameras are
deliberately disconnected in the September baseline. The service retains
OpenVINO/VA-API on the shared iGPU, MQTT TLS, authenticated HTTPS, HA integration,
and OMV-backed recordings. That evidence does not replace any blank-rebuild
checkpoint below. The repository's `config-baseline.yml` remains the canonical
no-camera recovery configuration.

## Runs on

- Proxmox host shell for template download, CT creation, device mapping, and
  the later OMV bind mount.
- Frigate CT 111 console/SSH at `192.168.30.20` for Debian, Docker, Frigate,
  firewall, stream, and API checks.
- Home Assistant UI for the Frigate integration and camera dashboard.
- Admin laptop for trusted HTTPS and network-boundary checks.
- Camera and managed-switch UIs during the separate bench procedure.

## Decision gates and stop conditions

Do not continue if:

- Phase 03 MQTT TLS, backup, and HA access are not stable;
- CT ID `111` or address `192.168.30.20` is already owned by an unknown guest;
- retired VM 101 is running or still connected to the production network;
- `/dev/dri/renderD128` and `/dev/dri/card0` are absent on Proxmox;
- a privileged LXC is being proposed instead of the approved unprivileged design;
- Docker is being installed with the convenience script instead of its signed
  Debian repository;
- RTSP or MQTT credentials would be committed or pasted into logs/chat;
- the full camera configuration is being enabled before each stream has passed
  the camera pre-flight checklist;
- the OMV child volume remains in Compose while `/mnt/nas/frigate` is neither a
  verified Proxmox bind mount nor deliberately removed from the live baseline;
- port `5000` would be exposed beyond the exact HA/monitoring sources that need
  the unauthenticated API.

## Prerequisites

- Phase 03 complete.
- Current Debian LXC template available on Proxmox.
- `local-lvm` has 32 GiB plus safe host headroom.
- Router DHCP/DNS/firewall source defines CT 111 on VLAN 30.
- `<ADMIN_SSH_PUBLIC_KEY>` is approved for CT administration.
- `<FRIGATE_RTSP_PASSWORD>` and `<FRIGATE_MQTT_PASSWORD>` have password-manager
  records, even if camera activation is deferred.
- [shared-iGPU decision](../../decisions/07-shared-igpu-lxc-infrastructure.md)
  and [camera pre-flight checklist](../../procedures/frigate_camera_preflight_checklist.md)
  have been read.

## Inputs

- `<ADMIN_SSH_PUBLIC_KEY>`
- `<FRIGATE_RTSP_PASSWORD>`
- `<FRIGATE_MQTT_PASSWORD>`
- Local CA public certificate and Frigate server certificate/key; CA private
  keys must never be copied into CT 111.

## 1. Prove the CT identity and GPU are available

Run on: Proxmox host shell.

```bash
if pct status 111 >/dev/null 2>&1; then
  echo 'STOP: CT ID 111 already exists.' >&2
  exit 1
fi

if qm status 101 >/dev/null 2>&1; then
  qm status 101
  qm config 101 | grep -E '^(name|net[0-9]+|onboot):' || true
fi

ls -ln /dev/dri/renderD128 /dev/dri/card0
pvesm status | grep -E '^(Name|local-lvm[[:space:]])'
```

Expected result:

- CT 111 is absent;
- VM 101 is absent, or is stopped with `onboot: 0` and no production NIC;
- both DRM nodes exist;
- `local-lvm` is active with adequate free space.

If VM 101 is running, stop and resolve its rollback ownership before proceeding.
Do not automatically stop, detach, or delete it from this guide.

## 2. Download a current Debian template and create CT 111

Run on: Proxmox host shell.

```bash
pveam update
pveam available --section system | grep 'debian-.*-standard.*amd64'
```

Expected output lists one or more signed Proxmox Debian templates. Select the
current stable Debian template supported by the Docker repository and record
its exact filename.

Run on: Proxmox host shell.

```bash
template_name='debian-VERSION-standard_VERSION_amd64.tar.zst'
pveam download local "$template_name"
pveam list local | grep -F "$template_name"
```

Replace the illustrative `VERSION` filename with the exact result selected
above. Expected result: the template appears under `local:vztmpl/` and the
download completes without a checksum error.

Run on: Proxmox host shell.

```bash
pct create 111 "local:vztmpl/${template_name}" \
  --hostname frigate-nvr \
  --unprivileged 1 \
  --features nesting=1,keyctl=1 \
  --cores 2 \
  --memory 6144 \
  --swap 0 \
  --rootfs local-lvm:32 \
  --net0 name=eth0,bridge=vmbr0,tag=30,ip=192.168.30.20/24,gw=192.168.30.1,type=veth \
  --nameserver 192.168.30.1 \
  --ssh-public-keys /root/.ssh/authorized_keys \
  --onboot 1 \
  --startup order=2

pct config 111
```

Expected configuration includes:

```text
cores: 2
features: keyctl=1,nesting=1
hostname: frigate-nvr
memory: 6144
onboot: 1
rootfs: local-lvm:vm-111-disk-0,size=32G
swap: 0
unprivileged: 1
```

The feature ordering and disk-volume suffix may differ. `net0` must include
`bridge=vmbr0`, `tag=30`, `ip=192.168.30.20/24`, and `gw=192.168.30.1`.

## 3. Map the shared Intel DRM devices

The current verified mapping uses render GID `993` and video GID `44`. The
actual Debian template remains authoritative: after boot, `getent group` must
agree with the mapping before Frigate starts.

Run on: Proxmox host shell.

```bash
pct set 111 --dev0 path=/dev/dri/renderD128,gid=993,mode=0660
pct set 111 --dev1 path=/dev/dri/card0,gid=44,mode=0660
pct config 111 | grep -E '^(dev[01]|features|unprivileged|swap):'
```

Expected output includes:

```text
dev0: path=/dev/dri/renderD128,gid=993,mode=0660
dev1: path=/dev/dri/card0,gid=44,mode=0660
features: keyctl=1,nesting=1
unprivileged: 1
```

This is shared device mapping, not PCI passthrough. Do not enable IOMMU or bind
the iGPU to `vfio-pci` for this architecture.

Run on: Proxmox host shell.

```bash
pct start 111
pct status 111
pct exec 111 -- ip -brief address
pct exec 111 -- getent group render
pct exec 111 -- getent group video
pct exec 111 -- ls -ln /dev/dri
```

Expected result:

- CT status is `running` and `eth0` owns `192.168.30.20/24`;
- the render/video group IDs match the mapped ownership;
- both DRM nodes are visible with group read/write permission.

If the template assigns a different render GID, stop the CT, change only the
`gid=` value for `dev0` to the reported render group, restart, and repeat the
ownership check. Do not use world-writable `0666` permissions as a shortcut.

## 4. Install the Debian baseline

Run on: Frigate CT console or SSH.

```bash
apt-get update
apt-get full-upgrade -y
apt-get install -y \
  ca-certificates curl ffmpeg gnupg intel-gpu-tools vainfo \
  ufw fail2ban sqlite3

hostname
ip -brief address
ffprobe -version | head -n 1
vainfo --display drm --device /dev/dri/renderD128 2>&1 | head -n 20
```

Expected output characteristics:

- hostname is `frigate-nvr`;
- VLAN 30 address and default route are correct;
- `ffprobe` prints its version;
- `vainfo` lists Intel VA-API profiles instead of `Permission denied` or
  `failed to initialize display`.

Do not install `nfs-common` inside CT 111. OMV NFS is mounted on Proxmox and
bind-mounted into this unprivileged CT in Phase 06.

## 5. Install Docker Engine from the signed repository

Run on: Frigate CT console or SSH.

```bash
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

cat >/etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/debian
Suites: $(. /etc/os-release && echo "$VERSION_CODENAME")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF

apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
systemctl enable --now docker
systemctl is-active docker
docker version
docker compose version
```

Expected result: client and server versions print, Compose reports version 2 or
newer, and `systemctl is-active docker` returns `active`.

Run on: Frigate CT console or SSH.

```bash
docker run --rm hello-world
```

Expected output includes:

```text
Hello from Docker!
```

If Docker fails with an AppArmor, nesting, keyctl, or device error, stop and fix
the LXC configuration on Proxmox. Do not make the CT privileged.

## 6. Create the migration-safe Frigate layout

Copy these repository files from the admin laptop or another approved source:

| Repository source | Live destination |
|---|---|
| `configs/frigate/docker-compose.yml` | `/opt/frigate/docker-compose.yml` |
| `configs/frigate/config-baseline.yml` | `/opt/frigate/config/config.yml` |
| `configs/frigate/frigate.env.example` | `/opt/frigate/.env` before secret replacement |
| `configs/frigate/system/frigate-nvr-fail2ban-sshd.local` | `/etc/fail2ban/jail.d/frigate-nvr-sshd.local` |

If Phase 06 has not yet created the Proxmox-host NFS mount and CT `mp0`, remove
only this child-volume line from the **live** Compose copy before first start:

```text
- /mnt/nas/frigate:/media/frigate/recordings
```

Do not edit the repository source to pretend OMV is absent; it represents the
current production layout. With the migration-safe config, cameras and recording
are disabled. Restore the child volume only after Phase 06 proves the mount and
UID mapping.

Run on: Frigate CT console or SSH.

```bash
install -d -m 0750 /opt/frigate/config /opt/frigate/db /opt/frigate/storage
install -d -m 0750 /opt/frigate/certs /opt/frigate/tls
chmod 0600 /opt/frigate/.env
chown -R root:root /opt/frigate

cd /opt/frigate
docker compose config -q
```

Expected result: Compose exits `0`. Unset-secret warnings are acceptable only
for the no-camera/no-MQTT baseline; YAML, missing-volume, and interpolation
errors are not.

Before adding real credentials, replace both example values in `/opt/frigate/.env`
using a local root-only editor and the password manager. Do not source the file
into an interactive shell, display it with `cat`, or include it in command
output. Recheck mode `0600` afterward.

Run on: Frigate CT console or SSH.

```bash
stat -c '%a %U:%G %n' /opt/frigate/.env
grep -Eq '^FRIGATE_RTSP_PASSWORD=.+$' /opt/frigate/.env
grep -Eq '^FRIGATE_MQTT_PASSWORD=.+$' /opt/frigate/.env
```

Expected result: mode is `600`, owner is `root:root`, and both `grep` commands
exit `0` without printing the secret values.

## 7. Start and validate the no-camera recovery baseline

Run on: Frigate CT console or SSH.

```bash
cd /opt/frigate
docker compose pull
docker compose up -d
docker compose ps
docker compose logs --tail=120 frigate
curl -fsS http://127.0.0.1:5000/api/version
docker image inspect ghcr.io/blakeblackshear/frigate:stable \
  --format '{{json .RepoDigests}}'
```

Expected result:

- the Frigate container becomes healthy;
- API version returns a version string;
- logs show no config parse, database, DRM permission, or restart-loop error;
- the immutable pulled image digest is recorded in the rebuild log;
- no camera ffmpeg process is expected because `cameras: {}`.

Run on: Frigate CT console or SSH.

```bash
docker exec frigate ls -ln /dev/dri
docker exec frigate ps aux | grep '[d]etector:ov'
docker stats --no-stream frigate
```

Expected result: both DRM nodes exist inside the container and an OpenVINO
detector process is present. Record CPU/memory as a baseline, not a fixed pass
threshold.

### Baseline recovery rehearsal

Keep a deployable copy of `config-baseline.yml` outside CT 111. To rehearse the
configuration rollback after a deliberately invalid **temporary copy** is
detected:

1. Copy the live config to a timestamped backup.
2. Validate candidate edits before replacing the live file.
3. If Frigate rejects the candidate or loops, restore
   `config-baseline.yml` as `/opt/frigate/config/config.yml`.
4. Run `docker compose config -q`, recreate Frigate, and repeat API/GPU checks.

Expected evidence: the container returns healthy, `/api/version` responds, and
the OpenVINO detector returns. Never corrupt the live production file merely to
demonstrate failure; the failure half can use a disposable candidate path.

## 8. Apply host firewall and Fail2ban policy

Docker uses host networking here, so Frigate listeners bind directly in CT 111.
OpenWrt remains the inter-VLAN authority; CT firewall policy is defense in depth.

Port intent:

| Port | Purpose | Allowed scope |
|---:|---|---|
| 22/tcp | SSH administration | management sources only |
| 8971/tcp | authenticated Frigate UI/API, project TLS enabled | approved management/LAN and explicitly approved narrow remote route |
| 5000/tcp | internal unauthenticated API | HA `192.168.20.101` and monitoring `192.168.60.10` only |
| 8554/tcp | RTSP restream | approved HA/viewer paths only |
| 8555/tcp+udp | WebRTC | approved viewer paths only |

Do not enable UFW until the current SSH session has a matching allow rule and a
second management session is ready. Reconcile exact source networks with the
canonical access matrix rather than copying a broad subnet from an old guide.

Run on: Frigate CT console or SSH after source rules are staged.

```bash
ufw status verbose
fail2ban-client -t
systemctl enable --now fail2ban
fail2ban-client status sshd
ss -lntup | grep -E ':(22|5000|8554|8555|8971)[[:space:]]'
```

Expected result: policy is explicit, Fail2ban configuration test passes, the
`sshd` jail is listed, and only intended Frigate/SSH listeners exist. Test every
allow and deny path from the actual source host; a rule listing alone is not
connectivity evidence.

## 9. Install CA trust and Frigate HTTPS material

Copy only public CA/certificate material and the Frigate server private key
needed by the service:

- MQTT CA -> `/opt/frigate/certs/ca-cert.pem`;
- Frigate certificate -> `/opt/frigate/tls/fullchain.pem`;
- Frigate server key -> `/opt/frigate/tls/privkey.pem`.

The certificate SANs must include `192.168.30.20`, `frigate.home.local`,
`frigate-nvr`, and `frigate`. Never copy the CA signing key into CT 111.

Run on: Frigate CT console or SSH.

```bash
chmod 0644 /opt/frigate/certs/ca-cert.pem /opt/frigate/tls/fullchain.pem
chmod 0600 /opt/frigate/tls/privkey.pem
openssl verify -CAfile /opt/frigate/certs/ca-cert.pem /opt/frigate/tls/fullchain.pem
openssl x509 -in /opt/frigate/tls/fullchain.pem -noout -issuer -dates -ext subjectAltName

cd /opt/frigate
docker compose up -d --force-recreate frigate
```

Expected result: OpenSSL prints `OK`, SANs and dates are correct, and the
container returns healthy.

Run on: Admin laptop with `Home Local CA` trusted.

```powershell
Test-NetConnection 192.168.30.20 -Port 8971
try {
    Invoke-WebRequest -Uri 'https://192.168.30.20:8971/api/version' -MaximumRedirection 0
} catch {
    $_.Exception.Response.StatusCode.value__
}
```

Expected result: TCP succeeds and an unauthenticated request returns `401`.
Do not use `-SkipCertificateCheck`; the purpose is to prove both TLS trust and
authentication enforcement.

## 10. Enable MQTT over TLS

Replace the live baseline with a copy of `configs/frigate/config.yml` only after
reviewing it. For the first MQTT proof, keep all cameras disabled or absent.
Required MQTT settings are broker `192.168.20.101`, port `8883`, user `mqtt`,
CA path `/config/certs/ca-cert.pem`, and `tls_insecure: false`.

Run on: Frigate CT console or SSH.

```bash
openssl s_client \
  -connect 192.168.20.101:8883 \
  -CAfile /opt/frigate/certs/ca-cert.pem \
  -verify_return_error </dev/null 2>&1 | grep -E 'subject=|issuer=|Verify return code'
```

Expected output ends with:

```text
Verify return code: 0 (ok)
```

Run on: Frigate CT console or SSH.

```bash
cd /opt/frigate
docker compose up -d --force-recreate frigate
docker compose logs --since=2m frigate | grep -Ei 'mqtt|error|failed|certificate' || true
curl -fsS http://127.0.0.1:5000/api/stats | grep -o '"mqtt"[^,}]*' | head
```

Expected result: no TLS/authentication error appears and stats report MQTT
enabled/connected. Confirm Frigate topics from Home Assistant's MQTT listen UI;
do not place the password on a shell command line.

Failure test: temporarily use an invalid password in a disposable `.env` copy,
run `docker compose --env-file` validation/start only in a bounded window, and
confirm broker authentication fails. Restore the real mode-`0600` file and
recreate Frigate immediately. Do not log either password.

## 11. Add OMV recording storage in Phase 06

CT 111 must not mount NFS directly. Phase 06 performs this chain:

```text
OMV NFS export -> Proxmox /mnt/omv/frigate -> CT 111 mp0 /mnt/nas/frigate
-> Compose child mount /media/frigate/recordings
```

Before restoring the Compose child-volume line, require all of these checks.

Run on: Proxmox host shell.

```bash
findmnt -T /mnt/omv/frigate
pct config 111 | grep '^mp0:'
getfacl -p /mnt/omv/frigate | grep -E 'user:100000:rwx|default:user:100000:rwx'
```

Expected result: source is the intended OMV export, CT `mp0` maps it to
`/mnt/nas/frigate`, and UID `100000` has access/default ACL entries.

Run on: Frigate CT console or SSH.

```bash
findmnt -T /mnt/nas/frigate
test_file="/mnt/nas/frigate/.frigate-write-test-$(date +%s)"
touch "$test_file"
test -f "$test_file"
rm -f "$test_file"
```

Expected result: the path is a mount, write/read/delete succeeds, and no test
file remains. Only then restore the Compose recording child mount and recreate
Frigate. If the mount disappears later, stop Frigate rather than allowing
recordings to fill the CT root filesystem.

## 12. Bench and activate one camera at a time

Follow
[frigate_camera_preflight_checklist.md](../../procedures/frigate_camera_preflight_checklist.md).
For each camera, record model, firmware, MAC, switch port, PoE draw, NTP/DNS,
cloud-disable state, RTSP main/sub paths, audio codec, resolution, FPS, reset
procedure, and credential owner before editing Frigate.

Use a non-admin RTSP/viewer account where camera firmware supports it. A direct
`ffprobe` URL may expose its password briefly to privileged process inspection;
perform the test only on isolated CT 111, never save the command in project
logs, and unset any temporary shell variable immediately.

Run on: Frigate CT console or SSH.

```bash
read -r -p 'RTSP user: ' rtsp_user
read -r -s -p 'RTSP password: ' rtsp_password; printf '\n'
ffprobe -v error -rtsp_transport tcp \
  -show_entries stream=index,codec_type,codec_name,width,height,avg_frame_rate \
  -of default=noprint_wrappers=1 \
  "rtsp://${rtsp_user}:${rtsp_password}@192.168.30.21:554/Streaming/Channels/102"
unset rtsp_user rtsp_password
```

Expected output reports a video stream, real codec, expected substream
resolution, and frame rate. Repeat against the main stream. If credentials
contain URL-reserved characters, percent-encode them for the probe/Frigate URL.

Add only the validated camera's go2rtc and camera blocks. Use main stream for
recording, substream for detection/mobile viewing, and leave detection disabled
until ingest is stable.

Run on: Frigate CT console or SSH.

```bash
cd /opt/frigate
cp -a config/config.yml "config/config.yml.pre-camera-$(date +%Y%m%dT%H%M%S)"
docker compose up -d --force-recreate frigate
sleep 30
curl -fsS http://127.0.0.1:5000/api/stats > /tmp/frigate-stats.json
grep -Eo '"camera_fps":[0-9.]+' /tmp/frigate-stats.json
docker compose logs --since=2m frigate | grep -Ei 'ffmpeg|error|failed|401|403' || true
```

Expected result: camera FPS is sustained near the configured value and logs do
not show repeating ffmpeg/auth/read-frame errors. Keep the timestamped config
until a full observation window passes.

## 13. Validate OpenVINO and VA-API under camera load

Run on: Frigate CT console or SSH.

```bash
vainfo --display drm --device /dev/dri/renderD128 >/tmp/vainfo-frigate.txt 2>&1
docker exec frigate ps aux | grep '[d]etector:ov'
docker compose logs --since=5m frigate | grep -Ei 'openvino|vaapi|hwaccel|error|failed' || true
timeout 10s intel_gpu_top -J -s 1000 -o /tmp/intel-gpu-frigate.json || true
test -s /tmp/intel-gpu-frigate.json
```

Expected result: OpenVINO detector runs, no repeating VA-API/OpenVINO error is
present, and GPU telemetry is non-empty during active streams. CPU-only decode
or inference is a temporary diagnostic fallback, not completion of this phase.

If CT 114 is already live, repeat while llama.cpp serves one request. The shared
architecture is accepted only when both workloads stay healthy concurrently.

## 14. Configure the Home Assistant integration

HA uses Frigate's internal API at `http://192.168.30.20:5000`, not the
authenticated user-facing URL on `8971`. Port 5000 is unauthenticated and must
remain source-restricted to HA and the approved monitoring host.

Run on: Home Assistant UI.

1. Confirm Frigate MQTT topics/entities are present first.
2. Install/approve the Frigate integration according to the Phase 03 HACS gate.
3. Add Frigate URL `http://192.168.30.20:5000`.
4. Confirm the config entry loads and camera/entities are available.
5. Add Advanced Camera Card only after basic camera entities and Frigate PWA
   viewing work; keep standard HA camera/image fallback available.

Run on: Home Assistant UI -> Developer Tools -> States.

Expected evidence for each camera includes a camera entity plus motion,
occupancy/object, and intended Frigate control entities. An entity appearing is
not enough: open its stream and exercise only non-destructive controls during
the acceptance window.

## 15. Authentication recovery rehearsal

If the Frigate admin password is lost, use the supported one-start reset flag:

Run on: Frigate CT console or SSH.

```yaml
auth:
  reset_admin_password: true
```

Add that setting to the live config, recreate Frigate, capture the generated
password directly into the password manager, sign in, and set the permanent
password. Then remove `reset_admin_password`, recreate Frigate again, and prove
the flag is absent.

Run on: Frigate CT console or SSH after recovery.

```bash
if grep -Eq '^[[:space:]]*reset_admin_password:[[:space:]]*true' /opt/frigate/config/config.yml; then
  echo 'STOP: temporary admin reset flag is still enabled.' >&2
  exit 1
fi
docker compose -f /opt/frigate/docker-compose.yml ps
```

Expected result: the guard prints nothing, exits `0`, and Frigate is healthy.
Do not place the generated password in the rebuild log.

## 16. Backup and isolated recovery proof

Return to this step after Phase06 establishes OMV and Phase10 establishes
backup policy. On a blank build, record it as deferred; do not block the
no-camera foundation on a NAS which has not yet been installed.

CT 111 joins the Proxmox LXC backup job only after the baseline is stable.
The OMV-backed job requires `tmpdir=/var/tmp` because the unprivileged backup
previously failed when its temporary directory was NFS-backed.

Run on: Proxmox host shell.

```bash
vzdump 111 --storage omv-backups --mode snapshot --compress zstd --tmpdir /var/tmp
ls -lh /mnt/pve/omv-backups/dump/vzdump-lxc-111-*.tar.zst | tail -n 1
```

Expected result: `vzdump` finishes successfully, removes its temporary snapshot,
and creates a non-zero archive. A current production proof exists in canonical
state, but a fresh rebuild requires a fresh archive.

For the recovery proof, restore the archive to a temporary CT ID with networking
disabled and do not start it on VLAN 30. Mount the stopped CT filesystem from
Proxmox, verify `/opt/frigate/docker-compose.yml`, baseline/production config,
database, and certificate paths exist, then unmount and remove the disposable
CT after recording evidence. This is an approval-gated destructive cleanup.

Expected evidence:

- archive decompression/restore completes;
- expected files are non-zero in the mounted temporary root;
- production CT 111 remains running and singular at `192.168.30.20`;
- temporary CT is removed only after verification.

Until that isolated proof passes, record **backup created, restore unproven**.

## End-of-phase validation

Run on: Frigate CT console or SSH.

```bash
cd /opt/frigate
docker compose config -q
docker compose ps
curl -fsS http://127.0.0.1:5000/api/version
curl -fsS http://127.0.0.1:5000/api/stats >/tmp/frigate-final-stats.json
docker exec frigate ps aux | grep '[d]etector:ov'
findmnt -T /mnt/nas/frigate || true
ss -lntup | grep -E ':(5000|8554|8555|8971)[[:space:]]'
docker compose logs --since=10m frigate | grep -Ei 'error|failed|permission denied|frame.*read' || true
```

Expected result: Compose validates, the intended containers are running, API
version/stats return, the OpenVINO detector process exists, recording storage
is the intended mount when enabled, listeners are present, and any matched log
line is explained rather than ignored because of `|| true`.

Run on: Admin laptop with the project CA trusted.

```powershell
Test-NetConnection 192.168.30.20 -Port 8971
try {
    Invoke-WebRequest -Uri 'https://192.168.30.20:8971/api/version' -MaximumRedirection 0
} catch {
    $_.Exception.Response.StatusCode.value__
}
Test-NetConnection 192.168.30.20 -Port 5000
```

Expected result:

- Compose validates and container is healthy;
- internal API reports the recorded Frigate version;
- authenticated HTTPS returns `401` when logged out and is trusted by the client;
- port 5000 succeeds only from approved HA/monitoring sources and is denied from
  ordinary clients; if the admin laptop is not approved, its test must fail;
- OpenVINO and VA-API remain healthy with active camera streams;
- MQTT is connected over TLS;
- recording path is OMV-backed before recording is enabled;
- each enabled camera sustains expected FPS without repeating stream errors;
- HA entities and viewing work without exposing raw RTSP credentials;
- current CT backup exists and isolated recovery is proven or explicitly open.

## Failure recovery matrix

| Failure | Safe response | Proof before continuing |
|---|---|---|
| CT 111/VM 101 identity conflict | Stop; identify the production owner. Never run both. | Only CT 111 owns `.20`; rollback VM is disconnected/off. |
| DRM devices absent on host | Stop; inspect host driver/device state. | Both nodes exist before mapping. |
| CT DRM permission denied | Match `dev0`/`dev1` GIDs to CT groups; retain `0660`. | `vainfo` succeeds inside CT and container. |
| Docker fails in LXC | Verify unprivileged CT plus nesting/keyctl; keep signed repository. | `hello-world` and Compose version pass. |
| Compose/config invalid | Restore migration-safe baseline and recreate. | Healthy container, API version, detector process. |
| Frigate restart loop | Read first fatal log; do not repeatedly restart. | Root cause corrected and 10-minute log stays clean. |
| MQTT CA/auth failure | Verify clock, CA, SAN, port 8883, user, and source firewall. | OpenSSL verify code 0 and MQTT connected. |
| HTTPS untrusted | Verify served certificate/SAN and client CA trust; do not bypass validation. | Logged-out request reaches trusted `401`. |
| Admin password lost | Use one-start reset flag, store replacement, remove flag. | Permanent login works and reset flag guard passes. |
| RTSP timeout/auth error | Return to bench checklist; verify PoE, VLAN, path, codec, and account. | `ffprobe` reports both real streams. |
| Camera works in VLC but not Frigate | Check RTSP auth mode and TCP stream from CT; ANNKE required `Digest/Basic`. | Stable Frigate FPS without auth errors. |
| OpenVINO/VA-API failure | Check mapped nodes/GIDs and logs; CPU fallback is diagnostic only. | Detector and hardware decode return. |
| OMV path permission denied | Stop recording; verify host mount, CT `mp0`, and UID 100000 ACL/default ACL. | CT write/read/delete and fresh segment pass. |
| OMV mount missing | Stop Frigate before local root fills; restore host mount/CT bind. | `findmnt` proves the exact source before restart. |
| HA integration unavailable | Prove MQTT and HA-to-5000 path separately. | API reachable from HA and entities recover. |
| Backup restore fails | Preserve production; retry a known archive in a fresh isolated CT. | Expected files are verified without network identity conflict. |

## Completion checklist

- [ ] CT 111 is unprivileged and matches canonical CPU/RAM/disk/VLAN/startup settings.
- [ ] Retired VM 101 is absent or stopped, disconnected, and `onboot=0`.
- [ ] Shared DRM devices use matching render/video GIDs and `0660` permissions.
- [ ] Debian packages, Docker Engine, Compose, `vainfo`, and `hello-world` pass.
- [ ] Migration-safe no-camera baseline starts healthy and its rollback is rehearsed.
- [ ] Frigate image digest and application version are recorded.
- [ ] CT firewall and Fail2ban allow/deny paths are tested from real sources.
- [ ] MQTT CA validation, valid connection, and invalid-auth rejection pass.
- [ ] Frigate HTTPS certificate is trusted and unauthenticated UI request returns `401`.
- [ ] OMV recording path is proven before recording is enabled.
- [ ] Every enabled camera passed bench `ffprobe`, FPS, audio, and log checks.
- [ ] OpenVINO and VA-API remain active under camera load.
- [ ] HA integration uses source-restricted port 5000 and camera entities/viewing work.
- [ ] Temporary admin reset flag is absent after any recovery.
- [ ] Fresh CT backup exists; isolated restore proof passes or remains explicitly open.
- [ ] WebRTC/audio requirements and observed behavior are recorded per camera.

Continue to [Phase 05 - Docker Host](05-docker-host.md) after the migration-safe
Frigate foundation is accepted. Phase 06 must complete OMV recording storage
before production recording is enabled.

## October 10, 2026 — idle configuration publisher retention

The outage was CT-local memory/cache pressure, not host-wide RAM exhaustion.
The main `python3 -u -m frigate` process held about 5 GiB anonymous RSS;
CT 111 used 5.96/6 GiB with no swap and only about 4 MiB ordinary file cache.
The host still had 21 GiB available, but load was 95/113/115 and disk readers
were blocked in `folio_wait_bit_common`. CT root storage (`dm-8`) had accumulated
96.8 TB reads; a five-second NVMe sample measured 11,784 reads/s and 459 MiB/s.
Two historical cgroup OOM kills were present. October 8 kernel warnings also
included monitoring VM102 disk workers blocked for more than 122 seconds.
NVMe SMART passed with zero media errors/error-log entries; the bounded kernel
check found no NVMe timeout/reset or NFS-server failure.

### Confirmed mechanism

In this installed 0.17.1 / pyzmq 26.2.1 / libzmq 4.3.5 runtime:

1. Disconnected streams repeatedly exit `video.capture_frames` and start again.
   Each invocation constructs a `CameraConfigUpdateSubscriber` and closes it
   on exit. The `finally` cleanup exists; this is not an omitted Python close.
2. Subscribers connect to the main process's idle `ConfigPublisher` at
   `ipc:///tmp/cache/config`. Native tracing caught 15 retained connection
   allocation groups in 60 seconds, including 18,160-byte malloc and two
   16,400-byte calloc blocks per group.
3. A conditional malloc breakpoint identified `libzmq` on its publisher IO
   thread. A 12-second targeted syscall trace showed that thread accepting
   subscriptions from the three capture PIDs and closing them about three
   seconds later. The listening FD mapped specifically to `/tmp/cache/config`.
4. Pending native attach/termination work accumulates when the application
   does not operate on the PUB socket. Two `getsockopt(zmq.EVENTS)` calls, with
   time for its IO thread to respond, followed by `malloc_trim(0)`, reduced
   main RSS from about 5.4 GiB to 593 MiB **without restarting**. `malloc_trim`
   alone previously reclaimed only about 11 MiB.

Python inspection found empty frame/object caches, 80 bounded stats samples,
and no large application container accounting for the heap. The 188 KiB DB
and approximately 56 MiB shared-memory allocation also did not account for it.
Do not mislabel this as the separately reported recording-manager,
embeddings-manager, or FFmpeg heap leaks.

The isolated reproduction is
`scripts/validation/frigate_zmq_idle_pub_repro.py`. It opens a unique temporary
IPC endpoint in a **separate process**, with no production socket, camera,
database or MQTT access. It compares an idle publisher against a publisher
whose owner thread regularly processes `ZMQ_EVENTS` during subscriber churn.
The final 600-reconnect experiment measured RSS 17,084,416 → 24,870,912 bytes;
after polling/trim it returned to 18,206,720, and the polling case ended at
18,132,992. Exact RSS depends on allocator and platform; compare deltas.

Run using Frigate's existing Python/pyzmq, after copying the script to CT 111:

```bash
docker cp /opt/frigate/incident-20261010/reproduce.py frigate:/tmp/frigate-zmq-repro.py
docker exec frigate python3 /tmp/frigate-zmq-repro.py
```

Do not add a background polling thread around a production ZeroMQ socket:
socket operations must be serialized on its owner thread. The live debugger
experiment was a controlled forensic intervention, not a scheduled remedy.
Relevant source:
[installed publisher](https://github.com/blakeblackshear/frigate/blob/v0.17.1/frigate/comms/config_updater.py),
[capture lifecycle](https://github.com/blakeblackshear/frigate/blob/v0.17.1/frigate/video.py),
and [libzmq command processing](https://github.com/zeromq/libzmq/blob/v4.3.5/src/socket_base.cpp).
The [0.17.2 publisher](https://github.com/blakeblackshear/frigate/blob/v0.17.2/frigate/comms/config_updater.py)
still lacks idle event polling; a blind update is not evidence of repair.

### Recovery and present operating state

- `pct set 111 --memory 12288` restored cache headroom immediately. Parent
  cgroup `memory.max=12884901888`, `memory.high=12784238592`, CT `/proc/meminfo`
  and Docker's denominator were verified. The dedicated CT's Docker daemon
  was restarted to refresh its cached former 6 GiB denominator. No host
  packages were upgraded; debugger dependencies were extracted under
  `/var/tmp/frigate-diag-tools/` rather than installed.
- Before YAML/Compose changes, saved originals and bounded heap/allocation
  evidence under CT `/opt/frigate/incident-20261010/` (directory mode 700).
  Files include `config.yml.before`, `docker-compose.yml.before`,
  `frigate-heap-summary.json`, `frigate-malloc-before.xml`,
  `frigate-live-memory.bin`, and `reproduce.py`. These stay outside the vault.
- Set `enabled: false` on all three intentionally disconnected cameras in
  source and live config. Validated the live candidate with
  `FrigateConfig.parse(...)` using the existing container environment before
  installing it. Stream/detection/recording definitions and host-only secrets
  remain available for later reconnection.
- Pinned the already installed 0.17.1 image to manifest digest
  `1724960349dad0bd2ae8ec884171a6fd5755a4dc242a0e66cadbda9c0e85c99b`.
  `docker compose config -q` and
  `docker compose up --pull never -d --force-recreate frigate` passed.
- Frigate returned healthy, API version responded, disabled cameras had no
  capture/process PIDs, unauthenticated HTTPS returned 401, and both host/CT
  NFS mounts retained the expected OMV export. One-minute host load fell below
  1, blocked tasks to zero and IO wait cleared. Camera/inference/recording
  acceptance remains unavailable while camera hardware is disconnected.
- Follow-up at 20:56–20:57 BST: main RSS about 324 MiB, Docker working memory
  about 675 MiB/12 GiB, CT usage including cache about 1.45 GiB, no new OOM
  kills, and zero CT-root reads in a five-second sample. MQTT TLS verification
  received retained Frigate availability `online`. HA/Homepage HTTPS returned
  200; Kuma returned 302. Intel GPU usage telemetry retains a separate PMU
  permission error; no capability/firewall change was made to silence it.
- Final 20:59 BST check: healthy, zero Docker restart count, 678 MiB working
  memory and host one-minute load 0.19. Compose source/live structures match;
  repository Frigate config passes the installed schema and matches live
  structure after masking host-only RTSP userinfo. The reproduction in the
  repository was rerun successfully in the recovered container.

The initial recovery above left upstream code unpatched. The subsequent local
lifecycle repair and RAM reassessment are recorded below. Real-stream GPU,
recording/playback and HA acceptance still require physical camera reconnection.

Rollback only the incident edits when deliberately resuming camera testing:
restore the two `.before` files into their original CT paths, validate Compose,
then recreate with `--pull never`. Preserve the current 12 GiB limit until
memory safety is established; restoring 6 GiB with the original retry trigger
would reintroduce the failure. Frigate's log timestamps during this incident
were UTC; host timestamps and this procedure use BST.

### Permanent local lifecycle repair and RAM reassessment

The pinned0.17.1 image now has a tracked read-only overlay:
[[../../../configs/frigate/patches/config_updater.py]]. ConfigPublisher's
dedicated owner thread creates, operates, polls and destroys its PUB socket.
MQTT/API callers submit bounded synchronous requests, so multipart messages
cannot interleave. Idle `ZMQ_EVENTS` polling every100ms processes native
connection cleanup; there is no cross-thread socket polling or malloc_trim
remedy. Shutdown drains accepted requests, closes with linger0 and joins the
owner. Startup/send failures propagate to callers. ConfigSubscriber and wire
topics/payloads remain unchanged.

Compose binds `/opt/frigate/patches/config_updater.py` over the image module
read-only. This survives recreation and host restarts. The patch is coupled
to the pinned image: compare/port it or remove after proving an equivalent
upstream fix whenever updating Frigate. See the [[../../../configs/frigate/patches/README|overlay guide]].

Validation using Frigate's installed Python/pyzmq:

- Three functional tests passed:100 concurrent multipart updates delivered
  intact, repeatable bounded shutdown/post-stop rejection, bind failure propagation.
- Candidate actual-class3600-reconnect test: RSS23,142,400→23,257,088bytes,
  only114,688bytes growth after warmup, without forced collection or trimming.
- Deployed-class repeat: maximum post-warmup growth491,520bytes.
- **Live** publisher12000 read-only reconnects: main RSS339,898,368→341,602,304
  bytes, maximum growth1,703,936bytes. The original idle lifecycle retained
  native connection groups; this repair drains them throughout churn.
- A separate `frigate-lifecycle-test` container used the same pinned image and
  overlay, network isolation, separate config/database/media, a4GiB memory
  limit and three lavfi720p/10fps cameras. OpenVINO GPU inference ran around4ms,
  all streams processed~10fps without skipped frames, software-H264 recording
  segments were written, and working memory was~1.2GiB. Synthetic FFmpeg
  interruption/recovery exercised real capture retries; production cameras,
  MQTT and NAS recordings were not touched. This does not certify real-camera
  codecs, VA-API decoding, upstream RTSP reconnects or long-term recording load.

The lifecycle fix removes the reason for the emergency12GiB allocation.
CT111 is now **2CPU / 6GiB / no swap**, retaining several GiB above the measured
idle and synthetic working sets for real-stream processes, tmpfs and file cache.
Do not shrink to the smallest idle footprint. Re-evaluate below6GiB only after
physical cameras are reconnected and sustained real-stream/recording peaks,
cache headroom and PSI are measured. Disabled production cameras remain disabled.

Deployment commands (CT paths):

```sh
# Save Compose before overlay deployment; retain host-only secrets/config.
cp /opt/frigate/docker-compose.yml /opt/frigate/incident-20261010/docker-compose.before-lifecycle.yml
# Upload tracked patch into /opt/frigate/patches/, then add the tracked bind mount.
cd /opt/frigate
docker compose config -q
docker compose up --pull never -d --force-recreate frigate
docker exec frigate python3 /tmp/frigate_publisher_lifecycle_test.py --churn
docker exec frigate python3 /tmp/frigate_publisher_lifecycle_test.py --live-churn
# On Proxmox, after validation:
pct set 111 --memory 6144
# Refresh Docker's cached denominator in the dedicated CT and verify recovery.
pct exec 111 -- systemctl restart docker
```

To roll back **only the lifecycle overlay**, restore the saved pre-lifecycle
Compose, validate and recreate using `--pull never`; keep disconnected cameras
disabled. Restore12GiB first if deliberately testing the original leaking
publisher under reconnects. Never combine rollback to the defective publisher
with re-enabled failing cameras at6GiB. The previous `.before` YAML contains
the original retry trigger and is not the appropriate lifecycle-only rollback.

Selected test evidence stays under CT `/opt/frigate/incident-20261010/`.
The isolated test container/media are removed after acceptance. Always-on
[[../../procedures/resource_pressure_monitor|resource alerts]] remain active.

Final6GiB check: cgroup `memory.max=6442450944`, Docker reports6GiB, Frigate
healthy with restart count0, working memory~670MiB and CT usable headroom~4.6GiB.
Memory PSI is0; cumulative OOM kills remain2. The overlay's SHA256 inside the
recreated container matches its host file (`ff482e7dfdf0dca929ca585b951cb6e50fb401ce9d2747671c882847dfbed303`).
Functional tests passed again after restart. Resource collector has all six
systems with no pending/active alerts and no blocked host tasks.
