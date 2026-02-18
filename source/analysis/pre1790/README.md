# Pre-1790 Analysis

Distribution, temporal, and geographic analysis of pre-1790 debt certificates.

### Code

- `analyze_debt_distribution.py` — Distribution analysis of certificate face values by bracket, state, and holder type.
- `analyze_by_year.jl` — Julia script analyzing debt certificate issuance patterns over time by state and month.
- `generate_pierce_maps.jl` — Julia script generating geographic maps for Pierce certificate data.

### Input

- `output/derived/pre1790/agg_debt_grouped.csv`
- `source/raw/society_members/` (society membership data)
- `source/raw/shapefiles/`

### Output

- `output/analysis/pre1790/` (PNGs, SVGs, CSVs for debt brackets, year charts, maps, member analysis)
