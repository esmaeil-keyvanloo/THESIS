"""W4 TASK C1 - Route + enrich the v6 world (trips_v6 + phantom_tracks).

Steps
  0. Type correction: trips_v6.json carries v5-inferred stops relabeled 'S'
     (T2 rebuild artifact) while the v6 re-assignment re-inserted the same
     readings as I/L.  A stop keeps 'S' only if it consumes a stamped stop
     (cid, HH:MM) from the identifier's chain in trips_v5_base.json; other
     'S' stops are dropped (their readings live on as v6 I/L/phantom stops).
  1. Route every track with >=2 corrected stops (trips + phantoms) on the
     drivable graph (fclass ban list), encoded polylines simplified at 8 m.
     Depot/TS legs for trips only.
  2. Merged tracks' speed_flags junctions: export the TRUCK-LEGAL fastest
     road sub-path per junction, flags:{tid:[{i,p,req,gap}]}; i = index of
     the earlier stamped stop in the ENRICHED stops array.
  3. Enrich all stops to 9 elements [lat,lon,cid,hhmm,type,fill,est_kg,mat,
     sensor]  (enrich_stops + v8 + v9 logic; S = pre-emptying fill, I/L/P =
     reading's own fill; est kg mid-density own material; nearest sensor
     reading +/-3 h, negatives kept as raw error codes).
  4. Trip-level estimates (est_lo/mid/hi strict stamped; est2 = strict +
     same-material observed, capped at identifier kg) -> trips_index_v6.json.

Outputs (W4/02_data_work):
  trips_v6_enriched.json, trips_routed_v6_fine.json ({"routes","flags"}),
  depot_legs_v6_fine.json, trips_index_v6.json
"""
import json, math, time, bisect, statistics
from collections import defaultdict
from datetime import datetime, timedelta

import duckdb
import numpy as np
import geopandas as gpd
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra, connected_components
from shapely.geometry import LineString
from pyproj import Transformer

ROOT = r"C:/Users/esmae/Desktop/phd Esmaeil/THESIS CLAUDE"
W4 = f"{ROOT}/W4/02_data_work"
TOL = 8.0
DEPOT = (39.33921, -8.92493)
TS = (39.31963, -8.92405)
BAN = {"path", "footway", "steps", "cycleway", "bridleway", "pedestrian"}
SPEED_LEGAL = {"motorway": 90, "trunk": 80, "primary": 80, "secondary": 80,
               "tertiary": 70, "motorway_link": 60, "trunk_link": 60,
               "primary_link": 55, "secondary_link": 55, "tertiary_link": 50}
DEF_LEGAL = 50
DENS = {"P": (25, 32, 40), "C": (50, 75, 100), "G": (250, 300, 350)}
DENS_MID = {"P": 32, "C": 75, "G": 300}
FR2L = {"Packaging": "P", "Paper/card": "C", "Glass": "G"}

t0 = time.time()

# ---------------- 0. load worlds, correct stop types ----------------
trips = json.load(open(f"{W4}/trips_v6.json", encoding="utf-8"))
phantoms = json.load(open(f"{W4}/phantom_tracks.json", encoding="utf-8"))
base = {t["id"]: t for t in
        json.load(open(f"{ROOT}/W2/02_data_work/trips_v5_base.json", encoding="utf-8"))}

dropped = kept_s = 0
for t in trips:
    bt = base.get(str(t.get("base_id") or t["id"]))
    avail = defaultdict(int)
    if bt:
        for s in bt["stops"]:
            avail[(str(s[2]), s[3])] += 1
    ns = []
    for s in t["stops"]:
        if s[4] == "S":
            k = (str(s[2]), s[3])
            if avail[k] > 0:
                avail[k] -= 1
                kept_s += 1
                ns.append(s)
            else:
                dropped += 1          # relabeled v5-inferred leftover
        else:
            ns.append(s)
    t["stops"] = ns
    t["n_bins"] = sum(1 for s in ns if s[4] == "S")
print(f"type correction: kept S {kept_s}, dropped relabeled {dropped}", flush=True)

R_EARTH = 6371.0088
def hav_km(a, b, c, d):
    p1, p2 = math.radians(a), math.radians(c)
    dl = math.radians(d - b)
    h = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R_EARTH * math.asin(math.sqrt(h))
for t in trips:
    st = t["stops"]
    t["km_line"] = round(sum(hav_km(*st[i][:2], *st[i + 1][:2])
                             for i in range(len(st) - 1)), 1) if len(st) > 1 else 0

world = trips + phantoms          # phantoms keep their own meta

# per-stop wrapped dates (midnight logic as merge/assign scripts)
def stop_dates(t):
    d0 = datetime.strptime(t["date"], "%Y-%m-%d")
    out, prev, off = [], None, timedelta(0)
    for s in t["stops"]:
        cur = d0 + off + timedelta(hours=int(s[3][:2]), minutes=int(s[3][3:]))
        if prev is not None:
            while cur < prev - timedelta(hours=12):
                cur += timedelta(days=1); off += timedelta(days=1)
        out.append(cur)
        prev = cur if prev is None else max(prev, cur)
    return out
sdates = {str(t["id"]): [d.strftime("%Y-%m-%d") for d in stop_dates(t)] for t in world}

# ---------------- 1. road graph: distance + legal-time weights ----------------
roads = gpd.read_file(f"{ROOT}/GIS_DATA/01_osm/riomaior_10km/osm_roads_riomaior10km.gpkg")
roads = roads[~roads["fclass"].isin(BAN)]
node_ids, node_xy = {}, []
eu, ev, wd, wl = [], [], [], []
def nid(x, y):
    k = (round(x), round(y))
    i = node_ids.get(k)
    if i is None:
        i = len(node_xy); node_ids[k] = i; node_xy.append((x, y))
    return i
for fclass, geom in zip(roads["fclass"], roads.geometry):
    if geom is None: continue
    v_l = SPEED_LEGAL.get(fclass, DEF_LEGAL)
    for ls in (geom.geoms if geom.geom_type == "MultiLineString" else [geom]):
        cs = np.asarray(ls.coords)
        ids = [nid(x, y) for x, y in cs[:, :2]]
        seg = np.hypot(np.diff(cs[:, 0]), np.diff(cs[:, 1]))
        for a, b, m in zip(ids[:-1], ids[1:], seg):
            if a != b:
                eu.append(a); ev.append(b); wd.append(m)
                wl.append(m / 1000.0 / v_l * 60.0)
N = len(node_xy); node_xy = np.asarray(node_xy)
u, v = np.asarray(eu), np.asarray(ev)
G_D = coo_matrix((np.r_[wd, wd], (np.r_[u, v], np.r_[v, u])), shape=(N, N)).tocsr()
G_L = coo_matrix((np.r_[wl, wl], (np.r_[u, v], np.r_[v, u])), shape=(N, N)).tocsr()
ncomp, labels = connected_components(G_D, directed=False)
main_idx = np.where(labels == np.argmax(np.bincount(labels)))[0]
tree = cKDTree(node_xy[main_idx])
to3763 = Transformer.from_crs(4326, 3763, always_xy=True)
towgs = Transformer.from_crs(3763, 4326, always_xy=True)
def snap(lat, lon):
    x, y = to3763.transform(lon, lat)
    _, i = tree.query([x, y]); return int(main_idx[i])
print(f"graph {N} nodes, {time.time()-t0:.0f}s", flush=True)

routable = [t for t in world if len(t["stops"]) >= 2]
coords = {}
for t in routable:
    for s in t["stops"]:
        coords[(s[0], s[1])] = None
keys = list(coords)
xs, ys = to3763.transform(np.array([k[1] for k in keys]), np.array([k[0] for k in keys]))
_, ii = tree.query(np.column_stack([xs, ys]))
for k, j in zip(keys, ii):
    coords[k] = int(main_idx[j])

trip_nodes, pairs = {}, set()
for t in routable:
    seq = []
    for s in t["stops"]:
        n = coords[(s[0], s[1])]
        if not seq or seq[-1] != n: seq.append(n)
    trip_nodes[str(t["id"])] = seq
    pairs.update(zip(seq[:-1], seq[1:]))

nd_depot, nd_ts = snap(*DEPOT), snap(*TS)
real = [t for t in routable if t.get("frac") != "Phantom"]
firsts = {trip_nodes[str(t["id"])][0] for t in real}
lasts = {trip_nodes[str(t["id"])][-1] for t in real}
by_src = defaultdict(set)
for a, b in pairs: by_src[a].add(b)
by_src[nd_depot].update(firsts | {nd_ts})
by_src[nd_ts].update(lasts)
print(f"routable {len(routable)}, sources {len(by_src)}, pairs {len(pairs)}", flush=True)

legs = {}
srcs = sorted(by_src)
CH = 16
for k0 in range(0, len(srcs), CH):
    chunk = srcs[k0:k0 + CH]
    dist, pred = dijkstra(G_D, directed=False, indices=chunk, return_predecessors=True)
    for r, a in enumerate(chunk):
        pr = pred[r]
        for b in by_src[a]:
            if not np.isfinite(dist[r, b]): legs[(a, b)] = None; continue
            path = [b]; c = b
            while c != a: c = pr[c]; path.append(c)
            legs[(a, b)] = (np.asarray(path[::-1], dtype=np.int32), float(dist[r, b]))
    if (k0 // CH) % 20 == 0:
        print(f"dijkstra {k0+len(chunk)}/{len(srcs)} {time.time()-t0:.0f}s", flush=True)
print(f"dijkstra done {time.time()-t0:.0f}s", flush=True)

def encode(latlons):
    out = []; pl, po = 0, 0
    for la, lo in latlons:
        ila, ilo = round(la * 1e5), round(lo * 1e5)
        for vc, vp in ((ila, pl), (ilo, po)):
            dv = vc - vp; dv = ~(dv << 1) if dv < 0 else dv << 1
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
back = legs.get((nd_depot, nd_ts))
back_km = round(back[1] / 1000, 2) if back else None
for t in routable:
    tid = str(t["id"])
    seq = trip_nodes[tid]
    full, km = [seq[0]], 0.0
    for a, b in zip(seq[:-1], seq[1:]):
        lg = legs.get((a, b))
        if lg is not None and not isinstance(lg, tuple):
            lg = None
        if lg: full.extend(lg[0][1:].tolist()); km += lg[1]
        else: full.append(b)
    routes[tid] = {"km": round(km / 1000, 1), "p": path_to_enc(full)}
    if t.get("frac") != "Phantom":
        lp = legs.get((nd_depot, seq[0])); lt = legs.get((nd_ts, seq[-1]))
        legsout[tid] = {
            "pre": path_to_enc(lp[0]) if lp else None,
            "pre_km": round(lp[1] / 1000, 2) if lp else None,
            "toTS": path_to_enc(lt[0][::-1]) if lt else None,
            "toTS_km": round(lt[1] / 1000, 2) if lt else None,
            "back_km": back_km,
        }
print(f"routes built {time.time()-t0:.0f}s", flush=True)

# ---------------- 2. speed_flags junction sub-paths (TRUCK-LEGAL graph) ------
# flag i in trips_v6 indexes tracks_v6 stops (pre-insertion) -> map via stamped
# ordinal to the enriched stops array.
tracks_v6 = {t["id"]: t for t in
             json.load(open(f"{W4}/tracks_v6.json", encoding="utf-8")) if t.get("merged")}
flag_jobs = []          # (tid, ordinal, req, gap, na, nb)
for t in trips:
    if not (t.get("merged") and t.get("speed_flags")): continue
    tid = str(t["id"])
    tv = tracks_v6[t["id"]]["stops"]
    s_pos = [k for k, s in enumerate(t["stops"]) if s[4] == "S"]
    remapped = []
    for i, req, gap in t["speed_flags"]:
        assert tv[i][4] == "S", (tid, i)
        o = sum(1 for s in tv[:i] if s[4] == "S")
        if o + 1 >= len(s_pos):        # junction needs a following stamped stop
            continue
        ia, ib = s_pos[o], s_pos[o + 1]
        na = coords.get((t["stops"][ia][0], t["stops"][ia][1])) or snap(t["stops"][ia][0], t["stops"][ia][1])
        nb = coords.get((t["stops"][ib][0], t["stops"][ib][1])) or snap(t["stops"][ib][0], t["stops"][ib][1])
        flag_jobs.append((tid, ia, req, gap, na, nb))
        remapped.append([ia, req, gap])
    t["speed_flags"] = remapped

flags_out = defaultdict(list)
by_src_f = defaultdict(list)
for job in flag_jobs:
    by_src_f[job[4]].append(job)
for a, jobs in by_src_f.items():
    dist, pred = dijkstra(G_L, directed=False, indices=a, return_predecessors=True)
    for tid, ia, req, gap, _, nb in jobs:
        if not np.isfinite(dist[nb]) or nb == a:
            enc = path_to_enc([a, nb])
        else:
            path = [nb]; c = nb
            while c != a: c = pred[c]; path.append(c)
            enc = path_to_enc(path[::-1])
        flags_out[tid].append({"i": ia, "p": enc, "req": req, "gap": gap})
n_flag_paths = sum(len(v) for v in flags_out.values())
print(f"flag sub-paths {n_flag_paths} on {len(flags_out)} tracks", flush=True)

s1 = json.dumps({"routes": routes, "flags": flags_out}, separators=(",", ":"))
s2 = json.dumps(legsout, separators=(",", ":"))
open(f"{W4}/trips_routed_v6_fine.json", "w", encoding="utf-8").write(s1)
open(f"{W4}/depot_legs_v6_fine.json", "w", encoding="utf-8").write(s2)
del legs, routes, legsout, G_D, G_L, tree
print("routed MB", round(len(s1.encode())/1e6, 2), "legs MB", round(len(s2.encode())/1e6, 2), flush=True)

# ---------------- 3. enrichment lookups ----------------
con = duckdb.connect()
rows = con.sql(f"""
  SELECT trim(idcontentor) cid, TRY_CAST("Data da leitura" AS TIMESTAMP) ts,
         TRY_CAST("Enchimento" AS INT) fill,
         (trim(idrecolha) NOT IN ('', '0') AND idrecolha IS NOT NULL) is_event
  FROM '{ROOT}/Brain/03_db/parquet/raw_collections.parquet'
  WHERE "Data da leitura" IS NOT NULL ORDER BY cid, ts
""").df()
prefill, readfill, prev = {}, defaultdict(list), {}
for r in rows.itertuples():
    key = (r.cid, r.ts.strftime("%Y-%m-%d %H:%M"))
    if r.is_event:
        p = prev.get(r.cid)
        if p is not None and (r.ts - p[0]).total_seconds() <= 900 and p[1] is not None and p[1] >= 0:
            prefill[key] = int(p[1])
    else:
        readfill[key].append(int(r.fill) if r.fill is not None else None)
    prev[r.cid] = (r.ts, r.fill)
del rows

bins = con.sql(f"""
  SELECT trim(idcontentor) cid, MAX(TRY_CAST("Volume do tipo de contentor" AS INT)) vol,
         ANY_VALUE(CASE WHEN description LIKE '%Vidro%' THEN 'G'
                        WHEN description LIKE '%papel%' THEN 'C' ELSE 'P' END) fl
  FROM '{ROOT}/Brain/03_db/parquet/raw_collections.parquet' GROUP BY 1
""").df()
VOL = {r.cid: (int(r.vol or 2500), r.fl) for r in bins.itertuples()}

sens = con.sql(f"""
  SELECT trim(idcontentor) cid, TRY_CAST("Data da leitura" AS TIMESTAMP) ts,
         TRY_CAST("Enchimento" AS INT) fill
  FROM '{ROOT}/Brain/03_db/parquet/raw_sensors.parquet'
  WHERE TRY_CAST("Enchimento" AS INT) IS NOT NULL ORDER BY cid, ts
""").df()
S_TS, S_F, CEIL = defaultdict(list), defaultdict(list), {}
for r in sens.itertuples():
    S_TS[r.cid].append(r.ts.timestamp()); S_F[r.cid].append(int(r.fill))
    if 0 <= r.fill <= 100 and r.fill > CEIL.get(r.cid, 0): CEIL[r.cid] = int(r.fill)
del sens

def sensor_val(cid, date, hhmm):
    ts_list = S_TS.get(cid)
    if not ts_list: return None
    tq = datetime.fromisoformat(f"{date} {hhmm}").timestamp()
    i = bisect.bisect_left(ts_list, tq)
    best, bd = None, 10801
    for j in (i - 1, i):
        if 0 <= j < len(ts_list):
            d = abs(ts_list[j] - tq)
            if d < bd: bd, best = d, j
    if best is None or bd > 10800: return None
    val = S_F[cid][best]
    if val < 0: return val
    return round(val * 100.0 / (CEIL.get(cid) or 84))

# ---------------- 4. enrich stops + trip estimates ----------------
hit_s = hit_i = miss = n_sens_valid = n_sens_neg = n_est_obs = 0
est = {}          # tid -> (lo, mid, hi, obs_same_material)
for t in world:
    tid = str(t["id"])
    tl = FR2L.get(t.get("mat_hint") if t.get("frac") == "Phantom" else t.get("frac"), "P")
    dts = sdates[tid]
    ns = []
    for s, sd in zip(t["stops"], dts):
        cid = str(s[2])
        key = (cid, f"{sd} {s[3]}")
        typ = s[4]
        if typ == "S":
            f = prefill.get(key)
            hit_s += f is not None
        else:
            vals = readfill.get(key)
            f = vals.pop(0) if vals else None
            hit_i += f is not None
        if f is None: miss += 1
        vol, fl = VOL.get(cid, (2500, tl))
        sv = sensor_val(cid, sd, s[3])
        if sv is not None:
            n_sens_neg += sv < 0; n_sens_valid += sv >= 0
        ns.append([s[0], s[1], s[2], s[3], typ, f, None, fl, sv])
    # strict estimate (stamped only), fallback fill = trip median of known fills
    fills = [x[5] for x in ns if x[5] is not None and x[5] >= 0]
    fallback = statistics.median(fills) if fills else 75
    lo = mid = hi = obs = 0.0
    for x in ns:
        vol, fl = VOL.get(str(x[2]), (2500, tl))
        if x[4] == "S":
            fill = x[5] if x[5] is not None and x[5] >= 0 else fallback
            m3 = vol / 1000 * fill / 100
            dl, dm, dh = DENS[fl]
            lo += m3 * dl; mid += m3 * dm; hi += m3 * dh
            x[6] = round(m3 * dm, 1)
        else:
            if x[5] is not None and x[5] >= 0 and fl in DENS_MID:
                x[6] = round(vol / 1000 * x[5] / 100 * DENS_MID[fl], 1)
                n_est_obs += 1
            if x[4] in ("I", "P") and fl == tl and x[5] is not None and x[5] >= 0:
                obs += vol / 1000 * x[5] / 100 * DENS_MID[fl]
    est[tid] = (lo, mid, hi, obs)
    t["stops"] = ns
print(f"fills: S {hit_s}, I/L/P {hit_i}, missing {miss} | sensor {n_sens_valid} valid + "
      f"{n_sens_neg} err | inferred est {n_est_obs} | {time.time()-t0:.0f}s", flush=True)

# identifier-level shares & cap (kg counted once per identifier; phantoms excluded)
def ident_of(t):
    return str(t.get("base_id") or t["id"])
g_mid = defaultdict(float); g_e2 = defaultdict(float); g_kg = {}
for t in trips:
    idn = ident_of(t)
    lo, mid, hi, obs = est[str(t["id"])]
    g_mid[idn] += mid; g_e2[idn] += mid + obs
    if g_kg.get(idn) is None: g_kg[idn] = t.get("kg")

index = []
n_capped = 0
for t in world:
    tid = str(t["id"])
    ph = t.get("frac") == "Phantom"
    lo, mid, hi, obs = est[tid]
    m = {
        "id": t["id"], "part": t.get("part", ""), "n_parts": t.get("n_parts", 1),
        "date": t["date"], "start": t["start"], "end": t["end"], "dur_h": t["dur_h"],
        "rota": t.get("rota"), "frac": t["frac"], "n_bins": t["n_bins"],
        "n_inferred": (len(t["stops"]) if ph else t.get("n_inferred", 0)),
        "n_lowconf": 0 if ph else t.get("n_lowconf", 0),
        "km_rec": t.get("km_rec"), "kg": t.get("kg"),
        "merged": bool(t.get("merged")),
        "flagged": bool(t.get("speed_flags")),
        "est_lo": round(lo), "est_mid": round(mid), "est_hi": round(hi),
    }
    if ph:
        m["est2_mid"] = round(obs); m["capped"] = False
        m["wshare"] = m["wshare2"] = None
        if t.get("mat_hint"): m["mat_hint"] = t["mat_hint"]
    else:
        idn = ident_of(t)
        kg = g_kg.get(idn)
        e2sum = g_e2[idn]
        factor, capped = 1.0, False
        if kg and e2sum > kg:
            factor = kg / e2sum; capped = True
        m["est2_mid"] = round((mid + obs) * factor)
        m["capped"] = capped
        n_capped += capped
        m["wshare"] = round(100 * g_mid[idn] / kg, 1) if kg else None
        m["wshare2"] = min(100.0, round(100 * e2sum * factor / kg, 1)) if kg else None
    index.append(m)

json.dump(world, open(f"{W4}/trips_v6_enriched.json", "w", encoding="utf-8"),
          ensure_ascii=False, separators=(",", ":"))
json.dump(index, open(f"{W4}/trips_index_v6.json", "w", encoding="utf-8"),
          ensure_ascii=False, separators=(",", ":"))

sh2 = [m["wshare2"] for m in index if m.get("wshare2") and m["n_parts"] == 1 and m.get("kg")]
print(json.dumps({
    "tracks_total": len(world), "trips": len(trips), "phantoms": len(phantoms),
    "routed": len({k for k in trip_nodes}), "flag_paths": n_flag_paths,
    "flagged_tracks": len(flags_out), "dropped_relabeled_S": dropped,
    "capped_tracks": n_capped,
    "median_wshare2_unsplit": round(statistics.median(sh2), 1) if sh2 else None,
}), flush=True)
print(f"done {time.time()-t0:.0f}s")
