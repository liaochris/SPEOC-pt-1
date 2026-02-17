# Derived Data / Cleaning Pipeline

Scripts that clean, transform, and combine raw data into analysis-ready datasets. Each subdirectory mirrors the structure of `source/raw/`.

## Directory Structure

- `post1790_cd/` — Post-1790 continental debt cleaning pipeline (geography, names, scraping integration, aggregation)
- `pre1790/` — Pre-1790 certificate cleaning (combining types, name cleaning, deduplication, ancestry search integration)
- `family_tree/` — WikiTree candidate matching and filtering (tasks 3-4)

OpenRefine project data lives in `output/derived/open_refine/` (no code, data only).

## Output

Intermediate and final CSVs are stored in `output/derived/{subfolder}/`.
