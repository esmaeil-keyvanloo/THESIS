"""W3 v9 - (a) Est. kg for inferred stops (own material x own fill, table only);
(b) sensor match includes negatives: nearest reading +/-3h; valid -> % of ceiling,
negative -> raw error code (client renders faded). Updates year_*.json in place.
"""
import duckdb, json, glob, bisect
from collections import defaultdict
from datetime import datetime

BASE = r"C:/Users/esmae/Desktop/phd Esmaeil/THESIS CLAUDE"
DATA = f"{BASE}/W3/03_outputs/explorer/data"
DENS_MID = {"P": 32, "C": 75, "G": 300}

con = duckdb.connect()
bins = con.sql(f"""
  SELECT trim(idcontentor) cid, MAX(TRY_CAST("Volume do tipo de contentor" AS INT)) vol
  FROM '{BASE}/Brain/03_db/parquet/raw_collections.parquet' GROUP BY 1
""").df()
VOL = {r.cid: int(r.vol or 2500) for r in bins.itertuples()}

sens = con.sql(f"""
  SELECT trim(idcontentor) cid, TRY_CAST("Data da leitura" AS TIMESTAMP) ts,
         TRY_CAST("Enchimento" AS INT) fill
  FROM '{BASE}/Brain/03_db/parquet/raw_sensors.parquet'
  WHERE TRY_CAST("Enchimento" AS INT) IS NOT NULL ORDER BY cid, ts
""").df()
S_TS, S_F, CEIL = defaultdict(list), defaultdict(list), {}
for r in sens.itertuples():
    S_TS[r.cid].append(r.ts.timestamp()); S_F[r.cid].append(int(r.fill))
    if 0 <= r.fill <= 100 and r.fill > CEIL.get(r.cid, 0): CEIL[r.cid] = int(r.fill)

def sensor_val(cid, date, hhmm):
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
    v = S_F[cid][best]
    if v < 0: return v                       # raw error code, negative
    return round(v * 100.0 / (CEIL.get(cid) or 84))   # % of ceiling

idx = json.load(open(f"{DATA}/trips_index.json", encoding="utf-8"))
meta = {str(t["id"]): t for t in idx}
n_est = n_neg = n_val = 0
for yf in sorted(glob.glob(f"{DATA}/year_*.json")):
    d = json.load(open(yf, encoding="utf-8"))
    for tid, stops in d["stops"].items():
        date = meta.get(tid, {}).get("date", "2022-01-01")
        for s in stops:
            while len(s) < 9: s.append(None)
            if s[4] == "I" and s[6] is None and s[5] is not None and s[5] >= 0 and s[7] in DENS_MID:
                s[6] = round(VOL.get(str(s[2]), 2500) / 1000 * s[5] / 100 * DENS_MID[s[7]], 1)
                n_est += 1
            sv = sensor_val(str(s[2]), date, s[3])
            s[8] = sv
            if sv is not None:
                n_neg += sv < 0; n_val += sv >= 0
    json.dump(d, open(yf, "w", encoding="utf-8"), separators=(",", ":"))
print(f"inferred est added: {n_est} | sensor matches: {n_val} valid + {n_neg} error codes")
