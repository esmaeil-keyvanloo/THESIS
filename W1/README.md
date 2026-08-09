---
name: w1-map
title: W1 — Working Round 1
type: working-round
round: 1
status: open
opened: 2026-08-08
updated: 2026-08-08
---

# W1 — Working Round 1

A **working round** is one self-contained attempt at a body of work: its own
plan, scripts, models, intermediate data, outputs and logs.

When an approach changes fundamentally — a different formulation, a different
data treatment, a different thesis structure — the round is **closed** and
`W2` is opened. Rounds are never edited retroactively; that is what makes the
history auditable.

## Relationship to the Brain

| | Brain | W1 |
|---|---|---|
| Lifetime | Permanent | One round |
| Contains | Truth, sources, database, index | Attempts, scripts, experiments |
| Editable | Append-only, verified | Freely |
| On failure | Untouched | Superseded by `W2` |

Verified results are **promoted** from `W1/04_outputs/` into
`Brain/02_notes/results/`. Nothing else crosses the boundary.
Every promotion is recorded in `Brain/00_canon/decisions/`.

## Structure

| Folder | Purpose |
|---|---|
| `00_plan/` | What this round is trying to achieve, and how we will know it worked. |
| `00_plan/objective/` | Round objective, scope boundary, and what is deliberately excluded. |
| `00_plan/tasks/` | Task breakdown and running status. |
| `00_plan/acceptance/` | Exit criteria — the conditions for closing this round. |
| `01_scripts/` | All executable code for this round. |
| `01_scripts/python/` | Data preparation, analysis, optimisation drivers. |
| `01_scripts/r/` | Statistical work and regression (continuation of `DATA/SCRIPT/`). |
| `01_scripts/sql/` | DuckDB queries against `Brain/03_db/`. |
| `01_scripts/mosel/` | Xpress-Mosel models (continuation of `DATA/Xpress fico/`). |
| `02_models/` | Model formulations and their instance/solution files. |
| `02_models/location_pmedian/` | **Core** — strategic container location. |
| `02_models/vrp/` | Tactical — vehicle routing. |
| `02_models/irp/` | Tactical — inventory routing. |
| `02_models/scheduling/` | Operational — collection scheduling. |
| `03_data_work/` | Derived, **disposable** data. Safe to delete and regenerate. |
| `03_data_work/interim/` | Partially cleaned intermediates. |
| `03_data_work/processed/` | Model-ready datasets. |
| `03_data_work/features/` | Engineered features (fill rates, seasonality, demand). |
| `04_outputs/` | Presentable results. Candidates for promotion to the Brain. |
| `04_outputs/figures/` | Charts and plots. |
| `04_outputs/tables/` | Result tables for the thesis. |
| `04_outputs/maps/` | Spatial outputs for Rio Maior. |
| `04_outputs/reports/` | Written summaries of this round. |
| `05_logs/` | Execution record. |
| `05_logs/runs/` | Run logs, solver output, timings. |
| `05_logs/errors/` | Failures worth remembering. |
| `06_review/` | Closing the round. |
| `06_review/open_issues/` | Unresolved problems carried into the next round. |
| `06_review/handover/` | Summary written when this round closes and `W2` opens. |

## Status

Round opened. Objective not yet written — pending the CSV interview and the
first full read of the source documents.
