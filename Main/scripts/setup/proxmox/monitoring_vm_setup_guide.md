# Monitoring VM Setup Guide
# VM 102 — Debian 12, VLAN 60 (Monitoring), 192.168.60.10
# Stack: Grafana + InfluxDB + Telegraf + Uptime Kuma (Docker Compose)
#
# Prerequisites:
#   - Proxmox setup complete (proxmox_setup_guide.md phases A–C done)
#   - Router VLANs live (router_setup_complete.md deployed)
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

---

## Phase 1 — Create VM 102 in Proxmox

### 1.1 — Download Debian 12 ISO (skip if already downloaded for VM 101)

```bash
# On Proxmox shell
wget -O /var/lib/vz/template/iso/debian-12-netinst-amd64.iso \
    https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-12-netinst-amd64.iso
```

### 1.2 — Create the VM

Click **Create VM** in Proxmox web UI:

**General**
| Field | Value |
|---|---|
| VM ID | `102` |
| Name | `monitoring` |
| Start at boot | ✅ |

**OS** — select the Debian 12 ISO → Guest OS: Linux, Version: 6.x

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

### 1.3 — Install Debian 12

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

### 1.4 — Note the MAC and update DHCP reservation

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

Re-apply DHCP config to router (Phase 3 of router_setup_complete.md) then reboot
VM 102 — it should come up at 192.168.60.10.

### 1.5 — Set startup order

`VM 102 → Options → Start/Shutdown Order`
Order: 3 (after HA=1, Frigate=2)

---

## Phase 2 — Base Debian configuration

SSH into the VM from your management laptop (VLAN 10 → VLAN 60 allowed):

```bash
ssh admin@192.168.60.10
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
      - "8086:8086"
    volumes:
      - ./influxdb/data:/var/lib/influxdb2
    environment:
      - DOCKER_INFLUXDB_INIT_MODE=setup
      - DOCKER_INFLUXDB_INIT_USERNAME=admin
      - DOCKER_INFLUXDB_INIT_PASSWORD=${INFLUXDB_PASSWORD}
      - DOCKER_INFLUXDB_INIT_ORG=homelab
      - DOCKER_INFLUXDB_INIT_BUCKET=homeassistant
      - DOCKER_INFLUXDB_INIT_RETENTION=90d

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    volumes:
      - ./grafana/data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
      - GF_USERS_ALLOW_SIGN_UP=false
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
    network_mode: host
    volumes:
      - ./telegraf/telegraf.conf:/etc/telegraf/telegraf.conf:ro
    depends_on:
      - influxdb

  uptime-kuma:
    image: louislam/uptime-kuma:1
    container_name: uptime-kuma
    restart: unless-stopped
    ports:
      - "3001:3001"
    volumes:
      - ./uptime-kuma:/app/data
EOF
```

Create the environment file (holds passwords — never commit to git):

```bash
cat > /opt/monitoring/.env << 'EOF'
INFLUXDB_PASSWORD=your-influxdb-password
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
[global_tags]
  host = "monitoring-vm"

[agent]
  interval = "30s"
  flush_interval = "30s"

# Output: InfluxDB v2
[[outputs.influxdb_v2]]
  urls = ["http://localhost:8086"]
  token = "INFLUXDB_TOKEN_HERE"    # fill in after Phase 6 step 6.2
  organization = "homelab"
  bucket = "system"

# System metrics — CPU, RAM, disk, network
[[inputs.cpu]]
  percpu = false
  totalcpu = true
[[inputs.mem]]
[[inputs.disk]]
  ignore_fs = ["tmpfs", "devtmpfs"]
[[inputs.net]]
  ignore_protocol_filters = ["lo"]
[[inputs.system]]

# OpenWrt syslog receiver (UDP 514)
# OpenWrt sends firewall block events here — see Phase 7 for router config
[[inputs.syslog]]
  server = "udp://:514"
EOF
```

> The `INFLUXDB_TOKEN_HERE` placeholder will be replaced in Phase 6.2 once
> InfluxDB is running and you've generated an API token.

---

## Phase 6 — First boot and InfluxDB setup

### 6.1 — Start the stack

```bash
cd /opt/monitoring
docker compose up -d
docker compose ps    # all four services should show "running"
```

### 6.2 — Generate InfluxDB API token for Telegraf

Open the InfluxDB UI: `http://192.168.60.10:8086`
Log in with `admin` / your INFLUXDB_PASSWORD.

Navigate: Load Data → API Tokens → Generate API Token → All Access Token.
Copy the token. Then update the Telegraf config and create a bucket for system metrics:

```bash
# Replace the placeholder token in telegraf.conf
sed -i 's/INFLUXDB_TOKEN_HERE/your-actual-token/' \
    /opt/monitoring/telegraf/telegraf.conf

# Create the system metrics bucket (90-day retention)
docker exec influxdb influx bucket create \
    --name system \
    --org homelab \
    --retention 90d

# Restart Telegraf to pick up the token
docker compose restart telegraf
```

Save the token to Bitwarden under `influxdb-telegraf-token`.

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

On HA VM (192.168.20.101), add to `/config/configuration.yaml`:

```yaml
influxdb:
  api_version: 2
  ssl: false
  host: 192.168.60.10
  port: 8086
  token: !secret influxdb_token
  organization: homelab
  bucket: homeassistant
  tags:
    source: homeassistant
  # Exclude noisy entities to keep storage lean
  exclude:
    entity_globs:
      - sensor.*_last_changed
      - sensor.*_last_updated
      - sensor.sun_*
```

Add to `/config/secrets.yaml` on the HA VM:
```yaml
influxdb_token: "your-ha-influxdb-token"    # Bitwarden: influxdb-ha-token
```

Restart HA. Within a few minutes, sensor data starts flowing into InfluxDB.
Verify: InfluxDB UI → Data Explorer → bucket: homeassistant → check for measurements.

---

## Phase 9 — Set up Grafana dashboards

### 9.1 — Add InfluxDB as a data source

Open Grafana: `http://192.168.60.10:3000`
Log in: admin / your GRAFANA_PASSWORD.

Connections → Data Sources → Add data source → InfluxDB:

| Field | Value |
|---|---|
| Query Language | `Flux` |
| URL | `http://influxdb:8086` |
| Organisation | `homelab` |
| Token | your all-access token (Bitwarden: influxdb-telegraf-token) |
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
| Proxmox | HTTP(s) | https://192.168.10.10:8006 |
| Home Assistant | HTTP(s) | http://192.168.20.101:8123 |
| Frigate | HTTP(s) | http://192.168.30.20:8971 |
| Pi NAS | Ping | 192.168.40.50 |
| GL-MT6000 Router | Ping | 192.168.10.1 |

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
- [ ] Debian 12 installed, SSH only, no desktop
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
- [ ] Telegraf API token generated and added to telegraf.conf
- [ ] HA API token generated and added to HA secrets.yaml
- [ ] `system` bucket created (90-day retention)
- [ ] `homeassistant_longterm` bucket created (1-year retention)
- [ ] Downsampling task created (Phase 11)

**Integrations**
- [ ] HA influxdb integration added to configuration.yaml, HA restarted
- [ ] Data flowing into homeassistant bucket (check InfluxDB Data Explorer)
- [ ] OpenWrt syslog forwarding to 192.168.60.10:514 (Phase 7)
- [ ] Telegraf receiving syslog events

**Grafana**
- [ ] InfluxDB datasource added and tested
- [ ] Community dashboards imported (system metrics, HA, energy)
- [ ] VentSys temperature/IAQ panels created
- [ ] Alerts configured (IAQ critical, smoke alarm, disk usage)

**Uptime Kuma**
- [ ] All VMs and infrastructure monitors added
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
