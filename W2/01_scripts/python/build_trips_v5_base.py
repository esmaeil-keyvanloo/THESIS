"""W2 v5 - Build base trips from raw event rows, ALL fractions (glass included).

Previous trips.json silently dropped glass runs. This rebuild groups event rows
(idrecolha not in '', '0', NULL) by idrecolha; stops = event rows ordered by
timestamp as [lat, lon, cid, 'HH:MM', 'S'].
Output: W2/02_data_work/trips_v5_base.json
"""
import duckdb, json, math
from collections import Counter

BASE = r"C:/Users/esmae/Desktop/phd Esmaeil/THESIS CLAUDE"
PARQ = f"{BASE}/Brain/03_db/parquet/raw_collections.parquet"
OUT = f"{BASE}/W2/02_data_work/trips_v5_base.json"

FRACMAP = {
    "Mistura de embalagens": "Packaging",
    "Embalagens de papel e cart\u00e3o": "Paper/card",
    "Embalagens de Vidro": "Glass",
}

def map_frac(s):
    s = (s or "").strip()
    if s in FRACMAP:
        return FRACMAP[s]
    if s.startswith("Mistura"):
        return "Packaging"
    if "papel" in s.lower():
        return "Paper/card"
    if "vidro" in s.lower():
        return "Glass"
    return "Packaging"

def hav_km(a, b, c, d):
    p = math.pi / 180
    x = 0.5 - math.cos((c - a) * p) / 2 + math.cos(a * p) * math.cos(c * p) * (1 - math.cos((d - b) * p)) / 2
    return 12742 * math.asin(math.sqrt(x))

con = duckdb.connect()
rows = con.sql(f"""
  SELECT trim(idrecolha) idr,
         trim(idcontentor) cid,
         trim(description) fraction,
         TRY_CAST(REPLACE(Latitude, ',', '.') AS DOUBLE) lat,
         TRY_CAST(REPLACE(Longitude, ',', '.') AS DOUBLE) lon,
         TRY_CAST("Data da leitura" AS TIMESTAMP) ts,
         trim(Rota) rota,
         TRY_CAST("Km totais" AS DOUBLE) km,
         TRY_CAST("Peso total" AS DOUBLE) peso
  FROM '{PARQ}'
  WHERE idrecolha IS NOT NULL AND trim(idrecolha) NOT IN ('', '0')
  ORDER BY idr, ts
""").df()
print("event rows:", len(rows))

trips = []
skipped = 0
for idr, g in rows.groupby("idr", sort=False):
    g = g.sort_values("ts")
    g = g[g.ts.notna() & g.lat.notna() & g.lon.notna()]
    if len(g) == 0:
        skipped += 1
        continue
    stops = [[round(r.lat, 6), round(r.lon, 6), str(r.cid), r.ts.strftime("%H:%M"), "S"]
             for r in g.itertuples()]
    km_line = sum(hav_km(stops[i][0], stops[i][1], stops[i + 1][0], stops[i + 1][1])
                  for i in range(len(stops) - 1))
    def tmin(hhmm):
        h, m = hhmm.split(":")
        return int(h) * 60 + int(m)
    dh = (tmin(stops[-1][3]) - tmin(stops[0][3])) / 60
    rota_c = Counter(x for x in g.rota if isinstance(x, str) and x.strip())
    frac_c = Counter(map_frac(x) for x in g.fraction)
    km_rec = g.km.max()
    kg = g.peso.max()
    trips.append({
        "id": str(idr),
        "date": g.ts.iloc[0].strftime("%Y-%m-%d"),
        "start": stops[0][3],
        "end": stops[-1][3],
        "dur_h": round(dh + (24 if dh < 0 else 0), 2),
        "rota": rota_c.most_common(1)[0][0] if rota_c else "",
        "frac": frac_c.most_common(1)[0][0],
        "n_bins": len(stops),
        "km_rec": float(km_rec) if km_rec == km_rec and km_rec and km_rec > 0 else None,
        "kg": float(kg) if kg == kg and kg and kg > 0 else None,
        "km_line": round(km_line, 1),
        "stops": stops,
    })

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(trips, f, ensure_ascii=False, separators=(",", ":"))

fc = Counter(t["frac"] for t in trips)
fc_multi = Counter(t["frac"] for t in trips if t["n_bins"] >= 2)
stats = {
    "trips_total": len(trips),
    "skipped_empty": skipped,
    "by_fraction": dict(fc),
    "by_fraction_multibin": dict(fc_multi),
}
print(json.dumps(stats, indent=1))
