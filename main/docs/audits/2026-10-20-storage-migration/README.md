# Print / Media storage migration audit

Date: 20–27 October 2026, Europe/London. Status: Z service/share cutover complete;
Media mirror healthy and synchronized. Y cold sync/full verification and current
Media baseline and combined proof passed; Y originals retained privately and
Print flattened with empty wrapper removed after proof. October27 share/client/
service cutover live; owner access confirmed, fresh backups and isolated restore
checks passed. Verified retained-source/staging retirement completed23:19 GMT.
Operational text references corrected; offline/native binary links remain a
documented client-check limitation, not a claim of universal rewriting.
The owner accepted the temporary
single-copy risk on 20 October 2026 and waived an independent full-data recovery
copy. Execution still requires the device-specific preflight gates below.

## Execution progress — 20–27 October 2026

- **October27 23:38 GMT explicit owner-authorized diagnostic deletion:**459
  Necron diagnostic files freshly SHA256-matched against current production
  Necron library, then exact manifest/inode/generation guarded unlink completed.
  10325643622B logical data removed (~10.3GB). All8 unverified files preserved;
  production originals, directories and synthetic test fixtures untouched.
  Evidence `/root/diagnostics-matched-retirement-20261027/` manifest/execution/
  result; manifest SHA256
  `bf56b4d29b44873467ede66f231b0950e83fb65a79102ae5ab2d89efe648993e`.
  This authorization covered459 matched files only, not whole-folder cleanup.

- **Owner-requested Z folder deletion review (no deletion):** .cleanupweb-source
  and .transferportal-smoke-destination empty; .transferportal-smoke-source only
  three known fixtures/~4MiB; legacy case-collision hold contains empty Media
  directory only. These four are disposable after rechecking emptiness/fixture
  identities at deletion. _codex_diagnostics totals17078667427B/7390 files;
  three synthetic subtrees disposable (focused-20261001-213336,
  sevenzip-20261001-213708, sevenzip-20261001-213911). For actual-necrons and
  later-necrons trees,459 real-model files hash-match current production library
  Y:/Models/Tabletop/GW/40K/Necron;8 were not verified there (possibly partial or
  renamed, not established unique). Keep those two trees pending disposition of
  two Overlord STLs, Loincloth3.stl, Armor_Plate .photon and four Ghost Ark/
  Doomsday Ark ZIP instances. Original multipart archive not found under Models.
  Do not treat entire diagnostic tree as proven disposable yet. TransferPortal
  and smoke mounts inactive/disabled, no corresponding active bind found.

- **October27 final retirement completed:** retained-source job exited0 at
  23:18:29 GMT,10233 exact entries removed using fd-anchored per-inode/type
  checks, no broad recursive deletion. Source manifest SHA256
  `2a4b3bc12e1fd3cbcbd7899e0ae47c7ab3bba0edc378ca35df97beb3a28cc873`.
  Seven private trees and empty retention wrappers removed; live Print/Media
  roots untouched. Y free increased about3.8 to4.4TiB (roughly654GiB reclaimed).
  All52 live deltas reviewed:5 approved merge parents,40 fresh-backup/parent
  changes,6 Immich startup markers,1 Frigate parent update; none unclassified.
- Staging retirement exited0 at23:19:09 GMT:312 sealed stale backup entries and
  eight empty staging directories removed, followed by empty session/maintenance
  wrappers. Quarantine seal validated against SHA256
  `8dcb1d4ea3e4db9bd3b97c3b2aa61f8efd2b97694a9cdf664f38c10b2bfb31ed`.
  Reviewed data was expired Oct12 Docker run, Oct20 CT111/114 dumps, Oct13 HA
  backup and superseded latest log/SQL extras, already absent from frozen source
  after normal retention. Fresh replacement backups/isolated restores had passed.
  No current backup generations, synthetic recording or policy-blocked SMB probe
  deleted. Detailed manifests/journals remain OS-private under
  `/root/household-storage-retirement-review-20261027/`.
- Final reference disposition: vault backup default/guard now Media/configs;
  canonical backup/rebuild docs and recovery checkpoint locations corrected.
  Managed collectd/monit regenerated, stale old-Z monitoring removed, services
  active. Twelve operational household-hub scripts remapped to Y root and parsed
  without execution. Bounded Print scan saw679577 files, scanned3064 text files,
  seven old references in six GW audit scripts/one JSON corrected, syntax checked,
  originals saved privately. Zero scan read errors; binary/native projects were
  not rewritten. Other copied worktrees are obsolete, refresh from canonical
  before future use; dated handoffs/checkpoints/mapping fixtures remain history.
  See `final-reference-disposition.json` for explicit bounds/dispositions.
- Final live checks: Y/Print and Z/Media mappings OK; GW and Calibre roots present,
  intentional `Y:\Models\Telegram` still absent; Print wrapper, retained-source
  and private staging trees absent. Both mirrors `[UU]`; no new kernel storage
  errors, SMB/Filebrowser/collectd/monit/OMV backup timer active. Owner recovery
  waiver unchanged. Operational migration/retirement complete; universal offline
  client/binary embedded-link acceptance is not claimed.

- **October27 retained proof completed20:42:30 GMT; inspected20:43 GMT:** unit
  active/exited status0. Retained-source inode/type/metadata/link/namespace and
  SHA256 checks passed10233 entries,701454752741B hashed, zero issues. Live
  destination states:10181 same verified generation,52 changed for separate
  review, zero missing/type-changed entries. Seven exact retained candidates
  listed in private summary; no deletion performed. Evidence:
  `/root/household-storage-retirement-review-20261027/summary.json` and
  `retained-proof.jsonl`. Both mirrors `[UU]`; Media disks SMART passed with
  sector/CRC attributes zero; no new kernel storage errors. Y3.8TiB/Media6.2TiB
  available. Completed monitor removed. Refreshed reference scan completed:
  7026 local text files/434 matching files, five hosts, zero read errors; raw
  matches include historical/prepared evidence and still need disposition.
  Owner confirmed intentional deletion `Y:\Models\Telegram`, unsure of others;
  do not recreate it or treat every other unknown missing path as approved.
  This Print path is outside the non-Print retained receipt. Next: review52
  destination changes and residual active references, then exact retirement.

- **October27 owner steering during retirement review:** owner deleted a couple
  of unneeded live folders; exact paths requested for disposition. Missing live
  destinations must not be automatically recreated. Retained-source proof stays
  separate from intentional live changes; do not infer every missing path was
  approved merely from this general statement. At19:48 GMT the reference scan
  completed (7026 local text files, five hosts, zero read errors); retained hash
  audit still running, about56.6GB read of roughly701GB logical data. ETA is
  approximate and depends on sequential backup-file throughput.

- **October27 about19:40 GMT retirement review started (owner continue):**
  read-only `household-storage-retained-proof-20261027.service` rehashes retained
  Y regular files against the sealed cold receipt, checks inode/type/metadata/
  link counts and exact retained namespace; only expected top-directory rename
  ctime changes are exempted. It records current destination generation changes/
  missing entries separately for live-write/retention disposition. Seven exact
  retained top-level candidates derive from retain-y plan, not wildcard discovery.
  No deletion is implemented. Runner/evidence:
  `/root/household-storage-retirement-review-20261027/`.
  A separate refreshed bounded text/config reference inventory is running across
  both local project roots and five hosts; private output
  `C:\Users\Admin\.codex\storage-migration-final-reference-20261027`.
  Generated/historical/copied/native embedded paths require explicit disposition;
  this scan does not rewrite binary CAD/slicer projects. Live shares/apps remain
  available. Retained/quarantined data and prior known fixtures remain untouched.

- **October27 about19:24–19:33 GMT service cutover:** activated publish-y and
  flatten-print boundaries before writes; Y root RW, NAS shared-folder identity
  preserved/renamed Print. Windows Y -> `\\192.168.40.50\Print`, Z -> Media,
  both create/read/remove-owned-fixture passed. Owner confirmed usual Y files,
  Immich and authenticated Filebrowser Print/Media access. Original root group/
  mode remain0:100/2775. Initial ShareMgmt rename saved its configuration but
  chgrp failed on frozen root; subsequent Samba deployment after controlled RW
  transition succeeded with correct Print path, no recursive permission change.
- Four OMV folder refs (Immich/Frigate/configs/ha-backups) retargeted new Media;
  three managed backup exports created with original exact clients/root mapping.
  Legacy physical-path exports retired. NFS first deployment found old exported
  binds busy; exports withdrawn/server stopped, clean unmount succeeded, then
  managed fstab/NFS redeployment passed. No lazy/forced unmount issued by agent.
  All twelve export binds now backed by new Media, no retained-Y export aliases.
  Seven VM103 mounts checked/recreated; Proxmox omv-backups ID/content/retention
  preserved with new export, HA nas_backups active/default at new scoped export.
  Live PVE version rejects mutable --export; exact checkpointed storage.cfg line
  changed instead. HA automatic schedule unchanged. Backup scripts/source guards
  updated; canonical NFS and deployed scripts reconciled. Undeployed coordinated
  Hub helper's source guard updated canonically, no new service deployed.
- Media/Immich containers recreated without pulling images; VPN container left
  running. Frigate CT111 running/healthy and mapped-UID write/read/remove test
  passed; no live-camera recording claimed. Watchtower monitor-only restored.
  OMV/VM103 backup timers, Bambuddy timer and both Proxmox backup jobs restored
  to prior active state. TransferPortal stays retired. Filebrowser managed OS
  composite view active, four local UUID guards pass; admin scope/account intact.
  Actual current UID994:100 preserved (older prepared UID1006 claim superseded).
- Fresh backups: OMV20261027T192738Z checksums + isolated XML restore/parse pass;
  HA full unprotected a6090ad7 on nas_backups,183398400B, nested archive3105
  entries and five selected config files restored offline (HA not booted).
  Docker app-data20261027T192711Z completed19:31:29 exit0; isolated Calibre-Web
  app.db/gdrive.db and Atsumeru users.db/library.db quick_check=ok. MediaMTX
  config checkpoint exit0. Proxmox CT111 backup19:29:10 passed, archive2.09GB;
  first attempt lacked scheduled job's /var/tmp and failed on NFS temp permissions,
  retry with /var/tmp passed. Full archive restored to temporary stopped CT105,
  NIC/data binds/devices removed before mounting; Frigate Compose/config hashes
  match live. Never booted, unmounted and temporary CT/root disk removed.
  Evidence `/root/household-storage-cutover-y-20261027/` on OMV/Proxmox;
  VM103 restore evidence under cold-y checkpoint's isolated-app-restore/.
  No retained originals/quarantines or known synthetic/SMB fixtures deleted.

- **October27 terminal layout confirmed19:23 GMT:** combined proof passed
  16:06:57 GMT,412464 entries/zero issues. Report
  `/root/household-storage-state-20261021/final-combined-55c5f9af35a04df89d581bfa782d5201.jsonl`,
  SHA256 `664f314d8d650be27991ed38ed2060686062a71c3b9826b17528ff62d12e51cb`.
  retain-y journal completed16:07:01; flatten-print completed16:07:04 and its
  journal records wrapper-intent/wrapper-removed only after complete proof.
  Print wrapper absent; original non-Print trees retained under root-owned mode
  2700 `.household-retained/household-20261021/` on Y. No retained data deleted.
  Runner refroze Y at16:07:05, unit active/exited status0. Both mirrors `[UU]`;
  Y root/all aliases still VFS+FS RO. Shares/services/client mounts remain paused;
  actual share rename/reconnect, exports/backups/Filebrowser and acceptance are
  next. Completed layout monitor removed. Independent recovery waiver unchanged.

- **October27 14:45 GMT owner-authorized layout continuation:** prepared/applied
  publish-y through the journal controller. No overwrite/leaf collision allowed;
  only five reviewed parent merges. New unit
  `household-storage-layout-y-20261027.service` started14:45:48 GMT and runs
  final-verify combined first. ONLY if that succeeds, it rechecks healthy mirror
  and stopped OMV writers, remounts Y root writable for controller (export aliases
  remain VFS RO), prepare/applies retain-y then flatten-print and proof-gated
  remove-print-wrapper. Finally refreezes Y root RO even on layout failure.
  It does not activate services, retarget shares, alter clients or delete retained
  originals. Logs/runner/execution.jsonl:
  `/root/household-storage-layout-y-20261027/`. No competing layout commands.
  Combined verification rehashes incoming Y and checks previously accepted
  current Media against its frozen identity baseline. Runtime maintenance and
  owner recovery waiver below remain unchanged. Config/service cutover still
  requires reviewed namespace completion and mount/backup/client acceptance.

- **October27 terminal cold proof, inspected14:26 GMT:** unit active/exited,
  MainPID0/ExecMainStatus0. Full Y SHA256/metadata verification completed
  12:41:21 GMT:10234 entries, zero issues; receipt
  `/root/household-storage-state-20261021/verify-y-a4c7e264801c47f9910fa96af026e108.jsonl`,
  SHA256 `c6713191e7ec270d8a058750a913b3eddc2a8c0f9121a75ddb41bf998a09733e`.
  Fresh current Media identity baseline completed12:41:58 GMT:402236 entries,
  zero issues; report `live-z-e2eb363549cc4a6a83814cca586f164f.jsonl` in same
  state directory, SHA256
  `f41a5554e7b4109601d336bc15a3e7b379bac5c006a49f7432d627478afa8927`.
  Baseline is identity/metadata proof, not a fresh full-Media hash or recovery
  copy. Reconciliation retained312 stale-stage entries in sealed private
  `quarantine-y-e492585aed884071b759837eedecb8a2`; no data deletion.
  Both mirrors `[UU]`, Media degraded0/idle, exact members/UUID confirmed;
  SMART sector/CRC attributes zero, no new kernel errors,6.2TiB free. Y root/all
  aliases still VFS+FS RO; Media export aliases VFS RO. Maintenance remains as
  recorded below. No publication/Print changes/services restored by monitor.
  Completed cold monitor removed; next reviewed section C cutover and acceptance.

- **October27 cold Y started10:21:12 GMT:** unit
  `household-storage-cold-y-20261027.service` runs frozen conflicts,
  reconciliation, final Y copy, full verification and snapshot-live-z ONLY.
  Frozen scan passed10:21:16 (Y10233/Media402235 entries, five approved merges).
  Reconciliation exit0 at10:21:19; final copy exit0 at10:21:20; hashes running.
  No publication, original retention, Print moves or service activation.
  Private runner/logs/checkpoints on OMV/VM103/Proxmox/HA:
  `/root/household-storage-cold-y-20261027/`. Initial10:20 preflight wrapper
  failed before data operations on expected systemctl inactive exit3; corrected
  wrapper, retained failed evidence and restarted successfully.
- Maintenance: Y root/all four aliases VFS+FS RO; five Media export aliases
  VFS RO, target root RW for controller. smbd stopped/runtime-masked; OMV config
  backup timer paused. Filebrowser paused, TransferPortal retired. VM103
  Watchtower, four Immich containers and five Media apps stopped; app-data,
  MediaMTX backup/Bambuddy timers paused (oneshots inactive). Seven client NFS
  mounts cleanly unmounted and mount/automount paths runtime-masked.
  Atsumeru SIGTERM initially relaunched under restart policy; corrected sequence
  issued Docker indefinite graceful stop BEFORE verified Java-child SIGTERM.
  Final stopped143, no SIGKILL. Proxmox two backup jobs and omv-backups storage
  disabled temporarily, no active backups; Frigate stopped, CT111 shut down,
  both NFS mounts unmounted. Preserve checkpointed schedules/retention/states.
- HA Core/safety functions remain live. SSH add-on lacks Core API permission
  to change automatic schedule, so NAS backup mount detached through Supervisor
  instead; exact mount/default/backup config saved privately. Current mounts
  empty/default null; daily03:00 schedule and14-copy retention unchanged.
  Restore nas_backups/default after reviewed retargeting. Do not restore old
  source mounts or clear masks before cutover. SMB/Media/Immich/Frigate stay
  unavailable through proof. Independent full-data recovery waiver unchanged.

- **October27 warm retry completed09:25:21 GMT; inspected10:14 GMT:**
  `household-storage-warm-y-retry-20261027.service` active/exited, MainPID0,
  ExecMainStatus0; session copy-finish role=y code0 final=false. Private report
  `/root/household-storage-state-20261021/copy-y-9989cc20c5d444058ff7040fe7e4f84c.log`
  lists10234 entries (8281 regular),701454752762B logical size,254 regular files
  transferred/70619881482B, zero deletions. Both mirrors `[UU]`, Media degraded0/
  idle, exact MD UUID/members; both Media SMART sector/CRC attributes zero and
  health passed, no new kernel storage errors,6.2TiB available. This is warm
  staging only, not cold-copy/hash/layout/application acceptance. Y originals
  and Print remain unchanged. Completed retry monitor removed. Next: recorded
  writer/schedule shutdown and frozen-source reconciliation/final sync/full
  verification before snapshot-live-z and guarded publication/Print flattening.

- **October27 owner-authorized continuation, about09:14 GMT:** reviewed active
  Proxmox02:00 backup/prune job (`34c415cb-dd1b-47c4-b764-69a01aa87312`,
  keep-daily7/monthly6), consistent with vanished older dumps during the first
  warm pass. Media/md0 both `[UU]`. New unit
  `household-storage-warm-y-retry-20261027.service` resumes ONLY `copy y --execute`
  under the same pinned controller/session. Log:
  `/root/household-storage-y-stage-20261025/warm-retry-20261027.log`.
  No writer shutdown or namespace mutation yet. Refreshed live namespace scan:
  Y non-Print10233 entries, current Media402235 entries, no read errors; exactly
  the five approved directory merges and no other collisions. Private SQLite:
  `/root/household-storage-y-stage-20261025/conflicts-20261027.sqlite`.
  Windows Y/NAS and Z/Media mappings OK. This live scan is not cold proof.

- **October27 09:05 GMT read-only monitor:** Media mirror confirmed healthy
  `[UU]`, degraded=0, sync_action=idle, exact MD UUID and both expected members.
  Runner recorded healthy-mirror-confirmed at01:00:10 GMT and began Y warm copy.
  At02:51:49 GMT it stopped with controller exit1 because rsync returned24:
  seven source backup files vanished during the live copy (six Proxmox dump/log
  files and one Immich database backup). This is incomplete warm staging, not
  accepted verification. Private evidence: execution.jsonl under
  `/root/household-storage-y-stage-20261025/` and
  `/root/household-storage-state-20261021/copy-y-6b3aa73e0e5143c083a75b66995f7cfa.log`.
  Rsync reported8267 regular files transferred,702041629953B total logical size.
  Both Media disks pass SMART; attributes5/196/197/198/199 zero, no new kernel
  storage errors; Y md0 `[UU]`, target6.3TiB available. No retry, source move,
  deletion, service change or namespace publication performed by the monitor.
  Next: review live backup retention/writers and refreshed conflicts, then the
  planned writer shutdown, reconciliation/final sync and full verification.
  Independent full-data recovery waiver remains. Terminal monitor removed.

- **Current resume point, October25 19:49 GMT:** original Z partition1, serial
  `3GHV81YE`, added to Media MD UUID `fd8de871:2fcb43a8:d97ff800:008ccb6b`.
  Rebuild started from verified serial `3HG402GN` partition1; expected `[U_]`
  while recovery runs. Initial194,618KiB/s/about1338 minutes is an estimate only.
  Existing Y md0 stays healthy `[UU]`. Old original-Z ext4 UUID retired and
  filesystem signatures removed: **no independent original-Z rollback copy**
  remains, consistent with owner waiver. Small configuration/GPT/signature
  checkpoints remain OS-private; no independent full-data copy was required.
  Selected current evidence: `z-cutover-and-mirror-start.json`; at19:56 GMT
  recovery was progressing with143,383,424/31,251,490,816 sectors synchronized
  (about0.46%) and the Y staging unit was waiting normally.
- Member-add safeguards: `check-original-z` confirmed all402,234 source entries
  unchanged. Retired old broad export/media folder config with `recursive:false`;
  all four TransferPortal binds and its service stopped/disabled. Original FS
  cleanly unmounted through OMV, no shared-folder refs/mounts/holders remained;
  serial/size/SMART rechecked. Only exact stable original-Z partition was wiped/
  added. MD configuration/initramfs persistence succeeded; md0 never targeted.
- Z now maps `\\192.168.40.50\Media` (OK); Y remains NAS until Print cutover.
  Five scoped NFS exports use new Media UUID; VM103 source assertions pass.
  Calibre host `/mnt/omv/calibre-library` -> `/books`; SQLite quick_check=ok,
  10548 books/11031 formats. Five media containers recreated, settings/images
  retained. qBittorrent's actual project is `download-gateway`; unchanged VPN
  namespace remains Mullvad-recognized. Monitor-only Watchtower and MediaMTX
  backup timer restored. Filebrowser paused/runtime-masked pending composite
  view; TransferPortal remains retired. Y service/backups paths have not moved.
- Acceptance: UID1007:100 scoped create/read/remove-own-fixture passed for
  Calibre-Web/Atsumeru/qBittorrent. All four Jellyfin mounts reject writes.
  MediaMTX authenticated synthetic publish/view/decode created531431B recording
  on new Media; completed file decoded in network-none disposable process.
  Jellyfin has no configured users; no household login/playback claimed.
  Owner directly answered **confirmed** to Calibre-Web/Atsumeru library/login
  and qBittorrent login acceptance. Automated stored-credential probe returned401;
  credentials untouched, no successful API login/torrent recheck falsely claimed.
- Canonical/live scoped diagnostic commands updated; static dashboard rebuilt/
  deployed, nginx validates. Prior image retained as
  `household-storage-dashboard-before-20261025:checkpoint`. Prepared collector
  source expects Media UUID; collector schedule/shipping remains undeployed.
  Renderer handles already-cut-over templates/omits empty patches;75 Linux
  tests still pass after canonical source changes.
- `household-storage-stage-y-20261025.service` waits up to72 hours for Media
  degraded=0/sync_action=idle and pinned membership, then ONLY `copy y --execute`,
  excluding Print. No Y source moves/deletions or cold acceptance. Runner/logs:
  `/root/household-storage-y-stage-20261025/`. Hourly
  `check-media-rebuild-and-y-staging` monitors quietly. Next after staging:
  refreshed collisions/references, Y cold sync/full proof and quiesced current-
  Media snapshot before guarded merge/retention/Print flattening. Exact Z
  cutover/member-add/config/application logs remain private under
  `/root/household-storage-cutover-z-20261025/` on each relevant host.
- Retained owned fixtures:531431B synthetic recording at
  `phone-recordings/garage-phone/2026-10-25_19-41-55-906311.mp4`;17B hidden
  `.migration-smb-probe-9772835e4ef34a609105a72164f5fcbb` at Media root.
  SMB create/read succeeded. Hidden-file cleanup needed Force; automatic
  approval review blocked both scoped removal attempts with only “blocked by
  policy”. Retained for explicit cleanup; no denial bypass via another tool.

- **Current resume point, confirmed October25 16:37 GMT:** final destination
  layout verification passed at **October25 09:46:47 GMT**, 402,233 checked
  entries, zero issues, complete terminal receipt. Both systemd jobs exit0,
  active/exited with MainPID0. Staged verification had passed October24
  16:11:12 BST with402,234 entries and all8,381,330,552,140 regular-file bytes
  checked. Flatten/publish journal steps completed October24 16:12:28 BST;
  the redundant Media wrapper is absent from the published namespace, explaining
  the one-entry difference. Calibre is at the new filesystem root's
  `calibre-library`; no service/share activation occurred.
  Final report: `/root/household-storage-state-20261021/final-z-5cd23de76ddc418a81e7f557f42ce2b2.jsonl`,
  SHA256 `20fee82a1e9b2c88196f6ea5090c3e7a73723ec31e22c9ebc510a1b622d5f71a`.
  Selected evidence: `final-z-completion.json`; full journals/phase logs remain
  private in the recorded session/layout directories. Original Z and all bind
  aliases remain read-only; md0 healthy `[UU]`, new Media expected `[U_]`,
  available7,518,855,913,472 bytes, no matching kernel I/O/filesystem errors.
  Completed monitor deleted. Next is reviewed OMV scoped exports/SMB/VM103 mounts/
  Compose cutover, application acceptance and only then original-Z repurposing.
  Writers/services remain stopped; owner independent-recovery waiver preserved.

- **Historical continuation, October24 15:55:33 BST:** owner said `continue`;
  started `household-storage-layout-z-20261024.service`, currently waiting for
  cold-unit exit0 AND its explicit `verified-staging-complete` event. Then it
  rechecks source read-only, target array identity and stopped OMV writers;
  runs tested prepare/apply flatten-z, prepare/apply publish-z, final-verify z.
  Controller validates sealed receipt hashes and target inode generations before
  changing anything. No overwrite, service activation, share rename or disk
  repurposing. Original Z/Y retained. Waiting expires after six hours without
  interrupting the cold job; any phase error halts progression. Exact runner,
  launch command and logs: `/root/household-storage-layout-z-20261024/`.
  At queue time staged verification had checked8.29TB with zero issues and no
  terminal receipt. Layout changes are QUEUED, not yet confirmed executed.
  Existing `check-media-cold-sync-and-verification` now follows BOTH units until
  final-layout proof/error; ordinary transitions stay quiet. Stop queued/layout
  unit before deliberate thaw/recovery. Reviewed NFS/SMB/Compose cutover and
  application acceptance remain next gates; do not erase original Z.

- **Historical cold start, October23 09:19:55 BST:** cold runner
  `household-storage-cold-z-20261023.service` active/running on OMV. It checks
  source freeze before each step, then runs `reconcile-extras z`,
  `copy z --execute --final`, and `verify z`, all with `--writers-stopped`.
  It halts on every nonzero result and does not flatten/publish or change shares.
  Evidence/runner/phase logs: `/root/household-storage-cold-z-20261023/`;
  session receipts stay in `/root/household-storage-state-20261021/`.
  Reconciliation finished exit0 at09:22:14 BST; cold final copy then started.
  Selected initial job/maintenance evidence: `cold-z-start.json`.
- VM103 Watchtower, Calibre-Web, Jellyfin, Atsumeru, qBittorrent and MediaMTX
  stopped; MediaMTX backup timer stopped. Atsumeru's PID1 shell failed to forward
  Docker SIGTERM: sent graceful SIGTERM to its uniquely verified Java child in
  the same container, after which it exited. No SIGKILL used. Original media
  NFS mount cleanly unmounted, mount/automount runtime-masked. On OMV,
  Filebrowser and TransferPortal stopped/runtime-masked. Private before-state,
  Compose/fstab/config and stopped Filebrowser checkpoints on both hosts under
  `/root/household-storage-cold-z-20261023/`; only previously active services
  are candidates for later restart.
- Original Z root and all three known bind aliases are confirmed **VFS and
  filesystem read-only**, exact source UUID pinned. This freezes SMB writes
  too; Y's filesystem remains writable and unchanged. No data deletion,
  namespace publication, share rename or second-member addition performed.
  Media applications, downloads/recording, Filebrowser and TransferPortal remain
  unavailable during cold work. Full hashing may run into the following day.
  Hourly `check-media-cold-sync-and-verification` monitors quietly, reports a
  terminal result/error and cannot advance cutover. Do not restart writers or
  unmask the old VM103 media mount during this stage. At cutover, remove its
  old fstab entry before clearing those mount masks.

- **Warm-copy completion, confirmed October23 09:06 BST:** initial Z warm copy
  completed successfully on **October22 23:30:54 BST**, systemd exit0,
  active/exited with MainPID0. Session journal records `copy-finish`, role z,
  code0, **final:false**; service output is `{"copied":"z"}`. Rsync reports
  402,234 entries (357,772 regular files,44,462 directories), all357,772 regular
  files transferred, **8,381,330,552,140 bytes**, zero deletions. Full private
  log: `/root/household-storage-state-20261021/copy-z-4d88c5409660488d93d3b6c3af32a9a3.log`.
  At observation target used8,354,624,450,560 bytes with7,518,855,913,472 bytes
  available; allocated usage differs from logical transfer size. Exact target
  UUID confirmed, original Z serial/UUID still present, Y md0 `[UU]`, new Media
  still expected `[U_]`. No matching kernel I/O/filesystem errors since preflight.
  Selected evidence: `warm-copy-completion.json`. This is warm-copy success
  only; no cold sync, SHA256/layout/service acceptance or cutover has occurred.
  Completion monitor `check-media-warm-copy` deleted; next is the runbook's
  externally quiesced reconciliation/cold sync and verification. No restart,
  service stop, data move/delete or disk-add operation ran during this check.

- **Historical start, October21 about15:48 BST:** original Z warm staging
  copy running under `household-storage-copy-z-20261021.service` on OMV.
  Systemd reports active/running and rsync processes were observed;
  target used space was5.55GB at15:49 BST. This is progress, not copy acceptance.
  At15:52:56 BST target used space was53.03GB and the unit remained running;
  no matching kernel I/O/filesystem errors since preflight. Selected evidence:
  `warm-copy-start.json` (unit activation15:48:44 BST).
  The new filesystem is ext4 label `Media`, UUID
  `a8843f98-c937-48a8-aefa-4cd0fb80667c`, mounted through OMV at
  `/srv/dev-disk-by-uuid-a8843f98-c937-48a8-aefa-4cd0fb80667c`.
  It backs `/dev/md/media` (currently md127), MD UUID
  `fd8de871:2fcb43a8:d97ff800:008ccb6b`, metadata1.2, internal bitmap,
  two configured slots with ONLY serial `3HG402GN` partition1 present.
  `[U_]` is intentional until verified Z cutover permits adding original Z.
  Existing Y md0 remains `[UU]`; original Z remains mounted and unchanged.
- Fresh preflight at15:43 BST confirmed all four health assessments pass and
  no reallocated/pending/offline-uncorrectable sectors. Existing sda CRC1 and
  sde historical SMART exit32 remain documented warnings, not new faults.
  Fourth-disk recursive NTFS inspection again found only Windows housekeeping;
  exact identity, no mount/holder, size and completed extended test were guarded
  immediately before repurposing it. Saved GPT/NTFS head/tail metadata and
  private OMV config checkpoint on the OS disk. The owner's independent
  full-data recovery waiver remains in effect.
- Fresh live layout inventory: **1,139,650 entries**, exactly the same five
  reviewed directory merges, no other issues. It remains a live snapshot.
  Private checkpoint/inventory/tool copies/execution logs:
  `/root/storage-migration-preflight-20261021T144508Z/`. Hardware commands and
  exit results are in `hardware-execution.jsonl`; persistence logs confirm
  successful `omv-salt deploy run --no-color mdadm fstab initramfs`.
- Copy state: `/root/household-storage-state-20261021/`; runtime controller:
  `/root/storage-migration-preflight-20261021T144508Z/tools/migration.py`;
  session `household-20261021`; destination
  `.household-migration/household-20261021/stage-z/` on new Media. Copy is
  `rsync -aHAXSx --numeric-ids --protect-args --modify-window=-1 --partial
  --stats --fsync`, without delete/inplace/source-removal. It runs independently
  of SSH via a systemd unit, Nice10/IO priority7, no automatic restart.
  Existing services/SMB clients stay available during this warm copy.
  Hourly heartbeat `check-media-warm-copy` monitored quietly until completion;
  it was deleted after recording the terminal result. Actual-UUID configuration artifacts
  rendered outside the vault; all three patches apply cleanly, none deployed.
- **Next:** successful warm-copy exit is only the staging checkpoint. Stop
  affected writers/clients, reconcile stale staging entries, cold final sync,
  full SHA256/metadata verification, journaled flatten/publish and mapped proof
  must precede service/share cutover. Do not add original Z to the array yet.
  Follow [the runbook](../../../tools/storage-migration/cutover-runbook.md).

- **21 October 14:38:54 BST: extended SMART test confirmed passed** on exact
  serial `3HG402GN`, model `WDC WD160EDGZ-11B2DA0`, capacity
  16,000,900,661,248 bytes. Read-only `smartctl -i -c -l selftest -H -A`
  reports execution status 0 and log entry #1 `Extended offline`,
  `Completed without error`, 00% remaining, lifetime 27578 hours, no failing
  LBA. This is the newly completed test started October20: the prior check at
  October21 13:41:48 BST still reported 10% remaining and no logged tests.
  Completion occurred between those observations; its exact wall-clock time
  is not exposed by this log. The original 22:20 estimate was conservative.
  Overall SMART health PASSED; attributes 5/196/197/198/199 are all zero;
  temperature 36 C. Selected evidence: `smart-extended-completion.json`.
- The completed-test heartbeat `check-media-mirror-disk-test` was deleted after
  recording the terminal result, so no further polling is scheduled. Only
  read-only disk inspection and local documentation updates ran. Fresh device/
  writer preflight remains required before the separate migration procedure;
  no array, filesystem, share or household data was changed.

- Owner requested continuation. Extended SMART test started at approximately
  14:38 BST on exact disk
  `/dev/disk/by-id/ata-WDC_WD160EDGZ-11B2DA0_3HG402GN`, serial `3HG402GN`.
  Before starting, identity, 16 TB capacity, unmounted NTFS partition and idle
  test status were rechecked. `smartctl -t long` confirmed test initiation;
  subsequent `smartctl -c` confirmed it running.
- Device estimate: 1,902 minutes, finishing 21 October at 22:19:57 BST.
  This is an estimate, not a passing result. The source Z disk was not tested
  or interrupted; no formats, array creation, data transfers or share changes ran.
- Hourly thread heartbeat `check-media-mirror-disk-test` monitored this exact
  test quietly while normal; it was deleted after the passing result above.
  It performed no destructive migration.
- Read-only layout planner and tests added under `main/tools/storage-migration`.
  Fourteen tests pass on OMV Linux; twelve pass on Windows with two Linux-only
  tests skipped. Covered mapping, hidden/empty paths, collisions, output/root
  guards, missing/symlinked wrappers, hardlinks/symlinks/sockets and exact
  preservation of metadata integers outside SQLite's signed 64-bit range.
  An initial live scan exposed that range issue. A retry exhausted the small
  RAM-backed `/var/tmp` overlay. Only the two generated incomplete SQLite
  databases/journal were removed, restoring that temporary space; no source
  entries were removed. Full inventories now use persistent `/root` ext4 with
  a free-space check and SQLite scratch files there.
- Follow-up at 19:31 BST: disk identity confirmed, extended test still running
  with 70% remaining; SMART health passes and bad-sector attributes remain zero.
  No completed extended-test log entry exists yet. Preserve the original finish
  estimate as an estimate rather than deriving an ETA from coarse percentages.
- Full read-only layout inventory completed at 14:49 BST on persistent OS
  storage: **1,134,167 entries**, five directory-merge reviews, no read errors
  or leaf/type/case conflicts. Full 958 MiB SQLite evidence remains private at
  `/root/storage-migration-20261020-v6kra242/layout.sqlite`; selected summary is
  `layout-plan-summary.json`. Counts differ from the earlier traversal because
  this is a later live snapshot; neither establishes a frozen generation.
- All five merged directory pairs have differing ACLs, even where owner/mode
  match. `merge-permissions.json` records the comparison. Final shared parent
  policy: preserve the incoming Y directory's ownership, mode and ACLs for these
  five parents; retain each existing Z child's own metadata. In particular,
  root-owned Y backups metadata takes precedence over the media-owned old Z
  backups parent. Record these five deliberate parent-metadata exceptions in
  final-layout verification; do not recursively apply the parent policy.
- Added Linux read-only `verify_copy.py` for original-layout staged copies.
  SHA256, names/types, numeric ownership, modes, nanosecond mtimes, ACL/xattr
  digests, symlinks, hardlinks, sparse materialisation, special files and changes
  during verification are checked. Requires externally quiesced writers and
  separately validated source/target mounts. No deletion authority is emitted.
- Waiting-time preparation complete: guarded rsync controller, atomic no-replace
  rename journal, interruption/resume/rollback, staged and final-layout checks,
  sealed stale-copy quarantines, original-Y retention and proof-gated empty
  Print-wrapper removal. Source payload deletion is not implemented; original
  retirement remains gated on application/backup/isolated-restore acceptance.
- Latest verification: **75 Linux tests passed**, including real disposable
  rsync, full namespace cutover, interruption/rollback, ACL/xattr/hardlink/sparse
  preservation, wrong UUID/case/overwrite refusal, late Print entries, damaged
  receipts, stale staging quarantine and legitimate Media writes before the Y
  merge. Windows: 19 pass, 56 Linux-specific skips. Fixture copying requires
  `--modify-window=-1` for exact nanosecond preservation. Reproduce with
  `python main/tools/storage-migration/run_linux_tests.py`.
- Prepared configuration renderer covers ten scoped NFS exports, VM103 mounts,
  Calibre-Web, backup clients/scripts, Filebrowser view and monitoring/diagnostic
  patches. All 17 artifacts render; all three patches pass `git apply --check`
  against the current canonical sources. Python/JSON and rendered shell syntax
  checks pass. No deployment ran. See the command sequence, writer shutdowns,
  Windows remapping, acceptance and recovery in
  [the cutover runbook](../../../tools/storage-migration/cutover-runbook.md).
- Filebrowser active database identified from its live process descriptor.
  Two identical read-only snapshots and valid Bolt metadata identify transaction
  80634, with one admin account scoped to `/srv` + `/`; sanitized evidence is
  `filebrowser-active-users.json`. Installed rootfs-sharing support permits an
  OMV-managed composite Print/Media view. A disposable real-image Podman test
  confirmed both nested bind views are visible as process UID 1006. Fixtures
  were cleaned; live Filebrowser settings/accounts are unchanged.
- Initial Z and incoming Y receive full SHA256 verification. Since Z becomes
  live before Y moves, the later combined check uses a fresh quiesced identity/
  metadata baseline for already accepted Media entries, preserving legitimate
  new writes. It checks inode/size/mtime/ctime and namespace through the merge;
  this baseline is not a new content-hash or recovery copy.
- Preparation-only status at the end of October20: no household data copy,
  rename, format, RAID or share change had occurred. Disposable tests stayed
  in temporary OS-disk directories and network-isolated containers. October21
  hardware preparation and initial warm copy are recorded above; cold-copy,
  native-client and backup/restore acceptance remain outstanding.

## Requested outcome

| Current location | Final location |
|---|---|
| `Y:\Print\*` | `Y:\*` |
| Everything else at Y root, including hidden entries | Same relative path at Z root |
| `Z:\Media\*` | `Z:\*` |
| `Z:\Media\books\calibre-library` | `Z:\calibre-library` (exception to the preceding rule) |
| Other existing Z-root entries, including ISO and the case-collision hold directory | Retained at Z root |
| `\\192.168.40.50\nas` | `\\192.168.40.50\Print`, mapped as Y |
| `\\192.168.40.50\14tb` | `\\192.168.40.50\Media`, mapped as Z |

Owner chose actual SMB share renames, moving all non-Print data, a staged copy,
and source cleanup only after recovery checks. Z must become mirrored first.
Removing Print and Media wrappers is conditional on complete reconciliation
and confirmed emptiness, not merely a successful transfer command.

## Findings and blockers

### 1. Four disks are present; only Y is mirrored

| Observed device | Model | Current purpose |
|---|---|---|
| sda | WDC WD160EDFZ-11AFWA0 | Y RAID1 member |
| sde | ST16000NM001G-2KK103 | Y RAID1 member |
| sdc | WDC WUH721816ALE6L4 | Z standalone ext4 |
| sdd | WDC WD160EDGZ-11B2DA0 | Unmounted NTFS, label New Volume |

All four are 16,000,900,661,248-byte disks. `md0` is clean RAID1, two active
synchronised members, zero failed devices. Both `lsblk` and the MD metadata
inspection establish that Z is a direct ext4 partition, not the second mirror.

Y filesystem UUID: `fdb92af7-371c-4793-8d98-ff47e961498d`.
Current Z filesystem UUID: `a216b8bb-708e-4342-a5be-a415cdc465fa`.
Use stable disk-by-id identity and serial verification for execution, never
assume these sda/sdc/sdd/sde letters will remain stable.

All four SMART health assessments pass, with zero reallocated, pending and
offline-uncorrectable sectors. sda has one recorded interface CRC error; this
alone does not establish a failed disk. No new self-tests were started.
Existing logs show a successful short test on sdc and successful short/extended
tests on sde; sda and sdd have no logged self-tests.

Recursive read-only `ntfsls` found only Windows housekeeping on sdd:
Recycle Bin desktop.ini, System Volume Information tracking.log and
WPSettings.dat. This is evidence for reuse, not an instruction to wipe it.
Revalidate the exact device and contents immediately before any destructive step.

### 2. Capacity fits; temporary single-copy risk is owner-accepted

Approximate allocated-byte observations:

| Dataset | Decimal size |
|---|---:|
| Y Print | 10.792 TB |
| Y non-Print to migrate | 0.699 TB |
| Entire current Z, including ISO | 8.381 TB |
| Of that, Z Media | 5.108 TB |
| Of that, Z ISO | 3.274 TB |
| Z free at initial inspection | 7.492 TB |
| Y free at initial inspection | 4.388 TB |
| Expected final Media allocated content | about 9.080 TB |

These are live, non-atomic measurements. A new filesystem's overhead, sparse
files, hardlinks, ongoing writes and checksum manifests must be accounted for.
Neither the 5.108 TB Media folder alone nor the share's apparent drive name
represents all the data on Z.

Y's free space cannot hold a complete independent 8.381 TB copy of Z.
No independently verified full-Z backup was established by this audit.
The owner explicitly chose to proceed without an independent recovery copy.
After the fourth-disk copy has passed full verification, original Z may be
repurposed under the reviewed execution procedure. From that point until
synchronisation finishes, the fourth disk is the only complete data copy.
A failure of that disk can lose data; the owner accepts this risk. A degraded
one-member array is not a second backup. This waiver removes the independent
data-backup gate, not checksum, identity, health, configuration-checkpoint or
cleanup verification requirements. It does not request deletion of any
existing backups.

### 3. Directory merges are required, but no overlapping file conflicts were found

The case-insensitive destination comparison found five directory overlaps:
`backups`, `_codex_diagnostics`, and three diagnostic subdirectories.
Recursive inspection of their intersecting paths found no file/type conflicts.
Re-run this check after writers are stopped; the namespace changed during the
audit, including temporary Calibre working folders disappearing between listings.

The full directory traversal recorded:

| Share | Regular files | Directories | Symlinks | Special entries |
|---|---:|---:|---:|---:|
| Y | 646,492 | 72,610 | 1 | 17 |
| Z | 357,772 | 44,461 | 0 | 0 |

There were no traversal errors or case-only sibling collisions at that time.
The relative symlink is `backups/configs/omv-config/latest`, pointing into its
own runs directory. All 17 special entries are archived qBittorrent IPC sockets
in backup generations/latest. Preserve their types and metadata rather than
following links or treating everything as ordinary Windows files.

Keep `__hold_media_case_collision_20260802` as existing data. Its historical
cleanup plan does not authorize discarding it during this migration.

### 4. Export flattening can widen access if done naively

`/export/media` currently exposes only Z's Media subtree to docker-host.
Pointing it at the final entire Media-disk root would also expose migrated
Proxmox/HA/config backups and Immich data through that export. Some backup
directories currently grant other-read/traverse permissions.

Preserve existing access boundaries. Recommended implementation: replace the
broad media mount with dataset-specific exports for the actual consumers
(Jellyfin, comics, incoming, phone recordings and calibre-library), mounted at
their existing logical subpaths where possible. Keep Immich, Frigate and backup
exports separately scoped. Validate ACLs and effective service identities; do
not solve permissions with a recursive chmod/chown or a root-wide container mount.

## Dependency and change map

| Surface | Observed dependency | Required migration treatment |
|---|---|---|
| OMV configuration | Shared-folder filesystem references and relative paths; generated fstab/exports/Samba/Monit/collectd | Register new array/filesystem; update OMV's managed configuration and regenerate. Do not merely edit generated files. Preserve unrelated md0 references because Print remains there. |
| SMB / Windows | Y → nas; Z → 14tb; active desktop SMB session | Rename shares to Print/Media; reconnect mappings; refresh shortcuts and credentials' target names as needed; test after a new login. |
| OMV custom exports | `/etc/exports.d/overwatch-backups.exports` | Move three backup exports to the new filesystem. Prefer stable dataset export names and update all three clients together. |
| Proxmox | `/etc/pve/storage.cfg` uses old physical UUID for `backups/proxmox`; health/dashboard scripts inspect storage | Update source while retaining storage ID `omv-backups`, content, retention, schedules and permissions. Test real backup and isolated restore. |
| Home Assistant | Supervisor `nas_backups` is active/default; source is old UUID `backups/home-assistant` | Update through Supervisor mount management, retaining logical backup name/default and schedule; verify new backup and restore readability. |
| Docker-host backup | fstab physical UUID; backup systemd units/scripts use `/mnt/omv/docker-host-backups` | Retarget mount; update physical-path checks in MediaMTX backup; preserve logical mountpoint and mount guards. Include app-data, coordinated Hub, MediaMTX and Bambuddy offline-update sources. |
| OMV config backup | `/usr/local/sbin/omv-config-backup`, service paths point at md0 backups | Move backup destination and mount requirements; retain root-only protection and relative latest symlink. |
| Immich | `/export/immich` → `/mnt/omv/immich` → container `/data` | Change backing filesystem/export; keep internal paths; stop upload and other media writers for final sync. Preserve UID/GID and ACLs. |
| Frigate | `/export/frigate` → Proxmox `/mnt/omv/frigate` → CT111 `/mnt/nas/frigate` → recordings | Change backing filesystem; remount/rebind clients; preserve mapped UID 100000 ACL. Stop recording writers for cutover. |
| Calibre-Web | `/mnt/omv/media/books/calibre-library:/books`; DB setting `/books` | New host mount for final root `calibre-library`; retain `/books` internally. No metadata rewriting just for this unchanged internal path. |
| Desktop Calibre | This desktop points at `K:\Documents\Ebooks` | Separate library: do not overwrite it or silently repoint it. Other desktop clients still need their own acceptance checks. |
| Jellyfin | Four read-only `/mnt/omv/media/jellyfin/*` bind mounts | Preserve internal `/media/*` paths and read-only boundaries; retarget scoped NFS backing mounts. |
| Atsumeru | `/mnt/omv/media/comics/atsumeru-library:/library` | Preserve `/library`; retarget scoped mount. |
| qBittorrent | `/mnt/omv/media/incoming/qbittorrent:/downloads` | Stop transfers for final sync; preserve `/downloads`, resume state and ownership; recheck data before resume. |
| MediaMTX | `/mnt/omv/media/phone-recordings:/recordings` | Pause recording writers; preserve `/recordings`; verify new recording and backup source guard. |
| Immich curated exporter | Repository templates point at existing media paths | Update rebuild sources and mount checks even though no matching live service was found by this scan. |
| Filebrowser on OMV | Podman bind of old Y root to `/srv/`; verified active database has one admin scoped to `/srv` + `/` | Prepared OMV-managed composite Print/Media bind view preserves account/scope and `/Print/...` links. Recheck accounts before deployment and complete authenticated UI acceptance. |
| TransferPortal | Bind units use current Z as source and Y as destination; smoke dirs and stored jobs refer to those roles | Disable admission during migration; retarget or retire old configuration deliberately. Historical jobs must not be replayable against newly repurposed endpoints. Do not use the existing portal as an assumed-safe migration engine. |
| Monitoring | SMART producer scans physical disks dynamically; mdadm currently lists only md0; OMV filesystem monitoring uses UUIDs | Add array assembly/health/resync monitoring; regenerate filesystem checks; update storage names and alert expectations. |
| Repository and local scripts | Canonical configs/runbooks, wiki references, copied worktrees, Household Hub `tmp_*` Print scripts | Update active sources; prevent old scripts/checkouts from replaying obsolete paths. Keep immutable historical evidence labelled as historical. |

No matching storage-path references were found in the selected live LLM-host
configuration scan. Monitoring configuration and the selected Grafana/Kuma
database columns also had no matching path references; this is not a claim
that no monitoring changes are needed.

The initial Filebrowser string inventory was not authoritative. Follow-up
read-only active-record inspection resolved the account/scope question as
recorded above. Live authenticated browsing and any newly added accounts still
require acceptance; the disposable mount test does not establish that outcome.

## Recommended execution sequence — not executed

1. **Freeze the plan and capture recovery evidence.** Record the accepted
   single-copy interval; identify disks by stable IDs; check SMART extended tests,
   power stability, array health and exact usable sizes. Take restorable
   OMV/client/application config checkpoints outside the disks being repurposed.
   Capture manifests including hidden files, empty directories, symlinks,
   hardlinks, sparse allocation, numeric ownership, modes, ACLs and xattrs.
2. **Prepare the mirror on the fourth disk only.** After explicit approval of
   that exact destructive operation, create a two-member RAID1 with one missing
   member, and a new filesystem on the resulting array. Original Z remains
   intact. Validate the exact procedure against the installed mdadm/OMV
   versions; this report intentionally contains no runnable wipe commands.
3. **Stage current Z in its original layout.** Copy the entire old Z, including
   ISO/hidden/hold entries, in one metadata-preserving transfer so hardlinks
   across folders survive and final sync can resume safely. Record the intended
   old-to-new mapping but defer destination flattening until final sync and
   verification. Preserve original Z's layout for rollback. Use root-run server-side
   metadata-preserving copying, with collision refusal and no destination-wide
   delete, in-place overwrite, or automatic source removal.
4. **Cut over existing Z consumers.** Stop all relevant writers, desktop
   clients, jobs and automatic restarts; reconcile changes/deletions using the
   manifest; checksum the final data and verify metadata. Flatten only the new
   destination using journaled same-filesystem renames, including the Calibre
   exception, and reconcile the final namespace against the mapping. Retarget scoped
   exports, SMB and services; remount NFS and recreate affected container bind
   mounts so they cannot retain stale handles. Complete library/service tests.
   Staging reduces transfer downtime but does not guarantee a short final
   checksum or maintenance window.
5. **Complete RAID1 before moving Y service data.** Verify the new copy and
   record the accepted single-copy risk before repurposing original Z as the
   second member. Wait for full synchronisation and clean two-member state;
   validate data, monitoring and assembly persistence. Never add a populated
   original Z directly to a new array while assuming its filesystem will survive.
6. **Stage Y non-Print data and switch its consumers.** Copy all root entries
   except exactly Print to the final Media root. Merge directories using the
   collision manifest; refuse any newly divergent leaf collision. Pause backups,
   retention, imports, uploads and recordings for final reconciliation. Update
   backup clients, OMV backup, Immich, Frigate, Filebrowser and transfer tooling.
7. **Flatten Print on its existing filesystem.** Quiesce Print clients and
   scripts, then perform checked same-filesystem child renames into Y root.
   Record old/new paths and inode identity; preserve directory ACLs/defaults.
   Update Y:\Print and nas\Print references to Y:\ and Print-share root.
8. **Acceptance, recovery and cleanup.** Keep cross-disk originals until all
   manifest/checksum/service gates, a fresh backup cycle and isolated restore
   checks pass. If failures occur after new writes, freeze writers and reconcile
   deltas before rollback—never simply point clients back at stale originals.
   Delete only manifest-verified original entries. Remove Print/Media wrappers
   with an empty-directory-only operation after a fresh enumeration proves
   nothing remains. Do not delete old evidence, hold folders, or backups as
   incidental cleanup. Remove obsolete shares/exports only after client checks.

The original Z rollback copy ceases to exist when that disk becomes a mirror
member. The owner has waived an independent recovery copy for that transition;
there is no full-data rollback copy once original Z is repurposed. Keep original
Z intact until the copied data, metadata and service acceptance gates pass.

OMV documents MD/mdadm as its software RAID mechanism:
[OMV RAID](https://docs.openmediavault.org/en/stable/administration/storage/raid.html).
Linux documents array states and member management:
[Linux MD](https://www.kernel.org/doc/html/next/admin-guide/md.html).
These support the approach; they do not substitute for a reviewed device-specific
execution script and tested recovery path.

## Verification gates

The prepared harness now covers the filesystem/controller cases below; retain
the remaining live application and client checks as execution gates:
hidden and empty entries; spaces/Unicode; case collisions; same-name equal and
unequal files; directory-versus-file collisions; Calibre's special mapping;
relative/absolute symlinks; hardlinks; ACLs/xattrs; sparse files; socket entries;
interruption/restart; unavailable or wrong mount; new writes; vanished source
files; destination-full; and rejection of a non-empty wrapper deletion.
No file may map to two conflicting destinations or escape its approved root.

During cutover:

- Match every original manifest entry to a verified destination. Hash regular
  file data after final synchronisation; compare metadata separately. For
  same-filesystem renames, verify identity and complete namespace reconciliation.
  Any read error, vanished entry or conflict prevents cleanup.
- Verify exact remote source/type and service-user read/write access at every
  mount; test failure when a mount is absent. Preserve Frigate UID 100000 and
  the media-service identity. Prove media consumers cannot read newly co-located
  backup/Immich datasets.
- Calibre baseline was 10,548 books and 11,031 format records, SQLite
  `quick_check=ok`, Calibre-Web library setting `/books`. Refresh the baseline
  after writers stop; compare counts/integrity, covers, downloads and a
  controlled metadata update after cutover.
- Exercise authenticated Jellyfin playback, Atsumeru reading, controlled
  qBittorrent recheck/resume, MediaMTX recording/playback, Immich upload/read,
  Frigate recordings (or a documented fixture if cameras remain disconnected),
  Filebrowser scopes and Windows SMB read/write after reconnect.
- Run fresh HA, Proxmox, Docker app-data and OMV config backups; perform isolated
  restore checks including a database-backed application. A 200 response or
  successful file listing alone is insufficient.
- Re-run reference inventory and reconcile every active match as updated,
  intentionally stable logical path, or retired. Retain historical strings
  with explicit disposition; do not bulk-replace UUIDs or rewrite history.
- Verify remount/restart persistence and both arrays healthy before cleanup.

## Initial audit checks and limits (before execution progress above)

- Read-only drive mappings, lsblk, mdstat/mdadm detail/signature inspection,
  SMART health/attributes/existing test logs, NTFS metadata and recursive listing.
- Full directory traversal on both shares, live du/df sizes, case and merge
  collision checks, selected ACLs, SMB sessions, running service/mount inventory.
- Reference scan: **6,969 eligible text files**, **1,759 matching lines in 408
  files**, including ignored/untracked material and copied worktrees. Matches
  are candidates, not 1,759 independently verified live dependencies.
  Dispositions: 342 canonical-review, 14 local operational-script, 21 test,
  42 historical, 8 wiki, 1,332 other-checkout lines.
- Live config scans on OMV, Docker, Proxmox, monitoring and LLM hosts:
  respectively 182, 43, 8, 0 and 0 candidate matching lines; zero reported
  read errors. Container mount inspection and timers included. Home Assistant
  Supervisor mount and CT111 mount/Compose checks were performed separately.
- Selected TransferPortal/Grafana/Kuma database-column inspection; Filebrowser
  BoltDB path-token inspection; Calibre database quick check/counts.
- This desktop's SMB mappings, Calibre library settings and scheduled-task
  actions were inspected. No scheduled-task action matched Y/Z paths, OMV IP
  or calibre in the selected action fields.
- Nine path-matcher fixture checks passed. This is collector verification,
  not migration-script or application acceptance testing.

No copy, format, RAID change, share rename, service restart, deletion, full
content hashing, filesystem repair or new SMART surface test ran. Only local
audit files and documentation pointers were added. The working repositories
already contain unrelated modifications, which were preserved.

Coverage is bounded: selected text extensions (local limit 8 MB, live limit
4 MB), configuration/source roots, and selected database columns. Dependency
caches, Git history, arbitrary binary project documents, encrypted settings,
unmounted/offline clients and other users' devices are not exhaustively audited.
Missing or dynamically generated paths require cold preflight and client
acceptance; no claim of “every reference everywhere proven absent” is justified.
Historical/copied files require review before reuse, not blind rewriting.

Evidence: `repository-references.csv`, `scan-summary.json`, host JSON inventories,
host baselines, `omv-contract.json`, `collisions.json`, `tree-audit.json`,
`calibre-baseline.json`, database-path inventories and `filebrowser-scopes.json`.
`collect.py` reproduces the reference/container/timer portion only; other
observations are dated one-off evidence and must be refreshed before execution.


### October28 diagnostic test-material cleanup

Owner explicitly authorized removing everything in `Z:\_codex_diagnostics` except the eight previously unverified files. Completed at 10:55:45 GMT: removed 6,923 files (6,458,227,311 logical bytes) and empty directories. A complete post-operation namespace check found exactly the eight preserved files and their parent directories. Production library files were outside this operation. Private manifest, per-file journal and result: `/root/diagnostics-synthetic-retirement-20261028/` on OMV. The four separately reviewed disposable root folders were already absent before this action.
