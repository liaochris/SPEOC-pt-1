### Overview

Pre-1790 debt certificates — the original revolutionary war debts issued by the Continental Congress and individual states before Hamilton's 1790 federal assumption plan. There is no ASD/CD distinction for pre-1790 data.

### Source

National Archives and Records Administration (NARA). Transcribed from microfilm and original ledger records. Contact: chrisliao (at) uchicago (dot) edu.

### When/where obtained & original form of files

XLSX spreadsheets transcribed from National Archives microfilm records, obtained via Dropbox from the research team. Original transcriptions done during Summer 2021.

### Description

**`orig/`** — Certificate XLSX files (one per type/state):
- `loan_office_certificates_9_states.xlsx` — Loan office certificates across 9 states (CT, DE, MA, NH, NJ, NY, PA, RI, VA). Source: NARA loan office ledgers.
- `liquidated_debt_certificates_CT.xlsx` — Connecticut state liquidated debt certificates. Source: NARA microfilm.
- `liquidated_debt_certificates_DE.xlsx` — Delaware state liquidated debt certificates. Source: NARA microfilm.
- `liquidated_debt_certificates_MA.xlsx` — Massachusetts state liquidated debt certificates. Source: NARA microfilm.
- `liquidated_debt_certificates_NH.xlsx` — New Hampshire state liquidated debt certificates. Source: NARA microfilm.
- `liquidated_debt_certificates_NJ.xlsx` — New Jersey state liquidated debt certificates. Source: NARA microfilm.
- `liquidated_debt_certificates_NY.xlsx` — New York state liquidated debt certificates. Source: NARA microfilm.
- `liquidated_debt_certificates_PA_stelle.xlsx` — Pennsylvania liquidated debt (Stelle ledger). Source: NARA microfilm.
- `liquidated_debt_certificates_PA_story.xlsx` — Pennsylvania liquidated debt (Story ledger). Source: NARA microfilm.
- `liquidated_debt_certificates_RI.xlsx` — Rhode Island state liquidated debt certificates. Source: NARA microfilm.
- `Marine_Liquidated_Debt_Certificates.xlsx` — Marine office certificates. <!-- ORIGIN UNKNOWN: columns include name, amount, date, state — likely NARA Marine Records collection. -->
- `Pierce_Certs_cleaned_2019.xlsx` — Pierce certificates (partially cleaned in 2019 by the research team). <!-- ORIGIN UNKNOWN: partially cleaned pre-existing dataset. -->

**`corrections/`** — Manually created correction lookup tables applied by the derived cleaning scripts. Each file only contains rows where a correction is needed; scripts fall back to the original value when no entry is found:
- `name_fix.csv` — Manual corrections for company/partnership and individual name records identified during quality review. Splits joint ownership entries (e.g., "Clark and Nightingale" → "Joseph Innes Clark | Joseph Nightingale") and standardizes spelling/capitalization. Columns: index, original, new. **Note:** the cleaning scripts also write updated corrections back to this file during the cleaning run — do not edit manually while the pipeline is running.

### Terms of Use

Academic research use. Data derived from public National Archives records.

### Notes

Covers four certificate types: loan office, state liquidated debt, Pierce, and marine. Pennsylvania has two separate ledgers (Stelle and Story). Pre-1790 data is read directly by the cleaning scripts (not via a metadata config file — unlike post-1790 CD which uses cd_import_metadata.csv).
