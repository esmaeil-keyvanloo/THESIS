"""W3 - Add fill values to every stop: stamped stops get their pre-emptying fill,
inferred stops get the reading's own fill. Output: trips_v5_enriched.json"""
import duckdb, json
from collections import defaultdict

BASE = r"C:/Users/esmae/Desktop/phd Esmaeil/THESIS CLAUDE"
con = duckdb.connect()
rows = con.sql(f"""
  SELECT trim(idcontentor) cid, TRY_CAST("Data da leitura" AS TIMESTAMP) ts,
         TRY_CAST("Enchimento" AS INT) fill,
         (trim(idrecolha) NOT IN ('', '0') AND idrecolha IS NOT NULL) is_event
  FROM '{BASE}/Brain/03_db/parquet/raw_collections.parquet' ORDER BY cid, ts
""").df()

# per event row: pre-emptying fill (prev reading same cid <=15 min, fill>=0)
prefill = {}     # (cid, 'YYYY-MM-DD HH:MM') -> fill before emptying
readfill = defaultdict(list)  # (cid, minute) -> [fill,...] for non-event rows
prev = {}
for r in rows.itertuples():
    key = (r.cid, r.ts.strftime("%Y-%m-%d %H:%M"))
    if r.is_event:
        p = prev.get(r.cid)
        if p is not None and (r.ts - p[0]).total_seconds() <= 900 and p[1] is not None and p[1] >= 0:
            prefill[key] = int(p[1])
    else:
        readfill[key].append(int(r.fill) if r.fill is not None else None)
    prev[r.cid] = (r.ts, r.fill)

trips = json.load(open(f"{BASE}/W2/02_data_work/trips_v5.json", encoding="utf-8"))
hit_s = hit_i = miss = 0
for t in trips:
    date = t["date"]
    ns = []
    for s in t["stops"]:
        key = (str(s[2]), f"{date} {s[3]}")
        typ = s[4] if len(s) > 4 else "S"
        if typ == "I":
            vals = readfill.get(key)
            f = vals.pop(0) if vals else None
            hit_i += f is not None
        else:
            f = prefill.get(key)
            hit_s += f is not None
        if f is None: miss += 1
        ns.append([s[0], s[1], s[2], s[3], typ, f])
    t["stops"] = ns

json.dump(trips, open(f"{BASE}/W2/02_data_work/trips_v5_enriched.json", "w", encoding="utf-8"), separators=(",", ":"))
print(f"stamped with pre-fill: {hit_s}, inferred with fill: {hit_i}, without: {miss}")
