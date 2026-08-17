# v5: route trips_v5 (ALL fractions incl. glass) on road graph + depot/TS legs + dump-leg hypothesis test
import json, time
import numpy as np
import geopandas as gpd
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra, connected_components
from shapely.geometry import LineString
from pyproj import Transformer

ROOT = r"C:/Users/esmae/Desktop/phd Esmaeil/THESIS CLAUDE"
ROADS = ROOT + "/GIS_DATA/01_osm/riomaior_10km/osm_roads_riomaior10km.gpkg"
TRIPS = ROOT + "/W2/02_data_work/trips_v5.json"
OUT_ROUTED = ROOT + "/W2/02_data_work/trips_routed_v5.json"
OUT_LEGS = ROOT + "/W2/02_data_work/depot_legs_v5.json"
OUT_ANAL = ROOT + "/W2/02_data_work/dumpleg_analysis_v5.json"

DEPOT = (39.33921, -8.92493)   # lat, lon
TS = (39.31963, -8.92405)

t0 = time.time()
BAN = {"path", "footway", "steps", "cycleway", "bridleway", "pedestrian"}

roads = gpd.read_file(ROADS)
if "fclass" in roads.columns:
    roads = roads[~roads["fclass"].isin(BAN)]
print("roads:", len(roads), flush=True)

node_ids = {}
node_xy = []
edges_u = []; edges_v = []; edges_w = []

def nid(x, y):
    k = (round(x), round(y))
    i = node_ids.get(k)
    if i is None:
        i = len(node_xy)
        node_ids[k] = i
        node_xy.append((x, y))
    return i

for geom in roads.geometry:
    if geom is None:
        continue
    parts = geom.geoms if geom.geom_type == "MultiLineString" else [geom]
    for ls in parts:
        cs = np.asarray(ls.coords)
        ids = [nid(x, y) for x, y in cs[:, :2]]
        seg = np.hypot(np.diff(cs[:, 0]), np.diff(cs[:, 1]))
        for a, b, w in zip(ids[:-1], ids[1:], seg):
            if a != b:
                edges_u.append(a); edges_v.append(b); edges_w.append(w)

N = len(node_xy)
node_xy = np.asarray(node_xy)
u = np.asarray(edges_u); v = np.asarray(edges_v); w = np.asarray(edges_w)
G = coo_matrix((np.concatenate([w, w]), (np.concatenate([u, v]), np.concatenate([v, u]))), shape=(N, N)).tocsr()
ncomp, labels = connected_components(G, directed=False)
main = np.argmax(np.bincount(labels))
main_idx = np.where(labels == main)[0]
tree = cKDTree(node_xy[main_idx])
print(f"graph {N} nodes, largest comp {len(main_idx)}, {time.time()-t0:.0f}s", flush=True)

to3763 = Transformer.from_crs(4326, 3763, always_xy=True)
towgs = Transformer.from_crs(3763, 4326, always_xy=True)

def snap_ll(lat, lon):
    x, y = to3763.transform(lon, lat)
    d, i = tree.query([[x, y]])
    return int(main_idx[i[0]]), float(d[0])

depot_n, depot_snap = snap_ll(*DEPOT)
ts_n, ts_snap = snap_ll(*TS)
print(f"depot node {depot_n} snap {depot_snap:.0f} m; TS node {ts_n} snap {ts_snap:.0f} m", flush=True)

# ---- trips
trips = json.load(open(TRIPS, encoding="utf-8"))
mtrips = [t for t in trips if t.get("n_bins", 0) >= 2 or t.get("n_bins", 0) + t.get("n_inferred", 0) >= 2]
print("multi-bin tracks:", len(mtrips), flush=True)

coords = {}
for t in mtrips:
    for s in t["stops"]:
        coords[(s[0], s[1])] = None
keys = list(coords.keys())
lons = np.array([k[1] for k in keys]); lats = np.array([k[0] for k in keys])
xs, ys = to3763.transform(lons, lats)
d, i = tree.query(np.column_stack([xs, ys]))
print("snap dist m: median %.0f max %.0f" % (np.median(d), d.max()), flush=True)
for k, ii in zip(keys, i):
    coords[k] = int(main_idx[ii])

trip_nodes = {}
pairs = set()
for t in mtrips:
    seq = []
    for s in t["stops"]:
        n = coords[(s[0], s[1])]
        if not seq or seq[-1] != n:
            seq.append(n)
    trip_nodes[t["id"]] = seq
    for a, b in zip(seq[:-1], seq[1:]):
        pairs.add((a, b))
print("unique consecutive pairs:", len(pairs), flush=True)

by_src = {}
for a, b in pairs:
    by_src.setdefault(a, set()).add(b)

legs = {}
srcs = sorted(by_src)
for ci, a in enumerate(srcs):
    dist, pred = dijkstra(G, directed=False, indices=a, return_predecessors=True)
    for b in by_src[a]:
        if not np.isfinite(dist[b]):
            legs[(a, b)] = None
            continue
        path = [b]
        c = b
        while c != a:
            c = pred[c]
            path.append(c)
        path.reverse()
        legs[(a, b)] = path
    if (ci + 1) % 200 == 0:
        print(f"  dijkstra {ci+1}/{len(srcs)} {time.time()-t0:.0f}s", flush=True)
print(f"dijkstra done {time.time()-t0:.0f}s", flush=True)

fallback_legs = 0
trip_geo = {}
for t in mtrips:
    seq = trip_nodes[t["id"]]
    coords_list = [node_xy[seq[0]]]
    for a, b in zip(seq[:-1], seq[1:]):
        leg = legs[(a, b)]
        if leg is None:
            fallback_legs += 1
            coords_list.append(node_xy[b])
        else:
            for n in leg[1:]:
                coords_list.append(node_xy[n])
    arr = np.asarray(coords_list)
    if len(arr) < 2:
        arr = np.vstack([arr, arr])
    km = float(np.hypot(np.diff(arr[:, 0]), np.diff(arr[:, 1])).sum() / 1000.0)
    trip_geo[t["id"]] = (km, arr)
print("fallback legs:", fallback_legs, flush=True)

# ---- serialize routed, adaptive tolerance
def build(tol):
    out = {}
    for tid, (km, arr) in trip_geo.items():
        ls = LineString(arr).simplify(tol, preserve_topology=False)
        cs = np.asarray(ls.coords)
        lon, lat = towgs.transform(cs[:, 0], cs[:, 1])
        path = [[round(float(la), 5), round(float(lo), 5)] for la, lo in zip(lat, lon)]
        out[str(tid)] = {"km": round(km, 1), "path": path}
    return out

tol = 15.0
while True:
    out = build(tol)
    s = json.dumps(out, separators=(",", ":"))
    mb = len(s.encode()) / 1e6
    print(f"tol={tol} -> {mb:.1f} MB", flush=True)
    if mb <= 11.5 or tol >= 200:
        break
    tol *= 1.6
open(OUT_ROUTED, "w", encoding="utf-8").write(s)
routed_tol = tol
routed_mb = mb

# ---- Step 2: depot / TS legs
# dijkstra from depot and from TS (undirected graph -> symmetric)
dist_dep, pred_dep = dijkstra(G, directed=False, indices=depot_n, return_predecessors=True)
dist_ts, pred_ts = dijkstra(G, directed=False, indices=ts_n, return_predecessors=True)
back_km = float(dist_ts[depot_n] / 1000.0)  # TS -> depot
print(f"TS->depot back_km {back_km:.2f}", flush=True)

def path_from(pred, src, dst):
    # path src..dst using predecessor array of dijkstra(indices=src)
    if not np.isfinite(dist_dep[dst]) and src == depot_n:
        return None
    path = [dst]
    c = dst
    while c != src:
        c = pred[c]
        if c < 0:
            return None
        path.append(c)
    path.reverse()
    return path

def simp_path(nodes, tol=60.0):
    arr = node_xy[np.asarray(nodes)]
    if len(arr) < 2:
        arr = np.vstack([arr, arr])
    ls = LineString(arr).simplify(tol, preserve_topology=False)
    cs = np.asarray(ls.coords)
    lon, lat = towgs.transform(cs[:, 0], cs[:, 1])
    return [[round(float(la), 5), round(float(lo), 5)] for la, lo in zip(lat, lon)]

leg_data = {}
for t in mtrips:
    if len(t["stops"]) < 2:
        continue
    seq = trip_nodes[t["id"]]
    first, last = seq[0], seq[-1]
    p_pre = path_from(pred_dep, depot_n, first)
    p_ts = path_from(pred_ts, ts_n, last)  # TS..last, reverse for last->TS
    if p_pre is None or p_ts is None:
        continue
    pre_km = float(dist_dep[first] / 1000.0)
    toTS_km = float(dist_ts[last] / 1000.0)
    leg_data[str(t["id"])] = {
        "pre": simp_path(p_pre),
        "toTS": simp_path(list(reversed(p_ts))),
        "back_km": round(back_km, 2),
        "pre_km": round(pre_km, 2),
        "toTS_km": round(toTS_km, 2),
    }

s2 = json.dumps(leg_data, separators=(",", ":"))
mb2 = len(s2.encode()) / 1e6
print(f"depot_legs {mb2:.2f} MB, {len(leg_data)} tracks", flush=True)
if mb2 > 8:
    # increase simplify tolerance
    tol2 = 120.0
    while mb2 > 8 and tol2 <= 500:
        for t in mtrips:
            tid = str(t["id"])
            if tid not in leg_data:
                continue
            seq = trip_nodes[t["id"]]
            leg_data[tid]["pre"] = simp_path(path_from(pred_dep, depot_n, seq[0]), tol2)
            leg_data[tid]["toTS"] = simp_path(list(reversed(path_from(pred_ts, ts_n, seq[-1]))), tol2)
        s2 = json.dumps(leg_data, separators=(",", ":"))
        mb2 = len(s2.encode()) / 1e6
        print(f"legs tol={tol2} -> {mb2:.2f} MB", flush=True)
        tol2 *= 1.6
open(OUT_LEGS, "w", encoding="utf-8").write(s2)

# ---- Step 3: dump-leg hypothesis on unsplit identifiers
def hour(t):
    try:
        return int(t.split(":")[0]) + int(t.split(":")[1]) / 60.0
    except Exception:
        return np.nan

# distance last stop -> depot directly (for no-dump model)
rows = []
for t in mtrips:
    if t.get("n_parts", 1) != 1:
        continue
    if t.get("n_bins", 0) < 5:
        continue
    km_rec = t.get("km_rec") or 0
    if km_rec <= 0:
        continue
    tid = str(t["id"])
    if tid not in leg_data:
        continue
    seq = trip_nodes[t["id"]]
    bin_km = trip_geo[t["id"]][0]
    pre_km = float(dist_dep[seq[0]] / 1000.0)
    toTS_km = float(dist_ts[seq[-1]] / 1000.0)
    last_dep_km = float(dist_dep[seq[-1]] / 1000.0)
    model_dump = bin_km + pre_km + toTS_km + back_km
    model_nodump = bin_km + pre_km + last_dep_km
    rows.append({
        "id": tid,
        "km_rec": float(km_rec),
        "bin_km": bin_km,
        "pre_km": pre_km,
        "toTS_km": toTS_km,
        "model_dump": model_dump,
        "model_nodump": model_nodump,
        "start_h": hour(t.get("start", "")),
        "n_bins": t.get("n_bins", 0),
    })

import math
def stats_for(rws, key):
    if not rws:
        return {"n": 0}
    km = np.array([r["km_rec"] for r in rws])
    mod = np.array([r[key] for r in rws])
    ratio = km / mod
    ape = np.abs(km - mod) / km * 100.0
    return {
        "n": int(len(rws)),
        "ratio_median": round(float(np.median(ratio)), 3),
        "ratio_p25": round(float(np.percentile(ratio, 25)), 3),
        "ratio_p75": round(float(np.percentile(ratio, 75)), 3),
        "ratio_mean": round(float(ratio.mean()), 3),
        "median_abs_pct_err": round(float(np.median(ape)), 1),
        "share_within_30pct": round(float(np.mean(np.abs(ratio - 1) <= 0.3)), 3),
    }

all_rows = rows
morning = [r for r in rows if not math.isnan(r["start_h"]) and r["start_h"] < 10]
afternoon = [r for r in rows if not math.isnan(r["start_h"]) and r["start_h"] >= 10]

# surplus vs distance-to-TS: surplus = km_rec - model_nodump; dist proxy = toTS_km + back_km - (last->depot direct)
from scipy.stats import pearsonr, spearmanr
surplus = np.array([r["km_rec"] - r["model_nodump"] for r in rows])
dump_extra = np.array([r["toTS_km"] + back_km for r in rows])
dist_ts_arr = np.array([r["toTS_km"] for r in rows])
if len(rows) > 2:
    pr = pearsonr(surplus, dist_ts_arr)
    sr = spearmanr(surplus, dist_ts_arr)
    corr = {"pearson_r": round(float(pr[0]), 3), "pearson_p": float(pr[1]),
            "spearman_r": round(float(sr[0]), 3), "spearman_p": float(sr[1])}
else:
    corr = {}

with_dump = stats_for(all_rows, "model_dump")
no_dump = stats_for(all_rows, "model_nodump")

analysis = {
    "selection": "n_parts==1 & n_bins>=5 & km_rec>0 & routed",
    "n_tracks": len(rows),
    "depot_snap_m": round(depot_snap, 1),
    "ts_snap_m": round(ts_snap, 1),
    "back_km_TS_to_depot": round(back_km, 2),
    "with_dump_leg": with_dump,
    "without_dump_leg": no_dump,
    "morning_with_dump": stats_for(morning, "model_dump"),
    "morning_without_dump": stats_for(morning, "model_nodump"),
    "afternoon_with_dump": stats_for(afternoon, "model_dump"),
    "afternoon_without_dump": stats_for(afternoon, "model_nodump"),
    "surplus_vs_distTS_corr": corr,
    "median_surplus_km": round(float(np.median(surplus)), 1) if len(rows) else None,
    "median_dump_extra_km": round(float(np.median(dump_extra)), 1) if len(rows) else None,
}

# verdict
v_with = with_dump.get("median_abs_pct_err", 999)
v_no = no_dump.get("median_abs_pct_err", 999)
r_with = with_dump.get("ratio_median", 0)
r_no = no_dump.get("ratio_median", 0)
share = with_dump.get("share_within_30pct", 0)
if v_with < v_no and abs(r_with - 1) < abs(r_no - 1):
    verdict = (f"Adding the transfer-station dump leg moves the median odometer/model ratio from {r_no} to {r_with} "
               f"and cuts the median absolute error from {v_no}% to {v_with}%, with {int(share*100)}% of unsplit runs within +/-30%. "
               f"Runs are consistent with closing at the Valorsul transfer station before returning to the depot; a single dump facility explains most of the recorded km surplus.")
else:
    verdict = (f"The dump leg does not clearly improve the fit (median ratio {r_no} without vs {r_with} with; "
               f"median abs error {v_no}% vs {v_with}%). The recorded km are not well explained by a single transfer-station closure.")
analysis["verdict"] = verdict

json.dump(analysis, open(OUT_ANAL, "w", encoding="utf-8"), indent=1)

stats = {
    "tracks_routed": len(mtrips),
    "fallback_legs": fallback_legs,
    "routed_tol_m": routed_tol,
    "routed_MB": round(routed_mb, 2),
    "legs_tracks": len(leg_data),
    "legs_MB": round(mb2, 2),
    "hyp_n": len(rows),
    "runtime_s": round(time.time() - t0),
}
print("STATS:", json.dumps(stats), flush=True)
print("VERDICT:", verdict, flush=True)
