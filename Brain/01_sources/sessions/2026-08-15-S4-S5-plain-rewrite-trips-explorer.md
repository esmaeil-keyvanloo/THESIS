# Session digest S4+S5 — 2026-08-15 (same chat as S2/S3)

## S4 — plain-language rewrite + first trips webGIS
- R2-01 rewritten in plain language after user feedback (tone too hard); one-paragraph "what the data says" story added; active windows explained simply (a container's own first-to-last-reading span).
- Record-count asymmetry explained: sensors report ~2.5×/day continuously, drivers only record during visits — row counts are not comparable effort.
- First Trip Explorer built (calendar of trip days, multi-select trips on Leaflet map).

## S5 — 9-question analytics round (workflow: 4 parallel agents)
- Fraction days: trips fraction-pure; packaging + paper same days (818/1,200 both), Mon–Sat, no glass circuits.
- Two-bin long trips = full shifts with partial logging (7.4 h/122 km ≈ 15+-bin trips).
- Road routing v1: 3,430 trips on drivable OSM graph (dijkstra), 0 disconnected.
- Depot = Estaleiro Municipal (39.3392, −8.9249); disposal = Valorsul transfer station + Ecocentro (Zona Industrial SE). Morning trips start in town, afternoon in south parishes.
- Bin categories: 233 high / 315 moderate / 221 low / 47 no-data (rule in bin_analytics.json).
- Unnecessary emptyings (≤50% full): 25.4% overall, 41.9% (2020) → 8.1% (2024).
- Temporal tables daily→annual + F10–F12; annual 2020: 2,821 trips/7,194 t/362k km → 2023: 1,573/4,414 t/210k km; kg/km stable 19–21.
- NEW defect: sensor scale discontinuity Nov 2020 (medians ~100% of ceiling before, 33–46% after).
- Explorer v2: road routes, numbered stops, fraction colours, facilities, bin-category layer, monthly-kg strip.
