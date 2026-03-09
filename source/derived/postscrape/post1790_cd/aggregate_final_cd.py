#!/usr/bin/env python
# coding: utf-8

# In[387]:


from pathlib import Path
import pandas as pd
from source.lib.ancestry_scraper.config import STATE_ABBREVIATIONS

INDIR_RAW = Path("source/raw/post1790_cd")
INDIR_PRESCRAPE = Path("output/derived/prescrape/post1790_cd")
OUTDIR = Path("output/derived/postscrape/post1790_cd")
INDIR_SCRAPE = Path("output/scrape/post1790_cd_census_match")


# ## Helper Structures

# In[388]:


statedict = STATE_ABBREVIATIONS
statedict_rev = {v: k for k, v in STATE_ABBREVIATIONS.items()}


# ## Helper Functions

# In[389]:


def parseLocationString(location, nametype):
    """
    function to parse location string that I can use when cleaning data

    :param location: string contaiing information about town county state and geo_level separated by |
    :param nametype: type of location
    :return:
    """
    if nametype == 'town':
        return location.split(" | ")[0], location.split(" | ")[1], location.split(" | ")[2], location.split(" | ")[3]
    elif nametype == 'county':
        return "", location.split(" | ")[0], location.split(" | ")[1], location.split(" | ")[2]
    else:  #nametype == 'state'
        return "", "", location.split(" | ")[0], location.split(" | ")[1]


def tNameList(lst):
    """
    takes a list of names and returns a string of names separated by " | ", sorted and with duplicates removed, and with "" removed
    :param lst: input lst
    :return: string with names joined
    """
    return " | ".join(sorted(list(set([ele for ele in lst if ele != ""]))))


# ## Import Data

# In[705]:


# aggregated debt data
CD_clean = pd.read_csv(INDIR_PRESCRAPE / 'geo_standardized_CD_post1790.csv', index_col=0).fillna("").drop_duplicates()
# all names that were scraped by the scraper
scraped_names = pd.read_csv(INDIR_SCRAPE / 'name_list_scraped.csv', index_col=0).fillna("").drop_duplicates()
# results of scraping
match_df = pd.read_csv(INDIR_SCRAPE / 'scrape_results.csv', index_col=0).fillna("").drop_duplicates()
# table that organizes results of scraping based off our list of names
name_df = pd.read_csv(INDIR_PRESCRAPE / 'check/name_changes_list.csv', index_col=0).fillna("").drop_duplicates()


# ## Add Missing Occupations

# In[391]:


# sometimes, an occupation is listed in the name but is not in the occupation column. we want to correct for this by adding the occupaiton title into the occupation column
# do this for treasurers
CD_clean.loc[CD_clean[CD_clean['Name'].apply(lambda x: 'treasurer' in x.lower())].index, 'occupation'] = [
    ele if ele != '' else 'Treasurer' for ele in
    CD_clean.loc[CD_clean[CD_clean['Name'].apply(lambda x: 'treasurer' in x.lower())].index, 'occupation']]
# do this for administrators
CD_clean.loc[
    CD_clean[CD_clean['Name'].apply(lambda x: ' adm' in x.lower() or 'adm ' in x.lower())].index, 'occupation'] = [
    ele if ele != '' else 'Administrator' for ele in CD_clean.loc[
        CD_clean[CD_clean['Name'].apply(lambda x: ' adm' in x.lower() or 'adm ' in x.lower())].index, 'occupation']]
# do this for trustees
CD_clean.loc[CD_clean[CD_clean['Name'].apply(lambda x: ' trust ' in x.lower())].index, 'occupation'] = [
    ele if ele != '' else 'Administrator' for ele in
    CD_clean.loc[CD_clean[CD_clean['Name'].apply(lambda x: ' trust ' in x.lower())].index, 'occupation']]
# do this for guardians
CD_clean.loc[CD_clean[CD_clean['Name'].apply(lambda x: 'guard' in x.lower())].index, 'occupation'] = [
    ele if ele != 'Yeoman' else 'Guardian | Yeoman' for ele in
    CD_clean.loc[CD_clean[CD_clean['Name'].apply(lambda x: 'guard' in x.lower())].index, 'occupation']]
# do this for school committee members
CD_clean.loc[CD_clean[CD_clean['Name'].apply(lambda x: 'school' in x.lower())].index, 'occupation'] = [
    ele if ele != '' else 'School Committee' for ele in
    CD_clean.loc[CD_clean[CD_clean['Name'].apply(lambda x: 'school' in x.lower())].index, 'occupation']]


# ## Merge Data

# In[392]:


# add in both names in cases where one row is identified with multiple name
CD_merged = pd.merge(CD_clean, name_df,
                     how='left',
                     on=['Name', 'new_town', 'county', 'new_state', 'country', 'geo_level', ])
# add in match index and status
CD_merged_mind = pd.merge(CD_merged,
                          scraped_names[
                              ['Fn_Fix', 'Ln_Fix', 'new_town', 'county', 'new_state', 'country', 'geo_level', 'url',
                               'Match Index', 'Match Status']],
                          how='left',
                          on=['Fn_Fix', 'Ln_Fix', 'new_town', 'county', 'new_state', 'country', 'geo_level'])
# combine names
CD_merged_mind['Full Search Name'] = CD_merged_mind['Fn_Fix'] + ' ' + CD_merged_mind['Ln_Fix']


# In[393]:


"""print(CD_clean.loc[[8, 9]][['Name', 'state_data', 'state_data_index', 'new_town', 'county', 'new_state', 'country', 'geo_level',]].to_markdown())
print(name_df.loc[[8, 9]][['Name', 'Fn_Fix', 'Ln_Fix', 'county', 'new_state', 'country', 'geo_level',]].to_markdown())
print(CD_merged.loc[[8,9,10]][['Name', 'state_data', 'state_data_index', 'Name_Fix', 'Fn_Fix', 'Ln_Fix', 'county', 'new_state', 'country', 'geo_level',]].to_markdown())"""


# In[394]:


"""print(CD_merged.loc[[8]][['Name', 'state_data', 'state_data_index', 'Name_Fix', 'Fn_Fix', 'Ln_Fix', 'county', 'new_state', 'country', 'geo_level',]].to_markdown())
print(scraped_names.loc[[8]][['Fn_Fix', 'Ln_Fix','county', 'new_state', 'country', 'geo_level','Match Index', 'Match Status']].to_markdown())
print(CD_merged_mind.loc[[8]][['Name', 'state_data', 'state_data_index', 'Name_Fix', 'Fn_Fix', 'Ln_Fix', 'Full Search Name', 'county', 'new_state', 'country', 'geo_level','Match Index', 'Match Status']].to_markdown())"""


# ## Group Names - Using Ancestry.com Matches
# basically group_name_df is a list of names we're going to group together and then we perform the grouping process

# In[395]:


# find names that are associated with multiple search names because they're actually the same name, by grouping based on match index (have same match index)
# these names are associated with multiple names because of spelling variation
# remove names with "" Match Index - too many
grouped_names = CD_merged_mind[CD_merged_mind['Match Index'] != ""].groupby('Match Index').agg(
    {'Full Search Name': lambda x: list(set(x))}).reset_index()
group_name_df = grouped_names[grouped_names['Full Search Name'].apply(lambda x: len(x) > 1)]
# denote the name we use moving forward as the name with the longest length (most information)
group_name_df['Rep Name'] = group_name_df['Full Search Name'].apply(lambda x: max(x, key=len))
group_name_df = group_name_df.explode('Full Search Name').reset_index(drop=True)


# In[396]:


# some manual corrections of the actual name we want to use for grouping
group_name_df.loc[group_name_df[group_name_df['Full Search Name'].apply(
    lambda x: 'Israel Joseph' in x)].index, 'Rep Name'] = 'Israel Joseph'
group_name_df.loc[group_name_df[group_name_df['Full Search Name'].apply(
    lambda x: 'William Larned' in x or 'William Learned' in x)].index, 'Rep Name'] = 'William Larned'
group_name_df.loc[group_name_df[group_name_df['Full Search Name'].apply(
    lambda x: 'Mathew Watson' in x or 'Matthew Watson' in x)].index, 'Rep Name'] = 'Mathew Watson'
group_name_df.drop(group_name_df[group_name_df['Rep Name'] + group_name_df[
    'Full Search Name'] == 'Samuel Vernon 2NdSamuel Vernon Ii'].index, inplace=True)
group_name_df.drop(group_name_df[group_name_df['Rep Name'] + group_name_df[
    'Full Search Name'] == 'Thomas Cloyd HalseyThomas Lloyd Halsey'].index, inplace=True)


# In[397]:


# we want to group all the mispelled names together under the same name, and set their information to be the same as the name that is representing them - the rep name
# first we find all names that are being grouped under a name that is not theirs
group_name_df = group_name_df[group_name_df['Full Search Name'] != group_name_df['Rep Name']]

# define new columns that represent the data we will use to group the data for
# don't want to change original columns etc so we don't have to change data
CD_merged_mind[
    ['Group Name', 'Group Town', 'Group County', 'Group State', 'Group Country', 'Group Name Type', 'Group Match Index',
     'Group Match Status', 'Group Match Url']] = CD_merged_mind[
    ['Full Search Name', 'new_town', 'county', 'new_state', 'country', 'geo_level', 'Match Index', 'Match Status',
     'url']]

# iterate through names
for ind in group_name_df.index:
    # obtain data - list of names and indices that we're replacing and the indexes of the data we are changing, and the indices where we're getting the data we're changing it to from
    match_ind, full_name, rep_name = group_name_df.loc[ind, ['Match Index', 'Full Search Name', 'Rep Name']]
    change_ind = CD_merged_mind[
        CD_merged_mind.apply(lambda x: x['Match Index'] == match_ind and (x['Full Search Name'] == full_name or x['Full Search Name'] == rep_name),
                             axis=1)].index
    info_ind = CD_merged_mind[
        CD_merged_mind.apply(lambda x: x['Match Index'] == match_ind and x['Full Search Name'] == rep_name,
                             axis=1)].index

    # sometimes the particular rep name has multiple types of locations - we want to pick the one that is most specific, so town > county > state
    # we will unify these locations later
    if CD_merged_mind.loc[info_ind, ['Group Name', 'Group Town', 'Group County', 'Group State', 'Group Country',
                                     'Group Name Type']].drop_duplicates().shape[0] > 1:
        # possible data we are replacing with
        possibilities = CD_merged_mind.loc[
            info_ind, ['Group Name', 'Group Town', 'Group County', 'Group State', 'Group Country', 'Group Name Type',
                       'Group Match Index', 'Group Match Status', 'Group Match Url']].drop_duplicates()
        if possibilities[possibilities['Group Name Type'] == 'town'].shape[0] == 1:
            possibilities = possibilities[possibilities['Group Name Type'] == 'town'].values.tolist()
        elif possibilities[possibilities['Group Name Type'] == 'county'].shape[0] == 1:
            possibilities = possibilities[possibilities['Group Name Type'] == 'county'].values.tolist()
        elif possibilities[possibilities['Group Name Type'] == 'state'].shape[
            0] == 1 or rep_name == 'Benjamin Tallmadge':
            possibilities = possibilities[possibilities['Group Name Type'] == 'state'].values.tolist()
            if rep_name == 'Benjamin Tallmadge':
                possibilities = [ele for ele in possibilities if ele[3] == 'CT']
        else:
            possibilities = possibilities[possibilities['Group Name Type'] == 'country'].values.tolist()
    # if there's only one type of location, no selection process needed
    else:
        possibilities = CD_merged_mind.loc[
            info_ind, ['Group Name', 'Group Town', 'Group County', 'Group State', 'Group Country', 'Group Name Type',
                       'Group Match Index', 'Group Match Status', 'Group Match Url']].drop_duplicates().values.tolist()
    # make sure we're only assigning one row of data
    assert (len(possibilities) == 1)
    CD_merged_mind.loc[
        change_ind, ['Group Name', 'Group Town', 'Group County', 'Group State', 'Group Country', 'Group Name Type',
                     'Group Match Index', 'Group Match Status', 'Group Match Url']] = [possibilities[0]]  * len(change_ind)


# In[398]:


"""print(CD_merged_mind[CD_merged_mind['Group Name'].apply(lambda x: x in ['Richard Woottan', 'Gassaway Watkins'])][['Name', 'state_data', 'state_data_index', 'Name_Fix', 'Fn_Fix', 'Ln_Fix', 'county', 'new_state', 'country', 'geo_level','Match Index', 'Match Status','Group Name', 'Group Town', 'Group County', 'Group State', 'Group Country', 'Group Name Type','Group Match Index', 'Group Match Status',]].to_markdown())"""


# ## Group Names - Fuzzy Matching
# used fuzzy matching to find list of names, then edited the list manually (result is name_agg.csv) - then applied process of replacement
# first  two code blocks show example of how I identified names

# In[399]:


"""
ny_names = CD_merged_mind[CD_merged_mind['state'] == 'NY']['Group Name'].unique()
ny_names = [n for n in ny_names if not pd.isnull(n)]
match_names = [process.extract(name, ny_names, score_cutoff = 80) for name in ny_names]
match_names_fin = [m for m in match_names if len(m) != 1]
i = -1
"""


# In[400]:


"""
i+=1
name_options = [n[0] for n in match_names_fin[i]]
CD_merged_mind[CD_merged_mind.apply(lambda x: x['Group State'] == 'NY' and x['Group Name'] in name_options, axis = 1)][[#'Name',
    'Group Name', 'Group State', 'Group Name Type', 'Group Match Index', 'Group Match Status', 'Group Match Url']].drop_duplicates()
"""


# In[401]:


# import names that we want to group together
# these might not be names that have the same match index, or names that have match index == ""
# contains location because we can only identify a person uniquely through name + location
rep_names = pd.read_csv(INDIR_RAW / 'corrections/name/postscrape/name_agg.csv')
rep_names['original'] = rep_names['original'].apply(lambda x: x.replace("\t", " "))
rep_names['new'] = rep_names['new'].apply(lambda x: x.replace("\t", " "))
rep_names['location'] = rep_names['location'].apply(lambda x: x.replace("\t", " ") if not pd.isnull(x) else x)
# notes - we identified the names using fuzzy matching, and then picked the name that was "right" by finding whether it was matched, or using ancestry.com to see which one had the most records that seemed correct
# this was quite an involved process - above commented code demonstrates how you would iterate through examining the options


# In[402]:


# we want to replace the location/info of the original name with the info of the new name
for og_name, new_name, loc in zip(rep_names['original'], rep_names['new'], rep_names['location']):
    # obtain values that we want to set the person's information to
    if pd.isnull(loc):
        vals = CD_merged_mind[CD_merged_mind['Group Name'] == new_name][
            ['Group Name', 'Group Town', 'Group County', 'Group State', 'Group Country', 'Group Name Type',
             'Group Match Index', 'Group Match Status', 'Group Match Url']].drop_duplicates().values.tolist()
    else:
        town, county, state, nametype = parseLocationString(loc, loc.split(" | ")[-1])
        vals = CD_merged_mind[CD_merged_mind.apply(
            lambda x: x['Group Name'] == new_name and x['Group Town'] == town and x['Group County'] == county and x[
                'Group State'] == state and x['Group Name Type'] == nametype, axis=1)][
            ['Group Name', 'Group Town', 'Group County', 'Group State', 'Group Country', 'Group Name Type',
             'Group Match Index', 'Group Match Status', 'Group Match Url']].drop_duplicates().values.tolist()
    if new_name == 'Henry Huttenstein':
        vals = [ele for ele in vals if ele[1] == 'Lancaster']

    # obtain index of the name whose information we want to replace
    # two cases - for if we need to input location information or not
    if CD_merged_mind[CD_merged_mind.apply(lambda x: x['Group Name'] == og_name, axis=1)][
        ['Group Town', 'Group County', 'Group State', 'Group Country', 'Group Name Type']].drop_duplicates().shape[
        0] > 1:
        # special exception
        if og_name == 'Benjamin Brown' or og_name == 'William Wheater':
            rep_ind = CD_merged_mind[
                CD_merged_mind.apply(lambda x: x['Group Name'] == og_name and x['Group State'] == 'RI', axis=1)].index
        else:
            rep_ind = CD_merged_mind[CD_merged_mind.apply(
                lambda x: x['Group Name'] == og_name and x['Group Town'] == town and x['Group County'] == county and x[
                    'Group State'] == state and x['Group Name Type'] == nametype, axis=1)].index
    else:
        rep_ind = CD_merged_mind[CD_merged_mind.apply(lambda x: x['Group Name'] == og_name, axis=1)].index

    # make sure we're only assigning one row of data - otherwise we have issues
    if len(vals) == 1:
        CD_merged_mind.loc[
            rep_ind, ['Group Name', 'Group Town', 'Group County', 'Group State', 'Group Country', 'Group Name Type',
                      'Group Match Index', 'Group Match Status', 'Group Match Url']] = vals[0]
    if len(vals) > 1:
        print(og_name, new_name)


# In[403]:


"""print(rep_names[rep_names['new'].apply(lambda x: x == 'Hannah Howley' or x == 'John Salter')].to_markdown())
print(CD_merged_mind[CD_merged_mind['Group Name'].apply(lambda x: x == 'Hannah Howley' or x == 'John Salter')][['Name', 'state_data', 'state_data_index', 'Name_Fix', 'Fn_Fix', 'Ln_Fix', 'county', 'new_state', 'country', 'geo_level','Match Index', 'Match Status','Group Name', 'Group Town', 'Group County', 'Group State', 'Group Country', 'Group Name Type','Group Match Index', 'Group Match Status',]].to_markdown())"""


# ## Group - same name, within state
# now, we have people who live in the same state with the same name - we want to figure out whether they represent the same identity
# our criteria is that the information must not contradict (cannot have two different counties/towns), and they must reside within the asme state

# In[404]:


# now, there are some names that are the same, but have different locations. We think that we can identify these by finding cases where the name is the same, but the locations differ (up to the state level)
# example: Man in montgomery MD, Man in MD
dup_state = CD_merged_mind[
    ['Group Name', 'Group State', 'Group County', 'Group Town', 'Group Name Type']].drop_duplicates().groupby(
    ['Group Name', 'Group State']).count().reset_index()


# In[405]:


for ind in dup_state[dup_state['Group County'] > 1].index:
    # information from dataframe with potentially duplicated individuals (people with same name, identity but different locations)
    name, state = dup_state.loc[ind, ['Group Name', 'Group State']]

    # values of all possible name types
    vals =  CD_merged_mind[CD_merged_mind.apply(lambda x: x['Group Name'] == name and x['Group State'] == state, axis=1)][
        'Group Name Type'].drop_duplicates().tolist()
    # list of unique towns
    towns = [ele for ele in CD_merged_mind[
        CD_merged_mind.apply(lambda x: x['Group Name'] == name and x['Group State'] == state, axis=1)][
        'Group Town'].drop_duplicates().tolist() if ele != ""]
    # list of unique counties
    counties = [ele for ele in CD_merged_mind[
        CD_merged_mind.apply(lambda x: x['Group Name'] == name and x['Group State'] == state, axis=1)][
        'Group County'].drop_duplicates().tolist() if ele != ""]

    # let towns, counties length equal 1 (excluding "") because we don't want contradicting information. for example, montgomery MD and anne arundel MD contradict but annapolis, anne arundel MD and anne arundel MD don't contradict because one is more specific than the other
    if len(vals) > 1 and dup_state.loc[ind, 'Group County'] < 3 and len(towns) == 1 and len(counties) == 1:
        # find what is the most specific location we have
        if 'town' in vals:
            change_val = CD_merged_mind.loc[CD_merged_mind.apply(
                lambda x: x['Group Name'] == name and x['Group State'] == state and x['Group Name Type'] == 'town',
                axis=1), ['Group Name', 'Group Town', 'Group County', 'Group State', 'Group Name Type',
                          'Group Match Index', 'Group Match Status', 'Group Match Url']].drop_duplicates().values
        elif 'county' in vals:
            change_val = CD_merged_mind.loc[CD_merged_mind.apply(
                lambda x: x['Group Name'] == name and x['Group State'] == state and x['Group Name Type'] == 'county',
                axis=1), ['Group Name', 'Group Town', 'Group County', 'Group State', 'Group Name Type',
                          'Group Match Index', 'Group Match Status', 'Group Match Url']].drop_duplicates().values
        else:  # 'state' in vals
            change_val = CD_merged_mind.loc[CD_merged_mind.apply(
                lambda x: x['Group Name'] == name and x['Group State'] == state and x['Group Name Type'] == 'state',
                axis=1), ['Group Name', 'Group Town', 'Group County', 'Group State', 'Group Name Type',
                          'Group Match Index', 'Group Match Status', 'Group Match Url']].drop_duplicates().values

        change_ind = CD_merged_mind[
            CD_merged_mind.apply(lambda x: x['Group Name'] == name and x['Group State'] == state, axis=1)].index
        CD_merged_mind.loc[change_ind, ['Group Name', 'Group Town', 'Group County', 'Group State', 'Group Name Type',
                                        'Group Match Index', 'Group Match Status', 'Group Match Url']] = change_val[0]


# In[406]:


"""print(dup_state[dup_state['Group Name'].apply(lambda x: x in ['Abigail Robbins', 'Abner Johnson'])].to_markdown())
print(CD_merged_mind[CD_merged_mind.apply(lambda x: x['Group Name'] in ['Abigail Robbins', 'Abner Johnson'] and x['Group State'] == 'CT', axis=1)][['Name', 'state_data', 'state_data_index', 'Name_Fix', 'Fn_Fix', 'Ln_Fix', 'county', 'new_state', 'country', 'geo_level','Match Index', 'Match Status','Group Name', 'Group Town', 'Group County', 'Group State', 'Group Country', 'Group Name Type','Group Match Index', 'Group Match Status',]].to_markdown())"""


# ## Create Group Columns and Group Data

# In[407]:


# define some columns that we will use later when grouping data - makes tracking stuff easier
CD_merged_mind['data_index'] = CD_merged_mind['state_data'] + "_" + CD_merged_mind['state_data_index'].astype(str)
CD_merged_mind['assets'] = CD_merged_mind['data_index'] + " : " + CD_merged_mind['6p_total'].astype(str) + ", " + CD_merged_mind['6p_def_total'].astype(str) + ", " + CD_merged_mind['3p_total'].astype(str)


# In[408]:


# fill in information for people who we could not search for on ancestry because their name was not formatted as a name - these are the unsearchables from the third cleaning script
na_ind = CD_merged_mind[CD_merged_mind['Group Name'].isnull()].index
CD_merged_mind.loc[na_ind, 'Group Name'] = CD_merged_mind.loc[na_ind, 'Name']
CD_merged_mind.loc[na_ind, 'Full Search Name'] = CD_merged_mind.loc[na_ind, 'Name']
CD_merged_mind.loc[na_ind, 'Group Match Index'] = 'Unsearchable (not a name)'
CD_merged_mind.loc[na_ind, 'Group Match Url'] = 'Unsearchable (not a name)'
CD_merged_mind.loc[na_ind, 'Name_Fix'] = CD_merged_mind.loc[na_ind, 'Name']


# In[409]:


# capitalize nams correctly
CD_merged_mind['Group Name'] = CD_merged_mind['Group Name'].apply(
    lambda x: " ".join([ele.capitalize() if "ii" not in ele.lower() else ele.upper() for ele in x.split(" ")]))


# In[410]:


# manually fix an entry - i don't know why this was not addressed by the above process, but now it is fixed
CD_merged_mind.loc[
    CD_merged_mind[CD_merged_mind['Name'].apply(lambda x: 'Bowdle' in x)].index, 'Group Town'] = 'Annapolis'
CD_merged_mind.loc[
    CD_merged_mind[CD_merged_mind['Name'].apply(lambda x: 'Gassaway Watkins' in x)].index, 'Group Town'] = 'Annapolis'


# In[669]:


# group together everyone with the same name, location and aggregate their assets and information
df_final = CD_merged_mind.fillna("").groupby(
    ['Group Name', 'Group State', 'Group County', 'Group Town', 'Group Name Type', 'Group Match Index',
     'Group Match Url']).agg({'Name_Fix': lambda x: list(set(x)), 'Full Search Name': tNameList, 'assets': tNameList,
                              'occupation': tNameList}).reset_index()


# In[670]:


"""print(df_final.loc[[4,8]].drop('Group Match Url', axis = 1).to_markdown())"""


# ## Impute Location - Corporations

# In[671]:


"""print(df_final[df_final['Name_Fix'].apply(lambda x: any(['Elnathan Keyes' in ele for ele in x]))].drop('Group Match Url', axis = 1).to_markdown())"""


# In[672]:


exception_names = []

# find cases where we have the same name but in different locations - we think that these are actually the same people so we want to group them together
dup_state_2 = df_final.explode("Name_Fix")[
    ['Name_Fix', 'Group Name', 'Group State', 'Group County', 'Group Town', 'Group Name Type']].drop_duplicates()
dup_state_2['Name_Fix'] = dup_state_2['Name_Fix'].apply(lambda x: x.split(" | "))
dup_state_2 = dup_state_2.explode('Name_Fix').drop_duplicates().groupby(
    ['Name_Fix', 'Group State']).nunique().reset_index()

# basically, we want to keep looping through this until the number of exceptions is the same as the number of ungrouped names
# exception names are names we can't merge, there's a process by which we can't combine them (basically if they have contradicting info - so Bob is in two different counties, then Bob is an exception)
# we have to run the loop multiple times because sometimes a name can be changed multiple times after its grouped
while len(exception_names) != dup_state_2[dup_state_2.apply(lambda x: x['Group County'] > 1 and x['Group Name'] > 1, axis=1)].shape[0]:
    dup_state_2 = df_final.explode("Name_Fix")[
        ['Name_Fix', 'Group Name', 'Group State', 'Group County', 'Group Town', 'Group Name Type']].drop_duplicates()
    dup_state_2['Name_Fix'] = dup_state_2['Name_Fix'].apply(lambda x: x.split(" | "))
    dup_state_2 = dup_state_2.explode('Name_Fix').drop_duplicates().groupby(
        ['Name_Fix', 'Group State']).nunique().reset_index()

    for ind in dup_state_2[dup_state_2.apply(lambda x: x['Group County'] > 1 and x['Group Name'] > 1, axis=1)].index:
        # information from dataframe with potentially duplicated individuals (people with same name, identity but different locations)
        name, state = dup_state_2.loc[ind, ['Name_Fix', 'Group State']]

        # values of all possible name types
        vals = df_final[
            df_final.apply(lambda x: any([name in ele for ele in x['Name_Fix']]) and x['Group State'] == state,
                           axis=1)]['Group Name Type'].drop_duplicates().tolist()
        # list of unique towns
        towns = [ele for ele in df_final[
            df_final.apply(lambda x: any([name in ele for ele in x['Name_Fix']]) and x['Group State'] == state,
                           axis=1)]['Group Town'].drop_duplicates().tolist() if ele != ""]
        # list of unique counties
        counties = [ele for ele in df_final[
            df_final.apply(lambda x: any([name in ele for ele in x['Name_Fix']]) and x['Group State'] == state,
                           axis=1)]['Group County'].drop_duplicates().tolist() if ele != ""]

        # let towns, counties length equal 1 (excluding "") because we don't want contradicting information. for example, montgomery MD and anne arundel MD contradict but annapolis, anne arundel MD and anne arundel MD don't contradict because one is more specific than the other
        if len(towns) <= 1 and len(counties) == 1:
            # find
            if 'town' in vals:
                change_val = df_final.loc[df_final.apply(
                    lambda x: any([name in ele for ele in x['Name_Fix']]) and x['Group State'] == state and x[
                        'Group Name Type'] == 'town', axis=1), ['Group Town', 'Group County', 'Group State',
                                                                'Group Name Type']].drop_duplicates().values
            elif 'county' in vals:
                change_val = df_final.loc[df_final.apply(
                    lambda x: any([name in ele for ele in x['Name_Fix']]) and x['Group State'] == state and x[
                        'Group Name Type'] == 'county', axis=1), ['Group Town', 'Group County', 'Group State',
                                                                  'Group Name Type']].drop_duplicates().values
            else:  # 'state' in vals
                change_val = df_final.loc[df_final.apply(
                    lambda x: any([name in ele for ele in x['Name_Fix']]) and x['Group State'] == state and x[
                        'Group Name Type'] == 'state', axis=1), ['Group Town', 'Group County', 'Group State',
                                                                 'Group Name Type']].drop_duplicates().values

            change_ind = df_final[
                df_final.apply(lambda x: any([name in ele for ele in x['Name_Fix']]) and x['Group State'] == state,
                               axis=1)].index
            assert (len(change_val) == 1)
            df_final.loc[change_ind, ['Group Town', 'Group County', 'Group State', 'Group Name Type']] = change_val[0]
        else:
            if [name, state] not in exception_names:
                exception_names.append([name, state])


# In[673]:


"""print(df_final[df_final['Name_Fix'].apply(lambda x: any(['Elnathan Keyes' in ele for ele in x]))].drop('Group Match Url', axis = 1).to_markdown())"""


# ## Cleaning Name_Fix

# In[674]:


"""print(df_final[df_final['Group Name'] == 'Ebenezer Denny'].drop('Group Match Url', axis = 1).to_markdown())"""


# In[675]:


# now, we want to find a way to systematize all the names - for example, Bob Rush and Bob Rushe are the same person but in our notation they are denoted as separate people
# we will use a dictionary to convert all Bob Rushe's in a particular location into Bob Rush
other_names = df_final[['Group Name', 'Group State', 'Group County', 'Group Town', 'Full Search Name']]
other_names['Full Search Name'] = other_names['Full Search Name'].apply(lambda x: x.split(" | "))
other_names = other_names.explode('Full Search Name')
namechange_dict = dict(zip(
    other_names['Full Search Name'] + other_names['Group Town'] + other_names['Group County'] + other_names[
        'Group State'], other_names['Group Name']))
# some manual additions due to idosyncracies of cleaning process
namechange_dict['DesdeilyNY'] = 'Desdeily'
namechange_dict['GrundNY'] = 'Grund'
namechange_dict['Thomas Cloyd HalseyProvidenceProvidence CountyRI'] = 'Thomas Lloyd Halsey'


# In[676]:


# more names that we add to the dictionary manually - we have to do this for the exceptions because these people are not accounted for for some weird reason in the original process of creating the dictionary
# also a special exception for how we process Samuel Vernon's name
for ele in exception_names:
    name, state = ele[0], ele[1]
    vals = df_final[
        df_final.apply(lambda x: any([name in ele for ele in x['Name_Fix']]) and x['Group State'] == state, axis=1)][
        ['Group Town', 'Group County', 'Group State']].drop_duplicates()
    for ind in vals.index:
        town, county, state = vals.loc[ind, 'Group Town'], vals.loc[ind, 'Group County'], vals.loc[ind, 'Group State']
        if name + town + county + state not in namechange_dict.keys():
            reps = [e for e in namechange_dict.keys() if name in e]
            if name == 'Samuel Vernon':
                namechange_dict[name + town + county + state] = name
            else:
                assert (len(list(set([namechange_dict[ele] for ele in reps]))) == 1)
                namechange_dict[name + town + county + state] = namechange_dict[reps[0]]


# In[677]:


# now we reformat the name
# : separates different institutions associated with someone, so for example, someone might own bonds as an individual Bob and with his friends (Bob and George) so the result is Bob : Bob | George
# ASDSD helps us find places where our dictionary fails
df_final['Name_Fix_Transfer'] = df_final.apply(lambda x: " : ".join(list(set([(tNameList([namechange_dict.get(
    subele + x['Group Town'] + x['Group County'] + x['Group State'],
    "ASDSD" + subele + x['Group Town'] + x['Group County'] + x['Group State']) for subele in ele.split(" | ")]) + " / " + ele) for ele
    in x['Name_Fix']]))), axis=1)
df_final['Name_Fix_Clean'] = df_final.apply(lambda x: " : ".join(list(set([tNameList([namechange_dict.get(
    subele + x['Group Town'] + x['Group County'] + x['Group State'],
    "ASDSD" + subele + x['Group Town'] + x['Group County'] + x['Group State']) for subele in ele.split(" | ")])  for ele
                                                                              in x['Name_Fix']]))), axis=1)


# In[678]:


df_final.drop('Name_Fix', axis=1, inplace=True)


# In[679]:


"""print(df_final[df_final['Group Name'] == 'Ebenezer Denny'].drop('Group Match Url', axis = 1).to_markdown())"""


# In[680]:


#CD_merged_mind[CD_merged_mind['Name'].apply(lambda x: 'Daniel Hartung' in x)]
#CD_merged_mind[CD_merged_mind['Name'].apply(lambda x: 'Dorothea Losh' in x)]
#CD_merged_mind[CD_merged_mind['Name'].apply(lambda x: 'Joseph Stiles' in x)]
#CD_merged_mind[CD_merged_mind['Name'].apply(lambda x: 'Walter S' in x)]
#CD_merged_mind[CD_merged_mind['Name'].apply(lambda x: 'William Allen' in x)]
#CD_merged_mind[CD_merged_mind['Name'].apply(lambda x: 'William Govett' in x)]


# In[681]:


#df_final.drop('Group Match Url', axis = 1).loc[[591, 728, 1667, 1877, 3668, 3686, 3761]]


# ## Manual Adjustments

# In[682]:


rep_list = df_final[df_final.duplicated(['Group Name', 'Group State', 'Group County', 'Group Town', 'Group Name Type'])][
    'Group Name'].tolist()
sorted(rep_list)


# 

# In[683]:


df_final[df_final['Group Name'].apply(lambda x: x in rep_list)]


# 

# In[684]:


# now, we have a case where the same person and location appears multiple times, so we need to combine them into one person. we do that here
# above we confirm the people for who we have to do this for
df_final.loc[
    df_final[df_final['Group Name'] == 'Love Stone'].index, ['Group Match Url', 'Name_Fix_Clean', 'Name_Fix_Transfer',
                                                             'assets', 'occupation']] = [
    'https://www.ancestrylibrary.com/search/collections/5058/?name=Love_Stone&name_x=1_1&residence=_charleston-south carolina-usa_552&residence_x=_1-0',
    'Joseph Vesey | Love Stone : Love Stone',
    'Joseph Vesey | Love Stone / Joseph Vesey | Love Stone : Love Stone / Love Stone',
    'SC_10 : 216.67, 108.33, 207.64 | SC_394 : 881.66, 2838.33, 856.64',
    'Administrators of Joseph Darrell | Widow']

df_final.loc[
    df_final[df_final['Group Name'] == 'John Gale'].index, ['Group Match Url', 'Group Match Index', 'Name_Fix_Clean',
                                                            'Name_Fix_Transfer',
                                                            'assets', 'occupation']] = [
    'https://www.ancestrylibrary.com/search/collections/5058/?name=John_Gale&name_x=1_1&residence=_Maryland-usa_23&residence_x=_1-0',
    '984 | 985', 'Ebenezer Finlays | John Gale : John Gale',
    'John Gale / John Gale : Ebenezer Finlays | John Gale / Ebenezer Finlays | John Gale',
    'MD_243 : 2148.66, 1074.34, 1409.32 | MD_244 : 1036.86, 518.43, 683.74 | PA_1080 : 176.58, 88.29, 201.48',
    ' | Executor of Ebenezer Finlay']

df_final.loc[
    df_final[df_final['Group Name'] == 'Nathaniel Irwin'].index, ['Group Match Index', 'Group Match Url',
                                                                  'Name_Fix_Clean', 'Name_Fix_Transfer',
                                                                                    'assets', 'occupation']] = ['1988',
                                                                                                                'https://www.ancestrylibrary.com/search/collections/5058/?name=Nathaniel_Irwin&name_x=s_s&residence=_bucks-pennsylvania-usa_403&residence_x=_1-0',
                                                                                                                'Nathaniel Irwin : Nathaniel Irwin | Richard Walker',
                                                                                                                'Nathaniel Irwin | Richard Walker / Nathaniel Irwin | Richard Walker : Nathaniel Irwin / Nathaniel Irwin',
                                                                                                                'PA_693 : 276.68, 138.35, 93.77 | PA_1117 : 0.0, 0.0, 26.02 | PA_949 : 617.36, 308.69, 179.16',
                                                                                                                'Administer Estate of Richard Walker Deceased']

"""df_final.loc[
    df_final[df_final['Group Name'] == 'Moses Brown'].index, ['Group Match Index', 'Group Match Url', 'Name_Fix_Clean',
                                                              'Name_Fix_Transfer',
                                                              'assets', 'occupation']] = ['2472',
                                                                                          'https://www.ancestrylibrary.com/search/collections/5058/?name=Moses_Brown&name_x=1_1&residence=_providence-providence-rhode island-usa_5531&residence_x=_1-0',
                                                                                          'Moses Brown | Nicholas Brown : John Francis | Moses Brown : Moses Brown',
                                                                                          'Moses Brown | Nicholas Brown / Mess Brown | Moses Brown | Nicholas Brown : Moses Brown / Moses Brown : Moses Brown | Nicholas Brown / Moses Brown | Nicholas Brown : John Francis | Moses Brown / John Francis | MOses Brown : Moses Brown / Moses Brown',
                                                                                          'RI_126 : 568.96, 284.47, 242.46 | RI_285 : 480.0, 240.0, 24095.11 | RI_334 : 266.67, 133.33, 72.0 | RI_516 : 942.65, 7889.63, 9392.12 | RI_598 : 4675.35, 1805.23, 2092.76 | RI_604 : 18067.23, 9033.61, 4878.15',
                                                                                          'Esquire | Extors to the Late Nicholas Brown Esq Deceased']
"""
df_final.loc[df_final[df_final['Group Name'].apply(lambda x: 'Peleg San' in x)].index, ['Group Name', 'Group State',
                                                                                        'Group County', 'Group Town',
                                                                                        'Group Name Type',
                                                                                        'Group Match Index',
                                                                                        'Group Match Url',
                                                                                        'Name_Fix_Clean',
                                                                                        'Name_Fix_Transfer',
                                                                                        'Full Search Name', 'assets',
                                                                                        'occupation']] = [
    'Peleg Sanford', 'CT', 'Hartford County', 'Hartford', 'town', '13',
    'https://www.ancestrylibrary.com/search/collections/5058/?name=Peleg_Sanford&name_x=ps_ps&residence=_hartford-hartford-connecticut-usa_999&residence_x=_1-1-a',
    'Peleg Sanford', 'Peleg Sandford : Peleg Sandford / Peleg Sanford : Peleg Sanford / Peleg Sanford', 'Peleg Sanford | Peleg Sandford',
    'CT_13 : 1000.17, 500.09, 1500.32 | CT_280 : 506.93, 253.47, 500.15 | CT_308 : 1200.0, 0.0, 0.0 | CT_672 : 389.47, 194.74, 177.76 | CT_836 : 39.82, 19.92, 0.0 | NY_1773 : 0.0, 0.0, 2665.61 | NY_2107 : 0.0, 0.0, 288.0 | NY_1773 : 0.0, 0.0, 2665.61 | NY_2107 : 0.0, 0.0, 288.0',
    'Merchant']

"""df_final.loc[
    df_final[df_final['Group Name'] == 'Tristram Bowdle'].index, ['Group Match Url', 'Name_Fix_Clean', 'Name_Fix_Transfer', 'Full Search Name',
                                                                  'assets']] = [
    'https://www.ancestrylibrary.com/search/collections/5058/?name=Tristram_Bowdle&name_x=ps_ps&residence=_anne+arundel-maryland-usa_169&residence_x=_1-1',
    'Gassaway Watkins | Tristram Bowdle : Tristram Bowdle',
    'Gassaway Watkins | Tristram Bowdle / Gassaway Watkins | Tristiam Bowdle | Tristram Bowdle : Tristram Bowdle / Tristram Bowdle',
    'Tristiam Bowdle | Tristram Bowdle',
    'MD_590 : 38.93, 62.48, 108.28 | MD_591 : 124.96, 0.0, 0.0']"""

df_final.drop_duplicates(inplace=True)


# ## Group Names - incorrect states
# basically because of the way we impute state info sometimes we have the wrong state for an individual (when a state is not listed for someone and we input the state for which the debt file is from, sometimes that state is wrong) - so we correct that when we identify cases where one name is in two states
# we do some figuring out to make sure the two people are actually different

# In[685]:


# look at list below
# go through and inspect to see whether they're the same
"""
name_list = []
for name in df_final['Group Name'].value_counts()[df_final['Group Name'].value_counts()>1].index:
    states = [ele for ele in df_final.fillna("")[df_final['Group Name'] == name]['Group State'].unique().tolist() if ele != '']
    counties = [ele for ele in df_final.fillna("")[df_final['Group Name'] == name]['Group County'].unique().tolist() if ele != '']
    if len(states) > 1 and len(counties) <= len(states) - 1:
        name_list.append(name)
"""


# In[686]:


"""print(df_final[df_final['Group Name'] == 'Adam Gilchrist'][['Group Name', 'Group State', 'Group County', 'Group Town', 'Group Name Type', 'Group Match Index']].to_markdown())"""


# In[687]:


# next, we have people who are the same, but live in different states (have the same name). these people have different states because earlier when we were cleaning code (in the first notebook), we imputed the state that someone lived in when the state was missing as the state of the debt file but sometimeds, these people are not from that state
# list of people
state_group_names = pd.read_csv(INDIR_RAW / 'corrections/name/postscrape/group_name_state.csv')
# in cases where we have people with the same name, and both names only have location information at the state level, we specify here which state we're choosing - basde off preliminary analysis
pickstate = {'Samuel W Johnson': 'NY', 'Josiah Watson': 'VA', 'Gerrard Alexander': 'VA', 'Benjamin Tallmadge': 'CT',
             'Edward Chinn': 'NY', 'Forman Mount': 'PA', 'Josiah Watson': 'VA', 'Thomas Robinson': 'DE',
             'Thomas Ross': 'SC', 'William Applegate': 'NJ'}
for ind in state_group_names.index:
    # get the name and the index/dataframe associated with the name
    group_name = state_group_names.loc[ind, 'Group Name']
    df_ind = df_final[df_final['Group Name'] == group_name].index
    df_final_sub = df_final.loc[df_ind]
    rep_vals = [group_name]
    # if the group name type is state for all appearances of that individual then we refer to the pickstate dictionary to get the state we want to keep
    if len(df_final.loc[df_ind, 'Group Name Type'].unique()) == 1 and df_final.loc[df_ind, 'Group Name Type'].unique()[
        0] == 'state':
        rep_vals.extend(df_final_sub[df_final_sub['Group State'].apply(lambda x: x == pickstate[group_name])][
                            ['Group State', 'Group County', 'Group Town', 'Group Name Type', 'Group Match Index',
                             'Group Match Url']].values.tolist()[0])
        for col in ['Full Search Name', 'assets', 'occupation','Name_Fix_Transfer', 'Name_Fix_Clean']:
            # have to handle the way we combine the name differently for Name_Fix column
            if col != 'Name_Fix_Clean' and col != 'Name_Fix_Transfer':
                rep_vals.append(tNameList(" | ".join(df_final_sub.loc[df_ind, col].tolist()).split(" | ")))
            else:
                rep_vals.append(" : ".join(list(set(" : ".join(df_final_sub.loc[df_ind, col].tolist()).split(" : ")))))
    else:
        # pick the geography level that's most specific
        rep_vals.extend(df_final_sub[df_final_sub['Group Name Type'].apply(lambda x: x == 'town' or x == 'county')][
                            ['Group State', 'Group County', 'Group Town', 'Group Name Type', 'Group Match Index',
                             'Group Match Url']].values.tolist()[0])
        for col in ['Full Search Name', 'assets', 'occupation','Name_Fix_Transfer', 'Name_Fix_Clean']:
            # have to handle the way we combine the name differently for Name_Fix column
            if col != 'Name_Fix_Clean' and col != 'Name_Fix_Transfer':
                rep_vals.append(tNameList(" | ".join(df_final_sub.loc[df_ind, col].tolist()).split(" | ")))
            else:
                rep_vals.append(" : ".join(list(set(" : ".join(df_final_sub.loc[df_ind, col].tolist()).split(" : ")))))
    # replace the index with the value
    df_final.loc[df_ind] = rep_vals


# In[688]:


# remove people from the location that was removed
df_final.drop_duplicates(inplace=True)


# In[689]:


"""print(df_final[df_final['Group Name'] == 'Adam Gilchrist'][['Group Name', 'Group State', 'Group County', 'Group Town', 'Group Name Type', 'Group Match Index']].to_markdown())"""


# ## Add Villages

# In[706]:


# another case where we have to clean the data manually because somehow this entry was not cleaned properly in the third notebook
print(match_df.loc[
          match_df[match_df['Home in 1790 (City, County, State)'].apply(lambda x: '\n' in x)].index, 'Match State'])
match_df.loc[match_df[match_df['Home in 1790 (City, County, State)'].apply(
    lambda x: '\n' in x)].index, 'Match State'] = 'South Carolina'


# In[707]:


# next, we want to define a "village" category that tells us what part of Philly/Charleston/New York someone lived in, if it's in their ancestry.com data
# we only do this for these 3 towns
village_ind = match_df[match_df['Match County'].apply(
    lambda x: 'philadelphia' in x.lower() or 'charleston' in x.lower() or 'new york' in x.lower())]['Match Town'].index
match_df.loc[village_ind, 'Match Village'] = [ele if ele != 'Philadelphia City' else '' for ele in match_df.loc[village_ind, 'Match Town'] ]
match_df.loc[village_ind, 'Match Town'] = [
    'Philadelphia' if 'philadelphia' in ele.lower() else 'Charleston' if 'charleston' in ele.lower() else 'New York City'
    for ele in match_df.loc[village_ind, 'Match County']]
match_df.fillna("", inplace=True)
# change match type based on village
match_df['Match Type'] = match_df.apply(lambda x: 'village' if x['Match Village'] != '' else x['Match Type'], axis=1)


# In[708]:


"""print(match_df[match_df['Name'] == 'Thomas Vail'].to_markdown())"""


# ## Get Occupations from Ancestry

# In[709]:


"""print(match_df[match_df['Name'] == 'Comfort (Wd) Clock | Wd Combert Clock'].to_markdown())"""


# In[710]:


# next, we're going to clean the match dataframe containing results from ancestry.com
# the first way we identify an entry that needs to be cleaned is if it has parentheses but no commas - the occupation is inside the parentheses
opt_one_ind = match_df[match_df['Name'].apply(lambda x: '(' in x and ',' not in x)].index
# we extract the occupation within the name, add it to an occupation column we create and then remove the occupation from the name
match_df.loc[opt_one_ind, 'Occupation'] = match_df.loc[opt_one_ind, 'Name'].apply(
    lambda x: tNameList([ele[ele.find("(") + 1:ele.find(")")] for ele in x.split(" | ") if '(' in ele]))
match_df.loc[opt_one_ind, 'Name'] = match_df.loc[opt_one_ind].apply(lambda x: tNameList(
    [(ele[0:ele.find("(") - 1] + ele[ele.find(")") + 1:]) if '(' in ele else ele.replace(x['Occupation'], '') for ele in
     x['Name'].split(" | ")]), axis=1)


# In[711]:


"""print(match_df.loc[[145]].to_markdown())"""


# In[712]:


# next, we have a few particular occupations that are noted with a comma in between names
esq_ind = match_df[
    match_df['Name'].apply(lambda x: ',' in x and '(' not in x and not any(char.isdigit() for char in x))].index
# there are only judges esquires or colonels, so we check and add these to the occupations columns if they're there
match_df.loc[esq_ind, 'Occupation'] = match_df.loc[esq_ind, 'Name'].apply(lambda x: 'Esquire' if 'Esq' in x else '')
match_df.loc[esq_ind, 'Occupation'] = match_df.loc[esq_ind].apply(
    lambda x: tNameList((x['Occupation'] + " | Colonel").split(" | ")) if 'Col' in x['Name'] else x['Occupation'],
    axis=1)
match_df.loc[esq_ind, 'Occupation'] = match_df.loc[esq_ind].apply(
    lambda x: tNameList((x['Occupation'] + " | Judge").split(" | ")) if 'Exce' in x['Name'] or 'Judge' in x['Name'] else
    x['Occupation'], axis=1)
# remove the parts of the name that contain the occupations
match_df.loc[esq_ind, 'Name'] = match_df.loc[esq_ind].apply(lambda x: tNameList([ele.replace(',', '').replace('Esquire',
                                                                                                              '').replace(
    'Esqr', '').replace('Esq.', '').replace('Esq', '').replace('Colonel', '').replace('Col', '').replace('  ',
                                                                                                         ' ').replace(
    '.', '').replace('His Excely ', '').replace('r|', 'r |').replace('y|', 'y |').replace('n|', 'n |').strip() for ele
                                                                                 in x['Name'].split(" | ")]), axis=1)


# In[713]:


# finally, we have a few particular occupations that are noted with a comma and parentheses in between names
both_ind = match_df[match_df['Name'].apply(lambda x: '(' in x and ',' in x)]['Name'].index
# first we remove the occupation inside the parentheses and remove it from the name
match_df.loc[both_ind, 'Occupation'] = match_df.loc[both_ind, 'Name'].apply(
    lambda x: tNameList([ele[ele.find("(") + 1:ele.find(")")] for ele in x.split(" | ") if '(' in ele]))
match_df.loc[both_ind, 'Name'] = match_df.loc[both_ind].apply(lambda x: tNameList(
    [(ele[0:ele.find("(") - 1] + ele[ele.find(")") + 1:]) if '(' in ele else ele.replace(x['Occupation'], '') for ele in
     x['Name'].split(" | ")]), axis=1)
# next, the only occupations that use the comma are esquire,colonel and judge so we just follow the same steps as before
match_df.loc[both_ind, 'Occupation'] = match_df.loc[both_ind].apply(
    lambda x: tNameList((x['Occupation'] + " | Esquire").split(" | ")) if 'Esq' in x['Name'] else x['Occupation'],
    axis=1)
match_df.loc[both_ind, 'Occupation'] = match_df.loc[both_ind].apply(
    lambda x: tNameList((x['Occupation'] + " | Colonel").split(" | ")) if 'Col' in x['Name'] else x['Occupation'],
    axis=1)
match_df.loc[both_ind, 'Occupation'] = match_df.loc[both_ind].apply(
    lambda x: tNameList((x['Occupation'] + " | Judge").split(" | ")) if 'Exce' in x['Name'] or 'Judge' in x['Name'] else
    x['Occupation'], axis=1)
# remove those occupations from the name
match_df.loc[both_ind, 'Name'] = match_df.loc[both_ind].apply(lambda x: tNameList([ele.replace(',', '').replace(
    'Esquire', '').replace('Esqr', '').replace('Esq.', '').replace('Esq', '').replace('Colonel', '').replace('Col',
                                                                                                             '').replace(
    '  ', ' ').replace('.', '').replace('His Excely ', '').replace('r|', 'r |').replace('y|', 'y |').replace('n|',
                                                                                                             'n |').strip()
                                                                                   for ele in x['Name'].split(" | ")]),
                                                              axis=1)


# In[714]:


# Finally, we have a few occupations - judges, reverends, majors, doctors and colonels that are not noted with anything - they are just aprt of the name, so we go through these one by one, add the occupation and remove the occupation names from the actual name column
# judges
honor_index = match_df[match_df['Name'].apply(lambda x: 'Honr.' in x or 'Honorable' in x or 'Honererable' in x)].index
match_df.loc[honor_index, 'Occupation'] = match_df.fillna("").loc[honor_index, 'Occupation'].apply(
    lambda x: tNameList((x + " | Judge").split(" | ")))
match_df.loc[honor_index, 'Name'] = match_df.loc[honor_index].apply(lambda x: tNameList(
    [ele.replace("Honr.", "").replace("Honorable", "").replace("Honererable", "").replace("  ", " ").strip() for ele in
     x['Name'].split(" | ")]), axis=1)


# In[715]:


# reverends
rev_index = match_df[match_df['Name'].apply(lambda x: 'Revd' in x or 'Reverend' in x)].index
match_df.loc[rev_index, 'Occupation'] = match_df.fillna("").loc[rev_index, 'Occupation'].apply(
    lambda x: tNameList((x + " | Reverend").split(" | ")))
match_df.loc[rev_index, 'Name'] = match_df.loc[rev_index].apply(lambda x: tNameList(
    [ele.replace("Revd", "").replace("Reverend", "").replace("  ", " ").strip() for ele in x['Name'].split(" | ")]),
                                                                axis=1)


# In[716]:


# majors
maj_index = match_df[match_df['Name'].apply(lambda x: 'Majr' in x or 'Major' in x)].index
match_df.loc[maj_index, 'Occupation'] = match_df.fillna("").loc[maj_index, 'Occupation'].apply(
    lambda x: tNameList((x + " | Major").split(" | ")))
match_df.loc[maj_index, 'Name'] = match_df.loc[maj_index].apply(lambda x: tNameList(
    [ele.replace("Majr", "").replace("Major", "").replace("  ", " ").strip() for ele in x['Name'].split(" | ")]),
                                                                axis=1)


# In[717]:


# doctors
doctor_index = match_df[
    match_df['Name'].apply(lambda x: 'Dr ' in x or 'Doctor' in x or 'Docr' in x or 'Doctr' in x or 'Dortoe' in x)].index
match_df.loc[doctor_index, 'Occupation'] = match_df.fillna("").loc[doctor_index, 'Occupation'].apply(
    lambda x: tNameList((x + " | Doctor").split(" | ")))
match_df.loc[doctor_index, 'Name'] = match_df.loc[doctor_index].apply(lambda x: tNameList([ele.replace("Doctor",
                                                                                                       "").replace(
    "Docr", "").replace('Docr', '').replace('Dortoe', '').replace('Dr ', '').replace("  ", " ").strip() for ele in
                                                                                           x['Name'].split(" | ")]),
                                                                      axis=1)


# In[718]:


# captains/colonels
officer_index = match_df[match_df['Name'].apply(lambda
                                                    x: 'Col.' in x or 'Cols' in x or 'Colonel' in x or 'Coln' in x or 'Colo' in x or 'General' in x or 'Capt' in x or 'Captain' in x)].index
match_df.loc[officer_index, 'Occupation'] = match_df.fillna("").loc[officer_index, 'Occupation'].apply(
    lambda x: tNameList((x + " | Military Officer").split(" | ")))
match_df.loc[officer_index, 'Name'] = match_df.loc[officer_index].apply(lambda x: tNameList([ele.replace(
    "Col.", "").replace('Cols', '').replace('Colonel', '').replace('Coln', '').replace('Colo', '').replace('General',
                                                                                                           '').replace(
    'Captain', '').replace('Capt', '').replace("  ", " ").strip() for ele in x['Name'].split(" | ")]), axis=1)


# In[719]:


# number of occupations gained
match_df[~match_df['Occupation'].isnull()].shape[0]


# ## Improve Scraper Match

# In[720]:


# next, we have a case where sometimes, one group name is matched to multiple people on ancestry, but we can actually reduce the number of people matched to by checking whether there are name(s) in the matched people from ancestry that correspond exactly to our "Group Name" column
# if we can reduce the number of matches we do so, otherwise we keep the original matches
mult_ind = df_final[df_final['Group Match Index'].apply(
    lambda x: 'Unsearchable' not in x and x != '' and len(x.split(" | ")) > 1)].index
# getting match information
df_final.loc[mult_ind, 'temp'] = df_final.loc[mult_ind].apply(
    lambda x: [ind + " | " + match_df.loc[int(ind), 'Name'] for ind in x['Group Match Index'].split(" | ")], axis=1)
# filtering to see if we can reduce the number of matches
df_final.loc[mult_ind, 'temp'] = df_final.loc[mult_ind].apply(
    lambda x: [ele.split(" | ")[0] for ele in x['temp'] if x['Group Name'] in ele], axis=1)
# changing the match indices if there is a direct name correspondence - otherwise we just keep the original match indices
df_final.loc[mult_ind, 'Group Match Index'] = df_final.loc[mult_ind].apply(
    lambda x: tNameList(x['temp']) if len(x['temp']) > 0 else x['Group Match Index'], axis=1)
df_final.drop('temp', axis=1, inplace=True)


# ## Eliminate Broad Location Matches

# In[721]:


match_df2 = match_df.copy()


# In[722]:


match_df = match_df.loc[sorted(list(set([int(ele) for ele in df_final['Group Match Index'].apply(lambda x: x.split(" | ") if x != '' and x != 'Unsearchable (not a name)' else []).explode().tolist() if not pd.isnull(ele)])))]


# In[760]:


"""print(df_final.loc[[1775]].drop('Group Match Url', axis = 1).to_markdown())
print(match_df.loc[[2862,2863,2864]].to_markdown())"""


# In[761]:


# next, we want to eliminate cases in the match dataframe where for some reason, the location given in the match dataframe is too broad and we can eliminate some of them
# we can do this because we now have more information about the location of the person, based off affiliated corporatiosn
for ind in df_final[df_final['Group Match Index'].apply(lambda x: "|" in x)].index:
    # get relevant data from our data and ancestry match data
    match_data = match_df.loc[[int(ele) for ele in df_final.loc[ind, 'Group Match Index'].split(" | ")]]
    town, county = df_final.loc[ind, 'Group Town'], df_final.loc[ind, 'Group County']
    match_town, match_county = [ele for ele in list(set(match_data['Match Town'].tolist())) if ele != ""], [ele for ele
                                                                                                            in list(
            set(match_data['Match County'].tolist())) if ele != ""]
    # if there is more than one town, and one of the towns matches our data's town, we only keep that town
    if len(match_town) > 1 and town in match_town:
        match_ind = match_data[match_data['Match Town'] == town]['index_new'].tolist()
        # print(ind, match_ind, tNameList([str(ele) for ele in match_ind]))
        df_final.loc[ind, 'Group Match Index'] = tNameList([str(ele) for ele in match_ind])

    # if there is more than one county, and one of the counties matches our data's county, we only keep that county
    elif len(match_county) == 2 and county in match_county:
        match_ind = match_data[match_data['Match County'] == county]['index_new'].tolist()
        # print(ind, match_ind, tNameList([str(ele) for ele in match_ind]))
        df_final.loc[ind, 'Group Match Index'] = tNameList([str(ele) for ele in match_ind])


# In[772]:


"""print(df_final[df_final['Group Name'] == 'Benjamin Gallup'].drop('Group Match Url', axis = 1).to_markdown())
print(match_df[match_df['Name'] == 'Benjn Gallop'].to_markdown())"""


# ## Use Census to Impute Location

# In[762]:


# finally, we want to mark places where the ancestry.com match locations don't match up with what we have, and places where we imput location
df_final['imputed_location'] = ''
df_final['location conflict'] = ''
ordering_dict = {'state': 0, 'county': 1, 'town': 2, 'village': 3, '' : -1}


# In[763]:


def sameLocation(locations):
    """
    This function takes in a list of locations and returns the location level that everything is the same at
    :param locations: list of locations from the match data
    :return: same location + location type
    """
    states = list(set([loc[0] for loc in locations]))
    counties = list(set([loc[1] for loc in locations]))
    towns = list(set([loc[2] for loc in locations]))
    villages = list(set([loc[3] if len(loc) > 3 else '' for loc in locations]))

    loc = locations[0]
    if len(villages) == 1 and '' not in villages:
        return [loc, 'village']
    elif len(towns) == 1 and '' not in towns:
        return [[loc[0],loc[1],loc[2],''], 'town']
    elif len(counties) == 1 and '' not in counties:
        return [[loc[0],loc[1],'',''], 'county']
    elif len(states) == 1 and '' not in states:
        return [[loc[0],'',''], 'state']
    else:
        return ['No Match']


# In[764]:


# add the location an individual has from ancestry.com if they only have one match
temp_ind = df_final[df_final.apply(
    lambda x: 'Unsearchable' not in x['Group Match Index'] and x['Group Match Index'] != '' and len(
        x['Group Match Index'].split(" | ")) == 1, axis=1)].index

# we only add location if we think that the location ancestry.com has is more specific than what we have
df_final.loc[temp_ind, 'temp'] = df_final.loc[temp_ind].apply(lambda x: match_df.loc[int(x['Group Match Index'])][
    ['Match State', 'Match County', 'Match Town', 'Match Village']].values.tolist() if ordering_dict[
                                                                                           x['Group Name Type']] <
                                                                                       ordering_dict[match_df.loc[int(x[
                                                                                                                          'Group Match Index']), 'Match Type']] else "",
                                                              axis=1)

# add location an individual has on ancestry.com if they have more than one match
# pick indices
mult_ind = df_final[df_final.apply(
    lambda x: 'Unsearchable' not in x['Group Match Index'] and x['Group Match Index'] != '' and len(
        x['Group Match Index'].split(" | ")) > 1, axis=1)].index
# find whether the multiple matches have the same location
df_final.loc[mult_ind, 'temp'] = df_final.loc[mult_ind].apply(lambda x: sameLocation(match_df.loc[[int(ele) for ele in x['Group Match Index'].split(" | ")], ['Match State', 'Match County', 'Match Town', 'Match Village']].values.tolist()), axis=1)
# figure out the location type of the ancestry.com location
df_final.loc[mult_ind, 'temp status'] = df_final.loc[mult_ind, 'temp'].apply(lambda x: x[1] if len(x)>1 else '')
# remove from the location
df_final.loc[mult_ind, 'temp'] = df_final.loc[mult_ind].apply(lambda x: x['temp'][0] if ordering_dict[x['temp status']]>ordering_dict[x['Group Name Type']] else '', axis = 1)


# In[765]:


# people for whom ancestry.com just messed up the matching - the state, county etc is wrong, so we want to remove these people from the match
rem_ind = df_final[df_final.fillna("")['temp'] != ""][df_final[df_final.fillna("")['temp'] != ""].apply(
    lambda x: statedict[x['Group State']] != x['temp'][0] and x['Group State'] != 'NY', axis=1)].index
df_final.loc[rem_ind, 'Group Match Index'] = ''

# places where the county that is given on ancestry is different from the county we have
county_loc_conflict = df_final[df_final.fillna("")['temp'] != ""][df_final[df_final.fillna("")['temp'] != ""].apply(
    lambda x: x['Group County'] != x['temp'][1] and x['Group County'] != '' and x['Group Match Index'] != '',
    axis=1)].index
df_final.loc[county_loc_conflict, 'location conflict'] = 'county'

# places where the town that is given on ancestry is different from the tow  we have
town_loc_conflict = df_final[df_final.fillna("")['temp'] != ""][df_final[df_final.fillna("")['temp'] != ""].apply(
    lambda x: x['Group Town'] != x['temp'][2] and x['Group Town'] != '' and x['Group Match Index'] != '' and x[
        'location conflict'] == '', axis=1)].index
df_final.loc[town_loc_conflict, 'location conflict'] = 'town'

# see if we can add location when we only have one match
rep_ind = df_final[df_final.fillna("")['temp'] != ""][df_final[df_final.fillna("")['temp'] != ""].apply(
    lambda x: x['location conflict'] == '' and x['Group Match Index'] != '', axis=1)].index


# In[766]:


# places where the town that is given on ancestry is different from the town we have
town_loc_conflict = df_final[df_final.fillna("")['temp'] != ""][df_final[df_final.fillna("")['temp'] != ""].apply(
    lambda x: x['Group Town'] != x['temp'][2] and x['Group Town'] != '' and x['Group Match Index'] != '' and x[
        'location conflict'] == '', axis=1)].index
df_final.loc[town_loc_conflict, 'location conflict'] = 'town'

# see if we can add location when we can recover the location
rep_ind = df_final[df_final.fillna("")['temp'] != ""][df_final[df_final.fillna("")['temp'] != ""].apply(
    lambda x: x['location conflict'] == '' and x['Group Match Index'] != '', axis=1)].index
df_final.loc[rep_ind, 'imputed_location'] = df_final.loc[rep_ind].apply(
    lambda x: match_df.loc[int(x['Group Match Index'])]['Match Type'] if pd.isnull(x['temp status']) else x[
        'temp status'], axis=1)

# add in imputed data
df_final.loc[rep_ind, 'Group State'] = df_final.loc[rep_ind, 'temp'].apply(lambda x: statedict_rev[x[0]])
df_final.loc[rep_ind, 'Group County'] = df_final.loc[rep_ind, 'temp'].apply(lambda x: x[1] + ' County')
df_final.loc[rep_ind, 'Group Town'] = df_final.loc[rep_ind, 'temp'].apply(lambda x: x[2])
df_final.loc[rep_ind, 'Group Village'] = df_final.loc[rep_ind, 'temp'].apply(lambda x: x[3])
df_final.fillna("", inplace=True)
df_final.drop('temp', axis=1, inplace=True)
df_final.drop('temp status', axis=1, inplace=True)


# ## Occupation Column Cleaning

# In[767]:


# next, we're going to add the occupation information from ancestry.com into the occupation column in our main data
match_df['Occupation'].fillna('', inplace=True)
df_final['occupation'] = df_final.apply(lambda x: tNameList((" | ".join(
    [match_df.loc[int(ele), 'Occupation'] for ele in x['Group Match Index'].split(" | ")]) + " | " + x[
                                                                 'occupation']).split(" | ")) if x[
                                                                                                     'Group Match Index'] != '' and
                                                                                                 x[
                                                                                                     'Group Match Index'] != 'Unsearchable (not a name)' else
x['occupation'], axis=1)


# In[768]:


# import dictionary to clean occupations
occ_data = pd.read_csv(INDIR_RAW / 'corrections/occ/postscrape/occ_fix.csv')
occ_dict = dict(zip(occ_data['Original'], occ_data['Corrected']))
# manual additions to occupation dictionary because we can't work with commas in a csv file
occ_dict[''] = ''
occ_dict['Notary, Scrivenor & Broker'] = 'Broker'
occ_dict['Notary, Scrivener & Broker'] = 'Broker'
occ_dict['Notary, Scrivener, & Broker'] = 'Broker'
# change occupations
df_final['occupation'] = df_final['occupation'].apply(
    lambda x: tNameList([str(occ_dict.get(ele, ele)) for ele in x.split(" | ")]))


# In[770]:


"""print(occ_data[occ_data['Corrected'].apply(lambda x: x in ['Merchant'])].head(9)[['Original', 'Corrected']].to_markdown())"""


# ## Reset Match Data Index

# In[773]:


# finally, we're going to create a new column in the match dataframe where all the indices of the people who are not matched to anyone are removed, so our match index goes from 0 to the total number of matches
# first we remove the people who are not matched to anyone
match_df = match_df.loc[sorted(list(set([int(ele) for ele in df_final['Group Match Index'].apply(lambda x: x.split(" | ") if x != '' and x != 'Unsearchable (not a name)' else []).explode().tolist() if not pd.isnull(ele)])))]


for ind in df_final[df_final['Group Match Index'].apply(lambda x: "|" in x)].index:
    match_data = match_df.loc[[int(ele) for ele in df_final.loc[ind, 'Group Match Index'].split(" | ")]]
    town, county = df_final.loc[ind, 'Group Town'], df_final.loc[ind, 'Group County']
    match_town, match_county = [ele for ele in list(set(match_data['Match Town'].tolist())) if ele != ""], [ele for ele
                                                                                                            in list(
            set(match_data['Match County'].tolist())) if ele != ""]
    if len(match_town) == 2 and town in match_town:
        match_ind = match_data[match_data['Match Town'] == town]['index_new'].tolist()
        df_final.loc[ind, 'Group Match Index'] = tNameList([str(ele) for ele in match_ind])
    elif len(match_county) == 2 and county in match_county:
        match_ind = match_data[match_data['Match County'] == county]['index_new'].tolist()
        df_final.loc[ind, 'Group Match Index'] = tNameList([str(ele) for ele in match_ind])

match_df.drop(['index_temp', 'index_new'], inplace=True, axis=1)

# next, we want to remove entries in match_list that are duplicated, and create a dictionary that maps the old indices in df_list to the new indices, after we drop duplicates in match_list

# save old index
match_df['index_old'] = match_df.index
# drop duplicates, create temporary index column
match_list_no_dup = match_df.drop_duplicates(subset=[ele for ele in match_df.columns if ele != 'index_old'])
match_list_no_dup.rename({'index_old': 'index_temp'}, axis=1, inplace=True)

# create mapping between old index, and temporary new index
# the temporary new index removes indices of repeated values without renumbering anything
match_dict_df = pd.merge(match_df.reset_index(),
                         match_list_no_dup,
                         how='left').set_index('index')
match_dict_df['index_old'] = match_dict_df.index

# now, we want to renumber the temporary index so that it is sequential and doesn't skip any numbers
# we call this the new index
gen_newind = match_dict_df[['index_temp']].drop_duplicates().reset_index(drop=True).copy()
gen_newind['index_new'] = gen_newind.index
# merge in new index to merged dataframe, map old index to new index
match_dict_df = pd.merge(match_dict_df, gen_newind)
match_dict = dict(zip(match_dict_df['index_old'], match_dict_df['index_new']))

# change from old indices to new indices in df_list dataframe
df_final['Group Match Index'] = df_final['Group Match Index'].apply(
    lambda x: tNameList([str(match_dict[int(ele)]) for ele in x.split(' | ')]) if x not in ["",
                                                                                            'Unsearchable (not a name)'] else "")
# change match_list dataframe so that it removes duplicates and is indexed by the new index method
match_df = pd.merge(match_list_no_dup, gen_newind)
match_df['index_new'] = match_df['index_new'].apply(lambda x: str(x))


# ## Aggregate Asset Totals

# In[774]:


# find how many people own a particular asset
# add that as suffix at end of debt asset
asset_count_dict = df_final['assets'].apply(lambda x: [ele.split(" : ")[0] for ele in x.split(" | ")]).explode().value_counts().to_dict()
asset_count_dict
df_final['assets'] = df_final['assets'].apply(lambda x: " | ".join([ele.split(" : ")[0] + "_" + str(asset_count_dict[ele.split(" : ")[0]]) + " : " + ele.split(" : ")[1] for ele in x.split(" | ")]))


# In[775]:


# total debt assets (not adjusted for ownership - sum is more than total amount of debt held
df_final['6p_total'] = df_final['assets'].apply(lambda x: sum([pd.to_numeric(ele.split(" : ")[1].split(",")[0]) for ele in x.split(" | ")]))
df_final['6p_def_total'] = df_final['assets'].apply(lambda x: sum([pd.to_numeric(ele.split(" : ")[1].split(",")[1]) for ele in x.split(" | ")]))
df_final['unpaid_interest'] = df_final['assets'].apply(lambda x: sum([pd.to_numeric(ele.split(" : ")[1].split(",")[2]) for ele in x.split(" | ")]))


# In[776]:


# total debt assets (adjusted for ownership, assuming equal ownership)
df_final['6p_total_adj'] = df_final['assets'].apply(lambda x: sum([pd.to_numeric(ele.split(" : ")[1].split(",")[0])/pd.to_numeric(ele.split(" : ")[0].split("_")[2]) for ele in x.split(" | ")]))
df_final['6p_def_total_adj'] = df_final['assets'].apply(lambda x: sum([pd.to_numeric(ele.split(" : ")[1].split(",")[1])/pd.to_numeric(ele.split(" : ")[0].split("_")[2]) for ele in x.split(" | ")]))
df_final['unpaid_interest_adj'] = df_final['assets'].apply(lambda x: sum([pd.to_numeric(ele.split(" : ")[1].split(",")[2])/pd.to_numeric(ele.split(" : ")[0].split("_")[2]) for ele in x.split(" | ")]))


# In[777]:


df_final['final_total'] = df_final['6p_total'] + df_final['6p_def_total']
df_final['final_total_adj'] = df_final['6p_total_adj'] + df_final['6p_def_total_adj']


# ## Final Data Export

# In[ ]:


df_final['Group County'] = df_final['Group County'].apply(lambda x: x.replace('County County', 'County') if not pd.isnull(x) else x)


# In[778]:


match_df.drop('index_temp', axis = 1).to_csv(OUTDIR / "match_data_CD.csv")
df_final.reset_index(drop = True).to_csv(OUTDIR / "final_data_CD.csv")


# In[781]:


match_df.drop('index_temp', axis = 1)

