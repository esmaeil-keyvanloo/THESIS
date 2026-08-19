"""W3 - Split explorer data: small index + per-year chunks for lazy loading."""
import json, shutil, os

BASE = r"C:/Users/esmae/Desktop/phd Esmaeil/THESIS CLAUDE"
W2 = f"{BASE}/W2/02_data_work"
OUT = f"{BASE}/W3/03_outputs/explorer/data"
os.makedirs(OUT, exist_ok=True)

trips = json.load(open(f"{W2}/trips_v5_enriched.json", encoding="utf-8"))
routes = json.load(open(f"{W2}/trips_routed_v5_fine.json", encoding="utf-8"))
legs = json.load(open(f"{W2}/depot_legs_v5_fine.json", encoding="utf-8"))

META = ["id", "part", "n_parts", "date", "start", "end", "dur_h", "rota", "frac",
        "n_bins", "n_inferred", "km_rec", "kg"]
index, years = [], {}
for t in trips:
    if t["n_bins"] + (t.get("n_inferred") or 0) < 2:
        continue
    index.append({k: t.get(k) for k in META})
    y = t["date"][:4]
    yd = years.setdefault(y, {"stops": {}, "routes": {}, "legs": {}})
    tid = str(t["id"])
    yd["stops"][tid] = t["stops"]
    if tid in routes: yd["routes"][tid] = routes[tid]
    if tid in legs: yd["legs"][tid] = legs[tid]

json.dump(index, open(f"{OUT}/trips_index.json", "w", encoding="utf-8"), separators=(",", ":"))
for y, yd in years.items():
    json.dump(yd, open(f"{OUT}/year_{y}.json", "w", encoding="utf-8"), separators=(",", ":"))

for src, dst in [("boundaries.json", "boundaries.json"), ("daily_kg.json", "daily_kg.json"),
                 ("facilities_v2.json", "facilities.json"), ("bins_categorized.json", "bins.json"),
                 ("temporal_summary.json", "tempo.json")]:
    shutil.copy(f"{W2}/{src}", f"{OUT}/{dst}")

for f in sorted(os.listdir(OUT)):
    print(f"{os.path.getsize(f'{OUT}/{f}')/1e6:6.2f} MB  {f}")
print("index tracks:", len(index))
