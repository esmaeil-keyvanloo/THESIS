---
name: interview-questions-draft
title: interview quetion
type: source
category: discussions
source_file: DATA/my concerns and history of discussion with chat gpt/doc/interview quetion.docx
source_sha256: e8b0d057726799a118e37faf90efb9ed3df4984f4faf89eff9e445fc729d44ac
source_bytes: 22258
ingested: 2026-08-09
words: 1800
verbatim: true
---

> Faithful conversion of `DATA/my concerns and history of discussion with chat gpt/doc/interview quetion.docx`. Do not edit — edit the source and re-run the ingest.

interview — 🔴 = blocks everything downstream

Sensor data

🔴1- What is Enchimento in the sensor file — % fill, cm of free space, or something else? Why the 82–84 ceiling?

Enchimento refers to the percentage of the filling level of container, which ranges from zero to 100 percent, with a value equal 100 percentage or more than 100 percentage being considered.as the overflow rate

🔴 2-What do negative values mean? Is −116 a different error from −3?

We do not have negative values ​​in the filling level in sensor and driver observation. If there are negative values, it is probably due to a sensor and system error. I think the negative values in fill level must be remove from the database,

3-Is this raw sensor output, or already processed by the provider?

Raw sensor output → Data collected directly from the sensor, before any processing or analysis has been applied.

Collections data

4. Confirm 0/25/50/75/100 is the driver's visual estimate. Recorded at collection, or on passing?

0/25/50/75/100 → The driver visually estimated the fill level of the bin.

Recorded at collection → The fill level was recorded at the time of collection/emptying of the bin.

5. What does -1 mean (249 rows)?

Where did you find these 249 rows of -1? There are more than 10000 rows of -1 values in Enchimento column in sensor CSV file, while there are also many other negative values

“-1 in the Enchimento field indicates a sensor  error, the fill-level measurement was not successfully recorded.”

6. Is idrecolha one container lift, or one route trip?

idrecolha represents one collection trip/event, not one individual container lift. All containers serviced during the same trip share the same idrecolha, regardless of the number of containers collected during that trip.

“From the data structure, idrecolha appears to identify a collection event/trip. It is only populated for records associated with a collection operation, while many sensor observations have no idrecolha. Therefore, a blank idrecolha does not necessarily mean that the container was not monitored; it indicates that no collection event is linked to that particular observation.”

7. 🔴 Are Km totais / Peso total per route or per container? If per route, weight cannot be attributed to a container — that changes the demand model completely.

“Based on the data structure, Km totais and Peso total are recorded at the collection-trip/event level, associated with idrecolha, rather than at the individual container level. Therefore, when a collection trip serves multiple containers, the total weight cannot be directly attributed to a specific container.”

8. Why do 23 % of rows have idrecolha but only 8.6 % have Rota?

“idrecolha identifies a collection event/trip, whereas Rota represents the route code. In our dataset, Rota is available only for a subset of the collection events. Therefore, some records have an idrecolha but no corresponding Rota. The exact reason for the missing route information is not confirmed from the available data.”

Coverage

9. 🔴 Can your provider re-export the sensor file without Excel (CSV or Parquet)? Highest-value single action.

No. At present, I only have access to the Excel file, and I do not have access to the raw sensor data or the ability to re-export the data directly from the provider's system. Therefore, the analysis must be conducted based on the available Excel file.

10. How many containers in Rio Maior actually have sensors?

The complete sensor dataset contains approximately 800 sensor-equipped containers. However, my study focuses specifically on the urban area of Rio Maior. After spatially matching the sensor data with the GIS boundary of the study area, approximately 400 sensor-equipped containers are located within the Rio Maior urban area.

11. Are the 816 containers the full municipal park?

The 816 containers represent the broader container dataset available for the municipality, including containers located both inside and outside the defined urban study area of Rio Maior. Therefore, the 816 containers should not necessarily be interpreted as the complete municipal container park.

For my analysis, I use the GIS shapefile defining the boundary of the Rio Maior urban study area. Based on this boundary, only containers located within the defined study area are considered in the analysis.

There are also two different sources of container information: driver-based observation records and sensor-based records. The driver-based dataset covers a larger number of containers than the sensor-based dataset. This is because sensors were installed only on a selected subset of containers as part of a pilot and testing phase.

Therefore, neither the driver-based nor the sensor-based dataset should automatically be considered a complete representation of the entire municipal container network. Both provide partial coverage, with the sensor dataset being more restricted because it includes only containers equipped with sensors for experimental purposes.

12. Is glass genuinely barely instrumented (1.9 % of sensor rows vs 25 % of collection rows)?

Not necessarily. The sensor dataset does not represent the full container network. Sensors were installed only on a selected subset of containers as part of a pilot and testing phase.

Therefore, the fact that glass accounts for only 1.9% of the sensor records, compared with approximately 25% of the collection records, does not necessarily mean that glass containers are genuinely barely instrumented. This difference may partly reflect how containers were selected for sensor installation during the pilot phase.

It is also important to distinguish between the number of records and the number of unique containers. A single sensor-equipped container can generate many records over time. Therefore, these percentages cannot be directly interpreted as the percentage of containers equipped with sensors.

To determine the actual sensor coverage for glass, I would need to compare the number of unique glass containers equipped with sensors with the total number of glass containers within the defined GIS study area.

Operations — needed for VRP/IRP

13. Fleet size, vehicle capacity (kg or m³), shift length, crew size?

“Fleet size, vehicle capacity, shift length, and crew size are not available in the current dataset. These operational parameters would need to be obtained from the municipality to incorporate vehicle capacity and workforce constraints into the optimization model.”

14. Depot location and sorting-facility destination?

The exact locations of the depot and sorting facility are not available in the current dataset. My main study area is the urban area of Rio Maior, defined using a GIS shapefile. The primary focus of the container-location and routing optimization is therefore on the containers and road network within this urban study area. However, some containers served by the Rio Maior collection system are located outside the urban boundary, and actual collection routes may extend beyond the study area. These external containers and road segments will be identified and analysed separately rather than simply excluded. If the depot and sorting-facility locations become available, they can be incorporated into the routing model to represent the complete operational collection route.

15. Current policy — fixed schedule, fill threshold, or driver discretion?

The current collection policy is not explicitly documented in the available dataset. The available records contain collection events and, in some cases, fill-level information, but they do not clearly indicate whether collection is triggered by a fixed schedule, a predefined fill-level threshold, driver discretion, or a combination of these approaches. This will need to be confirmed with the municipality or service provider.

16. Do you have the actual Summer 2023 routes your proposal refers to?

The proposal refers to the actual collection routes performed in Rio Maior during the Summer of 2023. However, I do not currently have the complete reconstructed route trajectories as GIS/GPS route data. The available operational data contain information related to collection activities, but the actual Summer 2023 routes still need to be identified or reconstructed from the available records before they can be compared with optimized routes.

Scope

17. Is Sensor-based Recyclables Collection Planning.docx the definitive scope? Is the final p-median deterministic, stochastic, or both?

Yes, this document defines the current core scope of the research. However, I do not consider it a completely closed or unchangeable framework, as the methodology may be further developed as the research progresses, depending on data availability and quality.

The core of the research focuses on waste-demand estimation and optimal container location. First, waste demand will be estimated using Stepwise Regression. A Deterministic Capacitated p-Median model will then be implemented as a baseline.

Since waste demand is not constant in practice and is subject to uncertainty, I also intend to incorporate this uncertainty into the optimization framework. Different demand scenarios may be generated, where appropriate, using Monte Carlo Simulation and subsequently incorporated into a Stochastic Capacitated p-Median model. Therefore, both deterministic and stochastic formulations will be considered: the deterministic model will serve as the baseline, while the stochastic model will be the main formulation for addressing demand uncertainty. If appropriate, a Robust Capacitated p-Median model may also be considered as an additional benchmark.

Therefore, the current core methodological framework is:

Stepwise Regression → Waste-Demand Estimation →  Deterministic Capacitated p-Median (Baseline) → Uncertainty/Scenario Generation→ Stochastic Capacitated p-Median (Main Model) → Robust/Sensitivity Comparison.

Routing is currently considered a potential extension, subject to the availability of sufficient operational data, rather than a necessary component of the core research framework.

My concerns are as follows.

- Regarding routing, the core research framework does not depend on including a routing component. Without routing, the study can be completed through demand estimation, uncertainty analysis, and optimal container location.
- I do not have further information, however, if sufficient and reliable operational data become available, such as the depot location, sorting or unloading facility destination, vehicle capacities, and reliable information on actual collection routes, the research may be extended to include routing. In that case, the optimized container locations could be used as inputs to a VRP/CVRP or an uncertainty-aware routing model.  IRP to be considered as well.
- Fulfilling above items in thesis requires data availability in hand, that I do not possess. Do your best to perform a deep research to gather as much information as publicly available to perform the analysis. The reference for data is essential. So avoid guessing or inventing. This step is my current concern. After you receive your answer, let me know what you can do to find these information.
- To be honest, I am not 100 percent familiar with all the technical terms I mentioned in response to question No. 17. In the initial report that I will ask you to prepare expand these terms, bring the relevant equations while keep it simple, concise and comprehensible. More importantly, is my proposed method. I need your expert idea about the method. Let me know your honest idea regarding the problem solving efficiency of my proposed methodology. For example the waste generation  the p-median, both the deterministic (baseline) and stochastic methods for waste bin location optimization, and eventually  demand
