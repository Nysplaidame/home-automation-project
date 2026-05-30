---
title: Install Decision Gates
description: Required approvals before risky or unresolved services become live
tags: [install, decision-gates, security]
created: 2026-05-24
modified: 2026-05-28
type: reference
status: active
---

# Install Decision Gates

Decision gates prevent a draft install from silently becoming a risky live service.

## Gate levels

| Level | Meaning |
|---|---|
| Draft installable | Commands exist and can create a local/internal service |
| Deploy approved | Backup, auth, exposure, update, and rollback choices are accepted |
| Live | Service is monitored, backed up, and depended on |

## Required gates

| Service | Required before deploy approved |
|---|---|
| Vaultwarden | Backup/restore test, admin token storage, HTTPS/reverse proxy plan, account recovery plan |
| Portainer | Decide whether Docker socket exposure is acceptable; restrict to Management/Tailscale only |
| Watchtower monitor-only | Confirm monitor-only mode; no automatic updates |
| Automatic updates (global policy) | Keep disabled by default; require explicit approval, rollback path, and post-update verification plan before enabling |
| Local registry mirror | Confirm disk quota, cache location, and Docker daemon rollback path |
| Node-RED | Confirm HA native automations are insufficient; flow backup and credential secret defined |
| Scrypted | Confirm Docker placement is acceptable despite upstream preference for Proxmox on dedicated servers |
| ntfy | Decide internal-only versus public relay; define auth and topic policy |
| Actual Budget | Backup and access review because financial data is sensitive |
| Penetration testing pass | Confirm scope, authorized targets, time window, and remediation logging owner before active testing |

Do not remove a gate from a service manual unless the decision is recorded in
`docs/decisions/` or `TO-DO.md`.
