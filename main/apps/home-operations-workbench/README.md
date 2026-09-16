# Home Operations Workbench

This is a local, read-only proof of concept for the selected Household and
Workshop Operations roadmap work:

- Today at Home
- dependency-aware troubleshooting
- recovery readiness
- Cook What We Have
- VentSys commissioning companion

It deliberately has no Home Assistant, Mealie, Grocy, GardenKeeper, Recomp,
MQTT, shell, or browser-storage integration. Importing data puts a normalized
copy into the current browser tab only. Closing or clearing the tab removes it.

## Evidence contract

The app accepts a JSON object with `schemaVersion: "1.0"`. The normalizer
supports these top-level areas:

- `today` with garden tasks, food, meals, workouts, and operations
- `dependencies` and `incidents`
- `recovery.systems` with separate backup, integrity, and restore evidence
- `cooking.candidates` with per-ingredient availability
- `commissioning.devices` and visual-only `commissioning.scenarios`

`fixtures/demo-operations.js` is the complete safe example. It is marked as a
demonstration and reflects no live service state.

The normalizer rejects unknown schema versions, caps collections, removes
non-HTTP(S) links, and omits imported detail that appears to contain a secret.
This is a presentation boundary, not a substitute for keeping credentials out
of source exports.

## Local verification

### Offline health imports

The file picker accepts saved `Windows management workstation` and `Proxmox
host` health-check JSON in addition to schema 1.0 workbooks. Only known check
statuses are copied; raw detail, filenames, command output and unknown fields
are discarded. These imports never contact a service or execute commands.

Evidence older than 36 hours is stale. Missing, malformed, timezone-ambiguous
or future timestamps produce unknown states. Older collectors emit local time
without an offset: explicitly convert those snapshots on the workstation using
the collector's offset at collection time (for example `+01:00` for London BST):

```powershell
node main/apps/home-operations-workbench/import-health.mjs .\windows-health.json .\operations-evidence.json +01:00
```

The converter refuses to overwrite existing output. Import its output in the
Workbench. Do not assume the Proxmox host uses the workstation's timezone.
Backup freshness never supplies integrity or restore proof. A failed camera
probe stays failed; intentional disconnection requires separate human evidence
and is not inferred from an IP address. The two collector formats can be
imported independently; each import replaces the current tab's evidence.

### Checks

```powershell
Set-Location K:\Documents\Obsidian\home-automation-project\main\apps\home-operations-workbench
npm run check

$server = Start-Process -FilePath python -ArgumentList '-m', 'http.server', '8129', '--bind', '127.0.0.1' -WorkingDirectory (Get-Location) -WindowStyle Hidden -PassThru
try {
  npm run test:browser
} finally {
  Stop-Process -Id $server.Id
}
```

Open `http://127.0.0.1:8129` while the local server runs to inspect the
workbench manually. Do not deploy this proof of concept or add it to the
Docker host until a live adapter contract and service placement decision exist.
