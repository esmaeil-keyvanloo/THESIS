#!/usr/bin/env python3
"""Chunk the Markdown corpus and build the hybrid retrieval index.

Usage:
    python Brain/05_tools/ingest/build_index.py

Indexes ONLY prose: Brain/00_canon, Brain/01_sources, Brain/02_notes.
Numeric data is never embedded — it is queried in DuckDB.

Outputs:
    Brain/04_index/chunks/chunks.jsonl
    Brain/04_index/lancedb/            (bge-m3 vectors)
    Brain/04_index/bm25/bm25.pkl
"""

import io
import json
import pickle
import re
import sys
from pathlib import Path

PROJ = Path(__file__).resolve().parents[3]
IDX = PROJ / "Brain" / "04_index"
SCAN = ["00_canon", "01_sources", "02_notes"]

TARGET_WORDS = 650      # ≈ 900 tokens
OVERLAP_WORDS = 100     # ≈ 15 %
MODEL = "BAAI/bge-m3"


def parse(path):
    raw = path.read_text(encoding="utf-8", errors="replace")
    meta = {}
    if raw.startswith("---"):
        end = raw.find("\n---", 3)
        if end > 0:
            for line in raw[3:end].splitlines():
                if ":" in line and not line.startswith((" ", "-")):
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip()
            raw = raw[end + 4:]
    return meta, raw


def sections(text):
    """Split into (heading_path, body) using ATX headings."""
    out, stack, buf, cur = [], [], [], ""
    for line in text.splitlines():
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            if buf:
                out.append((cur, "\n".join(buf).strip()))
                buf = []
            lvl, title = len(m.group(1)), m.group(2).strip()
            stack = stack[: lvl - 1] + [title]
            cur = " › ".join(stack)
        else:
            buf.append(line)
    if buf:
        out.append((cur, "\n".join(buf).strip()))
    return [(h, b) for h, b in out if b]


def pack(section_text):
    words = section_text.split()
    if len(words) <= TARGET_WORDS:
        return [section_text] if words else []
    out, i = [], 0
    while i < len(words):
        out.append(" ".join(words[i:i + TARGET_WORDS]))
        i += TARGET_WORDS - OVERLAP_WORDS
    return out


def build_chunks():
    chunks = []
    for folder in SCAN:
        for md in sorted((PROJ / "Brain" / folder).rglob("*.md")):
            if md.name == "README.md":
                continue
            meta, body = parse(md)
            rel = md.relative_to(PROJ).as_posix()
            for heading, text in sections(body):
                for j, piece in enumerate(pack(text)):
                    chunks.append({
                        "id": f"{rel}#{len(chunks)}",
                        "text": piece,
                        "heading": heading or "(document root)",
                        "file": rel,
                        "name": meta.get("name", md.stem),
                        "title": meta.get("title", md.stem),
                        "type": meta.get("type", "unknown"),
                        "category": meta.get("category", folder),
                        "source_file": meta.get("source_file", rel),
                        "words": len(piece.split()),
                        "part": j,
                    })
    return chunks


def main():
    IDX.mkdir(parents=True, exist_ok=True)
    (IDX / "chunks").mkdir(exist_ok=True)
    (IDX / "bm25").mkdir(exist_ok=True)

    chunks = build_chunks()
    print(f"  {len(chunks)} chunks from {len({c['file'] for c in chunks})} files")
    print(f"  {sum(c['words'] for c in chunks):,} words total")

    with open(IDX / "chunks" / "chunks.jsonl", "w", encoding="utf-8") as fh:
        for c in chunks:
            fh.write(json.dumps(c, ensure_ascii=False) + "\n")

    # ---- BM25 ----
    from rank_bm25 import BM25Okapi
    tok = lambda s: re.findall(r"\w+", s.lower())
    corpus = [tok(f"{c['title']} {c['heading']} {c['text']}") for c in chunks]
    with open(IDX / "bm25" / "bm25.pkl", "wb") as fh:
        pickle.dump({"bm25": BM25Okapi(corpus),
                     "ids": [c["id"] for c in chunks]}, fh)
    print("  bm25 index written")

    # ---- dense ----
    from sentence_transformers import SentenceTransformer
    import lancedb
    import pyarrow as pa

    print(f"  loading {MODEL} …")
    model = SentenceTransformer(MODEL)
    texts = [f"{c['title']} — {c['heading']}\n{c['text']}" for c in chunks]
    vecs = model.encode(texts, batch_size=8, show_progress_bar=True,
                        normalize_embeddings=True)
    dim = int(vecs.shape[1])
    print(f"  embedded {len(vecs)} chunks, dim={dim}")

    db = lancedb.connect(str(IDX / "lancedb"))
    rows = [{**c, "vector": v.tolist()} for c, v in zip(chunks, vecs)]
    if "corpus" in db.table_names():
        db.drop_table("corpus")
    db.create_table("corpus", rows)
    print(f"  lancedb table 'corpus' written -> {(IDX/'lancedb').relative_to(PROJ)}")


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
