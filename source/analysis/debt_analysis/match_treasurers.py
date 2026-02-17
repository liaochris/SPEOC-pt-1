#!/usr/bin/env python
# coding: utf-8

# In[19]:


# Searching liquidated debt certificates for exact matches on names

import pandas as pd

# set CSV paths
input_csv = "liquidated_debt_certificates_combined.csv"
output_csv = "matches_liquidated_debt_certificates.csv"

# list of people & states
people = pd.DataFrame(
    [("WILLIAM GARDNER","NH"),
     ("SAMUEL MATTOCKS","VT"),
     ("ALEXANDER HODGDON","MA"),
     ("JOSEPH CLARK","RI"),
     ("JEDEDIAH HUNTINGTON","CT"),
     ("GERARD BANCKER","NY"),
     ("JAMES MOTT","NJ"),
     ("CHRISTIAN FEBIGER","PA"),
     ("SAMUEL PATTERSON","DE"),
     ("WILLIAM RICHARDSON","MD"),
     ("SAMUEL MATTOCKS","VA"),
     ("JOHN HAYWOOD","NC"),
     ("JOHN MEALS","GA")],
    columns=["raw_name", "state"]
)

# read names & states from CSV
df = pd.read_csv(input_csv, usecols=["raw_name", "state", "Dollars", "90th"], low_memory=False)

# vectorized search
pairs = pd.MultiIndex.from_frame(people[["raw_name", "state"]])
mask = pd.MultiIndex.from_frame(df[["raw_name", "state"]]).isin(pairs)
matches = df[mask].assign(original_row=df.index[mask]+1)[["original_row", "raw_name", "state", "Dollars", "90th"]]

print(matches)
matches.to_csv(output_csv, index=False)


# In[23]:


# Searching loan office certificates for exact matches on names

import pandas as pd

# set CSV paths
input_csv = "loan_office_certificates_cleaned.csv"
output_csv = "matches_loan_office_certificates.csv"

# list of people & states
people = pd.DataFrame(
    [("WILLIAM GARDNER","NH"),
     ("SAMUEL MATTOCKS","VT"),
     ("ALEXANDER HODGDON","MA"),
     ("JOSEPH CLARK","RI"),
     ("JEDEDIAH HUNTINGTON","CT"),
     ("GERARD BANCKER","NY"),
     ("JAMES MOTT","NJ"),
     ("CHRISTIAN FEBIGER","PA"),
     ("SAMUEL PATTERSON","DE"),
     ("WILLIAM RICHARDSON","MD"),
     ("SAMUEL MATTOCKS","VA"),
     ("JOHN HAYWOOD","NC"),
     ("JOHN MEALS","GA")],
    columns=["raw_name", "state"]
)

# read names & states from CSV
df = pd.read_csv(input_csv, usecols=["raw_name", "state", "Face Value", "Specie Value"], low_memory=False)

# vectorized search
pairs = pd.MultiIndex.from_frame(people[["raw_name", "state"]])
mask = pd.MultiIndex.from_frame(df[["raw_name", "state"]]).isin(pairs)
matches = df[mask].assign(original_row=df.index[mask]+1)[["original_row", "raw_name", "state", "Face Value", "Specie Value"]]

print(matches)
matches.to_csv(output_csv, index=False)

# create CSV for total face & specie values
totals_per_person = (
    matches.groupby(["raw_name", "state"], as_index=False)
           .agg({"Face Value": "sum", "Specie Value": "sum"})
           .rename(columns={
               "Face Value": "Total Face Value",
               "Specie Value": "Total Specie Value"
           })
)

# Save matches
# matches.to_csv(output_csv, index=False)

# Save totals
totals_csv = "loan_office_certificates_totals.csv"
totals_per_person.to_csv(totals_csv, index=False)

print(totals_per_person)


# In[ ]:




