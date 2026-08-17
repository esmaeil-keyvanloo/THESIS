# Task B: road-following routes for multi-bin trips
import json, sys, time
import numpy as np
import geopandas as gpd
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra, connected_components
from shapely.geometry import LineString
from pyproj import Transformer

ROOT = r"C:/Users/esmae/Desktop/phd Esmaeil/THESIS CLAUDE"
ROADS = ROOT + "/GIS_DATA/01_osm/riomaior_10km/osm_roads_riomaior10km.gpkg"
TRIPS = ROOT + "/W2/02_data_work/trips_v3.json"
OUT = ROOT + "/W2/02_data_work/trips_routed_v3.json"

t0 = time.time()
BAN = {"path", "footway", "steps", "cycleway", "bridleway", "pedestrian"}

roads = gpd.read_file(ROADS)
print("roads rows:", len(roads), "crs:", roads.crs, flush=True)
if "fclass" in roads.columns:
    roads = roads[~roads["fclass"].isin(BAN)]
print("after fclass filter:", len(roads), flush=True)

# ---- build graph: nodes = polyline vertices (rounded 1 m), edges = vertex segments
node_ids = {}
node_xy = []
edges_u = []
edges_v = []
edges_w = []

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
print(f"graph: {N} nodes, {len(w)} edges, {time.time()-t0:.0f}s", flush=True)

ncomp, labels = connected_components(G, directed=False)
main = np.argmax(np.bincount(labels))
main_idx = np.where(labels == main)[0]
print(f"components: {ncomp}, largest: {len(main_idx)}", flush=True)

tree = cKDTree(node_xy[main_idx])

# ---- trips
trips = json.load(open(TRIPS, encoding="utf-8"))
mtrips = [t for t in trips if t.get("n_bins", 0) >= 2]
print("multi-bin trips:", len(mtrips), flush=True)

to3763 = Transformer.from_crs(4326, 3763, always_xy=True)
towgs = Transformer.from_crs(3763, 4326, always_xy=True)

# unique bin coords (lat, lon)
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

# trip node sequences (dedupe consecutive equal nodes)
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

# group targets by source
by_src = {}
for a, b in pairs:
    by_src.setdefault(a, set()).add(b)
print("unique sources:", len(by_src), flush=True)

# dijkstra per source, reconstruct needed legs
legs = {}       # (a,b) -> list of node ids (a..b) or None if unreachable
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
    if (ci + 1) % 100 == 0:
        print(f"  dijkstra {ci+1}/{len(srcs)} {time.time()-t0:.0f}s", flush=True)
print(f"dijkstra done {time.time()-t0:.0f}s", flush=True)

# ---- assemble per-trip paths
fallback_legs = 0
trip_geo = {}   # id -> (routed_km, np.array coords 3763)
for t in mtrips:
    seq = trip_nodes[t["id"]]
    nodes_path = [seq[0]]
    fb_mask = []  # parallel structure not needed; build coord list directly
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

# ---- simplify + serialize, adaptive tolerance to stay under ~11.5 MB
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

open(OUT, "w", encoding="utf-8").write(s)

routed = np.array([trip_geo[t["id"]][0] for t in mtrips])
straight = np.array([t.get("km_line", 0) or 0 for t in mtrips])
stats = {
    "trips_routed": len(mtrips),
    "fallback_legs": fallback_legs,
    "median_routed_km": round(float(np.median(routed)), 1),
    "median_straight_km": round(float(np.median(straight)), 1),
    "tolerance_m": tol,
    "file_MB": round(mb, 2),
    "snap_median_m": round(float(np.median(d)), 1),
    "snap_max_m": round(float(d.max()), 1),
    "runtime_s": round(time.time() - t0),
}
print("STATS:", json.dumps(stats), flush=True)
