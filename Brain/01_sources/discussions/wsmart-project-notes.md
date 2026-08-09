---
name: wsmart-project-notes
title: w smart project
type: source
category: discussions
source_file: DATA/my concerns and history of discussion with chat gpt/doc/w smart project.docx
source_sha256: acf01de2772a16bfdfc8560bea8cd7c8df63c715b2668564a6bb4b4a93fc0394
source_bytes: 69383
ingested: 2026-08-09
words: 5777
verbatim: true
---

> Faithful conversion of `DATA/my concerns and history of discussion with chat gpt/doc/w smart project.docx`. Do not edit — edit the source and re-run the ingest.

WSmartRoute+_Application (2)(20260809-091126).pdf

PDF

خلاصه نکات مهم را بگ.

Called tool

خلاصه‌ی مهم‌ترین نکات فایل WSmart Route+:

هدف اصلی پروژه: توسعه یک سیستم هوشمند برای برنامه‌ریزی جمع‌آوری پسماند که به‌جای مسیرهای ثابت (Static Routes) از مسیرهای پویا (Dynamic Routes) بر اساس وضعیت واقعی یا پیش‌بینی‌شده پرشدگی مخازن استفاده کند. پروژه ترکیبی از Data Analytics + Operations Research + Route Optimization است.

مشکل اصلی: در روش سنتی، کامیون‌ها طبق برنامه ثابت حرکت می‌کنند، حتی اگر مخزن تقریباً خالی باشد. در داده‌های ERSUC، حدود 52٪ مخازن در مناطق روستایی با کمتر از 25٪ پرشدگی تخلیه شده‌اند؛ در مقابل، در مناطق شهری مشکل overflow وجود دارد.

پروژه برای فهم وضعیت مخزن سه منبع داده را مقایسه می‌کند: مشاهده راننده، سنسور ثابت و سنسور متحرک. برای سنسورهای ثابت، Valorsul از قبل حدود 650 سنسور داشته و برای مقایسه سنسور متحرک با دو روش دیگر، آزمایش 6ماهه پیش‌بینی شده است.

سپس با روش‌های پیش‌بینی و Machine Learning، از مدل‌های سری زمانی تا LSTM Neural Networks، میزان پرشدگی آینده مخازن پیش‌بینی می‌شود. اطلاعاتی مانند نوع منطقه، روز هفته، تعطیلات و غیره نیز می‌تواند وارد مدل شود.

بعد از پیش‌بینی تقاضا، مسئله اصلی بهینه‌سازی مسیر جمع‌آوری است. نکته مهم این است که صرفاً «مخازن پر را جمع کنیم» کافی نیست؛ فاصله، هزینه، سطح خدمات، احتمال overflow و اثر تصمیم امروز بر روزهای آینده نیز باید در نظر گرفته شود.

برای مدل‌سازی مسیرها، پروژه به سمت Dynamic/Stochastic Inventory Routing Problem (IRP) می‌رود. مدل‌های MILP با GAMS و CPLEX نیز برای بررسی راه‌حل‌های بهینه در مسائل کوچک‌تر در نظر گرفته شده‌اند.

چون مدل‌های دقیق برای شبکه‌های بزرگ زمان‌بر هستند، پروژه در مرحله بعد از Heuristics و Metaheuristics استفاده می‌کند تا مسیرهای روزانه در زمان کوتاه تولید شوند و این روش‌ها در یک Decision Support Tool با GUI قرار گیرند.

یک بخش مهم دیگر، Sensor Placement است: قرار نیست همه مخازن سنسور داشته باشند، چون بسیار گران است. پروژه تعیین می‌کند کدام مخازن ارزش نصب سنسور ثابت دارند تا بهترین نسبت benefit/cost حاصل شود.

در Cost–Benefit Analysis، سیستم سنتی، بهینه‌سازی فرکانس/مسیر، شبکه کاملاً سنسوردار و راهکارهای هوشمند با هم مقایسه می‌شوند. مطالعات موردی اصلی ERSUC و Valorsul هستند.

در پایان، سیستم در محیط واقعی ERSUC آزمایش می‌شود. برای پایلوت حدود 75 سنسور ثابت پیش‌بینی شده و سایر مخازن با سنسور متحرک یا مشاهده رانندگان کنترل می‌شوند.

5 هدف اصلی پروژه

1. کاهش عدم‌قطعیت در میزان پرشدگی مخازن2. توسعه سیستم برنامه‌ریزی مسیرهای هوشمند و پویا3. تعیین بهترین مخازن برای نصب سنسور4. انجام Cost–Benefit Analysis در شرایط واقعی5. اجرای Pilot/Testbed واقعی

طبق پروپوزال، انتظار تیم این بوده که سیستم بتواند حدود 30٪ هزینه‌ها را کاهش دهد و در عین حال سطح خدمات به شهروندان را افزایش دهد.

نکته کلیدی: کل پروژه را می‌توان در یک زنجیره ساده خلاصه کرد:

Data → Fill-level Prediction → Dynamic Routing → Sensor Placement → Decision Support Tool → Cost-Benefit Analysis → Real-world Pilot

پروژه از 2 ژانویه 2023 با مدت برنامه‌ریزی‌شده 36 ماه تعریف شده است.

با جزییات بیشتر بتویس

حتماً. در ادامه، محتوای فایل WSmart Route+ را با جزئیات بیشتر، ولی به‌صورت منظم و قابل‌فهم خلاصه می‌کنم.

1. معرفی پروژه WSmart Route+

نام کامل پروژه:

WSmart Route+ — Towards a Smart Waste Collection Route Planning System

هدف پروژه ایجاد یک سیستم هوشمند برنامه‌ریزی جمع‌آوری پسماند است که تصمیم بگیرد:

کدام مخزن → چه زمانی → با چه مسیری → جمع‌آوری شود.

در سیستم‌های سنتی، مسیر و برنامه جمع‌آوری معمولاً ثابت است؛ یعنی کامیون طبق برنامه به مخازن مراجعه می‌کند، بدون اینکه الزاماً بداند هر مخزن چقدر پر شده است. WSmart Route+ می‌خواهد این سیستم را به Smart Dynamic Collection تبدیل کند.

پروژه از 2 ژانویه 2023 شروع شده و مدت آن 36 ماه تعریف شده است.

2. مشکل اصلی چیست؟

مسئله اصلی عدم قطعیت درباره مقدار زباله موجود در هر مخزن است.

اگر شرکت نداند هر مخزن چقدر پر است، ممکن است کامیون برای تخلیه مخزنی حرکت کند که تقریباً خالی است. از طرف دیگر ممکن است مخزن دیگری قبل از زمان برنامه‌ریزی‌شده پر شود و Overflow اتفاق بیفتد.

بنابراین دو مشکل متضاد داریم:

در مناطق کم‌تقاضا:

Unnecessary collection → wasted kilometres → wasted time → higher costs

در مناطق پرتراکم:

Late collection → overflow → poor service → environmental/public-health problems

داده‌های ERSUC نشان داده بود که در مناطق روستایی حدود 52٪ مخازن بازیافت در زمان جمع‌آوری کمتر از 25٪ پر بودند. بنابراین تعداد قابل‌توجهی از سفرهای جمع‌آوری عملاً بهره‌وری پایینی داشتند.

3. ایده مرکزی پروژه

ایده اصلی WSmart Route+ این است:

اول وضعیت مخازن را بفهمیم یا پیش‌بینی کنیم، سپس بر اساس آن مسیر جمع‌آوری را بهینه کنیم.

یعنی:

Data Acquisition↓Data Analytics↓Fill-Level Prediction↓Determine which bins should be collected↓Dynamic Route Optimization↓Daily Collection Plan

بنابراین پروژه صرفاً یک پروژه Routing نیست؛ بلکه Data Analytics و Operations Research را با هم ترکیب می‌کند.

4. سه روش برای فهمیدن میزان پرشدگی مخزن

یکی از مهم‌ترین قسمت‌های پروژه مقایسه سه منبع اطلاعاتی است.

روش اول: Driver Visual Observations

راننده هنگام مراجعه به مخزن، میزان پرشدگی را به‌صورت بصری ثبت می‌کند.

مثلاً:

25%50%75%100%

مزیت بزرگ این روش هزینه بسیار پایین است، زیرا نیازی به نصب سنسور روی هزاران مخزن وجود ندارد.

ولی مشکل آن این است که:

Human Error وجود دارد و اطلاعات نیز فقط زمانی دریافت می‌شود که راننده به مخزن مراجعه کند.

5. روش دوم: Static Sensors

روش دقیق‌تر نصب Volumetric Sensor روی مخزن است.

این سنسورها به‌صورت مداوم میزان پرشدگی مخزن را اندازه‌گیری می‌کنند.

در پروژه از سنسورهای توسعه‌یافته توسط EVOX Technologies استفاده شده که مبتنی بر فناوری Ultrasonic هستند و دارای واحد ارتباطی و باتری‌اند.

در Valorsul از سال 2020 حدود 650 سنسور ثابت نصب شده بود؛ بنابراین پروژه به حجم قابل‌توجهی از داده‌های واقعی دسترسی داشت.

مزیت:

Accurate + Continuous Monitoring

مشکل:

High Investment Cost

چون شرکت‌های بزرگ ممکن است هزاران مخزن داشته باشند، نصب سنسور روی همه آنها بسیار گران خواهد بود.

6. روش سوم: Mobile Sensors

پروژه یک راهکار بین دو حالت بالا را نیز بررسی می‌کند:

Mobile Sensor

در این حالت سنسور روی هر مخزن نصب نمی‌شود. راننده سنسور را همراه خود دارد و هنگام مراجعه به مخزن، میزان پرشدگی را با آن اندازه‌گیری می‌کند.

یعنی به جای:

1 sensor per bin

داریم:

1 mobile sensor per driver

در نتیجه هزینه سخت‌افزار به‌شدت کاهش پیدا می‌کند.

برای بررسی این روش، یک آزمایش 6ماهه طراحی شده بود. نکته مهم این بود که همان مخازنی انتخاب شوند که Static Sensor دارند.

بنابراین برای یک مخزن و در یک دوره زمانی می‌توان سه مقدار را مقایسه کرد:

Static Sensor ReadingMobile Sensor ReadingDriver Visual Observation

این طراحی اجازه می‌دهد دقت و ارزش اطلاعات هر سه روش مستقیماً مقایسه شود.

7. مرحله بعد: پیش‌بینی Fill Level

فقط دانستن وضعیت فعلی مخزن کافی نیست.

فرض کنید امروز مخزن 60٪ پر است.

برای برنامه‌ریزی چند روز آینده باید بدانیم:

فردا چقدر خواهد بود؟

دو روز دیگر چقدر خواهد بود؟

بنابراین پروژه از Predictive Models استفاده می‌کند.

روش‌های مورد بررسی از مدل‌های ساده‌تر Time Series تا مدل‌های پیشرفته‌تر مانند:

LSTM Neural Networks

را شامل می‌شوند.

8. متغیرهای مؤثر بر تولید زباله

در مدل‌های پیشرفته می‌توان علاوه بر تاریخچه Fill Level، ویژگی‌های محیطی و زمانی را هم وارد کرد.

در پروپوزال مثال‌هایی مانند:

نوع منطقه یا Neighborhood

Commercial / Residential

Day of the week

Holidays

School days

ذکر شده است.

بنابراین مدل تلاش می‌کند الگوی تولید زباله را برای هر مکان یاد بگیرد.

9. آموزش و ارزیابی مدل‌های پیش‌بینی

برای ارزیابی مدل‌ها، داده‌های هر منبع به دو قسمت تقسیم می‌شوند:

Training Set

و

Testing Set

مدل با Training Set آموزش داده می‌شود و سپس Fill Level مربوط به Testing Set را پیش‌بینی می‌کند.

در نهایت عملکرد سه منبع داده مقایسه می‌شود:

Driver Data vs Mobile Sensor vs Static Sensor

هدف صرفاً مقایسه خطای آماری نیست؛ پروژه می‌خواهد ببیند هر نوع اطلاعات چه ارزش عملیاتی دارد، مثلاً:

چند سفر غیرضروری حذف می‌شود؟

چند Overflow قابل جلوگیری است؟

و آیا هزینه سنسورها در برابر این مزایا توجیه‌پذیر است؟

10. Task 1 — Data Analytics and Predictive Models

بنابراین Task 1 اساساً مربوط به:

Data Acquisition + Data Analysis + Prediction

است.

سه Data Source اصلی:

1. Driver records

2. Static sensor readings

3. Mobile sensor readings

هستند.

Milestone مربوط به این بخش نیز:

M1 – Prediction Models Developed

تعریف شده بود.

11. Task 2 — Smart Waste Collection Routing Problem Modelling

بعد از اینکه مقدار پسماند مشخص یا پیش‌بینی شد، سؤال بعدی این است:

کدام مخازن را امروز جمع‌آوری کنیم و مسیر کامیون چگونه باشد؟

اینجاست که Operations Research وارد می‌شود.

یکی از نکات علمی مهم پروژه این است که نباید ابتدا صرفاً مخازن پر انتخاب شوند و سپس یک TSP/VRP روی آنها اجرا شود.

چرا؟

فرض کنید یک مخزن 95٪ پر است و کامیون برای تخلیه آن می‌رود.

یک مخزن 70٪ نیز فقط 100 متر با آن فاصله دارد.

ممکن است منطقی باشد مخزن دوم هم جمع‌آوری شود، حتی اگر هنوز کاملاً پر نشده باشد.

بنابراین:

Selection of bins + Routing

باید در یک چارچوب تصمیم‌گیری مناسب بررسی شوند.

12. مسئله فقط امروز نیست

یکی دیگر از نکات مهم پروژه Planning Horizon است.

ممکن است بهترین تصمیم برای امروز، بهترین تصمیم برای کل هفته نباشد.

مثلاً:

امروز مخزن A را جمع نکنیم → هزینه امروز کمتر شود.

اما:

فردا مخزن A سرریز کند → هزینه و Service Failure ایجاد شود.

بنابراین تصمیم امروز روی روزهای آینده تأثیر دارد.

به همین دلیل پروژه به سمت مدل‌های:

Dynamic

و

Stochastic

حرکت می‌کند.

13. Inventory Routing Problem

یکی از پایه‌های مدل‌سازی پروژه Inventory Routing Problem – IRP است.

به زبان ساده، IRP دو تصمیم را همزمان بررسی می‌کند:

When to collect?

و

How to route?

در WSmart Route+ این مفهوم برای جمع‌آوری پسماند توسعه داده می‌شود.

Milestone دوم پروژه:

M2 – Smart Routing Models Developed

بود که شامل توسعه مدل‌های Dynamic and Stochastic Inventory Routing with Profit می‌شد.

14. Service Level نیز وارد مدل می‌شود

هدف فقط کاهش هزینه نیست.

مدل باید Overflow و سطح خدمات به شهروندان را نیز در نظر بگیرد.

دو رویکرد در پروپوزال مطرح شده است:

Multi-objective approach:

Maximize Profit+Minimize Overflows

یا اینکه هزینه Overflow در تابع هدف اصلی وارد شود.

15. مدل‌های ریاضی

برای این مسائل، مدل‌های:

Mixed-Integer Linear Programming — MILP

توسعه داده می‌شوند.

در پروپوزال ذکر شده که مدل‌ها با:

GAMS

پیاده‌سازی و با:

CPLEX Optimizer

حل می‌شوند.

اما یک مشکل وجود دارد:

برای شبکه‌های واقعی و بزرگ، حل دقیق این مدل‌ها ممکن است زمان زیادی ببرد.

16. Task 3 — Decision Supporting Tool

به همین دلیل Task 3 بسیار مهم است.

مدل دقیق ممکن است برای مسائل کوچک یا متوسط مناسب باشد، ولی شرکت مدیریت پسماند ممکن است هزاران مخزن داشته باشد.

از طرف دیگر مسیر باید هر روز سریع تولید شود.

بنابراین پروژه از:

Heuristics

و

Metaheuristics

برای پیدا کردن جواب‌های خوب یا نزدیک به بهینه در زمان کوتاه استفاده می‌کند.

17. ساخت Decision Support System

این الگوریتم‌ها در نهایت در یک ابزار کاربردی قرار می‌گیرند.

یعنی پروژه فقط قرار نیست مقاله علمی تولید کند.

هدف ساخت یک:

Decision Supporting Tool

با:

Graphical User Interface – GUI

است.

در این ابزار، دو جزء مهم با هم ترکیب می‌شوند:

Predictive Models from Task 1

Routing Algorithms / Metaheuristics

بنابراین کاربر شرکت مدیریت پسماند می‌تواند اطلاعات مخازن را دریافت کند و مسیر پیشنهادی جمع‌آوری را بگیرد.

18. Task 4 — Strategic Location for Sensors Placement

این بخش یکی از مهم‌ترین قسمت‌های استراتژیک پروژه است.

سؤال:

آیا باید روی همه مخازن سنسور نصب کنیم؟

پاسخ پروژه:

نه لزوماً.

اگر یک شرکت هزاران مخزن داشته باشد، Full Sensorization بسیار گران است.

بنابراین سؤال علمی این است:

Which bins are worth being sensorized?

یعنی کدام مخازن باید سنسور ثابت داشته باشند تا بیشترین ارزش اطلاعاتی و عملیاتی ایجاد شود؟

Milestone این قسمت:

M3 – Sensor Placement Models Developed

است.

19. Task 5 — Cost-Benefit Analysis

بعد باید مشخص شود آیا سیستم هوشمند از نظر اقتصادی واقعاً ارزش دارد یا خیر.

برای این منظور Task 5 یک Cost–Benefit Analysis روی داده‌های واقعی انجام می‌دهد.

دو Case Study مهم:

ERSUC

و

Valorsul

هستند.

20. سناریوهای مقایسه

پروژه چند سطح مختلف Smartness را مقایسه می‌کند.

Scenario 1 — Current Situation

روش سنتی:

Blind Collection

بدون بهینه‌سازی جدی Frequency و Route.

مواردی مانند:

Collection frequencyWaste collectedKilometres travelledFill level at collection

بررسی می‌شوند.

Scenario 2 — Optimization without smart fill-level information

هنوز Blind Collection است، اما اثر بهینه‌سازی:

Collection Frequency

و

Route

به‌صورت جداگانه و ترکیبی بررسی می‌شود.

Scenario 3 — Full Smart/Sensorized Collection

در این حالت شبکه به‌صورت کامل سنسوردار فرض می‌شود.

اطلاعات Fill Level + Prediction + IRP + Route Optimization با هم ترکیب می‌شوند.

هدف این مقایسه این است که مشخص شود:

Sensorization واقعاً چقدر ارزش اضافه ایجاد می‌کند؟

21. Task 6 — Real-World Pilot

بعد از Simulation، سیستم باید در دنیای واقعی آزمایش شود.

Task 6 برای همین طراحی شده است.

محل اصلی Pilot:

ERSUC

بوده است.

پایلوت برای بازه April–December طراحی شده تا عملکرد سیستم در فصل‌ها، شرایط آب‌وهوایی و حجم‌های مختلف تقاضا بررسی شود.

22. حدود 75 سنسور در Pilot

در منطقه آزمایشی، پروژه پیش‌بینی کرده بود حدود:

75 Static Sensors

نصب شود.

سایر مخازن با:

Mobile Sensors

یا

Driver Visual Observations

پایش شوند.

سپس ابزار هوشمند هر روز مسیر پیشنهادی جمع‌آوری را در اختیار شرکت قرار دهد.

این قسمت بسیار مهم است زیرا پروژه را از یک مدل دانشگاهی به یک:

Real-world Decision Support System

تبدیل می‌کند.

23. اهداف رسمی پروژه

پنج هدف اصلی در پروپوزال به‌طور مشخص ذکر شده است:

هدف 1 — Data

بررسی روش‌های مختلف جمع‌آوری و پردازش Fill-Level Data برای کاهش عدم قطعیت.

هدف 2 — Smart Routing

ساخت و آزمایش ابزار برنامه‌ریزی مسیرهای هوشمند با استفاده از اطلاعات سنسورها و رانندگان.

هدف 3 — Sensor Placement

ساخت مدل‌هایی برای تعیین اینکه کدام مخازن باید سنسور داشته باشند.

هدف 4 — Cost-Benefit

مقایسه اقتصادی و عملیاتی سیستم فعلی با سیستم هوشمند.

هدف 5 — Real Pilot

اجرای آزمایش واقعی سیستم.

24. Milestones مهم

پروژه چند Milestone اصلی تعریف کرده است:

| Milestone | خروجی |
|---|---|
| M1 | Prediction Models Developed |
| M2 | Smart Routing Models Developed |
| M3 | Sensor Placement Models Developed |
| M4 | Decision Support Tool Developed |
| M5 | Cost-Benefit Analysis Concluded |

طبق برنامه اولیه، M1 پایان 2023، M2 سپتامبر 2024، M3 پایان 2024، M4 مارس 2025 و M5 ژوئن 2025 برنامه‌ریزی شده بودند.

25. اعضا و تخصص‌های پروژه

پروژه کاملاً Multidisciplinary طراحی شده است.

تیم اصلی شامل 8 پژوهشگر بوده و چند مرکز تحقیقاتی، شرکت فناوری و شرکت مدیریت پسماند در آن حضور دارند.

تقسیم تخصص‌ها تقریباً به این شکل است:

CEGIST → Operations Research + Mathematical Models + Waste Routing

INESC-ID → Data Science + Machine Learning

CITTA / University of Coimbra → Transportation Systems + Solution Methods

EVOX → Sensors + Monitoring Technology + Hardware/Software

ERSUC & Valorsul → Real Waste Collection Operations/Data

این تقسیم نقش در پروپوزال صریحاً توضیح داده شده است.

26. نقش University of Coimbra

دانشگاه Coimbra یکی از شرکای علمی پروژه است و António Pais Antunes از اعضای اصلی تیم پروژه بوده است.

در Task 3 نیز سهم قابل‌توجهی برای Coimbra دیده می‌شود؛ از جمله توسعه روش‌های حل و Decision Support برای مسئله Smart Waste Collection Routing.

همچنین در Task 6، تیم‌های EVOX و University of Coimbra به‌عنوان تیم‌های اصلی اجرای پایلوت معرفی شده‌اند.

27. شرکت‌های واقعی پروژه

دو Waste Management Company اصلی عبارت‌اند از:

ERSUC: در زمان تدوین پروژه عمدتاً دارای برنامه‌ریزی دستی و Static Routes معرفی شده است.

Valorsul: یک مرحله جلوتر بوده، زیرا تعدادی سنسور روی مخازن نصب کرده بود، ولی Routeها همچنان عمدتاً Static بودند.

بنابراین این دو شرکت دو سطح مختلف از بلوغ Smart Waste Collection را نشان می‌دهند.

28. خروجی عملی پروژه

خروجی نهایی فقط یک مدل ریاضی نیست.

هدف رسیدن به یک Prototype Smart Waste Collection Planning Tool است.

این Prototype قرار است:

Fill-level data دریافت کند↓Fill level آینده را پیش‌بینی کند↓مخازن مناسب برای جمع‌آوری را تعیین کند↓مسیرهای Dynamic ایجاد کند↓نتیجه را به Decision Maker ارائه دهد.

پروپوزال حتی پیش‌بینی کرده که Prototype از طریق قراردادهای همکاری، رایگان در اختیار شرکت‌های مدیریت پسماند قرار گیرد.

29. اثر مورد انتظار

پروژه سه نوع اثر مهم دارد:

اقتصادی: کاهش هزینه، کیلومتر طی‌شده و استفاده غیرضروری از منابع.

محیط‌زیستی: کاهش سفر کامیون‌ها و اثرات محیطی جمع‌آوری.

اجتماعی/خدماتی: کاهش Overflow و افزایش کیفیت خدمات به شهروندان.

پروژه این اهداف را با SDG 6، SDG 9 و SDG 11 مرتبط می‌کند.

بر اساس تجربه قبلی تیم، در Proposal برآورد شده که ابزار بتواند:

حدود 30٪ هزینه‌ها را کاهش دهد

و هم‌زمان:

Service Level را افزایش دهد.

30. خلاصه کل پروژه در یک تصویر مفهومی

می‌توان کل WSmart Route+ را این‌طور در ذهن نگه داشت:

Waste Bins

↓

Driver Observations / Mobile Sensors / Static Sensors

↓

Task 1

Data Analytics & Fill-Level Prediction

↓

Task 2

Dynamic & Stochastic Routing Models

↓

Task 3

Fast Algorithms + Decision Support Tool

↓

Task 4

Strategic Sensor Placement

↓

Task 5

Cost-Benefit Analysis

↓

Task 6

Real-World Pilot

↓

نتیجه نهایی

کاهش هزینه + کاهش کیلومتر + کاهش Overflow + افزایش Service Level

در واقع، مهم‌ترین ایده علمی WSmart Route+ این است که اطلاعات، پیش‌بینی و بهینه‌سازی را به یک زنجیره تصمیم‌گیری واحد تبدیل کند؛ یعنی فقط Route Optimization یا فقط Sensorization نیست، بلکه می‌خواهد مشخص کند چه اطلاعاتی واقعاً ارزش دارد، چگونه از آن برای پیش‌بینی استفاده کنیم، چگونه بر اساس آن تصمیم جمع‌آوری بگیریم و آیا منفعت این هوشمندسازی از هزینه آن بیشتر است یا نه.

Pasted text(20260809-093605).txt

Document

فایل جدید WSmart Route+ دریافت شد. این فایل شامل متن کامل‌تر پروپوزال پروژه است؛ از جمله اهداف، شکاف‌های پژوهشی، ۶ Task، مدل‌های IRP، روش‌های پیش‌بینی، Sensor Placement، Cost–Benefit Analysis و نقش اعضای پروژه.

اگر هدفتان ادامه همان کار قبلی است، می‌توانم این نسخه را مبنا قرار دهم و یک خلاصه بسیار دقیق و کامل، بخش‌به‌بخش و مخصوص فهم پروژه/آمادگی جلسه تهیه کنم.

اره

بله. بر اساس نسخه کامل فایل، خلاصه دقیق را در چند بخش می‌نویسم تا هم برای فهم پروژه و هم برای جلسه/مصاحبه یا دفاع کاربردی باشد.

1. پروژه دقیقاً درباره چیست؟

WSmart Route+ یک پروژه تحقیقاتی برای ایجاد سیستم هوشمند برنامه‌ریزی جمع‌آوری پسماند است.

ایده اصلی این است که سیستم سنتی:

Static / Blind Collection

به سیستم:

Data-driven + Predictive + Dynamic Waste Collection

تبدیل شود.

در روش سنتی، مسیرها از قبل تعیین شده‌اند و کامیون‌ها در فواصل مشخص به مخازن مراجعه می‌کنند، حتی اگر مقدار زباله داخل مخزن کم باشد. پروژه می‌خواهد ابتدا وضعیت یا Fill Level مخازن را بفهمد، آینده آنها را پیش‌بینی کند و سپس مشخص کند کدام مخازن، چه زمانی و در چه مسیری جمع‌آوری شوند.

2. چرا این پروژه لازم است؟

یک مثال بسیار مهم در پروپوزال از داده‌های ERSUC آمده است.

در مناطق روستایی:

52% مخازن هنگام جمع‌آوری کمتر از 25% پر بودند.

فقط:

9% مخازن بیشتر از 75% پر بودند.

یعنی کامیون‌ها در بسیاری از موارد مسافت طی می‌کنند تا مخازنی را تخلیه کنند که تقریباً خالی هستند.

در مناطق شهری مشکل برعکس است:

Overflow

اتفاق می‌افتد و زباله ممکن است اطراف مخزن جمع شود.

بنابراین پروژه با دو مشکل روبه‌رو است:

Rural areas → unnecessary collections

Urban areas → overflow

هدف، پیدا کردن تعادل بین:

Cost Efficiency ↔ Service Level

است.

3. سه ستون اصلی تحقیق

کل پروژه روی سه Research Stream اصلی بنا شده است:

A. Data & Prediction

چگونه Fill Level را اندازه‌گیری و پیش‌بینی کنیم؟

B. Dynamic Route Optimization

با استفاده از این اطلاعات چگونه بهترین برنامه جمع‌آوری را تعیین کنیم؟

C. Sensor Placement

کدام مخازن واقعاً باید Static Sensor داشته باشند؟

این سه بخش در نهایت در یک Decision Support Tool با یکدیگر ادغام می‌شوند.

4. بخش اول: Data Acquisition

پروژه سه روش مختلف برای اندازه‌گیری Fill Level را مقایسه می‌کند.

| روش | دقت | تعداد مشاهدات | هزینه |
|---|---|---|---|
| Driver Observation | پایین‌تر | کم | بسیار کم |
| Mobile Sensor | بالا | کم | متوسط/کم |
| Static Sensor | بالا | زیاد/Continuous | بالا |

این مقایسه یکی از Contributionهای اصلی پروژه است.

5. Driver Observation

در حال حاضر رانندگان برخی شرکت‌ها قبل از تخلیه مخزن، Fill Level را ثبت می‌کنند.

مثلاً:

25% – 50% – 75% – 100%

مزیت:

تقریباً بدون هزینه اضافی است.

مشکل:

Human Error + Subjectivity

و همچنین فقط زمانی داده داریم که راننده به مخزن مراجعه کند.

نکته مهم این است که پروژه می‌گوید این اطلاعات در شرکت‌ها وجود دارد، اما معمولاً برای Optimization به‌طور مؤثر استفاده نمی‌شود.

6. Static Sensors

راه دوم نصب سنسور ثابت داخل مخزن است.

مزیت بزرگ:

Accurate + Frequent/Continuous Information

اما مشکل:

Cost

است.

شرکت‌ها هزاران مخزن دارند و Sensorizing کل شبکه می‌تواند سرمایه‌گذاری بسیار بزرگی بخواهد.

Valorsul از قبل حدود:

650 volumetric sensors

نصب کرده بود.

7. Mobile Sensor

ایده سوم بسیار جالب است:

به جای اینکه:

هر Bin یک Sensor داشته باشد

راننده یک:

Mobile Sensor

همراه خود داشته باشد.

در هنگام مراجعه، Fill Level دقیق اندازه‌گیری می‌شود.

بنابراین:

Accuracy ≈ Sensor

اما:

Cost << Full Static Sensorization

این روش تلاش می‌کند مزایای دو روش قبلی را ترکیب کند.

8. آزمایش بسیار مهم سه روش

در Task 1 یک آزمایش 6ماهه طراحی شده است.

روی همان مخازنی که Static Sensor دارند، راننده:

Visual Observation

و:

Mobile Sensor Measurement

هم انجام می‌دهد.

بنابراین برای:

Same bin + Same period

سه Data Source خواهیم داشت:

Static SensorMobile SensorDriver Observation

و می‌توان آنها را مستقیماً مقایسه کرد.

این از نظر طراحی پژوهش بسیار مهم است.

9. Prediction

مرحله بعدی فقط دانستن Fill Level فعلی نیست.

سیستم باید بتواند بگوید:

این مخزن دو یا سه روز دیگر احتمالاً چقدر پر خواهد بود؟

بنابراین هر سه Dataset به مدل‌های Prediction داده می‌شوند.

روش‌های موردنظر از:

Time-Series Models

تا:

LSTM Neural Networks

هستند.

10. چه اطلاعاتی می‌تواند وارد Prediction شود؟

LSTM می‌تواند اطلاعات دیگری نیز دریافت کند، مانند:

Neighbourhood type

Commercial / Residential

Day of week

Holiday

School day

و سایر مشخصات مکانی و زمانی.

هدف:

Future fill-level prediction for individual bins

است.

11. Train/Test

برای ارزیابی علمی Prediction:

هر Dataset به:

Training Set

و

Testing Set

تقسیم می‌شود.

مدل روی Training آموزش می‌بیند و سپس Fill Level مربوط به Testing را پیش‌بینی می‌کند.

در نهایت سؤال مهم این نیست که فقط کدام مدل Error کمتری دارد.

بلکه:

این افزایش Accuracy چه ارزش عملیاتی دارد؟

مثلاً:

How many unnecessary visits can be avoided?

یا:

How many overflows can be prevented?

12. خروجی Task 1

Task 1 دو Paper مشخص دارد:

Paper 1:Comparison of three monitoring approaches: drivers records, static sensors and mobile sensors

Paper 2:New predictive models to estimate waste deposition based on drivers records versus sensors readings.

13. حالا وارد Optimization می‌شویم

فرض کنید Prediction Model گفته:

Bin A = 90%

Bin B = 65%

Bin C = 20%

Bin D = 85%

سؤال ساده این است:

آیا فقط A و D را جمع کنیم؟

پروژه می‌گوید الزاماً نه.

ممکن است B نزدیک A باشد و با یک Detour کوچک بتوان B را هم تخلیه کرد.

بنابراین استفاده از یک Threshold ساده مثل:

Collect if Fill Level > 80%

ممکن است بهترین تصمیم نباشد.

14. چرا TSP/VRP ساده کافی نیست؟

بسیاری از سیستم‌های موجود:

ابتدا مخازن را بر اساس Fill Level انتخاب می‌کنند.

بعد:

TSP / VRP

را برای آنها حل می‌کنند.

WSmart Route+ می‌گوید این روش چند مشکل دارد.

ممکن است مخزن نیمه‌پر در کنار یک مخزن پر باشد و جمع‌آوری آن اقتصادی باشد.

همچنین Service Level مهم است.

و مهم‌تر از همه:

Best decision today ≠ Best decision over several days

15. SWCRP

تیم قبلاً مسئله‌ای به نام:

Smart Waste Collection Routing Problem — SWCRP

معرفی کرده بود.

در نسخه اولیه از:

Vehicle Routing Problem with Profits — VRPP

استفاده شده بود.

هدف:

Maximize Daily Profit

بود.

یعنی تقریباً:

Revenue from collected recyclable waste − Transportation Cost

اما مشکل این بود که Planning Horizon فقط:

1 day

بود.

16. مشکل Myopic Decision

اگر فقط امروز را Optimize کنیم، تصمیم ممکن است:

Myopic

باشد.

مثلاً امروز یک Bin را جمع نمی‌کنیم چون اقتصادی نیست.

ولی فردا Overflow می‌کند.

بنابراین پروژه به جای:

One-day VRPP

به سمت:

Multi-day Inventory Routing Problem

حرکت کرده است.

17. Inventory Routing Problem — IRP

IRP سه سؤال را با هم حل می‌کند:

1. When to visit?

2. How much to collect?

3. How to combine bins into routes?

در مطالعات قبلی تیم، یک Horizon حدود:

10 days

نیز بررسی شده و IRP نسبت به VRPP نتایج بهتری نشان داده است.

18. Task 2 سه نوع IRP بررسی می‌کند

1. Deterministic IRP

فرض:

Demand از ابتدا معلوم است.

2. Stochastic IRP — SIRP

Demand دارای عدم قطعیت است.

از روش‌هایی مانند:

Stochastic Optimization

یا:

Robust Optimization

استفاده می‌شود.

3. Dynamic IRP — DIRP

اطلاعات در طول زمان آشکار و Update می‌شوند.

این دقیقاً با Static Sensorها مرتبط است؛ زیرا Sensor هر روز اطلاعات جدید ایجاد می‌کند.

19. هدف Optimization فقط Cost نیست

یکی از نکات بسیار مهم Proposal این است که:

Service Level

هم باید وارد مدل شود.

Service Level می‌تواند با مواردی مانند:

Number of overflowing bins

یا:

Maximum time without visiting a bin

اندازه‌گیری شود.

20. دو روش Objective Function

پروژه دو رویکرد پیشنهاد می‌کند.

Multi-objective:

Maximize Profit

و همزمان:

Minimize Overflow

یا:

Single Objective

Overflow را به یک Cost تبدیل کرده و وارد تابع هدف کنیم.

یعنی مدل باید بین:

Economic Efficiency

و:

Citizen Service Level

تعادل ایجاد کند.

21. مدل ریاضی

مدل‌ها به شکل:

Mixed-Integer Linear Programming — MILP

توسعه داده می‌شوند.

Implementation:

GAMS

Solver:

CPLEX Optimizer

22. مشکل MILP

MILP برای Benchmark و پیدا کردن Optimal Solution بسیار مهم است.

ولی برای شبکه واقعی با هزاران Bin:

Computational Time

می‌تواند بسیار زیاد شود.

در حالی که در Smart Waste Collection:

Every day a new route is needed.

پس Solution باید سریع باشد.

اینجاست که Task 3 وارد می‌شود.

23. Task 3 — Decision Support Tool

هدف Task 3 دو چیز است:

Fast Solution Algorithm

User-friendly Decision Support Tool

برای حل سریع مسئله، پروژه از:

Heuristics / Metaheuristics

استفاده می‌کند.

طبق برنامه، Task 3 از ماه 7 تا ماه 27 پروژه اجرا می‌شود.

24. GUI

پروژه صرفاً Algorithm نمی‌سازد.

با مدیران شرکت‌های Waste Collection مصاحبه و جلسه برگزار می‌شود تا مشخص شود:

چه اطلاعاتی نیاز دارند؟

چه زمانی نیاز دارند؟

با چه Format؟

سپس:

Graphical User Interface — GUI

ساخته می‌شود.

در نتیجه ابزار تقریباً این ساختار را دارد:

Input Data

↓

Prediction

↓

Optimization

↓

Daily Collection Plan

↓

GUI for Decision Maker

25. Task 4 — Sensor Placement

این بخش از نظر Strategic Planning بسیار مهم است.

سؤال:

کدام Bin باید Static Sensor داشته باشد؟

Full Sensorization بسیار گران است.

بنابراین همه Binها ارزش یکسانی ندارند.

مثلاً Proposal می‌گوید Sensor ممکن است برای:

Remote Bin + High Fill-Level Variability

ارزش بیشتری داشته باشد.

در حالی که:

Nearby Bin + Stable Fill Rate

ممکن است Sensor لازم نداشته باشد.

26. در نهایت شبکه Hybrid می‌شود

این یکی از مهم‌ترین مفاهیم کل پروژه است.

هدف الزاماً این نیست:

100% Static Sensors

بلکه:

Hybrid Monitoring Network

بعضی Binها:

Static Sensor

بعضی:

Mobile Sensor

بعضی:

Driver Observation

خواهند داشت.

این کار می‌تواند Cost/Benefit بهتری ایجاد کند.

27. Task 5 — Cost-Benefit Analysis

بعد باید مشخص شود:

آیا تمام این Smart Technology واقعاً ارزش اقتصادی دارد؟

برای این منظور از داده‌های واقعی:

ERSUC

و:

Valorsul

استفاده می‌شود.

Task 5 از ماه:

22 → 30

برنامه‌ریزی شده است.

28. وضعیت موجود Baseline است

Baseline:

Blind Collection + Pre-defined Collection Frequencies

است.

بعد سیستم‌های هوشمند با آن مقایسه می‌شوند.

در این مقایسه باید مشخص شود:

کاهش کیلومتر چقدر است؟

کاهش تعداد Visitها چقدر است؟

Overflow چقدر کم می‌شود؟

هزینه Sensor چقدر است؟

Operational Cost چقدر کاهش می‌یابد؟

و در نهایت:

Does the benefit justify the investment?

29. Task 6 — Prototype Validation

مرحله آخر:

Real-world Testbed

است.

محل:

ERSUC

Static Sensors روی تعدادی Bin منتخب بر اساس نتایج Task 4 نصب می‌شوند.

سایر Binها با:

Mobile Sensor

یا:

Visual Observation

پایش می‌شوند.

بعد ابزار هر روز:

Daily Collection Routes

را تولید می‌کند.

30. نقش ERSUC و Valorsul

این دو شرکت دو وضعیت متفاوت دارند.

ERSUC

در Proposal دارای بلوغ پایین‌تر Smart Collection معرفی شده:

Manual Planning

Static Routes

Valorsul

یک مرحله پیشرفته‌تر:

Sensors already installed

اما:

Routes still static

این تفاوت برای مقایسه بسیار مفید است.

31. ساختار تیم

پروژه 7 Entity اصلی را گرد هم آورده:

CEGIST

INESC-ID

CITTA / University of Coimbra

University of Bologna expert

EVOX

ERSUC

Valorsul

و تیم اصلی شامل 8 پژوهشگر معرفی شده است.

32. تقسیم تخصص

CEGIST

Operations Management + Mathematical Modelling + Waste Routing

INESC-ID

Data Science + Machine Learning

CITTA / Coimbra

Transportation Systems + Solution Methods

EVOX

Monitoring Technology + Sensors

ERSUC / Valorsul

Real-world Data + Operations + Validation

و Daniele Vigo نیز به‌عنوان متخصص بین‌المللی Routing در نقش Consultant ذکر شده است.

33. نقش University of Coimbra

در تیم اصلی:

António Pais Antunes

از University of Coimbra حضور دارد و در Proposal به‌عنوان Full Professor در:

Spatial Planning and Transport Systems

معرفی شده است.

بخش قابل‌توجهی از تحقیقات او نیز شامل:

Waste Management

Facility Location

و:

Recyclables Collection Routing

بوده است.

34. شکاف‌های علمی مهم پروژه

این بخش برای فهم ارزش PhD/Research بسیار مهم است.

Proposal چند Gap مشخص معرفی می‌کند:

Gap 1: تحقیقات معمولاً یا No Sensor دارند یا Full Sensorization؛ Hybrid Monitoring کمتر بررسی شده است.

Gap 2: Optimal Sensor Placement کم مطالعه شده است.

Gap 3: Mobile Sensors و Driver Observations در این چارچوب تقریباً بررسی نشده‌اند.

Gap 4: Prediction در سطح Individual Bin / Day-to-Day هنوز نیاز به توسعه دارد.

Gap 5: Dynamic/Stochastic IRP در Waste Collection بسیار محدود است.

Gap 6: ترکیب Prediction با DIRP کمتر بررسی شده است.

Gap 7: Updating مدل با Real-Time Information نیز شکاف پژوهشی است.

35. پنج سؤال تحقیقاتی بسیار مهم

اگر قرار باشد فقط یک قسمت فایل را برای جلسه حفظ کنید، این پنج سؤال بسیار مهم‌اند:

Data

بهترین منبع اطلاعات چیست؟

Driver؟

Mobile Sensor؟

Static Sensor؟

Dynamic Routing

بهترین مدل برای Dynamic Routes چیست؟

Planning Horizon چقدر باشد؟

Uncertainty چگونه مدیریت شود؟

Sensor Placement

کدام Binها واقعاً ارزش Sensorization دارند؟

Tool

چگونه در زمان کوتاه Solution خوب تولید و به Decision Maker ارائه شود؟

Benefits

سیستم هوشمند نسبت به وضعیت موجود چه مزایایی دارد؟

36. شش Task را خیلی ساده حفظ کنید

| Task | سؤال اصلی | خروجی |
|---|---|---|
| T1 | Fill Level را چگونه بفهمیم؟ | Data + Prediction |
| T2 | چه زمانی/کدام Bin جمع شود؟ | Dynamic/Stochastic IRP |
| T3 | چگونه سریع حل کنیم؟ | Algorithm + GUI |
| T4 | Sensor کجا نصب شود؟ | Sensor Placement |
| T5 | آیا اقتصادی است؟ | Cost-Benefit |
| T6 | در واقعیت کار می‌کند؟ | Real Pilot |

این ترتیب تقریباً کل منطق پروژه را نشان می‌دهد. Tasks و زمان‌بندی آنها نیز در برنامه تحقیق به همین زنجیره تعریف شده‌اند.

37. رابطه بین Taskها مهم‌تر از خود Taskهاست

این قسمت را باید کاملاً متوجه شوید:

T1Fill-Level Prediction می‌دهد.

↓

این Prediction وارد T2 می‌شود.

↓

T2 Mathematical Model می‌دهد.

↓

T3 آن را با الگوریتم سریع قابل استفاده می‌کند.

↓

T4 مشخص می‌کند برای تأمین اطلاعات، Sensorها کجا باشند.

↓

T5 بررسی می‌کند آیا این سیستم از نظر اقتصادی بهتر است.

↓

T6 کل سیستم را در ERSUC در شرایط واقعی آزمایش می‌کند.

بنابراین Tasks مستقل نیستند؛ یک Integrated Research Framework هستند. خود Proposal نیز تصریح می‌کند که Predictionهای T1 برای نگاه رو به جلو در Dynamic Routing لازم‌اند و Taskهای بعدی بر نتایج قبلی بنا می‌شوند.

38. پنج هدف رسمی پروژه

پروژه در نهایت پنج Research Goal دارد:

1. بررسی روش‌های مختلف جمع‌آوری و پردازش Fill-Level Data.

2. توسعه Planning Tool برای Smart Collection Routes.

3. توسعه مدل برای انتخاب Binهایی که باید Static Sensor داشته باشند.

4. Cost-Benefit Analysis روی Real Case Studies.

5. Real-world Testbed.

39. نتیجه مورد انتظار

بر اساس تجربه قبلی تیم، Proposal تخمین زده است:

≈ 30% reduction in operational costs

به همراه:

Higher Service Level

و:

Fewer Overflows

دقت کنید که 30٪ نتیجه اثبات‌شده پروژه نیست؛ در Proposal یک برآورد/انتظار بر اساس تجربه قبلی تیم است.

40. اگر بخواهیم کل پروژه را در یک جمله علمی بیان کنیم

WSmart Route+ develops an integrated data-driven decision-support framework that combines fill-level monitoring and prediction, dynamic and stochastic inventory-routing optimization, strategic sensor placement, and real-world validation to improve the efficiency and service level of waste collection systems.

و به زبان خیلی ساده:

پروژه می‌خواهد با استفاده از داده و پیش‌بینی بفهمد هر مخزن چه زمانی نیاز به تخلیه دارد، سپس بهترین مسیر جمع‌آوری را تعیین کند، بدون اینکه مجبور باشیم روی همه مخازن سنسور گران‌قیمت نصب کنیم.

نقشه ذهنی نهایی

3 Data SourcesDriver + Mobile Sensor + Static Sensor

↓

T1 — PredictHow much waste will be in each bin?

↓

T2 — OptimizeWhich bins + which day + which route?

↓

T3 — OperationalizeFast Metaheuristics + GUI

↓

T4 — Sensorize StrategicallyWhich bins deserve static sensors?

↓

T5 — EvaluateIs Smart Collection worth the cost?

↓

T6 — ValidateDoes it actually work at ERSUC?

↓

Final objective:Lower Cost + Fewer Unnecessary Trips + Fewer Overflows + Better Service

این زنجیره، مهم‌ترین چیزی است که برای فهم کامل WSmart Route+ باید در ذهن داشته باشید.

WSmartRoute+_Application (2)(20260809-094515).pdf

PDF

Pasted markdown.md

File

خلاصه مفید را بتویس

خلاصه مفید WSmart Route+:

هدف اصلی: تبدیل جمع‌آوری سنتی پسماند با مسیرهای ثابت به یک سیستم هوشمند و پویا که با ترکیب Data Analytics و Operations Research تصمیم بگیرد کدام مخزن، چه زمانی و از چه مسیری جمع‌آوری شود.

مشکل: در روش فعلی کامیون ممکن است برای مخزن تقریباً خالی حرکت کند، درحالی‌که مخزن دیگری سرریز شود. نمونه مهم پروژه نشان می‌دهد در مناطق روستایی ERSUC حدود 52٪ مخازن هنگام تخلیه کمتر از 25٪ پر بودند.

سه منبع اطلاعات Fill Level:Driver Observation = ارزان ولی کم‌دقت‌ترStatic Sensor = دقیق و پیوسته ولی گرانMobile Sensor = راه‌حل میانی؛ سنسور همراه راننده است.

Prediction: با استفاده از داده‌ها، میزان پرشدگی آینده هر مخزن پیش‌بینی می‌شود. روش‌ها از Time Series تا LSTM Neural Networks هستند و متغیرهایی مثل روز هفته، تعطیلات و نوع منطقه نیز می‌توانند استفاده شوند.

Routing Optimization: فقط جمع‌کردن مخازن پر کافی نیست؛ باید فاصله، هزینه، Fill Level، احتمال Overflow و وضعیت روزهای آینده همزمان بررسی شوند. به همین دلیل پروژه از Dynamic/Stochastic Inventory Routing Problem (IRP) استفاده می‌کند.

Sensor Placement: چون نصب سنسور روی همه مخازن گران است، پروژه مشخص می‌کند کدام مخازن واقعاً ارزش نصب Static Sensor دارند.

Decision Support Tool: مدل‌های پیش‌بینی و Routing با Heuristics/Metaheuristics ترکیب می‌شوند تا مسیرهای مناسب سریع تولید و از طریق یک GUI به مدیران ارائه شوند.

ارزیابی واقعی: سیستم از طریق Cost–Benefit Analysis و سپس Pilot واقعی در ERSUC ارزیابی می‌شود؛ Valorsul نیز یکی از Case Studyهای اصلی است.

۶ Task پروژه در یک نگاه

T1: Data + Fill-Level Prediction→ T2: Dynamic/Stochastic Routing→ T3: Fast Algorithms + Decision Support Tool→ T4: Optimal Sensor Placement→ T5: Cost–Benefit Analysis→ T6: Real-World Pilot

مهم‌ترین نکته‌ای که باید از پروژه به خاطر بسپارید

WSmart Route+ فقط Route Optimization نیست.

هسته پروژه این زنجیره است:

Data → Prediction → تصمیم اینکه چه مخزنی و چه زمانی جمع شود → Dynamic Routing → Strategic Sensor Placement → Cost/Benefit → Real-world Validation

هدف نهایی نیز کاهش سفر و هزینه‌های غیرضروری، جلوگیری از Overflow و افزایش سطح خدمات جمع‌آوری پسماند است. پروژه رسماً از 2 ژانویه 2023 برای مدت 36 ماه تعریف شده است
