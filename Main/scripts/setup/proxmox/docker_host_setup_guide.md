# Docker Host VM Setup Guide

**VM ID:** 103  
**Hostname:** docker-host  
**IP:** 192.168.20.102  
**VLAN:** 20, Automation / trusted app services  
**Host:** Proxmox on MINIX NEO Z350  
**Purpose:** Central Docker Compose host for lightweight trusted internal containers  
**First workload:** Bambuddy, exposed at `http://192.168.20.102:8000`

VM 103 is a QEMU VM on Proxmox. It is not a Proxmox LXC container and not part
of Home Assistant OS. Docker runs inside this Debian VM so small internal app
containers can share one managed host without changing the role of HAOS,
Frigate, NAS/storage, or future DMZ services.

Keep Frigate on VM 101 because it belongs on VLAN 30 and may need iGPU
passthrough. Keep Home Assistant OS on VM 100 because HAOS Supervisor is its
own appliance model.

---

## Current Live Build

| Setting | Value |
|---|---|
| OS | Debian GNU/Linux 13, trixie genericcloud |
| Hostname | docker-host |
| IP | 192.168.20.102/24 |
| Gateway/DNS | 192.168.20.1 |
| MAC | BC:24:11:BC:B8:1A |
| Machine | q35 |
| BIOS | OVMF, pre-enrolled keys disabled |
| Disk | local-lvm, 16 GiB, SCSI, discard on, SSD emulation |
| CPU/RAM | 1 core, 1024 MiB |
| Network | vmbr0, VLAN tag 20, VirtIO |
| Boot | onboot enabled, startup order 3 |

Completed live:

- Proxmox VM name set to `docker-host`.
- Guest hostname set to `docker-host`.
- `qemu-guest-agent` installed and active.
- Docker and Docker Compose installed and active.
- Bambuddy image `ghcr.io/maziggy/bambuddy:latest` pulled.
- Bambuddy stack staged at `/opt/stacks/bambuddy`.
- UFW enabled with default deny incoming and scoped allows.
- Router temporary internet rule removed after image pull.

Not started yet:

- Bambuddy container is intentionally not running until real credentials and
  printer details are added to `/opt/stacks/bambuddy/.env`.

---

## Host Policy

Use this VM for lightweight trusted internal containers, such as:

- Bambuddy
- HA-adjacent helper services
- internal dashboards or status pages
- MQTT helpers or bridges
- local admin utilities

Do not place these here without a separate architecture review:

- Frigate or camera/NVR workloads
- Home Assistant OS or HA Supervisor workloads
- NAS/storage appliances
- public/DMZ-facing services
- privileged hardware/USB passthrough services

---

## Phase 1 - Reproduce VM 103 From Debian Cloud Image

These commands are for rebuilding or reproducing the current live VM.

```bash
cd /var/lib/vz/template/iso
wget -O debian-13-genericcloud-amd64.qcow2 \
  https://cloud.debian.org/images/cloud/trixie/latest/debian-13-genericcloud-amd64.qcow2

qm create 103 \
  --name docker-host \
  --memory 1024 \
  --cores 1 \
  --cpu host \
  --machine q35 \
  --bios ovmf \
  --ostype l26 \
  --net0 virtio,bridge=vmbr0,tag=20,macaddr=BC:24:11:BC:B8:1A \
  --agent enabled=1 \
  --onboot 1 \
  --startup order=3

qm set 103 --efidisk0 local-lvm:0,efitype=4m,pre-enrolled-keys=0
qm importdisk 103 debian-13-genericcloud-amd64.qcow2 local-lvm
qm set 103 --scsihw virtio-scsi-single
qm set 103 --scsi0 local-lvm:vm-103-disk-0,discard=on,ssd=1,cache=writeback
qm resize 103 scsi0 16G
qm set 103 --boot order=scsi0
qm set 103 --ide2 local-lvm:cloudinit
qm set 103 --ciuser root
qm set 103 --sshkeys /root/proxmox-admin.pub
qm set 103 --ipconfig0 ip=192.168.20.102/24,gw=192.168.20.1
qm set 103 --nameserver 192.168.20.1
qm set 103 --searchdomain home.local
qm start 103
```

After first boot:

```bash
ssh root@192.168.20.102
hostnamectl set-hostname docker-host
apt-get update
apt-get install -y qemu-guest-agent
systemctl enable --now qemu-guest-agent
```

---

## Phase 2 - Temporary Internet Bootstrap

The router should normally block the Docker host from internet access. Enable
the `TEMP Docker Host Update Access` rule only while installing packages or
pulling container images. Remove it immediately afterwards.

Required temporary allowance:

- Source: `192.168.20.102`
- Destination zone: WAN
- Protocol: TCP
- Ports: 80, 443

After bootstrap, confirm the temp rule is gone:

```bash
uci show firewall | grep -i "TEMP Docker Host" || echo "temp rule absent"
```

Confirm internet is blocked from the VM:

```bash
curl -4I --connect-timeout 5 --max-time 8 https://download.docker.com/
# Expected after cleanup: connection failure/refused by router policy.
```

---

## Phase 3 - Install Docker

Run on VM 103 while temporary internet access is active:

```bash
apt-get update
apt-get install -y ca-certificates curl gnupg ufw

install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg \
  | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  > /etc/apt/sources.list.d/docker.list

apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
systemctl enable --now docker

docker --version
docker compose version
```

Remove the temporary router internet rule after package/image pulls are complete.

---

## Phase 4 - Configure Local Firewall

Current UFW policy on VM 103:

```bash
ufw default deny incoming
ufw default allow outgoing
ufw default deny routed
ufw allow from 192.168.10.0/24 to any port 22 proto tcp comment "Management SSH"
ufw allow from 192.168.10.0/24 to any port 8000 proto tcp comment "Management to Bambuddy UI"
ufw allow from 192.168.1.0/24 to any port 8000 proto tcp comment "LAN to Bambuddy UI"
ufw allow from 192.168.20.0/24 to any port 8000 proto tcp comment "Automation to Bambuddy UI"
ufw --force enable
ufw status verbose
```

Add ports only for workloads that are intentionally exposed. Keep workload
access scoped by source subnet.

---

## Phase 5 - Stack Layout

All Compose workloads live under `/opt/stacks/<service>/`.

```bash
mkdir -p /opt/stacks/bambuddy/{data,logs}
```

Bambuddy Compose file:

```text
/opt/stacks/bambuddy/docker-compose.yml
```

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

Example environment file:

```text
/opt/stacks/bambuddy/.env.example
```

```env
MQTT_HOST=192.168.20.101
MQTT_PORT=1883
MQTT_USER=mqtt
MQTT_PASSWORD=<set-from-bitwarden>
```

For the current pre-TLS stage, use MQTT port `1883`. After Mosquitto TLS is
configured and verified, change this to `8883` and add whatever TLS settings
Bambuddy requires.

When ready to start the service:

```bash
cd /opt/stacks/bambuddy
cp .env.example .env
nano .env
chmod 600 .env
docker compose up -d
docker compose logs bambuddy -f
```

---

## Phase 6 - Connect Bambuddy

Use the Bambuddy web UI as the canonical place to add:

- P1S printer IP: `192.168.35.200`
- P1S access code: from the printer screen
- P1S serial: from the printer or Bambu app
- Home Assistant URL: `http://192.168.20.101:8123`
- Home Assistant long-lived token: create in HA profile security settings

Open the UI from an allowed management or LAN client:

```text
http://192.168.20.102:8000
```

DNS aliases:

```text
docker-host.home.local -> 192.168.20.102
bambuddy.home.local    -> 192.168.20.102
```

---

## Phase 7 - Home Assistant Package

Do not deploy the Bambuddy HA package until the real P1S serial is known and
Bambuddy is publishing MQTT state.

Repo source file:

```text
configs/home-assistant/bambuddy_p1s_package.yaml
```

Before deployment, replace every `<P1S_SERIAL>` placeholder with the real serial:

```bash
grep '<P1S_SERIAL>' /config/packages/bambuddy_p1s_package.yaml
sed -i 's/<P1S_SERIAL>/<REAL_SERIAL>/g' /config/packages/bambuddy_p1s_package.yaml
ha core check
ha core restart
```

---

## Verification

Run from VM 103:

```bash
hostname
docker --version
docker compose version
cd /opt/stacks/bambuddy && docker compose config

# HA API, same VLAN trust boundary
timeout 5 bash -lc '</dev/tcp/192.168.20.101/8123' && echo HA_8123_OK

# Mosquitto pre-TLS, same VLAN trust boundary
timeout 5 bash -lc '</dev/tcp/192.168.20.101/1883' && echo MQTT_1883_OK

# Internet should be blocked after temp rule removal
curl -4I --connect-timeout 5 --max-time 8 https://download.docker.com/
```

Expected current result:

- `hostname` returns `docker-host`
- Compose config renders from `/opt/stacks/bambuddy`
- `HA_8123_OK`
- `MQTT_1883_OK`
- External Docker download blocked

After the P1S is physically ready, also test:

```bash
nc -zv 192.168.35.200 8883
nc -zv 192.168.35.200 21
```

---

## Completion Checklist

- [x] VM 103 created from Debian 13 cloud image.
- [x] Proxmox VM name set to `docker-host`.
- [x] Guest hostname set to `docker-host`.
- [x] Static IP 192.168.20.102 configured through cloud-init.
- [x] VLAN 20 tagging configured on Proxmox net0.
- [x] Start at boot enabled, startup order 3.
- [x] MAC identified as BC:24:11:BC:B8:1A.
- [x] Docker installed and working.
- [x] Bambuddy image pulled.
- [x] `/opt/stacks/bambuddy/{data,logs}` created or ready.
- [x] `/opt/stacks/bambuddy/docker-compose.yml` staged.
- [x] `/opt/stacks/bambuddy/.env.example` staged.
- [x] UFW enabled with scoped access rules.
- [x] Temporary Docker host update access removed from router after image pull.
- [x] VM can reach HA API on 8123.
- [x] VM can reach Mosquitto pre-TLS on 1883.
- [ ] Real `/opt/stacks/bambuddy/.env` created with MQTT password.
- [ ] Bambuddy container started successfully.
- [ ] Bambuddy UI accessible at `http://192.168.20.102:8000`.
- [ ] P1S added in Bambuddy UI.
- [ ] Bambuddy connected to Home Assistant API.
- [ ] HA Bambuddy package deployed after serial placeholder replacement.
- [ ] P1S entities visible in Home Assistant.

---

## VM Reference

| ID | Name | VLAN | IP | RAM | Cores | Boot |
|---|---|---|---|---|---|---|
| 100 | home-assistant | 20 | 192.168.20.101 | 4096 MB | 2 | order 1 |
| 103 | docker-host | 20 | 192.168.20.102 | 1024 MB | 1 | order 3 |
