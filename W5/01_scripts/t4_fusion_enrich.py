# TASK F (T4 fusion) - Enrich trips_v7 with CLEANED sensors; source tags.
# Inputs : trips_v7.json + phantom_tracks_v7.json + sensor_clean.parquet +
#          sensor_removed.parquet + sensor_drops_v2.parquet + raw_collections.parquet
# Stops -> 10 elements [lat,lon,cid,hhmm,type,fill,est_kg,mat,sensor_pct,src]
#   fill       : S = pre-emptying reading (<=15 min prior, raw); I/L/P = own fill
#   est_kg     : mid-density own material (P32/C75/G300 kg/m3 x litres x fill)
#   mat        : bin material letter (P/C/G)
#   sensor_pct : nearest CLEAN reading +/-3h as pct_of_era_ceiling (rounded);
#                if the nearest +/-3h reading is a removed NEGATIVE, raw value kept
#   src        : S = 'DS' if a drops_v2 event for that cid overlaps [ts-90m,ts+90m]
#                else 'D'; I/L/P = 'D'
# Per trip : sensor_events = unmatched drops_v2 on trip date(s) at bins within
#            300 m of any stop -> [lat,lon,cid,startHH:MM,endHH:MM,pct_before,conf]
#            evidence_mix {d_only, ds, s_only}
# Trip est : est_lo/mid/hi strict band (S stops); est2_mid = strict + same-material
#            observed capped at identifier kg (once per identifier); wshare/wshare2
# Outputs  : trips_v7_enriched.json, trips_index_v7.json (card fields incl
#            continues_from, flagged, evidence_mix, circuit_id null placeholder)
import json, math, time, bisect, statistics
from collections import defaultdict, Counter
from datetime import datetime, timedelta

import duckdb
import numpy as np
import pandas as pd

ROOT = r"C:/Users/esmae/Desktop/phd Esmaeil/THESIS CLAUDE"
W5 = f"{ROOT}/W5/02_data_work"
RAWC = f"{ROOT}/Brain/03_db/parquet/raw_collections.parquet"

DENS = {"P": (25, 32, 40), "C": (50, 75, 100), "G": (250, 300, 350)}
DENS_MID = {"P": 32, "C": 75, "G": 300}
FR2L = {"Packaging": "P", "Paper/card": "C", "Glass": "G"}
L2FR = {v: k for k, v in FR2L.items()}
SENS_WIN = 3 * 3600          # +/-3h nearest sensor reading
DS_WIN = 90 * 60             # +/-90 min drop-vs-stop overlap
EVT_RADIUS_KM = 0.3          # sensor_events within 300 m of any stop

t0 = time.time()
log = lambda *a: print(f"[{time.time()-t0:5.1f}s]", *a, flush=True)

# ---------------- 1. worlds ----------------
trips = json.load(open(f"{W5}/trips_v7.json", encoding="utf-8"))
phantoms = json.load(open(f"{W5}/phantom_tracks_v7.json", encoding="utf-8"))
world = trips + phantoms
log("trips", len(trips), "phantoms", len(phantoms))

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
sdt = {str(t["id"]): stop_dates(t) for t in world}

# ---------------- 2. raw-collections lookups ----------------
con = duckdb.connect()
rows = con.sql(f"""
  SELECT trim(idcontentor) cid, TRY_CAST("Data da leitura" AS TIMESTAMP) ts,
         TRY_CAST(replace("Enchimento", ',', '.') AS DOUBLE) fill,
         (idrecolha IS NOT NULL AND trim(idrecolha) NOT IN ('', '0')) is_event
  FROM '{RAWC}' WHERE "Data da leitura" IS NOT NULL ORDER BY cid, ts
""").df()
prefill, readfill, prev = {}, defaultdict(list), {}
for r in rows.itertuples():
    key = (r.cid, r.ts.strftime("%Y-%m-%d %H:%M"))
    if r.is_event:
        p = prev.get(r.cid)
        if p is not None and (r.ts - p[0]).total_seconds() <= 900 \
           and p[1] is not None and not math.isnan(p[1]) and p[1] >= 0:
            prefill[key] = int(round(p[1]))
    else:
        readfill[key].append(int(round(r.fill))
                             if r.fill is not None and not math.isnan(r.fill) else None)
    prev[r.cid] = (r.ts, r.fill)
del rows

bins = con.sql(f"""
  SELECT trim(idcontentor) cid,
         MAX(TRY_CAST("Volume do tipo de contentor" AS INT)) vol,
         ANY_VALUE(CASE WHEN description LIKE '%Vidro%' THEN 'G'
                        WHEN description LIKE '%papel%' THEN 'C' ELSE 'P' END) fl
  FROM '{RAWC}' GROUP BY 1
""").df()
VOL = {r.cid: (int(r.vol or 2500), r.fl) for r in bins.itertuples()}

# representative coordinate per bin (most frequent raw lat/lon)
bc = con.sql(f"""
  SELECT cid, lat, lon FROM (
    SELECT trim(idcontentor) cid,
           TRY_CAST(replace(Latitude, ',', '.') AS DOUBLE) lat,
           TRY_CAST(replace(Longitude, ',', '.') AS DOUBLE) lon,
           ROW_NUMBER() OVER (PARTITION BY trim(idcontentor) ORDER BY COUNT(*) DESC) rn
    FROM '{RAWC}' WHERE Latitude IS NOT NULL AND Longitude IS NOT NULL
    GROUP BY 1, 2, 3) WHERE rn = 1
""").df()
BINXY = {r.cid: (round(float(r.lat), 6), round(float(r.lon), 6))
         for r in bc.itertuples() if not (math.isnan(r.lat) or math.isnan(r.lon))}
log("collections lookups: prefill", len(prefill), "bins", len(VOL), "coords", len(BINXY))

# ---------------- 3. clean sensor arrays (+ removed negatives) ----------------
cl = pd.read_parquet(f"{W5}/sensor_clean.parquet", columns=["cid", "ts", "pct"])
rm = pd.read_parquet(f"{W5}/sensor_removed.parquet", columns=["cid", "ts", "fill", "reason"])
rm = rm[rm["fill"] < 0]                                # negative error codes only
cl_v = np.round(cl["pct"].values).astype("float64")    # pct >= 0
comb = pd.DataFrame({
    "cid": np.concatenate([cl["cid"].values, rm["cid"].values]),
    "e": np.concatenate([cl["ts"].values.astype("datetime64[s]").astype("int64"),
                         rm["ts"].values.astype("datetime64[s]").astype("int64")]),
    "v": np.concatenate([cl_v, rm["fill"].values]),
}).sort_values(["cid", "e"], kind="mergesort")
S_E, S_V = {}, {}
for cid, g in comb.groupby("cid", sort=False):
    S_E[cid] = g["e"].values; S_V[cid] = g["v"].values
del cl, rm, comb

def sensor_pct(cid, eq):
    e = S_E.get(cid)
    if e is None: return None
    i = int(np.searchsorted(e, eq))
    best, bd = None, SENS_WIN + 1
    for j in (i - 1, i):
        if 0 <= j < len(e):
            d = abs(int(e[j]) - eq)
            if d < bd: bd, best = d, j
    if best is None or bd > SENS_WIN: return None
    v = S_V[cid][best]
    return int(v) if v < 0 else int(round(v))

# ---------------- 4. drops_v2 indexes ----------------
dr = pd.read_parquet(f"{W5}/sensor_drops_v2.parquet")
dr = dr.reset_index(drop=True)
d_cid = dr["cid"].values
d_tb = dr["t_before"].values.astype("datetime64[s]").astype("int64")
d_ta = dr["t_after"].values.astype("datetime64[s]").astype("int64")
d_pct = dr["pct_before"].values
d_conf = dr["confidence"].values
drops_by_cid = defaultdict(list)          # cid -> [drop idx]
drops_by_day = defaultdict(list)          # date -> [drop idx] (window touches day)
for i in range(len(dr)):
    drops_by_cid[d_cid[i]].append(i)
    day = datetime.utcfromtimestamp(int(d_tb[i])).date()
    last = datetime.utcfromtimestamp(int(d_ta[i])).date()
    while day <= last:
        drops_by_day[day].append(i); day += timedelta(days=1)
log("drops_v2", len(dr), "bins with drops", len(drops_by_cid))

def epoch(dt):        # naive-consistent epoch (same convention as int64 ns // 1e9)
    return int((dt - datetime(1970, 1, 1)).total_seconds())

# ---------------- 5. enrich stops ----------------
matched_drops = set()
hit_s = hit_i = miss = n_ds = n_sens_valid = n_sens_neg = 0
est = {}
for t in world:
    tid = str(t["id"])
    ph = t.get("frac") == "Phantom"
    if ph:
        mats = Counter(VOL.get(str(s[2]), (None, "P"))[1] for s in t["stops"])
        tl = mats.most_common(1)[0][0]
        t["mat_hint"] = L2FR.get(tl, "Packaging")
    else:
        tl = FR2L.get(t.get("frac"), "P")
    ns = []
    for s, dt_ in zip(t["stops"], sdt[tid]):
        cid = str(s[2]); typ = s[4]
        key = (cid, dt_.strftime("%Y-%m-%d %H:%M"))
        if typ == "S":
            f = prefill.get(key)
            hit_s += f is not None
        else:
            vals = readfill.get(key)
            f = vals.pop(0) if vals else None
            hit_i += f is not None
        if f is None: miss += 1
        vol, fl = VOL.get(cid, (2500, tl))
        eq = epoch(dt_)
        sv = sensor_pct(cid, eq)
        if sv is not None:
            n_sens_neg += sv < 0; n_sens_valid += sv >= 0
        src = "D"
        if typ == "S":
            for di in drops_by_cid.get(cid, ()):
                if d_tb[di] <= eq + DS_WIN and d_ta[di] >= eq - DS_WIN:
                    src = "DS"; matched_drops.add(di)
        n_ds += src == "DS"
        ns.append([s[0], s[1], s[2], s[3], typ, f, None, fl, sv, src])
    # strict band (S stops, mid fill fallback = trip median of known fills)
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
            if x[4] in ("I", "P") and fl == tl and x[5] is not None and x[5] >= 0:
                obs += vol / 1000 * x[5] / 100 * DENS_MID[fl]
    est[tid] = (lo, mid, hi, obs)
    t["stops"] = ns
log(f"fills: S {hit_s}, I/L/P {hit_i}, missing {miss} | sensor {n_sens_valid} valid"
    f" + {n_sens_neg} err | DS stops {n_ds} | matched drops {len(matched_drops)}")

# ---------------- 6. per-trip sensor_events (S-only recovered emptyings) -----
def hhmm_e(e):
    return datetime.utcfromtimestamp(int(e)).strftime("%H:%M")

n_events = 0
for t in world:
    tid = str(t["id"])
    days = sorted({d.date() for d in sdt[tid]})
    cand = set()
    for day in days:
        cand.update(drops_by_day.get(day, ()))
    cand -= matched_drops
    evs = []
    if cand:
        st = t["stops"]
        slat = np.array([x[0] for x in st]); slon = np.array([x[1] for x in st])
        coslat = np.cos(np.radians(slat.mean()))
        for di in sorted(cand, key=lambda i: int(d_tb[i])):
            xy = BINXY.get(d_cid[di])
            if xy is None: continue
            dk = np.hypot((xy[0] - slat) * 110.574,
                          (xy[1] - slon) * 111.320 * coslat)
            if dk.min() <= EVT_RADIUS_KM:
                pb = None if math.isnan(d_pct[di]) else round(float(d_pct[di]), 1)
                evs.append([xy[0], xy[1], str(d_cid[di]), hhmm_e(d_tb[di]),
                            hhmm_e(d_ta[di]), pb, str(d_conf[di])])
    t["sensor_events"] = evs
    n_events += len(evs)
    mix = Counter(x[9] for x in t["stops"])
    t["evidence_mix"] = {"d_only": int(mix.get("D", 0)), "ds": int(mix.get("DS", 0)),
                         "s_only": len(evs)}
log("sensor_events attached", n_events, "over",
    sum(1 for t in world if t["sensor_events"]), "tracks")

# ---------------- 7. identifier cap + index ----------------
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
        "continues_from": t.get("continues_from"),
        "evidence_mix": t["evidence_mix"],
        "circuit_id": None,
        "est_lo": round(lo), "est_mid": round(mid), "est_hi": round(hi),
    }
    if t.get("verdict"):
        m["verdict"] = t["verdict"]
    if ph:
        m["est2_mid"] = round(obs); m["capped"] = False
        m["wshare"] = m["wshare2"] = None
        m["mat_hint"] = t["mat_hint"]
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

def np_default(o):
    if isinstance(o, np.floating): return float(o)
    if isinstance(o, np.integer): return int(o)
    if isinstance(o, np.bool_): return bool(o)
    raise TypeError(f"not serializable: {type(o)}")

s1 = json.dumps(world, ensure_ascii=False, separators=(",", ":"), default=np_default)
open(f"{W5}/trips_v7_enriched.json", "w", encoding="utf-8").write(s1)
s2 = json.dumps(index, ensure_ascii=False, separators=(",", ":"), default=np_default)
open(f"{W5}/trips_index_v7.json", "w", encoding="utf-8").write(s2)

report = {
    "tracks_total": len(world), "trips": len(trips), "phantoms": len(phantoms),
    "ds_corroborated_stops": int(n_ds),
    "drops_matched_to_stops": len(matched_drops),
    "s_only_events_attached": int(n_events),
    "tracks_with_s_only_events": int(sum(1 for t in world if t["sensor_events"])),
    "sensor_pct_valid": int(n_sens_valid), "sensor_pct_neg_codes": int(n_sens_neg),
    "fills": {"S_prefill": int(hit_s), "ILP_own": int(hit_i), "missing": int(miss)},
    "capped_tracks": int(n_capped),
    "index_records": len(index),
    "enriched_MB": round(len(s1.encode()) / 1e6, 2),
    "index_MB": round(len(s2.encode()) / 1e6, 2),
}
print(json.dumps(report, indent=2), flush=True)
log("done")
