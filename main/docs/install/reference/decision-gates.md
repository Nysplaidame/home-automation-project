---
title: Install Decision Gates
description: Required approvals before risky or unresolved services become live
tags: [install, decision-gates, security]
created: 2026-05-24
modified: 2026-08-09
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
| Portainer | Accept root-equivalent Docker socket exposure; require loopback UI, private HTTPS, named admin, encrypted config backup, no-socket restore test, and full route rollback |
| Watchtower monitor-only | Confirm monitor-only mode; no automatic updates |
| Automatic updates (global policy) | Keep disabled by default; require explicit approval, rollback path, and post-update verification plan before enabling |
| Local registry mirror | Require measured benefit, quota/alert, trusted TLS, public-only upstream, one-client canary, validated Docker daemon config and direct-pull rollback |
| Node-RED | Confirm HA native automations are insufficient; require safe-mode/authenticated editor, no safety-critical flow, flow-plus-secret restore, and explicit promotion gate |
| Paperless-ngx | Confirm PostgreSQL/OCR/ingest layout, sensitive-document retention, named auth, internal HTTPS, exporter backup, isolated importer restore, and rollback before real documents |
| Scrypted | Confirm the feature is not already met by Frigate/HA; prefer a dedicated Proxmox guest, and approve camera, discovery, iGPU, recording, backup and rollback boundaries before install |
| ntfy | Decide internal-only versus public relay; define auth and topic policy |
| Actual Budget | Require loopback raw listener, approved HTTPS, password/E2EE recovery, UI export, stopped-data backup, isolated restore and digest rollback before real financial data |
| Local AI inference | Confirm 32 GB sizing, model class, HA exposure list, and performance test pass before calling live |
| Hermes Agent | Confirm advisory/tooling scope, tool allowlist, sandboxing, credentials, logging, and no safety-critical direct control |
| Future AI query apps | Define app-specific API, egress, storage, auth, monitoring, and firewall rules before deployment |
| Penetration testing pass | Confirm scope, authorized targets, time window, and remediation logging owner before active testing |

Do not remove a gate from a service manual unless the decision is recorded in
`docs/decisions/` or `TO-DO.md`.

Vaultwarden's deployment gate passed on 2026-07-29: the raw listener is
loopback-only, dedicated local-CA HTTPS and no-framing policy are live, and two
isolated SQLite restore proofs succeeded. Its account-recovery gate remains
open until live DNS, owner onboarding, 2FA, recovery-code storage and emergency
access are completed; do not import real credentials before then.
