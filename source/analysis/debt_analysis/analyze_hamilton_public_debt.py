#!/usr/bin/env python
# coding: utf-8

# In[8]:


from pathlib import Path
import pandas as pd

INDIR_DERIVED = Path("output/derived/post1790_cd")
data_path = INDIR_DERIVED / 'final_data_CD.csv'
debt_data = pd.read_csv(data_path)


# In[9]:


names = [
    "Jedediah Huntington", "Peter Colt", "John Gordon", "John Gibbons", "John Meals",
    "Benjamin Hardwood", "John Haywood", "John Taylor Gilman", "William Gardner",
    "Oliver Peabody", "Nathaniel Gilman", "John Stevens", "Gerard Bancker",
    "David Rittenhouse", "Henry Sherburne", "Thomas Taylor"
]
states = ["CT", "DE", "GA", "MA", "MD", "NC", "NH", "NJ", "NY", "PA", "RI", "SC"]


# In[10]:


state_patterns = ["state of " + state.lower() for state in states] + ["commonwealth of " + state.lower() for state in states]

filtered_data = debt_data[
    (debt_data["Group State"].isin(states)) |
    (debt_data["Group Name"].isin(names)) |
    (debt_data["Group Name"].str.lower().isin(state_patterns))
]


# In[11]:


public_debt = filtered_data.groupby('Group State')['final_total_adj'].sum().reindex(states, fill_value=0)

debt_summary = pd.DataFrame({
    "State": states,
    "Private Debt": [0] * len(states), 
    "Public Debt": public_debt.values.astype(int)  
})


# In[13]:


print(debt_summary)


# In[ ]:




