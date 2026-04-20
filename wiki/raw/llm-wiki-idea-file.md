LLM Wiki
A pattern for building personal knowledge bases using LLMs.

The core idea: Instead of RAG (re-deriving knowledge from scratch on every query), the LLM incrementally builds and maintains a persistent wiki — a structured, interlinked collection of markdown files. When a new source is added, the LLM reads it, extracts key information, and integrates it into the existing wiki: updating entity pages, revising topic summaries, flagging contradictions, and strengthening the evolving synthesis.

Architecture:
- Raw sources (immutable)
- The wiki (LLM-generated markdown)
- The schema (CLAUDE.md / AGENTS.md — configuration for the LLM as wiki maintainer)

Operations:
- Ingest: process new source, update wiki pages, log
- Query: answer against wiki, optionally file answer back
- Lint: health check (orphans, contradictions, gaps)

Indexing: index.md (content catalog) + log.md (chronological append-only log)

Optional tooling: qmd (local hybrid search for markdown), Obsidian Web Clipper, Obsidian graph view, Marp (slide decks), Dataview plugin

Why it works: LLMs handle the maintenance burden (cross-references, consistency, bookkeeping) that causes humans to abandon wikis. Human curates and directs; LLM maintains.

Related: Vannevar Bush's Memex (1945) — personal curated knowledge store with associative trails.

Source: Idea file shared by user at wiki initialization, 2026-04-07.
