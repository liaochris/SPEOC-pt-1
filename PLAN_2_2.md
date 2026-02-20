# PLAN_2_2.md — Source/Scrape Analysis and Restructuring Plan

## Overview

This plan covers Step 2.2 of Task 2 (code quality improvements) for `source/scrape/`.
It addresses all questions raised in the review session and all TODO.MD items for `source/scrape`.

**Decisions made**:
- `reconciliation_services/` → **archive/** (manual OpenRefine workflow tool, not a pipeline component)
- `script.py` → **deleted** (interactive debug tool, no pipeline role)
- `analyze_results.py` → **moved to `source/analysis/pre1790/`** (in Step 2.2, not deferred)
- Shared Selenium setup → **`source/lib/selenium_base.py`** (abstract `GetChromeDriver()`)
- Two census scrapers stay **separate** but renamed: `ancestry_loan_office_scraper/` and `ancestry_cd_scraper/`
- Intermediate `town_pops_browse.csv` → **removed** (only save `town_pops_browse_clean.csv`)

---

## 1. Structure of Each Scraping Subfolder (TODO #1)

### `ancestry_town_population_scraper/` ✓ Good structure
**Purpose**: Scrape 1790 census town-level population counts from Ancestry.com browse hierarchy.

| Script | Role | Inputs | Outputs |
|---|---|---|---|
| `scrape_town_populations.py` | Main scraper | `output/derived/post1790_cd/final_data_CD.csv` | `town_pops.csv`, `town_pops_browse_clean.csv` |

**Notes**:
- Self-contained single script. Well-organized.
- Outputs not consumed downstream but kept for future per-capita debt analysis.

---

### `ancestry_person_county_scraper/` ✗ Four distinct roles mixed together

| Script | Role | Inputs | Outputs |
|---|---|---|---|
| `main.py` | Scraper entry point | `names_to_lookup_{state}.csv` | `results_{state}.csv`, `progress_{state}.json` → `output/scrape/ancestry_person_county_scraper/` |
| `ancestry_scraper/` (pkg) | Selenium scraper library | (called by main.py) | — |
| `create_names_lookup.py` | Name list generator (not a scraper) | `output/derived/pre1790/loan_office_certificates_cleaned.csv` | `names_to_lookup_{state}.csv` |
| `script.py` | Interactive CLI lookup tool (not a scraper) | `output/derived/pre1790/loan_office_certificates_cleaned.csv` | Terminal output only |
| `analyze_results.py` | Analysis/visualization (not a scraper) | `results_{state}.csv`, county shapefiles | `output/scrape/ancestry_person_county_scraper/maps/*.png` |

**Problems**: Mixes scraping, name generation, debugging, and analysis. `script.py` is a `while True: input(...)` loop. `analyze_results.py` belongs in `source/analysis/`. `ancestry_scraper/auth.py` has hardcoded personal dev path (`/Users/davidcho/Library/...`).

---

### `post1790_cd/` ✗ Orphan script, bad name

| Script | Role | Inputs | Outputs |
|---|---|---|---|
| `integrate_scraped_data.py` | Selenium scraper for CD person records | `output/derived/post1790_cd/name_list.csv` | `scrape_results.csv`, `name_list_scraped.csv`, `scrape_ids.csv` → `output/scrape/post1790_cd/` |

**Problems**: Name describes data domain, not function. No README, no tests.

---

### `reconciliation_services/` → **MOVE TO `archive/`**

| Script | Purpose | Port | Reads | Outputs |
|---|---|---|---|---|
| `reconcile_service.py` | Match against `raw_name` in Google Sheet | 5000 | Google Sheets (HTTP) | None — JSON to OpenRefine |
| `reconcile_last_name.py` | Match against `last_name_state` | 5000 ❌ | Same Google Sheet | None |
| `reconcile_loan_office_final_data_CD.py` | Match against `raw_name_state` | 5000 ❌ | Same Google Sheet | None |

**Reason to archive**: Manual OpenRefine workflow tools only — no pipeline role, all three on same port so cannot run simultaneously, no file outputs. Move to `archive/reconciliation_services/`.

---

### `wikitree/` ✓ Good structure
Well-organized with clear script names, README, and tests. No major issues.

---

## 2. Shared Abstraction: `source/lib/selenium_base.py`

Both `scrape_town_populations.py` and `ancestry_scraper/auth.py` define identical Chrome setup. Extract to a shared utility:

```python
# source/lib/selenium_base.py
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def GetChromeDriver(headless=True):
    options = Options()
    if headless:
        options.add_argument('--headless')
    options.add_argument("--window-size=1000,1000")
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--no-sandbox')
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
```

**Consumers after refactor**:
- `scrape_town_populations.py`: replaces the `CHROME_OPTIONS` block + all `webdriver.Chrome(service=..., options=CHROME_OPTIONS)` calls
- `ancestry_scraper/auth.py`: replaces the `Options()` block inside `GetAuthenticatedDriver()`; the user-data-dir and proxy URL stay in `auth.py` since they're auth-specific

**Also fix in `auth.py`**: Remove hardcoded `--user-data-dir=/Users/davidcho/...`. Replace with env var or configurable constant:
```python
CHROME_PROFILE_DIR = Path.home() / "Library/Application Support/Google/Chrome/TestProfile"
```

---

## 3. `analyze_results.py` → Move to `source/analysis/pre1790/`

**Decision**: Move NOW in Step 2.2 (not deferred). Rename to `analyze_ancestry_results.py`.

**Changes when moving**:
- Remove `argparse`
- Add constants: `CERT_YEAR = 1777`, run all `COLONIES_13` states + national choropleth by default in `Main()`
- Update `INDIR_RESULTS` to new path after folder rename: `Path("output/scrape/ancestry_loan_office_scraper/results")`
- Update test `test_extract_county.py` to import from new location: `source.analysis.pre1790.analyze_ancestry_results`

---

## 4. Reconciliation Services → `archive/`

**Action**: `git mv source/scrape/reconciliation_services/ archive/reconciliation_services/`

No code changes needed — just the move. Add a note in `source/scrape/README.md` that reconciliation services were archived.

---

## 5. Matching Algorithm Gap (for reference)

**`scrape_cd.py` algorithm** (sophisticated):
- 4–5 URL parameter combinations: exact → soundex → phonetic name matching
- Falls back from town → county → state location
- Handles 1–4 candidate matches with disambiguation
- Parses full household data

**`scrape_loan_office.py` algorithm** (simple):
- Single URL per person, state-specific Ancestry collection
- Parses only the county string from first result
- No fallback strategies

**Status**: Keep separate for now. Unifying requires shared auth, shared name+location input schema, and shared result parser. **Deferred to Task 3/4.**

---

## 6. Proposed Folder Restructuring

### Final structure

```
source/scrape/
├── README.md
│
├── ancestry_town_population_scraper/    # UNCHANGED
│   ├── scrape_town_populations.py      # (fix: remove intermediate town_pops_browse.csv)
│   └── README.md
│
├── ancestry_loan_office_scraper/        # RENAMED from ancestry_person_county_scraper/
│   │   Purpose: Scrape Ancestry 1790 census for pre-1790 loan office certificate holders
│   ├── ancestry_scraper/               # internal Selenium package
│   │   ├── auth.py                    # fix: remove hardcoded davidcho path
│   │   ├── config.py, parser.py, search.py, session.py, storage.py, worker.py
│   ├── scrape_loan_office.py          # RENAMED from main.py; remove argparse; loop all states
│   ├── generate_names.py              # RENAMED from create_names_lookup.py
│   │   (script.py DELETED)
│   ├── tests/
│   └── README.md
│
├── ancestry_cd_scraper/                 # RENAMED from post1790_cd/
│   │   Purpose: Scrape Ancestry 1790 census for post-1790 CD registrants
│   ├── scrape_cd.py                   # RENAMED from integrate_scraped_data.py
│   └── README.md                      # ADD
│
└── wikitree/                           # UNCHANGED
    ├── wikitree.py, get_bios.py, build_family_graph.py, search_wikitree_candidates.py
    ├── tests/
    └── README.md

archive/reconciliation_services/        # MOVED from source/scrape/reconciliation_services/

source/analysis/pre1790/
└── analyze_ancestry_results.py         # MOVED from ancestry_person_county_scraper/analyze_results.py

source/lib/
└── selenium_base.py                    # NEW
```

### Rationale for each change

| Change | Reason |
|---|---|
| `ancestry_person_county_scraper/` → `ancestry_loan_office_scraper/` | Describes function: scrapes Ancestry for loan office certificate holders |
| `post1790_cd/` → `ancestry_cd_scraper/` | Describes function: scrapes Ancestry for CD registrants |
| `main.py` → `scrape_loan_office.py` | Consistent with folder name, describes what it scrapes |
| `integrate_scraped_data.py` → `scrape_cd.py` | Short, descriptive, consistent with `scrape_loan_office.py` |
| `create_names_lookup.py` → `generate_names.py` | Simpler; accurately describes generating name lists |
| Delete `script.py` | Interactive debug tool, no pipeline role |
| Move `analyze_results.py` → `source/analysis/pre1790/` | Analysis code belongs in analysis folder |
| Move `reconciliation_services/` → `archive/` | Manual OpenRefine tools, not pipeline components, all share port 5000 |
| Create `source/lib/selenium_base.py` | DRY: shared Chrome driver setup |

### Output path changes required

| Script | Old output path | New output path |
|---|---|---|
| `scrape_loan_office.py` (via `storage.py`) | `output/scrape/ancestry_person_county_scraper/results/`, `progress/` | `output/scrape/ancestry_loan_office_scraper/results/`, `progress/` |
| `generate_names.py` | `output/scrape/ancestry_person_county_scraper/names_to_lookup/` | `output/scrape/ancestry_loan_office_scraper/names_to_lookup/` |
| `scrape_cd.py` | `output/scrape/post1790_cd/` | `output/scrape/ancestry_cd_scraper/` |
| `analyze_ancestry_results.py` | reads from `output/scrape/ancestry_person_county_scraper/results/` | reads from `output/scrape/ancestry_loan_office_scraper/results/` |

**Downstream**: `aggregate_final_cd.py` reads from `output/scrape/post1790_cd/` via `INDIR_SCRAPE` → update to `output/scrape/ancestry_cd_scraper/`.

---

## 7. TODO.MD — `source/scrape` Items

### TODO #1: Understand what goes on in source/scrape
→ Addressed in Section 1 above.

### TODO #2: See if scripts can not use derived outputs

| Script | Derived input | Can it be avoided? |
|---|---|---|
| `scrape_town_populations.py` | `output/derived/post1790_cd/final_data_CD.csv` | No — needs CD towns to know which locations to scrape |
| `scrape_cd.py` | `output/derived/post1790_cd/name_list.csv` | No — this is the name list to search |
| `generate_names.py` | `output/derived/pre1790/loan_office_certificates_cleaned.csv` | No — generates name list from derived data |

**Verdict**: All three are genuine unavoidable pipeline dependencies. Register in `SConstruct` so SCons enforces execution order. **Add to SConstruct update step.**

### TODO #3: Understand what the tests do and if they're necessary

**`ancestry_loan_office_scraper/tests/`** (renamed from `ancestry_person_county_scraper/tests/`):

| Test file | What it tests | Keep? | Action |
|---|---|---|---|
| `test_extract_county.py` | `ExtractCounty()` — now in `analyze_ancestry_results.py` | Yes | Update import to new location |
| `test_parser.py` | `ParseResidenceCounty()` in `ancestry_scraper/parser.py` | Yes | Fix imports |
| `test_search.py` | `FetchSearchPage()` in `ancestry_scraper/search.py` | Yes | Fix imports |
| `test_process_name.py` | `ProcessName()` — duplicate of test_worker.py | **Delete** | — |
| `test_worker.py` | `ProcessName()` in `ancestry_scraper/worker.py` | Yes | Fix imports |
| `test_storage.py` | `LoadProgress/SaveProgress/AppendResult()` | Yes | Fix imports |
| `test_session.py` | `GetSession()`, `RateLimited()` | Yes | Fix imports |
| `test_full_integration.py` | Full scraping flow (`@pytest.mark.integration`) | Yes — live test | Fix imports |
| `test_integration_search.py` | Live Ancestry fetch+parse (`@pytest.mark.integration`) | Yes — live test | Fix imports |

**`wikitree/tests/`**:

| Test file | Status |
|---|---|
| `test_wikitree.py`, `test_get_bios.py`, `test_task2.py` | Fixed in 2.2 |
| `test_task3.py` | Forward test for `source.derived.family_tree.match_candidates.RunTask3` (doesn't exist yet) — update to CamelCase |
| `test_task4.py` | Forward test for `source.derived.family_tree.filter_matches.RefineMatches/GetProfile` — update to CamelCase |

### TODO #4 & #5: Remove intermediate `town_pops_browse.csv`

**Fix**: Refactor `FormatBrowseResults(town_pops_dict)` to accept the dict directly from `ScrapeLocations()`.

```python
# Before in Main():
town_pops_browse = ScrapeLocations(browse_format=True, towns_l=towns_browse)
SaveResults(town_pops_browse, OUTDIR / "town_pops_browse.csv")
FormatBrowseResults()

# After in Main():
town_pops_browse = ScrapeLocations(browse_format=True, towns_l=towns_browse)
FormatBrowseResults(town_pops_browse)   # no intermediate file saved
```

`FormatBrowseResults(town_pops)` parses city/county/state/country from dict keys (currently done by reading from CSV), then saves only `town_pops_browse_clean.csv`.

### TODO #6: ancestry_person_county_scraper structure
→ Addressed in Section 6.

### TODO #7: Adapt scripts to not use command line args
→ `scrape_loan_office.py` (renamed main.py): remove `argparse`, loop over all states from `config.STATE_COLLECTION_URLS` in `Main()`. Skip states with no lookup file.
→ `analyze_ancestry_results.py` (renamed analyze_results.py): remove `argparse`, run all `COLONIES_13` + national choropleth in `Main()`.

---

## 8. Step 2.2 Remaining Implementation

### 2.2R.1 — Create `source/lib/selenium_base.py`
New file with `GetChromeDriver(headless=True)`. Import and use in:
- `scrape_town_populations.py` (replace `CHROME_OPTIONS` block)
- `ancestry_scraper/auth.py` (replace Options setup; fix davidcho path)

### 2.2R.2 — Folder renames (git mv)
```
git mv source/scrape/ancestry_person_county_scraper/ source/scrape/ancestry_loan_office_scraper/
git mv source/scrape/post1790_cd/ source/scrape/ancestry_cd_scraper/
git mv source/scrape/reconciliation_services/ archive/reconciliation_services/
```
Inside `ancestry_loan_office_scraper/`:
```
git mv main.py scrape_loan_office.py
git mv create_names_lookup.py generate_names.py
git rm script.py
git mv analyze_results.py ../../analysis/pre1790/analyze_ancestry_results.py
```
Inside `ancestry_cd_scraper/`:
```
git mv integrate_scraped_data.py scrape_cd.py
```

### 2.2R.3 — CamelCase rename in `ancestry_scraper/` package

| File | Renames |
|---|---|
| `parser.py` | `parse_residence_county` → `ParseResidenceCounty` |
| `search.py` | `fetch_search_page` → `FetchSearchPage`; `_get_driver` → `_GetDriver` |
| `session.py` | `get_session` → `GetSession`; `rate_limited` → `RateLimited`; `get_library_session` → `GetLibrarySession` |
| `storage.py` | `load_progress`→`LoadProgress`, `save_progress`→`SaveProgress`, `append_result`→`AppendResult`, `_progress_path`→`_ProgressPath`, `_results_path`→`_ResultsPath`; fix `ROOT` → `OUTDIR = Path("output/scrape/ancestry_loan_office_scraper")` |
| `worker.py` | `process_name` → `ProcessName` |
| `auth.py` | `get_authenticated_driver` → `GetAuthenticatedDriver`; fix hardcoded path; use `GetChromeDriver()` from `source.lib.selenium_base` |

### 2.2R.4 — Fix `scrape_loan_office.py` (was main.py)
- Fix import: `from source.scrape.ancestry_loan_office_scraper.ancestry_scraper.worker import ProcessName`
- Remove `argparse`; add `STATES = list(STATE_COLLECTION_URLS.keys())`
- `Main()` loops over all states; skips states with no lookup file

### 2.2R.5 — Fix all test file imports in `ancestry_loan_office_scraper/tests/`
`from ancestry_scraper.X import Y` → `from source.scrape.ancestry_loan_office_scraper.ancestry_scraper.X import Y`

Update all function name references to CamelCase. Delete `test_process_name.py`.

### 2.2R.6 — Fix `test_extract_county.py`
Update import to `from source.analysis.pre1790.analyze_ancestry_results import ExtractCounty, STATE_NAMES`.

### 2.2R.7 — Fix wikitree forward-reference tests
- `test_task3.py`: `run_task3` → `RunTask3`
- `test_task4.py`: `refine_matches` → `RefineMatches`; `mod.get_profile` → `mod.GetProfile`

### 2.2R.8 — Fix `analyze_ancestry_results.py` (moved from analyze_results.py)
Remove `argparse`. Add `CERT_YEAR = 1777`. `Main()` runs all `COLONIES_13` states + national choropleth.
Update `INDIR_RESULTS` to `Path("output/scrape/ancestry_loan_office_scraper/results")`.

### 2.2R.9 — Fix `scrape_town_populations.py`
- Import `GetChromeDriver` from `source.lib.selenium_base`; replace `CHROME_OPTIONS` block
- Refactor `FormatBrowseResults(town_pops)` to take dict directly
- Remove intermediate `town_pops_browse.csv` save from `Main()`

### 2.2R.10 — Fix `scrape_cd.py` output paths
Update `OUTDIR = Path("output/scrape/ancestry_cd_scraper")` (was `output/scrape/post1790_cd`).

### 2.2R.11 — Update `aggregate_final_cd.py`
`INDIR_SCRAPE = Path("output/scrape/ancestry_cd_scraper")`.

### 2.2R.12 — Add READMEs
- `source/scrape/ancestry_loan_office_scraper/README.md`
- `source/scrape/ancestry_cd_scraper/README.md`
- Note in `source/scrape/README.md` that reconciliation_services was archived

---

## 9. Deferred to Future Tasks

| Item | Deferred to |
|---|---|
| Unify matching algorithm between loan office and CD scrapers | Task 3/4 |
| Register scrape→derive dependencies in SConstruct | Step 2.5 or separate |
| Improve match rates for ancestry_loan_office_scraper | Task 3/4 |

---

## Critical Files Summary

| File | Change |
|---|---|
| `source/lib/selenium_base.py` | NEW — `GetChromeDriver()` |
| `source/scrape/ancestry_loan_office_scraper/ancestry_scraper/*.py` | CamelCase + fix paths (6 files) |
| `source/scrape/ancestry_loan_office_scraper/scrape_loan_office.py` | Renamed + remove argparse + loop all states |
| `source/scrape/ancestry_loan_office_scraper/generate_names.py` | Renamed from create_names_lookup.py |
| `source/scrape/ancestry_loan_office_scraper/tests/*.py` | Fix imports + CamelCase (8 files, delete 1) |
| `source/scrape/ancestry_cd_scraper/scrape_cd.py` | Renamed + update OUTDIR |
| `source/scrape/ancestry_town_population_scraper/scrape_town_populations.py` | Use `GetChromeDriver()`; remove intermediate save |
| `source/scrape/wikitree/tests/test_task3.py` | `RunTask3` |
| `source/scrape/wikitree/tests/test_task4.py` | `RefineMatches`, `GetProfile` |
| `source/analysis/pre1790/analyze_ancestry_results.py` | Moved from ancestry_person_county_scraper; remove argparse |
| `source/derived/post1790_cd/aggregate_final_cd.py` | Update `INDIR_SCRAPE` |
| `archive/reconciliation_services/` | Moved from source/scrape/ |
