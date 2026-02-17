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

## Next Step
4. **Step 1.3**: Move scraping code to `source/scrape/`
   - `open_refine/ancestry_scraper/` → `source/scrape/ancestry_person_county_scraper/`
   - `data_clean/Ancestry_Web_Scraper/web_scraper.ipynb` → convert to `source/scrape/ancestry_town_population_scraper/`
   - `family_tree/` tasks 1-2, wikitree.py, get_bios.py → `source/scrape/wikitree/`
   - `open_refine/reconciliation_services/` → `source/scrape/reconciliation_services/`

## Remaining Steps (Task 1)
5. Step 1.4: Move derived/cleaning code → `source/derived/` (convert notebooks to scripts)
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
