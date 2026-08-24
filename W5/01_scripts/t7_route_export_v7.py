"""T7: export v7 trip + phantom routes as encoded polylines (3 m tolerance).

Adapted from W2/01_scripts/route_export_fine.py.
Inputs : W5/02_data_work/trips_v7.json, phantom_tracks_v7.json (tracks >=2 stops)
Graph  : GIS_DATA OSM roads (drivable only), EPSG:3763
Outputs: W5/02_data_work/trips_routed_v7.json  {routes:{id:{km,p,anchors}}, flags:{id:[{i,p,req,gap}]}}
         W5/02_data_work/depot_legs_v7.json    {trip_id:{pre,pre_km,toTS,toTS_km,back_km}} (trips only)
         W5/02_data_work/unroutable.json       list of unreachable legs (expect empty)
No straight-lining: unreachable legs are skipped and listed; a trip loses its
route only when zero legs are reachable. Anchors give, per stop, the vertex
index in the decoded polyline so the UI can interpolate the vehicle by time.
"""
import json, time
import numpy as np
import geopandas as gpd
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra, connected_components
from shapely.geometry import LineString
from pyproj import Transformer

ROOT = r"C:/Users/esmae/Desktop/phd Esmaeil/THESIS CLAUDE"
OUT = ROOT + "/W5/02_data_work"
TOL_START = 3.0
MAX_MB = 16.0
DEPOT = (39.33921, -8.92493)
TS = (39.31963, -8.92405)

t0 = time.time()
BAN = {"path", "footway", "steps", "cycleway", "bridleway", "pedestrian"}
roads = gpd.read_file(ROOT + "/GIS_DATA/01_osm/riomaior_10km/osm_roads_riomaior10km.gpkg")
roads = roads[~roads["fclass"].isin(BAN)]

node_ids, node_xy, eu, ev, ew = {}, [], [], [], []
def nid(x, y):
    k = (round(x), round(y))
    i = node_ids.get(k)
    if i is None:
        i = len(node_xy); node_ids[k] = i; node_xy.append((x, y))
    return i
for geom in roads.geometry:
    if geom is None: continue
    for ls in (geom.geoms if geom.geom_type == "MultiLineString" else [geom]):
        cs = np.asarray(ls.coords)
        ids = [nid(x, y) for x, y in cs[:, :2]]
        seg = np.hypot(np.diff(cs[:, 0]), np.diff(cs[:, 1]))
        for a, b, w in zip(ids[:-1], ids[1:], seg):
            if a != b: eu.append(a); ev.append(b); ew.append(w)
N = len(node_xy); node_xy = np.asarray(node_xy)
u, v, w = map(np.asarray, (eu, ev, ew))
G = coo_matrix((np.r_[w, w], (np.r_[u, v], np.r_[v, u])), shape=(N, N)).tocsr()
ncomp, labels = connected_components(G, directed=False)
main_idx = np.where(labels == np.argmax(np.bincount(labels)))[0]
tree = cKDTree(node_xy[main_idx])
to3763 = Transformer.from_crs(4326, 3763, always_xy=True)
towgs = Transformer.from_crs(3763, 4326, always_xy=True)
def snap(lat, lon):
    x, y = to3763.transform(lon, lat)
    _, i = tree.query([x, y]); return int(main_idx[i])
print(f"graph {N} nodes, main comp {len(main_idx)} {time.time()-t0:.0f}s", flush=True)

trips = json.load(open(OUT + "/trips_v7.json", encoding="utf-8"))
phantoms = json.load(open(OUT + "/phantom_tracks_v7.json", encoding="utf-8"))
mtrips = [t for t in trips if len(t["stops"]) >= 2]
mphant = [p for p in phantoms if len(p["stops"]) >= 2]
tracks = [(t, True) for t in mtrips] + [(p, False) for p in mphant]
print(f"routable tracks: {len(mtrips)} trips + {len(mphant)} phantoms", flush=True)

# snap all stop coords (batch)
coords = {}
for t, _ in tracks:
    for s in t["stops"]: coords[(s[0], s[1])] = None
keys = list(coords)
xs, ys = to3763.transform(np.array([k[1] for k in keys]), np.array([k[0] for k in keys]))
_, i = tree.query(np.column_stack([xs, ys]))
for k, ii in zip(keys, i): coords[k] = int(main_idx[ii])

# per-track node sequence, one node per stop (no dedup: anchors are per stop)
track_nodes, pairs = {}, set()
for t, _ in tracks:
    seq = [coords[(s[0], s[1])] for s in t["stops"]]
    track_nodes[str(t["id"])] = seq
    pairs.update((a, b) for a, b in zip(seq[:-1], seq[1:]) if a != b)

nd_depot, nd_ts = snap(*DEPOT), snap(*TS)
by_src = {}
for a, b in pairs: by_src.setdefault(a, set()).add(b)
# depot/TS legs for trips only (not phantoms)
firsts = {track_nodes[str(t["id"])][0] for t in mtrips}
lasts = {track_nodes[str(t["id"])][-1] for t in mtrips}
by_src.setdefault(nd_depot, set()).update(firsts | {nd_ts})
by_src.setdefault(nd_ts, set()).update(lasts)

legs = {}
for a in sorted(by_src):
    dist, pred = dijkstra(G, directed=False, indices=a, return_predecessors=True)
    for b in by_src[a]:
        if not np.isfinite(dist[b]): legs[(a, b)] = None; continue
        path = [b]; c = b
        while c != a: c = pred[c]; path.append(c)
        legs[(a, b)] = (path[::-1], float(dist[b]))
n_unreach_pairs = sum(1 for v_ in legs.values() if v_ is None)
print(f"dijkstra done: {len(by_src)} sources, {len(legs)} legs, "
      f"{n_unreach_pairs} unreachable {time.time()-t0:.0f}s", flush=True)

def encode(latlons):
    out = []; pl, po = 0, 0
    for la, lo in latlons:
        ila, ilo = round(la * 1e5), round(lo * 1e5)
        for vcur, vprev in ((ila, pl), (ilo, po)):
            dv = vcur - vprev; dv = ~(dv << 1) if dv < 0 else dv << 1
            while dv >= 0x20:
                out.append(chr((0x20 | (dv & 0x1f)) + 63)); dv >>= 5
            out.append(chr(dv + 63))
        pl, po = ila, ilo
    return "".join(out)

def simp_coords(nodeseq, tol):
    """Simplified EPSG:3763 coords of a node path; endpoints always kept."""
    arr = node_xy[np.asarray(nodeseq)]
    if len(arr) < 2: return arr
    ls = LineString(arr).simplify(tol, preserve_topology=False)
    return np.asarray(ls.coords)

def enc3763(arr):
    if len(arr) < 2: arr = np.vstack([arr, arr])
    lon, lat = towgs.transform(arr[:, 0], arr[:, 1])
    return encode(zip(lat, lon))

def build(tol):
    # per-pair simplified coords cache at this tolerance
    simp = {k: (simp_coords(v_[0], tol) if v_ else None) for k, v_ in legs.items()}
    routes, flagsout, legsout, unroutable = {}, {}, {}, []
    lg_bk = legs.get((nd_depot, nd_ts))
    back_km = round(lg_bk[1] / 1000, 2) if lg_bk else None
    for t, is_trip in tracks:
        tid = str(t["id"])
        seq = track_nodes[tid]
        pts = [node_xy[seq[0]]]          # list of coord rows (3763)
        anchors = [0]
        km = 0.0
        n_ok = 0; n_legs = 0
        for li, (a, b) in enumerate(zip(seq[:-1], seq[1:])):
            if a == b:                    # same snapped node: zero-length leg
                anchors.append(len(pts) - 1)
                continue
            n_legs += 1
            lg = legs.get((a, b))
            if lg is None:
                unroutable.append({"id": tid, "leg": li,
                                   "from": t["stops"][li][2], "to": t["stops"][li + 1][2]})
                anchors.append(len(pts) - 1)
                continue
            n_ok += 1
            cs = simp[(a, b)]
            pts.extend(cs[1:])
            anchors.append(len(pts) - 1)
            km += lg[1]
        if n_legs > 0 and n_ok == 0:
            continue                      # zero legs reachable: route absent
        arr = np.asarray(pts)
        routes[tid] = {"km": round(km / 1000, 2), "p": enc3763(arr), "anchors": anchors}
        # speed-flag junction sub-paths (merged trips)
        fl = t.get("speed_flags") or []
        if fl:
            recs = []
            for i_, req, gap in fl:
                a, b = seq[i_], seq[i_ + 1]
                p_enc = None
                if a != b and legs.get((a, b)):
                    p_enc = enc3763(simp[(a, b)])
                recs.append({"i": i_, "p": p_enc, "req": req, "gap": gap})
            flagsout[tid] = recs
        if is_trip:
            lp = legs.get((nd_depot, seq[0])); lt = legs.get((nd_ts, seq[-1]))
            legsout[tid] = {
                "pre": enc3763(simp[(nd_depot, seq[0])]) if lp else None,
                "pre_km": round(lp[1] / 1000, 2) if lp else None,
                "toTS": enc3763(simp[(nd_ts, seq[-1])][::-1]) if lt else None,
                "toTS_km": round(lt[1] / 1000, 2) if lt else None,
                "back_km": back_km,
            }
    return routes, flagsout, legsout, unroutable

tol = TOL_START
while True:
    routes, flagsout, legsout, unroutable = build(tol)
    s1 = json.dumps({"routes": routes, "flags": flagsout}, separators=(",", ":"))
    mb = len(s1.encode()) / 1e6
    print(f"tol {tol} m -> routes file {mb:.1f} MB", flush=True)
    if mb <= MAX_MB: break
    tol += 1.0

s2 = json.dumps(legsout, separators=(",", ":"))
s3 = json.dumps(unroutable, separators=(",", ":"))
open(OUT + "/trips_routed_v7.json", "w", encoding="utf-8").write(s1)
open(OUT + "/depot_legs_v7.json", "w", encoding="utf-8").write(s2)
open(OUT + "/unroutable.json", "w", encoding="utf-8").write(s3)
print(f"DONE tol={tol}m routes={len(routes)} flagged_trips={len(flagsout)} "
      f"depot_legs={len(legsout)} unroutable={len(unroutable)}")
print(f"sizes MB: routes {len(s1.encode())/1e6:.2f} depot {len(s2.encode())/1e6:.2f} "
      f"unroutable {len(s3.encode())/1e6:.3f}  {time.time()-t0:.0f}s")
