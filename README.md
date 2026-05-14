---
title: Home Automation Project
description: Repository root — navigation guide
created: 2025-09-15
modified: 2026-05-08
---

# Home Automation Project

Fire safety ventilation, NVR surveillance, secure network architecture, and home automation for 3D printing operations.

**Repository:** https://github.com/Nysplaidame/home-automation-project

---

## Repository layout

```
home-automation-project/
├── main/               ← primary working tree (all active docs, configs, scripts)
│   ├── configs/        ← system configuration files (openwrt, esphome, ha, frigate, proxmox)
│   ├── docs/           ← decisions, procedures, diagrams, prompts, troubleshooting
│   ├── scripts/        ← setup guides and operational scripts
│   ├── tools/          ← router-deploy toolkit, playwright smoke tests
│   ├── ventsys/        ← VentSys ESPHome bundles and integration docs
│   ├── wiki/           ← LLM-maintained knowledge base (see wiki/CLAUDE.md)
│   ├── README.md       ← project overview and status (start here)
│   ├── PROJECT-INDEX.md← full documentation index
│   └── TO-DO.md        ← task list by phase
└── README.md           ← this file
```

**→ For everything project-related, go to [`main/`](main/).**

The root of this repo is the Obsidian vault wrapper. All active content lives under `main/`.

---

## Quick links

| What | Where |
|---|---|
| Project overview and current status | [`main/README.md`](main/README.md) |
| Full documentation index | [`main/PROJECT-INDEX.md`](main/PROJECT-INDEX.md) |
| Task list | [`main/TO-DO.md`](main/TO-DO.md) |
| Current session handoff | [`main/HANDOFF-2026-05-07-current.md`](main/HANDOFF-2026-05-07-current.md) |
| Router configs | [`main/configs/openwrt/`](main/configs/openwrt/) |
| ESPHome configs | [`main/configs/esphome/`](main/configs/esphome/) |
| VentSys bundles | [`main/ventsys/ventsys_bundle_updated/`](main/ventsys/ventsys_bundle_updated/) |
| Router deploy toolkit | [`main/tools/router-deploy/`](main/tools/router-deploy/) |
| Wiki | [`main/wiki/`](main/wiki/) |

---

*Last updated: May 2026*
