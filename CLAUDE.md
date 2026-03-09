# CLAUDE.md — Project Context for Claude Code

- Use python not python3 to test code

## Project Overview
SPEOC (Summer Project on the Economic Origins of the Constitution) analyzes whether US constitutional and state convention delegates' debt holdings influenced their votes, using historical debt certificate records from the National Archives.

## Two Main Data Domains
- **Pre-1790**: State-issued debt certificates (loan office, liquidated debt by state, Pierce, marine) — these are the original revolutionary war debts
- **Post-1790**: Federal debt certificates issued after Hamilton's 1790 assumption plan — continental debt (CD) and assumed state debt (ASD). ASD cleaning is not yet implemented.

## Key Pipeline
Raw XLSX (National Archives transcriptions) → cleaning/derived scripts → cleaned CSVs → analysis figures/tables

## Repository Structure (JMSLab template)
- `source/raw/` — Untouched original data, separated into `pre1790/`, `post1790_cd/`, `post1790_asd/`
- `source/scrape/` — Web scraping code (Ancestry.com, WikiTree)
- `source/derived/` — Data cleaning pipelines, mirrors raw/ structure
- `source/analysis/` — Figure and table generation, mirrors raw/ structure
- `source/webapp/` — Dash web application
- `source/lib/` — Shared utilities (SaveData, JMSLab builders)
- `output/` — Generated files, mirrors source/ structure
- `archive/` — Frozen legacy code (S2021, S2022)
- `issue/` — Work-in-progress tasks
- `SConstruct` + `SConscript` files define the build DAG

## Code Conventions (see QUALITY.md)
- Functions: CamelCase
- Variables: snake_case
- Global paths: CAPITALIZED, use `Path` objects, named `INDIR_*` / `OUTDIR_*`
- Every script has a `Main()` entry point (no arguments), with `if __name__ == "__main__": Main()`
- Functions ordered by call order, `Main()` first
- Save data with `SaveData` from `source/lib/SaveData.py`
- `PYTHONPATH=.` assumed — import from project root
- No typing annotations, minimal comments

## Build System
- SCons (Python-based). `SConstruct` at root, `SConscript` in each source/ subdirectory
- `env.Python(target, source)` to register build targets
- `scons` to build, `scons -n` for dry run

## Important Notes
- Post-1790 ASD and CD raw data separated into `source/raw/post1790_cd/` and `source/raw/post1790_asd/`. Current cleaning code only handles CD.
- ASD cleaning is not yet implemented — the old notebook was an empty placeholder.
- Raw data organized into `orig/`, `corrections/`, `docs/` subfolders within each `source/raw/` subdirectory.
- `source/analysis/post1790_cd/analyze_1790_debt.py` still needs deeper refactoring (notebook artifacts, bare CSV reads).
- `scrape_cd.py` lives in `source/scrape/post1790_cd_census_match/`; outputs go to `output/scrape/post1790_cd_census_match/`; `aggregate_final_cd.py` reads from there via `INDIR_SCRAPE`.
- `pre1790_census_match` outputs (`results_*.csv`) are analyzed by `source/analysis/pre1790/analyze_ancestry_results.py` — not consumed by any pipeline script.
- `source/lib/ancestry_scraper/` — shared Selenium package (auth, config, parser, search, session, storage, worker) used by `pre1790_census_match/`; all functions CamelCase.
- `source/lib/selenium_base.py` — `GetChromeDriver(headless=True)` shared by both Ancestry scrapers.
- `post1790_cd_town_pop` outputs (`town_pops_clean.csv`) are not consumed downstream but preserved for potential future per-capita debt analysis.
- Correction files contain only non-identity mappings; all scripts use `.get(key, key)` fallback pattern.
- `clean_names.py` (prescrape/pre1790), `clean_names_individual.py`, and `clean_names.py` (prescrape/post1790_cd) write back to `source/raw/pre1790/corrections/name_fix.csv` — data integrity concern flagged for Task 3/4.
