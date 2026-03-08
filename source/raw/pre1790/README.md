### Overview

Pre-1790 debt certificates — the original revolutionary war debts issued by the Continental Congress and individual states before Hamilton's 1790 federal assumption plan. 

### Source

Spreadsheets obtained via SPEOC dropbox. Contact: chrisliao (at) uchicago (dot) edu.

### When/where obtained & original form of files

XLSX spreadsheets transcribed from National Archives microfilm records, obtained via Dropbox from the research team. 

### Description

**`orig/`** — Certificate XLSX files (one per type/state):
- `loan_office_certificates_9_states.xlsx` — Loan office certificates across 9 states (CT, DE, MA, NH, NJ, NY, PA, RI, VA). 
- `liquidated_debt_certificates_CT.xlsx` — Connecticut state liquidated debt certificates.
- `liquidated_debt_certificates_DE.xlsx` — Delaware state liquidated debt certificates.
- `liquidated_debt_certificates_MA.xlsx` — Massachusetts state liquidated debt certificates.
- `liquidated_debt_certificates_NH.xlsx` — New Hampshire state liquidated debt certificates.
- `liquidated_debt_certificates_NJ.xlsx` — New Jersey state liquidated debt certificates.
- `liquidated_debt_certificates_NY.xlsx` — New York state liquidated debt certificates.
- `liquidated_debt_certificates_PA_stelle.xlsx` and `liquidated_debt_certificates_PA_story.xlsx` — Pennsylvania liquidated debt (Stelle ledger).
- `Marine_Liquidated_Debt_Certificates.xlsx` — Marine office certificates. 
- `Pierce_Certs_cleaned_2019.xlsx` — Pierce certificates (partially cleaned in 2019 by the research team).

**`corrections/`** — Manually curated correction lookup tables applied by the derived cleaning scripts. Organized by type (`name/`) and pipeline stage (`prescrape/`). Each file only contains rows where a correction is needed (identity mappings are omitted; scripts fall back to the original value when no entry is found):

`name/prescrape/` — Name corrections used by `combine_certificate_types.py`:
- `name_remove_words.csv` — Suffix and prefix stripping rules. `suffix` type removes the phrase from the end of the name; `prefix` type removes it from the start (e.g. `estate of`). Columns: `value`, `type`.
- `name_known_partners.csv` — Explicit name-to-person-list mappings. Each `original` (raw name or phrase) maps to a pipe-separated `new` value listing the canonical individual names. Used to resolve joint holders, companies, executors, and guardians. Columns: index, `original`, `new`.
- `name_unknown_partners.csv` — Institution names whose holders cannot be individually identified. Rows matching this list are flagged but not split. The script also writes newly detected suspicious names to `output/.../check/name_unknown_partners.csv` for human review. Column: `name`.
- `name_abbreviations.csv` — First-name abbreviation expansions (e.g. `Tho` → `Thomas`). Columns: `abbreviation`, `full_name`.
- `name_deceased_exceptions.csv` — Full names that should NOT trigger the deceased flag even though they contain a deceased keyword. Column: `name`.

### Terms of Use

Academic research use. Data derived from public National Archives records.
