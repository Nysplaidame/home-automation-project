# Frigate NVR VM — Setup Guide
**VM ID:** 101  **IP:** 192.168.30.20 — VLAN 30 (NVR)
**Host:** Proxmox on MINIX NEO Z350
**Cameras:** 4x IP cameras at 192.168.30.21–24
**Storage:** Local SSD + NAS at 192.168.40.50

> VLAN 30 has no internet access by design. Frigate is reachable from VLAN 20 (HA) and VLAN 10 (Management) only.

---

## Phase 1 — Create the VM

### 1.1 — Download Debian 12 ISO

```bash
# FIX #21: Previous URL used path /debian-iso/ (does not exist) and hardcoded
# version 12.7.0 which 404s when newer point releases publish (e.g. 12.8.0+).
# Correct path is /debian-cd/current/ which always resolves to the latest stable
# point release without needing a version bump in this guide.
cd /var/lib/vz/template/iso
wget -O debian-12-netinst-amd64.iso \
    "https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-12-netinst-amd64.iso"
```

> No internet during install? Download the latest netinst ISO from
> `https://www.debian.org/distrib/netinst` on another machine and upload via
> `pve → local → ISO Images → Upload`. Do the Debian install while internet is available,
> then move the VM to VLAN 30 after Docker + Frigate are installed.

### 1.2 — VM settings

Click **Create VM** in Proxmox:

**General:** VM ID `101`, Name `frigate-nvr`, Start at boot ✅, Boot order `2`

**OS:** ISO `debian-12-netinst-amd64.iso`, Guest OS: Linux 6.x

**System:** Machine `q35`, BIOS `OVMF (UEFI)`, EFI Storage `local-lvm`, SCSI Controller `VirtIO SCSI single`, Pre-enroll keys/TPM unticked

**Disks:** Storage `local-lvm`, Size `64 GiB`, Bus `SCSI → scsi0`, Cache `Write back`, Discard ✅, SSD emulation ✅

> 64GB is enough for OS, Docker, and Frigate database.
> Recordings go to the NAS (VLAN 40) — see Phase 4.

**CPU:** Sockets `1`, Cores `2`, Type `host`

**Memory:** `4096` MiB, Ballooning unticked

**Network:** Bridge `vmbr0`, VLAN Tag `30`, Model `VirtIO`, Firewall unticked

Click **Finish**.

---

## Phase 2 — Install Debian

### 2.1 — Run the installer

`VM 101 → Start` then open **Console**. Select **Install**.

Key choices during install:

| Step | Value |
|---|---|
| Hostname | `frigate-nvr` |
| Domain | `home.local` |
| Root password | strong — save in password manager |
| New user | `admin` |
| Partition | Guided — entire disk, single partition |
| Software | Untick everything except `SSH server` + `standard system utilities` |

Boot after install.

### 2.2 — Set static IP

Log in as `root` on the console:

```bash
# Check the interface name first
ip link
# Will show something like ens18 or ens3

nano /etc/network/interfaces
```

Replace the `iface ... dhcp` line with:

```
auto ens18
iface ens18 inet static
    address 192.168.30.20
    netmask 255.255.255.0
    gateway 192.168.30.1
    dns-nameservers 192.168.30.1
```

```bash
systemctl restart networking
ip addr show ens18    # confirm 192.168.30.20
```

### 2.3 — Note the MAC address for DHCP reservation

```bash
ip link show ens18 | grep link/ether
```

Update `configs/openwrt/dhcp-config.conf` — replace the MAC in the `frigate-nvr` host entry.

### 2.4 — Harden the OS

```bash
apt-get update && apt-get upgrade -y
apt-get install -y curl wget htop nano ufw nfs-common

# SSH key auth — add your public key FIRST
mkdir -p ~/.ssh
echo "ssh-ed25519 AAAA...your-key" >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys

sed -i \
    -e 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' \
    -e 's/^#\?PermitRootLogin.*/PermitRootLogin prohibit-password/' \
    /etc/ssh/sshd_config
systemctl restart sshd

# VM-level firewall
ufw default deny incoming
ufw default allow outgoing
ufw allow from 192.168.20.0/24 to any port 5000    # HA -> Frigate web/API (Frigate <0.14)
# H-7 fix: Frigate 0.14+ moved web UI/API from port 5000 to 8971. Both rules kept
# so the guide works regardless of Frigate version.
ufw allow from 192.168.20.0/24 to any port 8971    # HA -> Frigate web/API (Frigate 0.14+)
ufw allow from 192.168.10.0/24 to any port 8971    # Management -> Frigate UI (Frigate 0.14+)
ufw allow from 192.168.20.0/24 to any port 8554    # HA -> RTSP restream
ufw allow from 192.168.10.0/24 to any port 22      # Management SSH
# Bambuddy runs on dedicated VM 103. Do not open port 8000 on VM 101.
ufw enable
```

---

## Phase 3 — Install Docker and Frigate

### 3.1 — Install Docker

```bash
apt-get install -y ca-certificates curl gnupg lsb-release

install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | \
    gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
    https://download.docker.com/linux/debian $(lsb_release -cs) stable" \
    > /etc/apt/sources.list.d/docker.list

apt-get update && apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

docker --version && docker compose version
```

### 3.2 — Directory structure

```bash
mkdir -p /opt/frigate/config
mkdir -p /opt/frigate/storage
mkdir -p /opt/frigate/db
```

### 3.3 — Docker Compose file

> The inline compose below now matches `configs/frigate/docker-compose.yml`
> in the safety vault, including the `/db` volume, the separate MQTT password
> variable, and the NAS mount commented out pending Phase 4. Keep both in sync if you
> edit either — the vault file is the authoritative source; copy it here when it changes.

```bash
# Copy the vault file directly rather than cat-ing inline (avoids drift):
cp /path/to/vault/configs/frigate/docker-compose.yml /opt/frigate/docker-compose.yml

# Or recreate manually — must match configs/frigate/docker-compose.yml exactly:
cat > /opt/frigate/docker-compose.yml << 'COMPOSE'
services:
  frigate:
    container_name: frigate
    image: ghcr.io/blakeblackshear/frigate:stable
    restart: unless-stopped
    shm_size: "256mb"
    devices:
      # Uncomment after enabling iGPU passthrough (Phase 6):
      # - /dev/dri/renderD128:/dev/dri/renderD128
    volumes:
      - /opt/frigate/config:/config
      - /opt/frigate/storage:/media/frigate
      - /opt/frigate/db:/db
      # NAS recordings -- uncomment after Phase 4 NAS setup:
      # - /mnt/nas/frigate:/media/frigate/recordings
      - /etc/localtime:/etc/localtime:ro
      - /opt/frigate/certs:/config/certs:ro
    environment:
      - FRIGATE_RTSP_PASSWORD=${FRIGATE_RTSP_PASSWORD}
      - FRIGATE_MQTT_PASSWORD=${FRIGATE_MQTT_PASSWORD}
    network_mode: host
    tmpfs:
      - /tmp/cache

COMPOSE

# BEFORE FIRST START:
mkdir -p /opt/frigate/db
mkdir -p /opt/frigate/certs
# Set all variables in /opt/frigate/.env:
# FRIGATE_RTSP_PASSWORD, FRIGATE_MQTT_PASSWORD
```

### 3.4 — Frigate config.yml

```bash
cat > /opt/frigate/config/config.yml << 'CFG'
# Frigate NVR Config — frigate-nvr 192.168.30.20
# Update RTSP URLs to match your actual camera streams

mqtt:
  enabled: true
  host: 192.168.20.101
  port: 8883  # A9-3 fix: was 1883 (pre-TLS). Post-TLS system uses 8883.
  # Stage 1 (pre-TLS initial setup): change to port 1883 for first test,
  # then switch back to 8883 after docs/procedures/ssl_tls_guide.md MQTT TLS steps.
  tls_insecure: false
  tls_ca_certs: /config/certs/ca-cert.pem  # matches configs/frigate/config.yml
  user: mqtt
  password: "{FRIGATE_MQTT_PASSWORD}"   # FIX #15/#14: must be MQTT password, not RTSP

database:
  path: /db/frigate.db

detectors:
  cpu1:
    type: cpu
    num_threads: 2

record:
  enabled: true
  retain:
    days: 7
    mode: motion
  events:
    retain:
      default: 14
      mode: active_objects

snapshots:
  enabled: true
  retain:
    default: 14

cameras:
  cam_01:
    ffmpeg:
      inputs:
        - path: rtsp://admin:{FRIGATE_RTSP_PASSWORD}@192.168.30.21:554/stream1
          roles: [detect, record]
    detect:
      enabled: true
      width: 1920
      height: 1080
      fps: 5
    objects:
      track: [person, car, cat, dog]

  cam_02:
    ffmpeg:
      inputs:
        - path: rtsp://admin:{FRIGATE_RTSP_PASSWORD}@192.168.30.22:554/stream1
          roles: [detect, record]
    detect:
      enabled: true
      width: 1920
      height: 1080
      fps: 5
    objects:
      track: [person, car, cat, dog]

  cam_03:
    ffmpeg:
      inputs:
        - path: rtsp://admin:{FRIGATE_RTSP_PASSWORD}@192.168.30.23:554/stream1
          roles: [detect, record]
    detect:
      enabled: true
      width: 1920
      height: 1080
      fps: 5
    objects:
      track: [person, car]

  cam_04:
    ffmpeg:
      inputs:
        - path: rtsp://admin:{FRIGATE_RTSP_PASSWORD}@192.168.30.24:554/stream1
          roles: [detect, record]
    detect:
      enabled: true
      width: 1920
      height: 1080
      fps: 5
    objects:
      track: [person, car]
CFG
```

> **Before starting:** replace the RTSP paths with your actual camera URLs.
> Most cameras use `rtsp://<ip>/stream1` or `rtsp://<ip>/Streaming/Channels/1`.
> Check your camera model's documentation.

### 3.5 — Start Frigate

```bash
cd /opt/frigate
docker compose up -d
docker compose logs -f frigate
# Wait for: "Frigate is running" in logs
```

<!-- N-6 fix: primary URL updated to 8971 (Frigate 0.14+ UI/API port). Port 5000 is now metrics-only. -->
Open `http://192.168.30.20:8971` from your management laptop or via HA.
> **Note:** If running Frigate <0.14, use port 5000 instead. Check your version: `docker inspect frigate | grep -i image` on the Frigate VM. UFW rules for both ports are configured above.

---

## Phase 4 — NAS storage for recordings

When the Raspberry Pi NAS is online at `192.168.40.50`:

```bash
mkdir -p /mnt/nas/frigate

# Test NFS mount
mount -t nfs 192.168.40.50:/share/frigate /mnt/nas/frigate
df -h /mnt/nas/frigate    # confirm mounted

# Add to fstab for auto-mount at boot
echo "192.168.40.50:/share/frigate /mnt/nas/frigate nfs rw,soft,intr,timeo=30,_netdev 0 0" \
    >> /etc/fstab
```

Then update `/opt/frigate/docker-compose.yml` — swap the storage volume line:
```yaml
      # - /opt/frigate/storage:/media/frigate    # comment out local
      - /mnt/nas/frigate:/media/frigate           # use NAS
```

```bash
cd /opt/frigate && docker compose restart frigate
```

---

## Phase 5 — Home Assistant integration

### 5.1 — Add Frigate integration in HA

`Settings → Devices & Services → Add Integration → Frigate`

URL: `http://192.168.30.20:8971`  (Frigate 0.14+)  or  `http://192.168.30.20:5000`  (Frigate <0.14)

This creates entities for each camera:
- `camera.cam_01` – `camera.cam_04` (live streams)
- `binary_sensor.cam_01_person` etc. (motion/object detection)
- `sensor.cam_01_person_count` etc. (object counts)

### 5.2 — Verify MQTT events from Frigate

```bash
# Run on HA (Terminal add-on)
mosquitto_sub -h localhost -p 8883 --cafile /ssl/ca.crt -u mqtt -P <password> -t 'frigate/#' -v  # A8-2 fix: was -p 1883; post-TLS system uses 8883
```

You should see Frigate publishing stats and detection events.

### 5.3 — Frigate integration card (via HACS)

Install HACS in HA if not already done:
```bash
# HA Terminal
wget -O - https://get.hacs.xyz | bash -
# Restart HA, then: Settings → Integrations → HACS
```

Then install **Frigate Card** from HACS frontend section.
Add the card to a dashboard for a full camera view with event timeline.

---

## Phase 6 — Hardware acceleration (Intel iGPU + OpenVINO)

With 4 camera streams and AI detection, hardware acceleration is strongly
recommended. The i3-N350's Intel Xe GPU supports both VA-API hardware video
decode and OpenVINO GPU-accelerated object detection — together they reduce
CPU load from ~70-90% down to ~10-30%.

**Full setup guide:** `scripts/setup/proxmox/igpu_passthrough_guide.md`

That guide covers:
- Verifying IOMMU is active on the Proxmox host
- Identifying the iGPU PCI address and IOMMU group
- Adding the GPU as a PCI device to VM 101
- Installing Intel GPU drivers inside the VM (intel-media-va-driver, intel-opencl-icd)
- Updating docker-compose.yml with device mapping and group_add
- Replacing the CPU detector in config.yml with the OpenVINO GPU detector
- Adding `hwaccel_args: preset-vaapi` to all camera streams
- Verifying via `intel_gpu_top` and Frigate logs

The `devices` block in docker-compose.yml already has the line pre-commented:
```yaml
devices:
  # Uncomment after enabling iGPU passthrough (Phase 6):
  # - /dev/dri/renderD128:/dev/dri/renderD128
```

Follow the full guide before uncommenting — the device must exist in the VM
first or Frigate will fail to start.

---

## Completion checklist

**VM**
- [ ] VM 101 created: q35, OVMF, 4GB RAM, 64GB disk, VLAN 30
- [ ] Start at boot, boot order 2
- [ ] Debian 12 installed, minimal profile

**OS**
- [ ] Static IP: 192.168.30.20/24, gw 192.168.30.1
- [ ] MAC noted and added to dhcp-config.conf
- [ ] SSH key auth, password auth disabled
- [ ] UFW rules applied

**Frigate**
- [ ] Docker + Docker Compose installed
- [ ] /opt/frigate/ structure created
- [ ] docker-compose.yml written
- [ ] config/config.yml written with actual camera RTSP URLs
- [ ] Frigate container running, UI accessible at http://192.168.30.20:8971 (0.14+) or :5000 (<0.14)
- [ ] All 4 cameras streaming and detecting

**Storage**
- [ ] Local /opt/frigate/storage working
- [ ] NAS mount configured when VLAN 40 NAS is online

**Hardware acceleration**
- [ ] iGPU passthrough configured (see igpu_passthrough_guide.md)
- [ ] OpenVINO detector active in config.yml
- [ ] VA-API hwaccel enabled on all cameras
- [ ] `intel_gpu_top` confirms GPU activity during detection
- [ ] Frigate integration added in HA
- [ ] Camera entities visible in HA
- [ ] MQTT events flowing (frigate/# topics visible)

---

## Quick reference

| Item | Value |
|---|---|
| VM ID | 101 |
| OS | Debian 12 (Bookworm) |
| IP | 192.168.30.20 / VLAN 30 |
| Web UI | http://192.168.30.20:8971 (Frigate 0.14+) or :5000 (<0.14) |
| RTSP restream | rtsp://192.168.30.20:8554/<camera_name> |
| Cameras | 192.168.30.21 / .22 / .23 / .24 |
| Docker compose | /opt/frigate/docker-compose.yml |
| Config | /opt/frigate/config/config.yml |
| Local recordings | /opt/frigate/storage |
| NAS recordings | /mnt/nas/frigate (after NAS setup) |

## Troubleshooting

| Symptom | Check |
|---|---|
| Camera offline in Frigate | Test stream directly: `ffprobe rtsp://<ip>/stream1` |
| Frigate can't reach MQTT | From VM: `nc -zv 192.168.20.101 8883` (post-TLS) |
| HA can't reach Frigate | Confirm firewall allows VLAN 20 → VLAN 30:8971 (0.14+) or :5000 (<0.14) |
| High CPU | Enable iGPU passthrough + VA-API + OpenVINO (Phase 6 + igpu_passthrough_guide.md) |
| Disk full | Reduce `record.retain.days` or mount NAS |
| Container won't start | `docker compose logs frigate` |
