# Home Assistant VM — Setup Guide
**VM ID:** 100
**Name:** home-assistant
**IP:** 192.168.20.101 — VLAN 20 (Automation)
**Host:** Proxmox on MINIX NEO Z350, 192.168.10.10

> **Prerequisite:** VM 100 already created and HAOS booting per
> `scripts/setup/proxmox/proxmox_setup_guide.md` Phases D and F.
> This guide picks up from the moment HA is reachable on the network.

---

## Phase 1 — First boot and onboarding

### 1.1 — Confirm HA is reachable

Open `http://192.168.20.101:8123` in your browser.
If you get a timeout, check `VM 100 → Console` in Proxmox — HA should show
its IP on the console. If it still says "waiting for network", VLAN 20 isn't
live on the router yet (complete router cutover first).

### 1.2 — Complete the onboarding wizard

The wizard runs once on first boot. Fill in:

| Field | Value |
|---|---|
| Name | your name |
| Username | `admin` (or whatever you prefer) |
| Password | strong password — save it in a password manager |
| Location | set your location (used for sun-based automations) |
| Elevation | your elevation in metres |
| Time zone | Europe/London |
| Unit system | Metric |

Click through any device discovery screens — you can add discovered devices
later. The important thing is creating the admin account.

### 1.3 — Set a static IP inside HAOS

Even with a DHCP reservation on the router, set it statically inside HA too.
`Settings → System → Network → Configure (next to your wired interface)`

| Field | Value |
|---|---|
| IPv4 | Manual |
| IP address | 192.168.20.101 |
| Subnet mask | 255.255.255.0 (/24) |
| Gateway | 192.168.20.1 |
| DNS | 192.168.20.1 |

Save and wait for HA to reconnect. Reload the page at `http://192.168.20.101:8123`.

### 1.4 — Point HAOS time sync at the router

The router is the local NTP authority. Home Assistant should use the Automation
VLAN gateway (`192.168.20.1`) as its NTP source so HA-managed ESPHome/VentSys
devices receive router-derived time through `time: platform: homeassistant`.

Use the repo artifact:

```text
configs/home-assistant/haos-timesyncd-router.conf
```

Apply it as HAOS `/etc/systemd/timesyncd.conf` using a Home Assistant OS
`CONFIG` import or the HAOS host shell. This is OS-level configuration, not
normal `/config/configuration.yaml`.

From the Home Assistant Terminal add-on after preparing the `CONFIG` import:

```bash
ha os import
ha host reboot
```

After reboot, validate that HAOS has sane time before adopting ESPHome devices:

```bash
date
ha host info
```

---

## Phase 2 — Essential add-ons

Add-ons run as supervised containers inside HAOS. Install them via:
`Settings → Add-ons → Add-on Store`

Install these in order:

### 2.1 — Mosquitto MQTT Broker

Search: `Mosquitto broker`

Install, then go to the **Configuration** tab before starting:

```yaml
logins: []         # leave empty — auth configured via HA user below
require_certificate: false   # start without TLS; enable after testing
customize:
  active: false
```

Start the add-on. Then create an MQTT user:
`Settings → People → Add Person` — create a user named `mqtt` with a strong password.
This user is used by ESPHome devices and the MQTT integration.

Then configure the MQTT integration:
`Settings → Devices & Services → Add Integration → MQTT`

| Field | Value |
|---|---|
| Broker | `192.168.20.101` (localhost within HA) |
| Port | `1883` (start unencrypted, switch to 8883+TLS later) |
| Username | `mqtt` |
| Password | password you just created |

Click Submit. You should see "Connected".

> **TLS hardening** is covered separately in
> `docs/procedures/ssl_tls_guide.md`.
> The MQTT broker must be working unencrypted first before adding TLS.

### 2.2 — File Editor

Search: `File editor`

Install and start. This lets you edit config files directly in the HA web UI.
No special configuration needed.

Enable it in the sidebar:
Open the add-on → **Show in sidebar** toggle → On.

### 2.3 — Terminal & SSH

Search: `Terminal & SSH`

Install. In the **Configuration** tab:

```yaml
authorized_keys: []   # add your SSH public key here if you want SSH access
password: ""          # leave blank to disable password auth (use keys only)
```

Start. This gives you a shell inside HA (useful for running commands and
copying files without needing Proxmox shell access).

### 2.4 — ESPHome

Search: `ESPHome`

Install and start. Open the dashboard — you'll see it's empty until ESPHome
devices are adopted. This is where the VentSys fan and valve controllers will
appear when they come online.

No configuration needed at this stage.

---

## Phase 3 — Package configuration

Packages let you keep related config split across separate YAML files instead
of piling everything into `configuration.yaml`.

### 3.1 — Enable packages in configuration.yaml

Open File Editor → `configuration.yaml`

> **Do not replace a fresh HAOS `configuration.yaml` wholesale.** The vault
> `configs/home-assistant/configuration.yaml` is a reference config, but a fresh
> HAOS install usually contains `default_config:`. Removing that line can disable
> several useful built-in integrations and make onboarding harder. Patch the
> live file instead.

First make a backup from Terminal & SSH:

```bash
cp -a /config/configuration.yaml "/config/configuration.yaml.bak.$(date +%Y%m%d_%H%M%S)"
```

Then add only the package include. If the file already has a `homeassistant:`
block, add `packages:` inside that existing block:

```yaml
homeassistant:
  packages: !include_dir_named packages
```

If there is no `homeassistant:` block, add the block above at the top level.
Do **not** add a second `homeassistant:` block; YAML accepts duplicate keys in
some parsers and the later block can silently overwrite the earlier one.

Keep these existing fresh-install lines if present:

```yaml
default_config:
automation: !include automations.yaml
script: !include scripts.yaml
scene: !include scenes.yaml
```

If `frontend:` is already present, do not duplicate it. If it is not present
and you want theme support now, add:

```yaml
frontend:
  themes: !include_dir_merge_named themes
```

Save.

### 3.2 — Create required directories and placeholder files

In Terminal & SSH:
```bash
mkdir -p /config/packages /config/themes /config/www
touch /config/automations.yaml /config/scripts.yaml /config/scenes.yaml
```

`/config/themes` must exist if `frontend: themes: !include_dir_merge_named themes`
is enabled. The placeholder YAML files prevent hard startup errors if the
fresh-install includes still reference them.

### 3.3 — Copy VentSys package files

Copy these files from your vault into `/config/packages/` on the HA host.

The files live in `ventsys/ventsys_bundle_updated/` in the safety vault:

| Vault file | Destination on HA |
|---|---|
| `ventsys_ha_package.yaml` | `/config/packages/ventsys_ha_package.yaml` |
| `ventsys_ha_optional.yaml` | **DO NOT copy yet** — this file has a "DO NOT LOAD YET" header. Copy it only when all prerequisites in the file are met (sensor boards deployed, baro_pressure entities confirmed). A6-2 fix. |
| `ventsys_ha_scripts.yaml` | `/config/packages/ventsys_ha_scripts.yaml` |

Do not copy these yet:

| Vault file | Reason |
|---|---|
| `configs/home-assistant/bambuddy_p1s_package.yaml` | Contains `<P1S_SERIAL>` placeholders and depends on the Bambuddy workload on docker-host. |
| `ventsys_ha_optional.yaml` | Depends on pressure/PID sensor prerequisites that are not deployed yet. |
| `configs/home-assistant/automations.yaml` | Safety automations reference printer smart-plug entities; load only after the core VentSys package validates, then test each automation. |

**Method A — via Samba/file share (if you set up the Samba add-on)**
Mount `\\192.168.20.101\config` on your laptop and copy directly.

**Method B — via Terminal & SSH (paste the content)**
In Terminal: `nano /config/packages/ventsys_ha_package.yaml`
Paste the file content, Ctrl+X to save.

**Method C — via File Editor**
Create each file in File Editor by navigating to `/config/packages/` and
using the New File button.

### 3.4 — Copy the VentSys dashboard

```bash
mkdir -p /config/www
# Then copy dashboards/ventsys-dashboard.html into /config/www/ventsys-dashboard.html
```

After copying, edit the live HA copy and set your Long-Lived Token:
`Settings → Profile → Security → Long-Lived Access Tokens → Create Token`
Copy the token and paste it into `HA_CONFIG.token` in `/config/www/ventsys-dashboard.html`.
Leave the repo source `dashboards/ventsys-dashboard.html` on the placeholder value
`__SET_HA_TOKEN__` so the token never lands in Git.

### 3.5 — Restart HA to load packages

Before restarting, run the Home Assistant config checker from Terminal & SSH:

```bash
ha core check
```

Only restart if the check reports `Configuration check finished successfully`.
If it reports an error, fix the named file first and run `ha core check` again.

`Settings → System → Restart → Restart Home Assistant`

After restart, check `Settings → System → Logs` for any YAML errors.

---

## Phase 4 — Verify MQTT and VentSys entities

### 4.1 — Check entities were created

`Settings → Devices & Services → Entities`

Search for `ventsys` — you should see entities including:
- `fan.inline_fan`
- `fan.spray_booth_fan`
- `number.fdm_valve`, `number.sla_valve`  (`number.booth_valve` is commented out — no firmware yet; see A4-3)
- `number.fdm_branch_valve`, `number.fdm_360_intake` etc.
- `sensor.sla_risk`, `sensor.fdm_risk`
- `input_boolean.ventsys_failsafe`

### 4.2 — Test MQTT publish/subscribe

In Terminal:
```bash
# Subscribe to a topic (leave this running in one terminal)
mosquitto_sub -h localhost -p 1883 -u mqtt -P <password> -t 'ventsys/#' -v

# In another terminal, publish a test message
mosquitto_pub -h localhost -p 1883 -u mqtt -P <password> \
    -t 'ventsys/fan/control' -m 'on'
```

You should see `ventsys/fan/control on` appear in the subscriber window.

> **TLS note (A9-1):** Commands above use port 1883 (Stage 1 pre-TLS only).
> After MQTT TLS migration (`docs/procedures/ssl_tls_guide.md`),
> Mosquitto only listens on port 8883. Switch to:
> mosquitto_sub -h localhost -p 8883 --cafile /ssl/ca.crt -u mqtt -P <password> -t ventsys/# -v

### 4.3 — Test the dashboard

Open `http://192.168.20.101:8123/local/ventsys-dashboard.html`

The header should show `◉ HA LIVE` once the token is set correctly.
Test a mode button — it should call the corresponding HA script.

---

## Phase 5 — Frigate integration

This connects HA to the Frigate NVR VM once it's running on 192.168.30.20.

### 5.1 — Install the Frigate integration

`Settings → Devices & Services → Add Integration`
Search for `Frigate` — if not found, add it via HACS first (see 5.2).

| Field | Value |
|---|---|
| URL | `http://192.168.30.20:8971` |

> **F-36 — Port note:** Port 5000 was Frigate's web/API port up to v0.13.
> From Frigate 0.14+ the UI and API moved to port **8971**; port 5000 became
> a metrics/debug endpoint only. Check your deployed Frigate version:
> `docker inspect frigate | grep -i image` on the Frigate VM, then use 5000
> (≤0.13) or 8971 (≥0.14) accordingly. Update this guide and the firewall
> rule `HA to NVR Access` in `firewall-config.conf` to match.

### 5.2 — HACS (optional — needed for Frigate integration card)

HACS gives access to community integrations and frontend cards.

In Terminal:
```bash
wget -O - https://get.hacs.xyz | bash -
```

Restart HA after installing. Then:
`Settings → Devices & Services → Add Integration → HACS`

After HACS is installed, install the **Frigate Card** from HACS frontend section.
This adds a camera card with event timeline to your dashboards.

---

## Phase 6 — Add-ons reference

| Add-on | Purpose | Port | Status |
|---|---|---|---|
| Mosquitto | MQTT broker for all IoT devices | 1883 (8883 after TLS) | Required |
| File Editor | Edit YAML config in browser | — | Required |
| Terminal & SSH | Shell access inside HA | 22 (optional) | Required |
| ESPHome | Manage VentSys ESP32 devices | 6052 | Required |
| Samba | File share for config folder | 445 | Optional |
| HACS | Community integrations | — | Optional |

---

## Phase 7 — Security hardening

### 7.1 — Enable 2FA

`Settings → People → [your user] → Multi-factor Authentication → Enable TOTP`

Scan the QR code with an authenticator app.

### 7.2 — Create a separate admin backup account

Create a second admin account with a different username/password as a recovery
option. Store credentials in your password manager.

### 7.3 — Long-lived tokens

Create tokens only when needed and document what each token is used for.
Current tokens needed:
- VentSys dashboard (`HA_CONFIG.token` in `dashboards/ventsys-dashboard.html`)

### 7.4 — Trusted networks (optional)

If you want to skip login when on the VLAN 20 network:
`configuration.yaml`:
```yaml
homeassistant:
  auth_providers:
    - type: trusted_networks
      trusted_networks:
        - 192.168.20.0/24
      allow_bypass_login: true
    - type: homeassistant
```

> Only do this if you're confident in your VLAN isolation.

---

## Phase 8 — Backups

HA has its own backup system separate from Proxmox snapshots.

### 8.1 — Manual backup

`Settings → System → Backups → Create Backup`

Creates a `.tar` file of the entire HA config including add-on data.

CLI equivalent from the Terminal & SSH add-on:

```bash
ha backups new \
  --name "post-ha-ventsys-staged-YYYYMMDD" \
  --location=.local \
  --homeassistant-exclude-database=true
```

The `--location=.local` form is deliberate; the HAOS 2026 CLI treats
`--location .local` as a positional command and fails. The explicit
`--homeassistant-exclude-database=true` form is also deliberate; omitting
`=true` is accepted by the CLI but did not set the flag on this HAOS 2026 host.
Excluding the database keeps this as a compact config/add-on checkpoint rather
than a history archive.

Current baseline checkpoint created on this host:

```text
Name: post-ha-ventsys-staged-20260507-db-excluded
Slug: 5fdeaff7
File: /backup/5fdeaff7.tar
Database excluded: true
```

### 8.2 — Automatic backups

`Settings → System → Backups → Automatic Backups`

| Field | Value |
|---|---|
| Schedule | Daily |
| Time | 03:00 |
| Backups to keep | 7 |
| Location | Local storage or NAS (VLAN 40, 192.168.40.50 once configured) |

### 8.3 — NAS backup (when NAS is ready)

Add a network storage location:
`Settings → System → Storage → Add Network Storage`

| Field | Value |
|---|---|
| Name | NAS Backups |
| Server | `192.168.40.50` |
| Protocol | NFS or Samba |
| Share | `/export/ha-backups` or the OMV export path shown in the UI |

---

## Completion checklist

- [ ] HA reachable at `http://192.168.20.101:8123`
- [ ] Admin account created, password saved
- [ ] Static IP set inside HAOS (192.168.20.101/24, gw 192.168.20.1)
- [ ] Mosquitto add-on installed and running
- [ ] MQTT integration connected (localhost:1883 for Stage 1 pre-TLS; switch to 8883 after TLS migration)  # A10-2
- [ ] File Editor add-on installed
- [ ] Terminal & SSH add-on installed
- [ ] ESPHome add-on installed
- [ ] `/config/packages/` directory created
- [ ] VentSys package files copied to `/config/packages/`
- [ ] HA restarted, no YAML errors in logs
- [ ] VentSys entities visible in Settings → Entities
- [ ] Dashboard deployed to `/config/www/ventsys-dashboard.html`
- [ ] Long-lived token created and set in live `/config/www/ventsys-dashboard.html` only
- [ ] Dashboard shows `◉ HA LIVE`
- [ ] 2FA enabled on admin account
- [ ] Automatic backups scheduled

---

## Next steps

1. ESPHome device adoption — when VentSys ESP32 boards are flashed and online,
   they'll appear in the ESPHome add-on for adoption
2. MQTT TLS — `docs/procedures/ssl_tls_guide.md`
3. Frigate VM setup — `scripts/setup/proxmox/frigate_vm_setup_guide.md`
4. Docker host + Bambuddy/P1S integration — `scripts/setup/proxmox/docker_host_setup_guide.md`
   (Bambuddy runs as a workload on VM 103 at 192.168.20.102)
5. NAS integration — when OMV is configured on VLAN 40
