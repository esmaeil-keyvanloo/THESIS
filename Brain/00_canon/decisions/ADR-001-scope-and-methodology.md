---
name: adr-001-scope-and-methodology
title: ADR-001 — Core scope and methodological chain
type: canon
category: decisions
status: accepted
date: 2026-08-09
source: DATA/PROMPT/PROMPT 2.docx (Q17)
supersedes: none
---

# ADR-001 — Core scope and methodological chain

## Decision (author, 2026-08-09)

Core framework, open to refinement but binding as the baseline:

```
Stepwise Regression → Waste-Demand Estimation
  → Deterministic Capacitated p-Median  (baseline)
  → Uncertainty / Scenario Generation (Monte Carlo where appropriate)
  → Stochastic Capacitated p-Median     (main model)
  → Robust Capacitated p-Median         (optional benchmark)
  → Sensitivity comparison
```

- **Routing (VRP/CVRP/IRP) is an extension, not core.** The thesis stands
  without it. It activates only if depot, facility, fleet and reliable
  route data are obtained.
- Study area: urban Rio Maior per GIS boundary; containers outside are
  analysed separately, not silently dropped.
- Claude is mandated to **audit the methodology** and may propose stronger
  methods, subject to (a) data availability, (b) defensibility before the
  jury.

## Data rulings folded in

| Ruling | Effect |
|---|---|
| Negative `Enchimento` = sensor/system error | Remove in cleaning; count what is removed |
| Trip-level `Km totais` / `Peso total` | Container-level weight requires a disaggregation model, or weight is used only at trip/route level |
| No untruncated re-export | 344-container sensor file is final; validate its spatial coverage inside the study area |

## Amendment 2026-08-10 — boundary-crossing routes

Collection vehicles service containers **inside and outside** the urban
study-area boundary within the same trip. Consequences:

- Trip-level figures (`Km totais`, `Peso total`) cannot be assumed to refer
  to study-area containers only.
- Any routing model must either (a) include out-of-area containers as
  mandatory stops, or (b) model boundary-crossing explicitly; silently
  clipping routes at the border is not valid.
- Out-of-area containers are analysed separately, never dropped (Q14).

## Report standard amendment

The ≤15-page limit is soft — exceeding it is acceptable. Priorities, in
order: simplicity, legibility, aesthetic typography (deliberate font
pairing, restrained colour palette, clear heading hierarchy). Maps and a
professional pipeline flowchart (Figma/FigJam) are expected content.

## Consequences

- Demand estimation carries the thesis; its quality gates everything.
- The stochastic p-median is the scientific contribution; the deterministic
  run is the yardstick.
- Missing operational data moves routing to conditional status — public
  deep-research (with citations) is the assigned mitigation.
