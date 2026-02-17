### Post-1790 Continental Debt Cleaning Pipeline

Cleans and standardizes the post-1790 CD records from raw state XLSX files into a unified analysis-ready dataset.

### Code

- `standardize_geography.py` — Imports all state XLSX files via `cd_raw.csv` config, standardizes town/county/state names
- `clean_names_and_deduplicate.py` — Cleans and deduplicates holder names, handles company/partnership entities
- `integrate_scraped_data.py` — Integrates Ancestry scraper results (county lookups) into the cleaned dataset
- `aggregate_final_cd.py` — Final aggregation, merging, and output of the unified CD dataset
### Input

- `source/raw/post1790_cd/orig/{STATE}/*.xlsx` — Raw state XLSX files
- `source/raw/post1790_cd/docs/cd_raw.csv` — Import configuration
- `source/raw/post1790_cd/corrections/` — Manual correction files (town_fix, company_names_fix, occ_correction)

### Output

All output in `output/derived/post1790_cd/`:
- `final_data_CD.csv` — Final cleaned and aggregated dataset
- `aggregated_CD_post1790.csv`, `aggregated_CD_post1790_names.csv` — Aggregated variants
- `match_data_CD.csv` — Matching-ready dataset
- Various intermediate CSVs (name_list, name_agg, group_name_state, scrape files)
