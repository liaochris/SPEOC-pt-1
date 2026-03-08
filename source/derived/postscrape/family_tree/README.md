# source/derived/postscrape/family_tree

Matches WikiTree-scraped family tree data against the post-1790 CD dataset to identify intergenerational debt holders.

## Pipeline

```
output/scrape/wikitree/results/ (edges, nodes, task_1.csv)
output/derived/postscrape/post1790_cd/final_data_CD.csv
    └─► match_candidates.py → output/derived/postscrape/family_tree/task_3_matches.csv
            └─► filter_matches.py → task_4_matches_filtered.csv
                    └─► drop_same_name.py → task_4_matches_filtered_nosamenames.csv
                            └─► finalize_matches.py → task_4_final.csv, task_4_review.csv
```

## Scripts

| Script | Description |
|---|---|
| `match_candidates.py` | Checks WikiTree children against post-1790 dataset by normalized name and state |
| `filter_matches.py` | Filters matches by birth year range, attaches parent IDs |
| `drop_same_name.py` | Removes rows where parent and child share the same name (likely artifacts) |
| `finalize_matches.py` | Final deduplication, multi-parent flagging, splits into clean and review sets |

## Output

All results stored in `output/derived/postscrape/family_tree/`:
- `task_3_matches.csv` — Raw post-1790 match results
- `task_4_matches_filtered.csv` — Birth-year filtered matches
- `task_4_matches_filtered_nosamenames.csv` — Same-name artifacts removed
- `task_4_final.csv` — Clean final matches
- `task_4_review.csv` — Multi-parent/uncertain cases for manual review
