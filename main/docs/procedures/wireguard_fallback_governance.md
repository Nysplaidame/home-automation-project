---
title: WireGuard Fallback Governance
description: Activation policy, scope limits, and rollback rules for dormant OpenWrt WireGuard fallback
tags: [wireguard, remote-access, governance, fallback, security]
created: 2026-05-28
modified: 2026-05-28
type: procedure
status: active
---

# WireGuard Fallback Governance

WireGuard on OpenWrt is a contingency path, not the daily remote-access layer.
Daily remote access remains Tailscale host-route access through docker-host.

## Current baseline

- `wg0` is configured but disabled/down by default.
- No routine client rollout is required while Tailscale remains healthy.
- Allowed routes stay split-tunnel and host-scoped (`HA`, `OMV`, `LAN`, `DMZ`,
  and VPN subnet only).

## Activation criteria

Activate WireGuard fallback only when one of these is true:

1. Tailscale is unavailable for expected operator tasks and the outage is not a
   short-lived transient.
2. A deliberate change freezes Tailscale usage (policy, account, or provider issue).
3. A planned resilience drill is being run with explicit start and end times.

## Guardrails

- Do not advertise or grant broad Management, NVR, Printers, IoT, or full
  Storage VLAN access through WireGuard.
- Keep OMV access as host-route scope (`192.168.40.50/32`), not VLAN 40 wide.
- Do not enable full-tunnel internet routing (`0.0.0.0/0`) as a default profile.
- Keep WireGuard credentials/client files out of the repo.

## Activation checklist

1. Confirm Tailscale issue or planned drill context.
2. Enable `wg0` and verify interface up state.
3. Validate only intended fallback routes from one test client.
4. Confirm blocked-path expectations still hold (Management/NVR/Printers/IoT).
5. Record activation timestamp and reason in the current handoff file.

## Deactivation checklist

1. Confirm Tailscale daily path is healthy again.
2. Disconnect test client sessions.
3. Disable `wg0` and verify interface down state.
4. Record deactivation timestamp and outcome in the current handoff file.

## DDNS governance

- Enable WireGuard DDNS only if public IP churn causes repeated operational
  breakage.
- If DDNS is enabled, document provider, hostname, update mechanism, and
  secret handling in `docs/decisions/` and `docs/reference/access-matrix.md`.
