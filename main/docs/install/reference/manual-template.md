---
title: Install Manual Template
description: Required structure for beginner-safe phase and service manuals
tags: [install, template, documentation-standard]
created: 2026-05-24
modified: 2026-05-24
type: reference
status: active
---

# Install Manual Template

Every install manual in this suite must use this structure.

## Purpose

Explain what this component does and why the system needs it.

## Runs on

Name the exact command/UI context:

- Host or device name
- VLAN and IP address
- Shell, UI, or app context
- User account, such as `root`, `sudo user`, HA Terminal, or admin laptop

## Prerequisites

List prior phases, hardware, network state, packages, secrets, files, and backups.

## Inputs

List every placeholder and link to `secrets-placeholder-ledger.md`.

## Commands

Every command block must be preceded by a `Run on:` line.

## Explanation

Explain why each command group exists.

## Expected result

State the visible success condition.

## Validation

Provide commands or UI checks that prove the component works.

## Failure recovery

List likely failures and the safest rollback or diagnostic path.

## Completion checklist

Use checkboxes. The next phase may not start until all required checks pass.
