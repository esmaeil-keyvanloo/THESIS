---
name: brain-map
title: Brain — Map of Contents
type: canon
status: active
updated: 2026-08-08
---

# Brain — Map of Contents

The **Brain** is the persistent memory and source of truth for the thesis
*Sensor-based Recyclables Collection Planning* (Rio Maior, Portugal).

It survives across all working rounds (`W1`, `W2`, …). Working rounds are
disposable; the Brain is not.

## Rules

1. `../DATA/` is **frozen**. It is never edited, moved or renamed.
2. Everything in the Brain is either a faithful conversion of `DATA/`, or a
   derived artefact that **cites its source**.
3. If a fact is not traceable to `DATA/` or to a recorded interview answer,
   it is written as `NOT IN SOURCE` — never inferred, never invented.
4. Numbers come from `03_db` via SQL. They are never quoted from memory or
   from semantic search.
5. Every modelling or scoping choice is logged in `00_canon/decisions/`.

## Structure

| Folder | Purpose |
|---|---|
| `00_canon/` | **Source of truth.** Short, hand-verified, always loaded into context. |
| `00_canon/project/` | Charter, scope, objectives, thesis structure, timeline. |
| `00_canon/constraints/` | Hard rules: jury requirements, deadline, model assumptions, out-of-scope list. |
| `00_canon/data/` | Data dictionary, column semantics, units, known data-quality defects. |
| `00_canon/glossary/` | Terminology, PT ↔ EN mapping, container/waste-fraction taxonomy. |
| `00_canon/decisions/` | Decision log (ADR form): dated, with rationale and what it supersedes. |
| `01_sources/` | 1:1 Markdown conversions of `DATA/DOCUMENT/`, with provenance front-matter. |
| `01_sources/thesis/` | Current thesis project document. |
| `01_sources/proposal/` | Original full proposal and chapter drafts. |
| `01_sources/defence/` | Defence deck and jury questions. |
| `01_sources/field_survey/` | Rio Maior site-visit report. |
| `01_sources/application/` | WSmartRoute+ application documentation. |
| `01_sources/_raw_text/` | Unprocessed text dumps, kept for audit of the conversion step. |
| `02_notes/` | **Derived** analysis produced during the work. Every claim carries a citation. |
| `02_notes/literature/` | Literature review notes and reference mapping. |
| `02_notes/data_quality/` | Profiling reports, defect registry, cleaning decisions. |
| `02_notes/methodology/` | Model formulations, parameter derivations, algorithm choices. |
| `02_notes/results/` | Verified results, promoted here only after reproduction from `03_db`. |
| `02_notes/meetings/` | Supervisor and jury interaction records. |
| `03_db/` | **Exact numeric layer.** All statistics are computed here, in SQL. |
| `03_db/duckdb/` | `rio.duckdb` — sensor readings, collections, geodatabase attributes. |
| `03_db/parquet/` | Columnar copies of the raw CSVs and derived tables. |
| `03_db/geo/` | `gis rio.gdb` converted to GeoPackage / Parquet. |
| `03_db/schemas/` | DDL, table contracts, column type declarations. |
| `04_index/` | **Semantic retrieval layer** over `01_sources` and `02_notes` only. |
| `04_index/lancedb/` | Vector store (local `bge-m3` embeddings). |
| `04_index/chunks/` | Heading-aware chunks with source and section metadata. |
| `04_index/bm25/` | Lexical index, fused with vectors via reciprocal rank fusion. |
| `05_tools/` | The machinery. Reproducible, re-runnable, no manual steps. |
| `05_tools/ingest/` | Document → Markdown conversion and chunking. |
| `05_tools/query/` | `kb.py` — hybrid retrieval CLI. |
| `05_tools/db/` | CSV/GDB → DuckDB loaders and profilers. |
| `05_tools/env/` | Dependency pins and environment setup. |
| `06_manifest/` | Integrity and provenance tracking. |
| `06_manifest/checksums/` | SHA-256 of every file in `DATA/`, to detect drift. |
| `06_manifest/inventory/` | File inventory: what exists, what it is, when it was ingested. |
| `06_manifest/logs/` | Ingest and index build logs. |

## Retrieval contract

| Question type | Answered from | Never answered from |
|---|---|---|
| Counts, sums, distributions, dates | `03_db` (SQL) | `04_index` |
| Scope, rules, definitions, decisions | `00_canon` (always in context) | `04_index` |
| "What does the thesis say about X" | `04_index` → then read full source | memory |
| Geography, coordinates, distances | `03_db/geo` | `04_index` |
