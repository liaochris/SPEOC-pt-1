# Ancestry Loan Office Scraper

Scrapes individual person records from Ancestry Library Edition to find the residential county of pre-1790 loan office certificate holders. Uses Selenium to authenticate via a university library proxy, search the 1790 census collection, and parse county information from results.

## Usage

```bash
python source/scrape/ancestry_loan_office_scraper/scrape_loan_office.py
```

Requires Ancestry Library Edition access via a university proxy. See `source/lib/ancestry_scraper/auth.py` for proxy configuration (entry point URL to be updated in a future step).

## Code

- `scrape_loan_office.py` — Main entry point. Generates per-state name lookup CSVs (`GenerateNameFiles`), then scrapes Ancestry for each name (`ScrapeNames`)
- `tests/` — Unit and integration tests (`pytest`)

**Shared libraries** (in `source/lib/`):
- `source/lib/ancestry_scraper/` — Core package (auth, config, parser, search, session, storage, worker)
- `source/lib/selenium_base.py` — Shared Chrome driver setup (`GetChromeDriver`)

**Analysis** (moved to `source/analysis/`):
- `source/analysis/pre1790/analyze_ancestry_results.py` — Loads scraper results, parses county strings, generates choropleth maps

## Input

- `output/derived/pre1790/loan_office_certificates_cleaned.csv` — read by `GenerateNameFiles()` to produce per-state lookup CSVs
- `output/scrape/ancestry_loan_office_scraper/names_to_lookup/names_to_lookup_{state}.csv` — intermediate lookup files written by `GenerateNameFiles()`, read by `ScrapeNames()`

## Algorithm

`ScrapeLoanOffice` uses a stop-early multi-strategy search:
1. Iterates match strategies (`match_strategy`) in order: exact (`1_1`), soundex (`s_s`), phonetic (`ps_ps`)
2. For each strategy, tries year offsets in order: exact year, ±1 year, ±3 years
3. Stops and returns on the first strategy that yields any results
4. Falls back gracefully (`except Exception: continue`) on network/driver errors
5. Returns all counties found across matched records (pipe-separated in CSV)

Match status values: `Complete Match` (1 result), `N Potential Matches` (2–4), `Too Many Results` (>4), `No Match`.

## Output

All output in `output/scrape/ancestry_loan_office_scraper/`:
- `results/results_{state}.csv` — Scraped results per state (columns: `name`, `year`, `match_strategy`, `year_offset`, `url`, `match_status`, `counties`)
- `progress/progress_{state}.json` — Checkpoint files for resume

## Downstream Usage

The scraped `results/results_{state}.csv` files are consumed by `source/analysis/pre1790/analyze_ancestry_results.py` for choropleth visualization. They are not consumed by any derived pipeline script.

## Tests

Run with `pytest` from the project root (`PYTHONPATH=.`). 9 test files:

| File | Type | Live API? | What it covers |
|---|---|---|---|
| `conftests.py` | Fixtures | No | Dummy env vars; `dummy_html` fixture |
| `test_extract_county.py` | Unit | No | `ExtractCounty()` — parses location strings to county name |
| `test_parser.py` | Unit | No | `ParseResidenceCounty()` — extracts county from Ancestry HTML |
| `test_search.py` | Unit (mocked) | No | `FetchSearchPage()` — URL construction with name/state/year |
| `test_session.py` | Unit (mocked) | No | HTTP session setup, retry adapter, rate-limiting decorator |
| `test_storage.py` | Unit | No | CSV/JSON checkpoint I/O |
| `test_worker.py` | Unit (mocked) | No | `ProcessName()` — success and error paths with dummy storage |
| `test_integration_search.py` | Integration | **Yes** | Real Ancestry Library search + HTML parse (requires proxy) |
| `test_full_integration.py` | Integration | **Yes** | End-to-end: scrape, write CSV, verify progress checkpoint |

Integration tests require a Chrome profile with active Ancestry Library proxy cookies.
