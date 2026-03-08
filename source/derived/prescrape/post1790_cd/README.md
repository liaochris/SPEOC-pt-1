# source/derived/prescrape/post1790_cd

Imports and standardizes post-1790 continental debt (CD) records from state XLSX files into a unified, geography-matched, name-cleaned dataset ready for Ancestry.com scraping.

## Pipeline

```
source/raw/post1790_cd/orig/{STATE}/*.xlsx
source/raw/post1790_cd/docs/cd_import_metadata.csv
source/raw/census_data/orig/zip_code_database.csv
    └─► standardize_geography.py → output/derived/prescrape/post1790_cd/geo_standardized_CD_post1790.csv
                                  → check/town_occupation_aggregation_list.csv
                                  → check/town_changes_list.csv
            └─► clean_names_and_deduplicate.py → geo_name_standardized_CD_post1790.csv
                                               → check/name_changes_list.csv
                                               → check/companies_unidentified_partners.csv
                                               → check/name_town_conflicts_list.csv
```

## Scripts

### standardize_geography.py

Loads each state's XLSX file using import parameters from `cd_import_metadata.csv` (sheet names, header rows, column mappings). Most states have triplicate data columns — three side-by-side copies of name/town/occupation — reconciled by majority vote; ties take the longest value. Conflicts are logged to `check/town_occupation_aggregation_list.csv`. NY uses a single-column format and is handled separately.

Town names are matched to counties via direct lookup against the ZIP code crosswalk, then fuzzy matching. Manual overrides for unresolvable or mismatched towns are loaded from `corrections/geo/prescrape/geo_town_fix.csv`. State-specific string replacements (e.g. abbreviations, alternate spellings) are loaded from `corrections/geo/prescrape/geo_town_replacements.csv`. Match decisions are logged to `check/town_changes_list.csv`.

### clean_names_and_deduplicate.py

Strips company/partnership suffixes and end-anchors (loaded from `corrections/name/prescrape/name_remove_words.csv`) from raw name strings. Applies `corrections/name/prescrape/name_known_partners.csv` to expand known company names into their individual partner names (pipe-separated). Institutional names (loaded from `corrections/name/prescrape/name_unknown_partners.csv`) are excluded from individual-level splitting. After cleaning, names still containing ` and ` are flagged to `check/companies_unidentified_partners.csv` for manual review.

Produces `check/name_changes_list.csv`: a flat individual-level list with parsed first/last names (one row per person per unique name+location combination). Also produces `check/name_town_conflicts_list.csv`: rows where the parsed last name matches a known town or state name, flagging likely over-stripping.

---

## output/derived/prescrape/post1790_cd/geo_standardized_CD_post1790.csv

Produced by `standardize_geography.py`. One row per person-record in the post-1790 continental debt registers.

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
| `new_town` | str | Matched/standardized town name from crosswalk |
| `county` | str | Matched county name from ZIP code crosswalk |
| `new_state` | str | Matched state abbreviation |
| `country` | str | Country (always US for this dataset) |
| `geo_level` | str | How the location was matched: `town`, `county`, `state`, or `country` |

**State coverage:** CT, GA, MD, NC, NH, NJ, NY, PA, RI, SC, MA, VA, DE

---

## output/derived/prescrape/post1790_cd/check/town_occupation_aggregation_list.csv

Produced by `standardize_geography.py`. Audit log of rows where the three copies of a field (town, state, or occupation) disagreed and the longest value was chosen.

| Column | Type | Description |
|---|---|---|
| `row_id` | int | Unique row identifier |
| `old` | str | Set of conflicting values |
| `new` | str | Value chosen (longest string) |
| `type` | str | Field name: `town`, `state`, or `occupation` |
| `state` | str | Source state abbreviation |

---

## output/derived/prescrape/post1790_cd/check/town_changes_list.csv

Produced by `standardize_geography.py`. One row per unique (state, town) pair processed, logging how the town string was matched. Later log entries supersede earlier ones for the same town.

| Column | Type | Description |
|---|---|---|
| `row_id` | int | Unique row identifier |
| `state` | str | Source state abbreviation |
| `town_original` | str | Raw town string from the register |
| `town_matched` | str | Standardized town name after matching |
| `match_method` | str | How the match was resolved (e.g. `direct`, `fuzzy`, `manual_override`, `unmatched`) |

---

## output/derived/prescrape/post1790_cd/geo_name_standardized_CD_post1790.csv

Produced by `clean_names_and_deduplicate.py`. Extends `geo_standardized_CD_post1790.csv` with cleaned name field.

| Column | Type | Description |
|---|---|---|
| `row_id` | int | Unique row identifier |
| `Name_Fix` | str | Cleaned, standardized name (pipe-joined if multiple individuals) |
| *(all other columns)* | | All columns from `geo_standardized_CD_post1790.csv` |

---

## output/derived/prescrape/post1790_cd/check/name_changes_list.csv

Produced by `clean_names_and_deduplicate.py`. Flat list of individual person names parsed out of the pipe-joined `Name_Fix` field. For joint holders (e.g. `John Smith | Jane Smith`), each person gets their own row with parsed first/last name.

| Column | Type | Description |
|---|---|---|
| `row_id` | int | Unique row identifier |
| `Name` | str | Original name string from `geo_standardized_CD_post1790.csv` |
| `Name_Fix` | str | Cleaned name string |
| `Fn_Fix` | str | Parsed first name |
| `Ln_Fix` | str | Parsed last name |
| `new_town` | str | Matched town name |
| `county` | str | Matched county |
| `new_state` | str | Matched state abbreviation |
| `country` | str | Country |
| `geo_level` | str | Location match type (`town`, `county`, `state`, or `country`) |

**Name parsing rules:**
- Dutch prefixes (`van de`, `de la`, `de`, `van`, `ten`, `del`) keep the last 2–3 tokens as the last name
- Suffixes `II`, `2nd` keep the last 2 tokens as the last name
- Otherwise last name = final token, first name = everything before it

---

## output/derived/prescrape/post1790_cd/check/companies_unidentified_partners.csv

Produced by `clean_names_and_deduplicate.py`. Records whose names still contain ` and ` after cleaning — potential joint holders or company names needing further partner identification.

| Column | Type | Description |
|---|---|---|
| `row_id` | int | Unique row identifier |
| `Name` | str | Original name |
| `Name_Fix` | str | Cleaned name |
| `new_town` | str | Town |
| `county` | str | County |
| `new_state` | str | State |
| `country` | str | Country |
| `geo_level` | str | Location match type |

---

## output/derived/prescrape/post1790_cd/check/name_town_conflicts_list.csv

Produced by `clean_names_and_deduplicate.py`. Rows where the parsed last name (`Ln_Fix`) matches a known town or state name from the crosswalk — flags likely over-stripping or remaining geographic tokens in name strings.

| Column | Type | Description |
|---|---|---|
| `row_id` | int | Unique row identifier |
| `Name_Fix` | str | Cleaned name string |
| `Fn_Fix` | str | Parsed first name |
| `Ln_Fix` | str | Parsed last name (matched a geographic name) |
| `new_town` | str | Matched town for this record |
| `new_state` | str | Matched state for this record |
