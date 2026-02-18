#!/usr/bin/env python
# coding: utf-8

# # Analysis: Learning More About Matched Individuals

# In[141]:


from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

INDIR = Path("output/analysis/open_refine_analysis")
OUTDIR = Path("output/analysis/open_refine_analysis")

loan_office_certificates = pd.read_csv(INDIR / "loan_office_certificates_cleaned.csv")
post_1790 = pd.read_csv(INDIR / "post_1790.csv")


# In[143]:


loan_office_certificates["raw_name_state"] = loan_office_certificates["raw_name"] + "||" + loan_office_certificates["state"]


# In[144]:


loan_office_certificates["raw_name_state"].head()


# ## Percent of Total Debt Held By Matches

# In[145]:


# find total value of all debt certificates
total = loan_office_certificates["Face Value"].sum()
print(total) 


# In[146]:


# find total owned by matched names
total_matched = loan_office_certificates[loan_office_certificates["matched_status"]]["Face Value"].sum()
print(total_matched)


# In[147]:


# calculate percentage 
print((total_matched / total) * 100)


# In[148]:


# what percentage of debtholders did the matches make up
total_unique_names = loan_office_certificates["raw_name_state"].nunique()
total_unique_matched_names = loan_office_certificates[loan_office_certificates["matched_status"]]["raw_name_state"].nunique()
print("total unique names: " + str(total_unique_names))
print("total unique matched names: " + str(total_unique_matched_names))

print((total_unique_matched_names / total_unique_names) * 100)


# ## Average Amoung Held By Matches VS Non-Matches

# In[149]:


# filter only for matched rows
matched_df = loan_office_certificates[loan_office_certificates["matched_status"]]
# group rows by individuals, summing their certificates
grouped_matched = matched_df.groupby("raw_name_state")["Face Value"].sum()


# In[150]:


# calculate average
average_matched = grouped_matched.mean()
print(average_matched)


# In[151]:


# filter only for non-matched rows
nonmatched_df = loan_office_certificates[~loan_office_certificates["matched_status"]]
print(str(nonmatched_df.shape[0]) + " total rows")

grouped_nonmatched = nonmatched_df.groupby("raw_name_state")["Face Value"].sum()


# In[152]:


# calculate average
average_nonmatched = grouped_nonmatched.mean()
print(average_nonmatched)


# In[153]:


average_matched - average_nonmatched


# ## Comparing Holdings Before and After 1790

# In[154]:


# create reconcile id column that corresponds to "A[column + 2]:Z[column + 2]"
post_1790["recon_id"] = post_1790["Column"].apply(lambda x: f"A{x + 2}:Z{x + 2}")
post_1790["recon_id"].head()


# In[155]:


# get a list of reconcile ids from matched names from pre-1790 dataset
matched_recon_ids = loan_office_certificates.loc[loan_office_certificates["matched_status"], "recon_id"].dropna().unique()
print("example: " + matched_recon_ids[0]) # expect: A3339:Z3339


# In[156]:


# create a matched_status column in post-1790 dataset
post_1790["matched_status"] = post_1790["recon_id"].isin(matched_recon_ids) 
count = len(post_1790[post_1790["matched_status"] == True])
print(count)


# In[157]:


# see how many names were missed
matched_names_set = set(loan_office_certificates.loc[loan_office_certificates["matched_status"], "recon_id"].dropna().unique())
post_names_set = set(post_1790["recon_id"].unique())

# get a set of all missed names
missing = matched_names_set - post_names_set
print(f"{len(missing)} names from pre-1790 matched list not found in post-1790:")
print(sorted(missing))


# In[158]:


# get total owned by matches in pre-1790 dataset
total_matched_pre = loan_office_certificates.loc[loan_office_certificates["matched_status"], "Face Value"].sum()
# get total owned by matches in post-1790 dataset
total_matched_post = post_1790.loc[post_1790["matched_status"], "final_total_adj"].sum()
print(f"total owned by matches (pre-1790): ${total_matched_pre:.2f}")
print(f"total owned by matches (post-1790): ${total_matched_post:.2f}")


# In[159]:


post_1790["raw_name_state"] = post_1790["Group Name"].str.upper() + "||" + post_1790["state"]
post_1790.head()


# In[160]:


# save post-1790 file with matched_status for future use
post_1790.to_csv(OUTDIR / "post_1790_with_matched_status.csv", index=False)


# In[161]:


loan_office_certificates["raw_name_state"].head()


# In[162]:


post_1790["raw_name_state"].head()


# In[163]:


# calculate percent change per person

# group individuals by their reconcile id with their pre-1790 and post-1790 sums
pre_totals = loan_office_certificates.groupby(["recon_id", "raw_name_state"])["Face Value"].sum().rename("pre_value")
post_totals = post_1790.groupby(["recon_id", "raw_name_state"])["final_total_adj"].sum().rename("post_value")


# In[164]:


# pull out recon_id and occupation rows from the post 1790 dataset
occ_map = (
    post_1790
      .drop_duplicates(subset="recon_id")
      .loc[:, ["recon_id", "occupation", "Group Town"]]
)


# In[165]:


# combine reconcile id, pre-1790 sum, post-1790 sum into a single data frame
# combined = pd.concat([pre_totals, post_totals], axis=1).reset_index()
combined = (
    pre_totals.to_frame()
    .merge(post_totals.to_frame(), on="recon_id", how="inner")  # <- only IDs in both
    .reset_index()
    .merge(occ_map, on="recon_id", how="left")
)
combined.tail()


# In[166]:


print(combined.head())


# In[167]:


print(combined["recon_id"].nunique())


# In[168]:


# create a new percent change column
combined["percent_change"] = (combined["post_value"] - combined["pre_value"]) / combined["pre_value"] * 100


# In[169]:


# inspect first few results
combined.head()


# In[170]:


min_percent = combined["percent_change"].min()
max_percent = combined["percent_change"].max()

# create two panels: one full and one zoomed-in
fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True, figsize=(10,4),
                               gridspec_kw={"width_ratios":[3,1]})

# Main zoomed view
bins_zoom = list(range(int(min_percent), 501, 20))
ax1.hist(combined["percent_change"], bins=bins_zoom, edgecolor='black')
ax1.set_xlim(int(min_percent), 500)
ax1.set_title("Zoomed")
ax1.set_xlabel("Percent Change")

# Full-range view
bins_full = [min_percent,-50,-25,0,25,50,100,200,500,1000,2000,4000,max_percent]
ax2.hist(combined["percent_change"], bins=bins_full, edgecolor='black')
ax2.set_xlim(-100,8000)
ax2.set_title("Full Range")
ax2.set_xlabel("Percent Change")

fig.suptitle("Distribution of % Change in Holdings")
ax1.set_ylabel("Number of Individuals")
plt.tight_layout()
plt.show()


# In[171]:


# see outliers
outliers = combined.sort_values(by="percent_change", ascending=False)
print(outliers.head(10))


# In[172]:


# convert table to latex
print(outliers.head(10).to_latex())


# In[173]:


# how many doubled their holdings
increased = outliers[outliers["percent_change"] > 100]
count_large = len(increased)
print(count_large / len(combined))


# In[174]:


# find average percent change
combined["percent_change"].median()


# In[175]:


# find top 5 debtholders in loan office certificates
top5_debtholders = loan_office_certificates.groupby("raw_name_state")["Face Value"].sum().nlargest(5)
print(top5_debtholders)


# ## Geographical Analysis

# In[176]:


# get all the matched names
print(len(matched_df) / len(loan_office_certificates))


# In[177]:


# get percent of total records in loan_office_certificates
states_total = loan_office_certificates.groupby("state")["raw_name_state"].nunique().sort_values(ascending=False)
pct_states_total = states_total / states_total.sum() * 100
pct_states_total.name = "percent total"
print(pct_states_total)


# In[178]:


matched_states = matched_df.groupby("state")["recon_id"].nunique().sort_values(ascending=False)
matched_states.head()


# In[179]:


# group by state
matched_states.name = "debtholders"
pct = matched_states / matched_states.sum() * 100
pct.name = "percent matched"
matched_states = pd.concat([matched_states, pct, pct_states_total], axis=1)
matched_states.reset_index(inplace=True)
print(matched_states)


# In[180]:


latex_str = matched_states.to_latex()
print(latex_str)


# In[181]:


# draw map
fig = px.choropleth(
    matched_states,
    locations='state',                    
    locationmode='USA-states',             
    color='percent matched',              
    scope='usa',                           
    color_continuous_scale='OrRd',         
    labels={'percent matched':'% Matched'},
    title='Percent Matched by State'
)

fig.update_layout(margin=dict(l=10, r=10, t=50, b=10))
fig.show()


# ## Most Common Occupations

# In[182]:


# get all matched individuals in the post-1790 dataset
post_1790_matched = post_1790[post_1790["matched_status"]]
post_1790_matched.head()


# In[183]:


# 1) build the Series of sums (once)
pre_totals = (
    matched_df
      .groupby("recon_id")["Face Value"]
      .sum()
      .rename("pre_1790_total")
)

# 2) on your post-1790 DF, lookup & overwrite that column every time
post_1790_matched["pre_1790_total"] = (
    post_1790_matched["recon_id"]
      .map(pre_totals)    
      .fillna(0)          
)
post_1790_matched.head()


# In[184]:


# group by occupation
occupation_counts = post_1790_matched.groupby("occupation").agg(
    count = ("occupation", "size"),
    pre_1790_total = ("pre_1790_total", "sum"),
    post_1790_total = ("final_total_adj", "sum")
).sort_values("count", ascending=False)

# compute the overall sum
total_post1790 = occupation_counts['post_1790_total'].sum()
total_pre1790 = occupation_counts['pre_1790_total'].sum()

# create the percent‐of‐total column
occupation_counts['percent_of_pre1790_total'] = occupation_counts['pre_1790_total'] / total_pre1790 * 100
occupation_counts['percent_of_post1790_total'] = occupation_counts['post_1790_total'] / total_post1790 * 100

print(occupation_counts)


# In[185]:


# calcualate net change between pre_1790 and post_1790 datasets
occupation_counts["net_pct_change"] = (
    (occupation_counts["post_1790_total"] - occupation_counts["pre_1790_total"])
    / occupation_counts["pre_1790_total"]
    * 100
)
occupation_counts.head()


# In[186]:


print(occupation_counts.head().to_latex())


# In[187]:


# total number of occupations
print(occupation_counts.sum())


# In[188]:


unique_with_title = loan_office_certificates.loc[loan_office_certificates['raw_title'].notna(), 'raw_name_state'].nunique()
print(f"{unique_with_title} individuals have a title")

# Count total unique individuals
total_individuals = loan_office_certificates['raw_name_state'].nunique()

percent_with_title = unique_with_title / total_individuals * 100
print(f"{percent_with_title:.2f}% of individuals have a title")


# ## Ratios

# In[189]:


import numpy as np


# In[190]:


post_matched = post_1790[post_1790["matched_status"] == True].copy()
print(len(post_matched))


# In[191]:


# aggregate each person's 6p and def 6p stock
summary = (
    post_matched
    .groupby("recon_id")[["6p_total_adj", "6p_def_total_adj"]]
    .sum()
    .rename(columns={
        "6p_total_adj":      "six_percent_amt",
        "6p_def_total_adj":  "deferred_amt"
    })
)
print(summary.head())


# In[192]:


# compute ratios
summary["post_total"] = summary["six_percent_amt"] + summary["deferred_amt"]
summary["ratio_six"] = summary["six_percent_amt"]  / summary["post_total"]
summary["ratio_deferred"] = summary["deferred_amt"]    / summary["post_total"]
print(summary.head())


# In[193]:


# turn pre_totals (type: series) into a dataframe
pre_totals = pre_totals.rename("pre_total").reset_index()
pre_totals.head()


# In[194]:


# add pre_1790 totals
summary = summary.reset_index().merge(
    pre_totals.rename(columns={"Face Value":"pre_total"}),  # or however you named it
    on="recon_id",
    how="left"
)
summary.head()


# In[195]:


# compute expected dollar amounts
EXPECTED_SIX, EXPECTED_DEF = 2/3, 1/3
summary["expected_six_amt"]      = summary["pre_total"] * EXPECTED_SIX
summary["expected_deferred_amt"] = summary["pre_total"] * EXPECTED_DEF
summary.head()


# In[196]:


# flag those within a small tolerance of the ideal 66.67% / 33.33%
tol = 0.005  # ±0.5%
summary["in_ratio_tolerance"] = summary["ratio_six"].between(
    EXPECTED_SIX - tol, EXPECTED_SIX + tol
)
summary.head()


# In[197]:


# quick summary statistics
print(f"Fraction matching within ±{tol*100:.1f}%-points: ",
      summary["in_ratio_tolerance"].mean())
summary.head()


# ## How Many Names Were Women?

# In[198]:


# source: https://www.reddit.com/r/namenerds/comments/v7il84/most_popular_baby_names_in_the_usa_1780/
female_names_1780 = {
    "Mary", "Elizabeth", "Sarah", "Hannah", "Nancy", "Margaret", "Anna",
    "Jane", "Catherine", "Lydia", "Martha", "Ann", "Rebecca", "Abigail",
    "Sally", "Catharine", "Betsey", "Polly", "Lucy", "Rachel", "Susannah",
    "Ruth", "Esther", "Maria", "Phebe", "Susan", "Eunice", "Susanna",
    "Barbara", "Rhoda", "Deborah", "Olive", "Eleanor", "Charlotte",
    "Frances", "Sophia", "Catharina", "Clarissa", "Anne", "Mercy", "Lois",
    "Magdalena", "Dorcas", "Amy", "Betsy", "Cynthia", "Fanny", "Eliza",
    "Charity", "Christina", "Lucinda", "Chloe", "Joanna", "Elisabeth",
    "Alice", "Huldah", "Jemima", "Isabella", "Patience", "Jerusha",
    "Judith", "Mehitable", "Prudence", "Agnes", "Priscilla", "Julia",
    "Ellen", "Dorothy", "Harriet", "Dolly", "Keziah", "Thankful", "Marie",
    "Matilda", "Lucretia", "Temperance", "Tabitha", "Rachael", "Phoebe",
    "Asenath", "Eve", "Salome", "Amelia", "Grace", "Patty", "Persis",
    "Comfort", "Eva", "Hester", "Louisa", "Naomi", "Rebekah", "Bridget",
    "Freelove", "Katherine", "Leah", "Caroline", "Marcy", "Annie", "Azubah"
}

print(len(female_names_1780))


# In[199]:


def is_female_name(raw_first_name, female_set=female_names_1780):
    """
    Returns True if the given first name (string) appears in the 1780 female names list.
    """
    if not isinstance(raw_first_name, str) or not raw_first_name.strip():
        return False
    # take the first token, strip punctuation, capitalize
    first = raw_first_name.strip().split()[0].strip(".,").capitalize()
    return first in female_set


# In[200]:


# extract first name, reformat, and check if it is in female names list
loan_office_certificates_copy = loan_office_certificates.copy()
print("before dropping duplicates: " + str(len(loan_office_certificates_copy)))
loan_office_certificates_copy = loan_office_certificates_copy.drop_duplicates(subset="raw_name_state")
loan_office_certificates_copy["is_female"] = loan_office_certificates_copy["raw_first_name_1"].apply(is_female_name)
print("after dropping duplicates: " + str(len(loan_office_certificates_copy)))
loan_office_certificates_copy.head()


# In[201]:


# compute percent women
pct_women_loan_office = loan_office_certificates_copy["is_female"].mean() * 100
print(f"{pct_women_loan_office:.2f}% of unique loan office certificate debtholders were likely women")


# In[202]:


# do the same for liquidated debt certificates
liquidated_debt_certificates = pd.read_csv(INDIR / "liquidated_debt_certificates.csv")
liquidated_debt_certificates.rename(columns={'uid': 'raw_name_state'}, inplace=True)
print("before dropping duplicates: " + str(len(liquidated_debt_certificates)))
liquidated_debt_certificates = liquidated_debt_certificates.drop_duplicates(subset="raw_name_state")
liquidated_debt_certificates["is_female"] = liquidated_debt_certificates["raw_first_name_1"].apply(is_female_name)
print("after dropping duplicates: " + str(len(liquidated_debt_certificates)))
liquidated_debt_certificates.head()


# In[203]:


# compute percent women
pct_women_liquidated = liquidated_debt_certificates["is_female"].mean() * 100
print(f"{pct_women_liquidated:.2f}% of unique liquidated debt certificate debtholders were likely women")


# In[204]:


# do the same for pierce certificates (we expect 0)
pierce_certificates = pd.read_csv(INDIR / "pierce_certificates.csv")
print("before dropping duplicates: " + str(len(pierce_certificates)))
pierce_certificates = pierce_certificates.drop_duplicates(subset="raw_name_state")
pierce_certificates["is_female"] = pierce_certificates["raw_first_name_1"].apply(is_female_name)
print("after dropping duplicates: " + str(len(pierce_certificates)))

print(pierce_certificates[pierce_certificates["is_female"]].head())
# compute percent women
pct_women_pierce = pierce_certificates["is_female"].mean() * 100
print(f"{pct_women_pierce:.2f}% of unique pierce certificate debtholders were likely women")


# In[205]:


def extract_first_name(full_name):
    first = full_name.strip().split()[0]
    return first.strip(".,").capitalize()


# In[206]:


# do the same for the post-1790 dataset
post_1790 = pd.read_csv(INDIR / "post_1790.csv")
post_1790["first_name"] = post_1790["Group Name"].apply(extract_first_name)
print(post_1790["first_name"].head())


post_1790["is_female"] = post_1790["first_name"].apply(is_female_name)
print(post_1790[post_1790["is_female"]].head())

# compute percent women
pct_women_post_1790 = post_1790["is_female"].mean() * 100
print(f"{pct_women_post_1790:.2f}% of unique post-1790 debtholders were likely women")


# In[207]:


pierce_certificates.sample(10)[["raw_name_state","is_female"]]


# ## Ambiguous Matches: Matches That Need More Location Information

# In[208]:


post_1790_matched.head()


# In[209]:


loan_office_certificates.head()


# In[210]:


# Dedupe pre-1790 down to one row per person+state
unique_pre = loan_office_certificates.drop_duplicates(subset="raw_name_state")

# count how many records there are *per* name+state
post_counts = (
    post_1790_matched
      .groupby("raw_name_state")
      .size()
      .reset_index(name="post_count")
)


# Left-join those counts back into unique_pre
merged = unique_pre.merge(post_counts, on="raw_name_state", how="left")

total = len(unique_pre)

# How many have *no* post-1790 match at all?
no_match = (merged["post_count"].fillna(0) == 0).sum()

# How many have *exactly one* post-1790 match?
exactly_one = (merged["post_count"] == 1).sum()

# How many have *more than one* post-1790 match (i.e. ambiguous)?
ambiguous = (merged["post_count"] > 1).sum()

print(f"Total pre-1790 records:        {total}")
print(f"No post-1790 match:            {no_match} ({no_match/total:.1%})")
print(f"Exactly one post-1790 match:   {exactly_one} ({exactly_one/total:.1%})")
print(f"Ambiguous (>1 match):          {ambiguous} ({ambiguous/total:.1%})")


# ## Reconciling on Last Name and State Only

# In[211]:


# record-level coverage:
total_records = len(loan_office_certificates)
matched_records = loan_office_certificates["last_name_matched_status"].sum()
record_level_rate = matched_records / total_records * 100
print(f"Record-level match rate: {record_level_rate:.1f}% ({matched_records}/{total_records})") 


# In[212]:


# distinct-key coverage:
# first collapse to one row per last_name_state
keys = loan_office_certificates.drop_duplicates(subset="last_name_state")
total_keys = len(keys)
matched_keys = keys["last_name_matched_status"].sum()
key_level_rate = matched_keys / total_keys * 100
print(f"Distinct-key match rate: {key_level_rate:.1f}% ({matched_keys}/{total_keys})")


# In[ ]:


# record‐level match rate:
total_records = len(loan_office_certificates)
matched_records = loan_office_certificates['matched_status'].sum()  # assuming True/False or 1/0
record_match_rate = matched_records / total_records * 100

print(f"Record‐level match rate: {record_match_rate:.2f}% "
      f"({matched_records}/{total_records})")


# In[215]:


# distinct‐key match rate on raw_name_state:
unique_keys    = loan_office_certificates.drop_duplicates(subset='raw_name_state')
total_keys     = len(unique_keys)
matched_keys   = unique_keys['matched_status'].sum()
key_match_rate = matched_keys / total_keys * 100

print(f"Distinct-key match rate: {key_match_rate:.2f}% "
      f"({matched_keys}/{total_keys})")

