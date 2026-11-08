---
title: Household Hub source recovery register
description: Provenance boundary and recovery-generation record for the separate Household Hub application
tags: [household-hub, source, recovery, provenance]
created: 2026-09-18
type: recovery-register
status: active
---

# Household Hub source recovery register

## What is recovered

The protected source archive at
`C:/Users/Admin/home-automation-recovery/source-20260911-224938/household-hub-source.tar.gz`
is present and readable. Its recorded SHA-256 is
`be21e45bc0b1604b231d3c51cc36bbc5366cb25053f7f1fbda3a426f9b7eadab`.
It contains the API, worker, web, shared packages, infrastructure, root
manifests, documentation, and recorded Alembic migrations. The archive is a
known recovery generation: the September12 isolated API/database/Qdrant restore
and September16 offline source builds used its recovered source family.

## What is not recovered

The live tree and protected archive contain no Git metadata. The archive
intentionally excludes `.env*`, dependency caches, `.bak` files, application
data, credentials, and Git history. It therefore cannot identify the original
canonical repository URL, branch, commit, author history, or complete build
inputs. The tracked Compose directory is a deployment mirror only, not an
application repository.

Do not invent a remote or label the archive as an original upstream checkout.
Do not deploy, migrate, or replace live images merely because the source tree is
available. API image startup performs Alembic upgrade work unless explicitly
overridden for isolation.

## Recovery repository created

The owner authorized a new, clearly labelled local recovery repository on
2026-09-18 at `main/apps/household-hub-recovery`. Its first commit is
`c463bd9` (`chore(recovery): seed Household Hub source`) and has no configured
remote. It records the archive identity in `RECOVERY-PROVENANCE.md`, ignores
runtime secrets and generated output, and excludes the archived TypeScript
build-info artifact from history.

This preserves a reproducible project-owned baseline going forward; it does
not restore historical provenance. Do not add a guessed remote. If remote
collaboration is required later, the owner must choose its location and access
model, and the first publish must retain the archive hash and recovery status.

## Related evidence

- [Household Hub deployment boundary](../../configs/docker-host/stacks/household-hub/README.md)
- [Installation coverage](../install/INSTALL-TO-DO.md)
- [Read-only household release plan](read-only-product-release-plan.md)
