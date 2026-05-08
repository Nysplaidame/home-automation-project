# Secrets Reference
# Master inventory of all credentials and secrets in the home automation system
#
# STORAGE: Bitwarden (primary) + paper backup (offline, locked away)
# Never commit any actual secret values to GitHub — this file documents
# what secrets exist and where they are used, not their values.
#
# GITIGNORE CHECK: the following must be in .gitignore:
#   secrets.yaml  (ESPHome — in ventsys/ and configs/esphome/)
#   /config/secrets.yaml  (HA — never leaves the HA VM)
#   *.key, *.pem, *.crt  (TLS private keys and certs)
#
# BITWARDEN ORGANISATION: Create a collection named "Home Automation"
# with folders matching the sections below.
#
# Updated 2026-04-10:
#   - Section 1: HomePrinters WiFi added (VLAN 35)
#   - Section 7: P1S IP updated to 192.168.35.200; Docker host reference updated
#   - Section 9: Frigate-only note added (Bambuddy removed from VM 101)
#   - Section 11: Docker host (VM 103) added
#   - Credential rotation checklist: HomePrinters and Docker host entries added

---

## 1 — Network / Router (GL-MT6000 OpenWrt)

| Secret | Bitwarden entry | Notes |
|---|---|---|
| Router admin password | `router-admin` | LuCI web UI + SSH root login |
| HomeMain WiFi password | `wifi-homemain` | VLAN 1 — phones, laptops, tablets |
| HomeAdmin WiFi password | `wifi-homeadmin` | VLAN 10 — admin devices |
| HomePrinters WiFi password | `wifi-homeprinters` | VLAN 35 — Bambu P1S, Athena 2 |
| HomeIoT WiFi password | `wifi-homeiot` | VLAN 50 — all ESPHome devices |
| HomeGuest WiFi password | `wifi-homeguest` | VLAN 99 — visitor access |
| WireGuard server private key | `wireguard-server-privkey` | vlan-config.conf `private_key` field |
| WireGuard client 1 private key | `wireguard-client1-privkey` | Mobile device 1 — generate on client |
| WireGuard client 2 private key | `wireguard-client2-privkey` | Mobile device 2 |
| WireGuard client 3 private key | `wireguard-client3-privkey` | Laptop/Desktop |

> WireGuard keys are generated in pairs. The router config (vlan-config.conf)
> holds the SERVER private key and each client's PUBLIC key. Client private keys
> never leave the client device — store a Bitwarden copy as backup only.

---

## 2 — Proxmox Host (192.168.10.10)

| Secret | Bitwarden entry | Notes |
|---|---|---|
| Proxmox root password | `proxmox-root` | Web UI port 8006 + SSH |
| SSH public key (laptop) | `ssh-pubkey-laptop` | Added to ~/.ssh/authorized_keys on Proxmox |
| SSH private key (laptop) | `ssh-privkey-laptop` | Keep on laptop only; Bitwarden copy as backup |

---

## 3 — MQTT Broker (Mosquitto on HA VM, 192.168.20.101)

| Secret | Bitwarden entry | Used in |
|---|---|---|
| MQTT username | `mqtt-credentials` | All ESPHome YAMLs, HA MQTT integration, Bambuddy |
| MQTT password | `mqtt-credentials` | Same Bitwarden entry — username + password together |

> The MQTT username is `mqtt` (created in ha_vm_setup_guide.md Phase 2.1).
> The password is IDENTICAL at ports 1883 (pre-TLS) and 8883 (post-TLS) —
> only the port and ca_certificate setting change during TLS migration.

---

## 4 — ESPHome (secrets.yaml on your flashing workstation)

ESPHome reads secrets from a `secrets.yaml` file in the same directory as the
YAML configs. This file must NOT be committed to GitHub.

Create at both locations before flashing:
- `ventsys/ventsys_bundle_updated/secrets.yaml`
- `configs/esphome/secrets.yaml`

```yaml
# secrets.yaml — ESPHome (DO NOT COMMIT TO GITHUB)
wifi_ssid: "HomeIoT"
wifi_pass: "your-homeiot-password"         # Bitwarden: wifi-homeiot
mqtt_user: "mqtt"
mqtt_pass: "your-mqtt-password"            # Bitwarden: mqtt-credentials
mqtt_ca_cert: |
  -----BEGIN CERTIFICATE-----
  (paste contents of ca.crt — generated per docs/procedures/ssl_tls_guide.md)
  -----END CERTIFICATE-----
api_key: "your-32-byte-base64-api-key"     # generate: openssl rand -base64 32
ota_password: "your-ota-password"          # any strong password
```

| Secret key | Bitwarden entry | Notes |
|---|---|---|
| `wifi_pass` | `wifi-homeiot` | HomeIoT SSID password |
| `mqtt_pass` | `mqtt-credentials` | Same as Section 3 |
| `mqtt_ca_cert` | `tls-ca-cert` | Public CA cert — not sensitive, keep a Bitwarden copy |
| `api_key` | `esphome-api-key` | One per device ideally; shared across VentSys fleet is fine |
| `ota_password` | `esphome-ota-password` | One shared password for all VentSys OTA updates is fine |

> For pre-TLS stage-1 flashing, omit `mqtt_ca_cert` — the `_pretls.yaml`
> configs don't reference it. Add it once TLS is live per
> `docs/procedures/ssl_tls_guide.md`.

---

## 5 — Home Assistant (/config/secrets.yaml on the HA VM)

This file lives on the HA VM only. Never copy it to the vault or GitHub.
Edit via File Editor add-on or HA Terminal: `/config/secrets.yaml`

```yaml
# /config/secrets.yaml on HA VM — DO NOT COPY TO VAULT OR GITHUB
home_latitude: 51.xxxx
home_longitude: -0.xxxx
home_elevation: 10
external_url: "https://your-vpn-or-domain"
mqtt_username: "mqtt"
mqtt_password: "your-mqtt-password"        # Bitwarden: mqtt-credentials
```

| Secret key | Bitwarden entry | Notes |
|---|---|---|
| `home_latitude` / `home_longitude` | `home-location` | Used for sun-based automations |
| `home_elevation` | `home-location` | Same entry |
| `external_url` | `ha-external-url` | WireGuard VPN address or Nabu Casa URL |
| `mqtt_password` | `mqtt-credentials` | Same as Section 3 |

---

## 6 — TLS / PKI (generated per docs/procedures/ssl_tls_guide.md)

| File | Where stored | Sensitivity |
|---|---|---|
| `ca.key` (CA private key) | HA VM only — `/ssl/ca.key` | CRITICAL — never copy off the VM |
| `ca.crt` (CA certificate) | Safe to copy | Public — goes into ESPHome `mqtt_ca_cert` |
| `server.key` (Mosquitto key) | HA VM only — `/ssl/server.key` | HIGH — never copy off the VM |
| `server.crt` (Mosquitto cert) | HA VM only — `/ssl/server.crt` | Low — signed by your CA |

> `ca.key` is the most critical file in the system. If it leaks, anyone can
> issue certificates your ESPHome devices will trust. It is protected by
> Proxmox VM backups — snapshots include it automatically.
> **I-7 audit note:** This applies only if the CA is at `/config/ssl/ca/` on the HA VM
> (per `docs/procedures/ssl_tls_guide.md`). If you followed Option B from
> `ssl_tls_guide.md` and placed the CA on the NAS (`/mnt/nas/configs/ca/`), it is NOT
> covered by HA native backups or Proxmox VM snapshots. Run `backup-certificates.sh` from
> the TLS guide and store an encrypted copy of `ca.key` in Bitwarden as a secure note.
> Store `ca.crt` (the PUBLIC cert) in Bitwarden as `tls-ca-cert` for easy
> retrieval when re-flashing ESPHome boards.

---

## 7 — Bambuddy + P1S Printer

> P1S is at 192.168.35.200 (VLAN 35, HomePrinters WiFi).
> Bambuddy runs as a workload on docker-host, VM 103 (192.168.20.102, VLAN 20).
> See scripts/setup/proxmox/docker_host_setup_guide.md.

| Secret | Bitwarden entry | Notes |
|---|---|---|
| P1S serial number | `p1s-printer` | Format: 01P09C41xxxxxxx — required in bambuddy_p1s_package.yaml |
| P1S access code | `p1s-printer` | 8-digit code from printer Developer Mode screen |
| HomePrinters WiFi password | `wifi-homeprinters` | P1S connects via HomePrinters SSID on VLAN 35 |
| HA long-lived token (Bambuddy) | `ha-tokens` | HA: Profile → Security → Long-Lived Access Tokens |

> The P1S runs its own MQTT broker on port 8883. Bambuddy connects TO the
> printer as a client — the printer never initiates outbound connections.
> The P1S only supports one simultaneous local MQTT client — close Bambu Studio
> if Bambuddy shows a connection failure.

---

## 8 — Home Assistant long-lived tokens

| Token name | Bitwarden entry | Used in |
|---|---|---|
| `Bambuddy` | `ha-tokens` | Bambuddy web UI on docker-host → Settings → Home Assistant |
| `VentSys Dashboard` | `ha-tokens` | `HA_CONFIG.token` in live `/config/www/ventsys-dashboard.html` only |

> HA shows each token value only once at creation. Store immediately in Bitwarden.
> Keep the repo source `ventsys-dashboard.html` on the placeholder value
> `__SET_HA_TOKEN__`; only the live HA-served copy should contain the real token.

---

## 9 — Frigate NVR VM (192.168.30.20, VLAN 30)

> VM 101 runs Frigate only. Bambuddy runs on docker-host VM 103 — see Section 11.

| Secret | Bitwarden entry | Notes |
|---|---|---|
| Frigate VM admin password | `frigate-vm` | Debian install password for `admin` user; SSH access |
| Frigate UI password (if enabled) | `frigate-ui` | Only if auth is enabled in config.yml |

---

## 10 — NAS (192.168.40.50)

| Secret | Bitwarden entry | Notes |
|---|---|---|
| Pi NAS admin password | `pi-nas` | SSH + Samba share access |
| Samba share password | `pi-nas` | Same entry — Windows `net use` and HA network storage |

---

## 11 — Docker host VM (VM 103, 192.168.20.102, VLAN 20)

| Secret | Bitwarden entry | Notes |
|---|---|---|
| Docker host admin password | `docker-host-vm` | Debian admin/root credential for VM 103; SSH access |

> The Bambuddy application uses the P1S access code (Section 7), the HA token
> (Section 8), and the MQTT credentials (Section 3). The canonical workflow is
> to enter the printer details and HA token in the Bambuddy web UI. Keep
> `/opt/stacks/bambuddy/.env` limited to container/bootstrap settings such as MQTT
> publishing, and never commit it to GitHub.

---

## Credential rotation checklist

Run through this after any suspected compromise, or annually as good practice:

- [ ] Router admin password — update in Bitwarden, re-login to LuCI
- [ ] WiFi passwords — update in router wireless config; OTA-push updated
      secrets.yaml to all ESPHome devices (USB fallback if OTA unavailable).
      HomePrinters password change requires reconnecting P1S and Athena 2 manually.
- [ ] MQTT password — update in: Mosquitto config, HA MQTT integration, all
      ESPHome secrets.yaml files, and Bambuddy MQTT settings on docker-host. OTA push all ESP boards.
- [ ] ESPHome OTA password — OTA push new firmware to all boards
- [ ] ESPHome API key — OTA push; re-adopt in HA if required
- [ ] HA long-lived tokens — delete old in HA, create new, update
      ventsys-dashboard.html and the Bambuddy web UI on docker-host
- [ ] TLS CA/certs — follow `docs/procedures/ssl_tls_guide.md` re-issuance steps
- [ ] Proxmox root password — `passwd root` on Proxmox shell, update Bitwarden
- [ ] Docker host admin password — `passwd root` or the configured admin user on VM 103, update Bitwarden
- [ ] P1S access code — regenerate via printer touchscreen; update Bitwarden and
      Bambuddy printer settings in the web UI on docker-host
- [ ] WireGuard keys — regenerate pairs, update vlan-config.conf, redistribute configs

---

## Paper backup

Print or handwrite the following. Store in a locked location physically
separate from the hardware (not the same room as the MINIX):

1. Router admin password
2. Proxmox root password
3. MQTT username + password
4. HomeIoT WiFi password  — needed to re-flash ESPHome boards from scratch
5. HA admin username + password
6. Bitwarden master password  — recovery if Bitwarden is inaccessible

WireGuard keys, TLS keys, API tokens, and HomePrinters WiFi password do NOT
need to be on paper — they can all be regenerated or reconfigured from the
six above. The six above are the minimum to rebuild the entire system from
scratch with no internet access to Bitwarden.
