### WikiTree Scraper

Searches WikiTree for historical persons matching pre-1790 debt certificate holders, fetches their family trees, and collects biographical data via the WikiTree API.

### Code

- `wikitree.py` — WikiTree API client (`search_candidates_for_name()`, `get_profile()`, `get_descendants()`)
- `search_wikitree_candidates.py` — Searches WikiTree for matching profiles filtered by birth year range and state
- `build_family_graph.py` — Fetches children for each candidate, builds parent→child edge graph
- `get_bios.py` — Fetches full biographical profiles, supports resume via deduplication
- `tests/` — Unit tests (mocked API) and integration tests (live API)

### Input

- `output/derived/pre1790/loan_office_certificates_cleaned.csv`

### Output

All output in `output/scrape/wikitree/`:
- `candidates.csv` — WikiTree candidate matches per person
- `family_graph_nodes.json` — Person nodes
- `family_graph_edges.json` — Parent→child edges
- `wikitree_bios.jsonl` — Full biographical profiles (one JSON per line)

### Downstream Usage

- `candidates.csv`, `family_graph_nodes.json`, `family_graph_edges.json` → consumed by `source/derived/family_tree/` (match_candidates.py, filter_matches.py, finalize_matches.py)

### Tests

Run with `pytest` from this directory. 5 test files:

| File | Type | Live API? | What it covers |
|---|---|---|---|
| `test_wikitree.py` | Mixed | Partially | API functions (`_year_from_date`, `search_profile_key`, `get_descendants`); live tests for George Washington search and location lookup |
| `test_task2.py` | Unit (mocked) | No | `get_children()` — parent-child edge extraction from WikiTree profiles |
| `test_task3.py` | Unit (mocked) | No | `run_task3()` — matching WikiTree descendants against post-1790 debt CSV |
| `test_task4.py` | Unit (mocked) | No | `refine_matches()` — filtering by birth year window, same-name deduplication |
| `test_get_bios.py` | Unit + Integration | Optional | `main()` — bio fetching to JSONL; real Wentworth-1687 profile if integration flag set |

Live tests in `test_wikitree.py` call the real WikiTree API (no credentials required, but network access needed). Integration tests in `test_get_bios.py` are optional.

### Notes

Matching/filtering logic (tasks 3-4) lives in `source/derived/family_tree/`. Analysis code lives in `source/analysis/family_tree_analysis/`.
