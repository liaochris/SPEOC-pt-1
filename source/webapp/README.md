# Web Application

Dash web application for visualizing debt data and analysis results.

Built with [Plotly Dash](https://dash.plotly.com/).

### Launch

```bash
python source/webapp/web_app.py
```

### Code

- `app.py` — Dash app initialization
- `web_app.py` — Main entry point, page routing, and layout
- `about_us.py` — About us page
- `data_page.py` — Data exploration page
- `future.py` — Future work page
- `history.py` — Historical context page
- `maps.py` — Post-1790 map visualizations
- `pre_1790_map.py` — Pre-1790 map visualizations
- `pre_1790_data_description.py` — Pre-1790 data description page
- `pre_1790_tab.py` — Pre-1790 tab layout
- `tables.py` — Data table views
- `tables_style.py` — Table styling utilities

### Assets

- `assets/styles.css` — Application stylesheet
- `assets/*.pdf` — Hamilton exposition and data documents
- `assets/*.json` — Map descriptions and state codes
- `assets/map_df.csv` — Map data
- `assets/*.{png,jpg,jpeg,webp}` — Team member photos

### Input

- `output/derived/post1790_cd/final_data_CD.csv`
- `output/derived/pre1790/agg_debt_grouped.csv`
- `source/raw/shapefiles/`

### Notes

The app currently has hardcoded data paths that need updating (tracked in HANDOFF.md for Step 1.9).
