---
name: thesis-content-implementation-plan
title: 02_thesis_content_implementation_plan
type: source
category: discussions
source_file: DATA/my concerns and history of discussion with chat gpt/md/02_thesis_content_implementation_plan.md
source_sha256: 60600a01f89a29b9d9d99bc2238c6e6d910de778b819107c15fe3297bd2eba9f
source_bytes: 2268
ingested: 2026-08-09
words: 280
verbatim: true
---

> Faithful copy of `DATA/my concerns and history of discussion with chat gpt/md/02_thesis_content_implementation_plan.md`. Do not edit.

# Claude Code Prompt 2 --- Thesis Content → Implementable Research Plan

Review the PhD methodology as an engineering/research implementation
problem and convert it into a reproducible computational workflow for
Rio Maior recyclable waste collection.

The central research problem is that traditional **"blind collection"**
uses fixed schedules and routes despite uncertain and spatially
heterogeneous waste generation.

The computational system must address the main research gaps: -
real-world data are often poorly integrated; - facility location,
inventory planning and routing are usually studied separately; -
deterministic assumptions dominate despite uncertain fill levels; -
sustainability, service reliability and equity are often omitted; - many
models lack real municipal validation.

Implement the research around these questions:

-   **RQ1 --- System Assessment:** What are the spatial, temporal and
    operational characteristics of the current Rio Maior RWC system?
-   **RQ2 --- Performance:** What are the economic, environmental and
    service-performance characteristics of the baseline system?
-   **RQ3 --- Container Location:** Can stochastic/capacitated p-median
    models improve container allocation under uncertain demand?
-   **RQ4 --- Monitoring/Forecasting:** How well can driver
    observations, sensor data and predictive models estimate container
    fill/waste generation?
-   **RQ5 --- Routing:** How much improvement can optimized
    VRP/IRP/SIRP/DIRP approaches achieve relative to current collection
    practice?

The implementation must support:

A. Baseline characterization\
B. Waste-generation/demand modelling\
C. Fill-level forecasting\
D. Facility-location optimization\
E. Stochastic inventory-routing\
F. Daily routing\
G. Scenario/sensitivity analysis\
H. Cost-benefit and environmental evaluation\
I. Real-world validation

Keep the distinction between: - observed empirical results, -
model-generated results, - simulation results, - literature
benchmarks, - expected/target improvements.

Do not report target percentages as achieved results unless they are
reproduced from the supplied Rio Maior data.

Produce modular code, documented assumptions, reproducible experiments
and thesis-ready tables/figures.
