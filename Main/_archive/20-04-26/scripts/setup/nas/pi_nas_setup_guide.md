# Raspberry Pi NAS — Setup Guide
**Device:** Raspberry Pi 4 (4GB+ recommended)
**IP:** 192.168.40.50 — VLAN 40 (Storage)
**Port:** lan4 on GL-MT6000 (VLAN 40 untagged)
**Purpose:** NAS storage for Frigate footage, HA backups, config file backup

> VLAN 40 has no internet access. The NAS is accessible only from VLAN 10 (Management) and specific VMs per firewall rules.

---

## Phase 1 — Hardware and OS

### 1.1 — Hardware requirements

| Item | Minimum | Recommended |
|---|---|---|
| Raspberry Pi | Pi 4 2GB | Pi 4 4GB |
| Storage | 1x USB 3.0 drive | 2x USB 3.0 drives (for redundancy) |
| Boot | microSD 16GB | USB 3.0 SSD (more reliable than SD) |
| Case | any | one with active cooling |
| Power | official Pi PSU | official Pi PSU (5V 3A) |

> Booting from USB SSD instead of microSD is strongly recommended — SD cards fail under continuous NAS write loads.

### 1.2 — Flash Raspberry Pi OS Lite

Download Raspberry Pi Imager and flash **Raspberry Pi OS Lite (64-bit)** to your boot drive.

In Imager advanced settings before writing:
- Hostname: `pi-nas`
- Enable SSH: yes (key-based, add your public key)
- Username: `admin`
- Disable WiFi (NAS will use wired only)
- Locale: Europe/London

### 1.3 — Connect to VLAN 40

Plug the Pi into **lan4** on the GL-MT6000. This port carries VLAN 40 untagged — the Pi will get a DHCP address on 192.168.40.x until the static reservation is set.

Boot the Pi, find its DHCP address from the router (`192.168.40.1 → Status → DHCP`), then SSH in:

```bash
ssh admin@192.168.40.<dhcp-address>
```

### 1.4 — Set static IP

```bash
sudo nmcli con mod "Wired connection 1" \
    ipv4.method manual \
    ipv4.addresses 192.168.40.50/24 \
    ipv4.gateway 192.168.40.1 \
    ipv4.dns 192.168.40.1
sudo nmcli con up "Wired connection 1"
```

Verify:
```bash
ip addr show eth0    # should show 192.168.40.50
ping 192.168.40.1   # gateway reachable
```

### 1.5 — Note the MAC address

```bash
ip link show eth0 | grep link/ether
```

Update `configs/openwrt/dhcp-config.conf` — paste the MAC into the `pi-nas` host entry.

### 1.6 — Initial hardening

```bash
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y ufw fail2ban htop rsync

# Firewall — allow only management and specific VMs
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow from 192.168.10.0/24 to any port 22    # Management SSH
sudo ufw allow from 192.168.20.101 to any port 22     # HA SSH (for backup scripts)
sudo ufw allow from 192.168.20.101 to any port 2049   # HA → NFS
sudo ufw allow from 192.168.20.101 to any port 445    # HA → Samba
sudo ufw allow from 192.168.30.20 to any port 2049    # Frigate → NFS
sudo ufw allow from 192.168.30.20 to any port 445    # Frigate → Samba
sudo ufw enable
```

---

## Phase 2 — Storage setup

### 2.1 — Identify and partition storage drives

```bash
# List connected drives
lsblk

# Format for NAS use (adjust device names — /dev/sda, /dev/sdb etc.)
# WARNING: this destroys existing data on the drive
sudo mkfs.ext4 -L nas-storage /dev/sda1
```

### 2.2 — Create mount points and auto-mount

```bash
sudo mkdir -p /mnt/nas/{frigate,ha-backups,configs}

# Get UUID of drive
sudo blkid /dev/sda1

# Add to /etc/fstab (replace UUID with your actual value)
echo "UUID=your-drive-uuid  /mnt/nas  ext4  defaults,noatime  0  2" | sudo tee -a /etc/fstab

sudo mount -a
df -h /mnt/nas    # verify mounted
```

### 2.3 — Create share directories with correct permissions

```bash
sudo mkdir -p /mnt/nas/frigate
sudo mkdir -p /mnt/nas/ha-backups
sudo mkdir -p /mnt/nas/configs

sudo chown -R admin:admin /mnt/nas
sudo chmod 755 /mnt/nas /mnt/nas/frigate /mnt/nas/ha-backups /mnt/nas/configs
```

---

## Phase 3 — NFS (for Frigate and HA)

NFS is preferred for Linux-to-Linux file sharing (Frigate VM on Debian, HA on HAOS).

### 3.1 — Install NFS server

```bash
sudo apt-get install -y nfs-kernel-server
```

### 3.2 — Configure exports

```bash
sudo nano /etc/exports
```

Add:
```
# Frigate recordings — Frigate VM only
/mnt/nas/frigate    192.168.30.20(rw,sync,no_subtree_check,no_root_squash)

# HA backups — HA VM only
/mnt/nas/ha-backups    192.168.20.101(rw,sync,no_subtree_check,no_root_squash)

# Config backups — Management and HA
/mnt/nas/configs    192.168.10.0/24(rw,sync,no_subtree_check) 192.168.20.101(rw,sync,no_subtree_check)
```

Apply:
```bash
sudo exportfs -ra
sudo systemctl enable nfs-kernel-server
sudo systemctl restart nfs-kernel-server

# Verify exports
showmount -e localhost
```

### 3.3 — Test from Frigate VM

On `frigate-nvr` (192.168.30.20):
```bash
showmount -e 192.168.40.50
mount -t nfs 192.168.40.50:/mnt/nas/frigate /mnt/nas/frigate
df -h /mnt/nas/frigate
```

### 3.4 — Test from HA VM

In HA Terminal add-on:
```bash
mount -t nfs 192.168.40.50:/mnt/nas/ha-backups /mnt/nas
df -h /mnt/nas
```

---

## Phase 4 — Samba (optional, for Windows access from VLAN 10)

Only needed if you want to browse the NAS from a Windows laptop on the management network.

```bash
sudo apt-get install -y samba

sudo nano /etc/samba/smb.conf
```

Add at the bottom:
```ini
[nas-configs]
   path = /mnt/nas/configs
   browseable = yes
   read only = no
   valid users = admin
   hosts allow = 192.168.10.0/24

[ha-backups]
   path = /mnt/nas/ha-backups
   browseable = yes
   read only = yes
   valid users = admin
   hosts allow = 192.168.10.0/24
```

```bash
sudo smbpasswd -a admin    # set Samba password for admin user
sudo systemctl enable smbd nmbd
sudo systemctl restart smbd nmbd
```

Test from Windows laptop on VLAN 10: `\\192.168.40.50\nas-configs`

---

## Phase 5 — Automated backup from HA

### 5.1 — Add NAS as a backup location in HA

`Settings → System → Storage → Add Network Storage`

| Field | Value |
|---|---|
| Name | NAS Backups |
| Server | `192.168.40.50` |
| Protocol | NFS |
| Remote path | `/mnt/nas/ha-backups` |

### 5.2 — Set HA automatic backup to NAS

`Settings → System → Backups → Automatic Backups`

| Field | Value |
|---|---|
| Schedule | Daily |
| Time | 03:00 |
| Keep | 14 backups |
| Location | NAS Backups |

---

## Phase 6 — Storage health monitoring

```bash
# Install smartmontools for drive health
sudo apt-get install -y smartmontools

# Check drive health
sudo smartctl -a /dev/sda

# Enable periodic SMART tests (add to crontab)
sudo crontab -e
# Add:
# 0 2 * * 0   smartctl -t short /dev/sda >> /var/log/smart.log 2>&1
# 0 3 1 * *   smartctl -t long /dev/sda >> /var/log/smart.log 2>&1

# Disk usage alert script
cat > /usr/local/bin/disk_alert.sh << 'EOF'
#!/bin/bash
THRESHOLD=85
USAGE=$(df /mnt/nas | awk 'NR==2 {print $5}' | tr -d '%')
if [ "$USAGE" -gt "$THRESHOLD" ]; then
    echo "NAS disk usage at ${USAGE}% — above ${THRESHOLD}% threshold" | \
    logger -t disk_alert -p user.warning
fi
EOF
chmod +x /usr/local/bin/disk_alert.sh
echo "*/30 * * * * /usr/local/bin/disk_alert.sh" | sudo crontab -
```

---

## Completion checklist

- [ ] Pi booted from USB SSD (not SD card)
- [ ] Static IP set: 192.168.40.50/24, gw 192.168.40.1
- [ ] MAC noted and added to dhcp-config.conf
- [ ] UFW firewall rules applied
- [ ] Storage drives mounted at /mnt/nas
- [ ] NFS server configured and exports active
- [ ] Frigate VM can mount /mnt/nas/frigate via NFS
- [ ] HA VM can mount /mnt/nas/ha-backups via NFS
- [ ] Samba configured (if management VLAN Windows access needed)
- [ ] HA network storage configured pointing to NAS
- [ ] HA automatic backup schedule set (daily 03:00)
- [ ] SMART monitoring enabled
- [ ] Disk usage alert script scheduled

## Quick reference

| Item | Value |
|---|---|
| IP | 192.168.40.50 / VLAN 40 |
| NFS: Frigate | `192.168.40.50:/mnt/nas/frigate` |
| NFS: HA backups | `192.168.40.50:/mnt/nas/ha-backups` |
| NFS: Configs | `192.168.40.50:/mnt/nas/configs` |
| Samba | `\\192.168.40.50\nas-configs` (VLAN 10 only) |
| SSH | `admin@192.168.40.50` (key auth) |
| SMART log | `/var/log/smart.log` |
