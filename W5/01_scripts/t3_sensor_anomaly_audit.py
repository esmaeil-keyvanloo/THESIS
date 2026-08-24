# T3 FULL sensor anomaly audit (read-only on data)
# Output: W5/02_data_work/sensor_anomaly_report.json
import json
import numpy as np
import pandas as pd

ROOT = r"C:\Users\esmae\Desktop\phd Esmaeil\THESIS CLAUDE"
OUT = ROOT + r"\W5\02_data_work\sensor_anomaly_report.json"

FAM = {
    "Mistura de embalagens": "packaging",
    "Embalagens de Vidro": "glass",
}
def fam(d):
    if d in FAM:
        return FAM[d]
    return "paper"  # Embalagens de papel e cartao (mojibake-safe)

df = pd.read_parquet(ROOT + r"\Brain\03_db\parquet\raw_sensors.parquet",
                     columns=["idcontentor", "description", "Data da leitura", "Enchimento"])
df["ts"] = pd.to_datetime(df["Data da leitura"])
df["fill"] = pd.to_numeric(df["Enchimento"], errors="coerce").astype("int32")
df["family"] = df["description"].map(fam)
df["year"] = df["ts"].dt.year
df = df.sort_values(["idcontentor", "ts"]).reset_index(drop=True)
n_total = len(df)
valid = df["fill"] >= 0

report = {"meta": {
    "rows": int(n_total),
    "bins": int(df["idcontentor"].nunique()),
    "ts_min": str(df["ts"].min()), "ts_max": str(df["ts"].max()),
    "valid_rows": int(valid.sum()),
    "negative_rows": int((~valid).sum()),
    "definitions": {
        "valid": "Enchimento >= 0 (range observed 0..84); negatives are sensor error codes",
        "stuck": ">=6 identical consecutive valid values per bin spanning >48h",
        "spike": "rise >= +40 units between consecutive valid readings <=30 min apart",
        "rebound": "valid reading immediately after a negative run that is >= pre-run valid value (sensor recovers, no data lost) vs lower (possible missed emptying)",
        "big_drop": "fall >= 30 units between consecutive valid readings (collection-like)",
        "inconsistent_after_drop": "rise >= 20 units within 6h after a big drop",
        "silent_gap": "> 7 days between consecutive readings inside a bin's active window",
        "near_zero_bin": ">= 100 valid readings and >= 95% of them == 0",
        "eras": "E1 2020-01..2020-10 (pre Nov-2020 scale change), E2 2020-11..2022-12, E3 2023-01..2024-04 (post cadence doubling)",
    },
}}

# ---------- 1. negatives by family/year ----------
neg = df[~valid]
tab = neg.pivot_table(index="year", columns="family", values="fill", aggfunc="size", fill_value=0)
report["negatives"] = {
    "total": int(len(neg)),
    "share_pct": round(100 * len(neg) / n_total, 2),
    "by_family_year": {str(y): {c: int(v) for c, v in r.items()} for y, r in tab.iterrows()},
    "top_codes": {str(k): int(v) for k, v in neg["fill"].value_counts().head(10).items()},
    "bins_with_negatives": int(neg["idcontentor"].nunique()),
}

# ---------- per-bin sequential work ----------
g = df.groupby("idcontentor", sort=False)
df["prev_fill"] = g["fill"].shift()
df["prev_ts"] = g["ts"].shift()
df["dt_min"] = (df["ts"] - df["prev_ts"]).dt.total_seconds() / 60.0

# valid-only consecutive pairs (within bin)
dv = df[valid].copy()
gv = dv.groupby("idcontentor", sort=False)
dv["pf"] = gv["fill"].shift()
dv["pt"] = gv["ts"].shift()
dv["d_fill"] = dv["fill"] - dv["pf"]
dv["d_min"] = (dv["ts"] - dv["pt"]).dt.total_seconds() / 60.0

# ---------- 2. STUCK runs ----------
same = (dv["fill"] == dv["pf"])
run_id = (~same).cumsum()  # new run whenever value changes (or new bin, since pf NaN != fill)
runs = dv.groupby(run_id).agg(cid=("idcontentor", "first"), val=("fill", "first"),
                              n=("fill", "size"), t0=("ts", "first"), t1=("ts", "last"))
runs["hours"] = (runs["t1"] - runs["t0"]).dt.total_seconds() / 3600.0
stuck = runs[(runs["n"] >= 6) & (runs["hours"] > 48)].sort_values("hours", ascending=False)
stuck_nz = stuck[stuck["val"] > 0]
report["stuck_runs"] = {
    "count": int(len(stuck)),
    "count_nonzero_value": int(len(stuck_nz)),
    "count_zero_value": int(len(stuck) - len(stuck_nz)),
    "bins_affected": int(stuck["cid"].nunique()),
    "longest_examples": [
        {"cid": r.cid, "value": int(r.val), "n_readings": int(r.n),
         "start": str(r.t0), "end": str(r.t1), "days": round(r.hours / 24, 1)}
        for r in stuck.head(5).itertuples()],
    "longest_nonzero_examples": [
        {"cid": r.cid, "value": int(r.val), "n_readings": int(r.n),
         "start": str(r.t0), "end": str(r.t1), "days": round(r.hours / 24, 1)}
        for r in stuck_nz.head(5).itertuples()],
}

# ---------- 3. SPIKES ----------
sp = dv[(dv["d_fill"] >= 40) & (dv["d_min"] <= 30) & (dv["d_min"] > 0)]
report["spikes"] = {
    "count": int(len(sp)),
    "bins_affected": int(sp["idcontentor"].nunique()),
    "by_year": {str(k): int(v) for k, v in sp["year"].value_counts().sort_index().items()},
    "examples": [
        {"cid": r.idcontentor, "ts": str(r.ts), "from": int(r.pf), "to": int(r.fill),
         "minutes": round(r.d_min, 1)}
        for r in sp.sort_values("d_fill", ascending=False).head(5).itertuples()],
}

# ---------- 4. post-negative rebounds ----------
# find negative runs and compare last valid before vs first valid after
df["is_neg"] = ~valid
d = df
neg_block = (d["is_neg"] & (~d["is_neg"].shift(fill_value=False) | (d["idcontentor"] != d["idcontentor"].shift())))
d["neg_run"] = neg_block.cumsum().where(d["is_neg"])
# last valid fill before each row (per bin)
d["last_valid"] = d["fill"].where(valid).groupby(d["idcontentor"]).ffill()
d["prev_last_valid"] = d.groupby("idcontentor")["last_valid"].shift()
nr = d[d["is_neg"]].groupby("neg_run").agg(cid=("idcontentor", "first"), n=("fill", "size"),
                                           t0=("ts", "first"), t1=("ts", "last"),
                                           before=("prev_last_valid", "first"))
# first valid after: next valid row in same bin after t1
d["next_valid_fill"] = d["fill"].where(valid)
d["next_valid_fill"] = d.groupby("idcontentor")["next_valid_fill"].bfill()
after = d[d["is_neg"]].groupby("neg_run")["next_valid_fill"].last()  # bfill at last neg row = first valid after
nr["after"] = after
nr2 = nr.dropna(subset=["before", "after"])
reb = nr2[nr2["after"] >= nr2["before"]]
lower = nr2[nr2["after"] < nr2["before"]]
report["post_negative_rebounds"] = {
    "negative_runs_total": int(len(nr)),
    "runs_with_before_and_after": int(len(nr2)),
    "rebound_ge_before": int(len(reb)),
    "resume_lower_than_before": int(len(lower)),
    "rebound_share_pct": round(100 * len(reb) / max(len(nr2), 1), 1),
    "examples_rebound": [
        {"cid": r.cid, "neg_readings": int(r.n), "start": str(r.t0), "end": str(r.t1),
         "before": int(r.before), "after": int(r.after)}
        for r in reb.head(3).itertuples()],
    "examples_lower": [
        {"cid": r.cid, "neg_readings": int(r.n), "start": str(r.t0), "end": str(r.t1),
         "before": int(r.before), "after": int(r.after)}
        for r in lower.sort_values("before", ascending=False).head(3).itertuples()],
}

# ---------- 5. duplicate timestamps per cid ----------
dup_mask = df.duplicated(subset=["idcontentor", "ts"], keep=False)
dups = df[dup_mask]
dup_groups = dups.groupby(["idcontentor", "ts"])
n_dup_groups = dup_groups.ngroups
conflict = dup_groups["fill"].nunique()
n_conflict = int((conflict > 1).sum())
ex_conf = conflict[conflict > 1].head(3)
report["duplicate_timestamps"] = {
    "duplicate_rows": int(len(dups)),
    "duplicate_pairs_groups": int(n_dup_groups),
    "groups_with_conflicting_fill": n_conflict,
    "bins_affected": int(dups["idcontentor"].nunique()),
    "examples_conflicting": [
        {"cid": cid, "ts": str(ts),
         "values": [int(x) for x in df[(df["idcontentor"] == cid) & (df["ts"] == ts)]["fill"]]}
        for (cid, ts) in ex_conf.index],
}

# ---------- 6. cadence eras ----------
monthly = df.set_index("ts").groupby(pd.Grouper(freq="MS")).size()
days_in_month = monthly.index.days_in_month
per_day = (monthly / days_in_month).round(1)
# change-points: month-over-month ratio > 1.5 or < 0.67 with substantial volume
ratios = per_day / per_day.shift()
cps = [str(i.date()) for i, r in ratios.items()
       if (r > 1.5 or r < 0.67) and per_day.get(i, 0) + per_day.shift().get(i, 0) > 100]
report["cadence"] = {
    "readings_per_day_by_month": {str(i.date()): float(v) for i, v in per_day.items()},
    "change_point_months_ratio_gt1.5_or_lt0.67": cps,
    "mean_per_day_2020": float(per_day[per_day.index.year == 2020].mean().round(1)),
    "mean_per_day_2021": float(per_day[per_day.index.year == 2021].mean().round(1)),
    "mean_per_day_2022": float(per_day[per_day.index.year == 2022].mean().round(1)),
    "mean_per_day_2023": float(per_day[per_day.index.year == 2023].mean().round(1)),
    "mean_per_day_2024": float(per_day[per_day.index.year == 2024].mean().round(1)),
}

# ---------- 7. per-bin ceiling drift across eras ----------
def era(ts):
    if ts < pd.Timestamp("2020-11-01"):
        return "E1"
    if ts < pd.Timestamp("2023-01-01"):
        return "E2"
    return "E3"
dv["era"] = dv["ts"].map(era)
ceil = dv.pivot_table(index="idcontentor", columns="era", values="fill", aggfunc="max")
counts = dv.pivot_table(index="idcontentor", columns="era", values="fill", aggfunc="size")
# only bins with >=30 valid readings in both eras compared
def drift(a, b):
    m = (counts.get(a, pd.Series()).ge(30)) & (counts.get(b, pd.Series()).ge(30))
    sub = ceil.loc[m[m].index]
    dd = sub[b] - sub[a]
    return sub, dd
sub12, d12 = drift("E1", "E2")
sub23, d23 = drift("E2", "E3")
report["ceiling_drift"] = {
    "era_global_max": {e: int(dv[dv["era"] == e]["fill"].max()) for e in ["E1", "E2", "E3"]},
    "era_global_p99": {e: float(np.percentile(dv[dv["era"] == e]["fill"], 99)) for e in ["E1", "E2", "E3"]},
    "E1_to_E2": {
        "bins_compared": int(len(d12)),
        "median_ceiling_change": float(d12.median()) if len(d12) else None,
        "bins_ceiling_up_gt20": int((d12 > 20).sum()),
        "bins_ceiling_down_gt20": int((d12 < -20).sum()),
    },
    "E2_to_E3": {
        "bins_compared": int(len(d23)),
        "median_ceiling_change": float(d23.median()) if len(d23) else None,
        "bins_ceiling_up_gt20": int((d23 > 20).sum()),
        "bins_ceiling_down_gt20": int((d23 < -20).sum()),
    },
    "examples_biggest_E1E2_shift": [
        {"cid": i, "E1_max": int(sub12.loc[i, "E1"]), "E2_max": int(sub12.loc[i, "E2"])}
        for i in d12.abs().sort_values(ascending=False).head(3).index] if len(d12) else [],
}

# ---------- 8. long silent gaps ----------
gaps = df[df["dt_min"] > 7 * 24 * 60]
report["silent_gaps_gt7d"] = {
    "count": int(len(gaps)),
    "bins_affected": int(gaps["idcontentor"].nunique()),
    "longest_examples": [
        {"cid": r.idcontentor, "gap_days": round(r.dt_min / 1440, 1),
         "from": str(r.prev_ts), "to": str(r.ts)}
        for r in gaps.sort_values("dt_min", ascending=False).head(5).itertuples()],
    "total_silent_days": round(float(gaps["dt_min"].sum() / 1440), 0),
}

# ---------- 9. inconsistent rise right after big drop ----------
dv["next_fill"] = gv["fill"].shift(-1)
dv["next_dt_h"] = (gv["ts"].shift(-1) - dv["ts"]).dt.total_seconds() / 3600.0
drops = dv[(dv["d_fill"] <= -30)]
incons = drops[(drops["next_fill"] - drops["fill"] >= 20) & (drops["next_dt_h"] <= 6)]
report["post_drop_inconsistent"] = {
    "big_drops_ge30": int(len(drops)),
    "rise_ge20_within_6h_after_drop": int(len(incons)),
    "share_pct": round(100 * len(incons) / max(len(drops), 1), 2),
    "bins_affected": int(incons["idcontentor"].nunique()),
    "examples": [
        {"cid": r.idcontentor, "ts": str(r.ts), "pre_drop": int(r.pf), "post_drop": int(r.fill),
         "rebound_to": int(r.next_fill), "hours_to_rebound": round(r.next_dt_h, 1)}
        for r in incons.head(5).itertuples()],
}

# ---------- 10. almost-constant-zero bins ----------
vz = dv.groupby("idcontentor")["fill"].agg(n="size", zero=lambda s: (s == 0).sum(), mx="max")
vz["zero_pct"] = 100 * vz["zero"] / vz["n"]
nz = vz[(vz["n"] >= 100) & (vz["zero_pct"] >= 95)].sort_values("zero_pct", ascending=False)
report["near_zero_bins"] = {
    "count": int(len(nz)),
    "examples": [
        {"cid": i, "valid_readings": int(r["n"]), "pct_zero": round(r["zero_pct"], 1),
         "max_ever": int(r["mx"])} for i, r in nz.head(5).iterrows()],
}

# ---------- bullets ----------
b = []
b.append(f"{report['negatives']['total']:,} negative readings ({report['negatives']['share_pct']}% of {n_total:,}) across {report['negatives']['bins_with_negatives']} bins; code -116 alone {report['negatives']['top_codes'].get('-116', 0):,} rows")
yr_tot = {y: sum(v.values()) for y, v in report["negatives"]["by_family_year"].items()}
peak_y = max(yr_tot, key=yr_tot.get)
b.append(f"Negatives peak in {peak_y} ({yr_tot[peak_y]:,} rows); by-family/year table in report")
b.append(f"{report['stuck_runs']['count']:,} stuck runs (>=6 identical valid values >48h) on {report['stuck_runs']['bins_affected']} bins; {report['stuck_runs']['count_nonzero_value']:,} at non-zero values (frozen sensors)")
if report["stuck_runs"]["longest_examples"]:
    e0 = report["stuck_runs"]["longest_examples"][0]
    b.append(f"Longest stuck run: bin {e0['cid']} at {e0['value']} for {e0['days']} days ({e0['n_readings']} readings)")
b.append(f"{report['spikes']['count']:,} spikes (+40 within 30 min) on {report['spikes']['bins_affected']} bins")
b.append(f"{report['post_negative_rebounds']['rebound_share_pct']}% of {report['post_negative_rebounds']['runs_with_before_and_after']:,} negative runs rebound at/above pre-error level; {report['post_negative_rebounds']['resume_lower_than_before']:,} resume lower (possible masked emptying)")
b.append(f"{report['duplicate_timestamps']['duplicate_rows']:,} duplicate-timestamp rows ({report['duplicate_timestamps']['duplicate_pairs_groups']:,} groups, {report['duplicate_timestamps']['groups_with_conflicting_fill']:,} with conflicting fill values)")
b.append(f"Cadence: mean readings/day {report['cadence']['mean_per_day_2022']} (2022) -> {report['cadence']['mean_per_day_2023']} (2023); change-point months: {', '.join(report['cadence']['change_point_months_ratio_gt1.5_or_lt0.67'][:4]) or 'none'}")
cd = report["ceiling_drift"]
b.append(f"Ceiling drift: global p99 {cd['era_global_p99']['E1']} (E1) -> {cd['era_global_p99']['E2']} (E2) -> {cd['era_global_p99']['E3']} (E3); E1->E2 {cd['E1_to_E2']['bins_ceiling_down_gt20']} bins fell >20, {cd['E1_to_E2']['bins_ceiling_up_gt20']} rose >20")
b.append(f"{report['silent_gaps_gt7d']['count']:,} silent gaps >7d on {report['silent_gaps_gt7d']['bins_affected']} bins (~{int(report['silent_gaps_gt7d']['total_silent_days']):,} bin-days silent)")
b.append(f"{report['post_drop_inconsistent']['rise_ge20_within_6h_after_drop']:,} of {report['post_drop_inconsistent']['big_drops_ge30']:,} big drops (>=30) rebound >=20 within 6h ({report['post_drop_inconsistent']['share_pct']}%) - suspect false emptyings")
b.append(f"{report['near_zero_bins']['count']} bins are >=95% zero across >=100 valid readings (dead or unused sensors)")
report["bullets"] = b[:12]

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)
print("WROTE", OUT)
for x in report["bullets"]:
    print("-", x)
