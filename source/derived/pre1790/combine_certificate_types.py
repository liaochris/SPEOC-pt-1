#!/usr/bin/env python
# coding: utf-8

# # Cells order
#  - imports
#  - load/create dataframes
#  - helper functions
#  - any manual corrections / manually dropping invalid rows
#  - Standardizing Town/State/Estate/Heir of (obj. 4 & 8)
#  - Standardizing names containing 'of' entirely in the first name column
#  - Companies (obj 2)
#  - Entries with 2 names (obj 3)
#  - Names that are entirely in the first or last name column (obj 9)
#  - Filling in blank columns (obj 7)
#  - Deceased individuals (obj 12)
#  - abbreviations (obj 5)
#  - Group consecutive names (obj 1)
#  - Ancestry code
# # Objectives
# 
# [here](https://docs.google.com/document/d/1pcSQfWNll6K9tl-_rB4lztN0TsZsclU9vOnbyQob-Zs/edit).

# In[7]:


#Imports
import pandas as pd
import datetime
import numpy as np
import json
import os
from pathlib import Path
from fuzzywuzzy import fuzz

import nltk
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree
import ssl

from nameparser import HumanName
#---
import re
import csv
import ast

INDIR_DERIVED = Path("output/derived/pre1790")
INDIR_RAW = Path("source/raw/pre1790")
OUTDIR = Path("output/derived/pre1790")


# In[8]:


#Dataframes
agg_debt = pd.read_csv(INDIR_DERIVED / "final_agg_debt.csv")

name_changes = pd.DataFrame({'title_org': pd.Series(dtype='str'),
                       'title_new': pd.Series(dtype='str'),
                       'first_name_org': pd.Series(dtype='str'),
                       'last_name_org': pd.Series(dtype='str'),
                       'first_name_new': pd.Series(dtype='str'),
                       'last_name_new': pd.Series(dtype='str'),
                       'cleaning case': pd.Series(dtype='int'),
                       'file_loc': pd.Series(dtype='str'),
                       'org_index': pd.Series(dtype='int')})

# retrieve manual corrections from csv file if they exist 
manual_corrects_df = pd.read_csv(INDIR_RAW / "corrections/name_fix.csv")
manual_corrects_dict = manual_corrects_df.to_dict(orient='index')
manual_corrects = {}
# add manual corrections to manual_corrects dictionary
for correction in manual_corrects_dict.keys():
    manual_corrects[manual_corrects_dict[correction]['Unnamed: 0']] = [manual_corrects_dict[correction]['new first name'], manual_corrects_dict[correction]['new last name']]


# # Documenting Changes
# 
# <b>Goal: </b> We need to document changes we make to ```agg_debt.csv``` in a separate dataframe: ```name_changes```. This way, we can double-check whether those changes were appropriate. 
# 
# <b>Steps</b>
# 1. Create an empty dataframe. Here are the column names:
#     - ```title_org```: The original title of the individual (Mr., Ms., etc.)
#     - ```title_new```: The new title of the individual (Mr., Ms., etc.) 
#     - ```first_name_org```: The original first name of the individual from the unchanged ```agg_debt.csv```
#     - ```last_name_org```: The original last name of the individual from the unchanged ```agg_debt.csv``` 
#     - ```first_name_new``` : If first name changed, record it here. Otherwise, this entry will still be the old name. 
#     - ```last_name_new```: If last name changed, record it here. Otherwise, this entry will still be the old name. 
#     - ```cleaning case```: This corresponds with the task number in the objectives document linked above. 
#     - ```file_loc```: The individual state filename in which the row came from 
#     - ```org_index```: The original index/row that the debt entry can be found in ```file_loc``` 
# 2. Create a function that adds a new row to the dataframe. This function will be called while we are cleaning. 
# 
# **Cleaning case = Objective number** 
# - Combine multiple consective debt entries (optional) = 1,
# - Clean company names = 2,
# - Handle two names = 3,
# - Remove "Estate of" = 4,
# - Handle abbreviations = 5,
# - Standardize names (Ancestry) = 6
# - Fill in blank name columns = 7,
# - remove "Heirs of" prefixes = 8,
# - Names that are entierly in first or last name column = 9,
# - Occupations in the name = 10,
# - Entry on behalf of someone else = 11,
# - Mark deceased people = 12

# In[9]:


#Helper functions
def add_changes(title_org, title_new, fn_org, ln_org, fn_new, ln_new, case, file, index):
    name_changes.loc[len(name_changes.index)] = [title_org, title_new, fn_org, ln_org, fn_new, ln_new, case, file, index]

#Download the necessary NLTK models for the below function
#Change the below to True to use the workaround in case downloads don't work
if True:
    try:
        _unverified = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _unverified
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
def get_tags(text):
    nltk_results = ne_chunk(pos_tag(word_tokenize(text)))
    tags = {}
    for nltk_result in nltk_results:
        if type(nltk_result) == Tree:
            name = ''
            for nltk_result_leaf in nltk_result.leaves():
                name += nltk_result_leaf[0] + ' '
            tags[name] = nltk_result.label()
    return tags


# In[10]:


#Remove long strings
#Super fast method - instead of going through it and adding to a new dataset,
#use apply with a simple function that doesn't include long strings in a new dataset
agg_debt = agg_debt[agg_debt['to whom due | first name'].apply(lambda name: len(str(name).split()) > 10) == False]
agg_debt = agg_debt[agg_debt['to whom due | last name'].apply(lambda name: len(str(name).split()) > 10) == False]


# In[ ]:





# # Heirs of & Estate of
# 
# <b>Goal:</b> Remove "Estate of", "Heirs of", "State of" prefixes in an entry, and marks "State of" entries as organizations
# 
# <b>Steps:</b>
# 
# 1. Check if a first name entry is longer than 2 words. If it is, run fuzzy checks to see if it begins with State of/Town of/Estate of/Heirs of (Use fuzzy checks to account for typos, which are quite frequent)
# 2. For State of and Town of matches, make the first name "State" or "Town" respectively, make the last name the name of the state/town, and mark it as an organization
# 3. For Estate of and Heirs of, make the first word the first name, and everything beyond it the last name
# 4. Record any changes in ```name_changes```
# 
# <b>Notes:</b>
# 
# 1. Sometimes "Estate of" is abbreviated to "State of", which confuses it (an example is the first manual correction)
# 2. The "State of" fuzzy ratio threshold is higher than the "Estate of" and runs before it to catch "State of" as reliably as possible, just because they are 1 letter off.

# In[11]:


agg_debt["organization?"] = False

manual_corrections = [
    {"og_fname": "State of William Sweet",
     "new_title": "",
     "new_fname": "William", 
     "new_lname": "Sweet"},
    {"og_fname": "Estateof Doct James Front",
     "new_title": "Doct",
     "new_fname": "James",
     "new_lname": "Front"},
    {"og_fname": "Estate of Capt John Williams",
     "new_title": "Capt",
     "new_fname": "John",
     "new_lname": "Williams"},
    {"og_fname": "Estate ofJon Bowman",
     "new_title": "",
     "new_fname": "Jon",
     "new_lname": "Bowman"},
    {"og_fname": "Esatate of Matthew Fentom",
     "new_title": "",
     "new_fname": "Matthew",
     "new_lname": "Fentom"}
]

def handle_ofs(row):
    og_fname = str(row["to whom due | first name"])
    og_lname = str(row["to whom due | last name"])
    title = str(row["to whom due | title"])
    
    for c in manual_corrections:
        if c["og_fname"] == og_fname:
            row["to whom due | first name"] = c["new_fname"]
            row["to whom due | last name"] = c["new_lname"]
            row["to whom due | title"] = c["new_title"]
            return row
    
    og_fname = og_fname.replace("the ", "").replace("The ", "")
    og_lname = og_lname.replace("the ", "").replace("The ", "")
    
    if len(og_fname.split()) > 2:
        prefix = og_fname.split()[0] + og_fname.split()[1]
        prefix = prefix.lower()
        if fuzz.ratio(prefix, "state of") >= 88 and "est" not in prefix: #"not in" so that this one won't pick up "Estate of"
            lname =  " ".join(og_fname.split()[2:])
            fname = "State"
            add_changes(title, title, row["to whom due | first name"], row["to whom due | last name"], fname, lname, 8, row["org_file"], row["org_index"])
            #save_manual_correction(title, row["to whom due | first name"], row["to whom due | last name"], title, fname, lname, 8, row["org_file"], row["org_index"], is_manual=False)
            row["to whom due | first name"] = fname
            row["to whom due | last name"] = lname
            row["organization?"] = True
        elif fuzz.ratio(prefix, "town of") >= 88:
            lname =  " ".join(og_fname.split()[2:])
            fname = "Town"
            add_changes(title, title, row["to whom due | first name"], row["to whom due | last name"], fname, lname, 8, row["org_file"], row["org_index"])
            #save_manual_correction(title, row["to whom due | first name"], row["to whom due | last name"], title, fname, lname, 8, row["org_file"], row["org_index"], is_manual=False)
            row["to whom due | first name"] = fname
            row["to whom due | last name"] = lname
            row["organization?"] = True
        elif (fuzz.ratio(prefix, "estate of") >= 85 or fuzz.ratio(prefix, "Est of") >= 85) and "est" in prefix: #"in prefix" so that this one won't pick up "State of"
            #print(og_fname.split()[2:])
            name = " ".join(og_fname.split()[2:])
            fname =  name.split()[0]
            lname = name.split()[1:] if len(name.split()) > 1 else ""
            if len(lname) == 0 and row["to whom due | last name"] != "": lname = row["to whom due | last name"]
            if type(lname) == list: lname = " ".join(lname)
            add_changes(title, title, row["to whom due | first name"], row["to whom due | last name"], fname, lname, 4, row["org_file"], row["org_index"])
            #save_manual_correction(title, row["to whom due | first name"], row["to whom due | last name"], title, fname, lname, 4, row["org_file"], row["org_index"], is_manual=False)
            row["to whom due | first name"] = fname
            row["to whom due | last name"] = lname
        elif fuzz.ratio(prefix, "heir of") >= 85 or fuzz.ratio(prefix, "heirs of") >= 85:
            name = " ".join(og_fname.split()[2:])
            fname =  name.split()[0]
            lname = name.split()[1:] if len(name.split()) > 1 else ""
            add_changes(title, title, row["to whom due | first name"], row["to whom due | last name"], fname, lname, 4, row["org_file"], row["org_index"])
            #save_manual_correction(title, row["to whom due | first name"], row["to whom due | last name"], title, fname, lname, 4, row["org_file"], row["org_index"], is_manual=False)
            row["to whom due | first name"] = fname
            row["to whom due | last name"] = lname
    return row

agg_debt = agg_debt.apply(lambda row: handle_ofs(row), axis=1)


# In[13]:


#Standardizing names containing 'of' entirely in the first name column
manual_corrections = {
    "School Committee of Derbey": ["School Committee", "Derbey"],
    "Trusts of Wilmington Academy": ["Trusts", "Wilmington Academy"],
    "Trusts of Wilmington": ["Trusts", "Wilmington"],
    "Ruten of Chais": ["Ruten", ""]
}

def handle_all_orgs(row):
    og_fname = str(row["to whom due | first name"])
    og_lname = str(row["to whom due | last name"])
    title = row["to whom due | title"]
    
    for og, correction in manual_corrections.items():
        if og == og_fname:
            row["organization?"] = True
            row["to whom due | first name"] = correction[0]
            row["to whom due | last name"] = correction[1]
            return row
    
    fname, lname = "", ""
    if len(og_fname.split()) > 2 and (("of " in og_fname) or (" of" in og_fname)):
        tags = get_tags(og_fname)
        is_org = True
        for token, tag in tags.items():
            if tag == "PERSON": #Geo political entity
                is_org = False
        print(f"{og_fname} {tags}: {is_org}")
        if not is_org: return row
        row["organization?"] = True
        
        if (len(og_fname.split("of")) == 2):
            before_of, after_of = og_fname.split("of")
            fname = before_of.strip().replace("-", "")
            lname = after_of.strip().replace("-", "")
            add_changes(title, title, og_fname, og_lname, fname, lname, 14, row["org_file"], row["org_index"])
            #save_manual_correction(title, og_fname, og_lname, title, fname, lname, 14, row["org_file"], row["org_index"], is_manual=False)
            row["to whom due | first name"] = fname
            row["to whom due | last name"] = lname
    return row

agg_debt = agg_debt.apply(lambda row: handle_all_orgs(row), axis=1)


# In[ ]:


# Company names
# retrieve manual corrections from csv file if they exist 
manual_corrects_df = pd.read_csv(INDIR_RAW / "corrections/name_fix.csv")
manual_corrects_dict = manual_corrects_df.to_dict(orient='index')
manual_corrects = {}
# add manual corrections to manual_corrects dictionary
for correction in manual_corrects_dict.keys():
    manual_corrects[manual_corrects_dict[correction]['Unnamed: 0']] = [manual_corrects_dict[correction]['new first name'], manual_corrects_dict[correction]['new last name']]

# dictionary of manual changes i have to make 
changes = {
    'Henry Mc Clellen & Henry & co' : 'Henry Mc Clellen & Co'
}

conn_words = [' for ', ' of ', ' and '] # these are connector key words
corp_key_words = ('corporation', ' and co', ' and coy', ' and others', ' and several others', ' and heirs', ' and comp', ' and other trustees') # these are corporation key words

def handle_comp_name(row):        
    org_fname = str(row['to whom due | first name'])
    org_lname = str(row['to whom due | last name'])
    
    fname = str(row['to whom due | first name'])
    fname = fname.replace('&', 'and')
    fname = fname.replace('.', '')
    
    if fname in changes:
        fname = changes[fname]
    
    fname_l = str(fname).lower().strip()
    
    # check if string ends with co, coy, or others; if so, delete 
    for key_word in corp_key_words:
        if fname_l.endswith(key_word):
            print('index=' + str(row['Unnamed: 0']))
            print('old name=' + str(fname_l))      
            fname_corr = fname_l.split(key_word)
            print('corrected name=' + str(fname_corr[0])) 
            fname_corr = fname_corr[0]
            fname_sp = fname_corr.split()
            
            # only one name; put name into last name column 
            if len(fname_sp) == 1:
                row['to whom due | first name'] = ''
                row['to whom due | last name'] = fname_sp[0].capitalize()
                print('corrected name=' + str(fname_sp[0])) 
                print('new last name=' + str(fname_sp[0].capitalize()))
                
            # if there are is only a first name and a last name, put into respective columns
            elif len(fname_sp) == 2:
                row['to whom due | first name'] = fname_sp[0].capitalize()
                row['to whom due | last name'] = fname_sp[1].capitalize()
                print('new first name=' + str(fname_sp[0].capitalize()))
                print('new last name=' + str(fname_sp[1].capitalize()))
                
            # handles middle names; put middle names in last name column 
            elif len(fname_sp) == 3:
                row['to whom due | first name'] = fname_sp[0].capitalize() 
                row['to whom due | last name'] = fname_sp[1].capitalize() + ' ' + fname_sp[2].capitalize()
                print('new first name=' + str(fname_sp[0].capitalize()))
                print('new last name=' + str(fname_sp[1].capitalize() + ' ' + fname_sp[2].capitalize()))  
            # manually clean debt entries that have long names 
            else: 
                # check if name has already been manually cleaned
                if fname_corr in manual_corrects:
                    new_fname = manual_corrects[fname_corr][0]
                    new_lname = manual_corrects[fname_corr][1]
                else:
                    new_fname = input('new first name: ')
                    new_lname = input('new last name: ') 
                    manual_corrects[fname_corr] = [new_fname, new_lname]
                
                row['to whom due | first name'] = new_fname.capitalize()
                row['to whom due | last name'] = new_lname.capitalize()
                    
                print('new first name=' + str(new_fname.capitalize()))
                print('new last name=' + str(new_lname.capitalize()))  
                
            # record change 
            add_changes(row['to whom due | title'], row['to whom due | title'], org_fname, org_lname, 
                   row['to whom due | first name'], row['to whom due | last name'], 2, row['org_file'], row['org_index'])
            
            print('+------------------------------+')
        # if the name starts with any keyword: 'corporation for the relief of...'; manually change these names
        elif fname_l.startswith(key_word): 
            print('index=' + str(row['Unnamed: 0']))
            print('old name=' + str(fname_l))      
            
            # check if name has already been manually cleaned
            if fname_l in manual_corrects:
                new_fname = str(manual_corrects[fname_l][0])
                new_lname = str(manual_corrects[fname_l][1])
            else:
                new_fname = input('new first name: ')
                new_lname = input('new last name: ') 
                manual_corrects[fname_l] = [new_fname, new_lname]

            row['to whom due | first name'] = new_fname.capitalize()
            row['to whom due | last name'] = new_lname.capitalize()
            
            # record change 
            add_changes(row['to whom due | title'], row['to whom due | title'], org_fname, org_lname, 
                   row['to whom due | first name'], row['to whom due | last name'], 2, row['org_file'], row['org_index'])

            print('new first name=' + str(new_fname.capitalize()))
            print('new last name=' + str(new_lname.capitalize()))  
    
    return row

agg_debt = agg_debt.apply(lambda row: handle_comp_name(row), axis=1)
agg_debt['Unnamed: 0'] = agg_debt.index
agg_debt.rename(columns={'Unnamed: 0' : 'index'}, inplace=True)


# In[ ]:


# Entries with 2 names
changes = {
    'van zandt & kittletas' : ['', 'van zandt | kittletas'],
    'trustees of & davids church':['trustees of & davids church', '']
}
# make sure all names are of type: str
agg_debt[['to whom due | first name', 'to whom due | last name']] = agg_debt[['to whom due | first name', 'to whom due | last name']].astype(str)
# Function to convert
def listToString(s):
 
    # initialize an empty string
    str1 = " "
 
    # return string
    return (str1.join(s))

def handle_two_name(row):
    org_fn = row['to whom due | first name']
    org_ln = row['to whom due | last name']
    
    org_fn_l = str(org_fn).lower()
        
    # remove extraneous information like 'for the estates of...'
    org_fn_l = org_fn_l.split(' for ')[0]

    # remove extraneous information like 'of the heirs of...'
    org_fn_l = org_fn_l.split(' of ')[0]

    # remove occupations: guardians, etc. 
    org_fn_l = org_fn_l.replace(' guardian', '')
    
    # check if there are two individuals, but check if there are more than 7 words (most likely a society)
    if ' and ' in org_fn_l and len(org_fn_l.split()) <= 7:   
        print('original name= ' + org_fn_l)
        
        # cleaning extraneous information can reveal there to be only one name
        #if ' and ' in org_fn_l:
        person1 = org_fn_l.split(' and ')[0]
        person2 = org_fn_l.split(' and ')[1]
        person1_sp = person1.split() 
        person2_sp = person2.split()

        # recapitalize people's names
        person1_sp = [i.title() for i in person1_sp]
        person2_sp = [i.title() for i in person2_sp]

        # if both individuals only have a last name; put both last names into last name column  ex. edward and joseph
        if len(person1_sp) == 1 and len(person2_sp) == 1:
            row['to whom due | first name'] = ''
            row['to whom due | last name'] = [person1_sp[0], person2_sp[0]] 
            
            print('new last name col (org)=' + listToString(row['to whom due | last name']))
        # if there are three separate last names; put all three into last name column: ex. vance caldwell and vance
        elif len(person1_sp) == 2 and len(person2_sp) == 1:
            row['to whom due | first name'] = ''
            row['to whom due | last name'] = [person1_sp[0], person1_sp[1], person2_sp[0]]
            print('new last name col=' + listToString(row['to whom due | last name']))
        # if both individuals belong to the same family; put names into respective cols: ex. peter and isaac wikoff  
        elif len(person1_sp) == 1 and len(person2_sp) == 2:
            row['to whom due | first name'] = [person1_sp[0], person2_sp[0]]
            row['to whom due | last name'] = person2_sp[1]
            print('new first name col=' + listToString(row['to whom due | first name']))
            print('new last name col=' + listToString(row['to whom due | last name']))
        # if both individuals are two completely different people with full names; ex. john doe and james hill
        elif len(person1_sp) == 2 and len(person2_sp) == 2:
            row['to whom due | first name'] = [person1_sp[0], person2_sp[0]]
            row['to whom due | last name'] = [person1_sp[1], person2_sp[1]]
            print('new first name col=' + listToString(row['to whom due | first name']))
            print('new last name col=' + listToString(row['to whom due | last name']))
        # if either individual has a middle name; group middle names with the last name; ex. john hill doe and james madison hill
        elif len(person1_sp) == 3 or len(person2_sp) == 3:
            row['to whom due | first name'] = [person1_sp[0], person2_sp[0]]
            # determine which individual has the middle name
            if len(person1_sp) == 3:
                person2_ln = ''
                if len(person2_sp) > 1:
                    person2_ln = person2_sp[1]
                
                row['to whom due | last name'] = [person1_sp[1] + ' ' + person1_sp[2], person2_ln]
                print('new last name col=' + listToString(row['to whom due | last name']))
            elif len(person2_sp) == 3:
                person1_ln = ''
                if len(person1_sp) > 1:
                    person1_ln = person1_sp[1]
                
                row['to whom due | last name'] = [person1_ln, person2_sp[1] + ' ' + person2_sp[2]]
                print('new last name col=' + listToString(row['to whom due | last name']))
            # both individuals have a middle name 
            else:
                row['to whom due | last name'] = [person1_sp[1] + ' ' + person1_sp[2], person2_sp[1] + ' ' + person2_sp[2]]
                print('new last name col=' + listToString(row['to whom due | last name']))
        
        # handle all other types of names manually
        else:
            if org_fn in manual_corrects:
                new_fname = str(manual_corrects[org_fn][0])
                new_lname = str(manual_corrects[org_fn][1])
            else:
                new_fname = input('new first name: ')
                new_lname = input('new last name: ') 
                manual_corrects[org_fn] = [new_fname, new_lname]

            row['to whom due | first name'] = new_fname.capitalize()
            row['to whom due | last name'] = new_lname.capitalize()
        
        # record change 
        add_changes(row['to whom due | title'], row['to whom due | title'], org_fn, org_ln, 
                row['to whom due | first name'], row['to whom due | last name'], 3, row['org_file'], row['org_index'])
            
        print('+------------------------------+')
    # might be a corporation or many names; manually fix
    elif ' and ' in org_fn_l and len(org_fn_l.split()) > 7:
        print('original name= ' + org_fn_l)
         # check if name has already been manually cleaned
        if org_fn in manual_corrects:
            new_fname = str(manual_corrects[org_fn][0])
            new_lname = str(manual_corrects[org_fn][1])
        else:
            new_fname = input('new first name: ')
            new_lname = input('new last name: ') 
            manual_corrects[org_fn] = [new_fname, new_lname]

        row['to whom due | first name'] = new_fname.capitalize()
        row['to whom due | last name'] = new_lname.capitalize()
        
        # record change 
        add_changes(row['to whom due | title'], row['to whom due | title'], org_fn, org_ln, 
                row['to whom due | first name'], row['to whom due | last name'], 3, row['org_file'], row['org_index'])

        print('new first name col=' + listToString(row['to whom due | first name']))
        print('new last name col=' + listToString(row['to whom due | last name']))

        print('+------------------------------+')
    
    # capitalize the names properly 
    row['to whom due | first name'] = row['to whom due | first name']
    row['to whom due | last name'] = row['to whom due | last name']
        
    return row

agg_debt = agg_debt.apply(lambda row: handle_two_name(row), axis=1)

# save manual corrections 
manual_corrects_df = pd.DataFrame.from_dict(manual_corrects, orient='index') 
manual_corrects_df.columns = ['new first name', 'new last name']
manual_corrects_df.to_csv(INDIR_RAW / 'corrections/name_fix.csv')

# if there are debt entries with multiple individuals, split them into their own rows
agg_debt = agg_debt.explode('to whom due | first name')
agg_debt = agg_debt.explode('to whom due | last name')
# reindex
agg_debt['index'] = agg_debt.index


# In[ ]:


#Names that are entirely in the first or last name column

def correct_full_names_in_column(row):
    if row["organization?"] == True: return row #ignore orgnizations
    fname = str(row["to whom due | first name"])
    lname = str(row["to whom due | last name"])
    name = None
    if (len(lname.split()) == 0 or "nan" in lname or "NaN" in lname) and len(fname.split()) >= 2:
        name = HumanName(fname)
    if (len(fname.split()) == 0 or "nan" in fname or "NaN" in fname) and len(lname.split()) >= 2:
        name = HumanName(lname)
    if name == None:
        return row
    else:
        #save_manual_correction(row["to whom due | title"], fname, lname, row["to whom due | title"], name.first, name.last, 9, row["org_file"], row["org_index"], is_manual=False)
        add_changes(row["to whom due | title"], row["to whom due | title"], row["to whom due | first name"], fname, row["to whom due | last name"], lname, 9, row["org_file"], row["org_index"])
        row["to whom due | first name"] = name.first
        row["to whom due | last name"] = name.last
        return row

agg_debt = agg_debt.apply(lambda row: correct_full_names_in_column(row), axis=1)


# In[ ]:


#Filling in blank columns

def handle_blank_name_cols(row):
    fname = str(row["to whom due | first name"])
    lname = str(row["to whom due | last name"])
    if fname == "": fname = "UNDEFINED" # if there is no first name, make it undefined
    elif lname == "": lname = "UNDEFINED" # if there is no last name, make it undefined
    else: return row # if both aren't blank, return the row now
    #save_manual_correction(row["to whom due | title"], row["to whom due | first name"], row["to whom due | last name"], row["to whom due | title"], fname, lname, 7, row["org_file"], row["org_index"], is_manual=False)
    add_changes(row["to whom due | title"], row["to whom due | title"], row["to whom due | first name"], fname, row["to whom due | last name"], lname, 7, row["org_file"], row["org_index"])
    row["to whom due | first name"] = fname
    row["to whom due | last name"] = lname
    return row

agg_debt = agg_debt.apply(lambda row: handle_blank_name_cols(row), axis=1)


# In[ ]:


# Add a deceased column to get ready to mark all deceased owners
agg_debt["deceased?"] = False

# Define the keywords to search for in the name
keywords = [" dead", "deceased", " dec'd", " dec'", " decd", " deceasd"]

# List of names that should not be marked
manual_no_mark_list = ["Slaughter Deadloff"]

# A quick helper function to take a string and check if any keyword is in the string, if so return the keyword found
def check_keyword_in_string(word):
    for keyword in keywords:
        if keyword in word:
            return keyword
    return False

def check_deceased(row):
    fname = str(row["to whom due | first name"])
    lname = str(row["to whom due | last name"])
    fullname = fname + " " + lname #Create a full name to search for keywords
    if fullname in manual_no_mark_list: return row #If the fullname should not be marked, don't mark it
    k = check_keyword_in_string(fullname.lower()) #Use fullname.lower() to make sure string matching works correctly (ie. case-insensitive)
    if k != False: #Meaning a keyword was found
        row["deceased?"] = True #Mark the row
        fname = fname.replace(k, "") #Remove the keyword from the name
        lname = lname.replace(k, "")
        add_changes(row["to whom due | title"], row["to whom due | title"], row["to whom due | first name"], fname, row["to whom due | last name"], lname, 12, row["org_file"], row["org_index"], is_manual=False)
        row["to whom due | first name"] = fname
        row["to whom due | last name"] = lname
    return row

agg_debt = agg_debt.apply(lambda row: check_deceased(row), axis=1)


# In[ ]:


#Abbreviations
abbreviations = {
    'And':'Andrew', 'Ant':'Anthony', 'Bart':'Bartholomew', 'Cha':'Charles', 'Dor':'Dorothy', 'Dot':'Dorothy', 'Doth':'Dorothy',
    'Edw':'Edward', 'Eliz':'Elizabeth', 'Geo':'George', 'H':'Henry', 'Herb':'Herbert', 'Ja':'James', 'Jn':'John', 'Marg':'Margaret', 
    'Mich':'Michael', 'Pat': 'Patrick', 'Rich':'Richard', 'Tho':'Thomas', 'W':'William', 'Will\'m':'William'
}

def handle_abbreviations(row):
    fn = str(row['to whom due | first name'])
    if fn in abbreviations:
        row['to whom due | first name'] = abbreviations[fn]
        # record changes
        add_changes(row['to whom due | title'], row['to whom due | title'], fn, 
                    row['to whom due | last name'], row['to whom due | first name'], 
                    row['to whom due | last name'], 5, row['org_file'], row['org_index'])
    
    return row

agg_debt = agg_debt.apply(lambda row: handle_abbreviations(row), axis=1)


# ## Grouping Consecutive Names 

# In[ ]:


agg_debt[['to whom due | first name', 'to whom due | last name', 'amount | dollars', 'amount | 90th']].head()


# In[ ]:


agg_debt['full name'] = agg_debt['to whom due | first name'] + ' ' + agg_debt['to whom due | last name']
agg_debt['full name'].head()


# In[ ]:


# Create a final_agg_debt index column - The original index of the row in final_agg_debt.csv
agg_debt['final_agg_debt index'] = agg_debt.index

# Identify consecutive rows with the same name
g = (agg_debt['full name'] != agg_debt.shift().fillna(method='bfill')['full name']).cumsum() 

agg_debt['org_index'] = agg_debt['org_index'].astype(str)
agg_debt['final_agg_debt index'] = agg_debt['final_agg_debt index'].astype(str)

# Save the rest of the columns 
columns = {}
for col in agg_debt.columns:
    columns[col] = 'first'

columns['amount | dollars'] = sum 
columns['amount | 90th'] = sum
columns['org_index'] = ' | '.join 
columns['final_agg_debt index'] = ' | '.join 

# Merge consecutive rows with the same name
agg_debt = agg_debt.groupby([g]).agg(columns).drop('full name', axis=1)


# In[ ]:


agg_debt = agg_debt.reset_index(drop=True)


# In[ ]:


agg_debt = agg_debt.drop('index', axis=1)


# In[ ]:


agg_debt.to_csv(OUTDIR / 'agg_debt_grouped.csv') # Save


# In[ ]:


name_changes.to_csv(OUTDIR / "name_changes.csv")


# In[1]:


import pandas as pd


# In[2]:


final_data = pd.read_csv(OUTDIR / "agg_debt_grouped.csv")
final_data.dtypes


# In[3]:


final_data.isnull().all()


# In[18]:


final_data["exchange"].dropna()


# In[ ]:




