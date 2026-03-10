# Scraping Code

Scripts that fetch data from external sources (Ancestry, WikiTree API). These are not part of the automated SCons build since they require network access and authentication.

## Directory Structure

- `pre1790/` — Verifies whether two similar-sounding pre-1790 names refer to the same person, using Emory Ancestry subscription
- `ancestry_loan_office_scraper/` — Finds 1790 census location for pre-1790 loan office certificate holders (UChicago Ancestry)
- `ancestry_cd_scraper/` — Finds 1790 census records for post-1790 CD holders (UChicago Ancestry)
- `post1790_cd_town_pop/` — Scrapes 1790 census town populations for post-1790 CD analysis
- `wikitree/` — Searches WikiTree API for family tree data of pre-1790 certificate holders

**Archived:** `reconciliation_services/` was moved to `archive/reconciliation_services/`. It was a set of Flask services for OpenRefine name reconciliation (all ran on port 5000 — could not run simultaneously). It had no pipeline role and produced no file outputs.

## Shared Libraries

- `source/lib/selenium_base.py` — `GetChromeDriver(headless=True)` shared by both Ancestry scrapers
- `source/lib/ancestry_scraper/` — Shared package (auth, config, parser, search, session, storage, worker) used by `pre1790_census_match/`

## Output

Scraping results are stored in `output/scrape/{scraper_name}/`.

## Downstream Usage

| Scraper | Output dir | Consumed by |
|---|---|---|
| `pre1790` | `output/scrape/pre1790/` | `source/derived/postscrape/pre1790/integrate_ancestry_search.py` |
| `ancestry_loan_office_scraper` | `output/scrape/ancestry_loan_office_scraper/` | Analysis only — `source/analysis/pre1790/analyze_ancestry_results.py` |
| `ancestry_cd_scraper` | `output/scrape/ancestry_cd_scraper/` | `source/derived/postscrape/post1790_cd/aggregate_final_cd.py` via `INDIR_SCRAPE` |
| `post1790_cd_town_pop` | `output/scrape/post1790_cd_town_pop/` | Not consumed by any current script |
| `wikitree` | `output/scrape/wikitree/` | `source/derived/postscrape/family_tree/` (match_candidates.py, filter_matches.py, finalize_matches.py) |

## Running Manually

These scripts require Ancestry/WikiTree credentials and cannot run in the automated build. Run in pipeline order:

```
# Pre-1790 name resolution (requires Emory Ancestry credentials)
python source/scrape/pre1790/scrape_name_resolution.py

# Pre-1790 loan office census match (requires UChicago Ancestry credentials)
python source/scrape/ancestry_loan_office_scraper/scrape_loan_office.py

# Post-1790 CD census match (requires UChicago Ancestry credentials)
python source/scrape/ancestry_cd_scraper/scrape_cd.py

# Post-1790 CD town populations
python source/scrape/post1790_cd_town_pop/scrape_town_populations.py

# WikiTree family graph
python source/scrape/wikitree/search_wikitree_candidates.py
python source/scrape/wikitree/build_family_graph.py
python source/scrape/wikitree/get_bios.py
```

## Pipeline Dependency Note

- `pre1790/scrape_name_resolution.py` requires `output/derived/prescrape/pre1790/pre1790_cleaned.csv` and `similar_names/` — run prescrape pipeline first.
- `post1790_cd_town_pop/scrape_town_populations.py` reads `output/derived/postscrape/post1790_cd/final_data_CD.csv` — run postscrape pipeline first.
