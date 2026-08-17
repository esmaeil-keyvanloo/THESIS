"""W2 - Extract collection trips from the driver file for the webGIS.
A 'trip' here = one idrecolha (collection identifier): the containers it visited,
ordered by service timestamp. Distances between stops are straight lines (no GPS).
Outputs: trips.json (embedded later into the HTML), trip_stats.json
"""
import duckdb, json, math

BASE = r"C:/Users/esmae/Desktop/phd Esmaeil/THESIS CLAUDE"
OUT = f"{BASE}/W2/02_data_work"
con = duckdb.connect()

con.sql(f"""
  CREATE VIEW c AS SELECT
    trim(idcontentor) cid, trim(description) fraction,
    TRY_CAST(REPLACE(Latitude, ',', '.') AS DOUBLE) lat,
    TRY_CAST(REPLACE(Longitude, ',', '.') AS DOUBLE) lon,
    TRY_CAST("Enchimento" AS INT) fill, trim(idrecolha) idr, trim(Rota) rota,
    TRY_CAST("Data de \u00ednicio" AS TIMESTAMP) t_start,
    TRY_CAST("Data de fim" AS TIMESTAMP) t_end,
    TRY_CAST("Km totais" AS DOUBLE) km, TRY_CAST("Peso total" AS DOUBLE) peso,
    TRY_CAST("Data da leitura" AS TIMESTAMP) ts
  FROM '{BASE}/Brain/03_db/parquet/raw_collections.parquet'
  WHERE idrecolha IS NOT NULL AND trim(idrecolha) NOT IN ('', '0')
""")

rows = con.sql("""
  SELECT idr, cid, fraction, lat, lon, ts, rota, t_start, t_end, MAX(km) OVER (PARTITION BY idr) km,
         MAX(peso) OVER (PARTITION BY idr) peso
  FROM c ORDER BY idr, ts
""").df()

def hav(a, b, c, d):
    p = math.pi / 180
    x = 0.5 - math.cos((c - a) * p) / 2 + math.cos(a * p) * math.cos(c * p) * (1 - math.cos((d - b) * p)) / 2
    return 12742 * math.asin(math.sqrt(x))

trips = []
for idr, g in rows.groupby("idr", sort=False):
    g = g.sort_values("ts")
    stops = []
    seen = set()
    for r in g.itertuples():
        if r.cid in seen:  # keep first service of each container
            continue
        seen.add(r.cid)
        stops.append([round(r.lat, 6), round(r.lon, 6), r.cid, r.ts.strftime("%H:%M"), r.fraction[:1]])
    if not stops:
        continue
    d_line = sum(hav(stops[i][0], stops[i][1], stops[i+1][0], stops[i+1][1]) for i in range(len(stops)-1))
    t0 = g.t_start.min(); t1 = g.t_end.max()
    dur = (t1 - t0).total_seconds() / 3600 if (t0 is not None and t1 is not None and str(t0) != 'NaT' and str(t1) != 'NaT') else None
    fr = g.fraction.mode().iloc[0]
    trips.append({
        "id": str(idr),
        "date": g.ts.min().strftime("%Y-%m-%d"),
        "start": str(t0)[11:16] if dur is not None else g.ts.min().strftime("%H:%M"),
        "end": str(t1)[11:16] if dur is not None else g.ts.max().strftime("%H:%M"),
        "dur_h": round(dur, 2) if dur is not None else None,
        "rota": (g.rota.iloc[0] or ""),
        "frac": {"M": "Packaging", "E": "Paper/card", "m": "Packaging"}.get(fr[:1], "Packaging" if fr.startswith("Mistura") else ("Paper/card" if "papel" in fr else "Glass")),
        "n_bins": len(stops),
        "km_rec": g.km.iloc[0] if g.km.iloc[0] and g.km.iloc[0] > 0 else None,
        "kg": g.peso.iloc[0] if g.peso.iloc[0] and g.peso.iloc[0] > 0 else None,
        "km_line": round(d_line, 1),
        "stops": stops,
    })

with open(f"{OUT}/trips.json", "w", encoding="utf-8") as f:
    json.dump(trips, f, ensure_ascii=False, separators=(",", ":"))

# headline stats
import statistics as st
multi = [t for t in trips if t["n_bins"] >= 2]
withdur = [t for t in multi if t["dur_h"] and 0 < t["dur_h"] < 24]
S = {
    "collection_groups_total": len(trips),
    "groups_single_bin": len(trips) - len(multi),
    "trips_multi_bin": len(multi),
    "dates_with_activity": len({t["date"] for t in trips}),
    "max_trips_one_day": max(__import__('collections').Counter(t["date"] for t in multi).values()),
    "bins_per_trip_median": st.median(t["n_bins"] for t in multi),
    "bins_per_trip_p90": sorted(t["n_bins"] for t in multi)[int(0.9*len(multi))],
    "duration_h_median": round(st.median(t["dur_h"] for t in withdur), 1),
    "km_recorded_median": st.median(t["km_rec"] for t in multi if t["km_rec"]),
    "kg_median": st.median(t["kg"] for t in multi if t["kg"]),
    "kg_per_km_median": round(st.median(t["kg"]/t["km_rec"] for t in multi if t["kg"] and t["km_rec"]), 1),
    "straightline_vs_recorded_median_ratio": round(st.median(t["km_line"]/t["km_rec"] for t in multi if t["km_rec"] and t["km_line"] > 0), 2),
    "by_fraction": {},
}
for fr in ("Packaging", "Paper/card", "Glass"):
    sub = [t for t in multi if t["frac"] == fr]
    if sub:
        S["by_fraction"][fr] = {"trips": len(sub), "median_bins": st.median(t["n_bins"] for t in sub)}
with open(f"{OUT}/trip_stats.json", "w", encoding="utf-8") as f:
    json.dump(S, f, indent=1)
print(json.dumps(S, indent=1))
print("trips.json size MB:", round(len(json.dumps(trips))/1e6, 1))
