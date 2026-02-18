#!/usr/bin/env python
# coding: utf-8

# # Aggregate Debt Files

# Goal: Combine the debt files assigned to me. 
# 
# Input: My assigned debt files
# 1. Connecticut
# 2. Both Pennsylvania files (2)
# 3. Rhode Island
# 4. 9 states loan certificates 
# 5. Marine liquidated debt certificates 
# 
# Outpit: Aggregated csv file (```agg_debt_david.csv```) 

# In[1]:


# import all the necessary packages
from pathlib import Path
import pandas as pd

INDIR_RAW = Path("source/raw/pre1790")
OUTDIR = Path("output/derived/pre1790")


# In[2]:


def clean_table(table, drp_cols):
    table.drop(columns=drp_cols, inplace=True, axis=1)
    table.columns = table.columns.to_flat_index() 
    
    for column in table.columns:
        if 'Unnamed' in column[1]:
            table.rename(columns={column:(column[0],'')}, inplace=True)
    
    table.rename(columns=lambda x: x[0].lower().strip() + ' | ' + x[1].lower().strip() if (x[1] != '') else x[0].lower().strip(), inplace=True) # lowercase column titles 
    table.rename(columns={'state | ' : 'state'}, inplace=True)
    return table


# In[3]:


changes = {
    'to whom due (if second name) | first name':'to whom due | first name.1',
    'to whom due (if second name) | last name':'to whom due | last name.1',
    'to whom due (if second name) | title':'to whom due | title.1', 
    'time when the debt became due | dollars':'amount | dollars',
    'time when the debt became due | 90th':'amount | 90th',
    'time when the debt became due | date':'time when the debt became due | day',
    'line strike thorugh? | yes?':'line strike through? | yes?',
    'line strike thorugh? | notes':'notes',
    'line strike through? | notes':'notes',
    'line strike thorugh? | note':'line strike through? | note',
    'line strike through?' : 'line strike through? | note',
    'date of the certificate | date':'date of the certificate | day',
    'to whom issued | title':'to whom due | title',
    'to whom issued | first name':'to whom due | first name',
    'to whom issued | last name':'to whom due | last name',
    'comm of interest | year':'time when the debt became due | year',
    'comm of interest | month':'time when the debt became due | month',
    'comm of interest | date':'time when the debt became due | day',
    'comm of interest | dollars':'amount | dollars',
    'comm of interest | 90th':'amount | 90th',
    'comm of interest | 10th':'amount | 10th',
    'w | dollars':'amount | dollars',
    'w | 90th':'amount | 90th',
    'w | 8th':'amount | 8th',
    'year':'date of the certificate | year', 
    'month':'date of the certificate | month',
    'day':'date of the certificate | day', 
    'title 1':'to whom due | title', 
    'first name 1':'to whom due | first name',
    'last name 1':'to whom due | last name',
    'title 2':'to whom due | title.1', 
    'first name 2':'to whom due | first name.1',
    'last name 2':'to whom due | last name.1',
    'specie value':'amount in specie | dollars',
    'line strike thorugh? | yes?':'line strike through? | yes?',
    'line strike thorugh? | note':'line strike through? | note',
    'line strike thorugh? | notes':'notes',
    'face value':'amount | dollars'
}


# In[4]:


# handle the liquidated debt certificates first for each file and merge into 1 dataframe
ct_debt = pd.read_excel(INDIR_RAW / "orig/liquidated_debt_certificates_CT.xlsx", header=[10,11])
de_debt = pd.read_excel(INDIR_RAW / "orig/liquidated_debt_certificates_DE.xlsx", header=[9,10])
ma_debt = pd.read_excel(INDIR_RAW / "orig/liquidated_debt_certificates_MA.xlsx", header=[10,11])
nh_debt = pd.read_excel(INDIR_RAW / "orig/liquidated_debt_certificates_NH.xlsx", header=[10,11])
nj_debt = pd.read_excel(INDIR_RAW / "orig/liquidated_debt_certificates_NJ.xlsx", header=[9,10])
ny_debt = pd.read_excel(INDIR_RAW / "orig/liquidated_debt_certificates_NY.xlsx", header=[10,11])
pa_stelle_debt = pd.read_excel(INDIR_RAW / "orig/liquidated_debt_certificates_PA_stelle.xlsx", header=[10,11])
pa_story_debt = pd.read_excel(INDIR_RAW / "orig/liquidated_debt_certificates_PA_story.xlsx", header=[10,11])
ri_debt = pd.read_excel(INDIR_RAW / "orig/liquidated_debt_certificates_RI.xlsx", header=[10,11])
loan_9_debt = pd.read_excel(INDIR_RAW / "orig/loan_office_certificates_9_states.xlsx", header=0)
marine_debt = pd.read_excel(INDIR_RAW / "orig/Marine_Liquidated_Debt_Certificates.xlsx", header=[10, 11])

# add a state column to each dataframe
ct_debt['state'] = 'ct'
de_debt['state'] = 'de'
ma_debt['state'] = 'ma'
nh_debt['state'] = 'nh'
nj_debt['state'] = 'nj'
ny_debt['state'] = 'ny'
pa_stelle_debt['state'] = 'pa'
pa_story_debt['state'] = 'pa'
ri_debt['state'] = 'ri'

ny_drp_cols = ['Page', 'JPEG number', 'Number']
ny_debt = clean_table(ny_debt, ny_drp_cols)

# connecticut 
ct_drp_cols = ['Register Page', 'JPEG number', 'Number']
ct_debt = clean_table(ct_debt, ct_drp_cols)
# manual fixes
ct_debt.rename(columns=changes, inplace=True)
ct_debt['org_file'] = 'liquidated_debt_certificates_CT.xlsx'
print(ct_debt.dtypes)
print()

# pennsylvania: stelle
pa_stelle_drp = ['Register Page', 'JPEG number', 'No.']
pa_stelle_debt = clean_table(pa_stelle_debt, pa_stelle_drp)
# manual fixes
pa_stelle_debt.rename(columns=changes, inplace=True)
pa_stelle_debt['org_file'] = 'liquidated_debt_certificates_PA_stelle.xlsx'
print(pa_stelle_debt.dtypes)
print()

#pennsylvania: story 
pa_story_drp = ['Register Page', 'JPEG number', 'No.']
pa_story_debt = clean_table(pa_story_debt, pa_story_drp)
# manual fixes
pa_story_debt.rename(columns=changes, inplace=True)
pa_story_debt.columns.values[14] = 'amount in specie | dollars'
pa_story_debt.columns.values[15] = 'amount in specie | cents'
pa_story_debt['org_file'] = 'liquidated_debt_certificates_PA_story.xlsx'
print(pa_story_debt.dtypes)
print()

# rhode island 
ri_drp = ['Register Page', 'JPEG number', 'Number']
ri_debt = clean_table(ri_debt, ri_drp)
# manual fixes
ri_debt.rename(columns=changes, inplace=True)
ri_debt['org_file'] = 'liquidated_debt_certificates_RI.xlsx'
print(ri_debt.dtypes)
print()

# 9 states loan certificates
state_nums = {
    1: 'nh', 2: 'ma', 3: 'ct', 4: 'ny', 5: 'nj', 6: 'pa', 7: 'de', 8: 'md', 9: 'va'
}
loan_9_debt['State'] = loan_9_debt['State'].apply(lambda state_num: state_nums[state_num])
loan_9_debt.rename(columns=lambda x: x.lower().strip(), inplace=True)
# manual fixes
loan_9_debt.rename(columns=changes, inplace=True)
loan_9_debt['org_file'] = 'loan_office_certificates_9_states.xlsx'
print(loan_9_debt.dtypes)
print()

# marine debt 
marine_drp = ['Page', 'JPEG number', 'Number']
marine_debt = clean_table(marine_debt, marine_drp)
marine_debt.rename(columns=changes, inplace=True)
marine_debt.columns.values[12] = 'total dollars | notes'
marine_debt.columns.values[13] = 'total dollars | notes.1'
marine_debt['org_file'] = 'Marine_Liquidated_Debt_Certificates.xlsx'
print(marine_debt.dtypes)
print()


# In[5]:


debt_files = [ct_debt, pa_stelle_debt, pa_story_debt, ri_debt, loan_9_debt, marine_debt]


# In[6]:


for file in debt_files:
    file['org_index'] = file.index


# In[7]:


agg_debt = pd.concat(debt_files, ignore_index=True)


# In[8]:


for column in agg_debt.columns:
    print(column)


# In[9]:


agg_debt.to_csv(OUTDIR / 'agg_debt_david.csv')


# In[ ]:




