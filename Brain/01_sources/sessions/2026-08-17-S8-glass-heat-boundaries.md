# Session digest S8 — 2026-08-17 (same chat)

## Glass correction (user caught it)
- Earlier trips.json silently excluded ALL glass runs; the "glass has no trips" claim was an artifact. Raw: 556 glass identifiers, 281 multi-bin.
- Full v5 rebuild: base → segmentation (60 km/h) → loose-reading assignment → routing → depot/TS legs. 11,495 tracks: Packaging 6,147 / Paper 4,751 / Glass 597 (322 multi-bin). 8,242 routed, 0 fallbacks.

## Confirmed on the full set
- Material purity: 99.97% — one run = one material (7 mixed runs in 9,984, data noise). Operationally necessary (compactor vs crane truck).
- Glass rhythm: ~6 multi-bin runs/month, Wed–Fri, no dedicated days (93% coincide with other materials' days).
- km audit holds with glass: odometer ≈ 2.5× modeled route (all fractions alike) — fleet sweeps beyond logged stops.

## Important caveat
- Inferred stops (time+location assigned readings) are fraction-blind: only 13.7% match the trip's material — they're checks of co-located ecoponto bins seen from the truck's path. Valid as observations, INVALID as collection events. Excel labels them; analyses must not count them as emptyings.

## Deliverables
- Explorer v5: heat calendar (day fill = kg collected, global scale; month tonnes; tooltips), fraction strips per day, Glass button/green trips, CAOP boundary layer (muni + 10 freguesias). Heaviest day 2020-08-06 (58,020 kg).
- Excel glass-inclusive: 223,688 trip-block rows / 41,129 not assignable / 264,817 total accounted.
- New data: trips_v5*, reading_assignments_v5.parquet, boundaries.json (19 KB), daily_kg.json, stats_v5.json.
