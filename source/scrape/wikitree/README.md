### WikiTree Scraper

Searches WikiTree for historical persons matching pre-1790 debt certificate holders, fetches their family trees, and collects biographical data via the WikiTree API.

### Pipeline

1. `search_wikitree_candidates.py` (task 1) — For each unique person in the cleaned loan office certificates, searches WikiTree for matching profiles filtered by birth year range and state. Writes all candidates to `task_1.csv`.
2. `build_family_graph.py` (task 2) — For each candidate profile, fetches children via the WikiTree API. Builds a graph of parent→child edges (`edges_task_2.json`) and person nodes (`nodes_task_2.json`).
3. `get_bios.py` — Fetches full biographical profiles from WikiTree for all task 1 candidates. Writes one JSON record per line to `wikitree_bios.jsonl`. Supports resume via deduplication.

### Core Module

`wikitree.py` — WikiTree API client. Provides `search_candidates_for_name()`, `get_profile()`, `get_descendants()`, and related functions.

### Tests

```bash
pytest source/scrape/wikitree/
```

Unit tests mock the API. Integration tests (for real API calls) are included but require network access.

### Notes

Matching/filtering logic (tasks 3-4) lives in `source/derived/family_tree/`. Analysis code lives in `source/analysis/family_tree_analysis/`.
