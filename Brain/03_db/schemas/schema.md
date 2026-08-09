---
name: db-schema
type: schema
---

# DuckDB schema — `Brain/03_db/duckdb/rio.duckdb`

All columns are loaded as VARCHAR. Typing is deferred until the
column semantics are confirmed. See
`Brain/02_notes/data_quality/csv-first-pass-profile.md`.

## `geo_cbd_point_tm06` — 1 rows

| # | Column | Type |
|---|---|---|
| 1 | `Id` | INTEGER |
| 2 | `Longitude` | FLOAT |
| 3 | `Latitude` | FLOAT |

## `geo_driver_464_unique_bins_for_gis_tm06` — 464 rows

| # | Column | Type |
|---|---|---|
| 1 | `OBJECTID_1` | DOUBLE |
| 2 | `idcontentor` | INTEGER |
| 3 | `Matricula_do_contentor` | VARCHAR |
| 4 | `Tipo_de_contentor` | VARCHAR |
| 5 | `Volume_do_tipo_de_contentor` | INTEGER |
| 6 | `description` | VARCHAR |
| 7 | `Distrito` | VARCHAR |
| 8 | `Concelho` | VARCHAR |
| 9 | `Freguesia` | VARCHAR |
| 10 | `Localidade` | VARCHAR |
| 11 | `Latitude` | DOUBLE |
| 12 | `Longitude` | DOUBLE |
| 13 | `Data_da_leitura` | TIMESTAMP_MS |
| 14 | `Tempo_de_leitura` | VARCHAR |
| 15 | `Enchimento` | INTEGER |
| 16 | `idrecolha` | DOUBLE |
| 17 | `Rota` | VARCHAR |
| 18 | `Data_de__nicio` | TIMESTAMP_MS |
| 19 | `Tempo_de__nicio` | VARCHAR |
| 20 | `Data_de_fim` | TIMESTAMP_MS |
| 21 | `Tempo_de_fim` | VARCHAR |
| 22 | `Km_totais` | DOUBLE |
| 23 | `Peso_total` | DOUBLE |
| 24 | `Field23` | INTEGER |
| 25 | `Field24` | INTEGER |
| 26 | `Field25` | INTEGER |
| 27 | `Field26` | INTEGER |
| 28 | `Field27` | INTEGER |
| 29 | `Field28` | INTEGER |
| 30 | `Field29` | INTEGER |
| 31 | `Field30` | INTEGER |
| 32 | `Field31` | INTEGER |
| 33 | `Field32` | INTEGER |
| 34 | `Field33` | INTEGER |
| 35 | `Field34` | INTEGER |
| 36 | `Field35` | INTEGER |
| 37 | `Field36` | INTEGER |
| 38 | `Field37` | INTEGER |
| 39 | `Field38` | INTEGER |
| 40 | `Field39` | INTEGER |
| 41 | `Field40` | INTEGER |
| 42 | `Field41` | INTEGER |
| 43 | `Field42` | INTEGER |
| 44 | `Field43` | INTEGER |
| 45 | `Field44` | INTEGER |
| 46 | `Field45` | INTEGER |
| 47 | `Field46` | INTEGER |
| 48 | `Field47` | INTEGER |
| 49 | `Field48` | INTEGER |
| 50 | `Field49` | INTEGER |
| 51 | `Field50` | INTEGER |
| 52 | `Field51` | INTEGER |
| 53 | `Field52` | INTEGER |
| 54 | `Field53` | INTEGER |
| 55 | `Field54` | INTEGER |
| 56 | `Field55` | INTEGER |
| 57 | `Field56` | INTEGER |
| 58 | `Field57` | INTEGER |
| 59 | `Field58` | INTEGER |
| 60 | `Field59` | INTEGER |
| 61 | `Field60` | INTEGER |
| 62 | `Field61` | INTEGER |
| 63 | `Field62` | INTEGER |
| 64 | `Field63` | INTEGER |
| 65 | `Field64` | INTEGER |
| 66 | `Field65` | INTEGER |
| 67 | `Field66` | INTEGER |
| 68 | `Field67` | INTEGER |
| 69 | `Field68` | INTEGER |
| 70 | `Field69` | INTEGER |
| 71 | `Field70` | INTEGER |
| 72 | `Field71` | INTEGER |
| 73 | `Field72` | INTEGER |
| 74 | `NEAR_FID` | DOUBLE |
| 75 | `NEAR_DIST` | DOUBLE |

## `geo_driver_rio_maior_tm06_new` — 147,319 rows

| # | Column | Type |
|---|---|---|
| 1 | `cont_id` | INTEGER |
| 2 | `Matricu_id` | VARCHAR |
| 3 | `tipo_cont` | VARCHAR |
| 4 | `vol_cont` | INTEGER |
| 5 | `descriptn` | VARCHAR |
| 6 | `Distrito` | VARCHAR |
| 7 | `Concelho` | VARCHAR |
| 8 | `Freguesia` | VARCHAR |
| 9 | `Localidad` | VARCHAR |
| 10 | `Latitude` | DOUBLE |
| 11 | `Longitude` | DOUBLE |
| 12 | `read_date` | VARCHAR |
| 13 | `read_time` | VARCHAR |
| 14 | `fill_level` | INTEGER |
| 15 | `idrecolha` | INTEGER |
| 16 | `Rota` | VARCHAR |
| 17 | `dt_start` | VARCHAR |
| 18 | `tm_start` | VARCHAR |
| 19 | `dt_end` | VARCHAR |
| 20 | `tm_end` | VARCHAR |
| 21 | `km_total` | INTEGER |
| 22 | `weight_tot` | INTEGER |
| 23 | `field_23` | VARCHAR |
| 24 | `field_24` | VARCHAR |
| 25 | `field_25` | VARCHAR |
| 26 | `field_26` | VARCHAR |
| 27 | `field_27` | VARCHAR |
| 28 | `field_28` | VARCHAR |
| 29 | `field_29` | VARCHAR |
| 30 | `field_30` | VARCHAR |
| 31 | `field_31` | VARCHAR |
| 32 | `field_32` | VARCHAR |
| 33 | `field_33` | VARCHAR |
| 34 | `field_34` | VARCHAR |
| 35 | `field_35` | VARCHAR |
| 36 | `field_36` | VARCHAR |
| 37 | `field_37` | VARCHAR |
| 38 | `field_38` | VARCHAR |
| 39 | `field_39` | VARCHAR |
| 40 | `field_40` | VARCHAR |
| 41 | `field_41` | VARCHAR |
| 42 | `field_42` | VARCHAR |
| 43 | `field_43` | VARCHAR |
| 44 | `field_44` | VARCHAR |
| 45 | `field_45` | VARCHAR |
| 46 | `field_46` | VARCHAR |
| 47 | `field_47` | VARCHAR |
| 48 | `field_48` | VARCHAR |
| 49 | `field_49` | VARCHAR |
| 50 | `field_50` | VARCHAR |
| 51 | `field_51` | VARCHAR |
| 52 | `field_52` | VARCHAR |
| 53 | `field_53` | VARCHAR |
| 54 | `field_54` | VARCHAR |
| 55 | `field_55` | VARCHAR |
| 56 | `field_56` | VARCHAR |
| 57 | `field_57` | VARCHAR |
| 58 | `field_58` | VARCHAR |
| 59 | `field_59` | VARCHAR |
| 60 | `field_60` | VARCHAR |
| 61 | `field_61` | VARCHAR |
| 62 | `field_62` | VARCHAR |
| 63 | `field_63` | VARCHAR |
| 64 | `field_64` | VARCHAR |
| 65 | `field_65` | VARCHAR |

## `geo_population_rio_maior_2021_polygon` — 222 rows

| # | Column | Type |
|---|---|---|
| 1 | `OBJECTID_1` | DOUBLE |
| 2 | `fid_` | INTEGER |
| 3 | `OBJECTID_2` | INTEGER |
| 4 | `BGRI2021` | VARCHAR |
| 5 | `DT21` | VARCHAR |
| 6 | `DTMN21` | VARCHAR |
| 7 | `DTMNFR21` | VARCHAR |
| 8 | `DTMNFRSEC2` | VARCHAR |
| 9 | `SECNUM21` | VARCHAR |
| 10 | `SSNUM21` | VARCHAR |
| 11 | `SECSSNUM21` | VARCHAR |
| 12 | `SUBSECCAO` | VARCHAR |
| 13 | `NUTS1` | VARCHAR |
| 14 | `NUTS2` | VARCHAR |
| 15 | `NUTS3` | VARCHAR |
| 16 | `N_EDIFICIO` | DOUBLE |
| 17 | `N_EDIFIC_1` | DOUBLE |
| 18 | `N_EDIFIC_2` | DOUBLE |
| 19 | `N_EDIFIC_3` | DOUBLE |
| 20 | `N_EDIFIC_4` | DOUBLE |
| 21 | `N_EDIFIC_5` | DOUBLE |
| 22 | `N_EDIFIC_6` | DOUBLE |
| 23 | `N_EDIFIC_7` | DOUBLE |
| 24 | `N_EDIFIC_8` | DOUBLE |
| 25 | `N_EDIFIC_9` | DOUBLE |
| 26 | `N_EDIFI_10` | DOUBLE |
| 27 | `N_EDIFI_11` | DOUBLE |
| 28 | `N_ALOJAMEN` | DOUBLE |
| 29 | `N_ALOJAM_1` | DOUBLE |
| 30 | `N_ALOJAM_2` | DOUBLE |
| 31 | `N_ALOJAM_3` | DOUBLE |
| 32 | `N_RHABITUA` | DOUBLE |
| 33 | `N_RHABIT_1` | DOUBLE |
| 34 | `N_RHABIT_2` | DOUBLE |
| 35 | `N_RHABIT_3` | DOUBLE |
| 36 | `N_AGREGADO` | DOUBLE |
| 37 | `N_ADP_1_OU` | DOUBLE |
| 38 | `N_ADP_3_OU` | DOUBLE |
| 39 | `N_NUCLEOS_` | DOUBLE |
| 40 | `N_NUCLEOS1` | DOUBLE |
| 41 | `N_INDIVIDU` | DOUBLE |
| 42 | `N_INDIVI_1` | DOUBLE |
| 43 | `N_INDIVI_2` | DOUBLE |
| 44 | `N_INDIVI_3` | DOUBLE |
| 45 | `N_INDIVI_4` | DOUBLE |
| 46 | `N_INDIVI_5` | DOUBLE |
| 47 | `N_INDIVI_6` | DOUBLE |
| 48 | `SHAPE_Leng` | DOUBLE |
| 49 | `Shape_Le_1` | DOUBLE |
| 50 | `POP_TOTAL` | DOUBLE |
| 51 | `Shape_Length` | DOUBLE |
| 52 | `Shape_Area` | DOUBLE |

## `geo_reprojected_gis_osm_building100` — 14,448 rows

| # | Column | Type |
|---|---|---|
| 1 | `fid_1` | DOUBLE |
| 2 | `osm_id` | VARCHAR |
| 3 | `code` | INTEGER |
| 4 | `fclass` | VARCHAR |
| 5 | `name` | VARCHAR |
| 6 | `type` | VARCHAR |
| 7 | `landuse` | VARCHAR |
| 8 | `Area` | INTEGER |
| 9 | `Longitude` | INTEGER |
| 10 | `Latitude` | INTEGER |
| 11 | `LU_Class` | VARCHAR |
| 12 | `Shape_Length` | DOUBLE |
| 13 | `Shape_Area` | DOUBLE |

## `geo_rio_maior_border` — 1 rows

| # | Column | Type |
|---|---|---|
| 1 | `OBJECTID_1` | DOUBLE |
| 2 | `OBJECTID_2` | INTEGER |
| 3 | `DICOFRE` | VARCHAR |
| 4 | `Freguesia` | VARCHAR |
| 5 | `Concelho` | VARCHAR |
| 6 | `Distrito` | VARCHAR |
| 7 | `Area_ha` | DOUBLE |
| 8 | `Des_Simpli` | VARCHAR |
| 9 | `Shape_Leng` | DOUBLE |
| 10 | `Shape_Le_1` | DOUBLE |
| 11 | `Shape_Length` | DOUBLE |
| 12 | `Shape_Area` | DOUBLE |

## `geo_rio_maior_landuse` — 1,046 rows

| # | Column | Type |
|---|---|---|
| 1 | `OBJECTID_1` | INTEGER |
| 2 | `ID` | INTEGER |
| 3 | `COS18n1_C` | VARCHAR |
| 4 | `COS18n1_L` | VARCHAR |
| 5 | `COS18n2_C` | VARCHAR |
| 6 | `COS18n2_L` | VARCHAR |
| 7 | `COS18n3_C` | VARCHAR |
| 8 | `COS18n3_L` | VARCHAR |
| 9 | `COS18n4_C` | VARCHAR |
| 10 | `COS18n4_L` | VARCHAR |
| 11 | `Area_ha` | DOUBLE |
| 12 | `Shape_Leng` | DOUBLE |
| 13 | `Shape_Le_1` | DOUBLE |
| 14 | `Shape_Length` | DOUBLE |
| 15 | `Shape_Area` | DOUBLE |

## `raw_collections` — 264,817 rows

| # | Column | Type |
|---|---|---|
| 1 | `idcontentor` | VARCHAR |
| 2 | `Matricula do contentor` | VARCHAR |
| 3 | `Tipo de contentor` | VARCHAR |
| 4 | `Volume do tipo de contentor` | VARCHAR |
| 5 | `description` | VARCHAR |
| 6 | `Distrito` | VARCHAR |
| 7 | `Concelho` | VARCHAR |
| 8 | `Freguesia` | VARCHAR |
| 9 | `Localidade` | VARCHAR |
| 10 | `Latitude` | VARCHAR |
| 11 | `Longitude` | VARCHAR |
| 12 | `Data da leitura` | VARCHAR |
| 13 | `Enchimento` | VARCHAR |
| 14 | `idrecolha` | VARCHAR |
| 15 | `Rota` | VARCHAR |
| 16 | `Data de ínicio` | VARCHAR |
| 17 | `Data de fim` | VARCHAR |
| 18 | `Km totais` | VARCHAR |
| 19 | `Peso total` | VARCHAR |

## `raw_sensors` — 1,048,575 rows

| # | Column | Type |
|---|---|---|
| 1 | `idcontentor` | VARCHAR |
| 2 | `Matricula do contentor` | VARCHAR |
| 3 | `Tipo de contentor` | VARCHAR |
| 4 | `Volume do tipo de contentor` | VARCHAR |
| 5 | `description` | VARCHAR |
| 6 | `Distrito` | VARCHAR |
| 7 | `Concelho` | VARCHAR |
| 8 | `Freguesia` | VARCHAR |
| 9 | `Localidade` | VARCHAR |
| 10 | `Latitude` | VARCHAR |
| 11 | `Longitude` | VARCHAR |
| 12 | `Data da leitura` | VARCHAR |
| 13 | `Enchimento` | VARCHAR |
| 14 | `idrecolha` | VARCHAR |
| 15 | `Rota` | VARCHAR |
| 16 | `Data de ínicio` | VARCHAR |
| 17 | `Data de fim` | VARCHAR |
| 18 | `Km totais` | VARCHAR |
| 19 | `Peso total` | VARCHAR |
