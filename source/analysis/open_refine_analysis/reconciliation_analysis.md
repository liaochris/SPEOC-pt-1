# Reconciling the Debt: A Quantitative Match of Pre-1790 Certificates and Post-1790 Stock

**Author**: David Cho
**Date**: July 2025

## 1 Introduction

This report tracks our key questions about individuals whose names appear in both the pre-1790 loan office certificates and the post-1790 federal stock records. We refer to these linked individuals as *matches*. Our goal is to understand who these matched holders are and how their holdings changed. Because the loan office certificates yield the highest match rate, we focus on that source first. We begin with population-level patterns, then turn to notable individuals.

1. What share of total value is held by matches?
2. How do average holdings compare: matches vs. non-matches?
3. How do matched holdings change from pre-1790 to post-1790?
4. Which states show the highest match rates?
5. Which occupations are most common among matches?
6. Which matches increased their holdings, and were they prominent individuals?

## 2 Summary of Findings

**Definition.** "Matched" refers to individuals whose pre-1790 loan office certificates could be linked to post-1790 federal stock records.

- **Concentration of value.** Matched individuals are **4.32%** of all holders yet account for **12.53%** of total face value.
- **Larger pre-1790 holdings.** Matched individuals held more in pre-1790 certificates on average (**$9,037**) than non-matched (**$2,845**).
- **Net decline overall.** Among matched individuals, aggregate holdings fall from **$7,069,910** (pre-1790) to **$1,955,405** (post-1790); median percent change is negative.
- **But not for everyone.** About **19%** of matched individuals increase their holdings between periods.
- **State contrast.** Connecticut contributes **34.65%** of matched holders despite only **14.12%** of all holders, indicating over-representation in the matched set.
- **Occupations.** Pre-1790, **Esquires (lawyers)** hold the largest share (**21.19%**); post-1790, **Merchants** hold the largest share (**22.65%**). Merchant and Merchant-Esquire categories show net increases; most other occupations decline.

## 3 Limitations

1. To count the number of unique individuals, I counted the number of unique names. The issue is if two people with the same name live in the same state, they will be counted as one individual.
2. We used a basic matching process because of the pre-1790 dataset's current limitations. If the same name appeared in the pre-1790 and post-1790 datasets, it was considered a match.
3. Small changes to the reconciliation process seem to have noticeable changes. I made a small change and re-reconciled. Afterwards, Connecticut moved ahead of Pennsylvania for number of matched individuals.

## 4 Analysis

### 4.1 Percent of Total Debt Held By Matches

1. Create `matched_status` column: `true` if name was matched to name in post-1790 dataset, `false` otherwise
2. Calculate the total face value of loan office certificates. This turned out to be $56,419,829.
3. Calculate the total owned by matches. This turned out to be $7,069,910.

Approximately 12.53% of the loan office certificates were held by matches. Matched individuals made up roughly 4.32% of the dataset. Therefore, matches held a disproportionate share of the total loan office certificates.

### 4.2 Average Amounts: Matched vs. Non-Matched

When grouping, we are assuming each unique name corresponds to one unique individual.

- **Matched**: $9,037 per person
- **Non-Matched**: $2,845 per person

Matched individuals held on average $6,192 more than non-matched individuals.

### 4.3 Comparing Holdings Before and After 1790

Used the `final_total_adj` column in the post-1790 dataset compared to the Face Value column in the pre-1790 dataset.

- **Pre-1790**: $7,069,910.00
- **Post-1790**: $1,955,405.04
- **Median percent change**: -58.93% per individual

Most individuals reduced their holdings. However, one individual increased their holdings by >7000% and 108 individuals at least doubled their holdings.

### 4.4 Geographical Analysis

| State | Unique Individuals | Share of All Matches (%) | Share of All Holders (%) |
|-------|-------------------|------------------------|-------------------------|
| CT | 271 | 34.65 | 14.12 |
| PA | 261 | 33.38 | 38.81 |
| MD | 86 | 11.00 | 5.57 |
| NY | 72 | 9.21 | 8.04 |
| NH | 46 | 5.88 | 2.93 |
| MA | 31 | 3.96 | 15.95 |
| NJ | 12 | 1.53 | 10.35 |
| VA | 2 | 0.26 | 3.17 |
| DE | 1 | 0.13 | 1.05 |

Connecticut had a similar total of matched individuals to Pennsylvania (271 vs. 261) despite holding a considerably smaller share of all debt holders (14.12%). Hypothetical explanations: (1) Connecticut debt holders were more likely to hold onto their certificates, or (2) Connecticut may have had better preserved data.

### 4.5 Most Common Occupations

| Occupation | Count | Pre-1790 Total | Post-1790 Total | % of Pre-1790 | % of Post-1790 | Net % Change |
|-----------|-------|---------------|----------------|--------------|---------------|-------------|
| Farmer | 80 | 109,300 | 45,153 | 8.95 | 4.14 | -58.69 |
| Esquire | 75 | 258,800 | 194,783 | 21.19 | 17.88 | -24.74 |
| Merchant | 48 | 202,800 | 246,851 | 16.61 | 22.65 | 21.72 |
| Widow | 8 | 5,200 | 4,774 | 0.43 | 0.44 | -8.18 |
| Esquire-Merchant | 6 | 45,700 | 65,757 | 3.74 | 6.03 | 43.89 |

Holdings decreased for every occupation except merchants and esquire-merchants. This begs the question: Did merchants purchase these certificates from farmers?

### 4.6 Who Increased Their Holdings?

Top 10 individuals whose holdings increased:

| # | Name | State | Pre-1790 | Post-1790 | % Change | Occupation | Town |
|---|------|-------|----------|-----------|----------|-----------|------|
| 549 | Benjamin Harwood | MD | 1,500 | 645,030 | 42,902% | — | Annapolis |
| 368 | Joshua Lathrop | CT | 300 | 24,608 | 8,103% | — | Norwich |
| 332 | Joseph Boggs | PA | 200 | 15,629 | 7,714% | Broker | Philadelphia |
| 505 | Robert Buchanan | PA | 600 | 38,453 | 6,309% | Merchant | Philadelphia |
| 40 | Henry Hill | PA | 500 | 25,584 | 5,017% | Administrator, Esquire | Philadelphia |
| 71 | Isaac Wikoff | NJ | 200 | 9,095 | 4,447% | Esquire | — |
| 131 | James Williams | MD | 1,300 | 37,942 | 2,819% | — | Annapolis |
| 482 | Philip Schuyler | NY | 1,600 | 34,784 | 2,074% | — | Albany Ward 1 |
| 230 | John Keble | PA | 200 | 4,219 | 2,010% | Excise Officer | Philadelphia |
| 471 | Barnabas Deane | CT | 400 | 7,110 | 1,677% | Merchant | Hartford |

**Notable biographies:**

- **Benjamin Harwood**: Well-known merchant from Annapolis, Maryland. Established an import business with his brother Thomas. Served as militia lieutenant. Appointed Commissioner of Loans in 1777. Had $88,000 outstanding when he died.
- **Joshua Lathrop**: Owned a drugstore with his brother Daniel. Graduated from Yale. Well-respected doctor.
- **Henry Hill**: Prominent merchant in the Madeira wine trade. Knew George Washington during military service. Provided supplies for the Continental Army. Became a director for the Bank of North America.
- **James Williams**: Mayor of Annapolis (1793-1794).
- **Philip Schuyler**: US Senator from New York. Father-in-law of Alexander Hamilton. Served as Major General. Delegate to the Second Continental Congress. Federalist. Made money from land speculation.
- **Barnabas Deane**: Merchant handling shipments from France. Corresponded with Benjamin Franklin. Brother of Silas Deane (envoy to France, delegate to the Constitutional Convention).
