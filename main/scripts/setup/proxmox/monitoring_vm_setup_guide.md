# Monitoring VM Setup Guide
# VM 102 — Debian 13, VLAN 60 (Monitoring), 192.168.60.10
# Stack: Grafana + InfluxDB + Telegraf + Uptime Kuma (Docker Compose)
#
# Prerequisites:
#   - Proxmox setup complete (proxmox_setup_guide.md phases A–C done)
#   - Router VLANs live (`scripts/setup/router/` phases 1-8 deployed)
#   - VM 100 (HA) running — Grafana pulls sensor data via InfluxDB integration
#
# What this stack monitors:
#   - Network uptime / device availability     → Uptime Kuma
#   - VentSys + HA sensor history over time    → InfluxDB + Grafana
#   - Electricity usage from smart plugs       → InfluxDB + Grafana (via HA)
#   - VM and host system resources             → Telegraf + Grafana
#   - OpenWrt firewall / syslog events         → Telegraf syslog + Grafana
#
# Disk: 32GB (thin-provisioned, ~14GB actual at steady state)
# RAM:  2048 MB
# CPU:  2 cores

> Live note, 2026-05-08: VM 102 is deployed from the Debian 13 genericcloud
> image using cloud-init, not the older manual Debian 12 ISO path. Current MAC:
> `BC:24:11:A6:94:95`. Docker is installed, and the monitoring stack is running
> from `/opt/monitoring`. Generated credentials are stored at
> `/root/monitoring-stack-credentials.txt` on the VM.
> Uptime Kuma baseline monitors are configured, OpenWrt syslog is flowing into
> InfluxDB, and Home Assistant is exporting state history to the `homeassistant`
> bucket with `source=HA`.
> The live host firewall also permits docker-host `192.168.20.102` to the
> Grafana and Uptime Kuma published ports only. The source-controlled policy is
> `configs/monitoring/system/monitoring-firewall.sh`, enabled as
> `monitoring-firewall.service`.

---

## Phase 1 — Create VM 102 in Proxmox

### 1.1 — Preferred path: Debian 13 cloud image

Use the same local cloud-image workflow as `frigate-nvr` and `docker-host` when
possible. This is the path already used for the live VM 102 on 2026-05-08.

```bash
ls -lh /var/lib/vz/template/iso/debian-13-genericcloud-amd64.qcow2
```

If the cloud image is missing, download it or use the older installer path below
as a fallback.

### 1.2 — Fallback path: Debian 12 ISO

```bash
# On Proxmox shell
wget -O /var/lib/vz/template/iso/debian-12-netinst-amd64.iso \
    https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-12-netinst-amd64.iso
```

### 1.3 — Create the VM

Click **Create VM** in Proxmox web UI:

**General**
| Field | Value |
|---|---|
| VM ID | `102` |
| Name | `monitoring` |
| Start at boot | ✅ |

**OS** — preferred: Debian 13 cloud image workflow; fallback: Debian 12 ISO → Guest OS: Linux, Version: 6.x

**System**
| Field | Value |
|---|---|
| Machine | `q35` |
| BIOS | `OVMF (UEFI)` |
| EFI Storage | `local-lvm` |
| Pre-enroll keys | untick |
| TPM | untick |
| SCSI Controller | `VirtIO SCSI single` |

**Disks** — keep the default disk, resize to **32 GiB**
Cache: Write back, Discard: ✅, SSD emulation: ✅

**CPU** — Sockets: 1, Cores: 2, Type: host

**Memory** — 2048 MiB, Ballooning: untick

**Network**
| Field | Value |
|---|---|
| Bridge | `vmbr0` |
| VLAN Tag | `60` |
| Model | `VirtIO (paravirtualized)` |
| Firewall | untick |

Click **Finish**.

### 1.4 — Install Debian

If you used the Debian 13 cloud image, cloud-init handles the initial user,
network, and SSH key setup. Confirm SSH access at `192.168.60.10`, then continue
to the base Debian configuration.

Start VM 102, open the Console, and run through the installer:

- **Hostname:** `monitoring`
- **Domain:** `home.local`
- **Root password:** set and save to Bitwarden as `monitoring-vm`
- **User account:** create `admin` (non-root, sudo access)
- **Partitioning:** Guided — use entire disk, all files in one partition
- **Software selection:** untick everything except `SSH server` and `standard system utilities`
  (no desktop — headless server only)

After install completes, remove the ISO:
```bash
# On Proxmox shell
qm set 102 --delete ide2
```

### 1.5 — Note the MAC and update DHCP reservation

```bash
qm config 102 | grep net0
```

Update `configs/openwrt/dhcp-config.conf` — the monitoring-vm host entry already
exists with a placeholder MAC at 192.168.60.10. Replace the MAC:

```
config host
    option name 'monitoring-vm'
    option mac 'XX:XX:XX:XX:XX:XX'    <- replace with real MAC
    option ip '192.168.60.10'
```

Re-apply DHCP config to router (`scripts/setup/router/phase_3_dhcp_configuration.md`) then reboot
VM 102 — it should come up at 192.168.60.10.

### 1.6 — Set startup order

`VM 102 → Options → Start/Shutdown Order`
Order: 3 (after HA=1, Frigate=2)

---

## Phase 2 — Base Debian configuration

SSH into the VM from your management laptop (VLAN 10 → VLAN 60 allowed):

```bash
ssh root@192.168.60.10
```

```bash
# Update system
sudo apt-get update && sudo apt-get dist-upgrade -y

# Install essentials
sudo apt-get install -y curl wget git htop net-tools ca-certificates \
    gnupg lsb-release apt-transport-https

# Set timezone
sudo timedatectl set-timezone Europe/London

# Harden SSH — add your key first or you will lock yourself out
# echo "ssh-ed25519 AAAA...your-key" >> ~/.ssh/authorized_keys
sudo sed -i \
    -e 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' \
    -e 's/^#\?PermitRootLogin.*/PermitRootLogin prohibit-password/' \
    /etc/ssh/sshd_config
sudo systemctl restart sshd
```

---

## Phase 3 — Install Docker and Docker Compose

```bash
# Add Docker's GPG key and repo
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | \
    sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) \
    signed-by=/etc/apt/keyrings/docker.gpg] \
    https://download.docker.com/linux/debian \
    $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io \
    docker-buildx-plugin docker-compose-plugin

# Add admin user to docker group (no sudo needed for docker commands)
sudo usermod -aG docker admin
newgrp docker

# Verify
docker --version
docker compose version
```

---

## Phase 4 — Create the Docker Compose stack

```bash
# Create directory structure
mkdir -p /opt/monitoring/{influxdb,grafana,telegraf,uptime-kuma}
mkdir -p /opt/monitoring/influxdb/data
mkdir -p /opt/monitoring/grafana/data
cd /opt/monitoring
```

Create the Docker Compose file:

```bash
cat > /opt/monitoring/docker-compose.yml << 'EOF'
version: "3.8"

services:

  influxdb:
    image: influxdb:2.7
    container_name: influxdb
    restart: unless-stopped
    ports:
      - "192.168.60.10:8086:8086"
    volumes:
      - ./influxdb/data:/var/lib/influxdb2
    environment:
      - DOCKER_INFLUXDB_INIT_MODE=setup
      - DOCKER_INFLUXDB_INIT_USERNAME=admin
      - DOCKER_INFLUXDB_INIT_PASSWORD=${INFLUXDB_PASSWORD}
      - DOCKER_INFLUXDB_INIT_ORG=homelab
      - DOCKER_INFLUXDB_INIT_BUCKET=homeassistant
      - DOCKER_INFLUXDB_INIT_RETENTION=90d
      - DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=${INFLUXDB_TOKEN}

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    restart: unless-stopped
    ports:
      - "192.168.60.10:3000:3000"
    volumes:
      - ./grafana/data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_SECURITY_ALLOW_EMBEDDING=true
      - GF_SECURITY_COOKIE_SAMESITE=lax
      - GF_AUTH_ANONYMOUS_ENABLED=true
      - GF_AUTH_ANONYMOUS_ORG_NAME=Main Org.
      - GF_AUTH_ANONYMOUS_ORG_ROLE=Viewer
    depends_on:
      - influxdb
EOF
```

```bash
# Append Telegraf and Uptime Kuma to docker-compose.yml
cat >> /opt/monitoring/docker-compose.yml << 'EOF'

  telegraf:
    image: telegraf:latest
    container_name: telegraf
    restart: unless-stopped
    user: telegraf:998
    group_add:
      - "989"
    ports:
      - "192.168.60.10:514:6514/udp"
    volumes:
      - ./telegraf/telegraf.conf:/etc/telegraf/telegraf.conf:ro
      - /:/hostfs:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
    environment:
      HOST_ETC: /hostfs/etc
      HOST_PROC: /hostfs/proc
      HOST_SYS: /hostfs/sys
      HOST_VAR: /hostfs/var
      HOST_RUN: /hostfs/run
      HOST_MOUNT_PREFIX: /hostfs
      INFLUXDB_TOKEN: ${INFLUXDB_TOKEN}
    depends_on:
      - influxdb

  uptime-kuma:
    image: louislam/uptime-kuma:1
    container_name: uptime-kuma
    restart: unless-stopped
    ports:
      - "192.168.60.10:3001:3001"
    volumes:
      - ./uptime-kuma:/app/data
EOF
```

Create the environment file (holds passwords — never commit to git):

```bash
cat > /opt/monitoring/.env << 'EOF'
INFLUXDB_PASSWORD=your-influxdb-password
INFLUXDB_TOKEN=your-influxdb-admin-token
GRAFANA_PASSWORD=your-grafana-password
EOF
chmod 600 /opt/monitoring/.env
```

> Save both passwords to Bitwarden under `monitoring-stack` before continuing.

---

## Phase 5 — Configure Telegraf

Telegraf collects system metrics from the monitoring VM itself and receives
syslog from OpenWrt. It pushes everything into InfluxDB.

```bash
cat > /opt/monitoring/telegraf/telegraf.conf << 'EOF'
[agent]
  interval = "30s"
  round_interval = true
  metric_batch_size = 1000
  metric_buffer_limit = 10000
  collection_jitter = "0s"
  flush_interval = "10s"
  flush_jitter = "0s"
  hostname = "monitoring-vm"
  omit_hostname = false

# Output: InfluxDB v2
[[outputs.influxdb_v2]]
  urls = ["http://influxdb:8086"]
  token = "$INFLUXDB_TOKEN"
  organization = "homelab"
  bucket = "homeassistant"

# System metrics — CPU, RAM, disk, network
[[inputs.cpu]]
  percpu = true
  totalcpu = true
[[inputs.mem]]
[[inputs.disk]]
  ignore_fs = ["tmpfs", "devtmpfs", "devfs", "iso9660", "overlay", "aufs", "squashfs"]
[[inputs.net]]
[[inputs.system]]
[[inputs.docker]]
  endpoint = "unix:///var/run/docker.sock"

# OpenWrt syslog receiver. Docker maps host UDP/514 to container UDP/6514.
[[inputs.syslog]]
  server = "udp://:6514"
  syslog_standard = "RFC3164"
EOF
```

> The live stack stores `INFLUXDB_TOKEN` in `/opt/monitoring/.env`, mode `600`.

---

## Phase 6 — First boot and InfluxDB setup

### 6.1 — Start the stack

```bash
cd /opt/monitoring
docker compose up -d
docker compose ps    # all four services should show "running"
```

### 6.2 — Confirm InfluxDB token for Telegraf

Open the InfluxDB UI: `http://192.168.60.10:8086`
Log in with `admin` / your INFLUXDB_PASSWORD.

The live stack initializes InfluxDB with `DOCKER_INFLUXDB_INIT_ADMIN_TOKEN`
from `/opt/monitoring/.env`, and Telegraf reads that same value as
`INFLUXDB_TOKEN`. Confirm the token is present and restart Telegraf after any
config change:

```bash
grep '^INFLUXDB_TOKEN=' /opt/monitoring/.env

docker compose restart telegraf
```

The live deployment writes Telegraf host/container metrics, OpenWrt syslog, and
HA state history into the `homeassistant` bucket.

### 6.3 — Create InfluxDB retention policy with downsampling

This keeps raw 30-second data for 90 days, then compresses to 1-minute
averages kept for 2 years. Prevents unbounded disk growth.

```bash
docker exec influxdb influx bucket create \
    --name homeassistant_longterm \
    --org homelab \
    --retention 8760h    # 1 year (730 days is 8760 hours)
```

> The downsampling task (writing 1-min averages from homeassistant →
> homeassistant_longterm) is configured in InfluxDB UI:
> Tasks → Create Task → paste the flux task. See Phase 9 for the flux script.

---

## Phase 7 — Configure OpenWrt syslog forwarding

On the GL-MT6000, configure syslog to forward to the monitoring VM:

```bash
# SSH into router
uci set system.@system[0].log_ip='192.168.60.10'
uci set system.@system[0].log_port='514'
uci set system.@system[0].log_proto='udp'
uci set system.@system[0].log_size='64'
uci commit system
service log restart
```

Verify syslog is arriving (run on monitoring VM):
```bash
docker logs telegraf --tail 20 | grep syslog
# You should see incoming firewall drop events within a few minutes
```

---

## Phase 8 — Connect Home Assistant to InfluxDB

### 8.1 — Create InfluxDB token for HA

In InfluxDB UI: Load Data → API Tokens → Generate API Token → Custom Token.
Give it write access to the `homeassistant` bucket only.
Save to Bitwarden as `influxdb-ha-token`.

### 8.2 — Add InfluxDB integration to HA

HA 2026.9 removes YAML-based InfluxDB connection/auth settings. Configure the
connection in the HA UI and keep only optional filtering/tag behavior in YAML.

UI path:

- Settings -> Devices & services -> InfluxDB -> Configure
- host: `192.168.60.10`
- port: `8086`
- organization: `c0b6f51cbbd36975`
- bucket: `homeassistant`
- token: token with write access to `homeassistant`

Optional YAML behavior block in `/config/configuration.yaml`:

```yaml
influxdb:
  max_retries: 3
  default_measurement: state
  tags:
    source: HA
  tags_attributes:
    - friendly_name
  exclude:
    domains:
      - automation
      - persistent_notification
      - updater
```

OpenWrt must allow HA to reach InfluxDB:

```bash
uci add firewall rule
uci set firewall.@rule[-1].name='HA to InfluxDB'
uci set firewall.@rule[-1].src='automation'
uci set firewall.@rule[-1].src_ip='192.168.20.101'
uci set firewall.@rule[-1].dest='monitoring'
uci set firewall.@rule[-1].dest_ip='192.168.60.10'
uci set firewall.@rule[-1].dest_port='8086'
uci set firewall.@rule[-1].proto='tcp'
uci set firewall.@rule[-1].target='ACCEPT'
uci commit firewall
/etc/init.d/firewall reload
```

Run `ha core check`, restart HA, then verify `source=HA` rows in the
`homeassistant` bucket.

---

## Phase 9 — Set up Grafana dashboards

Live note: Grafana is configured with datasource `InfluxDB - Home Automation`
(`uid: influxdb-homeassistant`) and dashboard `Home Automation Overview` in the
`Home Automation` folder:

`http://192.168.60.10:3000/d/home-automation-overview/home-automation-overview`

Grafana iframe embedding is enabled by setting
`GF_SECURITY_ALLOW_EMBEDDING=true`. HA exposes a storage-managed `Monitoring`
dashboard at `/monitoring/overview` with an embedded Grafana webpage card and
direct links to Grafana and Uptime Kuma. Anonymous Grafana Viewer mode is
enabled in the live stack for iframe reliability in cross-origin browser
contexts. Uptime Kuma is not directly embedded
yet because it sends `X-Frame-Options: SAMEORIGIN`; use the direct UI until a
same-origin reverse proxy/HTTPS route exists.

### 9.1 — Add InfluxDB as a data source

Open Grafana: `http://192.168.60.10:3000`
Log in: admin / your GRAFANA_PASSWORD.

Connections → Data Sources → Add data source → InfluxDB:

| Field | Value |
|---|---|
| Query Language | `Flux` |
| URL | `http://influxdb:8086` |
| Organisation | `homelab` |
| Token | `INFLUXDB_TOKEN` from `/opt/monitoring/.env` |
| Default Bucket | `homeassistant` |

Click **Save & Test** — should show "datasource is working".

### 9.2 — Import community dashboards

Grafana has ready-made dashboards you can import by ID:

| Dashboard | Grafana ID | What it shows |
|---|---|---|
| InfluxDB 2.0 System Metrics | `16192` | CPU, RAM, disk, network for the monitoring VM |
| Home Assistant via InfluxDB | `13451` | HA entity states, history graphs |
| Energy Monitor | `15491` | Power consumption from smart plug entities |

Import: Dashboards → New → Import → enter ID → Load → select your InfluxDB datasource → Import.

After import you'll need to adjust the Flux queries to match your bucket names
(`homeassistant`, `system`) and your entity naming conventions
(e.g. `sensor.ventsys_fdm_temperature`).

### 9.3 — Create VentSys dashboard panel (example Flux query)

```flux
from(bucket: "homeassistant")
  |> range(start: -24h)
  |> filter(fn: (r) => r["_measurement"] == "sensor")  # TODO: verify measurement name matches your InfluxDB after deployment
  |> filter(fn: (r) => r["entity_id"] =~ /ventsys.*temperature/)
  |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)
  |> yield(name: "mean")
```

This gives a 24-hour temperature trend for all VentSys sensor boards.
Duplicate and change the filter to `iaq`, `humidity`, `smoke_alarm` for
additional panels on the same dashboard.

### 9.4 — Set up alerts

Grafana → Alerting → Alert Rules → New alert rule.

Suggested rules for your setup:

| Alert | Condition | Notify via |
|---|---|---|
| VentSys IAQ critical | FDM IAQ < 3000 Ω for 2 min | Email / ntfy |
| Smoke alarm triggered | `smoke_alarm` = ON | Email / ntfy |
| Disk usage high | monitoring VM disk > 80% | Email |
| HA unreachable | Uptime Kuma (see Phase 10) | Email / ntfy |

For email alerts: Grafana → Alerting → Contact Points → Add contact point → Email.
For push notifications: use [ntfy.sh](https://ntfy.sh) — free, self-hostable,
works with Grafana's webhook contact point.

---

## Phase 10 — Configure Uptime Kuma

Open Uptime Kuma: `http://192.168.60.10:3001`
Create your admin account on first visit.

Add monitors for every device in the system. Suggested list:

**VMs and infrastructure**
| Name | Type | Target |
|---|---|---|
| Router DNS | TCP port | 192.168.10.1:53 |
| Proxmox UI | HTTP(s) | https://192.168.10.10:8006 |
| Home Assistant UI | HTTP(s) | http://192.168.20.101:8123 |
| Docker Host SSH | TCP port | 192.168.20.102:22 |
| Docker Host APT Cache | TCP port | 192.168.20.102:3142 |
| Bambuddy UI Port | TCP port | 192.168.20.102:8000 |
| Grafana UI | HTTP(s) | http://grafana:3000 |
| InfluxDB Health | HTTP(s) | http://influxdb:8086/health |
| Uptime Kuma UI | HTTP(s) | http://127.0.0.1:3001 |
| Frigate | HTTPS | https://192.168.30.20:8971, after Frigate is started |
| OMV NAS | Ping | 192.168.40.50, after NAS is built |

**All 16 VentSys ESPHome boards (Ping)**
Add one entry per IP: 192.168.50.21, .22, .31, .32, .33, .34,
.41, .42, .43, .51, .52, .53, .54, .55, .56, .61, .62

**Smart plugs (Ping)**
Add: 192.168.50.71 through .78

Set all monitors to 60-second check interval. Enable notifications
for down events — Uptime Kuma supports email, Telegram, ntfy, and many others.

---

## Phase 11 — InfluxDB downsampling task

In InfluxDB UI: Tasks → Create Task → paste:

```flux
option task = {
  name: "Downsample homeassistant to 1m averages",
  every: 1h,
}

from(bucket: "homeassistant")
  |> range(start: -task.every)
  |> filter(fn: (r) => r["_field"] == "_value")
  |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)
  |> to(bucket: "homeassistant_longterm", org: "homelab")
```

This runs hourly, writing 1-minute averages of the past hour into the
long-term bucket. Raw 30-second data expires after 90 days; averaged data
is kept for 1 year. Grafana queries both buckets depending on time range.

---

## Phase 12 — Backup the monitoring VM

Add VM 102 to the Proxmox backup schedule:

`Datacenter → Backup → select existing job → Edit → add VM 102 to selection`

Live note: VM 102 is already included in the temporary local Proxmox backup job:
VMs `100,101,102,103`, daily `02:00`, snapshot mode, ZSTD compression, keep last
2 while the NAS target is not live.

**Important:** VM 102 is relatively small (~14GB at steady state) so local
backup is fine. However, the InfluxDB data directory grows over time —
check backup size monthly and adjust max_backups if needed.

Alternatively, since InfluxDB data can be rebuilt from HA history, you may
choose to exclude VM 102 from backups and just back up the compose files:

```bash
# On monitoring VM — backup just config (not data)
tar czf /tmp/monitoring-config-$(date +%Y%m%d).tar.gz \
    /opt/monitoring/docker-compose.yml \
    /opt/monitoring/telegraf/telegraf.conf
# Then copy to NAS or include in vault backup
```

---

## Completion checklist

**VM 102 — monitoring**
- [ ] VM created: q35, OVMF, VirtIO SCSI, VLAN 60, 32GB disk, 2GB RAM
- [ ] Debian 13 installed, SSH only, no desktop
- [ ] ISO removed after install (`qm set 102 --delete ide2`)
- [ ] Start at boot enabled, startup order: 3
- [ ] Static IP confirmed at 192.168.60.10
- [ ] MAC noted and added to dhcp-config.conf (monitoring-vm entry)
- [ ] SSH key added, password auth disabled

**Docker stack**
- [ ] Docker + Docker Compose installed
- [ ] `/opt/monitoring/docker-compose.yml` created
- [ ] `/opt/monitoring/.env` created with passwords (saved to Bitwarden)
- [ ] `docker compose up -d` — all 4 containers running
- [ ] InfluxDB UI reachable: http://192.168.60.10:8086
- [ ] Grafana UI reachable: http://192.168.60.10:3000
- [ ] Uptime Kuma reachable: http://192.168.60.10:3001

**InfluxDB**
- [x] Telegraf uses `INFLUXDB_TOKEN` from `/opt/monitoring/.env`
- [x] HA API token generated and added to HA `secrets.yaml`
- [x] `homeassistant` bucket active (90-day retention)
- [ ] `homeassistant_longterm` bucket created (1-year retention)
- [ ] Downsampling task created (Phase 11)

**Integrations**
- [x] HA influxdb integration added to configuration.yaml, HA restarted
- [x] Data flowing into homeassistant bucket (`source=HA`)
- [x] OpenWrt syslog forwarding to 192.168.60.10:514 (Phase 7)
- [x] Telegraf receiving syslog events

**Grafana**
- [x] InfluxDB datasource added and tested
- [x] Baseline Home Automation dashboard created
- [ ] Community dashboards imported or replaced with project-specific dashboards (system metrics, HA, energy)
- [ ] VentSys temperature/IAQ panels created
- [ ] Alerts configured (IAQ critical, smoke alarm, disk usage)

**Uptime Kuma**
- [x] Baseline VM and infrastructure monitors added
- [ ] All 16 VentSys boards added as Ping monitors
- [ ] All 8 smart plugs added as Ping monitors
- [ ] Notifications configured for down events

---

## Access URLs

| Service | URL | Notes |
|---|---|---|
| InfluxDB | http://192.168.60.10:8086 | Data storage and query UI |
| Grafana | http://192.168.60.10:3000 | Dashboards and alerting |
| Uptime Kuma | http://192.168.60.10:3001 | Uptime monitoring |

All accessible from VLAN 10 (management) and VLAN 20 (automation/HA).
Not accessible from VLAN 50 (IoT) or VLAN 99 (guest) — firewall blocks these.
