---
title: "Tailscale Remote Access"
category: concept
tags: [tailscale, vpn, remote-access, subnet-router]
created: 2026-05-23
updated: 2026-10-11
sources: [project-readme, project-todo]
status: active
---

# Tailscale Remote Access

## Definition

Tailscale is the project's daily remote-access layer. docker-host joins the
tailnet and advertises host routes only, not broad VLAN subnets.

## Relevance to This Project

Daily remote access should use docker-host's Tailscale node identity/MagicDNS
for docker-host services, plus narrow approved host routes:

- `192.168.20.101/32` for Home Assistant
- `192.168.20.104/32` for [[entities/llm-host]] (Voice Mixer `7860`, Open WebUI `3002`; added 2026-10-11)
- `192.168.30.20/32` for Frigate HTTPS `8971` only
- `192.168.40.50/32` for OMV
- `192.168.60.10/32` for Grafana and Uptime Kuma only

All five routes were approved and active on 2026-10-11. Routed traffic is SNATed
to docker-host `192.168.20.102`, so destination hosts scope access by that
source (e.g. CT 114 `DOCKER-USER`), and the tailnet policy is device-scoped.

Off-LAN validation passed on 2026-05-28 for docker-host and routed Home
Assistant/OMV host paths.

As of the 2026-05-31 mobile-access diagnosis, Home Assistant works over
Tailscale but Grafana and Uptime Kuma needed a new monitoring VM route.
docker-host now advertises the monitoring VM host route and has routed UFW
allowances for ports `3000` and `3001`; do not expose InfluxDB `8086` as part
of daily mobile access. Mobile clients may still need the new route approved in
Tailscale admin before it works off-LAN.

## Trade-offs / Considerations

- Simpler mobile access than maintaining WAN WireGuard endpoint changes.
- Requires persistent docker-host outbound connectivity.
- Does not replace OpenWrt firewall policy.
- Must not advertise Management, NVR, Printers, IoT, or broad Storage VLANs.
- Must not advertise the broad Monitoring VLAN; use only the monitoring VM host
  route when dashboard mobile access is intentionally allowed.
- WireGuard remains a dormant fallback, not a parallel daily-access default.

## Key Entities Using This Concept

- [[entities/docker-host]]
- [[entities/home-assistant]]
- [[entities/openmediavault-nas]]
- [[entities/monitoring-vm]]
- [[entities/gl-mt6000]]

## Sources

- Current canonical project decisions and reference docs in `main/docs/`.
