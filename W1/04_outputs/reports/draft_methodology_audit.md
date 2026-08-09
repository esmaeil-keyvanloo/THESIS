# Executive summary

This report audits the methodology proposed for the PhD thesis *Sensor-based Recyclables Collection Planning* and grounds it in the data that actually exist for Rio Maior. Three findings drive everything else.

First, the operational context is now documented. Rio Maior's ecoponto network is served by Valorsul within its 14-municipality Oeste system. Every collection circuit starts and ends at the CTRO facility in Cadaval, 23 km southwest of the city, outside the study area. Fleet composition, shift times, circuit periodicities and the driver fill-recording procedure are all recoverable from public sources, so the routing extension is no longer blocked by missing operational facts.

Second, the demand model in its current form does not work. The bin-level regression fitted to 452 containers explains 1.3 % of the variation in demand, and its overall F-test (p = 0.95) cannot reject the hypothesis that the predictors explain nothing at all. This is not a small weakness; demand estimation feeds every optimisation stage downstream. The cause is identifiable and repairable: a static, cross-sectional specification is being asked to explain a dynamic quantity, and the response variable itself is built on trip-level weights that cannot be attributed to single containers. The sensors, the thesis's own subject, provide the repair.

Third, the optimisation chain (deterministic capacitated p-median as baseline, stochastic scenario-based p-median as the main model) is methodologically sound, standard in the literature, and defensible before a jury. The existing Mosel implementation, however, is a synthetic proof of concept with ten invented population centres; it must be rebuilt on the real network before any thesis claim rests on it.

The report explains each method in plain terms, states the audit verdict with its evidence, and closes with a prioritised list of eleven recommendations. The single most important one: rebuild the demand model at the container-day level with sensor-derived fill rates as the response, and only then re-run the location models.

# 1. Problem and context

## 1.1 The operational problem

Recyclable waste in Rio Maior is deposited by citizens at ecopontos, street sites holding, in the usual case, three 2.5 m³ containers: blue for paper and card, yellow for packaging, green for glass. Collection is performed by Valorsul, the concession holder for Lisbon North and the Oeste region, using predefined closed circuits: a truck leaves the CTRO treatment centre in Cadaval, empties the containers of one material type along its route, and returns to CTRO to be weighed and unloaded.

The weakness of this arrangement is that circuits run on fixed periodicities while container filling does not. A 2014 study of the same system found circuits for paper running every 9.3 days on average and glass every 20.5 days, with fill levels recorded only as a driver's five-point visual estimate at the moment of collection. The result is the familiar pair of failures: trucks visiting containers that are nearly empty, and containers overflowing before their scheduled visit. WSmartRoute+ project data for a comparable operator found roughly half of rural containers below 25 % fill at the moment of collection.

Between 2020 and 2024, fill-level sensors were installed in a pilot subset of Rio Maior's containers. The thesis asks what this new information stream is worth: specifically, whether container *locations* — decided years ago on judgement — can be re-optimised now that actual demand per site can be measured rather than assumed.

## 1.2 Research question and scope

The core of the thesis is strategic: estimate waste generation per site from sensor and collection data, then locate containers optimally against that demand under both deterministic and uncertain formulations. Routing (VRP/IRP) and scheduling are extensions, activated only if operational data prove sufficient; the thesis stands without them. This scope was fixed at the proposal defence and is treated here as binding.

One boundary condition matters and is easy to get wrong: collection circuits serve containers inside and outside the urban study area in the same trip, and the depot itself lies outside it. Any routing analysis must model this explicitly. Clipping routes at the study-area border would fabricate distances and invalidate comparisons with real operations.

# 2. Data foundation

## 2.1 What exists

| Dataset | Content | Size | Confirmed semantics |
|---|---|---|---|
| Sensor readings CSV | Raw fill-level time series, 2020–2024 | 1,048,575 rows, 344 containers | Fill percentage; raw, unprocessed |
| Collection records CSV | Driver-recorded fills + trip data | 264,817 rows, 816 containers | 0/25/50/75/100 visual scale at collection; trip-level km and kg |
| Municipal GIS | Containers (464), BGRI 2021 census polygons (222), land use, buildings, boundary, CBD | file geodatabase | EPSG:3763 after harmonisation |
| Public operational sources | Depot, fleet, circuits, policy | — | Valorsul + IST dissertation (Lopes, 2014) |

The two CSVs share one 19-column schema. Their semantics were fixed by interview with the author and are recorded in the project's data dictionary; the key rulings are that `idrecolha` identifies a collection trip (not a container lift), that `Km totais` and `Peso total` are trip-level totals, and that negative fill readings are sensor errors to be removed.

## 2.2 Known defects and their consequences

| ID | Defect | Consequence |
|---|---|---|
| D1 | Sensor file truncated at exactly the Excel row limit (1,048,576); no re-export possible | The 344 sensor containers are an arbitrary subset of ≈800; coverage must be validated spatially, and the truncation disclosed as an inclusion criterion |
| D2 | `idrecolha` duplicates the fill value in 90.8 % of sensor rows | Sensor file carries no usable collection identifier; collection events must come from the driver file |
| D3 | Every sensor container's maximum reading is 82–84, never higher | The stated 0–100 % range is not what the data show; treat 82–84 as effective full, or rescale; unresolved with the data provider |
| D4 | 96,832 negative readings (9.2 %), in two distinct patterns (−1…−9 and −89…−116) | Removed as errors per author ruling; counts must be reported in the thesis |
| D5 | Trip weight cannot be attributed to single containers | Container-level demand in kg cannot come directly from `Peso total`; it must be constructed (Section 4.2) |
| D6 | Only 193 of the 464 GIS-mapped containers appear in the sensor data; 151 sensor containers have no GIS match | Spatial joins will silently lose containers; the match key set must be reconciled before modelling |
| D7 | BGRI polygons sum to 37,548 residents against a 2021 municipal population near 21,000 | The census layer likely contains duplicated or out-of-area subsections; must be resolved before population-weighted demand is computed |

Defects D1–D4 were previously registered; D6 and D7 were found during the mapping work for this report and are new.

## 2.3 Spatial picture

Three maps accompany this report. The container network map shows the 464 mapped sites concentrated in the urban core, with glass containers dispersed furthest into the periphery. The population map overlays the BGRI 2021 subsections; the visual correspondence between population mass and container density is good in the centre and weaker in the northern parishes. The sensor-coverage map is the important one: sensor-equipped containers cluster in and around the urban core, which is consistent with the pilot's stated design but means peripheral demand will be estimated, not measured.

# 3. The proposed methodology, explained

The proposed chain is: stepwise regression for waste-demand estimation; a deterministic capacitated p-median as baseline; Monte Carlo scenario generation for demand uncertainty; a stochastic capacitated p-median as the main model; a robust variant as benchmark. This section explains each piece in plain terms before Section 4 audits them.

## 3.1 Demand estimation by regression

The idea: waste generated at a container site should be predictable from its surroundings: how many people live nearby, what the land around it is used for. Fit a linear model of demand on such covariates, and the fitted equation can estimate demand anywhere, including candidate sites that hold no container today. That transferability is the whole point: the optimisation needs demand estimates for locations that have no measurement history.

*Stepwise* regression automates covariate selection: variables enter or leave the model one at a time according to a criterion (typically AIC or a p-value threshold) until no move improves it. It is convenient and widely taught, but it has known pathologies (inflated apparent significance, instability of the selected set under resampling), and juries know them too. Section 4.1 returns to this.

## 3.2 Monte Carlo scenario generation

Demand is not one number per site; it varies by season, weekday and behaviour. The Monte Carlo step acknowledges this by drawing many plausible demand vectors, called scenarios, from the distributions fitted to the data (for example, from the regression's predictive distribution, or from empirical residuals). Each scenario is one possible future. A set of a few hundred scenarios, each with a probability weight, becomes the input to the stochastic optimisation.

## 3.3 The p-median family

The p-median problem places p facilities among m candidate sites to minimise the total demand-weighted distance between users and their nearest open facility. It is the standard model for locating recycling drop-off points because its objective — accessibility — is exactly what determines whether citizens use the containers at all.

The deterministic capacitated formulation used as the baseline is:

[EQ-1: min Σᵢ Σⱼ wᵢ dᵢⱼ xᵢⱼ]

subject to

[EQ-2: Σⱼ xᵢⱼ = 1 for every demand point i]
[EQ-3: xᵢⱼ ≤ yⱼ for every i, j]
[EQ-4: Σⱼ yⱼ = p]
[EQ-5: Σᵢ wᵢ xᵢⱼ ≤ Qⱼ yⱼ for every site j]
[EQ-6: xᵢⱼ, yⱼ ∈ {0,1}]

Here wᵢ is the demand at point i, dᵢⱼ the distance from i to candidate site j, yⱼ = 1 if site j is opened, and xᵢⱼ = 1 if demand point i is assigned to site j. Constraint EQ-2 forces every demand point to be served; EQ-3 forbids assignment to closed sites; EQ-4 fixes the number of open sites; EQ-5 caps each site's load at its container capacity Qⱼ.

The stochastic version replaces the single demand vector with the scenario set from Section 3.2. Locations are first-stage decisions, fixed before demand is known, while assignments become second-stage decisions that may differ per scenario:

[EQ-7: min Σₛ pₛ Σᵢ Σⱼ wᵢˢ dᵢⱼ xᵢⱼˢ, with yⱼ shared across scenarios]

The solution is a single set of locations that performs well on average across all scenarios, rather than optimally for one guess. Standard diagnostics, the value of the stochastic solution (VSS) and the expected value of perfect information (EVPI), quantify whether the added machinery bought anything; a thesis should report both.

A robust variant replaces the probability-weighted average with protection against worst cases within an uncertainty set. It answers a different question ("how bad can it get" rather than "what is best on average") and serves as a benchmark on the same scenario data.

## 3.4 Why this chain is reasonable

The architecture (measure, model demand, locate deterministically, then under uncertainty) is coherent and matches how the location literature actually progressed. The p-median choice is conservative in the best sense: fifty years of theory, exact solvability at this instance size, and an objective a jury understands. The stochastic extension is where the scientific contribution lives, because it uses precisely the information sensors add: the per-site variability of waste arrival, which fixed-schedule planning has never been able to observe.

# 4. Audit findings

## 4.1 The regression, as currently fitted, has failed — and the failure is informative

The current model regresses log-transformed mean daily kilograms per container (N = 452) on buffered population and land-use shares. The output is unambiguous: R² = 0.013, adjusted R² below zero, no individually significant predictor, and an overall F-test p-value of 0.95. Multicollinearity is ruled out (all VIF ≈ 1.0). The predictors are simply unrelated, in cross-section, to the response.

Three causes, all fixable:

**The response variable is built on unattributable weights.** Mean kg/day per container cannot be derived from `Peso total`, which is a trip total across ~80 containers (D5). If the response was constructed by dividing trip weights across containers, it contains mostly allocation noise, and no spatial covariate will ever explain it.

**The unit of analysis discards the signal.** A cross-sectional model averages away exactly the variation (weekday, season, events) that drives waste generation. The regression's own documentation concedes this in its interpretation section. The data are a panel: 344 containers × up to four years of readings. Modelling at container-day level with temporal covariates is the natural specification, with the static spatial variables entering as container-level effects.

**One covariate is suspicious on its face.** The population coefficient of −6.4 × 10⁻⁷ with a standard error three times larger suggests a units or construction error in `Pop_100m`; a 100 m buffer population should be a number in the tens to hundreds, and its coefficient should not be nine orders of magnitude below the intercept.

The repair uses the thesis's own instrument. Sensor readings give fill level over time per container; the slope between collections is a fill *rate*. Multiplied by container volume and a fraction-specific bulk density, and calibrated so that summed container masses match the trip weigh-ins at CTRO (a mass-balance constraint the data support), this yields a defensible container-level demand series: measured, not allocated. The regression then has a real response, and its purpose sharpens: transfer measured demand to unmeasured locations.

On stepwise selection itself: use it, if at all, only as a screening step. Report an information-criterion path or a LASSO fit with cross-validation alongside, and validate on held-out containers. A jury member who asks "why should we trust stepwise p-values?" must receive a better answer than convention.

## 4.2 The demand indicator deserves to be the thesis's centrepiece, not a preprocessing step

The construction in 4.1, from sensor fill rates through bulk density to mass-balance calibration against weighbridge totals, is itself a contribution: it is precisely the "assessment of driver-based vs sensor-based fill information" chapter promised in the proposal, and it produces the demand input every later model needs. Treating it as a first-class chapter both strengthens the thesis narrative and de-risks the timeline: it is publishable even if the stochastic optimisation runs long.

The driver records enable the comparison directly: the five-point driver scale and the sensor reading exist for the same containers at collection moments. Agreement analysis (confusion matrices, systematic bias by fraction and area type) answers a question the 2014 operational literature explicitly flagged, fill-level uncertainty, with data that did not exist then.

## 4.3 The optimisation is sound in design and unusable in implementation — rebuild the instance, keep the formulation

The existing Mosel model is a correct-in-structure capacitated p-median with compatibility constraints. It is also a toy: ten invented population centres, eight invented sites, Euclidean distances on arbitrary coordinates, fabricated generation rates, and a bin-type set that includes METALICO, a type the municipal data explicitly mark "do not use". Nothing computed from it can appear in the thesis.

What must change for the real instance:

- **Demand points**: BGRI subsection centroids (after resolving D7) or building centroids aggregated to a walkable grid — not ten points.
- **Candidate sites**: the 464 mapped locations plus, if the thesis wants relocation freedom, a candidate grid along the road network.
- **Distances**: network distances (walking for the citizen-to-container objective), not Euclidean. The road network is absent from the GIS and must be sourced from OpenStreetMap.
- **Units**: demand and capacity in the same currency (kg/week or L/week per fraction), with capacity derated by the observed effective-full ceiling (D3).
- **Scale**: with ~200 demand points, ~500 sites and three fractions, the MIP has on the order of 3 × 10⁵ binaries — well within Xpress's reach with standard tightening (closest-assignment cuts, variable fixing by distance radius).

Two benchmarking additions cost little and buy jury credibility: solve the uncapacitated p-median as a bound, and compare against the current layout (the "do nothing" solution) so every improvement claim has a baseline.

## 4.4 The stochastic model is the right contribution — if its inputs are honest

Scenario-based two-stage stochastic programming is the standard, defensible way to inject demand uncertainty into location, and the sensor data genuinely support it: per-container demand distributions are observable, including their seasonality. Three requirements keep it honest:

- **Scenario provenance**: scenarios must come from the fitted demand model's uncertainty (parameter + residual), not from arbitrary ±X % perturbations. Monte Carlo is the sampler, not the model.
- **Stability**: report in-sample and out-of-sample stability of the solution as scenario count grows (sample average approximation practice), so the chosen scenario count is a result, not a guess.
- **Value metrics**: report VSS and EVPI. If VSS is near zero, say so — that is a finding about this system, not a failure of the thesis.

The robust variant is optional; if kept, a budget-of-uncertainty (Γ-robust) formulation on the same scenario statistics is the cleanest benchmark and requires no new data.

## 4.5 Residual data risks

D1 (truncation) is permanent: the thesis must state the 344-container subset as an inclusion criterion and check its spatial balance. D3 (the 82–84 ceiling) needs one email to the sensor provider; failing that, rescaling to per-container maxima is defensible and must be documented. D6 (GIS/sensor mismatch) and D7 (census overcount) are reconciliation tasks that block the real optimisation instance and should be closed first.

## 4.6 Verdict

The methodology chain — demand estimation, deterministic baseline, stochastic main model — is appropriate, standard, and defensible, and no stronger alternative is available that the data would support. The current executions of its first and third stages are not usable: the regression must be re-specified at container-day level on a sensor-derived response, and the optimisation must be re-instantiated on real geography. Neither repair changes the thesis's architecture; both are scoped, mechanical, and within reach of the data in hand. The single scientific risk that remains is D3: until the fill-level ceiling is explained, every quantity derived from sensor readings carries a calibration caveat.

# 5. Conclusion

The thesis is in better shape than its current artefacts suggest. Its architecture is sound and its data, defects and all, are sufficient for the core scope. The operational unknowns that seemed to block the routing extension are now documented from public sources. What stands between the present state and a defensible thesis is not a redesign but two rebuilds: a demand model that uses the sensors as its response rather than decoration, and an optimisation instance built on the real map. The audit found nothing that requires new data collection for the core scope, and one question (the sensor ceiling) that requires a single answer from the data provider.

# 6. Recommendations

| # | Priority | Action |
|---|---|---|
| 1 | Critical | Rebuild the demand variable from sensor fill rates with mass-balance calibration against CTRO weigh-ins |
| 2 | Critical | Re-specify the regression at container-day level with temporal covariates; validate on held-out containers |
| 3 | Critical | Reconcile container ID sets across sensor, driver and GIS data (D6) before any spatial modelling |
| 4 | Critical | Resolve the 82–84 ceiling with the provider; otherwise rescale and document (D3) |
| 5 | High | Resolve the BGRI population overcount (D7); recompute demand weights |
| 6 | High | Rebuild the p-median instance on real geography with OSM network distances |
| 7 | High | Add the current layout as the baseline alternative in all optimisation comparisons |
| 8 | High | Implement SAA stability checks, VSS and EVPI for the stochastic model |
| 9 | Medium | Replace pure stepwise selection with an information-criterion or LASSO path plus holdout validation |
| 10 | Medium | Write the driver-vs-sensor agreement analysis as a first-class chapter |
| 11 | Medium | Keep routing conditional; if activated, model boundary-crossing circuits from CTRO explicitly |

# References

- Daskin, M. S. (2013). *Network and Discrete Location: Models, Algorithms, and Applications* (2nd ed.). Wiley.
- Hakimi, S. L. (1964). Optimum locations of switching centers and the absolute centers and medians of a graph. *Operations Research*, 12(3), 450–459.
- Birge, J. R., & Louveaux, F. (2011). *Introduction to Stochastic Programming* (2nd ed.). Springer.
- Lopes, D. M. T. (2014). *Otimização da recolha seletiva na Valorsul: estudo de cenários alternativos*. MSc dissertation, Instituto Superior Técnico, Universidade de Lisboa.
- Valorsul, S.A. Recolha seletiva — áreas de negócio. valorsul.pt (accessed 2026-08-09).
- Valorsul, S.A. Instalações — CTRO. valorsul.pt/pt/contactos/instalacoes (accessed 2026-08-09).
- INE (2021). Base Geográfica de Referenciação de Informação (BGRI), Censos 2021.
- Author's thesis project document, proposal, defence materials and Rio Maior field survey (project archive, 2025–2026).
