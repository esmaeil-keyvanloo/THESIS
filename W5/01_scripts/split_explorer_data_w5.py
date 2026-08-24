"""W5 explorer builder: template -> index.html + editorial.html; data -> per-year chunks.

Inputs (W5/02_data_work): trips_v7_enriched.json, trips_index_v7.json, trips_routed_v7.json,
depot_legs_v7.json, sensor_drops_v2.parquet, site_index.parquet, site_travel.parquet,
circuit_membership.json, info_stats.json, calibration.json.
Static layers (bins/boundaries/facilities/tempo) are carried over from the W4 explorer (read-only).
Run:  python -X utf8 W5/01_scripts/split_explorer_data_w5.py
"""
import json
import math
import os
from collections import defaultdict

import duckdb

ROOT = r"C:/Users/esmae/Desktop/phd Esmaeil/THESIS CLAUDE"
W5D = f"{ROOT}/W5/02_data_work"
OUT = f"{ROOT}/W5/03_outputs/explorer"
W4DATA = f"{ROOT}/W4/03_outputs/explorer/data"
os.makedirs(f"{OUT}/data", exist_ok=True)
os.makedirs(f"{OUT}/info", exist_ok=True)

J = lambda p: json.load(open(p, encoding="utf-8"))


def dump(obj, name):
    p = f"{OUT}/data/{name}"
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, separators=(",", ":"), ensure_ascii=False)
    print(f"  {name}: {os.path.getsize(p)/1e6:.2f} MB")


# ---------- load ----------
enr = J(f"{W5D}/trips_v7_enriched.json")
tracks = enr["tracks"] if isinstance(enr, dict) and "tracks" in enr else enr
idx_raw = J(f"{W5D}/trips_index_v7.json")
idx_list = idx_raw["tracks"] if isinstance(idx_raw, dict) and "tracks" in idx_raw else idx_raw
routed_raw = J(f"{W5D}/trips_routed_v7.json")
routes = routed_raw.get("routes", routed_raw)
flags = routed_raw.get("flags", {})
legs_raw = J(f"{W5D}/depot_legs_v7.json")
legs = legs_raw.get("legs", legs_raw)
circ = {}
if os.path.exists(f"{W5D}/circuit_membership.json"):
    circ = J(f"{W5D}/circuit_membership.json")
print(f"tracks {len(tracks)} | index {len(idx_list)} | routes {len(routes)} | flagged {len(flags)} | legs {len(legs)}")

by_id_stops = {}
by_id_sensev = {}
for t in tracks:
    tid = str(t["id"])
    by_id_stops[tid] = t.get("stops") or []
    by_id_sensev[tid] = t.get("sensor_events") or []

# ---------- site travel lookup for playback legal speeds ----------
con = duckdb.connect()
sites = con.sql(f"SELECT * FROM '{W5D}/site_index.parquet'").df()
trav = con.sql(f"SELECT * FROM '{W5D}/site_travel.parquet'").df()
site_by_key = {(round(r.lat, 5), round(r.lon, 5)): int(r.site_id) for r in sites.itertuples()}
site_pts = [(float(r.lat), float(r.lon), int(r.site_id)) for r in sites.itertuples()]
tmat = {}
acol = "a" if "a" in trav.columns else "site_a"
bcol = "b" if "b" in trav.columns else "site_b"
for r in trav.itertuples():
    a, b = int(getattr(r, acol)), int(getattr(r, bcol))
    tmat[(a, b)] = (float(r.km), float(r.legal_min))
    tmat[(b, a)] = (float(r.km), float(r.legal_min))


def site_of(lat, lon):
    s = site_by_key.get((round(lat, 5), round(lon, 5)))
    if s is not None:
        return s
    best, bd = None, 9e9
    for la, lo, sid in site_pts:
        d = (la - lat) ** 2 + (lo - lon) ** 2
        if d < bd:
            bd, best = d, sid
    return best


def leg_info(stops):
    out = []
    for i in range(len(stops) - 1):
        a = site_of(stops[i][0], stops[i][1])
        b = site_of(stops[i + 1][0], stops[i + 1][1])
        km, lm = tmat.get((a, b), (None, None)) if a != b else (0.05, 0.1)
        out.append([round(km, 2) if km is not None else None, round(lm, 2) if lm is not None else None])
    return out


# ---------- index ----------
def slim(t):
    tid = str(t["id"])
    ev = t.get("evidence_mix") or t.get("ev") or {}
    o = {
        "id": tid, "date": t["date"], "start": t.get("start"), "end": t.get("end"),
        "dur_h": t.get("dur_h"), "rota": t.get("rota"), "frac": t.get("frac"),
        "n_bins": t.get("n_bins", 0), "n_inferred": t.get("n_inferred", 0), "n_lowconf": t.get("n_lowconf", 0),
        "km_rec": t.get("km_rec"), "kg": t.get("kg"),
    }
    for k in ("part", "n_parts", "merged", "flagged", "est_mid", "est_lo", "est_hi",
              "est2_mid", "capped", "wshare", "wshare2"):
        if t.get(k):
            o[k] = t[k]
    cont = t.get("continues_from") or t.get("cont")
    if cont:
        o["cont"] = str(cont)
    if ev and (ev.get("d") or ev.get("ds") or ev.get("s") or ev.get("d_only") or ev.get("s_only")):
        o["ev"] = {"d": ev.get("d", ev.get("d_only", 0)), "ds": ev.get("ds", 0), "s": ev.get("s", ev.get("s_only", 0))}
    if circ.get(tid):
        o["cir"] = circ[tid]
    return o


index = [slim(t) for t in idx_list]
dump(index, "trips_index.json")

# ---------- per-year chunks ----------
years = sorted({t["date"][:4] for t in index})
drops_df = con.sql(f"""
    SELECT cid, strftime(t_before, '%Y-%m-%d') AS d_after_day,
           strftime(t_before, '%H:%M') AS ws, strftime(t_after, '%H:%M') AS we,
           strftime(t_after, '%Y-%m-%d') AS day2,
           round(pct_before) AS pct, confidence, rebound
    FROM '{W5D}/sensor_drops_v2.parquet'
""").df()
bin_pos = {}
for t in tracks:
    for s in by_id_stops[str(t["id"])]:
        bin_pos.setdefault(str(s[2]), (s[0], s[1]))
bins_static = J(f"{W4DATA}/bins.json")
for b in bins_static:
    bin_pos.setdefault(str(b["cid"]), (b["lat"], b["lon"]))
bin_mat = {str(b["cid"]): b.get("frac") for b in bins_static}

drops_by_day = defaultdict(list)
for r in drops_df.itertuples():
    key = r.day2
    pos = bin_pos.get(str(r.cid))
    if not pos:
        continue
    drops_by_day[key].append([round(pos[0], 5), round(pos[1], 5), str(r.cid), r.ws if r.d_after_day == r.day2 else "…",
                              r.we, int(r.pct) if r.pct == r.pct else None, r.confidence, bin_mat.get(str(r.cid), "P")])

for y in years:
    stops_map, routes_map, legs_map, flags_map, sensev_map = {}, {}, {}, {}, {}
    for t in index:
        if t["date"][:4] != y:
            continue
        tid = t["id"]
        st = by_id_stops.get(tid) or []
        stops_map[tid] = [[round(s[0], 5), round(s[1], 5), s[2], s[3], s[4], s[5], s[6], s[7], s[8],
                           (s[9] if len(s) > 9 else "D")] for s in st]
        r = routes.get(tid)
        if r:
            o = {"km": r.get("km"), "p": r.get("p") or r.get("path")}
            anch = r.get("anchors") or r.get("a")
            if anch and len(anch) == len(st):
                o["a"] = anch
                o["lg"] = leg_info(st)
            routes_map[tid] = o
        if tid in legs:
            legs_map[tid] = legs[tid]
        if tid in flags:
            flags_map[tid] = flags[tid]
        sev = by_id_sensev.get(tid) or []
        if sev:
            sensev_map[tid] = [[round(e[0], 5), round(e[1], 5), str(e[2]), e[3], e[4], e[5], e[6],
                                (e[7] if len(e) > 7 else bin_mat.get(str(e[2]), "P"))] for e in sev]
    dchunk = {k: v for k, v in drops_by_day.items() if k[:4] == y}
    dump({"stops": stops_map, "routes": routes_map, "legs": legs_map, "flags": flags_map,
          "sensev": sensev_map, "drops": dchunk}, f"year_{y}.json")

# ---------- daily heat (kg from W4 base; sensor events + evidence share new) ----------
daily = J(f"{W4DATA}/daily_kg.json")
ev_by_day = defaultdict(lambda: [0, 0, 0])
for t in index:
    e = t.get("ev")
    if e:
        ev_by_day[t["date"]][0] += e.get("d", 0)
        ev_by_day[t["date"]][1] += e.get("ds", 0)
        ev_by_day[t["date"]][2] += e.get("s", 0)
smax = 0
for day, lst in drops_by_day.items():
    rec = daily.get(day)
    if rec is None or not isinstance(rec, dict):
        rec = daily[day] = {"kg": (rec if isinstance(rec, (int, float)) else 0)}
    rec["sn"] = len(lst)
    smax = max(smax, len(lst))
for day, (d, ds, s) in ev_by_day.items():
    rec = daily.get(day)
    if isinstance(rec, dict) and (d + ds + s) > 0:
        rec["es"] = round((ds + s) / (d + ds + s), 3)
daily["_smax"] = smax
dump(daily, "daily_kg.json")

# ---------- static + info ----------
for name in ("boundaries.json", "facilities.json", "bins.json", "tempo.json"):
    json.dump(J(f"{W4DATA}/{name}"), open(f"{OUT}/data/{name}", "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)
info = J(f"{W5D}/info_stats.json")
dump(info, "info_stats.json")
meth_src = f"{ROOT}/W5/03_outputs/info/methodology.html"
if os.path.exists(meth_src):
    open(f"{OUT}/info/methodology.html", "w", encoding="utf-8").write(open(meth_src, encoding="utf-8").read())
    print("  info/methodology.html copied")

# ---------- render both skins ----------
tpl = open(f"{ROOT}/W5/01_scripts/explorer_w5_template.html", encoding="utf-8").read()
open(f"{OUT}/index.html", "w", encoding="utf-8").write(
    tpl.replace("__SKIN__", "neu").replace("__OTHER_SKIN__", "editorial.html").replace("__OTHER_LABEL__", "editorial sample"))
open(f"{OUT}/editorial.html", "w", encoding="utf-8").write(
    tpl.replace("__SKIN__", "editorial").replace("__OTHER_SKIN__", "index.html").replace("__OTHER_LABEL__", "hybrid neumorph"))
print("index.html + editorial.html rendered")

# ---------- sanity ----------
for y in years:
    d = J(f"{OUT}/data/year_{y}.json")
    n_anch = sum(1 for r in d["routes"].values() if r.get("a"))
    assert d["routes"], f"year {y}: no routes!"
    print(f"  {y}: {len(d['stops'])} tracks, {len(d['routes'])} routes ({n_anch} playable), "
          f"{len(d['sensev'])} trips w/ sensor events, {len(d['drops'])} drop-days")
print("DONE")
