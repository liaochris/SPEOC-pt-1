### Overview

Historical geographic boundary shapefiles used for mapping debt distribution at the county and state level, primarily for the 1790 period.

### Source

- Atlas of Historical County Boundaries (Newberry Library): county boundaries
- NHGIS (National Historical Geographic Information System, IPUMS): state boundaries
- Esri / ArcGIS: modern state boundaries for reference

### When/where obtained & original form of files

Downloaded from respective sources. Shapefiles in standard ESRI format (.shp, .dbf, .shx, .prj).

### Description

**`orig/`** — Shapefile collections:
- `historicalcounties/` — 1790 county boundaries (COUNTY_1790_US_SL050_Coast_Clipped), clipped to coastline. Not used in active code (archive only).
- `historicalstates/` — Historical state/territory boundaries (US_HistStateTerr_Gen001), with date range attributes. Not used in active code (archive only).
- `stateshape/` — Modern US state boundaries (States_shapefile). Not used in active code (archive only).
- `stateshape_1790/` — 1790 state and county boundaries (US_States_and_Counties_WFL1). Used by: web app (maps.py).
- `nhgis_state_1790/` — NHGIS 1790 state boundaries (US_state_1790). Used by: web app (pre_1790_map.py).

**`docs/`** — Documentation about the dataset (to be populated).

### Terms of Use

NHGIS data subject to IPUMS terms of use. Atlas of Historical County Boundaries data is freely available for academic use. See individual source websites for full terms.

### Notes

Multiple overlapping boundary datasets exist for the 1790 period from different sources. The web app primarily uses `nhgis_state_1790/` for state-level maps and `stateshape_1790/` for county-level maps. The other three shapefile sets (historicalcounties, historicalstates, stateshape) are not referenced by active code.
