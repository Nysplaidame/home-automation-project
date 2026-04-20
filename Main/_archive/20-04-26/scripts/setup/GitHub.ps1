# Home Automation Safety System - Repository Structure Setup (Windows)
Write-Host "Creating Home Automation Safety System repository structure..." -ForegroundColor Green

# Create main directory
New-Item -ItemType Directory -Force -Path "home-automation-safety"
Set-Location "home-automation-safety"

# Create directory structure
$directories = @(
    "docs\session-states",
    "docs\decisions", 
    "docs\procedures",
    "docs\troubleshooting",
    "configs\openwrt",
    "configs\home-assistant",
    "configs\frigate",
    "configs\esphome", 
    "configs\proxmox",
    "hardware\stl-files",
    "hardware\wiring-diagrams",
    "hardware\part-lists",
    "scripts\setup",
    "scripts\backup",
    "scripts\monitoring"
)

foreach ($dir in $directories) {
    New-Item -ItemType Directory -Force -Path $dir
    Write-Host "Created: $dir" -ForegroundColor Yellow
}

# Create README.md
$readmeContent = @"
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
"@

$readmeContent | Out-File -FilePath "README.md" -Encoding UTF8

# Create session template
$sessionTemplate = @"
# Session: [System Focus] - [YYYY-MM-DD]

## Context Loading
**Previous Sessions:** 
**Current Phase:** 
**System Focus:** 
**Git Branch:** main

## Goals This Session
- [ ] Goal 1
- [ ] Goal 2
- [ ] Goal 3

## Decisions Made
### Decision 1: [Title]
**Problem:** 
**Solution:** 
**Rationale:** 
**Files Affected:** 
**Git Commit:** 

## Technical Context
**Key Files Referenced:** 
- path/to/config.yaml - Purpose

**Current State:**
- Working: 
- Issues: 
- Partially Done: 

## Artifacts Created/Modified
- [ ] Artifact 1: Description
- [ ] Artifact 2: Description

## Next Session Prep
**Immediate Next Steps:**
1. 
2. 
3. 

**Files to Review:** 
**Context Needed:** 
**Dependencies:** 

## Issues & Blockers
- Issue 1: 
- Workaround: 

## Git Integration
**Commits This Session:** 
**Files Modified:** 
**New Files Created:** 

---
**Session Duration:** 
**Complexity Level:** Low/Medium/High
**Success Rating:** 1-5 (how well did we achieve goals)
"@

$sessionTemplate | Out-File -FilePath "docs\session-states\session-template.md" -Encoding UTF8

# Create current session state
$currentSession = @"
# Session: Initial Documentation Structure - 2025-09-12

## Context Loading
**Previous Sessions:** Claude conversation with project prompt and network diagram
**Current Phase:** Network Architecture & Planning (15% complete)
**System Focus:** Documentation structure and repository setup
**Git Branch:** main

## Goals This Session
- [x] Create scalable documentation structure
- [x] Set up repository organization
- [x] Define session management strategy
- [x] Implement first session state files

## Decisions Made
### Decision 1: Modular Session-Based Documentation
**Problem:** Claude context limits will be exceeded as project grows
**Solution:** External git storage for configs, Claude sessions for decisions/context
**Rationale:** Separates large data (configs) from decision context (reasoning)
**Files Affected:** All future documentation structure
**Git Commit:** [Initial commit pending]

### Decision 2: Phase-Based Directory Structure
**Problem:** Need organized approach for complex multi-system project  
**Solution:** Separate directories by system type and project phase
**Rationale:** Matches project implementation phases, easier navigation
**Files Affected:** Repository root structure
**Git Commit:** [Initial commit pending]

## Next Session Prep
**Immediate Next Steps:**
1. Initialize git repository with structure
2. Create initial configuration files from previous session artifacts
3. Set up first system-specific session (OpenWrt configuration)

**Files to Review:** 
- Previous firewall configuration artifact
- Network diagram artifact  
- Project requirements document

**Context Needed:** 
- Current network setup progress
- Specific OpenWrt configuration requirements
- VLAN implementation details

---
**Session Duration:** 45 minutes
**Complexity Level:** Medium  
**Success Rating:** 5/5 (structure complete and implemented)
"@

$currentSession | Out-File -FilePath "docs\session-states\20250912-initial-documentation-session01.md" -Encoding UTF8

# Create network architecture decision
$networkDecision = @"
# Decision: 4-VLAN Security-Segmented Network Architecture

**Date:** 2025-09-09
**Status:** Accepted
**Context:** Need secure network design isolating safety systems from internet while enabling remote access

## Problem Statement
Design a network architecture that:
- Completely isolates fire safety sensors from internet access
- Isolates CCTV system from internet access  
- Enables secure remote access to Home Assistant
- Provides management access to all systems
- Balances security with operational needs

## Decision
**Chosen Option:** 4-VLAN Hybrid Architecture

**Rationale:** 
- Provides required security isolation for safety systems
- Enables remote access through Home Assistant bridge
- Manageable complexity with clear security boundaries
- Allows controlled inter-system communication

## Network Design
- **VLAN 20:** Automation & Management (192.168.20.0/24) - Internet access
- **VLAN 30:** CCTV (192.168.30.0/24) - No internet, HA bridge access  
- **VLAN 40:** Storage (192.168.40.0/24) - No internet, Frigate access
- **VLAN 50:** IoT Sensors (192.168.50.0/24) - No internet, HA control only

## Implementation
- **Files Affected:** 
  - configs/openwrt/firewall-rules.conf
  - configs/openwrt/vlan-config.conf 
  - Network device configurations
  
---
**Related Sessions:** 20250909-initial-planning, 20250912-documentation-setup
"@

$networkDecision | Out-File -FilePath "docs\decisions\001-network-architecture.md" -Encoding UTF8

# Create placeholder config files
"# OpenWrt Main Configuration" | Out-File -FilePath "configs\openwrt\main-config.conf" -Encoding UTF8
"# OpenWrt Firewall Rules" | Out-File -FilePath "configs\openwrt\firewall-rules.conf" -Encoding UTF8
"# OpenWrt VLAN Configuration" | Out-File -FilePath "configs\openwrt\vlan-config.conf" -Encoding UTF8
"# Home Assistant Configuration" | Out-File -FilePath "configs\home-assistant\configuration.yaml" -Encoding UTF8
"# Home Assistant Automations" | Out-File -FilePath "configs\home-assistant\automations.yaml" -Encoding UTF8
"# Frigate NVR Configuration" | Out-File -FilePath "configs\frigate\config.yml" -Encoding UTF8
"# ESPHome PrintAirPipe Configuration" | Out-File -FilePath "configs\esphome\printairpipe-controller.yaml" -Encoding UTF8
"# Proxmox VM Configurations" | Out-File -FilePath "configs\proxmox\vm-configs.conf" -Encoding UTF8

Write-Host ""
Write-Host "✅ Repository structure created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📁 Directory structure created:" -ForegroundColor Cyan
Get-ChildItem -Recurse -Directory | ForEach-Object { Write-Host "   $($_.FullName.Replace((Get-Location), '.'))" -ForegroundColor White }
Write-Host ""
Write-Host "🚀 Next steps:" -ForegroundColor Cyan
Write-Host "1. git init" -ForegroundColor Yellow
Write-Host "2. git add ." -ForegroundColor Yellow  
Write-Host "3. git commit -m 'Initial repository structure'" -ForegroundColor Yellow
Write-Host "4. Create GitHub repository and push" -ForegroundColor Yellow
Write-Host ""
Write-Host "📄 Key files created:" -ForegroundColor Cyan
Write-Host "- README.md (project overview)" -ForegroundColor White
Write-Host "- docs\session-states\session-template.md (for future sessions)" -ForegroundColor White
Write-Host "- docs\session-states\20250912-initial-documentation-session01.md (current state)" -ForegroundColor White
Write-Host "- docs\decisions\001-network-architecture.md (network design decision)" -ForegroundColor White
Write-Host "- Configuration placeholders for all major systems" -ForegroundColor White