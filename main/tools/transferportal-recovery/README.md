# TransferPortal recovery acceptance tools

These scripts support the recovery gate in `docs/install/services/transferportal.md`.
They are not a deployment installer and never restore production transfer data.

- `checkpoint.py`: run as root on OMV through SSH stdin after verifying idle state.
  It refuses active DB jobs or rsync/helper runners, checks the expected data-disk
  mount, stops the web service, captures matched app/venv/config/database/log/
  helper/policy/mount definitions with ACLs, records hashes/integrity/counts, and
  resumes the service in `finally`. The fixed checkpoint parent is root-only.
- `guest_console.py`: invokes temporary VM9108 through Proxmox guest agent using
  shell-safe argument quoting. Uploads only `/root/` test artifacts in bounded
  chunks. Before reuse, verify VM9108 is the disposable recovery guest, stopped
  before provisioning, and has no network device. Never target a production VM.
- `isolated_acceptance.py`: runs only in that disposable guest; refuses NICs,
  routes and NAS mounts. Requires read-only media containing `checkpoint.tar.gz`,
  `manifest.json`, `candidate.tar.gz` and an offline `rsync-runtime.tar.gz`.
  Preserves original checkpoint under `/root/recovery-saved`, installs saved
  app/helper/sudoers without activating production units or environment, then
  uses fresh config/credentials, real sudo helper and loopback HTTP to test
  saved and repaired generations. The optional `/root/recovery-root-helper.py`
  overlay supports the systemd fix discovered in this exercise; its hash is
  recorded. The script compares historical rows and disposable file hashes.
- `mount_paths_acceptance.py`: runs after the above test; verifies actual source
  and destination bind mounts with spaces, percent signs and embedded quotes.

The 2026-10-02 exercise cloned the existing stopped no-NIC VM9102 into new VM9108,
with `onboot=0`, 2GiB RAM and no NIC. No existing VM was modified. Inherited Docker
bridges were stopped/removed inside the disposable guest before acceptance.
Protected media was attached as a read-only ISO; no SSH network or production
mount was available in the guest. Runtime rsync binary/libraries came from OMV
and were kept under `/opt/recovery-rsync` without replacing system libraries.

Example commands used from the canonical checkout (PowerShell):

```powershell
# Code sent on stdin by Python as bytes, preserving LF on Windows:
# subprocess.run(['ssh','omv-lan','python3 -'], input=Path(...).read_bytes())
python main/tools/transferportal-recovery/guest_console.py upload main/tools/transferportal-recovery/isolated_acceptance.py /root/isolated_acceptance.py
python main/tools/transferportal-recovery/guest_console.py exec 'python3 /root/isolated_acceptance.py'
# Poll the returned guest PID with status; never re-execute a running test.
python main/tools/transferportal-recovery/guest_console.py status <guest-pid>
```

Media/checkpoint handling is privileged: preserve mode600 and root-only parents,
never print environment/secret values, and never commit the archive or runtime
bundles. Only the selected nonsensitive acceptance JSON is tracked. Save proof
beside the NAS checkpoint before removing the disposable VM and media. For a
future run, use a new generation, confirm a free VM ID and update the console
script deliberately. Refresh idle-state/checkpoint checks before live deployment.

Completed evidence: `docs/audits/2026-10-02-transferportal-recovery-evidence.json`.
The original production service was resumed; hardening was not deployed by this
exercise. VM9108 and temporary host/media copies were removed after acceptance.
