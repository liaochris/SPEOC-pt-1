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
  scrape/                   # Web scraping code (run manually)
    ancestry_loan_office_scraper/
    ancestry_cd_scraper/
    wikitree/               #   WikiTree family tree searches
  derived/                  # Data cleaning pipelines
    prescrape/              #   Scripts that run before scraping
      pre1790/              #     Cleans raw pre-1790 XLSX → scraper input
      post1790_cd/          #     Cleans raw CD XLSX → scraper input
    postscrape/             #   Scripts that integrate scraper outputs
      pre1790/              #     Integrates ancestry loan-office results
      post1790_cd/          #     Integrates CD census-match results → final_data_CD.csv
      family_tree/          #     Matches delegates to WikiTree profiles
  analysis/                 # Figure and table generation
    pre1790/                #   Debt distribution, year analysis, maps
    post1790_cd/            #   1790 debt validation
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

The full pipeline has two SCons runs bracketing a manual scraping step:

**Step 1 — Prescrape (`scons`)**: SCons automatically processes raw XLSX files from `source/raw/` through `source/derived/prescrape/`, producing cleaned CSVs used as scraper inputs in `output/derived/prescrape/`.

**Step 2 — Scrapers (manual)**: Three scrapers must be run manually; their outputs land in `output/scrape/`:
- `source/scrape/ancestry_loan_office_scraper/` — Ancestry.com search for pre-1790 loan office holders
- `source/scrape/ancestry_cd_scraper/` — Ancestry.com census match for post-1790 CD holders
- `source/scrape/wikitree/` — WikiTree family tree profiles and edges

**Step 3 — Postscrape + Analysis (`scons`)**: With scraper outputs in place, SCons runs `source/derived/postscrape/` (integration scripts) and `source/analysis/` (figures and tables).

## Environment Setup

This project uses a conda environment called `SPEOC` (Python 3.11).

```bash
conda activate SPEOC
export PYTHONPATH=.   # must be set before running python scripts; all imports assume project root
```

Key packages: `pandas`, `geopandas`, `matplotlib`, `scons`, `selenium`, `rapidfuzz`, `nameparser`, `dash`, `openpyxl`, `scipy`, `scikit-learn`.

## Build System

SCons (`scons`) orchestrates the build DAG defined by `SConstruct` and `SConscript` files in each `source/` subdirectory.

```bash
scons              # Run full pipeline (prescrape + postscrape + analysis)
scons -n           # Dry run — show what would execute without running it
scons -j N         # Run N independent targets in parallel
scons --tree=all   # View full dependency graph
```

Scripts are registered with `env.Python(target, source)`. Per-entity parallelism (e.g. per-state) is done by creating one `env.Python` call per entity with `CL_ARG=entity`.

## Getting Started

```bash
conda activate SPEOC
export PYTHONPATH=.

# Step 1: build prescrape outputs
scons output/derived/prescrape/pre1790/pre1790_cleaned.csv

# Step 2: run scrapers manually (see source/scrape/*/README.md)

# Step 3: build full pipeline
scons
```

Individual scripts can also be run standalone:
```bash
export PYTHONPATH=.
python source/derived/prescrape/pre1790/clean_names.py
python source/analysis/pre1790/analyze_debt_distribution.py
```

## References

See `QUALITY.md` for full details. 
See `LONGTERM.md` for long-term steps