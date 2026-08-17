# GIS_DATA — Free spatial data library for Rio Maior, Portugal

Assembled 2026-08-13 for the PhD thesis *Optimizing Recycling Waste Collection* (Rio Maior case study).
Municipality DICO code: **1414** (Santarém district) · NUTS3 Lezíria do Tejo · Area 273 km².
Working CRS: **ETRS89 / Portugal TM06 (EPSG:3763)**. All `*_riomaior10km*` files are clipped to the study-area boundary + 10 km buffer (`00_admin_boundaries/clip_mask_studyarea_buffer10km.gpkg`) and delivered in EPSG:3763.

## 00_admin_boundaries — DGT CAOP
| File | Content | Source |
|---|---|---|
| `CAOP_Continente_2025-gpkg.zip` + `CAOP_2025/` | Official admin boundaries, all Continente | DGT, CC-BY 4.0 |
| `municipio_riomaior_caop2025.geojson` | Rio Maior municipality polygon | DGT OGC API |
| `freguesias_riomaior_caop2025.geojson` | 10 freguesias | DGT OGC API |
| `clip_mask_studyarea_buffer10km.gpkg` | Study area + 10 km buffer (clip mask for everything) | derived |

## 01_osm — OpenStreetMap (© OpenStreetMap contributors, ODbL — attribution required)
| File | Content |
|---|---|
| `portugal-latest-free.shp.zip` | Full Geofabrik Portugal bundle (national backup) |
| `riomaior_10km/osm_roads…` | Road centerlines with `fclass` categories (motorway…track/path) |
| `riomaior_10km/osm_buildings_a…` | Building footprints |
| `riomaior_10km/` (18 more) | Land use, water, waterways, railways, places, POIs, traffic, transport, natural, protected areas, admin areas |

Note: OSM has no roads-as-polygons layer; road polygons exist only for `pedestrian`/`service` areas in `traffic_a`. For cartographic road casings use line symbology widths.

## 02_census_population — INE, JRC, WorldPop
| File | Content | Source |
|---|---|---|
| `BGRI2021_1414/` (.gpkg) | Census 2021 subsections + full attributes (572 polygons; pop field `N_INDIVIDUOS`) | INE, free |
| `BGRI2011_1414/` (.gpkg) | Census 2011 equivalent (896 polygons) for temporal comparison | INE |
| `C2021_SECCOES_1414_riomaior.zip` | Census sections (coarser) | INE |
| `INE_GRID1K_2021` + `ine_grid1km_riomaior10km.gpkg` | INE 1 km census grid | INE |
| `FS2021_sintese_subseccao_nacional_csv.zip` + `FS2021_variaveis_dicionario.csv` | Full national subsection stats table + variable dictionary | INE |
| `worldpop2020_riomaior10km.tif` | WorldPop 2020 UN-adjusted 100 m population raster | WorldPop, CC-BY |
| `ghs_pop_2020/2025_riomaior10km.tif` | GHSL GHS-POP 100 m epochs 2020 & 2025 | JRC, CC-BY |
| `INE_projecoes_2025_2100_NUTS2.xlsx` | Population projections 2025–2100. **Smallest level published is NUTS II** ("Oeste e Vale do Tejo") — no municipal projections exist; use Estimativas Anuais for municipal history | INE |

## 03_landuse — DGT
| File | Content | Source |
|---|---|---|
| `cos2018v4_studyarea.geojson` | COS 2018 v4 land use/cover 1:25k (63,528 polygons, 4 hierarchy levels) | DGT OGC API, CC-BY |
| `cos2025_studyarea.geojson` | COS 2025 v1 (newest) — same schema | DGT OGC API |
| `crus_riomaior_pdm.geojson` | Carta do Regime de Uso do Solo (PDM zoning, 1,113 polygons, `Classe_2021`/`Categoria_2021`) | DGT SNIT WFS, CC-BY |

National COS downloads (if full coverage ever needed): `https://geo2.dgterritorio.gov.pt/cos/S2/COS{2018|2023|2025}/…-gpkg.zip` (~850 MB each).

## 04_elevation
| File | Content | Source |
|---|---|---|
| `MDT10m2024_PTcontinente.zip` | **Official DTM 10 m 2024** (LiDAR-derived), whole Continente | DGT, CC-BY |
| `dgt_mdt10m_2024_riomaior10km.tif` | Clipped MDT 10 m (5–529 m) | derived |
| `…_hillshade.tif`, `…_slope_deg.tif` | Hillshade & slope (degrees) from MDT 10 m | derived |
| `Copernicus_DSM_30m_*.tif` + clipped | Copernicus GLO-30 **DSM** (surface incl. canopy/buildings) | ESA/Copernicus |

Finer data (50 cm / 2 m LiDAR MDT+MDS, LAZ point cloud): free but requires registration at `https://cdd.dgterritorio.gov.pt` (~200 km²/session cap). QGIS plugin: *DGT CDD Downloader*.

## 05_hydrography — APA
| File | Content |
|---|---|
| `rede_hidrografica_riomaior10km.gpkg` (+ national zip) | Official geocoded river network (troços) |
| `srup_albufeiras_studyarea.geojson` | Reservoirs |
| `srup_aquiferos_studyarea.geojson` | Aquifer systems |

EU-Hydro (Tagus basin) available at land.copernicus.eu with free EU-Login registration.

## 06_hazards_geology — APA, LNEG, SGIFR
| File | Content | Source |
|---|---|---|
| `apa_flood_zones_riomaior10km.gpkg` (+ national zip) | Flood extent zones, Floods Directive 2nd cycle (2022–2027) | APA PGRI, CC-BY |
| `srup_fire_hazard_studyarea.geojson` | Rural fire hazard classes (101k polygons, field `tipologia`: Muito Baixa→Muito Alta) | DGT/SGIFR |
| `lneg_faults_1M_bbox.geojson` | Geological faults 1:1M | LNEG OGC API |
| `lneg_lithology_50k_bbox.geojson` | Lithology 1:50k (13 units) | LNEG OGC API |

Flood depth/velocity grids: only via APA ArcGIS REST (`sniambgeoogc.apambiente.pt/getogc/rest/services/SNIAmb/Diretiva200760CE_2c/MapServer`). Active faults DB (QAFI v4): `http://info.igme.es/qafi/Download.aspx` (.rar, manual). No official vector for EC8 seismic zonation (PDF only).

## 07_utilities_energy — E-REDES (CC-BY), DGT, WRI
| File | Content |
|---|---|
| `eredes_postos_transformacao_riomaior.geojson` | 230 MV/LV distribution transformers with capacity, utilization, clients |
| `eredes_apoios_bt_riomaior.geojson` | 12,189 low-voltage poles |
| `eredes_subestacoes_carga.geojson` | HV/MV substations + load (national) |
| `eredes_centrais_geracao.geojson` | Grid-connected generation plants (national) |
| `eredes_ev_chargers_riomaior_TABLE.csv`, `eredes_iluminacao_publica_riomaior_TABLE.csv` | EV charging & public lighting (tabular, per freguesia — no geometry published) |
| `srup_rede_eletrica_studyarea.geojson` | Electric grid **lines** (137 features — E-REDES publishes no line geometry; this fills the gap) |
| `wri_global_power_plant_database.csv` | Global power plant DB (fallback) |

**Water / wastewater / stormwater: CLOSED.** Rio Maior networks are run directly by the Câmara Municipal (bulk supply: Águas do Vale do Tejo). No public GIS exists; ERSAR publishes indicators only. Options: request from CM Rio Maior directly, or digitize from PDM infrastructure plants (`dgterritorio.gov.pt/AcessoSimples/plantas.aspx?CONCNAME=RIO+MAIOR&TI=PDM&IDIGT=217`). No desalination/large STP data applies (inland municipality).

## 08_other_projects
Reserved for outputs of other projects (WSmartRoute etc.).

## 09_srup_pdm_layers — DGT SNIT (PDM servitudes & restrictions)
REN (ecological reserve), RAN (agricultural reserve), protected areas (Serras de Aire e Candeeiros NP edge), Natura 2000 ZEC, official road & railway networks.

## Not available / not applicable
- **Urban Atlas**: Rio Maior (~21k inh.) is not a Functional Urban Area — not covered. Use COS/CRUS.
- **Municipal projections**: don't exist below NUTS II.
- **Utility networks** (water/sewer/storm): closed, see above.
- **Orthophotos**: no free bulk download; WMS services work in QGIS: `https://ortos.dgterritorio.gov.pt/wms/ortosat2023` (30 cm, 2023) and `https://cartografia.dgterritorio.gov.pt/wms/ortos2018` (25 cm, 2018); files via CDD registration.

## QGIS
All layers are loaded and styled in `DATA/QGIS Layout template/QGIS Thesis.qgz`, grouped 0–8 mirroring these folders. Minor layers start unchecked — toggle in the layer tree.
