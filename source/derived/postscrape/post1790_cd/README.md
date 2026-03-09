# source/derived/postscrape/post1790_cd

Merges Ancestry.com scrape results with the pre-cleaned post-1790 CD data to produce the final analysis-ready dataset with county-level location data and aggregated debt totals.

## Pipeline

```
output/derived/prescrape/post1790_cd/geo_standardized_CD_post1790.csv
output/derived/prescrape/post1790_cd/check/name_changes_list.csv
output/scrape/ancestry_cd_scraper/
    └─► aggregate_final_cd.py → output/derived/postscrape/post1790_cd/final_data_CD.csv
                              → match_data_CD.csv
```

## Scripts

| Script | Input | Output |
|---|---|---|
| `aggregate_final_cd.py` | `geo_standardized_CD_post1790.csv`, `name_changes_list.csv`, `name_list_scraped.csv`, `scrape_results.csv`, correction CSVs | `final_data_CD.csv`, `match_data_CD.csv` |

## Notes

- Merges scraped county data with cleaned CD records. Groups persons by identity using Ancestry matches, fuzzy name matching, and `name_agg.csv`/`group_name_state.csv` manual corrections.
- Imputes county location for corporate partnerships from known partner locations.
- Applies occupation standardization using `occ_fix.csv`.
- Aggregates debt totals and computes share-adjusted amounts (6% face, 6% deferred face, 3% face; adjusted totals divide by number of co-holders).

See `pipeline_documentation.md` for detailed step-by-step pipeline description.
