"""W2 - Event-level driver-sensor matching (review items 1-7).
Outputs: event_level_dataset.parquet (+csv sample), match_stats.json
"""
import duckdb, json

BASE = r"C:/Users/esmae/Desktop/phd Esmaeil/THESIS CLAUDE"
OUT = f"{BASE}/W2/02_data_work"
con = duckdb.connect()

norm = """
    trim(idcontentor) AS cid, trim(description) AS fraction,
    trim("Tipo de contentor") AS ctype,
    TRY_CAST("Enchimento" AS INT) AS fill, trim(idrecolha) AS idr,
    TRY_CAST("Data da leitura" AS TIMESTAMP) AS ts
"""
con.sql(f"CREATE VIEW dv AS SELECT {norm} FROM '{BASE}/Brain/03_db/parquet/raw_collections.parquet'")
con.sql(f"CREATE VIEW sv AS SELECT {norm} FROM '{BASE}/Brain/03_db/parquet/raw_sensors.parquet'")

# driver rows on instrumented containers only
con.sql("""
  CREATE TABLE d AS
  SELECT row_number() OVER () AS did, cid, fraction, ctype, fill AS d_fill, idr, ts AS d_ts,
         (idr IS NOT NULL AND idr <> '' AND idr <> '0') AS is_event_row
  FROM dv WHERE cid IN (SELECT DISTINCT cid FROM sv)
""")
con.sql("CREATE TABLE s AS SELECT cid, fill AS s_fill, ts AS s_ts FROM sv")
con.sql("CREATE TABLE smax AS SELECT cid, MAX(CASE WHEN fill BETWEEN 0 AND 100 THEN fill END) s_max FROM sv GROUP BY cid")

R = {"driver_rows_on_instrumented": con.sql("SELECT COUNT(*) FROM d").fetchone()[0]}

# nearest VALID sensor reading (0..100) before and after each driver row
con.sql("""
  CREATE TABLE m_prev AS
  SELECT d.did, s.s_fill s_prev, s.s_ts ts_prev
  FROM d ASOF JOIN (SELECT * FROM s WHERE s_fill BETWEEN 0 AND 100) s
    ON d.cid = s.cid AND d.d_ts >= s.s_ts
""")
con.sql("""
  CREATE TABLE m_next AS
  SELECT d.did, s.s_fill s_next, s.s_ts ts_next
  FROM (SELECT did, cid, CAST('2100-01-01' AS TIMESTAMP) - d_ts AS rts FROM d) d
  ASOF JOIN (SELECT cid, s_fill, CAST('2100-01-01' AS TIMESTAMP) - s_ts AS rts, s_ts
             FROM s WHERE s_fill BETWEEN 0 AND 100) s
    ON d.cid = s.cid AND d.rts >= s.rts
""")
# nearest NEGATIVE sensor reading too (for the -1 and QC work)
con.sql("""
  CREATE TABLE pairs AS
  SELECT d.*, p.s_prev, p.ts_prev, n.s_next, n.ts_next,
    date_diff('minute', p.ts_prev, d.d_ts) AS gap_prev_min,
    date_diff('minute', d.d_ts, n.ts_next) AS gap_next_min,
    CASE WHEN gap_next_min IS NULL OR (gap_prev_min IS NOT NULL AND gap_prev_min <= gap_next_min)
         THEN p.s_prev ELSE n.s_next END AS s_val,
    CASE WHEN gap_next_min IS NULL OR (gap_prev_min IS NOT NULL AND gap_prev_min <= gap_next_min)
         THEN p.ts_prev ELSE n.ts_next END AS s_ts,
    LEAST(COALESCE(gap_prev_min, 999999), COALESCE(gap_next_min, 999999)) AS gap_min
  FROM d LEFT JOIN m_prev p USING (did) LEFT JOIN m_next n USING (did)
""")
con.sql("CREATE TABLE pairs2 AS SELECT p.*, x.s_max FROM pairs p JOIN smax x USING (cid)")

# gap distribution
R["gap_distribution_min"] = con.sql("""
  SELECT ['p10','p25','p50','p75','p90','p95'][i+1] q,
         round(quantile_cont(gap_min, [0.1,0.25,0.5,0.75,0.9,0.95])[i+1], 0) v
  FROM pairs2, generate_series(0,5) t(i) WHERE gap_min < 999999 GROUP BY i ORDER BY i
""").df().to_dict("records")

# sensitivity across matching windows
windows = [15, 30, 60, 180, 360, 720, 1440]
sens = []
for w in windows:
    row = con.sql(f"""
      SELECT COUNT(*) AS n_matched,
        round(100.0*COUNT(*)/(SELECT COUNT(*) FROM pairs2),1) pct_matched,
        SUM(CASE WHEN d_fill BETWEEN 0 AND 100 AND abs(d_fill - s_val*100.0/s_max) <= 25 THEN 1 ELSE 0 END) acceptable,
        round(avg(CASE WHEN d_fill BETWEEN 0 AND 100 THEN abs(d_fill - s_val*100.0/s_max) END),1) mean_absdiff_norm
      FROM pairs2 WHERE gap_min <= {w}
    """).df().iloc[0]
    sens.append({"window_min": w, "matched": int(row.n_matched), "pct_of_driver_rows": float(row.pct_matched),
                 "acceptable_pct_of_matched": round(100*row.acceptable/row.n_matched, 1) if row.n_matched else None,
                 "mean_absdiff_norm": float(row.mean_absdiff_norm)})
R["window_sensitivity"] = sens

W = 180  # chosen primary window (justified in report: p90 of gaps, agreement stable 60-360)
con.sql(f"""
  CREATE TABLE ev AS
  SELECT *, (gap_min <= {W}) AS is_matched,
    CASE WHEN s_max > 0 THEN s_val*100.0/s_max END AS s_norm,
    CASE WHEN d_fill BETWEEN 0 AND 100 AND gap_min <= {W} THEN abs(d_fill - s_val*100.0/s_max) END AS absdiff
  FROM pairs2
""")
matched = con.sql("SELECT COUNT(*) FROM ev WHERE is_matched").fetchone()[0]
R["primary_window_min"] = W
R["matched_pairs"] = matched

# 1: ceiling cases
ceil_ = con.sql("SELECT COUNT(*) FROM ev WHERE is_matched AND d_fill = 100 AND s_val BETWEEN 82 AND 84").fetchone()[0]
d100 = con.sql("SELECT COUNT(*) FROM ev WHERE is_matched AND d_fill = 100").fetchone()[0]
R["ceiling"] = {"matched_d100": d100, "d100_with_sensor_82_84": ceil_,
                "pct_of_d100": round(100*ceil_/d100, 1) if d100 else 0,
                "d100_with_sensor_ge_75norm": con.sql("SELECT COUNT(*) FROM ev WHERE is_matched AND d_fill = 100 AND s_norm >= 75").fetchone()[0]}

# 2: driver -1 rows
neg1 = con.sql("SELECT COUNT(*) FROM ev WHERE d_fill = -1").fetchone()[0]
neg1_matched = con.sql("SELECT COUNT(*) FROM ev WHERE d_fill = -1 AND is_matched").fetchone()[0]
R["driver_minus1"] = {
    "rows_on_instrumented": neg1, "with_valid_sensor_within_window": neg1_matched,
    "pct": round(100*neg1_matched/neg1, 1) if neg1 else None,
    "sensor_value_dist_p25_50_75": con.sql("SELECT quantile_cont(s_norm,[0.25,0.5,0.75]) FROM ev WHERE d_fill=-1 AND is_matched").fetchone()[0] if neg1_matched else None,
    "share_event_rows": con.sql("SELECT round(100.0*SUM(CASE WHEN is_event_row THEN 1 ELSE 0 END)/COUNT(*),1) FROM ev WHERE d_fill=-1").fetchone()[0],
}

# 3+4: difference categories on matched, non-event, valid driver readings
cats = con.sql("""
  SELECT
    SUM(CASE WHEN absdiff <= 12.5 THEN 1 ELSE 0 END) small,
    SUM(CASE WHEN absdiff > 12.5 AND absdiff <= 25 THEN 1 ELSE 0 END) moderate,
    SUM(CASE WHEN absdiff > 25 THEN 1 ELSE 0 END) AS n_large,
    COUNT(*) total
  FROM ev WHERE is_matched AND NOT is_event_row AND d_fill BETWEEN 0 AND 100
""").df().iloc[0]
R["diff_categories"] = {
    "compared_pairs": int(cats.total),
    "small_le_half_step": int(cats.small), "small_pct": round(100*cats.small/cats.total, 1),
    "moderate_le_one_step": int(cats.moderate), "moderate_pct": round(100*cats.moderate/cats.total, 1),
    "large_gt_one_step": int(cats.n_large), "large_pct": round(100*cats.n_large/cats.total, 1),
    "acceptable_le_25": int(cats.small + cats.moderate),
    "acceptable_pct": round(100*(cats.small + cats.moderate)/cats.total, 1),
}
R["diff_by_driver_value"] = con.sql("""
  SELECT d_fill, COUNT(*) n, round(avg(absdiff),1) mean_absdiff,
         round(100.0*SUM(CASE WHEN absdiff<=25 THEN 1 ELSE 0 END)/COUNT(*),1) acceptable_pct
  FROM ev WHERE is_matched AND NOT is_event_row AND d_fill BETWEEN 0 AND 100
  GROUP BY 1 ORDER BY 1
""").df().to_dict("records")

# 5: integrated dataset with QC flags
con.sql(f"""
  CREATE TABLE final AS
  SELECT cid, fraction, ctype, d_ts, d_fill, is_event_row, idr,
         s_val AS s_fill_raw, s_ts, gap_min, s_max, round(s_norm,1) s_fill_norm,
         round(absdiff,1) absdiff_norm,
    CASE
      WHEN is_event_row THEN 'EVENT_ZERO_POST_EMPTYING'
      WHEN d_fill = -1 AND is_matched THEN 'DRIVER_MISSING_SENSOR_AVAILABLE'
      WHEN d_fill = -1 THEN 'DRIVER_MISSING_NO_MATCH'
      WHEN NOT is_matched THEN 'NO_SENSOR_MATCH'
      WHEN d_fill = 100 AND s_val BETWEEN 82 AND 84 THEN 'CEILING_CASE'
      WHEN absdiff > 25 THEN 'LARGE_DISAGREEMENT'
      WHEN absdiff > 12.5 THEN 'MODERATE_AGREEMENT'
      ELSE 'GOOD_AGREEMENT' END AS qc_flag,
    CASE
      WHEN is_event_row THEN NULL
      WHEN is_matched AND (absdiff <= 25 OR (d_fill = 100 AND s_val BETWEEN 82 AND 84)) THEN round(s_norm,1)
      WHEN NOT is_matched AND d_fill BETWEEN 0 AND 100 THEN CAST(d_fill AS DOUBLE)
      ELSE NULL END AS selected_fill,
    CASE
      WHEN is_event_row THEN 'excluded: post-emptying record'
      WHEN is_matched AND d_fill = 100 AND s_val BETWEEN 82 AND 84 THEN 'sensor (normalized): ceiling case, driver corroborates full'
      WHEN is_matched AND absdiff <= 25 THEN 'sensor (normalized): validated by driver within one scale step'
      WHEN NOT is_matched AND d_fill BETWEEN 0 AND 100 THEN 'driver: no sensor reading within tolerance'
      ELSE 'none: flagged for investigation' END AS selection_rule
  FROM ev
""")
con.sql(f"COPY final TO '{OUT}/event_level_dataset.parquet' (FORMAT PARQUET)")
con.sql(f"COPY (SELECT * FROM final LIMIT 2000) TO '{OUT}/event_level_dataset_sample.csv' (HEADER)")
R["qc_flag_counts"] = con.sql("SELECT qc_flag, COUNT(*) n FROM final GROUP BY 1 ORDER BY 2 DESC").df().to_dict("records")
R["selected_fill_available"] = con.sql("SELECT COUNT(*) FROM final WHERE selected_fill IS NOT NULL").fetchone()[0]

# 6: negatives deep-dive
R["negatives"] = {
    "total": con.sql("SELECT COUNT(*) FROM sv WHERE fill < 0").fetchone()[0],
    "by_value_top": con.sql("SELECT fill, COUNT(*) n FROM sv WHERE fill<0 GROUP BY 1 ORDER BY 2 DESC LIMIT 8").df().to_dict("records"),
    "by_cluster": con.sql("""SELECT CASE WHEN fill >= -9 THEN 'small_-1..-9' ELSE 'large_-89..-116' END c,
        COUNT(*) n, round(100.0*COUNT(*)/(SELECT COUNT(*) FROM sv WHERE fill<0),1) pct
        FROM sv WHERE fill<0 GROUP BY 1""").df().to_dict("records"),
    "by_month": con.sql("SELECT strftime(ts,'%Y-%m') ym, COUNT(*) n FROM sv WHERE fill<0 GROUP BY 1 ORDER BY 1").df().to_dict("records"),
    "container_concentration": con.sql("""
        SELECT round(100.0*SUM(n)/(SELECT COUNT(*) FROM sv WHERE fill<0),1) FROM (
          SELECT COUNT(*) n FROM sv WHERE fill<0 GROUP BY cid ORDER BY 1 DESC LIMIT 34)""").fetchone()[0],
    "containers_with_negatives": con.sql("SELECT COUNT(DISTINCT cid) FROM sv WHERE fill<0").fetchone()[0],
    "by_fraction": con.sql("SELECT fraction, round(100.0*SUM(CASE WHEN fill<0 THEN 1 ELSE 0 END)/COUNT(*),1) neg_pct FROM sv GROUP BY 1").df().to_dict("records"),
    "by_ctype": con.sql("SELECT ctype, round(100.0*SUM(CASE WHEN fill<0 THEN 1 ELSE 0 END)/COUNT(*),1) neg_pct, COUNT(*) n FROM sv GROUP BY 1 ORDER BY n DESC").df().to_dict("records"),
}
# episodes: consecutive negative runs per container
con.sql("""
  CREATE TABLE eps AS
  SELECT cid, grp, COUNT(*) len, MIN(ts) t0, MAX(ts) t1, MIN(fill) worst
  FROM (
    SELECT cid, ts, fill,
      SUM(CASE WHEN fill >= 0 THEN 1 ELSE 0 END) OVER (PARTITION BY cid ORDER BY ts) grp
    FROM sv) WHERE fill < 0
  GROUP BY cid, grp
""")
R["negatives"]["episodes"] = {
    "n_episodes": con.sql("SELECT COUNT(*) FROM eps").fetchone()[0],
    "len_p50_p90_max": con.sql("SELECT quantile_cont(len,[0.5,0.9]) , MAX(len) FROM eps").fetchone(),
    "episodes_gt_1day_pct": con.sql("SELECT round(100.0*SUM(CASE WHEN date_diff('hour',t0,t1)>24 THEN 1 ELSE 0 END)/COUNT(*),1) FROM eps").fetchone()[0],
}
# adjacent valid readings around episodes: level shift?
R["negatives"]["level_shift_after_episode"] = con.sql("""
  WITH v AS (SELECT cid, ts, fill FROM sv WHERE fill BETWEEN 0 AND 100)
  SELECT round(avg(abs(a.next_v - a.prev_v)),1) FROM (
    SELECT e.cid,
      (SELECT fill FROM v WHERE v.cid=e.cid AND v.ts < e.t0 ORDER BY v.ts DESC LIMIT 1) prev_v,
      (SELECT fill FROM v WHERE v.cid=e.cid AND v.ts > e.t1 ORDER BY v.ts ASC LIMIT 1) next_v
    FROM eps e USING SAMPLE 2000) a
  WHERE a.prev_v IS NOT NULL AND a.next_v IS NOT NULL
""").fetchone()[0]
R["negatives"]["baseline_adjacent_change"] = con.sql("""
  SELECT round(avg(abs(fill - prev_f)),1) FROM (
    SELECT fill, lag(fill) OVER (PARTITION BY cid ORDER BY ts) prev_f
    FROM sv WHERE fill BETWEEN 0 AND 100 USING SAMPLE 500000)
  WHERE prev_f IS NOT NULL
""").fetchone()[0]

with open(f"{OUT}/match_stats.json", "w", encoding="utf-8") as f:
    json.dump(R, f, indent=1, ensure_ascii=False, default=str)
print(json.dumps(R, indent=1, default=str)[:4000])
