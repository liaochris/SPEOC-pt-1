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
- SCons (Python-based). `SConstruct` at root, `SConscript` in each source/ subdirectory (see QUALITY.md)
- `env.Python(target, source)` to register build targets; pass `CL_ARG=value` for script arguments read via `sys.argv`
- `scons` to build, `scons -n` for dry run, `scons -j N` to run independent targets in parallel
- `scons --tree=all` to view the full build DAG
