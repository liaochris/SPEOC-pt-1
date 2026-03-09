# Scraping Code

Scripts that fetch data from external sources (Ancestry, WikiTree API). These are not part of the automated SCons build since they require network access and authentication.

## Directory Structure

- `pre1790_census_match/` — Finds 1790 census location for pre-1790 loan office certificate holders
- `post1790_cd_census_match/` — Finds 1790 census records for post-1790 CD holders
- `post1790_cd_town_pop/` — Scrapes 1790 census town populations for post-1790 CD analysis
- `wikitree/` — Searches WikiTree API for family tree data of pre-1790 certificate holders

**Archived:** `reconciliation_services/` was moved to `archive/reconciliation_services/`. It was a set of Flask services for OpenRefine name reconciliation (all ran on port 5000 — could not run simultaneously). It had no pipeline role and produced no file outputs.

## Shared Libraries

- `source/lib/selenium_base.py` — `GetChromeDriver(headless=True)` shared by both Ancestry scrapers
- `source/lib/ancestry_scraper/` — Shared package (auth, config, parser, search, session, storage, worker) used by `pre1790_census_match/`

## Output

Scraping results are stored in `output/scrape/{scraper_name}/`.

## Downstream Usage

| Scraper | Output | Consumed by |
|---|---|---|
| `pre1790_census_match` | `results/results_{state}.csv` | Not consumed by any current pipeline script. Analysis in `source/analysis/pre1790/analyze_ancestry_results.py` |
| `post1790_cd_town_pop` | `town_pops_clean.csv` | Not consumed by any current script |
| `post1790_cd_census_match` | `scrape_ids.csv`, `scrape_results.csv`, `name_list_scraped.csv` | `source/derived/postscrape/post1790_cd/aggregate_final_cd.py` via `INDIR_SCRAPE` |
| `wikitree` | `candidates.csv`, `family_graph_nodes.json`, `family_graph_edges.json`, `wikitree_bios.jsonl` | `source/derived/family_tree/` (match_candidates.py, filter_matches.py, finalize_matches.py) |

## Running Manually

These scripts require Ancestry/WikiTree credentials and cannot run in the automated build:

```
python source/scrape/pre1790_census_match/scrape_loan_office.py
python source/scrape/post1790_cd_census_match/scrape_cd.py
python source/scrape/post1790_cd_town_pop/scrape_town_populations.py
python source/scrape/wikitree/search_wikitree_candidates.py
python source/scrape/wikitree/build_family_graph.py
python source/scrape/wikitree/get_bios.py
```

## Pipeline Dependency Note

`post1790_cd_town_pop/scrape_town_populations.py` reads `output/derived/post1790_cd/final_data_CD.csv`, so it cannot run until the post-1790 CD cleaning pipeline has completed.
