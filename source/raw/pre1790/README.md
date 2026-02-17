### Overview

Pre-1790 debt certificates — the original revolutionary war debts issued by the Continental Congress and individual states before Hamilton's 1790 federal assumption plan. There is no ASD/CD distinction for pre-1790 data.

### Source

National Archives and Records Administration (NARA). Transcribed from microfilm and original ledger records. Contact: chrisliao (at) uchicago (dot) edu.

### When/where obtained & original form of files

XLSX spreadsheets transcribed from National Archives microfilm records, obtained via Dropbox from the research team. Original transcriptions done during Summer 2021.

### Description

**Certificate XLSX files** (one per type/state):
- `loan_office_certificates_9_states.xlsx` — Loan office certificates across 9 states. Used by: web app (pre_1790_tab.py), cleaning pipeline.
- `liquidated_debt_certificates_{STATE}.xlsx` — State liquidated debt certificates (CT, DE, MA, NH, NJ, NY, PA_stelle, PA_story, RI). Used by: cleaning pipeline (via cd_raw.csv config).
- `Marine_Liquidated_Debt_Certificates.xlsx` — Marine office certificates. Used by: web app (pre_1790_tab.py).
- `Pierce_Certs_cleaned_2019.xlsx` — Pierce certificates (partially cleaned in 2019). Used by: web app (pre_1790_tab.py).

**`corrections/`** — Manually created correction and reference files:
- `corrections.json` — Manual name corrections applied during pre-1790 name cleaning, created by reviewing automated cleaning output against original documents
- `manual_corrections.csv` — Additional manual corrections for records identified during quality review
- `cd_info.csv` — Reference metadata for certificate types and their attributes
- `occupations_states.csv` — Occupation data by state for certificate holders

### Terms of Use

Academic research use. Data derived from public National Archives records.

### Notes

Covers four certificate types: loan office, state liquidated debt, Pierce, and marine. Pennsylvania has two separate ledgers (Stelle and Story). The correction files in `corrections/` are hand-curated reference data, not generated output.
