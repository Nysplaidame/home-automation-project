---
title: "LLM Wiki — Idea File"
category: source
tags: [meta, knowledge-management, workflow]
created: 2026-04-07
updated: 2026-04-07
status: stable
---

# Source: LLM Wiki — Idea File

**Original file:** `raw/llm-wiki-idea-file.md`
**Date ingested:** 2026-04-07
**Type:** idea file / methodology doc

## Summary

Describes a pattern for building a persistent personal knowledge base maintained by an LLM. Rather than re-deriving answers from raw documents on every query (RAG), the LLM incrementally writes and maintains a wiki of structured markdown pages. The human sources documents and asks questions; the LLM does all maintenance — cross-references, summaries, contradiction-flagging, bookkeeping. The result is a compounding artifact that grows richer with every ingest.

## Key Takeaways

- The wiki is a **persistent, compiled artifact** — not re-derived at query time.
- Three layers: raw sources (immutable) → wiki pages (LLM-owned) → schema (CLAUDE.md).
- Three core operations: **Ingest**, **Query**, **Lint**.
- `index.md` (content catalog) + `log.md` (chronological log) allow navigation at scale.
- Filed query answers compound the wiki just like ingested sources do.
- Optional tooling: qmd search, Obsidian Web Clipper, Marp, Dataview.
- Philosophical ancestor: Vannevar Bush's **Memex** (1945).

## Entities Mentioned

[[obsidian]], [[qmd]], [[marp]], [[dataview-plugin]], [[obsidian-web-clipper]]

## Concepts Mentioned

[[rag-vs-wiki-pattern]], [[personal-knowledge-management]], [[memex]]

## Contradictions / Updates

None — this is the founding methodology document.
