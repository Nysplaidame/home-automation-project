---
title: Gridfinity Layout Tool
description: Local Docker-host deployment for the Gridfinity Layout Tool
modified: 2026-07-19
type: runbook
status: live
---

# Gridfinity Layout Tool

This is a local static build of [andymai/gridfinity-layout-tool](https://github.com/andymai/gridfinity-layout-tool), served on docker-host at `http://192.168.20.102:8093` (planned DNS alias: `gridfinity.home.local`). The upstream project is AGPL-3.0-only.

## Scope

The local instance provides the browser-based layout planner, 3D preview, bin designer, baseplate generator, and export features. Layouts remain in the browser by default. Upstream OAuth sign-in, cloud sync, collaborative editing, Vercel API routes, and analytics are not enabled by this deployment.

## Deploy

Build the pinned upstream release on a Linux builder with Node.js 24 and pnpm
11.2.2, then copy the resulting `dist/` directory with the stack template to
`/opt/stacks/gridfinity-layout-tool/` on VM 103. Do not build this frontend on
docker-host: the full TypeScript/WebAssembly build is intentionally kept off
the shared application VM.

The stack uses the fixed `172.32.0.0/24` bridge subnet. Do not remove that
setting: an earlier automatic Docker allocation overlapped the management
network and broke VM 103 reachability.

On VM 103, run:

```sh
cd /opt/stacks/gridfinity-layout-tool
test -f dist/index.html
docker compose pull
docker compose up -d
curl -fsS http://127.0.0.1:8093/healthz
```

Open `http://192.168.20.102:8093` and test 3D preview plus STL/3MF export.

## Updates

The local workstation runs an automatic release check, external Linux build,
and deploy at 09:00 while the Windows user is signed in. It never opens WAN
access on docker-host. The scheduled task deploys only upstream version tags,
uses a dedicated non-interactive SSH key restricted to the management subnet,
and saves its latest result under `C:\ProgramData\home-automation-project\`.
The currently deployed release is `gridfinity-layout-tool-v4.253.0`.

Run the same check on demand from the repository root:

```powershell
.\main\scripts\maintenance\gridfinity-layout-tool-update.ps1 -Mode Check
```

To install the latest release, or a specific tag reported by the check:

```powershell
.\main\scripts\maintenance\gridfinity-layout-tool-update.ps1 -Mode Install
.\main\scripts\maintenance\gridfinity-layout-tool-update.ps1 -Mode Install -Version gridfinity-layout-tool-v4.249.0
```

The check uses a local version marker, initially set to the release deployed
when this workflow was introduced. Each successful install or rollback updates
that marker. The autodeploy task uses the dedicated SSH key at
`%USERPROFILE%\.ssh\gridfinity-layout-tool-autodeploy`; its private half is
outside this repository and must not be copied into it.

The install command builds the pinned release in WSL/Linux with Node.js 24 and
pnpm 11.2.2, uploads only the resulting static archive, switches `dist/`
atomically on VM 103, recreates Nginx, and validates `/healthz`. It preserves
one previous release and restores it automatically if the new release fails its
health check. It uses normal interactive SSH authentication, or pass
`-SshKeyPath <path>` for key-based access; no credentials are stored in this
repository.

To repair or change the daily local autodeploy task's time, run:

```powershell
.\main\scripts\maintenance\install-gridfinity-update-check-task.ps1 -AutoDeploy
.\main\scripts\maintenance\install-gridfinity-update-check-task.ps1 -AutoDeploy -At 14:30
```

To return to the immediately previous successful release:

```powershell
.\main\scripts\maintenance\gridfinity-layout-tool-update.ps1 -Mode Rollback
```

After a successful install, confirm the planner opens and exercise 3D preview
plus STL/3MF export before treating the update as complete. Record meaningful
changes in the weekly update review log.

## Data and security

This stack has no persistent server-side data or secrets. Do not add OAuth credentials to this stack without a separate design for callback URLs, storage, and access control. Keep it internal to VLAN 20 and do not publish it through WAN or DMZ paths.
