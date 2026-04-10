---
title: "RAG vs Wiki Pattern"
category: concept
tags: [knowledge-management, methodology, llm]
created: 2026-04-07
updated: 2026-04-07
sources: [llm-wiki-idea-file]
status: active
---

# RAG vs Wiki Pattern

## Definition

**RAG (Retrieval-Augmented Generation):** At query time, relevant chunks are retrieved from raw documents and the LLM synthesizes an answer. Knowledge is re-derived from scratch on every question. No accumulation occurs.

**Wiki Pattern (this project's approach):** The LLM incrementally builds a persistent wiki from raw sources. Knowledge is compiled once and kept current. Cross-references, contradictions, and syntheses are already present when a query arrives.

## Relevance to This Project

This wiki operates on the Wiki Pattern. Every source ingested into `raw/` is processed into `pages/` — it is never re-read at query time unless explicitly needed for verification. The index and cross-links do the retrieval work.

## Key Distinction

| | RAG | Wiki Pattern |
|---|---|---|
| Knowledge compiled | At query time | At ingest time |
| Accumulation | None | Compounding |
| Contradiction detection | Rare | Explicit |
| Maintenance cost | Low setup, high per-query | Low per-query, requires ingest discipline |

## Trade-offs / Considerations

- Wiki pattern requires disciplined ingest workflow.
- Works best when sources are added incrementally (one at a time with review).
- At scale (100+ sources), a search tool like `[[qmd]]` supplements the index.
- The wiki can go stale if sources are added without running ingest properly.

## Sources

- [[llm-wiki-idea-file]]
