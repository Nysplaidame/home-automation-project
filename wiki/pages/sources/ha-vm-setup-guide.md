---
title: "Home Assistant VM Setup Guide"
category: source
tags: [home-assistant, setup, mqtt, esphome, packages]
created: 2026-04-07
updated: 2026-04-07
status: stable
---

# Source: Home Assistant VM Setup Guide

**Original file:** `scripts/setup/proxmox/ha_vm_setup_guide.md`
**Date ingested:** 2026-04-07
**Type:** setup guide

## Summary

8-phase guide for onboarding HAOS on VM 100 after the VM is created and the router is live. Covers initial wizard, static IP, add-on installation, package deployment, VentSys entity verification, Frigate integration via HACS, and security hardening.

## Key Takeaways

- **Prerequisite:** router cutover complete; HA reachable at `http://192.168.20.101:8123`
- **Add-ons in order:** Mosquitto → File Editor → Terminal & SSH → ESPHome (optional: Samba, HACS)
- **MQTT:** start on port 1883 (pre-TLS); switch to 8883 after `ventsys_tls_implementation_guide.md`
- **Packages:** `configuration.yaml` already has `packages: !include_dir_named packages` — do NOT add it again or it silently overwrites the entire `homeassistant:` block (FIX #26)
- **`ventsys_ha_optional.yaml` — DO NOT copy yet:** has "DO NOT LOAD YET" header; only copy after all sensor boards are deployed and baro_pressure entities confirmed
- **VentSys dashboard:** copy `ventilation_v9k.html` to `/config/www/ventsys-dashboard.html`; set Long-Lived Token in `HA_CONFIG.token`
- **Frigate integration port:** 8971 for Frigate 0.14+; 5000 for older versions — verify before configuring
- **Trusted networks:** optionally bypass login from VLAN 20 subnet — only safe if VLAN isolation is confirmed
- **Backups:** daily at 03:00, 7 copies local, then switch target to NAS (VLAN 40) once available

## Add-on Reference

| Add-on | Port | Required |
|---|---|---|
| Mosquitto | 1883 / 8883 (TLS) | Yes |
| File Editor | — | Yes |
| Terminal & SSH | 22 | Yes |
| ESPHome | 6052 | Yes |
| Samba | 445 | Optional |
| HACS | — | Optional (needed for Frigate Card) |

## Entities Mentioned

[[entities/home-assistant]], [[entities/mosquitto-mqtt]], [[entities/esphome]], [[entities/frigate]], [[entities/ventsys]]

## Concepts Mentioned

[[concepts/mqtt-tls]]

## Contradictions / Updates

MQTT Integration port should start at 1883 for initial bring-up — not 8883. Switch to TLS only after testing confirms plain MQTT works.
