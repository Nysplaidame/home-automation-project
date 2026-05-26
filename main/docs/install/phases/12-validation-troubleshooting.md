---
title: Phase 12 - Validation Troubleshooting
description: End-to-end validation and failure diagnosis after rebuild
tags: [install, validation, troubleshooting]
created: 2026-05-24
modified: 2026-05-24
type: install-guide
status: active
---

# Phase 12 - Validation Troubleshooting

## Purpose

Prove that the full rebuilt system works end to end and that failures have a
known diagnostic path.

## Runs on

Admin laptop, plus the host named in each validation step.

## Prerequisites

- Prior phases complete or explicitly marked blocked.
- Service matrix and access matrix updated.
- Troubleshooting reference read.

## Inputs

Service-specific credentials from the secrets ledger.

## Commands

Run on: Admin laptop.

```powershell
Test-Connection 192.168.10.1 -Count 2
Test-Connection 192.168.10.10 -Count 2
Test-Connection 192.168.20.101 -Count 2
Test-Connection 192.168.20.102 -Count 2
Test-Connection 192.168.40.50 -Count 2
```

Run on: docker-host over SSH.

```sh
docker ps
tailscale status
```

Run on: Admin laptop from repository root.

```powershell
cd main
python tools/router-deploy/lint.py
python tools/router-deploy/compile.py --profile first-flight
```

## Explanation

Validation checks both live behavior and source-of-truth health. If source docs
and configs cannot validate, the rebuild is not reproducible.

## Expected result

- Required hosts respond.
- Expected Docker stacks are running.
- Tailscale advertises only approved host routes.
- Router-deploy validates.
- Troubleshooting reference has an entry for every live Tier 1 service.

## Failure recovery

- Diagnose from the nearest layer: power, link, IP, DNS, firewall, service, auth.
- Do not bypass segmentation to “make it work”; document the narrow rule needed.
- If a service is down and no runbook exists, write the runbook before relying on it.

## Completion checklist

- [ ] End-to-end ping checks pass where intended.
- [ ] DNS checks pass.
- [ ] Tailscale host routes work.
- [ ] Router-deploy validation passes.
- [ ] Service matrix and access matrix match the rebuilt system.
