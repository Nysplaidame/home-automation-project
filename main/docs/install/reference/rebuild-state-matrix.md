---
title: Rebuild State Matrix
description: Standard lifecycle states for every host, service, and phase
tags: [install, rebuild, state]
created: 2026-05-24
modified: 2026-05-24
type: reference
status: active
---

# Rebuild State Matrix

| State | Meaning | Required proof |
|---|---|---|
| Blank | Hardware or VM exists but no project configuration is applied | Inventory record only |
| Prepared | OS/network baseline is ready, backups or restore point exist | IP reachable, admin access works, restore path known |
| Installed | Packages or services are installed | Version command, package list, or container image present |
| Configured | Project-specific settings are applied | Config file, UI setting, or Compose stack present |
| Validated | The component works in isolation and over intended network paths | Validation commands pass |
| Live | The component is depended on by another live component or user workflow | Monitoring, backup, and rollback notes exist |

No service may be considered `live` until it has:

- a backup or restore note,
- an access-control note,
- a monitoring or health-check note,
- a troubleshooting entry,
- and a recorded owner decision for any unresolved risk gate.
