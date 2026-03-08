# source/derived — Cleaning Pipeline

Scripts that clean, transform, and combine raw data into analysis-ready datasets.

## Structure

```
source/derived/
├── prescrape/    — cleaning runs before web scraping (produces scraper inputs)
│   ├── pre1790/       aggregate_debt → combine_certificate_types → find_similar_names
│   └── post1790_cd/   standardize_geography → clean_names_and_deduplicate
└── postscrape/   — integration runs after web scraping (consumes scraper output)
    ├── pre1790/       integrate_ancestry_search
    ├── post1790_cd/   aggregate_final_cd
    └── family_tree/   match_candidates → filter_matches → drop_same_name → finalize_matches
```

## Outputs

Intermediate and final CSVs are stored in `output/derived/prescrape/` and `output/derived/postscrape/`, mirroring the source structure.

## Build

The `SConscript` in this directory registers all pipeline targets. Run from the repo root:
```
scons output/derived/prescrape/pre1790/agg_debt_grouped.csv
scons output/derived/prescrape/post1790_cd/geo_name_standardized_CD_post1790.csv
```
