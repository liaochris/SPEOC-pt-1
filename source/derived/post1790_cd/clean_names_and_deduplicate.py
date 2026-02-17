#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd


# ## Helper Functions and Structures

# In[2]:


def deNaN(series):
    """
    amends pandas series by replacing NaN values with empty strings
    :param series: pandas series
    """

    return series.apply(lambda x: "" if type(x) != str else x)


def simpleSplit(name):
    """
    split two people with the same last name. example: John and James Davenport
    :param name: input name
    :return: two separate names
    """
    name2 = name.split(" and ")[1]
    lname2 = name2.split(" ")[-1] if "Van" not in name2 else " ".join(name.split(" ")[-2:])
    name1 = name.split(" and ")[0] + " " + lname2
    return " | ".join([name1, name2])


def simpleSplit2(name):
    """
    split two people with different last names whose names are separated by "and"
    :param name: input name
    :return: two separate names
    """
    try:
        name2 = name.split(" and ")[1]
        name1 = name.split(" and ")[0]
    except:
        name2 = name.split(" And ")[1]
        name1 = name.split(" And ")[0]
    return " | ".join([name1, name2])


def tNameList(lst):
    """
    takes a list of names and returns a string of names separated by " | ", sorted and with duplicates removed
    :param lst: input lst
    :return: string with names joined
    """
    return " | ".join(sorted(list(set(lst))))


# ## Prepare List of Names

# In[3]:


# import data
CD_merged = pd.read_csv("../data_clean/aggregated_CD_post1790.csv", index_col=0)

# create name df
names = CD_merged[
    ['Name', 'First Name', 'Last Name', 'new_town', 'county', 'new_state', 'country', 'name_type']].fillna(
    "").drop_duplicates()


# In[4]:


names['Name_Fix'] = names['Name']


# In[5]:


# cleaning names - identify names to be cleaned
names['Name_Fix'] = names['Name_Fix'].apply(
    lambda x: x.lower().replace("and sons", "").replace("and son", "").replace("and co", "").replace("and others",
                                                                                                     "").replace(
        " mpany", "").replace(" mpaney", "").replace('as guardian', '').replace("and brothers", "").replace("and co\'",
                                                                                                            "").replace(
        '  ', ' ').strip().title().replace("And", "and"))

# list key words that classsify a name as one that needs to be fixed
name_fix_inds = names[names['Name_Fix'].apply(lambda x: ' and ' in x.lower() or
                                                        ' of ' in x.lower() or
                                                        'treas' in x.lower() or
                                                        ' to ' in x.lower() or
                                                        'adm ' in x.lower() or
                                                        ' adm' in x.lower() or
                                                        ' exec ' in x.lower() or
                                                        'agents' in x.lower() or
                                                        ' no ' in x.lower() or
                                                        ' comm' in x.lower() or
                                                        ' for ' in x.lower())].index


# ## Known Cleaning Process

# In[6]:


# group of names that have a particular form that need to be fixed
simplefix = ['John and James Davenport', 'Eunice and Betsey Wadsworth', 'Daniel and Elijah Boardman',
             'Dan and Elijah Boardman',
             'Samuel and Timothy Burr', 'Michael and Thomas Bull', 'Elias and Jeremiah Cowles',
             'Amasa and Elnathan Keyes', 'Horace and Seth Johnson',
             'Richard and James Potter', 'Elizabeth and John Grover', 'Nicholas and Hannah Cooke',
             'Moses and Nicholas Brown',
             'Samuel and Charles Sampson', 'John and Hugh Irvin', 'Jonathan and Mariamne Williams',
             'Jacob and Philip Mark', 'John and Nicholas J Roosevelt', 'Isaac and Henry Truax',
             'Catherine and Rachel Dow', 'Charles and J Shaw',
             'W and J Heyer', 'George and Edm Morewood', 'William and James Constable',
             'Horace and Seth Johnston', 'Michael and Thomas Bull', 'Daniel and E Marsh',
             'Michael and Abraham Van Peene', 'John and Alexander Mowatt', 'Alexander and Michael Mowatt',
             "Moses and Charles Ogden", "John and Francis Atkinson", "Abraham and James Cole"]
# replace names, then remove duplicates and reformat in our combined name format
names['Name_Fix'] = names['Name_Fix'].apply(
    lambda x: tNameList([simpleSplit(ele) if ele in simplefix else ele for ele in x.split(" | ")]))


# In[7]:


# group of names that have another form that need to be fixed
simplefix2 = ['Joshua Belden and James Wells', 'William Joseph and Richard Hart', 'Anthony Bradford and Stephen Hall',
              'John Dodd and John Porter',
              'Uriah Forrest and Benjamin Stoddert', 'Samuel John and Thomas Snowden',
              'John Laird and Thomas Dick', 'James Boyd and Jonathan B Smith', 'Nathan Waterman and Robert Newell',
              'Joseph Jenckes and David L Barnes',
              'Henry Laurens and Arnoldus Vanderhorst', 'Love Stone and Joseph Vesey',
              'Charles Stuart and James Mcculloch',
              'Robert Daniel and Guilian Crommelin']
# replace names, then remove duplicates and reformat in our combined name format
names['Name_Fix'] = names['Name_Fix'].apply(
    lambda x: tNameList([simpleSplit2(ele) if ele in simplefix2 else ele for ele in x.split(" | ")]))


# In[8]:


# fix people with "Treasurer in name among our problematic names
t_ind = names.loc[name_fix_inds][names.loc[name_fix_inds, 'Name_Fix'].apply(
    lambda x: 'treasurer' in x.lower() and 'cincinnati' not in x.lower())].index
# remove certain phrases
newvals = names.loc[t_ind, 'Name_Fix'].apply(lambda x: tNameList(
    [ele.replace('Society', '').replace('Proprietors', '').split("Treasurer")[0].strip() for ele in x.split(" | ")]))
names.loc[t_ind, 'Name_Fix'] = newvals


# In[9]:


# fix people with "transfer" and "of"" in name
trans_ind = names.loc[name_fix_inds][names.loc[name_fix_inds, 'Name_Fix'].apply(
    lambda x: all(['transfer' in ele.lower() and 'from' in ele.lower() for ele in x.split(" | ")]))].index
newvals = names.loc[trans_ind, 'Name_Fix'].apply(lambda x: tNameList(
    [ele.lower().split("transfer")[0].strip().title().replace(" And", "").split("In Trust")[0].strip() for ele in
     x.split(" | ")]))
names.loc[trans_ind, 'Name_Fix'] = newvals


# In[10]:


# fix people with "school" in name
s_ind = names.loc[name_fix_inds][
    names.loc[name_fix_inds, 'Name_Fix'].apply(lambda x: " school " in x.lower() and "com" in x.lower())].index
newvals = names.loc[s_ind, 'Name_Fix'].apply(lambda x: tNameList(
    [ele.lower().split("school")[0].replace("hon", "").replace("society committee", "").strip().title() for ele in
     x.split(" | ")]))
names.loc[s_ind, 'Name_Fix'] = newvals


# ## Import Name Fixes

# In[11]:


# import list of manual changes we make to names, then apply them
df_comp = pd.read_csv('clean_tools/company_names_fix.csv', index_col=0)
df_comp_dict = dict(zip(df_comp['original'].apply(lambda x: x.lower()), df_comp['new']))
names['Name_Fix'] = names['Name_Fix'].apply(lambda x: df_comp_dict.get(x.lower(), x) if not pd.isnull(x) else x)


# In[12]:


# remove duplicates and sort alphabetically
names['Name_Fix'] = names['Name_Fix'].apply(lambda x: x.replace("  ", " ").strip())
names['Name_Fix'] = names['Name_Fix'].apply(lambda x: tNameList(x.split(" | ")))


# ## Manual Fixes

# In[13]:


# manually fix some names that have issues that the above process did not solve
names.loc[names[names['Name_Fix'].apply(lambda x: 'virginia' in x.lower())].index, 'Name_Fix'] = [
    'Daniel Carroll Brant | Daniel Carroll Brent', 'Charles Lee | Richard Lee']
names.loc[names[names['Name_Fix'].apply(lambda x: 'the fred' in x.lower())].index, 'Name_Fix'] = ['Frderick Smith']
names.loc[names[names['Name_Fix'].apply(lambda x: 'dr ' in x.lower())].index, 'Name_Fix'] = [
    'William Handy | Philip N Brown']


# In[14]:


# export names that we want to do research on to figure out identities to check folder
change_index = names[names['Name'] != names['Name_Fix']].index
exc_ind = names[names.apply(lambda x: (x['Name'] == x['Name_Fix'] and ' and ' in x['Name']) or (
        x['Name'] != x['Name_Fix'] and ' and ' in x['Name_Fix']), axis=1)].index
names.drop(['First Name', 'Last Name'], axis = 1).loc[exc_ind].to_csv('../data_clean/check/company_research.csv')


# ## Create Dataset with Names Formatted for Scraping

# In[15]:


# create dataframe that contains first/last names
df_cols = ['Name', 'Fn_Fix', 'Ln_Fix', 'new_town', 'county', 'new_state', 'country', 'name_type', 'Name_Fix']
name_df = pd.DataFrame(columns=df_cols)
# exceptions where we have to handle fn/ln separation differently
# these are names we cannot search for on the scraper because they are not person names
excep_vals = [
    "Trustees Of 2Nd R Church | Trustees Of The Second Presbeterian Church | Trustees Of The Second Presbyterian",
    "The State Of Georgia",
    "The Trustees Of Frederick County | The Trustees Of Frederick County Poor | Trustees Of Frederick County Poor",
    "The Treasurer Of Cincinnati | The Treasurer Of The Cincinnati | The Treasurer Of The Cincinnati Of Maryland",
    "The Trustees Of Preb Church Work Joseph Buck County | Trustees Of The Presbyterean Church Warwick Township Bucks | Trustees Of The Presbyterian Church",
    "Society For Releif Of Poor Distressd Masters Of Ships | Society For The Relief Of Poor and Distressed Masters Of Ships Their Widows",
    "Jackson and Nightingale",
    "Nesmoz and Valiant | Nesmoz and Valliant",
    "Jackson and Evans | Jackson and Evens",
    "Trustees Of Prebn Church Abarwick Bucks County | Trustees Of The Presbyterean Church Warwick Township Bucks | Trustees Of The Presbyterian Church",
    "Trustees Of Prebn Church Abarwick Bucks",
    "Trustees Of The Presbyterian",
    "Bull and Keyes",
    "Saybrook 1St Society",
    "Fairfield 1St Society School",
    "State Of Connecticut",
    "Treasurer Of The Cincinnati Society Of Georgia",
    "Lamb and Chukley",
    "The Elders Of The Congregation",
    "Barclay and Mckean",
    "State Of New Hampshire",
    "The Trustees Of Phillips Academy",
    "Town Of Canterbury",
    "Corporation For The Relief Of Poor and Distressed Presbyterian Ministers",
    "Nesmoz and Valliant",
    "Greene and Cleverly",
    "Mann and Low",
    "Hoppin and Snow",
    "Brown and Francis",
    "Bank Of Providence",
    "President Directors Of The Bank Of Providence",
    "Vos and Graves",
    "The State Of South Carolina",
    "Watson and Greenleaf",
    "Brochholz and Livingston",
    "Anspach and Rogers",
    "Berry and Rogers",
    "Gardner and Rodman",
    "Haydock and March",
    "Robinson and Hartshorn",
    "Armstrong and Barnswall",
    "Amshong and Barnwall",
    "Bleeker and March",
    "Cooke and Cushing",
    "Coxe and Meilan",
    "Loomis and Tillinghast",
    "Chevallier and Rainctaux",
    "Phym, Ellice and Ingliss",
    "Coxe and Meilan",
    "The Treasurer Of The Cincinnati Of Maryland",
    "The Trustees Of Phillips Academy",
    "Trustees Of The Presbyterean Church Warwick Township Bucks",
    "Trustees Of The Second Presbeterian Church",
    "The Commonwealth Of Pennsylvania",
    "The President Of Bank Of Providence From The Books In Massachusetts",
    "The Trustees Of The Second Presbyterian Church In Philadelphia"
]

for ind in names.index:
    if (not pd.isnull(names.loc[ind, 'Last Name']) or "|" in names.loc[ind, 'Name_Fix']) and names.loc[
        ind, 'Name_Fix'] not in excep_vals:
        # if names are the same, just add the name
        for name in names.loc[ind, 'Name_Fix'].split(" | "):
            # split names for fn/ln,include last 2 for last name if ii in last name
            if ' van de ' in name.lower() or ' de la ' in name.lower():
                if ' de la ' in name.lower():
                    ln = " ".join(name.split(" ")[-3:])
                    fn = " ".join(name.split(" ")[:-3])
                else:
                    ln = " ".join(name.split(" ")[1:])
                    fn = " ".join(name.split(" ")[:1])
            elif ' de ' in name.lower():
                ln = " ".join(name.split(" ")[-2:])
                fn = " ".join(name.split(" ")[:-2])
            elif "ii" in name.lower() or '2nd' in name.lower() or ' van ' in name.lower() or ' ten ' in name.lower() or ' del ' in name.lower():
                ln = " ".join(name.split(" ")[-2:])
                fn = " ".join(name.split(" ")[:-2])
            else:
                ln = " ".join(name.split(" ")[-1:])
                fn = " ".join(name.split(" ")[:-1])
            # get rest of information for name, reset fn/ln columns, rename columns
            res = names.loc[[ind]].copy()
            res['First Name'] = fn
            res['Last Name'] = ln
            res.columns = df_cols
            # add to dataframe
            name_df = pd.concat([name_df, res])


# In[16]:


# Joseph Stiles = society of poor and distressed masters of ships and their widows


# In[17]:


name_df.to_csv('clean_tools/name_list.csv')


# In[18]:


# next we want to add the name fix column to the CD debt dataframe
CD_merged_names = pd.merge(CD_merged.fillna(""), name_df[['Name', 'Name_Fix', 'new_town', 'county', 'new_state', 'country', 'name_type']].drop_duplicates(),how = 'left')
CD_merged_names.loc[CD_merged_names[CD_merged_names['Name_Fix'].isnull()].index, 'Name_Fix'] = CD_merged_names.loc[CD_merged_names[CD_merged_names['Name_Fix'].isnull()].index, 'Name']


# In[19]:


CD_merged_names.to_csv('../data_clean/aggregated_CD_post1790_names.csv')


# In[36]:


print(df_comp.loc[[0,1,38]].to_markdown())

