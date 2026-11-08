# Storage migration preparation

The guarded controller and configuration renderer are prepared; execution is
underway. Follow [the cutover runbook](cutover-runbook.md)
for the exact sequence, shutdowns, mount/export changes, acceptance and recovery.
The extended hardware test remains a separate execution gate. The controller
has no disk wipe, format, RAID creation or member-add operation.

`plan_layout.py` creates a read-only namespace inventory in a new SQLite file.
It maps the requested Print/Media/Calibre final layout, records regular and
special file identities, and reports destination collisions. It has no
copy, move, delete, format or RAID-management operation.

Run tests:

```powershell
python -m unittest discover -s main/tools/storage-migration -v
python main/tools/storage-migration/run_linux_tests.py
```

For a live inventory, run on OMV after checking that each source is an actual
mount with the exact expected filesystem UUID. Do not infer mount identity
from a directory name or existence alone. Use a new evidence directory on the
OS filesystem, outside both source trees and outside the vault. Verify its
filesystem type and at least several GiB free before a full scan. On this OMV
host `/var/tmp` is a small RAM-backed overlay: do not use it for a full inventory.
Use a private directory under `/root` on the persistent ext4 OS filesystem and
set `SQLITE_TMPDIR` to that same directory for SQLite scratch space:

```sh
SQLITE_TMPDIR=/absolute/existing/private-evidence-directory python3 plan_layout.py \
  --y-root /srv/dev-disk-by-uuid-fdb92af7-371c-4793-8d98-ff47e961498d \
  --z-root /srv/dev-disk-by-uuid-a216b8bb-708e-4342-a5be-a415cdc465fa \
  --output /absolute/existing/private-evidence-directory/layout.sqlite
```

Exit 0 means no inventory review issues; exit 2 means issues were recorded.
An exception leaves incomplete evidence which must not be accepted or
overwritten. Directory merges also require review, even if modes and owners
appear equal: this helper does not capture ACLs or xattrs.

The database records every wrapper too, with a null destination. Those rows
are not instructions to delete it. No hashes are computed. A live snapshot
does not establish a consistent source generation, copy integrity, readiness
to erase a disk, or permission to delete anything.

The inventory preserves unsigned inode identifiers and out-of-range nanosecond
timestamps as exact decimal text; do not cast them to SQLite INTEGER in later
consumers. It never follows symlinks. Absolute or parent-traversing symlink
targets require review; other filesystems nested under the source roots are
reported and not traversed.

## Guarded transfer controller

Use one whole-Z staging copy in the original layout on the new filesystem,
preserving hardlinks across directories and allowing resumable final sync.
Only after writers are stopped, final reconciliation and checksum/metadata
verification pass should the destination be flattened with checked
same-filesystem renames. This avoids resyncing the original layout onto an
already-flattened destination.

`migration.py` pins source filesystem UUIDs and the new array's member serials,
requires a healthy synchronized mirror for Y copying, and previews copies by
default. `--execute` opts into rsync. State and evidence live on the persistent
OS disk, outside all datasets. `--writers-stopped` attests to an external
shutdown; it does not stop services or clients. See the runbook before using it.

The commands are `init`, `copy`, `reconcile-extras`, `verify`, `prepare`, `apply`,
`rollback`, `final-verify`, `check-original-z`, `snapshot-live-z`, `activate`, and
`remove-print-wrapper`. Transformation phases are `flatten-z`, `publish-z`,
`publish-y`, `retain-y`, and `flatten-print`. Dependencies and proof receipts
are checked, not inferred from directory existence. Verification issues return
nonzero exit status and must stop the sequence.

Renames use descriptor-anchored, same-filesystem no-replace operations, inode
receipts and durable intent/completion journals. Interrupted operations resume;
rollback restores directory metadata before live activation. Activation and
empty-wrapper removal close automatic rollback. Rolled-back plans stay closed.
Only the five audited directory merges are permitted, with incoming Y parent
metadata and unchanged existing Z children. Case aliases and leaf collisions fail.

Warm-copy deletions or type changes are moved into sealed private staging
quarantines by `reconcile-extras`, never silently deleted. A cold copy and fresh
verification must follow. Original Y trees are retained privately on Y after
successful final verification; then Print children are renamed to the root.
The Print wrapper is removed with rmdir only after every recorded child is
confirmed at its destination and the wrapper is empty. Payload deletion and
final retirement remain a separate acceptance-gated operation.

## Staged-copy verifier

`verify_copy.py` compares a staged copy in its original layout on Linux. It
hashes every regular file with SHA256; compares types, names, numeric ownership,
modes, exact nanosecond mtimes, symlink targets and all readable xattrs (including
POSIX ACLs); checks hardlink relationships in both directions; and reports
substantially sparse files that became fully allocated. It records allocation
sizes but does not demand identical physical extent layouts across filesystems.
It compares archived sockets/FIFOs as special entries rather than opening them.

It anchors traversal to directory descriptors, refuses symlink following and
nested filesystems, detects changes during individual comparisons, and writes
an exclusive JSONL report outside both trees. A report without its final
`complete` record, or with any issue, fails acceptance. The source and target
mount identities must be checked separately; this helper does not prove that
the target is the intended array.

```sh
python3 verify_copy.py --source /verified/original-root \
  --target /verified/staged-root --report /private/evidence/new-verification.jsonl \
  --writers-stopped
```

The flag attests that external writers have already been stopped; it does not
stop them. A file can change after its comparison finishes if writers remain
active. Run before destination flattening or directory merges. Verification of
the final mapped layout and its deliberate parent-directory metadata exceptions
is performed separately by `final-verify` before activation.

The tested rsync copy flags are `-aHAXSx --numeric-ids --protect-args
--modify-window=-1`. The negative modification window is required for exact
nanosecond comparisons: the real fixture exposed same-second directory,
symlink and special-entry timestamps being skipped with rsync's default window.
With that option the fixture preserves ACLs, xattrs, sparse allocation,
hardlinks, Unicode names, symlinks, sockets and FIFOs, and the verifier reports
zero issues. `--dry-run` was separately confirmed to leave the fixture target
empty. These are fixture results, not proof that household data has been copied.

`verify_layout.py` reconciles the mapped namespace, metadata, links and hashes
against sealed copy receipts. Since Media may receive legitimate writes before
Y moves, `snapshot-live-z` captures a fresh quiesced identity/metadata baseline
after Z activation. The later combined check proves existing Media entries
unchanged through the merge using inode, size, mtime and ctime; new Y copies
still receive full hash checks. This baseline is not new content-hash proof.
Unknown maintenance content fails; only exact validated sealed quarantines may
contain retained staging versions. `check-original-z` checks the frozen original
against its receipt before any separate disk-retirement action.

`render_cutover.py` produces reviewable configuration contracts and patches for
scoped OMV/NFS exports, VM103 mounts, Calibre-Web, backup guards/clients,
monitoring, diagnostics and Filebrowser's Print/Media composite view. It creates
a new output directory and deploys nothing. Read-only mount assertions refuse
missing mounts and wrong backing UUIDs. Filebrowser's database inspector emits
only selected account/scope fields from a read-only active Bolt snapshot.

The Linux test runner copies only code and sanitized templates into a temporary
OS-disk fixture on `omv-lan`, runs real rsync and namespace/recovery tests, and
cleans that fixture. It never copies household datasets or alters live configs.
Windows skips Linux-specific filesystem tests. These fixtures establish tool
behavior, not live application, backup/restore or offline-client acceptance.

See [the migration audit](../../docs/audits/2026-10-20-storage-migration/README.md)
for the accepted single-copy risk, dependency changes and acceptance tests.
