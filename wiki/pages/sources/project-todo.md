---
title: "Project Task List"
category: source
tags: [tasks, implementation, phases, todo]
created: 2026-04-07
updated: 2026-05-31
status: stable
---

# Source: Project Task List

**Original file:** `main/TO-DO.md`
**Date ingested:** 2026-04-07; audited against May 31 task list on 2026-05-31
**Type:** task list (living document)

## Summary

Full implementation task list organised across project phases and operational
next steps. The router, Proxmox, Home Assistant, docker-host, Tailscale,
monitoring stack, Tier 1 docker-host apps, ntfy, Watchtower monitor-only,
Grafana dashboards, and several exporters are live or pre-flight live. OMV,
Frigate application state, and VentSys hardware/entities remain unbuilt unless
explicitly revalidated.

## Key Takeaways

- **Planning baseline:** Treat OMV, Frigate app state, and VentSys hardware entities as unbuilt
- **Operational follow-up:** Apply the HA monitoring Grafana/Kuma direct-link snippet through the HA UI
- **Operational follow-up:** Add the monitoring VM Tailscale host route and
  routed UFW allowances so mobile clients can reach Grafana and Uptime Kuma
- **Operational follow-up:** Re-export/recreate `Proxmox Resource Overview`
  with explicit metric labels for bare percentage panels
- **Update governance:** Schedule a controlled docker-host patch window for Docker engine/component and kernel package candidates
- **Phase 3 (VentSys):** 17 ESP32 boards to flash and adopt in ESPHome; sensors still to be purchased
- **Phase 5 (CCTV):** Camera models TBD; RTSP URLs are placeholders
- **Phase 6 (Security):** MQTT TLS migration, HTTPS on HA, extending Fail2ban beyond docker-host, IDS/IPS baseline observation, WireGuard DDNS only if fallback endpoint churn matters
- **Ongoing:** Monthly backup health check; update MAC addresses in DHCP config when hardware arrives
- ESPHome device YAMLs for all 17 boards exist in `configs/esphome/`; only flashing remains

## Entities Mentioned

[[entities/gl-mt6000]], [[entities/proxmox]], [[entities/home-assistant]], [[entities/frigate]], [[entities/bambuddy]], [[entities/ventsys]], [[entities/esphome]], [[entities/openmediavault-nas]]

## Concepts Mentioned

[[concepts/vlan-segmentation]], [[concepts/mqtt-tls]]

## Contradictions / Updates

The old April source summary is superseded by the May 31 audit above. Current
canonical docs intentionally park OMV, Frigate app state, and VentSys hardware
entities until explicit live revalidation.
