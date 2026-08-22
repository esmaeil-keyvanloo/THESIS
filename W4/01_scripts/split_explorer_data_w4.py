"""W4 - Split v6 explorer data into index + per-year chunks (incl. speed-flag paths)."""
import json, shutil, os
BASE = r"C:/Users/esmae/Desktop/phd Esmaeil/THESIS CLAUDE"
W4 = f"{BASE}/W4/02_data_work"
OUT = f"{BASE}/W4/03_outputs/explorer/data"
os.makedirs(OUT, exist_ok=True)
idx = json.load(open(f"{W4}/trips_index_v6.json", encoding="utf-8"))
trips = json.load(open(f"{W4}/trips_v6_enriched.json", encoding="utf-8"))
_r = json.load(open(f"{W4}/trips_routed_v6_fine.json", encoding="utf-8"))
routes = _r.get("routes", _r)
flags = _r.get("flags", {})
legs = json.load(open(f"{W4}/depot_legs_v6_fine.json", encoding="utf-8"))
legs = legs.get("legs", legs)
stops = {str(t["id"]): t["stops"] for t in trips}
keep = [t for t in idx if (t.get("n_bins", 0) + (t.get("n_inferred") or 0) + (t.get("n_lowconf") or 0)) >= 2]
years = {}
for t in keep:
    y = t["date"][:4]
    yd = years.setdefault(y, {"stops": {}, "routes": {}, "legs": {}, "flags": {}})
    tid = str(t["id"])
    if tid in stops: yd["stops"][tid] = stops[tid]
    if tid in routes: yd["routes"][tid] = routes[tid]
    if tid in legs: yd["legs"][tid] = legs[tid]
    if tid in flags: yd["flags"][tid] = flags[tid]
json.dump(keep, open(f"{OUT}/trips_index.json", "w", encoding="utf-8"), separators=(",", ":"))
for y, yd in years.items():
    json.dump(yd, open(f"{OUT}/year_{y}.json", "w", encoding="utf-8"), separators=(",", ":"))
for f in ["boundaries.json", "daily_kg.json", "facilities.json", "bins.json", "tempo.json"]:
    shutil.copy(f"{BASE}/W3/03_outputs/explorer/data/{f}", f"{OUT}/{f}")
shutil.copy(f"{BASE}/W4/01_scripts/explorer_w4_template.html", f"{BASE}/W4/03_outputs/explorer/index.html")
shutil.copy(f"{BASE}/W3/03_outputs/explorer/Open_Explorer_Locally.bat", f"{BASE}/W4/03_outputs/explorer/Open_Explorer_Locally.bat")
for f in sorted(os.listdir(OUT)):
    print(f"{os.path.getsize(f'{OUT}/{f}')/1e6:6.2f} MB  {f}")
print("tracks in index:", len(keep))
