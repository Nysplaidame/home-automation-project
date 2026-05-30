---
title: "MQTT TLS with Local Certificate Authority"
category: concept
tags: [mqtt, tls, security, certificates, mosquitto]
created: 2026-04-07
updated: 2026-05-30
sources: [ventsys-technical-specs, ventsys-implementation-roadmap, troubleshooting-reference]
status: stable
---

# MQTT TLS with Local Certificate Authority

## Definition

MQTT TLS replaces plaintext MQTT (port `1883`) with TLS-encrypted MQTT (port `8883`), using a self-hosted Certificate Authority (CA) on Home Assistant to validate broker certificates for local clients. No internet dependency is required for runtime validation; certificates are generated and stored locally.

## Relevance to This Project

MQTT carries VentSys control/state, Bambuddy status, and future Frigate/automation messages. TLS matters because VLAN 50 devices are intentionally restricted and should not depend on plaintext credentials or control messages long-term.

The project is TLS-oriented now: Mosquitto TLS on `8883` is live and Bambuddy
has migrated successfully. Plain MQTT `1883` is deprecated, and canonical
router policy should not reintroduce a VentSys `1883` exception. Remaining
Frigate/VentSys clients should move onto `8883` before they are treated as live.

## Current Migration State

| Area | State |
|---|---|
| Mosquitto listener `8883` | ✅ Live and verified |
| CA-based TLS pub/sub test | ✅ Verified with `/ssl/ca.crt` |
| Bambuddy → Mosquitto | ✅ Migrated to `8883`, TLSv1.3 observed |
| Mosquitto listener `1883` | Deprecated bootstrap/legacy path; not a router-policy dependency |
| Frigate MQTT path | ✅ TLS path verified; app still not live |
| VentSys devices | ⏳ TLS-ready rollout blocked until `mqtt_ca_cert` exists in ESPHome secrets and hardware is adopted/revalidated |
| Temporary valve-1 firewall rule | ✅ No live/source valve-specific `1883` exception found in the 2026-05-28 parity check |

## CA / Certificate Placement

The live HA-side CA certificate is used for TLS validation. For ESPHome, the next documented step is to copy the CA certificate into both repo and HA-side ESPHome `secrets.yaml` as `mqtt_ca_cert`, then reference it from TLS YAMLs.

```yaml
mqtt_ca_cert: |
  -----BEGIN CERTIFICATE-----
  ...
  -----END CERTIFICATE-----
```

ESPHome YAML should then use the project-supported TLS form, e.g. `port: 8883` plus `certificate_authority: !secret mqtt_ca_cert` where the device YAML expects it.

## Certificate Naming Rule

For per-device certificate designs, certificate CN must exactly match the ESPHome `device_name` / mDNS hostname. A mismatch causes TLS validation failure. The current live migration path uses username/password plus broker TLS validation rather than requiring client certificates.

## Mosquitto TLS Config (design settings)

```conf
listener 8883
cafile /mosquitto/config/certs/ca-cert.pem
certfile /mosquitto/config/certs/server.crt
keyfile /mosquitto/config/certs/server.key
require_certificate false      # password + TLS, no client certs
tls_version tlsv1.2
allow_anonymous false
```

## Firewall Change

- Keep `8883` allowed from approved clients to Home Assistant/Mosquitto.
- Do not add broad or source-specific VentSys `1883` router access.
- OpenWrt NTP on UDP/123 must remain available from VLAN 50 for ESP32 time sync.

## Next Migration Actions

1. Add `mqtt_ca_cert` to both repo and HA-side ESPHome `secrets.yaml`.
2. Keep VentSys device YAMLs on `8883` with `certificate_authority: !secret mqtt_ca_cert` before treating them as live.
3. Flash/adopt remaining VentSys devices on the TLS path.
4. Confirm MQTT TLS works with `mosquitto_sub`/`mosquitto_pub` before enabling dependent HA automations.

## Key Entities Using This Concept

- [[entities/mosquitto-mqtt]]
- [[entities/ventsys]]
- [[entities/esphome]]
- [[entities/home-assistant]]
- [[entities/bambuddy]]

## Sources

- [[sources/ventsys-technical-specs]]
- [[sources/ventsys-implementation-roadmap]]
- Current canonical project docs: `main/TO-DO.md`, `main/HANDOFF-2026-05-28-preflight-next.md`.
