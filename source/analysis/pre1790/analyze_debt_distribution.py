#!/usr/bin/env python
# coding: utf-8

# <h1>Pre-1790 Data Analysis</h1>
# 
# - Barplot of debt distribution 
# 
# - Debt distribution by gender
# 
# - Top ten richest individual debt holders - biographies 
# 
# If time: find out if any const. convention or society of the cincinatti members had debt holdings 

# <h2>Debt Distribution</h2>
# 
# Two barplots: 
# 1. The total amount of debt held by each bracket 
# 2. The percentage of total debt held by each bracket 
#  

# In[23]:


# import necessary packages and import aggregated debt file
from pathlib import Path
import pandas

INDIR_DERIVED = Path("output/derived/pre1790")
INDIR_DERIVED_POST1790 = Path("output/derived/post1790_cd")
INDIR_MEMBERS = Path("source/raw/society_members/orig")
INDIR_DELEGATES = Path("source/raw/delegates/orig")
OUTDIR = Path("output/analysis/pre1790")
agg_debt = pandas.read_csv(INDIR_DERIVED / "agg_debt_grouped.csv")

# remove rows where no name exists 
agg_debt.drop(agg_debt.loc[agg_debt["to whom due | first name"].isna() & agg_debt["to whom due | last name"].isna()].index, inplace=True)

# new column for total amount of debt
agg_debt[["amount | dollars", "amount in specie | dollars", "amount in specie | cents"]] = agg_debt[["amount | dollars", "amount in specie | dollars", "amount in specie | cents"]].fillna(0)
agg_debt["amount_total"] = agg_debt["amount | dollars"] + agg_debt["amount in specie | dollars"] + agg_debt["amount in specie | cents"]
agg_debt.head()

# create full name column 
agg_debt["full_name"] = agg_debt["to whom due | first name"] + " " + agg_debt["to whom due | last name"]

# sort by amount of debt 
agg_debt_sorted = agg_debt.sort_values(by="amount_total", ascending=False)
agg_debt_sorted.head()


# In[24]:


# split into 4 groups
import numpy as np 
agg_debt_split = np.array_split(agg_debt_sorted, 4)
amounts = [round(agg_debt_split[i]["amount_total"].sum() / 1000000, 2) for i in range(4)]
for i in range(4):
    print(amounts[i])


# In[25]:


# graph amount of debt held by each wealth bracket 
import matplotlib.pyplot as plt
bars = plt.bar(x=range(4), height=amounts, tick_label=["75-100th", "50-75th", "25-50th", "0-25th"])
bars[0].set_color("#e41a1c")
bars[1].set_color("#377eb8")
bars[2].set_color("#4daf4a")
bars[3].set_color("#984ea3")

# add labels 
plt.xlabel("Debt Bracket (percentile)")
plt.ylabel("Amount of Debt (dollars in millions)")
plt.bar_label(bars, padding=1)
plt.title("Amount of Debt Held By Debt Bracket")
plt.savefig(OUTDIR / "debt_by_bracket.png")

boundary_0 = agg_debt_split[0]["amount_total"].iloc[0]
boundary_1 = agg_debt_split[0]["amount_total"].iloc[-1]
boundary_2 = agg_debt_split[1]["amount_total"].iloc[-1]
boundary_3 = agg_debt_split[2]["amount_total"].iloc[-1]
boundary_4 = agg_debt_split[3]["amount_total"].iloc[-1]

number_of_people = [agg_debt_split[i].shape[0] for i in range(4)]

print(number_of_people)

labels = ["$" + str(agg_debt_split[0]["amount_total"].iloc[0]) + " - " + str(agg_debt_split[0]["amount_total"].iloc[-1]), 
          "$" + str(agg_debt_split[1]["amount_total"].iloc[0]) + " - " + str(agg_debt_split[1]["amount_total"].iloc[-1]),
          "$" + str(agg_debt_split[2]["amount_total"].iloc[0]) + " - " + str(agg_debt_split[2]["amount_total"].iloc[-1]),
          "$" + str(agg_debt_split[3]["amount_total"].iloc[0]) + " - " + str(agg_debt_split[3]["amount_total"].iloc[-1])]

handles = [plt.Rectangle((0,0),1,1, color=c, ec="k") for c in ["#e41a1c", "#377eb8", "#4daf4a", "#984ea3"]]

plt.legend(handles=handles, labels=labels)
plt.savefig(OUTDIR / "debt_by_bracket.png")
plt.show()


# In[26]:


# calculate percentage of total wealth each bracket holds 
total_amt = agg_debt["amount_total"].sum() / 1000000
percentages = [round(((amounts[i] / total_amt) * 100), 1) for i in range(4)] 

print(percentages)

# graph percentages # add labels 
plt.bar(["75-100th", "50-75th", "25-50th", "0-25th"], percentages)
plt.xlabel("Debt Bracket (percentile)")
plt.ylabel("Percentage of Total Debt (%)")
plt.bar_label(plt.bar(["75-100th", "50-75th", "25-50th", "0-25th"], percentages), padding=1)
plt.title("Percentage of Total Debt by Debt Bracket")
plt.savefig(OUTDIR / "percent_debt_by_debt_bracket.png")
plt.show()


# <h2>Women Versus Men</h2>
# Barplot: compare amount of debt held by women versus men using NLTK 

# In[27]:


import gender_guesser.detector as gender
d = gender.Detector(case_sensitive=False)

# cast type of first name column to string
agg_debt["to whom due | first name"] = agg_debt["to whom due | first name"].astype(str)


# In[28]:


def count_genders(name):
    if d.get_gender(name, country="usa") == "male":
        print(name)
        return "Male"
    elif d.get_gender(name, country="usa") == "female":
        return "Female"
    else:
        return "Unknown"


# In[29]:


# run gender detector on entire dataset 
agg_debt["gender_prediction"] = agg_debt["to whom due | first name"].apply(count_genders) 
count = agg_debt["gender_prediction"].value_counts(normalize=True) * 100
print(count)


# In[30]:


# graph 
ax = count.plot.bar(xlabel="Gender", ylabel="Percentage of Total Debt Owned (%)", title="Percentage of Total Debt Owned by Gender")
ax.bar_label(ax.containers[0], padding=1)


# <h2>Top Ten Debt Holders</h2>
# 
# I researched the top ten debt holders from the pre-1790 data to find additional information and individual biographies. 
# 
# https://docs.google.com/document/d/1osUkB6xTnMBxe5OmWnL07VEh2e97iFr1a9YNku51MBc/edit?usp=sharing 

# In[31]:


# get the top ten debt holders from sorted dataset
richest_names = agg_debt_sorted.head(10)[["to whom due | first name", "to whom due | last name", "amount_total", "state", "date of the certificate | year"]]
richest_names


# In[32]:


agg_debt.columns


# <h2>Society of Cincinatti Members and Debt Holdings</h2>
# 
# 1. Find all members of the Society of Cincinatti who held debt - dataframe
# 2. Find out the percentage of total debt owned by society members - return a value

# In[33]:


import re 

# remove military titles 
def remove_titles(officer):
    officer = officer.replace("Surgeonâ€™s", "").replace("Surgeon General", "") #remove doctor titles 

    if '.' in officer:
        return re.sub(',[^.]+.', ',', officer) 

    return officer


# In[34]:


def clean(name_list):
    i = 0
    while i < len(name_list):
        name_list[i] = re.sub("\(.*?\)","", name_list[i]) # remove parantheses and everything inside them
        name_list[i] = name_list[i].replace(" and ", "") # remove '... and ...' 
        name_list[i] = re.sub("\[.*?\]","", name_list[i]) # remove [...]
        name_list[i] = remove_titles(name_list[i]) # remove titles 
        name_list[i] = name_list[i].strip() # remove endspaces 
        i += 1
    
    return name_list        


# In[35]:


# open file with all members of the society
all_officers = open(INDIR_MEMBERS / "all_officers_ari.txt", "r") 
all_officers = all_officers.read().splitlines() 
all_officers = [value for value in all_officers if value != '']

# get only massachusetts officers (state with most unclear names) 
mass_officers = []
for officer in all_officers:
    state = officer[officer.find("(")+1:officer.find(")")]
    if state == "Massachusetts":
        mass_officers.append(officer)

# remove military titles 
i = 0
while i < len(mass_officers):
    mass_officers[i] = remove_titles(remove_titles(mass_officers[i])) # running twice handles those who have two titles 
    mass_officers[i] = re.sub("\(.*?\)","", mass_officers[i])
    i += 1

# swap first and last names 
i = 0
while i < len(mass_officers):
    full_name_swapped = mass_officers[i].split(",")[1] + mass_officers[i].split(",")[0]
    full_name_swapped = full_name_swapped.strip()
    mass_officers[i] = full_name_swapped
    i += 1

# run cleaning function 
mass_officers = clean(mass_officers) 

print(mass_officers)


# In[36]:


# import society members from each state
total_members = 0 
meta_register = {} # store all members in a dictionary with state as key and list of members as value

ct_file = open(INDIR_MEMBERS / "connecticut.txt", "r")
ct_members = ct_file.read().split(",")
ct_members = clean(ct_members)
meta_register["ct"] = ct_members
total_members += len(ct_members)
#ct_members

de_file = open(INDIR_MEMBERS / "delaware.txt", "r") 
de_members = de_file.read().split(",")
de_members = clean(de_members)
meta_register["de"] = de_members 
total_members += len(de_members)
#de_members

ga_file = open(INDIR_MEMBERS / "georgia.txt", "r")
ga_members = ga_file.read().split(",")
ga_members = clean(ga_members)
meta_register["ga"] = ga_members 
total_members += len(ga_members)
#ga_members 

md_file = open(INDIR_MEMBERS / "maryland.txt", "r")
md_members = md_file.read().split(",")
md_members = clean(md_members)
meta_register["md"] = md_members
total_members += len(md_members)
#md_members

nh_file = open(INDIR_MEMBERS / "new_hampshire.txt", "r")
nh_members = nh_file.read().split(",")
nh_members = clean(nh_members)
meta_register["nh"] = nh_members
total_members += len(nh_members)
#nh_members

nj_file = open(INDIR_MEMBERS / "new_jersey.txt", "r")
nj_members = nj_file.read().split(",")
nj_members = clean(nj_members)
meta_register["nj"] = nj_members
total_members += len(nj_members)
#nj_members 

ny_file = open(INDIR_MEMBERS / "new_york.txt", "r")
ny_members = ny_file.read().split(",")
ny_members = clean(ny_members)
meta_register["ny"] = ny_members
total_members += len(ny_members)
#ny_members

pa_file = open(INDIR_MEMBERS / "pennsylvania.txt", "r")
pa_members = pa_file.read().split(",")
pa_members = clean(pa_members)
meta_register["pa"] = pa_members
total_members += len(pa_members)
#pa_members

ri_file = open(INDIR_MEMBERS / "rhode_island.txt", "r")
ri_members = ri_file.read().split(",")
ri_members = clean(ri_members)
meta_register["ri"] = ri_members
total_members += len(ri_members)
#ri_members

va_file = open(INDIR_MEMBERS / "virginia.txt", "r")
va_members = va_file.read().split(",")
va_members = clean(va_members)
meta_register["va"] = va_members
total_members += len(va_members)
#va_members

nc_file = open(INDIR_MEMBERS / "north_carolina.txt", "r")
nc_members = nc_file.read().split(",")
nc_members = clean(nc_members)
meta_register["nc"] = nc_members
total_members += len(nc_members)
#nc_members


# In[37]:


# check for repeated names in the society of the cinccinati list 

# combine all members into one list
all_members = []
for key in meta_register:
    all_members += meta_register[key]

# check for repeated names
repeated_names = []
for name in all_members:
    if all_members.count(name) > 1:
        repeated_names.append(name)

print(repeated_names)
        


# In[38]:


# create dataframe with only society members
members_owned_debt = pandas.DataFrame(columns=["full_name", "amount_total", "state", "org_file"])
for state in meta_register:
    society_members_per_state = agg_debt[agg_debt["full_name"].isin(meta_register[state]) & agg_debt["state"].isin([state])]
    members_owned_debt = pandas.concat([members_owned_debt, society_members_per_state[["full_name", "amount_total", "state", "org_file"]]], ignore_index=True)
members_owned_debt.tail()


# In[39]:


# find out how many members own debt
num_owned_debt = len(members_owned_debt["full_name"].unique())
print(num_owned_debt)


# In[40]:


# group by name and state
funcs = {"amount_total": "sum", "org_file": "first"}
members_owned_debt = members_owned_debt.groupby(["full_name", "state"]).agg(funcs).reset_index()
members_owned_debt.tail()


# In[41]:


# save to csv
members_owned_debt.to_csv(OUTDIR / "members/members_owned_debt.csv")


# In[42]:


# calculate the percentage of cincinatti members that owned debt 
(num_owned_debt / total_members) * 100


# In[43]:


agg_debt 


# In[44]:


# calculate the percentage of total debt owned by cincinatti members
(members_owned_debt["amount_total"].sum() / agg_debt["amount_total"].sum()) * 100


# <h1>Constitutional Convention Delegates</h1>

# In[45]:


const_delegates = pandas.read_csv(INDIR_DELEGATES / "constitutional_convention_1787.csv")
const_delegates["full_name"] = const_delegates["first name"] + " " + const_delegates["last name"]
const_delegates["state"] = const_delegates["state"].str.strip()

# map state names to abbreviations
state_map = {"Connecticut": "ct", "Delaware": "de", "Georgia": "ga", "Maryland": "md", "Massachusetts": "ma", "New Hampshire": "nh", "New Jersey": "nj", "New York": "ny", "North Carolina": "nc", "Pennsylvania": "pa", "Rhode Island": "ri", "South Carolina": "sc", "Virginia": "va"}
const_delegates["state"] = const_delegates["state"].map(state_map)
const_delegates.head()


# In[46]:


agg_debt.head()


# In[47]:


# create dataframe with only state delegate members that held debt 
exists_in_both = const_delegates.merge(agg_debt, on=["full_name", "state"], how="inner")
exists_in_both = exists_in_both[["full_name", "amount_total", "state"]]
exists_in_both_gdf = exists_in_both.groupby(["full_name", "state"]).agg({"amount_total": "sum"}).reset_index()
exists_in_both_gdf


# In[48]:


const_delegates.head()


# <h1>State Delegates</h1>

# In[49]:


# create dataframe with only state delegate members
state_delegates = pandas.read_csv(INDIR_DELEGATES / "state_delegates.csv")
state_delegates["First Name"] = state_delegates["First Name"].fillna("")
state_delegates["Last Name"] = state_delegates["Last Name"].fillna("")
state_delegates["full_name"] = state_delegates["First Name"] + " " + state_delegates["Last Name"] 
state_delegates["state"] = state_delegates["State"].str.lower()
state_delegates.head()


# In[50]:


# check post 1790 data 
agg_debt = pandas.read_csv(INDIR_DERIVED_POST1790 / "final_data_CD.csv")
agg_debt["state"] = agg_debt["Group State"].str.lower()
agg_debt["full_name"] = agg_debt["Group Name"]
agg_debt["amount_total"] = agg_debt["final_total_adj"]
agg_debt.head()


# In[51]:


# create dataframe with only state delegate members that held debt 
exists_in_both = state_delegates.merge(agg_debt, on=["full_name", "state"], how="inner")
exists_in_both = exists_in_both[["full_name", "amount_total", "state"]]
exists_in_both_gdf = exists_in_both.groupby(["full_name", "state"]).agg({"amount_total": "sum"}).reset_index()
exists_in_both_gdf
#exists_in_both_gdf.to_csv(OUTDIR / "members/state_delegates_owned_debt.csv")


# In[52]:


print(len(exists_in_both_gdf) / len(state_delegates))


# In[ ]:





# In[53]:


# calculate the percentage of total debt owned by state delegates
(exists_in_both_gdf["amount_total"].sum() / agg_debt["amount_total"].sum()) * 100

