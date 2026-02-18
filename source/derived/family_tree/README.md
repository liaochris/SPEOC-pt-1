### Family Tree Matching and Filtering

Matches WikiTree-scraped family tree data against the post-1790 CD dataset to identify intergenerational debt holders.

### Code

- `match_candidates.py` — Checks WikiTree children against the post-1790 dataset by normalized name and state
- `filter_matches.py` — Filters matches by birth year range, attaches parent IDs
- `drop_same_name.py` — Removes rows where parent and child share the same name (likely artifacts)
- `finalize_matches.py` — Final deduplication, multi-parent flagging, splits into clean and review sets

### Input

- `output/scrape/wikitree/results/` — WikiTree scraping output (edges, nodes, task_1.csv)
- `output/derived/post1790_cd/` — Post-1790 cleaned dataset

### Output

Results stored in `output/scrape/wikitree/results/`:
- `task_3_matches.csv` — Post-1790 match results
- `task_4_matches_filtered.csv` — Birth-year filtered matches
- `task_4_final.csv` — Clean final matches
- `task_4_review.csv` — Multi-parent/uncertain cases for review
