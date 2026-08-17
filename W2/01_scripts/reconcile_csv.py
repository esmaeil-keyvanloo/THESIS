"""W2 - Reconciliation of driver (collections) vs sensor CSVs.
Outputs: stats JSON + per-container GeoJSON layers for QGIS.
"""
import duckdb, json, math, os

BASE = r"C:/Users/esmae/Desktop/phd Esmaeil/THESIS CLAUDE"
OUT = f"{BASE}/W2/02_data_work"
os.makedirs(OUT, exist_ok=True)
con = duckdb.connect()
con.sql("INSTALL spatial; LOAD spatial;")

COLS = f"'{BASE}/Brain/03_db/parquet/raw_collections.parquet'"
SENS = f"'{BASE}/Brain/03_db/parquet/raw_sensors.parquet'"

def q(sql):
    return con.sql(sql).df()

norm = """
    trim(idcontentor) AS cid,
    trim("Matricula do contentor") AS plate,
    trim("Tipo de contentor") AS ctype,
    TRY_CAST("Volume do tipo de contentor" AS INT) AS vol,
    trim(description) AS fraction,
    trim(Freguesia) AS freguesia,
    trim(Localidade) AS localidade,
    TRY_CAST(REPLACE(Latitude, ',', '.') AS DOUBLE) AS lat,
    TRY_CAST(REPLACE(Longitude, ',', '.') AS DOUBLE) AS lon,
    TRY_CAST("Enchimento" AS INT) AS fill,
    trim(Rota) AS rota,
    TRY_CAST("Km totais" AS DOUBLE) AS km,
    TRY_CAST("Peso total" AS DOUBLE) AS peso,
    TRY_CAST("Data da leitura" AS TIMESTAMP) AS ts
"""
# date format check first
for name, src in [("collections", COLS), ("sensors", SENS)]:
    sample = q(f'SELECT "Data da leitura" d FROM {src} LIMIT 3')
    print(name, "date sample:", list(sample.d))

# build normalized views (try two date formats)
for name, src in [("collections", COLS), ("sensors", SENS)]:
    con.sql(f"CREATE OR REPLACE VIEW {name} AS SELECT {norm} FROM {src}")
    print(name, "null ts after parse:", con.sql(f"SELECT COUNT(*) FROM {name} WHERE ts IS NULL").fetchone()[0])

stats = {}

# --- headline ---
for name in ("collections", "sensors"):
    stats[name] = {
        "rows": con.sql(f"SELECT COUNT(*) FROM {name}").fetchone()[0],
        "containers_by_cid": con.sql(f"SELECT COUNT(DISTINCT cid) FROM {name}").fetchone()[0],
        "containers_by_plate": con.sql(f"SELECT COUNT(DISTINCT plate) FROM {name}").fetchone()[0],
        "date_min": str(con.sql(f"SELECT MIN(ts) FROM {name}").fetchone()[0]),
        "date_max": str(con.sql(f"SELECT MAX(ts) FROM {name}").fetchone()[0]),
    }

# --- ID overlap (by cid and by plate) ---
stats["overlap"] = {
    "cid_both": con.sql("SELECT COUNT(*) FROM (SELECT DISTINCT cid FROM collections INTERSECT SELECT DISTINCT cid FROM sensors)").fetchone()[0],
    "cid_driver_only": con.sql("SELECT COUNT(*) FROM (SELECT DISTINCT cid FROM collections EXCEPT SELECT DISTINCT cid FROM sensors)").fetchone()[0],
    "cid_sensor_only": con.sql("SELECT COUNT(*) FROM (SELECT DISTINCT cid FROM sensors EXCEPT SELECT DISTINCT cid FROM collections)").fetchone()[0],
    "plate_both": con.sql("SELECT COUNT(*) FROM (SELECT DISTINCT plate FROM collections INTERSECT SELECT DISTINCT plate FROM sensors)").fetchone()[0],
    "plate_driver_only": con.sql("SELECT COUNT(*) FROM (SELECT DISTINCT plate FROM collections EXCEPT SELECT DISTINCT plate FROM sensors)").fetchone()[0],
    "plate_sensor_only": con.sql("SELECT COUNT(*) FROM (SELECT DISTINCT plate FROM sensors EXCEPT SELECT DISTINCT plate FROM collections)").fetchone()[0],
}

# --- coordinate agreement for shared cids ---
con.sql("""
  CREATE OR REPLACE VIEW c_pos AS
  SELECT cid, ANY_VALUE(plate) plate, ANY_VALUE(ctype) ctype, ANY_VALUE(vol) vol,
         ANY_VALUE(fraction) fraction, ANY_VALUE(freguesia) freguesia, ANY_VALUE(localidade) localidade,
         median(lat) lat, median(lon) lon,
         COUNT(*) n_readings, MIN(ts) first_ts, MAX(ts) last_ts,
         AVG(CASE WHEN fill BETWEEN 0 AND 100 THEN fill END) mean_fill,
         SUM(CASE WHEN fill = 0 THEN 1 ELSE 0 END) * 1.0 / COUNT(*) share_zero,
         SUM(CASE WHEN fill < 0 THEN 1 ELSE 0 END) n_negative,
         COUNT(DISTINCT rota) FILTER (WHERE rota IS NOT NULL AND rota <> '') n_rotas
  FROM collections GROUP BY cid
""")
con.sql("""
  CREATE OR REPLACE VIEW s_pos AS
  SELECT cid, ANY_VALUE(plate) plate, ANY_VALUE(ctype) ctype, ANY_VALUE(vol) vol,
         ANY_VALUE(fraction) fraction, ANY_VALUE(freguesia) freguesia, ANY_VALUE(localidade) localidade,
         median(lat) lat, median(lon) lon,
         COUNT(*) n_readings, MIN(ts) first_ts, MAX(ts) last_ts,
         AVG(CASE WHEN fill BETWEEN 0 AND 100 THEN fill END) mean_fill,
         MAX(CASE WHEN fill BETWEEN 0 AND 100 THEN fill END) max_fill,
         SUM(CASE WHEN fill < 0 THEN 1 ELSE 0 END) n_negative
  FROM sensors GROUP BY cid
""")

agree = q("""
  SELECT c.cid, c.lat clat, c.lon clon, s.lat slat, s.lon slon,
         2*6371000*asin(sqrt( sin(radians(s.lat-c.lat)/2)^2 +
           cos(radians(c.lat))*cos(radians(s.lat))*sin(radians(s.lon-c.lon)/2)^2 )) dist_m,
         c.fraction cf, s.fraction sf, c.ctype cct, s.ctype sct, c.vol cv, s.vol sv
  FROM c_pos c JOIN s_pos s USING (cid)
""")
stats["coord_agreement"] = {
    "n_shared": len(agree),
    "median_dist_m": float(agree.dist_m.median()),
    "p90_dist_m": float(agree.dist_m.quantile(0.9)),
    "max_dist_m": float(agree.dist_m.max()),
    "within_10m": int((agree.dist_m <= 10).sum()),
    "within_100m": int((agree.dist_m <= 100).sum()),
    "over_500m": int((agree.dist_m > 500).sum()),
    "fraction_match": int((agree.cf == agree.sf).sum()),
    "type_match": int((agree.cct == agree.sct).sum()),
    "vol_match": int((agree.cv == agree.sv).sum()),
}

# --- study-area containment (municipality + 10km buffer, EPSG:3763) ---
con.sql(f"""
  CREATE OR REPLACE TABLE muni AS
  SELECT geom FROM ST_Read('{BASE}/GIS_DATA/00_admin_boundaries/municipio_riomaior_caop2025.geojson')
""")
con.sql(f"""
  CREATE OR REPLACE TABLE mask10 AS
  SELECT geom FROM ST_Read('{BASE}/GIS_DATA/00_admin_boundaries/clip_mask_studyarea_buffer10km.gpkg')
""")
# muni geojson is in EPSG:3763? OGC API returns CRS84 by default -> check via bounds
mb = q("SELECT ST_XMin(ST_Extent(geom)) a, ST_XMax(ST_Extent(geom)) b FROM muni")
muni_is_geo = abs(mb.a[0]) < 180
for name, view in [("collections", "c_pos"), ("sensors", "s_pos")]:
    if muni_is_geo:
        inside = con.sql(f"""
          SELECT COUNT(*) FROM {view} p, muni m
          WHERE ST_Contains(m.geom, ST_Point(p.lon, p.lat))
        """).fetchone()[0]
    else:
        inside = con.sql(f"""
          SELECT COUNT(*) FROM {view} p, muni m
          WHERE ST_Contains(m.geom, ST_Transform(ST_Point(p.lat, p.lon), 'EPSG:4326', 'EPSG:3763'))
        """).fetchone()[0]
    inside10 = con.sql(f"""
      SELECT COUNT(*) FROM {view} p, mask10 m
      WHERE ST_Contains(m.geom, ST_Transform(ST_Point(p.lat, p.lon), 'EPSG:4326', 'EPSG:3763'))
    """).fetchone()[0]
    stats[name]["inside_municipality"] = inside
    stats[name]["inside_10km_mask"] = inside10

# --- fill semantics ---
stats["fill"] = {
    "collections_values": q("SELECT fill, COUNT(*) n FROM collections GROUP BY 1 ORDER BY 1").to_dict("records"),
    "sensors_hist": q("SELECT CASE WHEN fill < 0 THEN 'neg' ELSE CAST(fill//10*10 AS VARCHAR) END bucket, COUNT(*) n FROM sensors GROUP BY 1 ORDER BY 1").to_dict("records"),
    "sensors_per_container_max": q("SELECT max_fill, COUNT(*) n FROM s_pos GROUP BY 1 ORDER BY 1").to_dict("records"),
}

# --- fraction composition ---
stats["fractions"] = q("""
  SELECT COALESCE(c.fraction, s.fraction) fraction,
         COUNT(c.cid) FILTER (WHERE c.cid IS NOT NULL) n_driver,
         COUNT(s.cid) FILTER (WHERE s.cid IS NOT NULL) n_sensor
  FROM c_pos c FULL JOIN s_pos s USING (cid) GROUP BY 1 ORDER BY 2 DESC
""").to_dict("records")

# --- freguesia composition ---
stats["freguesias"] = q("""
  SELECT COALESCE(c.freguesia, s.freguesia) freguesia,
         COUNT(c.cid) FILTER (WHERE c.cid IS NOT NULL) n_driver,
         COUNT(s.cid) FILTER (WHERE s.cid IS NOT NULL) n_sensor
  FROM c_pos c FULL JOIN s_pos s USING (cid) GROUP BY 1 ORDER BY 2 DESC
""").to_dict("records")

# --- rota / collection-event evidence ---
stats["routes"] = {
    "rows_with_rota": con.sql("SELECT COUNT(*) FROM collections WHERE rota IS NOT NULL AND rota <> ''").fetchone()[0],
    "distinct_rota": con.sql("SELECT COUNT(DISTINCT rota) FROM collections WHERE rota IS NOT NULL AND rota <> ''").fetchone()[0],
    "rows_with_peso": con.sql("SELECT COUNT(*) FROM collections WHERE peso IS NOT NULL AND peso > 0").fetchone()[0],
    "top_rotas": q("SELECT rota, COUNT(*) n, COUNT(DISTINCT cid) n_containers FROM collections WHERE rota IS NOT NULL AND rota <> '' GROUP BY 1 ORDER BY 2 DESC LIMIT 10").to_dict("records"),
}

# --- gdb 464 cross-check ---
con.sql(f"""
  CREATE OR REPLACE TABLE bins464 AS
  SELECT idcontentor cid464, Latitude lat, Longitude lon
  FROM ST_Read('{BASE}/Brain/03_db/parquet/geo_driver_464_unique_bins_for_gis_tm06.parquet')
""") if False else None
stats["gdb464"] = {
    "in_collections": con.sql(f"""
        SELECT COUNT(*) FROM (
          SELECT DISTINCT idcontentor FROM read_parquet('{BASE}/Brain/03_db/parquet/geo_driver_464_unique_bins_for_gis_tm06.parquet')
        ) g JOIN (SELECT DISTINCT cid FROM collections) c ON CAST(g.idcontentor AS VARCHAR) = c.cid
    """).fetchone()[0],
    "in_sensors": con.sql(f"""
        SELECT COUNT(*) FROM (
          SELECT DISTINCT idcontentor FROM read_parquet('{BASE}/Brain/03_db/parquet/geo_driver_464_unique_bins_for_gis_tm06.parquet')
        ) g JOIN (SELECT DISTINCT cid FROM sensors) s ON CAST(g.idcontentor AS VARCHAR) = s.cid
    """).fetchone()[0],
}

# --- temporal: readings per month per source ---
stats["monthly"] = q("""
  SELECT strftime(ts, '%Y-%m') ym,
    SUM(CASE WHEN src='d' THEN 1 ELSE 0 END) driver_rows,
    SUM(CASE WHEN src='s' THEN 1 ELSE 0 END) sensor_rows
  FROM (SELECT ts, 'd' src FROM collections UNION ALL SELECT ts, 's' src FROM sensors)
  WHERE ts IS NOT NULL GROUP BY 1 ORDER BY 1
""").to_dict("records")

# --- export container layers ---
con.sql(f"""
  COPY (
    SELECT COALESCE(c.cid, s.cid) cid,
      COALESCE(c.plate, s.plate) plate, COALESCE(c.ctype, s.ctype) ctype,
      COALESCE(c.vol, s.vol) vol, COALESCE(c.fraction, s.fraction) fraction,
      COALESCE(c.freguesia, s.freguesia) freguesia,
      CASE WHEN c.cid IS NOT NULL AND s.cid IS NOT NULL THEN 'both'
           WHEN c.cid IS NOT NULL THEN 'driver_only' ELSE 'sensor_only' END AS src_class,
      c.n_readings n_driver_rows, s.n_readings n_sensor_rows,
      c.mean_fill driver_mean_fill, c.share_zero driver_share_zero,
      s.mean_fill sensor_mean_fill, s.max_fill sensor_max_fill,
      c.n_rotas, ST_Point(COALESCE(c.lon, s.lon), COALESCE(c.lat, s.lat)) geom
    FROM c_pos c FULL JOIN s_pos s USING (cid)
    WHERE COALESCE(c.lon, s.lon) IS NOT NULL
  ) TO '{OUT}/containers_reconciled.geojson' WITH (FORMAT GDAL, DRIVER 'GeoJSON')
""")
print("layer written:", f"{OUT}/containers_reconciled.geojson")

with open(f"{OUT}/reconcile_stats.json", "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=1, ensure_ascii=False, default=str)
print(json.dumps({k: v for k, v in stats.items() if k in ('collections','sensors','overlap','coord_agreement','gdb464','routes')}, indent=1, default=str))
