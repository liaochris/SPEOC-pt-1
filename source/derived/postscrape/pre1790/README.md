# source/derived/postscrape/pre1790

Integrates Ancestry.com search results with the pre-cleaned pre-1790 debt data to disambiguate name spellings and produce the final cleaned debt dataset.

## Pipeline

```
output/derived/prescrape/pre1790/pre1790_cleaned.csv
output/scrape/pre1790_census_match/results/
    └─► integrate_ancestry_search.py → output/derived/postscrape/pre1790/final_agg_debt_cleaned.csv
                                     → ancestry_name_changes.csv
                                     → ancestry_name_changes_clean.csv
```

## Scripts

| Script | Input | Output |
|---|---|---|
| `integrate_ancestry_search.py` | `pre1790_cleaned.csv`, `similar_names/{state}.csv`, Ancestry scrape results | `final_agg_debt_cleaned.csv`, `ancestry_name_changes.csv`, `ancestry_name_changes_clean.csv` |

## Notes

- Uses phonetic and fuzzy string matching to identify similar names within each state, then validates them against Ancestry.com search results.
- If both name variants appear in Ancestry results with matches, the canonical spelling is selected. If neither matches, entries remain separate.
- Runtime is long due to Ancestry.com access (>200k debt entries).
- This script still uses notebook-style formatting and needs `Main()` refactoring (Step 2.4).
