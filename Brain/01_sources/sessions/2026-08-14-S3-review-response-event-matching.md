# Session digest S3 — 2026-08-14 (continuation of the S2 chat)

## Scope
Respond to the external review of R2-01 (15 comments); add the event-level driver–sensor comparison requested by the user; redeliver R2-01 (Rev B, then Rev C).

## Review response (Rev B)
- Executive summary restructured: matches / differs / uncertain / safe-next.
- "One master registry" downgraded to inference.
- Zeros decomposed: all 60,916 collection-event rows are fill=0 by construction; 60,273 zeros are post-emptying confirmations (paired ≤15 min to a nonzero reading); 81,703 standalone. Fill-at-collection must use pre-emptying readings.
- Cadence: 1.93 (calendar) / 2.55 (days with readings) / 1.58 (median within own active window); 64 containers active <1 yr; `sensor_active_windows.csv` exported; demand denominator = calendar days inside active window.
- Timestamps corrected: start/end on all 60,916 event rows (Rota only 22,674); two shifts 04–06 h and 14–15 h; median run 7.4 h.
- Run totals: km constant within run, weight NOT; median run records 1 container → weight allocation held.
- Glass gap: site-level policy tested (270 sites, 214 triple; 105 one-sensor, 118 two-plus, 30 none; paper+packaging = 342/344 sensors) — policy explains fractions, D1 governs counts.
- Route purity 91/92 (exception CE46; four "Óbidos CE*" codes flagged).
- N=452 (old regression): not reproducible from held data; rebuild recommended.
- D6 reclassified: registry risk closed; coverage difference expected; true fleet size awaits re-export.
- Six charts (F1–F6, matplotlib, reference palette); four maps rebuilt on `Layout template.qpt` — stats HTML box lower-left, tidy complete legends, CAOP provenance stated.

## Event-level comparison (Rev C, user items 1–7)
- Method: nearest valid sensor reading per driver row (127,928 rows on instrumented containers), ±3 h primary window (34% matched); sensitivity across 7 windows: acceptable share stable 48.9–50.9% → window-insensitive.
- Agreement: small 28.0%, moderate 17.1%, large 54.8%; **acceptable (≤25 = one driver step) 45.2%** — instruments non-interchangeable; sensor primary, driver ordinal covariate, instrument term required when mixing.
- Ceiling: driver=100 with sensor raw 82–84: 1,758/10,153 (17.3%) — ceiling ≠ sensor's 100; D3 open.
- Driver −1: 57.5% have valid sensor match with values spread across the range; none are event rows → missing entry, recode as missing.
- `event_level_dataset.parquet`: raw readings, timestamps, gap, s_max, normalized value, QC flags (NO_SENSOR_MATCH 62,309; EVENT_ZERO 36,790; LARGE_DISAGREEMENT 15,732 quarantined; GOOD 6,281; MODERATE 4,912; CEILING 1,758), selected_fill on 75,260 rows with rule text.
- Negatives: −1…−9 (47.3%) vs −89…−116 (52.7%, −116 alone 37,052); 329/344 containers affected; E BLUE BEE worst (23.6%); 29,885 episodes, 17.8% >24 h, max 1,226; level shift across episodes 28.5 vs 9.6 baseline → drop negatives, subtract >24 h episodes from active windows, never interpolate across episodes.

## Ops
QGIS crashed 4×: SCP plugin disabled AND real cause found — Python-GC'd `QgsLayerTree` passed to legend models (fix: pin refs in `builtins`). Labels in QGIS 3.44 need `setTextFormat`, not `setFont`. QGIS relaunched headless-style via `qgis-ltr-bin.exe`; port 9876 monitor pattern established.

## Pending
Operator data request (now incl. sensor unit, weighing point, −116 code, Óbidos circuits, D1 re-export); routable graph; regression-sample rebuild; R1-01 development (user review still to come — the reviewed file was R2-01, not R1-01).
