// R2-01 Revision D — plain-language rewrite addressing the 154 review comments of 15 Aug 2026
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
const t = (x, o = {}) => new TextRun({ text: x, font: FONT, size: 22, ...o });
const p = (x) => new Paragraph({ children: [t(x)], spacing: { after: 120 } });
const h1 = (x) => new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 320, after: 160 }, children: [t(x, { bold: true, size: 30 })] });
const h2 = (x) => new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 240, after: 120 }, children: [t(x, { bold: true, size: 25 })] });
const cap = (x) => new Paragraph({ spacing: { before: 60, after: 200 }, children: [t(x, { italics: true, size: 19 })] });
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
    rows: [new TableRow({ tableHeader: true, children: headers.map(x => mk(x, true, true)) }),
      ...rows.map(r => new TableRow({ children: r.map(c => mk(c)) }))],
  });
}
const bullets = { reference: 'b', levels: [{ level: 0, format: LevelFormat.BULLET, text: '–', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 360, hanging: 200 } } } }] };
const b = (x) => new Paragraph({ numbering: { reference: 'b', level: 0 }, spacing: { after: 80 }, children: [t(x)] });
const num = { reference: 'n', levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 360, hanging: 260 } } } }] };
const n1 = (x) => {
  const i = x.indexOf('—');
  const kids = i > 0 ? [t(x.slice(0, i + 1), { bold: true }), t(x.slice(i + 1))] : [t(x)];
  return new Paragraph({ numbering: { reference: 'n', level: 0 }, spacing: { after: 100 }, children: kids });
};
const img = (f, w, h) => new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { before: 120, after: 60 },
  children: [new ImageRun({ type: 'png', data: fs.readFileSync(f), transformation: { width: w, height: h } })],
});

const cover = [
  new Paragraph({ spacing: { before: 2800 } }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [t('Sensor-based Recyclables Collection Planning', { bold: true, size: 40 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 200 }, children: [t('Report R2-01 — Revision D', { size: 26 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 400 }, children: [t('The Two Container Data Files: What They Are, How They Relate, and What They Can Support', { bold: true, size: 32 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 200 }, children: [t('Rewritten in plain language after the full review of 15 August 2026 (154 comments)', { italics: true, size: 24 })] }),
  new Paragraph({ spacing: { before: 2400 } }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [t('Esmaeil Keyvanloo', { size: 24 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [t('PhD working repository · Working round W2 · 15 August 2026', { size: 22 })] }),
  new Paragraph({ children: [new PageBreak()] }),
];

const toc = [h1('Table of contents'), new TableOfContents('Table of contents', { hyperlink: true, headingStyleRange: '1-2' }), new Paragraph({ children: [new PageBreak()] })];

const lists = [
  h1('List of tables'),
  ...['Table 1 — The two files at a glance',
      'Table 2 — Container coverage across the two files',
      'Table 3 — Reconciliation checks on the 344 shared containers',
      'Table 4 — Sensor coverage by waste fraction',
      'Table 5 — The three parts of the 144,804 driver zeros',
      'Table 6 — Active windows: how long each sensor was alive',
      'Table 7 — Trip statistics (multi-bin collection identifiers)',
      'Table 8 — Record-level agreement between the two instruments',
      'Table 9 — The preliminary combined dataset: what each flag means',
      'Table 10 — What each variable can support now, and on what condition',
     ].map(x => p(x)),
  h1('List of figures'),
  ...['Figure 1 — Monthly record volume by source',
      'Figure 2 — Sensor-equipped containers inside the driver network (map)',
      'Figure 3 — Fill-value distributions of the two instruments',
      'Figure 4 — Classification of the driver zero records',
      'Figure 5 — Containers by waste fraction (map)',
      'Figure 6 — Active periods and the three recording rates',
      'Figure 7 — Collection start times',
      'Figure 8 — Negative sensor readings by year',
      'Figure 9 — Matching-window sensitivity',
      'Figure 10 — Agreement categories and by driver value',
      'Figure 11 — Negative readings by month and episode length',
      'Figure 12 — Mean sensor fill per container (map)',
      'Figure 13 — Where drivers most often record zero (map, supporting figure)',
     ].map(x => p(x)),
  new Paragraph({ children: [new PageBreak()] }),
];

const abbrev = [
  h1('Contractions and abbreviations'),
  tbl(['Term', 'Meaning'], [
    ['Driver file', 'Enchimentos_com_Recolhas: 264,817 rows written by collection crews, 2020–2024'],
    ['Sensor file', 'Enchimentos_de_Sensores: 1,048,575 rows from fill-level sensors, 2020–2024'],
    ['Bin / container', 'One recycling container; "cid" is its identifier (idcontentor)'],
    ['Ecoponto', 'A recycling point holding up to three containers: yellow (packaging), blue (paper), green (glass)'],
    ['Collection identifier', 'The idrecolha code that groups driver rows written during one servicing activity'],
    ['Active window', 'For one sensor: the days from its first to its last reading'],
    ['D1…D8', 'Numbered data problems tracked in the project defect register'],
    ['CAOP / DGT / INE', 'Official Portuguese boundaries / mapping agency / statistics institute'],
  ], [2100, 6900]),
  new Paragraph({ children: [new PageBreak()] }),
];

const story = [
  h1('The story in plain words'),
  p('The municipality has 816 recycling containers, standing in about 270 street sites, usually three together: yellow for packaging, blue for paper, green for glass. Two different "witnesses" tell us how full these containers were between January 2020 and April 2024. The first witness is the collection crew: each time they served a container they keyed in a rough eye estimate — empty, quarter, half, three-quarters, full — so the driver file only speaks on collection days. The second witness is a set of electronic sensors mounted inside 344 of the containers (nearly all on paper and packaging bins, almost none on glass), which measured the level automatically about twice a day, every day, whether or not anyone came. That is why the sensor file is four times larger — not because there is more waste, but because that witness talks more often. The two witnesses describe exactly the same containers, in the same places. But when we put their statements side by side at the same moments, they agree only about half the time, the sensors never report more than 82–84 even when the crew says "full", about nine percent of sensor readings are error codes rather than measurements, and most of the crew’s zeros turn out to be "I just emptied it" confirmations rather than "I found it empty". So each witness is useful — the sensor for how fast bins fill day by day, the crew for covering all 816 bins and the trips they drove — but neither can be taken at face value, and the report explains exactly what to trust each one for.'),
  new Paragraph({ children: [new PageBreak()] }),
];

const exec = [
  h1('Executive summary'),
  h2('What matches'),
  p('All 344 sensor-equipped containers also appear in the driver file, with identical positions, types, volumes, and waste fractions. Nothing appears on the sensor side only. This is consistent with both files coming from one shared container registry; the operator should confirm the export source, but the match itself is clean.'),
  h2('What differs'),
  p('The instruments work differently. The crew records one of five coded levels (0, 25, 50, 75, 100), and only when visiting. The sensor records a number between 0 and 84, on a schedule. Record counts are therefore not comparable: in 2023–2024 the sensors produced many readings per bin per day while the crew produced a few per bin per month. More sensor rows does not mean more waste or more bins.'),
  h2('What remains uncertain'),
  p('Four things need outside confirmation: what the sensor’s 82–84 upper limit physically means (possibly a blind-zone limit of the device); what exactly one collection identifier covers, since two thirds of them contain a single bin; how the trip weight is recorded (it is not always constant within one identifier); and whether 344 is the full instrumented fleet, because the sensor export stops exactly at the Excel row limit (D1).'),
  h2('What can be analysed next with the current evidence'),
  p('Fill-speed estimation per sensor bin using calendar time inside each bin’s active window; trip-level statistics (duration, distance, load, kg per km) computed once per collection identifier; network-wide siting on all 816 locations; and record-level cross-checks between the instruments. Weight per individual bin, formal shift rules, and any use of the 82–84 limit as "100%" stay on hold until the operator answers the open questions.'),
];

const s1 = [
  h1('1. The two files and how they relate'),
  p('Both files share one layout of 19 columns. The difference is who wrote the fill value and when. Table 1 says everything essential.'),
  tbl(['', 'Driver file', 'Sensor file'], [
    ['Who writes it', 'Collection crew, by eye', 'Electronic sensor, automatic'],
    ['When', 'Only at servicing visits', 'On a schedule, about twice a day'],
    ['Containers covered', '816 (all)', '344 (subset; 2 glass)'],
    ['Fill values', 'Five coded levels: 0, 25, 50, 75, 100 (plus −1 = missing entry)', '0 to 84, plus negative error codes (9.2%)'],
    ['Rows', '264,817', '1,048,575 — exactly the Excel row limit, so possibly cut short (D1)'],
    ['Period', 'Jan 2020 – Apr 2024', 'Jan 2020 – Apr 2024 (2024 is January–April only in both)'],
    ['Extra content', 'Collection identifiers, route codes, start/end times, trip km and kg', 'None usable (its idrecolha column is corrupted, D2)'],
  ], [1800, 3600, 3600]),
  cap('Table 1 — The two files at a glance.'),
  p('Figure 1 shows the monthly volumes. The sensor line rises steeply in 2023; treat that as recording behaviour, not as growth of the network — with a possibly truncated export we cannot separate more readings per bin from more active bins without the full export. The grey band marks 2024, which covers only four months; never compare it to a full year directly.'),
  img(path.join(FIGS, 'F1_monthly_volume.png'), 620, 244),
  cap('Figure 1 — Monthly record volume by source. The 2024 band is a partial year.'),
];

const s2 = [
  h1('2. Same containers? Yes — here is the check'),
  p('We joined the files on the container identifier. Every sensor-file container exists in the driver file; the shared 344 agree on position (to the metre), type, volume, and fraction, with zero exceptions. Tables 2 and 3 separate coverage from matching quality, as requested.'),
  tbl(['Container group', 'Containers', 'Share'], [
    ['Driver file (total)', '816', '100%'],
    ['In both files (sensor-equipped)', '344', '42.2%'],
    ['Driver-only', '472', '57.8%'],
    ['Sensor-only', '0', '0%'],
  ], [4200, 2600, 2200]),
  cap('Table 2 — Container coverage across the two files.'),
  tbl(['Reconciliation check (344 shared containers)', 'Result'], [
    ['Coordinate offset', '0.0 m for all 344'],
    ['Type mismatches', '0'],
    ['Volume mismatches', '0'],
    ['Waste-fraction mismatches', '0'],
  ], [5400, 3600]),
  cap('Table 3 — Reconciliation checks on the 344 shared containers.'),
  tbl(['Fraction', 'Driver containers', 'Sensor containers', 'Sensor coverage', 'Sensor observations'], [
    ['Paper/card (blue)', '280', '173', '61.8%', '509,091'],
    ['Packaging (yellow)', '278', '169', '60.8%', '519,405'],
    ['Glass (green)', '258', '2', '0.8%', '20,079'],
    ['All', '816', '344', '42.2%', '1,048,575'],
  ], [2100, 1800, 1800, 1600, 1700]),
  cap('Table 4 — Sensor coverage by fraction. Coverage = sensor containers ÷ driver containers in that fraction × 100.'),
  p('Why is glass almost uninstrumented? Grouping containers by identical coordinates gives 270 sites; 214 hold all three fractions. Of the 253 multi-container sites, 105 carry exactly one sensor, 118 carry two or more, and 30 carry none. The pattern strongly suggests the operator instrumented the faster-filling paper and packaging bins first — which matches the field visit of October 2025 — but the formal deployment policy should be confirmed with the operator, and the truncated export (D1) could also have removed containers. One warning for later modelling: because sensors sit almost only on two fractions, sensor-based demand results describe paper and packaging, not glass, and this selection must be kept in mind.'),
  p('On the old defect D6 ("the files have different container counts"): the dangerous interpretation — mismatched identities or positions — is ruled out. What remains is a coverage difference (only part of the network is instrumented), with the exact fleet size pending the complete export.'),
  img(path.join(MAPS, 'W2-M1 Source reconciliation.png'), 620, 438),
  cap('Figure 2 — The 344 sensor-equipped containers (green) as a subset of the 816 driver-recorded containers (orange). Boundary: CAOP 2025 (DGT).'),
  img(path.join(MAPS, 'W2-M2 Waste fractions.png'), 620, 438),
  cap('Figure 5 — Containers by waste fraction in ecoponto colours. Symbols overlap at shared sites; read composition from Table 4, not by counting dots. Colours show fraction, not sensor status.'),
];

const s3 = [
  h1('3. What each measurement really means'),
  h2('3.1 The driver values, and the three kinds of zero'),
  p('The crew’s scale has five coded levels. More than half of all driver rows are zero — but zero means three different things, and separating them changes every statistic about "how full bins are at collection". The 144,804 zeros split exactly like this:'),
  tbl(['Kind of zero', 'Rows', 'Plain meaning'], [
    ['Confirmation zero: written within 15 minutes AFTER a nonzero reading of the same bin — and every row that carries a collection identifier is one of these', '60,273', '"I just emptied this bin." Says nothing about how full it was before.'],
    ['Paired zero, previous reading also zero or invalid', '2,828', 'Unclear; kept separate, not used.'],
    ['Standalone zero: no other reading nearby', '81,703', 'The best candidates for "found the bin empty" — still to be validated before use.'],
  ], [4600, 1200, 3200]),
  cap('Table 5 — The three parts of the 144,804 driver zeros (they sum exactly).'),
  p('Rule that follows: to know how full a bin was when it was collected, use the reading just BEFORE the emptying, never the zero written after it. The −1 values (249 rows) are failed or forgotten entries, treated as missing.'),
  img(path.join(FIGS, 'F3_zero_anatomy.png'), 620, 205),
  cap('Figure 4 — Classification of the driver zero records. The timing pattern strongly supports, but does not formally prove, the post-emptying interpretation.'),
  h2('3.2 The sensor values and the 82–84 limit'),
  p('Sensor readings run from 0 to 84 and never higher — on every container, whatever its size or shape. So the field cannot yet be read as a true 0–100 percentage. One plausible physical explanation, to be checked with the supplier, is the sensor’s blind zone: an ultrasonic device cannot measure the last few centimetres below itself, so its scale may top out early. Until the supplier or operator answers, 82–84 is treated as an unresolved upper limit; where we need a 0–100 scale for comparisons we divide by each container’s own maximum, clearly labelled as a provisional assumption, and we always show the raw numbers beside it.'),
  img(path.join(FIGS, 'F2_fill_distributions.png'), 620, 244),
  cap('Figure 3 — The two instruments’ value distributions: five coded levels (left) against a near-continuous 0–84 range (right); negative sensor values are error codes shown separately.'),
  h2('3.3 Negative sensor readings — decision made'),
  p('9.2% of sensor rows (96,832) are negative, which no fill level can be. They span 111 distinct values from −1 to −116. Most sit at the small end (−1…−9: 47%) or at −116 and −89 (together 42%), with a thin spread between. They occur on 329 of the 344 containers, are worst in 2020 (36.6% of that year’s rows, falling to 2.6% by 2024), and worst on one sensor model (E BLUE BEE, 23.6%). They come in 29,885 consecutive bursts; most bursts are a single reading, but 17.8% last over a day, and the level often jumps across a burst (average change 28.5 points versus 9.6 between normal neighbouring readings), so something real — probably an emptying — often happens during them.'),
  p('The decision, closing this task: negative readings are removed from all fill analysis — they are device signals, not measurements — but kept in the raw data as quality metadata. No value is ever interpolated across a burst. Where a burst lasts longer than a threshold (provisionally 24 hours, to be finalised with the operator), those days are also removed from the bin’s observation time so that fill-speed estimates are not diluted. The exact meaning of the codes goes into the operator/supplier question list; if answers arrive, the rule can be refined, but no analysis waits for that.'),
  img(path.join(FIGS, 'F9_negatives_deepdive.png'), 620, 234),
  cap('Figure 11 — Negative readings by month (left; ranges labelled by observed magnitude, meaning pending confirmation) and burst length in consecutive readings (right).'),
  img(path.join(FIGS, 'F6_negatives_by_year.png'), 620, 205),
  cap('Figure 8 — Share of negative readings per year: 36.6% (2020), 8.7% (2021), 8.0% (2022), 6.3% (2023), 2.6% (partial Jan–Apr 2024).'),
  h2('3.4 Active windows, explained simply'),
  p('An active window is simply the stretch of time a sensor was actually alive: from its first reading to its last. Example: if a sensor’s first reading is 1 March 2022 and its last is 30 April 2024, its active window is those 792 days — even though the study spans 1,582 days. Why it matters: to say how fast a bin fills per day, you divide by days. Divide by the full 1,582 days for a sensor that only lived 792, and its fill speed looks half of what it really was. 66% of sensors lived through nearly the whole study, but 64 of them (19%) lived less than a year, so this correction is not cosmetic — for the shortest window (56 days) the error would be a factor of 28 (1,582 ÷ 56 ≈ 28).'),
  tbl(['Active window length', 'Containers', 'Share'], [
    ['Under 1 year', '64', '19%'],
    ['1–2 years', '1', '0%'],
    ['2–3 years', '4', '1%'],
    ['3–4 years', '49', '14%'],
    ['About the full period', '226', '66%'],
  ], [3600, 2700, 2700]),
  cap('Table 6 — Active windows: how long each sensor was alive (per-container list: sensor_active_windows.csv).'),
  p('Three recording rates were quoted in earlier revisions; they answer different questions and are all descriptive. 1.93 = all readings ÷ (344 bins × 1,582 days): how much data exists per bin per calendar day. 2.55 = the average count on days that have at least one reading: how often a working sensor reports. 1.58 = the median bin’s rate inside its own active window. For the demand model none of these is the denominator: the denominator is calendar days inside each bin’s own active window, minus confirmed outage days (effective exposure time = active-window days − confirmed outage days).'),
  img(path.join(FIGS, 'F4_cadence_windows.png'), 620, 244),
  cap('Figure 6 — Active periods (left; dashed line = 365 days) and the three descriptive rates (right). None of the three is the demand denominator.'),
];

const s4 = [
  h1('4. The trips'),
  p('The driver file records servicing work as collection identifiers (idrecolha). Each one groups the bins served, each with its timestamp, plus a start time, an end time, a distance, and a weight. Since every bin has coordinates, ordering the bins by time draws the recorded path of the trip. Two honest cautions first: two thirds of the 9,984 identifiers contain a single bin, so what is recorded is often only part of the real tour — the operator must confirm what one identifier covers; and connecting bins with straight lines is not the road the truck drove (no GPS exists). The straight-line path is typically only 13% of the recorded distance — the rest is depot travel, road detours, and unrecorded stops.'),
  tbl(['Statistic (over the 3,430 multi-bin trips)', 'Value'], [
    ['Days with recorded activity', '1,261 (up to 8 trips in one day)'],
    ['Bins recorded per trip', 'median 4, top tenth above 46'],
    ['Duration', 'median 7.6 h'],
    ['Recorded distance', 'median 135 km'],
    ['Recorded load', 'median 2,300 kg'],
    ['Efficiency, kg per km', 'median 16.8 (trip-level indicator only — never per-bin demand)'],
    ['Start times', 'two clusters: 04–06 h and 14–15 h, Monday to Saturday'],
    ['By fraction', 'packaging 1,725 trips, paper 1,705, glass none coded'],
  ], [5000, 4000]),
  cap('Table 7 — Trip statistics, computed once per identifier (distances and weights are never summed across rows — defect D8).'),
  p('The start-time clusters look like a morning and an afternoon operating period, and trip durations around 7.6 hours fit that picture; they are treated as observed patterns, not as formal shift rules, until the operator confirms the schedule. Weight needs one more caution: within some identifiers the recorded weight varies from row to row, so how and where weighing happens must be clarified before any weight is split over bins (defect D5). Until then, per-bin mass will be estimated from fill level, bin volume, and fraction-specific density, then scaled so the trip total matches — not divided equally.'),
  img(path.join(FIGS, 'F5_shift_structure.png'), 620, 218),
  cap('Figure 7 — Collection start times: two clear concentration periods (04–06 h, 14–15 h).'),
  p('An interactive companion, Trip_Explorer_RioMaior.html, lets you browse every trip on a calendar — days shaded by trip count, multiple trips per day listed separately — and draw any selection of trips on a street map with per-trip statistics. It is the fastest way to build intuition about the operation.'),
];

const s5 = [
  h1('5. Comparing the two instruments, record by record'),
  h2('5.1 Method, in one breath'),
  p('For each of the 127,928 driver rows on sensor-equipped bins, find the nearest valid sensor reading of the same bin, before or after; keep the pair if the time gap is at most 3 hours. The ±3 h choice is practical — wide enough to catch a same-shift reading, narrow enough to stay contemporaneous — and the honest justification is the sensitivity test: from ±15 minutes to ±24 hours the agreement rate stays between 48.9% and 50.9% (Table in Figure 9), though coverage grows from 5% to 71%, so sample composition does change with the window and the ±3 h results are read with that caution. Since most driver rows are not collection events, this is a record-level comparison; a collection-event version (pairing each emptying with the last valid sensor reading before it) is the next step once the identifier semantics are confirmed.'),
  img(path.join(FIGS, 'F7_window_sensitivity.png'), 620, 234),
  cap('Figure 9 — Wider matching windows add pairs but barely change the agreement rate.'),
  h2('5.2 How much do they agree?'),
  p('Thresholds come from the driver’s own 25-point spacing: within half a step (≤12.5) the two would usually round the same way; within one step (≤25) they sit in adjacent categories; beyond that they genuinely disagree. Sensor values are put on a 0–100 scale using the provisional ceiling assumption of section 3.2.'),
  tbl(['Result (28,683 matched pairs)', 'Value'], [
    ['Small difference (≤12.5)', '8,039 — 28.0%'],
    ['Moderate (12.5–25)', '4,912 — 17.1%'],
    ['Large (>25)', '15,732 — 54.8%'],
    ['Acceptable (within one step, ≤25)', '12,951 — 45.2%'],
    ['Agreement when driver said 25', '75.0% (best)'],
    ['Agreement when driver said 100', '38.4% (worst)'],
  ], [5000, 4000]),
  cap('Table 8 — Record-level agreement. "Acceptable" = within one driver scale step.'),
  p('Less than half agree. The rate is steady across windows, and agreement is weakest at the top of the driver scale: when the crew says "full", the sensor usually reads much lower — even at its raw ceiling of 82–84 in only 1,758 of the 10,153 driver-100 pairs (17.3%). Whether that reflects crew overstating, sensor under-reading near the top, or the unresolved ceiling cannot be decided from the data alone. The safe conclusion is simple: the two instruments are not interchangeable, neither one validates the other, and any model using both needs to know which instrument each number came from.'),
  img(path.join(FIGS, 'F8_agreement.png'), 620, 234),
  cap('Figure 10 — Agreement categories, and the acceptable share by driver value.'),
  h2('5.3 The combined dataset — preliminary'),
  p('All 127,928 rows, both raw readings, both timestamps, the gap, a plain flag, and a chosen value with its rule written out, live in event_level_dataset.parquet. It is labelled preliminary for a stated reason: the current rule keeps a sensor value partly when it agrees with the driver, which risks circularity; the final version will select on sensor quality alone and keep agreement as a separate diagnostic. Table 9 explains every flag in plain words.'),
  tbl(['Flag', 'Rows', 'Means', 'Chosen value'], [
    ['NO_SENSOR_MATCH', '62,309', 'No sensor reading within 3 h', 'Driver (where valid)'],
    ['EVENT_ZERO_POST_EMPTYING', '36,790', 'Confirmation zero written at a collection (carries an identifier)', 'None — excluded from fill statistics'],
    ['LARGE_DISAGREEMENT', '15,732', 'Instruments differ by more than one step', 'None — held for investigation (only this flag is a disagreement hold-out)'],
    ['GOOD / MODERATE_AGREEMENT', '6,281 / 4,912', 'Within half / one step', 'Sensor (provisional 0–100 scale)'],
    ['CEILING_CASE', '1,758', 'Driver 100 while sensor at raw 82–84', 'Sensor, rationale documented'],
    ['DRIVER_MISSING_*', '84 / 62', 'Driver wrote −1; sensor available / not', 'None under the current conservative rule (the 84 could take the sensor value once matching is finalised)'],
  ], [2300, 1300, 2900, 2500]),
  cap('Table 9 — The flags, in plain words. Categories are mutually exclusive; a chosen value exists on 75,260 rows (58.8%).'),
];

const s6 = [
  h1('6. What can be used now, and on what condition'),
  tbl(['Variable', 'Use now', 'Conditional / not yet'], [
    ['Sensor fill series (342 paper+packaging bins)', 'Fill-speed estimation with active-window exposure, after the negatives rule', 'Absolute percentages — wait for the ceiling answer; glass — only 2 bins'],
    ['Driver coded levels (816 bins)', 'Relative fullness patterns from pre-emptying readings; glass patterns', 'Any per-bin mass — needs density calibration, not level codes alone'],
    ['Container registry (816 bins, 270 sites)', 'Siting, distances, site-level aggregation', '—'],
    ['Collection identifiers (9,984)', 'Trip statistics computed once per identifier; kg/km; operating-time patterns', 'Treating each as one full vehicle tour; formal shift constraints — operator confirmation'],
    ['Trip weights / km', 'Fleet-level tonnage checks; km at trip level', 'Splitting weight over bins (D5); summing across rows (D8)'],
    ['Route codes (92)', 'Fraction-specific sequences on the coded 8.6% of rows', 'Complete circuit reconstruction'],
  ], [2400, 3400, 3200]),
  cap('Table 10 — What each variable can support now, and on what condition.'),
  p('Two defects join the register from this review. D5: trip weight cannot be attributed to individual containers; estimate per-bin mass from fill, volume, and density, calibrated to the trip total. D8: trip-level weight and distance repeat across rows of one identifier; every operational indicator must count them once per identifier.'),
  p('The old regression’s N = 452 stays unexplained: starting from 816 containers, every documented filter we tested lands elsewhere (801 with any weight record; 801 with distance; 498 with route codes; the geodatabase snapshot holds 464). Until the intermediate file or its rules are found, that regression is treated as not reproducible, and the sample will be rebuilt from the 816 with a written filtering log. A full exploratory round — fill, weight, and distance patterns by day, week, month, season, and year, by fraction, with spatial statistics — is planned as the next working round (W3) on top of the cleaned variables defined here.'),
  img(path.join(MAPS, 'W2-M3 Sensor mean fill.png'), 620, 438),
  cap('Figure 12 — Mean sensor fill per container (raw 0–84 scale, negatives removed).'),
  img(path.join(MAPS, 'W2-M4 Driver zero share.png'), 620, 438),
  cap('Figure 13 — Where drivers most often record zero. Supporting data-quality figure only: a zero can be a confirmation, an empty bin, or unclear (section 3.1).'),
];

const conclusion = [
  h1('Conclusion'),
  p('Confirmed by the data: one container network, fully reconciled between the two files; all 816 bins inside the official boundary; the exact composition of the driver zeros; the full shape of the negative-reading problem and a working rule for it; trip statistics computed the safe way, once per identifier.'),
  p('Supported but pending outside confirmation: the shared-registry reading of the perfect match; the sensor-deployment explanation of the glass gap; the two operating periods; the meaning of one collection identifier; the blind-zone reading of the 82–84 limit; the weighing mechanism behind the trip totals.'),
  p('None of the open points stops the work. They define it: the sensor series, cleaned by the negatives rule and measured over active windows, carries the demand model for paper and packaging; the driver file carries glass, the network, and the trips; and the question list for the operator — unit and ceiling of the sensor, identifier meaning, weighing point, complete export — is now precise enough to be answered quickly.'),
];

const recommendations = [
  h1('Recommendations'),
  h2('Adopt now'),
  n1('Use active-window exposure — every per-day rate divides by calendar days inside the bin’s own active window, minus confirmed outage days.'),
  n1('Apply the negatives rule — drop negatives from fill analysis, keep as QC metadata, never bridge across a burst.'),
  n1('Compute trip indicators once per identifier — including kg/km; never sum weight or distance across rows (D8).'),
  n1('Use pre-emptying readings for fill-at-collection — never the confirmation zero; treat driver −1 as missing.'),
  n1('Rebuild the regression sample from the 816 with a written filtering log — and record the reconstruction attempts that failed to reach 452.'),
  h2('Adopt after confirmation'),
  n1('Sensor 0–100 rescaling — keep provisional until the supplier explains the 82–84 limit; report raw values alongside.'),
  n1('Shift constraints — encode the two operating periods only after the operator confirms the schedule.'),
  n1('Per-bin mass — fill × volume × density, calibrated to trip totals (D5), once the weighing point is clarified.'),
  n1('Final combined dataset — reselect on sensor quality alone to remove the circularity, then freeze it as the bridge table.'),
  n1('Operator question list — sensor unit and ceiling, identifier meaning, weighing point, negative codes, Óbidos-named routes, complete untruncated export.'),
];

const references = [
  h1('References'),
  h2('Data and reproducibility sources'),
  ...[
    'Raw data: DATA/XLS/Enchimentos_com_Recolhas[RioMaior].csv; Enchimentos_de_Sensores[RioMaior].csv (parquet mirrors: Brain/03_db/parquet, built 2026-08-08).',
    'Scripts → outputs: reconcile_csv.py → reconcile_stats.json, containers_reconciled.geojson · verify_codex_comments.py → codex_verification.json, sensor_active_windows.csv, collection_runs.csv · match_events.py → event_level_dataset.parquet, match_stats.json · build_trips.py → trips.json, trip_stats.json · build_figures*.py → figures F1–F9 · QGIS project → maps W2-M1…M4 (all under W2/).',
    'Interactive: W2/03_outputs/Trip_Explorer_RioMaior.html.',
    'Internal reports: R1-01 Methodology Audit (defect register); R1-02 GIS and Spatial Data Inventory.',
    'Field survey notes, Rio Maior, 1 October 2025 — Brain/01_sources/field_survey.',
    'Reviewer comments: R2-01 …_Codex_Final_Review.docx (14 Aug) and the 154 in-document comments of 15 Aug 2026.',
  ].map(x => b(x)),
  h2('Bibliographic references'),
  p('None cited in this data report; methodological literature enters with the modelling rounds.'),
];

const appendices = [
  h1('Appendices'),
  h2('Appendix A — Reproducibility and environment'),
  b('Environment: Windows 11 · Python 3.12 (duckdb, pandas, matplotlib 3.11) · Node.js (docx) · QGIS 3.44.12 LTR · data date 2026-08-13.'),
  b('Parameters that matter: matching window ±180 min; agreement thresholds 12.5 / 25; negatives outage threshold 24 h (provisional); site = identical coordinates rounded to 5 decimals (≈1 m).'),
  b('The matching outputs reproduce the CURRENT specification; if the collection-event matching rule replaces the record-level rule, event_level_dataset.parquet and Figures 9–10 must be regenerated.'),
  h2('Appendix B — Review disposition, by certainty'),
  tbl(['Status', 'Topics'], [
    ['Resolved in the data', 'Zero decomposition (sums exactly); coverage tables and percentages; negatives distribution, decision rule, and yearly counts; active windows and exposure rule; trip statistics once per identifier; D5 and D8 registered; N = 452 attempts documented; plain-language rewrite throughout; simplified tables; corrected ±3 h justification; record-level naming.'],
    ['Provisionally classified', 'Post-emptying reading of confirmation zeros; sensor-deployment reading of the glass gap; operating-time clusters; magnitude-based negative groupings; ceiling normalization; combined-dataset selection rule (circularity flagged).'],
    ['Open — needs operator or supplier', 'Sensor unit and 82–84 limit; identifier semantics; weighing point and weight recording; negative-code meanings; Óbidos route family; complete export (D1); formal shift schedule; deployment policy document.'],
  ], [2200, 6800]),
  h2('Appendix C — Where to find every number'),
  b('Each table and figure lists its source script in Appendix A’s mapping; every statistic in the text traces to reconcile_stats.json, codex_verification.json, match_stats.json, or trip_stats.json.'),
];

const doc = new Document({
  numbering: { config: [bullets, num] },
  styles: { default: { document: { run: { font: FONT, size: 22 } } } },
  features: { updateFields: true },
  sections: [{
    properties: { page: { margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 18 })] })] }) },
    children: [
      ...cover, ...toc, ...lists, ...abbrev, ...story, ...exec,
      new Paragraph({ children: [new PageBreak()] }),
      ...s1, ...s2, ...s3, ...s4, ...s5, ...s6, ...conclusion, ...recommendations, ...references, ...appendices,
    ],
  }],
});

Packer.toBuffer(doc).then(buf => { fs.writeFileSync(OUT, buf); console.log('WROTE', OUT, buf.length); });
