// R1-02 GIS & Spatial Data Inventory report builder
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, PageBreak,
  Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType, TableOfContents,
  LevelFormat, ImageRun, Footer, PageNumber, NumberFormat,
} = require('docx');

const OUT = path.resolve(__dirname, '../../04_outputs/reports/R1-02_GIS_Data_Inventory.docx');

// ---------- helpers ----------
const FONT = 'Georgia';
const t = (text, opts = {}) => new TextRun({ text, font: FONT, size: 22, ...opts });
const p = (text, opts = {}) => new Paragraph({ children: [t(text, opts.run || {})], spacing: { after: 120 }, ...opts });
const h1 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 320, after: 160 }, children: [t(text, { bold: true, size: 30 })] });
const h2 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 240, after: 120 }, children: [t(text, { bold: true, size: 25 })] });
const caption = (text) => new Paragraph({ spacing: { before: 60, after: 200 }, children: [t(text, { italics: true, size: 19 })] });

const CW = 9360; // usable width DXA (A4, 1" margins ~ 9360 at 12240-page? A4: 11906-2880=9026) use 9000
const W = 9000;
function tbl(headers, rows, widths) {
  const ws = widths || headers.map(() => Math.floor(W / headers.length));
  const mk = (txt, bold, shade) => new TableCell({
    width: { size: 1, type: WidthType.AUTO },
    shading: shade ? { type: ShadingType.CLEAR, fill: 'E8E4DC' } : undefined,
    margins: { top: 60, bottom: 60, left: 90, right: 90 },
    children: String(txt).split(' ').map(s => new Paragraph({ children: [t(s, { bold: !!bold, size: 19 })] })),
  });
  return new Table({
    width: { size: W, type: WidthType.DXA },
    columnWidths: ws,
    rows: [
      new TableRow({ tableHeader: true, children: headers.map(hd => mk(hd, true, true)) }),
      ...rows.map(r => new TableRow({ children: r.map(c => mk(c)) })),
    ],
  });
}

const bullets = { config: [{ reference: 'b', levels: [{ level: 0, format: LevelFormat.BULLET, text: '–', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 360, hanging: 200 } } } }] }] };
const b = (text) => new Paragraph({ numbering: { reference: 'b', level: 0 }, spacing: { after: 80 }, children: [t(text)] });
const num = { reference: 'n', levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 360, hanging: 260 } } } }] };
const n1 = (text, boldLead) => {
  const idx = boldLead ? text.indexOf('—') : -1;
  const kids = idx > 0 ? [t(text.slice(0, idx + 1), { bold: true }), t(text.slice(idx + 1))] : [t(text)];
  return new Paragraph({ numbering: { reference: 'n', level: 0 }, spacing: { after: 100 }, children: kids });
};

const img = (file, w, h) => new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { before: 120, after: 60 },
  children: [new ImageRun({ type: 'png', data: fs.readFileSync(file), transformation: { width: w, height: h } })],
});

// ---------- content ----------
const cover = [
  new Paragraph({ spacing: { before: 2800 } }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [t('Sensor-based Recyclables Collection Planning', { bold: true, size: 40 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 200 }, children: [t('Report R1-02', { size: 26 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 400 }, children: [t('GIS and Spatial Data Inventory for the Rio Maior Case Study', { bold: true, size: 32 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 200 }, children: [t('Available, downloaded, and outstanding data, with relevance to the thesis pipeline', { italics: true, size: 24 })] }),
  new Paragraph({ spacing: { before: 2400 } }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [t('Esmaeil Keyvanloo', { size: 24 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [t('PhD working repository · Working round W1', { size: 22 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [t('13 August 2026', { size: 22 })] }),
  new Paragraph({ children: [new PageBreak()] }),
];

const toc = [
  h1('Table of contents'),
  new TableOfContents('Table of contents', { hyperlink: true, headingStyleRange: '1-2' }),
  new Paragraph({ children: [new PageBreak()] }),
];

const listOfTables = [
  h1('List of tables'),
  ...[
    'Table 1 — Layers held in DATA/GEO DATA/gis rio.gdb before this round',
    'Table 2 — Other spatial assets already in the repository',
    'Table 3 — Data downloaded into GIS_DATA on 13 August 2026',
    'Table 4 — Data obtainable but not yet downloaded',
    'Table 5 — Data that must be requested from institutions',
    'Table 6 — Relevance of each dataset to the pipeline stages',
  ].map(x => p(x)),
];

const listOfFigures = [
  h1('List of figures'),
  p('Figure 1 — Container network over the road graph (W1 map M1)'),
  p('Figure 2 — Sensor coverage of the container fleet (W1 map M3)'),
  new Paragraph({ children: [new PageBreak()] }),
];

const abbrev = [
  h1('Contractions and abbreviations'),
  tbl(['Term', 'Meaning'], [
    ['APA', 'Agência Portuguesa do Ambiente (environment agency)'],
    ['BGRI', 'Base Geográfica de Referenciação de Informação (census geography, INE)'],
    ['CAOP', 'Carta Administrativa Oficial de Portugal (official boundaries, DGT)'],
    ['COS', 'Carta de Uso e Ocupação do Solo (national land-use map, DGT)'],
    ['CRUS', 'Carta do Regime de Uso do Solo (PDM zoning)'],
    ['DGT', 'Direção-Geral do Território'],
    ['DTM / DSM', 'Digital terrain model / digital surface model'],
    ['gdb', 'Esri file geodatabase (DATA/GEO DATA/gis rio.gdb)'],
    ['INE', 'Instituto Nacional de Estatística'],
    ['MDT', 'Modelo Digital do Terreno (Portuguese for DTM)'],
    ['PDM', 'Plano Diretor Municipal'],
    ['PGRI', 'Plano de Gestão dos Riscos de Inundações (flood risk plan)'],
    ['REN / RAN', 'National ecological / agricultural reserve'],
    ['SRUP', 'Servidões e restrições de utilidade pública'],
    ['TM06', 'ETRS89 / Portugal TM06 projection, EPSG:3763'],
    ['UTM 29N', 'WGS 84 / UTM zone 29N projection, EPSG:32629'],
  ], [1600, 7400]),
  new Paragraph({ children: [new PageBreak()] }),
];

const execSummary = [
  h1('Executive summary'),
  p('This report answers three questions. What spatial data does the project already hold, what was added by the acquisition round of 13 August 2026, and what is still missing before the analysis chain (demand estimation, capacitated p-median, scenario generation) can run on real geography.'),
  p('The holdings before this round were thin. One Esri geodatabase carries seven layers, of which exactly one is irreplaceable: the 464 georeferenced container locations with type, volume, and waste fraction. The rest are partial copies of public data, and two carry defects: the census layer holds 222 of the 572 official 2021 subsections, and the 147,319-point sensor layer sits in UTM 29N while every other layer uses TM06. Its route, distance, and weight fields are present in the schema and empty in the data.'),
  p('The new GIS_DATA library (6 GB, 52 styled layers in the QGIS project) closes most public-data gaps: official boundaries, the full BGRI 2021 and 2011 census with population counts, two vintages of national land use, PDM zoning, a LiDAR-derived 10 m terrain model with slope, the geocoded river network, flood and rural-fire hazard, and the electricity distribution network down to individual poles. Everything is clipped to the study area plus 10 km and delivered in EPSG:3763.'),
  p('What remains cannot be downloaded. The operator’s collection routes, schedules, vehicle GPS, and per-event weights exist only inside Valorsul and the Câmara Municipal, and the full sensor export is still truncated at the Excel row limit (defect D1). These requests, already specified in report R1-01, are now the binding constraint on the thesis.'),
];

// Section 1
const s1 = [
  h1('1. Purpose and scope'),
  p('The inventory covers every spatial asset in the repository — DATA/GEO DATA, the CSV coordinate columns, Brain/03_db, the QGIS project — plus the GIS_DATA library assembled on 13 August 2026, and closes with a gap list and a relevance rating of each dataset against the pipeline stages. Non-spatial assets (documents, the semantic index) are out of scope; they are catalogued in the Brain manifests.'),
];

// Section 2: held
const s2 = [
  h1('2. What the project already held'),
  h2('2.1 The Esri geodatabase'),
  p('Seven layers, mixed provenance, mixed reference systems. Table 1 gives the verdict on each.'),
  tbl(['Layer', 'Content', 'N', 'CRS', 'Verdict'],
    [
      ['driver_464_unique_bins_for_GIS_TM06', 'Container locations with id, plate, type (OVO, TITAN, VRL…), volume (2500–5000 L), waste fraction, freguesia', '464', 'TM06', 'Irreplaceable. The only spatial asset the public sources cannot supply. Text encoding is damaged (“SANTARM”, “Vale de àbidos”) and needs one repair pass.'],
      ['driver_Rio_Maior_TM06_new', 'Sensor readings geocoded to container points; fill level, read date/time', '147,319', 'UTM 29N', 'Misleading name — these are sensor events, not driver traces. Rota, dt_start, km_total, weight_tot are empty in every sampled row. A geocoded subset of the raw_sensors table; keep as cross-check only.'],
      ['population_rio_maior_2021_polygon', 'BGRI 2021 subsections (geometry + codes)', '222', 'TM06', 'Incomplete: 222 of 572 official subsections, and no population attributes. Superseded by the official BGRI2021_1414 GeoPackage.'],
      ['Rio_Maior_landuse', 'COS 2018 clip, 4 class levels', '1,046', 'TM06', 'Superseded by the fresh COS 2018 v4 / COS 2025 extracts.'],
      ['Reprojected_gis_osm_building100', 'OSM building footprints (undated snapshot)', '14,448', 'TM06', 'Superseded by the current OSM clip.'],
      ['Rio_maior_border', 'Municipality boundary', '1', 'TM06', 'Superseded by CAOP 2025.'],
      ['CBD_point_TM06', 'City-centre reference point', '1', 'TM06', 'Keep; matches the field-survey notes.'],
    ], [2350, 2450, 600, 800, 2800]),
  caption('Table 1 — Layers held in DATA/GEO DATA/gis rio.gdb before this round.'),
  h2('2.2 Other spatial assets'),
  tbl(['Asset', 'Where', 'Notes'], [
    ['Two operational CSVs (collections 264,817 rows; sensors 1,048,575 rows)', 'DATA/XLS + Brain/03_db/parquet', 'Coordinates for every reading. The sensor file is cut at the Excel row limit (D1); the collections file carries 92 distinct Rota codes on 8.6% of rows and Km/weight totals on 23% — sparse but genuine route evidence.'],
    ['rio_maior.gpkg + 9 parquet layers + rio.duckdb', 'Brain/03_db', 'Cleaned mirrors of the gdb layers plus raw tables; regenerable by build_db.py.'],
    ['QGIS project + print template', 'DATA/QGIS Layout template', 'QGIS Thesis.qgz (EPSG:3763), now hosting the full styled library; Layout template.qpt for print maps.'],
    ['Maps M1–M3, pipeline figure F1', 'W1/04_outputs', 'Container network, population, sensor coverage; already used in R1-01.'],
  ], [2900, 2300, 3800]),
  caption('Table 2 — Other spatial assets already in the repository.'),
  img(path.resolve(__dirname, '../../04_outputs/maps/M1_container_network.png'), 480, 340),
  caption('Figure 1 — Container network over the road graph (W1 map M1).'),
  img(path.resolve(__dirname, '../../04_outputs/maps/M3_sensor_coverage.png'), 480, 340),
  caption('Figure 2 — Sensor coverage of the container fleet (W1 map M3).'),
];

// Section 3: downloaded
const s3 = [
  h1('3. What was downloaded on 13 August 2026'),
  p('GIS_DATA holds 6 GB across nine folders. National files are kept as archives; every working layer is clipped to the study-area boundary plus a 10 km buffer and reprojected to EPSG:3763. Sources, licences, and re-download URLs are in GIS_DATA/README.md; the endpoints and field-name pitfalls are also recorded in the project memory.'),
  tbl(['Category', 'Datasets (headline figures)', 'Source / licence'], [
    ['Administrative', 'CAOP 2025: municipality, 10 freguesias, national GeoPackage', 'DGT, CC-BY'],
    ['Roads & OSM', '20 clipped OSM layers — roads with class categories, buildings, land use, water, rail, POIs; national Geofabrik bundle retained', 'OSM contributors, ODbL'],
    ['Census & population', 'BGRI 2021 (572 subsections, N_INDIVIDUOS) and 2011 (896); INE 1 km grid; WorldPop 100 m; GHS-POP 2020/2025; NUTS II projections 2025–2100', 'INE / JRC / WorldPop'],
    ['Land use & zoning', 'COS 2018 v4 (63,528 polygons) and COS 2025 v1 (63,518), four class levels; CRUS PDM zoning (1,113 polygons)', 'DGT, CC-BY'],
    ['Terrain', 'DGT MDT 10 m 2024 (LiDAR DTM, national + clip) with derived hillshade and slope; Copernicus GLO-30 DSM', 'DGT / ESA'],
    ['Hydrography', 'APA geocoded river network; reservoirs; aquifer systems', 'APA, CC-BY'],
    ['Hazards & geology', 'PGRI flood zones (2nd cycle); rural fire hazard in 5 classes (101,218 polygons); LNEG faults 1:1M; lithology 1:50k (13 units)', 'APA / DGT / LNEG'],
    ['Utilities & energy', 'E-REDES: 230 MV/LV transformers with capacity and utilisation, 12,189 LV poles, substations, generation plants, EV and lighting tables; SRUP electricity grid lines (137)', 'E-REDES / DGT, CC-BY'],
    ['Planning constraints', 'REN, RAN, Natura 2000, protected areas, official road and rail networks', 'DGT SNIT'],
  ], [1700, 4900, 2400]),
  caption('Table 3 — Data downloaded into GIS_DATA on 13 August 2026.'),
];

// Section 4: gaps
const s4 = [
  h1('4. What is still missing'),
  h2('4.1 Obtainable, not yet downloaded'),
  p('Nothing in Table 4 blocks the pipeline. Each needs either a free registration or a manual step, and each has a stated trigger for bothering.'),
  tbl(['Dataset', 'Access', 'Trigger for acquiring'], [
    ['LiDAR MDT/MDS at 2 m and 50 cm', 'Free account at cdd.dgterritorio.gov.pt; ~200 km² per session; QGIS plugin installed', 'Only if a micro-siting chapter (sidewalk geometry, curb clearance) is written. User holds the account.'],
    ['Orthophotos 25–30 cm (2018, 2023)', 'WMS already usable in QGIS; bulk files via the same CDD account', 'Figure backgrounds; WMS suffices for now.'],
    ['EU-Hydro river network, CORINE', 'Free EU-Login at land.copernicus.eu', 'Only for cross-border comparability; APA and COS already cover the need.'],
    ['QAFI v4 active faults', 'Manual .rar download from IGME', 'Only if seismic siting risk enters the thesis. Unlikely.'],
    ['Flood depth and velocity grids', 'APA ArcGIS REST query (endpoint recorded)', 'If flood exposure of candidate sites is quantified rather than flagged.'],
  ], [2600, 3200, 3200]),
  caption('Table 4 — Data obtainable but not yet downloaded.'),
  h2('4.2 Must be requested — no public source exists'),
  p('These are the binding gaps. All four were flagged in R1-01; the route data gained urgency when inspection showed the gdb’s route fields empty and the collections CSV only 8.6% populated.'),
  tbl(['Data', 'Holder', 'Pipeline consequence if absent'], [
    ['Full sensor re-export (untruncated; defect D1)', 'Valorsul / sensor platform operator', 'Demand model runs on an arbitrary 344-container prefix instead of the instrumented fleet. Critical.'],
    ['Collection routes, schedules, vehicle GPS traces, per-event weights', 'Valorsul (recyclables circuits); Câmara Municipal (municipal fleet, machinery warehouse)', 'No validation of modelled routes against driven ones; the warehouse–transfer-station leg stays a computed placeholder. High.'],
    ['Staff shift structure', 'Same two institutions', 'Shift-length constraints in routing stay literature-based (Lopes 2014). Moderate.'],
    ['Water / wastewater / stormwater networks', 'Câmara Municipal de Rio Maior (direct operator)', 'None for the core pipeline; relevant only to utility-corridor siting arguments. Low.'],
  ], [3000, 2800, 3200]),
  caption('Table 5 — Data that must be requested from institutions.'),
];

// Section 5: relevance
const s5 = [
  h1('5. Relevance to the pipeline'),
  p('The rating asks one question per dataset: which pipeline stage breaks, weakens, or merely loses decoration if the dataset is removed. Stages: (i) demand estimation from fill rates, (ii) capacitated p-median siting, (iii) Monte Carlo scenarios and the stochastic model, (iv) routing extension, (v) writing and defence.'),
  tbl(['Dataset', 'Rating', 'Where it bites'], [
    ['464 container locations (gdb)', 'Critical', 'Every stage. The demand points and candidate sites.'],
    ['Sensor readings (CSV/parquet, pending D1 re-export)', 'Critical', 'Stage i is built on fill rates; D1 caps its validity today.'],
    ['Collections CSV (driver estimates, partial routes)', 'Critical', 'Stage i comparison chapter (driver vs sensor); only route evidence held.'],
    ['BGRI 2021 (official, with N_INDIVIDUOS)', 'Critical', 'Demand covariates and spatial weighting in stages i–ii; replaces the broken 222-polygon layer.'],
    ['OSM roads (clipped)', 'Critical', 'Network distances for stages ii and iv; straight-line distances are indefensible at defence.'],
    ['CAOP 2025 boundaries', 'High', 'Frame for every map and every clip; the analysis mask.'],
    ['MDT 10 m + slope', 'High', 'Road-gradient costs in stage iv; terrain covariate in stage i.'],
    ['COS 2018/2025 + CRUS zoning', 'High', 'Siting constraints and demand covariates in stage ii; land-use change between the 2018 and 2025 vintages is a defensible robustness check.'],
    ['Flood zones (PGRI)', 'Medium', 'Site-exclusion constraint in stage ii; one paragraph plus one map.'],
    ['E-REDES transformers and poles', 'Medium', 'Proxy for settlement intensity where census polygons are coarse; possible covariate.'],
    ['BGRI 2011, INE 1 km grid, WorldPop, GHS-POP', 'Medium', 'Cross-validation of the population surface; temporal context.'],
    ['Buildings (OSM)', 'Medium', 'Demand disaggregation weighting, if subsection polygons prove too coarse.'],
    ['River network, reservoirs, aquifers', 'Low', 'Cartographic context; no model role.'],
    ['Fire hazard, REN, RAN, Natura 2000', 'Low', 'Completeness of the siting-constraint narrative; rarely binding in the built-up areas where containers live.'],
    ['Faults, lithology, power plants, EV/lighting tables, NUTS II projections', 'Low', 'Background only.'],
  ], [3400, 1200, 4400]),
  caption('Table 6 — Relevance of each dataset to the pipeline stages.'),
];

const conclusion = [
  h1('Conclusion'),
  p('The public-data side of the thesis is closed. One acquisition round replaced every weak copy in the geodatabase with its authoritative source, added the terrain, hazard, zoning, and utility layers the pipeline can use, and left the whole library styled, clipped, documented, and reproducible from recorded URLs.'),
  p('What remains missing is exactly what was missing before, now with sharper evidence: the operator’s data. The gdb’s route fields are empty; the collections file carries route codes on fewer than one row in ten. Until the D1 re-export and the route request land, stage i runs on a truncated fleet and stage iv validates against nothing. The container locations, the two CSVs, the official BGRI, and the OSM road graph are the four assets the thesis cannot lose; everything else in the 6 GB is support.'),
];

const recommendations = [
  h1('Recommendations'),
  n1('Send the combined data request now — D1 re-export, routes, GPS, weights, shifts — to Valorsul and the Câmara in one letter each, reusing the R1-01 acquisition guide. Everything downstream of stage i waits on this.', true),
  n1('Adopt the official layers — retire the gdb census, boundary, land-use, and building layers from analysis; keep the gdb read-only as provenance. The 464-container layer stays canonical after an encoding repair.', true),
  n1('Enforce one CRS — EPSG:3763 everywhere; reproject the UTM 29N sensor layer on ingestion into DuckDB rather than in QGIS.', true),
  n1('Build the routable graph — convert the clipped OSM roads into a network with slope-weighted costs from the MDT; this gives the p-median stage real network distances and does not depend on the operator request.', true),
  n1('Freeze the library — add GIS_DATA checksums to Brain/06_manifest and pin the download date; the COS and CAOP vintages will change under the thesis otherwise.', true),
  n1('Defer fine LiDAR — revisit only if a micro-siting section is written; the account and procedure are documented.', true),
];

const references = [
  h1('References'),
  ...[
    'DGT — CAOP 2025, COS 2018 v4 / COS 2025 v1, CRUS, SRUP, MDT 10 m 2024. geo2.dgterritorio.gov.pt and ogcapi.dgterritorio.gov.pt. Licence CC-BY 4.0.',
    'INE — BGRI 2021/2011, census grid, síntese files, projections 2025–2100. mapas.ine.pt and ine.pt.',
    'APA — PGRI flood zones (2nd cycle), geocoded river network. sniambgeoviewer.apambiente.pt, CC-BY 4.0.',
    'LNEG — geological faults 1:1M, lithology 1:50k. ogcapi.lneg.pt.',
    'E-REDES — distribution-network open data. e-redes.opendatasoft.com, CC-BY 4.0.',
    'OpenStreetMap contributors — Geofabrik Portugal extract, 13 August 2026. download.geofabrik.de, ODbL.',
    'European Commission JRC — GHSL GHS-POP R2023A. jeodpp.jrc.ec.europa.eu, CC-BY 4.0.',
    'WorldPop — Portugal 100 m population 2020, UN-adjusted. data.worldpop.org, CC-BY 4.0.',
    'ESA / Airbus — Copernicus GLO-30 DEM. copernicus-dem-30m S3 bucket.',
    'Lopes, A. (2014) — Valorsul selective collection operations study, IST. Brain/02_notes/literature.',
    'Report R1-01 — Methodology Audit, this repository, W1/04_outputs/reports.',
  ].map(x => b(x)),
];

const appendices = [
  h1('Appendices'),
  h2('Appendix A — GIS_DATA folder sizes'),
  tbl(['Folder', 'Size', 'Content'], [
    ['04_elevation', '3.5 GB', 'MDT 10 m national zip + clips, hillshade, slope, Copernicus tiles'],
    ['01_osm', '822 MB', 'Geofabrik national zip + 20 clipped layers'],
    ['05_hydrography', '460 MB', 'River network national zip + clips, reservoirs, aquifers'],
    ['03_landuse', '386 MB', 'COS 2018/2025 extracts, CRUS'],
    ['02_census_population', '294 MB', 'BGRI 2021/2011, grids, rasters, projections'],
    ['00_admin_boundaries', '289 MB', 'CAOP 2025 + clip mask'],
    ['06_hazards_geology', '224 MB', 'Flood, fire hazard, faults, lithology'],
    ['09_srup_pdm_layers', '77 MB', 'REN, RAN, Natura, official networks'],
    ['07_utilities_energy', '28 MB', 'E-REDES layers, SRUP grid lines, power-plant DB'],
    ['08_other_projects', '—', 'Reserved'],
  ], [2400, 1200, 5400]),
  h2('Appendix B — Reproducibility endpoints'),
  b('DGT OGC API (GeoJSON, bbox filter, no auth): ogcapi.dgterritorio.gov.pt/collections — retry with page size ≤ 300 on HTTP 502.'),
  b('E-REDES filters: field con_name = "Rio Maior" on geo datasets, but DICO code "1414" in field concelho on apoios-baixa-tensao.'),
  b('INE municipal pattern: mapas.ine.pt/download/filesGPG/{year}/municipios/BGRI{year}_1414.zip.'),
  b('Clip mask: GIS_DATA/00_admin_boundaries/clip_mask_studyarea_buffer10km.gpkg (study area + 10 km, EPSG:3763).'),
  b('Full URL inventory: GIS_DATA/README.md.'),
];

// ---------- document ----------
const doc = new Document({
  numbering: { config: [...bullets.config, num] },
  styles: {
    default: { document: { run: { font: FONT, size: 22 } } },
    paragraphStyles: [
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { font: FONT, bold: true, size: 30, color: '1F2A1F' } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { font: FONT, bold: true, size: 25, color: '1F2A1F' } },
    ],
  },
  features: { updateFields: true },
  sections: [{
    properties: { page: { margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } },
    footers: {
      default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 18 })] })] }),
    },
    children: [
      ...cover, ...toc, ...listOfTables, ...listOfFigures, ...abbrev,
      ...execSummary, new Paragraph({ children: [new PageBreak()] }),
      ...s1, ...s2, ...s3, ...s4, ...s5,
      ...conclusion, ...recommendations, ...references, ...appendices,
    ],
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(OUT, buf);
  console.log('WROTE', OUT, buf.length, 'bytes');
});
