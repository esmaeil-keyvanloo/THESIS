---
name: holistic-master-pipeline
title: 05_holistic_master_pipeline
type: source
category: discussions
source_file: DATA/my concerns and history of discussion with chat gpt/md/05_holistic_master_pipeline.md
source_sha256: 905cc985d9fa6b0ea8a8236c09f76a52a2b12e8c47322bce70d77d7bc5c51bac
source_bytes: 8810
ingested: 2026-08-09
words: 1167
verbatim: true
---

> Faithful copy of `DATA/my concerns and history of discussion with chat gpt/md/05_holistic_master_pipeline.md`. Do not edit.

# Claude Code Master Prompt --- Full PhD Pipeline

Act as the lead research-software engineer for a PhD project on smart
recyclable-waste collection in **Rio Maior, Portugal**.

Project: **"Analysis of Recyclables Waste Collection Infrastructure and
Operations: Application to a Portuguese Municipality"**

The final objective is a reproducible, modular decision-support pipeline
connecting real municipal data, demand modelling, forecasting,
stochastic facility location, inventory-routing and daily vehicle
routing.

**Do NOT start by coding isolated optimization models.**

First inspect all available files/code/data, establish the data model,
identify what work already exists, and preserve reproducible completed
analyses.

## Phase 1 --- Project & Data Audit

Inventory all available: - datasets, - scripts, - notebooks, - GIS
files, - regression outputs, - optimization outputs, - WSmart Route+
files, - documentation.

Create a data dictionary and identify stable keys, especially container
ID, timestamp, route/trip ID and waste stream.

Map available data into: 1. container/infrastructure data; 2. collection
event data; 3. bin-day data; 4. sensor fill-level data; 5. driver
observations; 6. collected quantities; 7. trip/route/GPS data; 8. fleet
data; 9. population; 10. land use; 11. road-network/spatial data.

Do not invent missing fields.

## Phase 2 --- Data Cleaning & Integration

Create a reproducible ETL pipeline:

**raw data → schema validation → duplicate/error removal → missing-data
handling → unit harmonization → temporal alignment → spatial joins →
bin-event dataset → bin-day dataset → bin-level analytical dataset**

Keep raw data immutable and log all transformations.

## Phase 3 --- Baseline System Characterization

Describe the current Rio Maior system before optimizing it.

Calculate where possible: - container distribution; - capacities; -
waste streams; - service frequency; - collected quantities; - fill-level
patterns; - travelled distance; - current routes; - vehicle use; -
overflow/underutilization indicators; - accessibility.

This becomes the baseline for all later comparisons.

## Phase 4 --- Waste-Generation Modelling

Reproduce the existing regression analysis first.

Use demographic, spatial, land-use and operational predictors where
actually available.

Report: - coefficients; - significance; - R²/adjusted R²; - residual
diagnostics; - multicollinearity; - predictive error; - limitations.

Do not hide weak model performance.

Then test justified alternative statistical/ML models.

The purpose is to estimate container-level demand and create inputs for
optimization.

## Phase 5 --- Fill-Level Modelling & Data Fusion

Compare: - IoT sensor measurements; - driver observations; - historical
servicing information.

Assess accuracy, missingness, noise and bias.

Develop state-estimation/data-fusion procedures where useful.

For containers without reliable sensors, build virtual-sensing /
forecasting models using appropriate statistical and ML approaches.

Generate: - predicted fill levels; - prediction intervals; - uncertainty
measures.

Use time-aware validation and prevent leakage.

## Phase 6 --- Stochastic Demand Representation

Convert forecasts into optimization-ready uncertainty representations.

Where supported by data: - fit suitable probability distributions; -
model temporal/seasonal effects; - generate Monte Carlo scenarios; -
construct/reduce scenario trees.

Clearly separate expected demand, forecast uncertainty and observed
demand.

## Phase 7 --- Strategic Optimization

Start with a reproducible deterministic p-median baseline.

Then extend where justified to: - capacitated p-median; - multi-material
formulation; - stochastic/robust p-median; - optional sensor-placement
decisions.

Objectives/constraints may include: - demand-weighted travel/access
distance; - container capacity; - number of facilities; - overflow
reliability; - accessibility; - spatial equity; - sensor budget.

Preserve and reproduce any existing p-median results before changing the
formulation.

## Phase 8 --- Tactical Inventory-Routing

Develop the hierarchy:

**IRP → SIRP → DIRP where data support it.**

The tactical model decides: - WHICH bins to service; - WHEN to service
them; - service frequency; - waste accumulation/inventory evolution.

Use predicted stochastic fill levels.

Include: - vehicle/container capacities; - operational cost; - overflow
penalty/risk; - depot/shift restrictions as available.

Implement rolling-horizon planning:

**forecast horizon → optimize → implement first-period decisions →
receive new information → update state → re-optimize**

## Phase 9 --- Operational Routing

Given the bins selected by the tactical layer, solve daily routing.

Implement: - CVRP for mandatory service sets; - PCVRP / priority-based
routing for selective service.

Priority may reflect: - current fill; - predicted fill; - overflow
probability; - service criticality; - equity.

Use **REAL ROAD-NETWORK distances/travel times** when available, not
arbitrary Euclidean distances.

Include realistic: - vehicle capacities; - depot; - shifts; -
street/access constraints; - time restrictions; - route stability if
data permit.

## Phase 10 --- Closed-Loop Operation

Integrate:

**new sensor/driver observations → state update → new forecast →
tactical re-optimization → daily route optimization → executed route →
operational feedback**

Strategic location decisions should update much less frequently than
tactical and operational decisions.

Planning hierarchy: - Strategic = long-term / periodic - Tactical =
weekly or multi-day - Operational = daily / near-real-time

## Phase 11 --- Performance Evaluation

Compare CURRENT vs OPTIMIZED systems consistently.

### Economic

-   total collection cost;
-   km/VKT;
-   labour/time;
-   fuel;
-   fleet utilization.

### Service

-   overflow incidents/probability;
-   unnecessary early collection;
-   missed service;
-   reliability.

### Environmental

-   fuel;
-   CO₂/emissions.

### Spatial

-   accessibility;
-   equity/service gaps.

### Forecasting

-   MAE/RMSE/sMAPE or appropriate metrics.

### Optimization under Uncertainty

-   VSS where meaningful;
-   EVPI where meaningful.

## Phase 12 --- Validation & Robustness

Use: - historical back-testing; - temporal hold-out validation; -
actual-route vs optimized-route comparison; - scenario analysis; -
sensitivity analysis; - stress tests for sensor failure/demand
variation; - computational runtime/scalability assessment.

Never claim target improvements as empirical results unless reproduced
from the actual data.

Label every numerical result as one of: - OBSERVED - MODEL OUTPUT -
SIMULATION - LITERATURE BENCHMARK - TARGET KPI

## Phase 13 --- Cost-Benefit Analysis

Where adequate cost data exist, compare current vs smart system using: -
capital cost; - sensor cost; - operating cost; - fuel/labour savings; -
avoided overflow/service costs; - environmental benefits.

Calculate appropriate indicators such as: - NPV; - BCR; - payback
period.

## Phase 14 --- Final Decision-Support Pipeline

Produce one modular system:

**DATA\
↓\
CLEANING\
↓\
BASELINE CHARACTERIZATION\
↓\
REGRESSION / DEMAND MODEL\
↓\
FILL-LEVEL FORECASTING\
↓\
UNCERTAINTY / SCENARIOS\
↓\
STOCHASTIC P-MEDIAN\
↓\
SIRP / DIRP\
↓\
CVRP / PCVRP\
↓\
REAL-WORLD VALIDATION\
↓\
KPI + COST-BENEFIT EVALUATION\
↓\
DECISION-SUPPORT OUTPUTS**

## Software Requirements

Use a clean modular Python architecture.

Suggested modules:

``` text
/data
/preprocessing
/eda
/regression
/forecasting
/uncertainty
/facility_location
/inventory_routing
/vehicle_routing
/evaluation
/gis
/dashboard
/tests
/config
/docs
```

Prefer configuration files over hard-coded parameters.

Every major model should expose: - inputs; - parameters; -
assumptions; - solver; - outputs; - validation; - diagnostics.

Generate: - reproducible tables; - maps; - charts; - KPI reports; -
model comparison tables; - machine-readable outputs.

Maintain full traceability from raw data to thesis result.

## First Action

Before implementing anything:

1.  inspect the repository/files;
2.  identify existing completed work;
3.  map every available dataset;
4.  identify missing dependencies/data;
5.  propose the final folder architecture;
6.  produce a dependency-aware implementation roadmap;
7.  classify tasks as:
    -   already completed,
    -   needs reproduction,
    -   needs improvement,
    -   not yet implemented.

Then proceed sequentially.

Do not rewrite working analyses unnecessarily.\
Do not fabricate unavailable data.\
Do not silently change the scientific methodology.\
Ask for clarification only when a genuinely required input cannot be
inferred from the files.
