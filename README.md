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
| `GIS_DATA/` | Open spatial data library for Rio Maior (admin, OSM, census, land use, elevation, hydro, hazards, utilities) — see `GIS_DATA/README.md` for sources & licenses | Clipped to study area +10 km, EPSG:3763; large national files re-downloadable from documented URLs |
| `Brain/` | Persistent knowledge base: canon (scope, constraints, data dictionary, decisions), Markdown-converted sources, notes, DuckDB/GeoPackage numeric layer, hybrid semantic index, tooling | Append-only, verified; every claim cites a source |
| `W1/` | Working round 1: plans, scripts, models, outputs, logs | Disposable; verified results promoted to `Brain/` |
| `W2/` | Working round 2: driver–sensor reconciliation (scripts, reconciled layer, maps, report R2-01) | Same rule |
| `W3/` | Working round 3: fast split Trip Explorer (superseded by W4) | Read-only history |
| `W4/` | Working round 4: merged/flagged trips, all-readings assignment, phantom tracks, sensor drop-log, master dataset | Read-only history |
| `W5/` | Working round 5: road-legal speed engine + calibrated tolerances, audited & rebuilt trips v7, cleaned sensors v2 (rebound-aware drop log), driver–sensor fusion with source tags, circuit-dissolution finding, three reconciled Excel workbooks, responsive two-skin explorer (hybrid neumorph / editorial) with playback — live at esmaeil-keyvanloo.github.io/THESIS | Current round |
| `.claude/skills/` | Project skills (e.g. `human-writing` — de-AI style linter for deliverables) | |

Full navigation: [Brain/README.md](Brain/README.md) · [W1/README.md](W1/README.md)

## Key artefacts

- **Methodology audit report** — `W1/04_outputs/reports/R1-01_Methodology_Audit.docx` (22 pp): data defect register D1–D7, method explanations with OMML equations, audit verdict, 11 prioritised recommendations, data-acquisition guide (who to ask, what to request)
- **Data dictionary & rulings** — `Brain/00_canon/data/data-dictionary.md`
- **Scope decision log** — `Brain/00_canon/decisions/ADR-001-scope-and-methodology.md`
- **Operational parameters (public sources)** — `Brain/02_notes/literature/valorsul-operations-lopes-2014.md` (Valorsul CTRO depot, fleet, 82 circuits, shift times)
- **Data-request sheets (municipality + Valorsul, PT/EN)** — `W5/03_outputs/reports/Data_Request_Sheets.docx`
- **Maps** — `W1/04_outputs/maps/` (container network, population, sensor coverage)

## Status (2026-08-24)

| Stage | State |
|---|---|
| Knowledge base, DB, semantic index | ✅ built |
| CSV semantics interview + defect register | ✅ recorded in canon |
| Operational data (depot, fleet, policy) | ✅ documented from public sources |
| Methodology audit report R1-01 | ✅ delivered |
| GIS data library (`GIS_DATA/`, 6 GB, 52 styled layers in QGIS project) | ✅ built 2026-08-13 |
| Driver–sensor reconciliation (816 vs 344, report R2-01 Rev C, event-level QC dataset) | ✅ delivered 2026-08-14 |
| Trip analytics: vehicle-track segmentation, road-routed Trip Explorer v3, depot/disposal ID, hotspot categories, temporal tables | ✅ delivered 2026-08-17 |
| Trip-sorted driver workbook — 3 tiers, 75% of loose readings assigned (`W2/03_outputs/tables/Driver_Trips_Sorted.xlsx`) | ✅ delivered 2026-08-17 |
| Fleet story: waste-facility map, dump-leg km audit (recorded km ≈ 3× logged-stop route), Explorer v4 | ✅ delivered 2026-08-17 |
| Glass-inclusive rebuild (597 glass tracks recovered), Explorer v5: heat calendar, fraction strips, CAOP boundaries | ✅ delivered 2026-08-17 |
| W4 master rebuild: 477 splits re-merged (108 speed-flagged), all readings assigned (85.6k + 37.8k low-conf), 2,445 phantom tracks, 47k sensor drop events, master dataset frozen in Brain/03_db | ✅ delivered 2026-08-19 |
| W5 thesis-grade rebuild: per-road-type legal-speed engine (272-site matrix) + data-calibrated tolerances; full trip & sensor audits (12+12 findings); trips v7 (11,691 + 1,674 phantoms; I 120.8k, L 7.8k, evictions resolved); sensors v2 (75.5% kept; 47.5k drops, 44% rebound-demoted); fusion with D/DS/S source tags (9.5k corroborated stops, 38.4k sensor-only events on trips); 151 standing circuits — coverage dissolves 59.8% (2020) → 0% (2024); 3 m routes with playback anchors; three reconciled Excel workbooks + master_events_w5; responsive two-skin explorer (hybrid neumorph + editorial) with 3-way source views, ⓘ source-of-truth tabs, methodology page, animated trip playback — E2E-tested on 6 viewport sizes | ✅ delivered 2026-08-24 |
| Demand model rebuild (sensor fill rates, on master_events_w5) | ⏭ next — critical path |
| Container ID reconciliation (D6), BGRI fix (D7) | ⏭ next |
| Real p-median instance (OSM network distances) | pending demand rebuild |

## Reproducibility notes

- `DATA/XLS/Enchimentos_de_Sensores[RioMaior].csv` (163 MB) exceeds GitHub's
  100 MB file limit and is **not in the repository**. Its exact content is
  preserved as `Brain/03_db/parquet/raw_sensors.parquet` (zstd, 7.6 MB);
  regenerate the CSV-equivalent tables from there or place the original file
  back under `DATA/XLS/` locally.
- `GIS_DATA/` contents are **not in the repository** (multi-GB open datasets incl.
  user-downloaded 50 cm LiDAR): every layer is re-downloadable via the URLs in
  `GIS_DATA/README.md`, which is versioned. `W2/02_data_work/trips_routed*.json`
  regenerate via `W2/01_scripts/route_trips_v3.py`.
- `Brain/03_db/duckdb/rio.duckdb` and `Brain/04_index/` are **regenerable**:
  `python Brain/05_tools/db/build_db.py` and
  `python Brain/05_tools/ingest/build_index.py`.
- Report build: `node W1/01_scripts/python/build_report.js` (deps via npm).

---

*This README is a living document: it is updated at the close of every working
session and whenever a round (`W<n>`) opens, closes, or a major artefact lands.*
