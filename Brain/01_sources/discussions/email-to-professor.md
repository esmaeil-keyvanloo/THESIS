---
name: email-to-professor
title: email to prpfessor
type: source
category: discussions
source_file: DATA/my concerns and history of discussion with chat gpt/doc/email to prpfessor.docx
source_sha256: 4f7584bd78d4d7e76d59f9e1cbcb1770581906773ad680efbe31bbb952d980aa
source_bytes: 20134
ingested: 2026-08-09
words: 1252
verbatim: true
---

> Faithful conversion of `DATA/my concerns and history of discussion with chat gpt/doc/email to prpfessor.docx`. Do not edit — edit the source and re-run the ingest.

Subject: Additional Literature Supporting the Use of Logarithmic Transformation

Dear Professor Bigotte,

Thank you very much for your valuable question regarding the use of the logarithmic transformation in my regression model. Following your comment, I reviewed the recent literature to better understand and justify this methodological choice.

Based on this review, I found that the use of log(1+Y) is well supported both statistically and theoretically in municipal solid waste modeling.

The main arguments are summarized below.

1. Improving the normality assumption

The study by Araiza-Aguilar et al. (2020) follows an approach very similar to the one adopted in my research.

The authors first evaluated the normality of the dependent and explanatory variables using the Kolmogorov–Smirnov test. They found that municipal solid waste generation, population, population density, and several other variables were not normally distributed. Consequently, they transformed these variables using the natural logarithm before estimating the multiple linear regression model. Their results showed a substantial improvement in normality after the logarithmic transformation, supporting the use of this approach for regression modeling.

2. Linearising exponential relationships

The second justification comes from Alhanaqtah (2024).

This study explains that municipal solid waste generation frequently follows non-linear or exponential trends with variables such as population, GDP, and household consumption. Therefore, logarithmic and semi-logarithmic regression models are more appropriate because they transform exponential relationships into approximately linear ones, improving model estimation and interpretation.

3. Addressing the statistical characteristics of waste data

A recent study by Mwakalinga and Samli (2026) also recognises that municipal solid waste data are characterized by positive skewness, spatial dependence and heteroscedasticity. Instead of using a logarithmic transformation, the authors employed a Spatial Lag Gamma Generalised Linear Model because of the spatial nature of their data. Nevertheless, the study confirms that waste generation data rarely satisfy the assumptions of simple linear regression without an appropriate statistical treatment.

4. Theoretical support from urban scaling theory

Finally, Lu et al. (Worldwide Scaling of Waste Generation in Urban Systems) demonstrate that municipal solid waste generation follows a power-law relationship with city population.

The general relationship is expressed as

Y=αPβ

which becomes linear after taking logarithms

log(Y)=log(α)+βlog(P)

This provides a theoretical justification for analyzing waste generation in logarithmic space, since it converts non-linear scaling relationships into linear regression models that are easier to estimate and interpret.

Why I used log(1+Y)

Considering these studies together, the logarithmic transformation in my research was adopted for four complementary reasons:

to improve the normality assumption of the regression model;

to linearise potentially exponential relationships between waste generation and explanatory variables;

to reduce the influence of skewness and heteroscedasticity commonly observed in waste generation data;

and to retain observations with zero waste generation, since log(0) is undefined whereas log(1+0)=0.

Therefore, the use of log(1+Y) in my model was not an arbitrary mathematical choice. Rather, it was a methodological decision supported by previous empirical studies and by the statistical characteristics of municipal solid waste generation data.

2. Why was Distance to CBD included?

The inclusion of Distance to CBD is also supported by recent literature.

From an urban planning perspective, the Central Business District (CBD) represents the concentration of commercial activities, services, employment opportunities, accessibility and urban intensity. Consequently, the distance from the CBD acts as a proxy for several spatial characteristics influencing waste generation.

In particular, Golafshani et al. (2026) identified Population, Distance to CBD, and Land Area as the three most influential predictors of municipal solid waste generation using SHAP explainable AI analysis. Their findings indicate that urban form and spatial structure play a significant role in explaining variations in waste generation.

In addition, the recent study from Tanzania (2023) highlights the importance of spatial determinants, accessibility and neighbourhood effects in municipal solid waste generation, reinforcing the relevance of incorporating spatial variables into predictive waste-generation models.

Although Rio Maior is considerably smaller than a metropolitan area, its CBD still concentrates commercial, administrative and service activities. Therefore, the distance between each recycling container and the CBD can reasonably represent variations in human activity intensity and, consequently, recyclable waste generation.

I hope these additional references help clarify the methodological decisions adopted in my research.

Thank you once again for your valuable guidance and constructive feedback. I sincerely appreciate your time and would be grateful for any additional comments or suggestions you may have.

All documents are attached to this email for your reference. Best regards. Esmaeil Keyvanloo

////////////////

Dear Professor Bigotte,

I would like to provide some clarification regarding the R² value, which was 0.073889.

As I mentioned previously, I was unfortunately unable to obtain a complete land-use database at the parcel/building level. As far as I know, these data are held by the Municipality, and obtaining access requires coordination with the municipal authorities and possibly official authorization. Since I did not have access to this database, I had to collect information from several publicly available sources and combine them to create an incomplete land-use database. Consequently, many land parcels do not have land-use information, which has directly affected the quality of the analysis and the model's results.

In the images attached, you can see that around several waste containers there are many parcels with no land-use classification. In my opinion, this lack of information is one of the main reasons for the low R² value.

I believe that if we could obtain a complete and accurate land-use database, together with detailed population data at the parcel or building level, it would be possible to perform a much more reliable analysis, and the model's performance would improve significantly.

In addition, increasing the buffer radius could include more buildings that are likely to contribute to waste generation, which may also improve the explanatory power of the model.

I would also like to inform you that my FICO Xpress license expired on 16 July. Since then, I have been unable to open the software. Therefore, I would appreciate it if the University could renew my license so that I can continue developing the model and my research.

Finally, I would like to express my sincere interest in continuing my PhD under your supervision. It would be a great honor for me to complete my doctoral studies with your guidance, support, and valuable experience.

I have attached the relevant images to better illustrate these issues. Thank you very much for your time, support, and consideration. I look forward to receiving your valuable comments and suggestions.

/////////////

Subject: Revised Thesis Project Presentation for Final Review

Dear Professor João Bigotte,

Thank you very much for your detailed comments and valuable suggestions following our meeting.

I have carefully revised both the PowerPoint presentation and the thesis project document according to your recommendations. In particular, I have:

Added a brief introduction to the WSmartRoute+ project and clarified the relationship with my PhD research.

Reorganised the presentation to match the outline discussed during our meeting.

Revised the statistical modelling section to clearly state that the preliminary regression model requires further improvement.

Reduced the introduction to the deterministic p-median model and added a map illustrating the optimisation results.

Updated the research work plan to clearly distinguish the three stages of the PhD research:

Preliminary demand modelling,

Deterministic facility location,

Future stochastic facility location.

Revised the conclusion to better reflect the current status of the research and the future PhD work.

I would be very grateful if you could kindly review the revised PowerPoint presentation, which is attached to this email, and let me know if any further changes are required before the defense.

Thank you again for your guidance and continuous support.

////
