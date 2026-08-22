# master_events_w4.parquet — column dictionary

**Path:** `Brain/03_db/parquet/master_events_w4.parquet` (frozen W4 master dataset, task D1/T6a)
**Builder:** `W4/01_scripts/build_master_w4.py` · built 2026-08-22
**Rows: 311,910** = 264,817 driver readings (one per line of the raw driver CSV, natural pyarrow order) + 47,093 sensor drop events (`W4/02_data_work/sensor_drops.parquet`).

Grain: **one row per driver reading and one row per sensor drop event.** Nothing is duplicated: each of the 264,817 raw CSV lines appears exactly once, with exactly one `row_type`. This deliberately differs from `trips_v6.json`, whose stop lists double-carry readings (v5 inferred stops relabelled `S` at merge time plus a fresh I/L re-assignment of the same loose pool — 287,408 stops from 264,817 rows). Use this parquet, not the stop lists, for counting.

| Column | Type | Meaning |
|---|---|---|
| `source` | string | `driver` = row of the raw driver CSV; `sensor_drop` = sensor fill-drop event (≥25 raw units between consecutive valid readings, gap ≤24 h, negative-episode guarded — A2/T4 definition). |
| `raw_row_id` | Int64 | Driver rows: line number in the original CSV, 1…264,817, in pyarrow natural (file) order — the binding Row ID convention from S16. Null for sensor rows. |
| `cid` | string | Container id (`idcontentor`, trimmed). |
| `ts` | datetime | Driver rows: `Data da leitura`. Sensor rows: `ts_after` — the first reading showing the lower level (the drop is realised somewhere inside the before→after window; median window ≈ 4.7 h). |
| `trip_id` | string | Track the reading belongs to: idrecolha + part letter (`17466a`), plain idrecolha for unsplit tracks, or `PH…` phantom-track id for `P` rows. Null for isolated observations and all sensor rows. |
| `row_type` | string | Driver reading tier — `S` stamped collection record (the 60,916 rows with idrecolha whose stop is in the base stamped chain; the only rows that are *collections*); `pre` pre-emptying reading attached to the following stamped visit of the same bin (≤15 min); `I` loose reading assigned to a running track (p_best ≥ 0.7); `L` assigned low-confidence (p_best < 0.7); `P` absorbed into a phantom track (chain of ≥3 infeasible/no-trip readings); `isolated:INFEASIBLE` / `isolated:NO_TRIP_RUNNING` unattachable singletons. Null for sensor rows. **Canon: `I`, `L`, `P` and isolated rows are path observations, NOT collections.** |
| `fill` | float | Driver rows: raw `Enchimento` as logged (−1 = missing). Sensor rows: `fill_after` (raw units after the drop). |
| `sensor_pct` | float | Driver rows: nearest valid sensor reading within ±3 h, expressed as % of that container's own ceiling (from enrich_v9 matching; only where matched). Sensor rows: `pct_of_ceiling_before` — how full the bin read before the drop, % of ceiling. |
| `est_kg` | float | Driver rows: informational per-bin weight estimate carried from the enriched explorer stops (bin volume × pre-emptying fill × material mid density P 32 / C 75 / G 300 kg/m³); present on S/I/L stops with a usable fill. Sensor rows: `drop_units/100 × volume_l/1000 × mid density` — the recovered-emptying tonnage formula of C2/T5. Estimates, never weighbridge values. |
| `material` | string | `Packaging` / `Paper/card` / `Glass`, from the bin's `description` (driver rows) or the per-container registry mode (sensor rows). |
| `volume_l` | int | `Volume do tipo de contentor` (litres; 2500 = litres, never kg). Sensor rows: registry mode for the cid. |
| `kg_run_total` | float | Weighbridge total (`Peso total`) of the **whole identifier** (base_id) the row's track belongs to. **Repeats on every row of the identifier — canon: count kg once per identifier, never sum this column.** Null for phantom/isolated/sensor rows. |
| `km_run_total` | float | Recorded km (`Km totais`) of the whole identifier. Same repeat warning as `kg_run_total`. |
| `merged_flag` | boolean | True if the row's track is a re-merged split identifier (verdict `merge`, 477 tracks). Null where no v6 track. |
| `speed_flagged_trip` | boolean | True if the merged track carries speed flags (junction infeasible under TRUCK-LEGAL but feasible under CEILING — 108 tracks). |
| `p_best` | float | Assignment posterior for I/L rows (share of feasibility mass on the winning track; I ≥ 0.7 > L). Null otherwise. |
| `qc_negative` | boolean | Driver rows: raw fill < 0 (249 rows). Sensor rows: always False — drop events are built from valid (0–100) readings only; negative-code episodes are excluded upstream (see `sensor_quality.json`). |

## Companion census
`W4/02_data_work/trip_census.json` — trips by evidence class (stamped_single 8,837 · merged_clean 369 · merged_flagged 108 · split_multi_vehicle 1,268 · split_batch_entry 434 · phantom 2,445) and the reading-tier census (S 60,916 · pre 59,638 · I 85,597 · L 37,761 · P 20,368 · isolated 537 — sums to 264,817 exactly).

## Known caveats
- `trips_v6.json` stop lists are for map display; they over-count (see grain note). The master is the analytical source.
- `est_kg` on driver S rows uses the *pre-emptying* fill from enrichment while the `fill` column keeps the raw row value (often 0 = post-emptying confirmation); the two answer different questions.
- Sensor `ts` is an upper bound on the emptying time (event realised before `ts_after`).
- kg/km totals cannot be split across an identifier's a/b/c tracks (operator info still pending).
