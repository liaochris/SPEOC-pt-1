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

## Next Step
- **Step 2.2**: source/scrape — Documentation and path fixes

## Remaining Items (Task 2)
- Step 2.2: source/scrape — fix paths in scrape_town_populations.py and analyze_results.py, document tests
- Step 2.3: source/derived — add Main() to 14 scripts, remove get_ipython(), externalize statedict
- Step 2.4: source/analysis — add Main() to 7 scripts, deduplicate speculator list → CSV, convert Julia to Python
- Step 2.5: source/webapp — light review and cleanup

## Known Issues / Flags for User
- `Marine_Liquidated_Debt_Certificates.xlsx` and `Pierce_Certs_cleaned_2019.xlsx` in pre1790/orig/ have unknown origin — marked `<!-- ORIGIN UNKNOWN -->` in README
- `census.csv`, `countyPopulation.csv`, `zip_code_database.xls` in census_data/orig/ have unknown origin — marked `<!-- ORIGIN UNKNOWN -->`
- `all_officers_ari.txt` compilation method is unclear — marked `<!-- ORIGIN UNKNOWN -->`
- `clean_names.py`, `clean_names_individual.py`, `combine_certificate_types.py` all **write back** to `source/raw/pre1790/corrections/name_fix.csv` during the cleaning run — this modifies a raw file, which is a data integrity concern to fix in Step 2.3

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
