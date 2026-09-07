---
title: "Project Task List"
category: source
tags: [tasks, implementation, phases, todo]
created: 2026-04-07
updated: 2026-09-07
status: stable
---

# Source: Project Task List

**Original file:** `main/TO-DO.md`
**Date ingested:** 2026-04-07; refreshed against the canonical task list on 2026-09-05
**Type:** task list (living document)

## Summary

Full implementation task list organised across project phases and operational
next steps. The router, Proxmox, Home Assistant, docker-host, Tailscale,
monitoring stack, Tier 1 docker-host apps, ntfy, Watchtower monitor-only,
Grafana dashboards, and several exporters are live or pre-flight live. OMV,
Frigate and the household-service foundations are deployed; the cameras are
currently disconnected, while the P1S and VentSys hardware remain uncommissioned.

On 2026-09-05, the task list linked the proposed
[[household-workshop-operations-roadmap|Household, Workshop and Operations
Product Roadmap]]. It sequences read-only operational evidence, a daily
household view, diagnostics/recovery evidence, food workflows, workshop
inventory and VentSys commissioning while preserving the established owners of
live household and safety state.

## Key Takeaways

- **Physical integration:** The cameras are currently disconnected; P1S setup
  and VentSys hardware adoption remain open despite the live service foundations.
- **Operational follow-up:** Apply the HA monitoring Grafana/Kuma direct-link snippet through the HA UI
- **Operational follow-up:** Add the monitoring VM Tailscale host route and
  routed UFW allowances so mobile clients can reach Grafana and Uptime Kuma
- **Operational follow-up:** Approve/retest the monitoring VM host route in
  Tailscale admin if mobile clients still cannot reach Grafana/Kuma
- **Update governance:** Schedule a controlled docker-host patch window for Docker engine/component and kernel package candidates
- **Phase 3 (VentSys):** 17 ESP32 boards to flash and adopt in ESPHome; sensors still to be purchased
- **Phase 5 (CCTV):** Three ANNKE cameras were proven and are currently disconnected; fourth-camera selection and reconnection acceptance remain open.
- **Phase 6 (Security):** HA HTTPS is live. VM102/VM103 Fail2ban are confirmed active; CT114 APT access and its Fail2ban rollout remain open. Proxmox historical rollout and OMV status require current evidence.
- **Ongoing:** Monthly backup health check; update MAC addresses in DHCP config when hardware arrives
- ESPHome device YAMLs for all 17 boards exist in `configs/esphome/`; only flashing remains
- **Troubleshooting:** The read-only dashboard is staged on management-only
  port `8094`; real Proxmox backup-snapshot acceptance and any DNS/Homepage
  exposure remain open
- **Product roadmap:** Start with a versioned read-only evidence contract;
  daily household, workshop and physical-integration features follow their
  respective data and hardware acceptance gates.

## Entities Mentioned

[[entities/gl-mt6000]], [[entities/proxmox]], [[entities/home-assistant]], [[entities/frigate]], [[entities/bambuddy]], [[entities/ventsys]], [[entities/esphome]], [[entities/openmediavault-nas]], [[entities/troubleshooting-dashboard]]

## Concepts Mentioned

[[concepts/vlan-segmentation]], [[concepts/mqtt-tls]]

## Contradictions / Updates

The old April source summary is superseded by current canonical state. OMV and
Frigate service foundations are deployed, but their physical-camera and safety
hardware follow-ups remain explicitly gated.

## September7 reconciliation

The canonical audit refreshed reachable-host evidence and recovered missing branch sources. Watchtower is monitor-only but ntfy delivery fails; CT114 package access fails with stale June metadata. Proxmox guest backups and OMV SMART are not freshly verified because workstation SSH access is denied. The [[home-operations-workbench]] accepts saved Windows/Proxmox health JSON with freshness safeguards. Recovery tabletop documentation is paper review, not live-drill acceptance.
