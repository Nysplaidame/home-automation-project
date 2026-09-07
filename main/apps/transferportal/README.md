# OMV Transfer Portal

Native OpenMediaVault-hosted transfer console for local disk-to-disk rsync jobs.

This is intentionally not a Docker app and not yet an OMV plugin. It is a small
FastAPI service running as the unprivileged `transferportal` user. Root-only
operations are delegated to a narrow JSON-speaking helper through sudo.

## Layout

| Path | Purpose |
|---|---|
| `transferportal/` | Python package |
| `transferportal/app.py` | FastAPI app and server-rendered UI routes |
| `transferportal/root_helper.py` | Root helper entrypoint |
| `packaging/systemd/` | systemd service template |
| `packaging/sudoers/` | sudoers allowlist template |
| `packaging/examples/config.yaml` | Example app config |
| `tests/` | Unit tests for safety-critical logic |

## Development

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
pytest
uvicorn transferportal.app:create_app --factory --reload
```

## Safety Boundaries

- The web app never runs as root.
- The helper accepts structured JSON only and dispatches to an allowlisted
  command table.
- Generated rsync commands are arrays, not editable shell strings.
- The root-owned helper uses a compiled policy rather than trusting the
  service-user-writable application configuration.
- Rsync launch requires one allowlisted command shape, exact source/destination
  endpoints for the same portal, active bind mounts, and constrained log paths.
- Move mode is disabled until its copy, verification, and separately confirmed
  source-deletion phases are connected to the production job lifecycle.
- Destination deletion and `--inplace` are disabled until destructive
  permissions are sourced from a root-owned portal policy.
- Preview commands always include `--dry-run` and cannot be retried as live jobs.
- Active-job admission is an atomic database reservation; abandoned queued jobs
  are failed on service startup.
