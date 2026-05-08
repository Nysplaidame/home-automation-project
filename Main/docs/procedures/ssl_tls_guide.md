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

> For a home network accessed only via WireGuard, a self-signed certificate is sufficient. The browser warning is an inconvenience but not a security risk over an encrypted VPN. If you want a real cert (no warning), you need a domain name and use Let's Encrypt via the DuckDNS or NGINX Proxy Manager add-on.

## MQTT Transition Strategy

Current live state on 2026-05-08:

- HA / Mosquitto is still using `1883` as the active bootstrap path.
- `8883` is the target steady-state port for MQTT TLS.
- MQTT-backed integrations are still being introduced gradually, not all at once.

Because devices and entities will come online one by one, the migration should
be phased rather than a big-bang cutover.

### Staged plan

1. Keep `1883` available for bootstrap and early testing.
2. Prepare the CA, broker certificate, and Mosquitto TLS listener on `8883`.
3. Validate one client end-to-end on `8883` with cert trust enabled.
4. Move new integrations to `8883` individually as they are deployed.
5. Remove `1883` only after all real clients are off it.

### Client guidance during transition

- New integrations may use `1883` temporarily if the cert chain is not ready yet.
- Prefer moving each new client straight to `8883` once the CA and broker certs
  are in place.
- Do not leave a half-migrated undocumented state; every client should be clearly
  documented as either `bootstrap on 1883` or `steady-state on 8883`.

### Expected migration order

- Frigate
- Bambuddy, if it ultimately needs HA MQTT in practice
- Future ESPHome / VentSys devices
- Any later MQTT consumers

---

## Option A - Self-signed certificate (simplest)

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

The CA infrastructure was prepared on the router in Phase 8 (`/etc/ventsys/ca/`). You can also do this on the Pi NAS for persistence.

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

After enabling any cert, the `http:` block should look like:

```yaml
http:
  ssl_certificate: /ssl/fullchain.pem
  ssl_key: /ssl/privkey.pem
  server_host: 0.0.0.0
  server_port: 8123
```

And `internal_url` / `external_url` in the `homeassistant:` block should use `https://`:

```yaml
homeassistant:
  internal_url: https://192.168.20.101:8123
  external_url: https://yourname.duckdns.org:8123   # or your VPN IP
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
