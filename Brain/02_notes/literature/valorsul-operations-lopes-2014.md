---
name: valorsul-operations-lopes-2014
title: Valorsul Oeste selective collection — operational parameters
type: reference
category: literature
status: verified
updated: 2026-08-10
citation: >
  Lopes, D. M. T. (2014). Otimização da recolha seletiva na Valorsul:
  estudo de cenários alternativos. MSc dissertation, Instituto Superior
  Técnico, Universidade de Lisboa. Supervisors: A. P. Barbosa-Póvoa,
  T. R. P. Ramos.
local_pdf: Brain/02_notes/literature/pdfs/Lopes_Valorsul_recolha_seletiva_IST.pdf
url: https://fenix.tecnico.ulisboa.pt/downloadFile/1407770020544543/Dissertacao%20Mestrado%20Diogo%20Lopes_final.pdf
caveat: Operational snapshot Jan–Jun 2013; fleet has since grown (Valorsul site 2026 says 21 vehicles, ~24,000 containers). Verify currency before quoting as present-day.
---

# Valorsul Oeste selective collection — operational parameters (2013)

Fills most of the Q13–Q15 gaps (fleet, depot, policy) with a citable
public source covering the **same operator and network that includes Rio
Maior** (14 Oeste municipalities).

## Depot / facility — answers Q14

**CTRO location (Valorsul official
[installations page](https://www.valorsul.pt/pt/contactos/instalacoes/)):**
Estrada Nacional 361-1, km 14, Outeiro da Cabeça – Vilar, 2550-078 Vilar,
Cadaval. **Lat 39.188989, Lon −9.148423** — ~23 km SW of Rio Maior centre.

- Single vehicle base: **CTRO (Centro de Tratamento de Resíduos do Oeste),
  Cadaval** — sorting centre + landfill + ecocentro + transfer station.
- **All circuits are closed**: start and end at CTRO (pp. 11, 17).
- Weighing (báscula) at CTRO entrance on return → net weight recorded
  **per trip** — independently confirms `Peso total` is trip-level.
- Paper/card and plastic/metal go to the sorting line; **glass is not
  sorted** (Valorsul acts as receiver/shipper only).
- Dissertation scenarios studied adding bases at Nazaré / Óbidos transfer
  stations — evidence the single-base asymmetry is a known inefficiency.

## Fleet — answers Q13 (2013 snapshot)

| Vehicles | Role | Body | Volume | Payload |
|---|---|---|---|---|
| 3 × MAN 18.284 LK L2000 (2001) | collection | no compactor (used for glass) | 20 m³ | 15,000 kg |
| 2 × Volvo FM9 (2005, Ampliroll) | collection | compactor | 20 m³ | 13,945 kg |
| 5 × MAN TGM 18.280 (2007–08) | collection | compactor | 20 m³ | 5,580 kg |
| 2 × Volvo FM9 (2009, rear-load) | collection | compactor | 15 m³ | 4,465 kg |
| 2 × light trucks (Nissan/Toyota) | ecoponto maintenance | open box | — | ~2,500–2,800 kg |

- 12 collection + 2 maintenance vehicles; crane (grua) lifts, driver
  operates, one helper.
- Fuel consumption 40–60 L/100 km.
- 2026 Valorsul site: **21 collection vehicles**, ~24,000 containers,
  30 outsourced teams — fleet has roughly doubled since 2013.

## Circuits and policy — answers Q15

- **82 predefined circuits**: 26 paper/card, 26 plastic/metal, 30 glass.
- Collection Mon–Fri, **2 shifts/day**: 05:00–12:30 and 15:00–22:30
  (Fri 7 h). Circuit duration bounded by the shift (7.5 h / 7 h).
- Mean periodicity: paper/card **9.3 d**, plastic/metal **8.3 d**, glass
  **20.5 d** (max 14 / 14 / 30 d).
- ~81–83 containers collected per circuit, all three fractions.
- Circuit ends when list is done **or vehicle is full**, then returns.

## Driver fill records — confirms Q4 and the collections CSV encoding

At each ecoponto the crew records fill on a PDA as:
**vazio / menos de meio / meio / mais de meio / cheio**
(empty / <half / half / >half / full) → maps 1:1 to the
**0 / 25 / 50 / 75 / 100** in `Enchimentos_com_Recolhas`. Data feed the
routing-support software when the PDA syncs.

## Container park (2013)

- 2,544 ecopontos, 7,807 containers (2,542 papelão / 2,378 embalão /
  2,887 vidrão); ~85 % surface **OTTO + TITAN 2.5 m³**; underground
  MOLOK 3 and 5 m³. Volumes match the CSV (2500/3000/5000 L).
- Largest shares: Torres Vedras, Alcobaça, Caldas da Rainha.

## Known constraints (author's list, p. 17)

Intervention area too large and asymmetric w.r.t. CTRO; worker hour
limits; hard-to-access urban ecopontos; **uncertainty of fill levels** —
the exact problem the sensor thesis addresses.
