# T6 (Task I) - Three W5 workbooks + frozen master parquet.
#   1. Driver_Data_W5.xlsx   : Clean (by trip) / Dropped / METHOD
#   2. Sensor_Data_W5.xlsx   : Clean readings / Drop events / Removed / METHOD
#   3. Combined_Master_W5.xlsx: Events / Dropped (both files) / METHOD
#      + Brain/03_db/parquet/master_events_w5.parquet (same rows as Events)
# Classification mirrors t2_rebuild_v7.py exactly (dup mask, pre-readings,
# event/loose ordering) so every raw row maps to its v7 trip deterministically.
import json, math, time
from collections import defaultdict, Counter, deque
import numpy as np
import pandas as pd
import xlsxwriter

ROOT = r"C:/Users/esmae/Desktop/phd Esmaeil/THESIS CLAUDE"
W5 = f"{ROOT}/W5/02_data_work"
OUTDIR = f"{ROOT}/W5/03_outputs/tables"
PARQ = f"{ROOT}/Brain/03_db/parquet"
import os
os.makedirs(OUTDIR, exist_ok=True)

t0 = time.time()
log = lambda *a: print(f"[{time.time()-t0:6.1f}s]", *a, flush=True)

RAW_COLS = ["idcontentor", "Matricula do contentor", "Tipo de contentor",
            "Volume do tipo de contentor", "description", "Distrito", "Concelho",
            "Freguesia", "Localidade", "Latitude", "Longitude", "Data da leitura",
            "Enchimento", "idrecolha", "Rota", "Data de \u00ednicio", "Data de fim",
            "Km totais", "Peso total"]
MATW = {"P": "Packaging", "C": "Paper/card", "G": "Glass"}

# ---------------- 1. raw driver rows, t2-identical keys ----------------
raw = pd.read_parquet(f"{PARQ}/raw_collections.parquet")   # pyarrow file order
n_raw = len(raw)
assert n_raw == 264817
raw["_rid"] = np.arange(1, n_raw + 1)
raw["_cid"] = raw["idcontentor"].str.strip()
raw["_ts"] = pd.to_datetime(raw["Data da leitura"])
raw["_idr"] = raw["idrecolha"].str.strip()
raw["_ev"] = raw["_idr"].notna() & (raw["_idr"] != "") & (raw["_idr"] != "0")

srt = raw.sort_values(["_cid", "_ts", "_ev", "_rid"],
                      ascending=[True, True, False, True], kind="mergesort")
dupmask = srt.duplicated(["_cid", "_ts"], keep="first")
dup_rows = srt[dupmask]                                    # dropped duplicates
d = srt[~dupmask].copy()
log("duplicates:", len(dup_rows), "(events:", int(dup_rows._ev.sum()), ")")

d = d.sort_values(["_cid", "_ts", "_rid"], kind="mergesort").reset_index(drop=True)
same_next = d["_cid"].shift(-1) == d["_cid"]
next_ev = d["_ev"].shift(-1, fill_value=False)
next_gap = (d["_ts"].shift(-1) - d["_ts"]).dt.total_seconds()
d["_pre"] = (~d["_ev"]) & same_next & next_ev & (next_gap <= 900)
d["_next_rid"] = d["_rid"].shift(-1).astype("Int64")       # pre -> its event row
log("pre-readings:", int(d._pre.sum()))

events = d[d["_ev"]].sort_values(["_idr", "_ts", "_rid"], kind="mergesort")
loose = d[(~d["_ev"]) & (~d["_pre"])].sort_values(["_ts", "_rid"], kind="mergesort")
log("events:", len(events), "loose:", len(loose))

# ---------------- 2. v7 artifacts ----------------
world = json.load(open(f"{W5}/trips_v7_enriched.json", encoding="utf-8"))
adf = pd.read_parquet(f"{W5}/assignments_v7.parquet")
ddf = pd.read_parquet(f"{W5}/dropped_v7.parquet")

# positional identity: assignments rows [0:len(loose)] == loose in (ts,rid) order
nA = len(loose)
assert (adf["cid"].values[:nA] == loose["_cid"].values).all()
assert (adf["ts"].values[:nA].astype("datetime64[us]")
        == loose["_ts"].values.astype("datetime64[us]")).all()
log("assignments_v7 positional identity verified for", nA, "loose rows")

# stop lookup tables from enriched trips
tmeta, base_q, il_lut, p_lut, binmat = {}, defaultdict(deque), {}, {}, {}
for t in world:
    tid = str(t["id"])
    tmeta[tid] = (t["date"], t["start"], tid)
    for i, s in enumerate(t["stops"]):
        enr = (i + 1, s[5], s[6], s[7], s[8], s[9])  # stop_no, fill, est, mat, sens, src
        typ = s[4]
        cid = str(s[2])
        if s[7] and cid not in binmat:
            binmat[cid] = s[7]
        if typ == "S":
            base_q[str(t["base_id"])].append((tid, cid, s[3]) + enr)
        elif typ in ("I", "L"):
            il_lut.setdefault((tid, cid, s[3], typ), deque()).append(enr)
        else:  # P
            p_lut.setdefault((tid, cid, s[3]), deque()).append(enr)
log("trips:", len(world), "S queued:", sum(len(v) for v in base_q.values()))

def desc_mat(desc):
    if not isinstance(desc, str):
        return None
    if "Vidro" in desc: return "G"
    if "papel" in desc or "Papel" in desc: return "C"
    return "P"

# ---------------- 3. classify every raw row ----------------
# per-rid: (trip_id, stop_no, row_type, src, fill, sens, est, mat)
info = {}
mism = 0
for e_idr, e_cid, e_ts, e_rid in zip(events["_idr"].values, events["_cid"].values,
                                     events["_ts"].values, events["_rid"].values):
    q = base_q[e_idr]
    tid, scid, hhmm, stop_no, fill, est, mat, sens, src = q.popleft()
    if scid != e_cid or hhmm != pd.Timestamp(e_ts).strftime("%H:%M"):
        mism += 1
    info[int(e_rid)] = (tid, stop_no, "S", src, fill, sens, est, mat)
assert mism == 0, f"S-stop mismatches: {mism}"
assert all(len(q) == 0 for q in base_q.values())
log("S rows matched:", len(events))

loose_rids = loose["_rid"].values
a_stat = adf["status"].values
a_trk = adf["track_id"].values
a_cid = adf["cid"].values
a_hhmm = adf["ts"].dt.strftime("%H:%M").values
counts = Counter()
evicted_rids = []
for i in range(nA):
    rid = int(loose_rids[i]); st = a_stat[i]
    r_cid = a_cid[i]
    hhmm = a_hhmm[i]
    if st in ("I", "L"):
        tid = str(a_trk[i])
        q = il_lut.get((tid, r_cid, hhmm, st))
        enr = q.popleft() if q else (None,) * 6
        info[rid] = (tid, enr[0], st, enr[5] or "D", enr[1], enr[4], enr[2], enr[3])
        counts[st] += 1
    elif st == "EVICTED_CONFLICT":
        evicted_rids.append((rid, a_trk[i] if isinstance(a_trk[i], str) else ""))
        counts["EVICTED"] += 1
    elif isinstance(a_trk[i], str) and a_trk[i]:  # INFEASIBLE/NO_TRIP chained into a phantom track
        tid = str(a_trk[i])
        q = p_lut.get((tid, r_cid, hhmm))
        enr = q.popleft() if q else (None,) * 6
        info[rid] = (tid, enr[0], "P", enr[5] or "D", enr[1], enr[4], enr[2], enr[3])
        counts["P"] += 1
    else:
        info[rid] = ("", None, "iso", "", None, None, None, None)
        counts["iso"] += 1
log("loose classified:", dict(counts))
unmatched_il = sum(1 for v in info.values() if v[2] in ("I", "L", "P") and v[1] is None)
log("I/L/P rows without lut hit (should be 0):", unmatched_il)
assert unmatched_il == 0, "stop lookup failed for some I/L/P rows"
assert counts["P"] == 10136 and counts["iso"] == 1262, dict(counts)

# pre rows inherit trip/stop of their event
n_pre_ok = 0
pre_df = d[d["_pre"]]
for p_rid, p_next in zip(pre_df["_rid"].values, pre_df["_next_rid"].values):
    ev = info.get(int(p_next))
    if ev and ev[2] == "S":
        info[int(p_rid)] = (ev[0], ev[1], "pre", "", None, None, None, ev[7])
        n_pre_ok += 1
    else:  # event row itself was a duplicate that got dropped -> still attach by idr
        info[int(p_rid)] = ("", None, "pre", "", None, None, None, None)
log("pre attached to S:", n_pre_ok, "orphan pre:", int(d._pre.sum()) - n_pre_ok)

# dropped rows
drop_info = {}   # rid -> (reason, trip_id)
for du_rid in dup_rows["_rid"].values:
    drop_info[int(du_rid)] = ("DUPLICATE", "")
for rid, tid in evicted_rids:
    drop_info[rid] = ("EVICTED_CONFLICT", tid)
assert len(drop_info) == len(ddf), (len(drop_info), len(ddf))
assert len(info) + len(drop_info) == n_raw
log("accounting OK:", len(info), "clean +", len(drop_info), "dropped =", n_raw)

# ---------------- 4. ordering for the Clean sheet ----------------
raw_by_rid = raw.set_index("_rid")
FALLBACK = ("9999-99-99", "99:99", "")
def trip_key(rid):
    tid, stop, typ = info[rid][0], info[rid][1], info[rid][2]
    tk = tmeta.get(tid, FALLBACK)
    return (tk, stop if stop is not None else 10 ** 6,
            0 if typ == "pre" else 1, raw_by_rid.at[rid, "_ts"])
clean_rids = sorted(info.keys(), key=trip_key)
log("clean order built")

# ---------------- 5. workbook helpers ----------------
def new_book(path):
    wb = xlsxwriter.Workbook(path, {"constant_memory": True})
    F = {
        "head": wb.add_format({"bold": True, "font_name": "Arial", "font_size": 10,
                               "font_color": "white", "bg_color": "#3A3A38"}),
        "w": wb.add_format({"font_name": "Arial", "font_size": 10}),
        "g": wb.add_format({"font_name": "Arial", "font_size": 10, "bg_color": "#F2F2F2"}),
        "wi": wb.add_format({"font_name": "Arial", "font_size": 10, "italic": True,
                             "font_color": "#666666"}),
        "gi": wb.add_format({"font_name": "Arial", "font_size": 10, "italic": True,
                             "font_color": "#666666", "bg_color": "#F2F2F2"}),
    }
    return wb, F

def cellv(v):
    if v is None: return ""
    if isinstance(v, float) and math.isnan(v): return ""
    return v

def write_method(wb, F, lines):
    ws = wb.add_worksheet("METHOD")
    ws.set_column(0, 0, 118)
    for i, ln in enumerate(lines):
        ws.write(i, 0, ln, F["head"] if (ln and ln == ln.upper() and len(ln) > 3
                                         and not ln.startswith(" ")) else F["w"])

# ================= WORKBOOK 1: Driver_Data_W5.xlsx =================
log("writing Driver_Data_W5.xlsx ...")
wb, F = new_book(f"{OUTDIR}/Driver_Data_W5.xlsx")
HELP = ["Trip ID", "Raw Row ID", "Stop No", "Row type", "Source",
        "Fill %", "Sensor %", "Est. kg", "Bin material"]
ws = wb.add_worksheet("Clean (by trip)")
ws.freeze_panes(1, 0)
for c, h in enumerate(HELP + RAW_COLS):
    ws.write(0, c, h, F["head"])
for c, w in enumerate([13, 9, 7, 8, 7, 7, 8, 8, 11] +
                      [10, 12, 11, 8, 22, 10, 10, 16, 14, 10, 10, 19, 10, 9, 8, 19, 19, 9, 10]):
    ws.set_column(c, c, w)
band, last_tid, r = 0, object(), 1
type_counts = Counter()
raw_vals = raw.set_index("_rid")[RAW_COLS]
for rid in clean_rids:
    tid, stop, typ, src, fill, sens, est, mat = info[rid]
    if tid != last_tid:
        band ^= 1; last_tid = tid
    plain = typ == "S"
    fmt = (F["g"] if plain else F["gi"]) if band else (F["w"] if plain else F["wi"])
    type_counts[typ] += 1
    rowraw = raw_vals.loc[rid]
    if mat is None:
        mat = binmat.get(raw_by_rid.at[rid, "_cid"]) or desc_mat(rowraw["description"])
    vals = [tid, rid, "" if stop is None else stop, typ, src,
            cellv(fill), cellv(sens), cellv(est), MATW.get(mat, "")]
    vals += [cellv(v) for v in rowraw.values]
    ws.write_row(r, 0, vals, fmt)
    r += 1
n_clean_driver = r - 1
ws.autofilter(0, 0, r - 1, len(HELP + RAW_COLS) - 1)
log("Clean (by trip) rows:", n_clean_driver, dict(type_counts))

ws2 = wb.add_worksheet("Dropped")
ws2.freeze_panes(1, 0)
H2 = ["Raw Row ID", "Reason", "Evicted from Trip ID"] + RAW_COLS
for c, h in enumerate(H2):
    ws2.write(0, c, h, F["head"])
ws2.set_column(0, 0, 9); ws2.set_column(1, 1, 18); ws2.set_column(2, 2, 13)
r2 = 1
for rid in sorted(drop_info.keys()):
    reason, tid = drop_info[rid]
    vals = [rid, reason, tid] + [cellv(v) for v in raw_vals.loc[rid].values]
    ws2.write_row(r2, 0, vals, F["w"])
    r2 += 1
n_drop_driver = r2 - 1
ws2.autofilter(0, 0, r2 - 1, len(H2) - 1)
log("Dropped rows:", n_drop_driver)

method1 = [
    "DRIVER DATA W5 - HOW THIS WORKBOOK WAS BUILT",
    "",
    "Source file: Brain/03_db/parquet/raw_collections.parquet (264,817 rows, the frozen copy of",
    "Enchimentos_com_Recolhas[RioMaior].csv in original file order). Raw Row ID = line number 1..264,817.",
    "Trip logic: W5/02_data_work/trips_v7_enriched.json + assignments_v7.parquet (the v7 rebuild,",
    "which uses real road travel times - truck-legal speed limits on the OSM network - never a flat speed).",
    "",
    "SHEET 'CLEAN (BY TRIP)'",
    "Every kept raw row, arranged trip by trip (white / light-grey bands alternate per trip; trips are",
    "in date + start-time order, stops in service order). Row types, strongest evidence first:",
    "  S   - stamped emptying record: the row carries a collection number (idrecolha) and is a stop",
    "        of that vehicle trip. The driver's own record - no guessing.",
    "  pre - pre-reading: a fill check on the same bin at most 15 minutes before its stamped emptying.",
    "        It belongs to that visit, so it sits just above its S row. Its own Enchimento column",
    "        carries the fill value (helper Fill % left blank to avoid double counting).",
    "  I   - inferred: no trip stamp, but exactly one trip could physically reach this bin at this",
    "        moment (road-time feasible in both directions, best candidate p >= 0.7).",
    "        These are OBSERVATIONS of the bin, not collections.",
    "  L   - low confidence: same method, best candidate p < 0.7. Use with care.",
    "  P   - phantom: no recorded trip fits, but the readings trace a coherent vehicle path;",
    "        reconstructed vehicles get PH IDs (e.g. PH20200102-1). Evidence of unrecorded activity.",
    "  iso - isolated observation: fits no recorded trip and no phantom chain (fewer than 3 readings",
    "        would form the chain). Kept with a blank Trip ID at the bottom of the sheet.",
    "Helper columns: Source 'D' = driver reading only, 'DS' = a cleaned sensor drop event for the same",
    "bin overlaps the stop by +/-90 min (independent confirmation). Fill % = pre-emptying fill (S rows)",
    "or the reading's own fill (I/L/P). Sensor % = nearest CLEAN sensor reading within +/-3 h, expressed",
    "as % of that bin's own era ceiling (sensors saturate at 82-84 units, defect D3); negative values",
    "are sensor error codes kept for transparency. Est. kg = container volume (litres) x fill x",
    "mid literature density (Packaging 32, Paper/card 75, Glass 300 kg/m3) - an estimate, never a",
    "measurement. Bin material comes from the bin's own description; a different material inside a trip",
    "block means the bin was only OBSERVED at a shared site (trips are material-pure).",
    "",
    "SHEET 'DROPPED'",
    "The only rows removed before trip building, with the reason:",
    "  DUPLICATE        - identical bin + identical timestamp as another row; the first copy is kept",
    "                     (stamped copies preferred), the repeat is dropped. 1,703 rows.",
    "  EVICTED_CONFLICT - an inferred reading whose insertion made its trip physically impossible at",
    "                     legal road speeds; the chain validator removed the worst offender until the",
    "                     trip was feasible again. 2,981 rows.",
    "Nothing else was deleted: 260,133 clean + 4,684 dropped = 264,817 raw rows.",
    "",
    "ASSUMPTIONS",
    "  1. Duplicate = same container AND same timestamp to the millisecond.",
    "  2. Pre-reading window: 15 minutes before a stamped emptying of the same bin.",
    "  3. Feasibility: road time at truck-legal speed limits must fit the time gap (service time",
    "     0.02 min, minimum available 0.5 min). Identifiers needing above-ceiling speeds were split",
    "     into tracks a, b, c...; parts feasible at ceiling speeds were merged back.",
    "  4. Confidence p compares the best and second-best candidate trips by detour cost.",
    "  5. Phantom chains need >= 3 physically consistent readings on the same day.",
    "  6. Km totais / Peso total belong to the whole identifier (weighbridge totals);",
    "     when an identifier was split, its tracks share the value - kg/km counted once per identifier.",
    "  7. Container volume ('Volume do tipo de contentor') is LITRES, never a weight.",
]
write_method(wb, F, method1)
wb.close()
log("Driver_Data_W5.xlsx done")

# ================= WORKBOOK 2: Sensor_Data_W5.xlsx =================
log("writing Sensor_Data_W5.xlsx ...")
sc = pd.read_parquet(f"{W5}/sensor_clean.parquet")
sdrop = pd.read_parquet(f"{W5}/sensor_drops_v2.parquet")
srem = pd.read_parquet(f"{W5}/sensor_removed.parquet")
n_raw_sens = 1048575
assert len(sc) + len(srem) == n_raw_sens

wb, F = new_book(f"{OUTDIR}/Sensor_Data_W5.xlsx")
ws = wb.add_worksheet("Clean readings")
ws.freeze_panes(1, 0)
H = ["Container ID", "Timestamp", "Fill (raw units)", "Era", "% of era ceiling"]
for c, h in enumerate(H):
    ws.write(0, c, h, F["head"])
for c, w in enumerate([12, 20, 13, 6, 14]):
    ws.set_column(c, c, w)
ts_s = sc["ts"].dt.strftime("%Y-%m-%d %H:%M:%S").values
cid_s = sc["cid"].values; fill_s = sc["fill"].values
era_s = sc["era"].values; pct_s = np.round(sc["pct"].values, 1)
for i in range(len(sc)):
    ws.write_row(i + 1, 0, [cid_s[i], ts_s[i], fill_s[i], era_s[i],
                            "" if math.isnan(pct_s[i]) else pct_s[i]], F["w"])
n_sc = len(sc)
ws.autofilter(0, 0, n_sc, len(H) - 1)
log("Clean readings rows:", n_sc)

ws2 = wb.add_worksheet("Drop events")
ws2.freeze_panes(1, 0)
H2 = ["Container ID", "Fill before (ts)", "Fill after (ts)", "Window (min)",
      "Drop (units)", "% full before", "Confidence", "Rebound <24h"]
for c, h in enumerate(H2):
    ws2.write(0, c, h, F["head"])
for c, w in enumerate([12, 20, 20, 11, 11, 12, 10, 12]):
    ws2.set_column(c, c, w)
tb_s = pd.to_datetime(sdrop["t_before"]).dt.strftime("%Y-%m-%d %H:%M:%S").values
ta_s = pd.to_datetime(sdrop["t_after"]).dt.strftime("%Y-%m-%d %H:%M:%S").values
for i, rr in enumerate(sdrop.itertuples(index=False)):
    ws2.write_row(i + 1, 0, [rr.cid, tb_s[i], ta_s[i], rr.window_min, rr.drop_units,
                             cellv(rr.pct_before), rr.confidence,
                             "yes" if rr.rebound else "no"], F["w"])
n_sd = len(sdrop)
ws2.autofilter(0, 0, n_sd, len(H2) - 1)
log("Drop events rows:", n_sd)

ws3 = wb.add_worksheet("Removed")
ws3.freeze_panes(1, 0)
H3 = ["Container ID", "Timestamp", "Fill (raw units)", "Reason removed"]
for c, h in enumerate(H3):
    ws3.write(0, c, h, F["head"])
for c, w in enumerate([12, 20, 13, 14]):
    ws3.set_column(c, c, w)
rm_ts = srem["ts"].dt.strftime("%Y-%m-%d %H:%M:%S").values
rm_cid = srem["cid"].values; rm_fill = srem["fill"].values; rm_why = srem["reason"].values
for i in range(len(srem)):
    ws3.write_row(i + 1, 0, [rm_cid[i], rm_ts[i], rm_fill[i], rm_why[i]], F["w"])
n_sr = len(srem)
ws3.autofilter(0, 0, n_sr, len(H3) - 1)
log("Removed rows:", n_sr)

method2 = [
    "SENSOR DATA W5 - HOW THIS WORKBOOK WAS BUILT",
    "",
    "Source file: Brain/03_db/parquet/raw_sensors.parquet (1,048,575 rows). Cleaning script:",
    "W5/02_data_work/task_e_sensor_clean_v2.py; outputs sensor_clean.parquet, sensor_removed.parquet,",
    "sensor_drops_v2.parquet (all in W5/02_data_work). 791,207 kept + 257,368 removed = 1,048,575.",
    "",
    "SHEET 'CLEAN READINGS' - every reading that survived cleaning.",
    "Era: E1 up to 2020-10-31, E2 2020-11-01..2022-12-31, E3 from 2023-01-01 (hardware/firmware",
    "phases with different behaviour). % of era ceiling: the sensors saturate around 82-84 raw units",
    "(defect D3), so raw 'fill' is NOT a percentage; each bin's ceiling = its own maximum clean value",
    "within the era, and pct = fill / ceiling x 100 is the comparable fullness measure.",
    "",
    "SHEET 'DROP EVENTS' - probable emptyings seen by the sensors.",
    "A drop = fall of >= 25 raw units between two consecutive CLEAN readings of the same bin within",
    "<= 24 h. Confidence by window width: <= 6 h high, <= 12 h med, else low. Events whose window",
    "contains a removed (bad) reading are excluded. Rebound = fill rose back within 24 h (suggests",
    "a sensor glitch or immediate refill). 47,543 events.",
    "",
    "SHEET 'REMOVED' - readings taken out, rule by rule:",
    "  NEG_CODE  (< -10)      hard sensor error codes                      50,620 rows",
    "  NEG_SMALL (-10..-1)    transient negative errors                    46,212 rows",
    "  STUCK                  >= 6 identical consecutive values spanning > 48 h; first kept,",
    "                         repeats dropped (sensor frozen)             160,280 rows",
    "  SPIKE                  rise >= +40 units within <= 30 min (physically implausible)  218 rows",
    "  DUPLICATE              same bin + same timestamp, first kept            38 rows",
    "",
    "ASSUMPTIONS",
    "  1. A removed reading is an observation problem, not evidence the bin was or was not full.",
    "  2. Ceilings are per bin per era because saturation level drifts between hardware phases.",
    "  3. Drop events are candidate emptyings - only a driver record makes them a confirmed collection.",
]
write_method(wb, F, method2)
wb.close()
log("Sensor_Data_W5.xlsx done")

# ================= WORKBOOK 3: Combined_Master_W5.xlsx + parquet =================
log("building master events ...")
# driver part (clean rows in trip order), then sensor drop events by time
m_source, m_cid, m_ts, m_tid, m_rtype, m_src = [], [], [], [], [], []
m_fill, m_sens, m_est, m_conf, m_rid, m_win, m_units = [], [], [], [], [], [], []
CONF_D = {"S": "stamped", "pre": "pre-reading", "I": "inferred p>=0.7",
          "L": "low p<0.7", "P": "phantom", "iso": "isolated"}
ts_lut = raw_by_rid["_ts"]
ench = raw.set_index("_rid")["Enchimento"]
for rid in clean_rids:
    tid, stop, typ, src, fill, sens, est, mat = info[rid]
    m_source.append("driver"); m_cid.append(raw_by_rid.at[rid, "_cid"])
    m_ts.append(ts_lut.at[rid]); m_tid.append(tid); m_rtype.append(typ)
    m_src.append(src if src else ("D" if typ != "iso" else ""))
    if typ == "pre":
        ev = ench.at[rid]
        try: fill = float(str(ev).replace(",", "."))
        except (TypeError, ValueError): fill = None
    m_fill.append(fill); m_sens.append(sens); m_est.append(est)
    m_conf.append(CONF_D[typ]); m_rid.append(rid)
    m_win.append(None); m_units.append(None)
sdrop_sorted = sdrop.sort_values("t_after", kind="mergesort")
for rr in sdrop_sorted.itertuples(index=False):
    m_source.append("sensor-drop"); m_cid.append(rr.cid)
    m_ts.append(pd.Timestamp(rr.t_after)); m_tid.append(""); m_rtype.append("drop")
    m_src.append("S"); m_fill.append(None)
    m_sens.append(None if (rr.pct_before != rr.pct_before) else round(float(rr.pct_before), 1))
    m_est.append(None); m_conf.append(str(rr.confidence)); m_rid.append(None)
    m_win.append(float(rr.window_min)); m_units.append(float(rr.drop_units))

master = pd.DataFrame({
    "source": m_source, "cid": m_cid, "ts": m_ts, "trip_id": m_tid,
    "row_type": m_rtype, "src": m_src, "fill": pd.array(m_fill, dtype="Float64"),
    "sensor_pct": pd.array(m_sens, dtype="Float64"),
    "est_kg": pd.array(m_est, dtype="Float64"), "confidence": m_conf,
    "raw_row_id": pd.array(m_rid, dtype="Int64"),
    "window_min": pd.array(m_win, dtype="Float64"),
    "drop_units": pd.array(m_units, dtype="Float64"),
})
master.to_parquet(f"{PARQ}/master_events_w5.parquet", index=False)
log("master_events_w5.parquet frozen:", len(master), "rows")

log("writing Combined_Master_W5.xlsx ...")
wb, F = new_book(f"{OUTDIR}/Combined_Master_W5.xlsx")
ws = wb.add_worksheet("Events")
ws.freeze_panes(1, 0)
H = ["Source", "Container ID", "Timestamp", "Trip ID", "Row type", "Src tag",
     "Fill %", "Sensor %", "Est. kg", "Confidence", "Raw Row ID",
     "Window (min)", "Drop (units)"]
for c, h in enumerate(H):
    ws.write(0, c, h, F["head"])
for c, w in enumerate([11, 12, 20, 13, 9, 8, 8, 9, 9, 15, 10, 11, 11]):
    ws.set_column(c, c, w)
band, last_tid, r = 0, object(), 1
mts = master["ts"].dt.strftime("%Y-%m-%d %H:%M:%S").values
mvals = master.drop(columns=["ts"])
for i, rr in enumerate(master.itertuples(index=False)):
    key = rr.trip_id if rr.source == "driver" else "sensor"
    if key != last_tid:
        band ^= 1; last_tid = key
    fmt = F["g"] if band else F["w"]
    ws.write_row(r, 0, [rr.source, rr.cid, mts[i], rr.trip_id, rr.row_type, rr.src,
                        cellv(None if rr.fill is pd.NA else rr.fill),
                        cellv(None if rr.sensor_pct is pd.NA else rr.sensor_pct),
                        cellv(None if rr.est_kg is pd.NA else rr.est_kg),
                        rr.confidence,
                        cellv(None if rr.raw_row_id is pd.NA else int(rr.raw_row_id)),
                        cellv(None if rr.window_min is pd.NA else rr.window_min),
                        cellv(None if rr.drop_units is pd.NA else rr.drop_units)], fmt)
    r += 1
n_events = r - 1
ws.autofilter(0, 0, r - 1, len(H) - 1)
log("Events rows:", n_events)

ws2 = wb.add_worksheet("Dropped (both files)")
ws2.freeze_panes(1, 0)
H2 = ["Source file", "Container ID", "Timestamp", "Fill", "idrecolha",
      "Reason", "Trip ID (evicted from)"]
for c, h in enumerate(H2):
    ws2.write(0, c, h, F["head"])
for c, w in enumerate([11, 12, 20, 9, 10, 18, 13]):
    ws2.set_column(c, c, w)
r2 = 1
for rid in sorted(drop_info.keys()):
    reason, tid = drop_info[rid]
    ws2.write_row(r2, 0, ["driver", raw_by_rid.at[rid, "_cid"],
                          ts_lut.at[rid].strftime("%Y-%m-%d %H:%M:%S"),
                          cellv(ench.at[rid]), cellv(raw_by_rid.at[rid, "_idr"]),
                          reason, tid], F["w"])
    r2 += 1
n_drop_d = r2 - 1
for i in range(len(srem)):
    ws2.write_row(r2, 0, ["sensor", rm_cid[i], rm_ts[i], rm_fill[i], "",
                          rm_why[i], ""], F["w"])
    r2 += 1
n_drop_both = r2 - 1
ws2.autofilter(0, 0, r2 - 1, len(H2) - 1)
log("Dropped (both files) rows:", n_drop_both)

method3 = [
    "COMBINED MASTER W5 - EVERY EVENT FROM BOTH DATA STREAMS IN ONE TABLE",
    "",
    "SOURCE FILES (exact names)",
    "  Brain/03_db/parquet/raw_collections.parquet      264,817 driver rows (frozen raw)",
    "  Brain/03_db/parquet/raw_sensors.parquet        1,048,575 sensor rows (frozen raw)",
    "  W5/02_data_work/trips_v7_enriched.json            13,365 v7 trips incl. phantoms",
    "  W5/02_data_work/assignments_v7.parquet           144,263 loose-reading assignments",
    "  W5/02_data_work/dropped_v7.parquet                 4,684 dropped driver rows",
    "  W5/02_data_work/sensor_clean.parquet             791,207 clean sensor readings",
    "  W5/02_data_work/sensor_drops_v2.parquet           47,543 sensor drop events",
    "  W5/02_data_work/sensor_removed.parquet           257,368 removed sensor readings",
    "The Events sheet is frozen unchanged to Brain/03_db/parquet/master_events_w5.parquet.",
    "",
    "SHEET 'EVENTS' - one row per kept driver reading (260,133) plus one row per sensor drop",
    "event (47,543) = 307,676 rows. Driver rows come first, arranged by trip; sensor drop events",
    "follow in time order.",
    "  Source    driver = a row of the driver file; sensor-drop = a >= 25-unit fall between two",
    "            clean sensor readings within <= 24 h (a probable emptying seen by the sensor).",
    "  Row type  S stamped emptying / pre pre-reading / I inferred / L low-confidence /",
    "            P phantom / iso isolated observation / drop sensor drop event.",
    "  Src tag   D driver-only evidence; DS driver stop corroborated by a sensor drop within",
    "            +/-90 min; S sensor-only evidence.",
    "  Fill %    S rows: pre-emptying fill; pre rows: their own reading; I/L/P: own fill.",
    "  Sensor %  driver rows: nearest clean sensor reading +/-3 h as % of the bin's era ceiling",
    "            (negative = error code); drop rows: % full just before the fall.",
    "  Est. kg   volume (litres) x fill x mid density (Packaging 32, Paper/card 75, Glass 300",
    "            kg/m3). An estimate, never a measurement.",
    "  Confidence driver rows: evidence tier; drop rows: high (<= 6 h window) / med (<= 12 h) / low.",
    "  Raw Row ID line number in raw_collections.parquet (driver rows only).",
    "",
    "SHEET 'DROPPED (BOTH FILES)' - all 4,684 dropped driver rows + all 257,368 removed sensor",
    "readings = 262,052 rows, each with its rule:",
    "  driver DUPLICATE          same bin + timestamp, first copy kept            1,703",
    "  driver EVICTED_CONFLICT   inferred reading made its trip infeasible        2,981",
    "  sensor NEG_CODE (< -10)   hard sensor error codes                         50,620",
    "  sensor NEG_SMALL (-10..-1) transient negative errors                      46,212",
    "  sensor STUCK              frozen sensor: >= 6 identical values > 48 h    160,280",
    "  sensor SPIKE              rise >= +40 units in <= 30 min                      218",
    "  sensor DUPLICATE          same bin + timestamp, first kept                    38",
    "",
    "RULE-BY-RULE TREATMENT (canon)",
    "  1. Inferred / low-confidence / phantom / isolated rows are OBSERVATIONS, not collections.",
    "  2. Trips are material-pure; a different bin material inside a trip means observation only.",
    "  3. kg and km totals are counted once per identifier (weighbridge values are per run).",
    "  4. Sensor drop events are candidate emptyings; only a driver record confirms a collection.",
    "  5. Container volume is litres; densities are mid literature values.",
]
write_method(wb, F, method3)
wb.close()
log("Combined_Master_W5.xlsx done")

summary = {
    "Driver_Data_W5.xlsx": {"Clean (by trip)": n_clean_driver, "Dropped": n_drop_driver,
                            "reconcile_driver": n_clean_driver + n_drop_driver},
    "Sensor_Data_W5.xlsx": {"Clean readings": n_sc, "Drop events": n_sd, "Removed": n_sr,
                            "reconcile_sensor": n_sc + n_sr},
    "Combined_Master_W5.xlsx": {"Events": n_events, "Dropped (both files)": n_drop_both},
    "master_parquet_rows": len(master),
    "clean_type_counts": dict(type_counts),
}
print(json.dumps(summary, indent=2))
log("ALL DONE")
