# A2 (T4) - Sensor drop-event log + quality trends
# Inputs (read-only): Brain/03_db/parquet/raw_sensors.parquet, raw_collections.parquet
# Outputs: W4/02_data_work/sensor_drops.parquet, W4/02_data_work/sensor_quality.json
import json
import numpy as np
import pandas as pd

ROOT = r"C:/Users/esmae/Desktop/phd Esmaeil/THESIS CLAUDE"
SENS = f"{ROOT}/Brain/03_db/parquet/raw_sensors.parquet"
COLL = f"{ROOT}/Brain/03_db/parquet/raw_collections.parquet"
OUT_PARQ = f"{ROOT}/W4/02_data_work/sensor_drops.parquet"
OUT_JSON = f"{ROOT}/W4/02_data_work/sensor_quality.json"

# ---------- load sensors ----------
s = pd.read_parquet(SENS, columns=["idcontentor", "Data da leitura", "Enchimento"])
s.columns = ["cid", "ts", "fill"]
s["ts"] = pd.to_datetime(s["ts"], errors="coerce")
s["fill"] = pd.to_numeric(s["fill"], errors="coerce")
s = s.dropna(subset=["ts", "fill"]).copy()
s["cid"] = s["cid"].astype(str)
s = s.sort_values(["cid", "ts"], kind="mergesort").reset_index(drop=True)
s["valid"] = (s["fill"] >= 0) & (s["fill"] <= 100)
s["neg"] = s["fill"] < 0

# per-cid ceiling = max valid fill
ceiling = s.loc[s["valid"]].groupby("cid")["fill"].max().rename("ceiling")

# adjacency to a negative-code episode in the FULL time-ordered per-cid sequence
same_prev = s["cid"].eq(s["cid"].shift(1))
same_next = s["cid"].eq(s["cid"].shift(-1))
s["adj_neg"] = (s["neg"].shift(1, fill_value=False) & same_prev) | (
    s["neg"].shift(-1, fill_value=False) & same_next
)

# ---------- drop events on the valid-only subsequence ----------
v = s.loc[s["valid"], ["cid", "ts", "fill", "adj_neg"]].copy()
v["ts_prev"] = v.groupby("cid")["ts"].shift(1)
v["fill_prev"] = v.groupby("cid")["fill"].shift(1)
v["adj_neg_prev"] = v.groupby("cid")["adj_neg"].shift(1)
v["gap_min"] = (v["ts"] - v["ts_prev"]).dt.total_seconds() / 60.0
v["drop_units"] = v["fill_prev"] - v["fill"]

ev = v[
    v["ts_prev"].notna()
    & (v["gap_min"] <= 24 * 60)
    & (v["drop_units"] >= 25)
    & (v["adj_neg_prev"] != True)  # 'before' reading not adjacent to a negative episode
].copy()
ev = ev.merge(ceiling, on="cid", how="left")
ev["pct_of_ceiling_before"] = np.where(
    ev["ceiling"] > 0, ev["fill_prev"] / ev["ceiling"] * 100.0, np.nan
)

drops = pd.DataFrame(
    {
        "cid": ev["cid"],
        "ts_before": ev["ts_prev"],
        "ts_after": ev["ts"],
        "window_min": ev["gap_min"].round(2),
        "fill_before": ev["fill_prev"],
        "fill_after": ev["fill"],
        "drop_units": ev["drop_units"],
        "pct_of_ceiling_before": ev["pct_of_ceiling_before"].round(1),
    }
).sort_values(["cid", "ts_after"]).reset_index(drop=True)
drops.to_parquet(OUT_PARQ, index=False)

drops["year"] = drops["ts_after"].dt.year
per_year_drops = drops.groupby("year").size().to_dict()

# ---------- negatives recap by year (two families, reused convention) ----------
s["year"] = s["ts"].dt.year
neg_recap = {}
for y, g in s.groupby("year"):
    n = len(g)
    nn = int(g["neg"].sum())
    small = int(((g["fill"] < 0) & (g["fill"] >= -9)).sum())   # small family -1..-9
    large = int((g["fill"] <= -10).sum())                       # large family -10..-116
    neg_recap[int(y)] = {
        "readings": n,
        "negatives": nn,
        "neg_share_pct": round(100 * nn / n, 2),
        "family_small_-1..-9": small,
        "family_large_-10..-116": large,
    }

# ---------- driver-vs-sensor agreement by year (record-level, +/-3h, |diff|<=25 of ceiling-normalized) ----------
c = pd.read_parquet(COLL, columns=["idcontentor", "Data da leitura", "Enchimento", "idrecolha"])
c.columns = ["cid", "ts", "fill", "idrecolha"]
c["ts"] = pd.to_datetime(c["ts"], errors="coerce")
c["fill"] = pd.to_numeric(c["fill"], errors="coerce")
c["cid"] = c["cid"].astype(str)
c = c.dropna(subset=["ts"]).copy()

instrumented = set(ceiling.index)
cd = c[(c["cid"].isin(instrumented)) & (c["fill"] >= 0) & (c["fill"] <= 100)].copy()
cd = cd.sort_values("ts", kind="mergesort")

sv = s.loc[s["valid"], ["cid", "ts", "fill"]].rename(columns={"ts": "s_ts", "fill": "s_fill"})
sv = sv.sort_values("s_ts", kind="mergesort")

m = pd.merge_asof(
    cd,
    sv,
    left_on="ts",
    right_on="s_ts",
    by="cid",
    direction="nearest",
    tolerance=pd.Timedelta(hours=3),
)
m = m.dropna(subset=["s_fill"]).merge(ceiling, on="cid", how="left")
m["s_norm"] = np.where(m["ceiling"] > 0, m["s_fill"] / m["ceiling"] * 100.0, np.nan)
m["agree"] = (m["fill"] - m["s_norm"]).abs() <= 25
m["year"] = m["ts"].dt.year
agreement = {}
for y, g in m.groupby("year"):
    agreement[int(y)] = {
        "matched_records": int(len(g)),
        "agree_pct": round(100 * g["agree"].mean(), 1),
    }

# ---------- drop events vs stamped emptyings per year (instrumented bins) ----------
ce = c[(c["cid"].isin(instrumented)) & c["idrecolha"].notna() & (c["idrecolha"] != "")].copy()
ce["year"] = ce["ts"].dt.year
stamped = ce.drop_duplicates(subset=["cid", "idrecolha"]).groupby("year").size().to_dict()
coverage = {}
for y in sorted(set(list(per_year_drops.keys()) + list(stamped.keys()))):
    d = int(per_year_drops.get(y, 0))
    st = int(stamped.get(y, 0))
    coverage[int(y)] = {
        "sensor_drop_events": d,
        "stamped_emptyings_instrumented": st,
        "drops_per_stamped": round(d / st, 2) if st else None,
    }

# ---------- headline stats + findings ----------
n_events = int(len(drops))
med_win = float(drops["window_min"].median())
tot_neg = int(s["neg"].sum())
tot_rows = int(len(s))
tot_drops = n_events
tot_stamped = int(sum(stamped.values()))
overall_agree = round(100 * m["agree"].mean(), 1)

findings = [
    f"Sensors registered {tot_drops:,} drop events (fill fall >=25 units within 24 h) against "
    f"{tot_stamped:,} stamped driver emptyings on the same instrumented bins - the sensor stream "
    f"sees roughly {tot_drops / max(tot_stamped,1):.1f} drop events per stamped emptying, so many "
    f"emptyings (and some non-collection disturbances) are visible only in the sensor data.",
    f"Negative error codes make up {round(100*tot_neg/tot_rows,1)}% of all sensor rows overall, split "
    f"between the small family (-1..-9) and the large family (-10..-116, dominated by -116); the "
    f"yearly share varies (see negatives_by_year), so per-year exposure corrections are needed.",
    f"Record-level driver-vs-sensor agreement (+/-3 h nearest reading, within 25 points of the "
    f"ceiling-normalized fill) is {overall_agree}% overall and varies by year - consistent with the "
    f"earlier finding that the two instruments are not interchangeable.",
]

quality = {
    "task": "A2/T4 sensor drop-event log + quality trends",
    "definitions": {
        "drop_event": "fill decrease >=25 raw units between consecutive valid (0..100) readings, gap <=24 h, 'before' reading not adjacent (+/-1 reading) to a negative-code episode",
        "ceiling": "per-container max valid reading",
        "agreement": "driver record matched to nearest valid sensor reading within +/-3 h; agree if |driver - sensor/ceiling*100| <= 25",
        "stamped_emptying": "distinct (container, idrecolha) driver record with timestamp, instrumented bins only",
        "families": "small = -1..-9, large = -10..-116 (convention from R2-01 Rev C)",
    },
    "drop_events": {
        "total": n_events,
        "per_year": {int(k): int(v) for k, v in sorted(per_year_drops.items())},
        "median_window_min": round(med_win, 1),
        "containers_with_events": int(drops["cid"].nunique()),
    },
    "negatives_by_year": neg_recap,
    "agreement_by_year": agreement,
    "drops_vs_stamped_by_year": coverage,
    "findings": findings,
}
with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(quality, f, indent=2, ensure_ascii=False)

print(json.dumps({
    "events": n_events,
    "per_year": {int(k): int(v) for k, v in sorted(per_year_drops.items())},
    "median_window_min": round(med_win, 1),
    "agreement_overall_pct": overall_agree,
    "coverage": coverage,
}, indent=2))
