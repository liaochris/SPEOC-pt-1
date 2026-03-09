# pre1790 Name Resolution Scraper

> **Status: NOT YET RUN.** `output/scrape/pre1790/ancestry_name_changes_raw.csv` does not exist. Until this scraper is run, `source/derived/postscrape/pre1790/integrate_ancestry_search.py` cannot build.

Searches Ancestry.com to verify whether two similar-sounding names from the same state refer to the same historical person, using Emory University's Ancestry subscription.

## Script

**`scrape_name_resolution.py`** — For each pair of similar names identified by `find_similar_names.py`, searches both names in Ancestry's voter and census records. If both names resolve to the same Ancestry record, records the pair as a confirmed name change.

## Inputs

| File | Source |
|------|--------|
| `output/derived/prescrape/pre1790/pre1790_cleaned.csv` | `source/derived/prescrape/pre1790/clean_names.py` |
| `output/derived/prescrape/pre1790/similar_names/similar_names_{state}.csv` | `source/derived/prescrape/pre1790/find_similar_names.py` (one file per state) |

## Outputs

| File | Description |
|------|-------------|
| `output/scrape/pre1790/ancestry_name_changes_raw.csv` | Raw list of confirmed name changes (old name → new name, state) |
| `output/scrape/pre1790/ckpt_*.pkl` | Pickle checkpoint files; allow the scraper to resume after a crash |

## Authentication

Uses **Emory University's Ancestry library subscription** via `https://guides.libraries.emory.edu/ALE`. Requires Emory NetID credentials. This is separate from the UChicago Galileo proxy used by `source/scrape/ancestry_loan_office_scraper/` and `source/scrape/ancestry_cd_scraper/`.

## Checkpointing

The scraper saves the four state variables (`ancestry_name_changes`, `rerun_rows`, `checked`, `fixes`) as pickle files after each name pair. If the process crashes, re-run the script — it will skip already-processed pairs.

## Run Order

Must run **after** `source/derived/prescrape/pre1790/find_similar_names.py` has completed for all states.

Output is consumed by `source/derived/postscrape/pre1790/integrate_ancestry_search.py`.

```
python source/scrape/pre1790/scrape_name_resolution.py
```

Not part of the automated SCons build (requires credentials and network access).
