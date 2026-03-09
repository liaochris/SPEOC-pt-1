# SPEOC-pt-1

Code repository for a Summer Project on the Economic Origins of the Constitution. Contact: chrisliao (at) uchicago (dot) edu.

## Overview

This project analyzes whether US constitutional and state convention delegates' debt holdings influenced their votes, using historical debt certificate records from the National Archives.

## Data Domains

- **Pre-1790**: State-issued debt certificates (loan office, liquidated debt by state, Pierce, marine) — the original revolutionary war debts
- **Post-1790**: Federal debt certificates issued after Hamilton's 1790 assumption plan — continental debt (CD) and assumed state debt (ASD)

## Repository Structure

```
SConstruct                  # Build DAG (SCons)
source/
  raw/                      # Untouched original data
    pre1790/                #   Pre-1790 certificates (orig/, corrections/)
    post1790_cd/            #   Post-1790 continental debt by state
    post1790_asd/           #   Post-1790 assumed state debt by state
    census_data/            #   Census and population data
    shapefiles/             #   Geographic shapefiles
    delegates/              #   Convention delegate lists
    society_members/        #   Society of the Cincinnati membership
  scrape/                   # Web scraping code
    ancestry_person_county_scraper/
    ancestry_town_population_scraper/
    wikitree/               #   WikiTree family tree searches
    reconciliation_services/#   OpenRefine reconciliation
  derived/                  # Data cleaning pipelines
    post1790_cd/            #   CD cleaning (4 scripts)
    pre1790/                #   Pre-1790 cleaning (8 scripts)
    family_tree/            #   WikiTree matching (4 scripts)
  analysis/                 # Figure and table generation
    pre1790/                #   Debt distribution, year analysis, maps
    post1790_cd/            #   1790 debt analysis
    debt_analysis/          #   Treasurers, Hamilton, notable holdings
    open_refine_analysis/   #   OpenRefine reconciliation results
    family_tree_analysis/   #   WikiTree match analysis
  webapp/                   # Dash web application
  lib/                      # Shared utilities (SaveData, JMSLab builders)
output/                     # Generated files (mirrors source/ structure)
archive/                    # Frozen legacy code (S2021, S2022)
issue/                      # Work-in-progress tasks
```

## Pipeline

Raw XLSX (National Archives transcriptions) → `source/derived/` cleaning scripts → cleaned CSVs in `output/derived/` → `source/analysis/` scripts → figures/tables in `output/analysis/`

## Getting Started

```bash
# All scripts assume PYTHONPATH=. (project root)
export PYTHONPATH=.

# Build with SCons
scons        # Run full pipeline
scons -n     # Dry run (show what would execute)
```

Python scripts follow a `Main()` entry point convention — each can be run standalone:
```bash
python source/derived/pre1790/clean_names.py
```

Julia scripts (pre-1790 maps and year analysis) are run manually:
```bash
julia source/analysis/pre1790/analyze_by_year.jl
julia source/analysis/pre1790/generate_pierce_maps.jl
```

## Code Conventions

See `QUALITY.md` for full details. Key points:
- Functions: CamelCase; Variables: snake_case
- Global paths: CAPITALIZED `Path` objects (`INDIR_*`, `OUTDIR_*`)
- Every script has `Main()` with `if __name__ == "__main__": Main()`
- Save data with `SaveData` from `source/lib/SaveData.py`
