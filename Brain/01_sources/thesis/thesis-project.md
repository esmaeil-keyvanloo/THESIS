---
name: thesis-project
title: Sensor-based Recyclables Collection Planning
type: source
category: thesis
source_file: DATA/DOCUMENT/Sensor-based Recyclables Collection Planning.docx
source_sha256: cf776b4ebe470d529d71c31b5af5073e8f65dfb3c7f3845a27949a9e760731a4
source_bytes: 5914949
ingested: 2026-08-09
words: 22258
verbatim: true
---

> Faithful conversion of `DATA/DOCUMENT/Sensor-based Recyclables Collection Planning.docx`. Do not edit — edit the source and re-run the ingest.

Sensor-based Recyclables Collection Planning

Planeamento de Recolha de Resíduos Recicláveis com Informação de Sensores

Thesis Project

PhD Program in Transportation Systems

Esmaeil Keyvanloo

Supervisor:

Professor Joao Fonseca Bigotte

Coimbra, July 2026

Abstract

Municipal Solid Waste (MSW) management has become one of the major challenges facing cities due to rapid urbanization, increasing waste generation, and the growing demand for sustainable resource management. Although municipalities have adopted various recycling strategies to improve collection efficiency, strategic planning of waste collection infrastructure remains largely dependent on deterministic assumptions that fail to capture the inherent uncertainty of waste generation. Consequently, inefficient container placement, unnecessary operational costs, and uneven service coverage continue to affect municipal waste collection systems.

This research proposes a sequential, data-driven methodology that integrates waste generation modelling with deterministic and stochastic facility location optimisation for strategic municipal solid waste container planning. The methodology establishes a direct analytical relationship between statistical demand estimation and optimisation, allowing infrastructure decisions to be based on estimated waste generation rather than simplified assumptions.

The proposed framework is demonstrated through a real-world case study in the municipality of Rio Maior, Portugal. Historical waste collection records, Geographic Information System (GIS) data, demographic information, and land-use characteristics are integrated into a unified database describing the spatial and operational characteristics of the municipal waste collection system.

Waste generation is first estimated using a Stepwise Multiple Regression model. Alternative regression specifications are evaluated according to statistical significance, explanatory power, multicollinearity, residual diagnostics, and model parsimony in order to identify the most reliable demand estimation model. The resulting regression model provides spatial estimates of municipal solid waste generation that serve as the primary input for the optimisation stage.

The estimated waste demand is subsequently incorporated into a deterministic p-median facility location model to determine suitable locations for municipal solid waste containers while minimising weighted travel distance between demand points and candidate facilities. The deterministic solution provides a baseline representation of strategic infrastructure planning under fixed demand assumptions.

Recognising that municipal waste generation is inherently uncertain, the deterministic model is further extended into a stochastic p-median formulation that explicitly considers multiple demand scenarios. By incorporating demand uncertainty into the optimisation process, the stochastic model generates more robust facility location decisions capable of maintaining satisfactory service performance under varying future waste generation conditions.

The proposed methodology contributes to the literature by establishing a unified framework that links waste generation modelling with stochastic facility location optimisation. Unlike conventional approaches that treat demand estimation and infrastructure planning independently, this research integrates both components into a coherent decision-support methodology for strategic municipal waste management.

From a practical perspective, the proposed framework provides municipalities with a systematic and evidence-based tool for improving long-term infrastructure planning, increasing operational efficiency, and enhancing the resilience of municipal waste collection systems under uncertain demand conditions. Although the methodology is demonstrated using the municipality of Rio Maior, Portugal, it is sufficiently general to be adapted to other municipalities where operational, demographic, and spatial datasets are available, thereby supporting more sustainable and data-driven municipal solid waste management strategies.

Keywords: Municipal Solid Waste; Waste Generation Modelling; Stepwise Regression; Deterministic p-Median; Stochastic p-Median.

List of Figures

List of Tables

# Introduction

## Background and Rationale

Municipal Solid Waste (MSW) plays a critical role in modern urban infrastructure, profoundly determining outcomes in public health, environmental integrity, and municipal service delivery (Abubakar et al., 2022). The convergence of rapid urbanization, increasingly stringent climate commitments, and the global transition towards a circular economy intensified the unprecedented need for innovative and adaptive solutions for waste management. International forecasts highlight the magnitude scale of this challenge: municipal solid waste generation is expected to increase from 2.1 billion tons in 2023 to 3.8 billion tons by 2050, with corresponding management expenditures-invisible environmental and health considerations aside-expected to nearly double from USD 361 billion to USD 640 billion per year under business-as-usual assumptions(UNEP, 2024). In parallel, international sustainability agendas, including the European Green Deal, the Circular Economy Action Plan, and the Sustainable Development Goals (SDGs), have intensified the need for more efficient, adaptive, and environmentally sustainable waste management systems. In this context, Recyclables Waste Collection (RWC) has become a critical component of modern urban infrastructure due to its direct relationship with material recovery, landfill reduction, greenhouse gas mitigation, and resource efficiency.

Studies further indicate that effective implementation of circular economy principles - including the decoupling of waste generation and economic growth through prevention strategies, sustainability-oriented business models, and door-to-door collection systems and distributed bring points - can reverse this trend and generate approximately USD 108.5 billion in net savings annually by mid-century. Under this dynamic context, its Recyclables Waste Collection (RWC), encompassing paper, plastics, and glass- waste stream has gained special significance, serving both as a tool to reducing landfill dependency and a supporting for material recovery systems aligned with European Union sustainability targets (UNEP - UN Environment Programme, 2024)

The European Union (EU) set legally binding waste-management targets in two flagship laws and regulatory frameworks. The Waste Framework Directive has been revised as 2008/98/EC and makes it compulsory for Member States to have progressively stringent targets for recycling their municipal waste: at least 55% by 2025, 60% by 2030, and 65% by 2035 (European Commission [EC], n.d.). The Waste Framework Directive is joined by the respective recycling targets with the Landfill Directive 1999/31/EC as adapted with Directive (EU) 2018/850 as making it compulsory that the percentage of municipal wastages that go on landfill below 10% by 2035 targets (European Commission, 2025) In addition, the EU waste hierarchy prioritizes prevention, reuse, recycling, and minimization of landfill disposal (European Parliament & the Council, 2008)

Despite these policy initiatives, implementing sustainable waste management across Europe remains a significant challenge, exposing persistent structural weaknesses in waste management systems. Portugal reflects many of these challenges. Although several national initiatives and strategic plans, including the Strategic Plan for Urban Waste Management 2030 (PERSU 2030), have been introduced to improve municipal waste management performance, the country's recycling rate remains below the European Union average, while its reliance on landfill disposal continues to be relatively high(Resolution of the Council of Ministers No. 30/2023 approving the Strategic Plan for Urban Waste Management 2030 (PERSU 2030), 2023).

The European Environment Agency's 2023 early warning review chronicled troubling evidence of pandemic-scale problems across domains: 18 Member States endanger meeting the 55% municipal waste recycling targets by 2025, and 19 do likewise with the 50% plastic packaging recycling goal(EEA, 2023). The persistence of such problems is especially vexing - of 18 nations at risk for the 2025 municipal waste goal, 14 had also missed the prior 50% 2020 target goal (EEA, 2023). This trend indicates that the problem is not an instance of temporary backsliding but signals deep-seated structural mismatches between ambition and system capabilities (EEA, 2023). Despite the EU's directive's actual transposition, many Member States remain challenged in their fragmented collection systems, inadequately developed treatment facilities, and in their limited usage of monetary instruments like Extended Producer Responsibility (EPR) and Pay-As-You-Throw (PAYT) regimes (EEA, 2023; JRC, 2024; UNEP-IETC, 2024). Furthermore, chronic discrepancies in data reporting and performance monitoring gaps continue to erode transparency and frustrate adaptive policy interventions (EC, 2018; EEA, 2023). Overlaying these institutional deficiencies is the flawed characteristic of packaging waste, its multifaceted composition and low quality in terms of recyclable design often result in high losses in sorting and circumscribe the efficacy of the recycling process (EEA, 2023). Closing this chronic implementation gap will require not small bursts of improvement, but a systemic revolution in waste governance regimes, infrastructural capacity, and market-oriented incentive mechanisms(EEA, 2023)

In Southern Europe, including  Portugal, many municipalities persist to operate traditional “blind collection” systems based on fixed schedules and predetermined routes (Johansson, 2006). These systems operate independently of real-time operational conditions and do not take critical variables such as actual fill levels of containers, traffic flows, and neighborhood segregation patterns of waste collection into consideration. The separation of such systems yields three related inefficiencies. First, over-servicing happens with the emptying of containers even though there are minimal fill levels, which results in unnecessary vehicle journeys and fuel costs(Johansson, 2006). Second, under-servicing happens with unexpected surges in waste overfilling the capacity of containers, which leads to overflow incidents having negative impacts on sanitation and public trust (Johansson, 2006). Third, inefficient routing of waste collection vehicles has been shown to increase operational expenditures and emission levels, thereby exerting additional pressure on environmental sustainability.(Johansson, 2006).

These challenges are also evident in Portugal. Between 2013 and 2020, municipal waste generated grew by around 15%, surpassing the 5-million-ton milestone in 2023, to a level almost unchanged from the year earlier (Martinho, 2025). Despite the introduction of several policy provisions for the Strategic Plan for Municipal Waste (PERSU 2030), recycling rates remain relatively low, reaching just 32% in 2023, considerably below the European Union’s target of 55% for 2025 (Candeias, 2025; Martinho, 2025). Approximately 76% of municipal waste remains dumped in unsorted containers, and ultimately directed to landfills (Martinho, 2025). In addition, modest progress has been seen in the implementation of collection for the separately collected organic (bio-)waste, required across the nationwide since January 2024, with implementation at effective rates of just 43% of municipalities, showing serious infrastructure and governance weaknesses (Candeias, 2025). Similarly, about 57% of urban waste ended up at landfills even in 2022, not justifying the overwhelming dependence on this dumping strategy for Portugal (Candeias, 2025).commenting on both sides, both authors emphasize reunification efforts, especially expanding the coverage of Pay-As-You-Throw (PAYT) schemes, and environmental education efforts, especially among younger generations, to enhance recycle of municipal waste management performance for Portugal, align European sustainability target .

Improving the efficiency of municipal waste collection requires a decision-making framework that integrates strategic, tactical, and operational planning rather than treating them as independent processes. Waste generation is highly dynamic and influenced by factors such as population changes, seasonal tourism, consumption patterns, and unforeseen events, making traditional collection strategies increasingly inadequate (Esmaeilian et al., 2018). At the strategic level, municipalities must determine the optimal location and density of waste containers and monitoring infrastructure, as these decisions directly affect service accessibility and overall system performance. Tactical planning should then translate these long-term decisions into adaptive collection schedules and resource allocation that respond to fluctuations in waste generation. At the operational level, routing decisions should make use of real-time information to minimize unnecessary trips, reduce operational costs, and prevent container overflows, since fixed collection schedules rarely reflect actual waste generation patterns (Esmaeilian et al., 2018). Despite this close interaction across decision levels, much of the existing literature continues to examine facility location, inventory management, and vehicle routing as separate optimization problems. As a result, many proposed models fail to capture the interdependencies that characterize real municipal waste collection systems, creating a gap between theoretical optimization and practical implementation (Esmaeilian et al., 2018; Estay-Ossandon & Mena-Nieto, 2018). Developing integrated decision-support frameworks that address these planning levels simultaneously under uncertainty is therefore essential for improving the efficiency, flexibility, and long-term sustainability of smart municipal waste collection systems.

Effective municipal solid waste (MSW) collection depends on decisions made well before collection begins. The planning stage establishes many of the conditions that determine how efficiently the system will perform over time. Decisions about the location and density of waste containers, the use of monitoring technologies, and the organisation of collection services influence both the quality and reliability of collection. Despite sustained efforts across the European Union to strengthen municipal waste management, several Member States are still expected to fall short of the 2025 recycling targets. Persistent shortcomings in collection infrastructure, limited monitoring capacity, and weak coordination across planning levels continue to hinder progress (European Environment Agency, 2025). These challenges point to the importance of looking beyond day-to-day operations. Improving MSW collection also depends on strategic and tactical decisions that guide infrastructure development, monitoring practices, and the effective allocation of resources. Previous studies have shown that these planning decisions shape service quality, resource utilisation, and the overall performance of municipal waste collection systems (De Morais et al., 2024). This perspective has encouraged researchers to adopt integrated optimisation frameworks that examine infrastructure planning, monitoring strategies, and collection planning as connected elements of the same decision-making process, particularly under conditions of uncertainty and changing waste generation patterns (De Morais et al., 2024). Rio Maior provides a useful setting for investigating these questions. As a medium-sized municipality with limited institutional capacity, it faces planning constraints similar to those experienced by many local authorities, making it an appropriate case for examining how strategic and tactical planning can improve the efficiency and resilience of municipal waste collection systems.

From a methodological perspective, research on waste collection optimization is still remains fragmented. Although there is operational evidence that decisions on facility location, inventory planning, and routing are highly interconnected and jointly determine real-world performance, most studies still consider these issues in isolation from one another (Ramos et al., 2018). The neglect of such links leads to predictable inefficiencies: static routing, in the absence of fill-level information, yields unnecessary mileage, premature collections, and occasional overflow, as illustrated in empirical sensor-based case studies (Ramos et al., 2018). Furthermore, deterministic planning approaches still remain dominant even the inherently uncertain nature of waste generation that is highly variable and difficult to forecast. This limitation reduces the capability of current models to represent real operational dynamics accurately.

Another important challenge relates to the implementation and monitoring systems in small and medium-sized municipalities. Institutional evidence clearly shows that these municipalities, while being the majority of local authorities, are generally understudied and lacking in the financial, technical, and institutional capacities and limitations that restrict the adoption of advanced technologies and optimization frameworks required to adopt advanced optimization or monitoring tools. Various studies conducted in Indonesia make this contrast very clear. For example, a small city like Mojokerto suffers from a very limited budget, inadequate equipment, and centralized decision structures, while a larger city like Surabaya boasts of better cooperation mechanisms, more diversified funding, and greater technological readiness (Wibisono et al., 2020) .Similar capacity gaps are reported across other developing-country contexts. Taking all these insights together, there is an obvious need for integrated, uncertainty-aware optimisation frameworks that orchestrate strategic siting, tactical planning, and operational routing while remaining adaptable to structural constraints of small and medium municipalities.

The rationale for this analysis comes from five different but interrelated forces that are directing contemporary waste-management policy and practice. The first one is the global sustainability goals along with the climate-related imperatives that are increasingly pushing countries towards the adoption of waste governance that is more resource-efficient and adaptive to the changes (OECD, n.d; UNEP, n.d.). The second one is the binding recycling and landfill reduction targets of the European Union that are still in danger, with the European Environment Agency mentioning that some Member States will probably not meet the 2025 municipal-waste recycling goals (EEA, 2023). The third one is the situation of Portugal, which is still showing structural weaknesses in its waste-management system as the national recycling, separate-collection, and material-recovery rates are continually below the EU averages   (Candeias, 2025; Martinho, 2025). The fourth reason is the evidence from the local governments that involves case studies of recyclable-waste operations in Portugal shows that operational inefficiencies like overflow, premature collection, and unnecessary mileage still occur when collection is not supported by real-time or data-driven methods (Ramos et al., 2018). The last reason is even though these three layers are operationally interdependent, the academic literature still does not have integrated, multi-level optimisation frameworks that are capable of concurrently dealing with strategic siting, tactical planning, and real-time routing under uncertainty (De Morais et al., 2024; Ramos et al., 2018).

This research project is developed within the broader framework of the WSmartRoute+ project, which investigates a new paradigm for intelligent and sustainable recyclable waste collection through advanced optimization, sensor integration, predictive modelling, dynamic routing, and data-driven operational planning. The project explores different forms of data acquisition, including static sensors, mobile sensors, and drivers’ visual observations, combined with forecasting models and optimization methods to improve operational efficiency, resource utilization, and service levels. Within this broader context, the present research work focuses on the development of integrated stochastic and adaptive optimization frameworks for municipal recyclable waste collection systems operating under uncertain and dynamically evolving urban conditions.

Against this background, Smart Waste Management (SWM) emerges as a promising and forward-looking response to contemporary municipal waste challenges. Besides being a purely technological enhancement, SWM is understood as an integrated governance paradigm, which links IoT-based monitoring, predictive analytics, and stochastic optimization within a unified decision-support framework. This approach aligns with global policy and research trends, where adaptive, data-driven, and resource-efficient waste systems are increasingly considered vital to meet sustainability and circular-economy policy , which increasingly emphasize adaptive, data-driven, and resource-efficient waste-management systems. (OECD, n.d; UNEP, n.d.). In this light, the this preliminary research work advances a multi-level stochastic optimization framework that bridges the strategic siting, tactical planning, and operational routing problems, hence making contributions to methodological advancement and practical improvement of municipal waste-collection performance.

More specifically, this research investigates the transition from deterministic to stochastic approaches for strategic municipal solid waste (MSW) collection planning. The proposed methodology integrates waste generation modelling with facility location optimisation through a sequential modelling framework. Waste generation is first estimated using demographic characteristics, land-use patterns, and other relevant explanatory variables. These estimates are then incorporated into deterministic p-median facility location models to identify suitable locations for municipal solid waste containers. The deterministic formulation is subsequently extended to a stochastic p-median model, allowing uncertainty in waste generation to be explicitly incorporated into the optimisation process and supporting more robust strategic location decisions under different demand scenarios.

The proposed methodology contributes to the literature by establishing a direct link

between waste generation modelling and stochastic facility location optimisation within a unified analytical framework. By incorporating demand estimates into the optimisation process, it enables strategic infrastructure planning to account for both expected waste generation and demand uncertainty. This integrated approach supports more informed and robust facility location decisions while providing a practical framework for improving the long-term efficiency, resilience, and sustainability of municipal solid waste collection systems. Its applicability is demonstrated through a real-world case study, illustrating its potential to support evidence-based strategic planning in municipal waste management.

Figure ‎1.1. Risk assessment of EU Member States for meeting municipal and packaging waste recycling targets (European Environment Agency, 2023). source: https://www.eea.europa.eu/publications/many-eu-member-state

Figure ‎1.2.Recycling rates in Europe by waste stream, source: https://www.eea.europa.eu/en/analysis/indicators/waste-recycling-in-europe?utm_source=chatgpt.com&activeAccordion=546a7c35-9188-4d23-94ee-005d97c26f2b

Figure ‎1.2.Recycling rates in Europe by waste stream, source: https://www.eea.europa.eu/en/analysis/indicators/waste-recycling-in-europe?utm_source=chatgpt.com&activeAccordion=546a7c35-9188-4d23-94ee-005d97c26f2b

Figure ‎1.3.Municipal waste recycling rates in Europe by country , https://www.eea.europa.eu/en/analysis/indicators/waste-recycling-in-europe?utm_source=chatgpt.com&activeAccordion=546a7c35-9188-4d23-94ee-005d97c26f2b

## Motivation and Significance of Research

The motivation for this research arises from the need to improve the way municipalities plan recyclable waste collection infrastructure under increasingly dynamic and uncertain conditions. Although considerable progress has been made in waste collection technologies and optimisation methods, many municipal planning decisions continue to rely on simplified assumptions regarding waste generation and infrastructure demand. As a result, strategic decisions concerning the location of recyclable waste containers often fail to adequately represent the spatial variability of waste generation, reducing the overall efficiency of collection systems.

A major research challenge is that waste generation modelling and facility location optimisation are frequently investigated as separate problems. In practice, however, these two components are intrinsically linked, since the estimation of waste demand constitutes the primary input to facility location models. Ignoring this relationship may lead to infrastructure decisions that are based on unrealistic or oversimplified demand assumptions. Consequently, there is a clear need for methodologies that explicitly integrate demand estimation with strategic infrastructure planning.

Accordingly, this research proposes a sequential analytical framework in which recyclable waste demand is first estimated through statistical regression modelling and subsequently incorporated into deterministic and stochastic p-median facility location models. This approach establishes a direct methodological connection between demand estimation and infrastructure optimisation, enabling facility location decisions to be based on predicted waste generation rather than simplified average demand assumptions. The deterministic model provides a baseline planning solution, while the stochastic formulation extends the analysis by explicitly considering uncertainty in future waste generation.

The significance of this research is both methodological and practical. Methodologically, it integrates statistical demand modelling with facility location optimisation within a unified analytical framework for municipal solid waste management. Practically, the proposed methodology provides municipalities with a structured and data-driven approach for supporting strategic infrastructure planning, improving the allocation of recyclable waste containers, and enhancing the efficiency and robustness of municipal waste collection systems. Although the methodology is demonstrated using the municipality of Rio Maior, Portugal, its analytical framework is sufficiently general to be adapted to other municipalities where comparable demographic, spatial, and operational data are available.

## Research Question and Research Objectives

### Research Context within the WSmartRoute+ Project

This PhD research is conducted within the broader context of the WSmartRoute+ project, funded by the Portuguese Foundation for Science and Technology (FCT). Although the WSmartRoute+ project encompasses several research topics related to smart municipal solid waste management, this preliminary research work focuses specifically on waste generation modelling and strategic facility location optimisation for municipal solid waste containers.

This research investigates how municipal solid waste generation can be estimated using demographic, spatial, and land-use characteristics, and how these demand estimates can subsequently be incorporated into deterministic and stochastic p-median facility location models to support strategic infrastructure planning under demand uncertainty.

Accordingly, preliminary research work represents a focused component of broader WSmartRoute+ project while maintaining a coherent and feasible scope for research.

### Main Research Question

The central research question guiding this preliminary research work is:

How can waste generation modelling be integrated with deterministic and stochastic p-median facility location models to improve strategic municipal solid waste container planning under demand uncertainty?

To address this question, this preliminary research work is organized around three complementary research components:

- System Characterisation, involving the analysis of the existing municipal solid waste collection system, including its spatial configuration and operational characteristics;
- Waste Generation Modelling, aimed at estimating municipal solid waste demand using demographic characteristics, land-use patterns, and other relevant explanatory variables;
- Facility Location Optimisation, through the development of deterministic and stochastic p-median models to determine suitable locations for municipal solid waste containers while explicitly accounting for demand uncertainty.

### Research Objectives

The overall objective of this preliminary research workis to develop a methodology that combines waste generation modelling with deterministic and stochastic p-median facility location models to improve the strategic planning of municipal solid waste container locations under demand uncertainty.

To achieve this objective, the this preliminary research work pursues the following specific objectives:

Objective 1 – System Characterisation

Characterise and analyse the existing municipal solid waste collection system by examining its spatial configuration, operational characteristics, and the datasets required for subsequent modelling.

Objective 2 – Waste Generation Modelling

Develop and validate statistical waste generation models using demographic characteristics, land-use patterns, and other relevant explanatory variables to estimate the spatial distribution of municipal solid waste demand.

Objective 3 – Deterministic Facility Location Optimisation

Develop a deterministic p-median facility location model to determine the suitable locations for municipal solid waste containers based on the estimated waste demand.

Objective 4– Stochastic Facility Location Optimisation

Extend the deterministic p-median model to a stochastic formulation that explicitly accounts for uncertainty in waste generation, thereby supporting more robust strategic facility location decisions under demand uncertainty.

Finally, this preliminary research work seeks to strengthen the link between waste generation modelling and strategic facility location optimisation by developing a data-driven methodology for municipal solid waste infrastructure planning under demand uncertainty. Logical Research Framework

## Methodological Framework

This preliminary research work adopts a sequential, data-driven methodological framework that integrates waste generation modelling with deterministic and stochastic p-median facility location optimisation to support the strategic planning of municipal solid waste (MSW) container locations under demand uncertainty.

The proposed methodology follows a structured sequence in which the output of each stage provides the required input for the subsequent stage. This sequential organisation establishes a clear relationship between system characterisation, waste generation modelling, demand estimation, and facility location optimisation, thereby ensuring consistency between the research objectives, analytical methods, and optimisation models.

### Stage 1 - System Characterisation and Data Integration

The research begins with a comprehensive characterisation of the existing municipal solid waste collection system in Rio Maior, Portugal. This stage establishes the database required for the subsequent analyses by integrating historical waste collection records, GIS-based spatial information, and demographic datasets.

Historical waste collection records provide information on waste quantities, collection activities, and container characteristics. GIS data provide the spatial attributes required for the analysis, including container locations, land-use characteristics, service areas, and other geographical variables. Demographic datasets provide population-related information associated with each service area. These datasets are integrated at the container level to produce a unified database suitable for statistical modelling and optimisation.

### Stage 2 – Waste Generation Modelling

The second stage focuses on estimating municipal solid waste generation. Historical waste collection records provide the observed waste generation, while demographic characteristics, land-use variables, and other spatial attributes are used as explanatory variables.

A Stepwise Multiple Regression approach is employed to identify statistically significant predictors of waste generation and to develop a parsimonious demand estimation model. The calibrated regression model produces estimated waste demand for each service area, which subsequently serves as the primary input for the facility location optimisation models.

### Stage 3 – Deterministic Facility Location Optimisation

The estimated waste demand obtained from the regression model is incorporated into a deterministic p-median facility location model. The deterministic formulation assumes fixed demand throughout the planning horizon and identifies suitable locations for municipal solid waste containers by minimising the weighted accessibility cost between demand points and candidate facilities.

This stage establishes a baseline solution against which the influence of demand uncertainty can subsequently be evaluated.

### Stage 4 – Stochastic Facility Location Optimisation

Municipal solid waste generation is inherently uncertain because waste production varies according to demographic, seasonal, and spatial factors. To account for this uncertainty, the deterministic p-median formulation is extended to a stochastic facility location model that explicitly incorporates multiple demand scenarios derived from the waste generation model.

The stochastic formulation provides more robust facility location decisions by considering possible variations in future waste demand. The deterministic and stochastic solutions are subsequently compared to evaluate the influence of demand uncertainty on strategic infrastructure planning.

### Logical Research Framework

The overall methodological sequence adopted throughout this preliminary research work is illustrated in Figure 1.X. The framework summarises the logical relationship between the successive research stages, from data integration and waste generation modelling to deterministic and stochastic facility location optimisation.

Historical Waste Collection Records

↓

GIS-Based Spatial Data

↓

Demographic Data

↓

System Characterisation and Data Integration

↓

Waste Generation Modelling (Stepwise Multiple Regression)

↓

Municipal Solid Waste Demand Estimation

↓

Deterministic p-Median Facility Location Model

↓

Stochastic p-Median Facility Location Model

↓

Comparison of Deterministic and Stochastic Solutions

↓

Strategic Planning of Municipal Solid Waste Container Locations

*Figure ‎1.4. Logical Research Framework*

The proposed framework represents the core methodological contribution of this preliminary research work. Historical waste collection records, GIS-based spatial information, and demographic datasets are integrated to develop statistical models of municipal solid waste generation. The resulting demand estimates constitute the primary input to both deterministic and stochastic p-median facility location models. The deterministic model establishes a baseline solution under fixed demand assumptions, whereas the stochastic model explicitly incorporates demand uncertainty to obtain more robust facility location decisions. Comparing the two formulations enables the influence of demand uncertainty on strategic facility location planning to be evaluated and provides a structured methodology for supporting long-term municipal solid waste infrastructure planning.

## Thesis Project Structure

This preliminary research work is organised around a sequential and coherent research framework that integrates system characterisation, municipal solid waste generation modelling, and facility location optimisation for municipal solid waste containers under demand uncertainty. The research follows a progressive methodology in which the output of each chapter provides the necessary input for the subsequent stage, thereby ensuring methodological consistency throughout the thesis project. The overall objective is to develop a robust decision-support framework for the strategic planning of municipal solid waste collection infrastructure in the municipality of Rio Maior, Portugal.

Chapter 1 introduces the research background, motivation, research questions, research objectives, and the methodological framework adopted throughout this preliminary research work. It also defines the scope of the research and explains the logical relationships between the different research stages.

Chapter 2 presents a comprehensive characterisation of the existing municipal solid waste collection system in Rio Maior. The chapter describes the study area, demographic characteristics, land-use patterns, municipal infrastructure, recyclable waste container locations, historical waste collection records, and the available GIS and operational datasets. This chapter establishes the integrated database required for the subsequent modelling and optimisation stages.

Chapter 3 focuses on municipal solid waste generation modelling. Demographic, spatial, and land-use variables are analysed using a Stepwise Multiple Regression approach to identify statistically significant predictors of waste generation. The selected regression model is then used to estimate municipal solid waste demand for each service area. These estimated demand values constitute the primary input to the facility location optimisation models developed in the following chapter.

Chapter 4 develops deterministic and stochastic p-median facility location models for the strategic allocation of municipal solid waste containers. First, a deterministic p-median model is formulated to identify suitable container locations under fixed demand conditions. Subsequently, the deterministic formulation is extended to a stochastic p-median model that explicitly incorporates demand uncertainty through multiple demand scenarios. Finally, the deterministic and stochastic solutions are compared to evaluate the influence of uncertainty on strategic facility location decisions.

Chapter 5 presents the results and discussion of the proposed methodology. The chapter evaluates the statistical performance of the waste generation model, analyses the optimisation results obtained from the deterministic and stochastic p-median formulations, compares both modelling approaches, and discusses the practical implications of the findings for strategic municipal solid waste infrastructure planning under demand uncertainty.

Chapter 6 summarises the main conclusions of this preliminary research work. The chapter highlights the principal scientific and methodological contributions, discusses the limitations of the proposed approach, and identifies directions for future research, particularly regarding the further development of integrated optimisation models and advanced decision-support methodologies for municipal solid waste management.

*Figure ‎1.5. conceptional outline of PhD thesis structure*

*Figure ‎1.5. conceptional outline of PhD thesis structure*

# STATE OF THE ART

## Recyclables Waste Collection (RWC)

### Transition to a Circular Economy in Waste Management

The transition from the traditional linear model ("take–make–dispose") to a Circular Economy (CE) represents a fundamental transformation in production, consumption, and waste management systems. According to the European Parliament, the Circular Economy is a model of production and consumption that promotes sharing, leasing, reusing, repairing, refurbishing, and recycling products and materials to extend their life cycles and reduce waste generation (European Parliament, 2024). By keeping materials in use for as long as possible, valuable resources remain within the economy through recycling and recovery whenever feasible, thereby reducing the demand for primary raw materials and supporting more sustainable resource use (European Parliament, 2024).

The Ellen MacArthur Foundation complements this perspective by defining the Circular Economy as “a system where materials never become waste and nature is regenerated.” According to the Foundation, products and materials should remain in circulation through maintenance, reuse, repair, refurbishment, remanufacturing, recycling, and composting. It further identifies three fundamental principles of a circular economy: eliminating waste and pollution by design, circulating products and materials at their highest value, and regenerating natural systems   (Ellen MacArthur Foundation, n.d.). These principles provide a practical framework for designing more sustainable production, consumption, and municipal solid waste management systems.

the Circular Economy Action Plan under the European Green Deal and waste management systems made operationally relevant at the level of EU policy. The Plan declares that “high-quality recycling depends on the effective separate waste collection,” thus making the performance of collection a prerequisite condition for achieving circular economy goals. It also indicates that wherever separate collection systems are in place, “their efficiency varies considerably,” and that these differences are linked to the factors like density, accessibility, and convenience of collection points as well as to the participation of residents (European Commission, 2020). This policy framing supports the interpretation of waste collection not just as a logistical operation, but as a necessary core enabler component for the circular material flows.

The empirical monitoring evidence at the EU level supports this perspective. Eurostat reports that the disparities in waste production volumes among different countries “are not only determined by consumption patterns and the economic situation but also by the different methods of municipal waste collection and managed” (Eurostat, 2025). In 2023, the average municipal waste generated was 511 kg per capita in the EU, out of which 48% went through material recycling and composting treatment, while 22% was landfill. Eurostat, looking at the period of time ahead, reports that “even though the generation of waste has increased,” the “total municipal waste going to landfills has decreased,” with the landfill share decreasing from 61% in 1995 to 22% in 2023 (Eurostat, 2025). These observed trends provide empirical evidence for the claim that collection and management practices play a major role in the diversion of waste to landfills and to higher recycling rates.

In Portugal, the shift to a circular economy in the management of municipal waste has been made official by the Strategic Plan for Municipal Waste 2030 (PERSU 2030), which was approved by Resolution of the Council of Ministers n.º 31/2023. The legal document frames circular economy policy within the framework of the main goal of separating economic growth from resource use and of reintegrating more materials into the economy. It declares that the plan will lead to the prevention of waste and to an increase in preparation for reuse, recycling, or other forms of recovery- consequent use of primary raw materials would be reduced. Importantly for the municipality, PERSU 2030 “is concentrating on the reinforcing of selective collection in order to improve the quality of recovered waste,” and it is putting this explicitly as “an essential condition” for the higher-value added products to be obtained. Further, the plan also has a target for landfill diversion by 2035, municipal waste deposited in landfill be reduced to a maximum of 10% of total municipal waste produced (Agência Portuguesa do Ambiente, 2022; Ministry of Environment and Energy of Portuga, 2025; Portuguese Presidency of the Council of Ministers, 2023)

From a theoretical perspective, the Circular Economy can be interpreted through systems thinking and urban metabolism concepts, which emphasise closing material loops, reducing resource losses, and maintaining materials in productive use for as long as possible  (Kennedy et al., 2011; Meadows, 2009). Within this perspective, municipal solid waste collection is not merely an operational activity but an essential component of urban resource management. Efficient collection infrastructure and effective separate collection systems facilitate material recovery and contribute to achieving Circular Economy objectives.

the literature indicates that achieving a Circular Economy depends not only on recycling technologies but also on efficient and accessible separate collection systems. Policy initiatives such as the Circular Economy Action Plan and PERSU 2030 highlight that high-quality recycling begins with effective waste collection infrastructure. Consequently, understanding waste generation patterns and improving the strategic planning of municipal solid waste collection systems are essential for increasing recycling rates, reducing landfill disposal, and supporting the transition towards a Circular Economy (European Commission, 2020; European Parliament, 2024; Eurostat, 2025; Portuguese Presidency of the Council of Ministers, 2023).

Figure ‎2.1.Difference between linear economy and Circular economy, source: https://remade-project.eu/index.php/what-is-remadeari/our-mission-circular-economy/

Figure ‎2.2.Recycling rate of municipal waste in European Union , source: https://ec.europa.eu/eurostat/databrowser/view/sdg_11_60/default/line?lang=en

Figure ‎2.3.average municipal waste generated per capita in the EU countries in 2023, source:https://ec.europa.eu/eurostat/databrowser/view/env_wasmun/default/bar?lang=en

### Recyclables Waste Collection System Design

Based on the circular economy concept explained in Section 3.1.2, the design of the recyclables waste collection (RWC) system can be treated as a practical interface connecting policy intent and material outcomes. The main question is not if separate collection exists in theory, but whether the collection system is convenient, reliable, and configured in such a way that it protects material quality. This matches with EU policy logic: high-quality recycling depends on effective separation collection waste, and collection performance of which is influenced by different factors such as the density and accessibility, usability of collection points and the level of participation of residents.(European Commission, 2020). Empirical monitoring evidence supported This interpretation, with Eurostat's statement that recycling performance differences among Member States “also depend on municipal waste collection and management practices,” being one of the arguments in Favor of the interpretation(Eurostat, 2025). Within a circular economy framework, waste collection is not merely a logistical activity but a critical mechanism for maintaining material loops and ensuring that recyclable materials re-enter the economic cycle with minimal quality loss.

The service architecture is the first design decision in recyclable waste collection systems since it determines the behavioural expectations and the logistical baseline for subsequent operational choices. At the European level, municipal waste is primarily collected through two dominant service architectures: drop-off systems (bring banks or igloo schemes) and curb side collection systems (door-to-door service), which are often combined in hybrid configurations in cities with mixed housing typologies. (European Commission, 2020; European Environment Agency, 2023). Monitoring of the actual situation has proven that differences in recycling performance among the Member States are “not only influenced by patterns of consumption and economic conditions but also by the way municipal waste is collected and managed”(Eurostat, 2025). This evidence supports the interpretation of collection system architecture as a structural driver of recycling performance, rather than a secondary operational choice.

Within the service architecture selected, the next key decision is related to stream configuration, which refers to the number of fractions households have to separate and the type of collection system that is used, whether it is multi-stream, two-stream, or commingled collection. This practical trade-off remains consistent across contexts. An increasing number of separated streams can improve the material quality, and at the same time, the more difficult and riskier it is with regard to mis-sorting. On the other hand, combined systems, while reducing the effort for households, tend to shift the problem of controlling contamination to the sorting facilities downstream. EU policy emphasizing high-quality recycling implicitly forces the designers to consider the convenience and correctness side by side instead of only working with collection cost or participation rates (European Commission, 2020).

At this stage, network design becomes a public service issue rather than just a technical matter. Container density, their arrangement spacing, and the co-locating of them should be determined based on the levels of accessibility and the expected material yields, rather than by legacy placement patterns. The same policy logic that links the performance variation to the density and the accessibility of the collection points also implies that the poorly spaced infrastructure may limit participation and increase contamination and overflow, even when adequate treatment capacity downstream exists. In practical terms, system performance is shaped by how easy it is for residents to do the right thing consistently, especially in multi-family residential areas where in-home storage space is limited and walking distances become critical.(European Commission, 2020; European Environment Agency, 2025)

Container capacity and collection frequency should be planned in a coordinated manner to ensure that collection infrastructure can adequately respond to expected waste demand. Appropriate decisions regarding these design parameters improve the efficiency and reliability of municipal solid waste collection systems while supporting higher recycling performance. Consequently, they represent important strategic considerations in the design of effective waste collection infrastructure (European Commission, 2020; European Environment Agency, 2023).(European Commission, 2020; European Environment Agency, 2023).

From a strategic planning perspective, effective collection system design requires a clear understanding of waste generation patterns and their spatial distribution. Estimating waste demand therefore becomes a prerequisite for facility location optimisation, as the resulting demand estimates provide the primary input to deterministic and stochastic p-median models for strategic municipal solid waste container planning.

Governance arrangements and incentive mechanisms are important components of municipal solid waste collection system design because they encourage citizen participation and improve the performance of separate collection systems. Together with accessible and reliable collection infrastructure, these measures support higher recycling rates and contribute to the objectives of the Circular Economy and Portugal's PERSU 2030 strategy.(European Environment Agency, 2023; Portuguese Presidency of the Council of Ministers, 2023). effective waste collection systems require not only appropriate infrastructure but also supportive governance and active public participation to improve recycling performance.

Figure ‎2.4. Conceptual framework illustrating the main design components of recyclable waste collection systems within the Circular Economy. The framework highlights the relationships between service architecture, stream configuration, network design, container capacity, governance mechanisms, and collection performance in supporting high-quality recycling.

### Waste Generation Modelling

Waste generation modelling constitutes a fundamental component of strategicmunicipal solid waste (MSW) management because reliable estimates of current and future waste generation are essential for planning waste collection systems, designing collection infrastructure, allocating treatment capacity, and supporting long-term strategic planning. Accurate estimation of waste generation provides the information required for infrastructure development and resource allocation, making it one of the primary inputs for strategic waste management planning (Šomplák et al., 2023).

Municipal solid waste generation is a complex process influenced by numerous demographic, socioeconomic, spatial, and environmental factors. Previous studies have identified population, population density, land-use characteristics, household size, income level, commercial activities, urbanisation, and economic development as the principal determinants of waste generation. Since the relative importance of these variables varies according to local conditions, selecting the most relevant explanatory variables is a critical step in developing reliable prediction models (Popli et al., 2021; Šomplák et al., 2023).

A wide range of approaches has been proposed for modelling municipal solid waste generation, including statistical methods, time-series forecasting, machine learning algorithms, and artificial intelligence techniques. Among these approaches, regression-based models remain one of the most widely adopted because they provide transparent and interpretable relationships between waste generation and its explanatory variables while requiring relatively limited data and computational effort. Their simplicity, statistical interpretability, and practical applicability make them particularly suitable for strategic planning applications (Šomplák et al., 2023)..

Among regression-based approaches, Multiple Linear Regression (MLR) is one of the most widely used techniques for modelling municipal solid waste generation because it quantifies the relationship between a dependent variable and multiple explanatory variables simultaneously. When a large number of candidate predictors is available, stepwise multiple regression provides a systematic variable-selection procedure that identifies statistically significant variables while excluding redundant predictors, resulting in a parsimonious, statistically robust, and interpretable regression model. Consequently, stepwise regression has become a widely accepted approach for developing reliable waste generation models that support strategic planning and infrastructure design (Montgomery et al., n.d.; Popli et al., 2021).

From a strategic planning perspective, waste generation modelling and facility location optimisation are closely interconnected. Facility location models require reliable estimates of spatial waste demand to determine the appropriate location and capacity of collection infrastructure. Consequently, the quality of facility location decisions depends directly on the accuracy of demand estimation. In this preliminary research work, municipal solid waste demand is first estimated using a stepwise multiple regression model based on demographic, spatial, and land-use variables. The estimated waste demand subsequently serves as the primary input to the deterministic and stochastic p-median facility location models, thereby establishing an integrated framework for strategic municipal solid waste infrastructure planning under demand uncertainty(Daskin, 2013; Šomplák et al., 2023) .

### Demand Uncertainty and Its Implications for Facility Location Planning

Municipal solid waste generation is inherently uncertain because both the quantity and spatial distribution of waste continuously change over time. Unlike deterministic assumptions, real-world waste generation is influenced by dynamic demographic, socioeconomic, environmental, and behavioural factors that vary across locations and planning horizons. Consequently, future waste demand cannot be represented accurately by a single fixed value, making uncertainty an inherent characteristic of municipal solid waste management systems rather than an exceptional circumstance (Guerrero et al., 2013; Šomplák et al., 2023).

The magnitude and distribution of municipal solid waste are affected by numerous interacting factors. Population growth, urbanisation, household composition, income level, commercial activities, tourism, land-use changes, seasonal variations, and citizen participation in recycling programmes all contribute to temporal and spatial variability in waste generation. Since these factors evolve continuously, waste demand also changes over time, creating uncertainty for long-term infrastructure planning and resource allocation(Popli et al., 2021; Šomplák et al., 2023)

From a strategic planning perspective, demand uncertainty has important implications for the design of waste collection infrastructure. Collection facilities are generally planned for long operational lifetimes, whereas waste generation patterns may change substantially during this period. Infrastructure designed using only average or deterministic demand estimates may therefore become either underutilised or insufficient to satisfy future demand, resulting in reduced accessibility, container overflows, inefficient resource utilisation, and increased operational costs (Daskin, 2013; Snyder, 2006).

Facility location literature has consistently recognised uncertainty as one of the principal challenges in long-term infrastructure planning. As noted by Snyder (2006), facility location decisions must frequently be made despite uncertainty in demand, transportation costs, travel times, and other model parameters that evolve throughout the lifetime of the infrastructure. Similarly, robust optimisation methods explicitly account for uncertain input data by generating solutions that remain feasible and near-optimal under different future conditions, thereby reducing the risks associated with deterministic planning assumptions (Bertsimas & Sim, 2004).

These limitations indicate that deterministic facility location models alone may not adequately represent the complexity of real recyclable waste collection systems. Instead, planning approaches should explicitly incorporate demand uncertainty to improve the robustness and long-term performance of collection infrastructure. This need has motivated the development of stochastic facility location models that represent future waste generation through probabilistic or scenario-based formulations. The following section therefore reviews stochastic p-median models and their application to strategic recyclable waste collection planning under uncertain demand conditions.

### Deterministic versus Stochastic Facility Location Models

Facility location models can generally be classified into deterministic and stochastic formulations according to the assumptions made regarding input parameters. Classical deterministic models assume that demand, transportation costs, travel distances, and other model parameters are known with certainty and remain constant throughout the planning horizon. Under these assumptions, the objective is to identify facility locations that optimize a predefined performance measure, such as minimizing transportation costs or demand-weighted travel distance. Owing to their mathematical simplicity and computational efficiency, deterministic models have long formed the foundation of facility location research and have been widely applied in infrastructure planning (Daskin, 2013; Zanjirani Farahani & Hekmatfar, 2009)

Despite their widespread application, deterministic facility location models have important limitations when applied to municipal solid waste management. In practice, waste generation, transportation costs, travel times, and other planning parameters are inherently uncertain and may vary considerably over time. Infrastructure designed under fixed-demand assumptions may therefore fail to provide satisfactory performance under actual operating conditions, leading to reduced service efficiency, inadequate capacity utilisation, and increased operational costs(Snyder, 2006).

To address these limitations, stochastic facility location models explicitly incorporate uncertainty into the optimisation process. Rather than relying on a single deterministic estimate of future demand, stochastic formulations represent uncertainty through multiple demand scenarios or probability distributions, allowing planners to evaluate facility configurations under different future conditions. Consequently, stochastic models provide more reliable infrastructure decisions in environments characterised by uncertain demand and operating conditions (Snyder, 2006).

Robust optimisation represents another important approach for addressing uncertainty in facility location planning. Instead of optimising for a single demand scenario, robust optimisation seeks solutions that remain feasible and near-optimal under a range of possible parameter variations. Moreover, the approach enables decision-makers to explicitly control the level of conservatism incorporated into the optimisation model, thereby balancing solution robustness against nominal performance (Bertsimas & Sim, 2004).

For recyclable waste collection systems, where waste generation exhibits significant spatial and temporal variability, incorporating uncertainty into facility location planning is essential for improving long-term system reliability and resilience. These considerations have motivated the development of stochastic extensions of classical facility location models. Accordingly, the following section introduces the Stochastic p-Median Model, which extends the classical p-median formulation by explicitly incorporating uncertainty into facility location decisions (Bertsimas & Sim, 2004; Snyder, 2006).

### Digitalization and Sensor-Driven Innovations in RWC

Digitalization has significantly improved recyclable waste collection (RWC) systems by enabling data-driven monitoring and decision-making. Technologies such as IoT sensors, driver-based observations, and predictive analytics provide valuable information on container fill levels and waste-generation patterns, supporting more efficient planning and improved service reliability. Where large-scale sensor deployment is not feasible, forecasting models and virtual sensing approaches offer practical alternatives for estimating future collection needs. These digital technologies provide the information required to support more adaptive and intelligent recyclable waste collection systems and establish the foundation for the forecasting methods presented in the following sections.

## Facility Location

### Facility Location as the Strategic Backbone of RWC

Facility location is a strategic backbone in recyclables waste collection (RWC) since it defines the long-term spatial grid of collection points and container capacities, and this grid constrains what improvements in routing, scheduling, and operations can be realistically achieved later on. In practice, municipalities face increasing pressure to expand the separate collection streams as mandated by circular-economy policies, thus making the design of a collection-point network that operates efficiently not just an operational issue but also a core planning task (Nevrlý et al., 2021)

A key reason why facility location is strategically important is that the number of collection points is constrained by available resources. Consequently, planners must allocate a limited number of collection points across the service area while balancing multiple, often conflicting, performance objectives (Nevrlý et al., 2021). Nevrlý et al. (2021) demonstrate this challenge through a mixed-integer linear programming (MILP) model for container allocation, evaluating both single-objective and multi-objective formulations using four decision criteria representing accessibility, infrastructure investment, and operational efficiency.

The main insight is that these criteria can be opposite to one another in some instances.  Minimize the walking distance; for example, if it tends to, it leads to an increase in the number of collection points and containers, and that would escalate investment and servicing requirements; conversely, minimizing the number of collection points will lead to increased walking distance and might quite possibly undermine accessibility outcomes (Nevrlý et al., 2021). Besides, Nevrlý et al. (2021) demonstrate that the trade-off between walking distance and number of collection points can be represented through Pareto-type analysis, which is useful for the decision-makers since it poses the problem as a transparent choice among competing objectives rather than a single “optimal” answer (Nevrlý et al., 2021).

From a modeling perspective, it typically solves these strategic moves as facility location problems (FLPs) using Mixed-Integer Linear Programming (MILP). Collection sites and assigning demand nodes, like households or commercial units, are represented by binary decision variables. The p-median problem is a cornerstone of the location literature. It minimizes the weighted average distance between the waste generators and the selected facilities, directly capturing accessibility considerations (Daskin, 2013). Extensions such as the Capacitated p-Median Problem (CPMP), along with multi-material and equity-oriented variants, apply realistic constraints concerning constraints on bin capacities, heterogeneous waste streams, and service fairness, thus improving the generalizability of FLP models to real-world RWC systems (Nevrlý et al., 2021; Zanjirani Farahani & Hekmatfar, 2009).

Beyond trade-offs, the decisions on facility location must also handle uncertainty in waste generation. If the waste management system is designed only for average conditions, the real variations can lead to overflowing and unstable service. Several approaches have been proposed to address uncertainty in facility location problems, including robust and stochastic optimization models.(Bertsimas & Sim, 2004). In the particular situation of bin location under uncertain waste generation, robust bi-objective formulations can simultaneously handle (i) the investment decisions regarding location and capacity and (ii) the service implications, such as frequency of collection, enabling the planners to explore structured cost-reliability trade-offs (Rossit & Bard, 2025).

The location of the facility in RWC must be considered a planning decision with policy implications that determine the long-term performance frontier of the system. Multi-objective MILP models are appropriate when there are conflicting issues such as accessibility, investment, and operational burdens, and robust and stochastic optimization approaches provide effective tools for addressing demand uncertainty in strategic facility location planning.(Bertsimas & Sim, 2004; Nevrlý et al., 2021; Rossit & Bard, 2025).

Having established the strategic role of facility location in recyclable waste collection systems, the following section reviews the principal facility location models that provide the theoretical foundation for strategic infrastructure planning. Over the past decades, several classes of facility location problems have been proposed, each addressing different planning objectives related to accessibility, service coverage, transportation efficiency, and resource allocation. The following section reviews the most important classical facility location models that form the theoretical foundation of modern recycling infrastructure planning.

### Classical Facility Location Models

Facility Location Problems (FLPs) represent a fundamental class of optimization models concerned with the spatial allocation of infrastructure and service facilities. Within the fields of Operations Research, transportation planning, urban systems, and infrastructure management, these models are widely used to support strategic decision-making by identifying facility configurations that improve accessibility, enhance service provision, and reduce transportation and operational costs. Over the past several decades, a variety of formulations have been developed to address different planning objectives, service requirements, and resource constraints.

Among the most prominent formulations are the Set Covering Problem (SCP), which seeks to determine the minimum number of facilities required to provide complete service coverage; the Maximum Covering Location Problem (MCLP), which aims to maximize the amount of demand served within a predefined service distance under limited resource availability; the p-Center Problem, which minimizes the maximum distance between demand points and their assigned facilities in order to promote spatial equity and service accessibility; and the p-Median Problem (PMP), which minimizes the total demand-weighted distance between users and facilities, thereby improving overall system efficiency and accessibility.

Among these formulations, the p-median model has become one of the most widely applied approaches for municipal solid waste collection planning because it explicitly considers both waste demand distribution and accessibility. By minimising the demand-weighted distance between waste generators and collection facilities, the model supports efficient infrastructure planning while maintaining service accessibility. Consequently, the p-median model provides the theoretical foundation for the facility location component of this preliminary research work and is reviewed in greater detail in the following section (Daskin, 2013; Hakimi, 1964).

### The p-Median Model

Among the various facility location models available in the literature, the p-Median Problem (PMP) has become one of the most widely used approaches for infrastructure planning and service allocation. Originally introduced by Hakimi (1964), the p-median model seeks to identify the optimal location of a predefined number of facilities in order to minimize the total demand-weighted distance between demand points and service facilities. Unlike covering models, which primarily focus on ensuring service availability, the p-median model explicitly considers both the spatial distribution of demand and the travel effort required to access services. Consequently, it is particularly suitable for applications where accessibility and transportation efficiency are key planning objectives.

The classical p-median model can be formulated as follows:

Subject to:

where:

denotes the set of demand points;

denotes the set of candidate facility locations;

represents the demand associated with demand point ;

denotes the distance between demand point i and candidate location j;

is a binary variable indicating whether facility is selected;

is a binary variable indicating whether demand point  is assigned to facility ;

represents the predetermined number of facilities to be established.

The objective function minimizes the total weighted distance between demand points and selected facilities, while the constraints ensure that exactly p\ facilities are opened and that each demand point is assigned to one and only one active facility.

The p-median model offers several advantages for Recyclables Waste Collection (RWC) systems. By explicitly incorporating demand distribution into the optimization process, it supports the placement of recycling infrastructure closer to areas with higher waste-generation potential. This improves accessibility, encourages citizen participation in recycling programs, reduces travel effort, and contributes to lower operational and transportation costs. Furthermore, the model provides a flexible foundation that can be extended to incorporate capacity constraints, multiple recyclable-material streams, uncertainty, and spatial equity considerations.

Due to these characteristics, the p-median model has been extensively applied in the location of recycling containers, ecopoints, collection depots, transfer stations, and other municipal waste-management facilities. Consequently, it has become one of the most influential optimization frameworks in recyclable waste collection planning and serves as the theoretical basis for the facility location analysis developed in this research. (Daskin, 2013; Hakimi, 1964).

While the classical p-median model provides a robust foundation for recycling infrastructure planning, real-world recyclable waste collection systems are characterized by multiple waste streams, capacity limitations, spatial heterogeneity, and uncertainty in future demand. These practical considerations have motivated the development of more advanced facility location formulations capable of addressing the complexity of modern waste-management systems.

### Stochastic p-Median Models

The classical p-median model assumes that demand is known and remains constant throughout the planning horizon. While this assumption simplifies the optimisation process, it is rarely satisfied in real municipal solid waste (MSW) collection systems. In practice, waste generation varies over time due to demographic changes, land-use characteristics, seasonal fluctuations, tourism activities, economic conditions, and citizens' recycling behaviour. Consequently, facility location decisions based solely on deterministic demand estimates may not remain effective under actual operating conditions (Daskin, 2013; Snyder, 2006).

Demand uncertainty has therefore become an important consideration in strategic facility location planning. Ignoring uncertainty may result in inefficient infrastructure allocation, reduced accessibility, underutilised facilities, or insufficient collection capacity in areas experiencing higher-than-expected waste generation. As Snyder (2006) notes, demands, transportation costs, travel times, and other parameters of facility location problems are inherently uncertain over the long operational lifetime of infrastructure systems. This observation has motivated the development of stochastic facility location models that explicitly account for uncertainty in future operating conditions (Snyder, 2006).

Stochastic p-median models extend the classical deterministic formulation by representing waste demand through multiple scenarios or probability distributions rather than a single fixed estimate. Each scenario represents a plausible future realisation of waste generation, allowing planners to evaluate facility location decisions under different demand conditions. Compared with deterministic models, stochastic approaches generally provide solutions that are more robust and less sensitive to future demand variability (Birge & Louveaux, 2011).

Several stochastic programming approaches have been proposed in the facility location literature, including two-stage stochastic programming, scenario-based optimisation, chance-constrained programming, and robust optimisation (Bertsimas & Sim, 2004; Birge & Louveaux, 2011). Among these approaches, scenario-based stochastic programming has become one of the most widely adopted methods because it provides a practical representation of uncertainty while remaining computationally tractable for strategic planning applications. Robust optimisation further improves decision quality by controlling the trade-off between solution conservatism and robustness against uncertain parameter values (Bertsimas & Sim, 2004).

Recent studies have further expanded the classical stochastic p-median framework by incorporating dynamic demand patterns and robust optimisation techniques. For example, Sadeghi (Sadeghi et al., 2023) proposed a Dynamic Modified Stochastic p-Median model that simultaneously considers time-varying demand, facility relocation, and robust optimisation. Their mixed-integer linear programming formulation demonstrated that explicitly modelling uncertainty and temporal demand variation can substantially improve the reliability and adaptability of strategic location decisions under changing operating conditions.

Applications of stochastic optimisation in municipal solid waste management have also increased considerably in recent years. A recent systematic review by Alshaikh and Abdelfatah(Alshaikh & Abdelfatah, 2024) shows that optimisation models are increasingly being integrated with mathematical programming, artificial intelligence, IoT technologies, routing optimisation, and facility location planning to improve the efficiency and sustainability of waste management systems. However, the review also identifies the need for more integrated models capable of simultaneously addressing uncertainty, infrastructure planning, and operational decision-making, particularly for recyclable waste collection systems.

The performance of stochastic facility location models is commonly evaluated by comparing their solutions with those obtained from deterministic models. Performance measures such as the Value of the Stochastic Solution (VSS) and the Expected Value of Perfect Information (EVPI) are frequently employed to quantify the benefits of explicitly incorporating uncertainty into strategic planning decisions (Birge & Louveaux, 2011).

Given the inherent uncertainty associated with municipal solid waste generation, this preliminary research work adopts both deterministic and stochastic p-median models. Waste demand is first estimated through statistical waste generation modelling using demographic, spatial, and land-use variables. These demand estimates subsequently serve as the primary input to the deterministic p-median model, which provides a baseline solution for facility location planning. The deterministic formulation is then extended to a stochastic p-median model in order to explicitly account for demand uncertainty and evaluate the robustness of strategic infrastructure decisions. This sequential framework establishes the methodological foundation for the facility location analysis presented in the subsequent chapters.

# PROPOSED RESEARCH WORK / RESEARCH PLAN

## Research Work Plan

The proposed doctoral research is planned over a period of forty-eight months and follows a structured and sequential research workflow organised into seven interrelated research tasks. Each task builds upon the outcomes of the previous one, ensuring a coherent progression from system characterisation and waste generation modelling to deterministic and stochastic facility location optimisation under demand uncertainty. This integrated workflow is designed to develop a robust, data-driven decision-support framework for the strategic planning of municipal solid waste container locations.

The research begins with a comprehensive review of the scientific literature and the development of the conceptual and methodological framework. This initial stage establishes the theoretical foundation of the research by examining the current state of knowledge in municipal solid waste management, waste generation modelling, facility location optimisation, stochastic optimisation, and Geographic Information Systems (GIS). It also identifies the principal research gaps and defines the methodological approach adopted throughout this preliminary research work.

The second stage focuses on the characterisation of the existing municipal solid waste collection system in Rio Maior, Portugal. Historical waste collection records, GIS-based spatial information, demographic data, land-use characteristics, container inventories, and operational datasets are integrated into a unified analytical database. Data preprocessing, cleaning, exploratory data analysis, and spatial analysis are subsequently performed to ensure the quality, consistency, and reliability of the information used in the subsequent modelling stages.

The third stage is devoted to the development of a statistical municipal solid waste generation model using a Stepwise Multiple Regression approach. Significant explanatory variables are identified to estimate waste demand for each service area. The resulting demand estimates constitute the primary input for the deterministic and stochastic facility location optimisation models developed in the subsequent stages.

The fourth stage develops a deterministic p-median facility location model based on the estimated waste demand. This model identifies suitable locations for municipal solid waste containers under fixed demand conditions and provides a baseline solution for strategic infrastructure planning.

The fifth stage extends the deterministic formulation to a stochastic p-median facility location model that explicitly incorporates uncertainty in municipal solid waste generation through multiple demand scenarios. By accounting for demand variability, the stochastic model aims to identify more robust facility location decisions capable of maintaining satisfactory service performance under uncertain future conditions.

The sixth stage focuses on the integrated validation and evaluation of the proposed modelling framework. The statistical performance of the waste generation model is first assessed to verify the reliability of the estimated waste demand. Subsequently, the deterministic and stochastic p-median models are evaluated and compared with the existing municipal container configuration. The analysis considers accessibility, service coverage, infrastructure utilisation, computational performance, and sensitivity to demand uncertainty in order to assess the robustness and practical applicability of the proposed methodology.

The final stage is dedicated to integrating the research findings, preparing scientific publications, disseminating the results through international conferences, completing the doctoral thesis, and preparing for the doctoral thesis defence. This stage consolidates the scientific and practical contributions of the research and ensures the effective communication of the proposed methodology to both the academic community and practitioners.

## Research Tasks and Timeline

The proposed doctoral research is organised into seven sequential and interrelated research tasks over a period of forty-eight months. Together, these tasks establish a coherent research workflow that progresses systematically from literature review and system characterisation to waste generation modelling, deterministic and stochastic facility location optimisation, model validation, and the dissemination of research outcomes. Each task contributes directly to the overall objective of developing a data-driven decision-support framework for the strategic planning of municipal solid waste container locations under demand uncertainty.

Task 1 – Literature Review and Conceptual Framework

The first task consists of conducting a comprehensive review of the scientific literature and establishing the conceptual and methodological framework of the research. This task examines the current state of knowledge in municipal solid waste management, waste generation modelling, facility location optimisation, stochastic optimisation, and Geographic Information Systems (GIS). It also identifies the principal research gaps and defines the research methodology adopted throughout this preliminary research work.

Task 2 – System Characterisation

The second task focuses on characterising the existing municipal solid waste collection system in Rio Maior, Portugal. Historical waste collection records, GIS-based spatial information, demographic data, land-use characteristics, road network information, container inventories, and operational datasets are integrated into a unified analytical database. Data preprocessing, cleaning, exploratory data analysis, and spatial analysis are subsequently performed to ensure the quality, consistency, and reliability of the information used in the subsequent modelling stages.

Task 3 – Waste Generation Modelling

The third task is devoted to developing and validating a municipal solid waste generation model using a Stepwise Multiple Regression approach. Significant explanatory variables are identified to estimate municipal solid waste demand for each service area. The estimated demand generated by the regression model constitutes the principal input for the deterministic and stochastic p-median facility location optimisation models developed in the following tasks.

Task 4 – Deterministic p-Median Facility Location Optimisation

The fourth task develops a deterministic p-median facility location model based on the estimated waste demand obtained in the previous task. The model identifies suitable locations for municipal solid waste containers under fixed demand conditions and establishes a baseline solution for strategic infrastructure planning and subsequent comparison with the stochastic formulation.

Task 5 – Stochastic p-Median Facility Location Optimisation

The fifth task extends the deterministic formulation to a stochastic p-median facility location model that explicitly incorporates uncertainty in municipal solid waste generation through multiple demand scenarios. By accounting for demand variability, the stochastic model aims to identify more robust facility location decisions capable of maintaining satisfactory service performance under uncertain future conditions.

Task 6 – Integrated Model Validation, Comparative Evaluation and Sensitivity Analysis

The sixth task focuses on the integrated validation and evaluation of the proposed modelling framework. The statistical performance of the waste generation model is first assessed to verify the reliability of the estimated waste demand. Subsequently, the deterministic and stochastic p-median facility location models are evaluated and compared with the existing municipal container configuration. The analysis considers accessibility, service coverage, infrastructure utilisation, computational performance, and sensitivity to demand uncertainty in order to assess the robustness and practical applicability of the proposed methodology for strategic municipal solid waste planning.

Task 7 – Thesis Writing and Dissemination

The final task is dedicated to integrating the research findings, preparing scientific publications, disseminating the results through international conferences, completing the doctoral thesis, and preparing for the doctoral thesis defence. This final stage consolidates the scientific and practical contributions of the research and ensures the effective communication of the proposed methodology to both the academic community and practitioners

Table ‎3.1.Research Tasks and Timeline

| Task | Description | Duration |
|---|---|---|
| Task 1 | Literature review and development of the conceptual and methodological framework | Months 1–8 |
| Task 2 | System characterisation, database development, GIS integration, data preprocessing, exploratory data analysis, and spatial analysis | Months 4–14 |
| Task 3 | Development and validation of the municipal solid waste generation model and waste demand estimation | Months 10–22 |
| Task 4 | Development of the deterministic p-median facility location model | Months 18–28 |
| Task 5 | Development of the stochastic p-median facility location model under demand uncertainty | Months 24–36 |
| Task 6 | Integrated model validation, comparative evaluation, and sensitivity analysis | Months 34–42 |
| Task 7 | Thesis writing, scientific publications, and doctoral thesis preparation | Months 36–48 |

*Table ‎3.2.Key Milestones*

| Milestone | Expected Outcome | Month |
|---|---|---|
| M1 | Literature review and conceptual framework completed | 8 |
| M2 | System characterisation and integrated analytical database completed | 14 |
| M3 | Municipal solid waste generation model validated and waste demand estimation completed | 22 |
| M4 | Deterministic p-median model completed | 28 |
| M5 | Stochastic p-median model completed | 36 |
| M6 | Integrated model validation, comparative evaluation, and sensitivity analysis completed | 42 |
| M7 | Thesis submission and doctoral defence | 48 |

*Table ‎3.3.Expected Scientific Outputs*

| Output Category | Target Deliverables |
|---|---|
| SCI/SCIE Journal Articles | 2–3 Publications |
| International Conference Papers | 3–4 Presentations |
| Municipal Solid Waste Generation Model | One Stepwise Multiple Regression Model |
| Deterministic Facility Location Model | One Deterministic p-Median Model |
| Stochastic Facility Location Model | One Stochastic p-Median Model |
| Doctoral Thesis | One Doctoral Dissertation |

Timeline Summary

Year 1: Literature review, development of the conceptual framework, system characterisation, database development, GIS integration, data preprocessing, exploratory data analysis, and spatial analysis.

Year 2: Development and validation of the municipal solid waste demand model, waste demand estimation, and development of the deterministic p-median facility location model.

Year 3: Development of the stochastic p-median facility location model, integrated model validation, comparative evaluation of deterministic and stochastic solutions, and sensitivity analysis.

Year 4: Integration of research findings, preparation of scientific publications, completion of the doctoral thesis, thesis submission, and doctoral defence.

Figure ‎3.1.Schematic proposed Research Tasks

## Expected Outcomes

The proposed doctoral research is expected to generate significant scientific, methodological, and practical contributions to the field of Municipal Solid Waste (MSW) planning through the development of an integrated framework that combines waste generation modelling with deterministic and stochastic facility location optimisation. Using Rio Maior, Portugal, as the case study, the research aims to support strategic planning for municipal solid waste collection infrastructure under demand uncertainty.

Unlike many previous studies that investigate waste generation estimation and facility location as separate problems, this preliminary research work integrates these two components into a unified analytical framework. In the proposed methodology, waste demand estimated through statistical modelling serves as the direct input to deterministic and stochastic p-median optimisation models, providing a coherent decision-support approach for strategic infrastructure planning. The expected outcomes are organised into three categories: scientific journal publications, technical and methodological outputs, and scientific and practical contributions.

### Scientific Journal Publications

This preliminary research work is expected to generate two to three peer-reviewed journal articles corresponding to the principal stages of the research.

Paper 1 – Municipal Solid Waste Generation Modelling

This paper focuses on developing and validating a municipal solid waste generation model using demographic, land-use, and socioeconomic variables to estimate waste demand at the service-area level.

Proposed title

Spatial Regression Analysis of Municipal Solid Waste Generation: Application to Rio Maior, Portugal

Target Journal

Waste Management (Elsevier, Q1)

Planned submission

Year 2 – Semester 1

Paper 2 – Deterministic and Stochastic Facility Location Optimisation

This paper develops deterministic and stochastic p-median facility location models using the estimated waste demand obtained from the regression analysis. The study evaluates the influence of demand uncertainty on strategic container location decisions and compares deterministic and stochastic optimisation solutions.

Proposed title

Deterministic and Stochastic p-Median Optimisation for Municipal Solid Waste Container Location under Demand Uncertainty

Target Journal

European Journal of Operational Research (Elsevier, Q1)

Planned submission

Year 3 – Semester 1

Paper 3 – Integrated Framework for Municipal Solid Waste Planning (Optional)

Subject to the progress and maturity of the research, a third journal article may be prepared to present the overall methodological framework integrating waste generation modelling with deterministic and stochastic facility location optimisation.

Proposed title

An Integrated Framework for Waste Generation Modelling and Facility Location Optimisation for Municipal Solid Waste Planning

Target Journal

Transportation Research Part E: Logistics and Transportation Review (Elsevier, Q1)

Planned submission

Year 3 – Semester 2

Collectively, these journal articles are expected to contribute to advances in:

- Municipal solid waste generation modelling;
- GIS-based spatial analysis;
- Stepwise multiple regression for demand estimation;
- Deterministic and stochastic p-median facility location optimisation;
- Uncertainty-aware strategic infrastructure planning for municipal solid waste management.

### Technical and Methodological Outputs

Beyond scientific publications, the this preliminary research work is expected to generate several technical and methodological outputs, including:

An integrated GIS database for the Rio Maior municipal solid waste collection system;

A municipal solid waste generation dataset;

A Stepwise Multiple Regression model for waste demand estimation;

A deterministic p-median optimisation model;

A stochastic p-median optimisation model under demand uncertainty;

Python implementation of the statistical and optimisation models;

FICO Xpress Mosel implementation of the deterministic and stochastic optimisation models;

GIS-based analytical workflows;

Technical documentation describing data preparation, model development, validation procedures, and implementation guidelines.

These outputs are expected to improve the transparency, reproducibility, and applicability of the proposed methodology for municipal solid waste planning.

### Expected Scientific and Practical Contributions

The principal outcome of the dissertation is the development of an integrated framework linking municipal solid waste generation modelling with deterministic and stochastic facility location optimisation for strategic planning under demand uncertainty.

Scientific Contributions

The research is expected to contribute to:

Municipal solid waste generation modelling;

Stepwise Multiple Regression for demand estimation;

Integration of statistical demand modelling with facility location optimisation;

Deterministic p-median optimisation;

Stochastic p-median optimisation;

Uncertainty-aware strategic infrastructure planning.

Practical Contributions

The proposed framework is expected to support municipalities by providing:

Improved container location planning;

Enhanced service accessibility;

Better infrastructure utilisation;

More robust facility location decisions under demand uncertainty;

Reduced planning costs;

A transparent and reproducible decision-support framework for municipal solid waste planning.

## Proposed Structure for the PhD Thesis

The proposed PhD thesis is organised in a logical and progressive manner to develop a comprehensive methodology for the strategic planning of municipal solid waste (MSW) collection infrastructure under demand uncertainty. The dissertation follows a sequential research framework in which each chapter builds upon the results of the previous one. The research progresses from system characterisation and waste generation modelling to deterministic and stochastic facility location optimisation, ultimately providing a data-driven framework for strategic infrastructure planning in the municipality of Rio Maior, Portugal.

Chapter 1 – Introduction

The first chapter introduces the research background and motivation within the context of sustainable municipal solid waste management and circular economy policies. It presents the research problem, research questions, objectives, methodological approach, expected scientific contributions, and the overall organisation of the dissertation.

Chapter 2 – Literature Review

The second chapter reviews the scientific literature related to municipal solid waste management, waste generation modelling, Geographic Information Systems (GIS), deterministic and stochastic facility location optimisation, and p-median models. It critically analyses previous studies, identifies current research gaps, and establishes the theoretical foundation supporting the proposed methodology.

Chapter 3 – System Characterisation and Database Development

The third chapter characterises the existing municipal solid waste collection system in Rio Maior, Portugal. Historical collection records, GIS datasets, demographic information, land-use characteristics, road network data, and container inventories are integrated into a unified analytical database. Data preprocessing, exploratory analysis, and spatial analysis are conducted to establish the empirical basis required for the subsequent modelling stages.

Chapter 4 – Municipal Solid Waste Generation Modelling

The fourth chapter develops and validates a municipal solid waste generation model using Stepwise Multiple Regression. Demographic characteristics, land-use variables, and other explanatory factors are analysed to identify the significant determinants of waste generation. The resulting regression model is subsequently used to estimate waste demand for each service area, providing the principal input to the facility location optimisation models.

Chapter 5 – Deterministic and Stochastic Facility Location Optimisation

The fifth chapter develops deterministic and stochastic p-median facility location models for the strategic allocation of municipal solid waste containers. Initially, a deterministic model is formulated using the estimated waste demand obtained in the previous chapter, providing a baseline solution under fixed demand conditions. The deterministic formulation is subsequently extended to a stochastic p-median model that explicitly incorporates demand uncertainty through multiple demand scenarios. Finally, both models are compared in terms of accessibility, service coverage, infrastructure utilisation, and robustness in order to evaluate the benefits of stochastic optimisation for strategic infrastructure planning.

Chapter 6 – Discussion

The sixth chapter discusses the research findings and evaluates the scientific and practical implications of the proposed methodology. The chapter analyses the contribution of integrating waste generation modelling with deterministic and stochastic facility location optimisation, discusses methodological limitations, and assesses the applicability of the proposed framework for municipal infrastructure planning.

Chapter 7 – Conclusions and Future Research

The final chapter summarises the principal findings and contributions of the dissertation. It highlights the theoretical, methodological, and practical advances achieved throughout the research and provides recommendations for future work, including possible extensions towards integrated smart municipal solid waste management systems and more advanced optimisation methodologies.

Finally, the dissertation concludes with the list of references and appendices containing supplementary materials, including regression outputs, mathematical formulations of the optimisation models, GIS procedures, statistical analyses, and additional technical documentation supporting the research.

# CASE STUDY – Rio Maior

## Introduction

The municipality of Rio Maior, located in the district of Santarém in central Portugal, was selected as the case study for this research. Rio Maior provides an appropriate environment for investigating municipal solid waste (MSW) collection infrastructure due to its heterogeneous urban structure, diverse land-use characteristics, and variable waste generation patterns. The municipality also offers access to comprehensive operational and spatial datasets that support the development and validation of data-driven facility location models.

Rio Maior represents many of the characteristics commonly observed in medium-sized European municipalities. Unlike large metropolitan areas with extensive smart-city infrastructures, Rio Maior operates under practical financial, technical, and operational constraints. Consequently, it provides a realistic setting for evaluating optimisation methodologies intended to support strategic planning of municipal waste collection infrastructure.

The municipality is also one of the pilot case studies of the WSmartRoute+ research project, providing access to real operational data collected from municipal waste collection activities. These datasets enhance the empirical basis of the present research and allow the proposed methodology to be validated under actual operating conditions.

## Geographical and Administrative Characterisation

Rio Maior is located in the district of Santarém within the Centro region of Portugal and occupies an area of approximately 272 km². The municipality is strategically positioned between Lisbon and Leiria, benefiting from good regional accessibility while maintaining a combination of residential, commercial, industrial, agricultural, and tourism activities.

The municipality includes urban centres, peri-urban settlements, and rural areas, creating considerable spatial variability in population density, accessibility, and land-use characteristics. These differences directly influence municipal solid waste generation and the spatial distribution of waste collection demand.

The road network consists of municipal streets, regional roads, and interurban connections, which influence accessibility between residential areas and waste collection infrastructure. These geographical characteristics make Rio Maior an appropriate case study for analysing facility location problems.

## Demographic and Socioeconomic Characteristics

Rio Maior has experienced gradual demographic changes during recent decades. According to official statistics, the resident population increased from approximately 19,356 inhabitants in 1960 to approximately 21,004 inhabitants in 2021. At the same time, the municipality has undergone significant population ageing, with the ageing index increasing substantially over the same period.

Population density is concentrated within the urban centre, while peripheral and rural areas exhibit considerably lower densities. This heterogeneous population distribution contributes to spatial differences in municipal solid waste generation and collection requirements.

In addition to demographic factors, socioeconomic activities such as commercial services, educational institutions, industrial facilities, tourism, and public services also influence waste generation. Different land-use categories generate distinct waste production patterns and therefore represent important explanatory variables within the waste generation model developed in this research.

## Existing Municipal Solid Waste Collection System

The municipal solid waste collection system in Rio Maior is based on a network of recycling containers distributed throughout the municipality. The collection infrastructure includes several container types, including AMBI, OVO, OVO S, TITAN, VRL, MOXEA, and E BLUE BEE systems, which are allocated according to local service requirements.

Collection operations are generally performed according to predefined collection schedules. Consequently, differences in waste generation among service areas may lead to variations in infrastructure utilisation and collection efficiency.

These operational characteristics provide an appropriate context for evaluating alternative facility location strategies aimed at improving accessibility, service coverage, and infrastructure utilisation.

## Operational Database

One of the principal strengths of the Rio Maior case study is the availability of comprehensive municipal operational data. The research integrates multiple categories of information, including container locations, historical waste collection records, waste quantities, demographic data, land-use information, road-network characteristics, and GIS datasets.

The operational database contains more than one million records collected between 2020 and 2024, providing extensive spatial and temporal information for statistical analysis and optimisation modelling.

Prior to analysis, the datasets were subjected to preprocessing procedures, including data cleaning, consistency verification, outlier detection, and integration of multiple data sources. Geographic Information Systems (GIS) were subsequently employed to analyse the spatial distribution of containers, population, land use, and accessibility conditions throughout the municipality.

The resulting database provides the empirical foundation for both municipal solid waste generation modelling and the subsequent facility location optimisation models.

## Waste Generation Characteristics

Preliminary analysis of the operational database revealed considerable spatial and temporal variability in municipal solid waste generation across the municipality. Differences in demographic characteristics, land-use patterns, commercial activities, and seasonal variations contribute to heterogeneous waste generation behaviour among service areas.

Statistical analysis identified significant variation in waste quantities collected from different locations, indicating that waste demand cannot be adequately represented by a single uniform value across the municipality.

These observations support the development of a municipal solid waste generation model capable of estimating waste demand for each service area. The estimated demand values subsequently serve as the primary input to the deterministic and stochastic facility location optimisation models developed in the following chapters.

## Relevance of Rio Maior for the Present Research

Rio Maior provides an appropriate case study for developing and validating the proposed methodology because it combines heterogeneous waste generation patterns, diverse land-use characteristics, realistic municipal operational conditions, and comprehensive spatial datasets.

Unlike highly digitalised metropolitan environments frequently considered in the literature, Rio Maior represents a medium-sized municipality operating under practical financial and operational constraints. Consequently, it offers a realistic environment for evaluating deterministic and stochastic p-median facility location models under uncertain waste demand.

The availability of genuine municipal operational data enables the proposed methodology to be validated under real operating conditions. The results obtained from this case study are therefore expected to provide practical guidance for strategic municipal solid waste infrastructure planning and to be transferable to municipalities with similar demographic, spatial, and operational characteristics.

# WASTE PRODUCTION ANALYSIS (Regression Analysis)

## Introduction

Efficient management of recyclable municipal waste requires accurate estimation of waste generation at the individual container level, where operational decisions such as container placement, collection frequency, fleet allocation, and facility-location planning are implemented. Reliance on municipal average generation rates may therefore lead to inefficient collection operations, unnecessary collection trips, increased operational costs, and reduced service quality.

This chapter develops a regression-based framework for estimating recyclable waste generation at the container level in Rio Maior, Portugal, using operational data collected between 2020 and 2024. The objective is to identify a parsimonious and statistically robust demand estimation model capable of representing the spatial variability of municipal solid waste generation while maintaining operational interpretability.

The modelling process begins with the estimation of an initial full Ordinary Least Squares (OLS) regression model incorporating all candidate explanatory variables. Subsequently, a Stepwise Multiple Regression procedure is applied to systematically identify the subset of variables that provides the most appropriate balance between statistical performance, model parsimony, and compliance with the regression assumptions. The resulting candidate models are compared using multiple statistical criteria before selecting the final demand estimation model.

Rather than constituting an independent statistical exercise, the regression analysis serves as the empirical foundation of the optimisation framework developed throughout this preliminary research work. The estimated waste demand generated by the selected regression model is subsequently used as the primary input for the deterministic and stochastic p-median facility-location models presented in the following chapters, thereby establishing the methodological link between demand estimation and strategic infrastructure optimisation.

## Operational Database

This section describes the operational database used to develop the municipal solid waste generation model. The database integrates multiple municipal datasets collected in Rio Maior, Portugal, between 2020 and 2024, including collection records, Geographic Information Systems (GIS), demographic information, land-use characteristics, recycling container inventories, and other operational data. Before developing the regression models, the raw data were organised, processed, and transformed into a consistent analytical database suitable for statistical modelling.

The following subsections describe the structure of the operational database, the analytical unit adopted in the study, the definition of collection events, the procedure used to allocate trip-level waste quantities to individual containers, the derivation of operational indicators, and the data-cleaning and preprocessing procedures applied prior to regression modelling.

### Operational Database and Unit of Analysis

The regression analysis is based on an integrated operational database compiled from multiple municipal information systems in Rio Maior, Portugal. The database combines municipal collection records, Geographic Information Systems (GIS), demographic information, land-use characteristics, recycling container inventories, fill-level observations, road-network information, and operational routing data collected between 2020 and 2024. Overall, the database contains more than one million operational records, providing comprehensive spatial and temporal coverage for analysing municipal solid waste generation.

To support the subsequent regression analysis, the operational data were organised into three hierarchical analytical levels:

Bin–event level: individual container collection events;

Bin–day level: daily waste accumulation for each recycling container; and

Bin level: long-term average waste generation associated with each container.

The regression analysis is ultimately performed at the bin level, where each observation represents the long-term average municipal solid waste demand associated with an individual recycling container. The resulting demand estimates constitute the primary input for the deterministic and stochastic p-median facility location models presented in the subsequent chapters.

### Definition of Collection Events

A fundamental challenge in constructing the operational database is that municipal collection records are generated at the collection-trip level rather than at the level of individual recycling containers. Consequently, a consistent definition of collection events is required before estimating container-level waste generation and developing the regression models.

Each collection event is uniquely identified by the operational collection-trip identifier (idrecolha) recorded in the municipal information system. All operational records sharing the same idrecolha are considered part of a single collection event, regardless of the number of recycling containers serviced during that trip.

Operational variables such as the total quantity of recyclable waste collected and the travelled distance are recorded for the entire collection trip rather than for individual containers. Therefore, these variables cannot be directly assigned to specific recycling containers and must first be transformed into container-level indicators.

### Trip-Level Allocation of Waste Quantities

Because direct container-level weight measurements are unavailable in the municipal operational database, the total recyclable waste collected during each collection trip is proportionally allocated among all serviced containers according to

where

Peso bin is the estimated waste quantity assigned to an individual recycling container;

Peso trip​ is the total recyclable waste collected during the collection trip; and

n bins is the number of recycling containers serviced during that trip.

Although this proportional allocation does not capture the actual variability in waste quantities among individual containers, it provides a transparent, reproducible, and operationally feasible approximation for estimating container-level waste demand under real municipal operating conditions. The resulting estimates constitute the dependent variable used in the subsequent regression analysis.

### Operational Indicators

The operational event structure, defined by the combination of container identifier (idcontentor), collection-trip identifier (idrecolha), collection date, and collection time, enables the derivation of several temporal indicators describing collection behaviour.

For example, the collection frequency of container i is calculated as

where

Freqi is the collection frequency of container i;

N(idrecolhai)  is the number of collection trips serving container i; and

T is the length of the observation period.

Similarly, the inter-collection interval is calculated as

where

ICTi is the inter-collection interval for container i;

ti(k)is the timestamp of the current collection event; and

ti(k-1) is the timestamp of the previous collection event.

These indicators describe the temporal dynamics of municipal waste collection and are considered as candidate explanatory variables during the subsequent Stepwise Multiple Regression analysis.

### Data Cleaning and Preprocessing

Prior to regression modelling, the operational database underwent a comprehensive data-cleaning and preprocessing procedure to ensure data quality, consistency, and analytical reliability. The preprocessing workflow included the removal of duplicate records, treatment of missing values, standardisation of temporal information and operational variables, outlier detection, validation of geographical coordinates, and the integration of operational, demographic, and land-use datasets within a Geographic Information Systems (GIS) environment.

Special attention was given to identifying and correcting anomalous observations, including unrealistic fill-level measurements, inconsistent operational records, negative values, routing inconsistencies, and sensor-related anomalies. These procedures ensured that the operational database accurately represented municipal waste collection activities before statistical analysis.

To characterise the surrounding urban environment of each recycling container, a 100-m buffer was generated using GIS. Demographic and land-use characteristics extracted within each buffer were subsequently associated with individual containers and used as candidate explanatory variables in the regression analysis.

Overflow conditions were identified using binary indicators derived from both driver observations and sensor measurements:

Overflow observations were retained because they provide valuable information regarding capacity limitations, delayed collection services, and abnormal waste accumulation patterns under real operating conditions.

the cleaned and integrated operational database was aggregated at the container level to construct the cross-sectional dataset used for the subsequent regression analysis. This dataset provided the basis for developing the initial full regression model and the subsequent Stepwise Multiple Regression procedure presented in the following sections.

## Candidate Variables

This section describes the dependent and explanatory variables considered in the development of the municipal solid waste generation model. The candidate variables were selected based on the literature review, data availability, and their potential influence on spatial variations in recyclable waste generation. Before model estimation, all candidate variables were examined to ensure consistency with the analytical framework and to provide a comprehensive set of predictors for the initial regression model.

The regression analysis initially considered the complete set of candidate explanatory variables. Subsequently, a Stepwise Multiple Regression procedure was applied to identify the subset of variables that significantly contributed to explaining municipal solid waste generation while producing a parsimonious and statistically robust demand estimation model.

### Dependent Variable

The dependent variable represents the average daily recyclable waste demand associated with each recycling container. Since the facility location models developed in the subsequent chapters require a stable estimate of long-term waste demand, the dependent variable is defined as the average quantity of recyclable waste collected per container per day over the observation period.

The dependent variable is calculated as:

where:

Yi​ is the average daily waste demand associated with container i;

kgi,t is the quantity of recyclable waste assigned to container ion day t; and

Ti is the number of valid observation days for container i.

Municipal solid waste generation data typically exhibit right-skewed distributions and non-constant variance. To improve compliance with the assumptions of Ordinary Least Squares (OLS) regression, a logarithmic transformation was applied to the dependent variable:

The addition of one avoids computational problems associated with zero-valued observations while stabilising the variance and reducing the influence of extreme values. The transformed variable is subsequently used throughout the regression analysis.

### Candidate Explanatory Variables

The explanatory variables were derived from demographic information, GIS-based spatial analysis, land-use characteristics, and operational data describing the environment surrounding each recycling container. For each container, the variables were calculated within a 100-m spatial buffer in order to represent the local characteristics that may influence recyclable waste generation.

The initial set of candidate explanatory variables includes:

Population within the 100-m buffer (Population_Buffer);

Distance from the city centre (Distance_to_CBD);

Residential land-use proportion;

Commercial land-use proportion;

Industrial land-use proportion;

Institutional land-use proportion;

Administrative land-use proportion;

Healthcare land-use proportion;

Cultural land-use proportion;

Recreational land-use proportion; and

Transport-related land-use proportion.

*Table ‎5.1.Candidate Explanatory Variables*

| Variable | Description | Unit |
|---|---|---|
| Population_Buffer | Population within the 100-m buffer | persons |
| Distance_to_CBD | Distance from the container to the city centre | m |
| Pct_Residential | Residential land-use proportion | % |
| Pct_Commercial | Commercial land-use proportion | % |
| Pct_Industrial | Industrial land-use proportion | % |
| Pct_Institutional | Institutional land-use proportion | % |
| Pct_Administrative | Administrative land-use proportion | % |
| Pct_Healthcare | Healthcare land-use proportion | % |
| Pct_Cultural | Cultural land-use proportion | % |
| Pct_Recreational | Recreational land-use proportion | % |
| Pct_Transport | Transport-related land-use proportion | % |

All candidate variables were initially included in the full regression model. Their statistical contribution was subsequently evaluated through the Stepwise Multiple Regression procedure presented in the following section, which identified the subset of variables retained in the final municipal solid waste demand estimation model.

## Initial Full Regression Model

The regression modelling process began with the estimation of an initial full Ordinary Least Squares (OLS) regression model including all candidate explanatory variables identified in the previous section. The objective of this initial specification was to investigate the overall relationships between municipal solid waste generation and the available demographic, land-use, and spatial characteristics before applying any variable selection procedure.

The initial full regression model is specified as:

where:

Yi is the average daily municipal solid waste demand associated with container i;

Xij represents the j-th explanatory variable for container i;

β0​ is the intercept;

βj​ denotes the regression coefficients; and

εi​ is the random error term.

The explanatory variables included in the initial model comprised demographic indicators, spatial accessibility measures, and land-use characteristics extracted from the GIS analysis. All candidate variables were entered simultaneously into the regression model without prior variable selection.

The estimated regression coefficients and the corresponding goodness-of-fit statistics are presented in Table5.3 and Table 5.4respectively.

*Table ‎5.2.Estimated Coefficients of the Initial Full Regression Model*

| Variable | Coefficient | Std. Error | t-value | p-value |
|---|---|---|---|---|
| Intercept | 5.275631 | 0.582109 | 9.0630 | <0.001 |
| Pct_RESIDENTIAL | 0.344192 | 0.730749 | 0.4711 | 0.6378 |
| Pct_INSTITUTIONAL | 0.514317 | 0.912158 | 0.5638 | 0.5732 |
| Pct_CULTURAL | 1.199277 | 2.447939 | 0.4898 | 0.6246 |
| Pct_TRANSPORT | −0.559110 | 1.128226 | −0.4956 | 0.6204 |
| Pop_100m | −6.374×10⁻⁷ | 1.942×10⁻⁶ | −0.3282 | 0.7429 |
| Pct_HEALTHCARE | 0.397734 | 0.763129 | 0.5211 | 0.6025 |
| Pct_ADMINISTRATIVE | −0.680315 | 1.657369 | −0.4105 | 0.6816 |
| Pct_COMMERCIAL | 0.080507 | 0.233700 | 0.3445 | 0.7306 |
| Pct_INDUSTRIAL | 0.048440 | 0.129119 | 0.3751 | 0.7078 |
| Pct_RECREATIONAL | 0.022054 | 0.129994 | 0.1697 | 0.8654 |

*Table ‎5.3.Goodness-of-Fit Statistics of the Initial Full Regression Model*

| Metric | Value |
|---|---|
| Number of observations | 452 |
| R² | 0.0130 |
| Adjusted R² | −0.0100 |
| AIC | 1349.476 |
| BIC | 1398.885 |
| F-statistic (p-value) | 0.9504 |

As shown in Table 5.2 and Table 5.3 none of the explanatory variables included in the initial full regression model was statistically significant at the conventional significance levels, although the intercept remained statistically significant. These results indicate that the initial model contains redundant explanatory variables and does not provide a parsimonious representation of municipal solid waste generation.

The limited explanatory power of the full model suggests that including all candidate variables simultaneously increases model complexity without providing a meaningful improvement in explanatory performance. Consequently, the initial full regression model was not adopted as the final demand estimation model.

To obtain a more parsimonious and statistically robust specification, a Stepwise Multiple Regression procedure was subsequently implemented. The variable selection process systematically evaluated the contribution of each candidate explanatory variable and retained only those variables that significantly improved model performance according to the predefined selection criteria. The resulting candidate models are presented, compared, and evaluated in the following sections, from which the final waste demand estimation model is selected for integration with the deterministic and stochastic p-median facility location model

## Model Development and Selection Procedure

Following the estimation of the initial full regression model, a comprehensive model development and selection procedure was implemented to identify the most appropriate municipal solid waste demand estimation model. The procedure began with a Stepwise Multiple Regression analysis to eliminate redundant explanatory variables and identify statistically relevant predictors. Subsequently, a comprehensive search of alternative regression specifications was conducted to identify the most parsimonious and statistically robust model suitable for subsequent facility-location optimisation.

### Generation of Candidate Models

The model development process started with the initial full regression model containing all candidate explanatory variables. Based on the variables retained during the preliminary stepwise analysis, alternative regression specifications were generated by considering different combinations of the candidate predictors.

Assuming thirteen candidate explanatory variables, the total number of possible regression specifications is

where each specification represents a unique combination of explanatory variables.

### Model Screening

Each candidate model was estimated and evaluated using multiple statistical performance criteria, including:

Coefficient of determination (R²);

Adjusted coefficient of determination (Adjusted R²);

Akaike Information Criterion (AIC);

Bayesian Information Criterion (BIC);

Root Mean Squared Error (RMSE);

Mean Absolute Error (MAE);

Statistical significance of regression coefficients (p-values);

Variance Inflation Factor (VIF);

Durbin–Watson statistic; and

Breusch–Pagan test.

These indicators were jointly considered to evaluate explanatory performance, model complexity, multicollinearity, residual behaviour, and compliance with the assumptions of Ordinary Least Squares regression.

### Selection of Candidate Models

Following the comprehensive screening process, the 50 best-performing regression models were retained for further evaluation. These models were subsequently examined according to the predefined statistical criteria, from which the three highest-performing candidate models were selected for detailed comparison.

Finally, the most parsimonious, statistically robust, and operationally interpretable model was selected as the final municipal solid waste demand estimation model adopted throughout this preliminary research work. The estimated waste demand generated by this model serves as the primary input for the deterministic and stochastic p-median facility location models presented in the subsequent chapters.

## Comparison of Candidate Models

The comprehensive model selection procedure resulted in three candidate regression models that demonstrated the best overall statistical performance. Although each model satisfied the minimum statistical requirements, they differed with respect to model complexity, explanatory power, goodness-of-fit, and compliance with the assumptions of Ordinary Least Squares (OLS) regression.

To identify the most appropriate municipal solid waste demand estimation model, the three candidate models were compared using a comprehensive set of statistical performance indicators. The comparison considered both predictive performance and model interpretability, ensuring that the selected model was statistically robust while remaining operationally practical for subsequent facility location optimisation.

### Candidate Models

The three candidate models considered in this study are summarised below.

Model 1 – Strict Stepwise Model

This model retains only explanatory variables that are statistically significant at the 5% significance level. It represents the most parsimonious specification and minimises unnecessary model complexity.

Model 2 – Borderline Model

This model allows the inclusion of explanatory variables with marginal statistical significance, resulting in a slightly higher explanatory power while maintaining acceptable diagnostic performance.

Model 3 – Best AIC Model

This model corresponds to the regression specification with the lowest Akaike Information Criterion (AIC), providing the best compromise between model fit and complexity according to the information-theoretic criterion.

### Statistical Comparison

Table ‎5.4. Statistical performance of the three candidate regression models

| Criterion | Strict Model | Borderline Model | Best AIC Model |
|---|---|---|---|
| Predictors | 2 | 3 | 3 |
| R² | 0.0739 | 0.0804 | 0.0804 |
| Adjusted R² | 0.0698 | 0.0742 | 0.0742 |
| AIC | 1488.48 | 1487.31 | 1487.31 |
| BIC | 1500.82 | 1503.76 | 1503.76 |
| RMSE | 1.2473 | 1.2429 | 1.2429 |
| Maximum p-value | 0.0189 | 0.0763 | 0.0763 |
| Maximum VIF | 1.081 | 1.153 | 1.153 |
| Durbin–Watson | 0.981 | 0.986 | 0.986 |
| Breusch–Pagan p-value | 0.3235 | 0.0127 | 0.0127 |

Table5.4  compares the statistical performance of the three candidate regression models. Although the Borderline Model and the Best AIC Model achieved slightly lower AIC values and marginally higher coefficients of determination, the improvements in predictive performance were very limited. In contrast, the Strict Model retained only statistically significant explanatory variables, exhibited the lowest multicollinearity, and satisfied the homoscedasticity assumption according to the Breusch–Pagan test. Consequently, the Strict Model was considered the most parsimonious and statistically reliable specification.

As shown in Table 5.4, the three candidate models exhibit comparable predictive performance. Therefore, the final model selection was based not only on goodness-of-fit statistics but also on statistical significance, model parsimony, multicollinearity diagnostics, and residual behaviour.

To further assess the adequacy of the preferred candidate model, graphical diagnostic analyses were performed. Figure 5.1 presents the Q–Q plot of the residuals, while Figure 5.2 illustrates the residuals plotted against the fitted values.

Figure ‎5.1 illustrates the Q–Q plot of the residuals for the selected Strict Regression Model. Although moderate departures from normality are observed in the lower and upper tails, the central portion of the residual distribution closely follows the theoretical normal line. Such deviations are common in operational municipal solid waste datasets and are not considered sufficiently severe to compromise the validity of the regression model.

Figure ‎5.2 presents the residuals plotted against the fitted values. No systematic trend or pronounced funnel-shaped pattern is observed, indicating approximately constant residual variance across the fitted values. This visual assessment is consistent with the Breusch–Pagan test (p = 0.323), which indicates no statistically significant evidence of heteroscedasticity. Therefore, the residual diagnostics support the suitability of the selected regression model for estimating average municipal solid waste demand.

Based on the statistical comparison and diagnostic evaluation presented in this section, the final regression model is selected in the following section for subsequent demand estimation and integration with the deterministic and stochastic p-median optimisation models.

## Final Model Selection

Following the comprehensive statistical comparison presented in the previous section, the final municipal solid waste demand estimation model was selected based on statistical performance, model parsimony, compliance with the assumptions of Ordinary Least Squares (OLS) regression, and operational interpretability.

Although the Borderline Model and the Best AIC Model achieved slightly lower Akaike Information Criterion (AIC) values and marginally higher coefficients of determination, these improvements were relatively small and were obtained by introducing an additional explanatory variable that was not statistically significant at the conventional 5% significance level.

Conversely, the Strict Stepwise Model retained only statistically significant explanatory variables, exhibited the lowest multicollinearity, and satisfied the homoscedasticity assumption according to the Breusch–Pagan test. Moreover, the model provides a simpler and more interpretable representation of municipal solid waste generation, which is particularly desirable for subsequent optimisation models.

Therefore, the Strict Stepwise Model was selected as the final municipal solid waste demand estimation model adopted throughout this preliminary research work.

### Final Regression Equation

The final regression equation is expressed as

where

Y is the estimated average daily municipal solid waste generation (kg/day);

Population_Buffer represents the resident population within the predefined buffer surrounding each recycling container;

Distance_to_CBD denotes the distance from the recycling container to the central business district.

The corresponding demand estimation equation is

### Interpretation of the Final Model

The selected model indicates that municipal solid waste generation is primarily associated with two spatial characteristics.

The positive coefficient of Population_Buffer indicates that containers located in areas with larger surrounding populations tend to generate greater quantities of recyclable waste.

Similarly, the positive coefficient of Distance_to_CBD suggests that waste generation increases with increasing distance from the city centre, reflecting the spatial characteristics of residential development within the study area.

Both explanatory variables are statistically significant at the 5% significance level, indicating that they make meaningful contributions to explaining the spatial variability of municipal solid waste generation.

### Advantages of the Selected Model

The final regression model offers several advantages:

it contains only statistically significant explanatory variables;

it is parsimonious and easy to interpret;

it exhibits very low multicollinearity (maximum VIF = 1.081);

it satisfies the homoscedasticity assumption according to the Breusch–Pagan test (p = 0.323);

it provides stable and operationally meaningful demand estimates;

it is well suited for integration with deterministic and stochastic p-median facility location models.

### Estimated Waste Demand

Using the final regression equation, the average daily waste demand was estimated for each recycling container included in the study area. These predicted demand values constitute the primary input data for the deterministic and stochastic p-median facility location models developed in the following chapters.

Table ‎5.5. summary of the estimated demand

| Statistic | Value |
|---|---|
| Number of containers | 452 |
| Mean (kg/day) | 341.24 |
| Standard deviation | 136.80 |
| Minimum | 194.17 |
| 25th percentile | 241.25 |
| Median | 293.27 |
| 75th percentile | 397.07 |
| Maximum | 758.22 |

# PRELIMINARY CONTAINER LOCATION MODEL (Deterministic p-Median Facility Location Model)

## Introduction

The spatial allocation of recyclable waste containers represents one of the most important strategic decisions in municipal solid waste management. The location of collection facilities directly influences service accessibility, infrastructure utilisation, and the efficiency of the overall collection network. Consequently, the design of an appropriate container location system plays a fundamental role in improving municipal waste collection performance.

In many municipalities, including Rio Maior, Portugal, recyclable waste container locations have evolved gradually based on operational experience and local constraints rather than systematic optimisation. As a result, the existing network may exhibit spatial inefficiencies, uneven service coverage, and suboptimal accessibility for users.

Following the waste generation modelling presented in Chapter 5, this chapter develops a deterministic p-median facility location model to identify the optimal locations of recyclable waste containers. The estimated waste demand obtained from the selected regression model is used as the demand input for the optimisation model.

The deterministic p-median model assumes that waste demand is known and remains constant throughout the planning period. Under this assumption, the objective is to minimise the weighted distance between demand points and selected collection sites while ensuring that all demand is allocated to the available facilities.

The deterministic solution developed in this chapter provides a baseline facility configuration for comparison with the stochastic p-median model presented in the following chapter. This sequential approach establishes a clear methodological progression from demand estimation to deterministic optimisation and subsequently to optimisation under demand uncertainty.

## The Deterministic p-Median Problem

Facility location problems constitute one of the most widely studied classes of optimisation models in Operations Research and play a fundamental role in the planning of public-service infrastructure. In municipal recyclable waste collection systems, facility location models are used to determine the optimal locations of recycling containers and to allocate waste demand to the selected facilities in order to improve accessibility and service efficiency.

Among the available facility location models, the deterministic p-median model is particularly appropriate for strategic infrastructure planning because it identifies the set of facility locations that minimises the total weighted distance between demand points and selected facilities. The model assumes that waste demand is known and remains constant throughout the planning period, making it a suitable baseline for analysing the existing recyclable waste collection network.

In this research, the deterministic p-median model constitutes the first optimisation stage following the waste generation modelling presented in Chapter 5. The estimated waste demand obtained from the selected regression model is used as the demand input for the optimisation model. The objective is to determine the optimal locations of recyclable waste containers while minimising the weighted accessibility cost between demand points and candidate container sites.

The deterministic solution developed in this chapter provides a baseline against which the stochastic p-median model presented in the following chapter is evaluated. While the deterministic formulation assumes fixed waste demand, the stochastic model explicitly incorporates demand uncertainty through multiple demand scenarios, enabling the robustness of facility location decisions to be assessed under uncertain operating conditions.

Facility location problems represent one of the most important classes of optimization models within Operations Research, logistics planning, and urban infrastructure management. In municipal recyclable waste collection systems, facility-location models are used to determine:

where recyclable waste containers should be installed;

how many facilities should be selected;

and how population demand should be allocated across the infrastructure network.

The objective of these models is generally to minimize weighted accessibility cost, operational inefficiency, transportation distance, or service imbalance while satisfying infrastructure and operational constraints.

Within RWC systems, strategic infrastructure allocation strongly influences:

user participation behaviour;

walking accessibility;

recyclable waste separation efficiency;

fill-level dynamics;

collection frequency;

routing performance;

and overflow probability.

Consequently, facility-location optimization constitutes a fundamental component of integrated Smart Waste Management systems.

Among the different facility-location formulations proposed in the literature, the p-median problem remains one of the most widely applied models for public-service infrastructure allocation and accessibility analysis due to its analytical transparency and operational interpretability.

## Deterministic p-Median Formulation

The deterministic p-median problem seeks to determine the optimal locations of a predetermined number of recycling containers by minimizing the total weighted distance between waste demand points and the selected container locations. In this study, the estimated waste demand obtained from the regression model developed in Chapter 5 is used as the demand input for the deterministic optimisation model.

Within the context of recyclable waste collection, demand points represent population centres, while candidate facilities correspond to potential recycling container locations. The objective is to allocate each demand point to one selected container location in such a way that the overall weighted travel distance is minimized.

Within the context of recyclable waste collection systems:

demand points represent population centres or recyclable waste-generation zones;

candidate sites represent potential recyclable waste container locations;

and the optimization objective seeks to minimize weighted accessibility cost.

Sets

I=set of population centresJ=set of candidate recyclable waste container sites

K=set of recyclable waste streams

where:

K={Glass,Paper,Plastic}

Parameters

Decision Variables

Objective Function

The objective is to minimize the total weighted travel distance between demand points and the selected recycling container locations:

Model Constraints

Facility Number Constraint

Exactly p recyclable waste collection sites must be selected:

Demand Allocation

Each population centre must be assigned to exactly one selected facility for each recyclable waste stream:

Facility Activation

Population centres may only be assigned to activated facilities:

Binary Constraints

## Preliminary Optimization Scenario

Before applying the proposed methodology to the complete municipal database, a preliminary optimisation scenario was developed to verify the implementation of the deterministic p-median formulation in FICO Xpress Mosel and to validate the optimisation framework.

The optimization instance considered:

10 population centres;

8 candidate recyclable waste container sites;

3 recyclable waste streams (paper, plastic, and glass);

and a maximum of 3 selected ecoponto locations.

The total represented population within the optimization scenario was:

The preliminary optimization scenario generated:

240 assignment variables;

72 container-allocation variables;

and 8 site-selection variables;

resulting in a total of:

T

he final optimization matrix contained:

327 constraints;

320 variables;

and 1408 non-zero coefficients.

The recyclable waste quantities associated with each population centre were estimated using population-based waste-generation assumptions derived from municipal operational information.

## Computational Implementation

The deterministic p-median model was implemented using:

FICO Xpress Optimizer;

Mosel modelling language;

and Xpress-IVE visualization tools.

The optimization problem was solved using dual simplex procedures combined with branch-and-bound algorithms for mixed-integer optimization.

Figure ‎6.1.Computational Statistics and Optimal Solution Status of the Deterministic p-Median Model

The implementation integrated:

spatial demand data;

candidate site coordinates;

recyclable waste-generation estimates;

container compatibility constraints;

and GIS-based spatial information.

The optimization process converged successfully and produced a globally optimal solution.

Table ‎6.1.Solver Statistics

| Indicator | Value |
|---|---|
| Optimization status | Optimal solution found |
| Objective value | 65.1030 |
| Final MIP gap | 0% |
| Solution time | 0.1 seconds |
| Simplex iterations | 102 |
| Active branch-and-bound nodes | 0 |

The computational performance demonstrates that the deterministic p-median formulation remains computationally tractable for small and medium municipal optimization instances and can therefore be realistically integrated into municipal decision-support systems.

### Optimal Container Locations

The deterministic p-median model identified three optimal collection sites (Sites 1, 6, and 7) from a total of eight candidate locations. These sites were selected to minimize the weighted distance between population centres and recyclable waste collection facilities while ensuring complete service coverage throughout the study area. The resulting configuration provides a balanced spatial distribution of infrastructure and creates three distinct service zones capable of efficiently serving the surrounding demand clusters. Each selected location accommodates a complete set of AMBI containers for paper, plastic, and glass collection, thereby supporting integrated recyclable waste management. The optimization results indicate that the selected sites achieve an effective trade-off between accessibility, infrastructure efficiency, and service equity by reducing average travel distances for residents and avoiding excessive concentration of facilities in a single area. Consequently, the proposed network establishes a robust baseline configuration for future analyses involving stochastic facility location, sensor deployment, inventory-routing optimization, and adaptive decision-support systems developed in subsequent stages of the research.

Figure ‎6.2. illustrates the optimal spatial allocation of recyclable waste collection sites and the corresponding assignment of population centres obtained from the deterministic p-median model. Three ecoponto locations (Sites 1, 6 and 7) were selected to provide service coverage for the entire study population while minimizing weighted accessibility costs.

Selected Site 1

Coordinates: (120,490)

Installed containers:

Glass / AMBI

Paper / AMBI

Plastic / AMBI

Selected Site 6

Coordinates: (490,355)

Installed containers:

Glass / AMBI

Paper / AMBI

Plastic / AMBI

Selected Site 7

Coordinates: (220,195)

Installed containers:

Glass / AMBI

Paper / AMBI

Plastic / AMBI

Each selected ecoponto contains paper, plastic, and glass recyclable waste containers using the AMBI typology with a storage capacity of:

for each recyclable waste stream.

The selected facilities provide relatively balanced spatial coverage across northern, central, and southern sectors of the municipality.

Population-Centre Assignments

The deterministic optimization model assigns each population centre to the nearest feasible recyclable waste collection site while minimizing weighted accessibility cost.The resulting allocation structure reveals three principal service clusters.

Northern Service Cluster

Population centres:

PC1

PC2

PC4

were assigned to Site 1.

Eastern Service Cluster

Population centres:

PC3

PC6

PC9

were assigned to Site 6.

Southern-Central Service Cluster

Population centres:

PC5

PC7

PC8

PC10

were assigned to Site 7.

The resulting allocation structure demonstrates relatively balanced service coverage while minimizing weighted assignment distance.

### Performance Indicators

Several operational performance indicators were evaluated for the optimized deterministic network.

| Indicator | Value |
|---|---|
| Objective value | 65.1030 |
| Average service distance | 106.60 m |
| Total population served | 2770 residents |
| Cost per resident | 0.023503 |

The optimized infrastructure configuration achieved an average service distance of approximately:

which indicates relatively high accessibility between population centres and assigned recyclable waste containers.

The results further suggest that the optimized deterministic configuration is capable of serving the entire study population while maintaining relatively balanced accessibility conditions and low transportation cost.

Table ‎6.2.Xpress result

======================================================================

RIO MAIOR - DETERMINISTIC P-MEDIAN MODEL

======================================================================

Population centers  : 10

Candidate sites     : 8

Sites to select (p) : 3

Waste types         : Paper, Plastic, Glass

Total population    : 2770 residents

======================================================================

Population centers:

PC1  pop=320  coord=( 100.0,  500.0)

PC2  pop=185  coord=( 250.0,  480.0)

PC3  pop=410  coord=( 400.0,  510.0)

PC4  pop=270  coord=( 150.0,  350.0)

PC5  pop=155  coord=( 310.0,  340.0)

PC6  pop=390  coord=( 470.0,  360.0)

PC7  pop=230  coord=( 200.0,  200.0)

PC8  pop=295  coord=( 360.0,  190.0)

PC9  pop=175  coord=( 530.0,  210.0)

PC10  pop=340  coord=( 280.0,  130.0)

Candidate container sites:

Site 1  coord=( 120.0,  490.0)

Site 2  coord=( 280.0,  460.0)

Site 3  coord=( 440.0,  500.0)

Site 4  coord=( 160.0,  345.0)

Site 5  coord=( 320.0,  330.0)

Site 6  coord=( 490.0,  355.0)

Site 7  coord=( 220.0,  195.0)

Site 8  coord=( 380.0,  185.0)

Waste amounts [kg/week] (first 3 centers):

PC1 -> Paper= 28.48  Plastic= 20.50  Glass= 25.06

PC2 -> Paper= 16.66  Plastic= 12.00  Glass= 14.66

PC3 -> Paper= 36.35  Plastic= 26.17  Glass= 31.99

...

Variable counts:

X (assignment) : 240

Y (container)  : 72

Z (site open)  : 8

TOTAL          : 320

======================================================================

SOLVING DETERMINISTIC P-MEDIAN MODEL ...

======================================================================

======================================================================

OPTIMIZATION RESULTS

======================================================================

STATUS  : OPTIMAL SOLUTION FOUND

OBJ VAL :    65.1030  (distance x waste / 1000)

--- SELECTED CONTAINER SITES ---

[OPEN] Site 1  coord=( 120.0,  490.0)

Container: Glass | Type: AMBI | Capacity: 2500 L

Container: Paper | Type: AMBI | Capacity: 2500 L

Container: Plastic | Type: AMBI | Capacity: 2500 L

[OPEN] Site 6  coord=( 490.0,  355.0)

Container: Glass | Type: AMBI | Capacity: 2500 L

Container: Paper | Type: AMBI | Capacity: 2500 L

Container: Plastic | Type: AMBI | Capacity: 2500 L

[OPEN] Site 7  coord=( 220.0,  195.0)

Container: Glass | Type: AMBI | Capacity: 2500 L

Container: Paper | Type: AMBI | Capacity: 2500 L

Container: Plastic | Type: AMBI | Capacity: 2500 L

Total selected: 3 / 3 allowed

--- POPULATION CENTER ASSIGNMENTS ---

PC1 (pop=320) -> Glass:Site1  Paper:Site1  Plastic:Site1

PC2 (pop=185) -> Glass:Site1  Paper:Site1  Plastic:Site1

PC3 (pop=410) -> Glass:Site6  Paper:Site6  Plastic:Site6

PC4 (pop=270) -> Glass:Site1  Paper:Site1  Plastic:Site1

PC5 (pop=155) -> Glass:Site7  Paper:Site7  Plastic:Site7

PC6 (pop=390) -> Glass:Site6  Paper:Site6  Plastic:Site6

PC7 (pop=230) -> Glass:Site7  Paper:Site7  Plastic:Site7

PC8 (pop=295) -> Glass:Site7  Paper:Site7  Plastic:Site7

PC9 (pop=175) -> Glass:Site6  Paper:Site6  Plastic:Site6

PC10 (pop=340) -> Glass:Site7  Paper:Site7  Plastic:Site7

--- PERFORMANCE METRICS ---

Average service distance:   106.60 m

Total population served : 2770 residents

Cost per resident        : 0.023503

--- GENERATING IVE VISUALIZATIONS ---

7 plots generated successfully.

======================================================================

DETERMINISTIC P-MEDIAN MODEL - EXECUTION COMPLETE

======================================================================

Research : PhD Thesis - Rio Maior Waste Collection

Model    : Deterministic P-Median (no fixed costs)

N=10  |  M=8  |  p=3

======================================================================

### Computational Performance of the Optimization Model

In addition to the operational performance indicators, the computational performance of the deterministic p-median model was evaluated using the optimization statistics generated by the FICO Xpress solver. The model consisted of 320 decision variables and 327 constraints and was solved using a branch-and-bound algorithm combined with dual simplex procedures. The optimization process successfully converged to the global optimum with an objective value of 65.103 and a final MIP gap of 0%, confirming the optimality of the obtained solution.

To further evaluate the efficiency of the solution process, the evolution of the objective function and the corresponding MIP gap were monitored throughout the optimization procedure. Figure 6.3 illustrates the convergence behaviour of the branch-and-bound algorithm during the search process.

Figure ‎6.3.Evolution of the Objective Function and MIP Gap during the Optimization Process

As shown in Figure 6.3, the optimization model rapidly converged towards the optimal solution. The MIP gap decreased from 100% to 0% within a very short computational time, while the objective function progressively improved until reaching the optimal value. The convergence behaviour indicates that the deterministic p-median formulation is computationally efficient for medium-sized recyclable waste collection planning problems and can be solved within negligible computational time using standard optimization software. The rapid convergence and zero optimality gap also demonstrate the robustness of the mathematical formulation and provide confidence in the quality of the obtained facility-location solution.

### Visualization and Spatial Interpretation

The optimization framework generated multiple visualization outputs illustrating:

population-centre distribution;

candidate recyclable waste container locations;

selected optimal sites;

and assignment networks for paper, plastic, and glass recyclable waste streams.

The resulting allocation maps clearly demonstrate:

spatial clustering behaviour;

reduction of overlapping service areas;

and improved accessibility consistency

relative to non-optimized infrastructure distributions.

The integrated visualization outputs further demonstrate the practical applicability of the deterministic optimization framework for municipal infrastructure planning and decision-support applications.

### Limitations of the Deterministic Formulation

Although the deterministic p-median model provides an important strategic baseline for infrastructure planning, several limitations must be acknowledged.

First, the deterministic formulation assumes that recyclable waste demand is fully known and temporally stable. However, real municipal recyclable waste-generation behaviour is inherently dynamic and uncertain, influenced by:

seasonal fluctuations;

tourism activity;

behavioural variability;

operational conditions;

and temporal demand evolution.

Second, the deterministic model does not explicitly incorporate:

fill-level evolution;

overflow risk;

inventory dynamics;

collection-frequency variability;

or routing interactions.

Third, the model assumes static accessibility conditions and does not consider:

real-time operational information;

adaptive routing behaviour;

or stochastic demand variability.

Consequently, although the deterministic p-median model provides an analytically transparent and computationally efficient framework, it cannot fully represent the operational complexity of real municipal recyclable waste systems.

These limitations motivate the development of stochastic and adaptive optimization extensions investigated in subsequent stages of the this preliminary research work.

### Integration with Subsequent Optimization Stages

The deterministic p-median model developed in this chapter constitutes the first strategic optimization layer of the broader multi-level framework proposed throughout the this preliminary research work.

The resulting optimized container configurations provide key inputs for:

stochastic facility-location models;

sensor deployment optimization;

inventory-routing planning;

fill-level forecasting systems;

and adaptive routing methodologies.

More specifically, the optimized facility locations are subsequently used to:

define candidate sensor-allocation strategies;

support stochastic scenario generation;

improve routing efficiency;

reduce overflow risk;

and support integrated municipal decision-support procedures.

Consequently, the deterministic p-median framework functions not as a standalone optimization exercise, but rather as a foundational strategic component within the integrated Smart Waste Management architecture proposed throughout the This preliminary research work.

## Conclusions

### General Conclusions

This preliminary research work developed an integrated and data-driven methodology for supporting strategic recyclable waste container location decisions by combining statistical waste demand estimation with deterministic and stochastic facility location optimisation. The proposed framework establishes a direct methodological link between municipal waste generation modelling and optimisation-based infrastructure planning, enabling facility location decisions to be based on estimated waste demand rather than simplified assumptions.

The research began with the development of an integrated operational database for the municipality of Rio Maior, Portugal. The database combined municipal collection records, Geographic Information Systems (GIS), demographic information, land-use characteristics, road-network data, and operational information collected between 2020 and 2024. This integrated database provided the empirical foundation for both the statistical modelling and optimisation components of the research.

Using this database, a regression-based framework was developed to estimate municipal solid waste generation at the recycling-container level. An initial full Ordinary Least Squares (OLS) regression model was first estimated using all candidate explanatory variables. Since the full model contained redundant predictors and did not provide a statistically satisfactory specification, a comprehensive model selection procedure was subsequently implemented. Alternative regression specifications were systematically evaluated according to statistical significance, explanatory power, model parsimony, goodness-of-fit, multicollinearity, and residual diagnostics. The selected regression model provides statistically reliable estimates of municipal solid waste demand and constitutes the principal input to the optimisation models developed in this preliminary research work.

The estimated waste demand obtained from the regression analysis was subsequently incorporated into a deterministic p-median facility location model. The deterministic formulation identifies the optimal locations of recyclable waste containers by minimising the weighted accessibility distance between demand points and candidate facility locations under the assumption of fixed waste demand. The results demonstrate the applicability of optimisation methods for supporting strategic infrastructure planning in municipal recyclable waste collection systems.

Recognising that municipal solid waste generation is inherently uncertain, the deterministic formulation was subsequently extended to a stochastic p-median model that explicitly incorporates multiple demand scenarios. By considering uncertainty in future waste generation, the stochastic model provides more robust facility location decisions and improves the resilience of strategic infrastructure planning under variable operating conditions.

Overall, this this preliminary research workdemonstrates that integrating regression-based demand estimation with deterministic and stochastic p-median optimisation provides a coherent and scientifically rigorous framework for municipal recyclable waste infrastructure planning. Rather than treating waste generation modelling and facility location optimisation as independent problems, the proposed methodology establishes a unified analytical framework that supports evidence-based strategic decision making.

Although the methodology was demonstrated using the municipality of Rio Maior, Portugal, the proposed framework is sufficiently general to be applied to other municipalities where operational, demographic, spatial, and land-use information is available. Consequently, the research contributes both methodologically and practically to the field of municipal solid waste management by providing a systematic approach for estimating waste demand and optimising recycling-container locations under deterministic and uncertain demand conditions.

## Main Contributions

The principal contributions of this this preliminary research work can be summarised as follows:

Development of an integrated operational database combining municipal collection records, GIS information, demographic characteristics, land-use variables, and operational data for recyclable waste analysis.

Development of a regression-based methodology for estimating municipal solid waste demand at the recycling-container level.

Implementation of a comprehensive model selection procedure to identify a parsimonious and statistically robust waste demand estimation model.

Integration of regression-based waste demand estimation with deterministic p-median facility location optimisation.

Extension of the deterministic formulation to a stochastic p-median model that explicitly incorporates uncertainty in municipal waste generation.

Development of a sequential analytical framework linking demand estimation, deterministic optimisation, and stochastic optimisation for strategic infrastructure planning.

Demonstration of the applicability of the proposed methodology through a real municipal case study in Rio Maior, Portugal.

## Limitations

Despite the contributions of this research, several limitations should be acknowledged.

First, the regression analysis was developed using the operational, demographic, spatial, and land-use information available for the municipality of Rio Maior. The inclusion of additional socioeconomic, commercial, tourism-related, and behavioural variables could further improve the predictive performance of the demand estimation model.

Second, the deterministic p-median model assumes fixed waste demand throughout the planning period and therefore cannot represent temporal variations in municipal solid waste generation.

Third, although the stochastic p-median formulation explicitly incorporates uncertainty through multiple demand scenarios, other sources of uncertainty, including travel times, operational disruptions, and behavioural changes, were not considered within the scope of this research.

Finally, this preliminary research workfocuses exclusively on strategic facility location planning. Operational aspects of municipal waste collection, including vehicle routing, collection scheduling, and fleet management, were considered outside the scope of this study and may be addressed in future research.

## Future Research

Several opportunities exist for extending the methodology proposed in this preliminary research work.

Future research may investigate the development of dynamic waste demand models capable of representing temporal variations in municipal solid waste generation. Machine learning techniques, including Random Forest, Gradient Boosting, and Artificial Neural Networks, may also be explored to improve demand prediction accuracy.

The stochastic p-median model developed in this research may be extended to multi-objective optimisation frameworks that simultaneously consider economic, environmental, and social sustainability criteria. Additional uncertainty sources, including operational variability and transportation conditions, may also be incorporated into future stochastic formulations.

Further validation of the proposed methodology using municipalities with different demographic, geographic, and urban characteristics would contribute to assessing its generalisability and practical applicability under diverse municipal conditions.

Finally, future studies may integrate the strategic facility location models developed in this preliminary research work with operational decision-making components, such as vehicle routing and collection scheduling, to establish a comprehensive optimisation framework for municipal recyclable waste management.

# Reference

- Abubakar, I. R., Maniruzzaman, K. M., Dano, U. L., AlShihri, F. S., AlShammari, M. S., Ahmed, S. M. S., Al-Gehlani, W. A. G., & Alrawaf, T. I. (2022). Environmental Sustainability Impacts of Solid Waste Management Practices in the Global South. International Journal of Environmental Research and Public Health, 19(19), 12717. https://doi.org/10.3390/ijerph191912717
- Agência Portuguesa do Ambiente. (2022). Plano Estratégico para os Resíduos Urbanos—PERSU 2030 (031.21 – 21/06.11). https://participa.pt/contents/consultationdocument/R031.21_21.06.11_RA.pdf
- Alshaikh, R., & Abdelfatah, A. (2024). Optimization Techniques in Municipal Solid Waste Management: A Systematic Review. Sustainability, 16(15), 6585. https://doi.org/10.3390/su16156585
- Bertsimas, D., & Sim, M. (2004). The Price of Robustness. Operation Research, 52(1). https://doi.org/10.1287/opre.1030.0065
- Birge, J. R., & Louveaux, F. (2011). Introduction to Stochastic Programming. Springer. https://link.springer.com/book/10.1007/978-1-4614-0237-4
- Candeias, R. (2025, April 23). Waste management in Portugal «big problems require big solutions». Xqthenews. https://xqthenews.com/es/gestion-de-residuos-en-portugal-para-grandes-males-grandes-remedios/
- Daskin, M. S. (2013). Network and discrete location: Models, algorithms, and applications (Second edition). John Wiley & Sons, Inc. https://doi.org/10.1002/9781118537015
- De Morais, C. S., Ramos, T. R. P., Lopes, M., & Barbosa‐Póvoa, A. P. (2024). A data‐driven optimization approach to plan smart waste collection operations. International Transactions in Operational Research, 31(4), 2178–2208. https://doi.org/10.1111/itor.13235
- EC, E. C. [EC]. (2018, September 24). Commission reviews implementation of EU waste rules, proposes actions to help 14 Member States meet recycling targets—European Commission. European Commission. https://commission.europa.eu/news-and-media/news/commission-reviews-implementation-eu-waste-rules-proposes-actions-help-14-member-states-meet-2018-09-24_en
- EEA, E. E. A. (2023). Many EU Member States not on track to meet recycling targets for municipal waste and packaging waste [Official European Union website,European Environment Agency (EEA). (2022)]. European Environment Agency. https://www.eea.europa.eu/en/analysis/publications/many-eu-member-states
- Ellen MacArthur Foundation. (n.d.). What is the meaning of a circular economy and what are the main principles? What Is the Meaning of a Circular Economy and What Are the Main Principles? https://www.ellenmacarthurfoundation.org/topics/circular-economy-introduction/overview
- Esmaeilian, B., Wang, B., Lewis, K., Duarte, F., Ratti, C., & Behdad, S. (2018). The future of waste management in smart and sustainable cities: A review and concept paper. Waste Management, 81, 177–195. https://doi.org/10.1016/j.wasman.2018.09.047
- Estay-Ossandon, C., & Mena-Nieto, A. (2018). Modelling the driving forces of the municipal solid waste generation in touristic islands. A case study of the Balearic Islands (2000–2030). Waste Management, 75, 70–81. https://doi.org/10.1016/j.wasman.2017.12.029
- European Commission. (2020, March 11). A new Circular Economy Action Plan For a cleaner and more competitive Europe. https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:52020DC0098#:~:text=For%20citizens%2C%20the%20circular%20economy,produced%20in%20the%20first%20place.
- European Commission. (2025, June 2). Landfill waste – Environment – European Commission. https://environment.ec.europa.eu/topics/waste-and-recycling/landfill-waste_en
- European Environment Agency. (2023, August 6). Economic instruments and separate collection systems—Key strategies to increase recycling. https://www.eea.europa.eu/en/analysis/publications/economic-instruments-and-separate-collection?utm_source=chatgpt.com
- European Environment Agency. (2025). Waste recycling in Europe. European Environment Agency. https://www.eea.europa.eu/en/analysis/indicators/waste-recycling-in-europe?utm_source=chatgpt.com
- European Parliament. (2024, May 17). How the EU wants to achieve a circular economy by 2050. https://www.europarl.europa.eu/topics/en/article/20210128STO96607/how-the-eu-wants-to-achieve-a-circular-economy-by-2050
- European Parliament & the Council. (2008). Directive 2008/98/EC of the European Parliament and of the Council of 19 November 2008 on waste and repealing certain Directives (Waste Framework Directive) (pp. 3–30). Official Journal of the European Union. https://eur-lex.europa.eu/eli/dir/2008/98/oj/eng
- Eurostat. (2025). Municipal waste statistics. https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Municipal_waste_statistics
- Guerrero, L. A., Maas, G., & Hogland, W. (2013). Solid waste management challenges for cities in developing countries. Waste Management, 33(1), 220–232. https://doi.org/10.1016/j.wasman.2012.09.008
- Hakimi, S. L. (1964). Optimum Locations of Switching Centers and the Absolute Centers and Medians of a Graph. Operations Research, 12(3), 450–459. https://doi.org/https://doi.org/10.1287/opre.12.3.450
- Johansson, O. M. (2006). The effect of dynamic scheduling and routing in a solid waste management system. Waste Management, 26(8), 875–885. https://doi.org/10.1016/j.wasman.2005.09.004
- JRC, E. C. – J. R. C. (2024). Pay-as-you-throw | Green Best Practice Community. Green Best Practice Community – Joint Research Centre, European Commission. https://greenbestpractice.jrc.ec.europa.eu/node/7
- Kennedy, C., Pincetl, S., & Bunje, P. (2011). The study of urban metabolism and its applications to urban planning and design. Environmental Pollution, 159(8–9), 1965–1973. https://doi.org/10.1016/j.envpol.2010.10.022
- Martinho, G. (2025, April 17). Graça Martinho in Público newspaper “Portugal fails in waste reduction policies.” MARE. https://www.mare-centre.pt/en/gracamartinho_publico2025
- Meadows, D. H. (2009). Thinking in systems: A primer. Earthscan.
- Ministry of Environment and Energy of Portuga. (2025, September 15). 30 milhões de euros para reforçar reciclagem e valorização de resíduos. https://www.portugal.gov.pt/pt/gc25/comunicacao/comunicado?i=30-milhoes-de-euros-para-reforcar-reciclagem-e-valorizacao-de-residuos&utm_source=chatgpt.com
- Montgomery, D. C., Peck, E. A., & Vining, G. G. (n.d.). Introduction to Linear Regression Analysis (6th ed.). John Wiley & Sons, Inc. Retrieved https://www.wiley.com/en-us/Introduction+to+Linear+Regression+Analysis,+6th+Edition-p-9781119578727 (Original work published 2021)
- Nevrlý, V., Šomplák, R., Smejkalová, V., Lipovský, T., & Jadrný, J. (2021). Location of municipal waste containers: Trade-off between criteria. Journal of Cleaner Production, 278, 123445. https://doi.org/10.1016/j.jclepro.2020.123445
- OECD. (n.d). Resource efficiency and circular economy. https://www.oecd.org/en/topics/resource-efficiency-and-circular-economy.html
- Popli, K., Park, C., Han, S.-M., & Kim, S. (2021). Prediction of Solid Waste Generation Rates in Urban Region of Laos Using Socio-Demographic and Economic Parameters with a Multi Linear Regression Approach. Sustainability, 13(6), 3038. https://doi.org/10.3390/su13063038
- Portuguese Presidency of the Council of Ministers. (2023, March 24). Resolução do Conselho de Ministros n.o 31/2023, de 24 de março. https://diariodarepublica.pt/dr/detalhe/resolucao-conselho-ministros/31-2023-210923319
- Ramos, T. R. P., Morais, C. S. de, & Barbosa-Póvoa, A. P. (2018). The smart waste collection routing problem: Alternative operational management approaches. Expert Systems with Applications, 103, 146–158. https://doi.org/https://doi.org/10.1016/j.eswa.2018.03.001 Get rights and content
- Resolution of the Council of Ministers No. 30/2023 approving the Strategic Plan for Urban Waste Management 2030 (PERSU 2030). (2023). [Diário da República]. Government of Portugal. https://diariodarepublica.pt/dr/detalhe/resolucao-conselho-ministros/30-2023-210923318
- Rossit, D., & Bard, J. (2025). Solving the waste bin location problem with uncertain waste generation rate: A bi-objective robust optimization approach. Waste Management & Research: The Journal for a Sustainable Circular Economy, 43(3), 421–437. https://doi.org/10.1177/0734242X241248729
- Sadeghi, A. H., Sun, Z., Sahebi-Fakhrabad, A., Arzani, H., & Handfield, R. (2023). A Mixed-Integer Linear Formulation for a Dynamic Modified Stochastic p-Median Problem in a Competitive Supply Chain Network Design. Logistics, 7(1), 14. https://doi.org/10.3390/logistics7010014
- Snyder, L. V. (2006). Facility location under uncertainty: A review. IIE Transactions, 38, 547–564. https://doi.org/https://doi.org/10.1080/07408170500216480
- Šomplák, R., Smejkalová, V., Rosecký, M., Szásziová, L., Nevrlý, V., Hrabec, D., & Pavlas, M. (2023). Comprehensive Review on Waste Generation Modeling. Sustainability, 15(4), 3278. https://doi.org/10.3390/su15043278
- UNEP (Ed.). (2024). Beyond an age of waste: Turning rubbish into a resource. UNEP.
- UNEP. (n.d.). International Environmental Technology Centre (IETC). https://www.unep.org/ietc/
- UNEP - UN Environment Programme, U. N. (2024, February 25). Global Waste Management Outlook 2024 | UNEP - UN Environment Programme. https://www.unep.org/resources/global-waste-management-outlook-2024
- UNEP-IETC, U. N. E. P. – I. E. T. C. (UNEP-I. (2024, September 12). Extended Producer Responsibility | International Environmental Technology Centre. United Nations Environment Programme. https://www.unep.org/ietc/what-we-do/extended-producer-responsibility
- Wibisono, H., Firdausi, F., & Kusuma, M. E. (2020). Municipal solid waste management in small and metropolitan cities in Indonesia: A review of Surabaya and Mojokerto. IOP Conference Series: Earth and Environmental Science, 447(1), 012050. https://doi.org/10.1088/1755-1315/447/1/012050
- Zanjirani Farahani, R., & Hekmatfar, M. (Eds.). (2009). Facility Location: Concepts, Models, Algorithms and Case Studies. Physica-Verlag HD. https://doi.org/10.1007/978-3-7908-2151-2
