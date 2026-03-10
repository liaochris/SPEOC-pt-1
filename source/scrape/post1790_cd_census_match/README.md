# Ancestry CD Scraper

Scrapes Ancestry Library Edition to find 1790 census matches for post-1790 continental debt (CD) certificate holders. Uses Selenium with Chrome to authenticate via a university library proxy (`GetAuthenticatedDriver`), then searches the 1790 census collection using a multi-strategy matching algorithm (exact, soundex, phonetic) with fallback across town/county/state granularities.

## Usage

```bash
python source/scrape/ancestry_cd_scraper/scrape_cd.py
```

Requires Ancestry Library Edition access. Authentication is handled by `source/lib/ancestry_scraper/auth.py` via the Galileo proxy (entry point URL to be updated in a future step).

## Code

- `scrape_cd.py` — Main entry point. Reads `name_changes_list.csv` from derived output, loops all names, calls `ScrapeCD` from `source/lib/ancestry_scraper/scraper.py`, writes scraped results

**Shared libraries** (in `source/lib/`):
- `source/lib/ancestry_scraper/scraper.py` — Central scraping module: `ScrapeCD` + `ScrapeLoanOffice` + CD helper functions (`FindMatches`, `NavigateTo`, `ListPeople`, `GetInfo`, `DetermineMatchList`, `SearchLocationString`, `ProcessLocationString`)
- `source/lib/ancestry_scraper/auth.py` — Shared Chrome authentication via Galileo proxy

## Input

- `output/derived/post1790_cd/name_changes_list.csv` — cleaned name list from `source/derived/post1790_cd/clean_names_and_deduplicate.py`

## Output

All output in `output/scrape/ancestry_cd_scraper/`:
- `scrape_ids.csv` — search metadata (name, location, url, match index, match status) per scrape attempt
- `scrape_results.csv` — census record data (name, location, household info) for each matched person
- `name_list_scraped.csv` — merged view of `name_changes_list.csv` with scrape match results
- `scrape_ids_prelim.csv`, `scrape_results_prelim.csv` — checkpoint saves written during scraping

## Downstream Usage

`source/derived/post1790_cd/aggregate_final_cd.py` reads from `output/scrape/ancestry_cd_scraper/` via `INDIR_SCRAPE`.
