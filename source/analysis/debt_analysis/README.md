# Debt Analysis

Treasurer matching and Hamilton public debt analysis.

### Code

- `match_treasurers.py` — Matches state treasurer names against debt records. Data source: [The Political Graveyard](http://politicalgraveyard.com/) and this [Google Document](https://docs.google.com/document/d/1khn5-ga7sHQIj6xsysl5fMGg597mzmWPiw9MMnYssAQ/edit).
- `analyze_hamilton_public_debt.py` — Analyzes Hamilton's 1790 public debt report.
- `analyze_notable_holdings.py` — Examines holdings of notable individuals (convention delegates, founding fathers).

### Input

- `output/derived/post1790_cd/final_data_CD.csv`
- `output/derived/pre1790/pre1790_cleaned.csv`
- `source/raw/delegates/` (convention delegate rosters)

### Output

- `output/analysis/debt_analysis/` (match CSVs, debt summaries)

### Reference

- `state_treasurers.md` — Compiled list of state treasurers circa 1790 from The Political Graveyard and Wikipedia.
