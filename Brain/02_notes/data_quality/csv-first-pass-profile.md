---
name: csv-first-pass-profile
title: CSV First-Pass Profile and Defect Register
type: note
category: data_quality
status: provisional
updated: 2026-08-08
sources:
  - DATA/XLS/Enchimentos_com_Recolhas[RioMaior].csv
  - DATA/XLS/Enchimentos_de_Sensores[RioMaior].csv
tool: Brain/05_tools/db/profile_csv_stdlib.py
log: Brain/06_manifest/logs/csv_profile_pass1.log
---

# CSV First-Pass Profile

Provisional. Superseded once the DuckDB profile runs and the interview
answers are recorded in `Brain/00_canon/data/`.

Both files share one 19-column, semicolon-delimited schema. The user
described them as comma-delimited; they are not.

## Headline figures

| | `…com_Recolhas` | `…de_Sensores` |
|---|---|---|
| Rows | 264,817 | **1,048,575** |
| Distinct containers | 816 | 344 |
| Date range | 2020-01-02 → 2024-04-29 | 2020-01-01 → 2024-04-30 |
| `Enchimento` distinct values | **5** (+ `-1`) | 85 (+ negatives) |
| `Enchimento` range | 0, 25, 50, 75, 100 | 0 – 84, plus negatives |
| `idrecolha` populated | 23.0 % (60,916) | 100 % |
| `Rota` populated | 8.6 % (22,674) | 0 % |
| `Km totais` / `Peso total` | 23.0 % | 0 % |
| Distinct `idrecolha` | 9,984 | 85 |
| Distinct `Rota` | 92 | 0 |
| Coordinates outside Rio Maior | 0 | 0 |

## Defects

### D1 — Sensor file is truncated at the Excel row limit — **critical**

1,048,575 data rows + 1 header = **1,048,576**, exactly Excel's maximum.
The file is sorted by container, not by date, so truncation removed whole
**containers**, not a time period. The 344 containers present are therefore
an arbitrary prefix, not a sample.

*Action:* request a re-export as CSV or Parquet, written without Excel.

### D2 — `idrecolha` duplicates `Enchimento` in the sensor file — **critical**

Equal in 951,743 of 1,048,575 rows (**90.8 %**). In the collections file
the two columns never coincide. Column shift on export is the likely cause;
in effect the sensor file carries no usable collection identifier.

### D3 — `Enchimento` caps at 82–84 in the sensor file — **critical, unresolved**

Every one of the 344 containers has a maximum of 82, 83 or 84:

| Per-container max | Containers |
|---|---|
| 84 | 20 |
| 83 | 10 |
| 82 | 314 |

A percentage would not cap uniformly below 100 across every container and
every container type. The uniformity also argues against physical container
depth, since `OVO`, `TITAN`, `VRL` and `AMBI` at 2500, 3000 and 5000 L do
not share a geometry. The unit is therefore **unknown** and must not be
assumed to be percent. Pending interview.

### D4 — Negative `Enchimento` values — **high**

96,832 rows (9.2 % of the sensor file).

| Value | Rows |
|---|---|
| −116 | 37,052 |
| −3 | 11,748 |
| −1 | 10,114 |
| −4 | 8,422 |
| −2 | 5,804 |
| −89 | 3,353 |

The mixture of small magnitudes (−1 … −9, 40 k rows) and large discrete
ones (−116, −89, −94, −110) suggests two different failure modes rather
than one. Present across all seven container types.

### D5 — Driver estimates are quartile-coded — **informational**

The collections file takes only 0, 25, 50, 75, 100, with 249 rows at −1.
Consistent with a visual estimate recorded by the driver on a four-point
scale. 144,804 rows (54.7 %) are 0.

This is the raw material for the thesis chapter comparing driver-based
against sensor-based fill information.

### D6 — Container populations differ — **high**

816 containers in the collections file against 344 in the sensor file.
Confounded with D1, so the true count of instrumented containers is not yet
known.

### D7 — Glass is under-represented in the sensor file — **moderate**

| Fraction | Collections | Sensors |
|---|---|---|
| Mistura de embalagens | 101,291 | 519,405 |
| Embalagens de papel e cartão | 96,055 | 509,091 |
| Embalagens de Vidro | 67,471 | 20,079 |

Glass falls from 25 % of rows to 1.9 %. Either few glass containers are
instrumented, or glass containers were disproportionately lost to D1.

## Descriptive breakdowns

**Container types** — OVO, OVO S, VRL, TITAN, TITAN K, AMBI, MOXEA,
E BLUE BEE, and 164 rows of `METALICO-Não USAR` (literally "metallic — do
not use") in the collections file.

**Volumes** — 2500 L dominant, plus 3000 L and 5000 L.

**Parishes** — ten *freguesias*; Rio Maior itself carries ~62 % of rows.

## Open questions

Carried to the interview; recorded in `Brain/00_canon/data/` once answered.
Nothing downstream of this file is trustworthy until D1, D2 and D3 are
resolved.
