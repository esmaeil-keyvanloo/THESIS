---
name: report-standard
title: Deliverable Report Standard
type: canon
category: constraints
status: binding
updated: 2026-08-08
---

# Deliverable Report Standard

All formal reports for this thesis are **Word `.docx`** documents built with
the `docx` skill, delivered to `W<n>/04_outputs/reports/`.

## Mandatory structure (in order)

| # | Section | Notes |
|---|---|---|
| 1 | Cover page | Thesis title, author, institution, date, round reference |
| 2 | Title page | Report-specific title |
| 3 | Table of contents | Auto-generated, hyperlinked |
| 4 | List of tables | Numbered, with captions |
| 5 | List of figures / images | Numbered, with captions |
| 6 | Contractions and abbreviations | PT ↔ EN where relevant |
| 7 | Executive summary | Standalone; readable without the body |
| 8 | Report body | Sectioned, every claim cited to `DATA/` or `Brain/` |
| 9 | Conclusion | |
| 10 | Recommendations | Actionable, prioritised |
| 11 | References | |
| 12 | Appendices | Raw tables, code, query outputs |

## Rules

- Every table and figure is numbered and captioned, and appears in its list.
- Every quantitative statement traces to a SQL query in `Brain/03_db/`;
  the query goes in an appendix.
- Every qualitative claim cites its source document and section.
- Anything unavailable is written `NOT IN SOURCE`, never estimated silently.

## Chat vs report

Chat responses stay terse — bullets and tables only. Depth lives here.
