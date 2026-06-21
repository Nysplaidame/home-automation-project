# Proxmox VE — Setup Guide
**Hardware:** MINISFORUM M1 Pro-125H (Intel Core Ultra 5 125H, 32GB RAM, 1TB NVMe)
**Target host IP:** 192.168.10.10 — VLAN 10 (Management)
**First VM:** Home Assistant OS — 192.168.20.101, VLAN 20 (Automation)

> **Router status:** GL-MT6000 first-flight VLAN config is live and physically validated.
> Proven access ports: `lan5` recovery (VLAN 1), `lan2` management (VLAN 10),
> `lan3` NVR (VLAN 30), and `lan4` storage (VLAN 40). `lan1` is a tagged-only
> trunk for Proxmox and should not be treated as a normal laptop/access port.
>
> Current setup flow:
> - **Phase A** - use `lan2` or local console for initial Proxmox access
> - **Phase B** - configure the VLAN-aware bridge and permanent VLAN 10 host IP
> - **Phase F** - move the MINISFORUM host to `lan1` and verify the trunk

---

## Phase A — Find Proxmox and reach the web UI

### A1 — Connect the MINISFORUM host for initial setup

Preferred current path: plug the MINISFORUM ethernet into **lan2** on the GL-MT6000.
`lan2` is VLAN 10 untagged and should provide a temporary DHCP address in
`192.168.10.x`.

Do **not** start on `lan1`. `lan1` is the tagged Proxmox trunk; an ordinary
untagged host config may get no DHCP lease there.

Fallback path: use monitor + keyboard directly on the MINISFORUM host if network access is
not available yet.

### A2 — Find the IP Proxmox assigned itself

**Option 1 — home router DHCP table**
Log into your home router admin page. Look for a device named `proxmox` or `pve`.

**Option 2 — monitor + keyboard directly on the MINISFORUM host**
At the Proxmox boot screen you'll see the IP. Or log in as `root` and run:
```bash
ip addr show
```
Look for `inet` on `enp1s0` or `eno1` (whichever shows `state UP`).

**Option 3 — scan from your laptop (PowerShell)**
```powershell
# Adjust subnet if you are not scanning from VLAN 10
1..254 | ForEach-Object {
    $ip = "192.168.10.$_"
    if (Test-Connection $ip -Count 1 -Quiet -TimeoutSeconds 1) { $ip }
}
```

### A3 — Open the Proxmox web UI

Navigate to `https://<found-ip>:8006`. Accept the certificate warning.

Log in:
- **Username:** `root`
- **Realm:** `Linux PAM standard authentication`
- **Password:** set during installation

---

## Phase B — VLAN-aware bridge

One VLAN-aware bridge (`vmbr0`) on the physical NIC handles everything.
The Proxmox host uses VLAN 10. Each VM gets its own VLAN tag on the same bridge.

### B1 — Find your NIC name

`pve → Network` in the web UI. The entry with a MAC and no IP is your physical NIC.
This guide uses `enp1s0` — substitute your actual name if different.

### B2 — Write the new network config

In `pve → Shell`:
```bash
# Back up first
cp /etc/network/interfaces /etc/network/interfaces.bak.$(date +%Y%m%d_%H%M%S)

cat > /etc/network/interfaces << 'EOF'
auto lo
iface lo inet loopback

# Physical NIC — no IP, just a trunk carrier
auto enp1s0
iface enp1s0 inet manual

# VLAN-aware bridge — all VMs attach here with their VLAN tag
auto vmbr0
iface vmbr0 inet manual
        bridge-ports enp1s0
        bridge-stp off
        bridge-fd 0
        bridge-vlan-aware yes
        bridge-vids 2-4094

# VLAN 10 — Management (permanent Proxmox host IP on the lan1 trunk)
auto vmbr0.10
iface vmbr0.10 inet static
        address 192.168.10.10/24
        gateway 192.168.10.1
EOF
```

This final config expects the cable to move to **lan1** after `ifreload -a`.
If the MINISFORUM host is still on `lan2`, the tagged `vmbr0.10` interface will not match
the untagged access-port behavior.

### B3 — Apply

```bash
# Install ifupdown2 if not present (enables ifreload)
apt-get install -y ifupdown2

ifreload -a
```

You will lose the temporary `lan2` DHCP address. Move the MINISFORUM ethernet cable
to **lan1** on the GL-MT6000, keep your laptop on **lan2**, then reconnect at
`https://192.168.10.10:8006`.

Confirm `vmbr0` and `vmbr0.10` appear in `pve → Network`.

---

## Phase C — Host hardening

```bash
# 1. Back up and clean repositories.
# Proxmox VE 9 runs on Debian 13 "trixie" and uses Deb822 `.sources` files by
# default. Do not use old bullseye/bookworm `.list` entries.
cp -a /etc/apt/sources.list /etc/apt/sources.list.bak.$(date +%Y%m%d_%H%M%S)
cp -a /etc/apt/sources.list.d /etc/apt/sources.list.d.bak.$(date +%Y%m%d_%H%M%S)

# Remove stale manual entries from the legacy flat list.
cat > /etc/apt/sources.list << 'EOF'
# Managed by /etc/apt/sources.list.d/*.sources on this Proxmox VE 9 host.
EOF

# Disable paid enterprise repositories unless/until a subscription is added.
[ -f /etc/apt/sources.list.d/pve-enterprise.sources ] && \
    mv /etc/apt/sources.list.d/pve-enterprise.sources \
       /etc/apt/sources.list.d/pve-enterprise.sources.disabled
[ -f /etc/apt/sources.list.d/ceph.sources ] && \
    mv /etc/apt/sources.list.d/ceph.sources \
       /etc/apt/sources.list.d/ceph.sources.disabled

# 2. Add free no-subscription PVE repo.
cat > /etc/apt/sources.list.d/pve-no-subscription.sources << 'EOF'
Types: deb
URIs: http://download.proxmox.com/debian/pve
Suites: trixie
Components: pve-no-subscription
Signed-By: /usr/share/keyrings/proxmox-archive-keyring.gpg
EOF

# 3. Update
apt-get update && apt-get dist-upgrade -y

# 4. Remove subscription nag popup + install an apt hook to reapply automatically
# The sed patch is overwritten every time proxmox-widget-toolkit upgrades.
# The apt hook below reapplies it automatically after any upgrade that touches
# that package, so you don't have to remember to do it manually.
sed -Zi 's/res\s*=\s*await\s*window\.proxmoxAvailableChecks\.checkSubscription\(\)\s*;/res = {status: "active"};/' \
    /usr/share/javascript/proxmox-widget-toolkit/proxmoxlib.js && \
    systemctl restart pveproxy

# Create apt post-invoke hook — runs after every apt upgrade
cat > /etc/apt/apt.conf.d/86pve-no-nag << 'APTHOOK'
DPkg::Post-Invoke {
    "if dpkg -l proxmox-widget-toolkit 2>/dev/null | grep -q '^ii'; then \
        sed -Zi 's/res\\s*=\\s*await\\s*window\\.proxmoxAvailableChecks\\.checkSubscription\\(\\)\\s*;/res = {status: \"active\"};/' \
            /usr/share/javascript/proxmox-widget-toolkit/proxmoxlib.js; \
        systemctl restart pveproxy 2>/dev/null || true; \
    fi";
};
APTHOOK
echo "✓ Apt hook installed — nag patch will reapply automatically after proxmox-widget-toolkit upgrades"

# 5. Timezone
timedatectl set-timezone Europe/London

# 6. IOMMU — needed for USB passthrough to VMs (e.g. Zigbee dongle)
# Observed host CPU is Intel (Core Ultra 5 125H).
grep -q "intel_iommu" /etc/default/grub || \
    sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="quiet"/GRUB_CMDLINE_LINUX_DEFAULT="quiet intel_iommu=on iommu=pt"/' \
    /etc/default/grub && update-grub

# 7. SSH hardening — ADD YOUR PUBLIC KEY FIRST or you will lock yourself out
# echo "ssh-ed25519 AAAA...your-key" >> ~/.ssh/authorized_keys
sed -i \
    -e 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' \
    -e 's/^#\?PermitRootLogin.*/PermitRootLogin prohibit-password/' \
    /etc/ssh/sshd_config
systemctl restart sshd
```

---

## Phase D — Create the guests

> The former all-in-one `vm-setup.sh` is archived because it creates the
> retired VM 101 Frigate architecture. Build each guest from its current guide
> and verify against `configs/proxmox/guest-configs.md`.

### Current approach — individual VM/LXC guides

- VM 100: `ha_vm_setup_guide.md`
- VM 102: `monitoring_vm_setup_guide.md`
- VM 103: `docker_host_setup_guide.md`
- CT 111: `frigate_vm_setup_guide.md`
- CT 114: `llm_host_setup_guide.md`

---

### Manual creation detail

Follow the steps below if you prefer to create the VMs individually or need
to create only one of them.

### D1 — VM 100: Download HAOS image

```bash
# F-11 fix: look up the current stable version before downloading.
# Do NOT hardcode a version — HAOS releases frequently and an old image will
# immediately try to update itself on first boot, which is slow and failure-prone.
#
# Get the latest release tag:
HA_VERSION=$(curl -fsSL \
    "https://api.github.com/repos/home-assistant/operating-system/releases/latest" \
    | grep '"tag_name"' | head -1 | cut -d'"' -f4)
echo "Latest HAOS version: ${HA_VERSION}"
# Verify the version looks sane before continuing (should be e.g. "14.2" or "15.0")

cd /var/lib/vz/template/iso

wget -O haos_ova-${HA_VERSION}.qcow2.xz \
    "https://github.com/home-assistant/operating-system/releases/download/${HA_VERSION}/haos_ova-${HA_VERSION}.qcow2.xz"

xz -d haos_ova-${HA_VERSION}.qcow2.xz

ls -lh haos_ova-${HA_VERSION}.qcow2    # should be ~1–2 GB
```

> No internet yet? Download on your laptop → `pve → local → ISO Images → Upload`
> In that case, note the version you downloaded and set `HA_VERSION="x.y"` manually in D3.

### D2 — VM 100: Create the VM shell

Click **Create VM** in the web UI top-right:

**General**
| Field | Value |
|---|---|
| VM ID | `100` |
| Name | `home-assistant` |
| Start at boot | ✅ |

**OS** — select *Do not use any media* → Guest OS: Linux, Version: 6.x

**System**
| Field | Value |
|---|---|
| Machine | `q35` |
| BIOS | `OVMF (UEFI)` |
| EFI Storage | `local-lvm` |
| Pre-enroll keys | untick |
| TPM | untick |
| SCSI Controller | `VirtIO SCSI single` |

**Disks** — delete the default disk (bin icon on scsi0). We import ours in D3.

**CPU**
| Field | Value |
|---|---|
| Sockets | `1` |
| Cores | `2` |
| Type | `host` |

**Memory**
| Field | Value |
|---|---|
| Memory (MiB) | `4096` |
| Ballooning Device | untick |

**Network**
| Field | Value |
|---|---|
| Bridge | `vmbr0` |
| VLAN Tag | `20` |
| Model | `VirtIO (paravirtualized)` |
| Firewall | untick |

Click **Finish**.

### D3 — VM 100: Import the HAOS disk

```bash
# HA_VERSION must match the filename you downloaded in D1.
# If you used the curl method above, it will already be set in your shell.
# If you opened a new shell or uploaded manually, set it explicitly:
#   HA_VERSION="x.y"   # replace with your actual downloaded version

qm importdisk 100 \
    /var/lib/vz/template/iso/haos_ova-${HA_VERSION}.qcow2 \
    local-lvm \
    --format raw

# Output ends with: unused0: local-lvm:vm-100-disk-X
```

### D4 — VM 100: Attach the disk

`VM 100 → Hardware → Unused Disk 0` → double-click:

| Field | Value |
|---|---|
| Bus/Device | `SCSI → scsi0` |
| Cache | `Write back` |
| Discard | ✅ |
| SSD emulation | ✅ |

Click **Add**.

### D5 — VM 100: Set boot order

`VM 100 → Options → Boot Order` → Edit
Enable `scsi0`, move it first. Disable everything else.

### D6 — VM 100: Note the MAC address

`VM 100 → Hardware → Network Device (net0)` → Edit

Copy the MAC address. Update `configs/openwrt/dhcp-config.conf`:
```
config host
    option name 'home-assistant'
    option mac 'XX:XX:XX:XX:XX:XX'    ← paste actual MAC here
    option ip '192.168.20.101'
```

### D7 — VM 100: First boot

Click **Start** on VM 100, open **Console**.
First boot takes 2–3 minutes (filesystem expansion). You'll see:

```
Home Assistant
IP: waiting for network...
```

The IP stays "waiting" until the GL-MT6000 VLAN 20 is live — this is expected.

---

### D8 — VM 101: Preferred path is Debian 13 cloud image

The live Frigate VM 101 was created from the local Debian 13 genericcloud
image, mirroring the docker-host workflow.

```bash
ls -lh /var/lib/vz/template/iso/debian-13-genericcloud-amd64.qcow2
```

If that file is not present, you can still use the older Debian 12 ISO path
below as a fallback.

### D9 — VM 101 fallback: Download Debian 12 ISO

```bash
wget -O /var/lib/vz/template/iso/debian-12-netinst-amd64.iso \
    https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-12-netinst-amd64.iso
```

> Or upload via `pve → local → ISO Images → Upload`.

### D10 — VM 101: Create the VM shell

Click **Create VM**:

**General**
| Field | Value |
|---|---|
| VM ID | `101` |
| Name | `frigate-nvr` |
| Start at boot | ✅ |

**OS** — preferred: Debian 13 cloud image workflow; fallback: select the Debian 12 ISO → Guest OS: Linux, Version: 6.x

**System**
| Field | Value |
|---|---|
| Machine | `q35` |
| BIOS | `OVMF (UEFI)` |
| EFI Storage | `local-lvm` |
| Pre-enroll keys | untick |
| TPM | untick |
| SCSI Controller | `VirtIO SCSI single` |

**Disks** — keep the default disk, resize to **64 GiB**. Cache: Write back, Discard: ✅, SSD emulation: ✅

**CPU**
| Field | Value |
|---|---|
| Sockets | `1` |
| Cores | `2` |
| Type | `host` |

**Memory**
| Field | Value |
|---|---|
| Memory (MiB) | `4096` |
| Ballooning Device | untick |

**Network**
| Field | Value |
|---|---|
| Bridge | `vmbr0` |
| VLAN Tag | `30` |
| Model | `VirtIO (paravirtualized)` |
| Firewall | untick |

Click **Finish**.

### D11 — VM 101: Install Debian

Start VM 101 and open the **Console**. Run through the Debian installer:

- Hostname: `frigate-nvr`
- No desktop environment — select only `SSH server` and `standard system utilities`
- Create a non-root user (e.g. `admin`) — Frigate/Docker runs as this user
- Partitioning: Guided — use entire disk, all files in one partition

After install completes, the ISO will still be attached. Remove it:
```bash
qm set 101 --delete ide2
```

### D12 — VM 101: Note the MAC address

```bash
qm config 101 | grep net0
```

Add to `configs/openwrt/dhcp-config.conf`:
```
config host
    option name 'frigate-nvr'
    option mac 'XX:XX:XX:XX:XX:XX'    ← paste actual MAC here
    option ip '192.168.30.20'
```

Frigate NVR setup continues in `scripts/setup/proxmox/frigate_vm_setup_guide.md`.

---

## Phase E — Schedule backups

`Datacenter → Backup → Add`:

| Field | Value |
|---|---|
| Storage | `local` |
| Schedule | `0 2 * * *` (02:00 daily) |
| Selection | Include VM 100 |
| Mode | `Snapshot` |
| Compression | `ZSTD` |
| Max backups | `3` |

> **F-13 — Space planning:** The MINISFORUM M1 Pro-125H has a 1TB NVMe shared between Proxmox,
> local-lvm (VM disks), and local (backups/ISOs). Snapshot backups are
> compressed but still significant — plan accordingly:
>
> | VM | Disk size | Approx compressed backup | × 3 copies |
> |---|---|---|---|
> | VM 100 — Home Assistant | ~32GB allocated, ~2–4GB used | ~1–2 GB | ~3–6 GB |
> | VM 101 — Frigate NVR | 64GB allocated, grows with recordings | 10–30 GB | 30–90 GB |
>
> **Recommendation:** Do NOT include VM 101 in local daily backups — Frigate's
> video data makes snapshots huge and will fill the SSD quickly. Use the NAS
> (192.168.40.50, VLAN 40) as the backup target for VM 101 once it is
> available, or rely on Proxmox snapshots before config changes only.
>
> For VM 100 (HA), 3× daily local backups is fine — HA's config footprint is
> small (~100–500 MB compressed).
>
> Check remaining space before and after first backup runs:
> ```bash
> pvesm status     # shows used/available per storage pool
> df -h /var/lib/vz   # local storage on the SSD
> ```

---

## Phase F — Trunk verification

The router is already in first-flight state. Use this phase to verify the
Proxmox trunk after the VLAN-aware bridge is configured.

### F1 — Move the cable

Plug the MINISFORUM host into **lan1** on the GL-MT6000. This port carries tagged VLANs
`10,20,30,35,40,50,60,70`.

### F2 — Confirm no temporary access interface remains

The current recommended config does not include a temporary `vmbr0.1` interface.
If you previously used the older two-network flow, remove or comment out the
entire `vmbr0.1` block:

```bash
nano /etc/network/interfaces
# Remove or comment out the entire vmbr0.1 block:
#   auto vmbr0.1
#   iface vmbr0.1 inet static
#       address 192.168.1.220/24
#       gateway 192.168.1.1

ifreload -a
```

### F3 — Verify management access

Connect your laptop to **lan2** on the GL-MT6000 (VLAN 10 untagged).
You should get a DHCP address in `192.168.10.100–149`.

Open `https://192.168.10.10:8006` — Proxmox web UI should load.

### F4 — Verify HA gets its IP

`VM 100 → Console` — HA should now show `IP: 192.168.20.101`.

If it picked up a random DHCP address, set static inside HAOS:
```bash
# In HA console — press Enter, type 'login'
login

nmcli con mod "Wired connection 1" \
    ipv4.method manual \
    ipv4.addresses 192.168.20.101/24 \
    ipv4.gateway 192.168.20.1 \
    ipv4.dns 192.168.20.1
nmcli con up "Wired connection 1"
```
Or: `HA web UI → Settings → System → Network → IPv4 → Static`

---

## Access URLs

| Access method | URL | Available |
|---|---|---|
| Proxmox (temporary) | `https://<lan2-dhcp-ip>:8006` | Before trunk config, while plugged into lan2 |
| Proxmox (permanent) | `https://192.168.10.10:8006` | After moving MINISFORUM host to lan1 trunk |
| Home Assistant (local) | `http://192.168.20.101:8123` | After VM 100 is running on VLAN 20 |
| Home Assistant (remote) | `http://192.168.20.101:8123` via WireGuard | After VPN setup |

---

## Completion checklist

**Proxmox host**
- [ ] Web UI reachable on temporary lan2 DHCP IP before trunk config
- [ ] Enterprise repo disabled, no-subscription repo added
- [ ] `dist-upgrade` run
- [ ] Subscription nag popup removed
- [ ] Timezone: Europe/London
- [ ] IOMMU enabled (intel_iommu=on iommu=pt) + grub updated
- [ ] SSH key added, password auth disabled
- [ ] No stale `vmbr0.1` temporary interface remains
- [ ] Proxmox reachable at 192.168.10.10:8006 after moving MINISFORUM host to lan1

**VM 100 — home-assistant**
- [ ] VM created: q35, OVMF, VirtIO SCSI, VLAN 20
- [ ] HAOS qcow2 imported and attached as scsi0
- [ ] Boot order: scsi0 only
- [ ] Start at boot: enabled
- [ ] MAC noted and added to dhcp-config.conf
- [ ] Daily backup scheduled (local, VM 100 only — see Phase E space note)
- [ ] HAOS boots, onboarding wizard completed
- [ ] HA reachable at http://192.168.20.101:8123

**VM 101 — frigate-nvr**
- [x] VM created: q35, OVMF, VirtIO SCSI, VLAN 30, 64GB disk
- [x] Debian 13 cloud image live path used for current VM 101
- [ ] ISO removed after install (`qm set 101 --delete ide2`) if fallback installer path was used
- [x] Start at boot: enabled, startup order: 2
- [x] MAC noted and added to dhcp-config.conf (option ip 192.168.30.20)
- [ ] Frigate NVR setup: `scripts/setup/proxmox/frigate_vm_setup_guide.md`

---

## Next steps after HA is running

1. Deploy router -> `scripts/setup/router/` phases 1-8
2. MQTT + TLS setup → `docs/procedures/ssl_tls_guide.md`
3. Copy VentSys packages to `/config/packages/` on HA
4. Copy dashboard → `/config/www/ventsys-dashboard.html`
5. Frigate VM setup → `scripts/setup/proxmox/frigate_vm_setup_guide.md` (VM 101, VLAN 30)

---

## VM reference

| ID | Name | VLAN | IP | RAM | Cores | Boot |
|---|---|---|---|---|---|---|
| 100 | home-assistant | 20 | 192.168.20.101 | 4096 MB | 2 | order 1 |
| 101 | frigate-nvr | 30 | 192.168.30.20 | 4096 MB | 2 | order 2 |
| 102 | monitoring | 60 | 192.168.60.10 | 2048 MB | 2 | order 3 |
