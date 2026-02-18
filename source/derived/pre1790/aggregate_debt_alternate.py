#!/usr/bin/env python
# coding: utf-8

# Aggregating the following files: DE, MA, NH, NJ, NY, Pierce
# 
# Column order (copy and pasted from david):
#  - letter
#  - date of the certificate | month
#  - date of the certificate | day
#  - date of the certificate | year
#  - to whom due | first name
#  - to whom due | last name
#  - to whom due | title
#  - to whom due | first name.1
#  - to whom due | last name.1
#  - to whom due | title.1
#  - time when the debt became due | month
#  - time when the debt became due | day
#  - time when the debt became due | year
#  - amount | dollars
#  - amount | 90th
#  - line strike thorugh? | yes? 
#  - line strike thorugh? | note
#  - notes
#  - state

# In[14]:


#IMPORTS
from pathlib import Path
import pandas as pd
import numpy as np

INDIR_RAW = Path("source/raw/pre1790")
OUTDIR = Path("output/derived/pre1790")


# In[15]:


#Helpers
def deNaN(series):
    """
    amends pandas series by replacing NaN values with empty strings
    :param series: pandas series
    """

    return series.apply(lambda x: "" if type(x) != str else x)
oii = 0 #keeps track of the org_index
def add_org_index(series: pd.Series):
    global oii
    series.index
    series["org_index"] = oii
    oii = oii + 1
    return series


# In[16]:


nj = pd.read_excel(INDIR_RAW / "orig/liquidated_debt_certificates_NJ.xlsx")
nj = nj[10:5117].drop(columns=["Record Name", "Records of the New Jersey Continental Loan Office, 1777-1790", "Unnamed: 19"])

cols = {"Unnamed: 2": "letter", 
        "Unnamed: 3": "date of the certificate | month",
        "Unnamed: 4": "date of the certificate | day",
        "Unnamed: 5": "date of the certificate | year",
        "Unnamed: 6": "to whom due | title",
        "Unnamed: 7": "to whom due | first name",
        "Unnamed: 8": "to whom due | last name",
        "Unnamed: 9": "to whom due | title.1",
        "F": "to whom due | first name.1",
        "Unnamed: 11": "to whom due | last name.1",
        "Unnamed: 12": "time when the debt became due | day",
        "Unnamed: 13": "time when the debt became due | month",
        "Unnamed: 14": "time when the debt became due | year",
        "Unnamed: 15": "amount | dollars",
        "Unnamed: 16": "amount | 90th",
        "Unnamed: 17": "line strike through? | note",
        "Unnamed: 18": "notes"
}

nj = nj.rename(columns=cols)
nj['state'] = 'nj'
nj["line strike through? | yes?"] = 0 # add line strike through column
# line strike through binary col to 1 if note is present, 0 if note is not present
def add_strike_conf(series: pd.Series):
    if str(series["line strike through? | note"]) != "nan": #For some reason this means Nan
        series["line strike through? | yes?"] = 1
    else:
        series["line strike through? | yes?"] = ""
    return series
nj = nj.apply(add_strike_conf, axis=1)
nj['org_file'] = "liquidated_debt_certificates_NJ.xlsx"
nj["org_index"] = 0
oii = 0
nj = nj.apply(add_org_index, axis=1)
nj


# In[17]:


nh = pd.read_excel(INDIR_RAW / "orig/liquidated_debt_certificates_NH.xlsx")
nh = nh[11:189].drop(columns=["Record Name", "Records of the Connecticut, New Hampshire, and Rhode Island Continental Loan Office, 1777-1789", "Unnamed: 2"])

cols = {"Unnamed: 3": "letter", 
        "Unnamed: 4": "date of the certificate | month",
        "Unnamed: 5": "date of the certificate | day",
        "Unnamed: 6": "date of the certificate | year",
        "Unnamed: 7": "to whom due | first name",
        "Unnamed: 8": "to whom due | last name",
        "Unnamed: 9": "to whom due | title",
        "Unnamed: 10": "time when the debt became due | month",
        "Unnamed: 11": "time when the debt became due | day",
        "Unnamed: 12": "time when the debt became due | year",
        "Unnamed: 13": "amount | dollars",
        "Unnamed: 14": "amount | 90th",
        "Unnamed: 15": "line strike through? | yes?",
        "Unnamed: 16": "line strike through? | note",
        "Unnamed: 17": "notes"
}

nh = nh.rename(columns=cols)
nh['state'] = 'nh'
nh['org_file'] = "liquidated_debt_certificates_NH.xlsx"
nh["org_index"] = 0
oii = 0
nh = nh.apply(add_org_index, axis=1)
nh["to whom due | title.1"] = ""
nh["to whom due | first name.1"] = ""
nh["to whom due | last name.1"] = ""
nh


# In[18]:


ny = pd.read_excel(INDIR_RAW / "orig/liquidated_debt_certificates_NY.xlsx")
ny = ny[11:7319].drop(columns=["Record Name", "Records of the New Jersey and New York Continental Loan Offices 1777-1790", "Unnamed: 2"])

cols = {"Unnamed: 3": "letter", 
        "Unnamed: 4": "date of the certificate | month",
        "Unnamed: 5": "date of the certificate | day",
        "Unnamed: 6": "date of the certificate | year",
        "Unnamed: 7": "to whom due | first name",
        "Unnamed: 8": "to whom due | last name",
        "Unnamed: 9": "to whom due | title",
        "Unnamed: 10": "to whom due | first name.1",
        "Unnamed: 11": "to whom due | last name.1",
        "Unnamed: 12": "to whom due | title.1",
        "Unnamed: 13": "time when the debt became due | month",
        "Unnamed: 14": "time when the debt became due | day",
        "Unnamed: 15": "time when the debt became due | year",
        "Unnamed: 16": "amount | dollars",
        "Unnamed: 17": "amount | 90th",
        "Unnamed: 18": "line strike through? | yes?",
        "Unnamed: 19": "line strike through? | note",
        "Unnamed: 20": "notes"
}

ny = ny.rename(columns=cols)
ny['org_file'] = "liquidated_debt_certificates_NY.xlsx"
ny["org_index"] = 0
oii = 0
ny = ny.apply(add_org_index, axis=1)
ny['state'] = 'ny'
ny


# In[19]:


de = pd.read_excel(INDIR_RAW / "orig/liquidated_debt_certificates_DE.xlsx")
de = de[11:636].drop(columns=["Record Name", 
    "Mr Paterson remarks that the certificate No. 57 says interest payable from the 1st of March 1780 instead of 1st May 1780, 123 From the 1st of January 1780 instead of 14th January, 234 is in the name of James James    John James"])

cols = {"Unnamed: 2": "letter", 
        "Unnamed: 3": "date of the certificate | day",
        "Unnamed: 4": "date of the certificate | month",
        "Unnamed: 5": "date of the certificate | year",
        "Unnamed: 6": "to whom due | title",
        "Unnamed: 7": "to whom due | first name",
        "Unnamed: 8": "to whom due | last name",
        "Unnamed: 9": "time when the debt became due | day",
        "Unnamed: 10": "time when the debt became due | month",
        "Unnamed: 11": "time when the debt became due | year",
        "Unnamed: 12": "amount | dollars",
        "Unnamed: 13": "amount | 90th",
        "Unnamed: 14": "line strike through? | note",
        "Unnamed: 15": "notes"
}

de = de.rename(columns=cols)
de['state'] = 'de'
de["to whom due | title.1"] = ""
de["to whom due | first name.1"] = ""
de["to whom due | last name.1"] = ""
de['org_file'] = "liquidated_debt_certificates_DE.xlsx"
de["org_index"] = 0
oii = 0
de = de.apply(add_org_index, axis=1)
de["line strike through? | yes?"] = 0 # add line strike through column
# line strike through binary col to 1 if note is present, 0 if note is not present
def add_strike_conf(series: pd.Series):
    if str(series["line strike through? | note"]) != "nan": #For some reason this means Nan
        series["line strike through? | yes?"] = 1
    else:
        series["line strike through? | yes?"] = ""
    return series
de = de.apply(add_strike_conf, axis=1)
de


# In[20]:


ma = pd.read_excel(INDIR_RAW / "orig/liquidated_debt_certificates_MA.xlsx")
ma = ma[11:2089].drop(columns=["Record Name", "Records of the Massachusetts Continental Loan Office, 1777-1791", "Unnamed: 2", "Unnamed: 20"])

cols = {"Unnamed: 3": "letter", 
        "Unnamed: 4": "date of the certificate | month",
        "Unnamed: 5": "date of the certificate | day",
        "Unnamed: 6": "date of the certificate | year",
        "Unnamed: 7": "to whom due | first name",
        "Unnamed: 8": "to whom due | last name",
        "Unnamed: 9": "to whom due | title",
        "Unnamed: 10": "to whom due | first name.1",
        "Unnamed: 11": "to whom due | last name.1",
        "Unnamed: 12": "to whom due | title.1",
        "Unnamed: 13": "time when the debt became due | month",
        "Unnamed: 14": "time when the debt became due | day",
        "Unnamed: 15": "time when the debt became due | year",
        "Unnamed: 16": "amount | dollars",
        "Unnamed: 17": "amount | 90th",
        "Unnamed: 18": "line strike through? | note",
        "Unnamed: 19": "notes"
}

ma = ma.rename(columns=cols)
ma['state'] = 'ma'
ma["line strike through? | yes?"] = 0 # add line strike through column
ma['org_file'] = "liquidated_debt_certificates_MA.xlsx"
ma["org_index"] = 0
oii = 0
ma = ma.apply(add_org_index, axis=1)
# line strike through binary col to 1 if note is present, 0 if note is not present
def add_strike_conf(series: pd.Series):
    if str(series["line strike through? | note"]) != "nan": #For some reason this means Nan
        series["line strike through? | yes?"] = 1
    else:
        series["line strike through? | yes?"] = ""
    return series
ma = ma.apply(add_strike_conf, axis=1)
ma


# In[21]:


pierce = pd.read_excel(INDIR_RAW / "orig/Pierce_Certs_cleaned_2019.xlsx")
pierce = pierce[1:93308].drop(columns=["CN", "Group", "To Whom Issued", "Officer"])
#pierce = pierce[1:100].drop(columns=["CN", "Group", "To Whom Issued", "Officer"])

cols = {"First": "to whom due | first name",
        "Last": "to whom due | last name",
        "Value": "amount | dollars",
        "State": "state"
}

add_cols = ["letter", "date of the certificate | month", "date of the certificate | day",
            "date of the certificate | year", "to whom due | title", "to whom due | title.1",
            "to whom due | first name.1", "to whom due | last name.1",
            "time when the debt became due | day", "time when the debt became due | month",
            "time when the debt became due | year", "amount | 90th", "line strike through? | note",
            "notes"]

pierce['org_file'] = "Pierce_Certs_cleaned_2019.xlsx"
pierce["org_index"] = 0
oii = 0
pierce = pierce.apply(add_org_index, axis=1)

pierce = pierce.rename(columns=cols)
# line strike through binary col to 1 if note is present, 0 if note is not present
def lowercase_state_abbr(series: pd.Series):
    if str(series["state"]) != "nan": #For some reason this means NaN
        series["state"] = str.lower(series["state"])
    return series
pierce = pierce.apply(lowercase_state_abbr, axis=1)
for col in add_cols:
    pierce[col] = ""
pierce["line strike through? | yes?"] = "" # add line strike through column
pierce


# In[22]:


dataframes = [nh, nj, ny, ma, de, pierce]
david_debt = pd.read_csv(OUTDIR / "agg_debt_david.csv")
david_debt = david_debt.drop(columns=["Unnamed: 0"])
print(david_debt.columns)
for df in dataframes:
    df.reindex(columns=david_debt.columns, fill_value="nan")
concatenated_df = pd.concat(dataframes)


# In[23]:


final = pd.concat([concatenated_df, david_debt])
final.reset_index(inplace=True, drop=True)


# In[27]:


final.loc[final['org_file'] == 'Pierce_Certs_cleaned_2019.xlsx'].tail()


# In[25]:


print(len(final))


# In[26]:


final.to_csv(OUTDIR / "final_agg_debt.csv")

