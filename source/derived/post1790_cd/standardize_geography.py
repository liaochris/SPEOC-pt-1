#!/usr/bin/env python
# coding: utf-8

# In[1]:


from pathlib import Path
import numpy as np
import pandas as pd
from rapidfuzz import process

INDIR_RAW = Path("source/raw/post1790_cd")
INDIR_CENSUS = Path("source/raw/census_data")
OUTDIR = Path("output/derived/post1790_cd")


# ## Helper Functions

# In[2]:


def deNaN(series):
    """
    amends pandas series by replacing NaN values with empty strings
    :param series: pandas series
    """

    return series.apply(lambda x: "" if type(x) != str else x)


# In[3]:


def combineCols(df, state, num=3, namenum=3):
    """
    combines our multiple town, occupation and state columns into one column
    creates one town column from town 1, town 2, town 3 columns
    :param df: raw state debt dataframe
    :param state: abbreviation of state
    :param num: number of columns to combine (3 or 2) for each town, occupation and state
    :param namenum: number of name columns
    :return: dataframe with combined columns
    """

    # define dataframe that stores changes
    change_df_agg = pd.DataFrame(columns=['old', 'new', 'type'])
    # combine values for each type of column into a set
    for col in ['town', 'state', 'occupation']:
        if num == 3:
            df[col] = [set([" ".join(x.split()) for x in [t1, t2, t3] if not pd.isnull(x)]) for t1, t2, t3 in
                       zip(df[col + '1'],
                           df[col + '2'],
                           df[col + '3'])]
        else:
            df[col] = [set([" ".join(x.split()) for x in [t1, t2] if not pd.isnull(x)]) for t1, t2 in zip(df[col + '1'],
                                                                                                          df[
                                                                                                              col + '2'])]
        # if there is only one unique value, then change the set to a string
        if not any(df[col].apply(lambda x: len(x) > 1).tolist()):
            print("reformatting {}".format(col))
            df[col] = df[col].apply(lambda x: x.pop() if x != set() else np.nan)
        # if there are multiple unique values, then keep the value that has the most characters
        # record changes in change_df_agg
        else:
            print("{} column has multiple unique entries".format(col))
            print("see table at end for new entries")
            old = df[df[col].apply(lambda x: len(x) > 1)][col]
            df[col] = df[col].apply(
                lambda x: x.pop() if len(x) == 1 else np.nan if x == set() else max(list(x), key=len))

            # create dataframe of changes
            change_df = pd.DataFrame([old, df.loc[old.index][col]]).T
            change_df.columns = ['old', 'new']
            change_df['type'] = col
            # create dataframe of changes with strings because .drop_duplicates() only works with strings
            change_df_str = change_df.copy()
            change_df_str['old'] = change_df_str['old'].astype(str)
            change_df_str = change_df_str.drop_duplicates()
            # add filtered database of changes to aggregate dataset
            change_df_agg = pd.concat([change_df_agg, change_df.loc[change_df_str.index]])

    # combine names into one column
    if namenum == 3:
        df['Name 1'] = deNaN(df['First Name']) + " " + deNaN(df['Last Name'])
        df['Name 2'] = deNaN(df['First Name.1']) + " " + deNaN(df['Last Name.1'])
        df['Name 3'] = deNaN(df['First Name.2']) + " " + deNaN(df['Last Name.2'])
        df['Name'] = list(
            list(set([x.replace("  ", " ").strip() for x in [name1, name2, name3] if x.strip() != ""])) for
            name1, name2, name3 in zip(df['Name 1'], df['Name 2'], df['Name 3']))
        df['Name'] = df['Name'].apply(lambda x: " | ".join(sorted(x)))

    # add state label when missing
    df.loc[df.query('state.isna() and town.isna()').index, 'state'] = state
    df['state_data'] = state
    df['state_data_index'] = np.arange(1, df.shape[0] + 1, 1)
    change_df_agg['state'] = state

    return df[['6p_Dollar', '6p_Cents', '6p_def_Dollar', '6p_def_Cents', '3p_Dollar', '3p_Cents',
               'town', 'state', 'occupation', 'Name', 'First Name', 'Last Name', 'state_data', 'state_data_index']], change_df_agg


# In[4]:


def cleanSingleColumn(df, state):
    """
    format raw data with only one name/town/occupation column

    :param df: raw state debt dataframe
    :param state: abbreviation of state
    :return: dataframe with added columns
    """
    # create name column, format it in list, add state and state_data_index columns
    df['Name'] = deNaN(df['First Name']) + " " + deNaN(df['Last Name'])
    df.loc[df.query('state.isna() and town.isna()').index, 'state'] = state
    df['state_data'] = state
    df['state_data_index'] = np.arange(1, df.shape[0] + 1, 1)
    return df


# ## Import Raw Data

# In[5]:


# columns used for ct, md, pa, ri, sc, ny
tripcols = ['First Name', 'Last Name', 'town1', 'state1', 'occupation1', '6p_Dollar', '6p_Cents',
 'First Name.1', 'Last Name.1', 'town2', 'state2', 'occupation2', '6p_def_Dollar', '6p_def_Cents',
 'First Name.2', 'Last Name.2', 'town3', 'state3', 'occupation3', '3p_Dollar', '3p_Cents', ]
# columns used for ga, nc, nh
sincols = ['First Name', 'Last Name', 'town', 'state', 'occupation', '6p_Dollar', '6p_Cents',
 '6p_def_Dollar', '6p_def_Cents', '3p_Dollar', '3p_Cents']

# aggregate data column format
aggcols = ['6p_Dollar', '6p_Cents', '6p_def_Dollar', '6p_def_Cents', '3p_Dollar', '3p_Cents',
           'town', 'state', 'occupation', 'Name', 'First Name', 'Last Name', 'state_data', 'state_data_index']
CD_all = pd.DataFrame(columns= aggcols)
# format for data that we changed
change_df_CD = pd.DataFrame(columns = ['old', 'new', 'type', 'state'])


# In[6]:


# NY loan data
# new york data is formatted a bit differently so we have to handle it manually
# in particular it has no occupation or town data
NY_CD_raw = pd.read_excel(INDIR_RAW / "orig/NY/NY_1790_CD.xlsx",
                          header = 11, usecols = 'H, I, M, N, X, Y, AC, AD, AM, AN, AR, AS')
NY_CD_raw.columns = ['First Name', 'Last Name', '6p_Dollar', '6p_Cents',
                     'First Name.1', 'Last Name.1', '6p_def_Dollar', '6p_def_Cents',
                     'First Name.2', 'Last Name.2', '3p_Dollar', '3p_Cents']
# create name column
NY_CD_raw['Name 1'] =  deNaN(NY_CD_raw['First Name']) + " " + deNaN(NY_CD_raw['Last Name'])
NY_CD_raw['Name 2'] =  deNaN(NY_CD_raw['First Name.1']) + " " + deNaN(NY_CD_raw['Last Name.1'])
NY_CD_raw['Name 3'] =  deNaN(NY_CD_raw['First Name.2']) + " " + deNaN(NY_CD_raw['Last Name.2'])


NY_CD_raw['Name'] = list(
    list(set([x.replace("  ", " ").strip() for x in [name1, name2, name3] if x.strip() != ""])) for
    name1, name2, name3 in zip(NY_CD_raw['Name 1'], NY_CD_raw['Name 2'], NY_CD_raw['Name 3']))
NY_CD_raw['Name'] = NY_CD_raw['Name'].apply(lambda x: " | ".join(sorted(x)))
NY_CD_raw['town'] = np.nan
NY_CD_raw['state'] = 'NY'
NY_CD_raw['occupation'] = np.nan
NY_CD_raw['state_data'] = 'NY'
NY_CD_raw['state_data_index'] = np.arange(1, NY_CD_raw.shape[0] + 1, 1)


NY_CD = NY_CD_raw[['6p_Dollar', '6p_Cents', '6p_def_Dollar', '6p_def_Cents', '3p_Dollar', '3p_Cents',
 'town', 'state', 'occupation', 'Name', 'First Name', 'Last Name', 'state_data', 'state_data_index']]


# In[7]:


# import data, clean
raw_params = pd.read_csv(INDIR_RAW / 'docs/cd_raw.csv', delimiter=',', header=0)
raw_params.drop('Unnamed: 6', inplace=True, axis=1)

# iterate through each entry
for ind in raw_params.index:
    # define key variables
    file, header, usecols, numcols, state, dropcols = raw_params.loc[
        ind, ['file', 'header', 'usecols', 'numcols', 'state', 'dropcols']]
    print("\nCleaning " + state)
    cd_raw = pd.read_excel(file, header=header, usecols=usecols)
    cd_raw.columns = tripcols if numcols == 3 else sincols
    if not pd.isnull(dropcols):
        # convert to list of ints
        dropcols = [int(x) for x in dropcols.split(",")]
        cd_raw.drop(dropcols, inplace=True)
    if numcols == 3:
        cd_state, change_df = combineCols(cd_raw, state)
    else:
        cd_state = cleanSingleColumn(cd_raw, state)
        cd_state = cd_state[['6p_Dollar', '6p_Cents', '6p_def_Dollar', '6p_def_Cents', '3p_Dollar', '3p_Cents',
                             'town', 'state', 'occupation', 'Name', 'First Name', 'Last Name', 'state_data', 'state_data_index']]
    CD_all = pd.concat([CD_all, cd_state])
    change_df_CD = pd.concat([change_df_CD, change_df])


# In[8]:


CD_all = pd.concat([CD_all,NY_CD])


# ## Adding County (and Other Geography) Labels - Fuzzy Matching

# In[9]:


def fuzzyMatch(unmatched_towns, towns, crosswalk, primary_dict, dict_matchcol='primary_city', initial=True,
               score_threshold=85):
    """
    Function to support fuzzy matching algorithm that helps us match towns to counties. We use fuzzy matching to match our town names to town names in the crosswalk, and our town names to county names in the crosswalk (because sometimes the given town name is actually a county name)

    :param unmatched_towns: list of towns that need to be matched
    :param towns: dataframe of matched towns that we add to and items we want to match
    :param crosswalk: complete town-county crosswalk for our particular state, cannot use to directly match. used to obtain information for when we're doing city-county fuzzy matches vs. county-county fuzzy matches
    :param primary_dict: town-county crosswalk we can use to directly match towns
    :param dict_matchcol: column in crosswalk to match to - options are either 'primary_city' or 'county'.
    :param initial: whether this is the first time we're doing fuzzy matching on this set of unmatched towns
    :param score_threshold: threshold for a match in fuzzy score matching
    :return: towns dataframe with our matches added in
    """
    # decribe type of match
    if initial:
        print("\nFuzzy City name - county matches\n")
    else:
        print("\nFuzzy City name - county matches with manual string changes\n")

    printedtowns = []
    for town in unmatched_towns:
        # extract best match
        match_tuple = process.extractOne(town, [x for x in crosswalk[dict_matchcol] if not pd.isnull(x)])
        score = match_tuple[1]
        match = match_tuple[0]
        # if match above threshold, change + print match so we can hand check
        if score >= score_threshold:
            # we found another city that matches our city, so we can assign a county based on that
            if dict_matchcol == 'primary_city':
                county = primary_dict[match]
            # there is another county that resembles our city (which is actually a county)
            if dict_matchcol == 'county':
                county = match
            # add match, print out match
            # also add match information
            if initial:
                print("{} -> {} in {}".format(town, match, county))
                town_index = towns[towns['town'] == town].index
                towns.loc[town_index, 'county'] = county
                towns.loc[town_index, 'new_town'] = match
            else:
                original_town = towns[towns['town2'] == town]['town'].tolist()
                if town not in printedtowns:
                    print("{} (new name: {}) -> {} in {}".format(original_town, town, match, county))
                    printedtowns.append(town)
                town_index = towns[towns['town'].apply(lambda x: x in original_town)].index
                towns.loc[town_index, 'county'] = [county] * len(town_index)
                towns.loc[town_index, 'new_town'] = [match] * len(town_index)
    return towns


# In[10]:


def directTownMatch(state_cw_given, towns, col='primary_city', towncol='town'):
    """
    dataframe to directly match town names in towns to counties based off perfect name matches between town names in our dataset and town names in the crosswalk

    :param state_cw_given: the crosswalk for the state we have
    :param towns: dataframe of matched towns that we add to and items we want to match
    :param col: which column of crosswalk we're matching to - primary_city or acceptable_cities
    :param towncol: whether we're matching on town or town2 (town2 includes changes we've made to town column)
    :return: towns dataframe with our matches added in
    """
    print("Direct City name - county matches\n")
    #
    # create state crosswalk, with primary city as key and county as value
    # define city-county pair by picking which county appears most often for a given city
    state_cw = state_cw_given[[col, 'county']].groupby(col).county.agg(lambda x : x.mode()[0]).reset_index()
    # turn crosswalk into a hash map
    primary_dict = dict(zip(state_cw[col], state_cw['county']))

    # match on primary_city column of state cw
    if col == 'primary_city':
        towns['county'] = towns[towncol].apply(lambda x: primary_dict.get(x, np.nan))
        towns['new_town'] = [tn if not pd.isnull(cty) else np.nan for cty, tn in zip(towns['county'], towns['town'])]
    # match on acceptable_cities column of state cw
    if col == 'acceptable_cities':
        for ind in towns.index:
            town = towns.loc[ind, 'town']
            county = state_cw[state_cw[col].apply(lambda x: town in x if not pd.isnull(x) else False)][
                'county'].tolist()
            if len(county) > 0:
                towns.loc[ind, 'county'] = county[0]
                towns.loc[ind, 'new_town'] = town

    # only print out towns that were matched
    t = towns[towns['county'].apply(lambda x: not pd.isnull(x))]
    if towncol == 'town':
        for tn, cty in zip(t['town'], t['county']):
            print("{} was matched to {} directly using the crosswalk".format(tn, cty))
    if towncol == 'town2':
        for tn, tn_og, cty in zip(t['town2'], t['town'], t['county']):
            print("{} (original: {}) was matched to {} directly using the crosswalk".format(tn, tn_og, cty))
    return primary_dict, towns


# In[11]:


def directCountyMatch(state_cw, towns, towncol='town'):
    """
    dataframe to directly match town names in towns to counties based off perfect name matches, in cases when town names are actually county names based off perfect name matches between town names (county names) in our dataset and county names in the crosswalk

    :param state_cw: the crosswalk for the state we have
    :param towns: dataframe of matched towns that we add to and items we want to match
    :param towncol: whether we're matching on town or town2 (town2 includes changes we've made to town column)
    :return: towns dataframe with our matches added in
    """
    print("\nSome city names are actually county names")
    if towncol == 'town':
        print("Direct City (county) name - county matches\n")
    if towncol == 'town2':
        print("Direct City (county) name with string changes - county matches\n")
    # some own names are actually counties
    # match towns based off whether town name is actually county name in crosswalk
    counties = state_cw['county'].unique()
    # for towns with unmatched counties, if town column values are actually a county, add matched county
    nanindex = towns[towns['county'].apply(lambda x: pd.isnull(x))].index
    towns.loc[nanindex, 'county'] = towns.loc[nanindex, towncol].apply(
        lambda x: x if x in counties.tolist() else np.nan)
    # print out towns that were matched
    towns2 = towns.loc[nanindex]
    nanindex2 = towns2[towns2['county'].apply(lambda x: not pd.isnull(x))].index
    for t, c in zip(towns2.loc[nanindex2, towncol], towns2.loc[nanindex2, 'county']):
        print("{} was matched to {} using the crosswalk".format(t, c))

    return towns


# In[12]:


# change column of town dataframe's type to either town or county
def addType(towns, type='town'):
    """
    add type column to towns dataframe, based off whether the town we matched on is a town or a county
    :param towns: dataframe of matches
    :param type: the type we're inputting
    :return: towns dataframe with our matches
    """
    towns['name_type'] = [name_type if not pd.isnull(name_type) else type if not pd.isnull(county) else np.nan for
                          name_type, county in
                          zip(towns['name_type'], towns['county'])]
    return towns


# In[13]:


# crosswalk of city-county matches (modern-day)
city_county_cw = pd.read_excel(INDIR_CENSUS / 'orig/zip_code_database.xls')[['primary_city', 'acceptable_cities',
                                                                                 'unacceptable_cities', 'county',
                                                                                 'state']]

# columns of final crosswalk format
final_cw = pd.DataFrame(columns=['town', 'county', 'state', 'name_type', 'new_town', 'new_state', 'country'])
# list of states that we're going to clean/try to match
list_of_states = ['CT', 'GA', 'MD', 'NC', 'NH', 'NJ', 'PA', 'RI', 'SC',
                  'MA', 'VA', 'DE']
# each state has its own sequence of matching procedures (using the functions above) that I determined. the general options are
# 1. matching a town name to a town in the state crosswalk directly or through fuzzy matching
# 2. changing a town name to account for idiosyncracies before matching directly through the crosswalk or through fuzzy matching
# 3. matching a town name that's actually a county name to a county name directly or through fuzzy matching

for state in list_of_states:
    print("\n{} MATCHING \n".format(state))
    # create list of towns for each state
    towns = CD_all[CD_all['state'] == state][['town']].drop_duplicates()
    towns = towns[towns['town'].apply(lambda x: not pd.isnull(x))]
    # state crosswalk
    state_cw = city_county_cw[city_county_cw['state'] == state]
    if state == 'VA':
        state_cw = city_county_cw[city_county_cw['state'].apply(lambda x: x in ['VA', 'WV'])]
    state_cw = state_cw[state_cw['county'].apply(lambda x: 'county' in x.lower() if not pd.isnull(x) else False)]

    # try direct match: town name -> crosswalk town-county
    oldtowns = towns.copy()
    primary_dict, towns = directTownMatch(state_cw, towns, col='primary_city', towncol='town')
    # label name type
    towns['name_type'] = towns['county'].apply(lambda x: 'town' if not pd.isnull(x) else np.nan)

    if state == 'CT':
        # try fuzzy match: town name -> crosswalk town-county
        unmatched_towns1 = towns[towns['county'].apply(lambda x: pd.isnull(x))]['town']
        towns = fuzzyMatch(unmatched_towns1, towns, state_cw, primary_dict, dict_matchcol='primary_city', initial=True,
                           score_threshold=85)
        towns = addType(towns)

        # modify town names - towns changed names (see CT note)
        # retry fuzzy match: town name -> crosswalk town-county
        towns['town2'] = towns['town'].apply(
            lambda x: x.replace('Huntington', 'Shelton').replace('Chatham', 'East Hampton'))
        unmatched_towns2 = towns[towns['county'].apply(lambda x: pd.isnull(x))]['town2']
        towns = fuzzyMatch(unmatched_towns2, towns, state_cw, primary_dict, dict_matchcol='primary_city', initial=False,
                           score_threshold=85)
        towns = addType(towns)

    if state == 'GA':
        # some "town" names are actually counties
        # try direct match: town (county) name -> crosswalk county
        towns = directCountyMatch(state_cw, towns, towncol='town')
        towns = addType(towns, 'county')

    if state == 'MD':
        # remove instances where Maryland is mentioned and unabbreviate county abbreviations
        # use modified town names
        # try direct match: town (county) name -> crosswalk county
        towns['town2'] = towns['town'].apply(lambda x: x.replace('Maryland', '').replace('Co ', 'County').strip())
        towns = directCountyMatch(state_cw, towns, towncol='town2')
        towns = addType(towns, 'county')

        # use modified town names
        # try fuzzy match: town (county) name -> crosswalk county
        unmatched_towns2 = towns[towns['county'].apply(lambda x: pd.isnull(x))]['town2']
        towns = fuzzyMatch(unmatched_towns2, towns, state_cw, primary_dict, dict_matchcol='county', initial=False,
                           score_threshold=86)
        towns = addType(towns, 'county')

        # use modified town names
        # try fuzzy match: town name -> crosswalk town-county
        unmatched_towns2 = towns[towns['county'].apply(lambda x: pd.isnull(x))]['town2']
        towns = fuzzyMatch(unmatched_towns2, towns, state_cw, primary_dict, dict_matchcol='primary_city', initial=False,
                           score_threshold=85)
        towns = addType(towns)

        # correct a matching - Baltimore City to Baltimore County
        print("Baltimore City changed to Baltimore County")
        towns['county'] = towns['county'].apply(lambda x: x.replace('City', 'County') if not pd.isnull(x) else x)
        towns = addType(towns)
    if state == 'NC':
        # some "town" names are actually counties
        # try direct match: town (county) name -> crosswalk county
        towns = directCountyMatch(state_cw, towns, towncol='town')
        towns = addType(towns, 'county')
        # remove instances where North Carolina is mentioned and rename Tarborugh to enable matching
        towns['town2'] = towns['town'].apply(
            lambda x: x.replace('North Carolina', '').replace('Tarborugh', 'Tarboro').strip())
        # use modified town names
        # try fuzzy match: town name -> crosswalk town-county
        unmatched_towns2 = towns[towns['county'].apply(lambda x: pd.isnull(x))]['town2']
        towns = fuzzyMatch(unmatched_towns2, towns, state_cw, primary_dict, dict_matchcol='primary_city', initial=False,
                           score_threshold=85)
        towns = addType(towns)
    if state == 'NH':
        # use acceptable_cities instead of primary_cities column to match in the crosswalk
        # try direct match: town name -> crosswalk town-county
        null_ind = towns[towns['county'].apply(lambda x: pd.isnull(x))].index
        pdict, tn = directTownMatch(state_cw, towns.loc[null_ind], col='acceptable_cities', towncol='town')
        towns.loc[null_ind] = tn
        towns = addType(towns)
        # remove instances where New Hampshire and other geo-jurisdictional terms are used
        # rename Rockingham to enable matching
        towns['town2'] = towns['town'].apply(
            lambda x: x.replace('State', '').replace('New Hampshire', '').replace('of ', '').strip())
        towns['town2'] = towns['town2'].apply(lambda x: x.replace('Rockingham', 'Rockingham County').strip())
        # use modified town names
        # try fuzzy match: town name -> crosswalk town-county
        unmatched_towns2 = towns[towns['county'].apply(lambda x: pd.isnull(x))]['town2']
        towns = fuzzyMatch(unmatched_towns2, towns, state_cw, primary_dict, dict_matchcol='primary_city', initial=False,
                           score_threshold=85)
        towns = addType(towns)

        # some "town" names are actually counties
        # use modified town names
        # try direct match: town (county) name -> crosswalk county
        towns = directCountyMatch(state_cw, towns, towncol='town2')
        towns = addType(towns, 'county')
        # manual fixes for matches
        # manually adjust incorrect matches
        print("\nManual Match\n")
        for town, county in zip(['Brintwood', 'Portsmouth New Hampshire'],
                                ['Rockingham County', 'Rockingham County']):
            print("{} was matched to {}".format(town, county))
            if town == 'Brintwood':
                towns.loc[towns[towns['town'] == town].index, ['county', 'name_type']] = [county, 'town']
            else:
                towns.loc[towns[towns['town'] == town].index, ['county', 'name_type']] = [county, 'county']
    if state == 'NJ':
        # remove instances where New Jersey is used
        towns['town2'] = towns['town'].apply(lambda x: x.replace('New Jersey', '').strip())

        # use modified town names
        # try fuzzy match: town name -> crosswalk town-county
        unmatched_towns2 = towns[towns['county'].apply(lambda x: pd.isnull(x))]['town2']
        towns = fuzzyMatch(unmatched_towns2, towns, state_cw, primary_dict, dict_matchcol='primary_city', initial=False,
                           score_threshold=85)
        towns = addType(towns)
        # some "town" names are actually counties
        # use modified town names
        # try direct match: town (county) name -> crosswalk county
        towns = directCountyMatch(state_cw, towns, towncol='town2')
        towns = addType(towns, 'county')
    if state == 'PA':
        # some "town" names are actually counties
        # try direct match: town (county) name -> crosswalk county
        towns = directCountyMatch(state_cw, towns, towncol='town')
        towns = addType(towns, 'county')

        # use acceptable_cities instead of primary_cities column to match in the crosswalk
        # try direct match: town (county) name -> crosswalk county
        null_ind = towns[towns['county'].apply(lambda x: pd.isnull(x))].index
        pdict, tn = directTownMatch(state_cw, towns.loc[null_ind], col='acceptable_cities', towncol='town')
        towns.loc[null_ind] = tn
        towns = addType(towns)

        # remove instances where New Jersey is used, fix some notational issues
        # correct Dauphincoy to Dauphin and categorize Tulpehocken as being in Berks County
        towns['town2'] = towns['town'].apply(
            lambda x: x.replace('Co ', 'County').replace('Delaware', 'Delaware County').strip())
        towns['town2'] = towns['town2'].apply(
            lambda x: x.replace('Pennsylvania', '').replace('County County', 'County').strip())
        towns['town2'] = towns['town2'].apply(
            lambda x: x.replace('Country', 'County').replace('Dauphincoy', 'Dauphin').strip())
        towns['town2'] = towns['town2'].apply(lambda x: x.replace('Tulpehocken', 'Berks County').strip())

        # categorize different Philadelphia neighborhoods as belonging in Philadelphia
        philreptowns = ['Blockley', 'Northan Liberties', 'Northern Liberties',
                        'The Northern Libert', 'Passyunk', 'German Town', 'Southwark',
                        'Borden Town']  # not sure on this last one...
        for town in philreptowns:
            towns['town2'] = towns['town2'].apply(lambda x: x.replace(town, 'Philadelphia'))
        towns = addType(towns)
        # use modified town names
        # try direct match: town (county) name -> crosswalk county
        unmatched_towns2 = towns[towns['county'].apply(lambda x: pd.isnull(x))]['town2']
        towns = directCountyMatch(state_cw, towns, 'town2')
        towns = addType(towns, 'county')
        # some "town" names are actually counties
        # try direct match: town (county) name -> crosswalk county
        towns = directCountyMatch(state_cw, towns, towncol='town')
        towns = addType(towns, 'county')

        # use acceptable_cities instead of primary_cities column to match in the crosswalk
        # try direct match: town (county) name -> crosswalk county
        null_ind = towns[towns['county'].apply(lambda x: pd.isnull(x))].index
        pdict, tn = directTownMatch(state_cw, towns.loc[null_ind], col='acceptable_cities', towncol='town')
        towns.loc[null_ind] = tn
        towns = addType(towns)

        # remove instances where New Jersey is used, fix some notational issues
        # correct Dauphincoy to Dauphin and categorize Tulpehocken as being in Berks County
        towns['town2'] = towns['town'].apply(
            lambda x: x.replace('Co ', 'County').replace('Delaware', 'Delaware County').strip())
        towns['town2'] = towns['town2'].apply(
            lambda x: x.replace('Pennsylvania', '').replace('County County', 'County').strip())
        towns['town2'] = towns['town2'].apply(
            lambda x: x.replace('Country', 'County').replace('Dauphincoy', 'Dauphin').strip())
        towns['town2'] = towns['town2'].apply(lambda x: x.replace('Tulpehocken', 'Berks County').strip())

        # categorize different Philadelphia neighborhoods as belonging in Philadelphia
        philreptowns = ['Blockley', 'Northan Liberties', 'Northern Liberties',
                        'The Northern Libert', 'Passyunk', 'German Town', 'Southwark',
                        'Borden Town']  # not sure on this last one...
        for town in philreptowns:
            towns['town2'] = towns['town2'].apply(lambda x: x.replace(town, 'Philadelphia'))
        towns = addType(towns)
        # use modified town names
        # try direct match: town (county) name -> crosswalk county
        unmatched_towns2 = towns[towns['county'].apply(lambda x: pd.isnull(x))]['town2']
        towns = directCountyMatch(state_cw, towns, 'town2')
        towns = addType(towns, 'county')

        # use modified town names
        # try fuzzy match: town name -> crosswalk town-county
        unmatched_towns2 = towns[towns['county'].apply(lambda x: pd.isnull(x))]['town2']
        towns = fuzzyMatch(unmatched_towns2, towns, state_cw, primary_dict, dict_matchcol='primary_city', initial=False,
                           score_threshold=85)
        towns = addType(towns)

        # use modified town names
        # try fuzzy match: town (county) name -> crosswalk county
        unmatched_towns2_1 = [x for x in towns[towns['county'].apply(lambda x: pd.isnull(x))]['town2'] if x != '']
        towns = fuzzyMatch(unmatched_towns2_1, towns, state_cw, primary_dict, dict_matchcol='county', initial=False,
                           score_threshold=85)
        towns = addType(towns, 'county')

        # use modified town names
        # try fuzzy match: town name -> crosswalk town-county
        unmatched_towns2 = towns[towns['county'].apply(lambda x: pd.isnull(x))]['town2']
        towns = fuzzyMatch(unmatched_towns2, towns, state_cw, primary_dict, dict_matchcol='primary_city', initial=False,
                           score_threshold=85)
        towns = addType(towns)

        # use modified town names
        # try fuzzy match: town (county) name -> crosswalk county
        unmatched_towns2_1 = [x for x in towns[towns['county'].apply(lambda x: pd.isnull(x))]['town2'] if x != '']
        towns = fuzzyMatch(unmatched_towns2_1, towns, state_cw, primary_dict, dict_matchcol='county', initial=False,
                           score_threshold=85)
        towns = addType(towns, 'county')

    if state == 'RI':
        # remove instances where Rhode Island and other geo-jurisdictional terms are used
        towns['town2'] = towns['town'].apply(
            lambda x: x.replace('Rhode Island', '').replace('State ', '').replace('of', '').strip())
        # use modified town names
        # try fuzzy match: town name -> crosswalk town-county
        unmatched_towns2 = towns[towns['county'].apply(lambda x: pd.isnull(x))]['town2']
        towns = fuzzyMatch(unmatched_towns2, towns, state_cw, primary_dict, dict_matchcol='primary_city', initial=False,
                           score_threshold=85)
        towns = addType(towns)


    if state == 'SC':
        # remove instances where South Carolina is used, change number to character
        towns['town2'] = towns['town'].apply(
            lambda x: x.replace('South Carolina', '').replace('96', 'Ninety six').strip())

        # use modified town names
        # use acceptable_cities column
        # try fuzzy match: town (county) name -> crosswalk county
        null_ind = towns[towns['county'].apply(lambda x: pd.isnull(x))].index
        pdict, tn = directTownMatch(state_cw, towns.loc[null_ind], col='acceptable_cities', towncol='town2')
        towns.loc[null_ind] = tn
        towns = addType(towns)

        # use modified town names
        # try fuzzy match: town (county) name -> crosswalk county
        unmatched_towns2 = towns[towns['county'].apply(lambda x: pd.isnull(x))]['town2']
        towns = fuzzyMatch(unmatched_towns2, towns, state_cw, primary_dict, dict_matchcol='primary_city', initial=False,
                           score_threshold=85)
        towns = addType(towns)

        # some town names are actually county names
        # use modified town names
        # try fuzzy match: town (county) name -> crosswalk county
        unmatched_towns2_1 = towns[towns['county'].apply(lambda x: pd.isnull(x))]['town2']
        towns = fuzzyMatch(unmatched_towns2_1, towns, state_cw, primary_dict, dict_matchcol='county', initial=False,
                           score_threshold=85)
        towns = addType(towns, 'county')

    if state == 'MA':
        # remove instances where Massachusetts, MA or State is used
        towns['town2'] = towns['town'].apply(
            lambda x: x.replace('MA', '').replace('Massachusetts', '').replace('State', '').strip())
        # use modified town names
        # try fuzzy match: town (county) name -> crosswalk county
        unmatched_towns2 = towns[towns['county'].apply(lambda x: pd.isnull(x))]['town2']
        towns = fuzzyMatch(unmatched_towns2, towns, state_cw, primary_dict, dict_matchcol='primary_city', initial=False,
                           score_threshold=85)
        towns = addType(towns)

    if state == 'VA':
        # remove instances where Massachusetts, MA or State is used
        towns['town2'] = towns['town'].apply(
            lambda x: x.replace('VA', '').replace('Virginia', '').replace('Virgina', '').strip())
        towns['town2'] = towns['town2'].apply(lambda x: x.replace('State', '').replace(' of ', '').strip())
        # use modified town names
        # try fuzzy match: town (county) name -> crosswalk county
        unmatched_towns2 = towns[towns['county'].apply(lambda x: pd.isnull(x))]['town2']
        towns = fuzzyMatch(unmatched_towns2, towns, state_cw, primary_dict, dict_matchcol='primary_city', initial=False,
                           score_threshold=85)
        towns = addType(towns)

        # some town names are actually county names
        # use modified town names
        # try fuzzy match: town (county) name -> crosswalk county
        unmatched_towns2_1 = towns[towns['county'].apply(lambda x: pd.isnull(x))]['town2']
        towns = fuzzyMatch(unmatched_towns2_1, towns, state_cw, primary_dict, dict_matchcol='county', initial=False,
                           score_threshold=85)
        towns = addType(towns, 'county')

    if state == 'DE':
        # remove instances where Massachusetts, MA or State is used
        towns['town2'] = towns['town'].apply(
            lambda x: x.replace('Delaware', '').replace('State', '').replace(' of ', '').strip())
        towns['town2'] = towns['town2'].apply(lambda x: x.replace('Kent Company', 'Kent County').strip())
        # use modified town names
        # try fuzzy match: town (county) name -> crosswalk county
        unmatched_towns2 = towns[towns['county'].apply(lambda x: pd.isnull(x))]['town2']
        towns = fuzzyMatch(unmatched_towns2, towns, state_cw, primary_dict, dict_matchcol='primary_city', initial=False,
                           score_threshold=85)
        towns = addType(towns, 'county')

        # some town names are actually county names
        # use modified town names
        # try fuzzy match: town (county) name -> crosswalk county
        unmatched_towns2_1 = towns[towns['county'].apply(lambda x: pd.isnull(x))]['town2']
        towns = fuzzyMatch(unmatched_towns2_1, towns, state_cw, primary_dict, dict_matchcol='county', initial=False,
                           score_threshold=85)
        towns = addType(towns, 'county')

    # print out all unmatched names
    print("\nFinal Unmatched Names\n")
    t = towns[towns['county'].apply(lambda x: pd.isnull(x))]
    for tn in t['town']:
        print("{} was unable to be matched".format(tn))
    towns = towns[towns['county'].apply(lambda x: not pd.isnull(x))]
    towns['state'] = state
    towns['new_state'] = towns['state']
    # only Georgia doesn't have a town2 column
    if state not in ['GA']:
        towns.drop('town2', axis=1, inplace=True)

    final_cw = pd.concat([final_cw, towns])


# In[14]:


# merge our preliminary crosswalk with the original dataset to obtain full list of town-states that need to be matched
final_cw_all = pd.merge(CD_all[['town', 'state']].drop_duplicates(), final_cw, how='left', on=['town', 'state'])[
    ['town', 'state', 'new_town', 'county', 'new_state', 'country',
     'name_type']]
final_cw_all.reset_index(inplace=True, drop=True)


# ## Add Geography - Manual Changes

# In[15]:


# import dataset containing manual changes we make
df_manual = pd.read_csv(INDIR_RAW / 'corrections/town_fix.csv')
for ind in df_manual.index:
    match_town = df_manual.loc[ind, 'town']
    match_state = df_manual.loc[ind, 'state']

    # query the crosswalk to find the entry we want to change
    df_query = final_cw_all.copy()
    if not pd.isnull(match_town):
        if match_town == "*":
            df_query = df_query.query('town.isnull()')
        else:
            df_query = df_query.query(f'town ==  "{match_town}"')
    if not pd.isnull(match_state):
        df_query = df_query.query(f'state ==  "{match_state}"')

    # make the change
    final_cw_all.loc[df_query.index, ['new_town', 'county', 'new_state', 'name_type', 'country']] = df_manual.loc[ind, ['new_town', 'county', 'new_state', 'name_type', 'country']].tolist()

    print("Original Entry: {}".format(df_query[['town', 'state', 'new_town', 'county', 'new_state', 'country', 'name_type']].to_string(index=False)))
    print("Updated Entry: {}".format(final_cw_all.loc[df_query.index, ['town', 'state', 'new_town', 'county', 'new_state', 'country', 'name_type']].to_string(index=False)))


# In[16]:


# add country labels
final_cw_all.loc[final_cw_all[final_cw_all['country'].isnull()].index, 'country'] = 'US'


# ## Export Results

# In[17]:


# merge in our results to original debt dataset
CD_all = pd.merge(CD_all, final_cw_all, on=['town', 'state'], how='left')


# In[18]:


CD_all.loc[CD_all[CD_all['Name'].apply(lambda x: 'Samuel Athenton' in x)].index, 'new_state'] = 'MA'


# In[19]:


# find total amount of 6p certificates owned
CD_all['6p_total'] = CD_all['6p_Dollar'].apply(lambda x: 0 if pd.isnull(x) else x) + CD_all['6p_Cents'].apply(lambda x: 0 if pd.isnull(x) else x) / 100
CD_all['6p_def_total'] = CD_all['6p_def_Dollar'].apply(lambda x: 0 if pd.isnull(x) else x) + CD_all['6p_def_Cents'].apply(lambda x: 0 if pd.isnull(x) else x) / 100
CD_all['3p_total'] = CD_all['3p_Dollar'].apply(lambda x: 0 if pd.isnull(x) else x) + CD_all['3p_Cents'].apply(lambda x: 0 if pd.isnull(x) else x) / 100
CD_all = CD_all[CD_all.apply(lambda x: not (x['6p_total'] == 0 and x['6p_def_total'] == 0 and x['3p_total'] == 0), axis = 1)].reset_index(drop = True)


# In[20]:


CD_all.loc[CD_all[CD_all['state_data'] == 'NY'].index, 'new_state'] = 'NY'
CD_all.loc[CD_all[CD_all['state_data'] == 'NY'].index,'name_type'] = 'state'


# In[21]:


# data
CD_all.to_csv(OUTDIR / 'aggregated_CD_post1790.csv')
# check aggregation of towns/occupations
change_df_CD.to_csv(OUTDIR / 'check/town_occ_agg_check.csv')

