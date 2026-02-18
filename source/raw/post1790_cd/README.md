### Overview

Post-1790 continental debt (CD) records by state — federal debt certificates issued after Hamilton's 1790 assumption plan. These record who held the new federal securities (6%, 3%, and deferred 6% stocks).

### Source

National Archives and Records Administration (NARA), T-series microfilm records. Contact: chrisliao (at) uchicago (dot) edu.

### When/where obtained & original form of files

XLSX spreadsheets transcribed from National Archives T-series microfilm, obtained via Dropbox from the research team. Each state's records come from a specific T-series roll (e.g., T694 for GA, T695 for NC, T652 for NH, T653 for RI, T698 for NJ).

### Description

**`orig/`** — State XLSX files (one per state, in state-abbreviation subfolders):
- `CT/CT_post1790_CD_ledger.xlsx`
- `GA/T694_GA_Loan_Office_CD.xlsx`
- `MD/MD_post1790_CD.xlsx`
- `NC/T695_R4_NC_CD.xlsx`
- `NH/T652_R6_New_Hampshire_CD.xlsx`
- `NJ/NJ_3_percent_stock_T698_R1_R2.xlsx`
- `NY/NY_1790_CD.xlsx`
- `PA/PA_post1790_CD.xlsx`
- `RI/T653_Rhode_Island_CD.xlsx`
- `SC/Post_1790_South_Carolina_CD.xlsx`
- `VA/VA_CD.xlsx`

All state XLSX files are used by the cleaning pipeline (source/derived/post1790_cd/) via cd_import_metadata.csv config.

**`corrections/`** — Manually created correction lookup tables applied by the derived cleaning scripts. Each file only contains rows where a correction is needed (identity mappings are omitted; scripts fall back to the original value when no entry is found):
- `town_fix.csv` — Town/geography name corrections (columns: town, state, new_town, county, new_state, country, name_type). Created by comparing cleaning output against the USGS GNIS place name database.
- `company_names_fix.csv` — Company/partnership name corrections that split joint entities into individual names (columns: index, original, new). Original entries may be `|`-delimited variants; new entries use `|` to separate multiple individual names.
- `occ_fix.csv` — Occupation field standardization mapping for non-trivial corrections only (columns: Original, Corrected, Additional Info). Maps raw occupation strings to standardized categories; when no entry is found the original value is kept.

**`docs/`** — Helper/reference files:
- `cd_import_metadata.csv` — Metadata mapping each state's raw XLSX file path, header row, Excel column ranges, and column count for automated import by the cleaning pipeline.

### Terms of Use

Academic research use. Data derived from public National Archives records.

### Notes

Each state's XLSX has a different layout (column positions, header rows, number of name/town/occupation columns). The `cd_import_metadata.csv` file encodes these differences so the cleaning pipeline can import all states programmatically. NY is handled separately in the code due to unique formatting (no occupation or town data). NJ only has 3% stock data (no 6% or deferred 6%).
