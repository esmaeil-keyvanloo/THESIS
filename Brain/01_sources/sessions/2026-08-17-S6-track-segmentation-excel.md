# Session digest S6 — 2026-08-17 (same chat)

## Track segmentation (user-flagged flaw: impossible trip lines)
- Verified: 6.6% of 49,662 consecutive stop segments implied >60 km/h (p99 = 467 km/h) — parallel vehicles logged under one identifier + sparse logging.
- `segment_tracks.py`: greedy track assignment; a stop joins a track only if reachable at ≤60 km/h implied speed (haversine ×1.3 detour, 2-min service). 1,137/3,430 identifiers split (935→2, 191→3, 9→4, 2 pathological); 0 violations after; 4,423 consistent vehicle tracks; re-routed on road graph (0 disconnected).
- Explorer v3 delivered and opened in default browser: tracks a/b/c per identifier, shared kg/km marked "whole identifier". Evidence of multiple simultaneous crews (matters for VRP fleet size).

## Trip-sorted Excel (user request)
- `W2/03_outputs/tables/Driver_Trips_Sorted.xlsx`: Sheet 1 = 120,554 rows in 11,577 chronological track blocks, white/light-gray banding, stops in service order, pre-readings (≤15 min before emptying, 59,638) attached to their visit; Sheet 2 = 144,263 readings with no trip link, time-ordered; Sheet 3 = READ ME. All 19 original columns unchanged after 4 helper columns. Sensors untouched by request.
- Clarified for user: rows are readings, not drivers; only emptying records carry the trip id.

## Repo hygiene
- GIS_DATA excluded from git except README.md (all re-downloadable; user also self-downloaded ~20 GB of 50 cm LiDAR into 04_elevation). trips_routed*.json ignored (regenerable). Committed and pushed.
