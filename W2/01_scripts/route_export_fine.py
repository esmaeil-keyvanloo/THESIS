"""Re-export v5 routes + depot/TS legs at fine tolerance (8 m) as encoded polylines."""
import json, time
import numpy as np
import geopandas as gpd
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra, connected_components
from shapely.geometry import LineString
from pyproj import Transformer

ROOT = r"C:/Users/esmae/Desktop/phd Esmaeil/THESIS CLAUDE"
TOL = 8.0
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
print(f"graph {N} nodes {time.time()-t0:.0f}s", flush=True)

trips = json.load(open(ROOT + "/W2/02_data_work/trips_v5.json", encoding="utf-8"))
mtrips = [t for t in trips if len(t["stops"]) >= 2]
coords = {}
for t in mtrips:
    for s in t["stops"]: coords[(s[0], s[1])] = None
keys = list(coords)
xs, ys = to3763.transform(np.array([k[1] for k in keys]), np.array([k[0] for k in keys]))
d, i = tree.query(np.column_stack([xs, ys]))
for k, ii in zip(keys, i): coords[k] = int(main_idx[ii])

trip_nodes, pairs = {}, set()
for t in mtrips:
    seq = []
    for s in t["stops"]:
        n = coords[(s[0], s[1])]
        if not seq or seq[-1] != n: seq.append(n)
    trip_nodes[t["id"]] = seq
    pairs.update(zip(seq[:-1], seq[1:]))

nd_depot, nd_ts = snap(*DEPOT), snap(*TS)
by_src = {}
for a, b in pairs: by_src.setdefault(a, set()).add(b)
# depot/TS legs: all first/last nodes
firsts = {trip_nodes[t["id"]][0] for t in mtrips}
lasts = {trip_nodes[t["id"]][-1] for t in mtrips}
by_src.setdefault(nd_depot, set()).update(firsts | {nd_ts})
by_src.setdefault(nd_ts, set()).update(lasts)

legs = {}
for ci, a in enumerate(sorted(by_src)):
    dist, pred = dijkstra(G, directed=False, indices=a, return_predecessors=True)
    for b in by_src[a]:
        if not np.isfinite(dist[b]): legs[(a, b)] = None; continue
        path = [b]; c = b
        while c != a: c = pred[c]; path.append(c)
        legs[(a, b)] = (path[::-1], float(dist[b]))
print(f"dijkstra done {time.time()-t0:.0f}s", flush=True)

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

def path_to_enc(nodeseq):
    arr = node_xy[np.asarray(nodeseq)]
    if len(arr) < 2: arr = np.vstack([arr, arr])
    ls = LineString(arr).simplify(TOL, preserve_topology=False)
    cs = np.asarray(ls.coords)
    lon, lat = towgs.transform(cs[:, 0], cs[:, 1])
    return encode(zip(lat, lon))

routes, legsout = {}, {}
back_km = round(legs[(nd_depot, nd_ts)][1] / 1000, 2) if legs.get((nd_depot, nd_ts)) else None
for t in mtrips:
    seq = trip_nodes[t["id"]]
    full, km = [seq[0]], 0.0
    for a, b in zip(seq[:-1], seq[1:]):
        lg = legs.get((a, b))
        if lg: full.extend(lg[0][1:]); km += lg[1]
        else: full.append(b)
    routes[str(t["id"])] = {"km": round(km / 1000, 1), "p": path_to_enc(full)}
    lp = legs.get((nd_depot, seq[0])); lt = legs.get((nd_ts, seq[-1]))
    legsout[str(t["id"])] = {
        "pre": path_to_enc(lp[0]) if lp else None, "pre_km": round(lp[1] / 1000, 2) if lp else None,
        "toTS": path_to_enc(lt[0][::-1]) if lt else None, "toTS_km": round(lt[1] / 1000, 2) if lt else None,
        "back_km": back_km,
    }

s1 = json.dumps(routes, separators=(",", ":"))
s2 = json.dumps(legsout, separators=(",", ":"))
open(ROOT + "/W2/02_data_work/trips_routed_v5_fine.json", "w", encoding="utf-8").write(s1)
open(ROOT + "/W2/02_data_work/depot_legs_v5_fine.json", "w", encoding="utf-8").write(s2)
print("routes MB", round(len(s1.encode())/1e6, 1), "legs MB", round(len(s2.encode())/1e6, 1),
      "tracks", len(routes), f"{time.time()-t0:.0f}s")
