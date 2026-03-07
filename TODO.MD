### `source/raw`

1. Fill in ORIGIN UNKNOWN flags in READMEs:
    - `source/raw/pre1790/README.md`: confirm Dropbox folder/link where NARA transcriptions came from; fill in origin for Marine_Liquidated_Debt_Certificates.xlsx and Pierce_Certs_cleaned_2019.xlsx
    - `source/raw/post1790_cd/README.md`: confirm Dropbox folder/link and NARA T-series roll numbers for each state XLSX
    - `source/raw/post1790_asd/README.md`: same as post1790_cd
    - `source/raw/delegates/README.md`: identify published historical sources used for constitutional_convention_1787.xlsx and State Delegates.xlsx (e.g., Farrand's Records, state convention journals)
    - `source/raw/census_data/README.md`: look up exact source for zip_code_database.csv (likely US Census Bureau or similar)
    - `source/raw/shapefiles/README.md`: confirm download URLs / version numbers for each shapefile collection (Atlas of Historical County Boundaries, NHGIS, Esri)
    - `source/raw/society_members/README.md`: confirm compilation source of all_officers_ari.txt (until replaced by Wikipedia scraper in item 3)
2. Rename raw data files in `source/raw/census_data/orig/` to match project naming conventions (snake_case, descriptive names).
3. Verify correction files are correct and cover all cases — `source/raw/post1790_cd/corrections/company_names_fix.csv`, `occ_fix.csv`, `town_fix.csv`, `source/raw/pre1790/corrections/name_fix.csv`. First-pass review done; deeper verification deferred to source/derived refactoring (contextual).
4. Replace source/raw/society_members/orig/all_officers_ari.txt (and empty state .txt files) with a structured CSV derived from Wikipedia:
    - Write a scraper script (source/scrape/society_cincinnati/) that parses https://en.wikipedia.org/wiki/List_of_original_members_of_the_Society_of_the_Cincinnati and saves one row per member with columns: name, state
    - Save the Wikipedia page to the Wayback Machine (web.archive.org/save/) and record the archived URL + date extracted in the script and in source/raw/society_members/README.md
    - Output CSV to source/raw/society_members/orig/society_cincinnati_members.csv (replacing all_officers_ari.txt)
    - Delete all_officers_ari.txt and the empty state .txt files once the CSV is validated

### `source/scrape`

1. Understand in more detail what goes on in `source/scrape` - please have it report where each of the scrapers are used to generate output
2. See if there's a way scripts can not use derived outputs... +
3. Understand what the tests do and if they're necessary...


for source/scrape/ancestry_town_population_scraper
4.     SaveResults(town_pops_browse, OUTDIR / "town_pops_browse.csv")

    # Format Part II raw results into separate city/county/state columns
    FormatBrowseResults()
Do I need browse and brown_clean???
5. Shouldn't i just save the brows_clean once???

for source/scrape/ancestry_person_county_scraper
1. IT's not clear what script names in source/scrape/ancestry_person_county_scraper represent and what's being done in source/scrape/ancestry_person_county_scraper. Can you make a plan that analyzes this, understands functionality and propose separatoin?
2. Adapt all scripts in source/scrape to not use command line args, to run everything at once as opposed to by state, and update outputs accordingly. 