"""W2 - Verification analyses answering Codex review comments on R2-01.
Outputs: W2/02_data_work/codex_verification.json
"""
import duckdb, json

BASE = r"C:/Users/esmae/Desktop/phd Esmaeil/THESIS CLAUDE"
con = duckdb.connect()

norm = """
    trim(idcontentor) AS cid,
    trim(description) AS fraction,
    trim("Tipo de contentor") AS ctype,
    TRY_CAST(REPLACE(Latitude, ',', '.') AS DOUBLE) AS lat,
    TRY_CAST(REPLACE(Longitude, ',', '.') AS DOUBLE) AS lon,
    TRY_CAST("Enchimento" AS INT) AS fill,
    trim(idrecolha) AS idrecolha,
    trim(Rota) AS rota,
    TRY_CAST("Data de \u00ednicio" AS TIMESTAMP) AS t_start,
    TRY_CAST("Data de fim" AS TIMESTAMP) AS t_end,
    TRY_CAST("Km totais" AS DOUBLE) AS km,
    TRY_CAST("Peso total" AS DOUBLE) AS peso,
    TRY_CAST("Data da leitura" AS TIMESTAMP) AS ts
"""
con.sql(f"CREATE VIEW c AS SELECT {norm} FROM '{BASE}/Brain/03_db/parquet/raw_collections.parquet'")
con.sql(f"CREATE VIEW s AS SELECT {norm} FROM '{BASE}/Brain/03_db/parquet/raw_sensors.parquet'")

R = {}
def q(sql): return con.sql(sql).df()

# ---- #8/#11/#28: cadence formulas + active windows ----
total_s = con.sql("SELECT COUNT(*) FROM s").fetchone()[0]
span_days = con.sql("SELECT date_diff('day', MIN(ts), MAX(ts)) + 1 FROM s").fetchone()[0]
R["cadence"] = {
    "total_rows": total_s,
    "n_containers": 344,
    "full_window_days": span_days,
    "naive_calendar_rate": round(total_s / (344 * span_days), 3),
    "active_day_conditional_rate": float(q("SELECT round(avg(n),3) r FROM (SELECT cid, CAST(ts AS DATE) d, COUNT(*) n FROM s GROUP BY 1,2)").r[0]),
}
# per-container active windows
aw = q("""
  SELECT cid, MIN(ts) w_start, MAX(ts) w_end,
         date_diff('day', MIN(ts), MAX(ts)) + 1 AS active_days,
         COUNT(*) n_rows,
         COUNT(DISTINCT CAST(ts AS DATE)) days_with_readings
  FROM s GROUP BY cid
""")
aw["rate_active_window"] = aw.n_rows / aw.active_days
aw["coverage"] = aw.days_with_readings / aw.active_days
R["active_windows"] = {
    "active_days_min": int(aw.active_days.min()), "active_days_median": float(aw.active_days.median()),
    "active_days_max": int(aw.active_days.max()),
    "rate_within_window_median": round(float(aw.rate_active_window.median()), 3),
    "rate_within_window_mean": round(float(aw.rate_active_window.mean()), 3),
    "coverage_median": round(float(aw.coverage.median()), 3),
    "containers_window_lt_1yr": int((aw.active_days < 365).sum()),
    "containers_window_lt_full_75pct": int((aw.active_days < 0.75 * span_days).sum()),
}
aw[["cid","w_start","w_end","active_days","n_rows","days_with_readings"]].to_csv(f"{BASE}/W2/02_data_work/sensor_active_windows.csv", index=False)

# ---- #9: driver zeros = post-emptying confirmations? ----
R["zeros"] = {
    "driver_rows_with_idrecolha": con.sql("SELECT COUNT(*) FROM c WHERE idrecolha IS NOT NULL AND idrecolha <> '' AND idrecolha <> '0'").fetchone()[0],
    "idrecolha_rows_fill_zero": con.sql("SELECT COUNT(*) FROM c WHERE idrecolha IS NOT NULL AND idrecolha <> '' AND idrecolha <> '0' AND fill = 0").fetchone()[0],
}
con.sql("""
  CREATE VIEW c_pairs AS
  SELECT *, lag(ts) OVER w AS prev_ts, lag(fill) OVER w AS prev_fill,
         date_diff('minute', lag(ts) OVER w, ts) AS gap_min
  FROM c WINDOW w AS (PARTITION BY cid ORDER BY ts)
""")
zero = q("""
  SELECT COUNT(*) n_zero,
    SUM(CASE WHEN gap_min IS NOT NULL AND gap_min <= 15 THEN 1 ELSE 0 END) paired_15min,
    SUM(CASE WHEN gap_min IS NOT NULL AND gap_min <= 15 AND prev_fill > 0 THEN 1 ELSE 0 END) paired_prev_nonzero
  FROM c_pairs WHERE fill = 0
""")
R["zeros"].update({
    "total_zero_rows": int(zero.n_zero[0]),
    "zeros_with_reading_within_15min_before": int(zero.paired_15min[0]),
    "of_which_previous_nonzero": int(zero.paired_prev_nonzero[0]),
    "standalone_zeros": int(zero.n_zero[0] - zero.paired_15min[0]),
})

# ---- #12: timestamps vs Rota ----
R["timestamps_vs_rota"] = {
    "rows_with_t_start": con.sql("SELECT COUNT(*) FROM c WHERE t_start IS NOT NULL").fetchone()[0],
    "rows_with_rota": con.sql("SELECT COUNT(*) FROM c WHERE rota <> ''").fetchone()[0],
    "t_start_without_rota": con.sql("SELECT COUNT(*) FROM c WHERE t_start IS NOT NULL AND (rota = '' OR rota IS NULL)").fetchone()[0],
    "start_hour_hist": q("SELECT hour(t_start) h, COUNT(*) n FROM c WHERE t_start IS NOT NULL GROUP BY 1 ORDER BY 1").to_dict("records"),
    "weekday_hist": q("SELECT dayofweek(t_start) dow, COUNT(*) n FROM c WHERE t_start IS NOT NULL GROUP BY 1 ORDER BY 1").to_dict("records"),
    "run_duration_min": q("SELECT round(quantile_cont(date_diff('minute', t_start, t_end), [0.1,0.5,0.9])[i+1],0) v, ['p10','p50','p90'][i+1] p FROM (SELECT DISTINCT idrecolha, t_start, t_end FROM c WHERE t_start IS NOT NULL AND t_end IS NOT NULL), generate_series(0,2) t(i) GROUP BY i").to_dict("records"),
}

# ---- #13: per-idrecolha run distributions ----
runs = q("""
  SELECT idrecolha, ANY_VALUE(rota) rota, MAX(km) km, MAX(peso) peso,
         COUNT(DISTINCT cid) n_containers,
         MIN(t_start) t0, MAX(t_end) t1
  FROM c WHERE idrecolha IS NOT NULL AND idrecolha <> '' AND idrecolha <> '0'
  GROUP BY idrecolha
""")
R["runs"] = {
    "n_runs": len(runs),
    "km_consistent_within_run": bool(con.sql("SELECT COUNT(*) = 0 FROM (SELECT idrecolha FROM c WHERE idrecolha <> '' AND idrecolha <> '0' AND km > 0 GROUP BY idrecolha HAVING COUNT(DISTINCT km) > 1)").fetchone()[0]),
    "peso_consistent_within_run": bool(con.sql("SELECT COUNT(*) = 0 FROM (SELECT idrecolha FROM c WHERE idrecolha <> '' AND idrecolha <> '0' AND peso > 0 GROUP BY idrecolha HAVING COUNT(DISTINCT peso) > 1)").fetchone()[0]),
    "containers_per_run_p10_50_90": [float(runs.n_containers.quantile(x)) for x in (0.1, 0.5, 0.9)],
    "km_p10_50_90": [float(runs.km.quantile(x)) for x in (0.1, 0.5, 0.9)],
    "peso_p10_50_90": [float(runs.peso.quantile(x)) for x in (0.1, 0.5, 0.9)],
}
runs.to_csv(f"{BASE}/W2/02_data_work/collection_runs.csv", index=False)

# ---- #14: effective windows ----
R["effective_windows"] = {
    "driver": str(con.sql("SELECT MIN(ts) || ' to ' || MAX(ts) FROM c").fetchone()[0]),
    "sensor": str(con.sql("SELECT MIN(ts) || ' to ' || MAX(ts) FROM s").fetchone()[0]),
    "sensor_neg_share_by_year": q("SELECT year(ts) y, round(SUM(CASE WHEN fill<0 THEN 1 ELSE 0 END)*100.0/COUNT(*),1) neg_pct FROM s GROUP BY 1 ORDER BY 1").to_dict("records"),
    "note_2024": "Jan-Apr only in both sources",
}

# ---- #20: cluster instrumentation policy + row ordering ----
con.sql("""
  CREATE VIEW sites AS
  SELECT round(lat, 5) rlat, round(lon, 5) rlon, cid, ANY_VALUE(fraction) fraction
  FROM c GROUP BY 1, 2, cid
""")
con.sql("CREATE VIEW s_cids AS SELECT DISTINCT cid FROM s")
clusters = q("""
  SELECT rlat, rlon, COUNT(DISTINCT cid) n_units,
         SUM(CASE WHEN cid IN (SELECT cid FROM s_cids) THEN 1 ELSE 0 END) n_instrumented,
         STRING_AGG(DISTINCT CASE WHEN cid IN (SELECT cid FROM s_cids) THEN fraction END, '|') instr_fractions
  FROM sites GROUP BY 1, 2
""")
R["clusters"] = {
    "n_sites": len(clusters),
    "sites_by_units": clusters.groupby("n_units").size().to_dict(),
    "multiunit_sites": int((clusters.n_units >= 2).sum()),
    "multiunit_with_exactly_one_instrumented": int(((clusters.n_units >= 2) & (clusters.n_instrumented == 1)).sum()),
    "multiunit_with_zero_instrumented": int(((clusters.n_units >= 2) & (clusters.n_instrumented == 0)).sum()),
    "multiunit_with_2plus_instrumented": int(((clusters.n_units >= 2) & (clusters.n_instrumented >= 2)).sum()),
    "instrumented_fraction_counts": q("SELECT fraction, COUNT(*) n FROM sites WHERE cid IN (SELECT cid FROM s_cids) GROUP BY 1").to_dict("records"),
}
# row ordering: are sensor-file containers a prefix of some ordering?
first_seen = q(f"""
  SELECT cid, MIN(rowid) first_row FROM (SELECT trim(idcontentor) cid, row_number() OVER () rowid
  FROM '{BASE}/Brain/03_db/parquet/raw_sensors.parquet') GROUP BY cid ORDER BY first_row
""")
R["row_ordering"] = {
    "distinct_cids_in_file_order_sample_first10": first_seen.cid.head(10).tolist(),
    "last_container_rows": int(con.sql("SELECT COUNT(*) FROM s WHERE cid = (SELECT cid FROM (SELECT cid, MIN(rowid) fr FROM (SELECT trim(idcontentor) cid, row_number() OVER () rowid FROM '" + BASE + "/Brain/03_db/parquet/raw_sensors.parquet') GROUP BY cid) ORDER BY fr DESC LIMIT 1)").fetchone()[0]),
}

# ---- #22: route-fraction purity ----
purity = q("SELECT rota, COUNT(DISTINCT fraction) nf, STRING_AGG(DISTINCT fraction, ' | ') fr, COUNT(*) n FROM c WHERE rota <> '' GROUP BY rota HAVING COUNT(DISTINCT fraction) > 1")
R["route_purity"] = {
    "routes_total": con.sql("SELECT COUNT(DISTINCT rota) FROM c WHERE rota <> ''").fetchone()[0],
    "mixed_fraction_routes": purity.to_dict("records"),
    "malformed_prefixes": q("SELECT rota, COUNT(*) n FROM c WHERE rota <> '' AND substr(rota,1,2) NOT IN ('CE','CP') GROUP BY 1").to_dict("records"),
}

with open(f"{BASE}/W2/02_data_work/codex_verification.json", "w", encoding="utf-8") as f:
    json.dump(R, f, indent=1, ensure_ascii=False, default=str)
print(json.dumps(R, indent=1, default=str)[:4500])
