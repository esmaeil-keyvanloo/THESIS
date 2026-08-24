# TASK E (T3 clean) - Sensor cleaning v2 per sensor_anomaly_report.json rules
import json
import numpy as np
import pandas as pd

RAW = r"C:/Users/esmae/Desktop/phd Esmaeil/THESIS CLAUDE/Brain/03_db/parquet/raw_sensors.parquet"
OUT = r"C:/Users/esmae/Desktop/phd Esmaeil/THESIS CLAUDE/W5/02_data_work"

df = pd.read_parquet(RAW, columns=["idcontentor", "Data da leitura", "Enchimento"])
df = df.rename(columns={"idcontentor": "cid", "Data da leitura": "ts", "Enchimento": "fill"})
df["cid"] = df["cid"].astype(str)
df["ts"] = pd.to_datetime(df["ts"])
df["fill"] = pd.to_numeric(df["fill"], errors="coerce").astype("float64")
df = df.sort_values(["cid", "ts"], kind="mergesort").reset_index(drop=True)
n_raw = len(df)

reason = pd.Series(pd.NA, index=df.index, dtype="object")

# --- 1) Negatives: NEG_SMALL (-1..-10, transient errors) vs NEG_CODE (<-10, hard error codes)
neg = df["fill"] < 0
reason[neg & (df["fill"] >= -10)] = "NEG_SMALL"
reason[neg & (df["fill"] < -10)] = "NEG_CODE"

# --- 2) Duplicate timestamps (same cid+ts) among valid rows: keep first
alive = reason.isna()
dup = alive & df.loc[alive, ["cid", "ts"]].duplicated(keep="first").reindex(df.index, fill_value=False)
reason[dup] = "DUPLICATE"

# --- 3) Stuck runs: >=6 identical consecutive valid values spanning >48h -> drop all but first
alive = reason.isna()
a = df[alive].copy()
new_run = (a["cid"] != a["cid"].shift()) | (a["fill"] != a["fill"].shift())
a["run"] = new_run.cumsum()
g = a.groupby("run")
run_n = g["ts"].transform("size")
run_span = g["ts"].transform("max") - g["ts"].transform("min")
stuck_run = (run_n >= 6) & (run_span > pd.Timedelta(hours=48))
first_of_run = new_run
stuck_drop_idx = a.index[stuck_run & ~first_of_run]
reason[stuck_drop_idx] = "STUCK"

# --- 4) Spikes: rise >= +40 units between consecutive remaining readings <=30 min apart -> drop the spiked reading
alive = reason.isna()
a = df[alive]
same = a["cid"] == a["cid"].shift()
rise = a["fill"] - a["fill"].shift()
dt = a["ts"] - a["ts"].shift()
spike = same & (rise >= 40) & (dt <= pd.Timedelta(minutes=30))
reason[a.index[spike]] = "SPIKE"

# --- Split clean / removed
df["reason"] = reason
clean = df[df["reason"].isna()].drop(columns=["reason"]).copy()
removed = df[df["reason"].notna()].copy()

# --- 5) Eras and per-bin-era ceiling
def era_of(ts):
    out = np.where(ts <= pd.Timestamp("2020-10-31 23:59:59.999999"), "E1",
          np.where(ts <= pd.Timestamp("2022-12-31 23:59:59.999999"), "E2", "E3"))
    return out

clean["era"] = era_of(clean["ts"])
ceil_map = clean.groupby(["cid", "era"])["fill"].max().rename("ceiling")
clean = clean.merge(ceil_map, on=["cid", "era"], how="left")
clean["pct"] = np.where(clean["ceiling"] > 0, clean["fill"] / clean["ceiling"] * 100.0, np.nan)
clean = clean.sort_values(["cid", "ts"], kind="mergesort").reset_index(drop=True)

# --- 6) Drops v2 from CLEAN readings only
c = clean
same = c["cid"] == c["cid"].shift()
prev_fill = c["fill"].shift()
prev_ts = c["ts"].shift()
prev_pct = c["pct"].shift()
dt = c["ts"] - prev_ts
fall = prev_fill - c["fill"]
is_drop = same & (fall >= 25) & (dt <= pd.Timedelta(hours=24))

drops = pd.DataFrame({
    "cid": c.loc[is_drop, "cid"].values,
    "t_before": prev_ts[is_drop].values,
    "t_after": c.loc[is_drop, "ts"].values,
    "window_min": (dt[is_drop].dt.total_seconds() / 60.0).round(1).values,
    "drop_units": fall[is_drop].values,
    "pct_before": prev_pct[is_drop].round(1).values,
})
drops["confidence"] = np.where(drops["window_min"] <= 360, "high",
                       np.where(drops["window_min"] <= 720, "med", "low"))

# Exclude drops whose before->after interval contains a removed reading (touches a dropped reading)
rem = removed[["cid", "ts"]].sort_values(["cid", "ts"])
rem_by_cid = {k: v["ts"].values for k, v in rem.groupby("cid")}
keep_mask = np.ones(len(drops), dtype=bool)
tb = drops["t_before"].values
ta = drops["t_after"].values
cids = drops["cid"].values
for i in range(len(drops)):
    arr = rem_by_cid.get(cids[i])
    if arr is None:
        continue
    lo = np.searchsorted(arr, tb[i], side="right")
    hi = np.searchsorted(arr, ta[i], side="left")
    if hi > lo:
        keep_mask[i] = False
n_drops_raw = len(drops)
n_drops_excluded = int((~keep_mask).sum())
drops = drops[keep_mask].reset_index(drop=True)

# --- 7) Outputs
clean_out = clean[["cid", "ts", "fill", "era", "pct"]]
clean_out.to_parquet(f"{OUT}/sensor_clean.parquet", index=False)
removed_out = removed[["cid", "ts", "fill", "reason"]]
removed_out.to_parquet(f"{OUT}/sensor_removed.parquet", index=False)
drops.to_parquet(f"{OUT}/sensor_drops_v2.parquet", index=False)

# --- 8) Stats
years = sorted(set(clean["ts"].dt.year) | set(removed["ts"].dt.year))
first_year = clean.groupby("cid")["ts"].min().dt.year
active_by_year = {y: set(clean.loc[clean["ts"].dt.year == y, "cid"]) for y in years}
per_year = {}
seen = set()
for y in years:
    act = active_by_year.get(y, set())
    added = set(first_year[first_year == y].index)
    silent = seen - act
    rem_y = removed[removed["ts"].dt.year == y]
    dr_y = drops[pd.to_datetime(drops["t_after"]).dt.year == y]
    per_year[str(y)] = {
        "sensors_active": len(act),
        "sensors_added": len(added),
        "sensors_silent": len(silent),
        "readings_kept": int((clean["ts"].dt.year == y).sum()),
        "readings_removed_by_reason": {k: int(v) for k, v in rem_y["reason"].value_counts().items()},
        "drops_count": int(len(dr_y)),
        "drops_by_confidence": {k: int(v) for k, v in dr_y["confidence"].value_counts().items()},
    }
    seen |= act

era_ceil = clean.groupby(["cid", "era"])["fill"].max().reset_index()
era_table = {}
for e in ["E1", "E2", "E3"]:
    sub = clean[clean["era"] == e]
    ce = era_ceil[era_ceil["era"] == e]["fill"]
    era_table[e] = {
        "bins": int(sub["cid"].nunique()),
        "readings": int(len(sub)),
        "ceiling_median": float(ce.median()) if len(ce) else None,
        "ceiling_p25": float(ce.quantile(0.25)) if len(ce) else None,
        "ceiling_p75": float(ce.quantile(0.75)) if len(ce) else None,
        "ceiling_max": float(ce.max()) if len(ce) else None,
        "pct_mean": round(float(sub["pct"].mean()), 1),
    }

stats = {
    "input_rows": int(n_raw),
    "kept_rows": int(len(clean)),
    "removed_rows": int(len(removed)),
    "removed_by_reason": {k: int(v) for k, v in removed["reason"].value_counts().items()},
    "drops_v2": {
        "detected": int(n_drops_raw),
        "excluded_touching_removed": n_drops_excluded,
        "kept": int(len(drops)),
        "by_confidence": {k: int(v) for k, v in drops["confidence"].value_counts().items()},
    },
    "per_year": per_year,
    "era_table": era_table,
    "rules": {
        "NEG_SMALL": "fill in [-10, -1] transient negative",
        "NEG_CODE": "fill < -10 hard sensor error code",
        "DUPLICATE": "same cid+ts, keep first",
        "STUCK": ">=6 identical consecutive valid values spanning >48h; first kept, rest dropped",
        "SPIKE": "rise >= +40 units within <=30 min; spiked reading dropped",
        "eras": "E1 <=2020-10-31, E2 2020-11-01..2022-12-31, E3 >=2023-01-01",
        "ceiling": "per-bin-era max of clean fill; pct = fill/ceiling*100",
        "drops_v2": "clean consecutive fall >=25 units within <=24h; confidence <=6h high, <=12h med, else low; excluded if a removed reading lies between t_before and t_after",
    },
}
with open(f"{OUT}/sensor_stats.json", "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=2)

print(json.dumps({
    "kept": stats["kept_rows"], "removed": stats["removed_rows"],
    "by_reason": stats["removed_by_reason"], "drops": stats["drops_v2"],
}, indent=2))
