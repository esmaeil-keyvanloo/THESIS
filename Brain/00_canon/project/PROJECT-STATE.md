# PROJECT-STATE — live session-state file

> **Rule for every chat:** read this file at start; update it at session close and after every major deliverable. Newest entries on top. Keep it tight — details live in the linked files, not here.
> Last updated: **2026-08-13** (session S2).

## 1. Data map — what each dataset is and what it is for

| Data | Where | Purpose (question it answers) |
|---|---|---|
| Driver CSV (264,817 rows, 816 containers) | `DATA/XLS/Enchimentos_com_Recolhas…` → `Brain/03_db/parquet/raw_collections.parquet` | Network-wide relative demand; glass demand; driver-vs-sensor chapter; partial route codes (92, CE=packaging/CP=paper) |
| Sensor CSV (1,048,575 rows, 344 containers, truncated D1) | `DATA/XLS/Enchimentos_de_Sensores…` → `raw_sensors.parquet` | Fill-rate (demand) estimation; cadence 2.55/day; unit unverified (D3, ceiling 82–84); excludes glass (2 units) |
| Reconciled container layer (816 pts + per-container stats) | `W2/02_data_work/containers_reconciled.geojson` | **Canonical container dataset** — demand points and candidate sites for p-median |
| Container registry snapshot (464 bins, 193 instrumented) | `DATA/GEO DATA/gis rio.gdb` | Cross-check only; encoding damaged; other gdb layers retired (border is km smaller than CAOP) |
| GIS_DATA library (6 GB, 52 styled QGIS layers) | `GIS_DATA/` + `GIS_DATA/README.md` | Boundaries (CAOP 2025), BGRI 2021/2011 census, COS/CRUS land use, MDT 10 m + slope, flood/fire hazard, rivers, E-REDES grid, OSM roads — covariates, constraints, network |
| QGIS project | `DATA/QGIS Layout template/QGIS Thesis.qgz` | All layers grouped MY DATA / DOWNLOADED; W2 layouts M1–M4 |
| Knowledge base | `Brain/` (canon, sources, notes, DuckDB, index) | Provenance, defect register D1–D7, data dictionary |

## 2. Chat log — sessions, main points, outputs

### S18 — 2026-08-19 latest (W4 MASTER REBUILD; same chat)
- **T1** merge pass: 477 of 1,147 splits re-merged (ceiling policy); 108 carry speed_flags (117 junctions drawn DOTTED in explorer w/ tooltip); 554 multi-vehicle + 116 batch-entry stay split. Tracks 11,495 → 11,016 (+2,445 phantoms = 13,461).
- **T2** all loose readings assigned: 85,597 'I' (p≥0.7) + 37,761 'L' low-confidence ("?" markers); leftovers 20,905.
- **T3** phantoms: 2,445 reconstructed vehicles (≥3 stops, dotted lines, Phantom filter) absorbing 20,368 stops; 537 isolated observations remain.
- **T4** sensor drop-log: 47,093 machine-recorded emptying events; sensors see 1.5–2.4 drops per stamped emptying from 2021+; agreement flat ~50% (instruments non-interchangeable) while hardware improved (negatives 36.6%→2.6%).
- **T5** comparison (bin-days, instrumented): both 14,233 | driver-only 39,764 (81.9% explained by sensor faults/low cadence; 7,211 candidate false stamps) | sensor-only 32,203 → **30,504 recovered emptyings ≈ 1,678 t** never in the logbook.
- **T6** census: stamped_single 8,837 · merged_clean 369 · merged_flagged 108 · split_multi 1,268 · split_batch 434 · phantom 2,445. **Master dataset frozen: `Brain/03_db/parquet/master_events_w4.parquet`** (311,910 rows = 264,817 driver + 47,093 sensor; every raw line classified; schema in W4/02_data_work/master_schema.md).
- ⚠ Known defect (documented): intermediate `W4/02_data_work/trips_v6.json` double-carries relabeled stops — DO NOT USE; canonical are trips_v6_enriched.json and the master parquet (both verified clean, 60,916 genuine S).
- Explorer W4 live (root redirect updated): dotted above-legal segments, "?" low-conf stops, phantom layer, merge badges. Vercel LIVE on W4 (root dir fixed — failure cause was a trailing space in the setting: 'W4/03_outputs/explorer '); Pages live too. Deep links: ?trip=ID. Local: port 8766.

### S17 — 2026-08-19 latest (KMZ export; same chat)
- Explorer: 'Download selected trips as KMZ' — one folder per trip, sub-folders by geometry (Route line / numbered Stops points / depot+disposal legs), popup data tables per placemark; client-side KML+ZIP generation, validated (DOMParser + python zipfile). OPEN TOPICS parked for W4: split-identifier forensics, assign-all-ambiguous with <70/30 flag, phantom tracks, sensor drop-log + full file comparison, master dataset.

### S16 — 2026-08-19 (ID convention + raw workbook; same chat)
- **ID convention (binding, in CLAUDE.md):** Trip ID = idrecolha + track letter (e.g. 17242b), shown in ALL outputs; Row ID = line number in the original CSV. idrecolha alone is NOT a trip reference (splits + stampless rows).
- New deliverables in `W3/03_outputs/tables/`: raw CSV copy + **Raw_Drivers_Data.xlsx** (264,817 rows in original file order; helper cols Row ID / Trip ID / Row type incl. non-assignment reasons) + sorted workbook v5 (headers now Trip ID + **Raw Row ID** back-reference).
- Explorer chips/cards show #TripID. CLAUDE.md gained the **[Rephrase]** interaction rule (restate understanding → approval → simple human tone, technical terms in brackets).

### S15 — 2026-08-19 latest (Explorer v9 + folder discipline; same chat)
- **RULE (user, binding): a round's outputs are written ONLY inside that round's folder; older W folders are read-only inputs.** Violation corrected: canonical Excel moved to `W3/03_outputs/tables/Driver_Trips_Sorted.xlsx` (v4 builder now writes there); W2's historical v3 xlsx lives in git history (commit 570c8ccb^).
- Map markers now ring-coloured by the bin's OWN material (route line keeps trip colour) — cross-material observations visible on the map itself; inferred bins show informational Est. kg in tables (101,682 added; summary math unchanged); sensor matching now includes error codes: 23,303 valid + 11,247 negatives shown faded (raw code, no agreement mark). enrich_v9.py.

### S14 — 2026-08-19 (Excel v4; same chat)
- Excel updated to match Explorer v8 (`W3/01_scripts/build_trips_excel_v4.py`, 32.4 MB, same canonical path): 8 helper columns — Bin material (other-material rows = observed at shared site, never emptied by this truck), Fill % before emptying, Sensor fill % (±3 h, of ceiling), Est. kg (mid density). Sheet 2 gained Bin material. READ ME extended.
- Direction set by user: converge toward **one reliable analytical dataset** for the thesis statistics — candidates to merge: event_level_dataset.parquet + trips_v5_enriched + sensor_active_windows + bins_categorized. Next round (W4?) should build and freeze it in Brain/03_db.

### S13 — 2026-08-19 latest (v8: material-pure capped estimate + sensor columns; same chat)
- Two-value weight estimate per trip: emptied-only (strict) and **+ same-material observed bins, capped at the identifier's weighbridge load** (user's cap idea; other-material observations NEVER counted — trips are material-pure). Median share rises only 5.0→6.2%; 2,072 tracks hit the cap → density mids can overshoot on sparse runs (strict share >100% shown as ≥100%).
- Sensor integration in explorer: 25,127 stops matched to a sensor reading (±3 h, % of own ceiling); detail tables gained Mat dot (bin's own material) + Sensor column with ✓/⚠ agreement (one 25-pt step); per-trip "Sensor check" line. `W3/01_scripts/enrich_v8.py`; stops now 9-element.

### S12 — 2026-08-19 (weight-share estimate; same chat)
- **Recorded bins explain a median 5.0% of the weighbridge load** (packaging 3.6% / paper 8.6% / glass 12.0%; p10–p90 = 1.9–22%; 5,739 unsplit runs). Method: stamped stops only × bin volume × pre-emptying fill × literature density bands (P 25–40, C 50–100, G 250–350 kg/m³). `W3/01_scripts/estimate_weights.py`, `W3/02_data_work/weightshare_analysis.json`. Weight-based twin of the 3× km finding — most served bins were never logged.
- Explorer cards: est-weight band + share row; bin detail tables gained per-bin Est. kg column.

### S11 — 2026-08-19 later (Explorer v7 + Vercel; same chat)
- Deployed on Vercel too (user's account, GitHub-import, Root Directory = W3/03_outputs/explorer; auto-deploys on push). Local double-click needs `Open_Explorer_Locally.bat` (fetch blocked on file://); W2 monolith = offline copy.
- **v7 fixes/features** (user-reported bug: "missing" stop numbers were markers stacked at shared ecoponto sites): co-located markers spread in a ring — verified CE19b 2/2, CE39 11/11 distinct; stops enriched with fills (`enrich_stops.py`: stamped stops carry pre-emptying fill, 98.5% coverage); per-trip expandable bin tables (№/bin/time/type/fill), row click zooms to bin; panels drag-resize + collapse; chart/depot/notes behind ⓘ button; boundaries auto-flip light on satellite, Rio Maior line bolder. End-to-end browser-tested.

### S10 — 2026-08-19 (W3: fast split explorer for GitHub Pages; same chat)
- GitHub Pages activated by user: https://esmaeil-keyvanloo.github.io/THESIS/ (root index.html redirects to the explorer). Public — operational data visible to anyone with the link.
- **W3 round opened**: explorer split for speed — `W3/03_outputs/explorer/` = small shell (index.html, ~35 KB) + `data/` (trips_index 1.5 MB; per-year chunks 0.8–4.6 MB; boundaries/bins/facilities/daily/tempo ~0.2 MB). Page interactive after ~1.7 MB (was 20 MB monolith); year chunks lazy-load in background; splitter `W3/01_scripts/split_explorer_data.py`.
- W2 monolith kept as the offline single-file version. Vercel offered as optional mirror (needs user's own account; GitHub-import auto-deploys).

### S9 — 2026-08-17 (Explorer v6: basemaps + smooth routes; same chat)
- Basemap switcher: Street (OSM) / Satellite (Esri) / Satellite hybrid (labels) / Topography (OpenTopoMap) / Light (CARTO) — top-left control, no API keys.
- Routes re-exported at 8 m simplify tolerance as encoded polylines (`route_export_fine.py` → trips_routed_v5_fine.json 7.2 MB, depot_legs_v5_fine.json 3.6 MB — smaller than the old 60–100 m files); lines now hug the carriageway on satellite. Template v6 decodes polylines client-side.

### S8 — 2026-08-17 (glass rebuild, heat calendar, boundaries; same chat)
- **Glass correction**: earlier trips.json had silently dropped ALL glass runs; raw holds 556 glass identifiers (281 multi-bin). Full v5 pipeline rebuilt: 11,495 tracks (6,147 packaging / 4,751 paper / 597 glass), re-segmented, re-assigned (103,134 inferred stops), re-routed (8,242 tracks, 0 fallbacks).
- **Trip facts confirmed on full set**: trips are material-pure (99.97%); glass has no dedicated days (93% of glass days coincide with other fractions, ~6 multi-bin glass runs/month, Wed–Fri); ~3× km finding holds incl. glass (median 2.49×, consistent across fractions).
- **Caveat (stats agent)**: inferred stops are fraction-blind — only 13.7% match trip fraction (co-located ecoponto bins). They are path observations, NOT collection events; never count them as emptyings.
- **Explorer v5**: heat calendar (day background = kg collected, global scale, tooltip kg; month headers with tonnes), fraction strips per day (P/C/G), Glass button + green trips, CAOP boundaries layer (muni + 10 freguesias). Heaviest day: 2020-08-06, 58,020 kg.
- Excel rebuilt glass-inclusive: 223,688 rows in trip blocks / 41,129 not assignable / all 264,817 accounted.
- Files: trips_v5*.json, reading_assignments_v5.parquet, boundaries.json, daily_kg.json, stats_v5.json, dumpleg_analysis_v5.json.

### S7 — 2026-08-17 later (loose-reading assignment, waste-facility map, dump-leg verdict; same chat)
- **144,263 unstamped readings resolved**: 107,821 (74.7%) assigned to tracks by time+proximity (≤60 km/h feasibility, nearest-feasible, 1.5× ambiguity rule); 34,956 ambiguous (flagged, not forced); 1,486 infeasible/no-trip. `trips_v4.json` has them as "I" stops; Excel rebuilt: 228,375 rows in trip blocks / 36,442 not assignable with reasons.
- **Waste-facility inventory** (`facilities_v2.json`): only 2 licensed tipping points in the municipality — Valorsul transfer station (39.3196,−8.9241) + Ecocentro (39.3174,−8.9108); recyclables flow onward (Valorsul's haul, not municipal): TS → CTRO sorting Cadaval; undifferentiated → S. João da Talha incinerator / Mato da Cruz landfill. 39 regional sites mapped.
- **Dump-leg hypothesis TESTED AND REJECTED in strong form**: recorded km ≈ **3.1×** shortest-path through ALL known stops + depot + dump legs (539 clean runs; surplus ~107 km/run; uncorrelated with TS distance; morning=afternoon). Meaning: trucks sweep far more than logged bins — logged stops are a hard lower bound (~1/3) of real driving. Dump leg itself small (~9 km loop).
- Explorer v4: inferred stops (dashed numbered markers), dashed depot/TS legs with km, 50 facilities. Weight clarified everywhere: container 2500 = litres; Peso = weighbridge run total; never derived from fill.

### S6 — 2026-08-17 (spatio-temporal track segmentation, Explorer v3; same chat)
- User flagged impossible trip lines (far-apart stops connected by time order). Verified: 6.6% of 49,662 consecutive segments implied >60 km/h (p99 = 467 km/h) → parallel vehicles under one identifier + sparse logging.
- Built `segment_tracks.py`: greedy track assignment, VMAX 60 km/h implied (haversine ×1.3 detour, 2-min service time). 1,137 of 3,430 identifiers split (935→2 tracks, 191→3, 9→4, 2 pathological); **0 violating segments after**; 4,423 physically consistent vehicle tracks; re-routed on road graph (0 disconnected).
- Explorer v3 delivered: tracks labelled a/b/c under their identifier, shared kg/km totals marked "whole identifier". Data: `trips_v3.json`, `trips_routed_v3.json`, `segmentation_stats.json`.
- Caveat for demand/routing work: km_rec and kg cannot be split across an identifier's tracks — allocation still blocked on operator info.
- **Driver_Trips_Sorted.xlsx** (`W2/03_outputs/tables/`): driver rows arranged trip-by-trip (11,577 track blocks, white/gray banding, stops in service order, 59,638 pre-readings attached to their visits; 144k unattachable readings in sheet 2; sensors untouched by request).
- User self-downloaded the **DGT 50 cm LiDAR** into `GIS_DATA/04_elevation/` (~20 GB incl. MDT-50cm.vrt) — fine-terrain upgrade now available locally; GIS_DATA excluded from git (re-downloadable, see .gitignore).

### S5 — 2026-08-15 later (9-question trip analytics + Explorer v2; same chat)
- Parallel workflow (4 agents): typology/hotspots, OSM road routing, temporal aggregates, depot inference. Key results: trips fraction-pure (99.97%), packaging+paper run SAME days (818/1,200 both); two-bin "trips" last as long as 15+-bin ones (7.4 h/122 km vs 8.1 h/175 km) → identifiers span full shifts, logging partial; **unnecessary emptyings (≤50% full at emptying): 25.4% overall, falling 41.9% (2020) → 8.1% (2024)**; 816 bins categorized 233 high/315 moderate/221 low/47 no-data; depot = Estaleiro Municipal (39.3392,-8.9249), disposal = Valorsul transfer station + Ecocentro SE (Zona Industrial); morning trips start in town, afternoon in southern parishes; **NEW data-quality find: sensor scale discontinuity Nov 2020** (median ~100% of ceiling before, 33–46% after).
- **Trip Explorer v2** (`W2/03_outputs/Trip_Explorer_RioMaior.html`, 14.3 MB): road-following routes (3,430 trips routed, 0 disconnected legs, dijkstra on drivable OSM graph), stops numbered from 1, fraction-coloured trips + split-colour calendar, depot/disposal markers, 816-bin category layer, monthly-kg strip. Browser-verified.
- Temporal tables `W2/03_outputs/tables/temporal_{daily,weekly,monthly,seasonal,annual}.csv` + figures F10–F12. Annual: 2020 2,821 trips/7,194 t/362k km → 2023 1,573/4,414 t/210k km; kg/km stable 19–21.

### S4 — 2026-08-15 (plain-language rewrite + trips webGIS; same chat)
- Second review round: **154 in-document comments** extracted (preserved: `W2/02_data_work/review_comments_2026-08-15_extracted.txt`). Core asks: simple human language, cautious wording, trips analysis + interactive webGIS, negatives decision closed, active windows explained.
- **R2-01 Rev D**: full plain-language rewrite — opens with "The story in plain words"; zeros reconciled exactly (60,273 + 2,828 + 81,703); negatives DECISION: drop from fill analysis, keep as QC metadata, no interpolation across bursts, >24 h bursts subtracted from exposure (threshold provisional); sensor 82–84 = unresolved upper bound (blind-zone hypothesis); record-level (not event-level) comparison naming; D5 (weight attribution) + D8 (repeated trip totals) registered; N=452 attempts documented; disposition by certainty (resolved / provisional / open).
- **Trips**: 9,984 collection identifiers → 3,430 multi-bin trips (median 4 bins, 7.6 h, 135 km, 2,300 kg, 16.8 kg/km; straight-line path ≈13% of recorded km; 66% single-bin identifiers → partial recording). `W2/02_data_work/{trips.json, trip_stats.json}`.
- **Trip_Explorer_RioMaior.html** (`W2/03_outputs/`): self-contained Leaflet webGIS — calendar shaded by trips/day, per-day trip chips, multi-trip map drawing, per-trip stat cards. Verified working in browser.

### S3 — 2026-08-14 (review response + event-level comparison; same chat as S2)
- Addressed all 15 review comments on R2-01 (2 user + 13 Codex) → **Rev B**: exec summary restructured, registry as inference, zeros decomposed (60,273 post-emptying confirmations vs 81,703 standalone), cadence three denominators (1.93/2.55/1.58) + per-container active windows, shift structure found (04–06 h & 14–15 h), run-weight allocation held, glass explained by site policy (270 sites), CE46 + Óbidos route exceptions, N=452 not reproducible, D6 reclassified. Six charts F1–F6; maps rebuilt on thesis template (stats box lower-left, tidy legends).
- **Rev C** added event-level comparison (user items 1–7): nearest-reading matching ±3 h (sensitivity stable across 7 windows), agreement only **45.2% within one driver step** → instruments non-interchangeable; ceiling cases 1,758/10,153; driver −1 = missing; `event_level_dataset.parquet` (127,928 rows, QC flags, selected fill on 58.8%); negatives rule (two families, episode evidence, no interpolation).
- New key artifacts: `W2/02_data_work/{event_level_dataset.parquet, match_stats.json, codex_verification.json, sensor_active_windows.csv, collection_runs.csv}`, figures F1–F9, R2-01 Rev C.
- Ops: QGIS SCP plugin disabled; crash root cause = GC'd legend trees (pin refs via builtins); QGIS relaunch procedure + port monitor.

### S2 — 2026-08-13 (GIS data acquisition + driver/sensor reconciliation)
- Built `GIS_DATA/` (research → download → clip to study area +10 km, EPSG:3763); loaded 52 styled layers into QGIS; reorganized tree into MY DATA / DOWNLOADED.
- **R1-02 GIS Data Inventory** (`W1/04_outputs/reports/`): what's held / downloaded / must-be-requested, with relevance ratings.
- **R2-01 Driver–Sensor Reconciliation** (`W2/03_outputs/reports/`): 344 ⊂ 816, zero mismatches, one master registry; glass uninstrumented (258→2); all 816 inside municipality; maps W2-M1…M4 with HTML stat boxes.
- Ops notes: QGIS crash cause found (Python-owned legend tree GC'd) and fixed; SCP plugin disabled; DGT CDD LiDAR (2 m/50 cm) deferred — needs user's own login.
- Answered: routes/schedules/shifts are NOT public → request letters to Valorsul + Câmara (guide in R1-01).

### S1 — 2026-08-08 (repository + audit round)
- Built Brain (canon, converted sources, DuckDB, hybrid index), W1 structure, maps M1–M3.
- **R1-01 Methodology Audit**: defect register D1–D7, method chain, data-acquisition guide.

## 3. Open items / next steps
1. **R1-01 feedback** — user is reviewing; will send comments in the S2 chat; develop the audit accordingly.
2. **Data request letters** (Valorsul + Câmara): D1 re-export, routes/GPS/weights/shifts — top blocker.
3. **Routable graph** from OSM roads + MDT slope costs — unblocked, not started.
4. **D7/BGRI rebuild reminder** — when the database is ready: container/demand analysis on BGRI 2021 + OSM network (memory: reminder-d7-rebuild).
5. CDD LiDAR fine terrain — only if micro-siting chapter happens (user account exists).

## 4. Session digests (chat backup)
Full per-session digests: `Brain/01_sources/sessions/` — one file per session, git-committed, survives chat deletion.
