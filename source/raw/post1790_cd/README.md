### Overview

Post-1790 continental debt (CD) records by state — federal debt certificates issued after Hamilton's 1790 assumption plan. These record who held the new federal securities (6%, 3%, and deferred 6% stocks).

### Source

Spreadsheets obtained via SPEOC dropbox. Contact: chrisliao (at) uchicago (dot) edu.

### When/where obtained & original form of files

XLSX spreadsheets transcribed from National Archives T-series microfilm, obtained via Dropbox from the research team.

### Description

**`orig/`** — State XLSX files (one per state, in state-abbreviation subfolders), named `{STATE}/{STATE}_CD.xlsx`:
- `CT/CT_CD.xlsx`
- `GA/GA_CD.xlsx`
- `MD/MD_CD.xlsx`
- `NC/NC_CD.xlsx`
- `NH/NH_CD.xlsx`
- `NJ/NJ_CD.xlsx`
- `NY/NY_CD.xlsx`
- `PA/PA_CD.xlsx`
- `RI/RI_CD.xlsx`
- `SC/SC_CD.xlsx`
- `VA/VA_CD.xlsx`

All state XLSX files except NJ and NY are imported by the cleaning pipeline (source/derived/prescrape/post1790_cd/) via `docs/cd_import_metadata.csv`. NY is handled separately due to unique formatting (no occupation or town data). NJ only has 3% stock data (no 6% or deferred 6%).

**`corrections/`** — Manually created correction lookup tables applied by the derived cleaning scripts. Organized by type (`geo/`, `name/`, `occ/`) and pipeline stage (`prescrape/`, `postscrape/`). Each file only contains rows where a correction is needed (identity mappings are omitted; scripts fall back to the original value when no entry is found):

`geo/prescrape/` — Geography corrections used by `standardize_geography.py`:
- `geo_town_replacements.csv` — String substitutions applied to raw town names before automatic matching (columns: state, old, new, sort_order). `sort_order` groups substitutions into numbered passes (1, 2, 3) applied in sequence — all pass-1 substitutions run before pass-2 substitutions, allowing later passes to depend on the results of earlier ones.
- `geo_town_fix.csv` — Manual overrides for towns that could not be matched automatically or were matched incorrectly (columns: town, state, new_town, county, new_state, country, geo_level). Created by comparing output against the USGS GNIS place name database.
- `geo_person_state.csv` — Overrides the assigned state for specific individuals based on historical data (columns: name_contains, new_state).
- `geo_conflict_splits.csv` — Records where a single geographic field encodes multiple conflicting values that must be split (columns: state, type, val1, val2).

`name/prescrape/` — Name corrections used by `clean_names_and_deduplicate.py`:
- `name_known_partners.csv` — Splits company/partnership names into individual names using `|` separator (columns: index, original, new). List is derived from name context and historical research. 
- `name_remove_words.csv` — Words or phrases to strip from names during cleaning (columns: value, type).
- `name_unknown_partners.csv` — Group or institutional names that cannot be mapped to individual partners; excluded from splitting (columns: name).

`name/postscrape/` — Name corrections used by `aggregate_final_cd.py`:
- `name_agg.csv` — Merges misspellings or variants that refer to the same person into a canonical form (columns: original, new, location).
- `group_name_state.csv` — Maps group/company names to the state they operated in for disambiguation (columns: Group Name, Group State).

`occ/postscrape/` — Occupation corrections used by `aggregate_final_cd.py`:
- `occ_fix.csv` — Maps raw occupation strings to standardized categories (columns: Original, Corrected, Additional Info).

**`docs/`** — Helper/reference files:
- `cd_import_metadata.csv` — Metadata mapping each state's raw XLSX file path, header row, Excel column ranges, and column count for automated import by the cleaning pipeline.

### Terms of Use

Academic research use. Data derived from public National Archives records.
