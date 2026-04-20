---
title: "Home Assistant configuration.yaml"
category: source
tags: [home-assistant, config, mqtt, recorder, http]
created: 2026-04-07
updated: 2026-04-07
status: stable
---

# Source: Home Assistant configuration.yaml

**Original file:** `configs/home-assistant/configuration.yaml`
**Date ingested:** 2026-04-07
**Type:** configuration file

## Summary

The HA core config file. Sets locale (UK), enables packages, configures HTTP security, logger levels, recorder retention, and includes `automations.yaml`. Notable for what it does NOT include — `scripts.yaml` and `scenes.yaml` files don't exist; all scripts are inline in package files.

## Key Takeaways

- **Locale:** Europe/London, metric, GBP, GB — confirms UK-based project throughout
- **Packages directive:** `packages: !include_dir_named packages` — do NOT add a second `homeassistant:` block; it silently overwrites everything under it (FIX #26 in setup guide)
- **HTTP security:** `ip_ban_enabled: true`, ban after 5 failed login attempts; banned IPs in `/config/ip_bans.yaml`
- **Logger:** default `warning`; mqtt, esphome, frigate components set to `info`
- **Recorder:** 30-day retention, 30s commit interval; excludes automations, scripts, signal strength sensors
- **`history:` and `logbook:` keys deprecated** since HA 2024.6 — they work but log deprecation warnings on every startup; retention managed by `recorder:` instead (FIX #30)
- **scripts.yaml / scenes.yaml don't exist** — all scripts are inside package files; including them causes hard startup error (FIX #2)
- **Integrations managed via UI:** MQTT at 192.168.20.101:1883 (switch to 8883 after TLS); ESPHome auto-discovers VLAN 50 devices; Frigate at `http://192.168.30.20:8971`
- **`external_url`:** pulled from secrets.yaml — used for VPN/remote access URL

## Secrets Required

```yaml
home_latitude: 51.xxxx
home_longitude: -0.xxxx
home_elevation: 10
external_url: https://your-vpn-or-domain
mqtt_username: mqtt
mqtt_password: your-mqtt-password
```

## Entities Mentioned

[[entities/home-assistant]], [[entities/mosquitto-mqtt]], [[entities/esphome]], [[entities/frigate]]

## Concepts Mentioned

[[concepts/mqtt-tls]]

## Contradictions / Updates

`history:` and `logbook:` keys are still present as comments for reference but should not be uncommented — they are deprecated. Recorder handles filtering.
