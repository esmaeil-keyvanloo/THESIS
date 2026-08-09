---
name: thesis-overview
title: Overview of PhD thesis Optimizing Recycling Waste Collection
type: source
category: proposal
source_file: DATA/DOCUMENT/Overview of PhD thesis Optimizing Recycling Waste Collection.docx
source_sha256: 6a19e1026e38a869fa4677b4b2861332befd950080e220ff1ca93c789a5f5ab8
source_bytes: 44770
ingested: 2026-08-09
words: 5242
verbatim: true
---

> Faithful conversion of `DATA/DOCUMENT/Overview of PhD thesis Optimizing Recycling Waste Collection.docx`. Do not edit — edit the source and re-run the ingest.

Overview of PhD thesis: Optimizing Recycling Waste Collection

The focus of my PhD research is on developing efficient and sustainable strategies for the collection and transportation of recyclable waste- specifically paper, glass, and plastic. The primary goal is to optimize bin placement, volume allocation, and waste transportation logistics to minimize operational costs while ensuring adequate service coverage across population centers.

This research aims to address key challenges related to the design and efficiency of solid waste collection systems, including:

The placement and locating of bins to maximize accessibility and efficiency.

The capacity allocation of bins based on demand and waste generation rates.

The transportation routes and logistics for waste collection trucks.

By integrating advanced optimization techniques with real-world data, the project aspires to provide actionable solutions that balance cost-benefit (economic viability) with environmental sustainability. The ultimate goal is to design a system that enhances the collection and transportation of recyclable waste from bins to landfill sites or recycling facilities, ensuring optimal performance across various scenarios and conditions.

1. Waste Bins and Data Collection

Bin Types and Capacities:

The study focuses on three bin capacities: 2500, 3000, and 5000 liters, categorized into eight types: AMBI(2500 liters,paper, glass, plastic), EBLUE BEE(3000,5000 liters, paper, plastic), METALICO(3000 liters ,glass), MOXEA(5000 liters, paper , plastic), OVO(2500 liters, paper, glass, plastic), OVO S(2500 liters ,paper, plastic), TITAN(2500 liters, paper , plastic),and VRL(2500 liters ,paper , plastic)

Sensor Integration:

Both bins and collection trucks are equipped with sensors that continuously monitor fill levels.

Data Availability:

Data from 2021 to 2024 has been collected in two Excel files, containing daily fill-level recording. The data allows analysis across different timeframes (daily, weekly, monthly, seasonal, yearly) to detect waste generation patterns.

2. Population Distribution and Demand Analysis

Population as a Demand Metric:

Using Geographic Information Systems (GIS), population polygons were converted into geographic points, representing size and location (latitude and longitude).

Population Data:

Stored in the "AN" column under the "N_INDIVIDU" field of the population dataset,

land use types: residential, commercial, industrial, etc, each with distinct waste generation rates.

Objective:Correlate population and land use with waste generation to create precise demand profiles.

3. Research Objectives

To achieve objectives, multiple scenarios have been defined to evaluate the system under stochastic conditions. These scenarios incorporate uncertainties in waste generation rates and population growth, modeled using probabilistic distributions to account for risk and variability.

The main objective of the project is to evaluate and optimize the current placement of waste bins while considering various influencing factors. The research seeks to answer the following critical questions:

1. Location Efficiency: Are the current bin locations optimal for effective waste collection?

2. Capacity Sufficiency: Should additional bins be installed in other areas to meet growing demand?

3. Bin Designation: Should bins be resized or designated for specific waste types (e.g., paper, glass, plastic)?

4. Coverage Gaps: Where are the shortages of bins, and how can we improve coverage to meet population needs?

The study has revealed that some bins reach full capacity on a daily basis, indicating a potential need to either resize existing bins or install additional bins with varying capacities (2000, 3000, or 5000 liters). The overarching goal is to determine the most effective combination of bin placement, size, and type to meet the demands of different population centers.

4. Methodology

Optimization Techniques and Algorithms

Exact Methods:

Branch and Bound: Explore all potential solutions systematically.

Linear Programming (LP): Solve deterministic optimization problems.

Heuristic Methods:

Hill Climbing: Iteratively improve solutions.

Metaheuristic Algorithms:

Genetic Algorithms (GA): Efficiently explore large solution spaces.

Simulated Annealing: Avoid local optima by exploring global solutions.

Stochastic Modeling

p-Median Model:

Identify the best "p" bin locations to minimize collection costs and distances.

Uncertainty Incorporation:

Use probabilistic distributions to account for:

Seasonal variations in waste generation.

Population growth trends.

Variability in waste production based on land use.

5. Waste Generation Model for 100 Scenarios

Purpose of the Model

The waste generation model estimates the amount of waste (Wj) produced at specific locations (j) under varying conditions such as population size, land use type, and other influencing factors. It incorporates randomness to account for real-world uncertainties and evaluates these variations across 100 scenarios, each with a 1% probability.

The waste generated (Wj​) at location j is modeled as:

Wj=β1 ⋅ Pj + β2 ⋅ Yj+ Other Factors +εi

.

.

.

Wj=β100 ⋅ Pj + β101 ⋅ Yj+ Other Factors +εj

Where:

Wj​: Waste generated at location j.

Pj​: Population at location j.

Yj​: Land use type at location j (e.g., residential, commercial, industrial).

β1,β2 ​: Coefficients representing the relationship (impact) between population, land use, and waste generation.

Example: A larger β1 means population has a stronger influence on waste generation.

Other Factors: Includes variables like seasonal changes, income levels, special events, or holidays that impact waste.

ϵ : Error term accounting for randomness or model uncertainty, following a normal distribution N(μ,σ2)

100 Scenarios

Each scenario represents a unique set of conditions for waste generation. The scenarios capture different potential realities, such as:

Changes in population distribution (e.g., urban growth or migration).

Shifts in land use types (e.g., commercial expansion or increased industrial activity).

Seasonal or event-based waste fluctuations (e.g., festivals, holidays, or weekends).

Scenario Assumptions:

Equal Probability: Each scenario has a 1% probability of occurring.

Variability in Coefficients: Slight changes in β1 ​,β2​, and other factors simulate uncertainties in real-world conditions.

Random Error: A new random error (ϵ) is generated for each scenario.

Implementation Steps

Input Data:

Collect data on:

Population (Pj​) at each location.

Land use type (Yj​) for each location.

Define values for β1​, β2​, and standard deviation (σ) of ϵ.

Scenario Generation:

Create 100 scenarios by varying:

β1​,β2​: Adjust within realistic ranges.

  Base coefficients (β1,β2 ​) are chosen as starting points, e.g., β1=0.5,β2=0.3.

  Coefficients are perturbed slightly for each scenario:

β1(s)=β1+random normal noise,

β2(s) =β2+random normal noise

ϵ: For each scenario, generate ϵ\epsilonϵ values for all locations ϵ ∼N (μ, σ2)

Calculate Waste (Wj​):

For each location and scenario:

Wj(s) =β1(s) ⋅Pj+β2(s) ⋅Yj+ϵ(s)

Wj(s) ​: Waste at location j in scenario s.

β1(s) ,​ β2(s): Coefficients for scenario s.

ϵ(s): Random error for scenario s.

Probability Assignment:

Assign a probability of 1% (0.01) to each scenario.

Output Table:

Generate a table showing waste for all locations and scenarios.

6. Optimization Model

Objective Function:

Minimize total cost: Z=∑j∈ Markets ∑k ∈Sites ∑s ∈Scenarios Prob(s)⋅Djk⋅Wj⋅Xjks

Where:

 Djk​: Distance between population center j and bin k.

 Wj​: Waste generated at location j.

 Xjks​: Binary variable (1 if j is assigned to k in scenario s; otherwise, 0).

 Yk​: Binary variable (1 if bin k is selected; otherwise, 0).

 C: Fixed cost of using a bin.

 Prob(s): Probability of scenario s (e.g., weekdays, holidays).

Constraints:

Coverage: Each population center must be assigned to one bin for all scenarios:

∑k ∈ Bins Xjks =1   ∀ j,s

Capacity: Total waste assigned to a bin cannot exceed its capacity:

∑j ∈ MarketsWj ⋅Xjks ≤ Capacityk ⋅Yk    ∀ k,s

Bin Selection: Population centers can only be assigned to selected bins:

Xjks ≤ Yk           ∀ j,k,s

Reliability: Ensure a minimum reliability threshold:

∑ s ∈ Scenarios Prob(s)⋅Yk ≥ Smin

Selection Limit: Limit the number of selected bins:

∑ k ∈ Bins Yk ≤ Pmax

7. Uncertainty with Monte Carlo Simulation

Uncertainty: Probabilistic distributions are used to model uncertainties in waste generation rates and population growth, ensuring robust solutions under varying conditions. Techniques such as Monte Carlo Simulation will be utilized to evaluate risks and uncertainties.

To account for uncertainties (ε) in waste generation:

Wjsim = Wj+ε ,    ε∼ N(μ,σ2)

Simulated values (Wjsim ​) provide a range of predictions under varying scenarios, enhancing robustness.

XPRESS-MP Model for Optimizing Recycling Waste Collection in Rio Maior

Overview: The following provides a comprehensive optimization model for locating recycling waste bins in Rio Maior (Portugal), using FICO Xpress-MP with the Mosel modeling language. The model is formulated as a p-median location-allocation problem, extended to account for multiple waste categories (paper, plastic, glass) and container types/capacities. The goal is to select a fixed number of bin locations (p bins) and assign population-based demand points to these bins in order to minimize the total weighted distance that residents travel to dispose of recyclables​file-ya8q5nnelzzyqapoo8wju7. The model ensures that each demand point (derived from population centroids) is served by a bin, and that no bin’s capacity is exceeded (reflecting real-world cases where some bins currently reach full capacity daily​file-ya8q5nnelzzyqapoo8wju7). It also supports analysis under multiple scenarios (e.g. weekday vs. weekend waste generation) to ensure robust solutions under varying conditions.

Model Formulation and Assumptions

Sets and Indices:

Demand Points (i ∈ I): Locations (centroids) representing population clusters or areas where waste is generated. These are derived from GIS population polygons converted to points​file-ya8q5nnelzzyqapoo8wju7. Each demand point has an associated waste generation for each category (paper, glass, plastic).

Candidate Bin Sites (j ∈ J): Possible locations where recycling containers (bins) can be placed. This could include existing bin sites and/or potential new sites (e.g. street intersections, public facilities). Each site can host bins for one or more waste categories.

Waste Categories (c ∈ C): We consider three recyclables categories: Paper, Glass, and Plastic, as given in the project scope​file-ya8q5nnelzzyqapoo8wju7. Demand and bin capacity are tracked separately for each category, since bins are typically category-specific (you cannot mix different recyclables in one bin).

Container Types (t ∈ T): Different designs/sizes of recycling bins available. For Rio Maior, there are multiple bin types with varying capacities (e.g. 2500L, 3000L, 5000L) and designated usage​file-ya8q5nnelzzyqapoo8wju7. Examples include: “AMBI” (2500L, usable for paper/glass/plastic), “EBLUE” (3000L or 5000L, for paper/plastic), “METÁLICO” (3000L, for glass), “MOXEA” (5000L, for paper/plastic), “OVO” (2500L, for paper/glass/plastic), etc.​file-ya8q5nnelzzyqapoo8wju7. Each type t has a fixed capacity (volume in liters) and is only suitable for certain waste categories.

Scenarios (s ∈ S): Different waste generation scenarios to capture variability over time. For example, s=1 might represent a typical weekday and s=2 a weekend or holiday scenario with higher waste generation. Each scenario provides a different set of demand values for each point and category (e.g., higher waste volume on weekends). Scenarios can be assigned probabilities or weights if we want to optimize for expected performance.

Parameters:

demand<sub>i,c,s</sub>: Amount of waste (in liters or another unit) generated by demand point i for category c in scenario s. This could be derived from population and land use data​file-ya8q5nnelzzyqapoo8wju7​file-ya8q5nnelzzyqapoo8wju7, or from sensor-recorded fill levels over time. For example, if demand point i represents 100 people, and each generates 0.2 liters of plastic waste per day, then demand<sub>i,Plastic,weekday</sub> = 20 liters. Scenario variation might adjust these values (e.g., +20% on weekends).

distance<sub>i,j</sub>: Distance (or travel cost) from demand point i to candidate site j. This should be a weighted distance reflecting travel effort; for instance, it could be Euclidean distance or actual walking distance on the road network. We will minimize total weighted distance = distance × waste quantity, so this effectively means minimizing the “person-distance” or “waste-distance” traveled for disposal​file-ya8q5nnelzzyqapoo8wju7.

capacity<sub>t</sub>: The volume capacity of a bin of type t (in liters). For example, capacity(“AMBI”) = 2500 L, capacity(“METÁLICO”) = 3000 L, etc.​file-ya8q5nnelzzyqapoo8wju7. This is the maximum waste of the appropriate category that a single bin of this type can hold (likely between collections). The model will ensure no bin is assigned more waste than its capacity, addressing the issue of some bins overflowing daily​file-ya8q5nnelzzyqapoo8wju7.

p: The total number of bins to locate (across all categories). This is a fixed input reflecting, for example, budget or operational limits on how many bins can be deployed. The model uses a p-median style constraint to select exactly p bins out of all candidate options​file-ya8q5nnelzzyqapoo8wju7. (If needed, this could be turned into an inequality ≤p or a cost-minimizing formulation, but here we assume exactly p bins for simplicity.)

maxMetal, minType, etc.: Policy parameters for container type composition. For instance, maxMetal could limit how many metal containers (like “METÁLICO”) are used, if those are expensive or in limited supply. minTypeDiversity could require a mix of bin types (ensuring not all bins are of one type, for research or resilience reasons). These illustrate how additional constraints can enforce practical considerations like diversity of bin types or materials.

Decision Variables:

Y<sub>j,c,t</sub> ∈ {0,1}: Binary variable indicating if a bin of type t is installed at site j for waste category c. Y<sub>j,c,t</sub> = 1 means we place a bin at location j that serves category c and is of type t. Because each bin has a specific category, we effectively treat each category at a site as a separate facility option. Only one type per category per site will be chosen in the solution (ensured by constraints), meaning each site j can have at most one bin for category c (though it could host one for each of paper, glass, plastic if needed).

X<sub>i,j,c,s</sub> ∈ {0,1}: Binary variable indicating if demand point i in scenario s is assigned to the bin serving category c at site j. X<sub>i,j,c,s</sub> = 1 means that in scenario s, the waste of category c generated by demand i is disposed in the bin at j. For each demand and category, the model will choose one bin to assign to (ensuring coverage). Note: We allow the assignment to depend on scenario s, meaning the distribution of waste might adjust slightly under different scenarios if needed to avoid overloading a particular bin. In practice, residents likely use the same bin consistently; however, this flexibility in the model can represent, for example, some people using an alternate bin if their nearest one is over capacity on a high-demand day. If one wanted to enforce consistent assignment regardless of scenario, we could drop the index s on X (ensuring each demand point uses the same bin all the time). Here we include s for generality in handling variability.

Objective Function: Minimize the total weighted distance from demand points to assigned bins. Each demand assignment contributes distance[i,j] * demand[i,c,s] to the objective (distance multiplied by waste volume, effectively person-distance or waste-distance). Summing over all demands i, all categories c, and all scenarios s (optionally weighted by scenario probability) gives:

Minimize Z=∑s∈S∑i∈I∑c∈C∑j∈J(demandi,c,s)×(distancei,j)×Xi,j,c,s. \text{Minimize } Z = \sum_{s \in S} \sum_{i \in I} \sum_{c \in C} \sum_{j \in J} (\textit{demand}_{i,c,s}) \times (\textit{distance}_{i,j}) \times X_{i,j,c,s}.Minimize Z=∑s∈S​∑i∈I​∑c∈C​∑j∈J​(demandi,c,s​)×(distancei,j​)×Xi,j,c,s​.

If scenarios are given equal weight (or if we treat the sum as over a single combined planning horizon), this objective effectively minimizes the expected daily distance residents travel to recycle. If one scenario (e.g., weekend) is more frequent or important, weights/probabilities can be applied accordingly. The p-median formulation inherently tries to locate bins such that high-demand areas have a bin nearby, reducing the weighted distance cost​file-ya8q5nnelzzyqapoo8wju7.

Constraints: The model includes the following key constraints to ensure feasibility and enforce the problem requirements:

Demand Allocation (Coverage Constraint): Each demand point’s waste must be assigned to one open bin of the corresponding category in each scenario. For every demand point i, category c, and scenario s:∑j∈JXi,j,c,s=1,\sum_{j \in J} X_{i,j,c,s} = 1,∑j∈J​Xi,j,c,s​=1,meaning demand i’s category c waste is assigned to exactly one bin (one j). This ensures full coverage of all demand. (If for some reason a demand point had the option to not be served, a different constraint or objective term would handle unserved demand, but in our case we enforce full assignment.) If we had X without scenario index (consistent assignment), this constraint would be ∑jXi,j,c=1\sum_{j} X_{i,j,c} = 1∑j​Xi,j,c​=1.

p-Median Facility Count Constraint: Select exactly p bins in total.∑j∈J∑c∈C∑t∈TYj,c,t=p.\sum_{j \in J} \sum_{c \in C} \sum_{t \in T} Y_{j,c,t} = p.∑j∈J​∑c∈C​∑t∈T​Yj,c,t​=p.This ensures the solution uses a fixed number p of bins (the “medians”). Each Yj,c,tY_{j,c,t}Yj,c,t​ represents one bin. For example, if p=10p=10p=10, the model might choose 10 specific (site,category,type) combinations to open. (If desired, this could be an “at most p” constraint instead of equality, or we could associate a cost with each bin and let the model decide the optimal number. But the classic p-median fixes p.)

Assignment-to-Open Linking: Demand can only be assigned to a bin if that bin is opened. For each i, j, c, s:Xi,j,c,s≤∑t∈TYj,c,t.X_{i,j,c,s} \le \sum_{t \in T} Y_{j,c,t}.Xi,j,c,s​≤∑t∈T​Yj,c,t​.The right side ∑tYj,c,t\sum_{t} Y_{j,c,t}∑t​Yj,c,t​ is effectively a binary indicator (it will be 1 if a bin of any allowed type is placed at site j for category c, or 0 if none is placed). This constraint forces Xi,j,c,s=0X_{i,j,c,s} = 0Xi,j,c,s​=0 if no bin of category c is installed at j. In other words, demand cannot use a site that isn’t selected as a facility. Together with the demand allocation constraint, this also implies that for each category c, there must be at least one bin opened if there is any demand for that category (otherwise the left side for those demands could never sum to 1). In practice, since we have three waste categories, we must ensure ppp is large enough to place at least one bin for each category to cover all demands (e.g., p≥3p\ge 3p≥3 if each category needs coverage).

Capacity Constraints: Do not exceed bin capacities. For each bin (site j and category c chosen) and for each scenario s, the total assigned waste should not exceed that bin’s capacity. Given that a specific type t will be chosen if a bin is opened at j,c, we enforce:∑i∈Idemandi,c,s×Xi,j,c,s  ≤  ∑t∈T(capacityt×Yj,c,t),∀j∈J,  c∈C,  s∈S.\sum_{i \in I} \textit{demand}_{i,c,s} \times X_{i,j,c,s} \;\le\; \sum_{t \in T} (\textit{capacity}_t \times Y_{j,c,t}), \quad \forall j \in J,\; c \in C,\; s \in S.∑i∈I​demandi,c,s​×Xi,j,c,s​≤∑t∈T​(capacityt​×Yj,c,t​),∀j∈J,c∈C,s∈S.This says: if Yj,c,t=1Y_{j,c,t}=1Yj,c,t​=1 for some type t, the right side becomes capacity(t), and all demand assigned to that bin in scenario s must be less than or equal to that capacity. If no bin is open at (j,c), the right side is 0, and the constraint forces the assigned demand to 0 as well (which is already ensured by the linking constraint). We thus avoid overfilling any container in any scenario. Considering multiple scenarios means, for example, a weekend scenario with higher volumes could be the binding constraint that might push the model to choose a larger bin type or add another bin to distribute the load. This aligns with addressing daily overflow issues by resizing or adding bins​file-ya8q5nnelzzyqapoo8wju7. (If we assumed assignments are fixed across scenarios, this effectively ensures the bin capacity is enough for the worst-case scenario at that location. If assignments can vary by scenario, the model has more flexibility to respect capacity by rerouting some demand in high-demand scenarios.)

Container Type Constraints (Policy Constraints): These are optional constraints to enforce specific requirements or preferences regarding the mix of bin types:

Example: Limit on Metal Bins. If authorities want to limit the number of METÁLICO type bins (perhaps due to cost or availability of metal containers), we can impose:∑j,cYj,c,METAˊLICO≤MaxMetal.\sum_{j,c} Y_{j,c,\text{METÁLICO}} \le \textit{MaxMetal}.∑j,c​Yj,c,METAˊLICO​≤MaxMetal.Here MaxMetal is a given limit (e.g., at most 5 metal bins in total). This ensures the model doesn’t choose more than that number of the METÁLICO type.

Example: Diversity of Bin Types. To require a variety of bin designs (so the solution isn’t, say, all “OVO” type bins), one could add constraints such as:∑j,cYj,c,t≥1∀t∈Trequired,\sum_{j,c} Y_{j,c,t} \ge 1 \quad \forall t \in T_{\text{required}},∑j,c​Yj,c,t​≥1∀t∈Trequired​,meaning at least one bin of each required type t is used. This can be applied to each type or a subset of key types. Another approach to ensure diversity is to set upper and lower bounds on the count of each type (e.g., at most 50% of bins can be of any single type). These constraints can be adjusted to reflect procurement or strategic considerations.

Category Coverage Requirements: Although naturally each category with demand will be covered, we could explicitly require a minimum number of bins for each category if needed. For instance, to ensure at least 2 bins for glass if glass waste is heavy, etc. This would be: ∑j,tYj,Glass,t≥2\sum_{j,t} Y_{j,\text{Glass},t} \ge 2∑j,t​Yj,Glass,t​≥2, as an example.

The above formulation covers the core requirements: assignment, distance minimization, fixed number of bins, capacities, and type constraints. Next, we present the full Mosel model code incorporating these elements. The code is well-commented and organized into sections (data input, variable definitions, objective, constraints) for clarity.

Xpress-Mosel Implementation of the Model

Below is the XPRESS Mosel code for the optimization model. The code is structured into sections for easy understanding and future modifications. In a real setting, data (distances, demand values, etc.) would be read from data files or defined before solving. Here we show placeholders and structure; one can populate the sets/parameters with actual data from Rio Maior’s GIS and sensor records as needed.

mosel

CopyEdit

model WasteCollectionOptimization

uses "mmxprs"  ! Use the Xpress-MP optimizer

! =======================

! Data Declaration Section

! =======================

declarations

I = 1..N_DemandPoints        ! Set of demand points (indexed 1 to N_DemandPoints)

J = 1..N_CandidateSites      ! Set of candidate bin locations (1 to N_CandidateSites)

C = set of string            ! Set of waste categories, e.g., {"Paper","Glass","Plastic"}

T = set of string            ! Set of container types, e.g., {"AMBI","EBLUE","METALICO",...}

S = set of string            ! Set of scenarios, e.g., {"Weekday","Weekend"}

demand: array(S, I, C) of real        ! demand[s,i,c]: waste from demand point i of category c in scenario s

distance: array(I, J) of real         ! distance[i,j]: distance from demand point i to site j

capacity: array(T) of real            ! capacity[t]: volume capacity of bin type t

allowed: array(T, C) of boolean       ! allowed[t,c] = true if type t can be used for category c

p_bins: integer                       ! fixed number of bins to locate (p-median parameter)

maxMetal: integer                     ! (example) max number of METALICO type bins allowed

end-declarations

! Example of data initialization (in practice, read from file or data source)

initializations from MPSheet: "input_data.xlsx"  ! (Pseudo-code: assume data comes from an Excel or CSV)

demand as "DemandData"

distance as "DistanceMatrix"

capacity as "TypeCapacities"

allowed as "TypeCategoryAllowed"

p_bins as "NumberOfBins"

maxMetal as "MaxMetalBins"

end-initializations

! (If not reading from a file, one could alternatively assign values in-code.

!  For clarity, details of data loading are omitted here.)

! =======================

! Decision Variables

! =======================

declarations

X: array(S, I, J, C) of mpvar   ! X[s,i,j,c] = 1 if demand point i (category c) uses site j's bin in scenario s

Y: array(J, C, T) of mpvar      ! Y[j,c,t] = 1 if a bin of type t for category c is installed at site j

end-declarations

! Specify binary nature of variables

forall(s in S, i in I, j in J, c in C) X[s,i,j,c] is_binary

forall(j in J, c in C, t in T) Y[j,c,t] is_binary

! =======================

! Objective Function

! =======================

! Minimize total weighted distance (sum of distance * demand for all assignments across scenarios)

TotalDistance := sum(s in S, i in I, j in J, c in C) demand[s,i,c] * distance[i,j] * X[s,i,j,c]

minimize(TotalDistance)

! =======================

! Constraints

! =======================

! 1. Demand allocation: each demand point i's waste of category c in scenario s must be assigned to exactly one bin

forall(s in S, i in I, c in C) do

sum(j in J) X[s,i,j,c] = 1

end-do

! 2. p-median constraint: select exactly p_bins bins in total

sum(j in J, c in C, t in T) Y[j,c,t] = p_bins

! 3. Linking constraint: assignment only possible if a bin is open at that site for that category

forall(s in S, i in I, j in J, c in C) do

X[s,i,j,c] <= sum(t in T) Y[j,c,t]

! Note: sum(t in T) Y[j,c,t] will be 1 if any type bin for category c is installed at j, else 0.

end-do

! 4. One bin type per site-category: a site j can have at most one bin for category c

forall(j in J, c in C) do

sum(t in T) Y[j,c,t] <= 1

! prevents placing two different bin types for the same category at one site.

end-do

! 5. Capacity constraints: total assigned waste to a bin (j,c) cannot exceed its capacity in any scenario

forall(s in S, j in J, c in C) do

sum(i in I) demand[s,i,c] * X[s,i,j,c] <=

sum(t in T) capacity[t] * Y[j,c,t]

! If no bin at (j,c), Y sum = 0, so X must be 0 (already enforced by linking).

! If bin is open, the sum on RHS is the capacity of the chosen type.

end-do

! 6. Container type limitations (policy constraints)

! Example 6a: Limit on METALICO type bins

sum(j in J, c in C) Y[j,c,"METALICO"] <= maxMetal

! Example 6b: Ensure at least one bin of each major type (if desired for diversity)

! (Uncomment if needed)

!forall(t in T) do

!   sum(j in J, c in C) Y[j,c,t] >= 1

!end-do

! (Other constraints could be added similarly, e.g., minimum bins per category, etc.)

! =======================

! End of Model

! =======================

end-model

Notes on the code: The model uses the mmxprs module of Mosel (the Xpress Optimizer) to solve the MILP. The decision variables X and Y are declared as binary (is_binary). The objective TotalDistance aggregates distance times demand for every assignment. Constraints are added in a readable forall-do loop format, closely mirroring the mathematical formulation above. We included an explicit constraint (4) to ensure at most one bin type is chosen per site-category, which combined with the binary Y’s implicitly ensures Y[j,c,t] acts like a one-hot selection among types if a bin is placed at (j,c). The data initialization section is a placeholder – in practice, one would replace it with actual data reading (from a spreadsheet, database, or arrays defined in code). The parameter p_bins fixes the number of bins; if the problem is to decide the optimal number instead, one could remove that constraint and instead add a budget cost in the objective for each bin.

Suggestions for Further Extensions

This model can be extended or refined in several ways for academic and practical purposes:

Dynamic or Multi-Period Extension: Incorporate a time horizon with multiple periods rather than independent scenarios. For example, model each day of the week or month explicitly, with variables for whether a bin is used each period. This would allow optimizing bin placement and possibly collection schedules simultaneously. A true multi-period extension could also consider reallocation or expansion over time (where bins can be added in future periods if needed, subject to an investment budget).

Robust Optimization / Scenario Weights: In the current multi-scenario approach, we ensure feasibility under all scenarios and minimize a weighted sum of distances. One could instead optimize a worst-case scenario (minimize the maximum distance or ensure a certain level of service in the worst case), or use probabilistic constraints (e.g., ensure capacity is not exceeded in 95% of scenarios). This would involve different objective formulations or additional constraints. For instance, a maximin objective could replace the sum in the objective with a variable representing the worst-case cost, or chance constraints could be linearized for capacity overflow probability.

Cost Considerations and Multi-Objective: The model currently minimizes distance (a proxy for user convenience or operational efficiency). In practice, there may be other objectives, such as minimizing the cost of bins and collections or maximizing recycling rates. An extended model could include a cost term (each bin type t might have a fixed installation cost, and perhaps operating cost if larger bins are costlier to service)​file-ya8q5nnelzzyqapoo8wju7. This leads to a multi-objective optimization: one objective could be cost, another distance or service level. Techniques like weighted sum or Pareto optimization could be applied, or simply incorporate cost as an additional term in the single objective (with an appropriate weight). For example, one could add + sum(j,c,t) Cost[t] * Y[j,c,t] to the objective if data on bin costs is available.

Routing and Logistics Integration: Ultimately, the project aims to also optimize transportation routes and logistics for waste collection trucks​file-ya8q5nnelzzyqapoo8wju7. A comprehensive extension would integrate this location model with a vehicle routing model – effectively a Location-Routing Problem (LRP). After deciding bin locations, one could use the model’s output to plan collection routes, or more ambitiously, include routing decisions in the optimization (though this becomes a much larger combinatorial problem). For example, adding variables for vehicle routes and linking them to where bins are placed and how full they get. Due to complexity, a common approach is a two-stage solution (first locate bins, then optimize routes). However, iterative or combined optimization can yield better overall results.

Heuristics and Large-Scale Solving: If the instance (number of demand points and candidate sites) is very large (which can happen if using fine-grained population data), the exact MILP might become computationally intensive. The model could be used in combination with heuristic or metaheuristic algorithms​file-ya8q5nnelzzyqapoo8wju7. For example, one might use the Mosel model as a solver inside a Genetic Algorithm or Simulated Annealing that searches over possible bin configurations​file-ya8q5nnelzzyqapoo8wju7. Another approach is to apply a clustering heuristic to reduce the number of candidate sites (e.g., pre-select a set of promising locations via a k-means clustering of demand points, then run the MILP). The Xpress solver is quite powerful with Branch-and-Bound and can handle moderate sizes, but it’s wise to consider heuristics for a very large-scale city-wide problem.

Enriching the Demand Model: The demand input can be improved by using the waste generation model developed in the research​file-ya8q5nnelzzyqapoo8wju7​file-ya8q5nnelzzyqapoo8wju7. Instead of static demand values, one could integrate the regression model Wj=β1Pj+β2Yj+…+ϵjW_j = \beta_1 P_j + \beta_2 Y_j + \ldots + \epsilon_jWj​=β1​Pj​+β2​Yj​+…+ϵj​ into scenario generation. For example, generate multiple scenarios by sampling from this model (as the thesis does with 100 scenarios​file-ya8q5nnelzzyqapoo8wju7) and solve the location model for each or in a robust fashion. This helps ensure the solution is tailored to the realistic variability in waste generation (population, land use, seasonality, etc.).

Detailed Constraints: Additional practical constraints can be added as needed. For instance, there might be a maximum service distance for any demand (no one should have to walk more than, say, 500 meters to a recycling bin for convenience – this could be a constraint Xi,j,c=0X_{i,j,c}=0Xi,j,c​=0 if distance[i,j] > 500m for example). Or one could enforce equity constraints such that each neighborhood gets a fair share of bins relative to population, etc. These would translate to linear constraints in the model based on policy goals.

Result Analysis and Iteration: The model’s output (which bins to place and assignments) can be analyzed and then fed back into GIS for visualization. One extension is to iterate between the model and real-world considerations: e.g., remove or add candidate sites based on unmodeled factors (like availability of physical space, community acceptance), or run the model separately for each waste category if needed and then combine results. The modular structure of the Mosel code makes it relatively straightforward to adjust the input data or constraints and re-run various scenarios and what-if analyses.

By implementing and iterating on this model, the PhD research can evaluate questions of location efficiency, capacity sufficiency, and bin designation​file-ya8q5nnelzzyqapoo8wju7 with a rigorous optimization approach. The model is flexible to accommodate new data or constraints, and it provides a foundation for developing decision-support tools for the municipality (potentially linking with sensor data for dynamic optimization in the future). Overall, this p-median based optimization framework helps identify the best bin placement, sizes, and allocations to improve Rio Maior’s recyclables collection system in both typical and peak scenarios, balancing operational efficiency with service accessibility​file-ya8q5nnelzzyqapoo8wju7​file-ya8q5nnelzzyqapoo8wju7.

Sources:

PhD Thesis Overview – Optimizing Recycling Waste Collection in Rio Maior: Provided context on waste categories, bin types/capacities, and scenario considerations​file-ya8q5nnelzzyqapoo8wju7​file-ya8q5nnelzzyqapoo8wju7.

P-Median Model: Described as the approach to find the best p locations minimizing collection distance​file-ya8q5nnelzzyqapoo8wju7, which underpins the model’s objective and structure.

Research Objectives: Highlighted the need to evaluate bin placement efficiency, capacity, and coverage gaps​file-ya8q5nnelzzyqapoo8wju7, directly addressed by this model’s constraints and possible extensions.
