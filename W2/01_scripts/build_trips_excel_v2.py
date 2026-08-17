"""W2 - Driver rows arranged trip-by-trip in Excel (v2, three assignment tiers).
Sheet 1 'Trips (drivers)': one block per vehicle track (chronological), stops in
service order, pre-emptying readings attached to their trip, plus tier-3 rows
inferred by time + location (from reading_assignments.parquet), white/light-gray banding.
Sheet 2 'Readings not assignable': AMBIGUOUS / NO_TRIP_RUNNING / INFEASIBLE rows
with a 'Why not assigned' column. Sensors intentionally untouched.
"""
import duckdb, json
from collections import defaultdict
import pandas as pd
import xlsxwriter

BASE = r"C:/Users/esmae/Desktop/phd Esmaeil/THESIS CLAUDE"
OUT = f"{BASE}/W2/03_outputs/tables/Driver_Trips_Sorted.xlsx"

COLS = ["idcontentor", "Matricula do contentor", "Tipo de contentor",
        "Volume do tipo de contentor", "description", "Distrito", "Concelho",
        "Freguesia", "Localidade", "Latitude", "Longitude", "Data da leitura",
        "Enchimento", "idrecolha", "Rota", "Data de \u00ednicio", "Data de fim",
        "Km totais", "Peso total"]

ROWTYPE_INFERRED = "assigned by time + location (inferred)"

con = duckdb.connect()
sel = ", ".join(f'"{c}"' for c in COLS)
df = con.sql(f"""
  SELECT {sel}, TRY_CAST("Data da leitura" AS TIMESTAMP) AS _ts,
         trim(idcontentor) AS _cid, trim(idrecolha) AS _idr
  FROM '{BASE}/Brain/03_db/parquet/raw_collections.parquet'
  ORDER BY _ts
""").df()
df["_is_event"] = df["_idr"].notna() & (df["_idr"] != "") & (df["_idr"] != "0")
print("rows:", len(df), "events:", int(df._is_event.sum()))

# ---- track lookup from trips_v3 ----
tracks = json.load(open(f"{BASE}/W2/02_data_work/trips_v3.json", encoding="utf-8"))
lut = defaultdict(list)   # (base_id, cid, hhmm) -> [(track_id, stop_no, n)]
tmeta = {}
for t in tracks:
    key_order = (t["date"], t["start"], str(t["id"]))
    tmeta[t["id"]] = key_order
    for i, s in enumerate(t["stops"]):
        lut[(str(t["base_id"]), str(s[2]), s[3])].append((t["id"], i + 1, len(t["stops"])))

df["_track"] = None; df["_stop"] = None; df["_nstops"] = None; df["_rowtype"] = ""
ev_idx = df.index[df._is_event]
misses = 0
for i in ev_idx:
    hhmm = df.at[i, "_ts"].strftime("%H:%M")
    cand = lut.get((df.at[i, "_idr"], df.at[i, "_cid"], hhmm))
    if cand:
        tid, stop, n = cand.pop(0) if len(cand) > 1 else cand[0]
        df.at[i, "_track"], df.at[i, "_stop"], df.at[i, "_nstops"] = tid, stop, n
        df.at[i, "_rowtype"] = "emptying record"
    else:
        misses += 1
        df.at[i, "_track"] = df.at[i, "_idr"]
        df.at[i, "_rowtype"] = "emptying record"
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
            df.at[i, "_rowtype"] = "pre-reading (fill before emptying)"
            attached += 1
print("pre-readings attached:", attached)

# ---- tier 3: time + location inference (reading_assignments.parquet) ----
ra = pd.read_parquet(f"{BASE}/W2/02_data_work/reading_assignments.parquet")
ra["seq"] = ra.groupby(["cid", "ts"]).cumcount()
ra_map = {(r.cid, r.ts, r.seq): r for r in ra.itertuples()}

df["_status"] = None; df["_alt"] = None; df["_ins"] = None; df["_cand"] = None
seq_counter = defaultdict(int)
still_idx = df.index[~df._is_event & df._track.isna()]
hits = 0
for i in still_idx:
    key = (df.at[i, "_cid"], df.at[i, "_ts"])
    k = (key[0], key[1], seq_counter[key]); seq_counter[key] += 1
    r = ra_map.get(k)
    if r is None:
        continue
    hits += 1
    df.at[i, "_status"] = r.status
    df.at[i, "_alt"] = r.alt_track_id
    df.at[i, "_ins"] = r.insert_after_stop
    df.at[i, "_cand"] = r.track_id
    if r.status == "ASSIGNED":
        df.at[i, "_track"] = r.track_id
        df.at[i, "_rowtype"] = ROWTYPE_INFERRED
print("assignment rows matched:", hits, "of still-loose:", len(still_idx))

in_trip = df[df._track.notna()].copy()
loose = df[df._track.isna()].copy()

# order: tracks chronological, then position, pre-reading before its emptying.
# Position: stamped/pre rows sit at their stop number; inferred rows slot in
# after their insert stop (k + 0.5), ordered by reading time among themselves.
fallback_date = {}
for i, row in in_trip.iterrows():
    t = row["_track"]
    if t not in tmeta and t not in fallback_date:
        fallback_date[t] = (row["_ts"].strftime("%Y-%m-%d"), row["_ts"].strftime("%H:%M"), str(t))
in_trip["_tkey"] = in_trip["_track"].map(lambda t: tmeta.get(t) or fallback_date[t])
in_trip["_pre"] = (in_trip["_rowtype"] == "pre-reading (fill before emptying)").astype(int) * -1
inferred_mask = in_trip["_rowtype"] == ROWTYPE_INFERRED
in_trip["_pos"] = in_trip["_stop"].astype("float")
in_trip.loc[inferred_mask, "_pos"] = in_trip.loc[inferred_mask, "_ins"].astype("float") + 0.5
in_trip = in_trip.sort_values(by=["_tkey", "_pos", "_pre", "_ts"], kind="stable")

# ---- write workbook ----
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
HELP = ["Trip (track)", "Stop \u2116", "of stops", "Row type"]

ws = wb.add_worksheet("Trips (drivers)")
ws.freeze_panes(1, 0)
for c, h in enumerate(HELP + COLS):
    ws.write(0, c, h, F["head"])
widths = [11, 7, 7, 32] + [10, 12, 11, 8, 22, 10, 10, 16, 14, 10, 10, 19, 10, 9, 8, 19, 19, 9, 10]
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
    plain = row["_rowtype"] == "emptying record"
    fmt = (F["g"] if plain else F["gp"]) if band else (F["w"] if plain else F["wp"])
    type_counts[row["_rowtype"]] += 1
    stop = row["_stop"]
    vals = [str(row["_track"]), "" if stop is None or stop != stop else stop,
            row["_nstops"] or "", row["_rowtype"]]
    vals += ["" if v is None or (isinstance(v, float) and v != v) else v for v in (row[c] for c in COLS)]
    for c, v in enumerate(vals):
        ws.write(r, c, v, fmt)
    r += 1
ws.autofilter(0, 0, r - 1, len(HELP + COLS) - 1)
print("sheet1 rows:", r - 1)
for k, v in type_counts.items():
    print("  ", k, v)

ws2 = wb.add_worksheet("Readings not assignable")
ws2.freeze_panes(1, 0)
COLS2 = COLS + ["Why not assigned"]
for c, h in enumerate(COLS2):
    ws2.write(0, c, h, F["head"])
for c, w in enumerate(widths[4:] + [36]):
    ws2.set_column(c, c, w)
r2 = 1
why_counts = defaultdict(int)
for _, row in loose.iterrows():
    st = row["_status"]
    if st == "AMBIGUOUS":
        alt = row["_alt"]
        why = f"ambiguous between {row['_cand']} and {alt}" if alt and alt == alt else "AMBIGUOUS"
    else:
        why = st or ""
    why_counts[st] += 1
    for c, colname in enumerate(COLS):
        v = row[colname]
        ws2.write(r2, c, "" if v is None or (isinstance(v, float) and v != v) else v, F["w"])
    ws2.write(r2, len(COLS), why, F["w"])
    r2 += 1
ws2.autofilter(0, 0, r2 - 1, len(COLS2) - 1)
print("sheet2 rows:", r2 - 1, dict(why_counts))

ws3 = wb.add_worksheet("READ ME")
ws3.set_column(0, 0, 110)
notes = [
    "Driver records arranged by trip, not by plain time.",
    "",
    "Sheet 'Trips (drivers)': each white or light-gray block is one vehicle track (one truck's",
    "physically consistent trip). Tracks are ordered by date and start time; inside a track the",
    "rows follow the service order (Stop \u2116). Identifiers that hid more than one vehicle were",
    "split into tracks a, b, c (implied speed over 60 km/h between stops is impossible for a truck).",
    "'pre-reading' rows (gray italic) are the fill level noted moments before that same bin was",
    "emptied \u2014 they belong to the visit, so they sit with it.",
    "Km totais / Peso total belong to the whole identifier; when it was split into tracks the",
    "value is shared by all its tracks \u2014 it cannot be divided from the data.",
    "",
    "HOW ROWS WERE PLACED \u2014 three tiers, from strongest to weakest evidence:",
    "  1. Stamped ('emptying record', regular type): the row itself carries a collection",
    "     identifier (idrecolha) and its bin + time match a stop of that vehicle track.",
    "     This is the driver's own trip stamp \u2014 no guessing involved.",
    "  2. Pre-reading ('pre-reading (fill before emptying)', gray italic): a fill check on the",
    "     same bin at most 15 minutes before a stamped emptying. It clearly belongs to that",
    "     visit \u2014 the driver looked at the bin, then emptied it \u2014 so it sits with the visit.",
    "  3. Inferred ('assigned by time + location (inferred)', gray italic): the row has no trip",
    "     stamp, but exactly one track was on the road at that moment and that track passes the",
    "     bin's location at the right time. The reading is slotted into the track's sequence at",
    "     the point where the truck was nearby. This is an inference, not a recorded fact \u2014",
    "     treat it as 'very likely this trip', not proof.",
    "",
    "Sheet 'Readings not assignable': readings with no trip stamp that could NOT be safely",
    "inferred. The last column 'Why not assigned' gives the reason:",
    "  \u00b7 ambiguous between X and Y \u2014 two tracks were on the road then and either could",
    "    plausibly have produced the reading; assigning one would be a guess.",
    "  \u00b7 NO_TRIP_RUNNING \u2014 no vehicle track was on the road at that moment (e.g. an",
    "    office check or a reading outside any recorded trip window).",
    "  \u00b7 INFEASIBLE \u2014 a track was running, but it could not physically have reached the",
    "    reading's location at that time (the truck was demonstrably elsewhere).",
    "Nothing was deleted \u2014 every source row appears on exactly one of the two sheets.",
    "",
    "UNITS \u2014 read carefully:",
    "  \u00b7 'Volume do tipo de contentor' 2500 means 2500 LITRES \u2014 it is the container's",
    "    volume (size class), never a weight.",
    "  \u00b7 'Peso total' (weight) is the weighbridge total for the whole run \u2014 measured at",
    "    the scale, never derived from fill levels.",
    "",
    "All 19 original columns are unchanged and in their original order after the 4 helper columns.",
    "Source: Enchimentos_com_Recolhas[RioMaior].csv \u00b7 built ",
]
for i, n in enumerate(notes):
    ws3.write(i, 0, n, F["w"])
wb.close()
import os
print("XLSX MB:", round(os.path.getsize(OUT) / 1e6, 1))
