# HANDOFF.md — Session Continuity

## Current Task
Task 2: Code quality improvements across source/raw, source/scrape, source/derived, source/analysis, source/webapp.
- **Branch**: `task2/code-quality`

## Completed Steps
### Task 1 (branch: reorganize/jmslab-structure)
1. **Step 1.0**: Cloned JMSLab template — SConstruct, source/lib/, placeholder SConscripts
2. **Step 1.1**: Cleaned up duplicates — deleted `family_tree copy/`, temp files, `__pycache__/`, archived Julia configs, updated `.gitignore`
3. **Step 1.2**: Moved raw data to `source/raw/` — separated post1790 into `post1790_cd/` and `post1790_asd/` by state, moved correction CSVs with documentation, deleted `web_app/data_raw/` duplicate
4. **Step 1.2 fixes**: Renamed `pre1790_cd/` → `pre1790/` (no ASD/CD split for pre-1790), separated corrections into `corrections/` subfolders, flattened nhgis nesting, fixed society_members doubled path, moved derived county_debt_total.csv out of raw
5. **Step 1.2 subfolder**: Organized raw data into `orig/`, `corrections/`, `docs/` subfolders. Deleted empty corrections.json, moved derived files (occupations_states.csv, cd_info.csv) to output/derived/pre1790/. Moved cd_raw.csv to docs/ (helper file). Removed all empty directories.
6. **Step 1.3**: Moved scraping code to `source/scrape/`
7. **Step 1.4**: Moved derived/cleaning code → `source/derived/`
8. **Step 1.5**: Moved analysis code → `source/analysis/`
9. **Step 1.6**: Moved web app → `source/webapp/`
10. **Step 1.7**: Organized WIP into `issue/`, moved legacy files to `archive/`
11. **Step 1.8**: Set up `source/lib/` with SaveData.py and `__init__.py`
12. **Step 1.9**: Fixed all imports and paths across the codebase
13. **Step 1.10**: Rewrote README.md to reflect new JMSLab structure

### Task 2 (branch: task2/code-quality)
14. **Step 2.1**: source/raw — Documentation and data cleanup
    - Renamed `cd_raw.csv` → `cd_import_metadata.csv` (docs/), updated all references in standardize_geography.py and READMEs
    - Renamed `manual_corrections.csv` → `name_fix.csv` (pre1790/corrections/), updated all references in 3 scripts
    - Renamed `occ_correction.csv` → `occ_fix.csv` (post1790_cd/corrections/), updated reference in aggregate_final_cd.py
    - Filtered `occ_fix.csv` to only include non-identity mappings (66 identity rows removed); updated aggregate_final_cd.py to use `.get(ele, ele)` fallback
    - Cleaned `statepop.csv` (removed 13 trailing empty columns and empty rows)
    - Updated all 7 source/raw/*/README.md files: added file origins (with ORIGIN UNKNOWN flags for unclear sources), corrections/ subfolder documentation, usage information, and fixed incorrect "via cd_raw.csv config" reference in pre1790 README
    - Updated source/derived/post1790_cd/README.md, source/derived/pre1790/README.md, and pipeline_documentation.md with new filenames
    - Society members: documented that 11 state .txt files are empty (all_officers_ari.txt is the only source)

15. **Step 2.2**: source/scrape — Restructuring, code quality, and documentation
    - **Renamed folders**: `ancestry_person_county_scraper/` → `ancestry_loan_office_scraper/`; `post1790_cd/` → `ancestry_cd_scraper/`
    - **Archived**: `reconciliation_services/` → `archive/reconciliation_services/` (all 3 services ran on port 5000; manual OpenRefine tool; no pipeline role)
    - **Moved** `ancestry_scraper/` package → `source/lib/ancestry_scraper/` (shared library; enables future sharing between scrapers)
    - **Moved** `analyze_results.py` → `source/analysis/pre1790/analyze_ancestry_results.py` (analysis code, not scraping)
    - **Deleted** `script.py` (interactive debug tool, no pipeline role)
    - **Renamed files**: `main.py` → `scrape_loan_office.py`; `create_names_lookup.py` → `generate_names.py`; `integrate_scraped_data.py` → `scrape_cd.py`
    - **Created** `source/lib/selenium_base.py` with `GetChromeDriver(headless=True)` — shared Chrome setup for both Ancestry scrapers
    - **CamelCase** all functions in `source/lib/ancestry_scraper/` (auth, parser, search, session, storage, worker); updated all relative imports
    - `scrape_loan_office.py`: removed argparse, now loops all 9 states in a single run; imports from `source.lib.ancestry_scraper`
    - `scrape_town_populations.py`: replaced `CHROME_OPTIONS` + `webdriver.Chrome(...)` with `GetChromeDriver()`; `FormatBrowseResults()` now takes dict directly (no intermediate `town_pops_browse.csv`)
    - `scrape_cd.py`: `OUTDIR = Path("output/scrape/ancestry_cd_scraper")`; `aggregate_final_cd.py`: `INDIR_SCRAPE = Path("output/scrape/ancestry_cd_scraper")`
    - `analyze_ancestry_results.py`: removed argparse; `Main()` loops COLONIES_13 and calls `PlotNationalChoropleth()` by default; updated all INDIR/OUTDIR paths
    - Fixed all 8 test files in `ancestry_loan_office_scraper/tests/` (imports `→ source.lib.ancestry_scraper.*`, CamelCase function names); deleted `test_process_name.py` (duplicate of test_worker.py)
    - `auth.py`: replaced hardcoded Chrome user-data-dir with `GetChromeDriver(headless=False)`; added `# TODO: update entry point URL in future step`; left proxy/login logic untouched
    - Added `ancestry_loan_office_scraper/README.md` and `ancestry_cd_scraper/README.md`; updated `source/scrape/README.md` to reflect new folder names and archived reconciliation_services

16. **Step 2.2.5**: source/scrape — Ancestry scraper unification
    - **Created** `source/lib/ancestry_scraper/scraper.py` — central scraping module with `ScrapeLoanOffice` (multi-strategy loan office search) and `ScrapeCD` (wrapper for CD helpers); all CD helper functions moved here from `scrape_cd.py` (`FindMatches`, `NavigateTo`, `ListPeople`, `GetInfo`, `DetermineMatchList`, `SearchLocationString`, `ProcessLocationString`, `LOCATIONSUFFIX`)
    - **`ScrapeLoanOffice` algorithm**: iterates `NAME_X_STRATEGIES = ["1_1", "s_s", "ps_ps"]` × `YEAR_OFFSETS = [0, 1, 3]`; stops early on first match; falls back on `Exception`; returns `MatchResult` namedtuple
    - **`ScrapeCD`**: thin wrapper around `FindMatches` (unchanged algorithm)
    - **Auth unified**: `scrape_cd.py` now uses `GetAuthenticatedDriver()` (Chrome via Galileo proxy) — Safari + UChicago Okta login block removed
    - **Storage schema updated**: 6 columns — `name, name_x, year_offset, url, match_status, counties` (counties pipe-separated)
    - **`FetchSearchPage`**: now accepts `name_x` parameter (default `"1_1"`)
    - **`ParseAllResidenceCounties`**: new parser function returning list of all county strings across all result rows
    - **`STATE_ABBREVIATIONS`** consolidated: replaces `STATEDICT` (scrape_cd.py), `statedict` (aggregate_final_cd.py), `STATE_CODES` (scrape_town_populations.py), `STATE_NAMES` (search_wikitree_candidates.py); canonical 15-state dict in `config.py`
    - **Code quality fixes**: stale OUTDIR path in `generate_names.py` fixed; 3 bare `except:` → `except Exception:` in `scrape_town_populations.py`; `_YearFromDate` → `YearFromDate` in `wikitree.py`
    - Updated `NAME_X_STRATEGIES`, `YEAR_OFFSETS` added to `config.py`
    - All 4 unit test files updated for new API (ScrapeLoanOffice, 6-column schema, ParseAllResidenceCounties, name_x param)

17. **Step 2.3**: source/derived/prescrape/ — reorganize + code quality for pre-scrape derived scripts
    - `git mv` all 9 prescrape scripts into `source/derived/prescrape/pre1790/` and `source/derived/prescrape/post1790_cd/`
    - Updated all OUTDIR path constants: `output/derived/pre1790` → `output/derived/prescrape/pre1790`; `output/derived/post1790_cd` → `output/derived/prescrape/post1790_cd`
    - Added `def Main():` wrapper with `if __name__ == "__main__": Main()` to all scripts
    - Renamed all functions to CamelCase; moved NLTK setup into `SetupNltk()`, pure helpers to module level
    - `find_similar_names.py`: removed `get_ipython().run_cell_magic('timeit', ...)` wrapper; removed unused imports
    - `name_fix.csv` write-back redirected to `output/derived/prescrape/pre1790/name_fix_auto.csv`
    - Updated `source/derived/SConscript`: replaced stale paths/targets
    - **QUALITY.md compliance pass**: Added `SaveData` to all saves in all 9 scripts; removed dead code; removed inline comments
    - **Dead scripts deleted**: `clean_names.py`, `clean_names_individual.py`, `clean_imperfections.py` — all three were superseded by `clean_names.py`, not registered in SConscript, and `clean_names.py` had interactive `input()` calls
    - **Scripts combined**: `aggregate_debt.py` + `aggregate_debt_alternate.py` merged into single `aggregate_debt.py` that outputs `final_agg_debt.csv` directly; intermediate `agg_debt_david.csv` eliminated
    - **`clean_names.py` modularized**: constants (`MANUAL_CORRECTIONS_OFS`, `MANUAL_CORRECTIONS_ORGS`, `CHANGES_COMP`, `CORP_KEY_WORDS`, `DECEASED_KEYWORDS`, `MANUAL_NO_MARK_LIST`, `ABBREVIATIONS`) and pure functions (`GetTags`, `CheckKeywordInString`, `SetupNltk`) moved to module level; dead first `manual_corrects` load removed; `ListToString` helper removed (replaced with `" ".join()` inline); `if True: try:` SSL pattern simplified; `type(x) != Tree` → `isinstance(x, Tree)`
    - **`aggregate_debt.py` modularized**: `COLUMN_CHANGES` dict, `CleanTable`, `DeNaN`, `AddStrikeConf`, `LowercaseStateAbbr` moved to module level; `AddOrgIndex` stays inside `Main()` (uses `nonlocal oii`)
    - **SConscript updated**: removed two-step `agg_debt_david.csv` → `final_agg_debt.csv` chain; now single step `aggregate_debt.py` → `final_agg_debt.csv`
    - **Data dictionaries created**: `source/derived/prescrape/pre1790/DATA_DICTIONARY.md` and `source/derived/prescrape/post1790_cd/DATA_DICTIONARY.md` documenting all input/output columns for all pipeline scripts

## Next Step
- **Step 2.4**: source/derived/postscrape/ — reorganize + code quality for post-scrape derived scripts (`integrate_ancestry_search.py`, `aggregate_final_cd.py`, `match_candidates.py`, `filter_matches.py`, `drop_same_name.py`, `finalize_matches.py`)

## Remaining Items (Task 2)
- Step 2.4: source/derived/postscrape/ — reorganize + code quality for post-scrape derived scripts
- Step 2.5: source/analysis — add Main() to 7 scripts, deduplicate speculator list → CSV, convert Julia to Python, systematize PNG outputs
- Step 2.6: source/webapp — light review, cleanup, and Heroku/alternate deployment decision

## Broader Task Plan

| Task | Description | Status |
|------|-------------|--------|
| Task 1 | Reorganize repo to JMSLab structure | DONE (branch: reorganize/jmslab-structure) |
| Task 2 | Code quality improvements (source/raw, scrape, derived, analysis, webapp) | IN PROGRESS |
| Task 3 | Document dependencies, create virtual environment | PENDING |
| Task 4 | Complete SCons build scripts (add remaining targets, dependency chains) | PENDING |

### Task 2 — GOALS_EOW.md Alignment

| Goal | Step | Status |
|------|------|--------|
| source/raw in good state | 2.1 | DONE |
| source/derived/prescrape runs + replicable | 2.3 | DONE |
| source/scrape input/routine/output clear | 2.2, 2.2.5 | DONE (pending TODO items: driver unification, rerun scraper) |
| source/derived/postscrape runs + produces output | 2.4 | NEXT |
| Website: Heroku / alternate deployment | 2.6 | PENDING |
| Systematize PNG outputs | 2.5 | PENDING |
| Decide whether to integrate existing drafts | — | UNSCHEDULED |

## Planned derived/ Folder Reorganization (Steps 2.3–2.4)

`source/derived/` will gain a two-level nesting: `prescrape/` and `postscrape/`, each preserving the existing `pre1790/`, `post1790_cd/`, `family_tree/` structure beneath. `output/derived/` mirrors the same layout.

```
source/derived/
├── prescrape/
│   ├── pre1790/          ← scripts that produce pre1790_cleaned.csv (scraper input)
│   │   ├── aggregate_debt.py          ← merged from aggregate_debt + aggregate_debt_alternate
│   │   ├── clean_names.py
│   │   └── find_similar_names.py
│   └── post1790_cd/      ← scripts that produce name_list.csv (CD scraper input)
│       ├── standardize_geography.py
│       └── clean_names_and_deduplicate.py
└── postscrape/
    ├── pre1790/           ← consumes loan office scraper output
    │   └── integrate_ancestry_search.py
    ├── post1790_cd/       ← consumes CD scraper output
    │   └── aggregate_final_cd.py
    └── family_tree/       ← consumes final_data_CD.csv + wikitree scraper output
        ├── match_candidates.py
        ├── filter_matches.py
        ├── drop_same_name.py
        └── finalize_matches.py
```

**Step 2.3 scope** (prescrape/ only — complete):
- All prescrape scripts moved, cleaned, and modularized
- Dead scripts deleted; aggregate scripts combined
- Data dictionaries written

**Step 2.4 scope** (postscrape/ only — 6 scripts):
- `git mv` all postscrape scripts into `source/derived/postscrape/`
- Update all INDIR/OUTDIR path constants; update `INDIR_SCRAPE` in `aggregate_final_cd.py`
- Add `Main()`, remove `get_ipython()`
- Second-pass verification of correction files (contextual, while refactoring)
- Update SConscript

## Known Issues / Flags for User
- `Marine_Liquidated_Debt_Certificates.xlsx` and `Pierce_Certs_cleaned_2019.xlsx` in pre1790/orig/ have unknown origin — marked `<!-- ORIGIN UNKNOWN -->` in README
- `county_demographics_1790.csv` (NHGIS/IPUMS), `county_pop_fips.csv` (Social Explorer), `zip_code_database.csv` in census_data/orig/ — origins now documented in census_data/README.md
- `all_officers_ari.txt` compilation method is unclear — marked `<!-- ORIGIN UNKNOWN -->`

## Key Decisions Made
- Post-1790 ASD and CD separated into distinct folders (raw/derived/analysis mirror each other)
- ASD cleaning not yet implemented — empty notebook was a placeholder
- `web_app/data_raw/` confirmed duplicate and deleted; derived CSVs preserved in `output/derived/`
- Both ancestry scrapers kept (person-county lookup vs town-population lookup) with clear naming
- Family tree split: scraping (tasks 1-2) → scrape/, matching (tasks 3-4) → derived/
- No `paths.py` — each script defines its own INDIR/OUTDIR constants
- Documentation as READMEs in relevant source/ folders, not a separate docs/ directory
- File names reflect purpose (e.g., `standardize_geography.py`), not step numbers
- SCons defines execution order
- Archive stays as-is; future PR to delete once replicability confirmed
- Raw data READMEs follow JMSLab template standard
- Pre-1790 is just `pre1790/` (no ASD concept), corrections in `corrections/` subfolder
- Notebook→script conversion must preserve all output logging (print statements, data shape checks)
- Task 4 should include separating debt original owners from executors in corrections CSVs and outputs
- Webapp CSV outputs go to `output/webapp/` (not written back to `source/raw/`)
- Individual state CSV reads in analyze_1790_debt.py deferred to Task 4 refactoring
- Correction files only contain non-identity mappings; scripts use fallback to original value
- occ_fix.csv uses `.get(ele, ele)` fallback in aggregate_final_cd.py
