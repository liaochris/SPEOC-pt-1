# HANDOFF.md — Session Continuity

## Current Task
Reorganizing SPEOC-pt-1 codebase to follow the JMSLab/template structure.
- **Branch**: `reorganize/jmslab-structure`
- **Plan file**: `.claude/plans/clever-launching-pretzel.md`
- **PR**: Not yet created (will be opened after all steps complete)

## Completed Steps
1. **Step 1.0**: Cloned JMSLab template — SConstruct, source/lib/, placeholder SConscripts
2. **Step 1.1**: Cleaned up duplicates — deleted `family_tree copy/`, temp files, `__pycache__/`, archived Julia configs, updated `.gitignore`
3. **Step 1.2**: Moved raw data to `source/raw/` — separated post1790 into `post1790_cd/` and `post1790_asd/` by state, moved correction CSVs with documentation, deleted `web_app/data_raw/` duplicate
4. **Step 1.2 fixes**: Renamed `pre1790_cd/` → `pre1790/` (no ASD/CD split for pre-1790), separated corrections into `corrections/` subfolders, flattened nhgis nesting, fixed society_members doubled path, moved derived county_debt_total.csv out of raw

5. **Step 1.2 subfolder**: Organized raw data into `orig/`, `corrections/`, `docs/` subfolders. Deleted empty corrections.json, moved derived files (occupations_states.csv, cd_info.csv) to output/derived/pre1790/. Moved cd_raw.csv to docs/ (helper file). Removed all empty directories.
6. **Step 1.3**: Moved scraping code to `source/scrape/`
   - `open_refine/ancestry_scraper/` → `source/scrape/ancestry_person_county_scraper/` (code + tests + output)
   - `data_clean/Ancestry_Web_Scraper/web_scraper.ipynb` → converted via nbconvert to `source/scrape/ancestry_town_population_scraper/scrape_town_populations.py`
   - `family_tree/` tasks 1-2, wikitree.py, get_bios.py, tests → `source/scrape/wikitree/`
   - `open_refine/reconciliation_services/` → `source/scrape/reconciliation_services/`
   - Added READMEs for each scrape subfolder and updated SConscript

## Next Step
7. **Step 1.4**: Move derived/cleaning code → `source/derived/` (convert notebooks to scripts)

## Remaining Steps (Task 1)
8. Step 1.4: Move derived/cleaning code → `source/derived/` (convert notebooks to scripts)
6. Step 1.5: Move analysis code → `source/analysis/` (convert notebooks to scripts)
7. Step 1.6: Move web app → `source/webapp/`
8. Step 1.7: Handle WIP (issue/), archive, documentation
9. Step 1.8: Set up source/lib/ SaveData
10. Step 1.9: Fix all imports, finalize SConstruct
11. Step 1.10: Update README

## Future Tasks (separate PRs)
- Task 2: Document dependencies, create virtual environment
- Task 3: Complete SCons build scripts
- Task 4: Code quality improvements and recommendations

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
- Raw data READMEs follow JMSLab template standard from docs/raw_directory_readme_template.md
- Pre-1790 is just `pre1790/` (no ASD concept), corrections in `corrections/` subfolder
- Notebook→script conversion must preserve all output logging (print statements, data shape checks)
- Task 4 should include separating debt original owners from executors in corrections CSVs and outputs
- Workflow: `git add` only — do not commit until user gives the go-ahead
- Use `jupyter nbconvert --to script` for notebook→script conversion, then clean up for QUALITY.md
- Path updates deferred to Step 1.9 — tracked below

## Path Updates Needed (for Step 1.9)

Accumulated list of internal file paths that reference old locations and need updating.

### source/scrape/ancestry_person_county_scraper/
- `create_names_lookup.py`: reads `loan_office_certificates_cleaned.csv` (was `data/loan_office_certificates_cleaned.csv`, now `output/scrape/ancestry_person_county_scraper/data/`)
- `analyze_results.py`: reads results CSVs, shapefile (old relative paths to `results/`, `data/data/US_AtlasHCB_Counties_Gen01/`)
- `ancestry_scraper/config.py`: may have hardcoded paths
- `ancestry_scraper/auth.py`: hardcoded macOS Chrome profile path (user-specific, leave as-is)

### source/scrape/ancestry_town_population_scraper/
- `scrape_town_populations.py`: reads `final_data_CD.csv`, writes `town_pops.csv`, `town_pops_clean.csv`, `town_pops_2.csv` — all need path updates

### source/scrape/wikitree/
- `search_wikitree_candidates.py` (task_1): reads `data/loan_office_certificates_cleaned.csv` → now `output/scrape/wikitree/data/`; writes `results/task_1.csv` → `output/scrape/wikitree/results/`
- `build_family_graph.py` (task_2): reads/writes from `results/` → `output/scrape/wikitree/results/`
- `get_bios.py`: reads `results/task_1.csv`, writes `wikitree_bios.jsonl` → output paths
- `tests/`: relative paths to `data/test.csv` and `results/`

### source/scrape/reconciliation_services/
- All 3 Flask services: fetch from Google Sheets (no local path issues), but service metadata URLs may need review

### source/raw/post1790_cd/docs/
- `cd_raw.csv`: contains `file` column with old paths like `../data_raw/post1790/CT/CT_post1790_CD_ledger.xlsx` → need to update to new `source/raw/post1790_cd/orig/CT/...` paths

### source/derived/post1790_cd/
- `standardize_geography.py`: reads `clean_tools/cd_raw.csv` → `source/raw/post1790_cd/docs/cd_raw.csv`; reads `clean_tools/town_fix.csv` → `source/raw/post1790_cd/corrections/town_fix.csv`; reads `../data_raw/post1790/` → `source/raw/post1790_cd/orig/`; writes to `../data_clean/` → `output/derived/post1790_cd/`
- `clean_names_and_deduplicate.py`: reads `../data_clean/` → `output/derived/post1790_cd/`; reads `clean_tools/company_names_fix.csv` → `source/raw/post1790_cd/corrections/`
- `integrate_scraped_data.py`: reads `../data_clean/` and `scrape_tools/` → `output/derived/post1790_cd/`
- `aggregate_final_cd.py`: reads `../data_clean/` → `output/derived/post1790_cd/`; reads `clean_tools/occ_correction.csv` → `source/raw/post1790_cd/corrections/`

### source/derived/pre1790/
- All scripts: read `../data_raw/pre1790/` → `source/raw/pre1790/orig/`; read/write `data/` → `output/derived/pre1790/`; read `corrections/` → `source/raw/pre1790/corrections/`

### source/derived/family_tree/
- `match_candidates.py`: reads `results/` → `output/scrape/wikitree/results/`; reads `data/post_1790.csv` → `output/scrape/wikitree/data/`; imports from `wikitree` → `source.scrape.wikitree.wikitree`; imports from `task_3` (self-references)
- `filter_matches.py`: reads `results/` → `output/scrape/wikitree/results/`; imports `wikitree`, `task_3`
- `drop_same_name.py`: similar to filter_matches
- `finalize_matches.py`: reads/writes `results/` → `output/scrape/wikitree/results/`
