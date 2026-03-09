# source/derived/postscrape/family_tree

Matches WikiTree-scraped family tree data against the post-1790 CD dataset to identify intergenerational debt holders.

## Pipeline

```
output/scrape/wikitree/ (family_graph_edges.json, family_graph_nodes.json, candidates.csv)
output/derived/postscrape/post1790_cd/final_data_CD.csv
    └─► match_candidates.py → output/derived/postscrape/family_tree/candidate_matches.csv
            └─► filter_matches.py → filtered_matches.csv
                    └─► drop_same_name.py → filtered_matches_no_same_name.csv
                            └─► finalize_matches.py → final_matches.csv, review_matches.csv
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
- `candidate_matches.csv` — Raw post-1790 match results
- `filtered_matches.csv` — Birth-year filtered matches
- `filtered_matches_no_same_name.csv` — Same-name artifacts removed
- `final_matches.csv` — Clean final matches
- `review_matches.csv` — Multi-parent/uncertain cases for manual review
