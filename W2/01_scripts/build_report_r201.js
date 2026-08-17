// R2-01 Driver vs Sensor reconciliation report — Revision B (addresses the Codex review of 14 Aug 2026)
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, PageBreak,
  Table, TableRow, TableCell, WidthType, ShadingType, TableOfContents,
  LevelFormat, ImageRun, Footer, PageNumber,
} = require(path.resolve(__dirname, '../../W1/01_scripts/python/node_modules/docx'));

const OUT = path.resolve(__dirname, '../03_outputs/reports/R2-01_Driver_Sensor_Reconciliation.docx');
const MAPS = path.resolve(__dirname, '../03_outputs/maps');
const FIGS = path.resolve(__dirname, '../03_outputs/figures');

const FONT = 'Georgia';
const t = (text, opts = {}) => new TextRun({ text, font: FONT, size: 22, ...opts });
const p = (text) => new Paragraph({ children: [t(text)], spacing: { after: 120 } });
const h1 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 320, after: 160 }, children: [t(text, { bold: true, size: 30 })] });
const h2 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 240, after: 120 }, children: [t(text, { bold: true, size: 25 })] });
const caption = (text) => new Paragraph({ spacing: { before: 60, after: 200 }, children: [t(text, { italics: true, size: 19 })] });
const W = 9000;
function tbl(headers, rows, widths) {
  const mk = (txt, bold, shade) => new TableCell({
    width: { size: 1, type: WidthType.AUTO },
    shading: shade ? { type: ShadingType.CLEAR, fill: 'E8E4DC' } : undefined,
    margins: { top: 60, bottom: 60, left: 90, right: 90 },
    children: [new Paragraph({ children: [t(String(txt), { bold: !!bold, size: 19 })] })],
  });
  return new Table({
    width: { size: W, type: WidthType.DXA },
    columnWidths: widths || headers.map(() => Math.floor(W / headers.length)),
    rows: [
      new TableRow({ tableHeader: true, children: headers.map(x => mk(x, true, true)) }),
      ...rows.map(r => new TableRow({ children: r.map(c => mk(c)) })),
    ],
  });
}
const bullets = { reference: 'b', levels: [{ level: 0, format: LevelFormat.BULLET, text: '–', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 360, hanging: 200 } } } }] };
const b = (text) => new Paragraph({ numbering: { reference: 'b', level: 0 }, spacing: { after: 80 }, children: [t(text)] });
const num = { reference: 'n', levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 360, hanging: 260 } } } }] };
const n1 = (text) => {
  const idx = text.indexOf('—');
  const kids = idx > 0 ? [t(text.slice(0, idx + 1), { bold: true }), t(text.slice(idx + 1))] : [t(text)];
  return new Paragraph({ numbering: { reference: 'n', level: 0 }, spacing: { after: 100 }, children: kids });
};
const img = (file, w, h) => new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { before: 120, after: 60 },
  children: [new ImageRun({ type: 'png', data: fs.readFileSync(file), transformation: { width: w, height: h } })],
});

const cover = [
  new Paragraph({ spacing: { before: 2800 } }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [t('Sensor-based Recyclables Collection Planning', { bold: true, size: 40 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 200 }, children: [t('Report R2-01 — Revision B', { size: 26 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 400 }, children: [t('Driver and Sensor Records: Description, Reconciliation, and Fitness for Analysis', { bold: true, size: 32 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 200 }, children: [t('Revised after external review; all reviewer checks recomputed from the raw data', { italics: true, size: 24 })] }),
  new Paragraph({ spacing: { before: 2400 } }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [t('Esmaeil Keyvanloo', { size: 24 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [t('PhD working repository · Working round W2', { size: 22 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [t('14 August 2026', { size: 22 })] }),
  new Paragraph({ children: [new PageBreak()] }),
];

const toc = [
  h1('Table of contents'),
  new TableOfContents('Table of contents', { hyperlink: true, headingStyleRange: '1-2' }),
  new Paragraph({ children: [new PageBreak()] }),
];

const lists = [
  h1('List of tables'),
  ...['Table 1 — The shared 19-column schema and what each parameter carries (corrected)',
      'Table 2 — Headline comparison and effective analysis windows',
      'Table 3 — Container population reconciliation',
      'Table 4 — Fill-value semantics by source (revised zero interpretation)',
      'Table 5 — Waste-fraction composition and site-level instrumentation',
      'Table 6 — Collection-run evidence in the driver file',
      'Table 7 — Matching-window sensitivity for the event-level comparison',
      'Table 8 — Event-level agreement between matched driver and sensor readings',
      'Table 9 — Negative sensor readings: structure and filtering rule',
      'Table 10 — Fitness of each variable for the next analyses',
     ].map(x => p(x)),
  h1('List of figures'),
  ...['Figure 1 — Monthly record volume by source',
      'Figure 2 — Sensor fleet inside the driver census (map W2-M1)',
      'Figure 3 — Fill-value distributions, driver vs sensor',
      'Figure 4 — Anatomy of the 144,804 driver zeros',
      'Figure 5 — Containers by waste fraction (map W2-M2)',
      'Figure 6 — Active windows and the three cadence denominators',
      'Figure 7 — Collection start times: the two shifts',
      'Figure 8 — Negative sensor readings by year',
      'Figure 9 — Matching-window sensitivity',
      'Figure 10 — Event-level agreement categories and by driver value',
      'Figure 11 — Negative readings by month and episode length',
      'Figure 12 — Mean sensor fill per container (map W2-M3)',
      'Figure 13 — Share of driver estimates equal to zero (map W2-M4)',
     ].map(x => p(x)),
  new Paragraph({ children: [new PageBreak()] }),
];

const abbrev = [
  h1('Contractions and abbreviations'),
  tbl(['Term', 'Meaning'], [
    ['BGRI', 'Census geography of INE (2021 subsections)'],
    ['cid', 'Container identifier (idcontentor)'],
    ['CE / CP', 'Route-code prefixes: circuito de embalagens / de papel'],
    ['D1…D7', 'Defect register of report R1-01'],
    ['Driver file', 'Enchimentos_com_Recolhas[RioMaior].csv — 264,817 rows'],
    ['Sensor file', 'Enchimentos_de_Sensores[RioMaior].csv — 1,048,575 rows'],
    ['Ecoponto', 'Portuguese three-fraction recycling point (amarelo, azul, verde)'],
    ['Active window', 'Per-container span from first to last sensor reading'],
    ['TM06', 'ETRS89 / Portugal TM06, EPSG:3763'],
  ], [1900, 7100]),
  new Paragraph({ children: [new PageBreak()] }),
];

const exec = [
  h1('Executive summary'),
  h2('What matches'),
  p('The 344 sensor-file containers are a strict subset of the 816 in the driver file. On every shared identifier the median coordinates agree exactly (0.0 m), and container type, volume, and waste fraction never disagree. This exact agreement is consistent with both exports drawing on a single container registry; it supports that inference without proving it, since two synchronised copies would look the same. All 816 containers fall inside the CAOP 2025 municipal boundary.'),
  h2('What differs'),
  p('The instruments measure differently. Drivers record a four-point visual scale; sensors record a near-continuous value on a schedule. The headline "55% of driver entries are zero" hides a mechanism: every one of the 60,916 collection-event rows carries fill = 0, and 60,273 of the zeros sit within 15 minutes of a nonzero reading of the same container. Those are post-emptying confirmations written by the workflow, not containers found empty. Standalone zeros — 81,703 rows — are the ones that can mean an empty container.'),
  h2('What remains uncertain'),
  p('The sensor unit: a uniform 82–84 ceiling across all container geometries rules out verified percent (defect D3). The instrumented-fleet size: the sensor export stops at the Excel row limit (D1), so 344 is a floor. The glass gap (2 instrumented of 258) now has a tested candidate explanation in site-level policy rather than truncation alone. And the old regression sample of 452 bins cannot be reproduced from any file now held.'),
  h2('What can safely be analysed next'),
  p('Fill-rate estimation on the instrumented set, with the denominator taken as calendar days inside each container’s own active window; glass demand from driver quartiles; siting on all 816 locations; and the two-shift structure recovered from 60,916 collection timestamps as routing constraints. Weight allocation to containers must wait until the run-level recording gaps described in section 3 are resolved.'),
];

const s1 = [
  h1('1. What each file is'),
  p('Both files export the same 19-column, semicolon-delimited schema; they differ in which instrument produced the fill value and which containers appear. Table 1 is corrected on two rows the review flagged: the collection timestamps are far more widely populated than the route codes, and the run totals need caveats before any allocation.'),
  tbl(['Column', 'Carries', 'Behaviour observed (verified this revision)'], [
    ['idcontentor / Matricula', 'Container id and plate', 'One-to-one in both files; join key. 816 and 344 distinct values.'],
    ['Tipo / Volume', 'Model and nominal litres (2500–5000)', 'Identical across files for shared cids.'],
    ['description', 'Waste fraction', 'Three values; drives ecoponto colour and route prefix.'],
    ['Distrito…Localidade', 'Administrative placement', 'Constant Distrito/Concelho; 10 freguesias; Localidade sparse.'],
    ['Latitude / Longitude', 'Container position, WGS 84', 'Stable per cid; identical across files; all inside the municipality.'],
    ['Data da leitura', 'Reading timestamp', 'Jan 2020 – Apr 2024 both files; cadence discussed in section 3.1.'],
    ['Enchimento', 'Fill value', 'Driver: {0,25,50,75,100} plus −1. Sensor: 0–84 plus negatives. See Table 4.'],
    ['idrecolha', 'Collection-event id', 'Driver file: 9,984 events on 60,916 rows — every such row carries fill = 0 (post-emptying record). Sensor file: duplicates Enchimento in 90.8% of rows (D2); unusable there.'],
    ['Rota', 'Route code', 'Driver file: 92 codes on 22,674 rows (8.6%). Prefix encodes fraction. Section 3.4.'],
    ['Data de início / fim', 'Collection start/end', 'CORRECTED: populated on all 60,916 event rows — 38,242 of them carry no route code. Start times reveal a two-shift operation (Figure 7).'],
    ['Km totais / Peso total', 'Run totals', 'On the 60,916 event rows (23%). Km is constant within a run; weight is NOT always constant within a run, and the median recorded run covers a single container — see section 3.3 before allocating anything.'],
  ], [1750, 2650, 4600]),
  caption('Table 1 — The shared 19-column schema and what each parameter carries (corrected).'),
  tbl(['', 'Driver file', 'Sensor file'], [
    ['Rows', '264,817', '1,048,575 (Excel limit — truncated, D1)'],
    ['Distinct containers', '816', '344'],
    ['Nominal period', '2020-01-02 to 2024-04-29', '2020-01-01 to 2024-04-30'],
    ['Effective window for analysis', 'Full span; 2024 is Jan–Apr only and must not be compared as a year', 'Negatives fall from 36.6% (2020) to 6–9% (2021–23) and 2.6% (2024): early 2020 needs screening; per-container active windows apply (section 3.1)'],
    ['Fill scale', 'Quartiles {0,25,50,75,100}', 'Near-continuous 0–84'],
    ['Invalid fills', '249 rows of −1 (0.1%)', '96,832 negative rows (9.2%)'],
  ], [2200, 3400, 3400]),
  caption('Table 2 — Headline comparison and effective analysis windows.'),
  img(path.join(FIGS, 'F1_monthly_volume.png'), 620, 244),
  caption('Figure 1 — Monthly record volume by source. The sensor series’ growth is confounded with truncation (D1) and is not evidence of fleet expansion; the shaded band marks partial 2024.'),
];

const s2 = [
  h1('2. Reconciliation'),
  h2('2.1 One registry behind both exports — as inference'),
  p('Joining on idcontentor left nothing ambiguous. Every sensor container exists in the driver census; none exists only on the sensor side. For all 344 shared identifiers the median coordinates, type, volume, and fraction agree without a single exception. The evidence is consistent with both exports drawing on a common container registry. That is an inference from agreement, not a documented fact about the operator’s systems; the export-provenance question goes into the data request.'),
  tbl(['Population', 'Containers', 'Share'], [
    ['Driver census (total)', '816', '100%'],
    ['Instrumented (both files)', '344', '42.2%'],
    ['Driver-only', '472', '57.8%'],
    ['Sensor-only', '0', '0%'],
    ['Coordinate offset, shared cids', '0.0 m (all 344)', '—'],
    ['Type / volume / fraction mismatches', '0', '—'],
  ], [4200, 2600, 2200]),
  caption('Table 3 — Container population reconciliation.'),
  p('The 464-point geodatabase layer sits between the two populations: all 464 appear in the driver census and 193 carry sensors. Its boundary layer differs from CAOP 2025 by several kilometres and is retired; the container points remain useful as a dated snapshot.'),
  img(path.join(MAPS, 'W2-M1 Source reconciliation.png'), 620, 438),
  caption('Figure 2 — Sensor fleet inside the driver census (map W2-M1; boundary: CAOP 2025, DGT).'),
  h2('2.2 Defect D6, restated'),
  p('R1-01 logged D6 as "container populations differ (816 vs 344), confounded with D1". This report closes the dangerous half of D6: the difference is not a registry mismatch, duplicate identifiers, or positional disagreement. What remains of D6 is reclassified as an expected coverage difference — instrumentation covers part of the census — with one residual unknown inherited from D1: whether 344 is the true instrumented count. The defect register entry should read: geometry and identity reconciled; coverage difference explained by site-level policy (section 2.4); true fleet size pending the untruncated re-export.'),
  h2('2.3 Where they disagree: measurement, not geography'),
  tbl(['Property', 'Driver', 'Sensor', 'Consequence'], [
    ['Scale', '5 values', '85 values (0–84)', 'Ordinal vs near-continuous.'],
    ['Ceiling', '100 reachable', '82–84, never 100', 'Unit unverified (D3); treat as monotone index; model the ceiling as censoring.'],
    ['Zeros', '144,804 rows, of which 60,273 are post-emptying confirmations paired to a nonzero reading ≤15 min earlier; 81,703 standalone', '12.2% of rows', 'Fill-at-collection statistics must use the pre-emptying member of each pair; standalone zeros are the only candidates for "found empty".'],
    ['Negatives', '0.1%', '9.2% in two clusters (−1…−9; −89…−116), concentrated in 2020', 'Two failure modes; filter by mode and screen early 2020.'],
    ['Cadence', 'At collection events', 'Three denominators, section 3.1', 'Sensors support rate estimation; drivers event snapshots.'],
  ], [1250, 2900, 2000, 2850]),
  caption('Table 4 — Fill-value semantics by source (revised zero interpretation).'),
  img(path.join(FIGS, 'F2_fill_distributions.png'), 620, 244),
  caption('Figure 3 — Fill-value distributions. The driver scale is discrete by design; the sensor scale stops at 82–84.'),
  img(path.join(FIGS, 'F3_zero_anatomy.png'), 620, 205),
  caption('Figure 4 — Anatomy of the driver zeros. The red bar is workflow output, not observed emptiness.'),
  h2('2.4 The glass gap: policy first, truncation second'),
  tbl(['Fraction', 'Driver containers', 'Sensor containers'], [
    ['Embalagens de papel e cartão (azul)', '280', '173'],
    ['Mistura de embalagens (amarelo)', '278', '169'],
    ['Embalagens de Vidro (verde)', '258', '2'],
  ], [4200, 2400, 2400]),
  caption('Table 5 — Waste-fraction composition and site-level instrumentation.'),
  p('The review pointed to the field observation of October 2025 — containers cluster in three-fraction sites and typically one unit per site carries a sensor, with priority to the faster-filling streams — and asked for a direct test. Grouping the 816 containers by shared coordinates gives 270 sites, 214 of them classic three-fraction ecopontos. Of the 253 multi-unit sites, 105 have exactly one instrumented unit, 118 have two or more, and 30 have none. Instrumentation is therefore not strictly one-per-site, but it is decisively fraction-selective: paper and packaging account for 342 of 344 sensors. The 173/169/2 split matches the priority policy far better than random truncation would. Truncation (D1) still removed whole containers — the file’s last container breaks off mid-series — so D1 governs how many instrumented containers exist, while policy explains which fractions they serve. The re-export decides the residual.'),
  img(path.join(MAPS, 'W2-M2 Waste fractions.png'), 620, 438),
  caption('Figure 5 — Containers by waste fraction, ecoponto colours (map W2-M2). At shared sites the symbols overlap; composition is read from Table 5, not by counting dots.'),
];

const s3 = [
  h1('3. Measurement mechanics established this revision'),
  h2('3.1 Cadence has three honest denominators'),
  p('The review was right that 2.55 readings per container-day is not reproducible from total rows over containers and days — that quotient is 1.93 (1,048,575 rows ÷ 344 containers ÷ 1,582 days). The three defensible statements are: 1.93 per calendar day over the full window; 2.55 per day averaged over container-days that have at least one reading; and 1.58 as the median container’s rate inside its own active window (first to last reading). The distinction matters because 64 of the 344 containers were active for less than a year, and the median coverage inside an active window is 98% of days. Per-container windows are exported to sensor_active_windows.csv and are inputs to the demand model, not an assumption of uniformity.'),
  img(path.join(FIGS, 'F4_cadence_windows.png'), 620, 244),
  caption('Figure 6 — Active windows and the three cadence denominators.'),
  h2('3.2 The demand denominator'),
  p('Daily demand per container must divide by calendar days inside that container’s active window — not by days on which a reading happens to exist, and not by the full study span. Using the full span deflates rates for late-installed containers by up to a factor of twenty-eight (the shortest window is 56 days); using reading-days inflates rates wherever coverage dips. Gaps inside a window longer than a sensor outage threshold (to be fixed at the unit interview) should be subtracted rather than filled.'),
  h2('3.3 Collection runs: what the totals can and cannot support'),
  tbl(['Evidence', 'Extent', 'Verified reading'], [
    ['Collection events (idrecolha)', '9,984 runs on 60,916 rows', 'Start/end timestamps on every event row; median run duration 7.4 h (p10 6.3, p90 9.1).'],
    ['Shift structure', '60,916 timestamped rows', 'Bimodal starts: 04–06 h and 14–15 h — two shifts, Monday-to-Saturday (Figure 7). Direct evidence for routing shift constraints.'],
    ['Kilometres', '23% of rows', 'Constant within every run: genuine run totals (p50 126 km).'],
    ['Weights', '23% of rows', 'NOT always constant within a run, and the median run records only one container (p90 ≈ 23). Recording is partial: run totals cannot yet be allocated to containers, and where weighing occurs is undocumented — added to the data request.'],
  ], [2100, 2300, 4600]),
  caption('Table 6 — Collection-run evidence in the driver file.'),
  img(path.join(FIGS, 'F5_shift_structure.png'), 620, 218),
  caption('Figure 7 — Collection start times. The two shifts bound feasible route durations in the optimisation.'),
  h2('3.4 Route codes: purity confirmed, exceptions identified'),
  p('The review’s claim checks out at 91 of 92: every coded route carries a single waste fraction except CE46, which mixes packaging with paper on 250 rows. Four further codes are not malformed CE/CP prefixes but a different naming family — "Óbidos CE01/02/03/CESexta", 171 rows — apparently circuits shared with or named after the Óbidos system; they are flagged for the operator interview. Within-stream purity means run weights, once allocable, stay inside one bulk-density class. No glass circuit appears anywhere in the coded rows.'),
  h2('3.5 Effective windows and the 2020 problem'),
  p('Negative sensor readings are strongly time-dependent: 36.6% of 2020 rows, 6–9% through 2021–2023, 2.6% in partial 2024 (Figure 6). Early 2020 looks like a commissioning period and should be screened, or modelled separately, rather than averaged in. 2024 stops in April in both files; no annual statistic in this project may treat it as a complete year.'),
  img(path.join(FIGS, 'F6_negatives_by_year.png'), 620, 205),
  caption('Figure 8 — Negative sensor readings by year.'),
  h2('3.6 The regression sample of 452 cannot be reproduced'),
  p('R1-01’s bin-level regression reports N = 452. No selection rule on the files now held yields that number: 801 of the 816 containers have at least one weighted collection event, and the geodatabase snapshot holds 464. The likeliest origin is the 464-bin snapshot minus twelve bins lost in cleaning or spatial joins, but the intermediate file (regdata_input.csv) is not in the repository and the exclusion rules were never written down. Until that file is recovered or the sample is rebuilt from the canonical 816 with explicit rules, the regression’s population is undefined — which is itself a finding about reproducibility.'),
];

const s4ev = [
  h1('4. Event-level comparison of the two instruments'),
  h2('4.1 Matching method and tolerance'),
  p('Records are matched by container identifier and timestamp: for each of the 127,928 driver rows on instrumented containers, the nearest valid sensor reading (0–100) on either side of the driver timestamp is located, and the pair is kept when the gap is inside the tolerance window. The gap distribution justifies the choice: p10 is 30 minutes, the median 347 minutes, and beyond p75 the gaps explode into multi-day sensor outages. The primary window is ±3 hours — close to the median gap and well under the typical inter-reading interval — which matches 43,477 driver rows (34.0%). The sensitivity analysis in Table 7 is the reason the choice is safe: the acceptable-agreement share barely moves (48.9–50.9%) from ±15 minutes to ±24 hours, so no conclusion in this section depends on the window.'),
  tbl(['Window', 'Matched rows', '% of driver rows', 'Acceptable agreement (% of matched)', 'Mean |diff| (normalized)'], [
    ['±15 min', '6,097', '4.8', '50.9', '38.6'],
    ['±30 min', '11,995', '9.4', '49.5', '40.0'],
    ['±1 h', '20,862', '16.3', '50.2', '39.4'],
    ['±3 h (primary)', '43,477', '34.0', '48.9', '40.1'],
    ['±6 h', '60,584', '47.4', '48.9', '39.9'],
    ['±12 h', '83,127', '65.0', '49.1', '39.9'],
    ['±24 h', '90,310', '70.6', '48.9', '40.2'],
  ], [1500, 1700, 1700, 2400, 1700]),
  caption('Table 7 — Matching-window sensitivity for the event-level comparison.'),
  img(path.join(FIGS, 'F7_window_sensitivity.png'), 620, 234),
  caption('Figure 9 — Matching-window sensitivity. Coverage grows with the window; agreement does not change.'),
  h2('4.2 Agreement categories and the acceptance threshold'),
  p('For comparison the sensor value is normalized by its container’s own ceiling (82–84 mapped to 100) — an explicit, flagged assumption that the ceiling means full, made only for comparability and revisited at the unit interview. Thresholds follow the driver’s 25-point scale: a difference within 12.5 (half a step) is small — the two instruments would round to the same category; within 25 (one step) is moderate — adjacent categories; beyond 25 is large — the instruments disagree by more than the driver scale’s own resolution. Acceptable agreement is defined as within one step (≤25).'),
  tbl(['Measure', 'Value'], [
    ['Compared pairs (±3 h, valid driver reading, non-event rows)', '28,683'],
    ['Small difference (≤12.5)', '8,039 (28.0%)'],
    ['Moderate difference (12.5–25)', '4,912 (17.1%)'],
    ['Large difference (>25)', '15,732 (54.8%)'],
    ['Acceptable (≤25)', '12,951 (45.2%)'],
    ['Best-agreeing driver value', '25 (75.0% acceptable)'],
    ['Worst-agreeing driver value', '100 (38.4% acceptable)'],
  ], [5400, 3600]),
  caption('Table 8 — Event-level agreement between matched driver and sensor readings.'),
  p('The verdict is uncomfortable and important: fewer than half of the matched readings agree within one driver step, and the rate is stable across every matching window, so it is not a matching artifact. Agreement is worst exactly where the driver scale is most used — the extremes. This is not sufficient to treat the instruments as interchangeable, and it forbids using one to silently validate the other. It is sufficient for the design already adopted: the sensor is the primary continuous signal, the driver series is an ordinal covariate and glass fallback, and any model mixing both must carry an instrument term.'),
  img(path.join(FIGS, 'F8_agreement.png'), 620, 234),
  caption('Figure 10 — Agreement categories and acceptable share by driver value.'),
  h2('4.3 Ceiling cases: driver 100 vs sensor 82–84'),
  p('Among the 10,153 matched pairs where the driver recorded 100, the sensor sat at its raw ceiling of 82–84 in 1,758 cases (17.3%), and at 75 or more after normalization in 3,901 (38.4%). The co-occurrence is real but minority: most driver "full" calls do not find the sensor anywhere near its ceiling. These 1,758 rows are flagged CEILING_CASE in the event dataset; the sensor value is selected with the rationale documented, and the D3 unit question stays open — the ceiling behaves like a saturation limit, not like the sensor’s expression of 100%.'),
  h2('4.4 Driver −1: missing, not a state'),
  p('Of the 249 rows with driver fill −1, 146 fall on instrumented containers; 84 of those (57.5%) have a valid sensor reading within ±3 hours, and the matched sensor values spread across the whole range (quartiles 12, 23, 86 after normalization). None of the −1 rows is a collection-event row. A code that co-occurs with arbitrary true fill levels and never with events is a missing or failed manual entry, not information. Rule: treat −1 as missing; where a matched sensor reading exists, the event dataset supplies it.'),
  h2('4.5 The integrated event-level dataset'),
  p('event_level_dataset.parquet holds all 127,928 driver rows on instrumented containers with: both raw readings, both timestamps, the signed time gap, the per-container sensor ceiling, the normalized sensor value, the absolute difference, a QC flag, the selected fill value, and the selection rule as text. Selection is conservative: the sensor value is used when it is nonnegative and validated by the driver within one scale step, or in documented ceiling cases; the driver value is used when no sensor reading exists within tolerance; large disagreements select nothing and stay flagged for investigation — 15,732 rows (12.3%) are held out this way rather than auto-accepted. A selected value exists for 75,260 rows (58.8%).'),
  tbl(['QC flag', 'Rows', 'Selected value'], [
    ['NO_SENSOR_MATCH', '62,309', 'driver (where valid)'],
    ['EVENT_ZERO_POST_EMPTYING', '36,790', 'none — excluded from fill statistics'],
    ['LARGE_DISAGREEMENT', '15,732', 'none — flagged for investigation'],
    ['GOOD_AGREEMENT', '6,281', 'sensor (normalized)'],
    ['MODERATE_AGREEMENT', '4,912', 'sensor (normalized)'],
    ['CEILING_CASE', '1,758', 'sensor — documented rationale'],
    ['DRIVER_MISSING_SENSOR_AVAILABLE / _NO_MATCH', '84 / 62', 'sensor / none'],
  ], [3400, 1600, 4000]),
  caption('Table 9 — QC flags in the integrated event dataset and the selection rule applied to each.'),
  h2('4.6 Negative sensor readings: structure and filtering rule'),
  p('The 96,832 negatives split into two families of almost equal size: transient small values −1…−9 (45,788 rows, 47.3%) and discrete fault codes −89…−116 (51,044 rows, 52.7%), of which −116 alone contributes 37,052 rows. They are not a few bad sensors: 329 of 344 containers produce negatives, and the most affected tenth of containers accounts for only 28.8% of them. They are strongly time-dependent (heaviest through 2020) and type-dependent — the E BLUE BEE model runs at 23.6% negative against 3.2% for AMBI. The 96,832 rows group into 29,885 consecutive episodes; the median episode is a single reading, but 17.8% last longer than a day and the longest runs to 1,226 readings. The decisive observation is the level comparison around episodes: the mean jump between the last valid reading before and the first after is 28.5 points, three times the baseline adjacent-reading change of 9.6 — episodes coincide with real state changes, usually an emptying the sensor missed. The filtering rule follows: negatives carry no fill information and are dropped; −1…−9 rows count as isolated missing readings; −89…−116 as device fault codes; episodes longer than 24 hours are subtracted from the container’s active window; and no interpolation is permitted across an episode, because the level demonstrably moves during them.'),
  img(path.join(FIGS, 'F9_negatives_deepdive.png'), 620, 234),
  caption('Figure 11 — Negative readings by month and cluster (left) and episode-length distribution (right).'),
];

const s4 = [
  h1('5. Fitness for the next analyses'),
  tbl(['Variable', 'Fit for', 'Not fit for'], [
    ['Sensor fill series (344 units, active windows attached)', 'Fill-rate estimation with calendar-day denominators; censoring-aware modelling of the 82–84 ceiling; driver-comparison chapter', 'Absolute volume claims before the unit interview; glass; early-2020 rows without screening'],
    ['Driver quartile series (816 units, zeros decomposed)', 'Network-wide relative demand from pre-emptying readings; glass demand; validation of sensor-derived rates', 'Fill-at-collection statistics that include confirmation zeros; continuous rate estimation'],
    ['Container registry (816 locations, 270 sites)', 'p-median demand points and candidate sites; site-level (ecoponto) aggregation; distance matrices on the OSM graph', '—'],
    ['Run records (9,984 events)', 'Shift constraints; run-duration envelopes; tonnage sanity checks at fleet level', 'Per-container weight allocation until recording gaps are explained'],
    ['Rota codes (92)', 'Within-stream circuit reconstruction; validation target for operator GPS', 'Complete route recovery (8.6% coverage)'],
  ], [2400, 3700, 2900]),
  caption('Table 10 — Fitness of each variable for the next analyses.'),
  img(path.join(MAPS, 'W2-M3 Sensor mean fill.png'), 620, 438),
  caption('Figure 12 — Mean sensor fill per container (map W2-M3).'),
  img(path.join(MAPS, 'W2-M4 Driver zero share.png'), 620, 438),
  caption('Figure 13 — Share of driver estimates equal to zero (map W2-M4); interpret with the zero decomposition of Figure 4.'),
];

const conclusion = [
  h1('Conclusion'),
  p('The reconciliation stands, now on stricter footing. The subset relation, exact positional agreement, and zero attribute conflicts are consistent with one registry behind both exports; all 816 containers sit inside the official boundary; and defect D6 reduces to an explained coverage difference plus one number that only the re-export can supply. The review’s challenges produced real corrections: the driver zeros are two different phenomena and the larger one is workflow output; the cadence figure needed three denominators and per-container windows; the collection timestamps were under-described and contain the operation’s shift structure; the run weights cannot be allocated yet; and the old regression’s sample is not reproducible from held data.'),
  p('None of this weakens the pipeline. It sharpens what each variable is allowed to claim, and it converts three vague uncertainties into specific questions for the operator: the sensor unit, the weighing point, and the untruncated export.'),
];

const recommendations = [
  h1('Recommendations'),
  n1('Adopt the reconciled layer and windows — containers_reconciled.geojson plus sensor_active_windows.csv become canonical; promote both to Brain/03_db.'),
  n1('Estimate demand with active-window calendar denominators — per container, calendar days inside its own window, ceiling as censoring, negatives filtered by failure mode, 2020 screened.'),
  n1('Recompute fill-at-collection from pre-emptying readings — never from the paired zero; keep standalone zeros as the empty-container signal.'),
  n1('Adopt the event-level dataset — event_level_dataset.parquet is the bridge table between instruments; its selected_fill and QC flags are the only sanctioned way to mix sources, and the 15,732 large-disagreement rows stay quarantined until investigated.'),
  n1('Treat the instruments as non-interchangeable — 45.2% one-step agreement means neither validates the other at event level; models using both must include an instrument term, and driver −1 is recoded as missing.'),
  n1('Apply the negatives rule — drop all negatives, subtract episodes over 24 hours from active windows, never interpolate across an episode; revisit only if the operator identifies the −116 code.'),
  n1('Use the shift structure — encode the 04–06 h and 14–15 h shifts and the 7.4-hour median run duration as constraints in the routing extension.'),
  n1('Hold weight allocation — until the operator explains partial run recording and the weighing point; then allocate within single-fraction routes only.'),
  n1('Rebuild the regression sample — from the canonical 816 with written selection rules, or recover regdata_input.csv; either way, document exclusions.'),
  n1('Extend the data request — add export provenance (registry system), the sensor unit, the weighing point, the Óbidos-named circuits, and the untruncated export (D1).'),
];

const references = [
  h1('References'),
  ...[
    'DATA/XLS/Enchimentos_com_Recolhas[RioMaior].csv and Enchimentos_de_Sensores[RioMaior].csv — source files (parquet mirrors in Brain/03_db).',
    'W2/01_scripts/reconcile_csv.py and verify_codex_comments.py; W2/02_data_work/reconcile_stats.json and codex_verification.json — every figure in this report.',
    'W2/02_data_work/sensor_active_windows.csv and collection_runs.csv — per-container windows and per-run records.',
    'Report R1-01 — Methodology Audit (defect register); Report R1-02 — GIS and Spatial Data Inventory.',
    'Reviewer comments — R2-01_Driver_Sensor_Reconciliation_Codex_Final_Review.docx, 14 August 2026.',
    'Field survey notes, Rio Maior, October 2025 — Brain/01_sources/field_survey (site-level instrumentation policy).',
  ].map(x => b(x)),
];

const appendices = [
  h1('Appendices'),
  h2('Appendix A — Reproducibility'),
  b('Verification analyses: python W2/01_scripts/verify_codex_comments.py (DuckDB).'),
  b('Event matching: python W2/01_scripts/match_events.py — outputs event_level_dataset.parquet, match_stats.json.'),
  b('Charts: python W2/01_scripts/build_figures.py and build_figures_events.py (matplotlib, light-mode reference palette).'),
  b('Maps: QGIS layouts W2-M1…M4 rebuilt on DATA/QGIS Layout template/Layout template.qpt; HTML statistics boxes lower-left; boundary CAOP 2025 (DGT); exported 150 dpi.'),
  b('Report build: node W2/01_scripts/build_report_r201.js.'),
  h2('Appendix B — Comment-by-comment disposition'),
  tbl(['Review comment', 'Disposition in this revision'], [
    ['Charts and dashboards throughout', 'Six analytical charts added (Figures 1–6) beside the four maps.'],
    ['Executive summary in four parts', 'Restructured: matches / differs / uncertain / safe next.'],
    ['Registry claim as inference', 'Reworded in summary and section 2.1.'],
    ['Cadence 2.55 not reproducible', 'Three denominators reported with formulas; windows exported (3.1).'],
    ['Zeros are post-emptying confirmations', 'Quantified: 60,273 paired vs 81,703 standalone; Table 4 and Figure 3 revised.'],
    ['Active periods are demand inputs', 'Per-container windows in sensor_active_windows.csv; denominator rule in 3.2.'],
    ['Timestamps vs Rota mis-stated', 'Corrected in Table 1; distributions added (3.3, Figure 5).'],
    ['Run totals need verification', 'Km constant, weight not; median run records one container; allocation held (3.3).'],
    ['Effective windows, partial 2024', 'Table 2 and section 3.5.'],
    ['Glass: test cluster policy', 'Tested on 270 sites; policy explains fractions, D1 governs counts (2.4).'],
    ['Route purity 91/92', 'Confirmed; CE46 exception and Óbidos codes identified (3.4).'],
    ['N = 452 unexplained', 'Not reproducible from held data; rebuild recommended (3.6).'],
    ['D6 status', 'Reclassified in section 2.2; register wording supplied.'],
    ['Maps on the thesis template, tidy legends, box lower-left', 'All four maps rebuilt on the template; legends list every visible layer; statistics boxes lower-left; boundary provenance stated on each map.'],
    ['Ceiling cases (sensor 82–84 vs driver 100)', 'Quantified: 1,758 of 10,153 matched driver-100 rows (17.3%); flagged and documented (4.3).'],
    ['Driver −1 investigation', '57.5% have a valid sensor match; spread of matched values shows a missing observation, not a state; recoded as missing (4.4).'],
    ['Difference categories with justified thresholds', 'Half-step / one-step / beyond, from the 25-point driver scale; 28.0 / 17.1 / 54.8% (4.2).'],
    ['Acceptable agreement rate and sufficiency', '45.2% within one step — insufficient for interchangeability, sufficient for the adopted division of roles (4.2).'],
    ['Integrated event-level dataset', 'event_level_dataset.parquet with raw readings, timestamps, gaps, selected fill, selection rule, QC flags; large disagreements quarantined (4.5).'],
    ['Negative readings analysis', 'Two families, 329 containers, episode structure, level-shift evidence, explicit filtering rule (4.6).'],
    ['Event-matching method documented', 'Nearest-reading match by cid and timestamp, ±3 h primary window, gap distribution and seven-window sensitivity reported (4.1).'],
  ], [4300, 4700]),
];

const doc = new Document({
  numbering: { config: [bullets, num] },
  styles: { default: { document: { run: { font: FONT, size: 22 } } } },
  features: { updateFields: true },
  sections: [{
    properties: { page: { margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 18 })] })] }) },
    children: [
      ...cover, ...toc, ...lists, ...abbrev, ...exec,
      new Paragraph({ children: [new PageBreak()] }),
      ...s1, ...s2, ...s3, ...s4ev, ...s4, ...conclusion, ...recommendations, ...references, ...appendices,
    ],
  }],
});

Packer.toBuffer(doc).then(buf => { fs.writeFileSync(OUT, buf); console.log('WROTE', OUT, buf.length); });
