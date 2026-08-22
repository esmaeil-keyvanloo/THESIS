"""W4 TASK B2 (T3) - Phantom tracks from the leftovers.

Input: W4/02_data_work/reading_assignments_v6.parquet rows with status
INFEASIBLE or NO_TRIP_RUNNING. Per DATE, chain greedily in time order under
the same physics as assign_loose_readings_v6 (haversine x1.3, service 2 min,
min gap 0.5 min, feasible <= 60 km/h). Each reading joins the best feasible
open chain (lowest implied speed from the chain's last stop), else opens a
new chain.

Chains with >=3 stops -> phantom tracks  id PH<yyyymmdd>-<n>
Chains with 1-2 stops -> isolated observations (reason = original status)

Outputs:
  W4/02_data_work/phantom_tracks.json
  W4/02_data_work/isolated_observations.parquet
  W4/02_data_work/phantom_stats.json
"""
import json
import math
from collections import Counter, defaultdict

import pandas as pd

BASE = r"C:/Users/esmae/Desktop/phd Esmaeil/THESIS CLAUDE"
IN_ASSIGN = f"{BASE}/W4/02_data_work/reading_assignments_v6.parquet"
PARQ_COLL = f"{BASE}/Brain/03_db/parquet/raw_collections.parquet"
PARQ_SENS = f"{BASE}/Brain/03_db/parquet/raw_sensors.parquet"
OUT_TRACKS = f"{BASE}/W4/02_data_work/phantom_tracks.json"
OUT_ISOLATED = f"{BASE}/W4/02_data_work/isolated_observations.parquet"
OUT_STATS = f"{BASE}/W4/02_data_work/phantom_stats.json"

R_EARTH = 6371.0088
DETOUR = 1.3
SERVICE_MIN = 2.0
MIN_GAP_MIN = 0.5
VMAX = 60.0
MIN_CHAIN = 3

LEFTOVER = {"INFEASIBLE", "NO_TRIP_RUNNING"}


def hav_km(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    h = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R_EARTH * math.asin(math.sqrt(h))


def implied_speed(lat1, lon1, t1, lat2, lon2, t2):
    """km/h for the leg; haversine x detour over (gap - service, floored)."""
    dist = hav_km(lat1, lon1, lat2, lon2) * DETOUR
    gap_min = max(abs((t2 - t1).total_seconds()) / 60.0 - SERVICE_MIN, MIN_GAP_MIN)
    return dist / (gap_min / 60.0)


# ---------------- 1. bin -> material map ----------------
def material_of(desc):
    d = str(desc).lower()
    if "papel" in d:
        return "Paper/card"
    if "vidro" in d:
        return "Glass"
    if "embalagen" in d:  # 'Mistura de embalagens'
        return "Packaging"
    return None


mat_votes = defaultdict(Counter)
for pq_file in (PARQ_COLL, PARQ_SENS):
    d = pd.read_parquet(pq_file, columns=["idcontentor", "description"])
    d["idcontentor"] = d["idcontentor"].astype(str).str.strip()
    for cid, desc, n in d.groupby(["idcontentor", "description"]).size().reset_index().values:
        m = material_of(desc)
        if m:
            mat_votes[cid][m] += n
cid_mat = {cid: c.most_common(1)[0][0] for cid, c in mat_votes.items()}

# ---------------- 2. leftovers ----------------
adf = pd.read_parquet(IN_ASSIGN)
left = adf[adf["status"].isin(LEFTOVER)].copy()
left["cid"] = left["cid"].astype(str).str.strip()
n_input = len(left)
input_by_status = left["status"].value_counts().to_dict()

# rows without coordinates cannot be chained -> isolated straight away
no_coord = left[left["lat"].isna() | left["lon"].isna()]
chainable = left[left["lat"].notna() & left["lon"].notna()].sort_values(["ts", "cid"])

isolated_rows = [
    (r.cid, r.ts, r.lat, r.lon, r.fill, r.status)
    for r in no_coord.itertuples(index=False)
]

# ---------------- 3. greedy chaining per date ----------------
phantoms = []
largest = None
for date, day in chainable.groupby(chainable["ts"].dt.date, sort=True):
    chains = []  # each: list of (lat, lon, cid, ts, fill, status)
    for r in day.itertuples(index=False):
        ts = r.ts.to_pydatetime()
        best_i, best_v = None, None
        for i, ch in enumerate(chains):
            llat, llon, _, lts, _, _ = ch[-1]
            v = implied_speed(llat, llon, lts, r.lat, r.lon, ts)
            if v <= VMAX and (best_v is None or v < best_v):
                best_i, best_v = i, v
        stop = (r.lat, r.lon, r.cid, ts, r.fill, r.status)
        if best_i is None:
            chains.append([stop])
        else:
            chains[best_i].append(stop)

    chains.sort(key=lambda ch: ch[0][3])  # order by chain start time
    n = 0
    for ch in chains:
        if len(ch) < MIN_CHAIN:
            for lat, lon, cid, ts, fill, status in ch:
                isolated_rows.append((cid, ts, lat, lon, fill, status))
            continue
        n += 1
        pid = f"PH{date.strftime('%Y%m%d')}-{n}"
        t0, t1 = ch[0][3], ch[-1][3]
        km_line = round(sum(
            hav_km(a[0], a[1], b[0], b[1]) for a, b in zip(ch, ch[1:])), 2)
        mats = Counter(cid_mat[s[2]] for s in ch if s[2] in cid_mat)
        mat_hint = mats.most_common(1)[0][0] if mats else "Unknown"
        rec = {
            "id": pid,
            "date": date.isoformat(),
            "start": t0.strftime("%H:%M"),
            "end": t1.strftime("%H:%M"),
            "dur_h": round((t1 - t0).total_seconds() / 3600.0, 2),
            "n_bins": len(ch),
            "frac": "Phantom",
            "mat_hint": mat_hint,
            "km_line": km_line,
            "stops": [[round(s[0], 6), round(s[1], 6), str(s[2]),
                       s[3].strftime("%H:%M"), "P"] for s in ch],
        }
        phantoms.append(rec)
        if largest is None or rec["n_bins"] > largest["n_bins"]:
            largest = rec

# ---------------- 4. outputs ----------------
with open(OUT_TRACKS, "w", encoding="utf-8") as f:
    json.dump(phantoms, f, ensure_ascii=False)

iso = pd.DataFrame(isolated_rows, columns=["cid", "ts", "lat", "lon", "fill", "reason"])
iso = iso.sort_values(["ts", "cid"]).reset_index(drop=True)
iso.to_parquet(OUT_ISOLATED, index=False)

stops_absorbed = sum(p["n_bins"] for p in phantoms)
stats = {
    "input_leftovers": n_input,
    "input_by_status": input_by_status,
    "no_coordinate_rows": len(no_coord),
    "phantom_tracks": len(phantoms),
    "stops_absorbed": stops_absorbed,
    "isolated_observations": len(iso),
    "isolated_by_reason": iso["reason"].value_counts().to_dict(),
    "dates_with_phantoms": len({p["date"] for p in phantoms}),
    "mat_hint_counts": dict(Counter(p["mat_hint"] for p in phantoms)),
    "n_bins_distribution": {
        "min": min((p["n_bins"] for p in phantoms), default=0),
        "median": float(pd.Series([p["n_bins"] for p in phantoms]).median()) if phantoms else 0,
        "max": max((p["n_bins"] for p in phantoms), default=0),
    },
    "largest_phantom": {k: largest[k] for k in
                        ("id", "date", "start", "end", "dur_h", "n_bins", "km_line", "mat_hint")}
                       if largest else None,
    "params": {"detour": DETOUR, "service_min": SERVICE_MIN,
               "min_gap_min": MIN_GAP_MIN, "vmax_kmh": VMAX,
               "min_chain_stops": MIN_CHAIN},
}
with open(OUT_STATS, "w", encoding="utf-8") as f:
    json.dump(stats, f, ensure_ascii=False, indent=2)

print(json.dumps(stats, indent=2))
