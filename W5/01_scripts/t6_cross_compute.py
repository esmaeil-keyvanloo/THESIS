# TASK J step 1 of 2 - run BEFORE t6_info_stats.py (writes _cross_tmp.json,
# which t6_info_stats.py consumes and then removes).
# TASK J helper - derive cross-file per-year table + cadence from W5 artifacts
import json, math, time
from collections import defaultdict, Counter
from datetime import datetime, timedelta

import duckdb
import numpy as np

ROOT = r"C:/Users/esmae/Desktop/phd Esmaeil/THESIS CLAUDE"
W5 = f"{ROOT}/W5/02_data_work"
t0 = time.time()
log = lambda *a: print(f"[{time.time()-t0:5.1f}s]", *a, flush=True)

world = json.load(open(f"{W5}/trips_v7_enriched.json", encoding="utf-8"))
log("world", len(world))

def stop_dates(t):
    d0 = datetime.strptime(t["date"], "%Y-%m-%d")
    out, prev, off = [], None, timedelta(0)
    for s in t["stops"]:
        cur = d0 + off + timedelta(hours=int(s[3][:2]), minutes=int(s[3][3:]))
        if prev is not None:
            while cur < prev - timedelta(hours=12):
                cur += timedelta(days=1); off += timedelta(days=1)
        out.append(cur)
        prev = cur if prev is None else max(prev, cur)
    return out

# stamped stops with src tag (10-element stops: [lat,lon,cid,hhmm,type,fill,est,mat,sens,src])
stamp_by_cid = defaultdict(list)   # cid -> [epoch]
per_year = defaultdict(lambda: Counter())
s_total = ds_total = 0
for t in world:
    if t.get("frac") == "Phantom":
        continue
    dts = stop_dates(t)
    for s, dt in zip(t["stops"], dts):
        if s[4] != "S":
            continue
        y = dt.year
        stamp_by_cid[str(s[2])].append(dt.timestamp())
        s_total += 1
        if s[9] == "DS":
            per_year[y]["ds"] += 1; ds_total += 1
        else:
            per_year[y]["d"] += 1
for v in stamp_by_cid.values():
    v.sort()
log("stamped stops", s_total, "ds", ds_total)

# drops: matched if a stamped stop for same cid falls in [t_before-90m, t_after+90m]
con = duckdb.connect()
dr = con.sql(f"SELECT cid, t_before, t_after, confidence FROM '{W5}/sensor_drops_v2.parquet'").df()
W = 90 * 60
import bisect
m_total = 0
for r in dr.itertuples():
    cid = str(r.cid)
    tb = r.t_before.timestamp() - W
    ta = r.t_after.timestamp() + W
    y = r.t_after.year
    arr = stamp_by_cid.get(cid)
    hit = False
    if arr:
        i = bisect.bisect_left(arr, tb)
        hit = i < len(arr) and arr[i] <= ta
    if hit:
        per_year[y]["drop_matched"] += 1; m_total += 1
    else:
        per_year[y]["s_only"] += 1
log("drops matched", m_total, "of", len(dr))

# instrumented split of D-only: bins with >=1 kept reading in that year
act = con.sql(f"""
  SELECT year(ts) y, cid, count(*) n,
         date_diff('day', min(ts), max(ts)) + 1 span_days
  FROM '{W5}/sensor_clean.parquet' GROUP BY 1,2
""").df()
act_year = defaultdict(set)
for r in act.itertuples():
    act_year[int(r.y)].add(str(r.cid))

d_instr = defaultdict(int)
for t in world:
    if t.get("frac") == "Phantom":
        continue
    dts = stop_dates(t)
    for s, dt in zip(t["stops"], dts):
        if s[4] == "S" and s[9] == "D" and str(s[2]) in act_year.get(dt.year, ()):
            d_instr[dt.year] += 1

# cadence: kept readings per bin per active day (span first->last kept reading in year)
cad = {}
for y, g in act.groupby("y"):
    tot_read = int(g["n"].sum()); tot_days = int(g["span_days"].sum())
    per_bin = (g["n"] / g["span_days"]).median()
    cad[int(y)] = {"readings_per_bin_day_mean": round(tot_read / tot_days, 2),
                   "readings_per_bin_day_median_bin": round(float(per_bin), 2)}

out = {"per_year": {}, "totals": {
    "stamped_stops": s_total, "ds": ds_total,
    "drops_kept": int(len(dr)), "drops_matched": m_total,
    "s_only": int(len(dr)) - m_total}}
for y in sorted(per_year):
    c = per_year[y]
    out["per_year"][str(y)] = {
        "d_only_all": int(c["d"]), "d_only_instrumented": int(d_instr.get(y, 0)),
        "ds": int(c["ds"]), "s_only": int(c["s_only"]),
        "drops_matched": int(c["drop_matched"]),
        "cadence": cad.get(y)}
json.dump(out, open(f"{ROOT}/W5/02_data_work/_cross_tmp.json", "w"), indent=1)
print(json.dumps(out, indent=1))
