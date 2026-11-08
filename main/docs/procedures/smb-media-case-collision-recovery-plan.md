---
title: SMB Media case-collision recovery plan
description: Reversible approval-gated plan for the Media/media namespace collision
tags: [omv, smb, storage, recovery]
created: 2026-09-18
type: recovery-plan
status: approval-required
---

# SMB Media case-collision recovery plan

## Known state

Server-side inspection recorded `Media` as the populated canonical library and
`media` as a distinct, empty wrapper containing only `media/Media`. Windows
SMB's case-insensitive lookup aliases the names and causes intermittent Explorer
failures. `/export/media` correctly bind-mounts only the canonical `Media` path;
no active NFS, systemd, or fstab reference was found for the wrapper.

This plan does not authorize deletion or renaming. It establishes evidence and
rollback requirements for a later approved maintenance action.

## Preconditions

1. Owner approves the exact canonical path, the wrapper path, and a maintenance
   window with no active SMB clients or media imports.
2. Capture read-only inode/path listings, SMB share configuration, NFS exports,
   mount references, active client sessions, and the wrapper's exact contents.
3. Confirm a current OMV backup or storage snapshot can recover both paths, and
   record its identity and restore route.
4. Prepare a reversible wrapper rename to a unique quarantine name on the same
   filesystem. Do not plan a recursive move, merge, or delete.

## Approved execution outline

Quiesce clients, repeat the preflight, rename only the verified empty wrapper,
and immediately re-check the canonical library, `/export/media`, SMB listing,
NFS mount, and media-service paths. Keep the quarantine path in place until
Windows clients remount cleanly and the owner accepts the result. Roll back by
renaming the same verified quarantine path to its original name; never target
the populated `Media` directory.

## Failure boundary

Stop without change if the wrapper is non-empty beyond its known nested entry,
any active configuration points to it, the backup evidence is missing, client
sessions cannot be quiesced, or canonical-path identity is ambiguous. Escalate
with the captured read-only evidence rather than attempting path cleanup.

## Evidence to retain

Retain the pre/post listings, inode identity, share/export/mount references,
backup identity, client revalidation results, exact command transcript with
secrets removed, and owner acceptance. Update the service/current-state docs
only after the approved action succeeds.
