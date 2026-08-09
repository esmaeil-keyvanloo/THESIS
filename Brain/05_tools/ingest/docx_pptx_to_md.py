#!/usr/bin/env python3
"""Convert DATA/ .docx and .pptx sources to provenance-stamped Markdown.

Stdlib only — Office files are ZIP + XML.

Usage:
    python Brain/05_tools/ingest/docx_pptx_to_md.py

Writes to Brain/01_sources/<category>/<slug>.md and records a SHA-256 of
every source file so drift in DATA/ is detectable.
"""

import hashlib
import html
import io
import re
import sys
import zipfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]          # THESIS CLAUDE/Brain -> up 2
PROJ = ROOT.parent if ROOT.name == "Brain" else ROOT
DATA = PROJ / "DATA"
OUT = PROJ / "Brain" / "01_sources"

# source file  ->  (category folder, output slug)
ROUTE = {
    "Sensor-based Recyclables Collection Planning.docx":
        ("thesis", "thesis-project"),
    "Chapters - Recyclables Waste Collection in a Portuguese Municipality.docx":
        ("proposal", "proposal-chapters"),
    "Esmaeil_ThesisProject-outline .docx":
        ("proposal", "thesis-outline"),
    "Overview of PhD thesis Optimizing Recycling Waste Collection.docx":
        ("proposal", "thesis-overview"),
    "PROPOSAL DEFENCE SESSION OUPUT.docx":
        ("defence", "jury-questions"),
    "defence powerpoint_final-esmaeil keyvanloo.pptx":
        ("defence", "defence-slides"),
    "riomaior .docx":
        ("field_survey", "rio-maior-field-survey"),
    "مرکز شهر .docx":
        ("field_survey", "city-centre-notes-fa"),
    "PROMPT 1.docx":
        ("application", "project-brief"),
    "PROMPT 2.docx":
        ("application", "interview-answers"),
    # discussion history with ChatGPT
    "email to prpfessor.docx":
        ("discussions", "email-to-professor"),
    "exel define.docx":
        ("discussions", "excel-columns-definition"),
    "interview quetion.docx":
        ("discussions", "interview-questions-draft"),
    "w smart project.docx":
        ("discussions", "wsmart-project-notes"),
    "روند.docx":
        ("discussions", "process-notes-fa"),
    "نکات مهم .docx":
        ("discussions", "important-points-fa"),
}

NS_T = re.compile(r"<w:t[^>]*>([^<]*)</w:t>")
P_SPLIT = re.compile(r"<w:p[ >].*?</w:p>|<w:p/>", re.S)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def para_text(block):
    """Text of a <w:p>, with tabs/breaks and OMML equations marked."""
    b = re.sub(r"<w:tab[^>]*/>", "\t", block)
    b = re.sub(r"<w:br[^>]*/>", " ", b)
    # mark equations before stripping tags
    b = re.sub(r"<m:oMathPara.*?</m:oMathPara>", " ⟦EQUATION:display⟧ ", b, flags=re.S)
    b = re.sub(r"<m:oMath.*?</m:oMath>", " ⟦EQUATION:inline⟧ ", b, flags=re.S)
    txt = "".join(NS_T.findall(b))
    return html.unescape(txt).strip()


def docx_to_md(path):
    z = zipfile.ZipFile(path)
    xml = z.read("word/document.xml").decode("utf-8", "ignore")

    # isolate tables so their rows are not emitted as loose paragraphs
    out, pos = [], 0
    for tm in re.finditer(r"<w:tbl>.*?</w:tbl>", xml, re.S):
        out.append(("flow", xml[pos:tm.start()]))
        out.append(("table", tm.group(0)))
        pos = tm.end()
    out.append(("flow", xml[pos:]))

    lines = []
    for kind, chunk in out:
        if kind == "table":
            rows = []
            for rm in re.finditer(r"<w:tr[ >].*?</w:tr>", chunk, re.S):
                cells = [para_text("".join(P_SPLIT.findall(cm.group(0))) or cm.group(0))
                         for cm in re.finditer(r"<w:tc>.*?</w:tc>", rm.group(0), re.S)]
                cells = [c.replace("|", "\\|").replace("\t", " ") or " " for c in cells]
                if any(c.strip() for c in cells):
                    rows.append(cells)
            if rows:
                width = max(len(r) for r in rows)
                rows = [r + [" "] * (width - len(r)) for r in rows]
                lines.append("")
                lines.append("| " + " | ".join(rows[0]) + " |")
                lines.append("|" + "---|" * width)
                for r in rows[1:]:
                    lines.append("| " + " | ".join(r) + " |")
                lines.append("")
            continue

        for block in P_SPLIT.findall(chunk):
            style = re.search(r'<w:pStyle w:val="([^"]+)"', block)
            style = style.group(1) if style else "Normal"
            txt = para_text(block)
            if not txt:
                continue
            if style.startswith("TOC") or style == "TableofFigures":
                continue                                    # regenerated, not content
            hm = re.match(r"Heading(\d)", style)
            if hm:
                lines.append("")
                lines.append("#" * min(int(hm.group(1)), 6) + " " + txt)
                lines.append("")
            elif style == "Caption":
                lines.append("")
                lines.append(f"*{txt}*")
                lines.append("")
            elif style in ("ListParagraph", "ListBullet", "ListNumber"):
                lines.append(f"- {txt}")
            elif style == "Bibliography":
                lines.append(f"- {txt}")
            else:
                lines.append(txt)
                lines.append("")
    return lines


def pptx_to_md(path):
    z = zipfile.ZipFile(path)
    slides = sorted(
        (n for n in z.namelist()
         if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)),
        key=lambda n: int(re.search(r"(\d+)", n.split("/")[-1]).group(1)))
    notes = {n: True for n in z.namelist() if "notesSlide" in n}

    lines = []
    for n in slides:
        idx = int(re.search(r"(\d+)", n.split("/")[-1]).group(1))
        xml = z.read(n).decode("utf-8", "ignore")
        texts = []
        for sp in re.finditer(r"<p:sp>.*?</p:sp>", xml, re.S):
            body = "".join(
                html.unescape("".join(re.findall(r"<a:t>([^<]*)</a:t>", pm.group(0))))
                for pm in re.finditer(r"<a:p>.*?</a:p>", sp.group(0), re.S))
            for pm in re.finditer(r"<a:p>.*?</a:p>", sp.group(0), re.S):
                t = html.unescape("".join(re.findall(r"<a:t>([^<]*)</a:t>", pm.group(0)))).strip()
                if t:
                    texts.append(t)
        lines.append("")
        lines.append(f"## Slide {idx}")
        lines.append("")
        if texts:
            lines.append(f"**{texts[0]}**")
            lines.append("")
            for t in texts[1:]:
                lines.append(f"- {t}")
        else:
            lines.append("*(no text on slide)*")
        # speaker notes
        nn = f"ppt/notesSlides/notesSlide{idx}.xml"
        if nn in notes:
            nx = z.read(nn).decode("utf-8", "ignore")
            nt = [html.unescape("".join(re.findall(r"<a:t>([^<]*)</a:t>", pm.group(0)))).strip()
                  for pm in re.finditer(r"<a:p>.*?</a:p>", nx, re.S)]
            nt = [t for t in nt if t and not t.isdigit()]
            if nt:
                lines.append("")
                lines.append("> **Notes:** " + " ".join(nt))
        lines.append("")
    return lines


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = []
    for src in sorted(DATA.rglob("*")):
        if src.name.startswith("~$") or src.is_dir():
            continue
        if src.suffix.lower() not in (".docx", ".pptx"):
            continue
        route = ROUTE.get(src.name)
        if not route:
            print(f"  SKIP (unrouted): {src.name}")
            continue
        cat, slug = route
        dest_dir = OUT / cat
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / f"{slug}.md"

        body = docx_to_md(src) if src.suffix.lower() == ".docx" else pptx_to_md(src)
        text = re.sub(r"\n{3,}", "\n\n", "\n".join(body)).strip()
        digest = sha256(src)
        words = len(text.split())

        rel = src.relative_to(PROJ).as_posix()
        fm = (
            "---\n"
            f"name: {slug}\n"
            f"title: {src.stem.strip()}\n"
            "type: source\n"
            f"category: {cat}\n"
            f"source_file: {rel}\n"
            f"source_sha256: {digest}\n"
            f"source_bytes: {src.stat().st_size}\n"
            f"ingested: {date.today().isoformat()}\n"
            f"words: {words}\n"
            "verbatim: true\n"
            "---\n\n"
            f"> Faithful conversion of `{rel}`. Do not edit — edit the source "
            "and re-run the ingest.\n\n"
        )
        dest.write_text(fm + text + "\n", encoding="utf-8")
        manifest.append((rel, digest, src.stat().st_size, words,
                         dest.relative_to(PROJ).as_posix()))
        print(f"  OK  {cat:13s} {words:7d} w  <- {src.name}")

    # checksum manifest
    man = PROJ / "Brain" / "06_manifest" / "checksums" / "sources.md"
    man.parent.mkdir(parents=True, exist_ok=True)
    rows = ["| Source | SHA-256 (first 16) | Bytes | Words | Markdown |",
            "|---|---|---|---|---|"]
    for rel, dg, by, wd, out in manifest:
        rows.append(f"| `{rel}` | `{dg[:16]}` | {by:,} | {wd:,} | `{out}` |")
    man.write_text(
        f"---\nname: source-checksums\ntype: manifest\nupdated: "
        f"{date.today().isoformat()}\n---\n\n# Source checksums\n\n"
        + "\n".join(rows) + "\n", encoding="utf-8")
    print(f"\n  manifest -> {man.relative_to(PROJ)}")


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
