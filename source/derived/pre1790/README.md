### Pre-1790 Certificate Cleaning Pipeline

Cleans and processes pre-1790 debt certificates (loan office, liquidated debt, Pierce, marine) into analysis-ready datasets.

### Code

- `combine_certificate_types.py` — Combines all certificate types into a unified dataset
- `clean_names.py` — Cleans and standardizes holder names
- `clean_names_individual.py` — Individual-level name cleaning and corrections
- `clean_imperfections.py` — Fixes data imperfections and formatting issues
- `find_similar_names.py` — Identifies potentially duplicate names across states using string similarity
- `integrate_ancestry_search.py` — Integrates Ancestry search results for name disambiguation
- `aggregate_debt.py` — Aggregates debt by holder
- `aggregate_debt_alternate.py` — Alternative aggregation approach
### Input

- `source/raw/pre1790/orig/*.xlsx` — Raw certificate XLSX files
- `source/raw/pre1790/corrections/name_fix.csv` — Manual name corrections

### Output

All output in `output/derived/pre1790/`:
- `loan_office_certificates_cleaned.csv` — Cleaned loan office certificates
- `liquidated_debt_certificates_combined.csv` — Combined liquidated debt certificates
- `final_agg_debt.csv` — Final aggregated debt
- Various intermediate CSVs (name changes, similar names, aggregation intermediates)
