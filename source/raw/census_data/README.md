### Overview

1790 census population data used for calculating debt-per-capita figures and geographic analysis.

### Source

US Census Bureau historical data and derived population datasets. Contact: chrisliao (at) uchicago (dot) edu.

### When/where obtained & original form of files

CSV and XLS files obtained via Dropbox from the research team. Census data sourced from published 1790 census tabulations.

### Description

**`orig/`** — Original data files:
- `census.csv` — Census data (slave population figures by county). <!-- ORIGIN UNKNOWN: likely derived from 1790 US Census published tabulations. -->
- `countyPopulation.csv` — County-level population and FIPS data. <!-- ORIGIN UNKNOWN: likely derived from 1790 US Census with FIPS codes added. -->
- `statepop.csv` — State-level population figures (columns: State, Total Pop, Slave Pop) for 18 states/territories. Source: 1790 US Census. Cleaned version (trailing blank columns and empty rows removed).
- `zip_code_database.xls` — ZIP code geographic reference database, used as city-county crosswalk for fuzzy geographic matching. <!-- ORIGIN UNKNOWN: likely from free ZIP code database providers (e.g., UnitedStatesZipCodes.org). -->

**`docs/`** — Documentation about the dataset (to be populated).

### Terms of Use

Public domain (US Census data).

### Notes

`county_debt_total.csv` was previously here but moved to `output/derived/census/` — it is a derived file combining census and debt information, not raw data, and is not referenced by any active code.
