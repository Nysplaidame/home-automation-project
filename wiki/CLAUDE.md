# CLAUDE.md — LLM Wiki Schema
## Home Automation Project · Second Brain

> This file is the authoritative schema for the wiki. Read it at the start of every session.
> The LLM writes and maintains all wiki content. The human curates sources and directs analysis.

---

## 1. Root Layout

```
wiki/
├── CLAUDE.md          ← this file (schema, rules, workflows)
├── index.md           ← content catalog; LLM reads this first on every query
├── log.md             ← append-only chronological record of all operations
├── raw/               ← IMMUTABLE source documents (human drops files here)
│   └── assets/        ← downloaded images referenced by raw docs
└── pages/             ← LLM-generated markdown (the wiki proper)
    ├── entities/      ← hardware, devices, integrations, people, services
    ├── concepts/      ← protocols, patterns, architectural ideas
    ├── sources/       ← one summary page per ingested raw document
    └── analyses/      ← query answers, comparisons, investigations filed back
```

**Rules:**
- `raw/` is read-only for the LLM. Never modify or delete files there.
- `pages/` is owned entirely by the LLM. Humans read; LLM writes.
- Always use `[[WikiLink]]` syntax for internal links (Obsidian-compatible).
- Every page must have YAML frontmatter (see Section 3).

---

## 2. Workflows

### 2A. INGEST — adding a new source

Triggered when the human says: `ingest`, `process this`, or drops a file path.

**Steps (in order):**
1. Read the source file from `raw/`.
2. Briefly discuss key takeaways with the human (2–5 bullet points). Confirm emphasis.
3. Write a source summary page → `pages/sources/<slug>.md`
4. Identify all entities and concepts mentioned. For each:
   - If the page exists → open it, append/update with new info, note the source.
   - If it doesn't exist → create it.
5. Update `index.md` — add the new source page and any new entity/concept pages.
6. Append an entry to `log.md` (see Section 5 for format).
7. Report back: list every file touched (created or updated).

**Scope rule:** A single ingest typically touches 5–15 pages. If a source is narrow, fewer is fine.

### 2B. QUERY — answering a question

Triggered when the human asks a question or says `query`.

**Steps:**
1. Read `index.md` to identify relevant pages.
2. Read those pages (and follow internal links if needed).
3. Synthesize an answer with `[[WikiLink]]` citations to source pages.
4. Ask: "Should I file this as an analysis?" If yes → write to `pages/analyses/<slug>.md`.
5. If filed, update `index.md` and `log.md`.

### 2C. LINT — wiki health check

Triggered when the human says `lint` or `health check`.

**Check for:**
- Pages with no inbound links (orphans) — list them.
- Claims that newer sources may have superseded.
- Concepts mentioned on multiple pages but lacking their own page.
- Missing cross-links between obviously related pages.
- Gaps that could be filled with a web search or a new source.

**Output:** A lint report filed to `pages/analyses/lint-<date>.md`, plus a prioritised action list.

---

## 3. Page Frontmatter (required on every page)

```yaml
---
title: "Page Title"
category: entity | concept | source | analysis
tags: [tag1, tag2]
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [source-slug-1, source-slug-2]   # omit on source pages
status: stub | active | stable            # stub = <200 words, stable = well-developed
---
```

- `category` drives the folder: entity → `entities/`, concept → `concepts/`, etc.
- `sources` links every claim back to what it came from.
- `status: stub` flags a page as needing expansion.

---

## 4. Page Templates

### Entity page (`pages/entities/<slug>.md`)
```
---
[frontmatter]
---
# Entity Name

**Type:** device | integration | service | person | vendor
**Status:** [operational / planned / deprecated]
**Related:** [[link1]], [[link2]]

## Overview
One paragraph description.

## Key Properties
- property: value

## Notes & Observations
Bullet points with source citations, e.g. "Supports Zigbee 3.0 [[source-slug]]"

## Open Questions
- [ ] Question to resolve

## Change Log
- YYYY-MM-DD: what changed and why
```

### Concept page (`pages/concepts/<slug>.md`)
```
---
[frontmatter]
---
# Concept Name

## Definition
Concise definition (2–4 sentences).

## Relevance to This Project
Why does this matter here?

## Key Entities Using This Concept
- [[entity-1]]
- [[entity-2]]

## Trade-offs / Considerations
Pros, cons, gotchas.

## Sources
- [[source-slug]]
```

### Source page (`pages/sources/<slug>.md`)
```
---
[frontmatter]
---
# Source: Title

**Original file:** `raw/<filename>`
**Date ingested:** YYYY-MM-DD
**Type:** article | datasheet | forum post | transcript | doc | image

## Summary
3–6 sentence summary of the source.

## Key Takeaways
- bullet 1
- bullet 2

## Entities Mentioned
[[entity-1]], [[entity-2]]

## Concepts Mentioned
[[concept-1]]

## Contradictions / Updates
Any conflicts with existing wiki content.
```

### Analysis page (`pages/analyses/<slug>.md`)
```
---
[frontmatter]
---
# Analysis: Title

**Query:** What was asked
**Date:** YYYY-MM-DD

## Answer / Findings
Main content.

## Sources Used
[[source-1]], [[entity-1]]

## Follow-up Questions
- [ ] next thing to investigate
```

---

## 5. Log Format

File: `log.md`
Every entry starts with a parseable prefix:

```
## [YYYY-MM-DD] <operation> | <title>
```

Operations: `ingest` · `query` · `lint` · `create` · `update` · `schema`

Example:
```markdown
## [2026-04-07] ingest | Zigbee2MQTT Getting Started Guide
- Source: `raw/zigbee2mqtt-getting-started.md`
- Pages created: [[sources/zigbee2mqtt-getting-started]], [[entities/zigbee2mqtt]], [[entities/coordinator]]
- Pages updated: [[concepts/zigbee]], [[index]]
- Notes: First ingest. Established Zigbee as primary mesh protocol for this project.
```

To see recent history: `grep "^## \[" log.md | tail -10`

---

## 6. Index Format

File: `index.md`
Organized by category. Each entry: `[[link]] — one-line description`

The LLM reads `index.md` first on every query to orient itself before opening individual pages.

---

## 7. Naming Conventions

- Filenames: `kebab-case.md` (no spaces, no special chars)
- WikiLinks: use the filename slug without extension, e.g. `[[zigbee2mqtt]]`
- Slugs for sources: derived from the source filename or a short title, e.g. `zigbee2mqtt-getting-started`
- Dates: always `YYYY-MM-DD`

---

## 8. Session Start Checklist

At the start of every session, the LLM should:
1. Read `CLAUDE.md` (this file) — confirm schema is loaded.
2. Read `log.md` (last 10 entries) — orient to recent activity.
3. Read `index.md` — know what's in the wiki.
4. Confirm ready: "Wiki loaded. [N] pages indexed. Last activity: [date+op]."

---

## 9. Domain Notes (Home Automation Project)

This wiki is specifically for a **home automation project**. Common entity types:
- **Devices:** smart switches, sensors, bulbs, plugs, locks, cameras
- **Hubs/Controllers:** Home Assistant, Zigbee coordinator, Z-Wave stick
- **Protocols:** Zigbee, Z-Wave, Matter, Thread, Wi-Fi, MQTT
- **Integrations:** HA add-ons, HACS integrations, ESPHome, Node-RED
- **Vendors:** IKEA, Sonoff, Shelly, Philips Hue, Aqara, Tuya, etc.
- **Rooms/Zones:** physical locations in the home
- **Automations:** named automations and their logic

Prefer specific entity pages over vague topic pages. Every device model mentioned in a source should eventually get its own entity page.

---

*Schema version: 1.0 · Created: 2026-04-07 · Maintained by: LLM Wiki Agent*
