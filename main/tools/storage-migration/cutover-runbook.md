# Print / Media execution runbook

**October27 23:19 GMT FINAL OPERATIONAL STATE:** layout, shares, clients, services,
backups/isolated restores and exact retained-source/staging retirement completed.
Private migration trees removed; journals/receipts remain OS-private. Do not
rerun historical phase commands below against the current live namespace.
See audit final reference disposition for bounded text corrections and remaining
offline/native binary client checks. Known test fixtures remain intentionally.

**October27 19:33 GMT CURRENT — prior execution notes below are historical:**
combined proof/retention/Print flattening passed; publish-y and flatten-print
activated. Print/Media SMB and all scoped service/backup exports live, clients
retargeted, runtime masks cleared as appropriate, previous services/jobs/timers
restored. HA nas_backups active/default. Owner Y/Immich/Filebrowser acceptance,
fresh backups and isolated CT/config/app database restores passed. Do not repeat
layout/cutover commands. TransferPortal remains retired. Retained originals and
quarantines remain private pending separate retirement/native-path disposition.
Exact evidence and test limits are in audit/current-live-state. No booted HA
restore or live-camera recording claim.

**October27 14:45 GMT latest:** publish-y journal applied; background unit
`household-storage-layout-y-20261027.service` runs combined verification, then
proof-gated retain-y/flatten-print/empty-wrapper removal and refreezes Y RO.
No services activated. Do not duplicate section C layout commands. Logs under
`/root/household-storage-layout-y-20261027/`; frozen clients/masks remain until
reviewed namespace completion and config/mount/service acceptance.

**October27 10:21 GMT current:** cold Y unit
`household-storage-cold-y-20261027.service` runs reconciliation/final copy/full
verification/snapshot-live-z ONLY. First two passed; hashes running. No duplicate
commands or publication. Y frozen RO; affected services/SMB paused; client mounts
runtime-masked; backup jobs/storage/timers paused. HA NAS mount detached, schedule
unchanged; restore saved mount/default after retargeting. Checkpoints/logs all
four hosts `/root/household-storage-cold-y-20261027/`. Audit/current-live-state
record exact maintenance state; section C publication/Print still pending.

**October27 current execution supersedes historical notes below:** both mirrors
healthy `[UU]`. First Y warm pass failed closed on rsync24 (seven backup files
vanished during live retention). Owner authorized continuation; warm-only retry
`household-storage-warm-y-retry-20261027.service` now running, logs under
`/root/household-storage-y-stage-20261025/`. Do not launch another copy. Refreshed
namespace scan found only the same five approved merges. Y cold/merge/Print
steps remain unexecuted; all current writers must be quiesced before section C.

**Current October25 execution:** phase A hashes/layout proof and phase B
scoped NFS/SMB/Compose cutover passed. Owner confirmed Calibre/Atsumeru/qBittorrent
access; permission boundaries and synthetic authenticated recording/decode pass.
Original Z generation proof passed, aliases/config refs retired, filesystem
cleanly unmounted, exact partition serial3GHV81YE added to new Media. Rebuild is
running; do NOT repeat any original-Z wipe/member-add step. No independent old-Z
rollback remains (owner-waived). Y/md0 unchanged. `household-storage-stage-y-20261025.service`
waits for healthy fully synced Media then runs warm Y copy only; do not launch a
second copy. Logs `/root/household-storage-y-stage-20261025/`; member-add/config/
acceptance evidence `/root/household-storage-cutover-z-20261025/` on relevant hosts.
Y cold/merge/Print steps below remain unexecuted. Media consumers are active;
Filebrowser stays paused pending composite view and TransferPortal is retired.

Prepared for the audited OMV host. **Hardware preparation and initial Z warm
copy started October21; cold sync/cutover sections are not yet executed.** The
fourth disk passed its extended test. Current progress and exact evidence are
in [the audit](../../docs/audits/2026-10-20-storage-migration/README.md).
Warm copy finished October22 23:30:54 BST. October23 09:19:55 BST the frozen
reconcile/final-sync/verification runner started under
`household-storage-cold-z-20261023.service`; inspect its phase logs under
`/root/household-storage-cold-z-20261023/` before running any command below.
October24 15:55 BST: `household-storage-layout-z-20261024.service` queued behind
successful cold-job exit and explicit completion event. It runs the prepared
flatten/publish journal steps and final mapped verification, then stops without
activation. Logs/runner: `/root/household-storage-layout-z-20261024/`. Do not run
competing manual layout commands. Six-hour waiting deadline; failure requires
reviewing phase journals before retry. Monitor follows both jobs through proof.
This does not claim verified household copies or accepted applications.
The owner accepted the temporary single-copy period
while converting original Z into the second mirror member.

## Preconditions and checkpoints

- Fourth disk is exactly `ata-WDC_WD160EDGZ-11B2DA0_3HG402GN`, 16 TB,
  serial `3HG402GN`. Its extended SMART test must finish without error, with
  no new pending/reallocated/offline-uncorrectable sectors. Do not interrupt it.
- Original Z is `ata-WDC_WUH721816ALE6L4_3GHV81YE`, filesystem UUID
  `a216b8bb-708e-4342-a5be-a415cdc465fa`. Original Y/Print is RAID1 md0,
  UUID `fdb92af7-371c-4793-8d98-ff47e961498d`. Never identify disks by sdc/sdd
  alone. Neither existing md0 member is a target for formatting or replacement.
- Recheck current mounts, sizes, SMART, RAID membership, root free space and
  folder collisions. Refresh the path audit. Record active SMB clients and
  NAS writers, including desktop extraction, Calibre and the `tmp_*` Print tools.
- Keep private configuration checkpoints on the OS disks, outside all datasets:
  OMV XML/fstab/exports/exports.d/mdadm.conf/Samba, Filebrowser configuration and
  supported database checkpoint, affected unit files; VM103 Compose/env/app
  checkpoints, fstab and backup scripts; Proxmox storage/jobs/fstab/CT111 config;
  HA mount/default/schedule state. Keep credentials out of the vault and output.
  The full-data-backup waiver does not waive these small configuration copies.
- Save previous active/enabled container, service and timer states. Restore only
  those originally active; do not enable prepared but undeployed services.
- Use private OS-backed state under `/root`; check at least 5 GiB free for
  manifests/reports and more as needed. `/var/tmp` is a small RAM-backed overlay
  on this host and must not hold a full inventory.

## Hardware preparation: separate from the data controller

Only after the fourth-disk test passes, review the exact stable device identity,
its unmounted NTFS housekeeping-only contents and a fresh partition/signature
listing. Save its partition-table/signature evidence. Prepare a new two-member
MD RAID1 named `media` using **only that fourth disk and a missing member**,
metadata 1.2, then create an ext4 filesystem labelled Media on the array.
Do not create an array over populated original Z. No force/assume-clean option
is part of this procedure. This remains a device-specific execution gate;
the Python tooling deliberately cannot wipe, format or add a RAID member.

Register/mount the new filesystem through OMV. Record its new filesystem UUID
and OMV mount-entry reference. It must be distinct from both original UUIDs.
Its root should contain only optional empty `lost+found`. Save MD array UUID,
member serial, filesystem UUID and mount identity; persist MD assembly through
OMV. One degraded member is expected only during the initial conversion stage.

Observed Media filesystem UUID: `a8843f98-c937-48a8-aefa-4cd0fb80667c`;
OMV mount reference `8cb2fc04-1a6f-469d-9060-7d4eb7356afe`; MD UUID
`fd8de871:2fcb43a8:d97ff800:008ccb6b`. Array creation used the guarded fourth
disk's partition1 and `missing`, never original Z. Private hardware commands,
checks and output: `/root/storage-migration-preflight-20261021T144508Z/`.
MD configuration, fstab and initramfs were deployed successfully through OMV.
The following render has already run into the new output directory; do not
overwrite it. For another render, choose another new output directory:

```powershell
python main/tools/storage-migration/render_cutover.py --media-uuid a8843f98-c937-48a8-aefa-4cd0fb80667c --output C:\Users\Admin\.codex\storage-migration-rendered-20261021
```

The output directory must not exist. Review the rendered contract and diffs.
Upload runtime `.py` modules and rendered configuration to private OS-disk
directories on the relevant hosts; retain hashes of the installed tool version.
Rendering deploys nothing. The renderer reads canonical source templates, so run
it from this checkout rather than from a flat runtime-tools installation.

## A. Stage and verify Z, then publish its final namespace

The following Bash commands are for OMV, from the uploaded runtime tools.
Initialization and the first warm copy below have already been started for
session `household-20261021`; do not reinitialize it or start a second copy.
Inspect `household-storage-copy-z-20261021.service` and session events first.

```sh
set -euo pipefail
tools_root=/root/storage-migration-preflight-20261021T144508Z/tools
migration_state=/root/household-storage-state-20261021
y_root=/srv/dev-disk-by-uuid-fdb92af7-371c-4793-8d98-ff47e961498d
z_root=/srv/dev-disk-by-uuid-a216b8bb-708e-4342-a5be-a415cdc465fa
media_uuid=a8843f98-c937-48a8-aefa-4cd0fb80667c
media_root=/srv/dev-disk-by-uuid-$media_uuid

python3 "$tools_root/migration.py" --state "$migration_state" init \
  --y-root "$y_root" --z-root "$z_root" --target-root "$media_root" \
  --target-uuid "$media_uuid" --session household-20261021
python3 "$tools_root/migration.py" --state "$migration_state" copy z
python3 "$tools_root/migration.py" --state "$migration_state" copy z --execute
```

The default copy command is a preview, not execution. The target is a private
staging directory on the new array, not the published dataset root. Original Z
stays intact. Copies use metadata/hardlink/sparse preservation, numeric IDs,
exact nanosecond comparison, partial-file resume and file fsync; no `--delete`,
`--inplace` or source-removal option is used.

Before the cold final pass, stop NAS library imports/downloads/recording and
desktop Z writers. On VM103 record states, then stop Watchtower and the affected
containers: `calibre-web`, `jellyfin`, `atsumeru`, `qbittorrent`, `mediamtx`.
Stop the curated exporter if deployed. Stop publishers as well as consumers.
Quiesce SMB clients for any Samba configuration apply. Use graceful stops;
failure to stop or unmount is a maintenance failure, not a reason to force it.

Actual October23 shutdown: the five media containers and Watchtower are stopped;
MediaMTX backup timer paused. Atsumeru needed SIGTERM to its verified Java child
because PID1 shell did not forward Docker stop; no SIGKILL. Old VM103 media NFS
was cleanly unmounted, its mount and automount runtime-masked. OMV Filebrowser
and TransferPortal are stopped/runtime-masked, stopped Filebrowser data archived.
Original Z and all three bind aliases are read-only at filesystem and VFS layers.
Private config/stopped-state checkpoints exist on both hosts under
`/root/household-storage-cold-z-20261023/`. The running cold unit performs ONLY
the first three commands below; do not duplicate them or publish before its
successful zero-issue receipt.

Recovery before publication: first stop/confirm the queued/layout unit is no
longer waiting or mutating, then stop/confirm the cold unit is no longer doing
verification, then deliberately restore original Z to read/write at its root
and aliases, exact UUID checked, and undo only the recorded runtime masks.
Restore VM103 old mount before restarting its recorded active consumers. At
forward cutover, remove old media fstab entry and reload systemd BEFORE clearing
the parent mount masks; then establish/check the new child mounts. Unmask OMV
Filebrowser only after its desired backing view is mounted and verified.
TransferPortal stays stopped unless deliberately retargeted. Never use this
recovery to redirect clients after activation without reconciling new writes.

```sh
python3 "$tools_root/migration.py" --state "$migration_state" --writers-stopped reconcile-extras z
python3 "$tools_root/migration.py" --state "$migration_state" --writers-stopped copy z --execute --final
python3 "$tools_root/migration.py" --state "$migration_state" --writers-stopped verify z
python3 "$tools_root/migration.py" --state "$migration_state" --writers-stopped prepare flatten-z
python3 "$tools_root/migration.py" --state "$migration_state" --writers-stopped apply flatten-z
python3 "$tools_root/migration.py" --state "$migration_state" --writers-stopped prepare publish-z
python3 "$tools_root/migration.py" --state "$migration_state" --writers-stopped apply publish-z
python3 "$tools_root/migration.py" --state "$migration_state" --writers-stopped final-verify z
```

Inspect each result and stop on every nonzero/issue result. Verification is a
full SHA256/metadata comparison and may take many hours; staging does not
guarantee a short outage. The source must remain quiescent throughout the cold
copy, verification and namespace changes. Calibre becomes `calibre-library` at
the root; other books stay under `books`. The original Z disk is unchanged.

## B. Retarget Z consumers and establish the second mirror member

Use `desired-omv-contract.json` as the exact dataset/client contract. In OMV
create the five phase-z shared folders on the new filesystem with the specified
relative paths and client/squash options. Generate their NFS exports through
OMV; `exports.reference` is review evidence, not a replacement for generated
`/etc/exports`. Jellyfin host storage stays writable for the curated exporter;
the four Jellyfin container bindings stay read-only.

On VM103, while consumers are stopped:

1. Stop the old `/mnt/omv/media` automount/mount and unmount it cleanly. Remove
   its fstab entry; daemon-reload. Do not use lazy/forced unmounts. The parent
   `/mnt/omv/media` becomes a plain directory containing the new child mounts.
2. Create the five empty mountpoints listed in `docker-host-z.fstab`, add those
   entries, reload systemd and mount each explicit path. This creates mountpoints,
   not replacement library directories under a missing mount.
3. Apply the reviewed Calibre-Web binding change in both canonical source and
   deployed Compose: `/mnt/omv/calibre-library:/books`. Keep its setting `/books`.
   Other media container paths remain the same because the new child mounts
   preserve their logical paths.
4. Use the phase-z subset of `expected-docker-mounts.json` with `assert_mounts.py`;
   verify server-side bind/export backing UUIDs are the new Media UUID too.
   Compose validation must pass. Recreate affected containers when opening
   access so they cannot retain old bind handles.

Retire old `/export/media` after consumers have unmounted it. Remove its OMV
shared-folder configuration only when no references remain; never request data
deletion. Removing the old `media` folder record also avoids a `media`/`Media`
naming collision when the old `14tb` root share is renamed.

Change the root `14tb` shared-folder record to the new filesystem root and name
`Media`; preserve its SMB identity/privileges where appropriate. Reconnect Z to
`\\192.168.40.50\Media`. Keep original `14tb` access disabled or read-only
during the transition so clients cannot write the rollback copy.

On each Windows client, first record `Get-SmbMapping` and `Get-SmbConnection`,
close affected applications/Explorer windows and confirm the new share is
accessible using the existing Credential Manager account. In that client's
normal user session, replace Z only at this phase:

```powershell
$ErrorActionPreference = 'Stop'
Get-SmbMapping -LocalPath 'Z:'
if (-not (Test-Path -LiteralPath '\\192.168.40.50\Media')) { throw 'Media share unavailable' }
# Continue only when the recorded old mapping is expected.
Remove-SmbMapping -LocalPath 'Z:' -UpdateProfile -Confirm:$false
New-SmbMapping -LocalPath 'Z:' -RemotePath '\\192.168.40.50\Media' -Persistent $true
```

Do not use forced disconnects or put passwords in scripts. A failed replacement
stops client acceptance; use the recorded mapping for a deliberate recovery.

After zero-issue final verification, the exact mount/export checks and reviewed
configuration are ready, mark the activation boundary **before** opening writes:

```sh
python3 "$tools_root/migration.py" --state "$migration_state" --writers-stopped activate publish-z
```

Restart only previously active affected services and run the acceptance checks
below. Automatic namespace rollback is now closed because new writes may exist.
Original Z is still available for a deliberate reconciliation-based recovery.

Before repurposing original Z, retain all verification reports and successful
application checks. Prove there are no original-Z writers/mount aliases left:
retire or retarget TransferPortal source/smoke units, remove obsolete export
binds and close clients. Remount the old filesystem read-only, confirm that
condition, and while it remains mounted at its pinned UUID path run:

```sh
python3 "$tools_root/migration.py" --state "$migration_state" --writers-stopped check-original-z
```

This checks every original generation against the sealed copy receipt and
refuses late changes. A failure requires reconciliation; do not erase the disk.
Then remove its managed filesystem references and cleanly unmount it.
Capture `findmnt` by physical source as well as by
path, because bind aliases elsewhere can retain old data. Revalidate the exact
old filesystem UUID on partition 1 of serial `3GHV81YE` immediately before the
destructive member-add procedure. Only this original Z device becomes the
second member of the already-verified Media array. Do not touch md0.

There is intentionally no independent full-data recovery copy at this point.
Wait until the array has both expected member serials, zero degraded members,
idle sync action and passing health before staging Y. Confirm assembly/mount
persistence and monitoring; do not interrupt a rebuild to conduct a reboot test.

## C. Move Y non-Print data, protect originals, and flatten Print

The controller refuses Y copies unless the new mirror is healthy and synced.
Stage Y while services are available; the source Print tree is excluded exactly.

```sh
python3 "$tools_root/migration.py" --state "$migration_state" copy y
python3 "$tools_root/migration.py" --state "$migration_state" copy y --execute
```

For the cold pass pause OMV config backup, VM103 app-data and MediaMTX backup
timers, Bambuddy offline updater, any coordinated/export jobs actually installed,
Proxmox backup jobs and HA automatic backups. Let active backups finish or stop
them cleanly. Record schedules/defaults/retention before changing them. Observed
Proxmox jobs were `34c415cb-dd1b-47c4-b764-69a01aa87312` and
`a8c84d38-2a73-4d9d-bf34-111114000001`; re-read current IDs before acting.
Local-only Gardenkeeper backups need not be disabled unless live inspection
shows a new NAS dependency.

Stop Immich upload/media writers. Shut CT111 down gracefully after stopping
Frigate recording, so its Proxmox NFS bind can be unmounted and recreated.
Pause Filebrowser, TransferPortal and all Y/Print desktop jobs before namespace
changes. Keep unrelated HA safety/automation functions running.
Also stop all current Media writers and consumers from phase A again. Keep
both datasets quiescent through the baseline, merge, verification and retargeting.

```sh
python3 "$tools_root/migration.py" --state "$migration_state" --writers-stopped reconcile-extras y
python3 "$tools_root/migration.py" --state "$migration_state" --writers-stopped copy y --execute --final
python3 "$tools_root/migration.py" --state "$migration_state" --writers-stopped verify y
python3 "$tools_root/migration.py" --state "$migration_state" --writers-stopped snapshot-live-z
python3 "$tools_root/migration.py" --state "$migration_state" --writers-stopped prepare publish-y
python3 "$tools_root/migration.py" --state "$migration_state" --writers-stopped apply publish-y
python3 "$tools_root/migration.py" --state "$migration_state" --writers-stopped final-verify combined
python3 "$tools_root/migration.py" --state "$migration_state" --writers-stopped prepare retain-y
python3 "$tools_root/migration.py" --state "$migration_state" --writers-stopped apply retain-y
python3 "$tools_root/migration.py" --state "$migration_state" --writers-stopped prepare flatten-print
python3 "$tools_root/migration.py" --state "$migration_state" --writers-stopped apply flatten-print
python3 "$tools_root/migration.py" --state "$migration_state" --writers-stopped remove-print-wrapper
```

Only the five reviewed directory merges are allowed. Incoming Y parent metadata
wins; existing Z child metadata stays unchanged. Retention validates original
Y identities/generations against its copy receipt, then journal-renames those
original top-level trees into root-private `.household-retained/<session>/` on
Y. Their data is not deleted. This removes writable old aliases during the
acceptance period while keeping the ordinary Print namespace usable. Keep this
private directory out of sharing/indexing/backup recursion. A changed source or
new top-level entry stops retention instead of moving unverified data.

The current Media baseline preserves legitimate writes since phase B. Initial
Z and newly copied Y files receive full SHA256 verification. For already
accepted Media content, the combined check proves unchanged inode, size,
mtime, ctime, metadata and complete namespace against this fresh quiesced
baseline; it does not compare legitimate newer content with the old Z copy.
It is an identity baseline, not a new content-hash or independent recovery copy.

Print flattening consists of atomic same-filesystem child renames. The wrapper
can be removed only after every originally recorded child is reconciled at its
destination inode and it is empty. It uses rmdir only; a late/new entry blocks
removal. Existing filesystem root permissions stay in place; no recursive
chmod/chown is used.

Apply the phase-y OMV contract and `docker-host-y.fstab` replacement entries.
Keep `/export/immich`, `/export/frigate` and their client paths, but retarget
their server-side backing folders to the new filesystem. Retarget the dormant
configs/ha-backups shared-folder binds as well; do not recreate retired exports.
Preserve Immich ownership and Frigate's UID 100000 ACL. Cleanly remount VM103,
Proxmox backup and Frigate mounts; fresh-start CT111 only after its host mount
is proven correct. Do not bind a new mount over containers retaining old handles.

Use `backup-client-commands.txt` to change Proxmox's export while retaining
storage ID `omv-backups`, and HA's NFS path while retaining `nas_backups`, backup
usage/default and schedule. Install the rendered OMV backup script/unit and
MediaMTX backup script after comparing the deployed versions with the prepared
sources; preserve any unrelated live corrections. The OMV script now checks the
exact new filesystem UUID rather than assuming md0 or a particular md device
number. Restore timer schedules only after fresh backup checks pass.

Rename the existing NAS root share to `Print`, keeping filesystem UUID F... on
md0. Reconnect Y to `\\192.168.40.50\Print`. Update Windows and canonical
operational references: `Y:\Print\x` and `nas\Print\x` become `Y:\x` and
`Print\x`; non-Print Y paths become Z/Media paths; Z Media paths lose the Media
prefix, with Calibre's explicit exception. Do not repoint this desktop's separate
`K:\Documents\Ebooks` library. Stop/relaunch old scripts after editing; changing
a source file does not change paths already loaded in a running process.

Use the same Windows prechecks as phase B, then replace Y in its normal user
session after the Print share is ready:

```powershell
$ErrorActionPreference = 'Stop'
Get-SmbMapping -LocalPath 'Y:'
if (-not (Test-Path -LiteralPath '\\192.168.40.50\Print')) { throw 'Print share unavailable' }
# Continue only when the recorded old mapping is expected.
Remove-SmbMapping -LocalPath 'Y:' -UpdateProfile -Confirm:$false
New-SmbMapping -LocalPath 'Y:' -RemotePath '\\192.168.40.50\Print' -Persistent $true
```

After the configuration/mount checks, mark `publish-y` and `flatten-print` as
activated with the same CLI pattern as phase B, then resume only previously
active services. Apply the diagnostics and health-collector patches at this
cutover, not while the old topology is still live. Collector identifiers
`nas`/`14tb` remain compatibility keys; the expected Media UUID changes and
display names should map them to Print/Media. Regenerate OMV monitoring from its
managed configuration and add health/assembly monitoring for the new array.

## Filebrowser composite view

Read-only discovery confirmed one active `admin` account with scope
`{name: /srv, scope: /}` and admin permissions. Recheck before deployment; new
accounts require their own scope review. OMV's Filebrowser service is on 3670,
uses the NAS shared-folder reference, and is generated by the OMV plugin.
`openmediavault-sharerootfs` is installed, so the view can be managed normally.

Create `/srv/filebrowser/Print` and `/srv/filebrowser/Media` on the OS filesystem;
install the rendered mount units and their container-service drop-in. Install
`assert_local_mounts.py` as `/usr/local/sbin/assert-local-storage.py` and its
rendered JSON contract under `/etc/household-storage/filebrowser-mounts.json`.
Create OMV shared folder `filebrowser-view` on the system filesystem, relative
path `srv/filebrowser/`, using the installed rootfs-sharing support. Select that
folder for Filebrowser and regenerate its managed configuration. Do not hand-edit
the generated Podman command or change credentials, port/certificate, account
database or persistent `/var/lib/filebrowser` mapping.

The bind views expose final Print and Media roots under the unchanged container
source `/srv`. The tested Podman bind includes these submounts. The service
requires both view mounts, and its pre-start helper requires four exact whole-
filesystem UUID mounts, preventing an empty local-directory fallback. Keep the
existing process UID/GID 1006:100. Admin access preserves filesystem ACL limits;
private backup data is not made world-readable.

Filebrowser `/Print/...` links retain their meaning. Old non-Print root links
such as `/backups/...` become `/Media/backups/...`. Check saved links and native
indexing/authenticated browsing after the switch. The real-image, network-none,
UID-1006 disposable composite-bind test passed; the live configuration has not
been changed. Do not recursively apply ACLs through the composite view.

## Recovery and acceptance

- Copy interruption: rerun the same copy command before a transformation plan
  is sealed. Final copy/verification must be repeated after any retry. No copy
  may resume into a transformed namespace.
- Same-size/same-time corruption: keep writers stopped; use `copy ROLE --execute
  --final --checksum-repair`, then obtain a fresh zero-issue verification report.
- Source deletions/type changes during warm copying: `reconcile-extras ROLE`
  journal-renames stale target entries into a private quarantine on the same
  new filesystem. It neither deletes them nor changes the source. The quarantine
  is sealed with exact entry identities/generations and a hashed manifest.
  Repeat the cold copy and verification afterwards, including when no extras
  were found; reconciliation invalidates earlier copy completion. Rerun an
  interrupted reconciliation to resume its pending plan. Keep all quarantines
  until the separate final retirement review.
- Namespace interruption: rerun `apply PHASE`; durable intent plus inode checks
  distinguish completed renames from pending work. Unexpected identities or
  destination data stop recovery. No-replace rename is required.
- Before activation, `rollback PHASE` reverses an incomplete/complete namespace
  plan; roll back later phases first. Metadata and touched-parent state are
  restored. After activation or empty-wrapper finalization, automatic rollback
  is closed. Stop writers and reconcile new data/configuration explicitly rather
  than pointing services at stale originals. The retained originals are available
  for that recovery until final retirement.
  A rolled-back plan stays closed; do not discard its journal and reapply it.
  A new reviewed session/generation or explicit recovery procedure is required.
- Before opening writes, final mapped verification must pass with the content
  and identity checks described above, plus metadata and namespace checks.
  Extra system trees are limited to empty maintenance directories, empty
  lost+found and the exact validated sealed quarantines. Arbitrary unpublished
  files cannot hide there; changed quarantine entries block acceptance. Repeat
  exact remote-source and server-side UUID checks after remounts.
- Perform authenticated Calibre login/read/cover/download and a controlled
  metadata update; refresh and compare its stopped-library counts/integrity.
  Exercise Jellyfin playback, Atsumeru reading, qBittorrent recheck/resume with
  VPN intact, MediaMTX recording/playback, Immich upload/read, Frigate recording
  or an explicit fixture if cameras remain disconnected, Filebrowser scopes and
  Windows reconnect/login/read/write. Check all media consumers remain unable
  to browse migrated backup/Immich datasets outside their scoped mounts.
- Run fresh HA, Proxmox, VM103 app-data and OMV config backups and isolated
  restore exercises. Document exact generation IDs and outcomes. HTTP status,
  container running state and backup file existence alone do not pass acceptance.
- Before final cleanup, refresh source/client reference inventories, update
  canonical configs/manuals/current-live-state and wiki as appropriate, and
  disposition historical/copied checkouts explicitly. Offline devices, shortcuts,
  CAD/slicer project links and arbitrary binary embedded paths still require
  native-client checks; this tooling does not rewrite unknown binary formats.

Retained originals and internal empty staging wrappers are a separate final
retirement operation after successful service tests, a fresh backup cycle and
isolated restores. Produce exact candidates from the session receipts, account
for legitimate new destination writes, revalidate retained-source hashes and
identities and close the acceptance record before deleting anything. No broad
recursive deletion command is supplied by the controller. The retention folder
is not permanent final Print content; remove it only through that verified final
retirement step. No extra independent full-data backup is required by this plan.
