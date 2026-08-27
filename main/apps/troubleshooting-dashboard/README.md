# Troubleshooting Dashboard POC

Read-only, dependency-free dashboard for turning a visible symptom into an
ordered diagnostic sequence. The initial scope follows the five symptoms in
`main/TO-DO.md`:

1. Homepage access;
2. Home Assistant availability;
3. one camera path;
4. P1S telemetry;
5. backup freshness.

## Data boundary

The POC does not probe the network or execute commands. Load the JSON produced
on the Proxmox host:

```sh
main/scripts/monitoring/health_check.sh --json > health.json
```

Or from a Windows management workstation:

```powershell
main\scripts\monitoring\health_check.ps1 -Full -Json > health.json
```

The file is parsed in the browser and is not uploaded. Unknown or skipped
checks stay `Needs evidence`; they are never treated as healthy.

The Windows collector includes the observed endpoint or HTTP result beside each
status. The Proxmox collector supplies the guest-mount and per-guest backup
freshness checks that cannot be established from the management workstation.
For a backup incident, use the Proxmox JSON snapshot rather than treating the
missing Windows signals as a failure or a pass.

The interface highlights the first failed or missing evidence signal and names
the host on which each displayed command must be run. These are instructions
only: copying a command never runs it.

## Local verification

```powershell
cd main/apps/troubleshooting-dashboard
npm run check
docker compose config
```

Serve the directory with any static server for browser review. The staged
container binds only `192.168.20.102:8094`, uses reserved explicit bridge
`10.240.32.0/24`, and requires the tracked management-only `DOCKER-USER`
policy. It has no DNS, Homepage, LAN, monitoring or Tailscale exposure.

## Deliberate v1 exclusions

- no arbitrary shell input or command execution;
- no automatic restart, firewall, restore or remediation controls;
- no credentials, tokens or embedded authenticated monitoring APIs;
- no persistence beyond the current browser tab;
- no claim that a missing signal is healthy.

## Staged live state

- [x] Five diagnostic sequences reviewed with explicit execution hosts.
- [x] Staged deployment on management-only port `8094`.
- [x] Desktop/mobile acceptance using a real 13/13 Windows snapshot.
- [x] Stop/start rollback proof and post-rollback access revalidation.
- [ ] Real Proxmox snapshot acceptance for mount and backup-freshness evidence.
- [ ] Explicit approval for any DNS name or Homepage placement.

The pre-change live firewall and audit scripts are retained on VM 103 under
`/opt/backups/troubleshooting-dashboard-20260825T1518Z/`.
