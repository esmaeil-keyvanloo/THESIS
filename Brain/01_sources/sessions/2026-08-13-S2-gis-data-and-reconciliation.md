# Session digest S2 — 2026-08-13

## Scope
Free spatial data acquisition for Rio Maior; QGIS library build; inspection of existing GIS assets; driver-vs-sensor CSV reconciliation; two reports.

## Done
1. **GIS_DATA/ built (6 GB, 9 folders)** — deep research (DGT, INE, APA, LNEG, E-REDES) then downloads: CAOP 2025, BGRI 2021/2011 (mun. 1414), INE 1 km grid, WorldPop/GHS-POP, COS 2018+2025 (via DGT OGC API, bbox-paged), CRUS PDM zoning (WFS), MDT 10 m 2024 LiDAR DTM (+hillshade, slope), Copernicus 30 m, APA rivers + flood zones, fire hazard, LNEG faults/lithology, E-REDES (230 transformers, 12,189 LV poles), SRUP layers incl. electric-grid lines, OSM Geofabrik clipped ×20. Everything clipped to study area +10 km, EPSG:3763. Sources/licences: `GIS_DATA/README.md`.
2. **QGIS**: 52 styled layers, tree = MY DATA (containers/W2/study/legacy) + DOWNLOADED (9 thematic). Print layouts W2-M1…M4, each with bottom-right HTML stat box; exported 150 dpi.
3. **R1-02 GIS Data Inventory** (W1/04_outputs/reports) — held vs downloaded vs must-request; relevance per pipeline stage; gdb findings (sensor layer's route fields empty; gdb border ≠ CAOP; census layer 222/572).
4. **W2 reconciliation** (`W2/01_scripts/reconcile_csv.py`, stats JSON, `containers_reconciled.geojson`): 344 sensor ⊂ 816 driver, 0 mismatches, 0.0 m offset; all inside municipality; glass 258→2; fill semantics (driver quartiles 54.7% zeros; sensor 82–84 ceiling, 9.2% negatives); routes CE/CP = fraction; weights are route-run totals. **R2-01** delivered (12-part standard).
5. **Ops**: QGIS crash root cause = Python-GC'd legend tree (fixed by pinning refs); SCP plugin disabled; QGIS babysitting monitor set up.

## Decisions / policies
- Clip mask = study area +10 km buffer (user choice).
- W2 folder for this round; reports numbered R<round>-<n>.
- Credentials: Claude never handles passwords — CDD LiDAR download is user-run; deferred.
- Routes/schedules/shifts/water networks: not public; request from Valorsul + Câmara (LADA fallback).

## Pending
R1-01 feedback (user reviewing, will send in this chat); request letters; routable graph; D7/BGRI rebuild when DB ready.
