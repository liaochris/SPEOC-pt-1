# Data Dictionary — source/derived/prescrape/pre1790

## Pipeline overview

```
source/raw/pre1790/orig/*.xlsx (12 files)
    └─► aggregate_debt.py → output/derived/prescrape/pre1790/final_agg_debt.csv
            └─► combine_certificate_types.py → agg_debt_grouped.csv
                                              → name_changes.csv
                                              → name_fix_auto.csv
                    └─► find_similar_names.py → similar_names/{state}.csv
```

---

## output/derived/prescrape/pre1790/final_agg_debt.csv

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

**Source files:**
- `liquidated_debt_certificates_CT.xlsx` — Connecticut
- `liquidated_debt_certificates_PA_stelle.xlsx` — Pennsylvania (Stelle register)
- `liquidated_debt_certificates_PA_story.xlsx` — Pennsylvania (Story register)
- `liquidated_debt_certificates_RI.xlsx` — Rhode Island
- `loan_office_certificates_9_states.xlsx` — 9-state loan office (NH, MA, CT, NY, NJ, PA, DE, MD, VA)
- `Marine_Liquidated_Debt_Certificates.xlsx` — Marine department
- `liquidated_debt_certificates_NJ.xlsx` — New Jersey
- `liquidated_debt_certificates_NH.xlsx` — New Hampshire
- `liquidated_debt_certificates_NY.xlsx` — New York
- `liquidated_debt_certificates_DE.xlsx` — Delaware
- `liquidated_debt_certificates_MA.xlsx` — Massachusetts
- `Pierce_Certs_cleaned_2019.xlsx` — Pierce certificates (all states)

---

## output/derived/prescrape/pre1790/agg_debt_grouped.csv

Produced by `combine_certificate_types.py`. Cleaned and grouped version of `final_agg_debt.csv`. Name cleaning, organization detection, deceased flagging, and abbreviation expansion are applied. Rows for the same person holding debt across multiple adjacent entries are merged.

| Column | Type | Description |
|---|---|---|
| `row_id` | int | Unique row identifier |
| `org_index` | str | Pipe-joined list of source `org_index` values merged into this row |
| `final_agg_debt index` | str | Pipe-joined list of `final_agg_debt.csv` row indices |
| `organization?` | bool | True if the holder name was identified as an organization |
| `deceased?` | bool | True if a deceased marker was found in the name |
| `to whom due \| first name` | str | Cleaned first name |
| `to whom due \| last name` | str | Cleaned last name |
| `to whom due \| title` | str | Cleaned title |
| `amount \| dollars` | float | Sum of dollars across merged rows |
| `amount \| 90th` | float | Sum of 90ths across merged rows |
| *(other columns)* | | All other columns from `final_agg_debt.csv` (first value within group) |

**Cleaning cases applied (recorded in name_changes.csv):**
| Case | Rule |
|---|---|
| 2 | Company/partnership suffix stripped (` and co`, `corporation`, etc.) |
| 3 | Two-person joint entry split (` and ` in name) |
| 4 | Estate-of / heir-of prefix stripped |
| 5 | First name abbreviation expanded (e.g. `Tho` → `Thomas`) |
| 7 | Blank name field set to `UNDEFINED` |
| 8 | State-of / town-of prefix detected as org |
| 9 | Full name parsed from single field using HumanName |
| 12 | Deceased keyword removed from name |
| 14 | Organization detected by NLTK NER and split on `of` |

---

## output/derived/prescrape/pre1790/name_changes.csv

Produced by `combine_certificate_types.py`. Audit log of every name change made during cleaning.

| Column | Type | Description |
|---|---|---|
| `change_id` | int | Unique change identifier |
| `title_org` | str | Original title |
| `title_new` | str | New title |
| `first_name_org` | str | Original first name |
| `last_name_org` | str | Original last name |
| `first_name_new` | str | Corrected first name |
| `last_name_new` | str | Corrected last name |
| `cleaning case` | int | Cleaning rule code (see table above) |
| `file_loc` | str | Source XLSX file |
| `org_index` | int | Row index in source file |

---

## output/derived/prescrape/pre1790/name_fix_auto.csv

Produced by `combine_certificate_types.py`. Lookup table of manual corrections applied during interactive sessions (for company names and multi-person entries requiring human judgment). Used as a cache to avoid re-prompting for the same name.

| Column | Type | Description |
|---|---|---|
| `name` | str | Original name string (lookup key) |
| `new first name` | str | Corrected first name |
| `new last name` | str | Corrected last name |

---

## output/derived/prescrape/pre1790/similar_names/{state}.csv

Produced by `find_similar_names.py`. One file per state. Contains rows from `agg_debt_grouped.csv` that have at least one near-duplicate name within the same state (fuzzy score ≥ 90, excluding exact matches).

| Column | Type | Description |
|---|---|---|
| `row_id` | int | Unique row identifier |
| `full name` | str | Combined first + last name |
| `matches` | str | Stringified list of `(matched_name, score, index)` tuples |
| *(other columns)* | | All columns from `agg_debt_grouped.csv` |

**States covered:** all states except `cs` (Continental/general), `f` (federal), and `de` (Delaware).
