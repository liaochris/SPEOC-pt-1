### Ancestry Town Population Scraper

Scrapes 1790 census town population data from Ancestry.com. Uses Selenium to navigate census search, input town/county/state, and extract result counts as population figures.

### Pipeline

1. Loads unique towns from `final_data_CD.csv`
2. For each town, searches Ancestry's 1790 census collection (collection 5058)
3. Extracts population from result count
4. Handles errors by re-running failed towns
5. Part II: Enumerates all towns in Ancestry's 1790 census browse interface for comprehensive coverage

### Output

- `town_pops.csv` — Raw scraping results (location string → population)
- `town_pops_clean.csv` — Cleaned with separate city/county/state/population columns

### Notes

Converted from `web_scraper.ipynb` via nbconvert. Requires Selenium and ChromeDriver. States without Ancestry 1790 census records (VA, GA, NJ, DE) are excluded.
