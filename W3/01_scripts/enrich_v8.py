"""W3 v8 - Per stop: add bin material letter + nearest sensor fill (% of ceiling, +/-3h).
Per trip: est2 = emptied + same-material observed bins, capped at identifier load.
Updates year_*.json (stops -> 9 elements) and trips_index.json (est2_mid, wshare2, capped).
"""
import duckdb, json, glob, bisect
from collections import defaultdict

BASE = r"C:/Users/esmae/Desktop/phd Esmaeil/THESIS CLAUDE"
DATA = f"{BASE}/W3/03_outputs/explorer/data"
DENS_MID = {"P": 32, "C": 75, "G": 300}
FR2L = {"Packaging": "P", "Paper/card": "C", "Glass": "G"}

con = duckdb.connect()
bins = con.sql(f"""
  SELECT trim(idcontentor) cid, MAX(TRY_CAST("Volume do tipo de contentor" AS INT)) vol,
         ANY_VALUE(CASE WHEN description LIKE '%Vidro%' THEN 'G'
                        WHEN description LIKE '%papel%' THEN 'C' ELSE 'P' END) fl
  FROM '{BASE}/Brain/03_db/parquet/raw_collections.parquet' GROUP BY 1
""").df()
VOL = {r.cid: (int(r.vol or 2500), r.fl) for r in bins.itertuples()}

sens = con.sql(f"""
  SELECT trim(idcontentor) cid, TRY_CAST("Data da leitura" AS TIMESTAMP) ts,
         TRY_CAST("Enchimento" AS INT) fill
  FROM '{BASE}/Brain/03_db/parquet/raw_sensors.parquet'
  WHERE TRY_CAST("Enchimento" AS INT) BETWEEN 0 AND 100 ORDER BY cid, ts
""").df()
S_TS, S_F, CEIL = defaultdict(list), defaultdict(list), {}
for r in sens.itertuples():
    S_TS[r.cid].append(r.ts.timestamp()); S_F[r.cid].append(r.fill)
    if r.fill > CEIL.get(r.cid, 0): CEIL[r.cid] = r.fill

from datetime import datetime
def sensor_pct(cid, date, hhmm):
    ts_list = S_TS.get(cid)
    if not ts_list: return None
    t0 = datetime.fromisoformat(f"{date} {hhmm}").timestamp()
    i = bisect.bisect_left(ts_list, t0)
    best, bd = None, 10801
    for j in (i - 1, i):
        if 0 <= j < len(ts_list):
            d = abs(ts_list[j] - t0)
            if d < bd: bd, best = d, j
    if best is None or bd > 10800: return None
    c = CEIL.get(cid) or 84
    return round(S_F[cid][best] * 100.0 / c)

idx = json.load(open(f"{DATA}/trips_index.json", encoding="utf-8"))
meta = {str(t["id"]): t for t in idx}
track_est2 = {}
n_sens = 0
for yf in sorted(glob.glob(f"{DATA}/year_*.json")):
    d = json.load(open(yf, encoding="utf-8"))
    for tid, stops in d["stops"].items():
        t = meta.get(tid, {})
        tl = FR2L.get(t.get("frac"), "P")
        date = t.get("date", "2022-01-01")
        strict = t.get("est_mid") or 0
        obs = 0.0
        for s in stops:
            vol, fl = VOL.get(str(s[2]), (2500, tl))
            sp = sensor_pct(str(s[2]), date, s[3])
            if sp is not None: n_sens += 1
            # normalize to 9 elements: [...,fill,estkg,mat,sensorPct]
            while len(s) < 7: s.append(None)
            if len(s) == 7: s.extend([fl, sp])
            else: s[7], s[8] = fl, sp
            if s[4] == "I" and fl == tl and s[5] is not None and s[5] >= 0:
                obs += vol / 1000 * s[5] / 100 * DENS_MID[fl]
        track_est2[tid] = strict + obs
    json.dump(d, open(yf, "w", encoding="utf-8"), separators=(",", ":"))

by_ident = defaultdict(lambda: {"kg": None, "sum": 0.0})
def ident_of(t):
    return str(t["id"])[:-len(t["part"])] if t.get("part") else str(t["id"])
for t in idx:
    g = by_ident[ident_of(t)]
    g["kg"] = g["kg"] or t.get("kg")
    g["sum"] += track_est2.get(str(t["id"]), 0)
for t in idx:
    e2 = track_est2.get(str(t["id"]))
    if e2 is None: continue
    g = by_ident[ident_of(t)]
    factor = 1.0
    capped = False
    if g["kg"] and g["sum"] > g["kg"]:
        factor = g["kg"] / g["sum"]; capped = True
    t["est2_mid"] = round(e2 * factor)
    t["capped"] = capped
    t["wshare2"] = min(100.0, round(100 * g["sum"] * factor / g["kg"], 1)) if g["kg"] else None
json.dump(idx, open(f"{DATA}/trips_index.json", "w", encoding="utf-8"), separators=(",", ":"))

import statistics
sh2 = [t["wshare2"] for t in idx if t.get("wshare2") and t.get("n_parts") == 1 and t.get("kg")]
capped_n = sum(1 for t in idx if t.get("capped"))
print("stops with sensor match:", n_sens, "| capped tracks:", capped_n,
      "| median wshare2 (unsplit):", round(statistics.median(sh2), 1), "% vs strict 5.0%")
