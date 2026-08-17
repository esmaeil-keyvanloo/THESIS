"""W2 TASK A - Assign unstamped driver readings to vehicle tracks by time + proximity.

Loose reading = driver row with no idrecolha stamp AND not a pre-reading
(pre-reading = next reading on the same bin is an event row <= 15 min later,
exactly as in build_trips_excel.py).

v5: input trips_v5_seg.json (ALL fractions incl. glass).
Outputs:
  W2/02_data_work/reading_assignments_v5.parquet
  W2/02_data_work/trips_v5.json
  W2/02_data_work/assignment_stats_v5.json
"""
import duckdb, json, math, bisect
from collections import defaultdict
from datetime import datetime, timedelta
from statistics import median
import pandas as pd

BASE = r"C:/Users/esmae/Desktop/phd Esmaeil/THESIS CLAUDE"
PARQ = f"{BASE}/Brain/03_db/parquet/raw_collections.parquet"
V3 = f"{BASE}/W2/02_data_work/trips_v5_seg.json"
OUT_ASSIGN = f"{BASE}/W2/02_data_work/reading_assignments_v5.parquet"
OUT_V4 = f"{BASE}/W2/02_data_work/trips_v5.json"
OUT_STATS = f"{BASE}/W2/02_data_work/assignment_stats_v5.json"

R_EARTH = 6371.0088
DETOUR = 1.3
SERVICE_MIN = 2.0
MIN_GAP_MIN = 0.5
VMAX = 60.0
WINDOW_MIN = 30

def hav_km(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    h = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R_EARTH * math.asin(math.sqrt(h))

def implied_speed(lat1, lon1, t1, lat2, lon2, t2):
    """km/h for leg between two points; haversine x detour, minus service, min gap."""
    dist = hav_km(lat1, lon1, lat2, lon2) * DETOUR
    gap_min = max(abs((t2 - t1).total_seconds()) / 60.0 - SERVICE_MIN, MIN_GAP_MIN)
    return dist / (gap_min / 60.0)

def pfloat(s):
    if s is None:
        return None
    s = str(s).strip().replace(",", ".")
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None

# ---------------- 1. loose readings ----------------
con = duckdb.connect()
df = con.sql(f"""
  SELECT trim(idcontentor) AS cid,
         TRY_CAST("Data da leitura" AS TIMESTAMP) AS ts,
         Enchimento AS fill_raw, Latitude AS lat_raw, Longitude AS lon_raw,
         trim(idrecolha) AS idr
  FROM '{PARQ}'
  ORDER BY ts
""").df()
df["is_event"] = df["idr"].notna() & (df["idr"] != "") & (df["idr"] != "0")
print("rows:", len(df), "events:", int(df.is_event.sum()))

# pre-reading exclusion, exactly as build_trips_excel.py (same ts-sorted order, groupby cid)
pre = pd.Series(False, index=df.index)
for cid, g in df.groupby("cid", sort=False):
    idx = g.index.to_list()
    for pos, i in enumerate(idx):
        if df.at[i, "is_event"] or pos + 1 >= len(idx):
            continue
        j = idx[pos + 1]
        if df.at[j, "is_event"] and (df.at[j, "ts"] - df.at[i, "ts"]).total_seconds() <= 900:
            pre[i] = True
print("pre-readings excluded:", int(pre.sum()))

loose = df[~df.is_event & ~pre & df.ts.notna()].copy()
print("loose readings:", len(loose))

# ---------------- 2. tracks with absolute datetimes ----------------
tracks = json.load(open(V3, encoding="utf-8"))
by_date = defaultdict(list)  # date-iso -> list of track dicts (internal)
tinfo = {}
for t in tracks:
    d0 = datetime.strptime(t["date"], "%Y-%m-%d")
    start_dt = d0 + timedelta(hours=int(t["start"][:2]), minutes=int(t["start"][3:]))
    end_dt = d0 + timedelta(hours=int(t["end"][:2]), minutes=int(t["end"][3:]))
    if end_dt < start_dt:
        end_dt += timedelta(days=1)
    # stop datetimes: sequential, wrap past midnight when jump back > 12 h
    sdts = []
    prev = start_dt
    day_off = timedelta(0)
    for s in t["stops"]:
        cur = d0 + day_off + timedelta(hours=int(s[3][:2]), minutes=int(s[3][3:]))
        while cur < prev - timedelta(hours=12):
            cur += timedelta(days=1)
            day_off += timedelta(days=1)
        sdts.append(cur)
        prev = max(prev, cur)
    mono = []  # cummax for bisect (tolerates tiny local inversions)
    m = sdts[0]
    for x in sdts:
        m = max(m, x)
        mono.append(m)
    w0 = start_dt - timedelta(minutes=WINDOW_MIN)
    w1 = end_dt + timedelta(minutes=WINDOW_MIN)
    tinfo[t["id"]] = dict(t=t, w0=w0, w1=w1, sdts=sdts, mono=mono)
    d = w0.date()
    while d <= w1.date():
        by_date[d.isoformat()].append(t["id"])
        d += timedelta(days=1)

# ---------------- 3. assignment ----------------
rows = []
for r in loose.itertuples(index=False):
    ts = r.ts.to_pydatetime()
    lat, lon = pfloat(r.lat_raw), pfloat(r.lon_raw)
    fill = pfloat(r.fill_raw)
    if lat is None or lon is None:
        rows.append((r.cid, ts, lat, lon, fill, "INFEASIBLE", None, None, None, None))
        continue
    cands = []
    for tid in by_date.get(ts.date().isoformat(), ()):  # ids registered per covered date
        ti = tinfo[tid]
        if not (ti["w0"] <= ts <= ti["w1"]):
            continue
        stops = ti["t"]["stops"]
        p = bisect.bisect_right(ti["mono"], ts)  # insertion point: after stop p (1-based), 0 = before first
        speeds = []
        if p > 0:
            s = stops[p - 1]
            speeds.append(implied_speed(s[0], s[1], ti["sdts"][p - 1], lat, lon, ts))
        if p < len(stops):
            s = stops[p]
            speeds.append(implied_speed(lat, lon, ts, s[0], s[1], ti["sdts"][p]))
        if all(v <= VMAX for v in speeds):
            cands.append((max(speeds), str(tid), p))
    if not cands:
        # distinguish: any track window covered ts at all?
        had_window = any(tinfo[tid]["w0"] <= ts <= tinfo[tid]["w1"]
                         for tid in by_date.get(ts.date().isoformat(), ()))
        status = "INFEASIBLE" if had_window else "NO_TRIP_RUNNING"
        rows.append((r.cid, ts, lat, lon, fill, status, None, None, None, None))
        continue
    cands.sort(key=lambda c: (c[0], c[1]))
    best = cands[0]
    if len(cands) > 1 and cands[1][0] < 1.5 * best[0]:
        rows.append((r.cid, ts, lat, lon, fill, "AMBIGUOUS",
                     best[1], cands[1][1], best[2], best[0]))
    else:
        rows.append((r.cid, ts, lat, lon, fill, "ASSIGNED",
                     best[1], None, best[2], best[0]))

adf = pd.DataFrame(rows, columns=["cid", "ts", "lat", "lon", "fill", "status",
                                  "track_id", "alt_track_id", "insert_after_stop", "score"])
adf["insert_after_stop"] = adf["insert_after_stop"].astype("Int64")
adf.drop(columns=["score"]).to_parquet(OUT_ASSIGN, index=False)
print(adf.status.value_counts())

# ---------------- 4. trips_v4 ----------------
ins_by_track = defaultdict(list)  # tid -> [(pos, ts, lat, lon, cid)]
for r in adf[adf.status == "ASSIGNED"].itertuples(index=False):
    ins_by_track[r.track_id].append((int(r.insert_after_stop), r.ts, r.lat, r.lon, r.cid))

v4 = []
for t in tracks:
    nt = dict(t)
    ins = sorted(ins_by_track.get(str(t["id"]), []), key=lambda x: (x[0], x[1]))
    new_stops = []
    k = 0
    for i, s in enumerate(t["stops"]):
        while k < len(ins) and ins[k][0] <= i:
            _, its, ilat, ilon, icid = ins[k]
            new_stops.append([round(ilat, 6), round(ilon, 6), str(icid), its.strftime("%H:%M"), "I"])
            k += 1
        new_stops.append([s[0], s[1], s[2], s[3], "S"])
    while k < len(ins):
        _, its, ilat, ilon, icid = ins[k]
        new_stops.append([round(ilat, 6), round(ilon, 6), str(icid), its.strftime("%H:%M"), "I"])
        k += 1
    nt["stops"] = new_stops
    nt["n_inferred"] = len(ins)
    km = sum(hav_km(new_stops[i][0], new_stops[i][1], new_stops[i + 1][0], new_stops[i + 1][1])
             for i in range(len(new_stops) - 1))
    nt["km_line"] = round(km, 1) if len(new_stops) > 1 else 0
    v4.append(nt)

with open(OUT_V4, "w", encoding="utf-8") as f:
    json.dump(v4, f, ensure_ascii=False, separators=(",", ":"))
print("trips_v4 tracks:", len(v4), "inserted stops:", sum(t["n_inferred"] for t in v4))

# ---------------- 5. stats ----------------
total = len(adf)
by_status = adf.status.value_counts().to_dict()
per_year = {}
for y, g in adf.groupby(adf.ts.dt.year):
    per_year[str(int(y))] = {"total": int(len(g)),
                             **{s: int(n) for s, n in g.status.value_counts().items()}}
scores = adf.loc[adf.status == "ASSIGNED", "score"].dropna().tolist()
stats = {
    "loose_readings_total": int(total),
    "counts_by_status": {k: int(v) for k, v in by_status.items()},
    "pct_by_status": {k: round(100.0 * v / total, 2) for k, v in by_status.items()},
    "per_year": per_year,
    "median_score_assigned_kmh": round(median(scores), 2) if scores else None,
    "params": {"window_min": WINDOW_MIN, "vmax_kmh": VMAX, "detour": DETOUR,
               "service_min": SERVICE_MIN, "min_gap_min": MIN_GAP_MIN,
               "ambiguity_ratio": 1.5},
}
with open(OUT_STATS, "w", encoding="utf-8") as f:
    json.dump(stats, f, ensure_ascii=False, indent=2)
print(json.dumps(stats["counts_by_status"]))
print("median score:", stats["median_score_assigned_kmh"])
