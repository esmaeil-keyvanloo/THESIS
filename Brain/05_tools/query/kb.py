#!/usr/bin/env python3
"""Query the Brain — hybrid retrieval over the prose corpus.

Usage:
    python Brain/05_tools/query/kb.py "how is demand estimated"
    python Brain/05_tools/query/kb.py "p-median" -k 8 --full
    python Brain/05_tools/query/kb.py "jury question" --type source
    python Brain/05_tools/query/kb.py --sql "SELECT count(*) FROM raw_sensors"

Dense (bge-m3) and lexical (BM25) results are fused with reciprocal rank
fusion. Every hit reports its source file and heading so any claim can be
traced back to DATA/.

Numbers must be obtained with --sql, never from retrieved prose.
"""

import argparse
import json
import pickle
import re
import sys
import io
from pathlib import Path

PROJ = Path(__file__).resolve().parents[3]
IDX = PROJ / "Brain" / "04_index"
DB = PROJ / "Brain" / "03_db" / "duckdb" / "rio.duckdb"
K_RRF = 60


def load_chunks():
    with open(IDX / "chunks" / "chunks.jsonl", encoding="utf-8") as fh:
        return {c["id"]: c for c in map(json.loads, fh)}


def bm25_rank(query, n):
    with open(IDX / "bm25" / "bm25.pkl", "rb") as fh:
        blob = pickle.load(fh)
    scores = blob["bm25"].get_scores(re.findall(r"\w+", query.lower()))
    order = sorted(range(len(scores)), key=lambda i: -scores[i])[:n]
    return [blob["ids"][i] for i in order]


def dense_rank(query, n):
    from sentence_transformers import SentenceTransformer
    import lancedb
    model = SentenceTransformer("BAAI/bge-m3")
    v = model.encode([query], normalize_embeddings=True)[0].tolist()
    tbl = lancedb.connect(str(IDX / "lancedb")).open_table("corpus")
    return [r["id"] for r in tbl.search(v).limit(n).to_list()]


def rrf(*rankings):
    score = {}
    for r in rankings:
        for pos, cid in enumerate(r):
            score[cid] = score.get(cid, 0.0) + 1.0 / (K_RRF + pos + 1)
    return sorted(score, key=lambda c: -score[c])


def run_sql(sql):
    import duckdb
    con = duckdb.connect(str(DB), read_only=True)
    try:
        con.execute("LOAD spatial;")
    except Exception:
        pass
    cur = con.execute(sql)
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    widths = [max(len(str(c)), *(len(str(r[i])) for r in rows[:200]) if rows else len(str(c)))
              for i, c in enumerate(cols)]
    print("  " + " | ".join(str(c).ljust(w) for c, w in zip(cols, widths)))
    print("  " + "-+-".join("-" * w for w in widths))
    for r in rows[:200]:
        print("  " + " | ".join(str(x).ljust(w) for x, w in zip(r, widths)))
    if len(rows) > 200:
        print(f"  … {len(rows)-200} more rows")
    print(f"\n  {len(rows)} rows")
    con.close()


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("query", nargs="?", help="natural-language query")
    ap.add_argument("-k", type=int, default=6, help="hits to return")
    ap.add_argument("--full", action="store_true", help="print whole chunk")
    ap.add_argument("--type", help="filter: source | note | canon")
    ap.add_argument("--category", help="filter: thesis, defence, data_quality, …")
    ap.add_argument("--sql", help="run SQL against rio.duckdb instead")
    a = ap.parse_args()

    if a.sql:
        return run_sql(a.sql)
    if not a.query:
        ap.print_help()
        return

    chunks = load_chunks()
    pool = a.k * 8
    ranked = rrf(dense_rank(a.query, pool), bm25_rank(a.query, pool))

    shown = 0
    for cid in ranked:
        c = chunks.get(cid)
        if not c:
            continue
        if a.type and c["type"] != a.type:
            continue
        if a.category and c["category"] != a.category:
            continue
        shown += 1
        print(f"\n[{shown}] {c['title']}")
        print(f"    {c['file']}")
        print(f"    § {c['heading']}")
        body = c["text"] if a.full else " ".join(c["text"].split()[:70])
        print(f"    {body}{'' if a.full else ' …'}")
        if shown >= a.k:
            break
    if not shown:
        print("  no hits — NOT IN SOURCE")
    print()


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
