# Home Automation Project

A comprehensive home automation system focused on fire safety and safe ventilation for 3D printing operations, with integrated CCTV monitoring, secure network architecture, and AI-driven automation.

## Project Status
- **Current Phase:** Network Architecture & Planning
- **Progress:** 15% Complete
- **Priority:** Safety systems implementation

## Quick Start
1. Review docs/decisions/ for architecture decisions
2. Check docs/session-states/ for latest development context  
3. See configs/ for current system configurations
4. Refer to docs/procedures/ for setup instructions

## System Overview
- **Network:** 4-VLAN security-segmented architecture
- **Hardware:** MINIX mini PC with Proxmox virtualization
- **Safety:** PrintAirPipe smart ventilation with fire detection
- **Monitoring:** Frigate NVR with isolated CCTV network
- **AI:** Claude MCP integration for intelligent automation

## Repository Structure
docs/                    # Documentation and session states
├── session-states/      # Claude session documentation
├── decisions/           # Architecture decisions and rationale
├── procedures/          # Step-by-step procedures
└── troubleshooting/     # Known issues and solutions
configs/                 # System configurations
├── openwrt/            # Router configurations
├── home-assistant/      # HA configs and automations
├── frigate/            # NVR configurations
├── esphome/            # PrintAirPipe and sensor configs
└── proxmox/            # VM configurations
hardware/               # Physical system documentation
├── stl-files/          # 3D printing files
├── wiring-diagrams/    # Circuit diagrams
└── part-lists/         # Component specifications
scripts/                # Automation and setup scripts
├── setup/              # Installation scripts
├── backup/             # Backup procedures
└── monitoring/         # Health check scripts

## Safety Warning
⚠️ This system includes fire safety components. Always prioritize safety features and test thoroughly before deployment.
