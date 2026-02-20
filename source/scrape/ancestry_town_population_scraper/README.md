### Ancestry Town Population Scraper

Scrapes 1790 census town population data from Ancestry.com. Uses Selenium to navigate census search, input town/county/state, and extract result counts as population figures.

### Code

- `scrape_town_populations.py` — Main scraper (converted from `web_scraper.ipynb` via nbconvert)

### Input

- `output/derived/post1790_cd/final_data_CD.csv` — Post-1790 CD cleaning pipeline output. **Dependency note:** this scraper cannot run until the post-1790 CD cleaning pipeline (`source/derived/post1790_cd/`) has been executed.

### Output

All output in `output/scrape/ancestry_town_population_scraper/`:
- `town_pops.csv` — Raw Part I scraping results (location string → population count)
- `town_pops_browse.csv` — Raw Part II scraping results (all Ancestry browse towns)
- `town_pops_browse_clean.csv` — Cleaned with separate city/county/state/population columns

### Downstream Usage

These outputs are not currently consumed by any downstream derived or analysis scripts. The town-level 1790 census population counts could be useful for future per-capita debt analysis (normalizing certificate amounts by local population), but no such analysis has been built yet.

### Notes

Requires Selenium and ChromeDriver. States without Ancestry 1790 census records (VA, GA, NJ, DE) are excluded from Part I. Part II of the script independently enumerates all towns in Ancestry's 1790 census browse interface for comprehensive coverage, regardless of certificate data.
