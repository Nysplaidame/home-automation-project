---
title: "RAG vs Wiki Pattern"
category: concept
tags: [knowledge-management, methodology, llm]
created: 2026-04-07
updated: 2026-10-04
sources: [llm-wiki-idea-file]
status: active
---

# RAG vs Wiki Pattern

## Definition

**RAG (Retrieval-Augmented Generation):** Retrieved material informs a generated
answer. The original RAG paper combines model parameters with a persistent dense
vector index; retrieval does not imply that stored knowledge is discarded or
cannot accumulate. [Lewis et al., 2020](https://arxiv.org/abs/2005.11401).

**Wiki Pattern (this project's approach):** The LLM incrementally builds a persistent wiki from raw sources. Knowledge is compiled once and kept current. Cross-references, contradictions, and syntheses are already present when a query arrives.

## Relevance to This Project

This wiki operates on the Wiki Pattern. Every source ingested into `raw/` is processed into `pages/` — it is never re-read at query time unless explicitly needed for verification. The index and cross-links do the retrieval work.

## Key Distinction

| | RAG | Wiki Pattern |
|---|---|---|
| Knowledge compiled | At query time | At ingest time |
| Durable artifact | Retrieval corpus/index; maintenance depends on implementation | Curated summaries, links and synthesis |
| Contradiction handling | Requires explicit retrieval/application policy | Requires explicit editorial maintenance |
| Maintenance | Index/source refresh plus retrieval policy | Source review and page updates |

## Trade-offs / Considerations

- Wiki pattern requires disciplined ingest workflow.
- Works best when sources are added incrementally (one at a time with review).
- At scale (100+ sources), a search tool such as `qmd` can supplement the index;
  [[entities/qmd]] is an optional candidate, with adoption unverified.
- The wiki can go stale if sources are added without running ingest properly.
- These approaches can coexist: canonical current-state documentation records
  Household Hub's Qdrant-backed RAG, while this wiki remains a compiled knowledge
  layer. Neither approach automatically certifies current operational facts.
  [[entities/household-hub]]

## Sources

- [[sources/llm-wiki-idea-file]]
- [[../../../main/docs/reference/current-live-state]]
