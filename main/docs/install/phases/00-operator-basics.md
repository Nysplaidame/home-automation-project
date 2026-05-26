---
title: Phase 00 - Operator Basics
description: Safety, inventory, assumptions, and beginner operating rules before installation
tags: [install, phase, basics]
created: 2026-05-24
modified: 2026-05-24
type: install-guide
status: active
---

# Phase 00 - Operator Basics

## Purpose

Prepare the person, workstation, hardware list, and safety rules before any live
device is changed. This phase prevents the common rebuild failure where commands
are correct but run on the wrong host or with missing secrets.

## Runs on

Admin laptop on a trusted local network.

## Prerequisites

- Repository available locally.
- Admin laptop has Git, SSH, a browser, and a text editor.
- Password manager available for secret values.
- Hardware list reviewed in `README.md` and `bill-of-materials/`.

## Inputs

- `<ADMIN_SSH_PUBLIC_KEY>`
- Password manager vault location
- Hardware serials and MAC addresses as they become available

## Commands

Run on: Admin laptop.

```powershell
git status --short
git ls-files | Select-String -Pattern '^[A-Z]ain/' | Measure-Object
git ls-files | Select-String -Pattern '^main/' | Measure-Object
```

## Explanation

The first command checks for local work. The next two commands verify that Git
uses lowercase `main/` as the canonical active project path.

## Expected result

- You understand where every later command will run.
- Git reports no tracked uppercase active-project paths.
- You know where secrets will be recorded outside Git.

## Validation

Run on: Admin laptop.

```powershell
ssh -V
git --version
```

## Failure recovery

- If `ssh` is missing, install or enable the Windows OpenSSH client.
- If `git status` shows unexpected changes, stop and inspect before continuing.
- If tracked uppercase active-project paths appear, fix repository casing before adding new docs.

## Completion checklist

- [ ] Admin laptop can run Git and SSH.
- [ ] Password manager is ready.
- [ ] Hardware inventory has been reviewed.
- [ ] You can explain the command location rule in `reference/command-location-legend.md`.
