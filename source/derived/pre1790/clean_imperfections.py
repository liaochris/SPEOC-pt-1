#!/usr/bin/env python
# coding: utf-8

# # File Organization
#  - Imports
#  - Load & create dataframes
#  - Declare Helper functions
#  - Manual corrections & dropping invalid rows
#  - Standardizing Town/State/Estate/Heir of (4 & 8)
#  - Standardizing names containing 'of' that are entirely in the first name column (14)
#  - Companies (2)
#  - Entries with 2 names (3)
#  - Names that are entirely in the first or last name column (9)
#  - Filling in blank columns (7)
#  - Deceased individuals (12)
#  - abbreviations (5)
#  - Group consecutive names (1)
#  - Ancestry code (6)
# 
# Refer to the 3rd cell (underneath imports) for information on each cleaning case (the numbers in parentheses above).

# In[1]:


#Imports
from pathlib import Path
import pandas as pd
import datetime
import numpy as np
import json
import os
from fuzzywuzzy import fuzz

import nltk
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree
import ssl

from nameparser import HumanName

OUTDIR = Path("output/derived/pre1790")


# In[2]:


#Load the aggregated file
#og_df = original dataframe
og_df = pd.read_csv(OUTDIR / "final_agg_debt.csv")

#Load the changes dataframe
corrections_df = None
if not os.path.exists(OUTDIR / "name_changes_liam.csv"):
    corrections_df = pd.DataFrame({'og_title': pd.Series(dtype='str'),
                       'og_fname': pd.Series(dtype='str'),
                       'og_lname': pd.Series(dtype='str'),
                       'new_title': pd.Series(dtype='str'),
                       'new_fname': pd.Series(dtype='str'),
                       'new_lname': pd.Series(dtype='str'),
                       'cleaning_case': pd.Series(dtype='int'),
                       'file_loc': pd.Series(dtype='str'),
                       'org_index': pd.Series(dtype='int')})
else:
    corrections_df = pd.read_csv(OUTDIR / "name_changes_liam.csv")


# ### Helper functions
#  - retrieve_correction: Get the correction for the title, fname and lname in the dataframe
#  - save_correction: Save the correction, given the original and new names
#  - process_date: (Unused) Correct dates by prompting the user
#  - text_contains_human_name: Returns an array of human names in the supplied text, empty array if no human names. More information from [this blog post](https://unbiased-coder.com/extract-names-python-nltk/)

# In[3]:


#Ask running user if they want to enable manual corrections
enable_manual_corrections = input("Enable manual correction system (yes, no)? (DO NOT ENABLE IF YOU ARE NOT READY TO MAKE MANUAL CORRECTIONS) > ")
enable_manual_corrections = True if enable_manual_corrections == "yes" else False

def retrieve_correction(og_title, og_fname, og_lname):
    '''
    Looks for a correction in the corrections dataframe
    '''
    for index, row in corrections_df.iterrows():
        if row["og_title"] == og_title and row["og_fname"] == og_fname and row["og_lname"] == og_lname:
            return (row["new_title"], row["new_fname"], row["new_lname"])
    return None

def save_manual_correction(og_title, og_fname, og_lname, new_title, new_fname, new_lname, clean_case, file, org_i, is_manual):
    """
    Saves a correction to the correction df
    """
    if is_manual and not enable_manual_corrections: return
    corrections_df.loc[len(corrections_df.index)] = [
        og_title, og_fname, og_lname,
        new_title, new_fname, new_lname,
        clean_case, file, org_i]

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

def process_date(yr, mon, day, is_issued_date: bool, state_code, index):
    """ Dates in the files can sometimes be invalid, specifically:\n
     - month and year are swapped\n
     - Typos in the year column (ex. 17780)\n
     - Dates that are impossible (Feburary 31, there are only 28 days in feburary)\n
    Args:
        yr (int): Year
        mon (int): Month
        day (int): Day
        is_issued_date (bool): specifies whether this date is the date a certificate is issued or the date is the maturity.
        state_code (str): state code
        index (int): index of row

    Returns:
        (int: ordinal of the date (datetime.toordinal(s)), bool: did a manual correction need to be made?)
    """
    try:
        d = datetime.date(int(yr), int(mon), int(day))
        return (d.toordinal(), False)
    except Exception as e:
        if "10: ''" in str(e): #ie. the "Invalid literal for base 10: ''" error, which means blank, which means just make it 0
            return (0, False)
        manual = retrieve_manual_correction(state_code, index)
        if manual == None:
            if 'month must' in str(e): #ie. month must be in range 1..12 - just swap month and day
                d = datetime.date(yr, day, mon)
                return (d.toordinal(), False)
            new = input(f"{state_code}: {'RE, ' if ('range' in str(e)) else ''}{'Issued: ' if is_issued_date else 'Expiries: '} {yr} {mon} {day} (yr-mon-day):")
            if new == "" and is_issued_date == False:
                return (0, False)
            d = datetime.date(int(new.split()[0]), int(new.split()[1]), int(new.split()[2]))
            return (d.toordinal(), True)
        else:
            return (int(manual[1].split('-')[0]) if is_issued_date else int(manual[1].split('-')[1]), False)


# # Manual Corrections
# 
# <b>Goal: </b>Remove very long names
# 
# <b>Step: </b> Remove rows that contain names longer than 10 words (in either the first name or last name category)

# In[5]:


#Super fast method - instead of going through it and adding to a new dataset,
#use apply with a simple function that doesn't include long strings in a new dataset
og_df = og_df[og_df['to whom due | first name'].apply(lambda name: len(str(name).split()) > 5) == False]
og_df = og_df[og_df['to whom due | last name'].apply(lambda name: len(str(name).split()) > 5) == False]


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
# 3. Example: First name: "State of New York", Last name: "" -> First name: "State", Last name: "New York"
# 4. Example: First name: "Estate of William Garrett", Last name: "" -> First name: "William", Last name: "Garrett"

# In[6]:


agg_debt = pd.DataFrame(columns=og_df.columns)
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
     "new_lname": "Fentom"},
    {"og_fname": "Estate ofJon Bowman",
     "new_title": "",
     "new_fname": "Thomas",
     "new_lname": "Meredith"}
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
            lname =  "-".join(og_fname.split()[2:])
            fname = "State"
            save_manual_correction(title, row["to whom due | first name"], row["to whom due | last name"], title, fname, lname, 8, row["org_file"], row["org_index"], is_manual=False)
            row["to whom due | first name"] = fname
            row["to whom due | last name"] = lname
            row["organization?"] = True
        elif fuzz.ratio(prefix, "town of") >= 88:
            lname =  "-".join(og_fname.split()[2:])
            fname = "Town"
            save_manual_correction(title, row["to whom due | first name"], row["to whom due | last name"], title, fname, lname, 8, row["org_file"], row["org_index"], is_manual=False)
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
            save_manual_correction(title, row["to whom due | first name"], row["to whom due | last name"], title, fname, lname, 4, row["org_file"], row["org_index"], is_manual=False)
            row["to whom due | first name"] = fname
            row["to whom due | last name"] = lname
        elif fuzz.ratio(prefix, "heir of") >= 85 or fuzz.ratio(prefix, "heirs of") >= 85:
            name = " ".join(og_fname.split()[2:])
            fname =  name.split()[0]
            lname = name.split()[1:] if len(name.split()) > 1 else ""
            save_manual_correction(title, row["to whom due | first name"], row["to whom due | last name"], title, fname, lname, 4, row["org_file"], row["org_index"], is_manual=False)
            row["to whom due | first name"] = fname
            row["to whom due | last name"] = lname
    return row

agg_debt = og_df.apply(lambda row: handle_ofs(row), axis=1)


# # Organizations
# 
# <b>Goal: </b> Catch and mark any organizations that were not caught in the above cell
# 
# <b>Steps: </b>
# 1. Handle any manual corrections
# 2. Use NLTK to check if a name is an organization
# 
# <b>Notes: </b>
# 1. NLTK is much more accurate when detecting if an entry is a person versus an organization, so anything not marked as a person is assumed to be an organization (that has the keyword "of" in the first name)

# In[22]:


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
        before_of, after_of = og_fname.split("of")
        fname = before_of.strip().replace("-", "")
        lname = after_of.strip().replace("-", "")
        save_manual_correction(title, og_fname, og_lname, title, fname, lname, 14, row["org_file"], row["org_index"], is_manual=False)
        row["to whom due | first name"] = fname
        row["to whom due | last name"] = lname
    return row

agg_debt = agg_debt.apply(lambda row: handle_all_orgs(row), axis=1)


# # Name in only first or last name column
# 
# <b>Goal: </b>Some names are entirely in the first name column or last name column, so split the name into their respective categories
# 
# <b>Steps: </b>
# 1. Check if one column has a name and the other is blank
# 2. Use the human name parser library to determine the first name and last names. 
# 3. Put each person's first name and last name in the respective columns
# 4. Record change in ```name_changes```.

# In[8]:


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
        save_manual_correction(row["to whom due | title"], fname, lname, row["to whom due | title"], name.first, name.last, 9, row["org_file"], row["org_index"], is_manual=False)
        row["to whom due | first name"] = name.first
        row["to whom due | last name"] = name.last
        return row

agg_debt = agg_debt.apply(lambda row: correct_full_names_in_column(row), axis=1)


# # Mark blank name columns with UNDEFINED
# 
# <b>Goal: </b>Mark name columns (first name, last name) that are blank with UNDEFINED.
# 
# <b>Steps: </b>
# 1. If ```to whom due | first name``` is blank, fill it in with the word UNDEFINED
# 2. If ```to whom due | last name``` is blank, fill it in with the word UNDEFINED
# 3. Record change in ```name_changes```.

# In[76]:


def handle_blank_name_cols(row):
    fname = str(row["to whom due | first name"])
    lname = str(row["to whom due | last name"])
    if fname == "": fname = "UNDEFINED" # if there is no first name, make it undefined
    elif lname == "": lname = "UNDEFINED" # if there is no last name, make it undefined
    else: return row # if both aren't blank, return the row now
    save_manual_correction(row["to whom due | title"], row["to whom due | first name"], row["to whom due | last name"], row["to whom due | title"], fname, lname, 7, row["org_file"], row["org_index"], is_manual=False)
    row["to whom due | first name"] = fname
    row["to whom due | last name"] = lname
    return row

agg_debt = og_df.apply(lambda row: handle_blank_name_cols(row), axis=1)


# # Deceased Individuals
# 
# <b>Goal: </b>Add a column and mark each row if the individual is deceased
# 
# <b>Steps: </b>
# 1. Check if a keyword is present in either name column
# 2. If so, mark the row as deceased and remove the keyword from whatever column it was found in
# 3. Record changes in ```name_changes```.

# In[14]:


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
        save_manual_correction(row["to whom due | title"], row["to whom due | first name"], row["to whom due | last name"], row["to whom due | title"], fname, lname, 12, row["org_file"], row["org_index"], is_manual=False)
        row["to whom due | first name"] = fname
        row["to whom due | last name"] = lname
    return row

agg_debt = og_df.apply(lambda row: check_deceased(row), axis=1)

