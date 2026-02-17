## S2022
Summer Team: Chris Liao (chrisliao@uchicago.edu), David Cho, Jiacheng Li, Maria Dubasov, Miguel Santos

This folder contains all work that was done by the 2022 Summer Team on exploring the history behind America's early national debt. 
Much of the work done by this summer's cohort focused on analyzing the post-1790 debt certificates, the ones that people redeemed for consols following the passage of Hamilton's plan to refund the national debt. 
Within this subset, we were most interested in the Continental Debt certificates, rather than the Assumed State Debt Certificates.

Chronologically, the S2022 timeline is as follows. If you just care about our results, see bullet point **8**.
1. First, [`data_cleaning_cl.ipynb`](cleaning_CD/data_cleaning_cl.ipynb) cleans the post-1790 debt certificates, producing
   1. [`aggregated_CD.csv`](data_raw/post1790/Aggregated/raw/aggregated_CD.csv), an aggregated version of all post-1790 debt certificates that has the county column added
   2. [`county_cw.csv`](data_raw/AssetGeography/county_cw.csv), a preliminary geographical crosswalk
      1. Geographical labels refers to town, county, state and country names
2. [`cleaning_town.ipynb`](archive/S2022/debt_distribution_tables/cleaning_town.ipynb) takes as input [`aggregated_CD.csv`](data_raw/post1790/Aggregated/raw/aggregated_CD.csv) and standardizes our geographical labels, producing
   1. [`aggregated_CD_final.csv`](data_raw/post1790/Aggregated/raw/aggregated_CD_final.csv) - an improved version of [`aggregated_CD.csv`](data_raw/post1790/Aggregated/raw/aggregated_CD.csv) with standardized town names
   2. [`final_geographical_cw.csv`](data_raw/AssetGeography/final_geographical_cw.csv) - final geographical crosswalk that links original and cleaned geographical labels
3. [`AvgDebtPerOccupation.ipynb`](archive/S2022/occupational_analysis/avg_debt_occupation/AvgDebtPerOccupation.ipynb) takes as input [`aggregated_CD.csv`](data_raw/post1790/Aggregated/raw/aggregated_CD.csv) and helps standardize different occupation names, producing
   1. [`occupation_mapping.csv`](data_raw/post1790/Aggregated/occupation/occupation_mapping.csv) - mapping from original occupation names to their standardized names
4. [`NY_webscrape.ipynb`](archive/S2022/scraping/NY_webscrape.ipynb) take as input [`NY_1790_CD.xlsx`](data_raw/post1790/NY/NY_1790_CD.xlsx) and produce
   1. [`NY_results.csv`](archive/S2022/scraping/NY_results.csv), a raw version of scraped data for New York from the U.S. Federal Census by scraping ancestry.com
5. [`NY_process_webscrape.ipynb`](archive/S2022/scraping/NY_process_webscrape.ipynb) takes as input [`NY_results.csv`](archive/S2022/scraping/NY_results.csv) and produces
   1. [`NY_table.csv`](data_raw/post1790/Aggregated/NY_table.csv), the final version of our combined New York dataset that includes both original debt certificate and ancestry.com data
   2. [`NY_table2.csv`](data_raw/post1790/Aggregated/NY_table.csv), a supplementary table
6. [`CD_webscrape.ipynb`](archive/S2022/scraping/CD_webscrape.ipynb) takes as input [`aggregated_CD_final.csv`](data_raw/post1790/Aggregated/raw/aggregated_CD_final.csv) and produces
   1. [`CD_results.csv`](archive/S2022/scraping/CD_results.csv), a raw version of scraped data for the rest of our states (minus Virginia) from the U.S. Federal Census by scraping ancestry.com
7. [`CD_process_webscrape.ipynb`](archive/S2022/scraping/CD_process_webscrape.ipynb) takes as input [`CD_results.csv`](archive/S2022/scraping/CD_results.csv), [`NY_table.csv`](data_raw/post1790/Aggregated/NY_table.csv), and [`NY_table2.csv`](data_raw/post1790/Aggregated/NY_table.csv), producing
   1. [`CD_table.csv`](archive/S2022/Results/CD_table.csv) and [`CD_table2.csv`](archive/S2022/Results/CD_table2.csv), our final tables that index individuals by search group, aggregate their debt holdings and are combined with scraped ancestry.com data
      1. [`CD_table.csv`](archive/S2022/Results/CD_table.csv) is the final table we use to produce our final results 
8. [`final_analysis.ipynb`](archive/S2022/final_analysis/analysis.ipynb) takes as input [`CD_table.csv`](archive/S2022/Results/CD_table.csv) and outputs
   1. [`maps`](archive/S2022/Results/maps) - which consists of maps sumarizing total and average debt holdings across county and state
   2. [`geography_table.csv`](archive/S2022/Results/geography_table.csv) - which summarizes debt holdings by geographic location
   3. [`Occupation_table.csv`](archive/S2022/Results/Occupation_table.csv) - which summarizes debt holdings by occupation
      1. [`Occupation_states`](archive/S2022/Results/Occupation_states) contain the same information, but by state.  

delete unused folders,

write bash script to execute everything for replicability. 


## Data

