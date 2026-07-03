# SSL/TLS Certificate Guide
# Covers: HTTPS for the HA web UI, local CA for MQTT TLS
# This is the canonical MQTT TLS and HTTPS procedure for active deployment.

---

## Overview

Two separate TLS concerns:

| What | Where | Method |
|---|---|---|
| HA web UI HTTPS | https://192.168.20.101:8123 | Self-signed cert or local CA |
| MQTT TLS | Mosquitto port 8883 | Local CA (covered in this guide) |
| Remote access HTTPS | WireGuard tunnel + HA | Not needed - VPN is already encrypted |

> For a home network accessed only through a VPN, a self-signed certificate can
> be acceptable, but this project now uses a local CA so browsers and the
> Companion App can trust Home Assistant without exposing HA publicly.

## Current HA Native HTTPS State

Live as of 2026-07-02:

- Home Assistant native HTTPS is enabled at
  `https://192.168.20.101:8123`.
- HTTP on `192.168.20.101:8123` is no longer the active HA UI.
- HA uses `/ssl/fullchain.pem` and `/ssl/privkey.pem`.
- `/ssl/fullchain.pem` chains to `/ssl/ca.crt`, the local `Home Local CA`.
- The certificate SANs include `192.168.20.101`, `homeassistant.home.local`,
  `homeassistant`, and `core-mosquitto.local.hass.io`.
- `/ssl/ha_https_preflight_fullchain.pem` and
  `/ssl/ha_https_preflight_privkey.pem` still exist but are legacy pre-flight
  self-signed material and are not the active HA HTTPS cert/key.
- `homeassistant.internal_url` is set in YAML to
  `https://192.168.20.101:8123`; no `external_url` is currently set.
- The local CA was trusted on the Windows operator profile and on the operator
  Android Companion App device during cutover.

Live HA source pattern:

```yaml
homeassistant:
  internal_url: https://192.168.20.101:8123
  packages: !include_dir_named packages

http:
  ssl_certificate: /ssl/fullchain.pem
  ssl_key: /ssl/privkey.pem
  server_host: 0.0.0.0
  server_port: 8123
```

Cutover evidence and rollback:

- Restricted local pre-change snapshot:
  `C:\Users\Administrator\ha-live-snapshots\pre-ha-native-tls-20260702-102124`
- HA backup created before cutover:
  `pre-ha-native-tls-20260702-db-excluded`, slug `04da1c7d`, local location,
  database excluded.
- Live config backup before cutover:
  `/config/configuration.yaml.pre-native-tls-20260702-104713`.
- Rollback command path: restore that backup over `/config/configuration.yaml`,
  run `ha core check`, then restart HA Core. Restore the Companion App URL to
  `http://192.168.20.101:8123` only if HTTPS rollback is actually performed.

Post-cutover validations completed:

- Browser access to `https://192.168.20.101:8123` returned HTTP 200 and used a
  trusted chain on the Windows operator profile.
- Companion App on Android connected after the local CA was trusted.
- CCTV `Mobile Balanced` and `Mobile Full Control` views worked on mobile.
- Advanced Camera Card main and substream views were validated through the
  mobile views.
- Frigate HA integration remained reachable; Frigate API version/stats returned
  the live first camera.
- VentSys dashboard assets served over HA HTTPS and still use relative
  same-origin behavior.
- Grafana and Uptime Kuma remain direct HTTP links from HA, not embedded mixed
  content.

Remote/mobile note: at home, use trusted WiFi direct access to
`https://192.168.20.101:8123` with Tailscale off. Off-WiFi remote access should
use Tailscale. DERP relay was observed on the operator Android phone and can
cause HA Companion App websocket drops; see
`docs/procedures/tailscale_remote_access_guide.md`.

## MQTT Transition Strategy

Current live state on 2026-05-15:

- HA / Mosquitto still has `1883` open as the active bootstrap path for existing clients.
- `8883` is live for MQTT TLS and has been validated with authenticated publish/subscribe.
- Valve1 has been validated end-to-end on MQTT TLS over `8883`.
- New MQTT-backed ESPHome integrations should now be introduced directly on TLS.
- CA and broker certificate files are installed on HA under `/ssl`:
  `/ssl/ca.crt`, `/ssl/ca.key`, `/ssl/server.crt`, `/ssl/fullchain.pem`, and
  `/ssl/privkey.pem`.

Because devices and entities will come online one by one, the migration should
be phased rather than a big-bang cutover.

### Staged plan

1. Keep `1883` available for bootstrap and early testing.
2. Prepare the CA, broker certificate, and Mosquitto TLS listener on `8883`. ✅
3. Validate one client end-to-end on `8883` with cert trust enabled. ✅
4. Deploy new integrations directly on `8883` where practical.
5. Remove `1883` only after all real clients are off it.

### Client guidance during transition

- New integrations should use `8883` directly now that the CA and broker certs
  are proven.
- Use `1883` only as an explicit temporary recovery/bootstrap exception, and
  document the exception before enabling it.
- Do not leave a half-migrated undocumented state; every client should be clearly
  documented as either `bootstrap on 1883` or `steady-state on 8883`.
- Do not close firewall access to `1883` until all real clients have been moved
  and retested on `8883`.

### Expected migration order

- Frigate
- Bambuddy, if it ultimately needs HA MQTT in practice
- Future ESPHome / VentSys devices
- Any later MQTT consumers

### ESPHome client baseline after valve1 pilot

The successful valve1 migration on 2026-05-15 established this working client
pattern for ESPHome devices on VLAN 50:

```yaml
wifi:
  use_address: ${device_ip}
  manual_ip:
    static_ip: ${device_ip}
    gateway: 192.168.50.1
    subnet: 255.255.255.0
    dns1: 192.168.50.1

mqtt:
  broker: 192.168.20.101
  port: 8883
  username: !secret mqtt_user
  password: !secret mqtt_pass
  discovery: false
  discover_ip: false
  certificate_authority: !secret mqtt_ca_cert
```

Validation evidence from the broker log:

- Valve1's last plain MQTT connection was on `1883` at `2026-05-15 10:23:13`.
- Its first TLS connection was on `8883` at `2026-05-15 10:24:08`.
- Mosquitto recorded `negotiated TLSv1.2 cipher ECDHE-RSA-AES256-GCM-SHA384`.

---

## Option A - Self-signed certificate (simplest)

### Legacy HA HTTPS pre-flight state

As of 2026-07-02, HA has separate HTTPS pre-flight files:

```text
/ssl/ha_https_preflight_fullchain.pem
/ssl/ha_https_preflight_privkey.pem
```

These files are not enabled in `/config/configuration.yaml`. The 2026-07-02
cutover deliberately used the local CA-backed `/ssl/fullchain.pem` and
`/ssl/privkey.pem` instead because the pre-flight pair was self-signed and did
not chain to `/ssl/ca.crt`.

### Generate cert on the HA VM

In HA Terminal:

```bash
mkdir -p /ssl

# Generate 10-year self-signed cert for the HA IP
openssl req -x509 -newkey rsa:4096 -nodes \
    -keyout /ssl/privkey.pem \
    -out /ssl/fullchain.pem \
    -days 3650 \
    -subj "/CN=homeassistant.home.local" \
    -addext "subjectAltName=IP:192.168.20.101,DNS:homeassistant.home.local"

chmod 600 /ssl/privkey.pem
ls -la /ssl/
```

### Enable HTTPS in HA

Edit `/config/configuration.yaml` - update the `http:` block:

```yaml
http:
  ssl_certificate: /ssl/fullchain.pem
  ssl_key: /ssl/privkey.pem
  server_host: 0.0.0.0
  server_port: 8123
```

Restart HA: `Settings ? System ? Restart`

HA is now at `https://192.168.20.101:8123`. Your browser will warn about the self-signed cert - accept the exception once.

### Trust the cert on your devices (optional - removes browser warning)

Export the cert and install it as a trusted root:

```bash
# Copy cert to your Windows machine
scp admin@192.168.20.101:/ssl/fullchain.pem .
```

**Windows:** Double-click the `.pem` file ? Install Certificate ? Local Machine ? Trusted Root Certification Authorities

**macOS:** Open Keychain Access ? drag cert in ? double-click ? Trust ? Always Trust

**iOS:** Send cert via AirDrop or email, tap to install, then Settings ? General ? About ? Certificate Trust Settings ? enable

---

## Option B - Local Certificate Authority (recommended for MQTT + HA)

A local CA lets you issue certs for both HA and Mosquitto, and install only the CA cert once on your devices to trust everything.

The CA infrastructure was prepared on the router in Phase 8 (`/etc/ventsys/ca/`). You can also do this on the OMV NAS for persistence.

> **I-5 audit note:** This guide describes two CA placement options. **Alternative (recommended):** place
> the CA on the HA VM at `/config/ssl/ca/` -- this keeps the CA within HA native backups and
> avoids cross-VLAN key transfer.
> If placing on the NAS (VLAN 40), ensure VLAN 40 is reachable from VLAN 20 in your firewall,
> transfer the CA key securely via SCP over the management interface, and delete it from the NAS
> once certificate signing is complete. Use this file as the single source of truth for
> production CA workflow.

### Create the CA (on NAS or HA VM)

```bash
mkdir -p /mnt/nas/configs/ca/{certs,private,crl,newcerts}
chmod 700 /mnt/nas/configs/ca/private
touch /mnt/nas/configs/ca/index.txt
echo 1000 > /mnt/nas/configs/ca/serial

# Generate CA private key
openssl genrsa -aes256 -out /mnt/nas/configs/ca/private/ca.key 4096
chmod 400 /mnt/nas/configs/ca/private/ca.key

# Generate CA certificate (10 years)
openssl req -new -x509 -days 3650 \
    -key /mnt/nas/configs/ca/private/ca.key \
    -out /mnt/nas/configs/ca/certs/ca.crt \
    -subj "/O=Home Automation/CN=Home Local CA"

echo "CA created: /mnt/nas/configs/ca/certs/ca.crt"
```

### Issue a certificate for Home Assistant

```bash
# Generate HA private key and CSR
openssl genrsa -out /ssl/privkey.pem 2048
openssl req -new \
    -key /ssl/privkey.pem \
    -out /tmp/ha.csr \
    -subj "/CN=homeassistant.home.local"

# Create extension file
cat > /tmp/ha.ext << 'EOF'
subjectAltName=IP:192.168.20.101,DNS:homeassistant.home.local
keyUsage=digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth
EOF

# Sign with local CA
openssl x509 -req -days 3650 \
    -in /tmp/ha.csr \
    -CA /mnt/nas/configs/ca/certs/ca.crt \
    -CAkey /mnt/nas/configs/ca/private/ca.key \
    -CAcreateserial \
    -out /ssl/fullchain.pem \
    -extfile /tmp/ha.ext

echo "HA cert issued: /ssl/fullchain.pem"
```

### Configure HA to use the cert

Same as Option A - update `configuration.yaml` `http:` block with the cert paths, restart HA.

### Issue a certificate for Mosquitto MQTT

Use this same CA for Mosquitto MQTT TLS certificates and client trust chains.

### Live Mosquitto add-on state

The Home Assistant Mosquitto add-on uses these certificate files from `/ssl`:

```yaml
certfile: fullchain.pem
keyfile: privkey.pem
require_certificate: false
customize:
  active: false
```

With those files present, restarting the add-on enables TLS listeners on
`8883` and `8884` while keeping the non-TLS listeners on `1883` and `1884`
until the staged migration is complete.

Validation completed on 2026-05-08:

```bash
mosquitto_sub -h 192.168.20.101 -p 8883 --cafile /ssl/ca.crt \
  -u mqtt -P '<mqtt-password>' -t '<test-topic>' -C 1

mosquitto_pub -h 192.168.20.101 -p 8883 --cafile /ssl/ca.crt \
  -u mqtt -P '<mqtt-password>' -t '<test-topic>' -m TLS_OK
```

Result: authenticated TLS publish/subscribe succeeded.

---

## Option C - Let's Encrypt with DuckDNS (real cert, no browser warning)

Requires a domain name and internet access from HA. Uses the DuckDNS add-on to get a free subdomain and auto-renewing Let's Encrypt certificate.

### Step 1 - Register a DuckDNS subdomain

Go to `https://www.duckdns.org/` and register. Note:
- Your subdomain: `yourname.duckdns.org`
- Your DuckDNS token

### Step 2 - Install DuckDNS add-on in HA

`Settings ? Add-ons ? Add-on Store ? search DuckDNS`

Configure:
```yaml
lets_encrypt:
  accept_terms: true
  certfile: fullchain.pem
  keyfile: privkey.pem
domains:
  - yourname.duckdns.org
token: your-duckdns-token
aliases: []
```

Start the add-on. It will:
1. Point `yourname.duckdns.org` to your public IP
2. Request a Let's Encrypt certificate via DNS challenge
3. Place the cert in `/ssl/fullchain.pem` and `/ssl/privkey.pem`
4. Auto-renew every 60 days

### Step 3 - Configure HA with the cert

```yaml
http:
  ssl_certificate: /ssl/fullchain.pem
  ssl_key: /ssl/privkey.pem
  server_host: 0.0.0.0
  server_port: 8123
  # If behind a reverse proxy, add:
  # use_x_forwarded_for: true
  # trusted_proxies:
  #   - 127.0.0.1
```

Restart HA. Access via `https://yourname.duckdns.org:8123`.

### Step 4 - Update VPN client config

Add `yourname.duckdns.org` as the `external_url` in `secrets.yaml`:
```yaml
external_url: https://yourname.duckdns.org:8123
```

This allows the HA mobile app to connect using the domain when on VPN.

---

## Updating HA configuration.yaml for HTTPS

After enabling any cert, the live `http:` block should look like:

```yaml
http:
  ssl_certificate: /ssl/fullchain.pem
  ssl_key: /ssl/privkey.pem
  server_host: 0.0.0.0
  server_port: 8123
```

And `internal_url` in the `homeassistant:` block should use `https://`.
Set `external_url` only after the remote URL is known and tested:

```yaml
homeassistant:
  internal_url: https://192.168.20.101:8123
  # external_url: https://yourname.duckdns.org:8123
```

---

## Certificate renewal reminder

| Option | Renewal |
|---|---|
| Self-signed (10 year) | Manual - set a calendar reminder for year 9 |
| Local CA (10 year) | Manual - same |
| Let's Encrypt (DuckDNS add-on) | Automatic - add-on handles it |

---

## Choosing an option

| Situation | Recommended |
|---|---|
| VPN-only access, no external domain | Option A (self-signed) |
| Want MQTT TLS too, no external domain | Option B (local CA) |
| Want proper cert + mobile app access | Option C (Let's Encrypt + DuckDNS) |
