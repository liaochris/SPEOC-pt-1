# Data Dictionary — source/derived/prescrape/post1790_cd

## Pipeline overview

```
source/raw/post1790_cd/orig/ (state XLSX files)
source/raw/post1790_cd/docs/cd_import_metadata.csv
source/raw/census_data/orig/zip_code_database.csv
    └─► standardize_geography.py → output/derived/prescrape/post1790_cd/aggregated_CD_post1790.csv
                                  → output/derived/prescrape/post1790_cd/check/town_occ_agg_check.csv
            └─► clean_names_and_deduplicate.py → aggregated_CD_post1790_names.csv
                                               → name_list.csv
                                               → check/company_research.csv
```

---

## output/derived/prescrape/post1790_cd/aggregated_CD_post1790.csv

Produced by `standardize_geography.py`. One row per person-record in the post-1790 continental debt registers. State XLSX files are loaded using parameters from `cd_import_metadata.csv`; triplicate name/town/occupation columns are reconciled into single values; unresolvable conflicts take the longest value.

| Column | Type | Description |
|---|---|---|
| `state_data` | str | State abbreviation of the source register (e.g. `CT`, `NY`, `PA`) |
| `state_data_index` | int | Row index within the state source file (1-based) |
| `6p_Dollar` | float | 6% stock principal (dollars) |
| `6p_Cents` | float | 6% stock principal (cents) |
| `6p_def_Dollar` | float | 6% deferred stock principal (dollars) |
| `6p_def_Cents` | float | 6% deferred stock principal (cents) |
| `3p_Dollar` | float | 3% stock principal (dollars) |
| `3p_Cents` | float | 3% stock principal (cents) |
| `town` | str | Town of residence (raw from register, may be county or state name) |
| `state` | str | State of residence (from register; may differ from `state_data` for transient holders) |
| `occupation` | str | Holder's occupation |
| `Name` | str | Pipe-joined set of name variants across triplicate columns (e.g. `John Smith \| Jonathan Smith`) |
| `First Name` | str | First name from primary record column |
| `Last Name` | str | Last name from primary record column |

**State coverage:** CT, GA, MD, NC, NH, NJ, NY, PA, RI, SC, MA, VA, DE

**Geographic reconciliation:** For states with triplicate data columns (most), town/state/occupation take the most frequent value across the three copies; conflicts are logged to `check/town_occ_agg_check.csv`. NY uses a separate single-column format.

---

## output/derived/prescrape/post1790_cd/check/town_occ_agg_check.csv

Produced by `standardize_geography.py`. Audit log of rows where the three copies of a field (town, state, or occupation) disagreed and the longest value was chosen.

| Column | Type | Description |
|---|---|---|
| `row_id` | int | Unique row identifier |
| `old` | str | Set of conflicting values |
| `new` | str | Value chosen (longest string) |
| `type` | str | Field name: `town`, `state`, or `occupation` |
| `state` | str | Source state abbreviation |

---

## output/derived/prescrape/post1790_cd/aggregated_CD_post1790_names.csv

Produced by `clean_names_and_deduplicate.py`. Extends `aggregated_CD_post1790.csv` with cleaned names and matched geographic information. Name cleaning normalizes company suffixes, splits joint entries, and applies the `company_names_fix.csv` correction lookup.

| Column | Type | Description |
|---|---|---|
| `row_id` | int | Unique row identifier |
| `Name_Fix` | str | Cleaned, standardized name (pipe-joined if multiple individuals) |
| `new_town` | str | Matched/standardized town name from crosswalk |
| `county` | str | Matched county name from zip code crosswalk |
| `new_state` | str | Matched state abbreviation |
| `country` | str | Country (always US for this dataset) |
| `name_type` | str | How the location was matched: `town` (direct city match) or `county` (direct county match) |
| *(all other columns)* | | All columns from `aggregated_CD_post1790.csv` |

---

## output/derived/prescrape/post1790_cd/name_list.csv

Produced by `clean_names_and_deduplicate.py`. Flat list of individual person names parsed out of the pipe-joined `Name_Fix` field. For joint holders (e.g. `John Smith | Jane Smith`), each person gets their own row with parsed first/last name.

| Column | Type | Description |
|---|---|---|
| `row_id` | int | Unique row identifier |
| `Name` | str | Original name string from `aggregated_CD_post1790.csv` |
| `Name_Fix` | str | Cleaned name string |
| `Fn_Fix` | str | Parsed first name |
| `Ln_Fix` | str | Parsed last name |
| `new_town` | str | Matched town name |
| `county` | str | Matched county |
| `new_state` | str | Matched state abbreviation |
| `country` | str | Country |
| `name_type` | str | Location match type (`town` or `county`) |

**Name parsing rules:**
- Dutch prefixes (`van de`, `de la`, `de`, `van`, `ten`, `del`) keep the last 2–3 tokens as the last name
- Suffixes `II`, `2nd` keep the last 2 tokens as the last name
- Otherwise last name = final token, first name = everything before it

---

## output/derived/prescrape/post1790_cd/check/company_research.csv

Produced by `clean_names_and_deduplicate.py`. Subset of records whose names still contain ` and ` after cleaning (potential joint holders or company names that need further review).

| Column | Type | Description |
|---|---|---|
| `row_id` | int | Unique row identifier |
| `Name` | str | Original name |
| `Name_Fix` | str | Cleaned name |
| `new_town` | str | Town |
| `county` | str | County |
| `new_state` | str | State |
| `country` | str | Country |
| `name_type` | str | Location match type |
