### `source/raw`

1. Fill in ORIGIN UNKNOWN flags in READMEs:
- `source/raw/shapefiles/README.md`: confirm download URLs / version numbers for each shapefile collection (Atlas of Historical County Boundaries, NHGIS, Esri)
2. Verify correction files are correct and cover all cases in future work `source/raw/post1790_cd/corrections`, `source/raw/pre1790/corrections`
3. review `source/raw/readme.md`

### `source/derived/prescrape`

- remove source/raw/pre1790/corrections/name_org_fix.csv, update names from source/raw/pre1790/corrections/name_fix.csv to include all desired ones, and go through "suspicious" names to fix them and harmonize fixes. 
  - I will just go through in pre1790 and clean up names that "clearly aren't names" but could become names
  - Then, I will scrape. Then, I will group by names after scrpe. 
  - On grouping - check if pre1790 does the "same person many in a row aggregation" 

### `source/scrape`

1. Understand in more detail what goes on in `source/scrape` - please have it report where each of the scrapers are used to generate output
2. Fix town population scraper URL: change `ancestry.com` → `ancestrylibrary.com` in `source/scrape/ancestry_town_population_scraper/scrape_town_populations.py:60` (CD and loan office already use the library edition)
3. Parameterize auth entry point URL in `source/lib/ancestry_scraper/auth.py:8-9`: replace hardcoded Georgia Tech Galileo proxy URL with `os.environ.get("ANCESTRY_PROXY_URL", "<default>")` so other institutions can configure their own proxy
4. Unify the driver singleton: loan office owns a separate module-level `_driver` in `source/lib/ancestry_scraper/search.py:7-13`; CD and town pop create a driver in `Main()` and pass it through — refactor to pass a single authenticated driver into `FetchSearchPage` for one shared login session across all scrapers
5. Automate auth login flow (deferred): `source/lib/ancestry_scraper/auth.py:12` currently waits up to 5 min for manual browser interaction to complete Okta/SSO redirect — needs credentials + MFA injected programmatically


### OVERALL

I want claude to write a DATA_APPENDIX.MD that documents
- different data sources being used (lightly describe this since source/raw provides more detail)
- key data decisions made when cleaning and scraping (can I broadly summarize these into a few princples, and point people to the corrections docs that contain omre info?)
