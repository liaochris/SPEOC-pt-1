#!/usr/bin/env python
# coding: utf-8

# # Cleaning Names

# The purpose of this notebook is to clean the names of individuals. All the problems that we aim to fix in this notebook are listed [here](https://docs.google.com/document/d/1pcSQfWNll6K9tl-_rB4lztN0TsZsclU9vOnbyQob-Zs/edit).

# In[1]:


# import all the necessary packages
from pathlib import Path
import pandas as pd
import numpy as np
import re
import csv
import ast

INDIR_RAW = Path("source/raw/pre1790")
OUTDIR = Path("output/derived/pre1790")


# In[2]:


# import aggregated debt file
agg_debt = pd.read_csv(OUTDIR / 'final_agg_debt.csv')


# In[3]:


print(agg_debt.dtypes)


# ## Documenting Changes

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
# - Clean company names = 2,
# - Handle two names = 3,
# - Handle abbreviations = 5,
# - Standardize names (Ancestry) = 6

# In[4]:


# record changes in this dataframe
name_changes = pd.DataFrame({'title_org': pd.Series(dtype='str'),
                       'title_new': pd.Series(dtype='str'),
                       'first_name_org': pd.Series(dtype='str'),
                       'last_name_org': pd.Series(dtype='str'),
                       'first_name_new': pd.Series(dtype='str'),
                       'last_name_new': pd.Series(dtype='str'),
                       'cleaning case': pd.Series(dtype='int'),
                       'file_loc': pd.Series(dtype='str'),
                       'org_index': pd.Series(dtype='int')})


# In[5]:


def add_changes(title_org, title_new, fn_org, ln_org, fn_new, ln_new, case, file, index):
    new_row = [title_org, title_new, fn_org, ln_org, fn_new, ln_new, case, file, index]
    name_changes.loc[len(name_changes.index)] = new_row


# ## Company Names

# <b>Goal: </b> Some debt entries are actually company names or represent a group of people (example: ```James Vernon & Co.```). 
# 
# <b>Steps: </b>
# 1. Use string parsing to find if a debt entry has '& co' or '& others' in it's name. Note: I noticed these company names appear in the first name column. I do <b>not</b> run this program on the last name column.
# 2. I remove the '& co' or '& others' from the name. I use a human name parser library. This library can find out what parts of the name are the first name versus last name. 
# 3. I put the first name and last name in their own respective columns. 
# 4. Record name change in ``name_changes``.

# In[6]:


# retrieve manual corrections from csv file if they exist 
manual_corrects_df = pd.read_csv(INDIR_RAW / 'corrections/manual_corrections.csv')
manual_corrects_dict = manual_corrects_df.to_dict(orient='index')
manual_corrects = {}
# add manual corrections to manual_corrects dictionary 
for correction in manual_corrects_dict.keys():
    manual_corrects[manual_corrects_dict[correction]['Unnamed: 0']] = [manual_corrects_dict[correction]['new first name'], manual_corrects_dict[correction]['new last name']]

print(manual_corrects)


# In[7]:


# dictionary of manual changes i have to make 
changes = {
    'Henry Mc Clellen & Henry & co' : 'Henry Mc Clellen & Co'
}

conn_words = [' for ', ' of ', ' and '] # these are connector key words
corp_key_words = ('corporation', ' and co', ' and coy', ' and others', ' and several others', ' and heirs', ' and comp', ' and other trustees') # these are corporation key words


# In[8]:


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
            print('old name=' + str(org_fname))      
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


# In[9]:


# checkup on name_changes
name_changes.tail()


# In[10]:


agg_debt['Unnamed: 0'] = agg_debt.index


# In[11]:


agg_debt.rename(columns={'Unnamed: 0' : 'index'}, inplace=True)


# ## Cleaning Entries with Two Names

# <b>Goal: </b>There are debt entries that have two names in a single cell: ```NY_2422: Messes Williamson & Beckman```. The plan is to split the name across the first name and last name columns. Note: I have to check naming conventions during thre 1700s. 
# 
# <b>Steps: </b>
# 1. Use string parsing to check if the name contains '&' or 'and' and split the string accordingly. 
# 2. Use the human name parser library to determine the first name and last names. 
# 3. Put each person's first name and last name in the respective columns, split by ```|``` to separate both individuals' names. 
# 4. Record change in ```name_changes```.
# 
# <b>Examples of different formats</b>
# - James and Ash 
# - William Miller and John Gamble

# In[12]:


changes = {
    'van zandt & kittletas' : ['', 'van zandt | kittletas'],
    'trustees of & davids church':['trustees of & davids church', '']
}


# In[13]:


# make sure all names are of type: str
agg_debt[['to whom due | first name', 'to whom due | last name']] = agg_debt[['to whom due | first name', 'to whom due | last name']].astype(str)


# In[14]:


# function to convert
def listToString(s):
 
    # initialize an empty string
    str1 = " "
 
    # return string
    return (str1.join(s))


# In[15]:


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


# In[16]:


# save manual corrections 
manual_corrects_df = pd.DataFrame.from_dict(manual_corrects, orient='index') 
manual_corrects_df.columns = ['new first name', 'new last name']
manual_corrects_df.to_csv(INDIR_RAW / 'corrections/manual_corrections.csv')


# In[17]:


# if there are debt entries with multiple individuals, split them into their own rows
agg_debt = agg_debt.explode('to whom due | first name')
agg_debt = agg_debt.explode('to whom due | last name')
# reindex
agg_debt['index'] = agg_debt.index


# In[18]:


# checkup on name_changes
name_changes.tail()


# ## Handle Abbreviations of a Name

# <b>Goal: </b>There are individuals who have a handwritten abbreviation of a name in their debt entry. Thanks to Chris, he found a website with all these [abbreviations](https://hull-awe.org.uk/index.php/Conventional_abbreviations_for_forenames). 
# 
# <b>Steps: </b>
# 1. Copy and past the name abbreviations from the website into a dictionary. 
# 2. Iterate through each row in the dataframe.
# 3. Check if the name is an abbreviation and change accordingly. 
# 4. Record changes. 
# 

# In[19]:


abbreviations = {
    'And':'Andrew', 'Ant':'Anthony', 'Bart':'Bartholomew', 'Cha':'Charles', 'Dor':'Dorothy', 'Dot':'Dorothy', 'Doth':'Dorothy',
    'Edw':'Edward', 'Eliz':'Elizabeth', 'Geo':'George', 'H':'Henry', 'Herb':'Herbert', 'Ja':'James', 'Jn':'John', 'Marg':'Margaret', 
    'Mich':'Michael', 'Pat': 'Patrick', 'Rich':'Richard', 'Tho':'Thomas', 'W':'William', 'Will\'m':'William'
}


# In[20]:


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


# In[21]:


# checkup on name_changes
name_changes.tail()


# ## Grouping Consecutive Names - David

# In[22]:


agg_debt[['to whom due | first name', 'to whom due | last name', 'amount | dollars', 'amount | 90th']].head()


# In[23]:


agg_debt['full name'] = agg_debt['to whom due | first name'] + ' ' + agg_debt['to whom due | last name']
agg_debt['full name'].head()


# In[24]:


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


# In[25]:


agg_debt = agg_debt.reset_index(drop=True)


# In[26]:


agg_debt = agg_debt.drop('index', axis=1)


# In[27]:


agg_debt.to_csv(OUTDIR / 'agg_debt_grouped.csv') # Save


# In[28]:


breakpoint

