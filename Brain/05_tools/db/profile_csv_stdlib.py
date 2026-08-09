#!/usr/bin/env python3
"""First-pass profile of the two Rio Maior sensor CSVs. Stdlib only.

Usage:
    python Brain/05_tools/db/profile_csv_stdlib.py

Purpose: surface the facts needed to ask the right interview questions.
This is NOT the authoritative profile — that comes from DuckDB later.
"""

import csv
import io
import sys
from collections import Counter, defaultdict
from pathlib import Path

PROJ = Path(__file__).resolve().parents[2].parent
XLS = PROJ / "DATA" / "XLS"
FILES = ["Enchimentos_com_Recolhas[RioMaior].csv",
         "Enchimentos_de_Sensores[RioMaior].csv"]

csv.field_size_limit(10_000_000)


def profile(path):
    print("=" * 78)
    print(path.name)
    print("=" * 78)

    with open(path, encoding="utf-8-sig", errors="replace", newline="") as fh:
        rd = csv.reader(fh, delimiter=";")
        header = next(rd)
        n = len(header)
        rows = 0
        nonempty = Counter()
        types = Counter()
        descs = Counter()
        vols = Counter()
        freg = Counter()
        containers = set()
        routes = set()
        recolhas = set()
        fill = Counter()
        fill_num = []
        dmin = dmax = None
        eq_idrec_ench = 0
        idrec_present = 0
        lat_lon_bad = 0
        per_container_dates = defaultdict(lambda: [None, None])
        malformed = 0

        i = {k: idx for idx, k in enumerate(header)}
        C = lambda r, k: r[i[k]].strip() if i[k] < len(r) else ""

        for r in rd:
            rows += 1
            if len(r) != n:
                malformed += 1
                continue
            for idx, v in enumerate(r):
                if v.strip():
                    nonempty[header[idx]] += 1

            cid = C(r, "idcontentor")
            containers.add((cid, C(r, "Matricula do contentor")))
            types[C(r, "Tipo de contentor")] += 1
            descs[C(r, "description")] += 1
            vols[C(r, "Volume do tipo de contentor")] += 1
            freg[C(r, "Freguesia")] += 1

            d = C(r, "Data da leitura")
            if d:
                dmin = d if dmin is None or d < dmin else dmin
                dmax = d if dmax is None or d > dmax else dmax
                pc = per_container_dates[cid]
                pc[0] = d if pc[0] is None or d < pc[0] else pc[0]
                pc[1] = d if pc[1] is None or d > pc[1] else pc[1]

            e = C(r, "Enchimento")
            fill[e] += 1
            if e.replace(".", "", 1).isdigit():
                fill_num.append(float(e))

            ir = C(r, "idrecolha")
            if ir:
                idrec_present += 1
                recolhas.add(ir)
                if ir == e:
                    eq_idrec_ench += 1

            ro = C(r, "Rota")
            if ro:
                routes.add(ro)

            try:
                la, lo = float(C(r, "Latitude")), float(C(r, "Longitude"))
                if not (38.9 < la < 39.7 and -9.4 < lo < -8.4):
                    lat_lon_bad += 1
            except ValueError:
                lat_lon_bad += 1

    print(f"\nrows (excl. header) : {rows:,}   malformed: {malformed:,}")
    print(f"distinct containers : {len(containers):,}")
    print(f"reading date range  : {dmin}  ->  {dmax}")
    print(f"distinct idrecolha  : {len(recolhas):,}")
    print(f"distinct Rota       : {len(routes):,}  {sorted(routes)[:8]}")
    print(f"coords out of Rio Maior box : {lat_lon_bad:,}")

    print("\n-- column fill rate --")
    for h in header:
        c = nonempty[h]
        print(f"   {h:32s} {c:>10,}  {c/max(rows,1)*100:6.2f}%")

    print("\n-- Tipo de contentor --")
    for k, v in types.most_common():
        print(f"   {k or '(blank)':20s} {v:>10,}")
    print("\n-- description (waste fraction) --")
    for k, v in descs.most_common():
        print(f"   {k or '(blank)':40s} {v:>10,}")
    print("\n-- Volume --")
    for k, v in vols.most_common(10):
        print(f"   {k or '(blank)':20s} {v:>10,}")
    print("\n-- Freguesia --")
    for k, v in freg.most_common(15):
        print(f"   {k or '(blank)':30s} {v:>10,}")

    print("\n-- Enchimento --")
    vals = sorted(fill, key=lambda x: fill[x], reverse=True)[:12]
    for k in vals:
        print(f"   {k or '(blank)':>10s} {fill[k]:>10,}")
    if fill_num:
        fill_num.sort()
        q = lambda p: fill_num[int(len(fill_num) * p)]
        print(f"   min {fill_num[0]:.0f} | p25 {q(.25):.0f} | median {q(.5):.0f} "
              f"| p75 {q(.75):.0f} | p95 {q(.95):.0f} | max {fill_num[-1]:.0f}")
        print(f"   distinct values: {len(set(fill_num))}")
        print(f"   values > 100  : {sum(1 for x in fill_num if x > 100):,}")

    if idrec_present:
        print(f"\n-- idrecolha --")
        print(f"   populated          : {idrec_present:,}")
        print(f"   equal to Enchimento: {eq_idrec_ench:,} "
              f"({eq_idrec_ench/idrec_present*100:.1f}%)")

    act = [c for c, (a, b) in per_container_dates.items() if a]
    print(f"\ncontainers with >=1 dated reading: {len(act):,}")


def main():
    for f in FILES:
        p = XLS / f
        if p.exists():
            profile(p)
            print()
        else:
            print(f"MISSING: {p}")


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
