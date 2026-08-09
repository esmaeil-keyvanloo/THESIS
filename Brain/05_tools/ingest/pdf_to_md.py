#!/usr/bin/env python3
"""Convert DATA/ PDFs to provenance-stamped Markdown.

Usage:
    python Brain/05_tools/ingest/pdf_to_md.py
"""

import hashlib
import io
import re
import sys
from datetime import date
from pathlib import Path

import pdfplumber

PROJ = Path(__file__).resolve().parents[3]
DATA = PROJ / "DATA"
OUT = PROJ / "Brain" / "01_sources"

ROUTE = {
    "WSmartRoute+_Application (2).pdf": ("application", "wsmartroute-application"),
    "regresion.pdf": ("thesis", "regression-output"),
}


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def main():
    for src in sorted(DATA.rglob("*.pdf")):
        route = ROUTE.get(src.name)
        if not route:
            print(f"  SKIP (unrouted): {src.name}")
            continue
        cat, slug = route
        lines = []
        with pdfplumber.open(src) as pdf:
            for i, page in enumerate(pdf.pages, 1):
                lines.append(f"\n## Page {i}\n")
                txt = page.extract_text() or ""
                lines.append(txt.strip() or "*(no extractable text — likely an image)*")
                for t in page.extract_tables() or []:
                    rows = [[(c or "").replace("|", "\\|").replace("\n", " ").strip() or " "
                             for c in r] for r in t if any(r)]
                    if len(rows) < 2:
                        continue
                    w = max(len(r) for r in rows)
                    rows = [r + [" "] * (w - len(r)) for r in rows]
                    lines.append("")
                    lines.append("| " + " | ".join(rows[0]) + " |")
                    lines.append("|" + "---|" * w)
                    for r in rows[1:]:
                        lines.append("| " + " | ".join(r) + " |")
                    lines.append("")

        text = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()
        dest = OUT / cat
        dest.mkdir(parents=True, exist_ok=True)
        rel = src.relative_to(PROJ).as_posix()
        fm = (f"---\nname: {slug}\ntitle: {src.stem}\ntype: source\n"
              f"category: {cat}\nsource_file: {rel}\n"
              f"source_sha256: {sha256(src)}\nsource_bytes: {src.stat().st_size}\n"
              f"ingested: {date.today().isoformat()}\nwords: {len(text.split())}\n"
              f"verbatim: true\n---\n\n> Faithful conversion of `{rel}`. "
              "Do not edit — edit the source and re-run the ingest.\n\n")
        (dest / f"{slug}.md").write_text(fm + text + "\n", encoding="utf-8")
        print(f"  OK  {cat:13s} {len(text.split()):7d} w  <- {src.name}")


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
