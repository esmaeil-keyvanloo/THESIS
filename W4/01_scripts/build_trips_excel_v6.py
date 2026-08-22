"""W4 - v6: sorted workbook (Trip ID + Raw Row ID) AND raw-order workbook
(Raw_Drivers_Data.xlsx: Row ID, Trip ID, Row type + untouched originals in file order).

Based on W3 build_trips_excel_v5.py; v6 changes:
  - inputs: trips_v6_enriched.json (regular + phantom trips, 9-element enriched stops),
    reading_assignments_v6.parquet (ASSIGNED / ASSIGNED_LOW / INFEASIBLE / NO_TRIP_RUNNING),
    phantom stop membership taken from the PH* trips inside trips_v6_enriched.json,
    isolated_observations.parquet (the only rows left unassignable).
  - row types: 'emptying record', 'pre-reading (fill before emptying)',
    'assigned by time + location (inferred)', 'assigned - LOW CONFIDENCE (p<0.7)',
    'phantom track (reconstructed vehicle)'.
  - sheet 2 'Readings not assignable' now holds ONLY isolated observations, with reason.
  - stop numbering comes from the enriched trip's full stop sequence (S/I/L/P inline).
"""
import json, os, shutil
from collections import defaultdict
import pandas as pd
import xlsxwriter

BASE = r"C:/Users/esmae/Desktop/phd Esmaeil/THESIS CLAUDE"
OUTDIR = f"{BASE}/W4/03_outputs/tables"
os.makedirs(OUTDIR, exist_ok=True)
OUT = f"{OUTDIR}/Driver_Trips_Sorted.xlsx"
RAWOUT = f"{OUTDIR}/Raw_Drivers_Data.xlsx"

COLS = ["idcontentor", "Matricula do contentor", "Tipo de contentor",
        "Volume do tipo de contentor", "description", "Distrito", "Concelho",
        "Freguesia", "Localidade", "Latitude", "Longitude", "Data da leitura",
        "Enchimento", "idrecolha", "Rota", "Data de \u00ednicio", "Data de fim",
        "Km totais", "Peso total"]

RT_EMPTY = "emptying record"
RT_PRE = "pre-reading (fill before emptying)"
RT_INF = "assigned by time + location (inferred)"
RT_LOW = "assigned - LOW CONFIDENCE (p<0.7)"
RT_PH = "phantom track (reconstructed vehicle)"

df = pd.read_parquet(f"{BASE}/Brain/03_db/parquet/raw_collections.parquet")  # pyarrow preserves file (=CSV) order
df = df[COLS].copy()
df["_rawid"] = range(1, len(df) + 1)
df["_ts"] = pd.to_datetime(df["Data da leitura"])
df["_cid"] = df["idcontentor"].str.strip()
df["_idr"] = df["idrecolha"].fillna("").str.strip()
df = df.sort_values("_ts", kind="stable")
df["_is_event"] = (df["_idr"] != "") & (df["_idr"] != "0")
print("rows:", len(df), "events:", int(df._is_event.sum()))

# ---- trip lookup from trips_v6_enriched (regular + phantom, enriched stops) ----
tracks = json.load(open(f"{BASE}/W4/02_data_work/trips_v6_enriched.json", encoding="utf-8"))
tmeta = {}          # trip id -> (date, start, id) chronological sort key
ntrips_ph = 0
ev_lut = defaultdict(list)   # (base_id, cid, hhmm) -> [(tid, stop_no, n, enrich)]
il_lut = defaultdict(list)   # (tid, cid, hhmm)    -> [(stop_no, n, enrich)]  (I and L stops)
ph_lut = defaultdict(list)   # (date, cid, hhmm)   -> [(tid, stop_no, n, enrich)]
MATW = {"P": "Packaging", "C": "Paper/card", "G": "Glass"}
for t in tracks:
    tid = str(t["id"])
    tmeta[tid] = (t["date"], t["start"], tid)
    n = len(t["stops"])
    is_ph = tid.startswith("PH")
    if is_ph:
        ntrips_ph += 1
    for i, s in enumerate(t["stops"]):
        enrich = (s[5], s[6], s[7], s[8])   # fill, est kg, material code, sensor %
        flag = s[4]
        if flag == "S":
            ev_lut[(str(t["base_id"]), str(s[2]), s[3])].append((tid, i + 1, n, enrich))
        elif flag in ("I", "L"):
            il_lut[(tid, str(s[2]), s[3])].append((i + 1, n, enrich))
        elif flag == "P":
            ph_lut[(t["date"], str(s[2]), s[3])].append((tid, i + 1, n, enrich))
print("trips:", len(tracks), "(phantom:", ntrips_ph, ")",
      "S-lut:", sum(len(v) for v in ev_lut.values()),
      "IL-lut:", sum(len(v) for v in il_lut.values()),
      "P-lut:", sum(len(v) for v in ph_lut.values()))

# per-bin material for pre-readings / sheet 2
binmat = {}
for t in tracks:
    for s in t["stops"]:
        if s[7]:
            binmat.setdefault(str(s[2]), s[7])

def pick(lst):
    return lst.pop(0) if len(lst) > 1 else lst[0]

# ---- tier 1: stamped emptying records ----
df["_track"] = None; df["_stop"] = None; df["_nstops"] = None; df["_rowtype"] = ""
df["_enr"] = None
ev_idx = df.index[df._is_event]
misses = 0
for i in ev_idx:
    hhmm = df.at[i, "_ts"].strftime("%H:%M")
    cand = ev_lut.get((df.at[i, "_idr"], df.at[i, "_cid"], hhmm))
    if cand:
        tid, stop, n, enrich = pick(cand)
        df.at[i, "_track"], df.at[i, "_stop"], df.at[i, "_nstops"] = tid, stop, n
        df.at[i, "_enr"] = enrich
    else:
        misses += 1
        df.at[i, "_track"] = df.at[i, "_idr"]
    df.at[i, "_rowtype"] = RT_EMPTY
print("event rows unmatched to a track:", misses)

# ---- tier 2: attach pre-readings (same bin, <=15 min before an event row) ----
attached = 0
for cid, g in df.groupby("_cid", sort=False):
    idx = g.index.to_list()
    for pos, i in enumerate(idx):
        if df.at[i, "_is_event"] or pos + 1 >= len(idx):
            continue
        j = idx[pos + 1]
        if df.at[j, "_is_event"] and (df.at[j, "_ts"] - df.at[i, "_ts"]).total_seconds() <= 900:
            df.at[i, "_track"] = df.at[j, "_track"]
            df.at[i, "_stop"] = df.at[j, "_stop"]
            df.at[i, "_nstops"] = df.at[j, "_nstops"]
            df.at[i, "_rowtype"] = RT_PRE
            attached += 1
print("pre-readings attached:", attached)

# ---- tiers 3-5: reading_assignments_v6 (inferred / low-confidence / phantom) + isolated ----
ra = pd.read_parquet(f"{BASE}/W4/02_data_work/reading_assignments_v6.parquet")
ra["seq"] = ra.groupby(["cid", "ts"]).cumcount()
ra_map = {(str(r.cid), r.ts, r.seq): r for r in ra.itertuples()}

iso = pd.read_parquet(f"{BASE}/W4/02_data_work/isolated_observations.parquet")
iso_lut = defaultdict(list)
for r in iso.itertuples():
    iso_lut[(str(r.cid), r.ts)].append(r.reason)

df["_why"] = None
seq_counter = defaultdict(int)
still_idx = df.index[~df._is_event & df._track.isna()]
tier_hits = defaultdict(int)
for i in still_idx:
    cid, ts = df.at[i, "_cid"], df.at[i, "_ts"]
    k = (cid, ts, seq_counter[(cid, ts)]); seq_counter[(cid, ts)] += 1
    r = ra_map.get(k)
    if r is None:
        # assignment run nudged a handful of timestamps by 5 min; retry shifted
        for off in (pd.Timedelta(minutes=5), pd.Timedelta(minutes=-5)):
            r = ra_map.get((cid, ts + off, 0))
            if r is not None:
                ts = ts + off   # use the shifted time for stop lookups below
                break
    if r is None:
        # not in RA at all -> unassignable, no recorded reason
        iso_r = iso_lut.get((cid, ts))
        df.at[i, "_why"] = iso_r.pop(0) if iso_r else "NOT_IN_ASSIGNMENT_RUN"
        tier_hits["not_in_ra"] += 1
        continue
    if r.status in ("ASSIGNED", "ASSIGNED_LOW"):
        hhmm = ts.strftime("%H:%M")
        cand = il_lut.get((str(r.track_id), cid, hhmm))
        if cand:
            stop, n, enrich = pick(cand)
            df.at[i, "_stop"], df.at[i, "_nstops"], df.at[i, "_enr"] = stop, n, enrich
        df.at[i, "_track"] = str(r.track_id)
        df.at[i, "_rowtype"] = RT_INF if r.status == "ASSIGNED" else RT_LOW
        tier_hits[r.status] += 1
    else:  # INFEASIBLE / NO_TRIP_RUNNING -> phantom stop or isolated observation
        hhmm = ts.strftime("%H:%M")
        cand = ph_lut.get((ts.strftime("%Y-%m-%d"), cid, hhmm))
        if cand:
            tid, stop, n, enrich = pick(cand)
            df.at[i, "_track"], df.at[i, "_stop"], df.at[i, "_nstops"] = tid, stop, n
            df.at[i, "_enr"] = enrich
            df.at[i, "_rowtype"] = RT_PH
            tier_hits["PHANTOM"] += 1
        else:
            iso_r = iso_lut.get((cid, ts))
            df.at[i, "_why"] = iso_r.pop(0) if iso_r else str(r.status)
            tier_hits["ISOLATED"] += 1
print("tier hits:", dict(tier_hits), "of still-loose:", len(still_idx))

in_trip = df[df._track.notna()].copy()
loose = df[df._track.isna()].copy()
print("in-trip rows:", len(in_trip), "loose rows:", len(loose))

# order: trips chronological, then stop position; pre-reading just before its emptying.
fallback_date = {}
for i, row in in_trip.iterrows():
    t = row["_track"]
    if t not in tmeta and t not in fallback_date:
        fallback_date[t] = (row["_ts"].strftime("%Y-%m-%d"), row["_ts"].strftime("%H:%M"), str(t))
in_trip["_tkey"] = in_trip["_track"].map(lambda t: tmeta.get(t) or fallback_date[t])
in_trip["_pre"] = (in_trip["_rowtype"] == RT_PRE).astype(int) * -1
in_trip["_pos"] = in_trip["_stop"].astype("float")
in_trip = in_trip.sort_values(by=["_tkey", "_pos", "_pre", "_ts"], kind="stable")

# ---- write sorted workbook ----
wb = xlsxwriter.Workbook(OUT, {"constant_memory": True})
F = {
    "head": wb.add_format({"bold": True, "font_name": "Arial", "font_size": 10,
                           "font_color": "white", "bg_color": "#3A3A38", "border": 0}),
    "w": wb.add_format({"font_name": "Arial", "font_size": 10}),
    "g": wb.add_format({"font_name": "Arial", "font_size": 10, "bg_color": "#F2F2F2"}),
    "wp": wb.add_format({"font_name": "Arial", "font_size": 10, "italic": True, "font_color": "#666666"}),
    "gp": wb.add_format({"font_name": "Arial", "font_size": 10, "italic": True,
                          "font_color": "#666666", "bg_color": "#F2F2F2"}),
}
HELP = ["Trip ID", "Raw Row ID", "Stop \u2116", "of stops", "Row type",
        "Bin material", "Fill % before emptying", "Sensor fill % (\u00b13h, of ceiling)", "Est. kg (mid density)"]

ws = wb.add_worksheet("Trips (drivers)")
ws.freeze_panes(1, 0)
for c, h in enumerate(HELP + COLS):
    ws.write(0, c, h, F["head"])
widths = [13, 9, 7, 7, 34, 11, 10, 12, 9] + [10, 12, 11, 8, 22, 10, 10, 16, 14, 10, 10, 19, 10, 9, 8, 19, 19, 9, 10]
for c, w in enumerate(widths):
    ws.set_column(c, c, w)

r = 1
band = 0
last_track = object()
type_counts = defaultdict(int)
for _, row in in_trip.iterrows():
    if row["_track"] != last_track:
        band ^= 1
        last_track = row["_track"]
    plain = row["_rowtype"] == RT_EMPTY
    fmt = (F["g"] if plain else F["gp"]) if band else (F["w"] if plain else F["wp"])
    type_counts[row["_rowtype"]] += 1
    stop = row["_stop"]
    enr = row["_enr"]
    fill, est, mat, snr = enr if enr is not None else (None, None, None, None)
    if row["_rowtype"] == RT_PRE:
        fill = est = snr = None   # its own Enchimento column already carries the value
        mat = binmat.get(row["_cid"])
    vals = [str(row["_track"]), row["_rawid"], "" if stop is None or stop != stop else stop,
            row["_nstops"] or "", row["_rowtype"],
            MATW.get(mat, ""), "" if fill is None else fill,
            "" if snr is None else snr, "" if est is None else est]
    vals += ["" if v is None or (isinstance(v, float) and v != v) else v for v in (row[c] for c in COLS)]
    for c, v in enumerate(vals):
        ws.write(r, c, v, fmt)
    r += 1
ws.autofilter(0, 0, r - 1, len(HELP + COLS) - 1)
print("sheet1 rows:", r - 1)
for k, v in sorted(type_counts.items()):
    print("  ", k, v)

ws2 = wb.add_worksheet("Readings not assignable")
ws2.freeze_panes(1, 0)
WHY = {"INFEASIBLE": "isolated observation \u2014 no vehicle track could physically have "
                     "reached this bin at this time",
       "NO_TRIP_RUNNING": "isolated observation \u2014 no vehicle track (real or reconstructed) "
                          "was on the road at this moment",
       "NOT_IN_ASSIGNMENT_RUN": "reading absent from the assignment run"}
COLS2 = COLS + ["Bin material", "Why not assigned"]
for c, h in enumerate(COLS2):
    ws2.write(0, c, h, F["head"])
for c, w in enumerate(widths[9:] + [11, 60]):
    ws2.set_column(c, c, w)
r2 = 1
why_counts = defaultdict(int)
for _, row in loose.iterrows():
    why = row["_why"] or ""
    why_counts[why] += 1
    for c, colname in enumerate(COLS):
        v = row[colname]
        ws2.write(r2, c, "" if v is None or (isinstance(v, float) and v != v) else v, F["w"])
    ws2.write(r2, len(COLS), MATW.get(binmat.get(row["_cid"]), ""), F["w"])
    ws2.write(r2, len(COLS) + 1, WHY.get(why, why), F["w"])
    r2 += 1
ws2.autofilter(0, 0, r2 - 1, len(COLS2) - 1)
print("sheet2 rows:", r2 - 1, dict(why_counts))

ws3 = wb.add_worksheet("READ ME")
ws3.set_column(0, 0, 112)
notes = [
    "Driver records arranged by trip, not by plain time.",
    "",
    "Sheet 'Trips (drivers)': each white or light-gray block is one vehicle trip (one truck's",
    "physically consistent run). Trips are ordered by date and start time; inside a trip the",
    "rows follow the service order (Stop \u2116). Identifiers that hid more than one vehicle were",
    "split into tracks a, b, c; split parts whose gap is feasible at legal-ceiling road speeds",
    "were MERGED back into one trip (merge policy: the ceiling speed graph decides; trips that",
    "needed above-legal speeds to merge are kept split and flagged in the online explorer).",
    "'pre-reading' rows (gray italic) are the fill level noted moments before that same bin was",
    "emptied \u2014 they belong to the visit, so they sit with it.",
    "Km totais / Peso total belong to the whole identifier; when it was split into tracks the",
    "value is shared by all its tracks \u2014 it cannot be divided from the data.",
    "",
    "HOW ROWS WERE PLACED \u2014 five row types, from strongest to weakest evidence:",
    "  1. Stamped ('emptying record', regular type): the row itself carries a collection",
    "     identifier (idrecolha) and its bin + time match a stop of that vehicle trip.",
    "     This is the driver's own trip stamp \u2014 no guessing involved.",
    "  2. Pre-reading ('pre-reading (fill before emptying)', gray italic): a fill check on the",
    "     same bin at most 15 minutes before a stamped emptying. It clearly belongs to that",
    "     visit \u2014 the driver looked at the bin, then emptied it \u2014 so it sits with the visit.",
    "  3. Inferred ('assigned by time + location (inferred)', gray italic): the row has no trip",
    "     stamp, but one trip was on the road at that moment and passes the bin's location at",
    "     the right time with high confidence (p \u2265 0.7). The reading is slotted into the trip's",
    "     sequence where the truck was nearby. An inference, not a recorded fact \u2014 treat it as",
    "     'very likely this trip', not proof. These are OBSERVATIONS of the bin, not collections.",
    "  4. Low confidence ('assigned - LOW CONFIDENCE (p<0.7)', gray italic): same method, but",
    "     the best candidate trip won with probability below 0.7 \u2014 another trip could plausibly",
    "     have produced the reading. Use with care; excluded from any per-trip statistics.",
    "  5. Phantom ('phantom track (reconstructed vehicle)', gray italic): no recorded trip could",
    "     have produced the reading, but the readings themselves trace a coherent vehicle path.",
    "     These reconstructed vehicles get PH trip IDs (e.g. PH20200102-1). They are evidence of",
    "     unrecorded collection activity \u2014 no stamped identifier, no weighbridge weight exists.",
    "",
    "Sheet 'Readings not assignable': the remaining ISOLATED observations \u2014 readings that fit",
    "no recorded trip and no reconstructed (phantom) vehicle path. The last column",
    "'Why not assigned' gives the reason (no trip running / no track could reach the bin).",
    "Nothing was deleted \u2014 every source row appears on exactly one of the two sheets.",
    "",
    "UNITS \u2014 read carefully:",
    "  \u00b7 'Volume do tipo de contentor' 2500 means 2500 LITRES \u2014 it is the container's",
    "    volume (size class), never a weight.",
    "  \u00b7 'Peso total' (weight) is the weighbridge total for the whole run \u2014 measured at",
    "    the scale, never derived from fill levels.",
    "",
    "ENRICHMENT COLUMNS (matching the online explorer):",
    "  \u00b7 Bin material \u2014 the bin's own material; inside a trip block, a different material",
    "    means the bin was only OBSERVED at a shared site, never emptied by this truck",
    "    (trips are material-pure).",
    "  \u00b7 Fill % before emptying \u2014 for emptying records: the pre-emptying reading; for",
    "    inferred / low-confidence / phantom rows: the reading itself. Blank on pre-reading",
    "    rows (their Enchimento IS the fill).",
    "  \u00b7 Sensor fill % \u2014 nearest sensor reading within \u00b13 h, as % of that bin's own",
    "    ceiling (82\u201384 cap, defect D3). Only ~42% of bins carry sensors; blank means no match.",
    "  \u00b7 Est. kg \u2014 volume \u00d7 fill \u00d7 mid literature density (packaging 32,",
    "    paper 75, glass 300 kg/m\u00b3). An estimate, never a measurement; only emptied bins",
    "    count toward any trip weight.",
    "",
    "All 19 original columns are unchanged and in their original order after the 9 helper columns.",
    "Source: Enchimentos_com_Recolhas[RioMaior].csv (copy alongside this workbook) \u00b7 built from",
    "W4 v6 data (trips_v6_enriched.json, reading_assignments_v6.parquet, phantom tracks).",
]
for i, n in enumerate(notes):
    ws3.write(i, 0, n, F["w"])
wb.close()

# ---- RAW-ORDER workbook ----
raw = df.sort_values("_rawid", kind="stable")
wb2 = xlsxwriter.Workbook(RAWOUT, {"constant_memory": True})
Fh = wb2.add_format({"bold": True, "font_name": "Arial", "font_size": 10,
                     "font_color": "white", "bg_color": "#3A3A38"})
Fw = wb2.add_format({"font_name": "Arial", "font_size": 10})
Fi = wb2.add_format({"font_name": "Arial", "font_size": 10, "italic": True, "font_color": "#666666"})
wsr = wb2.add_worksheet("Raw data (file order)")
wsr.freeze_panes(1, 0)
RH = ["Row ID", "Trip ID", "Row type"]
for c, h in enumerate(RH + COLS):
    wsr.write(0, c, h, Fh)
for c, w in enumerate([8, 13, 34] + widths[9:]):
    wsr.set_column(c, c, w)
rr = 1
raw_type_counts = defaultdict(int)
for _, row in raw.iterrows():
    if row["_track"] is not None and row["_track"] == row["_track"]:
        tid, typ = str(row["_track"]), row["_rowtype"]
    else:
        why = row["_why"] or ""
        tid = ""
        typ = {"INFEASIBLE": "isolated observation (no track could reach it)",
               "NO_TRIP_RUNNING": "isolated observation (no trip running)"}.get(why, "unassigned")
    raw_type_counts[typ] += 1
    fmt = Fw if typ == RT_EMPTY else Fi
    vals = [row["_rawid"], tid, typ]
    vals += ["" if v is None or (isinstance(v, float) and v != v) else v for v in (row[c] for c in COLS)]
    for c, v in enumerate(vals):
        wsr.write(rr, c, v, fmt)
    rr += 1
wsr.autofilter(0, 0, rr - 1, len(RH + COLS) - 1)
wsn = wb2.add_worksheet("READ ME")
wsn.set_column(0, 0, 112)
for i, n in enumerate([
    "Exact copy of Enchimentos_com_Recolhas[RioMaior].csv in its ORIGINAL row order.",
    "Nothing removed or reordered; the 19 original columns are untouched.",
    "Three helper columns were added on the left:",
    "  \u00b7 Row ID \u2014 the line number in the raw file (1\u2026264,817).",
    "  \u00b7 Trip ID \u2014 the unique trip this row belongs to: collection number (idrecolha)",
    "    plus a track letter when one number hid several vehicles (e.g. 17242b), or a",
    "    PH\u2026 id for a reconstructed (phantom) vehicle with no recorded trip.",
    "  \u00b7 Row type \u2014 how the row relates to its trip: emptying record (has idrecolha),",
    "    pre-reading (fill noted \u226415 min before that emptying), assigned by time + location",
    "    (inferred, p \u2265 0.7), assigned - LOW CONFIDENCE (p<0.7), phantom track (reconstructed",
    "    vehicle), or isolated observation (the reason it stays unassigned).",
    "The trip-arranged view of the same data is Driver_Trips_Sorted.xlsx (its Raw Row ID",
    "column points back to Row ID here).",
]):
    wsn.write(i, 0, n, Fw)
wb2.close()
print("SORTED XLSX MB:", round(os.path.getsize(OUT) / 1e6, 1))
print("RAW XLSX MB:", round(os.path.getsize(RAWOUT) / 1e6, 1), "rows:", rr - 1)
print("raw type counts:", dict(raw_type_counts))
assert (r - 1) + (r2 - 1) == len(df), f"accounting fail: {(r-1)+(r2-1)} != {len(df)}"
print("ACCOUNTING OK:", (r - 1), "+", (r2 - 1), "=", len(df))

# ---- copy raw CSV alongside ----
src = f"{BASE}/DATA/XLS/Enchimentos_com_Recolhas[RioMaior].csv"
dst = f"{OUTDIR}/Enchimentos_com_Recolhas[RioMaior].csv"
shutil.copy2(src, dst)
print("CSV copied:", round(os.path.getsize(dst) / 1e6, 1), "MB")
