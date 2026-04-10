---
title: "MQTT TLS with Local Certificate Authority"
category: concept
tags: [mqtt, tls, security, certificates, mosquitto]
created: 2026-04-07
updated: 2026-04-07
sources: [ventsys-technical-specs, ventsys-implementation-roadmap, troubleshooting-reference]
status: stable
---

# MQTT TLS with Local Certificate Authority

## Definition

MQTT TLS replaces plaintext MQTT (port 1883) with TLS-encrypted MQTT (port 8883), using a self-hosted Certificate Authority (CA) on Home Assistant to issue and validate all certificates. No internet dependency at any stage — certificates are generated on HA and embedded in ESPHome firmware at flash time.

## Relevance to This Project

All 17 VentSys ESP32 devices communicate via MQTT. Without TLS, messages are readable by any device on VLAN 50. Implementing MQTT TLS is Phase 6 (security hardening) of the project deployment plan.

## CA Architecture

```
/config/ssl/ca/
├── certs/
│   ├── ca-cert.pem          ← Root CA (10-year validity)
│   ├── 192.168.20.101-cert.pem  ← MQTT broker cert
│   └── <device>-cert.pem    ← Per-device certs (3-year validity)
├── private/
│   ├── ca-key.pem           ← Root CA private key (chmod 700)
│   └── <device>-key.pem
└── openssl.cnf
```

## Certificate Naming Rule

**Critical:** Certificate CN must exactly match the ESPHome `device_name` (= mDNS hostname). Mismatch = TLS validation failure.

Canonical device names (from `dhcp-config.conf`):
- `ventsys-main-fan` (192.168.50.21)
- `ventsys-sla-print-valve` (192.168.50.56)
- `ventsys-fdm-print-valve` (192.168.50.55)
- `ventsys-booth-sensor` (192.168.50.33)
- `enc-fdm-sensors` (192.168.50.31)
- `enc-sla-sensors` (192.168.50.32)

## Mosquitto TLS Config (key settings)

```conf
listener 8883
cafile /mosquitto/config/certs/ca-cert.pem
certfile /mosquitto/config/certs/server.crt
keyfile /mosquitto/config/certs/server.key
require_certificate false      # password + TLS, no client certs
tls_version tlsv1.2
allow_anonymous false
```

## ESPHome Integration

The CA certificate is embedded directly in each device's YAML at flash time:
```yaml
mqtt:
  broker: 192.168.20.101
  port: 8883
  ca_certificate: |
    -----BEGIN CERTIFICATE-----
    # ca-cert.pem content pasted here
    -----END CERTIFICATE-----
```

## Firewall Change

- After TLS migration: remove the temporary 1883 rule, keep only 8883 rule
- Explicit block on 1883: `Block IoT Plain MQTT` rule in `firewall-config.conf`
- OpenWrt NTP on port 123 must be open from VLAN 50 (for ESP32 time sync)

## Certificate Lifecycle

- Root CA: 10 years (low maintenance)
- Device certs: 3 years (renew 6 months before expiry)
- Renewal distribution: via MQTT publish to `ventsys/system/certificate/<device>/renewal`
- HA monitors cert expiry via template sensor — alerts when < 60 days remain

## Implementation Timeline

9-week plan — see [[sources/ventsys-implementation-roadmap]]:
1. Wks 1–2: OpenWrt NTP + CA deployment
2. Wk 3: Mosquitto TLS on 8883
3. Wks 4–5: Flash all devices with TLS certs
4. Wk 6: HA + Node-RED updated to TLS
5. Wks 7–8: Automated certificate renewal
6. Wk 9: Full validation

## Key Entities Using This Concept

- [[entities/mosquitto-mqtt]]
- [[entities/ventsys]]
- [[entities/esphome]]
- [[entities/home-assistant]]

## Sources

- [[sources/ventsys-technical-specs]]
- [[sources/ventsys-implementation-roadmap]]
