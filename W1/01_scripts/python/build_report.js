// Methodology audit report — styled DOCX with OMML equations
// Run: node build_report.js   (from its own directory)
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, PageBreak,
  Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType, ImageRun,
  Footer, Header, PageNumber, NumberFormat, TableOfContents, LevelFormat,
  Math: DMath, MathRun, MathSubScript, MathSuperScript, MathSum, MathFraction,
  SectionType, VerticalAlign,
} = require("docx");

const ROOT = "C:/Users/esmae/Desktop/phd Esmaeil/THESIS CLAUDE";
const MAPS = `${ROOT}/W1/04_outputs/maps`;
const FIGS = `${ROOT}/W1/04_outputs/figures`;

// ---------- palette & typography ----------
const INK = "1F2937";        // near-black body
const ACCENT = "1F4E79";     // deep blue headings
const ACCENT2 = "2E74B5";
const GREY = "6B7280";
const LIGHT = "D9E2F3";      // table header fill
const RULE = "9CB3D4";

const FONT = "Calibri";
const FONTH = "Calibri Light";

// ---------- helpers ----------
const t = (text, o = {}) => new TextRun({ text, font: FONT, size: 22, color: INK, ...o });
const p = (children, o = {}) =>
  new Paragraph({ children: Array.isArray(children) ? children : [t(children)], spacing: { after: 120, line: 300 }, alignment: AlignmentType.JUSTIFIED, ...o });

const h1 = (text, num) => new Paragraph({
  heading: HeadingLevel.HEADING_1, pageBreakBefore: true,
  spacing: { before: 0, after: 240 },
  children: [new TextRun({ text: num ? `${num}.  ${text}` : text, font: FONTH, size: 32, bold: true, color: ACCENT })],
});
const h2 = (text, num) => new Paragraph({
  heading: HeadingLevel.HEADING_2, spacing: { before: 280, after: 140 },
  children: [new TextRun({ text: num ? `${num}  ${text}` : text, font: FONTH, size: 26, bold: true, color: ACCENT2 })],
});
const bold = (x) => t(x, { bold: true });

function figCaption(n, text) {
  return new Paragraph({
    spacing: { before: 80, after: 240 }, alignment: AlignmentType.CENTER,
    children: [t(`Figure ${n} — `, { size: 19, color: GREY, bold: true }), t(text, { size: 19, color: GREY })],
  });
}
function tabCaption(n, text) {
  return new Paragraph({
    spacing: { before: 200, after: 80 }, keepNext: true,
    children: [t(`Table ${n} — `, { size: 19, color: GREY, bold: true }), t(text, { size: 19, color: GREY })],
  });
}
function img(file, wCm, hCm) {
  return new Paragraph({
    alignment: AlignmentType.CENTER, spacing: { before: 120, after: 0 }, keepNext: true,
    children: [new ImageRun({ type: "png", data: fs.readFileSync(file), transformation: { width: wCm * 37.8, height: hCm * 37.8 } })],
  });
}

// tables: horizontal rules only, shaded header
const NOB = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const HB = (sz = 6, c = RULE) => ({ style: BorderStyle.SINGLE, size: sz, color: c });
function mkTable(headers, rows, widths) {
  const total = widths.reduce((a, b) => a + b, 0);
  const cell = (txt, i, isHead, isLast) => new TableCell({
    width: { size: widths[i], type: WidthType.DXA },
    borders: { top: isHead ? HB(10, ACCENT) : NOB, bottom: isHead ? HB(6) : (isLast ? HB(10, ACCENT) : HB(2, "E3E9F3")), left: NOB, right: NOB },
    shading: isHead ? { type: ShadingType.CLEAR, fill: LIGHT } : undefined,
    margins: { top: 60, bottom: 60, left: 80, right: 80 },
    verticalAlign: VerticalAlign.CENTER,
    children: [new Paragraph({ spacing: { after: 0 }, children: [t(txt, { size: 19, bold: isHead })] })],
  });
  return new Table({
    width: { size: total, type: WidthType.DXA }, columnWidths: widths,
    rows: [
      new TableRow({ tableHeader: true, children: headers.map((h, i) => cell(h, i, true, false)) }),
      ...rows.map((r, ri) => new TableRow({ children: r.map((c, i) => cell(String(c), i, false, ri === rows.length - 1)) })),
    ],
  });
}

// ---------- OMML equation builders ----------
const mr = (x, o = {}) => new MathRun(x);
const sub = (base, s) => new MathSubScript({ children: [mr(base)], subScript: [mr(s)] });
const sup = (base, s) => new MathSuperScript({ children: [mr(base)], superScript: [mr(s)] });
const subsup = (base, s, S) => new MathSubScript({ children: [new MathSuperScript({ children: [mr(base)], superScript: [mr(S)] })], subScript: [mr(s)] });
const SUM = (subS, kids) => new MathSum({ children: kids, subScript: [mr(subS)] });

function eq(children, tag) {
  return new Paragraph({
    alignment: AlignmentType.CENTER, spacing: { before: 120, after: 120 },
    children: [new DMath({ children }), t(`      (${tag})`, { color: GREY, size: 19 })],
  });
}

// deterministic p-median
const EQ1 = eq([mr("min  Z = "), SUM("i∈I", []), SUM("j∈J", []), mr(" "), sub("w", "i"), mr(" "), sub("d", "ij"), mr(" "), sub("x", "ij")], "1");
const EQ2 = eq([SUM("j∈J", []), sub("x", "ij"), mr(" = 1        ∀ i ∈ I")], "2");
const EQ3 = eq([sub("x", "ij"), mr(" ≤ "), sub("y", "j"), mr("        ∀ i ∈ I,  j ∈ J")], "3");
const EQ4 = eq([SUM("j∈J", []), sub("y", "j"), mr(" = p")], "4");
const EQ5 = eq([SUM("i∈I", []), sub("w", "i"), mr(" "), sub("x", "ij"), mr(" ≤ "), sub("Q", "j"), mr(" "), sub("y", "j"), mr("        ∀ j ∈ J")], "5");
const EQ6 = eq([sub("x", "ij"), mr(" , "), sub("y", "j"), mr(" ∈ {0, 1}")], "6");
// stochastic
const EQ7 = eq([mr("min  "), SUM("s∈S", []), sub("p", "s"), mr(" "), SUM("i∈I", []), SUM("j∈J", []), subsup("w", "i", "s"), mr(" "), sub("d", "ij"), mr(" "), subsup("x", "ij", "s"), mr("        with  "), sub("y", "j"), mr("  shared across scenarios")], "7");
// regression
const EQR1 = eq([mr("log"), sub("Y", "i"), mr(" = ln( 1 + "), sub("kg", "i"), mr(" )")], "8");
const EQR2 = eq([mr("log"), sub("Y", "i"), mr(" = "), sub("β", "0"), mr(" + "), sub("β", "pop"), mr(" "), sub("Pop", "i"), mr(" + "), SUM("k", []), sub("β", "k"), mr(" "), sub("Pct", "k,i"), mr(" + "), sub("ε", "i")], "9");

// ---------- content ----------
const abbrevRows = [
  ["BGRI", "Base Geográfica de Referenciação de Informação (INE census geography)"],
  ["CBD", "Central business district (city centre)"],
  ["CTRO", "Centro de Tratamento de Resíduos do Oeste, Cadaval (Valorsul)"],
  ["CVRP", "Capacitated vehicle routing problem"],
  ["EVPI", "Expected value of perfect information"],
  ["IRP", "Inventory routing problem"],
  ["MIP", "Mixed-integer programme"],
  ["OSM", "OpenStreetMap"],
  ["SAA", "Sample average approximation"],
  ["VIF", "Variance inflation factor"],
  ["VSS", "Value of the stochastic solution"],
  ["Ecoponto", "Street recycling site (PT); typically blue, yellow and green containers"],
  ["Enchimento", "Fill level (PT), the fill column in both CSV files"],
  ["Freguesia", "Civil parish (PT administrative unit)"],
];

const md = fs.readFileSync(`${ROOT}/W1/04_outputs/reports/draft_methodology_audit.md`, "utf-8");
// split draft into named sections on markdown headings
function section(name) {
  const rx = new RegExp(`^#{1,2} ${name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\s*$`, "m");
  const m = md.match(rx);
  if (!m) throw new Error("missing section " + name);
  const start = m.index + m[0].length;
  const rest = md.slice(start);
  const next = rest.search(/^#{1,2} /m);
  return (next < 0 ? rest : rest.slice(0, next)).trim();
}

// markdown paragraph/table renderer (subset used by the draft)
function renderMd(txt) {
  const out = [];
  const blocks = txt.split(/\n\n+/);
  for (const b of blocks) {
    const lines = b.trim().split("\n");
    if (!lines[0]) continue;
    if (lines[0].startsWith("|")) {
      const rows = lines.filter(l => l.startsWith("|")).map(l => l.replace(/^\||\|$/g, "").split("|").map(c => c.trim()));
      const headers = rows[0];
      const body = rows.slice(2);
      const w = Math.floor(9600 / headers.length);
      out.push(mkTable(headers, body, headers.map(() => w)));
      out.push(new Paragraph({ spacing: { after: 160 }, children: [] }));
      continue;
    }
    if (/^### /.test(lines[0])) { out.push(h2(lines[0].replace(/^### /, ""), null)); continue; }
    if (/^## /.test(lines[0])) { out.push(h2(lines[0].replace(/^## /, ""), null)); continue; }
    // inline md: **bold**, *ital*, `code`
    const runs = [];
    const text = lines.join(" ");
    const parts = text.split(/(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g);
    for (const part of parts) {
      if (!part) continue;
      if (/^\*\*[^*]+\*\*$/.test(part)) runs.push(t(part.slice(2, -2), { bold: true }));
      else if (/^\*[^*]+\*$/.test(part)) runs.push(t(part.slice(1, -1), { italics: true }));
      else if (/^`[^`]+`$/.test(part)) runs.push(t(part.slice(1, -1), { font: "Consolas", size: 20 }));
      else runs.push(t(part));
    }
    out.push(p(runs));
  }
  return out;
}

// replace [EQ-n: ...] placeholders in 3.3 with real OMML afterwards
function renderMethodology() {
  const txt = section("3.3 The p-median family");
  const before = txt.split("[EQ-1")[0];
  const afterEq6 = txt.split("[EQ-6: xᵢⱼ, yⱼ ∈ {0,1}]")[1] || "";
  const parts = afterEq6.split("[EQ-7");
  const middle = parts[0];
  const tail = (parts[1] || "").replace(/^[^\]]*\]/, "");
  return [
    ...renderMd(before),
    EQ1, p([t("subject to", { italics: true })], { alignment: AlignmentType.LEFT }), EQ2, EQ3, EQ4, EQ5, EQ6,
    ...renderMd(middle),
    EQ7,
    ...renderMd(tail),
  ];
}

// ---------- assemble document ----------
const headerBody = new Header({
  children: [new Paragraph({
    alignment: AlignmentType.RIGHT, spacing: { after: 60 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: RULE } },
    children: [t("Methodology audit — Sensor-based Recyclables Collection Planning", { size: 16, color: GREY, allCaps: true })],
  })],
});
const footRoman = new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 18, color: GREY })] })] });
const footArabic = new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 18, color: GREY })] })] });

const A4 = { page: { size: { width: 11906, height: 16838 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } };

const cover = [
  new Paragraph({ spacing: { before: 3200, after: 200 }, alignment: AlignmentType.CENTER, children: [t("PHD THESIS WORKING ROUND 1", { size: 20, color: GREY, allCaps: true, characterSpacing: 40 })] }),
  new Paragraph({
    alignment: AlignmentType.CENTER, spacing: { after: 160 },
    children: [new TextRun({ text: "Sensor-based Recyclables Collection Planning", font: FONTH, size: 52, bold: true, color: ACCENT })],
  }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 500 }, children: [new TextRun({ text: "Methodology audit and data-grounded work plan", font: FONTH, size: 30, color: ACCENT2 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, border: { top: { style: BorderStyle.SINGLE, size: 8, color: RULE } }, spacing: { before: 200, after: 120 }, children: [t("")] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 }, children: [t("Esmaeil Keyvanloo  ·  Rio Maior case study", { size: 22 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 }, children: [t("Prepared with the project knowledge base (Brain) as source of truth", { size: 19, color: GREY })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [t("August 2026  ·  Report R1-01", { size: 19, color: GREY })] }),
];

const frontMatter = [
  new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: true, children: [new TextRun({ text: "Contents", font: FONTH, size: 32, bold: true, color: ACCENT })] }),
  new TableOfContents("Contents", { hyperlink: true, headingStyleRange: "1-2" }),
  new Paragraph({ children: [t("Update fields in Word (Ctrl+A, F9) to populate contents and page numbers.", { size: 17, color: GREY, italics: true })], spacing: { before: 120 } }),

  new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: true, children: [new TextRun({ text: "Tables, figures and equations", font: FONTH, size: 32, bold: true, color: ACCENT })] }),
  tabCaption("i", "List of tables"),
  mkTable(["#", "Title"], [
    ["1", "Datasets available to the thesis"],
    ["2", "Defect register and modelling consequences"],
    ["3", "Valorsul Oeste fleet, 2013 snapshot"],
    ["4", "Prioritised recommendations"],
    ["5", "Abbreviations and Portuguese terms"],
    ["6", "Data to request from Valorsul"],
    ["7", "Data to request from the municipality"],
    ["8", "Data to request from the sensor supplier"],
    ["9", "Public sources to harvest directly"],
  ], [700, 8900]),
  tabCaption("ii", "List of figures"),
  mkTable(["#", "Title"], [
    ["1", "Thesis pipeline from data to optimisation"],
    ["2", "Recyclables container network, Rio Maior study area"],
    ["3", "Population distribution and container network"],
    ["4", "Sensor coverage of the mapped container network"],
  ], [700, 8900]),
  new Paragraph({ spacing: { before: 100 }, children: [t("Equations (1)–(7) define the location models; (8)–(9) the demand regression.", { size: 19, color: GREY })] }),

  new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: true, children: [new TextRun({ text: "Abbreviations", font: FONTH, size: 32, bold: true, color: ACCENT })] }),
  mkTable(["Term", "Meaning"], abbrevRows, [2000, 7600]),

  new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: true, children: [new TextRun({ text: "Executive summary", font: FONTH, size: 32, bold: true, color: ACCENT })] }),
  ...renderMd(section("Executive summary")),
];

const body = [
  h1("Problem and context", "1"),
  h2("1.1  The operational problem", null),
  ...renderMd(section("1.1 The operational problem")),
  h2("1.2  Research question and scope", null),
  ...renderMd(section("1.2 Research question and scope")),

  h1("Data foundation", "2"),
  h2("2.1  What exists", null),
  tabCaption("1", "Datasets available to the thesis"),
  ...renderMd(section("2.1 What exists")),
  h2("2.2  Known defects and their consequences", null),
  tabCaption("2", "Defect register and modelling consequences"),
  ...renderMd(section("2.2 Known defects and their consequences")),
  h2("2.3  Spatial picture", null),
  ...renderMd(section("2.3 Spatial picture")),
  img(`${MAPS}/M1_container_network.png`, 15.6, 11.0), figCaption("2", "Recyclables container network, Rio Maior study area. 464 mapped sites by waste fraction; municipal GIS, EPSG:3763."),
  img(`${MAPS}/M2_population_containers.png`, 15.6, 11.0), figCaption("3", "Population distribution (INE BGRI 2021, quantile classes) with the container network overlaid."),
  img(`${MAPS}/M3_sensor_coverage.png`, 15.6, 11.0), figCaption("4", "Sensor coverage: 193 of 464 mapped containers appear in the sensor dataset (defect D6)."),

  h1("The proposed methodology, explained", "3"),
  img(`${FIGS}/F1_thesis_pipeline.png`, 16.5, 3.3), figCaption("1", "Thesis pipeline from data to optimisation. Blue: core scope. Yellow: conditional routing extension."),
  h2("3.1  Demand estimation by regression", null),
  ...renderMd(section("3.1 Demand estimation by regression")),
  EQR1, EQR2,
  p([t("Equation (8) defines the log response used in the current fit; (9) its linear specification on buffered population and land-use shares. Section 4.1 examines what happened when this was estimated.")]),
  h2("3.2  Monte Carlo scenario generation", null),
  ...renderMd(section("3.2 Monte Carlo scenario generation")),
  h2("3.3  The p-median family", null),
  ...renderMethodology(),
  h2("3.4  Why this chain is reasonable", null),
  ...renderMd(section("3.4 Why this chain is reasonable")),

  h1("Audit findings", "4"),
  h2("4.1  The regression, as currently fitted, has failed — and the failure is informative", null),
  ...renderMd(section("4.1 The regression, as currently fitted, has failed — and the failure is informative")),
  h2("4.2  The demand indicator deserves to be the thesis's centrepiece, not a preprocessing step", null),
  ...renderMd(section("4.2 The demand indicator deserves to be the thesis's centrepiece, not a preprocessing step")),
  h2("4.3  The optimisation: sound design, unusable implementation", null),
  ...renderMd(section("4.3 The optimisation is sound in design and unusable in implementation — rebuild the instance, keep the formulation")),
  h2("4.4  The stochastic model is the right contribution — if its inputs are honest", null),
  ...renderMd(section("4.4 The stochastic model is the right contribution — if its inputs are honest")),
  h2("4.5  Residual data risks", null),
  ...renderMd(section("4.5 Residual data risks")),
  h2("4.6  Verdict", null),
  ...renderMd(section("4.6 Verdict")),

  h1("Conclusion", "5"),
  ...renderMd(section("5. Conclusion").length ? section("5. Conclusion") : ""),

  h1("Recommendations", "6"),
  tabCaption("4", "Prioritised recommendations"),
  ...renderMd(section("6. Recommendations")),

  h1("References", "7"),
  ...section("References").split("\n").filter(l => l.startsWith("- ")).map(l =>
    new Paragraph({ spacing: { after: 100 }, indent: { left: 400, hanging: 400 }, children: [t(l.slice(2))] })),

  h1("Appendix A — Operational parameters from public sources", "8"),
  tabCaption("3", "Valorsul Oeste fleet, 2013 snapshot (Lopes, 2014, Table 3)"),
  mkTable(["Vehicles", "Role", "Body", "Volume", "Payload"], [
    ["3 × MAN 18.284 LK", "Collection (glass)", "No compactor", "20 m³", "15,000 kg"],
    ["2 × Volvo FM9 (2005)", "Collection", "Compactor, Ampliroll", "20 m³", "13,945 kg"],
    ["5 × MAN TGM 18.280", "Collection", "Compactor", "20 m³", "5,580 kg"],
    ["2 × Volvo FM9 (2009)", "Collection", "Compactor, rear-load", "15 m³", "4,465 kg"],
    ["2 × light trucks", "Ecoponto maintenance", "Open box", "—", "≈2,500–2,800 kg"],
  ], [2400, 2200, 2200, 1300, 1500]),
  p([t("Depot and destination: CTRO, Estrada Nacional 361-1, km 14, Vilar, Cadaval (39.188989, −9.148423). Circuits: 82 predefined (26 paper, 26 plastic/metal, 30 glass); Monday–Friday, two shifts (05:00–12:30, 15:00–22:30); mean periodicity 9.3 / 8.3 / 20.5 days for paper / packaging / glass. Driver fill scale: vazio, menos de meio, meio, mais de meio, cheio — the 0/25/50/75/100 encoding in the collection CSV. The 2026 Valorsul site reports 21 collection vehicles and ≈24,000 containers across the network.")]),

  h1("Appendix B — Data acquisition guide: who to ask, what to request", "9"),
  p([t("Requests are grouped by authority, ordered by expected yield. Priority "), bold("A"), t(" items unblock thesis components now; "), bold("B"), t(" items enrich the cost, environmental and routing analyses; "), bold("C"), t(" items are context. Requests to Valorsul and the sensor supplier are best routed through the supervisor under the WSmartRoute+ project relationship; municipal requests can cite Portugal's access-to-documents law (Lei n.º 26/2016, LADA) if a formal channel is needed.")]),

  h2("C.1  Valorsul, S.A. — operator of the Oeste selective collection (primary target)", null),
  tabCaption("6", "Data to request from Valorsul"),
  mkTable(["Pri", "Item", "Detail to specify", "Thesis use"], [
    ["A", "Untruncated sensor export", "Full 2020–2024 readings for all ≈800 sensor containers, CSV/Parquet direct from database, not Excel", "Repairs D1; doubles the demand sample"],
    ["A", "Sensor system documentation", "Sensor make/model, measurement principle, mounting geometry, error-code table, calibration procedure", "Resolves D3 (82–84 ceiling) and D4 (negative codes)"],
    ["A", "Circuit definitions for Rio Maior", "Current circuit list with container sequence, periodicity, material type; the 2023 versions if archived", "Routing baseline; reconstructs Summer-2023 routes"],
    ["A", "Trip logs linked to weighbridge", "Per idrecolha: date, route code, vehicle, driver-recorded fills, net weight at CTRO báscula", "Mass-balance calibration of the demand variable"],
    ["A", "Container asset register", "All Rio Maior containers with ID, matrícula, type, volume, install/removal dates, sensor yes/no", "Reconciles the 344/464/816 ID mismatch (D6)"],
    ["B", "Current fleet specification", "Vehicle list with body type, volume, payload, year; assignment to circuits", "CVRP capacities; updates the 2013 snapshot"],
    ["B", "Fuel consumption records", "L/100 km per vehicle or per circuit, ideally monthly", "Cost model; carbon footprint of current vs optimised routes"],
    ["B", "Vehicle maintenance records", "Frequency, downtime, cost per vehicle-year", "Operating-cost model; fleet availability constraint"],
    ["B", "Crew and shift structure", "Teams per shift, working-time rules, overtime policy", "Route duration constraints"],
    ["B", "Collection costs", "€/tonne or annual cost breakdown for selective collection (fuel, labour, maintenance, tolls)", "Cost–benefit chapter"],
    ["C", "Contamination rates by fraction", "Rejected material share at CTRO sorting per circuit or municipality", "Quality dimension of container placement"],
    ["C", "Historical overflow complaints", "Date, location, fraction", "Validation of the stochastic model's overflow predictions"],
  ], [500, 2000, 3600, 3500]),

  h2("C.2  Câmara Municipal de Rio Maior — Divisão de Ambiente / Serviços Urbanos", null),
  tabCaption("7", "Data to request from the municipality"),
  mkTable(["Pri", "Item", "Detail to specify", "Thesis use"], [
    ["A", "Municipal container registry", "All ecoponto sites with coordinates, installation year, ownership (municipal vs Valorsul)", "Candidate-site set; cross-check of the 464 GIS bins"],
    ["A", "PAPERSU / municipal waste plan", "Current plan with targets, planned container investments, service standards", "Constraints and policy targets for the optimisation"],
    ["B", "Urban waste collection schedules", "Undifferentiated + selective calendars by parish/zone, if the municipality holds them", "Context for citizen deposit behaviour; scheduling layer"],
    ["B", "Road restrictions for heavy vehicles", "Weight/height limits, one-ways, pedestrian zones in the urban core", "Network model for routing"],
    ["B", "Urban development plans (PDM extracts)", "Approved allotments, expected population growth areas", "Future-demand scenarios for the stochastic model"],
    ["C", "Street cleaning and complaint records", "Overflow or littering complaints near ecopontos", "Placement quality evidence"],
    ["C", "Tourism and events calendar", "Fairs, festivals, sports events with expected attendance", "Temporal covariates for demand regression"],
  ], [500, 2000, 3600, 3500]),

  h2("C.3  Sensor supplier (via Valorsul; identity in procurement records)", null),
  tabCaption("8", "Data to request from the sensor supplier"),
  mkTable(["Pri", "Item", "Detail to specify", "Thesis use"], [
    ["A", "Technical datasheet", "Measurement range, resolution, blind zone (dead band) near the sensor face", "The 82–84 ceiling is very likely the ultrasonic blind zone; this is the document that proves it"],
    ["A", "Error-code dictionary", "Meaning of −1…−9 and −89…−116 style readings", "Turns D4 from deletion into documented filtering"],
    ["B", "Calibration and drift policy", "Factory calibration, temperature compensation, expected drift", "Measurement-error term for the demand model"],
    ["C", "Battery and transmission logs", "Reporting frequency vs battery state", "Explains gaps in the reading series"],
  ], [500, 2000, 3600, 3500]),

  h2("C.4  National authorities and public repositories (no request letter needed)", null),
  tabCaption("9", "Public sources to harvest directly"),
  mkTable(["Source", "What to take", "Thesis use"], [
    ["ERSAR — annual RASARP indicators", "Quality-of-service indicators for waste systems, per operator and municipality", "Benchmarking; service-standard justification"],
    ["APA — RARU annual reports", "Municipal waste production and recycling rates, Oeste region time series", "Demand trends; PERSU 2030 targets as constraints"],
    ["INE — BGRI 2021 official download", "Authoritative census subsection polygons and population counts", "Fixes D7; demand weights"],
    ["INE — municipal statistics", "Population projections, tourism overnight stays for Rio Maior", "Long-run demand scenarios"],
    ["IPMA — climate normals and daily series", "Temperature, precipitation for Santarém/Rio Maior", "Temporal covariates in the container-day regression"],
    ["OpenStreetMap", "Road network with speeds and restrictions", "Network distances for p-median and routing"],
    ["EMEP/EEA emission factor guidebook", "Heavy-duty vehicle CO₂ and pollutant factors by Euro class", "Carbon footprint of current vs optimised operations"],
    ["Sociedade Ponto Verde — annual reports", "Packaging flows and financial compensation values (Valor Ponto Verde)", "Revenue side of the cost–benefit analysis"],
    ["Pordata", "Municipal socio-economic indicators", "Regression covariates; context chapter"],
  ], [2500, 3600, 3500]),

  p([t("Two practical notes. First, request machine-readable formats explicitly (CSV, GeoPackage, Excel as a last resort) and the associated data dictionary in the same email; a second round-trip costs weeks. Second, log every request and response in the project decision log, because data provenance will be examined at the defence.", { })]),

  h1("Appendix C — Reproducibility", "10"),
  p([t("Every figure in this report traces to the project knowledge base. Row counts and container populations: SQL against Brain/03_db/duckdb/rio.duckdb (tables raw_sensors, raw_collections, geo_*). Defect evidence: Brain/02_notes/data_quality/csv-first-pass-profile.md and Brain/06_manifest/logs. Regression figures: Brain/01_sources/thesis/regression-output.md (pages 19–22). Maps: QGIS 3.44 project over Brain/03_db/geo/rio_maior.gpkg, exported through the thesis layout template. Interview rulings: Brain/00_canon/data/data-dictionary.md; scope decisions: Brain/00_canon/decisions/ADR-001.")]),
];

const doc = new Document({
  creator: "Claude (thesis assistant)",
  title: "Methodology audit — Sensor-based Recyclables Collection Planning",
  styles: { default: { document: { run: { font: FONT, size: 22, color: INK } } } },
  features: { updateFields: true },
  sections: [
    { properties: { ...A4, titlePage: true }, children: cover },
    { properties: { ...A4, type: SectionType.NEXT_PAGE, page: { ...A4.page, pageNumbers: { start: 1, formatType: NumberFormat.LOWER_ROMAN } } }, headers: { default: headerBody }, footers: { default: footRoman }, children: frontMatter },
    { properties: { ...A4, type: SectionType.NEXT_PAGE, page: { ...A4.page, pageNumbers: { start: 1, formatType: NumberFormat.DECIMAL } } }, headers: { default: headerBody }, footers: { default: footArabic }, children: body },
  ],
});

Packer.toBuffer(doc).then(buf => {
  const out = `${ROOT}/W1/04_outputs/reports/R1-01_Methodology_Audit.docx`;
  fs.writeFileSync(out, buf);
  console.log("written:", out, buf.length, "bytes");
});
