#!/usr/bin/env python
# coding: utf-8

# In[14]:


from pathlib import Path
import pandas as pd
import recordlinkage
import numpy as np
import timeit
from rapidfuzz import process

OUTDIR = Path("output/derived/pre1790")


# In[15]:


agg_debt = pd.read_csv(OUTDIR / 'agg_debt_grouped.csv')
agg_debt.head()


# In[16]:


agg_debt.loc[agg_debt['org_file'] == 'Pierce_Certs_cleaned_2019.xlsx'].head()


# In[17]:


# Create a full name column because process.extract can only compare one string at a time
agg_debt['full name'] = [' '.join([str(fn), str(ln)]) for fn, ln in zip(agg_debt['to whom due | first name'], agg_debt['to whom due | last name'])]
agg_debt['full name'].head()


# In[18]:


# Remove 'cs' (congress) and 'f' (foreign officers); these are not states, but specific regiments / types of officers
agg_debt_copy = agg_debt[(agg_debt['state'] != 'cs') & (agg_debt['state'] != 'f') & (agg_debt['state'] != 'de')]

# Split dataframe based on state; makes searching faster
agg_debt_sp = agg_debt_copy.groupby('state')
agg_debts_st = [agg_debt_sp.get_group(x) for x in agg_debt_sp.groups]


for st in agg_debt_sp.groups:
    print(st)


# In[19]:


# Remove matches that have a score of 100 
def remove_exact_matches(matches):
    n_matches = []
    for match in matches:
        if match[1] < 100:
            n_matches.append(match)
    return n_matches


# In[20]:


# Remove duplicate matches
def remove_dup_matches(matches):
    visited = {}
    output = []
    for name, score, index in matches:
        # Check if the first value is already present in the dictionary
        if name not in visited:
            visited[name] = True
            output.append((name, score, index))
    return output


# In[21]:


get_ipython().run_cell_magic('timeit', '', "for state in agg_debt_sp.groups:\n    agg_debt_st = agg_debt_sp.get_group(state)\n    # Iterate through each state's dataframe and .extract all the matches for each row \n    agg_debt_st['matches'] = agg_debt_st['full name'].apply(lambda full_name: process.extract(full_name, agg_debt_st['full name'], score_cutoff=90))\n    print(state, str(len(agg_debt_st['matches'])))\n    # Remove matches that have a score of 100 \n    agg_debt_st['matches'] = agg_debt_st['matches'].apply(lambda matches: remove_exact_matches(matches))\n    # Remove duplicate matches\n    agg_debt_st['matches'] = agg_debt_st['matches'].apply(lambda matches: remove_dup_matches(matches)) \n    # Remove rows that have no matches \n    agg_debt_st_clean = agg_debt_st.loc[agg_debt_st.matches.str.len() > 0]\n    # Save as a .csv file\n    agg_debt_st_clean.to_csv(str(OUTDIR / 'similar_names/similar_names_') + state + '.csv')\n")


# In[ ]:




