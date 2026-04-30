# Bambuddy VM — Setup Guide
**VM ID:** 103  **IP:** 192.168.20.102 — VLAN 20 (Automation)
**Host:** Proxmox on MINIX NEO Z350
**Purpose:** Bambu Lab P1S print management and HA integration
**Printer:** Bambu P1S at 192.168.35.200 (VLAN 35 — Printers)

> Why a dedicated VM? Bambuddy is an automation integration service, not an NVR
> component. Separating it from Frigate (VM 101) gives VM 101 a clean single-purpose
> NVR role and places Bambuddy correctly on VLAN 20 alongside Home Assistant.
> See docs/decisions/02-printer-vlan-architecture.md for full rationale.

---

## Phase 1 — Create the VM

### 1.1 — Download Debian 12 ISO (skip if already on Proxmox)

```bash
cd /var/lib/vz/template/iso
wget -O debian-12-netinst-amd64.iso \
    "https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-12-netinst-amd64.iso"
```

### 1.2 — VM settings

Click **Create VM** in Proxmox:

**General:** VM ID `103`, Name `bambuddy`, Start at boot ✅, Boot order `3`

**OS:** ISO `debian-12-netinst-amd64.iso`, Guest OS: Linux 6.x

**System:** Machine `q35`, BIOS `OVMF (UEFI)`, EFI Storage `local-lvm`,
SCSI Controller `VirtIO SCSI single`, Pre-enroll keys/TPM unticked

**Disks:** Storage `local-lvm`, Size `16 GiB`, Bus `SCSI → scsi0`,
Cache `Write back`, Discard ✅, SSD emulation ✅

**CPU:** Sockets `1`, Cores `1`, Type `host`

**Memory:** `1024` MiB, Ballooning unticked

**Network:** Bridge `vmbr0`, VLAN Tag `20`, Model `VirtIO`, Firewall unticked

Click **Finish**.

---

## Phase 2 — Install Debian

### 2.1 — Run the installer

`VM 103 → Start` then open **Console**. Select **Install**.

| Step | Value |
|---|---|
| Hostname | `bambuddy` |
| Domain | `home.local` |
| Root password | strong — save in Bitwarden as `bambuddy-vm` |
| New user | `admin` |
| Partition | Guided — entire disk, single partition |
| Software | Untick everything except `SSH server` + `standard system utilities` |

### 2.2 — Set static IP

Log in as `root` on the console:

```bash
ip link    # find interface name — typically ens18
nano /etc/network/interfaces
```

Replace the `iface ... dhcp` line with:

```
auto ens18
iface ens18 inet static
    address 192.168.20.102
    netmask 255.255.255.0
    gateway 192.168.20.1
    dns-nameservers 192.168.20.1
```

```bash
systemctl restart networking
ip addr show ens18    # confirm 192.168.20.102
```

### 2.3 — Remove the ISO

```bash
qm set 103 --delete ide2
```

### 2.4 — Note the MAC address

```bash
qm config 103 | grep net0
```

Add to `configs/openwrt/dhcp-config.conf`:
```
config host
    option name 'bambuddy'
    option mac 'XX:XX:XX:XX:XX:XX'    ← paste actual MAC here
    option ip '192.168.20.102'
```

---

## Phase 3 — Install Docker

Deployment dependency: the router firewall must still have
`TEMP Bambuddy Update Access` active for VM 103. It allows only outbound TCP
80/443 from `192.168.20.102` so Debian packages and Docker images can be
downloaded during bootstrap.

```bash
# Update and install prerequisites
apt-get update && apt-get install -y ca-certificates curl gnupg

# Add Docker's official GPG key
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg \
    | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker repo
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Allow admin user to run Docker
usermod -aG docker admin

# Verify
docker --version
docker compose version
```

---

## Phase 4 — Deploy Bambuddy

### 4.1 — Create directories

```bash
mkdir -p /opt/bambuddy/{data,logs}
```

### 4.2 — Create minimal `.env` file for container bootstrap

```bash
nano /opt/bambuddy/.env
```

```env
# MQTT publishing — Bambuddy pushes print events to Mosquitto on HA.
# TLS on port 8883 is the canonical target state.
MQTT_HOST=192.168.20.101
MQTT_PORT=8883
MQTT_USER=mqtt
MQTT_PASSWORD=<mosquitto mqtt password — Bitwarden: mqtt-credentials>
```

Use the Bambuddy web UI as the canonical place to add:
- the P1S printer IP, access code, and serial
- the Home Assistant URL and token

Keep `.env` limited to container/bootstrap settings and MQTT publishing unless
you have a deliberate reason to pre-seed advanced settings outside the UI.

Protect the file:
```bash
chmod 600 /opt/bambuddy/.env
```

### 4.3 — Create docker-compose.yml

```bash
nano /opt/bambuddy/docker-compose.yml
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
      - /opt/bambuddy/data:/app/data
      - /opt/bambuddy/logs:/app/logs
```

### 4.4 — Start Bambuddy

```bash
cd /opt/bambuddy
docker compose up -d
docker compose logs bambuddy -f    # watch for startup errors
```

After the first successful image pull/start, remove `TEMP Bambuddy Update Access`
on the router unless you are actively updating Bambuddy.

Confirm the UI is accessible from a VLAN 1 laptop:
```
http://192.168.20.102:8000
```

---

## Phase 5 — Connect Bambuddy to HA

### 5.1 — Add the P1S printer in Bambuddy UI

This is the canonical setup path:

1. Open `http://192.168.20.102:8000`
2. Settings → Printers → Add Printer
3. IP: `192.168.35.200`, Access Code: `<from printer screen>`, Serial: `<serial>`
4. Use the secure printer connection mode offered by Bambuddy for the P1S
5. Click Connect — status dot should go green

### 5.2 — Connect Bambuddy to Home Assistant API

1. In HA: **Settings → Profile → Security → Long-Lived Access Tokens → Create Token**
   Name it `Bambuddy`. Copy the value immediately → paste into Bitwarden as `ha-tokens`.
2. In Bambuddy UI: **Settings → Home Assistant**
   - HA URL: `http://192.168.20.101:8123`
   - Token: paste the long-lived token
3. Status dot should go green.

### 5.3 — Deploy HA package

The `configs/home-assistant/bambuddy_p1s_package.yaml` file provides HA entities
for the P1S. Copy it to the HA VM and update the serial number placeholder:

```bash
# On HA VM (192.168.20.101 Terminal add-on):
cp /config/packages/bambuddy_p1s_package.yaml /config/packages/bambuddy_p1s_package.yaml.bak

# Verify placeholder is replaced:
grep '<P1S_SERIAL>' /config/packages/bambuddy_p1s_package.yaml
# Should return nothing. If it returns a match, replace it:
sed -i 's/<P1S_SERIAL>/01P09C411500579/g' /config/packages/bambuddy_p1s_package.yaml
```

Restart HA. Confirm `binary_sensor.p1s_printing` and other entities appear in
**Settings → Devices & Services → Entities**.

---

## Phase 6 — Verify network paths

Run these checks from the Bambuddy VM console. The printer paths are routed
through OpenWrt and source-IP scoped to VM 103. The HA/Mosquitto paths stay
inside VLAN 20, which is accepted as the HA+Bambuddy trust boundary; those
checks verify service reachability rather than router firewall policy.

```bash
# Bambuddy → P1S MQTT (should say 'open')
nc -zv 192.168.35.200 8883

# P1S secure file transfer reachable
nc -zv 192.168.35.200 21     # should say 'open'

# Bambuddy → Mosquitto on HA (same VLAN trust boundary)
nc -zv 192.168.20.101 8883

# Bambuddy → HA API (same VLAN trust boundary)
nc -zv 192.168.20.101 8123

# Confirm internet is blocked after removing TEMP Bambuddy Update Access
nc -zv 8.8.8.8 80 -w 3      # should fail
```

---

## Completion checklist

- [ ] VM 103 created: q35, OVMF, VirtIO SCSI, VLAN 20, 16GB disk, 1GB RAM
- [ ] Debian 12 installed, SSH enabled, no desktop
- [ ] Static IP 192.168.20.102 set and confirmed
- [ ] ISO removed after install
- [ ] Start at boot enabled, startup order 3
- [ ] MAC noted and added to dhcp-config.conf
- [ ] Docker installed and working (`docker --version`)
- [ ] `TEMP Bambuddy Update Access` removed from router after initial image pull
- [ ] /opt/bambuddy/{data,logs} directories created
- [ ] Minimal `.env` file created for container bootstrap and MQTT settings
- [ ] docker-compose.yml created
- [ ] `docker compose up -d` successful
- [ ] Bambuddy UI accessible at http://192.168.20.102:8000 from VLAN 1 laptop
- [ ] P1S added in Bambuddy UI with secure transport and showing green status
- [ ] Bambuddy connected to HA API (long-lived token saved in Bitwarden)
- [ ] bambuddy_p1s_package.yaml deployed to HA, serial placeholder replaced
- [ ] HA P1S entities visible (binary_sensor.p1s_printing etc.)
- [ ] Routed printer paths and same-VLAN HA paths verified with nc checks above
- [ ] Confirm old Bambuddy removed from VM 101 (see note below)

## Removing Bambuddy from VM 101

Once VM 103 is live and confirmed working:

```bash
# On VM 101 (frigate-nvr):
cd /opt/frigate
docker compose down bambuddy
docker compose up -d    # restarts Frigate only

# Clean up old Bambuddy data (after confirming VM 103 has all state)
rm -rf /opt/frigate/bambuddy/

# Verify only Frigate is running
docker ps
```

The updated `configs/frigate/docker-compose.yml` no longer contains the Bambuddy
service block — pulling the updated config is sufficient once the VM is live.

---

## VM reference

| ID | Name | VLAN | IP | RAM | Cores | Boot |
|---|---|---|---|---|---|---|
| 100 | home-assistant | 20 | 192.168.20.101 | 4096 MB | 2 | order 1 |
| 101 | frigate-nvr | 30 | 192.168.30.20 | 4096 MB | 2 | order 2 |
| 103 | bambuddy | 20 | 192.168.20.102 | 1024 MB | 1 | order 3 |
| 102 | monitoring | 60 | 192.168.60.10 | 2048 MB | 2 | order 4 |
