# Session digest S19 — 2026-08-24 (W5 thesis-grade rebuild; same chat)

## What ran (10 agents, 4 waves + orchestrator integration wave)

- **T0+T1 road-speed engine & calibration (A)**: OSM drivable graph (236k nodes) with per-road-type truck-legal speeds (motorway 90 / trunk–primary–secondary 80 / tertiary 70 / links 50–60 / default 50) and car-ceiling weights; full 272-site travel matrix (`site_travel.parquet`: legal_min, ceiling_min, km — zero unreachable). Calibration on 13,386 trusted stamped gaps: service_med 0.02 min (66% of stamps are ≤5 s batch entries), slack p05 = +2.53 min → **tolerance 0**. Lesson: the 13-min-hop false exclusions were caused by the flat-60 model, not by tight tolerances.
- **T2 audit (B) → rebuild (D)**: 12-bullet doubt list (exact duplicates 868; in-trip repeat stamps 1,270; 118 impossible same-minute bursts; 113 admin-split tour pairs; zero-duration trips; 3,135-km odometer entry; 320 copy-paste kg combos; 02–04 h stamps; registry — not GPS — coordinates; no usable fill in driver stream; 7 material-mixed identifiers). Rebuild v7 from scratch on engine physics: 11,691 trips + 1,674 phantoms; tier accounting closes exactly on 264,817 rows (S 60,477 / pre 59,638 / I 120,813 / L 7,807 / P 10,136 / iso 1,262 / evicted 2,981 / dup 1,703); full-chain mutual-feasibility validation residual 0 (the #1068 class of contradictions is gone); 133 continuation pairs annotated, never merged; 87 flagged tracks (90 above-legal junctions, dotted).
- **T3 audit (C) → clean (E)**: 12-bullet list (negatives 96,832 across 329 bins; 11,862 frozen runs, worst 306 days at 82; 218 spikes; cadence doubling Jun-2023; ceilings stable 82–84 across eras; 640 silent gaps >7 d). Cleaned readings 791,207 kept / 257,368 removed with reasons. Drops v2 47,543. **Orchestrator post-pass: rebound rule** (fill +20 within 6 h after a drop ⇒ suspect false emptying) demoted 21,055 drops (44.3%) to low confidence → high 14,864 / med 6,447 / low 26,232.
- **T4 fusion (F)**: 10-element stops with src tag; 9,515 D+S corroborated stamped stops (±90 min); 38,419 sensor-only recovered emptyings attached to 6,638 trips (diamonds, confidence-graded); per-trip evidence_mix; per-year cross table (sensor-only ≈ 4,541 t of never-logged work — now stated with confidence tiers).
- **T5 circuits (G)**: 151 standing circuits (Jaccard 0.5 per material; 1,103 member trips). **Headline: standing circuits dissolve — per-year coverage 54.6% (2020) → 27.0 → 28.6 → 19.9 → 0.0% (2024)**; 2020 fixed-weekday mega-rounds (71–85 core sites, Tue/Thu) die by Feb-2021; compact ~8-site cores persist to mid-2023; in 2024, at peak sensor cadence, no site set recurs ≥3× — collection has become fill-driven and ad-hoc. Glass never repeats a site set. Drivers repeat WHERE (cohesion 0.69) far more than the ORDER (0.67, mega-rounds ~0.72).
- **T7 routes (H)**: 3 m simplify tolerance (12.86 MB), 9,908 routes, 0 unroutable, verified per-stop playback anchors, depot/TS legs, flag sub-paths.
- **T6 workbooks (I) + source-of-truth (J)**: three reconciled Excels in `W5/03_outputs/tables/` (Driver / Sensor / Combined; clean + dropped-with-reason + METHOD sheets; openpyxl-verified headers and totals) and **`Brain/03_db/parquet/master_events_w5.parquet`** (307,676 events — frozen twin of the Combined Events sheet). `info_stats.json` + standalone `methodology.html` (anchored sections matching the explorer's read-more links).

## Explorer W5 (orchestrator wave; `W5/03_outputs/explorer/`, local port 8767)

- **Hybrid-neumorphic UI** (soft chrome / flat data layer) + separate **editorial.html** sample skin (paper, hairlines, serif; switch link in ⓘ footer) — both from one template (`explorer_w5_template.html`, `__SKIN__` token).
- **3-way source views** Driver / Sensor / Combined (?view= deep link): sensor view turns the calendar into a drop-event heat map with diamond markers and per-event chips; driver view hides all sensor artefacts.
- Per-stop **D / D+S tags**, diamond sensor-only markers, evidence bars on chips and cards, teal evidence strips on calendar days, continuation cross-reference (⧉ likely continues #id).
- **Trip playback (T9)**: timestamp-driven truck marker along the real route (anchor interpolation), live clock, speed readout vs per-leg legal average (red above legal), pause/scrub/×5–×180.
- **Responsive everywhere**: fluid ≥1180 px, narrowed panels to 920 px, drawer layout with FABs below 920 px, phone-tuned down to 360 px; coarse-pointer hit targets.
- **E2E green**: Playwright matrix — 6 viewports (2560×1400 → 360×700) × ~25 assertions incl. road-following geometry (pts > stops×3), playback clock/scrub, view switching, info tabs, drawers, deep links; zero console errors (`e2e_check_w5.py`).

## Decisions / rules added
- Rebound-demotion rule for sensor drops (documented in sensor_stats.json + assumptions register).
- Continuation pairs: annotate (`continues_from`), never merge (operator semantics unknown).
- W5 explorer is the deployed one (root redirect updated). Vercel Root Directory must be switched by the user to `W5/03_outputs/explorer`.

## Next (critical path unchanged)
Demand model on `master_events_w5.parquet` (drops as service events, active windows as denominators) → real p-median instance. Parked: operator data-request letters; D7/BGRI rebuild (memory reminder standing).
