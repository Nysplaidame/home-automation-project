---
title: IDS IPS Progression Plan
description: Practical phased plan for host hardening, log-driven blocking, and optional network IDS/IPS
tags: [security, ids, ips, fail2ban, crowdsec, suricata, monitoring]
created: 2026-05-28
modified: 2026-07-31
type: procedure
status: active
---

# IDS IPS Progression Plan

This project should add IDS/IPS capability in layers, not by deploying a heavy
stack too early.

## Current state (2026-05-30)

- Central monitoring is live (Kuma, InfluxDB, Grafana, Telegraf).
- OpenWrt selective deny logging is live and forwarded.
- True network IDS and IPS are not deployed.
- Docker-host Fail2ban `sshd` baseline is deployed and exported into the `dockerhost` InfluxDB bucket.
- Frigate CT Fail2ban `sshd` baseline is deployed at `/etc/fail2ban/jail.d/frigate-nvr-sshd.local`.

Update (2026-07-31): the remaining applicable Linux hosts were enumerated and
each now has a canonical jail source plus a deployment/rollback procedure in
`docs/procedures/fail2ban_host_rollout.md`. Source is ready and not deployed for
the Proxmox host, monitoring VM 102, CT 114 `llm-host` and OMV. Home Assistant
OS, the OpenWrt router, the managed switch and the cameras are excluded with
written reasons in that procedure.

## Phase plan

### Phase A - host hardening first

1. Extend Fail2ban from docker-host/Frigate to any other Linux service host
   with meaningful auth surfaces. Execute through
   `docs/procedures/fail2ban_host_rollout.md`, one host per window.
2. Standardize jail policies and ban windows — the standard is now
   `bantime 1h`, `findtime 10m`, `maxretry 5`, `backend systemd`, with
   `banaction` matched to each host's live firewall backend.
3. Add monitoring signals for Fail2ban service health and active bans. The
   existing exporter tags only `jail`, so add a `host` tag or per-host buckets
   before a second host exports.

### Phase B - log-driven response evaluation

1. Evaluate CrowdSec only if recurring auth-abuse patterns are observed.
2. Keep scope narrow (high-value service logs first).
3. Require rollback notes before enabling automated remediation.

### Phase C - dedicated network IDS/IPS decision

1. Evaluate Suricata only on dedicated x86 capacity (not on GL-MT6000).
2. Define throughput target, false-positive tolerance, and maintenance owner.
3. Run IDS-only mode before any IPS/blocking mode.

### Phase D - scoped penetration testing readiness

1. Run a controlled internal pentest pass only after core hardening and update
   governance are stable.
2. Keep tests scoped to approved targets and maintenance windows.
3. Record findings, remediation owners, and retest evidence in project docs.

## Decision gates

- Do not deploy router-hosted heavyweight IDS/IPS.
- Do not enable auto-blocking without documented rollback path.
- Do not mark IDS/IPS as production until alerts, ownership, and update cadence
  are documented.

## Exit criteria

- Fail2ban deployed and monitored where applicable.
- At least one month of security-event baseline captured.
- Suricata/CrowdSec decision recorded as either approved-for-pilot or deferred.
