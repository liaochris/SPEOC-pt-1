### Ancestry Town Population Scraper

Scrapes 1790 census town population data from Ancestry.com. Uses Selenium to navigate census search, input town/county/state, and extract result counts as population figures.

### Code

- `scrape_town_populations.py` — Main scraper (converted from `web_scraper.ipynb` via nbconvert)

### Input

- `final_data_CD.csv` (from post-1790 CD cleaning pipeline output)

### Output

All output in `output/scrape/ancestry_town_population_scraper/`:
- `town_pops.csv` — Raw scraping results (location string → population)
- `town_pops_clean.csv` — Cleaned with separate city/county/state/population columns

### Notes

Requires Selenium and ChromeDriver. States without Ancestry 1790 census records (VA, GA, NJ, DE) are excluded. Part II of the script enumerates all towns in Ancestry's 1790 census browse interface for comprehensive coverage.
