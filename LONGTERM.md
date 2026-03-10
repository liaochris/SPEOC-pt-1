## Scrape

The following scrape scripts have **not yet been run** and their outputs are missing. Downstream derived scripts cannot build until these are run.

1. `source/scrape/pre1790/scrape_name_resolution.py` — produces `output/scrape/pre1790/ancestry_name_changes_raw.csv`. Requires Emory NetID + Ancestry subscription. Blocks `source/derived/postscrape/pre1790/integrate_ancestry_search.py`.

2. `source/scrape/wikitree/fetch_wikitree_profiles.py` — produces `output/scrape/wikitree/wikitree_profiles.csv`. Fetches WikiTree profiles for all child+parent IDs in `family_graph_edges.json`. No credentials required (public WikiTree API). Blocks all `source/derived/postscrape/family_tree/` scripts.

---

## Data

1. No cleaning pipeline exists for assumed state debt data yet. The pipeline should mirror the post-1790 continental debt pipeline structure.
2. Incorporate Society of the Cincinnati membership as a variable in analyses. The Society of the Cincinnati was an organization of Revolutionary War officers founded in 1783; membership may correlate with delegate debt holdings or voting behavior. Use the Wikipedia list of original members as the data source: https://en.wikipedia.org/wiki/List_of_original_members_of_the_Society_of_the_Cincinnati
3. I want to improve raw name parsing to account for both the executors, and the person who they are executing on behalf of. The steps roughly follow as such
  - Amend relevant files in `source/raw/pre1790/corrections` and `source/raw/post1790/corrections` 
  - Distinguish between executors and original owners in  `source/derived` downstream code
4. I want to provide more detailed instructions on all the raw data in my dataset 
  - there should be `docs` folder with documentation the raw data
  - there should be a 
5. Reduce reundancy
  - Can I consolidate stateshape_1790 and nhgis_state_1790
6. I want claude to write a DATA_APPENDIX.MD that documents
  - different data sources being used (lightly describe this since source/raw provides more detail)
  - key data decisions made when cleaning and scraping (can I broadly summarize these into a few princples, and point people to the corrections docs that contain omre info?)


## Cleaning

1. There is no unified, principled system for name aggregation — deciding (a) when two
   differently-spelled names refer to the same person, and (b) which spelling to use as the
   canonical form. The current pipeline uses three overlapping mechanisms with no documented
   decision rule or priority order:
   - A heuristic (longest-name-wins) in `GroupByAncestryMatchIndex()` that fails often enough
     to require many hardcoded exceptions
   - A manual corrections file (`name_agg.csv`) that renames variants to a target spelling
   - Hardcoded overrides and drops scattered in code
   This produces silent errors: the wrong canonical spelling can be chosen, two records for
   the same person can remain split, or two distinct people can be merged. The fix should
   consolidate all name-identity decisions into a single auditable corrections CSV with an
   explicit documented rule, applied consistently across both `pre1790` and `post1790_cd`
   data. Note: `post1790_cd` currently does this `postscrape` using Ancestry match indices;
   `pre1790` does it `prescrape` (partly) in `source/derived/prescrape/pre1790/find_similar_names.py`
   — the two pipelines should be brought into alignment.
2. `pre1790` has no postscrape aggregation step. After the Ancestry scrape returns name
   resolution results, there is no pipeline equivalent to `aggregate_final_cd.py` that
   uses those results to disambiguate names, impute locations, and produce a person-level
   table. `source/derived/postscrape/post1790_cd/aggregate_final_cd.py` should serve as
   the template (GroupByAncestryMatchIndex, GroupByFuzzyCorrections, UnifyLocationWithinState,
   ImputeLocationFromPartners, ImputeLocationFromCensus, etc.).

3. Another aspect of the cleaning process is to separate text descriptions of debtholders into the names of the debtholder within that text. I think it would be helpful, for ease of understanding how the data is cleaned, to standardize the corrections made (if possible).
  - From the list of all names, see which ones are "suspicious" names that don't seem like names but could become names (if you remove extraneous text or separate out other names for example), and update the relevant file in source/raw/pre1790/corrections to turn the "suspicious" names into actual names
3. `Norm()` in `source/lib/wikitree_utils.py` is the sole name normalization function used throughout
   all family tree matching but has no docstring specifying what transformations it applies (casing,
   punctuation, suffixes like Jr/Sr, accented characters). Because all match/no-match decisions
   in `source/derived/postscrape/family_tree/` depend on it, any undocumented behavior is a silent
   source of missed or spurious matches. 


## Architecture

1. All code should be written in python
2. OpenRefine CSVs — manually exported inputs (not script outputs)
- These 4 files live in output/analysis/open_refine_analysis/ and are read by analysis scripts, not produced by them They're manually exported from OpenRefine:
  - liquidated_debt_certificates.csv
  - loan_office_certificates_cleaned.csv
  - pierce_certificates.csv
  - post_1790.csv
- These are essentially source data and arguably belong in source/raw/ rather than output/.
3. `output/analysis` is poorly organized 

## Code Quality

1. `source/derived/postscrape/post1790_cd/aggregate_final_cd.py` is 744 lines and mixes
   multiple responsibilities (name disambiguation, location imputation, occupation extraction,
   debt totaling). Refactor into focused modules, e.g. `aggregate_names.py`,
   `aggregate_locations.py`, `aggregate_occupations.py`, `aggregate_debts.py`, with
   `aggregate_final_cd.py` as the orchestrator. In addition, within each module, the code should be rewritten to disambiguate what's being done. 

2. `ApplyManualAdjustments()` in `source/derived/postscrape/post1790_cd/aggregate_final_cd.py`
   overrides records for four specific persons (Love Stone, John Gale, Nathaniel Irwin, Peleg
   Sanford) directly in code. This makes corrections invisible to auditors and hard to update.
   Externalize to a CSV under `source/raw/post1790_cd/corrections/` (analogous to `name_agg.csv`)
   that maps person identifiers to corrected field values.

3. The `PICKSTATE` dict in `source/derived/postscrape/post1790_cd/aggregate_final_cd.py` maps
   nine person names to a preferred state when they appear in multiple states. Embedding this
   in the script body makes it hard to audit or extend. Move to a CSV correction file under
   `source/raw/post1790_cd/corrections/name/postscrape/state_preferences.csv`.

4. `GroupByAncestryMatchIndex()` in `source/derived/postscrape/post1790_cd/aggregate_final_cd.py`
   selects the longest name spelling as the canonical form when multiple variants map to the same
   Ancestry profile. The numerous hardcoded exceptions in the same function (`'Israel Joseph'`,
   `'William Larned'`, etc.) confirm this heuristic fails regularly. Document the failure rate or
   replace with a frequency-based heuristic (most commonly observed spelling). Externalize the
   name override and drop entries to a corrections CSV.

5. `AddOccupationsFromTitle()` and `ExtractOccupationsFromCensus()` in
   `source/derived/postscrape/post1790_cd/aggregate_final_cd.py` hardcode keyword→occupation
   mappings (treasurer, adm, guard, school; Esq, Col, Rev, Dr, Major, etc.) inline. Externalize
   to `source/raw/post1790_cd/corrections/occ/prescrape/title_keywords.csv`.

6. Go through all `SaveData` calls across `source/analysis/` and rethink which keys are used,
   so that the conceptual meaning of each saved file aligns with the key choice. Some current
   keys (e.g. `original_row`, composite name+state pairs) are technically unique but do not
   reflect a meaningful identifier for the observation.

7. The `assets` column in `aggregate_final_cd.py` encodes structured per-record debt data
   as a pipe-delimited string (`"{data_index}_{N} : {6p},{6p_def},{3p} | ..."`). It is
   built in `AggregateIntoPersonTable()` (line ~259) and then parsed back via repeated
   string splitting in `AggregateDebtTotals()` (lines ~756–762). This is fragile and
   obscures what the data represents. Replace with a list of dicts (or a tidy long-format
   DataFrame) that carries `data_index`, `count`, `6p`, `6p_def`, `3p` as named fields,
   eliminating the string encode/decode round-trip.

8. `filter_matches.py` in `source/derived/postscrape/family_tree/` selects the first
   alphabetically-sorted parent ID when a WikiTree child has multiple parents. If both parents
   are in the post-1790 CD dataset the correct link could be silently discarded. Replace with
   logic that checks which parent(s) appear in `final_data_CD.csv` and prefers those; flag
   cases where both or neither match.


## Methodology

1. **Birth year window [1740–1780] for intergenerational matching** (`filter_matches.py`): The window
   `CENTER_YEAR=1760 ± YEAR_WINDOW=20` is hardcoded with no justification. Children of 1790 CD
   holders plausibly span a broader range. Examine the actual birth year distribution among
   WikiTree children of known CD holders and choose the window based on that distribution; document
   the rationale and move the constants to a shared config file.

2. **Selection bias from dropping missing birth years** (`filter_matches.py`,
   `DROP_IF_MISSING_YEAR=True`): Records without a parseable birth date are silently excluded from
   the intergenerational analysis. If missing birth years correlate with state, wealth, or record
   completeness, this introduces selection bias. Log the drop rate and check whether dropped records
   are geographically or economically distinctive before discarding them.


## Web App

1. Ensure that the relevant additions from summer 2025 can be viewed on the web app
2. Update the app's hardcoded data paths
3. Review web app code. 
