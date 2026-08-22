# Session digest S18 — 2026-08-19 (W4 master rebuild; same chat)

## What ran (8 agents, 4 waves)
- **T1 merge pass**: ceiling policy (user decision after their Google-Maps falsification of #40265): 477/1,147 splits re-merged; 108 merged trips carry 117 speed-flagged junctions (feasible only above truck-legal speeds) — drawn as DOTTED segments with tooltips; 554 multi-vehicle + 116 batch-entry stay split. Deep research confirmed: A15 is the only >90 road (120 = car limit); trucks limiter-capped at 90; even absurd speeds merge max 478.
- **T2 assign-all**: every feasible loose reading assigned: 85,597 'I' (p≥0.7) + 37,761 'L' low-confidence ('?' markers, quiet style per user).
- **T3 phantoms**: 2,445 reconstructed vehicles (dotted lines, Phantom filter button), 20,368 stops; 537 isolated observations left.
- **T4 sensor drop-log**: 47,093 machine emptying events (≥25-unit fall ≤24 h, negative-adjacent excluded); from 2021 sensors record 1.5–2.4 drops per stamped emptying; hardware improved (neg 36.6%→2.6%) but driver-sensor agreement flat ~50%.
- **T5 comparison** (instrumented bin-days): both 14,233 / driver-only 39,764 (81.9% explained by sensor faults or low cadence; 7,211 candidate false stamps) / sensor-only 32,203 → **30,504 recovered emptyings ≈ 1,678 t** absent from the logbook (per-year 113/441/415/439/270 t).
- **T6**: census (stamped_single 8,837 · merged_clean 369 · merged_flagged 108 · split_multi 1,268 · split_batch 434 · phantom 2,445) and **master dataset frozen: `Brain/03_db/parquet/master_events_w4.parquet`** — 311,910 rows (264,817 driver + 47,093 sensor), every raw CSV line classified exactly once; schema in `W4/02_data_work/master_schema.md`.

## Data-quality note (important)
`W4/02_data_work/trips_v6.json` (intermediate) double-carries readings (v5 'I' stops relabelled 'S' at merge + re-assigned) — flagged by two agents independently and corrected downstream. **Canonical files: trips_v6_enriched.json + master_events_w4.parquet** (verified: exactly 60,916 genuine stamped stops). Do not use trips_v6.json.

## Deliverables
- Explorer W4 (`W4/03_outputs/explorer/`, root redirect updated; Vercel Root Directory must be switched to this path by the user): dotted above-legal segments, '?' low-conf stops, phantom layer, merge badges on cards/chips.
- Excel v6 pair in `W4/03_outputs/tables/` (five row tiers incl. LOW CONFIDENCE and phantom; isolated-only sheet 2).
- All W4 scripts in `W4/01_scripts/`.

## Next (critical path unchanged)
Demand model on the master dataset (sensor drops = service events; active windows as denominators); then p-median instance.
