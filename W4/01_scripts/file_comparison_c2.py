# C2 (T5) - Two-file comparison at bin-day level
# Inputs (read-only): W4/02_data_work/sensor_drops.parquet, W4/02_data_work/trips_v6.json,
#                     Brain/03_db/parquet/raw_sensors.parquet, raw_collections.parquet,
#                     W4/02_data_work/sensor_quality.json (A2 agreement table)
# Output: W4/02_data_work/file_comparison.json
import json
from collections import defaultdict

import duckdb
import numpy as np
import pandas as pd

ROOT = r"C:/Users/esmae/Desktop/phd Esmaeil/THESIS CLAUDE"
DROPS = f"{ROOT}/W4/02_data_work/sensor_drops.parquet"
TRIPS = f"{ROOT}/W4/02_data_work/trips_v6.json"
SENS = f"{ROOT}/Brain/03_db/parquet/raw_sensors.parquet"
COLL = f"{ROOT}/Brain/03_db/parquet/raw_collections.parquet"
QUAL = f"{ROOT}/W4/02_data_work/sensor_quality.json"
OUT = f"{ROOT}/W4/02_data_work/file_comparison.json"

DENS_MID = {"P": 32.0, "C": 75.0, "G": 300.0}  # kg/m3 (estimate_weights.py convention)

# ---------- bin volume + material (raw_collections) ----------
con = duckdb.connect()
bins = con.sql(f"""
  SELECT trim(idcontentor) cid,
         MAX(TRY_CAST("Volume do tipo de contentor" AS INT)) vol,
         ANY_VALUE(CASE WHEN description LIKE '%Vidro%' THEN 'G'
                        WHEN description LIKE '%papel%' THEN 'C' ELSE 'P' END) fl
  FROM '{COLL}' GROUP BY 1
""").df()
VOL = {str(r.cid): (int(r.vol) if pd.notna(r.vol) else 2500, r.fl) for r in bins.itertuples()}

# ---------- sensors: per-bin-day valid reading count + negative flag ----------
s = pd.read_parquet(SENS, columns=["idcontentor", "Data da leitura", "Enchimento"])
s.columns = ["cid", "ts", "fill"]
s["ts"] = pd.to_datetime(s["ts"], errors="coerce")
s["fill"] = pd.to_numeric(s["fill"], errors="coerce")
s = s.dropna(subset=["ts", "fill"])
s["cid"] = s["cid"].astype(str)
s["day"] = s["ts"].dt.date
s["valid"] = (s["fill"] >= 0) & (s["fill"] <= 100)
s["neg"] = s["fill"] < 0

day_valid = s[s["valid"]].groupby(["cid", "day"]).size()          # valid readings per bin-day
neg_days = set(s.loc[s["neg"], ["cid", "day"]].itertuples(index=False, name=None))
instrumented = set(s.loc[s["valid"], "cid"].unique())
cov = s[s["valid"]].groupby("cid")["day"].agg(["min", "max"])      # sensor coverage per bin
valid_count = dict(day_valid)

# ---------- drops: sensor evidence days ----------
d = pd.read_parquet(DROPS)
d["cid"] = d["cid"].astype(str)
d["d0"] = d["ts_before"].dt.date
d["d1"] = d["ts_after"].dt.date

sensor_days = defaultdict(list)  # (cid, day) -> list of drop row idx
for i, cid, d0, d1 in d[["cid", "d0", "d1"]].itertuples(name=None):
    sensor_days[(cid, d0)].append(i)
    if d1 != d0:
        sensor_days[(cid, d1)].append(i)

# ---------- trips v6: driver S-days + any-visit days ----------
trips = json.load(open(TRIPS, encoding="utf-8"))
driver_days = set()   # (cid, day) with stamped 'S' stop
visit_days = set()    # (cid, day) with ANY stop (S/I/L)
for t in trips:
    day = pd.Timestamp(t["date"]).date()
    for st in t["stops"]:
        cid, typ = str(st[2]), st[4]
        visit_days.add((cid, day))
        if typ == "S":
            driver_days.add((cid, day))

# ---------- bin-day confusion matrix over each bin's sensor coverage ----------
matrix = {"both": 0, "driver_only": 0, "sensor_only": 0, "neither_with_activity": 0}
per_year = defaultdict(lambda: {"both": 0, "driver_only": 0, "sensor_only": 0,
                                "neither_with_activity": 0})
sensor_only_class = {"logging_gap_track_visited": 0, "off_log_or_phantom": 0}
driver_only_class = {"sensor_negative_episode": 0, "low_cadence_lt2_readings": 0,
                     "no_drop_possible_false_stamp": 0}
recovered_event_idx = set()

for cid in instrumented:
    lo, hi = cov.loc[cid, "min"], cov.loc[cid, "max"]
    for day in pd.date_range(lo, hi, freq="D").date:
        key = (cid, day)
        drv = key in driver_days
        sen = key in sensor_days
        y = day.year
        if drv and sen:
            matrix["both"] += 1; per_year[y]["both"] += 1
        elif drv:
            matrix["driver_only"] += 1; per_year[y]["driver_only"] += 1
            if key in neg_days:
                driver_only_class["sensor_negative_episode"] += 1
            elif valid_count.get(key, 0) < 2:
                driver_only_class["low_cadence_lt2_readings"] += 1
            else:
                driver_only_class["no_drop_possible_false_stamp"] += 1
        elif sen:
            matrix["sensor_only"] += 1; per_year[y]["sensor_only"] += 1
            if key in visit_days:
                sensor_only_class["logging_gap_track_visited"] += 1
            else:
                sensor_only_class["off_log_or_phantom"] += 1
            recovered_event_idx.update(sensor_days[key])
        elif valid_count.get(key, 0) > 0:
            matrix["neither_with_activity"] += 1
            per_year[y]["neither_with_activity"] += 1

# ---------- recovered emptyings: drop events never matched by a driver S-day ----------
# an event is 'matched' if ANY day its window touches has a stamped stop for that bin
matched_idx = set()
for i, cid, d0, d1 in d[["cid", "d0", "d1"]].itertuples(name=None):
    if (cid, d0) in driver_days or (cid, d1) in driver_days:
        matched_idx.add(i)
rec = d.loc[~d.index.isin(matched_idx)].copy()

def est_kg(row):
    vol_l, fl = VOL.get(row.cid, (2500, "P"))
    return (vol_l / 1000.0) * (row.drop_units / 100.0) * DENS_MID[fl]

rec["kg"] = [est_kg(r) for r in rec.itertuples()]
rec["year"] = rec["ts_after"].dt.year
rec_year = {int(y): {"events": int(len(g)), "tonnes": round(g["kg"].sum() / 1000.0, 1)}
            for y, g in rec.groupby("year")}
rec_visited = rec.apply(lambda r: (r["cid"], r["d1"]) in visit_days
                        or (r["cid"], r["d0"]) in visit_days, axis=1)

qual = json.load(open(QUAL, encoding="utf-8"))

n_both, n_do, n_so = matrix["both"], matrix["driver_only"], matrix["sensor_only"]
n_rec = int(len(rec))
rec_t = round(rec["kg"].sum() / 1000.0, 1)
pct_so_visited = round(100 * sensor_only_class["logging_gap_track_visited"] /
                       max(n_so, 1), 1)
pct_do_sensorfault = round(100 * (driver_only_class["sensor_negative_episode"] +
                                  driver_only_class["low_cadence_lt2_readings"]) /
                           max(n_do, 1), 1)

findings = [
    f"On instrumented bins the two files agree on only {n_both:,} bin-days (both a stamped stop and a "
    f"sensor drop); the driver file alone claims {n_do:,} more emptying days and the sensor alone shows "
    f"{n_so:,} more - neither record is a superset of the other.",
    f"Of the {n_so:,} sensor-only days, {sensor_only_class['logging_gap_track_visited']:,} "
    f"({pct_so_visited}%) fall on days when a v6 track did visit the bin without stamping it "
    f"(logging gap); the remaining {sensor_only_class['off_log_or_phantom']:,} have no recorded visit at "
    f"all - off-log services or non-collection disturbances.",
    f"Of the {n_do:,} driver-only days, {pct_do_sensorfault}% are explained by the sensor itself - a "
    f"negative-code episode ({driver_only_class['sensor_negative_episode']:,}) or fewer than two valid "
    f"readings that day ({driver_only_class['low_cadence_lt2_readings']:,}); only "
    f"{driver_only_class['no_drop_possible_false_stamp']:,} days show a healthy, well-sampled sensor "
    f"with no drop, the candidate false stamps.",
    f"{n_rec:,} drop events are never matched by a stamped stop on any day of their window - recovered "
    f"emptyings worth an estimated {rec_t:,} tonnes (drop magnitude x bin volume x material mid "
    f"density), material the driver file misses entirely.",
    f"Record-level agreement between the two instruments stays flat at roughly half (39-52% by year, "
    f"A2 table), so the comparison must stay at bin-day granularity; the confusion matrix, not either "
    f"file alone, is the honest inventory of service events.",
]

out = {
    "task": "C2/T5 two-file comparison, bin-day level",
    "definitions": {
        "universe": "instrumented bins (>=1 valid sensor reading) x days within each bin's first-to-last valid-reading span",
        "driver_evidence": "bin appears as an 'S' (stamped) stop in a trips_v6 track that day",
        "sensor_evidence": "a sensor drop event (A2) whose before-after window touches that day",
        "neither_with_activity": "no evidence from either file but >=1 valid sensor reading that day",
        "recovered_emptying": "drop event with no stamped stop for that bin on any day of its window",
        "tonnage": "drop_units/100 x bin volume (L, raw_collections; default 2500) x material mid density P32/C75/G300 kg/m3",
    },
    "bins_instrumented": len(instrumented),
    "confusion_matrix": matrix,
    "confusion_matrix_per_year": {int(y): v for y, v in sorted(per_year.items())},
    "sensor_only_classification": sensor_only_class,
    "driver_only_classification": driver_only_class,
    "recovered_emptyings": {
        "events": n_rec,
        "estimated_tonnes_mid": rec_t,
        "per_year": rec_year,
        "events_on_days_with_any_track_visit": int(rec_visited.sum()),
    },
    "agreement_over_time": qual["agreement_by_year"],
    "findings": findings,
}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

print(json.dumps({"matrix": matrix, "sensor_only": sensor_only_class,
                  "driver_only": driver_only_class,
                  "recovered": {"events": n_rec, "tonnes": rec_t}}, indent=2))
