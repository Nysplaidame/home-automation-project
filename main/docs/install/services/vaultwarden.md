---
title: Vaultwarden Install Manual
description: Live internal password vault with HTTPS, restore proof, and gated owner onboarding
tags: [install, docker-host, vaultwarden, tier3]
created: 2026-05-24
modified: 2026-07-29
type: install-guide
status: live-onboarding-gated
---

# Vaultwarden Install Manual

## Purpose

Operate the live internal Vaultwarden service without weakening its HTTPS,
backup, recovery or account-enrolment boundaries.

## Runs on

docker-host at `192.168.20.102`; production access is only
`https://vault.home.local`.

## Live deployment

Follow the implementation design and gates in
[[docs/procedures/household-services-implementation-plan|Household Services
Implementation Plan]]. Vaultwarden `1.36.0` is live under
`/opt/stacks/vaultwarden` with persistent `/data`, explicit Docker subnet
`10.240.30.0/24`, and a raw listener bound only to `127.0.0.1:8222`. The fixed
Nginx proxy terminates the dedicated local-CA certificate for
`vault.home.local`, adds HSTS and deliberately permits no iframe embedding.
`SIGNUPS_ALLOWED=false`; the admin endpoint is disabled because `ADMIN_TOKEN`
is blank.

## Prerequisites

- Deploy the staged OpenWrt DNS alias for `vault.home.local` and validate it
  from normal local and Tailscale clients.
- Keep the fixed proxy and source-scoped firewall in place.
- Preserve the completed SQLite-consistent NAS backup and isolated restore
  evidence.
- Before importing real credentials, complete owner onboarding, 2FA,
  recovery-code storage and owner-controlled emergency-access policy.

## Inputs

- No secret input is stored in Git. The production admin endpoint remains
  disabled unless a separately approved administration workflow is adopted.

## Commands

Run from the repository checkout:

```powershell
scp main/configs/docker-host/stacks/vaultwarden/docker-compose.yml docker-host-lan:/tmp/vaultwarden-compose.yml
ssh docker-host-lan 'sudo install -d -m 0750 /opt/stacks/vaultwarden/data; sudo install -o root -g root -m 0644 /tmp/vaultwarden-compose.yml /opt/stacks/vaultwarden/docker-compose.yml; rm -f /tmp/vaultwarden-compose.yml'
```

Validate and reconcile only after comparing live `.env` and data paths; never
overwrite them from Git:

```sh
cd /opt/stacks/vaultwarden
docker compose up -d
docker compose ps
```

## Explanation

The tracked Compose file is the rebuild shape. Live `.env`, SQLite data,
attachments, keys and recovery material remain host-only.

## Expected result

Vaultwarden is internal-only, HTTPS-valid and restore-proven. It is not used for
primary passwords until owner onboarding and recovery policy are complete.

## Validation

Run on: docker-host over SSH.

```sh
cd /opt/stacks/vaultwarden && docker compose ps
```

## Backup

`docker-host-app-data-backup.sh` creates a SQLite-consistent staged database and
copies the complete data directory to dated OMV `backups/docker-host` runs.
Backup run `20260729T160804Z` passed a clean restore and a separate disposable-
account restore with integrity, exact-account-count and HTTP checks.

## Failure recovery

If any gate is unresolved, stop the service:

Run on: docker-host over SSH.

```sh
cd /opt/stacks/vaultwarden
docker compose down
```

## Completion checklist

- [x] Dedicated HTTPS certificate and fixed proxy proven.
- [x] Raw HTTP bound to loopback only.
- [x] Two isolated restore proofs passed.
- [x] Sign-ups and admin endpoint disabled.
- [ ] Live local and Tailscale DNS validated.
- [ ] Owner account created during a bounded enrolment window.
- [ ] 2FA, recovery-code storage and emergency access completed.
