# Claude Code Prompt 1 --- Thesis Architecture & Research Framework

You are supporting a PhD project titled:

**"Analysis of Recyclables Waste Collection Infrastructure and
Operations: Application to a Portuguese Municipality"**

Case study: **Rio Maior, Portugal**.

Your task is to establish the correct computational architecture of the
thesis before implementing individual models.

The research should be organized as an integrated hierarchical
decision-support framework:

## 1. Data / Analytics Layer

-   Operational collection records
-   Container locations/capacities
-   Waste quantities
-   Sensor fill-level measurements
-   Driver observations
-   Population, land use and GIS variables
-   Road network and fleet information
-   Historical routes

## 2. Demand / Forecasting Layer

-   Clean and aggregate raw data
-   Characterize waste generation at container level
-   Build statistical/regression baseline models
-   Forecast container fill levels
-   Quantify prediction uncertainty
-   Generate stochastic demand scenarios

## 3. Strategic Layer

-   Facility-location optimization
-   Deterministic → capacitated → stochastic p-median
-   Optimize container locations/capacities
-   Optionally optimize sensor placement
-   Consider accessibility, reliability, capacity and spatial equity

## 4. Tactical Layer

-   IRP/SIRP/DIRP
-   Determine which containers should be serviced and when
-   Model stochastic waste accumulation
-   Use rolling-horizon planning and overflow-risk control

## 5. Operational Layer

-   CVRP/PCVRP/dynamic routing
-   Determine daily executable routes
-   Prioritize containers using actual/predicted fill level and overflow
    risk
-   Respect vehicle capacity, shifts, depot and road constraints

## 6. Feedback Loop

-   New sensor/driver/operational data update state estimates
-   Reforecast demand
-   Re-run tactical and operational decisions
-   Periodically reconsider strategic decisions

## 7. Performance Evaluation

Compare current vs optimized system using cost, VKT, fuel/emissions,
overflow, vehicle utilization, reliability, accessibility and equity.

Design the codebase so every layer can run independently but also
connect through explicit input/output interfaces.

Before coding, create: - system architecture, - module structure, -
data-flow diagram, - dependency map, - expected inputs/outputs for every
stage.

Do not invent unavailable data or results. Clearly distinguish actual
results, simulations, literature values and target KPIs.
