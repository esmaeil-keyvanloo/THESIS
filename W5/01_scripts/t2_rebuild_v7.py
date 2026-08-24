# T2 (Task D) - Clean trip rebuild v7 from raw stamps, engine-based feasibility.
# Uses ONLY W5 engine artifacts (site_travel.parquet + calibration.json) for travel
# times. Never a flat 60 km/h.
# Outputs: trips_v7.json, phantom_tracks_v7.json, assignments_v7.parquet,
#          dropped_v7.parquet, rebuild_stats.json (all in W5/02_data_work).
import json, math, time, bisect
from collections import defaultdict, Counter
import numpy as np
import pandas as pd

ROOT = r"C:/Users/esmae/Desktop/phd Esmaeil/THESIS CLAUDE"
RAW = ROOT + "/Brain/03_db/parquet/raw_collections.parquet"
OUT = ROOT + "/W5/02_data_work"

cal = json.load(open(OUT + "/calibration.json"))
SERVICE = cal["service_med_min"]          # 0.02 min
TOL = cal["tol_min"]                      # 0
MIN_AVAIL = 0.5
CEIL_SERVICE = 0.5
WINDOW_MIN = 30 + TOL
P_LOW = 0.7
BATCH_GAP = 1.0
BATCH_KM = 2.0
CONT_GAP = 20.0
CONT_KM = 3.0
PH_MIN = 3
EPS = 1e-9
R_EARTH = 6371.0088

FRAC = {"Mistura de embalagens": "Packaging",
        "Embalagens de Vidro": "Glass"}  # papel/cartao handled by startswith

def frac_of(desc):
    if desc is None or (isinstance(desc, float) and math.isnan(desc)):
        return None
    if desc.startswith("Embalagens de papel"):
        return "Paper/card"
    return FRAC.get(desc, desc)

def hav_km(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    h = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R_EARTH * math.asin(math.sqrt(h))

t0 = time.time()
log = lambda *a: print(f"[{time.time()-t0:6.1f}s]", *a, flush=True)

def np_default(o):
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    raise TypeError(f"not serializable: {type(o)}")

# ---------------- 1. Engine matrices ----------------
si = pd.read_parquet(OUT + "/site_index.parquet")
stv = pd.read_parquet(OUT + "/site_travel.parquet")
nS = len(si)
M_leg = np.zeros((nS, nS)); M_cei = np.zeros((nS, nS))
a = stv["a"].values; b = stv["b"].values
M_leg[a, b] = stv["legal_min"].values; M_leg[b, a] = stv["legal_min"].values
M_cei[a, b] = stv["ceiling_min"].values; M_cei[b, a] = stv["ceiling_min"].values
site_lut = {(int(round(la * 1e5)), int(round(lo * 1e5))): int(s)
            for la, lo, s in zip(si["lat"], si["lon"], si["site_id"])}
log("engine loaded: sites", nS)

def feas_legal(sa, sb, gap_min):
    avail = max(gap_min - SERVICE + TOL, MIN_AVAIL)
    return M_leg[sa, sb] <= avail + EPS

def feas_ceil(sa, sb, gap_min):
    avail = max(gap_min - CEIL_SERVICE, MIN_AVAIL)
    return M_cei[sa, sb] <= avail + EPS

# ---------------- 2. Raw rows ----------------
raw = pd.read_parquet(RAW, columns=["idcontentor", "Data da leitura", "Enchimento",
                                    "Latitude", "Longitude", "idrecolha", "Rota",
                                    "description", "Km totais", "Peso total"])
n_raw = len(raw)
df = pd.DataFrame({
    "row_id": np.arange(1, n_raw + 1),
    "cid": raw["idcontentor"].str.strip(),
    "ts": pd.to_datetime(raw["Data da leitura"]),
    "fill": pd.to_numeric(raw["Enchimento"].str.replace(",", ".", regex=False), errors="coerce"),
    "lat": pd.to_numeric(raw["Latitude"].str.replace(",", ".", regex=False), errors="coerce"),
    "lon": pd.to_numeric(raw["Longitude"].str.replace(",", ".", regex=False), errors="coerce"),
    "idr": raw["idrecolha"].str.strip(),
    "rota": raw["Rota"].str.strip(),
    "desc": raw["description"],
    "km_tot": pd.to_numeric(raw["Km totais"].str.replace(",", ".", regex=False), errors="coerce"),
    "kg_tot": pd.to_numeric(raw["Peso total"].str.replace(",", ".", regex=False), errors="coerce"),
})
df["is_event"] = df["idr"].notna() & (df["idr"] != "") & (df["idr"] != "0")
assert len(df) == 264817

# exact duplicates cid+ts: keep first (events preferred, then lowest row_id)
df = df.sort_values(["cid", "ts", "is_event", "row_id"],
                    ascending=[True, True, False, True], kind="mergesort")
dupmask = df.duplicated(["cid", "ts"], keep="first")
dropped_dup = df[dupmask].copy()
d = df[~dupmask].copy()
log("exact duplicates dropped:", len(dropped_dup),
    "(events among dropped:", int(dropped_dup.is_event.sum()), ")")

# pre-readings: non-event whose next same-cid reading is an event <= 15 min later
d = d.sort_values(["cid", "ts", "row_id"], kind="mergesort").reset_index(drop=True)
same_next = d["cid"].shift(-1) == d["cid"]
next_ev = d["is_event"].shift(-1, fill_value=False)
next_gap = (d["ts"].shift(-1) - d["ts"]).dt.total_seconds()
d["is_pre"] = (~d["is_event"]) & same_next & next_ev & (next_gap <= 900)
n_pre = int(d["is_pre"].sum())
log("pre-readings:", n_pre)

# site id per row
lat5 = (d["lat"].round(5) * 1e5).round().astype("int64")
lon5 = (d["lon"].round(5) * 1e5).round().astype("int64")
d["site"] = [site_lut.get((la, lo), -1) for la, lo in zip(lat5, lon5)]
assert (d["site"] >= 0).all(), "unmapped coordinates"
d["ts_py"] = d["ts"]

events = d[d["is_event"]].sort_values(["idr", "ts", "row_id"], kind="mergesort")
loose = d[(~d["is_event"]) & (~d["is_pre"])].sort_values(["ts", "row_id"], kind="mergesort")
log("events:", len(events), "loose:", len(loose), "pre:", n_pre)

# ---------------- 3. Identifier chains -> split/merge ----------------
ident_meta = {}
tracks = []                     # working track dicts
verdict_counts = Counter()
n_flagged_junctions_seed = 0

for idr, g in events.groupby("idr", sort=True):
    rows = list(g.itertuples(index=False))
    rota = next((r.rota for r in rows if isinstance(r.rota, str) and r.rota), None)
    descs = Counter(frac_of(r.desc) for r in rows if r.desc is not None)
    frac = descs.most_common(1)[0][0] if descs else None
    km_rec = next((r.km_tot for r in rows if not math.isnan(r.km_tot)), None)
    kg = next((r.kg_tot for r in rows if not math.isnan(r.kg_tot)), None)
    ident_meta[idr] = dict(rota=rota, frac=frac, km_rec=km_rec, kg=kg,
                           first=rows[0], last=rows[-1])
    # per-link evaluation
    links = []
    for i in range(len(rows) - 1):
        u, v = rows[i], rows[i + 1]
        gap = (v.ts_py - u.ts_py).total_seconds() / 60.0
        straight = hav_km(u.lat, u.lon, v.lat, v.lon)
        links.append(dict(i=i, gap=gap, straight=straight,
                          leg=M_leg[u.site, v.site],
                          ok_l=feas_legal(u.site, v.site, gap),
                          ok_c=feas_ceil(u.site, v.site, gap)))
    if all(l["ok_c"] for l in links):
        merged = any(not l["ok_l"] for l in links)
        n_flagged_junctions_seed += sum(1 for l in links if not l["ok_l"])
        tracks.append(dict(tid=str(idr), base=str(idr), part="", n_parts=1,
                           merged=merged, verdict=None, stamped=rows))
        verdict_counts["single-merged" if merged else "single-clean"] += 1
    else:
        # split at ceiling-infeasible junctions
        bad = [l for l in links if not l["ok_c"]]
        cuts = {l["i"] for l in bad}
        verdict = ("batch-entry" if any(l["gap"] <= BATCH_GAP and l["straight"] > BATCH_KM
                                        for l in bad) else "multi-vehicle")
        verdict_counts[verdict] += 1
        parts, cur = [], [rows[0]]
        for i in range(1, len(rows)):
            if (i - 1) in cuts:
                parts.append(cur); cur = []
            cur.append(rows[i])
        parts.append(cur)
        letters = "abcdefghijklmnopqrstuvwxyz"
        for k, pr in enumerate(parts):
            lett = letters[k] if k < 26 else f"z{k}"
            tracks.append(dict(tid=f"{idr}{lett}", base=str(idr), part=lett,
                               n_parts=len(parts), merged=False, verdict=verdict,
                               stamped=pr))
log("identifiers:", len(ident_meta), "tracks:", len(tracks),
    "verdicts:", dict(verdict_counts))

# ---------------- 4. Continuations (recomputed per audit criteria) ----------------
idents = []
for idr, m in ident_meta.items():
    pref = m["rota"][:2] if m["rota"] else None
    idents.append((idr, m["first"].ts_py, m["last"].ts_py,
                   (m["first"].lat, m["first"].lon), (m["last"].lat, m["last"].lon),
                   pref, m["frac"]))
by_day = defaultdict(list)
for it in idents:
    by_day[it[2].date()].append(it)   # index by end date
cont_pairs = []
for day, lst in by_day.items():
    for a_ in lst:
        for b_ in by_day.get(day, []):
            if a_[0] == b_[0]:
                continue
            gap = (b_[1] - a_[2]).total_seconds() / 60.0
            if not (0 <= gap <= CONT_GAP):
                continue
            key = a_[5] if a_[5] else a_[6]
            keyb = b_[5] if b_[5] else b_[6]
            if key is None or key != keyb:
                continue
            dist = hav_km(a_[4][0], a_[4][1], b_[3][0], b_[3][1])
            if dist <= CONT_KM:
                cont_pairs.append((a_[0], b_[0], gap, dist))
# later trip keeps closest predecessor only
best_pred = {}
for pa, pb, gap, dist in cont_pairs:
    if pb not in best_pred or gap < best_pred[pb][1]:
        best_pred[pb] = (pa, gap, dist)
continues_from = {pb: pa for pb, (pa, gap, dist) in best_pred.items()}
log("continuation pairs found:", len(cont_pairs),
    "later-trips annotated:", len(continues_from))

# ---------------- 5. Track index for assignment ----------------
by_date_tracks = defaultdict(list)
for k, tr in enumerate(tracks):
    ts0 = tr["stamped"][0].ts_py
    ts1 = tr["stamped"][-1].ts_py
    w0 = ts0 - pd.Timedelta(minutes=WINDOW_MIN)
    w1 = ts1 + pd.Timedelta(minutes=WINDOW_MIN)
    tr["w0"], tr["w1"] = w0, w1
    tr["sts"] = [r.ts_py for r in tr["stamped"]]
    tr["inserted"] = []
    dd = w0.date()
    while dd <= w1.date():
        by_date_tracks[dd].append(k)
        dd += pd.Timedelta(days=1)

# ---------------- 6. Loose-reading assignment ----------------
assign_rows = []   # dicts
loose_list = list(loose.itertuples(index=False))
for li, r in enumerate(loose_list):
    ts = r.ts_py
    cands = []
    had_window = False
    for k in by_date_tracks.get(ts.date(), ()):
        tr = tracks[k]
        if not (tr["w0"] <= ts <= tr["w1"]):
            continue
        had_window = True
        stp = tr["stamped"]
        p = bisect.bisect_right(tr["sts"], ts)
        ok = True
        score = 0.0
        if p > 0:
            u = stp[p - 1]
            gap = (ts - u.ts_py).total_seconds() / 60.0
            if not feas_legal(u.site, r.site, gap):
                ok = False
        if ok and p < len(stp):
            v = stp[p]
            gap = (v.ts_py - ts).total_seconds() / 60.0
            if not feas_legal(r.site, v.site, gap):
                ok = False
        if not ok:
            continue
        if 0 < p < len(stp):
            u, v = stp[p - 1], stp[p]
            score = max(0.0, M_leg[u.site, r.site] + M_leg[r.site, v.site]
                        - M_leg[u.site, v.site])
        elif p > 0:
            score = M_leg[stp[p - 1].site, r.site]
        else:
            score = M_leg[r.site, stp[0].site]
        cands.append((score, tr["tid"], k, p))
    if not cands:
        status = "INFEASIBLE" if had_window else "NO_TRIP"
        assign_rows.append(dict(cid=r.cid, ts=r.ts_py, lat=r.lat, lon=r.lon,
                                fill=r.fill, status=status, track_id=None,
                                alt_track_id=None, p_best=None,
                                insert_after_stop=None, site=r.site))
        continue
    cands.sort(key=lambda c: (c[0], c[1]))
    best = cands[0]
    if len(cands) > 1:
        alt = cands[1]
        denom = best[0] + alt[0]
        p_best = (alt[0] / denom) if denom > 0 else 0.5
        alt_tid = alt[1]
    else:
        p_best, alt_tid = 1.0, None
    status = "I" if p_best >= P_LOW else "L"
    ai = len(assign_rows)
    assign_rows.append(dict(cid=r.cid, ts=r.ts_py, lat=r.lat, lon=r.lon,
                            fill=r.fill, status=status, track_id=best[1],
                            alt_track_id=alt_tid, p_best=p_best,
                            insert_after_stop=best[3], site=r.site))
    tracks[best[2]]["inserted"].append(ai)
log("assignment pass done:", Counter(a["status"] for a in assign_rows))

# ---------------- 7. Full-chain validation with eviction ----------------
n_evicted = 0
for tr in tracks:
    if not tr["inserted"]:
        tr["chain"] = [("S", i) for i in range(len(tr["stamped"]))]
        continue
    ins = sorted(tr["inserted"],
                 key=lambda ai: (assign_rows[ai]["insert_after_stop"],
                                 assign_rows[ai]["ts"]))
    while True:
        # build chain: inserted with pos<=i go before stamped i
        chain = []
        k = 0
        for i in range(len(tr["stamped"])):
            while k < len(ins) and assign_rows[ins[k]]["insert_after_stop"] <= i:
                chain.append(("A", ins[k])); k += 1
            chain.append(("S", i))
        while k < len(ins):
            chain.append(("A", ins[k])); k += 1

        def node(cnode):
            kind, idx = cnode
            if kind == "S":
                r = tr["stamped"][idx]
                return r.ts_py, r.site
            arow = assign_rows[idx]
            return arow["ts"], arow["site"]

        worst_ai, worst_viol = None, 0.0
        for i in range(len(chain) - 1):
            (ka, ia), (kb, ib) = chain[i], chain[i + 1]
            if ka == "S" and kb == "S":
                continue  # stamped-stamped: pre-existing, handled by flags/splits
            ta, sa_ = node(chain[i]); tb, sb_ = node(chain[i + 1])
            gap = (tb - ta).total_seconds() / 60.0
            avail = max(gap - SERVICE + TOL, MIN_AVAIL)
            viol = M_leg[sa_, sb_] - avail
            if viol > EPS:
                for kind, idx in (chain[i], chain[i + 1]):
                    if kind == "A" and viol > worst_viol:
                        worst_viol, worst_ai = viol, idx
        if worst_ai is None:
            tr["chain"] = chain
            break
        assign_rows[worst_ai]["status"] = "EVICTED_CONFLICT"
        ins = [ai for ai in ins if ai != worst_ai]
        n_evicted += 1
log("evictions:", n_evicted,
    "statuses:", Counter(a["status"] for a in assign_rows))

# zero check: no legal violation on any link adjacent to a surviving inserted stop
viol_residual = 0
for tr in tracks:
    ch = tr["chain"]
    for i in range(len(ch) - 1):
        (ka, ia), (kb, ib) = ch[i], ch[i + 1]
        if ka == "S" and kb == "S":
            continue
        ra = tr["stamped"][ia] if ka == "S" else None
        ta = ra.ts_py if ra is not None else assign_rows[ia]["ts"]
        sa_ = ra.site if ra is not None else assign_rows[ia]["site"]
        rb = tr["stamped"][ib] if kb == "S" else None
        tb = rb.ts_py if rb is not None else assign_rows[ib]["ts"]
        sb_ = rb.site if rb is not None else assign_rows[ib]["site"]
        gap = (tb - ta).total_seconds() / 60.0
        if M_leg[sa_, sb_] > max(gap - SERVICE + TOL, MIN_AVAIL) + EPS:
            viol_residual += 1
log("residual inserted-link violations (must be 0):", viol_residual)

# ---------------- 8. Phantom chaining ----------------
leftover = [i for i, a_ in enumerate(assign_rows)
            if a_["status"] in ("INFEASIBLE", "NO_TRIP")]
by_day_lo = defaultdict(list)
for i in leftover:
    by_day_lo[assign_rows[i]["ts"].date()].append(i)
phantoms = []
n_isolated = 0
for day in sorted(by_day_lo):
    idxs = sorted(by_day_lo[day], key=lambda i: assign_rows[i]["ts"])
    chains, cur = [], [idxs[0]]
    for i in idxs[1:]:
        pa, pb = assign_rows[cur[-1]], assign_rows[i]
        gap = (pb["ts"] - pa["ts"]).total_seconds() / 60.0
        if feas_legal(pa["site"], pb["site"], gap):
            cur.append(i)
        else:
            chains.append(cur); cur = [i]
    chains.append(cur)
    kph = 0
    for ch in chains:
        if len(ch) >= PH_MIN:
            kph += 1
            pid = f"PH{day.strftime('%Y%m%d')}-{kph}"
            for i in ch:
                assign_rows[i]["track_id"] = pid
            phantoms.append((pid, day, ch))
        else:
            n_isolated += len(ch)
log("phantom tracks:", len(phantoms), "isolated leftovers:", n_isolated)

# ---------------- 9. Outputs ----------------
def hhmm(ts):
    return ts.strftime("%H:%M")

trips_out = []
tier = Counter()
for tr in tracks:
    stops, kinds = [], []
    for kind, idx in tr["chain"]:
        if kind == "S":
            r = tr["stamped"][idx]
            stops.append([round(r.lat, 6), round(r.lon, 6), str(r.cid), hhmm(r.ts_py), "S"])
            kinds.append(("S", r.ts_py, r.site))
        else:
            a_ = assign_rows[idx]
            stops.append([round(a_["lat"], 6), round(a_["lon"], 6), str(a_["cid"]),
                          hhmm(a_["ts"]), a_["status"]])
            kinds.append((a_["status"], a_["ts"], a_["site"]))
    # speed flags on final stamped-stamped adjacent links failing legal
    flags = []
    for i in range(len(kinds) - 1):
        if kinds[i][0] == "S" and kinds[i + 1][0] == "S":
            gap = (kinds[i + 1][1] - kinds[i][1]).total_seconds() / 60.0
            leg = M_leg[kinds[i][2], kinds[i + 1][2]]
            if leg > max(gap - SERVICE + TOL, MIN_AVAIL) + EPS:
                flags.append([i, round(float(leg), 2), round(gap, 1)])
    m = ident_meta[tr["base"]]
    t_first = kinds[0][1]; t_last = kinds[-1][1]
    n_i = sum(1 for k in kinds if k[0] == "I")
    n_l = sum(1 for k in kinds if k[0] == "L")
    tier["S"] += sum(1 for k in kinds if k[0] == "S")
    tier["I"] += n_i; tier["L"] += n_l
    rec = {
        "id": tr["tid"], "base_id": tr["base"], "part": tr["part"],
        "n_parts": tr["n_parts"], "merged": tr["merged"],
        "speed_flags": flags,
        "continues_from": (continues_from.get(tr["base"])
                           if tr["part"] in ("", "a") else None),
        "date": tr["stamped"][0].ts_py.strftime("%Y-%m-%d"),
        "start": hhmm(t_first), "end": hhmm(t_last),
        "dur_h": round((t_last - t_first).total_seconds() / 3600.0, 2),
        "rota": m["rota"], "frac": m["frac"],
        "n_bins": len(tr["stamped"]), "n_inferred": n_i, "n_lowconf": n_l,
        "km_rec": m["km_rec"], "kg": m["kg"],
        "stops": stops,
    }
    if tr["verdict"] in ("batch-entry", "multi-vehicle"):
        rec["verdict"] = tr["verdict"]
    trips_out.append(rec)

with open(OUT + "/trips_v7.json", "w", encoding="utf-8") as f:
    json.dump(trips_out, f, ensure_ascii=False, separators=(",", ":"), default=np_default)
log("trips_v7.json:", len(trips_out), "tracks; stop tiers:", dict(tier))

ph_out = []
for pid, day, ch in phantoms:
    rows = [assign_rows[i] for i in ch]
    mats = Counter()
    stops = []
    for a_ in rows:
        stops.append([round(a_["lat"], 6), round(a_["lon"], 6), str(a_["cid"]),
                      hhmm(a_["ts"]), "P"])
    ph_out.append({
        "id": pid, "date": day.strftime("%Y-%m-%d"),
        "start": hhmm(rows[0]["ts"]), "end": hhmm(rows[-1]["ts"]),
        "dur_h": round((rows[-1]["ts"] - rows[0]["ts"]).total_seconds() / 3600.0, 2),
        "n_bins": len(rows), "frac": "Phantom", "stops": stops,
    })
with open(OUT + "/phantom_tracks_v7.json", "w", encoding="utf-8") as f:
    json.dump(ph_out, f, ensure_ascii=False, separators=(",", ":"), default=np_default)

# assignments parquet: every loose reading (incl. loose duplicates as DUPLICATE)
adf = pd.DataFrame([{k: v for k, v in a_.items() if k != "site"}
                    for a_ in assign_rows])
loose_dups = dropped_dup[~dropped_dup["is_event"]]
if len(loose_dups):
    ddf = pd.DataFrame({
        "cid": loose_dups["cid"].values, "ts": loose_dups["ts"].values,
        "lat": loose_dups["lat"].values, "lon": loose_dups["lon"].values,
        "fill": loose_dups["fill"].values, "status": "DUPLICATE",
        "track_id": None, "alt_track_id": None, "p_best": np.nan,
        "insert_after_stop": pd.array([pd.NA] * len(loose_dups), dtype="Int64"),
    })
    adf = pd.concat([adf, ddf], ignore_index=True)
adf["insert_after_stop"] = adf["insert_after_stop"].astype("Int64")
adf.to_parquet(OUT + "/assignments_v7.parquet", index=False)

# dropped parquet: duplicates (stamped + loose) + evicted
drop_recs = [{"cid": r.cid, "ts": r.ts, "idrecolha": (r.idr if r.is_event else None),
              "reason": "DUPLICATE", "track_id": None}
             for r in dropped_dup.itertuples(index=False)]
for a_ in assign_rows:
    if a_["status"] == "EVICTED_CONFLICT":
        drop_recs.append({"cid": a_["cid"], "ts": a_["ts"], "idrecolha": None,
                          "reason": "EVICTED_CONFLICT", "track_id": a_["track_id"]})
pd.DataFrame(drop_recs).to_parquet(OUT + "/dropped_v7.parquet", index=False)

# ---------------- 10. Stats + accounting ----------------
status_counts = Counter(a_["status"] for a_ in assign_rows)
n_s_stops = tier["S"]
n_dup_events = int(dropped_dup["is_event"].sum())
n_dup_loose = int(len(dropped_dup) - n_dup_events)
accounted = (n_s_stops + n_dup_events + n_pre + len(assign_rows) + n_dup_loose)
kg_total = sum(m["kg"] for m in ident_meta.values() if m["kg"] is not None)
km_total = sum(m["km_rec"] for m in ident_meta.values() if m["km_rec"] is not None)
stats = {
    "raw_rows": int(n_raw),
    "accounting": {
        "stamped_stops_in_tracks": int(n_s_stops),
        "stamped_duplicates_dropped": n_dup_events,
        "pre_readings": n_pre,
        "loose_readings_assessed": len(assign_rows),
        "loose_duplicates_dropped": n_dup_loose,
        "total_accounted": int(accounted),
        "all_rows_accounted": bool(accounted == n_raw),
    },
    "identifiers": len(ident_meta),
    "tracks": len(trips_out),
    "track_verdicts": dict(verdict_counts),
    "split_identifiers": int(verdict_counts["batch-entry"] + verdict_counts["multi-vehicle"]),
    "merged_single_tracks": int(verdict_counts["single-merged"]),
    "speed_flagged_junctions": int(sum(len(t["speed_flags"]) for t in trips_out)),
    "continuations": {"pairs_found": len(cont_pairs),
                      "later_trips_annotated": len(continues_from),
                      "criteria": "same end/start date, same rota prefix (material if "
                                  "rota missing), 0<=gap<=20min, last-first bins <=3km"},
    "assignment_status_counts": {k: int(v) for k, v in status_counts.items()},
    "tier_stop_counts": {k: int(v) for k, v in tier.items()},
    "evictions": int(n_evicted),
    "residual_inserted_link_violations": int(viol_residual),
    "phantoms": {"tracks": len(ph_out),
                 "stops_in_tracks": int(sum(p["n_bins"] for p in ph_out)),
                 "isolated": int(n_isolated)},
    "kg_total_once_per_identifier": float(kg_total),
    "km_rec_total_once_per_identifier": float(km_total),
    "params": {
        "service_med_min": SERVICE, "tol_min": TOL, "min_avail_min": MIN_AVAIL,
        "ceiling_service_min": CEIL_SERVICE, "window_min": WINDOW_MIN,
        "p_low_threshold": P_LOW, "batch_gap_min": BATCH_GAP, "batch_km": BATCH_KM,
        "phantom_min_stops": PH_MIN,
        "feasible_legal": "legal_min <= max(gap - service_med + tol, 0.5)",
        "feasible_ceiling": "ceiling_min <= max(gap - 0.5, 0.5)",
        "engine": "W5 site_travel.parquet (truck-legal + ceiling road times); no flat speed",
        "p_best": "altScore/(best+alt), score = legal-min detour cost of insertion",
    },
}
with open(OUT + "/rebuild_stats.json", "w", encoding="utf-8") as f:
    json.dump(stats, f, ensure_ascii=False, indent=2, default=np_default)
log("ACCOUNTING", accounted, "of", n_raw, "OK" if accounted == n_raw else "MISMATCH")
log("done")
