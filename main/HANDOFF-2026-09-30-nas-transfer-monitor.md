# NAS transfer stall investigation — 2026-09-30

Active: monitor concurrent GW archive extraction and Z:\Media Calibre metadata work without interrupting either workload.

## Evidence at 09:40 BST

- GW chat: `01a0e966-0351-7f10-a854-5fab54a41571`; 7-Zip PID 20004 is extracting set 072 (`4_Elites.zip.001`) from and to `\\192.168.40.50\nas` through Windows SMB.
- Media chat: `01a0ea26-b6aa-75d3-ac81-17a884104b2e`; parallel metadata readers use the same NAS's `14tb` share. Shared server is confirmed; shared physical disks are not yet established.
- PC Ethernet and router NAS port lan4 both negotiate 1 Gbps. Windows adapter and lan4 report zero packet errors/discards. Router-origin NAS ping: 4/4 replies, 0.181–0.313 ms. Windows-origin ICMP is rejected and cannot measure NAS health.
- Extraction process counters advanced only about 0.041 MiB/s read and 0.106 MiB/s write over a 193-second initial observation, with near-zero CPU use. Subsequent activity resumed briefly. A simple UNC directory metadata probe took 30,994 ms to complete. This implicates SMB/server/storage waiting, but does not identify the underlying disk or service fault.
- SMB sample counters contain many zeros; do not equate zero counters with a stall without corroborating process progress. A captured active sample showed ~46 ms average read latency. SMB event-log access is denied without elevation; earlier empty results are inconclusive.
- OMV `omv-lan` desktop SSH key was rejected. Server-side disk latency, load, mount mapping, and Samba logs remain unverified. Router SSH works.

## Monitoring / resume

Raw telemetry and sampler remain outside the vault at `C:\Users\Admin\.codex\visualizations\2026\09\30\01a0f172-8745-7441-98b6-d5a55c118359`. Use `nas-telemetry.csv`, `extraction-samples.csv`, and `ethernet-samples.csv`. Earlier `nas-samples*.csv` are discarded collection attempts and must not be used for conclusions. Compare counters only within the same PID. Sampler records approximately every 2 seconds for 900 samples (~30 minutes); process id is recorded separately in `monitor-pid.txt`.

Chat heartbeat `monitor-nas-transfer-stalls` checks every 10 minutes, stays quiet for unchanged conditions, and stops after both workloads finish. Do not interrupt jobs or change NAS settings based on this preliminary evidence. Next diagnostic gate is existing authorized OMV management access for read-only disk/Samba telemetry; then correlate NAS wait times with both shares. Close this handoff with a brief result once the investigation ends.


## 09:52 BST follow-up

Media catalogue screening completed at approximately 09:39 BST; its chat is idle. GW remains active on set 072/PID 20004. The most recent 2-minute process-counter interval averaged 2.35 MiB/s reads and 10.37 MiB/s writes, compared with 0.041/0.106 MiB/s during the earlier stall. Over the last 6 minutes, the `14tb` share had no measured SMB data traffic; GW still showed variable throughput. Recovery is confirmed, but the media job is not established as its cause.

Latest 6-minute SMB observations: NAS average ~2.01 MiB/s reads / 7.63 MiB/s writes, maximum observed mean read latency 34.7 ms, data queue up to 21, zero credit stalls. PC Ethernet and router lan4 remain at zero packet errors/discards. Router NAS ping remains 0.171–0.304 ms, 3/3 replies. Continuous sampler PID 31900 is healthy. Continue monitoring GW and obtain read-only NAS disk/Samba metrics through authorized management access when available.

## 10:05 BST continuation

User requested continued monitoring. Sampler PID 31900 remains running and the existing 10-minute heartbeat remains configured. GW is still extracting set 072: its latest 10-minute process-counter interval averaged 0.865 MiB/s reads and 2.55 MiB/s writes. Ethernet error/discard counts remain zero. The media chat has resumed file-content/PDF inspection, so both workloads are now active again. Supplied root authentication was rejected by OMV SSH; no additional authentication attempts are planned without clarification. Existing Windows SMB access remains sufficient for client-side observations. Continue reporting only meaningful changes.

## 10:12 BST follow-up

Set 72 completed and passed the GW chat's verification (1,887 files / 14.57 GB). Set 73/PID 28020 began at ~10:09 BST and initially showed at least 131 seconds without process read/write progress, then resumed: by 10:11:49 it had read ~248 MB and written ~243 MB. Thus another startup pause and recovery are corroborated by process counters, not just zero SMB rates.

Media file inspection is active again. Over the latest 10-minute SMB interval, `14tb` averaged 2.28 MiB/s reads with maximum sampled mean read latency 206 ms; `nas` averaged 0.87 MiB/s reads / 4.07 MiB/s writes, maximum read latency 56.6 ms. No SMB credit stalls. Ethernet/router packet errors and drops remain zero; router NAS ping 0.327–0.443 ms, 3/3 replies. Higher SMB latency on both shares strengthens the server/storage-delay hypothesis but does not establish physical-disk contention. Keep observing; no configuration changes.

## Latest observation — 20:03 BST

GW reports all remaining extraction sets verified; Modern GrimDark matches6,478 files/147,424,857,028 bytes exactly. No7z process present; quiet SMB counters now expected, not a stall. GW chat still active reconciling results/manual deletion list, media idle. NAS100% idle,zero I/O/swap, no recent kernel errors; Ethernet errors/discards zero and no Samba lease-error matches last10 minutes. Await final GW chat completion before final monitor findings/automation shutdown. Extraction itself completed successfully despite observed pauses; no source deletion or service changes by monitor.

## Expanded diagnostics — 14:04 BST

User requested systemic analysis across both shares. Router snapshot showed 94% idle CPU, load ~0.27, ample available RAM, and zero NAS-port errors/drops. Windows 30-second host counters: CPU average 13.6%, available RAM minimum ~28,188 MB; TCP retransmissions average 2.26/sec versus ~30,905 segments/sec (~0.0073%). These are host-wide counters, not specific to the NAS flow, and do not exclude intermittent network faults outside the sample.

Defender/MsMpEng process read counters advanced ~974 MB between two snapshots while GW and media processes were active. This does not identify which files were scanned or prove NAS involvement. Expanded sampler now records PID/name/CPU/read/write counters for Defender, Python, Calibre and 7-Zip in external process-io-samples.csv, enabling timing correlation. Its refreshed PID is stored in monitor-pid.txt. client-system-samples.csv holds the bounded TCP/CPU/RAM capture.

Correction: Windows SMB event-log enumeration and Get-SmbConnection are denied without elevation. Earlier empty event-query results must not be interpreted as absence of SMB errors. No elevation or settings changes were performed.

Most decisive missing evidence: OMV share-to-filesystem/device mapping; per-disk await/queue/utilization; CPU iowait, dirty/writeback memory and memory pressure; Samba connection/lock state; kernel ATA/USB/reset/I/O errors; read-only SMART health/error counters; active NAS background jobs. Obtain through working authorized OMV SSH/console. Do not run SMART self-tests, benchmarks, or service restarts during concurrent work.




## SSH restored — 14:34 BST

Corrected password authenticated successfully; existing desktop public key added and BatchMode root login verified via omv-lan. No credentials recorded. Heartbeat updated to use read-only OMV telemetry. Initial vmstat interval reported 12% iowait, no active swap-in/out during sampled intervals; cause not yet established. iostat absent, use diskstats deltas. Canonical access facts recorded in OMV manual/current-live-state.


## First server-side correlation — 14:38 BST

Both workload chats remain active. Live mapping proves the two shares use separate data devices: NAS is md0 RAID1/sda+sde, 14tb is sdd1. md0 is [UU], no rebuild. Three 5-second diskstats intervals showed sdd read awaits ~3.2–4.2 ms while NAS RAID member write awaits in the last interval were ~103 ms (sda) and ~152 ms (sde); md0 average write await ~75 ms. Physical-disk utilization was below 25% in these intervals, so no sustained saturation established. Earlier vmstat interval showed 13–21% CPU iowait. Share delays cannot be attributed simply to both jobs using one disk.

Read-only SMART health passed for sda/sde/sdd with zero reallocated/pending/uncorrectable sectors. sde has lifetime UDMA CRC count 1, unknown age; monitor its delta before inferring current cabling trouble. No matching kernel errors/resets/timeouts in queried last-two-hour logs. Samba showed many leased open entries from the desktop connection; that alone does not establish blocking locks. Future lock reads must be summarized remotely rather than printing the full list.

Expanded continuous sampler ended normally; a fresh 20-sample client capture completed. No Ethernet errors/discards. Continue read-only correlation during an actual pause; root cause remains unresolved. Device mapping recorded in canonical OMV manual/current-live-state.

## Defender focused sample — 14:40 BST

A 29.5-second focused sample measured MsMpEng at 10.49 MiB/s process reads, ~0.082 CPU cores (~0.41% total CPU on 20 logical processors), ~681 MiB working set. This excludes CPU saturation during that window but does not identify paths or lock delays. Network-file scanning is enabled; mapped-drive scanning for full scans is disabled. Real-time protection enabled; last reported quick scan was September 9 and full scan April 26; no recent scheduled-scan start/end events found in a successful event query. Real-time scanning is plausible, not proven as the source of current NAS delays.

Built-in New-MpPerformanceRecording is installed but denied with 0x80070005 without Administrator privileges. No Defender settings changed. A concrete 60-second trace/report script is saved outside the vault as record-defender.ps1 in the existing telemetry directory; user can run it in Administrator PowerShell while transfers are active. Its report identifies scanned files/processes/extensions and is the next attribution gate. External focused sample: defender-focused.csv.





## New Samba evidence — 15:30 BST

Samba service logs reveal repeated contend_dirleases errors in smbd PID 1774372, shared by the desktop client across both shares. Calibre metadata.db-journal on 14tb is being statted with cwd pointing to the NAS filesystem; reciprocal GW paths on NAS show cwd pointing to the 14tb filesystem. Parent stat fails with ENOENT. This cross-share cwd mismatch is direct server-log evidence, not inferred from throughput. Last-30-minute query returned 262 lines containing contend_dirleases (~131 two-line events). Samba version 4.22.10-Debian-4.22.10+dfsg-0+deb13u2. Raw evidence saved externally as samba-dirlease-errors-20260930.txt.

This is the strongest specific SMB lead so far; causal connection to 30-second pauses remains unproven. No changes made. Next step: verify upstream issue/version status and correlate error timestamps with slow operations; keep any controlled lease-setting or connection-isolation test for an approved maintenance point rather than changing active jobs.


## Defender trace analysis — 15:48 BST

User Administrator recording succeeded at 15:45:10–15:46:11 BST (60.66 seconds). ETL/report now present externally; initial file check occurred before artifacts became available. Parsed full TopFiles (113 paths, 419 scans) and Overview into defender-performance-raw.json. Aggregate scan duration ~3.891 seconds; longest individual scan ~232 ms. Codex executable scans total ~1.564 seconds and three Codex session JSONL files ~1.829 seconds (~87% of aggregate scan duration together).

NAS paths, including redirected Z: device paths, account for seven scans totaling ~120 ms; slowest ~40 ms. Calibre metadata.db scan ~3.91 ms, notes.db ~2.75 ms. No GW paths appear in the completed-scan report. This trace does not support Defender scan time as the cause of tens-of-seconds NAS pauses in this recording window. It cannot exclude other windows or operations absent from captured completed scans. Do not interpret prior high process read-byte rates as NAS scan workload. No exclusions or security changes warranted by this evidence; Samba cross-share directory-lease errors remain the stronger specific lead.


## Ten-minute Defender trace — 16:02 BST

Completed user trace defender-performance-10min-20260930-155015.etl spans 600.28 seconds (~15:50:15–16:00:16 BST). Full parsed report saved externally as defender-10min-raw.json. Overview: 3,138 scans, summed scan durations 26.16 seconds, longest individual scan 253.65 ms. NAS paths (including redirected device paths) comprise 477 distinct paths, summed duration 9.342 seconds, maximum individual NAS scan 111.55 ms; no GW paths appear. Highest single-path aggregate is local codex.exe (~7.40 seconds across 33 scans); session logs also feature prominently.

This longer recording confirms Defender scans media files, but captured scan durations do not explain tens-of-seconds GW stalls. Do not equate aggregate scan duration with wall-clock CPU utilization or claim all possible blocking is excluded. Samba cross-share directory-lease errors remain the stronger specific lead (178 matching lines/~89 events in latest 10 minutes). Both workloads remain active, no kernel events in latest 15 minutes, client Ethernet errors/discards zero; bounded sampling completed normally.


## Long SMB trace prepared

User requested long-duration capture. External record-smb.ps1 runs in Administrator PowerShell for up to 60 minutes with FileSharing ETW, NAS-IP-filtered 256-byte packet captures, 2048 MB circular cap, 5-second process/NAS diskstats snapshots and final Samba journal export. Press S after observing a stall to stop and preserve recent rolling history. Script stops only a trace it successfully started; existing trace is left untouched on start failure. No configuration/service changes. Capture not yet started; awaiting user execution due required Windows elevation.


## SMB trace storage relocation

C: has ~1.55 GiB free, insufficient for the 2 GiB ring. E: verified as local fixed disk with ~1,644 GiB free. record-smb.ps1 now defaults OutputRoot to E:\CodexDiagnostics\NAS; script remains at the existing C: location, but all new trace/run artifacts go to E:. No existing files moved/deleted. Capture still requires user Administrator execution.





## Confirmed extraction pauses — 17:12 BST

E: supporting process/NAS sampler captured four recent unchanged 7z PID 27016 read, write and CPU intervals lasting 32.06–32.24 seconds (17:04:53–17:05:25, 17:06:46–17:07:18, 17:09:22–17:09:54, 17:10:05–17:10:37 BST), with progress in the following sample. This confirms repeated process pauses, not their cause. During 17:11:05–17:11:10 the NAS data-device counters were unchanged and client smbd was waiting in do_epoll_wait. Current vmstat shows 100% idle, no active swap or I/O wait, and no recent kernel errors. Samba directory-lease errors persist (142 matching lines/10 minutes). Both chats remain active. Supporting sampler files continue growing, but client.etl is still zero bytes and netsh reports no active trace; packet/ETW capture remains unverified. User already asked for Administrator start output. No services, workloads or settings changed.


## SMB capture finalized — 17:23 BST

User screenshot confirms successful elevated trace start and subsequent merge, with warning that some events were lost. Earlier non-elevated netsh status/zero-byte checks did not establish capture failure; those claims are superseded. Final client.etl is 2,143,813,632 bytes; client.cab 2,552,050 bytes under E:\CodexDiagnostics\NAS\smb-trace-20260930-164952. Stall marker 17:16:45.195 BST. Supporting process history identifies 19 recovered pauses of at least 25 seconds, saved as confirmed-pauses.csv, many around 32 seconds. Original samba-log.txt empty; independently recovered bounded 17:09–17:17 server journal as samba-stall-window.txt (43,251 bytes). It contains cross-share directory-lease errors during recorded pause windows, including 17:15:46–47, but causality remains unproven. ETL SMBClient window query and tracerpt summary are running; do not infer absent events until parsing and retained-time/event-loss coverage have been checked. Both workload chats remain active; capture completion is not workload completion.


Parsing update: bounded Get-WinEvent SMBClient-name query for 17:10–17:11 returned no matches. This does not establish absence of SMB activity: retained events/provider decoding and dropped-event coverage remain unchecked. tracerpt summary scan is progressing (about 51% at last check), session 69104. Supporting disk-rates.csv shows md0 writes near zero in 17:15:28–50 while 7z I/O/CPU unchanged at 17:15:16–48; NAS reads continue lightly during that interval. Therefore do not describe all data disks as idle throughout every pause. Pause list: 19 recovered intervals 26.77–32.27 seconds, mean 30.22 seconds at ~5.35-second sampling resolution.


Completed ETL summary scan: 7,080,785 retained events, 51,982,785 events reported lost, elapsed 1,616 seconds. SMBClient events are present in the summary, so earlier no-match Get-WinEvent query is not evidence of absent SMB data. High event loss substantially limits request/response timing and negative conclusions. Summary at E:\CodexDiagnostics\NAS\smb-trace-20260930-164952\etl-summary.txt. Capture is valid but not a complete timeline; retain process/NAS logs as independent pause evidence. Next analysis should extract surviving SMB lease-break/request events using GUID/ETW-aware decoding; any repeat capture should narrow provider selection and event rate to reduce losses, rather than extending the same broad FileSharing trace.


















## Closed — 20:12 BST

Both monitored chats are idle with completed turns. GW reports all78 archive sets passed file/byte verification:51,367 files,734.4 GB. Media latest pass completed, with an unverified series lookup left after a stall. Monitoring heartbeat removed after final report; no workloads/services/security settings changed by monitor.

Final findings: repeated~27–33-second extraction I/O/CPU pauses and longer near-stalls were confirmed; some coincided with idle NAS disks/CPU and clear Ethernet error counters. Media suffered database-open failures and path mismatches repaired by its own worker. Defender recordings did not explain tens-of-seconds GW pauses. Samba cross-share directory-lease cwd errors are a concrete defect lead, but later pauses occurred with media idle and no new such logs, so causal attribution remains unresolved. SMB capture contains7.08 million retained events but reports51.98 million lost, limiting timing/negative conclusions.

Resume investigation with focused lower-volume SMB/lease capture during reproduction, retain independent process/NAS samples, and compare surviving request/response timing. Raw artifacts remain outside vault at E:\CodexDiagnostics\NAS\smb-trace-20260930-164952 and existing C: telemetry directory. Do not interpret ordinary zero counters after completed workloads as stalls.


## Focused reproduction — 2026-10-01 21:34 BST

User authorized next focused test. Elevated named CodexSMBFocused session successfully ran SMBClient-only keywords0x445,level5,no packet capture,512MB circular,E: storage. Dedicated _codex_diagnostics/focused-20261001-213336 folders only; existing content untouched, test files retained. Two512MiB unbuffered robocopy runs: quiet69,542,864 bytes/s,synthetic14tb create/rename activity115,555,512 bytes/s; both exit1(successful copy),zero failed files. First baseline phases lasted7 and4 seconds,too short to exclude sporadic30-second stalls or reproduce7-Zip/Samba lease interaction. Artifacts E:\CodexDiagnostics\NAS\focused-20261001-213336; script at existing external telemetry/test-smb-focused.ps1. No services/security settings changed. Trace summary checked separately for event-loss coverage. Current NAS share UUID mapping still verified, but physical disk naming changed since9/30; do not reuse old sdd mapping without fresh device discovery.

Focused trace summary:45,910 events retained,zero reported lost,19 seconds elapsed; client ETL20MiB. Ethernet error deltas zero. Samba journal recovered independently for exact test window because script-generated journal file absent. This validates lower-volume capture quality but not root cause.

## Longer 7-Zip reproduction — 2026-10-01 21:46 BST

User authorized longer reproduction. Created synthetic1GiB archive:1,032 files,five256MiB multipart volumes,compressionmx1. Read archive and wrote output on NAS share in isolated _codex_diagnostics/sevenzip-20261001-213911. Three-minute quiet phase followed by three-minute synthetic media create/rename phase. Four full quiet passes exit0,about39–44sec each; two full media-active passes exit0,about52/92sec. Final partial pass in each phase deliberately terminated at phase deadline (own test process only),not interpreted as failure. All sampled extraction counters advanced every~2.3sec; no flat read/write/CPU intervals detected. Completed-pass sampled write rates quiet23.5–27.6MiB/s,media11.3–20.4MiB/s. Zero Ethernet error deltas. Trace2,810,588 retained events,zero reported lost,365sec;512MiB ring reachedcap,so earliest events may be overwritten despite zero dropped events. Independent process/NAS logs cover both phases. Samba journal recovered for exact window. Raw outputs E:\CodexDiagnostics\NAS\sevenzip-20261001-213911 (analysis.csv,summary.txt,process.csv,nas.txt,samba.txt).

First attempt sevenzip-20261001-213708 completed extraction cleanly but script misread null process exitcode; fixed by retaining process handle and waiting for exit before rerun. Not a NAS failure. Existing media/GW files untouched; diagnostic archives/output retained for targeted future reproduction. No services/security settings changed. No heartbeat re-created.

Conclusion: synthetic concurrent media activity measurably reduced extraction throughput in this ordered short trial,but did not reproduce prior27–33sec complete pauses; cache/order confounds prevent causal attribution. Next useful reproduction is focused capture around actual affected archive/file operation or a longer matched trial; do not change Samba/Defender solely on this result.

Server journal during focused reproduction contains5,322 matching contend_dirleases lines despite no sampled extraction plateaus. This reproduces the lease-log defect alongside throughput reduction,but shows those log messages do not invariably produce complete pauses. Causality still requires surviving SMB request/lease timing or controlled configuration comparison.

## Actual Necrons archive reproduction — 2026-10-01 22:01 BST

User continued investigation. Source Necrons ultimate collection.zip.001 verified present by read-only NAS stat; original archive/verified extraction untouched. Focused named SMB trace and separate diagnostic extraction outputs under _codex_diagnostics/actual-necrons-20261001-215428. Three-minute quiet and three-minute synthetic media-active phases each deliberately ended own partial extraction at deadline. Both sampled first~3GB output only; did not reach previous~14–32GB slow areas. Quiet10.29MiB/s read/16.22MiB/s write;media10.64/16.92. No complete I/O+CPU counter plateaus at~2.3sec sampling. Zero Ethernet error deltas. ETL1,703,253 events,zero reported lost,363sec,337.6MB below1GBcap; independent NAS/process logs available. Server journal84 contend_dirleases matches despite smooth counters. Ordered phases/cache differences prevent general throughput or causality claims.

Results E:\CodexDiagnostics\NAS\actual-necrons-20261001-215428; source script external telemetry/test-actual-smb.ps1. Diagnostic partial outputs retained, not valid completed extraction. No credentials/services/Defender/Samba configuration changes. Conclusion: affected archive early portion does not reproduce stalls today. Next evidence gate is capture around later affected file/offset range or longer full reproduction with clear bounded time/storage, rather than treating this negative early-window test as resolution.


## Later archive regions — 2026-10-01 22:10 BST

User authorized later-region test. Bounded7-Zip listing produced file inventory; selected cumulative unpacked byte ranges14–16GB and26–28GB. Ran each region3min,isolated diagnostic paths,same focused trace. First full late14 pass exit0 reported127 files/2,010,982,004 bytes (~116sec); selection list contained128 files/2,024,932,388 bytes,so do not claim all selected128 were exercised (one13,950,384-byte item unmatched; investigate list matching if needed). Late26 full pass exit0 reported67 files/2,244,575,976 bytes (~109sec),matching selected count/bytes. Repeats terminated at phase deadlines. Every~2.3sec sample advanced read/write/CPU; MaxFlatSeconds0 across all4 processes. Sampled write rates16.77/19.65MiB/s full passes,22.18/21.75 repeats. No Ethernet error deltas. ETL1,388,101 retained events,zero reported lost,363sec,302MB below1GBcap. Samba22 contend_dirleases matches without stalls. Raw data E:\CodexDiagnostics\NAS\later-necrons-20261001-220326; scripts/list files retained in external telemetry. No original archive/verified extraction/settings changed.

Current conclusion: affected archive later file ranges largely extract smoothly today as isolated operations; no evidence warrants a Samba/Defender fix yet. Remaining hypotheses include long-lived client/lease state or timing/concurrency not recreated by selective extraction. Next useful step is decode focused SMB events and compare preserved September30 capture around confirmed pauses; avoid further repetitive throughput-only tests unless a new reproducer differs materially.


## Preserved pause decoded — 2026-10-01

Surviving SMBClient events now identify a34.8125911-second file-open/create for OBJ_Head_Orb_Supported.obj in GW staging075/Pipermakes/WatchmanGoby,17:15:15.588–17:15:50.401BST onSeptember30. Start/end timestamps calibrate TotalDuration units as nanoseconds. Same-activity final create exchange lasts only0.7678ms; almost all RxContext time is CreateProcessing before that final exchange. Separate blank-activity exchange-create summary lasts35.0105sec in CreateStart, but missing matching start prevents definitive linkage. Read/write buffer summaries in17:15:10–17:16:05 retained window max88.8/120.6ms; these do not bound dropped requests. Cross-share Samba lease errors at17:15:46–47 coincide with blocked open, but today's error-without-stall reproductions still prevent causal proof. Lead is open/create/lease coordination or earlier operation state, not bulk throughput for this particular stall. No settings changed.

Evidence and caveats: E:\CodexDiagnostics\NAS\smb-trace-20260930-164952\pause-analysis.md,blocked-create-finding.json,smb-pause-summaries.csv,smb-pause-starts.csv. Original51.98million lost events limit negative conclusions. Targeted complete-activity export in progress. Next capture should include summary keyword0x800 as well as prior0x445 and pair client/server operation/lease timing around a reproduced stall; no more repetitive throughput tests without a distinct reproducer.

Complete target-activity export finished (blocked-create-activity.csv,20 events): matched CREATE send/receive MessageId12600501,17:15:50.3999108–50.4006092BST,Status0,0.6984ms wire request/response. Cache lookup events immediately precede send,cache invalidation/update follow response. Retained activity does not reveal why create waited34.81sec beforehand. Strengthens pre-final-request coordination lead; does not prove directory leases caused it. No analysis processes remain running.

## Paired capture ready — 2026-10-01 22:35 BST

User chose prepare for later. External telemetry folder now contains start-paired-smb.cmd,mark-paired-smb.cmd,stop-paired-smb.cmd,record-paired-smb.ps1,capture-omv-headers.py and paired-capture-readme.md. No ongoing capture or workload started. Launcher requests Windows administrator elevation, runs a named passive SMB trace at keywords0xc4c (IO starts,summary,info/cache/connectivity; excludes optional32007 transition flood),4GiB ring onE:,30min ceiling. Existing Python raw socket onOMV filters IPv4 TCP445 desktop192.168.10.132 and records control headers,SYN/FIN/RST in four16MiB PCAP ringfiles; excludes bulk READ/WRITE,ACK/continuations and may miss compound/split messages. Diskstats/pressure/wchan about5sec; bounded lock snapshots about30sec. No packages/services/security/debug settings changed. Own server artifacts under/tmp/codex-paired-open-TIMESTAMP retained and downloaded toE: on completion.

Final10sec preflight paired-open-20261001-223403 validated both packet directions (229 desktop,124 NAS control packets),353 saved headers,zero socket drops. Windows27,162 events,zero reported lost; clean stop/artifact copy. Earlier preflight uncovered hidden SSH stdin hang,fixed with-n/BatchMode; first socket protocol captured inbound only,fixed toETH_P_ALL plus kernelIPv4/TCP/client filter. Final validation supersedes earlier tests. Raw preflights outside vault. Resume: user double-clicks Start immediately before affected work,marks stall,stops shortly after recovery,then provides completed run path. Capture duration is bounded; ring overwrite and deliberate packet omissions remain coverage limitations. Do not claim root cause from this preparation or restart old heartbeat.
