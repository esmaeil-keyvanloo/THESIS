---
name: document-style
title: Word Document Style Specification
type: canon
category: constraints
status: binding
updated: 2026-08-08
derived_from: DATA/DOCUMENT/Sensor-based Recyclables Collection Planning.docx
---

# Word Document Style Specification

Baseline inherited from the thesis project document; deviations below are
deliberate improvements to legibility, marked **↑**.

## Page

| Setting | Value |
|---|---|
| Size | A4, 210 × 297 mm (11906 × 16838 twips) |
| Margins | 25.4 mm all sides ↑ *left 30 mm if bound* |
| Header / footer distance | 12.7 mm |
| Body font | Times New Roman 12 pt, or Calibri 11 pt ↑ (pick one per document) |
| Line spacing | 1.5 in body ↑, single in captions, tables and footnotes |
| Paragraph spacing | 0 before, 6 pt after ↑; no blank paragraphs used as spacing |
| Alignment | Justified body ↑ with hyphenation on, to avoid rivers |
| Widow/orphan control | On ↑ |

## Headings

| Level | Format | Numbering |
|---|---|---|
| H1 | 16 pt bold, sentence case, page break before ↑ | `1` |
| H2 | 14 pt bold | `1.1` |
| H3 | 12 pt bold | `1.1.1` |
| H4 ↑ | 12 pt bold italic, run-in | `1.1.1.1` |

- Multilevel list bound to the Heading styles so numbering is automatic.
- `Keep with next` on every heading ↑ — no heading stranded at a page foot.
- Sentence case throughout, not Title Case ↑.
- Noun-phrase headings only. No gerunds, no questions.

## Captions

Current document writes `Table 3.2.Key Milestones` — missing space,
inconsistent capitalisation, one duplicated number. Corrected form:

```
Figure 1.4 — Logical research framework
Table 3.2 — Key milestones
```

| Rule | Value |
|---|---|
| Style | `Caption`, 10 pt, sentence case, not italic ↑ |
| Numbering | `STYLEREF 1 \s` + `SEQ Figure \* ARABIC \s 1` — chapter-scoped, as-is |
| Separator | En dash with spaces ↑ (was a bare full stop) |
| Table captions | **Above** the table ↑ |
| Figure captions | **Below** the figure ↑ |
| Keep with next | On for table captions; keep with previous for figures ↑ |
| Source line ↑ | 9 pt below caption where data are not the author's: `Source: …` |
| Cross-references | Word `REF` fields, never typed literals ↑ |

Every table and figure must be referenced in the text **before** it appears.

## Tables ↑

- Header row bold, repeated on page break, `Keep with next` on.
- Horizontal rules only — top, below header, bottom. No vertical borders.
- Numbers right-aligned and decimal-consistent; text left-aligned.
- Units in the column header, not repeated in every cell.
- No merged cells except in the header.

## Equations

- **Native Word OMML only.** No images, no MathType, no LaTeX text.
- Display equations centred, number right-aligned in parentheses, chapter-scoped:
  `(3.2)` ↑ via a right-aligned tab stop and `SEQ Equation`.
- Referenced as *Equation (3.2)* through `REF` fields.
- Every symbol defined at first use; a notation table in front matter for
  documents with more than ten equations ↑.

## Front matter and pagination ↑

| Part | Numbering |
|---|---|
| Cover, title | No number shown |
| TOC, lists, abbreviations, executive summary | Roman `i, ii, iii` |
| Body onward | Arabic, restarting at `1` |

Achieved with section breaks. Footer centred. Header from the body onward
carries the chapter name via `STYLEREF 1 \n \* MERGEFORMAT`, suppressed on
the first page of each chapter.

## Lists, TOC and references

- TOC: fields, levels 1–3, hyperlinked, right-aligned page numbers with
  dot leaders.
- List of Tables and List of Figures: separate `TOC \c "Table"` and
  `TOC \c "Figure"` fields.
- Abbreviations: two-column table, alphabetical, PT ↔ EN where relevant.
- Bibliography: CSL via Zotero/Mendeley, as in the source document. One
  style throughout; APA 7 unless the faculty requires otherwise.

## Writing quality gate

Every document passes the `human-writing` skill before delivery:

```bash
python .claude/skills/human-writing/scripts/ai_tells.py <file>
```

Required: **zero critical hits**, density below 4 per 500 words.
