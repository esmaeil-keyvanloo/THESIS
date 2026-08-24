# T0+T1 — Shared road-speed engine + tolerance calibration (W5, Task A)
# Outputs: W5/02_data_work/site_index.parquet, site_travel.parquet, calibration.json
import json, math, time
import numpy as np
import pandas as pd
import geopandas as gpd
from pyproj import Transformer
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra, connected_components
from scipy.spatial import cKDTree

ROOT = r"C:/Users/esmae/Desktop/phd Esmaeil/THESIS CLAUDE"
GPKG = ROOT + "/GIS_DATA/01_osm/riomaior_10km/osm_roads_riomaior10km.gpkg"
RAW = ROOT + "/Brain/03_db/parquet/raw_collections.parquet"
MASTER = ROOT + "/Brain/03_db/parquet/master_events_w4.parquet"
TRIPS_IDX = ROOT + "/W4/02_data_work/trips_index_v6.json"
OUT = ROOT + "/W5/02_data_work"

BAN = {"path", "footway", "steps", "cycleway", "bridleway", "pedestrian"}
LEGAL = {"motorway": 90, "motorway_link": 60, "trunk": 80, "trunk_link": 60,
         "primary": 80, "primary_link": 50, "secondary": 80, "secondary_link": 50,
         "tertiary": 70, "tertiary_link": 50}
LEGAL_DEF = 50
CEIL = {"motorway": 130, "trunk": 100, "primary": 100, "secondary": 90, "tertiary": 80}
CEIL_DEF = 60
DEPOT = (39.33921, -8.92493)
TS = (39.31963, -8.92405)

t0 = time.time()
log = lambda *a: print(f"[{time.time()-t0:7.1f}s]", *a, flush=True)

# ---------- 1. Graph ----------
roads = gpd.read_file(GPKG)
roads = roads[~roads["fclass"].isin(BAN)].reset_index(drop=True)
log("roads kept:", len(roads))

xs_i, ys_i, xs_j, ys_j, kms, legs, ceis = [], [], [], [], [], [], []
for fclass, geom in zip(roads["fclass"].values, roads.geometry.values):
    v_leg = LEGAL.get(fclass, LEGAL_DEF)
    v_cei = CEIL.get(fclass, CEIL_DEF)
    if geom.geom_type == "LineString":
        parts = [geom]
    else:
        parts = list(geom.geoms)
    for ls in parts:
        c = np.asarray(ls.coords)
        if len(c) < 2:
            continue
        seg = np.hypot(np.diff(c[:, 0]), np.diff(c[:, 1])) / 1000.0  # km
        xs_i.append(c[:-1, 0]); ys_i.append(c[:-1, 1])
        xs_j.append(c[1:, 0]); ys_j.append(c[1:, 1])
        kms.append(seg)
        legs.append(seg / v_leg * 60.0)
        ceis.append(seg / v_cei * 60.0)

xi = np.concatenate(xs_i); yi = np.concatenate(ys_i)
xj = np.concatenate(xs_j); yj = np.concatenate(ys_j)
km = np.concatenate(kms); leg = np.concatenate(legs); cei = np.concatenate(ceis)

# node ids: round coords to 1 cm and dedupe
all_xy = np.round(np.concatenate([np.column_stack([xi, yi]), np.column_stack([xj, yj])]), 2)
uniq, inv = np.unique(all_xy, axis=0, return_inverse=True)
n_nodes = len(uniq)
ni = inv[:len(xi)]; nj = inv[len(xi):]
log("nodes:", n_nodes, "segments:", len(ni))

# dedupe parallel edges (keep min weight), add both directions
e = pd.DataFrame({"i": ni, "j": nj, "km": km, "leg": leg, "cei": cei})
e = e[e.i != e.j]
e2 = pd.concat([e, e.rename(columns={"i": "j", "j": "i"})], ignore_index=True)
e2 = e2.groupby(["i", "j"], as_index=False).min()
G_km = csr_matrix((e2.km.values, (e2.i.values, e2.j.values)), shape=(n_nodes, n_nodes))
G_leg = csr_matrix((e2.leg.values, (e2.i.values, e2.j.values)), shape=(n_nodes, n_nodes))
G_cei = csr_matrix((e2.cei.values, (e2.i.values, e2.j.values)), shape=(n_nodes, n_nodes))
ncomp, labels = connected_components(G_km, directed=False)
main = np.bincount(labels).argmax()
in_main = labels == main
log(f"components: {ncomp}, main component nodes: {in_main.sum()}/{n_nodes}")

# ---------- 2. Sites ----------
raw = pd.read_parquet(RAW, columns=["Latitude", "Longitude"])
lat = pd.to_numeric(raw["Latitude"].str.replace(",", ".", regex=False), errors="coerce")
lon = pd.to_numeric(raw["Longitude"].str.replace(",", ".", regex=False), errors="coerce")
pts = pd.DataFrame({"lat": lat.round(5), "lon": lon.round(5)}).dropna().drop_duplicates()
sites = pd.concat([pts, pd.DataFrame([{"lat": DEPOT[0], "lon": DEPOT[1]},
                                      {"lat": TS[0], "lon": TS[1]}])], ignore_index=True)
sites = sites.drop_duplicates().reset_index(drop=True)
sites["site_id"] = np.arange(len(sites))
log("sites:", len(sites))

tr = Transformer.from_crs(4326, 3763, always_xy=True)
sx, sy = tr.transform(sites["lon"].values, sites["lat"].values)
tree = cKDTree(uniq[in_main])
main_idx = np.flatnonzero(in_main)
snap_d, snap_k = tree.query(np.column_stack([sx, sy]))
sites["node"] = main_idx[snap_k]
sites["snap_m"] = snap_d
log(f"snap dist m: median {np.median(snap_d):.1f}, p95 {np.percentile(snap_d,95):.1f}, max {snap_d.max():.1f}")

sites[["site_id", "lat", "lon", "node", "snap_m"]].to_parquet(OUT + "/site_index.parquet", index=False)

# ---------- 3. Full site-to-site matrices ----------
u_nodes, u_inv = np.unique(sites["node"].values, return_inverse=True)  # site -> row in matrix via u_inv
nU = len(u_nodes)
log("unique snapped nodes:", nU)

def full_matrix(G):
    M = np.empty((nU, nU))
    CH = 64
    for s in range(0, nU, CH):
        idx = u_nodes[s:s + CH]
        D = dijkstra(G, directed=True, indices=idx)
        M[s:s + CH, :] = D[:, u_nodes]
    return M

M_leg = full_matrix(G_leg); log("legal matrix done")
M_cei = full_matrix(G_cei); log("ceiling matrix done")
M_km = full_matrix(G_km); log("km matrix done")
for nm, M in [("legal", M_leg), ("ceiling", M_cei), ("km", M_km)]:
    ninf = np.isinf(M).sum()
    log(f"{nm}: inf cells {ninf}, max {np.nanmax(M[np.isfinite(M)]):.1f}")

nS = len(sites)
site_row = u_inv  # per site -> matrix row
a_idx, b_idx = np.triu_indices(nS, k=1)
pairs = pd.DataFrame({
    "a": sites["site_id"].values[a_idx],
    "b": sites["site_id"].values[b_idx],
    "legal_min": M_leg[site_row[a_idx], site_row[b_idx]],
    "ceiling_min": M_cei[site_row[a_idx], site_row[b_idx]],
    "km": M_km[site_row[a_idx], site_row[b_idx]],
})
pairs[["legal_min", "ceiling_min", "km"]] = pairs[["legal_min", "ceiling_min", "km"]].round(4)
pairs.to_parquet(OUT + "/site_travel.parquet", index=False)
log("site_travel rows:", len(pairs))

# ---------- 4. Calibration ----------
tri = json.load(open(TRIPS_IDX, encoding="utf-8"))
clean_ids = {t["id"] for t in tri
             if t["n_parts"] == 1 and t["part"] == "" and not t["merged"] and not t["flagged"]}
mst = pd.read_parquet(MASTER, columns=["raw_row_id", "ts", "trip_id", "row_type", "source"])
mst = mst[(mst.source == "driver") & (mst.row_type == "S") & (mst.trip_id.isin(clean_ids))]
log("trusted stamped rows:", len(mst), "trips:", mst.trip_id.nunique())

# map raw_row_id -> site_id via rounded coords
raw_full = pd.read_parquet(RAW, columns=["Latitude", "Longitude"])
raw_full["raw_row_id"] = np.arange(1, len(raw_full) + 1)
raw_full["lat"] = pd.to_numeric(raw_full["Latitude"].str.replace(",", ".", regex=False), errors="coerce").round(5)
raw_full["lon"] = pd.to_numeric(raw_full["Longitude"].str.replace(",", ".", regex=False), errors="coerce").round(5)
site_map = sites.set_index(["lat", "lon"])["site_id"]
raw_full = raw_full.merge(sites[["lat", "lon", "site_id"]], on=["lat", "lon"], how="left")
mst = mst.merge(raw_full[["raw_row_id", "site_id"]], on="raw_row_id", how="left")
mst = mst.dropna(subset=["site_id"]).sort_values(["trip_id", "ts"])

mst["site_id"] = mst["site_id"].astype(int)
g = mst.groupby("trip_id", sort=False)
mst["prev_site"] = g["site_id"].shift()
mst["gap_min"] = (mst["ts"] - g["ts"].shift()).dt.total_seconds() / 60.0
pairs_cal = mst.dropna(subset=["prev_site"]).copy()
pairs_cal["prev_site"] = pairs_cal["prev_site"].astype(int)

# lookup km + legal between prev_site and site
ra = site_row[pairs_cal["prev_site"].values]
rb = site_row[pairs_cal["site_id"].values]
pairs_cal["link_km"] = M_km[ra, rb]
pairs_cal["link_legal_min"] = M_leg[ra, rb]
pairs_cal = pairs_cal[np.isfinite(pairs_cal["link_km"])]
pairs_cal = pairs_cal[pairs_cal["gap_min"] > 0]
log("consecutive stamped gaps usable:", len(pairs_cal))

# service time: same site (road_km < 0.05)
same = pairs_cal[(pairs_cal["link_km"] < 0.05) & (pairs_cal["gap_min"] <= 60)]
service_med = float(same["gap_min"].median())
service_p75 = float(same["gap_min"].quantile(0.75))
log(f"same-site gaps n={len(same)}, median={service_med:.2f}, p75={service_p75:.2f}")

# slack on distinct-site links
links = pairs_cal[(pairs_cal["link_km"] >= 0.05) & (pairs_cal["gap_min"] <= 180)].copy()
links["slack"] = links["gap_min"] - service_med - links["link_legal_min"]
qs = {f"p{int(q*100):02d}": float(links["slack"].quantile(q))
      for q in [0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]}
p05 = links["slack"].quantile(0.05)
tol_min = int(math.ceil(max(0.0, -p05)))
log(f"links n={len(links)}, slack p05={p05:.2f}, tol_min={tol_min}")

same_gt5s = same[same["gap_min"] > 5 / 60.0]
cal = {
    "service_med_min": round(service_med, 2),
    "service_p75_min": round(service_p75, 2),
    "same_site_gap_quantiles_min": {f"p{int(q*100):02d}": round(float(same["gap_min"].quantile(q)), 3)
                                    for q in [0.25, 0.50, 0.75, 0.90, 0.95]},
    "same_site_share_le_5s": round(float((same["gap_min"] <= 5 / 60.0).mean()), 3),
    "same_site_med_excl_le_5s": round(float(same_gt5s["gap_min"].median()), 2) if len(same_gt5s) else None,
    "tol_min": tol_min,
    "slack_quantiles": {k: round(v, 2) for k, v in qs.items()},
    "n_links_used": int(len(links)),
    "n_same_site_gaps": int(len(same)),
    "n_trusted_trips": int(mst.trip_id.nunique()),
    "notes": "Trusted evidence = consecutive S-rows within clean unsplit trips "
             "(n_parts=1, not merged, not flagged, from trips_index_v6). "
             "Same-site: road_km<0.05 & gap<=60min. Links: road_km>=0.05 & gap<=180min. "
             "tol_min = ceil(max(0, -p05(slack))).",
    "site_note": "270 unique rounded-5dp coordinates across 816 containers (multi-bin sites share "
                 "coordinates) + depot + TS = 272 sites.",
    "graph": {"nodes_main_component": int(in_main.sum()), "roads_features": int(len(roads)),
              "n_sites": int(nS), "n_unique_snapped_nodes": int(nU),
              "snap_m_median": round(float(np.median(snap_d)), 1),
              "snap_m_max": round(float(snap_d.max()), 1)},
}
json.dump(cal, open(OUT + "/calibration.json", "w"), indent=2)
log("done")
