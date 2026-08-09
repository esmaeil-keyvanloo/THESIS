---
name: regression-output
title: regresion
type: source
category: thesis
source_file: DATA/DOCUMENT/regresion.pdf
source_sha256: 456dc012713b577b047233e12d8e08894b4fc490ac92bc82f5d1b8ce9206758f
source_bytes: 429690
ingested: 2026-08-08
words: 6820
verbatim: true
---

> Faithful conversion of `DATA/DOCUMENT/regresion.pdf`. Do not edit — edit the source and re-run the ingest.

## Page 1

Regression Model for Predicting Recyclable Waste Generation
Case Study: Rio Maior, Portugal
Written by: Esmaeil Keyvanloo
January 2026
1

## Page 2

5. Abstract
Efficient management of recyclable waste at the urban scale requires accurate demand
prediction at fine spatial resolution, since waste generation and accumulation occur at
the container level, and key operational decisions such as container sizing, placement,
collection frequency, and routing are made at this scale. This study develops a
multivariate linear regression model based on Ordinary Least Squares (OLS) at the bin
level to explain and predict the intensity of recyclable waste collection demand as a
function of local spatial and demographic characteristics. The case study focuses on the
municipality of Rio Maior, Portugal, using real operational data from 2020 to 2024.
Raw operational data at the bin–day level were first processed under a trip weight
allocation assumption, and then aggregated to construct a stable demand indicator for
each container, defined as mean_kg_per_day. To improve the statistical properties of
the dependent variable, a logarithmic transformation was applied using logY = ln(1 +
mean_kg_per_day). Explanatory variables include population within a 100 m buffer
and land-use share variables within the same buffer, derived through GIS-based spatial
analysis. To avoid perfect multicollinearity inherent to compositional land-use shares,
one category was excluded and treated as the baseline. Multicollinearity diagnostics
based on the Variance Inflation Factor (VIF) indicate values close to unity, confirming
the absence of problematic collinearity.
Estimation results show that, in this specification, none of the static spatial variables are
statistically significant at conventional levels, except for the intercept. The very low
coefficient of determination (R2) and the non-significant overall F-test indicate that
static spatial features alone have limited explanatory power for average daily collection
demand. This outcome is consistent with the operational nature of municipal waste
systems, where demand variability is largely driven by dynamic and non-spatial factors
such as service schedules, collection frequency, day-of-week and seasonal effects,
container type, waste stream characteristics, operational policies, and user behavior.
In conclusion, the proposed model should be interpreted as a transparent and
reproducible spatial baseline, suitable for structuring subsequent analyses and for
integration with higher-level decision-support models for container location and
collection routing or scheduling. However, it is insufficient on its own to capture the
dynamics of daily demand. A logical next step is to shift the unit of analysis to the bin–
day level and/or to incorporate temporal and operational variables, as well as
complementary analyses such as overflow behavior.
Keywords: Recyclable Waste Collection, Bin-Level Demand Modeling, Spatial
Regression Analysis, Urban Waste Management, Operational Data Analytics
2

## Page 3

Contents
5. Abstract ........................................................................................................................................... 2
6. Introduction ..................................................................................................................................... 5
7. Conceptual Framework and Regression Methodology ................................................................... 6
8. Statistical Evidence Supporting the Use of OLS ............................................................................ 6
9. Regression Computation Process in Five Layers ............................................................................ 7
5.1. Layer 1. Problem Definition, Unit of Analysis, and Variables ................................................ 7
Study Objective ............................................................................................................................... 7
5.1. Unit of Analysis ...................................................................................................................... 8
6.1. Definition of Unit of Analysis and Variables in the Regression Model .................................. 8
1) Unit of Analysis .......................................................................................................................... 8
5.1. Model Specifications .............................................................................................................. 9
1.1.1 Specification A (complementary): Bin–day model ......................................................... 9
2.1.1 Specification B (main model): Bin-level regression ....................................................... 9
.6.1 Dependent Variable (Y) .......................................................................................................... 9
3.1.1 Conceptual clarification .................................................................................................. 9
7.1. Dependent Variable in Specification B (Main Model) ........................................................... 9
3.3 Complementary dependent variables (Specification A only) ................................................. 10
.8.1 Independent Variables (X) .................................................................................................... 11
4.1.1 General principle ........................................................................................................... 11
5.1.1 Independent Variables Used in the Main Model ........................................................... 11
6.1.1 Baseline rule and multicollinearity control ................................................................... 12
7.1.1 Regression Model (Specification B) ............................................................................. 12
6.1. Layer 2. Data Ingestion and Construction of the Base Dataset ............................................. 12
8.1.1 Input Files and Their Roles in the Processing Chain .................................................... 12
9.1.1 Intermediate Outputs ..................................................................................................... 13
10.1.1 Integration of Operational Data Sources ....................................................................... 13
7.1. Data Sources and Construction of the Regression Base Dataset .......................................... 13
11.1.1 Collection Operations Data (Driver Data) .................................................................... 13
8.1. Methodological Note ............................................................................................................ 14
12.1.1 Container Fill-Level Sensor Data.................................................................................. 14
13.1.1 Spatial and Land-Use Data (GIS) ................................................................................. 15
14.1.1 Layer 3. Data Quality Control and Error Management (Including Overflow) ............. 16
15.1.1 Data Cleaning and Harmonization ................................................................................ 16
3.2 Construction of Standardized Datetime Variables .................................................................. 16
3.3 Definition of Operational Overflow ........................................................................................ 16
3.4 Computational Overflow and Mitigation Strategies ............................................................... 17
3

## Page 4

Layer 4. Regression Computation (From Events to Bin-Level OLS) ............................................... 17
4.1 Construction of the Event-Level Table (bin–event) ................................................................ 17
4.2 Temporal Matching of Sensor and Driver Events ................................................................... 17
4.3 Key Assumption: Allocation of Trip Weight to Containers ................................................... 18
4.4 Computation of Daily Demand (bin–day)............................................................................... 18
4.5 Construction of the Final Dependent Variable........................................................................ 18
4.6 Final Regression Dataset ......................................................................................................... 18
9.1. Logarithmic Transformation of the Dependent Variable and Model Diagnostics ................. 23
Additional Diagnostic Considerations .......................................................................................... 23
10.1. Variables Not Included in the Current Regression Specification .......................................... 24
11.1. Conclusion ........................................................................................................................ 25
4

## Page 5

6. Introduction
Efficient management of recyclable waste at the urban scale requires accurate and
reliable demand forecasts at a fine spatial resolution, as waste generation and
accumulation occur at the level of individual collection containers. In practice, key
operational decisions such as container capacity selection, container siting, service
frequency determination, and collection route design are inherently made at the
container level rather than at the neighbourhood or citywide scale. Consequently,
aggregated analyses that report only zonal or city-level averages are often insufficient
for operational decision support and may result in uneven capacity allocation, increased
risk of overflow, and higher collection costs.
The objective of this study is to develop and estimate a multiple linear regression
(MLR) model at the container level to explain and predict recyclable waste demand as
a function of surrounding environmental and spatial characteristics. Within this
framework, variables are explicitly defined as a dependent variable (Y) and a set of
independent variables (X). The explanatory variables include demographic indicators,
land-use composition metrics (expressed as the proportion of each land-use class within
a 100-m buffer around each container), and additional spatial attributes derived from
Geographic Information Systems (GIS).
The proposed model is developed using real operational data from the municipality of
Rio Maior, Portugal, covering the period 2020–2024. Two independent operational data
sources are integrated:
(1) collection operation records from the truck driver’s perspective, registered through
the collection management system; and
(2) fill-level sensor data, consisting of time series of container fill percentages.
The integration of these data sources enables a distinction between collected waste and
accumulated or potentially generated waste, thereby providing a more comprehensive
representation of container-level demand behaviour.
The core assumption underlying this research is that the intensity of recyclable waste
generation or accumulation at each container reflects the surrounding pattern of human
activity, land-use structure, and relative location within the urban system. In particular,
containers located in areas with higher population density or a greater share of
commercial, service, or institutional land uses-typically concentrated in central urban
areas-are expected to exhibit demand patterns distinct from those located in
predominantly residential neighbourhoods. Quantifying these relationships yields two
direct practical benefits: first, improving the prediction and interpretation of existing
container performance to support service scheduling and capacity allocation; and
5

## Page 6

second, estimating potential demand at locations without containers to support network
expansion and container location decisions.
The regression model developed in this study is not used solely as an independent
statistical analysis tool, but rather as an input module for subsequent decision-making
stages, including container location models (p-median) and collection routing and
scheduling models (VRP/IRP). Accordingly, emphasis is placed on data transparency,
precise variable definition, and model reproducibility, ensuring that the results are both
scientifically defensible and operationally applicable for urban planning and waste
management.
The remainder of this section is organized as follows. First, the data sources and data
cleaning and standardization procedures are described. Next, the definition of the
dependent and independent variables, the rationale for feature selection, and the
construction of the final regression dataset are presented. Finally, the regression model
specification, diagnostic tests (including multicollinearity control and error assumption
checks), and estimation results with managerial interpretation are reported.
7. Conceptual Framework and Regression Methodology
The purpose of the regression analysis in this study is to model the relationship between
recyclable waste generation or collection (dependent variable) and a set of
demographics, spatial, and land-use explanatory factors (independent variables) at the
level of individual urban containers. The output of this regression serves as an input to
container location models (p-median) and collection routing and planning models
(VRP/IRP).
The primary unit of observation is the container–day (bin–day), meaning that each
observation represents the behaviour of a specific container on a specific day. This
structure allows the analysis of daily variability and the derivation of stable demand
indicators. For the estimation of the baseline regression model, however, daily
observations are aggregated to the container level, and a cross-sectional regression
model is estimated at the bin level.
The statistical model employed is a classical multiple linear regression estimated
using Ordinary Least Squares (OLS). The analysis does not involve panel regression
techniques, logistic or Poisson models, nor machine-learning-based estimators. Instead,
a standard OLS specification is adopted as a baseline explanatory model for spatial
demand analysis at the container level.
8. Statistical Evidence Supporting the Use of OLS
The regression outputs exhibit the four canonical components of an OLS model:
6

## Page 7

^ ^
estimated coefficients (𝛽), standard errors (𝑆𝐸(𝛽)), t-statistics, and p-values. This four-
element structure constitutes the definitive statistical signature of an OLS regression. In
OLS, the t-statistic is computed as:
^
𝛽
𝑡 =
^
𝑆𝐸(𝛽)
The explicit presence of these statistics in the model outputs confirms that the estimation
method is Ordinary Least Squares. If an alternative modeling framework had been used,
different statistical indicators would have appeared. For example:
• Logistic regression models report z-statistics
• Poisson or count models typically report Wald statistics
• Maximum likelihood–based models emphasize log-likelihood values
• Panel data models report variance components such as effects, 𝜎 , 𝜌
𝑢
• The absence of such indicators, combined with the presence of coefficient
estimates, standard errors, and t-statistics, unequivocally demonstrates that the
model employed in this study is a cross-sectional OLS regression at the
container level.
this study applies a multiple linear regression model estimated via Ordinary Least
Squares as a baseline, interpretable, and spatially explicit tool for analysing recyclable
waste demand at the container level. The model is not intended to replace machine
learning approaches, but rather to provide a transparent and theoretically grounded
foundation that can be directly linked to spatial optimization and operational planning
models in subsequent stages of analysis.
9. Regression Computation Process in Five Layers
From raw data ingestion to variable construction, overflow definition, OLS estimation,
and result interpretation
5.1. Layer 1. Problem Definition, Unit of Analysis, and Variables
Study Objective
The objective of this analysis is to explain and predict the intensity of recyclable waste
collection demand at the level of individual urban containers. The resulting model is
designed to serve as a direct input to subsequent decision-support models, including
container location planning (p-median) and collection routing and scheduling models
(VRP/IRP). The primary emphasis is on developing a transparent, reproducible, and
interpretable baseline model that quantitatively links waste collection demand to the
surrounding spatial and demographic context of each container.
7

## Page 8

5.1. Unit of Analysis
Although data are available at multiple temporal and operational levels, the final
regression model is specified as a cross-sectional model at the container (bin-level).
The data hierarchy is as follows:
• Raw operational level: bin–event
• Intermediate analytical level: bin–day
• Final regression level: bin-level, where each row corresponds to a unique
container identifier (idcontentor)
Temporal information (daily or event-based) is used exclusively to construct a stable
demand indicator and is subsequently aggregated to the container level. As a result, the
final model:
• Is cross-sectional
• Is neither time-series nor panel-based
• Functions as a baseline spatial regression
6.1. Definition of Unit of Analysis and Variables in the Regression Model
1) Unit of Analysis
In this study, the raw data are observed at two different levels; however, the core
regression model of the thesis is estimated at the container level (bin-level).
Level A: Bin–day (container–day)
At this level, observations are constructed for each container i and each day t. This level
is used exclusively to:
• aggregate collection events into daily values,
• derive temporal features such as lags and rolling statistics,
• analyse service dynamics and filling behaviour,
• support exploratory and complementary analyses.
This level does not generate the final regression coefficients reported in the thesis.
Level B: Bin-level (container level) – Main model
In the final model:
• Each row of the dataset corresponds to one container, uniquely identified by
idcontentor.
• Daily and event-level data are first aggregated to construct a stable demand
indicator, which is then transferred to the bin-level.
8

## Page 9

Accordingly, the main regression model is:
• cross-sectional,
• neither time-series nor panel-based,
• and serves as a baseline spatial regression to quantify the effect of demographic
and land-use characteristics on waste collection demand intensity.
5.1. Model Specifications
To avoid any ambiguity regarding data structure and coefficient interpretation, two
model specifications are explicitly distinguished.
1.1.1 Specification A (complementary): Bin–day model
• Purpose: analysis of temporal patterns, lag effects, service intervals, and
behavioural dynamics.
• Role: supplementary and exploratory.
2.1.1 Specification B (main model): Bin-level regression
• Purpose: construction of a transparent, reproducible baseline model suitable for
spatial decision-making and integration with p-median, VRP, and IRP
frameworks.
• All regression results reported in the Excel file correspond exclusively to
this specification.
6.1. Dependent Variable (Y)
The dependent variable represents a stable indicator of waste collection demand at the
container level and is defined.
3.1.1 Conceptual clarification
Two operational data sources are available: driver records and container sensors.
While both allow the definition of dependent variables, the key point is that:
In the final Excel-based regression (Specification B), the dependent variable is
derived solely from driver data.
Sensor data are not used as the primary dependent variable in the main model and serve
only a complementary analytical role.
7.1. Dependent Variable in Specification B (Main Model)
(B1) Stable demand indicator at bin-level
For each container i, the raw dependent variable is defined as:
9

## Page 10

𝑌 = 𝑚𝑒𝑎𝑛_𝑘𝑔_𝑝𝑒𝑟_𝑑𝑎𝑦
𝑖 𝑖
where:
• 𝑚𝑒𝑎𝑛_𝑘𝑔_𝑝𝑒𝑟_𝑑𝑎𝑦 : represents the average daily collected weight from
𝑖
container i over the entire observation period, expressed in kg/day.
Formally:
𝑇
𝑖
1
𝑚𝑒𝑎𝑛_𝑘𝑔_𝑝𝑒𝑟_𝑑𝑎𝑦 = ∑𝑘𝑔_𝑑𝑎𝑦
𝑖 𝑖,𝑡
𝑇
𝑖
𝑡=1
with:
• 𝑘𝑔_𝑑𝑎𝑦 : total weight collected from container i on day t, after aggregating all
𝑖,𝑡
service events occurring on that day;
• 𝑇: number of days with valid operational data for container i.
𝑖
This indicator smooths short-term fluctuations and provides a robust proxy for long-
term demand intensity at the container level.
(B2) Regression form of the dependent variable
Due to the strong right-skewness typically observed in waste collection data, a
logarithmic transformation is applied.
If all values are strictly positive:
𝑙𝑜𝑔𝑌 = ln (𝑚𝑒𝑎𝑛_𝑘𝑔_𝑝𝑒𝑟_𝑑𝑎𝑦 )
𝑖 𝑖
If zero values may occur:
𝑙𝑜𝑔𝑌 = ln (1+𝑚𝑒𝑎𝑛_𝑘𝑔_𝑝𝑒𝑟_𝑑𝑎𝑦 )
𝑖 𝑖
The exact transformation applied must be stated explicitly in the final report,
consistent with the Excel implementation.
3.3 Complementary dependent variables (Specification A only)
For completeness, but not used in the main regression:
• Driver-based daily variable:
𝑌𝑑𝑟𝑖𝑣𝑒𝑟 = 𝑘𝑔_𝑑𝑎𝑦
𝑖,𝑡 𝑖,𝑡
10

## Page 11

• Sensor-based daily variable:
𝑌𝑠𝑒𝑛𝑠𝑜𝑟 = max (𝐸𝑛𝑐ℎ𝑖𝑚𝑒𝑛𝑡𝑜 )
𝑖,𝑡 𝑖,𝑡
These variables are used solely for exploratory and behavioural analyses.
8.1. Independent Variables (X)
Independent variables consist primarily of static spatial and demographic characteristics
within a 100-meter buffer around each container, including:
4.1.1 General principle
Under Specification B, all independent variables are:
• static,
• spatial,
• defined at the bin-level.
They are primarily extracted from GIS layers using a 100-metre buffer around each
container.
5.1.1 Independent Variables Used in the Main Model
(X1) Demographic variable
𝑃𝑜𝑝_100𝑚
𝑖
Population residing within a 100-metre radius of container i.
(X2) Land-use composition variables
For each container i, the share of land-use class k within the 100-metre buffer is defined
as:
𝑃𝑐𝑡_𝑘
𝑖
The following land-use classes are included:
• Pct_RESIDENTIAL i
• Pct_COMMERCIAL i
• Pct_INDUSTRIAL i
• Pct_INSTITUTIONAL i
• Pct_ADMINISTRATIVE i
• Pct_HEALTHCARE i
• Pct_CULTURAL i
• Pct_RECREATIONAL i
11

| 𝑃𝑐𝑡_ | 𝑘 |   |
|---|---|---|
|   |   | 𝑖 |

## Page 12

• Pct_TRANSPORT i
• Pct_OTHER i
Additional classes are included where present in the GIS dataset.
6.1.1 Baseline rule and multicollinearity control
Since land-use percentages typically sum to 100%:
∑𝑃𝑐𝑡_𝑘 = 100
𝑖
𝑘
one category must be excluded to avoid perfect multicollinearity.
In this study, Pct_OTHER is omitted and acts as the baseline category.
i
All estimated coefficients therefore represent marginal effects relative to this omitted
class.
7.1.1 Regression Model (Specification B)
The estimated cross-sectional log-linear model is:
𝑙𝑜𝑔𝑌 = 𝛽 +𝛽 𝑃𝑜𝑝_100𝑚 + ∑𝛽 𝑃𝑐𝑡_𝑘 +𝜀
𝑖 0 1 𝑖 𝑘 𝑖 𝑖
𝑘∈𝐾
where 𝜀 is the error term.
𝑖
In the final regression model (Specification B), the dependent variable 𝑙𝑜𝑔𝑌 is
𝑖
constructed from driver data and is rooted in the container-level indicator
𝑚𝑒𝑎𝑛_𝑘𝑔_𝑝𝑒𝑟_𝑑𝑎𝑦 . The independent variables consist of 𝑃𝑜𝑝_100𝑚 and land-use
𝑖 𝑖
composition variables 𝑃𝑐𝑡_𝑘 defined within a 100-metre buffer around each container.
𝑖
To control for perfect multicollinearity, the category 𝑃𝑐𝑡_𝑂𝑇𝐻𝐸𝑅 is omitted and
𝑖
serves as the baseline. Sensor data are not used as the primary dependent variable in
this model and are employed only as complementary information for analysing filling
behaviour and supporting robustness checks.
6.1. Layer 2. Data Ingestion and Construction of the Base Dataset
8.1.1 Input Files and Their Roles in the Processing Chain
This study relies on four primary datasets, each with a clearly defined role in the data-
processing pipeline:
1. Enchimentos_com_Recolhas_RioMaior_2023.csv
Raw collection operation data recorded by drivers and the operational system.
This dataset forms the basis for event-level construction and extraction of
12

## Page 13

collected waste quantities.
2. Enchimentos_de_Sensores_RioMaior_2023.csv
Raw time-series data from container fill-level sensors. These data are used for
quality control, overflow analysis, and linking near-emptying fill conditions to
collection events.
3. bins_spatial_features_binlevel.csv
Spatial and land-use attributes surrounding each container at the bin level. This
file is the primary source of Pop_100m and Pct_* variables.
4. regdata_input.csv
The final regression-ready dataset, where each row represents a single container
and includes the dependent variable and all explanatory variables.
9.1.1 Intermediate Outputs
Several intermediate datasets are generated during processing:
• event_stops_merged.csv: event-level data after merging driver and sensor
information
• trip_summary.csv: trip-level summaries
• cont_daily.csv: bin–day indicators
• cont_stats.csv: bin-level summary including mean_kg_per_day
10.1.1 Integration of Operational Data Sources
Driver and sensor datasets are complementary. Driver data provide the primary measure
of collected quantities, while sensor data offer a more accurate representation of actual
fill behavior and overflow conditions. These datasets are integrated using:
• Common identifier: idcontentor
• Temporal rule: linking the last sensor reading prior to the emptying time
(backward temporal matching)
7.1. Data Sources and Construction of the Regression Base Dataset
According to the data structure, this study relies on two primary operational data
sources and one spatial (GIS) data source. These datasets are linked using common
identifiers and explicit temporal rules in order to construct a consistent dataset at the
bin–event level and, ultimately, to derive a stable demand indicator at the bin level.
11.1.1 Collection Operations Data (Driver Data)
Enchimentos_com_Recolhas_RioMaior_2023.csv
13

## Page 14

This file contains raw collection operation records reported by truck drivers and the
operational management system. It represents the primary source for estimating
collected waste quantities.
Key Columns
• idcontentor: Unique container identifier (primary key for data integration)
• idrecolha: Collection trip or event identifier
• Data de início + Tempo de início: Start time of container emptying
• Peso totl: Total collected weight per trip (kg)
• Km totais: Total distance traveled during the trip (km)
• Enchimento: Fill level (%) reported by the driver prior to emptying
8.1. Methodological Note
The weight reported in this dataset is recorded at the trip level, not necessarily at the
individual container level. Therefore, a weight allocation assumption is required when
analyzing demand at the container level. This assumption is explicitly defined and
discussed in later stages of the methodology.
After data cleaning, time standardization, and consistency checks, this dataset is
transformed into the event_stops table, where each row represents one container
serviced during one collection trip.
Structure of the Driver Dataset
Column Description
idcontentor Container identifier (join key)
Tipo de contentor Container type (AMBI, OVO, VRL, etc.)
Volume do tipo de contentor Container volume (liters)
description Waste type (paper, glass, plastic, etc.)
Longitude / Latitude Container coordinates
Data de início Date of emptying start
Tempo de início Time of emptying start
Data de fim Date of emptying end
Tempo de fim Time of emptying end
Enchimento Fill level (%)
idrecolha Collection trip/truck identifier
Peso totl Collected weight (kg)
Km totais Distance traveled (km)
12.1.1 Container Fill-Level Sensor Data
Enchimentos_de_Sensores_RioMaior_2023.csv
14

| Column | Description |
|---|---|
| idcontentor | Container identifier (join key) |
| Tipo de contentor | Container type (AMBI, OVO, VRL, etc.) |
| Volume do tipo de contentor | Container volume (liters) |
| description | Waste type (paper, glass, plastic, etc.) |
| Longitude / Latitude | Container coordinates |
| Data de início | Date of emptying start |
| Tempo de início | Time of emptying start |
| Data de fim | Date of emptying end |
| Tempo de fim | Time of emptying end |
| Enchimento | Fill level (%) |
| idrecolha | Collection trip/truck identifier |
| Peso totl | Collected weight (kg) |
| Km totais | Distance traveled (km) |

## Page 15

This dataset contains time-series sensor readings of container fill levels and serves as
a complementary source to the driver-reported data. Sensor data are used to observe
actual accumulation behavior, identify overflow events, and validate fill levels close to
collection times.
Key Columns
• idcontentor: Unique container identifier
• Data da leitura + Tempo de leitura: Sensor reading timestamp
• Enchimento (%): Fill level measured by the sensor
Main Uses of Sensor Data
• Analysis of real container filling behavior
• Definition and validation of overflow indicators
• Temporal alignment of fill conditions immediately prior to emptying
Temporal Matching of Sensor and Driver Data
Using backward temporal matching (analogous to merge_asof), the last sensor
reading prior to each emptying event is linked to the corresponding collection record.
The output of this step is the event_stops_merged dataset, in which both driver-
reported and sensor-based fill levels are available for each collection event when sensor
data exist.
Structure of the Sensor Dataset
Column Description
idcontentor Container identifier (join key)
Tipo de contentor Container type
Volume do tipo de contentor Container volume (liters)
description Waste type
Longitude / Latitude Container coordinates
Data da leitura Reading date
Tempo de leitura Reading time
Enchimento Fill level (%)
idrecolha Trip identifier (if recorded)
Peso totl Collected weight (if recorded)
Km totais Distance traveled (if recorded)
13.1.1 Spatial and Land-Use Data (GIS)
bins_spatial_features_binlevel.csv
This file stores static spatial attributes of each container and constitutes the main
source of explanatory variables in the regression model. All features are extracted
15

| Column | Description |
|---|---|
| idcontentor | Container identifier (join key) |
| Tipo de contentor | Container type |
| Volume do tipo de contentor | Container volume (liters) |
| description | Waste type |
| Longitude / Latitude | Container coordinates |
| Data da leitura | Reading date |
| Tempo de leitura | Reading time |
| Enchimento | Fill level (%) |
| idrecolha | Trip identifier (if recorded) |
| Peso totl | Collected weight (if recorded) |
| Km totais | Distance traveled (if recorded) |

## Page 16

within a 100-meter buffer around each container using GIS processing.
Main Contents
• Surrounding population
• Land-use composition
• Distance to city business district (CBD)
• Physical container attributes (volume, container type, waste type) to understand
stream Material
Key Derived Variables
• Pop_100m: Population within a 100-meter buffer
• Land-use shares
14.1.1 Layer 3. Data Quality Control and Error Management (Including
Overflow)
At this stage, it is essential to clearly distinguish between two fundamentally different
concepts:
• Operational overflow (container overflow): a capacity and service-level issue
based on fill percentage
• Computational overflow: a numerical processing issue resulting in ∞ or NaN
values
15.1.1 Data Cleaning and Harmonization
• Files are read using appropriate encodings (UTF-8 or Latin-1)
• Column names are standardized across the entire pipeline
• idcontentor is converted to a uniform data type (string)
• Invalid records are removed or corrected, including:
o Negative fill levels
o Negative weights
o Inconsistent timestamps (end time preceding start time)
o Unrealistic or out-of-bound spatial coordinates
3.2 Construction of Standardized Datetime Variables
For both driver and sensor data:
• Date and time fields are combined into standardized datetime variables
• Records are temporally sorted to ensure correct sensor–event alignment
3.3 Definition of Operational Overflow
16

## Page 17

Operational overflow is defined as follows:
• overflow_driver = 1 if fill_driver ≥ 100, otherwise 0
• overflow_sensor = 1 if fill_sensor ≥ 100, otherwise 0
• overflow_combined = max(overflow_driver, overflow_sensor)
Methodological note: overflow observations are not removed. They are labeled to:
• Avoid sample-selection bias
• Preserve information for supplementary analyses
• Enable managerial interpretation related to capacity shortages or service delays
3.4 Computational Overflow and Mitigation Strategies
Computational overflow occurs when numerical values exceed computational limits
and become ∞ or NaN. Common causes include:
• ln(0) or ln(negative values)
• High-order powers or multiplication of large variables
• Unit inconsistencies (e.g., km vs. m)
Standard mitigation strategies include:
• Logarithmic transformations using +1 or ε
• Standardization or normalization of large-magnitude variables
• Unit consistency checks prior to data integration
• Outlier labeling and sensitivity analysis instead of blind removal
Layer 4. Regression Computation (From Events to Bin-Level OLS)
4.1 Construction of the Event-Level Table (bin–event)
Each row represents the servicing of one container during a collection event and
includes:
• idrecolha, idcontentor
• datetime_start
• fill_driver
• Peso_totl and Km_totais (typically recorded at the trip level and repeated across
stops)
4.2 Temporal Matching of Sensor and Driver Events
For each emptying event:
• Key: idcontentor
17

## Page 18

• Rule: last sensor reading prior to datetime_start
• Maximum tolerance window: 2 hours
• Method: backward temporal matching (merge_asof-like)
The output is event_stops_merged.csv. Missing sensor data for some events are
accepted and treated as missing, not as errors.
4.3 Key Assumption: Allocation of Trip Weight to Containers
Since collected weight is recorded at the trip level and individual stop weights are
unavailable, an equal allocation assumption is applied:
𝑃𝑒𝑠𝑜
𝑡𝑟𝑖𝑝
𝑃𝑒𝑠𝑜 =
𝑏𝑖𝑛
𝑛
𝑏𝑖𝑛𝑠
This assumption is common in operational studies; however, its limitations are
explicitly acknowledged in the Limitations section.
4.4 Computation of Daily Demand (bin–day)
After weight allocation, data are aggregated at the (idcontentor, date) level:
• kg_day
• mean_fill_driver_day
• mean_fill_sensor_day
• overflow_driver_day, overflow_sensor_day
Output: cont_daily.csv
4.5 Construction of the Final Dependent Variable
For each container i:
1
mean_kg_per_day = ∑𝑘𝑔
𝑖 𝑇 𝑖,𝑡
𝑖
𝑡
where Ti is the number of valid observation days. Output: cont_stats.csv
4.6 Final Regression Dataset
The following datasets are joined by idcontentor:
• cont_stats.csv
• bins_spatial_features_binlevel.csv
Final output: regdata_input.csv
18

## Page 19

OLS Regression Model at the Bin Level
11.1 Unit of Analysis and Dependent Variable
The model is estimated as a cross-sectional OLS regression at the bin level, meaning
that each observation represents a unique bin (N = 452). The daily bin–day records are
used only to construct a stable demand indicator at the bin level.
The dependent variable is defined as:
𝑙𝑜𝑔𝑌 = ln (1+mean_kg_per_day )
𝑖 𝑖
This transformation (log1p) is applied to reduce right skewness, limit the influence of
outliers, and promote a more stable error variance.
11.2 Explanatory Variables and the Baseline Category for Land-Use Shares
The explanatory variables include:
• Pop_100m i : population within a 100 m buffer
• Pct k,i : land-use share of class k within same buffer (fractions between 0 and 1)
Because land-use shares are compositional (their sum is approximately 1), one class
must be omitted to avoid perfect multicollinearity. In this project:
• Pct_OTHER is excluded and treated as the baseline.
Accordingly, the coefficients of Pct_* represent effects relative to the baseline
category (OTHER), holding the other variables constant.
12) Model Form and Estimated Equation
12.1 General Model Form
𝑙𝑜𝑔𝑌 = 𝛽 +𝛽 𝑃𝑜𝑝_100𝑚 +∑𝛽 𝑃𝑐𝑡 +𝜀
𝑖 0 𝑃𝑜𝑝 𝑖 𝑘 𝑘,𝑖 𝑖
𝑘
12.2 Estimated Equation (as reported in regression_coefficients.csv)
^
𝑙𝑜𝑔𝑌 = 5.275631+0.344192 𝑃𝑐𝑡_𝑅𝐸𝑆𝐼𝐷𝐸𝑁𝑇𝐼𝐴𝐿+0.514317 𝑃𝑐𝑡_𝐼𝑁𝑆𝑇𝐼𝑇𝑈𝑇𝐼𝑂𝑁𝐴𝐿
+1.199277 𝑃𝑐𝑡_𝐶𝑈𝐿𝑇𝑈𝑅𝐴𝐿−0.559110 𝑃𝑐𝑡_𝑇𝑅𝐴𝑁𝑆𝑃𝑂𝑅𝑇
−6.374×10−7 𝑃𝑜𝑝_100𝑚+0.397734 𝑃𝑐𝑡_𝐻𝐸𝐴𝐿𝑇𝐻𝐶𝐴𝑅𝐸
−0.680315 𝑃𝑐𝑡_𝐴𝐷𝑀𝐼𝑁𝐼𝑆𝑇𝑅𝐴𝑇𝐼𝑉𝐸 +0.080507 𝑃𝑐𝑡_𝐶𝑂𝑀𝑀𝐸𝑅𝐶𝐼𝐴𝐿
+0.048440 𝑃𝑐𝑡_𝐼𝑁𝐷𝑈𝑆𝑇𝑅𝐼𝐴𝐿+0.022054 𝑃𝑐𝑡_𝑅𝐸𝐶𝑅𝐸𝐴𝑇𝐼𝑂𝑁𝐴𝐿
12.3 Back-Transformation to the Original Scale (kg/day)
To convert predictions from the log scale back to the original demand scale:
19

## Page 20

^ ^
mean_kg_per_day = exp (𝑙𝑜𝑔𝑌)−1
If the goal is unbiased prediction of the conditional mean on the original scale, direct
exponentiation can introduce retransformation bias. If needed, a smearing estimator
(Duan) can be applied in the prediction stage.
13) Coefficients and Statistical Inference (Coefficients)
The OLS coefficients are extracted from regression_coefficients.csv.
Variable Coefficient (β) Std. Err t p-value Significance
Intercept 5.275631 0.582109 9.0630 5.50e-18 ***
Pct_RESIDENTIAL 0.344192 0.730749 0.4711 0.6378
Pct_INSTITUTIONAL 0.514317 0.912158 0.5638 0.5732
Pct_CULTURAL 1.199277 2.447939 0.4898 0.6246
Pct_TRANSPORT -0.559110 1.128226 -0.4956 0.6204
Pop_100m -6.374e-07 1.942e-06 -0.3282 0.7429
Pct_HEALTHCARE 0.397734 0.763129 0.5211 0.6025
Pct_ADMINISTRATIVE -0.680315 1.657369 -0.4105 0.6816
Pct_COMMERCIAL 0.080507 0.233700 0.3445 0.7306
Pct_INDUSTRIAL 0.048440 0.129119 0.3751 0.7078
Pct_RECREATIONAL 0.022054 0.129994 0.1697 0.8654
Direct statistical interpretation: In this model run, with the exception of the intercept,
none of the explanatory variables is statistically significant even at the 0.10 level.
Therefore, the current specification should be treated primarily as a spatial baseline
rather than a strong inferential model for identifying independent effects of land use or
buffered population.
Technical note: A statistically significant intercept alone typically indicates the
existence of a baseline level of logY, while the selected spatial predictors are not
capturing the variation in demand across bins.
14) Model Fit
According to regression_metrics.csv:
• Number of observations: N=452
• R2=0.0130
20

| Variable | Coefficient (β) | Std. Err | t | p-value | Significance |
|---|---|---|---|---|---|
| Intercept | 5.275631 | 0.582109 | 9.0630 | 5.50e-18 | *** |
| Pct_RESIDENTIAL | 0.344192 | 0.730749 | 0.4711 | 0.6378 |   |
| Pct_INSTITUTIONAL | 0.514317 | 0.912158 | 0.5638 | 0.5732 |   |
| Pct_CULTURAL | 1.199277 | 2.447939 | 0.4898 | 0.6246 |   |
| Pct_TRANSPORT | -0.559110 | 1.128226 | -0.4956 | 0.6204 |   |
| Pop_100m | -6.374e-07 | 1.942e-06 | -0.3282 | 0.7429 |   |
| Pct_HEALTHCARE | 0.397734 | 0.763129 | 0.5211 | 0.6025 |   |
| Pct_ADMINISTRATIVE | -0.680315 | 1.657369 | -0.4105 | 0.6816 |   |
| Pct_COMMERCIAL | 0.080507 | 0.233700 | 0.3445 | 0.7306 |   |
| Pct_INDUSTRIAL | 0.048440 | 0.129119 | 0.3751 | 0.7078 |   |
| Pct_RECREATIONAL | 0.022054 | 0.129994 | 0.1697 | 0.8654 |   |

## Page 21

• Adj.R2=−0.0100
• AIC = 1349.476
• BIC = 1398.885
• F-test p-value = 0.9504
Methodological interpretation: The very low R2 and the non-significant overall F-
test indicate that static spatial predictors (land-use shares and buffered population) have
limited explanatory power for average daily collection demand. In practice, most
demand variability in municipal service systems is often driven by non-spatial and
dynamic factors, such as:
• operational planning and service policy (collection frequency, route allocation,
operational decisions)
• temporal effects (day of week, month, season, holidays, short-term events)
• equipment and material-flow characteristics (bin type, capacity, waste stream,
operational constraints)
• user behavior and local participation patterns
A defensible thesis conclusion is that a purely static spatial model is insufficient as the
primary explanation of daily demand, and that explanatory performance requires either
(i) moving to the bin–day level or (ii) incorporating temporal and operational
covariates.
15) Multicollinearity (VIF) and Detection of Strong Correlation
Multicollinearity among the explanatory variables was assessed using the Variance
Inflation Factor (VIF). VIF measures how much the variance of an estimated
regression coefficient is inflated due to linear dependence with other predictors.
A commonly accepted rule of thumb for interpreting VIF values is as follows:
• VIF < 5 → Excellent; no multicollinearity concerns
• 5 ≤ VIF < 10 → Acceptable; moderate multicollinearity, warrants caution
• VIF ≥ 10 → Problematic; severe multicollinearity, variables should be
removed, combined, or redefined
In this study, all VIF values are close to 1, indicating that the explanatory variables are
largely independent and that multicollinearity is not a concern. Therefore, any lack of
statistical significance in the estimated coefficients is not attributable to collinearity
issues, but rather to the limited explanatory power of the selected predictors.
Based on vif_table.csv, all VIF values are close to 1 (approximately 1.00 to 1.06).
21

## Page 22

Conclusion: There is no evidence of problematic multicollinearity. The lack of
explanatory power is not driven by collinearity, but rather by the limited scope of
predictors restricted to static spatial variables.
16) Direction-of-Effect Interpretation (Descriptive Only)
Since Pct_* variables are fractions between 0 and 1, an increase of 0.10 corresponds to
a 10 percentage-point increase in the land-use share within the buffer.
With the log1p specification, if the predicted change in logY is Δ, the relative change
in (1+Y) is approximately:
1+𝑌
𝑛𝑒𝑤 ≈ 𝑒𝛥
1+𝑌
𝑜𝑙𝑑
Descriptive example: Cultural land use
If Pct_CULTURAL increases by 0.10:
𝛥𝑙𝑜𝑔𝑌 ≈ 1.199277× 0.10 = 0.1199
𝑒0.1199 ≈ 1.127
This implies an approximate 12.7% increase in (1+Y).
Important: because the p-value is high, this is strictly a directional/descriptive
interpretation and should not be reported as an inferential conclusion.
Descriptive example: Population
An increase of 10,000 people in Pop_100m:
𝛥𝑙𝑜𝑔𝑌 = (−6.374×10−7)×10000 = −0.00637
𝑒−0.00637 ≈ 0.9936
This corresponds to about a 0.6% decrease in (1+Y). This effect is also non-significant
and remains descriptive.
17) Short Summary Suitable for Emailing a supervisor
• Daily bin–day records were aggregated to a stable bin-level demand indicator
(mean_kg_per_day, in cont_stats.csv).
• Spatial predictors within a 100 m buffer were extracted (Pop_100m and Pct_*,
in bins_spatial_features_binlevel.csv).
• A final regression dataset was built with 452 bins (regdata_input.csv).
• The dependent variable was defined as 𝑙𝑜𝑔𝑌 = ln (1+mean_kg_per_day)
• An OLS model was estimated and outputs were reported
(regression_coefficients.csv, regression_metrics.csv).
22

## Page 23

Key result: Static spatial predictors alone provide very limited explanatory power. A
logical next step is to move to the bin–day level and/or add temporal and operational
variables (day-of-week, month/season, number of services, time since last service, bin
type, waste stream, sensor indicators, routing/fleet features).
9.1. Logarithmic Transformation of the Dependent Variable and Model
Diagnostics
Prior to estimating the regression model, a logarithmic transformation was applied to
the dependent variable. This procedure represents a standard methodological practice
in regression analysis and is typically adopted when the dependent variable exhibits
strong right-skewness or when its variance increases with the mean (heteroskedasticity).
The dependent variable was logarithmically transformed prior to model estimation to
reduce skewness and stabilize the error variance.
In this study, the dependent variable is defined as:
logY = ln (mean_kg_per_day)
The application of this transformation serves several purposes:
• to reduce right-skewness in the distribution of the dependent variable,
• to mitigate the influence of extreme observations (outliers),
• to stabilize the variance of the error term,
• and to improve compliance with the classical assumptions of linear regression.
The final regression model is therefore estimated in the logarithmic scale. To obtain
predictions in the original measurement units (kilograms per day), the inverse
exponential transformation is applied:
^ ^
mean_kg_per_day = exp (logY)
It should be noted that when the objective is accurate prediction on the original scale,
the exponential back-transformation may introduce bias. In such cases, bias-correction
techniques such as the Smearing Estimator may be employed. However, given that
the primary focus of this analysis is on structural interpretation and comparative
model assessment rather than point forecasting, the standard exponential
transformation is considered sufficient.
Additional Diagnostic Considerations
In addition to the logarithmic transformation, several diagnostic checks were
conducted at a descriptive level to assess model adequacy:
23

## Page 24

• examination of residual patterns to detect systematic structure,
• qualitative assessment of heteroskedasticity,
• sensitivity analysis with respect to outliers through identification, labeling, and
comparison of model behavior.
These diagnostics indicate that the logarithmic transformation of the dependent
variable improves coefficient stability and overall model behavior, supporting its use
in the final model specification.
10.1. Variables Not Included in the Current Regression Specification
Several potentially relevant explanatory factors were not incorporated into the current
regression model. Their exclusion is deliberate and reflects data scope and model
parsimony considerations rather than methodological oversight.
Overflow events were not included in the regression analysis. However, overflow can
be systematically derived from sensor data using standard definitions based on
sustained high fill levels beyond operational thresholds. As such, overflow is well suited
to be analyzed as a complementary outcome variable or modeled separately using a
dedicated specification focused on service reliability and risk conditions.
Street network density was not considered in the regression model. Although network
density may influence accessibility and collection efficiency, it represents an
infrastructural characteristic that is more directly related to routing and operational
performance than to baseline demand generation at the bin level.
Distance to the city center was also excluded from the regression. While this variable
may capture aspects of urban hierarchy and land-use intensity, its effect is partially
embedded in land-use composition and population distribution variables already
considered, and its explicit inclusion was deferred to avoid redundancy in the baseline
spatial specification.
Rainfall and weather conditions were not incorporated into the regression model.
Precipitation primarily affects short-term waste generation behavior and collection
operations and is therefore more appropriately analyzed in a temporal or bin–day
framework rather than in a cross-sectional bin-level model.
The current regression is intentionally specified as a baseline spatial model using static
neighborhood characteristics only. Dynamic, operational, and environmental variables
such as overflow, routing constraints, network structure, distance to city center, and
rainfall are more suitably addressed in extended specifications or separate analyses
focused on temporal dynamics, operational performance, or service reliability.
24

## Page 25

• For the construction of the final regression dataset, a cross-sectional bin-level unit
of analysis was adopted, meaning that each row represents a single bin with a unique
identifier. The raw operational data, originally recorded at the trip and bin–day levels,
were first processed using a weight allocation assumption, whereby the collected
trip weight was distributed among the bins serviced during that trip. Subsequently, a
daily demand per bin was computed and then aggregated to derive a stable demand
indicator at the bin level. Accordingly, although the original information exists at
daily or inter-emptying intervals, the final regression model is estimated on bin-level
aggregated data, rather than on bin–day observations or inter-collection intervals.
11.1. Conclusion
In this study, a multivariate linear regression model based on Ordinary Least Squares
(OLS) was developed at the bin-level to explain the intensity of recyclable waste
collection demand using spatial characteristics around each container. Daily operational
data recorded at the bin–day level was first aggregated to construct a stable demand
indicator, mean_kg_per_day, for each bin. To improve the statistical properties of the
dependent variable, a logarithmic transformation logY = ln(1 + mean_kg_per_day)
was applied.
The results indicate that, in the current specification, static spatial variables-namely
population within a 100 m buffer and land-use shares-have very limited explanatory
power for variations in average daily collection demand. This is reflected in the lack of
statistical significance of explanatory variables (except for the intercept), the very low
R², and the non-significant overall F-test. Variance Inflation Factor (VIF) diagnostics
confirm that multicollinearity is not an issue; therefore, the weak performance of the
model is attributable to the intrinsic limitations of static spatial predictors rather than
statistical instability.
From a methodological perspective, these findings are consistent with the nature of
urban service systems. A substantial share of demand variability in waste collection is
typically driven by temporal and operational factors, such as service frequency,
routing decisions, day-of-week and seasonal effects, container characteristics, waste
type, operational policies, and user behaviour-factors not included in the present spatial-
only specification.
the proposed model should be interpreted as a transparent and reproducible spatial
baseline rather than a fully explanatory demand model. It is suitable for structuring
subsequent analyses and for integration with higher-level decision-support models, but
it is insufficient on its own to capture daily demand dynamics. A logical next step is to
shift the unit of analysis to the bin–day level and/or to incorporate temporal,
25

## Page 26

operational, and behavioural variables, potentially complemented by separate
analyses of overflow and service performance indicators.
26
