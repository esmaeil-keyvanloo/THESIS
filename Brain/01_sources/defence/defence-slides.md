---
name: defence-slides
title: defence powerpoint_final-esmaeil keyvanloo
type: source
category: defence
source_file: DATA/DOCUMENT/defence powerpoint_final-esmaeil keyvanloo.pptx
source_sha256: 2c15715bd9b911c8c1d3fa3399c9644ba480359ee680f6fcd8f2cc106fab0b53
source_bytes: 6085863
ingested: 2026-08-09
words: 1743
verbatim: true
---

> Faithful conversion of `DATA/DOCUMENT/defence powerpoint_final-esmaeil keyvanloo.pptx`. Do not edit — edit the source and re-run the ingest.

## Slide 1

**PHD THESIS PROJECT  ·  PHD PROGRAM IN TRANSPORTATION SYSTEMS**

- Sensor-based Recyclables Collection Planning
- Collection Planning
- Planeamento de Recolha de Resíduos Recicláveis com Informação de Sensores
- Esmaeil Keyvanloo
Supervisor: Professor João Fonseca Bigotte
University of Coimbra  ·  Coimbra, July 28, 2026

## Slide 2

**PRESENTATION OUTLINE**

- What We Will Cover Today
- 1
- WSmartRoute+ Project
- 2
- Background & Rationale
- 3
- Research  Gap
- 4
- Research Question & Objectives
- 5
- Case Study: Rio Maior, Portugal
- 7
- Operational Database & Waste Generation  Modelling
- 8
- Waste generation Modelling & Regression Analysis
- 9
- Deterministic Facility Location Model
- 10
- WHY STOCHASTIC OPTIMISATION? From Fixed Demand to Robust Strategic Planning
- 11
- CONCLUSION
- 1
- PROPOSED METHODOLOGY
- 6

## Slide 3

**GOAL   Develop intelligent and sustainable municipal waste collection systems.**

- IoT
- Sensors
- →
- Demand
- Forecasting
- →
- Facility
- Location
- →
- Vehicle
- Routing
- →
- Decision
- Support
- MY PhD FOCUS
- Strategic Infrastructure Planning
- Waste Demand Modelling   |   Deterministic Facility Location   |   Stochastic Facility Location
- My research contributes is limited the strategic planning level of the WSmartRoute.
- 1.WSmartRoute+ Project
- FCT Research Project

## Slide 4

**WHY IT MATTERS**

- 2. Background & Rationale
- Traditional planning (blind collection)
- Fixed collection schedules
- No demand estimation
- ignores fill levels,
- Fails to capture spatial and temporal demand variability.
- Reality of waste generation
- Dynamic and uncertain
- Spatially and temporally variable
- Requires data-driven demand estimation
- Key Takeaway:
- .
- Static planning is insufficient. Data-driven demand estimation enables robust infrastructure planning.

## Slide 5

**From Reactive Waste Collection to Predictive Infrastructure Planning**

- Research Streams Commonly Studied Separately
- +
- Proposed integrated framework
- This research integrates three sequential components into a unified decision-support framework:
- →
- Stochastic Facility Location
- Waste Generation  Modeling
- Facility-location planning
- Demand uncertainty
- +
- →
- Deterministic Facility Location
- Demand Estimation
- 3.RESEARCH GAP
- The Core Research Gap
- Fixed collection schedules
- Deterministic demand assumption
- Reactive ("blind") collection
- Current Planning Limitations
- Key Takeaway:
- Existing studies typically investigate waste demand modelling, facility location, and demand uncertainty as separate research problems. Few study integrate these components into a unified decision-support framework.
- This research proposes a sequential decision-support framework that integrates demand estimation with deterministic and stochastic facility-location models to support robust strategic municipal waste infrastructure planning under demand uncertainty

## Slide 6

**4. MAIN RESEARCH QUESTION**

- RESEARCH OBJECTIVES
- 01
- 02
- 03
- 04
- “How can waste generation modelling be integrated with deterministic and stochastic p-median facility location models to improve strategic municipal solid waste container planning under demand uncertainty?”
- System Characterisation
- Characterise the existing municipal solid waste collection system in Rio Maior and develop the spatial and operational database.
- Waste Generation Modelling
- Develop and validate statistical models for estimating municipal solid waste generation.
- Deterministic Facility Location
- Develop a deterministic p-median model to identify baseline strategic container locations.
- Stochastic Facility Location
- Extend the deterministic model to explicitly incorporate demand uncertainty.
- Overall Goal: Develop a robust and transferable framework for strategic municipal waste planning under demand uncertainty

## Slide 7

**5. Case Study: Rio Maior, Portugal**

- Municipal Profile
- Area: 272 km², Santarém District, Central Portugal
- Population: 21,004  inhabitants (2021Census (
- Recycling Infrastructure: different  ecoponto container typologies
- Company Valorsul responsible all management system
- Operational database (2020–2024): GIS layers, sensor records, driver observations and collection data
- Operational Challenges
- Fixed collection schedules independent of actual fill levels ("blind collection")
- Partial sensor coverage with hybrid monitoring (IoT + driver observations)
- Seasonal variation  from and summer activity
- Limited financial  and technical resources - representative of medium-sized EU municipalities
- Key Takeaway:
- These characteristic make Rio Maior a representative real-world case study for developing and validating data-driven methods for strategic municipal waste infrastructure planning.

## Slide 8

**6 · PROPOSED METHODOLOGY**

- A Sequential, Data-Driven Research Framework
- 1. System Characterisation& Database Development
- Input• Historical collection records• GIS layers• Demographic data• Land use dataOutputContainer-level database
- 2. Waste GenerationModelling
- • Stepwise regression
- OutputEstimated waste generation
- 3. DeterministicFacility Location
- • Deterministic p-median• Determine optimal facility locations
- OutputBaseline facility location solution
- 4. StochasticFacility Location
- • Demand uncertainty• Stochastic p-median
- Outputmore Robust strategic facility-location decisions
- KEY MESSAGE: From data to robust strategic infrastructure planning under demand uncertainty.
- Each stage provides the input for the next, creating an integrated decision-support framework for strategic municipal waste infrastructure planning.

## Slide 9

**7.Operational Database**

- Historical Collection
- records
- GIS spatial data
- Demographics information
- Land-use
- characteristics
- Integrated analytical database
- 2020–2024 · Bin-event → Bin-day → Bin-level
- Stepwise Multiple
- Regression
- Stepwise variable selection
- Candidate Models
- Strict / Borderline
- / Best-AIC
- Selected candidate models
- Waste Generation Modelling
- Dependent variable:
- Average daily waste per container
- Candidate predictors:
- Population · Distance to CBD · Land-use proportions
- Model evaluation criteria:
- R2 ,Adjusted R2
- AIC-BIC
- VIF(multicollinearity)
- Residual diagnostics ( normality , Homoscedasticity)
- Initial Full OLS
- R² = 0.013
- low explanatory power
- Model refinement required
- Initial specification not adequate
- Data Sources
- Regression Modeling Workflow

## Slide 10

**8.WASTE GENERATION MODELLING**

- From Full OLS to a Parsimonious Model
- Full OLS Model
- All  candidate explanatory variables
- R² = 0.013
- →
- Stepwise Regression
- Systematic variable
- selection procedure
- →
- Alternative Candidate Models
- Strict ·
- Borderline
- Best-AIC
- →
- Final Selected Model
- Strict Stepwise Model
- (most parsimonious)
- Stepwise Multiple Regression Model
- Regression Equation:  log(1+Y) = 5.186 + 0.000477 × Population_Buffer + 0.000212 × Distance_to_CBD
- R²
- 0.074
- Maximum VIF
- 1.081 (no multicollinearity)
- Breusch-Pagan p
- 0.323 (No evidence of heteroskedasticity )
- Key Findings:
- Population within the 100 m buffer was significant.
- Distance to the CBD was significant.
- Demand Equation:  Y = exp(5.186 + 0.000477 × Population_Buffer + 0.000212 × Distance_to_CBD_m) - 1
- objective of this model is demand estimation rather than behavioural prediction
- Estimated demand for 452 containers.
- Average estimated demand = 341.24 kg/day.
- Compared using statistical and diagnostic criteria

## Slide 11

**✓ Residuals are approximately normally distributed in the central region.**

- ✓ Moderate deviations appear in the tails.
- ✓ Normality assumption is reasonably satisfied.
- ✓ Overall, the residual diagnostics support the adequacy of the regression model for estimate waste genaration
- ✓ Residuals randomly scattered around zero
- ✓ No systematic pattern detected
- ✓ Approximately constant variance
- ✓ Breusch–Pagantest : p = 0.323 (> 0.05)
- Conclusion: Homoscedasticity assumption is satisfied.

## Slide 12

**9.Deterministic Facility Location Model**

- Mathematical Formulation
- Objective: Minimize total weighted distance
- between demand points and selected sites
- (facility location)
- Constraints: Exactly p facilities open; each demand point assigned once; binary decision variables.
- Implementation
- Software: FICO Xpress Optimizer, Mosel
- Method: Dual simplex
- Test Scenario Results
- 3 Facilities Selected
- Sites 1, 6, and 7 from 8 candidates
- 10
- population centers
- (Demand Points)
- 2,770 Residents
- Population covered
- 106.6 m
- Average service distance
- Key ASSUMPTION
- Waste demand is fixed and known throughout the planning horizon
- OUTPUT
- Baseline facility-location solution
- min Σᵢ Σⱼ wᵢ dᵢⱼ Xᵢⱼ
- The deterministic model generated a feasible baseline facility-location solution under fixed demand assumptions.
- This solution is integrated into the subsequent stochastic optimization model, where demand uncertainty is explicitly incorporated to support more robust strategic facility-location decisions.

## Slide 13

**Three optimal ecoponto locations (Sites 1, 6, and 7) were selected.**

- All population centres are assigned to the nearest selected facility.
- The solution minimizes the total demand-weighted travel distance while ensuring full service coverage.
- This deterministic solution provides the baseline facility-location configuration for the subsequent stochastic optimisation model.
- Assumption: fixed and known waste demand
- Deterministic Facility Location Results (FICO Xpress)
- The solution minimises the total demand-weighted travel distance while ensuring full service coverage.

## Slide 14

**10 · Why Stochastic Facility Location?**

- From Fixed Demand to Robust Strategic Planning
- DETERMINISTIC     p-MEDIAN
- • Fixed demand
- • Single demand estimate
- • Static assumptions
- Baseline solution
- REAL-WORLD CONDITIONS
- • Seasonal variation
- • Population dynamics
- • Tourism
- • Behavioural variability
- Dynamic & uncertain demand
- STOCHASTIC APPROACH
- • Explicit uncertainty
- • Robust optimisation
- • More robust facility-location decisions
- • More resilient infrastructure planning
- More robust strategic planning
- Fixed Demand
- ≠
- Real Municipal waste Generation
- KEY MESSAGE: Municipal waste demand is inherently uncertain. therefore, strategic facility-location decisions should explicitly account for uncertainty rather than relying solely on deterministic demand assumptions
- Current Approach
- Real-World Challenge
- Proposed Solution

## Slide 15

**11.CONCLUSION**

- Towards a Unified Framework for Municipal Solid Waste Infrastructure Planning
- RESEARCH CONTRIBUTION
- This research proposes a sequential, data-driven framework integrating waste demand modelling with deterministic and stochastic facility-location optimisation for strategic municipal recycling infrastructure planning under demand uncertainty.
- STEP 1
- Waste Demand Modelling
- • Demand estimated using stepwise regression
- • population with buffer area and CBD distance identified  as most significant predictors
- • demand estimates used as input for facility location
- STEP 2
- Deterministic Facility location
- • Deterministic p-median developed.
- • Generated a baseline facility –location configuration
- Provides a reliable baseline strategic  solution
- Minimize total weighted distance
- between demand points and selected sites under fixed demand
- STEP 3
- Stochastic Facility location
- • Explicitly incorporates demand uncertainly (seasonality , population dynamics, behaviour, tourism).• proposes a stochastic optimization framework
- objective is supports more robust facility -locations decision and supports more resilient infrastructure planning under real world condition
- Thank You for Your Attention
- Overall contribution: integration of waste demand estimation, deterministic optimization, and stochastic optimization into a unified decision –support framework for strategic municipal infrastructure planning
