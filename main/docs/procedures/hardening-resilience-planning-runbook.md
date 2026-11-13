---
title: Hardening and resilience planning runbook
description: Non-destructive preparation for credential rotation and recovery drills
tags: [security, resilience, recovery, credentials]
created: 2026-09-18
type: procedure
status: planned
---

# Hardening and resilience planning runbook

This runbook prepares controlled hardening and resilience work. It does not
authorize a credential rotation, firewall change, reboot, restore, or outage.
Each live action needs its own maintenance window, target list, rollback, and
owner approval.

## Hardening inventory

Create a protected, non-Git operator inventory of the following without storing
secret values: owner, system, purpose, credential class, last rotation, dependent
systems, storage location, rotation order, validation method, revocation step,
and rollback. Cover OpenWrt, Proxmox, OMV, Home Assistant, Docker host,
Frigate, llm-host, monitoring, Tailscale, WireGuard, the local CA, service
accounts, API tokens, SSH keys, certificates, and password-manager records.

Rotate in dependency order: recovery/admin access first, service credentials
next, consumer credentials after their providers, then revoke the old value only
after named validation succeeds. Never place values, recovery codes, private
keys, tokens, or certificate material in this repository, terminal history, or
incident evidence.

## Resilience planning table

| Scenario | Trusted recovery route | Stop/ask gate |
|---|---|---|
| Router or Internet loss | Local management access and physical LAN recovery guidance | Do not reload network or change VLAN/firewall rules without a local operator |
| Proxmox or guest loss | OMV backup evidence, isolated restore procedure, console | No production guest replacement or ID reuse without owner confirmation |
| OMV loss | Local host storage, export/config recovery runbooks | Do not initialize disks, alter arrays, or run repair tools without an approved recovery plan |
| Docker-host app failure | Service runbook, scoped app-data backup, local console | Do not overwrite data volumes or recreate a database before checkpoint review |
| HA/Frigate/llm-host failure | Proxmox console, host-specific runbook, backups | No safety automation change or GPU mapping change during incident response |
| Monitoring/Tailscale/local CA failure | Direct local access and independent health signals | Do not widen exposure or bypass TLS validation as a permanent fix |
| Credential loss | Owner-approved password-manager recovery and break-glass record | Do not disable authentication or create untracked replacement accounts |

## Low-risk drill order

Start with read-only evidence collection and non-critical isolated restores.
Then use reversible dependency-loss simulations with an observer outside the
affected service. Mini PC, router, OMV, broad network, safety automation, and
credential-loss drills remain maintenance-window activities with an explicit
rollback owner.

For every drill record the objective, scope, starting evidence, operator,
observer, exact stop condition, outcome, recovery time, residual risk, and
canonical documentation updates. A successful archive check must never be
described as an application or full-system restore proof.

## Assistant evidence-retention policy

Default to 48-hour retention for structured assistant state, compact tool
summaries, performance timings, and redacted task outcomes. Exclude raw audio,
full prompts/tool dumps, credentials, private payloads, and unbounded verbose
logs. Enable additional diagnostic logging only for a time-bounded incident,
with owner, expiry, redaction review, and removal recorded.

## Related work

- [Backup strategy](../../scripts/backup/backup_strategy.md)
- [Update maintenance playbook](update_maintenance_playbook.md)
- [Current live state](../reference/current-live-state.md)
- [Access matrix](../reference/access-matrix.md)
