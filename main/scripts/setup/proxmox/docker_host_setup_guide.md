# Docker Host VM Setup Guide

**VM ID:** 103  
**Hostname:** docker-host  
**IP:** 192.168.20.102  
**VLAN:** 20, Automation / trusted app services  
**Host:** Proxmox on MINISFORUM M1 Pro-125H
**Purpose:** Central Docker Compose host for lightweight trusted internal containers and Tailscale host-route access
**First workload:** Bambuddy, exposed at `http://192.168.20.102:8000`

VM 103 is a QEMU VM on Proxmox. It is not a Proxmox LXC container and not part
of Home Assistant OS. Docker runs inside this Debian VM so small internal app
containers can share one managed host without changing the role of HAOS,
Frigate, OMV/storage, or future DMZ services.

Keep Frigate on CT 111 because it belongs on VLAN 30 and uses shared-iGPU
passthrough. Keep Home Assistant OS on VM 100 because HAOS Supervisor is its
own appliance model.

Keep local LLM, STT, TTS and wake-word inference on CT 114 `llm-host`. VM 103 is the
expected target for future containerized AI-adjacent query apps, but those apps
must define their own API, egress, monitoring, and firewall rules before
deployment.

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
| Disk | local-lvm, 32 GiB, SCSI, discard on, SSD emulation |
| CPU/RAM | 2 cores, 4096 MiB |
| Network | vmbr0, VLAN tag 20, VirtIO |
| Boot | onboot enabled, startup order 3 |

Completed live:

- Proxmox VM name set to `docker-host`.
- Guest hostname set to `docker-host`.
- `qemu-guest-agent` installed and active.
- Docker and Docker Compose installed and active.
- Bambuddy image `ghcr.io/maziggy/bambuddy:latest` pulled.
- Bambuddy stack staged at `/opt/stacks/bambuddy`.
- Homepage stack staged at `/opt/stacks/homepage` and live on port `3001`.
- Dozzle stack staged at `/opt/stacks/dozzle` and live on port `8081`.
- AdGuard Home stack staged at `/opt/stacks/adguard-home`, with DNS on
  `192.168.20.102:53` and admin UI on `8080`.
- Immich skeleton stack staged at `/opt/stacks/immich` and live on port `2283`;
  it uses local placeholder storage only until OMV storage and backup/restore
  are ready.
- ntfy stack staged at `/opt/stacks/ntfy` and live internally on port `8085`,
  with default access denied and credentials stored at `/root/ntfy-credentials.txt`.
- Watchtower monitor-only stack staged at `/opt/stacks/watchtower`, with
  `WATCHTOWER_MONITOR_ONLY=true` and notifications pointed at internal ntfy.
- SearXNG and Whoogle direct-access pre-flight stacks staged at
  `/opt/stacks/searxng` and `/opt/stacks/whoogle`, live on ports `8087` and
  `8088`.
- Non-secret rebuild templates for these live stacks and the host firewall are
  stored under `configs/docker-host/`; live secrets and app databases stay on
  VM 103 and are not committed.
- UFW enabled with default deny incoming and scoped allows.
- `docker-host-firewall.service` applies `DOCKER-USER` rules so Docker-published
  admin/DNS ports stay scoped despite Docker DNAT bypassing normal UFW input.
- Tailscale installed and `tailscaled` active; docker-host is authenticated as
  `100.94.122.18` and advertises only `192.168.20.101/32` and
  `192.168.40.50/32`.
- `/etc/apt/apt.conf.d/01proxy` keeps HTTP apt traffic through apt-cacher-ng and
  sends HTTPS apt traffic direct because apt-cacher-ng rejects HTTPS CONNECT.
- Router temporary internet rule removed after image pull.
- VM 103 disk was expanded online to 64 GiB on 2026-06-21.
- Uptime Kuma notification `ntfy Monitoring` is live and mapped to all active
  monitors through ntfy topic `monitoring`.
- UFW route rules allow only AdGuard's Docker bridge subnet `172.20.0.0/16`
  to reach upstream DNS ports `53/tcp`, `53/udp`, and `853/tcp`; this is
  required because UFW otherwise denies Docker routed traffic.
- Rebuildable source script for these routed DNS allowances is
  `configs/docker-host/system/docker-host-ufw-route-dns.sh` (deploy to
  `/usr/local/sbin/` and run after UFW baseline policy is active).
  The script is intentionally subnet-based (not pinned to `docker0`) because
  live Compose bridge names are usually `br-<hash>`.
- `fail2ban` is installed and enabled on docker-host, with an SSH jail defined
  at `/etc/fail2ban/jail.d/docker-host-sshd.local`.

Current service direction:

- Bambuddy is the first live workload.
- Tailscale will run as a host service, not a Compose workload.
- Tier 1 Compose stack still needing real storage cutover is Immich.
- Tier 2 notification service `ntfy` is pre-flight live for internal alerts.
- Tier 3 Watchtower is monitor-only and does not update containers.
- All Compose stacks use `/opt/stacks/<service>/`.

---

## Host Policy

Use this VM for lightweight trusted internal containers, such as:

- Bambuddy
- HA-adjacent helper services
- internal dashboards or status pages
- MQTT helpers or bridges
- local admin utilities
- future internal AI-adjacent query/tool apps after app-specific review
- AdGuard Home DNS filtering
- Immich gallery/photos, with OMV-backed media storage
- Tailscale as a host-level remote-access service

Do not place these here without a separate architecture review:

- Frigate or camera/NVR workloads
- Home Assistant OS or HA Supervisor workloads
- NAS/storage appliances
- public/DMZ-facing services
- privileged hardware/USB passthrough services
- local LLM, STT, or TTS inference services

---

## Phase 1 - Reproduce VM 103 From Debian Cloud Image

These commands are for rebuilding or reproducing the current live VM.

```bash
cd /var/lib/vz/template/iso
wget -O debian-13-genericcloud-amd64.qcow2 \
  https://cloud.debian.org/images/cloud/trixie/latest/debian-13-genericcloud-amd64.qcow2

qm create 103 \
  --name docker-host \
  --memory 4096 \
  --cores 2 \
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
qm resize 103 scsi0 32G
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

Current Tier 1 service additions:

```bash
ufw allow from 192.168.10.0/24 to any port 2283 proto tcp comment "Management to Immich"
ufw allow from 192.168.1.0/24 to any port 2283 proto tcp comment "LAN to Immich"
ufw allow from 192.168.60.10 to any port 2283 proto tcp comment "Monitoring to Immich"
ufw allow in on tailscale0 to any port 2283 proto tcp comment "Tailscale Immich"
ufw allow from 192.168.10.0/24 to any port 3001 proto tcp comment "Management to Homepage"
ufw allow from 192.168.1.0/24 to any port 3001 proto tcp comment "LAN to Homepage"
ufw allow from 192.168.10.0/24 to any port 8080 proto tcp comment "Management to AdGuard UI"
ufw allow from 192.168.10.0/24 to any port 8081 proto tcp comment "Management to Dozzle"
```

Apply routed DNS allowances for the AdGuard Docker bridge subnet:

```bash
install -m 0755 /path/to/repo/main/configs/docker-host/system/docker-host-ufw-route-dns.sh /usr/local/sbin/docker-host-ufw-route-dns.sh
/usr/local/sbin/docker-host-ufw-route-dns.sh
ufw status verbose
```

Install and configure Fail2ban (host hardening baseline):

```bash
apt-get update
apt-get install -y fail2ban
install -d -m 0755 /etc/fail2ban/jail.d
install -m 0644 /path/to/repo/main/configs/docker-host/system/docker-host-fail2ban-sshd.local \
  /etc/fail2ban/jail.d/docker-host-sshd.local
systemctl enable --now fail2ban
systemctl restart fail2ban
fail2ban-client status
fail2ban-client status sshd
```

Tailscale rules should be scoped to `tailscale0` or approved tailnet source
addresses. Do not open admin tools to Guest, DMZ, NVR, Printers, or IoT.

Add ports only for workloads that are intentionally exposed. Keep workload
access scoped by source subnet.

Docker-published ports can bypass UFW's normal `INPUT` path. For admin-only
published ports, use `DOCKER-USER` as well. Live VM 103 has
`/usr/local/sbin/docker-host-firewall.sh` and
`docker-host-firewall.service` applying:

```bash
iptables -A DOCKER-USER -m conntrack --ctstate RELATED,ESTABLISHED -j RETURN
iptables -A DOCKER-USER -p tcp -s 192.168.10.0/24 -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 2283 -j RETURN
iptables -A DOCKER-USER -p tcp -s 192.168.1.0/24 -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 2283 -j RETURN
iptables -A DOCKER-USER -p tcp -s 192.168.60.10 -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 2283 -j RETURN
iptables -A DOCKER-USER -i tailscale0 -p tcp -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 2283 -j RETURN
iptables -A DOCKER-USER -p tcp -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 2283 -j DROP
iptables -A DOCKER-USER -p tcp -s 192.168.10.0/24 -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8081 -j RETURN
iptables -A DOCKER-USER -p tcp -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8081 -j DROP
iptables -A DOCKER-USER -j RETURN
```

---

## Phase 5 - Stack Layout

All Compose workloads live under `/opt/stacks/<service>/`.

Repo-side rebuild templates live under `configs/docker-host/` and mirror the
intended `/opt/stacks/<service>/` layout without live secrets or app databases.

```bash
mkdir -p /opt/stacks/bambuddy/{data,logs}
mkdir -p /opt/stacks/adguard-home/{conf,work}
mkdir -p /opt/stacks/immich
mkdir -p /opt/stacks/homepage/config
mkdir -p /opt/stacks/dozzle
mkdir -p /opt/stacks/ntfy/{cache,etc}
mkdir -p /opt/stacks/watchtower
mkdir -p /opt/stacks/searxng/searxng
mkdir -p /opt/stacks/whoogle
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
MQTT_PORT=8883
MQTT_USER=mqtt
MQTT_PASSWORD=<set-from-bitwarden>
```

Use MQTT port `8883` after Mosquitto TLS is configured and verified. Also enable
TLS in the Bambuddy application settings so its internal MQTT relay connects
over TLS.

When ready to start the service:

```bash
cd /opt/stacks/bambuddy
cp .env.example .env
nano .env
chmod 600 .env
docker compose up -d
docker compose logs bambuddy -f
```

### Tier 1 stack paths

| Service | Path | Planned port(s) | Notes |
|---|---|---|---|
| AdGuard Home | `/opt/stacks/adguard-home/` | 53/tcp+udp, 3000 initial, 8080 admin target | Router forwards DNS here first; public fallback stays on router |
| Immich | `/opt/stacks/immich/` | 2283/tcp | Pre-flight live with local placeholder storage; store real media on OMV-backed mount, not the VM disk |
| Homepage | `/opt/stacks/homepage/` | 3001/tcp | Internal dashboard |
| Dozzle | `/opt/stacks/dozzle/` | 8081/tcp | Internal Docker log viewer |
| SearXNG | `/opt/stacks/searxng/` | 8087/tcp | Direct-access metasearch pre-flight |
| Whoogle | `/opt/stacks/whoogle/` | 8088/tcp | Direct-access Google search proxy pre-flight |

Do not make router-deploy manage these containers. Router-deploy only owns
OpenWrt DHCP/DNS/firewall/WireGuard generated artifacts.

---

## Phase 5b - Tailscale Host-Route Subnet Router

Tailscale is installed on the host OS, not inside Docker.

Target route advertisement:

```bash
tailscale up --advertise-routes=192.168.20.101/32,192.168.40.50/32,192.168.60.10/32
```

Approve each host route in the Tailscale admin console. Do not advertise broad
VLAN routes such as `192.168.20.0/24`, `192.168.40.0/24`, or
`192.168.60.0/24`.

Remote access model:

- Home Assistant through `192.168.20.101/32`.
- OMV through `192.168.40.50/32`.
- Grafana and Uptime Kuma through `192.168.60.10/32`, with only ports `3000`
  and `3001` allowed through docker-host routed firewall policy.
- Docker-host services through docker-host's Tailscale node identity/MagicDNS.
- WireGuard remains dormant fallback, not daily access.

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

# Mosquitto TLS, same VLAN trust boundary
timeout 5 bash -lc '</dev/tcp/192.168.20.101/8883' && echo MQTT_8883_OK

# Internet should be blocked after temp rule removal
curl -4I --connect-timeout 5 --max-time 8 https://download.docker.com/
```

Expected current result:

- `hostname` returns `docker-host`
- Compose config renders from `/opt/stacks/bambuddy`
- `HA_8123_OK`
- `MQTT_8883_OK`
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
- [x] VM can reach Mosquitto TLS on 8883.
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
| 103 | docker-host | 20 | 192.168.20.102 | 4096 MB | 2 | order 3 |
