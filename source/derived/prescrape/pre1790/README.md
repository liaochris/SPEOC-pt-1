# source/derived/prescrape/pre1790

Cleans and aggregates raw pre-1790 debt certificates (loan office, liquidated debt, Pierce, marine) into a unified, name-cleaned dataset ready for Ancestry.com scraping.

## Pipeline

```
source/raw/pre1790/orig/*.xlsx (12 files)
source/raw/pre1790/corrections/*.csv
source/raw/pre1790/docs/*.csv
    └─► aggregate_debt.py         → output/derived/prescrape/pre1790/combined_pre1790.csv
                                  → check/name_dropped.csv
            └─► combine_certificate_types.py → agg_debt_grouped.csv
                                             → name_list.csv
                                             → check/name_changes_list.csv
                                             → check/name_unknown_partners.csv
                    └─► find_similar_names.py → similar_names/{state}.csv
```

## Scripts

### aggregate_debt.py

Loads 12 XLSX files using two raw layouts:
- **CleanTable format** (CT, PA-stelle, PA-story, RI, Marine): multi-level header rows, uniform column structure, processed by the shared `CleanTable()` helper. PA-story and Marine have extra column renaming after the standard clean.
- **Manual format** (NJ, NH, NY, DE, MA, Pierce): single-level headers with file-specific drop/rename dicts, handled by `LoadManualFile()`.
- **Loan-9**: single-header format covering 9 states; state is encoded as a numeric column mapped via `docs/state_num_map.csv`.

Column names are standardized across all files using `docs/column_renames.csv`. All files are concatenated and output as `combined_pre1790.csv`. Load order: loan office → liquidated debt → marine → Pierce. Rows where first or last name exceeds 10 tokens are dropped before cleaning and logged to `check/name_dropped.csv`.

### combine_certificate_types.py

Applies name cleaning to `combined_pre1790.csv` using a CSV-driven approach (aligned with the post-1790 pipeline):

1. **Word stripping** (`StripNameWords`): suffix rules (e.g. `and co`, `and others`) and prefix rules (e.g. `estate of`, `heir of`) from `corrections/name_remove_words.csv` are applied to the first name field.
2. **Known partner lookup** (`ApplyKnownPartners`): the cleaned first name is looked up in `corrections/name_known_partners.csv`. If found, the mapping expands the entry into one or more individual names (pipe-separated), which are then exploded into separate rows.
3. **Suspicious name detection** (`DetectSuspiciousNames`): after exploding, first names still containing ` and `, ` of `, more than 5 tokens, or starting with `state of`/`town of` are written to `check/name_unknown_partners.csv` for manual review.
4. **Full-name parsing** (`CleanSplitNames`): rows where first or last name is blank/NaN but the other field has ≥2 tokens are re-parsed via `nameparser.HumanName`; remaining blanks become `UNDEFINED`.
5. **Deceased + abbreviation normalization** (`NormalizeNameTokens`): deceased keywords (e.g. `deceased`, `dec'd`) are stripped and the `deceased?` flag set (exceptions in `corrections/name_deceased_exceptions.csv`); first-name abbreviations (e.g. `Tho` → `Thomas`) are expanded via `corrections/name_abbreviations.csv`.

After cleaning, consecutive rows with the same `full name` are collapsed by summing `amount | dollars` and `amount | 90th`. All changes are logged to `check/name_changes_list.csv`.

### find_similar_names.py

Uses rapidfuzz to find near-duplicate names within each state from `agg_debt_grouped.csv` (score ≥ 90, excluding exact matches and deduplicated). States `cs`, `f`, and `de` are excluded. One output file per state under `similar_names/`.

---

## output/derived/prescrape/pre1790/combined_pre1790.csv

Produced by `aggregate_debt.py`. One row per raw certificate entry across all 12 source XLSX files.

| Column | Type | Description |
|---|---|---|
| `org_file` | str | Source XLSX filename (e.g. `liquidated_debt_certificates_CT.xlsx`) |
| `org_index` | int | Row index within the source file (0-based) |
| `state` | str | State abbreviation (lowercase: `ct`, `pa`, `ri`, `nj`, `nh`, `ny`, `de`, `ma`, `va`, …) |
| `letter` | str | Register letter from the ledger |
| `date of the certificate \| month` | str/int | Month the certificate was issued |
| `date of the certificate \| day` | str/int | Day the certificate was issued |
| `date of the certificate \| year` | str/int | Year the certificate was issued |
| `to whom due \| title` | str | Title/honorific of primary holder (e.g. `Capt`, `Dr`) |
| `to whom due \| first name` | str | First name of primary certificate holder |
| `to whom due \| last name` | str | Last name of primary certificate holder |
| `to whom due \| title.1` | str | Title of secondary holder (for joint certificates) |
| `to whom due \| first name.1` | str | First name of secondary holder |
| `to whom due \| last name.1` | str | Last name of secondary holder |
| `time when the debt became due \| month` | str/int | Due date month |
| `time when the debt became due \| day` | str/int | Due date day |
| `time when the debt became due \| year` | str/int | Due date year |
| `amount \| dollars` | float | Principal amount (dollars) |
| `amount \| 90th` | float | Fractional cents (in 90ths of a dollar) |
| `amount \| 10th` | float | Fractional cents (in 10ths) — some files only |
| `amount \| 8th` | float | Fractional cents (in 8ths) — some files only |
| `amount in specie \| dollars` | float | Specie-equivalent value — PA story file only |
| `amount in specie \| cents` | float | Specie cents — PA story file only |
| `total dollars \| notes` | str | Notes column from Marine file |
| `total dollars \| notes.1` | str | Second notes column from Marine file |
| `line strike through? \| yes?` | int/str | 1 if the row is struck through (voided), blank otherwise |
| `line strike through? \| note` | str | Reason or note for the strikethrough |
| `notes` | str | General transcription notes |

**Source files (load order):**
1. `loan_office_certificates_9_states.xlsx` — 9-state loan office (NH, MA, CT, NY, NJ, PA, DE, MD, VA)
2. `liquidated_debt_certificates_CT.xlsx` — Connecticut
3. `liquidated_debt_certificates_PA_stelle.xlsx` — Pennsylvania (Stelle register)
4. `liquidated_debt_certificates_PA_story.xlsx` — Pennsylvania (Story register)
5. `liquidated_debt_certificates_RI.xlsx` — Rhode Island
6. `liquidated_debt_certificates_NJ.xlsx` — New Jersey
7. `liquidated_debt_certificates_NH.xlsx` — New Hampshire
8. `liquidated_debt_certificates_NY.xlsx` — New York
9. `liquidated_debt_certificates_DE.xlsx` — Delaware
10. `liquidated_debt_certificates_MA.xlsx` — Massachusetts
11. `Marine_Liquidated_Debt_Certificates.xlsx` — Marine department
12. `Pierce_Certs_cleaned_2019.xlsx` — Pierce certificates (all states)

---

## output/derived/prescrape/pre1790/check/name_dropped.csv

Produced by `aggregate_debt.py`. Rows dropped because first or last name exceeds 10 tokens (likely data errors or over-long transcription notes).

| Column | Type | Description |
|---|---|---|
| `row_id` | int | Unique row identifier |
| `org_file` | str | Source XLSX filename |
| `org_index` | int | Row index within the source file |
| `to whom due \| first name` | str | Original first name (too long to clean) |
| `to whom due \| last name` | str | Original last name (too long to clean) |

---

## output/derived/prescrape/pre1790/agg_debt_grouped.csv

Produced by `combine_certificate_types.py`. Cleaned version of `combined_pre1790.csv` with consecutive identical-name rows collapsed.

| Column | Type | Description |
|---|---|---|
| `row_id` | int | Unique row identifier |
| `org_index` | str | Pipe-joined list of source `org_index` values merged into this row |
| `final_agg_debt index` | str | Pipe-joined list of `combined_pre1790.csv` row indices |
| `organization?` | bool | True if the holder name was identified as an organization |
| `deceased?` | bool | True if a deceased marker was found in the name |
| `to whom due \| first name` | str | Cleaned first name |
| `to whom due \| last name` | str | Cleaned last name |
| `to whom due \| title` | str | Cleaned title |
| `amount \| dollars` | float | Sum of dollars across collapsed rows |
| `amount \| 90th` | float | Sum of 90ths across collapsed rows |
| *(other columns)* | | All other columns from `combined_pre1790.csv` (first value within group) |

**Cleaning case codes** (recorded in `check/name_changes_list.csv`):

| Case | Rule |
|---|---|
| 2 | Suffix or prefix stripped via `name_remove_words.csv` |
| 3 | Name expanded via `name_known_partners.csv` lookup |
| 5 | First name abbreviation expanded (e.g. `Tho` → `Thomas`) |
| 7 | Blank name field set to `UNDEFINED` |
| 9 | Full name parsed from single field using HumanName |
| 12 | Deceased keyword removed from name |

---

## output/derived/prescrape/pre1790/name_list.csv

Produced by `combine_certificate_types.py`. One row per unique (first name, last name, state) combination across all cleaned entries. Includes both names that were cleaned and those that were not.

| Column | Type | Description |
|---|---|---|
| `row_id` | int | Unique row identifier |
| `first name` | str | Cleaned first name |
| `last name` | str | Cleaned last name |
| `state` | str | State abbreviation |
| `title` | str | Cleaned title (first value within group) |
| `org_index` | str | Pipe-joined list of source `org_index` values for all entries with this name+state |
| `name_cleaned` | bool | True if any entry for this name+state had at least one cleaning step applied |

---

## output/derived/prescrape/pre1790/check/name_changes_list.csv

Produced by `combine_certificate_types.py`. Audit log of every name change made during cleaning.

| Column | Type | Description |
|---|---|---|
| `change_id` | int | Unique change identifier |
| `title_org` | str | Original title |
| `title_new` | str | New title after cleaning |
| `first_name_org` | str | Original first name |
| `last_name_org` | str | Original last name |
| `first_name_new` | str | Corrected first name |
| `last_name_new` | str | Corrected last name |
| `cleaning case` | int | Cleaning rule code (see table above) |
| `file_loc` | str | Source XLSX file |
| `org_index` | int | Row index in source file |

---

## output/derived/prescrape/pre1790/check/name_unknown_partners.csv

Produced by `combine_certificate_types.py`. Newly detected suspicious names (those still containing ` and `, ` of `, >5 tokens, or starting with `state of`/`town of`) that are not already in `corrections/name_unknown_partners.csv`. Review this file after each run and promote confirmed institutions to `corrections/name_unknown_partners.csv` or confirmed resolvable entries to `corrections/name_known_partners.csv`.

| Column | Type | Description |
|---|---|---|
| `row_id` | int | Unique row identifier |
| `to whom due \| first name` | str | Suspicious name string |
| `state` | str | State abbreviation |
| `org_file` | str | Source XLSX filename |
| `org_index` | int | Row index within the source file |

---

## output/derived/prescrape/pre1790/similar_names/{state}.csv

Produced by `find_similar_names.py`. One file per state. Contains rows from `agg_debt_grouped.csv` that have at least one near-duplicate name in the same state (fuzzy score ≥ 90, exact matches excluded).

| Column | Type | Description |
|---|---|---|
| `row_id` | int | Unique row identifier |
| `full name` | str | Combined first + last name |
| `matches` | str | Stringified list of `(matched_name, score, index)` tuples |
| *(other columns)* | | All columns from `agg_debt_grouped.csv` |

**States covered:** all states in `agg_debt_grouped.csv` except `cs` (Continental/general), `f` (federal), and `de` (Delaware).
