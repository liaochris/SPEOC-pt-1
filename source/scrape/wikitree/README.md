### WikiTree Scraper

Searches WikiTree for historical persons matching pre-1790 debt certificate holders, fetches their family trees, and collects biographical data via the WikiTree API.

### Code

- `wikitree.py` — WikiTree API client (`search_candidates_for_name()`, `get_profile()`, `get_descendants()`)
- `search_wikitree_candidates.py` — Searches WikiTree for matching profiles filtered by birth year range and state
- `build_family_graph.py` — Fetches children for each candidate, builds parent→child edge graph
- `get_bios.py` — Fetches full biographical profiles, supports resume via deduplication
- `tests/` — Unit tests (mocked API) and integration tests (live API)

### Input

- `output/scrape/wikitree/data/loan_office_certificates_cleaned.csv`
- `output/scrape/wikitree/data/post_1790.csv`

### Output

All output in `output/scrape/wikitree/`:
- `results/task_1.csv` — WikiTree candidate matches
- `results/edges_task_2.json` — Parent→child edges
- `results/nodes_task_2.json` — Person nodes
- `wikitree_bios.jsonl` — Full biographical profiles (one JSON per line)

### Notes

Matching/filtering logic (tasks 3-4) lives in `source/derived/family_tree/`. Analysis code lives in `source/analysis/family_tree_analysis/`.
