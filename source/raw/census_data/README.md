### Overview

1790 census population data used for calculating debt-per-capita figures and geographic analysis.

### Source

US Census Bureau historical data and derived population datasets. Contact: chrisliao (at) uchicago (dot) edu.

### When/where obtained & original form of files

CSV and XLS files obtained via Dropbox from the research team. Census data sourced from published 1790 census tabulations.

### Description

**`orig/`** — Original data files:
- `census.csv` — Census data (slave population figures). Used by: web app (maps.py).
- `countyPopulation.csv` — County-level population and FIPS data. Used by: web app (maps.py).
- `statepop.csv` — State-level population figures. Used by: web app (maps.py, pre_1790_map.py).
- `zip_code_database.xls` — ZIP code geographic reference database, used as city-county crosswalk for fuzzy matching. Used by: cleaning pipeline (standardize_geography.py).

**`docs/`** — Documentation about the dataset (to be populated).

### Terms of Use

Public domain (US Census data).

### Notes

`county_debt_total.csv` was previously here but moved to `output/derived/census/` — it is a derived file combining census and debt information, not raw data, and is not referenced by any active code.
