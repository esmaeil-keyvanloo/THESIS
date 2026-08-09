#!/usr/bin/env python3
"""Detect LLM writing signatures in a document.

Usage:
    python ai_tells.py <file.md|file.txt|file.docx> [--quiet]

Stdlib only. Reports hits by category with line numbers, sentence-length
statistics, and a density score (hits per 500 words).

Exit codes:  0 clean  |  1 tells found  |  2 bad input
"""

import io
import re
import sys
import statistics
import zipfile
from collections import defaultdict

# ---------------------------------------------------------------- patterns
# (severity, label, regex)
PATTERNS = [
    # --- lexical -------------------------------------------------------
    ("C", "flagged verb", r"\b(delv\w+|leverag\w+|utiliz\w+|underscor\w+|showcas\w+|foster\w+|harness\w+|embark\w+|unlock\w+|elevat\w+|streamlin\w+|spearhead\w+)\b"),
    ("C", "flagged adjective", r"\b(pivotal|crucial|vital|seamless|holistic|multifaceted|nuanced|intricate|invaluable|cutting-edge|game-changing|ever-evolving)\b"),
    ("C", "flagged noun", r"\b(myriad|plethora|realm|tapestry|testament|beacon|cornerstone|synergy)\b"),
    ("C", "figurative landscape", r"\b(landscape|arena|sphere) of\b"),
    ("C", "stock phrase", r"(navigat\w+ the complexit|in today's [\w\s-]{0,20}world|at its core|treasure trove|plays? a pivotal role|serves? as a testament|the world of)"),
    ("C", "announcement phrase", r"(it is (important|worth|crucial) to note|it should be (noted|emphasi[sz]ed)|^\s*(Notably|Importantly|Interestingly),)"),
    ("H", "hollow intensifier", r"\b(significantly|substantially|dramatically|vastly|remarkably|greatly)\b(?![^.]{0,60}\d)"),
    ("M", "hedge stack", r"\b(may potentially|could possibly|might arguably|may or may not|potentially could)\b"),

    # --- syntactic -----------------------------------------------------
    ("C", "not-just-but", r"(not (just|only|merely) [^.,;]{2,60}[,—-]{1,3} (it|this|they|but)\b|isn't (just|about)[^.]{0,60}\bit's\b)"),
    ("H", "trailing participle", r",\s+(ensuring|highlighting|underscoring|paving|showcasing|reflecting|emphasi[sz]ing|ultimately leading|thereby)\b"),
    ("M", "rule-of-three transition", r"^\s*(Furthermore|Moreover|Additionally|In addition),"),
    ("M", "conclusion opener", r"^\s*(In conclusion|Overall|Ultimately|In summary|To sum up),"),

    # --- academic ------------------------------------------------------
    ("C", "unattributed authority", r"\b(studies (show|have shown|indicate)|research (shows|indicates|suggests)|experts agree|it is widely (accepted|recognised|recognized))\b(?![^.]{0,80}\()"),
    ("C", "generic contribution", r"\b(valuable insights?|significant contribution to the (literature|field)|sheds? light on)\b"),
    ("H", "literature drone", r"\b(numerous|several|many|various) (studies|researchers|authors|works) have (explored|examined|investigated|analy[sz]ed|shown)\b"),

    # --- structural / typographic --------------------------------------
    ("H", "gerund heading", r"^#{1,6}\s+(Understanding|Exploring|Navigating|Unlocking|Unpacking|Harnessing|Leveraging|Diving)\b"),
    ("H", "question heading", r"^#{1,6}\s+.*\?\s*$"),
    ("C", "emoji", "[\U0001F300-\U0001FAFF✀-➿☀-⛿]"),
    ("H", "arrow/check glyph", r"[→✓✔➤➔]"),
    ("M", "title case heading", r"^#{1,6}\s+(?:[A-Z][a-z]+\s+){3,}[A-Z][a-z]+\s*$"),
]

BOLD_LEAD = re.compile(r"^\s*[-*]\s+\*\*[^*]{2,60}\*\*\s*[-–—:]")
LIST_ITEM = re.compile(r"^\s*[-*]\s+")
TRICOLON = re.compile(r"\b[\w-]+,\s+[\w-]+,\s+and\s+[\w-]+\b")
EMDASH = re.compile(r"—")

CODE_FENCE = re.compile(r"^\s*```")


# ---------------------------------------------------------------- loading
def load(path):
    if path.lower().endswith(".docx"):
        z = zipfile.ZipFile(path)
        xml = z.read("word/document.xml").decode("utf-8", "ignore")
        xml = re.sub(r"</w:p>", "\n", xml)
        xml = re.sub(r"<[^>]+>", "", xml)
        import html
        return html.unescape(xml)
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def strip_code(lines):
    """Blank out fenced code blocks so they are not linted as prose."""
    out, inside = [], False
    for ln in lines:
        if CODE_FENCE.match(ln):
            inside = not inside
            out.append("")
            continue
        out.append("" if inside else ln)
    return out


# ---------------------------------------------------------------- analysis
def sentences(text):
    text = re.sub(r"\s+", " ", re.sub(r"^#.*$", "", text, flags=re.M))
    raw = re.split(r"(?<=[.!?])\s+(?=[A-Z\"'(])", text)
    return [s for s in raw if len(s.split()) >= 3]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    quiet = "--quiet" in sys.argv
    if not args:
        print(__doc__)
        return 2
    path = args[0]

    try:
        text = load(path)
    except Exception as exc:                       # noqa: BLE001
        print(f"cannot read {path}: {exc}")
        return 2

    lines = strip_code(text.splitlines())
    body = "\n".join(lines)
    words = len(body.split())
    if words == 0:
        print("empty document")
        return 2

    hits = defaultdict(list)
    for sev, label, pat in PATTERNS:
        rx = re.compile(pat, re.I | re.M)
        for i, ln in enumerate(lines, 1):
            for m in rx.finditer(ln):
                frag = m.group(0).strip()
                if frag:
                    hits[(sev, label)].append((i, frag[:70]))

    # tricolon density
    tri = [(i, m.group(0)[:70]) for i, ln in enumerate(lines, 1)
           for m in TRICOLON.finditer(ln)]
    # academic prose legitimately carries ~1 per 400 words; flag real abuse only
    if len(tri) > max(2, words // 300):
        hits[("C", "tricolon abuse")] = tri

    # em dash density
    ed = EMDASH.findall(body)
    if len(ed) > max(1, words // 300):
        hits[("H", "em-dash saturation")] = [(0, f"{len(ed)} em dashes in {words} words")]

    # bold lead-in ratio
    items = [ln for ln in lines if LIST_ITEM.match(ln)]
    bolds = [ln for ln in items if BOLD_LEAD.match(ln)]
    if len(items) >= 4 and len(bolds) / len(items) > 0.8:
        hits[("H", "universal bold lead-ins")] = [
            (0, f"{len(bolds)}/{len(items)} bullets use **term** —")]

    # rhythm
    sents = sentences(body)
    lens = [len(s.split()) for s in sents]
    rhythm_flag = False
    if len(lens) >= 10:
        sd = statistics.pstdev(lens)
        mean = statistics.mean(lens)
        short = sum(1 for x in lens if x < 8)
        if sd < 8:
            rhythm_flag = True
            hits[("C", "uniform sentence length")] = [
                (0, f"sd={sd:.1f} words (target > 8), mean={mean:.1f}")]
        if short / len(lens) < 0.08:
            hits[("H", "no short sentences")] = [
                (0, f"only {short}/{len(lens)} sentences under 8 words")]

    # ---------------------------------------------------------- report
    total = sum(len(v) for v in hits.values())
    density = total / words * 500

    order = {"C": 0, "H": 1, "M": 2}
    print(f"\n  {path}")
    print(f"  {words} words | {len(sents)} sentences | "
          f"{total} hits | density {density:.1f} per 500 words\n")

    if not hits:
        print("  clean — no tells detected\n")
        return 0

    for (sev, label) in sorted(hits, key=lambda k: (order[k[0]], k[1])):
        found = hits[(sev, label)]
        print(f"  [{sev}] {label}  ({len(found)})")
        if not quiet:
            for line_no, frag in found[:6]:
                loc = f"L{line_no}" if line_no else "  —"
                print(f"        {loc}: {frag}")
            if len(found) > 6:
                print(f"        … {len(found) - 6} more")
        print()

    crit = sum(len(v) for k, v in hits.items() if k[0] == "C")
    verdict = "FAIL" if (crit or density >= 4) else "PASS"
    print(f"  critical: {crit} | density: {density:.1f} | {verdict}")
    print("  target: 0 critical, density < 4\n")
    return 1 if verdict == "FAIL" else 0


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                                  errors="replace")
    sys.exit(main())
