"""W3 - Estimate weight of recorded bins per trip via material density bands.
Only STAMPED stops count (inferred = observations, not collections - canon rule).
Updates explorer data in place: trips_index.json (est_lo/mid/hi, wshare) and
year_*.json stops gain 7th element est_kg (mid). Writes weightshare_analysis.json.
"""
import duckdb, json, glob, statistics

BASE = r"C:/Users/esmae/Desktop/phd Esmaeil/THESIS CLAUDE"
DATA = f"{BASE}/W3/03_outputs/explorer/data"
DENS = {"P": (25, 32, 40), "C": (50, 75, 100), "G": (250, 300, 350)}  # kg/m3 lo/mid/hi
FR2L = {"Packaging": "P", "Paper/card": "C", "Glass": "G"}

con = duckdb.connect()
bins = con.sql(f"""
  SELECT trim(idcontentor) cid,
         MAX(TRY_CAST("Volume do tipo de contentor" AS INT)) vol,
         ANY_VALUE(CASE WHEN description LIKE '%Vidro%' THEN 'G'
                        WHEN description LIKE '%papel%' THEN 'C' ELSE 'P' END) fl
  FROM '{BASE}/Brain/03_db/parquet/raw_collections.parquet' GROUP BY 1
""").df()
VOL = {r.cid: (int(r.vol or 2500), r.fl) for r in bins.itertuples()}

idx = json.load(open(f"{DATA}/trips_index.json", encoding="utf-8"))
meta = {t["id"]: t for t in idx}
est = {}

for yf in sorted(glob.glob(f"{DATA}/year_*.json")):
    d = json.load(open(yf, encoding="utf-8"))
    for tid, stops in d["stops"].items():
        t = meta.get(tid) or {}
        fills = [s[5] for s in stops if len(s) > 5 and s[5] is not None and s[5] >= 0]
        fallback = statistics.median(fills) if fills else 75
        lo = mid = hi = 0.0
        for s in stops:
            typ = s[4] if len(s) > 4 else "S"
            if typ == "I":
                s.append(None) if len(s) == 6 else None
                if len(s) == 5: s.extend([None, None])
                continue
            vol, fl = VOL.get(str(s[2]), (2500, FR2L.get(t.get("frac"), "P")))
            fill = s[5] if len(s) > 5 and s[5] is not None and s[5] >= 0 else fallback
            m3 = vol / 1000 * fill / 100
            dl, dm, dh = DENS[fl]
            lo += m3 * dl; mid += m3 * dm; hi += m3 * dh
            ekg = round(m3 * dm, 1)
            if len(s) == 5: s.extend([None, ekg])
            elif len(s) == 6: s.append(ekg)
            else: s[6] = ekg
        est[tid] = [round(lo), round(mid), round(hi)]
    json.dump(d, open(yf, "w", encoding="utf-8"), separators=(",", ":"))

# identifier-level share (kg is shared across an identifier's tracks)
by_ident = {}
for t in idx:
    ident = str(t["id"]).rstrip("abcdefghijklmnopqrstuvwxyz") if t.get("part") else str(t["id"])
    by_ident.setdefault(ident, {"kg": t.get("kg"), "mid": 0.0})
    by_ident[ident]["mid"] += est.get(str(t["id"]), [0, 0, 0])[1]
for t in idx:
    e = est.get(str(t["id"]))
    if not e: continue
    t["est_lo"], t["est_mid"], t["est_hi"] = e
    ident = str(t["id"]).rstrip("abcdefghijklmnopqrstuvwxyz") if t.get("part") else str(t["id"])
    g = by_ident[ident]
    t["wshare"] = round(100 * g["mid"] / g["kg"], 1) if g["kg"] else None
json.dump(idx, open(f"{DATA}/trips_index.json", "w", encoding="utf-8"), separators=(",", ":"))

# analysis: unsplit identifiers with kg>0
shares = [t["wshare"] for t in idx if t.get("wshare") and t.get("n_parts") == 1 and t.get("kg")]
byfrac = {}
for t in idx:
    if t.get("wshare") and t.get("n_parts") == 1 and t.get("kg"):
        byfrac.setdefault(t["frac"], []).append(t["wshare"])
A = {
    "densities_kg_m3": {"Packaging": DENS["P"], "Paper/card": DENS["C"], "Glass": DENS["G"]},
    "rule": "stamped stops only; fill = pre-emptying reading (trip-median fallback); est = vol*fill*density",
    "n_unsplit_trips_with_kg": len(shares),
    "share_pct_p10_50_90": [round(statistics.quantiles(shares, n=10)[0], 1),
                             round(statistics.median(shares), 1),
                             round(statistics.quantiles(shares, n=10)[8], 1)],
    "median_share_by_fraction": {k: round(statistics.median(v), 1) for k, v in byfrac.items()},
}
json.dump(A, open(f"{BASE}/W3/02_data_work/weightshare_analysis.json", "w", encoding="utf-8"), indent=1)
print(json.dumps(A, indent=1))
