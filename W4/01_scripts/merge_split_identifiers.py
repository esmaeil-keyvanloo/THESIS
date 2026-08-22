"""W4 TASK A1 (T1) - Merge pass on split identifiers with per-junction legality flags.

For each of the 1,147 split identifiers (parts a/b/c... in trips_v5.json):
  merged chain = base stamped stops time-ordered (trips_v5_base.json).
  Link i->i+1 feasible if fastest road time <= max(gap - service, 0.5 min).
  Two fclass speed graphs:
    TRUCK-LEGAL: motorway 90, trunk/primary/secondary 80, tertiary 70,
                 links 50-60, default 50; per-stop service 1.0 min.
    CEILING:     motorway 130, trunk/primary 100, secondary 90, tertiary 80,
                 default 60; per-stop service 0.5 min.
  Verdicts:
    MERGE        all links feasible under CEILING (ratio <= 1.0)
    batch-entry  not mergeable AND any link gap <= 1 min with straight-line > 2 km
    multi-vehicle otherwise (stays split)
  Merged tracks carry speed_flags = [[i, req_min_legal, gap_min], ...] for each
  junction infeasible under TRUCK-LEGAL but ok under CEILING (i indexes the
  earlier stamped stop in the OUTPUT stops array).

Outputs:
  W4/02_data_work/tracks_v6.json   (all tracks; merged ids collapsed to one)
  W4/02_data_work/merge_report.json
"""
import json, math, time
from collections import defaultdict
from datetime import datetime, timedelta

import numpy as np
import geopandas as gpd
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra, connected_components
from pyproj import Transformer

ROOT = r"C:/Users/esmae/Desktop/phd Esmaeil/THESIS CLAUDE"
V5 = f"{ROOT}/W2/02_data_work/trips_v5.json"
VBASE = f"{ROOT}/W2/02_data_work/trips_v5_base.json"
ROADS = f"{ROOT}/GIS_DATA/01_osm/riomaior_10km/osm_roads_riomaior10km.gpkg"
OUT_TRACKS = f"{ROOT}/W4/02_data_work/tracks_v6.json"
OUT_REPORT = f"{ROOT}/W4/02_data_work/merge_report.json"

BAN = {"path", "footway", "steps", "cycleway", "bridleway", "pedestrian"}
MIN_BUDGET_MIN = 0.5          # floor on (gap - service)
SERVICE_LEGAL = 1.0           # min per stop, TRUCK-LEGAL
SERVICE_CEIL = 0.5            # min per stop, CEILING
BATCH_GAP_MIN = 1.0           # batch-entry: gap <= 1 min ...
BATCH_KM = 2.0                # ... and straight-line > 2 km

SPEED_LEGAL = {"motorway": 90, "trunk": 80, "primary": 80, "secondary": 80,
               "tertiary": 70, "motorway_link": 60, "trunk_link": 60,
               "primary_link": 55, "secondary_link": 55, "tertiary_link": 50}
DEF_LEGAL = 50
SPEED_CEIL = {"motorway": 130, "trunk": 100, "primary": 100, "secondary": 90,
              "tertiary": 80}
DEF_CEIL = 60

R_EARTH = 6371.0088
def hav_km(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    h = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R_EARTH * math.asin(math.sqrt(h))

t0 = time.time()

# ---------------- 1. road graph, two time weightings (minutes) ----------------
roads = gpd.read_file(ROADS)
roads = roads[~roads["fclass"].isin(BAN)]
node_ids, node_xy = {}, []
eu, ev, wl, wc = [], [], [], []
def nid(x, y):
    k = (round(x), round(y))
    i = node_ids.get(k)
    if i is None:
        i = len(node_xy); node_ids[k] = i; node_xy.append((x, y))
    return i
for fclass, geom in zip(roads["fclass"], roads.geometry):
    if geom is None:
        continue
    v_l = SPEED_LEGAL.get(fclass, DEF_LEGAL)
    v_c = SPEED_CEIL.get(fclass, DEF_CEIL)
    for ls in (geom.geoms if geom.geom_type == "MultiLineString" else [geom]):
        cs = np.asarray(ls.coords)
        ids = [nid(x, y) for x, y in cs[:, :2]]
        seg_m = np.hypot(np.diff(cs[:, 0]), np.diff(cs[:, 1]))
        for a, b, m in zip(ids[:-1], ids[1:], seg_m):
            if a != b:
                eu.append(a); ev.append(b)
                wl.append(m / 1000.0 / v_l * 60.0)
                wc.append(m / 1000.0 / v_c * 60.0)
N = len(node_xy); node_xy = np.asarray(node_xy)
u, v = np.asarray(eu), np.asarray(ev)
G_L = coo_matrix((np.r_[wl, wl], (np.r_[u, v], np.r_[v, u])), shape=(N, N)).tocsr()
G_C = coo_matrix((np.r_[wc, wc], (np.r_[u, v], np.r_[v, u])), shape=(N, N)).tocsr()
ncomp, labels = connected_components(G_L, directed=False)
main_idx = np.where(labels == np.argmax(np.bincount(labels)))[0]
tree = cKDTree(node_xy[main_idx])
to3763 = Transformer.from_crs(4326, 3763, always_xy=True)
print(f"graph {N} nodes, main comp {len(main_idx)}, {time.time()-t0:.0f}s", flush=True)

# ---------------- 2. load tracks, group splits ----------------
v5 = json.load(open(V5, encoding="utf-8"))
base = {t["id"]: t for t in json.load(open(VBASE, encoding="utf-8"))}
split_parts = defaultdict(list)   # base_id -> [v5 part tracks] in file order
for t in v5:
    if t.get("part"):
        split_parts[str(t["base_id"])].append(t)
split_ids = sorted(split_parts)
print("split identifiers:", len(split_ids))

def stop_datetimes(date_str, stops):
    """Absolute datetimes with midnight-wrap (same logic as assign_loose_readings_v5)."""
    d0 = datetime.strptime(date_str, "%Y-%m-%d")
    out, prev, day_off = [], None, timedelta(0)
    for s in stops:
        cur = d0 + day_off + timedelta(hours=int(s[3][:2]), minutes=int(s[3][3:]))
        if prev is not None:
            while cur < prev - timedelta(hours=12):
                cur += timedelta(days=1)
                day_off += timedelta(days=1)
        out.append(cur)
        prev = cur if prev is None else max(prev, cur)
    return out

# ---------------- 3. snap base stops of split ids ----------------
coords = {}
for b in split_ids:
    for s in base[b]["stops"]:
        coords[(s[0], s[1])] = None
keys = list(coords)
xs, ys = to3763.transform(np.array([k[1] for k in keys]), np.array([k[0] for k in keys]))
_, ii = tree.query(np.column_stack([xs, ys]))
for k, j in zip(keys, ii):
    coords[k] = int(main_idx[j])
print("unique stop coords:", len(keys), flush=True)

# needed source->target node pairs
pairs = set()
for b in split_ids:
    st = base[b]["stops"]
    for a, c in zip(st[:-1], st[1:]):
        na, nc = coords[(a[0], a[1])], coords[(c[0], c[1])]
        if na != nc:
            pairs.add((na, nc))
by_src = defaultdict(set)
for a, c in pairs:
    by_src[a].add(c)
print("unique sources:", len(by_src), "pairs:", len(pairs), flush=True)

# ---------------- 4. shortest times (minutes), chunked multi-source ----------------
time_legal, time_ceil = {}, {}
srcs = sorted(by_src)
CH = 128
for k0 in range(0, len(srcs), CH):
    chunk = srcs[k0:k0 + CH]
    dl = dijkstra(G_L, directed=False, indices=chunk)
    dc = dijkstra(G_C, directed=False, indices=chunk)
    for r, a in enumerate(chunk):
        for b in by_src[a]:
            time_legal[(a, b)] = float(dl[r, b])
            time_ceil[(a, b)] = float(dc[r, b])
    if (k0 // CH) % 10 == 0:
        print(f"dijkstra {k0+len(chunk)}/{len(srcs)} {time.time()-t0:.0f}s", flush=True)
print(f"dijkstra done {time.time()-t0:.0f}s", flush=True)

# ---------------- 5. verdicts ----------------
def link_eval(bid):
    """Yield per-link dicts for the base stamped chain of identifier bid."""
    st = base[bid]["stops"]
    dts = stop_datetimes(base[bid]["date"], st)
    for i in range(len(st) - 1):
        a, c = st[i], st[i + 1]
        na, nc = coords[(a[0], a[1])], coords[(c[0], c[1])]
        gap = (dts[i + 1] - dts[i]).total_seconds() / 60.0
        tl = 0.0 if na == nc else time_legal[(na, nc)]
        tc = 0.0 if na == nc else time_ceil[(na, nc)]
        bud_l = max(gap - SERVICE_LEGAL, MIN_BUDGET_MIN)
        bud_c = max(gap - SERVICE_CEIL, MIN_BUDGET_MIN)
        yield dict(i=i, gap=gap, straight=hav_km(a[0], a[1], c[0], c[1]),
                   tl=tl, tc=tc,
                   ok_l=(math.isfinite(tl) and tl <= bud_l),
                   ok_c=(math.isfinite(tc) and tc <= bud_c))

verdict = {}          # base_id -> 'merge' | 'batch-entry' | 'multi-vehicle'
flags_by_id = {}      # base_id -> [(base_chain_i, req_min_legal, gap_min), ...]
for b in split_ids:
    links = list(link_eval(b))
    if all(l["ok_c"] for l in links):
        verdict[b] = "merge"
        flags_by_id[b] = [(l["i"], round(l["tl"], 2), round(l["gap"], 1))
                          for l in links if not l["ok_l"]]
    elif any(l["gap"] <= BATCH_GAP_MIN and l["straight"] > BATCH_KM for l in links):
        verdict[b] = "batch-entry"
    else:
        verdict[b] = "multi-vehicle"

from collections import Counter
vc = Counter(verdict.values())
print("verdicts:", dict(vc), flush=True)

# ---------------- 6. build tracks_v6 ----------------
def build_merged(bid):
    """One merged track: parts' stops (S + I) merged by absolute datetime."""
    parts = split_parts[bid]
    allstops = []
    for pi, p in enumerate(parts):
        dts = stop_datetimes(p["date"], p["stops"])
        for dt, s in zip(dts, p["stops"]):
            allstops.append((dt, pi, s))
    allstops.sort(key=lambda x: (x[0], x[1]))
    stops = [s for _, _, s in allstops]
    dts = [dt for dt, _, _ in allstops]
    n_bins = sum(1 for s in stops if s[4] == "S")
    n_inferred = sum(1 for s in stops if s[4] == "I")
    km_line = sum(hav_km(stops[i][0], stops[i][1], stops[i+1][0], stops[i+1][1])
                  for i in range(len(stops) - 1))
    bt = base[bid]
    # map base-chain junction index -> index of that stamped stop in output stops
    s_pos = [i for i, s in enumerate(stops) if s[4] == "S"]
    speed_flags = [[s_pos[i], req, gap] for i, req, gap in flags_by_id[bid]]
    return {
        "id": bid, "date": bt["date"],
        "start": dts[0].strftime("%H:%M"), "end": dts[-1].strftime("%H:%M"),
        "dur_h": round((dts[-1] - dts[0]).total_seconds() / 3600.0, 2),
        "rota": bt["rota"], "frac": bt["frac"],
        "n_bins": n_bins, "km_rec": bt["km_rec"], "kg": bt["kg"],
        "km_line": round(km_line, 1) if len(stops) > 1 else 0,
        "stops": stops, "base_id": bid, "part": "", "n_parts": 1,
        "n_inferred": n_inferred, "merged": True, "speed_flags": speed_flags,
    }

out = []
done_merged = set()
for t in v5:
    if t.get("part"):
        b = str(t["base_id"])
        if verdict[b] == "merge":
            if b not in done_merged:
                out.append(build_merged(b))
                done_merged.add(b)
        else:
            nt = dict(t)
            nt["merged"] = False
            nt["speed_flags"] = []
            nt["verdict"] = verdict[b]
            out.append(nt)
    else:
        nt = dict(t)
        nt["merged"] = False
        out.append(nt)

with open(OUT_TRACKS, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
print("tracks_v6:", len(out), flush=True)

# ---------------- 7. report ----------------
flagged_total = sum(len(flags_by_id[b]) for b in flags_by_id if verdict[b] == "merge")
parts_removed = sum(len(split_parts[b]) - 1 for b in done_merged)
report = {
    "split_identifiers": len(split_ids),
    "verdict_counts": {"merge": vc.get("merge", 0),
                       "batch-entry": vc.get("batch-entry", 0),
                       "multi-vehicle": vc.get("multi-vehicle", 0)},
    "flagged_junctions_total": flagged_total,
    "merged_tracks_with_flags": sum(1 for b in done_merged if flags_by_id[b]),
    "tracks_before": len(v5),
    "tracks_after": len(out),
    "parts_collapsed": parts_removed,
    "params": {
        "speeds_truck_legal_kmh": {**SPEED_LEGAL, "default": DEF_LEGAL},
        "speeds_ceiling_kmh": {**SPEED_CEIL, "default": DEF_CEIL},
        "service_min": {"truck_legal": SERVICE_LEGAL, "ceiling": SERVICE_CEIL},
        "min_budget_min": MIN_BUDGET_MIN,
        "feasible_rule": "fastest road time <= max(gap - service, 0.5 min)",
        "batch_entry_rule": "any link gap <= 1 min AND straight-line > 2 km",
        "merged_chain": "base stamped stops time-ordered (trips_v5_base.json)",
        "speed_flags": "junction infeasible under TRUCK-LEGAL, feasible under CEILING; i = index of earlier stamped stop in output stops",
        "banned_fclass": sorted(BAN),
    },
}
with open(OUT_REPORT, "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
print(json.dumps(report["verdict_counts"]))
print("flagged junctions:", flagged_total, "tracks", len(v5), "->", len(out),
      f"{time.time()-t0:.0f}s")
