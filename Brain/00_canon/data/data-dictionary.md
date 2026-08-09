---
name: data-dictionary
title: Data Dictionary — Rio Maior CSVs
type: canon
category: data
status: binding
updated: 2026-08-09
basis: PROMPT 2 interview answers (DATA/PROMPT/PROMPT 2.docx) + first-pass profile
---

# Data Dictionary

Semantics confirmed by the author on 2026-08-09 (PROMPT 2). Anything marked
⚠ is an unresolved contradiction — do not build on it without a decision.

## Shared schema (both CSVs, semicolon-delimited)

| Column | Meaning | Confirmed |
|---|---|---|
| `idcontentor` | Container ID | ✔ |
| `Matricula do contentor` | Container registration code | ✔ |
| `Tipo de contentor` | Container model (OVO, TITAN, VRL, AMBI, MOXEA, E BLUE BEE …) | ✔ |
| `Volume do tipo de contentor` | Container volume, litres (2500 / 3000 / 5000) | ✔ |
| `description` | Waste fraction: Mistura de embalagens (packaging), Embalagens de papel e cartão (paper/card), Embalagens de Vidro (glass) | ✔ |
| `Distrito` / `Concelho` / `Freguesia` / `Localidade` | Administrative location | ✔ |
| `Latitude` / `Longitude` | WGS84 position | ✔ |
| `Data da leitura` | Reading timestamp | ✔ |
| `Enchimento` | Fill level, **percent 0–100**; ≥100 = overflow. −1 = sensor error (measurement not recorded); other negatives = sensor/system error → **remove** | ✔ / ⚠ see D3 |
| `idrecolha` | **Collection trip/event ID** — shared by all containers serviced on the same trip. Blank = no collection linked to that reading | ✔ |
| `Rota` | Route code; populated only for a subset of collection events, reason unconfirmed | ✔ |
| `Data de ínicio` / `Data de fim` | Trip start / end | ✔ |
| `Km totais` | Total km of the **trip** (not per container) | ✔ |
| `Peso total` | Total weight of the **trip** (not per container) — cannot be attributed to a single container directly | ✔ |

## File-level facts

| Fact | Value | Source |
|---|---|---|
| `…de_Sensores` = raw sensor output, unprocessed | ✔ | Q3 |
| `…com_Recolhas` fill = driver visual estimate {0,25,50,75,100}, recorded **at collection** | ✔ | Q4 |
| Sensor park (full dataset) | ≈ 800 containers | Q10 |
| Sensor park within urban study area | ≈ 400 containers | Q10 |
| 816 collection-file containers | broader municipal set, **not** the full park | Q11 |
| Study area | urban Rio Maior, defined by GIS boundary shapefile | Q11 |
| Sensors installed | pilot/testing subset only — neither dataset is complete coverage | Q11/Q12 |
| Re-export of untruncated sensor file | **NOT POSSIBLE** — Excel file is the only access | Q9 |
| Fleet, capacities, shifts, crew | NOT IN SOURCE — must come from municipality | Q13 |
| Depot / sorting facility locations | NOT IN SOURCE | Q14 |
| Collection policy (schedule vs threshold vs discretion) | NOT IN SOURCE | Q15 |
| Summer 2023 actual routes | not held as GPS/GIS; must be reconstructed from records | Q16 |

## ⚠ Open contradictions

| ID | Issue | Status |
|---|---|---|
| **D3** | Author says `Enchimento` is 0–100 % with ≥100 possible; but every one of the 344 sensor-file containers maxes at **82–84**, and no value >84 exists. Answer does not explain the ceiling. Possible sensor saturation. | OPEN — treat 82–84 as effective full until resolved |
| **D4a** | Author's "−1 ≈ 10,000+ rows" refers to the **sensor** file (10,114 rows of −1 confirmed); the 249 rows of −1 I reported are in the **collections** file. Both exist; no conflict, but the collections −1 also needs the same treatment (error → remove) | CLARIFIED, rule: drop all negatives in both files |
| **D1** | Sensor file truncated at Excel row limit; author cites ≈800 sensors total vs 344 in file → roughly half the sensor park is missing from the CSV. No re-export possible. Coverage of the 344 must be checked against the urban study area before use | OPEN — mitigation: GIS spatial join |
| **D2** | `idrecolha` = `Enchimento` in 90.8 % of sensor rows — still unexplained; treat sensor-file `idrecolha` as unusable | OPEN |
