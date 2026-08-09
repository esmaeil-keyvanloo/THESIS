# Sensor-based Recyclables Collection Planning

PhD thesis working repository — **Esmaeil Keyvanloo** · Rio Maior case study (Portugal).

The thesis optimises the location of recyclable-waste containers using four years
of container fill-level sensor data (2020–2024), with routing and scheduling as
conditional extensions.

**Methodological chain:** demand estimation (regression on sensor-derived fill
rates) → deterministic capacitated p-median (baseline) → Monte Carlo demand
scenarios → stochastic capacitated p-median (main model) → robust/sensitivity
comparison.

## Repository layout

| Folder | Role | Rule |
|---|---|---|
| `DATA/` | Original data & documents — **frozen source of truth** | Never edited; SHA-256 manifest in `Brain/06_manifest/` |
| `Brain/` | Persistent knowledge base: canon (scope, constraints, data dictionary, decisions), Markdown-converted sources, notes, DuckDB/GeoPackage numeric layer, hybrid semantic index, tooling | Append-only, verified; every claim cites a source |
| `W1/` | Working round 1: plans, scripts, models, outputs, logs | Disposable; verified results promoted to `Brain/` |
| `.claude/skills/` | Project skills (e.g. `human-writing` — de-AI style linter for deliverables) | |

Full navigation: [Brain/README.md](Brain/README.md) · [W1/README.md](W1/README.md)

## Key artefacts

- **Methodology audit report** — `W1/04_outputs/reports/R1-01_Methodology_Audit.docx` (22 pp): data defect register D1–D7, method explanations with OMML equations, audit verdict, 11 prioritised recommendations, data-acquisition guide (who to ask, what to request)
- **Data dictionary & rulings** — `Brain/00_canon/data/data-dictionary.md`
- **Scope decision log** — `Brain/00_canon/decisions/ADR-001-scope-and-methodology.md`
- **Operational parameters (public sources)** — `Brain/02_notes/literature/valorsul-operations-lopes-2014.md` (Valorsul CTRO depot, fleet, 82 circuits, shift times)
- **Maps** — `W1/04_outputs/maps/` (container network, population, sensor coverage)

## Status (2026-08-10)

| Stage | State |
|---|---|
| Knowledge base, DB, semantic index | ✅ built |
| CSV semantics interview + defect register | ✅ recorded in canon |
| Operational data (depot, fleet, policy) | ✅ documented from public sources |
| Methodology audit report R1-01 | ✅ delivered |
| Demand model rebuild (sensor fill rates) | ⏭ next — critical path |
| Container ID reconciliation (D6), BGRI fix (D7) | ⏭ next |
| Real p-median instance (OSM network distances) | pending demand rebuild |

## Reproducibility notes

- `DATA/XLS/Enchimentos_de_Sensores[RioMaior].csv` (163 MB) exceeds GitHub's
  100 MB file limit and is **not in the repository**. Its exact content is
  preserved as `Brain/03_db/parquet/raw_sensors.parquet` (zstd, 7.6 MB);
  regenerate the CSV-equivalent tables from there or place the original file
  back under `DATA/XLS/` locally.
- `Brain/03_db/duckdb/rio.duckdb` and `Brain/04_index/` are **regenerable**:
  `python Brain/05_tools/db/build_db.py` and
  `python Brain/05_tools/ingest/build_index.py`.
- Report build: `node W1/01_scripts/python/build_report.js` (deps via npm).

---

*This README is a living document: it is updated at the close of every working
session and whenever a round (`W<n>`) opens, closes, or a major artefact lands.*
