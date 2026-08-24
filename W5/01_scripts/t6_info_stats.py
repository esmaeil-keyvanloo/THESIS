# TASK J (T6 info) - build W5/02_data_work/info_stats.json, the single source of
# truth for the explorer's info tabs (schema matches explorer_w5_template.html IT.*).
# Inputs : rebuild_stats.json, calibration.json, sensor_stats.json,
#          sensor_anomaly_report.json, trip_anomaly_report.json, circuits.json,
#          _cross_tmp.json (per-year driver-vs-sensor + cadence, from compute_cross),
#          sensor_drops_v2.parquet + raw_collections.parquet (recovered tonnage).
import json, math
from datetime import datetime

import duckdb

ROOT = r"C:/Users/esmae/Desktop/phd Esmaeil/THESIS CLAUDE"
W5 = f"{ROOT}/W5/02_data_work"
RAWC = f"{ROOT}/Brain/03_db/parquet/raw_collections.parquet"

J = lambda p: json.load(open(p, encoding="utf-8"))
rb = J(f"{W5}/rebuild_stats.json")
cal = J(f"{W5}/calibration.json")
ss = J(f"{W5}/sensor_stats.json")
sa = J(f"{W5}/sensor_anomaly_report.json")
ta = J(f"{W5}/trip_anomaly_report.json")
ci = J(f"{W5}/circuits.json")
cx = J(f"{W5}/_cross_tmp.json")

# ---------- recovered tonnage: s_only drops x bin volume x pct_before x mid density
con = duckdb.connect()
VOL = {r[0]: (int(r[1] or 2500), r[2]) for r in con.sql(f"""
  SELECT trim(idcontentor) cid,
         MAX(TRY_CAST("Volume do tipo de contentor" AS INT)) vol,
         ANY_VALUE(CASE WHEN description LIKE '%Vidro%' THEN 'G'
                        WHEN description LIKE '%papel%' THEN 'C' ELSE 'P' END) fl
  FROM '{RAWC}' GROUP BY 1""").fetchall()}
DENS_MID = {"P": 32, "C": 75, "G": 300}
dr = con.sql(f"SELECT cid, t_before, t_after, pct_before FROM '{W5}/sensor_drops_v2.parquet'").df()

# rebuild the stamped-stop match exactly as compute_cross did (stamp epoch lists)
import bisect
from collections import defaultdict
from datetime import timedelta
world = J(f"{W5}/trips_v7_enriched.json")
stamp_by_cid = defaultdict(list)
for t in world:
    if t.get("frac") == "Phantom":
        continue
    d0 = datetime.strptime(t["date"], "%Y-%m-%d")
    prev, off = None, timedelta(0)
    for s in t["stops"]:
        cur = d0 + off + timedelta(hours=int(s[3][:2]), minutes=int(s[3][3:]))
        if prev is not None:
            while cur < prev - timedelta(hours=12):
                cur += timedelta(days=1); off += timedelta(days=1)
        prev = cur if prev is None else max(prev, cur)
        if s[4] == "S":
            stamp_by_cid[str(s[2])].append(cur.timestamp())
for v in stamp_by_cid.values():
    v.sort()
W90 = 90 * 60
rec_kg = 0.0; n_rec = 0
for r in dr.itertuples():
    arr = stamp_by_cid.get(str(r.cid))
    tb = r.t_before.timestamp() - W90; ta_ = r.t_after.timestamp() + W90
    hit = False
    if arr:
        i = bisect.bisect_left(arr, tb)
        hit = i < len(arr) and arr[i] <= ta_
    if not hit:
        vol, fl = VOL.get(str(r.cid), (2500, "P"))
        pct = r.pct_before if r.pct_before == r.pct_before else 75.0
        rec_kg += vol / 1000 * pct / 100 * DENS_MID[fl]
        n_rec += 1
rec_t = round(rec_kg / 1000)
print("s_only drops", n_rec, "est recovered t", rec_t)

# ---------- assemble ----------
fmt_i = lambda x: f"{x:,}"
py = cx["per_year"]; ct = cx["totals"]
d_only_all = sum(v["d_only_all"] for v in py.values())
d_only_instr = sum(v["d_only_instrumented"] for v in py.values())
sy = ss["per_year"]
rm_tot = lambda y: sum(sy[y]["readings_removed_by_reason"].values())
el = ci["meta"]["eligibility"]

info = {
  "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
  "task": "W5 T6 info (Task J) - source of truth for explorer info tabs + methodology page",
  "period": "January 2020 - April 2024",

  "totals": {
    "driver_rows": 264817, "sensor_rows": 1048575,
    "tracks": rb["tracks"], "phantom_tracks": rb["phantoms"]["tracks"],
    "identifiers": rb["identifiers"],
    "bins": 816, "instrumented_bins": 344,
    "kg_total_once_per_identifier": rb["kg_total_once_per_identifier"],
    "tonnes_total": round(rb["kg_total_once_per_identifier"] / 1000),
    "km_recorded_once_per_identifier": rb["km_rec_total_once_per_identifier"],
    "materials_tracks": {"Packaging": 6019, "Paper/card": 5093, "Glass": 579},
    "sensor_readings_kept": ss["kept_rows"], "sensor_readings_removed": ss["removed_rows"],
    "sensor_emptyings_detected": ss["drops_v2"]["kept"],
    "sensor_only_recovered": ct["s_only"], "recovered_est_tonnes": rec_t,
  },

  "tiers": [
    ["S", 60477, "Stamped emptying record - the driver pressed the button at the bin. The only rows counted as collections."],
    ["pre", 59638, "Pre-emptying fill reading logged moments before an S row; attached to its stop as the bin's fill before emptying."],
    ["I", 120813, "Inferred pass-by - unstamped reading placed on the one track that could feasibly produce it (p >= 0.7). An observation, not a collection."],
    ["L", 7807, "Low-confidence placement (p < 0.7) - more than one track fits; drawn with a ? mark."],
    ["P", 10136, "Phantom stop - reading no logged truck could reach, chained with others into 1,674 reconstructed vehicle tracks (dotted)."],
    ["isolated", 1262, "Unreachable readings too few to chain (fewer than 3 stops) - kept as isolated observations."],
    ["evicted", 2981, "Placements evicted when a better-fitting reading claimed the same gap; listed in the workbook with reason."],
    ["duplicates", 1703, "Exact duplicate rows removed (439 stamped + 1,264 unstamped) - same bin, same timestamp."],
  ],
  "tiers_note": "8 rows account for all 264,817 driver-file rows: 60,477 + 59,638 + 120,813 + 7,807 + 10,136 + 1,262 + 2,981 + 1,703 = 264,817.",

  "trips_story": ("Drivers log an emptying by pressing a button at the bin, and rows sharing one identifier "
    "(idrecolha) were long treated as one trip. Tested against truck-legal road times, many cannot be: "
    "660 identifiers mix several vehicles, 101 were typed in at day end as a batch, and 16 splits proved "
    "to be a single vehicle after all. Every consecutive stamp pair in the rebuilt 11,691 tracks is now "
    "physically drivable; 90 junctions stand only under physical ceiling speeds and stay flagged (dotted). "
    "The 142,999 unstamped fill readings were then offered to these tracks: 120,813 fit exactly one "
    "feasible track (I), 7,807 stay ambiguous (L, drawn with ?), and 11,398 that no logged truck could "
    "reach were chained into 1,674 reconstructed phantom vehicles plus 1,262 isolated observations."),
  "trip_steps": [
    ["Raw driver rows", 264817],
    ["Stamped emptying records (raw)", 60916],
    ["- exact duplicates removed", 439],
    ["Stamped stops in tracks (S)", 60477],
    ["Collection identifiers (idrecolha)", 9984],
    ["Vehicle tracks after split / merge", 11691],
    ["- identifiers split (several vehicles)", 660],
    ["- split tracks re-merged (one vehicle)", 16],
    ["- batch-entry tracks (typed at day end)", 101],
    ["- ceiling-only junctions (kept, dotted)", 90],
    ["- continuation pairs (same crew, next run)", 133],
    ["Unstamped readings assessed", 142999],
    ["- inferred onto one feasible track (I)", 120813],
    ["- ambiguous, kept with ? (L)", 7807],
    ["- evicted in conflict resolution", 2981],
    ["Phantom tracks reconstructed", 1674],
    ["- stops absorbed by phantoms", 10136],
    ["- isolated observations left", 1262],
  ],
  "reading_note": ("S = stamped emptying (a collection). pre = fill noted just before it. I = reading inferred "
    "onto the only feasible track - an observation of the bin, never a collection. L = low-confidence (?), "
    "P = phantom-vehicle stop (dotted). Weighbridge kg and recorded km belong to the whole identifier and "
    "are counted once, even when it splits into several tracks."),

  "sensor_years": [
    [y, sy[y]["sensors_active"], sy[y]["sensors_added"], sy[y]["sensors_silent"],
     sy[y]["readings_kept"], rm_tot(y), sy[y]["drops_count"]]
    for y in ["2020", "2021", "2022", "2023", "2024"]
  ],
  "sensor_note": ("344 of the 816 bins carry a fill sensor (glass almost none: 2 units). Raw units are "
    "unverified and the scale changed in November 2020, so fill is always shown as % of the bin's own era "
    "ceiling (median 82). Hardware improved sharply: error codes fell from 36.6% of 2020 readings to 2.6% "
    "in 2024, and a typical bin now reports ~1.4 times per day (0.5 in 2020). 'Emptying events' are clean "
    "falls of >= 25 points within 24 h."),

  "cross_years": [
    [y, py[y]["d_only_instrumented"], py[y]["ds"], py[y]["s_only"]]
    for y in ["2020", "2021", "2022", "2023", "2024"]
  ],
  "cross_note": (f"Counted on bins whose sensor reported that year. Driver-only = stamped emptyings no sensor "
    f"confirmed (faults and low cadence explain most). Both = a detected sensor emptying within 90 minutes of "
    f"the stamp. Sensor-only = clean detected emptyings with no stamp within 90 minutes - work done but never "
    f"logged: {fmt_i(ct['s_only'])} events, roughly {fmt_i(rec_t)} t. The logbook also holds "
    f"{fmt_i(d_only_all - d_only_instr)} stamped emptyings at bins with no live sensor that year."),

  "assumptions": [
    ["Road-type legal speeds", "90/80/80/80/70; links 50-60; other 50 km/h",
     "Feasibility clock = fastest a loaded truck may legally drive each OSM road class (motorway/trunk/primary/secondary/tertiary); no flat network speed."],
    ["Ceiling speeds (merge policy only)", "130/100/100/90/80; other 60 km/h",
     "Physical upper bounds used only to judge split junctions: infeasible even at ceiling = different vehicles; legal-infeasible but ceiling-feasible = merged with a visible flag (90 junctions, dotted)."],
    ["Service time at a stop", "0.02 min median (p75 0.29)",
     "Calibrated from 12,587 consecutive stamp pairs inside 8,837 clean trips - stamps arrive in bursts, so almost no time passes between consecutive stamps."],
    ["Feasibility tolerance", "0 min",
     "The 5th percentile of slack on trusted links is +2.5 min, so no extra allowance is needed (tol = ceil(max(0, -p05 slack)) = 0)."],
    ["Inference cutoff", "p >= 0.7",
     "A loose reading becomes an I stop only when the best track beats the runner-up at least 70/30 on legal-time detour cost; otherwise it stays L with a ? mark."],
    ["Batch-entry rule", "gap <= 1 min & jump > 2 km",
     "Consecutive stamps seconds apart but kilometres apart = data typed in at day end, not a live route; 101 tracks marked and excluded from circuit mining."],
    ["Phantom rule", ">= 3 chained stops",
     "Readings unreachable by any logged truck are reconstructed into a phantom vehicle only when at least 3 chain feasibly; fewer stay isolated observations."],
    ["Sensor error codes", "fill < -10 removed (50,620)",
     "Hard error codes (-116, -3, -1, ...), never fill levels; kept as QC metadata, shown faded."],
    ["Transient negatives", "-10 to -1 removed (46,212)", "Brief electronic glitches around zero."],
    ["Stuck filter", ">= 6 identical values over > 48 h (160,280 removed)",
     "A frozen sensor repeats one number for weeks (longest: 305 days at '82'); the first reading is kept, repeats dropped."],
    ["Spike filter", "rise >= +40 units in <= 30 min (218 removed)", "No bin fills 40 points in half an hour; physically implausible."],
    ["Emptying (drop) detection", "fall >= 25 units within <= 24 h",
     "Smallest fall clearly separated from noise; confidence: <= 6 h high, <= 12 h medium, else low; windows touching a removed reading are excluded (3,357)."],
    ["Rebound demotion", "rise >= 20 within 6 h after a drop -> low",
     "A quick refill right after an apparent emptying suggests a sensor dip, not a truck (21,055 demoted)."],
    ["Era ceilings", "E1 <= Oct 2020 | E2 Nov 2020-Dec 2022 | E3 2023+",
     "The scale changed in Nov 2020 and cadence doubled in 2023; fill is expressed as % of the bin's own era maximum (median 82, max 84) because raw units are unverified."],
    ["Density bands", "P 25-40 | C 50-100 | G 250-350 kg/m3",
     "Literature ranges for loose collected packaging/paper/glass; mid values 32/75/300 give single estimates, the band gives the range."],
    ["Sensor display window", "+/- 3 h", "A stop shows the nearest clean sensor reading within 3 hours; a negative error code is shown raw and faded."],
    ["Corroboration window (D+S)", "+/- 90 min", "A stamped stop counts as sensor-confirmed when a detected emptying overlaps it by at most 90 minutes."],
    ["Sensor-event radius", "300 m", "A sensor-only emptying is drawn on a trip (diamond) only if its bin lies within 300 m of that day's route."],
    ["Circuit threshold", "Jaccard >= 0.5, >= 3 occurrences",
     "Coverage/cohesion elbow (34.9% / 0.685); reads as 'majority of sites shared with the founding trip'; batch and flagged tracks excluded."],
    ["kg / km accounting", "once per identifier",
     "Weighbridge kg and recorded km describe the whole identifier; when it splits into tracks, totals are shown per track but summed once."],
  ],

  "sources": [
    ["DATA/XLS/Enchimentos_com_Recolhas[RioMaior].csv", "Driver logbook - 264,817 rows, 816 bins (frozen; mirrored as Brain/03_db/parquet/raw_collections.parquet)"],
    ["DATA/XLS/Enchimentos_de_Sensores[RioMaior].csv", "Sensor file - 1,048,575 readings, 344 bins (frozen; mirrored as raw_sensors.parquet)"],
    ["GIS_DATA/01_osm/riomaior_10km/osm_roads_riomaior10km.gpkg", "OSM road network (EPSG:3763) behind all travel times; footpaths banned"],
    ["W5/02_data_work/site_travel.parquet + calibration.json", "272-site truck-legal + ceiling road-time matrix; calibrated service time and tolerance (T0/T1)"],
    ["W5/02_data_work/trips_v7.json + phantom_tracks_v7.json + rebuild_stats.json", "Track rebuild: splits, merges, batch flags, I/L assignment, phantoms (T2)"],
    ["W5/02_data_work/assignments_v7.parquet + dropped_v7.parquet", "Row-by-row fate of every unstamped reading, with reasons (T2)"],
    ["W5/02_data_work/sensor_clean.parquet + sensor_removed.parquet + sensor_stats.json", "Sensor cleaning: kept vs removed readings by rule (Task E)"],
    ["W5/02_data_work/sensor_drops_v2.parquet", "47,543 detected emptying events with confidence and rebound flag (Task E)"],
    ["W5/02_data_work/trip_anomaly_report.json + sensor_anomaly_report.json", "Anomaly audits: duplicates, same-minute bursts, stuck runs, negative codes (T3)"],
    ["W5/02_data_work/trips_v7_enriched.json + trips_index_v7.json", "Fusion: fills, sensor columns, D/DS source tags, sensor-only events, weight bands (T4)"],
    ["W5/02_data_work/circuits.json + circuit_membership.json", "151 standing circuits and their member trips (T5)"],
    ["W5/02_data_work/trips_routed_v7.json + depot_legs_v7.json", "Road-following route geometry and depot/disposal legs (T7; 0 unroutable)"],
    ["W4/02_data_work/trips_v5_base.json", "Reference: the 9,984 stamped identifiers carried into W5"],
    ["W5/02_data_work/info_stats.json", "This file - source of truth for every number on this page"],
  ],
  "sources_note": ("DATA/ is frozen and never edited. Every number above regenerates from these files via the "
    "scripts in W5/01_scripts/; dropped rows sit in the companion workbooks with their reason."),

  "tier_detail": {
    "S": 60477, "pre": 59638, "I": 120813, "L": 7807,
    "P_stops": 10136, "phantom_tracks": 1674, "isolated": 1262,
    "evicted": 2981, "duplicates_stamped": 439, "duplicates_loose": 1264,
    "assignment_status_counts": rb["assignment_status_counts"],
    "sum_check": 264817,
  },
  "trip_step_detail": {
    "track_verdicts": rb["track_verdicts"],
    "split_identifiers": rb["split_identifiers"],
    "merged_single_tracks": rb["merged_single_tracks"],
    "speed_flagged_junctions": rb["speed_flagged_junctions"],
    "continuations": rb["continuations"],
    "duplicates": {"stamped_exact": 439, "loose_exact": 1264,
                   "same_bin_repeat_pairs": ta["same_bin_repeat_in_identifier"]["bin_identifier_pairs"],
                   "same_minute_far_bursts": ta["same_minute_far_apart_bursts"]["bursts"]},
  },
  "sensor_detail": {
    "per_year": {y: {
        "active": sy[y]["sensors_active"], "added": sy[y]["sensors_added"],
        "silent": sy[y]["sensors_silent"], "kept": sy[y]["readings_kept"],
        "removed_by_reason": sy[y]["readings_removed_by_reason"], "removed_total": rm_tot(y),
        "drops": sy[y]["drops_count"], "drops_by_confidence": sy[y]["drops_by_confidence"],
        "cadence_mean_per_bin_day": py[y]["cadence"]["readings_per_bin_day_mean"],
        "cadence_median_bin_per_day": py[y]["cadence"]["readings_per_bin_day_median_bin"],
      } for y in sy},
    "removed_by_reason_total": ss["removed_by_reason"],
    "drops": {"detected": ss["drops_v2"]["detected"],
              "excluded_touching_removed": ss["drops_v2"]["excluded_touching_removed"],
              "kept": ss["drops_v2"]["kept"],
              "confidence_initial": ss["drops_v2"]["by_confidence"],
              "confidence_final_after_rebound": ss["drops_by_confidence"],
              "rebound_demoted": ss["drops_rebound_demoted"]},
    "era_table": ss["era_table"],
    "negatives": {"total": sa["negatives"]["total"], "share_pct": sa["negatives"]["share_pct"],
                  "share_2020_pct": 36.6, "share_2024_pct": 2.6,
                  "top_codes": sa["negatives"]["top_codes"]},
  },
  "cross_detail": {
    "per_year": py,
    "totals": {"stamped_stops": ct["stamped_stops"], "ds": ct["ds"],
               "d_only_all": d_only_all, "d_only_instrumented": d_only_instr,
               "d_only_uninstrumented": d_only_all - d_only_instr,
               "s_only_unique_drops": ct["s_only"],
               "s_only_placements_on_tracks": 38419, "tracks_with_s_only": 6638,
               "recovered_est_tonnes": rec_t},
    "method": "match = detected drop window overlaps the stamp by <= 90 min (same bin); instrumented = bin had >= 1 clean reading that calendar year",
  },
  "circuits_summary": {
    "n_circuits": ci["meta"]["n_circuits"], "member_trips": ci["meta"]["member_trips"],
    "eligible_trips": el["eligible_trips"], "total_tracks": el["total_trips_v7"],
    "excluded": el["excluded"],
    "coverage_ge3_pct": ci["meta"]["coverage_ge3_pct"],
    "coverage_by_year_pct": ci["meta"]["coverage_by_year_main_run_pct"],
    "median_cohesion": 0.685, "largest_occurrences": 89,
    "threshold": 0.5, "min_occurrences": 3,
    "justification": ci["meta"]["justification"],
  },
  "params": {"rebuild": rb["params"], "calibration": {
      "service_med_min": cal["service_med_min"], "service_p75_min": cal["service_p75_min"],
      "tol_min": cal["tol_min"], "n_links_used": cal["n_links_used"],
      "n_trusted_trips": cal["n_trusted_trips"], "slack_p05": cal["slack_quantiles"]["p05"],
      "sites": 272, "graph_nodes": cal["graph"]["nodes_main_component"],
      "snap_m_median": cal["graph"]["snap_m_median"]}},
}

open(f"{W5}/info_stats.json", "w", encoding="utf-8").write(
    json.dumps(info, ensure_ascii=False, indent=1))
print("info_stats.json written,", round(len(json.dumps(info)) / 1024, 1), "KB")

# tidy the temp cross file
import os
os.remove(f"{W5}/_cross_tmp.json")
print("temp removed")
