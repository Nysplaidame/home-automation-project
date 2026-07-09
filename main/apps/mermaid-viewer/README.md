---
title: Mermaid Diagram Viewer
description: Internal read-only web viewer for canonical Mermaid diagrams
tags: [apps, diagrams, mermaid, internal]
created: 2026-07-09
modified: 2026-07-09
type: app-spec
status: draft
---

# Mermaid Diagram Viewer

Read-only internal web UI for browsing the canonical Mermaid sources under
`docs/diagrams/`.

## Goals

- Browse the diagram library by section and title.
- Search across titles, descriptions, and tags.
- Open a diagram in-place with Mermaid rendering.
- Copy a Markdown link or relative file path.
- Stay internal-only and read-only.

## Proposed shape

- Static frontend served from docker-host.
- Manifest file listing the canonical `.mermaid` sources.
- Mermaid rendering in the browser from the source text.
- No edit, upload, or write-back path.

## Suggested path

```text
/opt/stacks/mermaid-viewer/
```

## Suggested exposure

- Internal LAN / Tailscale only.
- No public exposure.
- No auth beyond the existing internal network boundary unless later required.
