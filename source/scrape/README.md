# Scraping Code

Scripts that fetch data from external sources (Ancestry, WikiTree API). These are not part of the automated SCons build since they require network access and authentication.

## Directory Structure

- `ancestry_loan_office_scraper/` — Scrapes Ancestry Library Edition for residential county of pre-1790 loan office certificate holders (renamed from `ancestry_person_county_scraper/`)
- `ancestry_town_population_scraper/` — Scrapes 1790 census town populations from Ancestry
- `ancestry_cd_scraper/` — Scrapes Ancestry Library Edition for 1790 census matches of post-1790 CD holders (renamed from `post1790_cd/`)
- `wikitree/` — Searches WikiTree API for family tree data of pre-1790 certificate holders

**Archived:** `reconciliation_services/` was moved to `archive/reconciliation_services/`. It was a set of Flask services for OpenRefine name reconciliation (all ran on port 5000 — could not run simultaneously). It had no pipeline role and produced no file outputs.

## Shared Libraries

- `source/lib/selenium_base.py` — `GetChromeDriver(headless=True)` shared by both Ancestry scrapers
- `source/lib/ancestry_scraper/` — Shared package (auth, config, parser, search, session, storage, worker) used by `ancestry_loan_office_scraper/`

## Output

Scraping results are stored in `output/scrape/{scraper_name}/`.

## Downstream Usage

| Scraper | Output | Consumed by |
|---|---|---|
| `ancestry_loan_office_scraper` | `results/results_{state}.csv` | Not consumed by any current pipeline script. Analysis in `source/analysis/pre1790/analyze_ancestry_results.py` |
| `ancestry_town_population_scraper` | `town_pops*.csv` | Not consumed by any current script |
| `ancestry_cd_scraper` | `scrape_ids.csv`, `scrape_results.csv`, `name_list_scraped.csv` | `source/derived/post1790_cd/aggregate_final_cd.py` via `INDIR_SCRAPE` |
| `wikitree` | `results/task_1.csv`, `edges_task_2.json`, `nodes_task_2.json` | `source/derived/family_tree/` (match_candidates.py, filter_matches.py, finalize_matches.py) |

## Pipeline Dependency Note

`ancestry_town_population_scraper/scrape_town_populations.py` reads `output/derived/post1790_cd/final_data_CD.csv`, so it cannot run until the post-1790 CD cleaning pipeline has completed.
