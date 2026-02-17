## Post-1790 Continental Debt Data Dictionary

Documentation for all variables in `final_data_CD.csv`.

**Group Name**, **Group State**, **Group County**, **Group Town** uniquely identify an individual debtholder.

### Variables

| Variable | Description |
|---|---|
| **Group Name** | One name used to group together debt held by individuals with the same identity but potentially different name spellings. |
| **Group State** | 2-letter abbreviation for the state debtholders reported when redeeming debt. Presumably their state of residence, as it generally matches the residence data from the 1790 Census. |
| **Group County** | The county debtholders reported when redeeming debt. May also have been imputed using Ancestry.com's 1790 census data. Interpreted as county of residence. |
| **Group Town** | The town debtholders reported when redeeming debt. May also have been imputed using Ancestry.com's 1790 census data. Interpreted as town of residence. |
| **Group Name Type** | Greatest level of geographical location detail available. Values: `Country` (US only), `State`, `County`, `Town`. Each implies knowledge of all broader levels. |
| **Group Match Index** | Index of foreign key matching to `match_data_CD.csv` (from the 1790 census). One debtholder may match multiple census individuals. |
| **Group Match Url** | URL on ancestry.com to locate matched individuals corresponding to Group Match Index. |
| **Full Search Name** | All names used to search for this identity on Ancestry.com, separated by `\|`. |
| **assets** | All records of assets from raw continental debt ledger data. Lines separated by `\|`, index and assets separated by `:`, 6%/6% deferred/3% stocks separated by `,`. |
| **occupation** | All occupations associated with this individual, from original ledger data or the 1790 census. Census occupations only imported if one match or all matches share the same occupation. |
| **Name_Fix_Transfer** | Mapping between uncleaned and cleaned names. Mappings separated by `:`, format `value / key`. Example: `Ebenezer Denny / Ebenezar Denny` means original name `Ebenezar Denny` is now `Ebenezer Denny`. |
| **Name_Fix_Clean** | Debtholder groups an identity was associated with. Groups separated by `:`, individuals within a group separated by `\|`. Example: `Ebenezer Denny : Ebenezer Denny \| Edward Denny` means individual and partnership holdings. |
| **imputed_location** | Whether geographical data was imputed from census. Same values as Group Name Type, plus `village` if sub-city information from census is available. |
| **location conflict** | Whether there is a conflict between Ancestry.com data and ledger data for residence location, and the broadest level of geography with conflict (e.g., `county`). |
| **Group Village** | Village/sub-city geographical region from Ancestry.com data. |
| **6p_total** | Total 6% stocks held across individual holdings and partnerships. |
| **6p_def_total** | Total deferred 6% stocks held across individual holdings and partnerships. |
| **unpaid_interest** | Total 3% stocks held across individual holdings and partnerships. |
| **6p_total_adj** | 6% stocks adjusted for partnerships (divided by number of partners). Sum of all `6p_total_adj` equals total 6% stock held by everyone. |
| **6p_def_total_adj** | Same as `6p_total_adj` but for deferred 6% stock. |
| **unpaid_interest_adj** | Same as `6p_total_adj` but for 3% stock. |
| **final_total** | Sum of `6p_total` and `6p_def_total`. |
| **final_total_adj** | Sum of `6p_total_adj` and `6p_def_total_adj`. |
