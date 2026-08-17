# Session digest S7 — 2026-08-17 (same chat)

## Loose-reading assignment (user request: manage all 144k unstamped rows)
- Rule: reading joins a trip if inside its time window and reachable at ≤60 km/h implied speed from both neighbouring stops; nearest-feasible wins; runner-up within 1.5× → AMBIGUOUS (never forced).
- Result: 107,821 assigned (74.7%) · 34,956 ambiguous · 774 infeasible · 712 no-trip-running.
- `trips_v4.json` (stops carry S/I markers, n_inferred per track); Excel rebuilt (`build_trips_excel_v2.py`): 228,375 rows in trip blocks, 36,442 in "Readings not assignable" with reasons; READ ME explains three tiers + units.

## Waste-facility inventory (`facilities_v2.json`)
- Municipality has exactly 2 licensed tipping points: Valorsul Estação de Transferência Rio Maior (39.3196,−8.9241) and Ecocentro (39.3174,−8.9108). Onward flow is Valorsul's own haul: TS → CTRO Cadaval (sorting, co-located with Aterro do Oeste); undifferentiated → S. João da Talha CTRSU; Mato da Cruz backup. 10 local + 39 regional sites; ~570 street ecopontos excluded.

## Dump-leg / km audit (539 clean unsplit runs)
- **Recorded odometer km ≈ 3.1× the shortest road path through ALL known stops + depot + dump legs.** Surplus ~107 km/run; uncorrelated with TS distance; morning = afternoon; dump loop itself ~9 km.
- Interpretation: fleet sweeps whole areas; logged stops are a hard LOWER bound (~1/3) of real driving. Any VRP calibrated on logged stops underestimates ~3× → strongest argument for operator GPS request.

## Explorer v4
- Inferred stops as dashed numbered markers; dashed depot (gray) and transfer-station (red) legs with km; 50 facility markers; weight semantics stated (2500 = litres; Peso = weighbridge run total).

## Weight clarification (user question)
- Never derived from fill; never assumed full. Container "2500" is litres. `Peso total` is the run's weighbridge ticket; per-bin allocation still impossible without operator info.
