# HANDOFF.md — Session Continuity

## Current Task
Reorganizing SPEOC-pt-1 codebase to follow the JMSLab/template structure.
- **Branch**: `reorganize/jmslab-structure`
- **PR**: Not yet created (will be opened after all steps complete)

## Completed Steps
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
    - Analysis scripts: match_treasurers.py, analyze_notable_holdings.py, analyze_openrefine_results.py, analyze_matches.py, analyze_non_matched.py — added INDIR/OUTDIR Path constants, replaced bare filenames and relative paths
    - Julia files: analyze_by_year.jl, generate_pierce_maps.jl — updated all `data/`, `results/`, `data_raw/`, `data_clean/` references to new `output/` and `source/raw/` paths
    - Webapp: pre_1790_tab.py (raw XLSX → `source/raw/pre1790/orig/`, derived CSVs → `output/`), pre_1790_map.py (fixed `../cleaning_CD/` reference)
    - Scrape: wikitree.py (fixed `../data/` reference)
    - Post-1790 analysis: analyze_1790_debt.py — added path constants, fixed aggregated input/output paths (individual state CSV reads still need refactoring — they reference CSVs that only exist as XLSX in raw)
    - Updated `source/analysis/SConscript` with build targets
    - Verified no remaining `../` relative paths or `data_raw`/`data_clean` references in source/
13. **Step 1.10**: Rewrote README.md to reflect new JMSLab structure

## Next Step
- **PR**: Create pull request for the reorganization branch

## Remaining Items (for future PRs)
- `source/analysis/post1790_cd/analyze_1790_debt.py` needs deeper refactoring: still has `get_ipython()` calls, individual state reads use bare CSV filenames that don't exist as CSVs (only XLSX in raw)
- `source/scrape/ancestry_town_population_scraper/scrape_town_populations.py` path updates not verified
- `source/scrape/ancestry_person_county_scraper/analyze_results.py` and `config.py` path updates not verified

## Future Tasks (separate PRs)
- Task 2: Code quality improvements (proper Main() functions for all notebook conversions, remove `get_ipython()` calls, deduplicate speculator lists in analyze_notable_holdings.py). Also reorganize code so its written in a modular format, check whether non-scrapes run, have data be imported asopposed to defined in scripts. convert al julia to pyhton
- Task 3: Document dependencies, create virtual environment
- Task 4: Complete SCons build scripts (add remaining targets, dependency chains)

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
