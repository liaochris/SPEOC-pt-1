# Scraping Code

Scripts that fetch data from external sources (Ancestry, WikiTree API, OpenRefine). These are not part of the automated SCons build since they require network access and authentication.

## Directory Structure

- `ancestry_person_county_scraper/` — Scrapes Ancestry Library Edition for residential county of individual debt certificate holders
- `ancestry_town_population_scraper/` — Scrapes 1790 census town populations from Ancestry
- `wikitree/` — Searches WikiTree API for family tree data of pre-1790 certificate holders
- `reconciliation_services/` — Flask services for OpenRefine name reconciliation against post-1790 CD data

## Output

Scraping results are stored in `output/scrape/{scraper_name}/`.
