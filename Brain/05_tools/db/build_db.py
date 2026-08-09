#!/usr/bin/env python3
"""Load DATA/ into the exact numeric layer: DuckDB + Parquet + GeoPackage.

Usage:
    python Brain/05_tools/db/build_db.py

Loads RAW. No cleaning, no type coercion beyond what is unambiguous, no
row filtering. Cleaning happens later, in a documented step, once the
column semantics are confirmed by interview.
"""

import io
import sys
from pathlib import Path

import duckdb

PROJ = Path(__file__).resolve().parents[3]
DATA = PROJ / "DATA"
DB = PROJ / "Brain" / "03_db" / "duckdb" / "rio.duckdb"
PARQ = PROJ / "Brain" / "03_db" / "parquet"
GEO = PROJ / "Brain" / "03_db" / "geo"
SCHEMA = PROJ / "Brain" / "03_db" / "schemas"

CSVS = {
    "raw_collections": "Enchimentos_com_Recolhas[RioMaior].csv",
    "raw_sensors": "Enchimentos_de_Sensores[RioMaior].csv",
}


def load_csvs(con):
    for table, fname in CSVS.items():
        src = (DATA / "XLS" / fname).as_posix()
        print(f"  loading {table} <- {fname}")
        con.execute(f"""
            CREATE OR REPLACE TABLE {table} AS
            SELECT * FROM read_csv(
                '{src}',
                delim=';', header=true, sample_size=-1,
                all_varchar=true, ignore_errors=false
            )
        """)
        n = con.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
        print(f"      {n:,} rows")
        out = (PARQ / f"{table}.parquet").as_posix()
        con.execute(f"COPY {table} TO '{out}' (FORMAT PARQUET, COMPRESSION ZSTD)")
        print(f"      -> {Path(out).name}")


def load_geo(con):
    import geopandas as gpd
    import pyogrio

    gdb = (DATA / "GEO DATA" / "gis rio.gdb").as_posix()
    gpkg = GEO / "rio_maior.gpkg"
    if gpkg.exists():
        gpkg.unlink()

    for name, _ in pyogrio.list_layers(gdb):
        gdf = gpd.read_file(gdb, layer=name, engine="pyogrio")
        src_crs = gdf.crs
        # harmonise to ETRS89 / PT-TM06, the Portuguese national grid
        if gdf.crs is not None and gdf.crs.to_epsg() != 3763:
            gdf = gdf.to_crs(3763)
        gdf.to_file(gpkg, layer=name, driver="GPKG")
        print(f"  geo  {name:38s} {len(gdf):>7,}  {src_crs.to_string() if src_crs else '?'} -> EPSG:3763")

        # attributes into DuckDB for joining with the CSVs
        att = gdf.drop(columns=[gdf.geometry.name]).copy()
        att.columns = [str(c) for c in att.columns]
        tbl = "geo_" + name.lower().replace("-", "_")[:50]
        con.register("tmp_att", att)
        con.execute(f"CREATE OR REPLACE TABLE {tbl} AS SELECT * FROM tmp_att")
        con.unregister("tmp_att")
        att.to_parquet(PARQ / f"{tbl}.parquet", index=False)


def dump_schema(con):
    lines = ["---", "name: db-schema", "type: schema", "---", "",
             "# DuckDB schema — `Brain/03_db/duckdb/rio.duckdb`", "",
             "All columns are loaded as VARCHAR. Typing is deferred until the",
             "column semantics are confirmed. See",
             "`Brain/02_notes/data_quality/csv-first-pass-profile.md`.", ""]
    tables = [r[0] for r in con.execute(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema='main' ORDER BY table_name").fetchall()]
    for t in tables:
        n = con.execute(f'SELECT count(*) FROM "{t}"').fetchone()[0]
        cols = con.execute(
            "SELECT column_name, data_type FROM information_schema.columns "
            f"WHERE table_name='{t}' ORDER BY ordinal_position").fetchall()
        lines += [f"## `{t}` — {n:,} rows", "", "| # | Column | Type |",
                  "|---|---|---|"]
        for i, (c, d) in enumerate(cols, 1):
            lines.append(f"| {i} | `{c}` | {d} |")
        lines.append("")
    (SCHEMA / "schema.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"\n  schema -> {(SCHEMA/'schema.md').relative_to(PROJ)}")


def main():
    for d in (DB.parent, PARQ, GEO, SCHEMA):
        d.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB))
    con.execute("INSTALL spatial; LOAD spatial;")
    load_csvs(con)
    load_geo(con)
    dump_schema(con)
    con.close()
    print(f"\n  database -> {DB.relative_to(PROJ)}")


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
