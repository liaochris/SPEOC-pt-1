# Post-1790 Continental Debt (CD) — Postscrape

**Author:** Chris Liao

## Objective

Aggregate standardized geography data, Ancestry census match results, and manual corrections into a person-level table of post-1790 continental debt holdings.

---

## Script

**`source/derived/postscrape/post1790_cd/aggregate_final_cd.py`**

---

## Inputs

- `output/derived/prescrape/post1790_cd/geo_standardized_CD_post1790.csv` — geo-standardized records from NARA transcriptions
- `output/derived/prescrape/post1790_cd/check/name_changes_list.csv` — prescrape name change audit log
- `output/scrape/post1790_cd_census_match/name_list_scraped.csv` — names sent to Ancestry (manual scrape)
- `output/scrape/post1790_cd_census_match/scrape_results.csv` — raw Ancestry census match results
- `source/raw/post1790_cd/corrections/name/postscrape/name_agg.csv` — manual name aggregation rules
- `source/raw/post1790_cd/corrections/occ/postscrape/occ_fix.csv` — occupation corrections

---

## Processing Steps (in call order)

1. **`AddOccupationsFromTitle`** — extract occupations embedded in name strings
   (e.g. "John Smith Esq" → occupation = "Esquire")

2. **`MergeScrapedData`** — left-join geo-standardized data with Ancestry scrape results on
   `(Fn_Fix, Ln_Fix, new_town, county, new_state, country, geo_level)`

3. **`GroupByAncestryMatchIndex`** — when multiple name spellings share one Ancestry match index,
   consolidate them under a single representative name (longest string wins)

4. **`GroupByFuzzyCorrections`** — apply manual name aggregation rules from `name_agg.csv`
   to merge near-duplicate name entries

5. **`UnifyLocationWithinState`** — when a person appears at multiple specificity levels
   (town + county + state) in the same state, keep the most specific

6. **`AggregateIntoPersonTable`** — group all certificate rows for each person into one row;
   encode assets as `"{state}_{row} : {6%},{6%def},{3%}"` pipe-separated strings

7. **`ImputeLocationFromPartners`** — when a person appears in multiple locations, use
   co-holders who share the same certificate to resolve the correct location

8. **`BuildNameChangeDictionary`** — create a lookup mapping every name variant to its
   canonical group name, including manual overrides

9. **`UnifyNameSpellings`** — apply the name change dictionary to produce `Name_Fix_Clean`
   and `Name_Fix_Transfer` columns

10. **`ApplyManualAdjustments`** — hardcoded corrections for ~4 known problem cases
    (Love Stone, John Gale, Nathaniel Irwin, Peleg Sanford)

11. **`CorrectWrongStateAssignments`** — for names that appear in multiple states with only
    state-level location data, pick the preferred state using `PICKSTATE` dict and
    `group_name_state.csv`

12. **`AddVillageInfo`** — promote Philadelphia/Charleston/NYC matches from town to village level

13. **`ExtractOccupationsFromCensus`** — parse occupations and titles (Esq, Dr, Col, etc.)
    out of Ancestry `Name` field

14. **`ResolveMultipleMatches`** — when a person has multiple census matches, narrow to the
    one whose name matches the person's group name

15. **`EliminateBroadLocationMatches`** — when multiple matches exist, remove those whose
    town/county doesn't match the known location

16. **`ImputeLocationFromCensus`** — use the remaining census match to refine the person's
    town/county/village location

17. **`StandardizeOccupations`** — merge occupations from census matches with those from name
    parsing; apply `occ_fix.csv` corrections

18. **`ReindexMatchData`** — deduplicate the match table and assign sequential integer indices;
    update `Group Match Index` in the final table accordingly

19. **`AggregateDebtTotals`** — compute per-person debt totals:
    - `6p_total`, `6p_def_total`, `unpaid_interest` — raw sums
    - `6p_total_adj`, `6p_def_total_adj`, `unpaid_interest_adj` — divided by co-holder count
    - `final_total`, `final_total_adj` — sum of 6% and 6% deferred

---

## Output Schema

### final_data_CD.csv (person-level)

| Column | Description |
|---|---|
| `Group Name` | Canonical debtholder name |
| `Group State` | State abbreviation |
| `Group County` | County (standardized) |
| `Group Town` | Town |
| `Group Village` | Village (Philadelphia/Charleston/NYC only) |
| `Group Name Type` | Specificity of location: `town`, `county`, `state`, or `country` |
| `Group Match Index` | Index into match_data_CD.csv (pipe-separated if multiple) |
| `Group Match Status` | Ancestry match confidence |
| `Group Match Url` | Ancestry search URL |
| `Name_Fix_Clean` | Canonical names for all persons on this certificate |
| `Name_Fix_Transfer` | Variant → canonical name mapping audit trail |
| `Full Search Name` | All name variants (pipe-separated) |
| `assets` | Pipe-separated asset strings: `{state}_{row}_{N} : {6%},{6%def},{3%}` |
| `occupation` | Pipe-separated occupations |
| `imputed_location` | Specificity level imputed from census match |
| `location conflict` | Conflict type (`county`, `town`) if census location disagrees |
| `6p_total` | Total 6% face value |
| `6p_def_total` | Total 6% deferred face value |
| `unpaid_interest` | Total unpaid interest (3%) |
| `6p_total_adj` | 6% total ÷ co-holder count |
| `6p_def_total_adj` | 6% deferred total ÷ co-holder count |
| `unpaid_interest_adj` | Unpaid interest ÷ co-holder count |
| `final_total` | `6p_total + 6p_def_total` |
| `final_total_adj` | `6p_total_adj + 6p_def_total_adj` |

### match_data_CD.csv (census match reference)

One row per unique Ancestry census match. Indexed by `index_new` (referenced from `final_data_CD.csv`).
