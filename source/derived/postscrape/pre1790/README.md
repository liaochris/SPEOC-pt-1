# source/derived/postscrape/pre1790

Cleans and integrates Ancestry.com name-resolution results with the pre-cleaned pre-1790 debt data to produce the final cleaned debt dataset.

## Pipeline

```
output/derived/prescrape/pre1790/pre1790_cleaned.csv
output/derived/prescrape/pre1790/check/name_changes_list.csv
output/scrape/pre1790/ancestry_name_changes_raw.csv   ← produced manually by source/scrape/pre1790/scrape_name_resolution.py
    └─► integrate_ancestry_search.py → output/derived/postscrape/pre1790/ancestry_name_changes_clean.csv
                                     → output/derived/postscrape/pre1790/name_changes_david.csv
                                     → output/derived/postscrape/pre1790/final_agg_debt_cleaned.csv
```

## Scripts

| Script | Input | Output |
|---|---|---|
| `integrate_ancestry_search.py` | `pre1790_cleaned.csv`, `name_changes_list.csv`, `ancestry_name_changes_raw.csv` | `ancestry_name_changes_clean.csv`, `name_changes_david.csv`, `final_agg_debt_cleaned.csv` |

## Notes

- The scraping step (Ancestry.com search for name pairs) is handled separately by `source/scrape/pre1790/scrape_name_resolution.py`, which outputs `ancestry_name_changes_raw.csv`. That script requires Emory University Ancestry credentials and is not part of the automated SCons build.
- This script only processes already-scraped results: it deduplicates confirmed name changes, appends them to the manual corrections list, and applies them to `pre1790_cleaned.csv`.
