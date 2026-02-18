#!/usr/bin/env python
# coding: utf-8

from pathlib import Path
from rapidfuzz import process, fuzz

INDIR_POST1790_CD = Path("source/raw/post1790_cd/orig")
INDIR_POST1790_ASD = Path("source/raw/post1790_asd/orig")
INDIR_DERIVED_POST1790 = Path("output/derived/post1790_cd")
INDIR_DERIVED_PRE1790 = Path("output/derived/pre1790")
OUTDIR = Path("output/analysis/post1790_cd")


# In[3]:


import pandas as pd


# # Post-1790

# ## Virginia

# In[4]:


post1790VA = pd.read_csv('VA_ASD.csv')


# In[5]:


#Detect date values over 31
VA_mask_strange_date =  (
    (pd.to_numeric(post1790VA['Def_6p_Day'], errors='coerce') >31) |
    (pd.to_numeric(post1790VA['6p_Day'], errors='coerce') >31) |
    (pd.to_numeric(post1790VA['3p_Day'], errors='coerce') >31)
)
print(f'\nAmount of dates over 31: {VA_mask_strange_date}')


# In[6]:


#Detect month values over 12
VA_mask_strange_month =  (
    (pd.to_numeric(post1790VA['Def_6p_Month'], errors='coerce') >12) |
    (pd.to_numeric(post1790VA['6p_Month'], errors='coerce') >12) |
    (pd.to_numeric(post1790VA['3p_Month'], errors='coerce') >12)
)
print(f'\nAmount of months over 12: {VA_mask_strange_month}')


# In[7]:


#Detect year values under 1790
VA_mask_strange_year =  (
    (pd.to_numeric(post1790VA['Def_6p_Year'], errors='coerce') <1790) |
    (pd.to_numeric(post1790VA['6p_Year'], errors='coerce') <1790) |
    (pd.to_numeric(post1790VA['3p_Year'], errors='coerce') <1790)
)
print(f'\nAmount of years under 1790: {VA_mask_strange_year}')


# ### Preview of Very Similar Names:

# In[8]:


# columns to check separately
VA_columns_to_check = ['6p_First_Name', '6p_Last_Name', 'Def_6p_First_Name', 'Def_6p_Last_Name', '3p_First_Name', '3p_Last_Name']

threshold = 90
all_matches = []

for col in VA_columns_to_check:
    VA_unique_vals = post1790VA[col].dropna().unique().tolist()
    
    for val in VA_unique_vals:
        result = process.extract(val, VA_unique_vals, scorer=fuzz.token_sort_ratio)
        
        for match_val, score, _ in result:
            if val != match_val and score >= threshold:
                all_matches.append((col, val, match_val, score))

# Convert to DataFrame to review
VA_fuzzy_matches = pd.DataFrame(all_matches, columns=['Column', 'Original', 'Match', 'Score'])
print(VA_fuzzy_matches)


# ## South Carolina

# In[9]:


post1790SC = pd.read_csv('Post_1790_South_Carolina_CD.csv')


# In[10]:


#Detect date values over 31
SC_mask_strange_date =  (
    (pd.to_numeric(post1790SC['Def_6p_Day'], errors='coerce') >31) |
    (pd.to_numeric(post1790SC['6p_Day'], errors='coerce') >31) |
    (pd.to_numeric(post1790SC['3p_Day'], errors='coerce') >31)
)
print(f'\nAmount of dates over 31: {SC_mask_strange_date}')


# In[11]:


#Detect month values over 12
SC_mask_strange_month =  (
    (pd.to_numeric(post1790SC['Def_6p_Month'], errors='coerce') >12) |
    (pd.to_numeric(post1790SC['6p_Month'], errors='coerce') >12) |
    (pd.to_numeric(post1790SC['3p_Month'], errors='coerce') >12)
)
print(f'\nAmount of months over 12: {SC_mask_strange_month}')


# In[12]:


#Detect year values under 1790
SC_mask_strange_year =  (
    (pd.to_numeric(post1790SC['Def_6p_Year'], errors='coerce') <1790) |
    (pd.to_numeric(post1790SC['6p_Year'], errors='coerce') <1790) |
    (pd.to_numeric(post1790SC['3p_Year'], errors='coerce') <1790)
)
print(f'\nAmount of years under 1790: {SC_mask_strange_year}')


# ### Preview of Very Similar Names:

# In[13]:


# columns to check separately
post1790SC.columns = post1790SC.columns.str.strip()
SC_columns_to_check = ['6p_First_Name', '6p_Last_Name', 'Def_6p_First_Name', 'Def_6p_Last_Name', '3p_First_Name', '3p_Last_Name']

threshold = 90
all_matches = []

for col in SC_columns_to_check:
    SC_unique_vals = post1790SC[col].dropna().unique().tolist()
    
    for val in SC_unique_vals:
        result = process.extract(val, SC_unique_vals, scorer=fuzz.token_sort_ratio)
        
        for match_val, score, _ in result:
            if val != match_val and score >= threshold:
                all_matches.append((col, val, match_val, score))

# Convert to DataFrame to review
SC_fuzzy_matches = pd.DataFrame(all_matches, columns=['Column', 'Original', 'Match', 'Score'])
print(SC_fuzzy_matches)


# ## Rhode Island

# In[14]:


post1790RI = pd.read_csv('T653_Rhode_Island_ASD.csv')


# In[15]:


#Detect date values over 31
RI_mask_strange_date =  (
    (pd.to_numeric(post1790RI['Def_6p_Day'], errors='coerce') >31) |
    (pd.to_numeric(post1790RI['6p_Day'], errors='coerce') >31) |
    (pd.to_numeric(post1790RI['3p_Day'], errors='coerce') >31)
)
print(f'\nAmount of dates over 31: {RI_mask_strange_date}')


# In[16]:


#Detect month values over 12
RI_mask_strange_month =  (
    (pd.to_numeric(post1790RI['Def_6p_Month'], errors='coerce') >12) |
    (pd.to_numeric(post1790RI['6p_Month'], errors='coerce') >12) |
    (pd.to_numeric(post1790RI['3p_Month'], errors='coerce') >12)
)
print(f'\nAmount of months over 12: {RI_mask_strange_month}')


# In[17]:


#Detect year values under 1790
RI_mask_strange_year =  (
    (pd.to_numeric(post1790RI['Def_6p_Year'], errors='coerce') <1790) |
    (pd.to_numeric(post1790RI['6p_Year'], errors='coerce') <1790) |
    (pd.to_numeric(post1790RI['3p_Year'], errors='coerce') <1790)
)
print(f'\nAmount of years under 1790: {RI_mask_strange_year}')


# ### Preview of Very Similar Names:

# In[18]:


# columns to check separately
RI_columns_to_check = ['6p_First_Name', '6p_Last_Name', 'Def_6p_First_Name', 'Def_6p_Last_Name', '3p_First_Name', '3p_Last_Name']

threshold = 90
all_matches = []

for col in RI_columns_to_check:
    RI_unique_vals = post1790RI[col].dropna().unique().tolist()
    
    for val in RI_unique_vals:
        result = process.extract(val, RI_unique_vals, scorer=fuzz.token_sort_ratio)
        
        for match_val, score, _ in result:
            if val != match_val and score >= threshold:
                all_matches.append((col, val, match_val, score))

# Convert to DataFrame to review
RI_fuzzy_matches = pd.DataFrame(all_matches, columns=['Column', 'Original', 'Match', 'Score'])
print(RI_fuzzy_matches)


# ## Pennsylvania

# In[19]:


post1790PA = pd.read_csv('PA_post1790_CD.csv')


# In[20]:


#Detect date values over 31
PA_mask_strange_date =  (
    (pd.to_numeric(post1790PA['Def_6p_Day'], errors='coerce') >31) |
    (pd.to_numeric(post1790PA['6p_Day'], errors='coerce') >31) |
    (pd.to_numeric(post1790PA['3p_Day'], errors='coerce') >31)
)
print(f'\nAmount of dates over 31: {PA_mask_strange_date}')


# In[21]:


#Detect month values over 12
PA_mask_strange_month =  (
    (pd.to_numeric(post1790PA['Def_6p_Month'], errors='coerce') >12) |
    (pd.to_numeric(post1790PA['6p_Month'], errors='coerce') >12) |
    (pd.to_numeric(post1790PA['3p_Month'], errors='coerce') >12)
)
print(f'\nAmount of months over 12: {PA_mask_strange_month}')


# In[22]:


#Detect year values under 1790
PA_mask_strange_year =  (
    (pd.to_numeric(post1790PA['Def_6p_Year'], errors='coerce') <1790) |
    (pd.to_numeric(post1790PA['6p_Year'], errors='coerce') <1790) |
    (pd.to_numeric(post1790PA['3p_Year'], errors='coerce') <1790)
)
print(f'\nAmount of years under 1790: {PA_mask_strange_year}')


# ### Preview of Very Similar Names:

# In[23]:


# columns to check separately
PA_columns_to_check = ['6p_First_Name', '6p_Last_Name', 'Def_6p_First_Name', 'Def_6p_Last_Name', '3p_First_Name', '3p_Last_Name']

threshold = 90
all_matches = []

for col in PA_columns_to_check:
    PA_unique_vals = post1790PA[col].dropna().unique().tolist()
    
    for val in PA_unique_vals:
        result = process.extract(val, PA_unique_vals, scorer=fuzz.token_sort_ratio)
        
        for match_val, score, _ in result:
            if val != match_val and score >= threshold:
                all_matches.append((col, val, match_val, score))

# Convert to DataFrame to review
PA_fuzzy_matches = pd.DataFrame(all_matches, columns=['Column', 'Original', 'Match', 'Score'])
print(PA_fuzzy_matches)


# ## New York

# In[24]:


post1790NY = pd.read_csv('NY_1790_ASD.csv')


# In[25]:


#Detect date values over 31
NY_mask_strange_date =  (
    (pd.to_numeric(post1790NY['Def_6p_Day'], errors='coerce') >31) |
    (pd.to_numeric(post1790NY['6p_Day'], errors='coerce') >31) |
    (pd.to_numeric(post1790NY['3p_Day'], errors='coerce') >31)
)
print(f'\nAmount of dates over 31: {NY_mask_strange_date}')


# In[26]:


#Detect month values over 12
NY_mask_strange_month =  (
    (pd.to_numeric(post1790NY['Def_6p_Month'], errors='coerce') >12) |
    (pd.to_numeric(post1790NY['6p_Month'], errors='coerce') >12) |
    (pd.to_numeric(post1790NY['3p_Month'], errors='coerce') >12)
)
print(f'\nAmount of months over 12: {NY_mask_strange_month}')


# In[27]:


#Detect year values under 1790
NY_mask_strange_year =  (
    (pd.to_numeric(post1790NY['Def_6p_Year'], errors='coerce') <1790) |
    (pd.to_numeric(post1790NY['6p_Year'], errors='coerce') <1790) |
    (pd.to_numeric(post1790NY['3p_Year'], errors='coerce') <1790)
)
print(f'\nAmount of years under 1790: {NY_mask_strange_year}')


# ### Preview of Very Similar Names:

# In[28]:


# columns to check separately
NY_columns_to_check = ['6p_First_Name', '6p_Last_Name', 'Def_6p_First_Name', 'Def_6p_Last_Name', '3p_First_Name', '3p_Last_Name']

threshold = 90
all_matches = []

for col in NY_columns_to_check:
    NY_unique_vals = post1790NY[col].dropna().unique().tolist()
    
    for val in NY_unique_vals:
        result = process.extract(val, NY_unique_vals, scorer=fuzz.token_sort_ratio)
        
        for match_val, score, _ in result:
            if val != match_val and score >= threshold:
                all_matches.append((col, val, match_val, score))

# Convert to DataFrame to review
NY_fuzzy_matches = pd.DataFrame(all_matches, columns=['Column', 'Original', 'Match', 'Score'])
print(NY_fuzzy_matches)


# ## New Jersey

# In[29]:


post1790NJ = pd.read_csv('NJ_3_percent_stock_T698_R1_R2.csv')


# In[30]:


#Detect date values over 31
NJ_mask_strange_date =  (pd.to_numeric(post1790NJ['Day'], errors='coerce') >31)
print(f'\nAmount of dates over 31: {NJ_mask_strange_date}')


# In[31]:


#Detect month values over 12
NJ_mask_strange_month =  (pd.to_numeric(post1790NJ['Month'], errors='coerce') >12)
print(f'\nAmount of dates over 31: {NJ_mask_strange_month}')


# ### Preview of Very Similar Names:

# In[32]:


# columns to check separately
NJ_columns_to_check = ['First_Name', 'Last_Name']

threshold = 90
all_matches = []

for col in NJ_columns_to_check:
    NJ_unique_vals = post1790NJ[col].dropna().unique().tolist()
    
    for val in NJ_unique_vals:
        result = process.extract(val, NJ_unique_vals, scorer=fuzz.token_sort_ratio)
        
        for match_val, score, _ in result:
            if val != match_val and score >= threshold:
                all_matches.append((col, val, match_val, score))

# Convert to DataFrame to review
NJ_fuzzy_matches = pd.DataFrame(all_matches, columns=['Column', 'Original', 'Match', 'Score'])
print(NJ_fuzzy_matches)


# ## New Hampshire

# In[33]:


post1790NH = pd.read_csv('T652_New_Hampshire_ASD.csv')


# In[34]:


#drop duplicates
post1790NH.drop_duplicates(inplace = True)


# ### Preview of Very Similar Names:

# In[35]:


# columns to check separately
NH_columns_to_check = ['6p_First_Name', '6p_Last_Name', 'Def_6p_First_Name', 'Def_6p_First_Name', '3p_First_Name', '3p_Last_Name']

threshold = 90
all_matches = []

for col in NH_columns_to_check:
    NH_unique_vals = post1790NH[col].dropna().unique().tolist()
    
    for val in NH_unique_vals:
        result = process.extract(val, NH_unique_vals, scorer=fuzz.token_sort_ratio)
        
        for match_val, score, _ in result:
            if val != match_val and score >= threshold:
                all_matches.append((col, val, match_val, score))

# Convert to DataFrame to review
NH_fuzzy_matches = pd.DataFrame(all_matches, columns=['Column', 'Original', 'Match', 'Score'])
print(NH_fuzzy_matches)


# In[36]:


#Detect date values over 31
NH_mask_strange_date =  (
    (pd.to_numeric(post1790NH['Def_6p_Day'], errors='coerce') >31) |
    (pd.to_numeric(post1790NH['6p_Day'], errors='coerce') >31) |
    (pd.to_numeric(post1790NH['3p_Day'], errors='coerce') >31)
)
print(f'\nAmount of dates over 31: {NH_mask_strange_date}')


# In[37]:


#Detect month values over 12
NH_mask_strange_month =  (
    (pd.to_numeric(post1790NH['Def_6p_Month'], errors='coerce') >12) |
    (pd.to_numeric(post1790NH['6p_Month'], errors='coerce') >12) |
    (pd.to_numeric(post1790NH['3p_Month'], errors='coerce') >12)
)
print(f'\nAmount of dates over 31: {NH_mask_strange_month}')


# In[38]:


#Detect year values under 1790
NH_mask_strange_year =  (
    (pd.to_numeric(post1790NH['Def_6p_Year'], errors='coerce') <1790) |
    (pd.to_numeric(post1790NH['6p_Year'], errors='coerce') <1790) |
    (pd.to_numeric(post1790NH['3p_Year'], errors='coerce') <1790)
)
print(f'\nAmount of years before 1790: {NH_mask_strange_year}')


# ## North Carolina

# In[39]:


post1790NC = pd.read_csv('T695_R3_NC_ASD.csv')


# In[40]:


#drop duplicates
post1790NC.drop_duplicates(inplace = True)


# ### Preview of Very Similar Names:

# In[41]:


# columns to check separately
NC_columns_to_check = ['First_Name', 'Last_Name']

threshold = 90
all_matches = []

for col in NC_columns_to_check:
    NC_unique_vals = post1790NC[col].dropna().unique().tolist()
    
    for val in NC_unique_vals:
        result = process.extract(val, NC_unique_vals, scorer=fuzz.token_sort_ratio)
        
        for match_val, score, _ in result:
            if val != match_val and score >= threshold:
                all_matches.append((col, val, match_val, score))

# Convert to DataFrame to review
NC_fuzzy_matches = pd.DataFrame(all_matches, columns=['Column', 'Original', 'Match', 'Score'])
print(NC_fuzzy_matches)


# In[42]:


#Detect date values over 31
NC_mask_strange_date = (pd.to_numeric(post1790NC['Day'], errors='coerce') >31)
print(f'\nAmount of dates over 31: {NC_mask_strange_date}')


# In[43]:


#Detect month values over 12
NC_mask_strange_month = (pd.to_numeric(post1790NC['Month'], errors='coerce') >12)
print(f'\nAmount of month values over 12: {NC_mask_strange_month}')


# In[44]:


#Detect year values under 1790
NC_mask_strange_year = (pd.to_numeric(post1790NC['Year'], errors='coerce') <1790)
print(f'\nAmount of year values under 1790: {NC_mask_strange_year}')


# ## Maryland

# In[45]:


post1790MD = pd.read_csv('MD_post1790_ASD.csv')


# In[46]:


#drop duplicates
post1790MD.drop_duplicates(inplace = True)


# ### Preview of Very Similar Names:

# In[47]:


# columns to check separately
MD_columns_to_check = ['6p_Name', '6p_Last Name', '6p_Def_First_Name', '6p_Def_Last_Name', '3p_First_Name', '3p_Last_Name']

threshold = 90
all_matches = []

for col in MD_columns_to_check:
    MD_unique_vals = post1790MD[col].dropna().unique().tolist()
    
    for val in MD_unique_vals:
        result = process.extract(val, MD_unique_vals, scorer=fuzz.token_sort_ratio)
        
        for match_val, score, _ in result:
            if val != match_val and score >= threshold:
                all_matches.append((col, val, match_val, score))

# Convert to DataFrame to review
MD_fuzzy_matches = pd.DataFrame(all_matches, columns=['Column', 'Original', 'Match', 'Score'])
print(MD_fuzzy_matches)


# In[48]:


#Detect date values over 31
MD_mask_strange_date = (
    (pd.to_numeric(post1790MD['6p_Day'], errors='coerce') >31) | 
    (pd.to_numeric(post1790MD['6p_Def_Day'], errors='coerce') >31) | 
    (pd.to_numeric(post1790MD['3p_Day'], errors='coerce') >31)
)
print(f'\nAmount of dates over 31: {MD_mask_strange_date}')


# In[49]:


#detect months after december
MD_mask_strange_month = (
    (pd.to_numeric(post1790MD['6p_Def_Month'], errors='coerce') >12) |
    (pd.to_numeric(post1790MD['6p_Month'], errors='coerce') >12) |
    (pd.to_numeric(post1790MD['3p_Month'], errors='coerce') >12)
)
print(f'\nAmount of month values over 12: {MD_mask_strange_month}')


# #

# In[50]:


#detect years before 1790
MD_mask_strange_year = (
    (pd.to_numeric(post1790MD['6p_Def_Year'], errors='coerce') <1790) |
    (pd.to_numeric(post1790MD['6p_Year'], errors='coerce') <1790) |
    (pd.to_numeric(post1790MD['3p_Year'], errors='coerce') <1790)
)
print(f'\nAmount of year values under 1790: {MD_mask_strange_year}')


# ## Georgia

# In[51]:


post1790GA = pd.read_csv('T694_GA_Loan_Office_CD.csv')


# In[52]:


#drop duplicates
post1790GA.drop_duplicates(inplace = True)


# ### Preview of Very Similar Names:

# In[53]:


# columns to check separately
GA_columns_to_check = ['First_Name', 'Last_Name', 'First_Name.1']

threshold = 90
all_matches = []

for col in GA_columns_to_check:
    GA_unique_vals = post1790GA[col].dropna().unique().tolist()
    
    for val in GA_unique_vals:
        result = process.extract(val, GA_unique_vals, scorer=fuzz.token_sort_ratio)
        
        for match_val, score, _ in result:
            if val != match_val and score >= threshold:
                all_matches.append((col, val, match_val, score))

# Convert to DataFrame to review
GA_fuzzy_matches = pd.DataFrame(all_matches, columns=['Column', 'Original', 'Match', 'Score'])
print(GA_fuzzy_matches)


# In[54]:


#detect date values over 31
GA_mask_strange_date = pd.to_numeric(post1790GA['Day'], errors='coerce') >31
print(f'\nAmount of dates over 31: {GA_mask_strange_date}')


# In[55]:


#detect month values over 12
GA_mask_strange_month = pd.to_numeric(post1790GA['Month'], errors='coerce') >12
print(f'\nAmount of months listed as after December: {GA_mask_strange_month}')


# In[56]:


#detect year values under 1790 (or equal to)
GA_mask_strange_year = pd.to_numeric(post1790GA['Year'], errors='coerce') < 1790
print(f'\nAmount of years listed as before 1790: {GA_mask_strange_year}')


# ## Connecticut

# In[57]:


post1790CT = pd.read_csv('CT_post1790_CD_ledger.csv')


# In[58]:


#drop duplicates
post1790CT.drop_duplicates(inplace = True)


# In[59]:


#missing values
CT_missing_summary = post1790CT.isnull().sum().to_frame(name = 'CT_missing_count')
CT_missing_summary['CT_missing_percent'] = 100*CT_missing_summary['CT_missing_count']/len(post1790CT)
print("Missing Value Summary:")
print(CT_missing_summary.sort_values('CT_missing_percent', ascending=False))


# In[60]:


#uncombined rows 
CT_amount_fields = ['6p_Dollar', '6p_Cents', 'Def_6p_Dollar', 'Def_6p_Cents','3p_Dollar','3p_Cents']
CT_mask_name_missing = post1790CT[['6p_First_Name',
    '6p_Last_Name',
    'Def_6p_First_Name',
    'Def_6_Last_Name',
    '3p_First_Name',
    '3p_Last_Name'
]].isnull().any(axis=1)
CT_mask_amount_present = post1790CT[CT_amount_fields].notnull().any(axis=1)
CT_mask_uncombined = CT_mask_name_missing & CT_mask_amount_present


# In[61]:


#typos? (more unique values than there should be)
CT_string_cols = post1790CT.select_dtypes(include='object')
CT_string_uniques = CT_string_cols.nunique(dropna=False).to_frame(name='CT_unique_values')
print("Unique value counts for all string columns:")
print(CT_string_uniques.sort_values('CT_unique_values', ascending=False))


# In[62]:


#convert dates to datetime (format)
CT_date_cols = [col for col in post1790CT.columns if ('Month' in col.lower()) or ('Year' in col.lower()) or ('Day' in col.lower())]
for col in CT_date_cols:
    post1790CT[col] = pd.to_datetime(post1790CT[col], errors='coerce')


# In[63]:


#converting numbers to number types (format)
CT_numeric_pattern = ['Dollar', 'Cents']
CT_numeric_obj_cols = [col for col in post1790CT.select_dtypes(include = 'object').columns if any (pat in col for pat in CT_numeric_pattern)]
for col in CT_numeric_obj_cols:
    post1790CT[col] = pd.to_numeric(post1790CT[col].str.replace(',', ''), errors = 'coerce')


# In[64]:


#duplicates (make sure there's no more)
CT_new_dupcount = post1790CT.duplicated().sum()
print('number of duplicates:')
print(CT_new_dupcount)


# In[65]:


#detect negatives
CT_mask_negative = post1790CT[[col for col in post1790CT.columns if any (pat in col for pat in CT_numeric_pattern)]].lt(0).any(axis = 1)
print(f'\nAmount of negative values: {CT_mask_negative.sum()}')


# In[66]:


print(post1790CT.columns)


# In[67]:


#not CT
mask_not_CT = (post1790CT['6p_State'] != 'CT') | (post1790CT['Def_6p_State'] != 'CT') | (post1790CT['3p_State'] != 'CT')
print(f'\nAmount of times the state is not listed as CT: {mask_not_CT.sum()}')


# In[68]:


# columns to check separately
CT_columns_to_check = ['6p_First_Name', '6p_Last_Name', 'Def_6_Last_Name','Def_6p_First_Name','3p_First_Name', '3p_Last_Name']

threshold = 90
all_matches = []

for col in CT_columns_to_check:
    CT_unique_vals = post1790CT[col].dropna().unique().tolist()
    
    for val in CT_unique_vals:
        result = process.extract(val, CT_unique_vals, scorer=fuzz.token_sort_ratio)
        
        for match_val, score, _ in result:
            if val != match_val and score >= threshold:
                all_matches.append((col, val, match_val, score))


# ### Preview of Very Similar Names:

# In[69]:


# Convert to DataFrame to review
CT_fuzzy_matches = pd.DataFrame(all_matches, columns=['Column', 'Original', 'Match', 'Score'])
print(CT_fuzzy_matches)


# ## Aggregated

# In[70]:


post1790 = pd.read_csv(INDIR_DERIVED_POST1790 / 'aggregated_CD_post1790.csv')


# In[71]:


#suspicious rows 
post1790CT['suspicious row'] = False
post1790CT['suspicious reason'] = ''

CT_mask_many_missing = post1790.isnull().sum(axis=1) > post1790.shape[1]/4
post1790CT.loc[CT_mask_many_missing, 'suspicious row'] = True
post1790CT.loc[CT_mask_many_missing, 'suspicious reason'] += 'More than 25% missing'

post1790CT.loc[CT_mask_negative, 'suspicious row'] = True
post1790CT.loc[CT_mask_negative, 'suspicious reason'] += 'Negative value'

post1790CT.loc[CT_mask_uncombined, 'suspicious row'] = True
post1790CT.loc[CT_mask_uncombined, 'suspicious reason'] = 'Uncombined Row, name is missing but amount is not'


# In[72]:


#Rare places (possible typos)
def CT_flag_rare(col_name, threshold):
    CT_counts = post1790CT[col_name].fillna(' ').str.strip().value_counts()
    CT_rare_vals = CT_counts[CT_counts <= threshold].index
    return post1790CT[col_name].fillna(' ').str.strip().isin(CT_rare_vals), CT_rare_vals
rare_threshold = 1 


CT6_mask_rare_town, CT6_rare_towns = CT_flag_rare('6p_Town', rare_threshold)
post1790CT.loc[CT6_mask_rare_town, 'suspicious row'] = True
post1790CT.loc[CT6_mask_rare_town, 'suspicious reason'] += 'Rare town (might be spelled wrong)'

CTDef6_mask_rare_town, CTDef6_rare_towns = CT_flag_rare('Def_6p_Town', rare_threshold)
post1790CT.loc[CTDef6_mask_rare_town, 'suspicious row'] = True
post1790CT.loc[CTDef6_mask_rare_town, 'suspicious reason'] += 'Rare town (might be spelled wrong)'

CT3_mask_rare_town, CT3_rare_towns = CT_flag_rare('3p_Town', rare_threshold)
post1790CT.loc[CT3_mask_rare_town, 'suspicious row'] = True
post1790CT.loc[CT3_mask_rare_town, 'suspicious reason'] += 'Rare town (might be spelled wrong)'

print(f'\nNumber of rare (possibly misspelled) towns: {CT6_mask_rare_town.sum()+CTDef6_mask_rare_town.sum()+CT3_mask_rare_town.sum()}')


# In[73]:


#clean vs suspicious
clean_post1790CT = post1790CT[~post1790CT['suspicious row']]
suspicious_post1790CT = post1790CT[post1790CT['suspicious row']]


# In[74]:


#save clean & suspicious just in case they need to be referred to when scanning errors
clean_post1790CT.to_csv(OUTDIR / "cleaned_CT_post1790_CD_ledger.csv", index=False)
suspicious_post1790CT.to_csv(OUTDIR / "suspicious_CT_post1790_CD_ledger.csv", index=False)


# In[75]:


#print suspicious rows
print(f"Suspicious rows: {post1790CT['suspicious row'].sum()}")
print("\nPreview of Suspicious Rows:")
print(suspicious_post1790CT.head(5))


# In[76]:


#drop duplicates
post1790.drop_duplicates(inplace = True)


# In[77]:


#missing values
missing_summary = post1790.isnull().sum().to_frame(name = 'missing_count')
missing_summary['missing_percent'] = 100*missing_summary['missing_count']/len(post1790)
print("Missing Value Summary:")
print(missing_summary.sort_values('missing_percent', ascending=False))


# In[78]:


#uncombined rows 
amount_fields = ['6p_Dollar', '6p_Cents', '6p_def_Dollar', '6p_def_Cents','3p_Dollar','3p_Cents', '6p_total','6p_def_total','3p_total']
mask_name_missing = post1790['Name'].isnull()
mask_amount_present = post1790[amount_fields].notnull().any(axis=1)
mask_uncombined = mask_name_missing & mask_amount_present


# In[79]:


#typos? (more unique values than there should be)
string_cols = post1790.select_dtypes(include='object')
string_uniques = string_cols.nunique(dropna=False).to_frame(name='unique_values')
print("Unique value counts for all string columns:")
print(string_uniques.sort_values('unique_values', ascending=False))


# In[80]:


#convert dates to datetime (format)
date_cols = [col for col in post1790.columns if 'date' in col.lower()]
for col in date_cols:
    post1790[col] = pd.to_datetime(post1790[col], errors='coerce')


# In[81]:


#converting numbers to number types (format)
numeric_pattern = ['Dollar', 'Cents', 'Total']
numeric_obj_cols = [col for col in post1790.select_dtypes(include = 'object').columns if any (pat in col for pat in numeric_pattern)]
for col in numeric_obj_cols:
    post1790[col] = pd.to_numeric(post1790[col].str.replace(',', ''), errors = 'coerce')


# In[82]:


#duplicates (make sure there's no more)
post1790_new_dupcount = post1790.duplicated().sum()
print('number of duplicates:')
print(post1790_new_dupcount)


# In[83]:


#detect negatives
mask_negative = post1790[[col for col in post1790.columns if any (pat in col for pat in numeric_pattern)]].lt(0).any(axis = 1)
print(f'\aAmount of negative values: {mask_negative.sum()}')


# In[84]:


#Put together full name
post1790['Combined_Name'] = (post1790['First Name'] + ' ' + post1790['Last Name'])
mask_name_mismatch = (post1790['Name'] != post1790['Combined_Name']) 


# In[85]:


#name mismatch
post1790['Name'] = post1790['Name'].fillna('')
post1790['First Name'] = post1790['First Name'].fillna('')
post1790['Last Name'] = post1790['Last Name'].fillna('')
print(f'\nAmount of rows where Name != First Name + Last Name: {mask_name_mismatch.sum()}')


# In[86]:


#not United States
mask_not_US = (post1790['country'] != 'US')
print(f'\nAmount of times the country is not listed as US: {mask_not_US.sum()}')


# In[87]:


#Use correct column name here
unique_names = post1790['Name'].dropna().unique().tolist()


# In[88]:


# Set similarity threshold
threshold = 90
matches = []


# In[89]:


# Find fuzzy matches
for name in unique_names:
    result = process.extract(name, unique_names, scorer=fuzz.token_sort_ratio)
    for match_name, score, _ in result:
        if name != match_name and score >= threshold:
            matches.append((name, match_name, score))


# ### Preview of Very Similar Names:

# In[90]:


# Review results
fuzzy_matches = pd.DataFrame(matches, columns=['Original', 'Match', 'Score'])
print(fuzzy_matches)


# In[91]:


#suspicious rows 
post1790['suspicious row'] = False
post1790['suspicious reason'] = ''

mask_many_missing = post1790.isnull().sum(axis=1) > post1790.shape[1]/4
post1790.loc[mask_many_missing, 'suspicious row'] = True
post1790.loc[mask_many_missing, 'suspicious reason'] += 'More than 25% missing'

post1790.loc[mask_negative, 'suspicious row'] = True
post1790.loc[mask_negative, 'suspicious reason'] += 'Negative value'

post1790.loc[mask_uncombined, 'suspicious row'] = True
post1790.loc[mask_uncombined, 'suspicious reason'] = 'Uncombined Row, name is missing but amount is not'

post1790.loc[mask_name_mismatch, 'suspicious row'] = True
post1790.loc[mask_name_mismatch, 'suspicious reason']= 'Name != First Name + Last Name '


# In[92]:


#Rare places (possible typos)
def flag_rare(col_name, threshold):
    counts = post1790[col_name].fillna(' ').str.strip().value_counts()
    rare_vals = counts[counts <= threshold].index
    return post1790[col_name].fillna(' ').str.strip().isin(rare_vals), rare_vals
rare_threshold = 1 
mask_rare_new_town, rare_new_towns = flag_rare('new_town', rare_threshold)
post1790.loc[mask_rare_new_town, 'suspicious row'] = True
post1790.loc[mask_rare_new_town, 'suspicious reason'] += 'Rare new_town (might be spelled wrong)'

mask_rare_town, rare_towns = flag_rare('town', rare_threshold)
post1790.loc[mask_rare_town, 'suspicious row'] = True
post1790.loc[mask_rare_town, 'suspicious reason'] += 'Rare town (might be spelled wrong)'


mask_rare_county, rare_counties = flag_rare('county', rare_threshold)
post1790.loc[mask_rare_county, 'suspicious row'] = True
post1790.loc[mask_rare_county, 'suspicious reason'] += 'Rare county (might be spelled wrong)'
print(f'\nNumber of rare (possibly misspelled) new towns: {mask_rare_new_town.sum()}')
print(f'\nNumber of rare (possibly misspelled) counties: {mask_rare_county.sum()}')
print(f'\nNumber of rare (possibly misspelled) towns: {mask_rare_town.sum()}')


# In[93]:


#clean vs suspicious
clean_post1790 = post1790[~post1790['suspicious row']]
suspicious_post1790 = post1790[post1790['suspicious row']]


# In[94]:


#save clean & suspicious just in case they need to be referred to when scanning errors
clean_post1790.to_csv(OUTDIR / "cleaned_aggregated_CD_post1790.csv", index=False)
suspicious_post1790.to_csv(OUTDIR / "suspicious_aggregated_CD_post1790.csv", index=False)


# In[95]:


#print suspicious rows
print(f"Suspicious rows: {post1790['suspicious row'].sum()}")
print("\nPreview of Suspicious Rows:")
print(suspicious_post1790.head(5))


# # Pre-1790

# ## Rhode Island

# In[96]:


pre1790RI = pd.read_csv('liquidated_debt_certificates_RI.csv')


# In[97]:


#Detect date values over 31
preRI_mask_strange_date =  (
    (pd.to_numeric(pre1790RI['Day'], errors='coerce') >31) |
    (pd.to_numeric(pre1790RI['Day_Due'], errors='coerce') >31) |
    (pd.to_numeric(pre1790RI['Day_Delivered'], errors='coerce') >31)
)
print(f'\nAmount of dates over 31: {preRI_mask_strange_date}')


# In[98]:


#Detect month values over 12
preRI_mask_strange_month =  (
    (pd.to_numeric(pre1790RI['Month'], errors='coerce') >12) |
    (pd.to_numeric(pre1790RI['Month_Due'], errors='coerce') >12) |
    (pd.to_numeric(pre1790RI['Month_Delivered'], errors='coerce') >12)
)
print(f'\nAmount of months over 12: {preRI_mask_strange_month}')


# In[99]:


#Detect year values over 1790
preRI_mask_strange_year =  (
    (pd.to_numeric(pre1790RI['Year'], errors='coerce') >1790) |
    (pd.to_numeric(pre1790RI['Year_Due'], errors='coerce') >1790) |
    (pd.to_numeric(pre1790RI['Year_Delivered'], errors='coerce') >1790)
)
print(f'\nAmount of years over 1790: {preRI_mask_strange_year}')


# ### Preview of Very Similar Names:

# In[100]:


# columns to check separately
preRI_columns_to_check = ['First_Name', 'Last_Name','First_Name.1','Last_Name.1']

threshold = 90
all_matches = []

for col in preRI_columns_to_check:
    preRI_unique_vals = pre1790RI[col].dropna().unique().tolist()
    
    for val in preRI_unique_vals:
        result = process.extract(val, preRI_unique_vals, scorer=fuzz.token_sort_ratio)
        
        for match_val, score, _ in result:
            if val != match_val and score >= threshold:
                all_matches.append((col, val, match_val, score))

# Convert to DataFrame to review
preRI_fuzzy_matches = pd.DataFrame(all_matches, columns=['Column', 'Original', 'Match', 'Score'])
print(preRI_fuzzy_matches)


# ## Pennsylvania

# In[101]:


pre1790PA = pd.read_csv('liquidated_debt_certificates_PA_stelle.csv')


# In[102]:


#Detect date values over 31
prePA_mask_strange_date =  (
    (pd.to_numeric(pre1790PA['Date'], errors='coerce') >31) |
    (pd.to_numeric(pre1790PA['Date_Due'], errors='coerce') >31)
)
print(f'\nAmount of dates over 31: {prePA_mask_strange_date}')


# In[103]:


#Detect month values over 12
prePA_mask_strange_month =  (
    (pd.to_numeric(pre1790PA['Month'], errors='coerce') >12) |
    (pd.to_numeric(pre1790PA['Month_Due'], errors='coerce') >12)
)
print(f'\nAmount of months over 12: {prePA_mask_strange_month}')


# In[104]:


#Detect year values over 1790
prePA_mask_strange_year =  (
    (pd.to_numeric(pre1790PA['Year'], errors='coerce') >1790) |
    (pd.to_numeric(pre1790PA['Year_Due'], errors='coerce') >1790)
)
print(f'\nAmount of years over 1790: {prePA_mask_strange_year}')


# ### Preview of Very Similar Names:

# In[105]:


# columns to check separately
prePA_columns_to_check = ['First_Name', 'Last_Name','First_Name.1','Last_Name.1']

threshold = 90
all_matches = []

for col in prePA_columns_to_check:
    prePA_unique_vals = pre1790PA[col].dropna().unique().tolist()
    
    for val in prePA_unique_vals:
        result = process.extract(val, prePA_unique_vals, scorer=fuzz.token_sort_ratio)
        
        for match_val, score, _ in result:
            if val != match_val and score >= threshold:
                all_matches.append((col, val, match_val, score))

# Convert to DataFrame to review
prePA_fuzzy_matches = pd.DataFrame(all_matches, columns=['Column', 'Original', 'Match', 'Score'])
print(prePA_fuzzy_matches)


# ## New York

# In[106]:


pre1790NY = pd.read_csv('liquidated_debt_certificates_NY.csv')


# In[107]:


#Detect date values over 31
preNY_mask_strange_date =  (
    (pd.to_numeric(pre1790NY['Day'], errors='coerce') >31) |
    (pd.to_numeric(pre1790NY['Day_Due'], errors='coerce') >31)
)
print(f'\nAmount of dates over 31: {preNY_mask_strange_date}')


# In[108]:


#Detect month values over 12
preNY_mask_strange_month =  (
    (pd.to_numeric(pre1790NY['Month'], errors='coerce') >12) |
    (pd.to_numeric(pre1790NY['Month_Due'], errors='coerce') >12)
)
print(f'\nAmount of months over 12: {preNY_mask_strange_month}')


# In[109]:


#Detect year values over 1790
preNY_mask_strange_year =  (
    (pd.to_numeric(pre1790NY['Year'], errors='coerce') >1790) |
    (pd.to_numeric(pre1790NY['Year_Due'], errors='coerce') >1790)
)
print(f'\nAmount of years over 1790: {preNY_mask_strange_year}')


# ### Preview of Very Similar Names:

# In[110]:


# columns to check separately
preNY_columns_to_check = ['First_Name', 'Last_Name','First_Name.1','Last_Name.1']

threshold = 90
all_matches = []

for col in preNY_columns_to_check:
    preNY_unique_vals = pre1790NY[col].dropna().unique().tolist()
    
    for val in preNY_unique_vals:
        result = process.extract(val, preNY_unique_vals, scorer=fuzz.token_sort_ratio)
        
        for match_val, score, _ in result:
            if val != match_val and score >= threshold:
                all_matches.append((col, val, match_val, score))

# Convert to DataFrame to review
preNY_fuzzy_matches = pd.DataFrame(all_matches, columns=['Column', 'Original', 'Match', 'Score'])
print(preNY_fuzzy_matches)


# ## New Jersey

# In[111]:


pre1790NJ = pd.read_csv('liquidated_debt_certificates_NJ.csv')


# In[112]:


#Detect date values over 31
preNJ_mask_strange_date =  (
    (pd.to_numeric(pre1790NJ['Day'], errors='coerce') >31) |
    (pd.to_numeric(pre1790NJ['Day_Due'], errors='coerce') >31)
)
print(f'\nAmount of dates over 31: {preNJ_mask_strange_date}')


# In[113]:


#Detect month values over 12
preNJ_mask_strange_month =  (
    (pd.to_numeric(pre1790NJ['Month'], errors='coerce') >12) |
    (pd.to_numeric(pre1790NJ['Month_Due'], errors='coerce') >12)
)
print(f'\nAmount of months over 12: {preNJ_mask_strange_month}')


# In[114]:


#Detect year values over 1790
preNJ_mask_strange_year =  (
    (pd.to_numeric(pre1790NJ['Year'], errors='coerce') >1790) |
    (pd.to_numeric(pre1790NJ['Year_Due'], errors='coerce') >1790)
)
print(f'\nAmount of years over 1790: {preNJ_mask_strange_year}')


# ### Preview of Very Similar Names:

# In[115]:


# columns to check separately
preNJ_columns_to_check = ['First_Name', 'Last_Name','First_Name.1','Last_Name.1']

threshold = 90
all_matches = []

for col in preNJ_columns_to_check:
    preNJ_unique_vals = pre1790NJ[col].dropna().unique().tolist()
    
    for val in preNJ_unique_vals:
        result = process.extract(val, preNJ_unique_vals, scorer=fuzz.token_sort_ratio)
        
        for match_val, score, _ in result:
            if val != match_val and score >= threshold:
                all_matches.append((col, val, match_val, score))

# Convert to DataFrame to review
preNJ_fuzzy_matches = pd.DataFrame(all_matches, columns=['Column', 'Original', 'Match', 'Score'])
print(preNJ_fuzzy_matches)


# ## New Hampshire

# In[116]:


pre1790NH = pd.read_csv('liquidated_debt_certificates_NH.csv')


# In[117]:


#Detect date values over 31
preNH_mask_strange_date =  (
    (pd.to_numeric(pre1790NH['Day'], errors='coerce') >31) |
    (pd.to_numeric(pre1790NH['Day_Due'], errors='coerce') >31)
)
print(f'\nAmount of dates over 31: {preNH_mask_strange_date}')


# In[118]:


#Detect month values over 12
preNH_mask_strange_month =  (
    (pd.to_numeric(pre1790NH['Month'], errors='coerce') >12) |
    (pd.to_numeric(pre1790NH['Month_Due'], errors='coerce') >12)
)
print(f'\nAmount of months over 12: {preNH_mask_strange_month}')


# In[119]:


#Detect year values over 1790
preNH_mask_strange_year =  (
    (pd.to_numeric(pre1790NH['Year'], errors='coerce') >1790) |
    (pd.to_numeric(pre1790NH['Year_Due'], errors='coerce') >1790)
)
print(f'\nAmount of years over 1790: {preNH_mask_strange_year}')


# ### Preview of Very Similar Names:

# In[120]:


# columns to check separately
preNH_columns_to_check = ['First_Name', 'Last_Name']

threshold = 90
all_matches = []

for col in preNH_columns_to_check:
    preNH_unique_vals = pre1790NH[col].dropna().unique().tolist()
    
    for val in preNH_unique_vals:
        result = process.extract(val, preNH_unique_vals, scorer=fuzz.token_sort_ratio)
        
        for match_val, score, _ in result:
            if val != match_val and score >= threshold:
                all_matches.append((col, val, match_val, score))

# Convert to DataFrame to review
preNH_fuzzy_matches = pd.DataFrame(all_matches, columns=['Column', 'Original', 'Match', 'Score'])
print(preNH_fuzzy_matches)


# ## Massachusetts

# In[121]:


pre1790MA = pd.read_csv('liquidated_debt_certificates_MA.csv')


# In[122]:


#Detect date values over 31
preMA_mask_strange_date =  (
    (pd.to_numeric(pre1790MA['Date'], errors='coerce') >31) |
    (pd.to_numeric(pre1790MA['Date_Due'], errors='coerce') >31)
)
print(f'\nAmount of dates over 31: {preMA_mask_strange_date}')


# In[123]:


#Detect month values over 12
preMA_mask_strange_month =  (
    (pd.to_numeric(pre1790MA['Month'], errors='coerce') >12) |
    (pd.to_numeric(pre1790MA['Month_Due'], errors='coerce') >12)
)
print(f'\nAmount of months over 12: {preMA_mask_strange_month}')


# In[124]:


#Detect year values over 1790
preMA_mask_strange_year =  (
    (pd.to_numeric(pre1790MA['Year'], errors='coerce') >1790) |
    (pd.to_numeric(pre1790MA['Year_Due'], errors='coerce') >1790)
)
print(f'\nAmount of years over 1790: {preMA_mask_strange_year}')


# ### Preview of Very Similar Names:

# In[125]:


# columns to check separately
preMA_columns_to_check = ['First_Name', 'Last_Name', 'First_Name.1', 'Last_Name.1']

threshold = 90
all_matches = []

for col in preMA_columns_to_check:
    preMA_unique_vals = pre1790MA[col].dropna().unique().tolist()
    
    for val in preMA_unique_vals:
        result = process.extract(val, preMA_unique_vals, scorer=fuzz.token_sort_ratio)
        
        for match_val, score, _ in result:
            if val != match_val and score >= threshold:
                all_matches.append((col, val, match_val, score))

# Convert to DataFrame to review
preMA_fuzzy_matches = pd.DataFrame(all_matches, columns=['Column', 'Original', 'Match', 'Score'])
print(preMA_fuzzy_matches)


# ## Delaware

# In[126]:


pre1790DE = pd.read_csv('liquidated_debt_certificates_DE.csv')


# In[127]:


#Detect date values over 31
preDE_mask_strange_date =  (
    (pd.to_numeric(pre1790DE['Date'], errors='coerce') >31) |
    (pd.to_numeric(pre1790DE['Date_Due'], errors='coerce') >31)
)
print(f'\nAmount of dates over 31: {preDE_mask_strange_date}')


# In[128]:


#Detect month values over 12
preDE_mask_strange_month =  (
    (pd.to_numeric(pre1790DE['Month'], errors='coerce') >12) |
    (pd.to_numeric(pre1790DE['Month_Due'], errors='coerce') >12)
)
print(f'\nAmount of months over 12: {preDE_mask_strange_month}')


# In[129]:


#Detect year values over 1790
preDE_mask_strange_year =  (
    (pd.to_numeric(pre1790DE['Year'], errors='coerce') >1790) |
    (pd.to_numeric(pre1790DE['Year_Due'], errors='coerce') >1790)
)
print(f'\nAmount of years over 1790: {preDE_mask_strange_year}')


# ### Preview of Very Similar Names:

# In[130]:


# columns to check separately
preDE_columns_to_check = ['First_Name', 'Last_Name']

threshold = 90
all_matches = []

for col in preDE_columns_to_check:
    preDE_unique_vals = pre1790DE[col].dropna().unique().tolist()
    
    for val in preDE_unique_vals:
        result = process.extract(val, preDE_unique_vals, scorer=fuzz.token_sort_ratio)
        
        for match_val, score, _ in result:
            if val != match_val and score >= threshold:
                all_matches.append((col, val, match_val, score))

# Convert to DataFrame to review
preDE_fuzzy_matches = pd.DataFrame(all_matches, columns=['Column', 'Original', 'Match', 'Score'])
print(preDE_fuzzy_matches)


# ## Connecticut

# In[131]:


pre1790CT = pd.read_csv('liquidated_debt_certificates_CT.csv')


# In[132]:


#Detect date values over 31
preCT_mask_strange_date =  (
    (pd.to_numeric(pre1790CT['Day'], errors='coerce') >31) |
    (pd.to_numeric(pre1790CT['Day_Due'], errors='coerce') >31)
)
print(f'\nAmount of dates over 31: {preCT_mask_strange_date}')


# In[133]:


#Detect month values over 12
preCT_mask_strange_month =  (
    (pd.to_numeric(pre1790CT['Month'], errors='coerce') >12) |
    (pd.to_numeric(pre1790CT['Month_Due'], errors='coerce') >12)
)
print(f'\nAmount of months over 12: {preCT_mask_strange_month}')


# In[134]:


#Detect year values over 1790
preCT_mask_strange_year =  (
    (pd.to_numeric(pre1790CT['Year'], errors='coerce') >1790) |
    (pd.to_numeric(pre1790CT['Year_Due'], errors='coerce') >1790)
)
print(f'\nAmount of years over 1790: {preCT_mask_strange_year}')


# ### Preview of Very Similar Names:

# In[135]:


# columns to check separately
preCT_columns_to_check = ['First_Name', 'Last_Name','First_name.1', 'Last_name.1']

threshold = 90
all_matches = []

for col in preCT_columns_to_check:
    preCT_unique_vals = pre1790CT[col].dropna().unique().tolist()
    
    for val in preCT_unique_vals:
        result = process.extract(val, preCT_unique_vals, scorer=fuzz.token_sort_ratio)
        
        for match_val, score, _ in result:
            if val != match_val and score >= threshold:
                all_matches.append((col, val, match_val, score))

# Convert to DataFrame to review
preCT_fuzzy_matches = pd.DataFrame(all_matches, columns=['Column', 'Original', 'Match', 'Score'])
print(preCT_fuzzy_matches)


# ## Pierce

# In[137]:


pre1790Pierce = pd.read_csv('Pierce_Certs_cleaned_2019.csv')


# ### Preview of Very Similar Names:

# In[139]:


# columns to check separately
Pierce_columns_to_check = ['First', 'Last']

threshold = 90
all_matches = []

for col in Pierce_columns_to_check:
    Pierce_unique_vals = pre1790Pierce[col].dropna().unique().tolist()
    
    for val in Pierce_unique_vals:
        result = process.extract(val, Pierce_unique_vals, scorer=fuzz.token_sort_ratio)
        
        for match_val, score, _ in result:
            if val != match_val and score >= threshold:
                all_matches.append((col, val, match_val, score))

# Convert to DataFrame to review
Pierce_fuzzy_matches = pd.DataFrame(all_matches, columns=['Column', 'Original', 'Match', 'Score'])
print(Pierce_fuzzy_matches)


# ## Marine

# In[140]:


pre1790Marine = pd.read_csv('Marine_Liquidated_Debt_Certificates.csv')


# In[141]:


#Detect date values over 31
Marine_mask_strange_date =  (
    (pd.to_numeric(pre1790Marine['Day'], errors='coerce') >31) |
    (pd.to_numeric(pre1790Marine['Day_Due'], errors='coerce') >31)
)
print(f'\nAmount of dates over 31: {Marine_mask_strange_date}')


# In[142]:


#Detect month values over 12
Marine_mask_strange_month =  (
    (pd.to_numeric(pre1790Marine['Month'], errors='coerce') >12) |
    (pd.to_numeric(pre1790Marine['Month_Due'], errors='coerce') >12)
)
print(f'\nAmount of months over 12: {Marine_mask_strange_month}')


# In[143]:


#Detect year values over 1790
Marine_mask_strange_year =  (
    (pd.to_numeric(pre1790Marine['Year'], errors='coerce') >1790) |
    (pd.to_numeric(pre1790Marine['Year_Due'], errors='coerce') >1790)
)
print(f'\nAmount of years over 1790: {Marine_mask_strange_year}')


# ### Preview of Very Similar Names:

# In[144]:


# columns to check separately
Marine_columns_to_check = ['First_Name', 'Last_Name']

threshold = 90
all_matches = []

for col in Marine_columns_to_check:
    Marine_unique_vals = pre1790Marine[col].dropna().unique().tolist()
    
    for val in Marine_unique_vals:
        result = process.extract(val, Marine_unique_vals, scorer=fuzz.token_sort_ratio)
        
        for match_val, score, _ in result:
            if val != match_val and score >= threshold:
                all_matches.append((col, val, match_val, score))

# Convert to DataFrame to review
Marine_fuzzy_matches = pd.DataFrame(all_matches, columns=['Column', 'Original', 'Match', 'Score'])
print(Marine_fuzzy_matches)


# ## Aggregated

# In[145]:


pre1790 = pd.read_csv(INDIR_DERIVED_PRE1790 / 'agg_debt_david.csv')


# In[146]:


#rid of duplicates
pre1790.drop_duplicates(inplace=True)


# In[147]:


#duplicates (make sure there's no more)
pre1790_new_dupcount = pre1790.duplicated().sum()
print('number of duplicates:')
print(pre1790_new_dupcount)


# In[148]:


#missing
pre_missing_summary = pre1790.isnull().sum().to_frame(name='pre_missing_count')
pre_missing_summary['pre_missing_percent'] = 100 * pre_missing_summary['pre_missing_count'] / len(pre1790)
print("Missing Value Summary:")
print(pre_missing_summary.sort_values('pre_missing_percent', ascending=False))


# ### Important note:
# A lot of these do have 99% missing; I have checked the data set and for the most part these columns to the right of org_index are generally empty.

# In[149]:


#uncombined rows 
pre_amount_fields = ['amount | dollars', 'amount | 90th']
pre_mask_name_missing = pre1790[[
    'to whom due | first name',
    'to whom due | last name',
    'to whom due | first name.1',
    'to whom due | last name.1',
    'to whom due | title.1',
    'to whom due | title'
]].isnull().any(axis=1)

pre_mask_amount_present = pre1790[pre_amount_fields].notnull().any(axis=1)
pre_mask_uncombined = pre_mask_name_missing & pre_mask_amount_present


# In[150]:


#typos? (more unique values than there should be)
pre_string_cols = pre1790.select_dtypes(include='object')
pre_string_uniques = pre_string_cols.nunique(dropna=False).to_frame(name='pre_unique_values')
print("Unique value counts for all string columns:")
print(pre_string_uniques.sort_values('pre_unique_values', ascending=False))


# In[151]:


#convert dates to datetime (format)
pre_date_cols = [col for col in pre1790.columns if ('date' in col.lower()) or ('time' in col.lower())]
for col in pre_date_cols:
    pre1790[col] = pd.to_datetime(pre1790[col], errors='coerce')


# In[152]:


#converting numbers to number types (format)
pre_numeric_pattern = ['amount']
pre_numeric_obj_cols = [col for col in pre1790.select_dtypes(include = 'object').columns if any (pat in col for pat in pre_numeric_pattern)]
for col in pre_numeric_obj_cols:
    pre1790[col] = pd.to_numeric(pre1790[col].str.replace(',', ''), errors = 'coerce')


# In[153]:


#detect negatives
pre_mask_negative = pre1790[[col for col in pre1790.columns if any(pat in col for pat in pre_numeric_pattern)]].lt(0).any(axis = 1)
print(f'\aAmount of negative values: {pre_mask_negative.sum()}')


# In[154]:


#detect date values over 31
pre_mask_strange_date = pd.to_numeric(pre1790['date of the certificate | day'], errors='coerce') >31
pre_mask_strange_due_date = pd.to_numeric(pre1790['time when the debt became due | day'], errors='coerce') >31
strange_date_sum = pre_mask_strange_date.sum() + pre_mask_strange_due_date.sum()
print(f'\nAmount of dates over 31: {strange_date_sum}')


# In[155]:


#detect month values over 12 
pre_mask_strange_month= pd.to_numeric(pre1790['date of the certificate | month'], errors='coerce') >12
pre_mask_strange_due_month= pd.to_numeric(pre1790['time when the debt became due | month'], errors='coerce') >12
strange_month_sum = pre_mask_strange_month.sum() + pre_mask_strange_due_month.sum()
print(f'\nAmount of months that are over 12: {strange_month_sum}')


# In[156]:


# columns to check separately
columns_to_check = ['to whom due | first name', 'to whom due | last name', 'to whom due | first name.1','to whom due | last name.1']

threshold = 90
all_matches = []

for col in columns_to_check:
    unique_vals = pre1790[col].dropna().unique().tolist()
    
    for val in unique_vals:
        result = process.extract(val, unique_vals, scorer=fuzz.token_sort_ratio)
        
        for match_val, score, _ in result:
            if val != match_val and score >= threshold:
                all_matches.append((col, val, match_val, score))


# In[ ]:


# Convert to DataFrame to review
fuzzy_matches = pd.DataFrame(all_matches, columns=['Column', 'Original', 'Match', 'Score'])
print(fuzzy_matches)


# In[ ]:


#suspicious rows 
pre1790['listed suspicious row'] = False
pre1790['reason for being suspicious'] = ''

pre_mask_many_missing = pre1790.isnull().sum(axis=1) > pre1790.shape[1]/4
pre1790.loc[pre_mask_many_missing, 'listed suspicious row'] = True
pre1790.loc[pre_mask_many_missing, 'reason for being suspicious'] += 'More than 25% missing'

pre1790.loc[pre_mask_negative, 'listed suspicious row'] = True
pre1790.loc[pre_mask_negative, 'reason for being suspicious'] += 'Negative value'

pre1790.loc[pre_mask_uncombined, 'listed suspicious row'] = True
pre1790.loc[pre_mask_uncombined, 'reason for being suspicious'] = 'Uncombined Row, name is missing but amount is not'


pre1790.loc[pre_mask_strange_date, 'listed suspicious row'] = True
pre1790.loc[pre_mask_strange_date, 'reason for being suspicious'] = 'Date is over 31'


pre1790.loc[pre_mask_strange_month, 'listed suspicious row'] = True
pre1790.loc[pre_mask_strange_month, 'reason for being suspicious'] = 'Month is after December'


# In[ ]:


#clean vs suspicious
clean_pre1790 = pre1790[~pre1790['listed suspicious row']]
suspicious_pre1790 = pre1790[pre1790['listed suspicious row']]


# In[ ]:


#save clean & suspicious
clean_pre1790.to_csv(OUTDIR / "cleaned_agg_debt_david.csv", index=False)
suspicious_pre1790.to_csv(OUTDIR / "suspicious_agg_debt_david.csv", index=False)


# In[ ]:


#print suspicious row summary
print(f"Suspicious rows: {pre1790['listed suspicious row'].sum()}")
print("\nPreview of Suspicious Rows:")
print(suspicious_pre1790.head(5))

