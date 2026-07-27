---
title: Home Automation Project
description: Repository root navigation guide
created: 2025-09-15
modified: 2026-05-25
---

# Home Automation Project

Fire safety ventilation, NVR surveillance, secure network architecture, and home automation for 3D printing operations.

**Repository:** https://github.com/Nysplaidame/home-automation-project

---

## Repository Layout

```text
home-automation-project/
├── main/               ← primary working tree (all active docs, configs, scripts)
│   ├── configs/        ← system configuration files
│   ├── docs/           ← decisions, install manuals, procedures, diagrams, troubleshooting
│   ├── scripts/        ← setup guides and operational scripts
│   ├── tools/          ← router-deploy toolkit, smoke tests
│   ├── ventsys/        ← VentSys ESPHome bundles and integration docs
│   ├── README.md       ← project overview and status
│   ├── PROJECT-INDEX.md← documentation index
│   └── TO-DO.md        ← current task list
├── wiki/               ← separate LLM-maintained knowledge base
└── README.md           ← this file
```

For active project work, start in [`main/`](main/).
The root of this repo is the Obsidian vault wrapper. The wiki lives separately under [`wiki/`](wiki/).

---

## Quick Links

| What | Where |
|---|---|
| Project overview and current status | [`main/README.md`](main/README.md) |
| Full documentation index | [`main/PROJECT-INDEX.md`](main/PROJECT-INDEX.md) |
| Task list | [`main/TO-DO.md`](main/TO-DO.md) |
| Current session handoff | [`main/HANDOFF-2026-07-27-portal-services.md`](main/HANDOFF-2026-07-27-portal-services.md) |
| Fresh rebuild manual | [`main/docs/install/START-HERE.md`](main/docs/install/START-HERE.md) |
| Router configs | [`main/configs/openwrt/`](main/configs/openwrt/) |
| Router deploy toolkit | [`main/tools/router-deploy/`](main/tools/router-deploy/) |
| ESPHome configs | [`main/configs/esphome/`](main/configs/esphome/) |
| VentSys bundles | [`main/ventsys/ventsys_bundle_updated/`](main/ventsys/ventsys_bundle_updated/) |
| Wiki operating rules | [`wiki/CLAUDE.md`](wiki/CLAUDE.md) |

---

*Last updated: June 2026*
