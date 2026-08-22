"""W4 - D1 (T6a): trip census + frozen master dataset.

Outputs:
  W4/02_data_work/trip_census.json
  Brain/03_db/parquet/master_events_w4.parquet
  W4/02_data_work/master_schema.md (written separately)

One master row per driver CSV row (264,817) and per sensor drop event (47,093).
Raw Row ID convention (S16, binding): line number in the original CSV in
pyarrow natural order, 1..264,817.
"""
import json
from collections import defaultdict, Counter

import numpy as np
import pandas as pd

BASE = "C:/Users/esmae/Desktop/phd Esmaeil/THESIS CLAUDE"
W4 = f"{BASE}/W4/02_data_work"

DENS_MID = {"Packaging": 32.0, "Paper/card": 75.0, "Glass": 300.0}  # kg/m3 mids
MATW = {"P": "Packaging", "C": "Paper/card", "G": "Glass"}
DESC2MAT = {
    "Mistura de embalagens": "Packaging",
    "Embalagens de Vidro": "Glass",
}  # paper matched by prefix (encoding-damaged accent)


def desc_to_mat(d):
    if not isinstance(d, str):
        return None
    if d in DESC2MAT:
        return DESC2MAT[d]
    if d.startswith("Embalagens de papel"):
        return "Paper/card"
    return None


# ---------------- load trips ----------------
trips = json.load(open(f"{W4}/trips_v6.json", encoding="utf-8"))
phant = json.load(open(f"{W4}/phantom_tracks.json", encoding="utf-8"))
enr = json.load(open(f"{W4}/trips_v6_enriched.json", encoding="utf-8"))
base = json.load(open(f"{BASE}/W2/02_data_work/trips_v5_base.json", encoding="utf-8"))

# base stamped-stop keys: (base_id, cid, hhmm) -> multiset (true collections)
base_keys = Counter()
base_meta = {}  # base_id -> (kg, km_rec)
for t in base:
    base_meta[str(t["id"])] = (t.get("kg"), t.get("km_rec"))
    for s in t["stops"]:
        base_keys[(str(t["id"]), str(s[2]), s[3])] += 1

# trip meta
tmeta = {}
for t in trips:
    tmeta[str(t["id"])] = {
        "base_id": str(t["base_id"]),
        "merged": bool(t.get("merged")),
        "flagged": bool(t.get("speed_flags")),
        "verdict": t.get("verdict"),
        "part": t.get("part", ""),
        "frac": t.get("frac"),
    }

# stamped-stop lookup: only stops that are genuine base collections
# (v6 relabelled v5 inferred stops 'S'; those are NOT collections -> excluded
#  by requiring the key to exist in trips_v5_base with remaining multiplicity)
lut_s = defaultdict(list)  # (base_id, cid, hhmm) -> [trip_id, ...]
for t in trips:
    bid = str(t["base_id"])
    for s in t["stops"]:
        if s[4] == "S":
            k = (bid, str(s[2]), s[3])
            if base_keys.get(k, 0) > 0:
                lut_s[k].append(str(t["id"]))

# enrichment lookup: (trip_id, cid, hhmm, type) -> [(fill, est, mat, sensor)]
lut_e = defaultdict(list)
for t in enr:
    tid = str(t["id"])
    for s in t["stops"]:
        fill = s[5] if len(s) > 5 else None
        est = s[6] if len(s) > 6 else None
        mat = s[7] if len(s) > 7 else None
        snr = s[8] if len(s) > 8 else None
        lut_e[(tid, str(s[2]), s[3], s[4])].append((fill, est, mat, snr))

# phantom lookup: (date, cid, hhmm) -> [phantom_id, ...]
lut_p = defaultdict(list)
for t in phant:
    for s in t["stops"]:
        lut_p[(t["date"], str(s[2]), s[3])].append(str(t["id"]))

# ---------------- load raw driver CSV (natural order) ----------------
df = pd.read_parquet(f"{BASE}/Brain/03_db/parquet/raw_collections.parquet")
df["_rawid"] = np.arange(1, len(df) + 1)
df["_ts"] = pd.to_datetime(df["Data da leitura"])
df["_cid"] = df["idcontentor"].str.strip()
df["_idr"] = df["idrecolha"].fillna("").str.strip()
df["_isev"] = (df["_idr"] != "") & (df["_idr"] != "0")
df["_fill"] = pd.to_numeric(df["Enchimento"], errors="coerce")
df["_vol"] = pd.to_numeric(df["Volume do tipo de contentor"], errors="coerce")
df["_mat"] = df["description"].map(desc_to_mat)
print("raw rows:", len(df), "| event:", int(df._isev.sum()),
      "| non-event:", int((~df._isev).sum()))

# per-container registry (for sensor rows): modal volume + material
reg = (df.groupby("_cid")
         .agg(vol=("_vol", lambda s: s.mode().iat[0] if s.notna().any() else np.nan),
              mat=("_mat", lambda s: s.mode().iat[0] if s.notna().any() else None)))
reg_vol = reg["vol"].to_dict()
reg_mat = reg["mat"].to_dict()

# ---------------- loose-reading assignments ----------------
ra = pd.read_parquet(f"{W4}/reading_assignments_v6.parquet")
ra["seq"] = ra.groupby(["cid", "ts"]).cumcount()
ra_map = {(r.cid, r.ts, r.seq): r for r in ra.itertuples()}

iso = pd.read_parquet(f"{W4}/isolated_observations.parquet")
iso["seq"] = iso.groupby(["cid", "ts"]).cumcount()
iso_map = {(r.cid, r.ts, r.seq): r.reason for r in iso.itertuples()}

# ---------------- classify driver rows ----------------
n = len(df)
trip_id = np.full(n, None, dtype=object)
row_type = np.full(n, None, dtype=object)
sensor_pct = np.full(n, np.nan)
est_kg = np.full(n, np.nan)
p_best = np.full(n, np.nan)

cids = df["_cid"].to_numpy()
tss = df["_ts"].to_numpy()
idrs = df["_idr"].to_numpy()
isev = df["_isev"].to_numpy()
hhmm_all = df["_ts"].dt.strftime("%H:%M").to_numpy()

s_hits = s_miss = 0
for i in range(n):
    if not isev[i]:
        continue
    k = (idrs[i], cids[i], hhmm_all[i])
    cand = lut_s.get(k)
    if cand:
        tid = cand.pop(0)
        trip_id[i] = tid
        row_type[i] = "S"
        e = lut_e.get((tid, cids[i], hhmm_all[i], "S"))
        if e:
            fill_e, est_e, mat_e, snr_e = e.pop(0)
            if est_e is not None:
                est_kg[i] = est_e
            if snr_e is not None:
                sensor_pct[i] = snr_e
        s_hits += 1
    else:
        # stamped row whose (idr,cid,hhmm) not found among base stops
        row_type[i] = "S"
        trip_id[i] = idrs[i] if idrs[i] in tmeta else None
        s_miss += 1
print("stamped matched:", s_hits, "| stamped unmatched to a stop:", s_miss)

# loose rows via assignments
seq_counter = defaultdict(int)
tier = Counter()
loose_no_rec = 0
loose_idx = [i for i in range(n) if not isev[i]]
in_ra = np.zeros(n, dtype=bool)
for i in loose_idx:
    key = (cids[i], tss[i])
    k = (key[0], pd.Timestamp(key[1]), seq_counter[key])
    r = ra_map.get(k)
    if r is None:
        continue  # pre-reading, handled below (do NOT advance seq)
    seq_counter[key] += 1
    in_ra[i] = True
    st = r.status
    if st == "ASSIGNED":
        row_type[i] = "I"
        trip_id[i] = str(r.track_id)
        p_best[i] = r.p_best
        e = lut_e.get((str(r.track_id), cids[i], hhmm_all[i], "I"))
    elif st == "ASSIGNED_LOW":
        row_type[i] = "L"
        trip_id[i] = str(r.track_id)
        p_best[i] = r.p_best
        e = lut_e.get((str(r.track_id), cids[i], hhmm_all[i], "L"))
    else:
        e = None
        date = pd.Timestamp(tss[i]).strftime("%Y-%m-%d")
        ph = lut_p.get((date, cids[i], hhmm_all[i]))
        if ph:
            row_type[i] = "P"
            trip_id[i] = ph.pop(0)
        else:
            reason = iso_map.get((cids[i], pd.Timestamp(tss[i]),
                                  0)) or st  # fall back to status
            row_type[i] = f"isolated:{reason}"
    if e:
        fill_e, est_e, mat_e, snr_e = e.pop(0)
        if est_e is not None:
            est_kg[i] = est_e
        if snr_e is not None:
            sensor_pct[i] = snr_e
    tier[row_type[i]] += 1
print("loose classified:", dict(tier))

# remaining non-event rows = pre-readings; attach to next event row same bin <=15 min
pre_cnt = pre_unattached = 0
order = df.sort_values(["_cid", "_ts"], kind="stable").index.to_numpy()
pos_of = {idx: p for p, idx in enumerate(order)}
for i in loose_idx:
    if in_ra[i] or row_type[i] is not None:
        continue
    row_type[i] = "pre"
    pre_cnt += 1
    p = pos_of[i]
    # scan forward within same cid for the next event row within 15 min
    attached = False
    for q in range(p + 1, min(p + 30, len(order))):
        j = order[q]
        if cids[j] != cids[i]:
            break
        if (tss[j] - tss[i]) / np.timedelta64(1, "s") > 900:
            break
        if isev[j] and trip_id[j] is not None:
            trip_id[i] = trip_id[j]
            attached = True
            break
    if not attached:
        pre_unattached += 1
print("pre-readings:", pre_cnt, "| unattached pre:", pre_unattached)

# ---------------- trip-level flags + run totals ----------------
merged_flag = np.full(n, None, dtype=object)
flagged = np.full(n, None, dtype=object)
kg_run = np.full(n, np.nan)
km_run = np.full(n, np.nan)
for i in range(n):
    tid = trip_id[i]
    if tid is None:
        continue
    m = tmeta.get(tid)
    if m is None:
        continue  # phantom ids
    merged_flag[i] = m["merged"]
    flagged[i] = m["flagged"]
    bm = base_meta.get(m["base_id"])
    if bm:
        kg_run[i] = bm[0] if bm[0] is not None else np.nan
        km_run[i] = bm[1] if bm[1] is not None else np.nan

driver = pd.DataFrame({
    "source": "driver",
    "raw_row_id": df["_rawid"].to_numpy(),
    "cid": cids,
    "ts": df["_ts"].to_numpy(),
    "trip_id": trip_id,
    "row_type": row_type,
    "fill": df["_fill"].to_numpy(),
    "sensor_pct": sensor_pct,
    "est_kg": est_kg,
    "material": df["_mat"].to_numpy(),
    "volume_l": df["_vol"].to_numpy(),
    "kg_run_total": kg_run,
    "km_run_total": km_run,
    "merged_flag": merged_flag,
    "speed_flagged_trip": flagged,
    "p_best": p_best,
    "qc_negative": (df["_fill"] < 0).to_numpy(),
})

# ---------------- sensor drop events ----------------
sd = pd.read_parquet(f"{W4}/sensor_drops.parquet")
sd["cid"] = sd["cid"].str.strip()
svol = sd["cid"].map(reg_vol)
smat = sd["cid"].map(reg_mat)
dens = smat.map(DENS_MID)
sest = sd["drop_units"] / 100.0 * (svol.fillna(2500.0) / 1000.0) * dens

sensor = pd.DataFrame({
    "source": "sensor_drop",
    "raw_row_id": pd.array([None] * len(sd), dtype="Int64"),
    "cid": sd["cid"],
    "ts": sd["ts_after"],
    "trip_id": None,
    "row_type": None,
    "fill": sd["fill_after"].astype(float),
    "sensor_pct": sd["pct_of_ceiling_before"],
    "est_kg": sest,
    "material": smat,
    "volume_l": svol,
    "kg_run_total": np.nan,
    "km_run_total": np.nan,
    "merged_flag": None,
    "speed_flagged_trip": None,
    "p_best": np.nan,
    "qc_negative": False,
})

master = pd.concat([driver, sensor], ignore_index=True)
master["raw_row_id"] = master["raw_row_id"].astype("Int64")
master["merged_flag"] = master["merged_flag"].astype("boolean")
master["speed_flagged_trip"] = master["speed_flagged_trip"].astype("boolean")
master["qc_negative"] = master["qc_negative"].astype("boolean")
for c in ["source", "cid", "trip_id", "row_type", "material"]:
    master[c] = master[c].astype("string")
master["ts"] = pd.to_datetime(master["ts"])

out_parquet = f"{BASE}/Brain/03_db/parquet/master_events_w4.parquet"
master.to_parquet(out_parquet, index=False)
print("master rows:", len(master), "->", out_parquet)
print(master["source"].value_counts().to_dict())

# ---------------- trip census ----------------
def trip_class(t):
    if t.get("part"):
        return ("split_multi_vehicle" if t.get("verdict") == "multi-vehicle"
                else "split_batch_entry")
    if t.get("merged"):
        return "merged_flagged" if t.get("speed_flags") else "merged_clean"
    return "stamped_single"

census = defaultdict(lambda: {"trips": 0, "stops_total": 0,
                              "stops_by_type": Counter()})
for t in trips:
    c = census[trip_class(t)]
    c["trips"] += 1
    c["stops_total"] += len(t["stops"])
    for s in t["stops"]:
        c["stops_by_type"][s[4]] += 1
c = census["phantom"]
for t in phant:
    c["trips"] += 1
    c["stops_total"] += len(t["stops"])
    for s in t["stops"]:
        c["stops_by_type"][s[4]] += 1

tiers = driver["row_type"].value_counts(dropna=False).to_dict()
tiers = {("unclassified" if pd.isna(k) else k): int(v) for k, v in tiers.items()}

census_out = {
    "task": "D1/T6a trip census + master dataset",
    "trip_classes": {k: {"trips": v["trips"],
                         "stops_total": v["stops_total"],
                         "stops_by_type": dict(v["stops_by_type"])}
                     for k, v in sorted(census.items())},
    "trip_class_note": ("trips_v6.json stop lists double-carry readings: v5 "
                        "inferred stops were relabelled 'S' at merge time AND "
                        "the same loose pool was re-assigned as I/L, so "
                        "stops_total across classes (287,408 driver-file "
                        "stops) exceeds the 264,817 raw rows. The master "
                        "parquet is deduplicated: one row per raw reading; "
                        "row_type 'S' is granted only to the 60,916 stamped "
                        "collection rows."),
    "reading_tiers": {
        "S_stamped_collection": tiers.get("S", 0),
        "pre_reading": tiers.get("pre", 0),
        "I_inferred_assigned": tiers.get("I", 0),
        "L_inferred_low_confidence": tiers.get("L", 0),
        "P_phantom_absorbed": tiers.get("P", 0),
        "isolated_by_reason": {k.split(":", 1)[1]: v for k, v in tiers.items()
                               if isinstance(k, str) and k.startswith("isolated:")},
        "unclassified": tiers.get("unclassified", 0),
        "total_driver_rows": int(len(driver)),
    },
    "master": {
        "rows_total": int(len(master)),
        "rows_driver": int((master["source"] == "driver").sum()),
        "rows_sensor_drop": int((master["source"] == "sensor_drop").sum()),
        "path": "Brain/03_db/parquet/master_events_w4.parquet",
    },
}
with open(f"{W4}/trip_census.json", "w", encoding="utf-8") as f:
    json.dump(census_out, f, indent=2, ensure_ascii=False)
print(json.dumps(census_out["trip_classes"], indent=1))
print(json.dumps(census_out["reading_tiers"], indent=1))
