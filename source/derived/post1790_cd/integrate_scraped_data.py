#!/usr/bin/env python
# coding: utf-8

# In[1]:


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import numpy as np
from selenium.webdriver.common.keys import Keys


# ## Helper Structures and Data

# In[2]:


# state abbreviation conversion dictionary
statedict = {'PA': 'Pennsylvania', 'CT': 'Connecticut', 'MA': 'Massachusetts', 'NH': 'New Hampshire', 'DE': 'Delaware',
             'NC': 'North Carolina', 'GA': 'Georgia', 'NY': 'New York', 'NJ': 'New Jersey', 'RI': 'Rhode Island',
             'VA': 'Virginia', 'MD': 'Maryland', 'SC': 'South Carolina', 'VT': 'Vermont'}
# user variable
user = "Chris"


# In[8]:


final_name_list = pd.read_csv('scrape_tools/name_list.csv', index_col=0)[
    ['Fn_Fix', 'Ln_Fix', 'new_town', 'county', 'new_state', 'country', 'name_type']].drop_duplicates()
final_name_list.reset_index(inplace=True, drop=True)


# ## Helper Functions

# In[4]:


def tNameList(lst):
    """
    takes a list of names and returns a string of names separated by " | ", sorted and with duplicates removed, and with "" removed
    :param lst: input lst
    :return: string with names joined
    """
    return " | ".join(sorted(list(set([ele for ele in lst if ele != ""]))))


# In[5]:


def determineMatchList(name_type,state):
    """
    lists out the different options (how strict we will be with location + name) for searching that we will iterate through based on whether our location option is a town, county, state or nation location
    :param name_type: whether we have a town, county, state or nation location
    :return: strictness_params
    """
    if name_type == "town":
        return ["name_x=1_1&residence_x=_1-0", "name_x=s_s&residence_x=_1-0", "name_x=ps_ps&residence_x=_1-0",
                "name_x=ps_ps&residence_x=_1-1", "name_x=ps_ps&residence_x=_1-1-a"]
    elif name_type == "county":
        return ["name_x=1_1&residence_x=_1-0", "name_x=s_s&residence_x=_1-0", "name_x=ps_ps&residence_x=_1-0",
                "name_x=ps_ps&residence_x=_1-0-a", "name_x=ps_ps&residence_x=_1-1"]
    else:
        # name_type = state
        if state == 'NY':
            return ["name_x=1_1&residence_x=_1-0", "name_x=s_s&residence_x=_1-0", "name_x=ps_ps&residence_x=_1-0",
                    "name_x=ps_ps&residence_x=_1-0-a"]
        else:
            return ["name_x=1_1&residence_x=_1-0", "name_x=s_s&residence_x=_1-0", "name_x=ps_ps&residence_x=_1-0",
                "name_x=ps_ps&residence_x=_1-0"]


# In[6]:


def processLocationString(name_type, town, county, state, keep_county=True):
    """
    Convert our information on a geography into a well-formatted string
    :param name_type_fn: whether we have a town, county or a state
    :param town: town name, if exists
    :param county: county name, if exists
    :param state: state name
    :return:
    """
    if not keep_county and name_type != 'state':
        county = county.replace(" County", "").strip()

    if name_type == "town":
        return town + ", " + county + ", " + statedict[state]
    elif name_type == "county":
        return county + ", " + statedict[state]
    else:
        # name_type is state
        return statedict[state]


# In[7]:


# function that controls settings for strictness of search and returns final data for each individual
def findMatches(fn, ln, driver, search_town, search_county, search_state, name_type):
    """
    Function that controls settings for strictness of search and returns final data for each individual

    :param fn: first name
    :param ln: last name
    :param driver: selenium web scraper driver
    :param search_town: name of town we are searching for
    :param search_county: name of county we are searching for
    :param search_state: name of state we are searching for
    :param name_type: type of location given (town, county, state)
    :return: final data for each individual from ancestry database
    """
    # how many searches to conduct
    max_searchind = 4 if name_type != "state" else 3
    # navigate to original url
    search_ind = 0

    # navigate to initial url for person
    driver, url = navigateTo(fn, ln, driver, search_ind, search_town, search_county, search_state, name_type,
                             initial=True)
    time.sleep(1)

    # see if there are any matches using initial strict settings
    val, search_ind = listPeople(driver, search_ind, name_type)

    # if we have found a match or we have exhausted all possible matchings, exit while loop
    # finding a match will automatically make seach_ind = max_searchind
    while search_ind < max_searchind:
        search_ind += 1
        # navigate to url with new settings
        driver, url = navigateTo(fn, ln, driver, search_ind, search_town, search_county, search_state, name_type)
        time.sleep(1.5)
        val, search_ind = listPeople(driver, search_ind, name_type)

    # add last url used to data
    val['url'] = url
    return val


# In[8]:


# probably could amend this so that we don't have an "initial" setting, we just search for the location code for the particular location
def navigateTo(fn, ln, driver, search_ind, search_town, search_county, search_state, name_type_fn, initial=False):
    """
    Function that helps us navigate to the correct url for a particular name search, given the location as well as the iteration of the search (iteration will determine which index we use)

    :param fn: first name
    :param ln: last name
    :param driver: selenium web scraper driver
    :param search_ind: index of the search we are doing, deterines strictness of name and location suffix parameters
    :param search_town: town name
    :param search_county: county name
    :param search_state: state name
    :param name_type_fn: whether we are searching for a town, county or state
    :param initial: whether this is the first time we are doing this search
    :return: selenium web scraper driver and the url we navigated to
    """
    # replace spaces with + for url formatting
    fn = fn.replace(" ", "+")
    ln = ln.replace(" ", "+")

    # get name and location suffix parameters for search
    searchstr = searchLocationString(name_type, search_town, search_county, search_state)
    search_params = determineMatchList(name_type_fn, search_state)[search_ind]
    namesuffix = search_params.split("&")[0].replace("name_x=", "")
    locsuffix = search_params.split("&")[1].replace("residence_x=", "")

    # get location number for the particular location we are searching for
    if initial:
        # there are two formats for the location string, one with the word county in the county name and one without
        locationstr_keep = processLocationString(name_type, search_town, search_county, search_state, True)
        locationstr_disc = processLocationString(name_type, search_town, search_county, search_state, False)

        # see if there is a location string that we have a valid code for
        # by default, if there is no location string that we have a valid code for, we will use the location string with the county name
        # this is because we use the location string with the county name to search for the correct code
        if locationstr_disc in locationsuffix.keys():
            locationstr = locationstr_disc
        else:
            locationstr = locationstr_keep

        # if we have the location code, and this is the initial search, enter the necessary information
        if locationstr in locationsuffix.keys():
            locationnum = locationsuffix[locationstr]
            url = f"https://www.ancestrylibrary.com/search/collections/5058/?name={fn}_{ln}&name_x={namesuffix}&residence=_{searchstr}_{locationnum}&residence_x={locsuffix}"
            driver.get(url)
            time.sleep(3)
        else:
            # need to find the location code - we do this by doing a general search using the location and then obtaning the code from the search url
            driver.get('https://www.ancestrylibrary.com/search/collections/5058/')
            time.sleep(2)
            #val = driver.find_element(by = By.XPATH, value ="//*[@id=\"sfs_ContentBased\"]/div[1]/div/fieldset[1]/div[2]/label").get_attribute("for").split("Place_")[1]

            # try obtaining the code by using either the location string with the county name or the location string without the county name
            try:
                driver.find_element(by=By.XPATH, value=f"//*[@id=\"sfs__SelfResidencePlace\"]").send_keys(
                    locationstr_keep)
                time.sleep(2)
                driver.find_element(by=By.XPATH, value=f"//*[@id=\"sfs__SelfResidencePlaceAutocomplete0\"]").click()
                time.sleep(1)
                driver.find_element(by=By.XPATH, value=f"//*[@id=\"sfs__SelfResidencePlace\"]").send_keys(Keys.ENTER)
                time.sleep(2)
                currurl = driver.current_url
                code = currurl.split("usa_")[1]
                locationsuffix[locationstr] = code
            except:
                driver.get('https://www.ancestrylibrary.com/search/collections/5058/')
                time.sleep(3)
                driver.find_element(by=By.XPATH, value=f"//*[@id=\"sfs__SelfResidencePlace\"]").send_keys(
                    locationstr_disc)
                time.sleep(2)
                driver.find_element(by=By.XPATH, value=f"//*[@id=\"sfs__SelfResidencePlaceAutocomplete0\"]").click()
                time.sleep(1)
                driver.find_element(by=By.XPATH, value=f"//*[@id=\"sfs__SelfResidencePlace\"]").send_keys(Keys.ENTER)
                time.sleep(2)
                print(currurl)
                currurl = driver.current_url
                code = currurl.split("usa_")[1]
                locationsuffix[locationstr] = code

            # final url with all the necessary inputs
            url = f"https://www.ancestrylibrary.com/search/collections/5058/?name={fn}_{ln}&name_x={namesuffix}&residence=_{searchstr}_{code}&residence_x={locsuffix}"
            driver.get(url)
            time.sleep(3)
    else:
        # if we are not doing the initial search, we can just use the url that we have already obtained and then input the desired parameters
        currurl = driver.current_url
        url = currurl.split("&name_x")[0] + f"&name_x={namesuffix}" + "&residence=_" + currurl.split("&residence=_")[1].split("&residence_x=")[0] + f"&residence_x={locsuffix}"
    driver.get(url)

    return driver, url


# In[9]:


def listPeople(driver, search_ind, name_type):
    """
    Function that obtains data on individuals from an Ancestry.com search page

    :param driver: driver for selenium web scraper
    :param fn:
    :param ln:
    :param samelocation:
    :param expandGeography:
    :param expandNameMatch:
    :return:
    """

    max_searchind = 4 if name_type != "state" else 3

    info = dict()
    # if no matches found, loosen the restrictions on gegraphy and name
    try:
        count_text = driver.find_element(By.XPATH, "//*[@id=\"results-footer\"]/h3").text
        search_ind = max_searchind
    except:
        # we only have 4/5 search options
        if search_ind == max_searchind:
            info['Match Status'] = 'No Match'
            return info, search_ind
        else:
            return "continue searching", search_ind

    count = int(count_text.split(" of ")[1])
    # if multiple matches found, see if any of them are all in the same place
    # we can categorize this as a "location match"
    if count > 1:
        if count < 5:  # likelihood of same location for over 5 individuals = rare
            info['Match Status'] = f'{count} Potential Matches Found'
            for i in range(count):
                currurl = driver.current_url
                p_info = getInfo(driver, i)
                info[f'Match {i + 1}'] = p_info
                driver.get(currurl)
        else:
            info['Match Status'] = f'No Match: Too Many Potential Matches Found {count}'
        return info, search_ind
    # if only one name is found then we categorize this as a person match
    else:
        p_info = getInfo(driver, 0)
        info['Match Status'] = 'Complete Match'
        info[f'Match 1'] = p_info
        return info, search_ind


# In[10]:


def getInfo(driver, i):
    """
    Function that obtains data on an individual from an Ancestry.com search page

    :param driver: selenium driver
    :param i: which index on the search page to gather data for
    :return: dictionary of data for individual
    """
    time.sleep(1.5)
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, f"//*[@id=\"sRes-{i}\"]/td[1]/span[1]/a")))
    driver.find_element(By.XPATH, f"//*[@id=\"sRes-{i}\"]/td[1]/span[1]/a").click()
    print("clicked!")
    time.sleep(1.5)
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, f"//*[@id=\"recordServiceData\"]/tbody/tr[1]/th")))

    success = True
    ind = 1
    info = {}
    while success:
        try:
            key = driver.find_element(By.XPATH, f"//*[@id=\"recordServiceData\"]/tbody/tr[{ind}]/th").text.strip()
            val = driver.find_element(By.XPATH, f"//*[@id=\"recordServiceData\"]/tbody/tr[{ind}]/td").text.strip()
            info[key] = val
            ind += 1
        except:
            success = False
    return info


# In[11]:


def searchLocationString(name_type, town, county, state):
    """
    Function that creates the location string for the Ancestry.com search page
    :param name_type: type of name we are searching for (town, county, state)
    :param town: town name
    :param county: county name
    :param state: state name
    :return: location string
    """

    # county name should not have County in it, must be formatted in a certain way
    if not pd.isnull(county):
        county = county.replace('County', '').strip().replace(' ', '+').replace('\'', '+').lower()
    # connect different parts of name, add necessary suffixes
    if name_type == "town":
        return town.lower() + "-" + county + "-" + statedict[state].lower() + "-usa"
    elif name_type == "county":
        return county + "-" + statedict[state].lower() + "-usa"
    elif name_type == "state" or name_type == "state_flag":
        return statedict[state] + "-usa"
    else:
        return "usa"


# In[12]:


def addToResult(res, fn, ln, search_town, search_county, search_state, name_type):
    """
    Function that adds parameters to the result dictionary

    :param res: result dictionary
    :param fn: first name
    :param ln: last name
    :param search_town: town name
    :param search_county: county name
    :param search_state: state name
    :param name_type: type of name we are searching for (town, county, state)
    :return:
    """
    res['First Name'] = fn
    res['Last Name'] = ln
    res['Search Town'] = search_town
    res['Search County'] = search_county
    res['Search State'] = search_state
    res['Name Type'] = name_type
    return res


# In[13]:


def parseResult(res, df_list, match_list):
    """
    Function that parses the result dictionary and adds the results to df_list, match_list

    :param res: result dictionary
    :param df_list: dataframe that contains all of the people we searched for
    :param match_list: database of results from ancestry.com that people are linked to
    :return: df_list, match_list with res added in
    """

    # if there is at least one potential match, we want to see how many there are
    if 'No Match' not in res['Match Status']:
        # find number of matches
        i = 1
        pres = True
        while pres:
            try:
                res[f'Match {i}']
                i += 1
            except:
                pres = False
        # iterate through all matches, add the corresponding match information in res to match_list
        match_inds = []
        for j in range(1, i):
            match_list = pd.concat([match_list, pd.DataFrame(res[f'Match {j}'].copy(), index=[0])]).reset_index(
                drop=True)
            match_inds.append(str(match_list.shape[0] - 1))
            del res[f'Match {j}']
        res['Match Index'] = " | ".join(match_inds) if len(match_inds) > 1 else match_inds[0]
    # add person in res to df_list
    df_list = pd.concat([df_list, pd.DataFrame(res, index=[0])]).reset_index(drop=True)

    return df_list, match_list


# In[14]:


def verifyNoMatch(driver, res):
    """
    Function that verifies that there is no match for a person on ancestry.com

    :param driver: selenium web scraper driver
    :param res: url of our research result
    :return: whether there is actually a result
    """
    driver.get(res['url'])
    time.sleep(2)
    try:
        driver.find_element(By.XPATH, "//*[@id=\"results-footer\"]/h3").text
        return True
    except:
        return False


# ## Run the Scraper

# In[15]:


# structures that store our data
df_list_og = pd.DataFrame(columns = ['First Name', 'Last Name', 'Search Town', 'Search County', 'Search State', 'Name Type', 'url', 'Match Index', 'Match Status'])
match_list_og = pd.DataFrame(columns = ['Name', 'Home in 1790 (City, County, State)', 'Free White Persons - Males - 16 and over', 'Free White Persons - Females', 'Number of Household Members'])
locationsuffix = dict()


# In[16]:


locationsuffix['Littleton, Middlesex County, Massachusetts'] = 4534


# In[224]:


# iterate through all individuals and try to find ancestry.com data for them
# set selenium driver
driver = webdriver.Safari(executable_path=r'/usr/bin/safaridriver')  #set driver
# login details for uchicago server authentication
if user == "Chris":
    file = pd.read_csv('~/Desktop/login_details.txt')
# get login information
username = file.columns[0]
password = file[username].tolist()[0]
# navigate to url
driver.set_window_size(1000, 700)
driver.get("http://www.lib.uchicago.edu/h/ancestry")
# login to uchicago server
WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.ID, "okta-signin-username"))).send_keys(username)
time.sleep(1)
driver.find_element(by=By.ID, value="okta-signin-password").send_keys(password)
time.sleep(5)
# click on login button
driver.find_element(by=By.ID, value="okta-signin-submit").click()  #sign in
# click on duo authentication button
time.sleep(10)
WebDriverWait(driver, 100).until(
    EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//*[@id=\"form62\"]/div/div[2]/iframe")))
WebDriverWait(driver, 100).until(
    EC.element_to_be_clickable((By.XPATH, "//*[@id=\"auth_methods\"]/fieldset/div[1]/button"))).click()

# wait for page to load
time.sleep(17)

# specify name match and location match options
for index in final_name_list.index:
    """if index < 4401: #3606:
        continue"""
    # save our data after each run
    df_list_og.to_csv('scrape_tools/scrape_ids_prelim.csv')
    match_list_og.to_csv('scrape_tools/scrape_results_prelim.csv')

    # obtain attributes of data we want to use to search
    fn = final_name_list.loc[index, 'Fn_Fix']
    ln = final_name_list.loc[index, 'Ln_Fix']
    search_town = final_name_list.loc[index, 'new_town']
    search_county = final_name_list.loc[index, 'county']
    search_state = final_name_list.loc[index, 'new_state']
    name_type = final_name_list.loc[index, 'name_type']

    if name_type != "country":
        # transform information into searchable params
        searchparams = determineMatchList(name_type, search_state)
        location = processLocationString(name_type, search_town, search_county, search_state)
        # distinguish between names that correspond to multiple real names vs. just one name
        if type(fn) != str:
            fn = ""
        name = fn + " " + ln
        print(f"Searching for {name} that lived in {location}")

        # if matching one time fails, retry (up to 8 times)
        # when matching fails its likely a bug
        match = False
        tries = 0
        while not match and tries < 8:
            try:
                res = findMatches(fn, ln, driver, search_town, search_county, search_state, name_type)
                while res['Match Status'] == 'No Match' and verifyNoMatch(driver, res):
                    print("Need to obtain information again")
                    res = findMatches(fn, ln, driver, search_town, search_county, search_state, name_type)
                match = True
            except:
                print("trying again")
                tries += 1
                pass

        print(tries, res)
        # transform our result and add it to our dataframes
        res = addToResult(res, fn, ln, search_town, search_county, search_state, name_type)
        df_list_og, match_list_og = parseResult(res, df_list_og, match_list_og)


# ## Clean Scraped Data

# In[18]:


# create copies of our dataframe before we edit them
match_list = match_list_og.copy()
df_list = df_list_og.copy()


# In[19]:


# correct matches for certain people who we know for sure the match is wrong for
df_list.loc[df_list[df_list['First Name'] + df_list['Last Name'] == 'AnnCook'].index,
               ['Match Index', 'Match Status']] = [np.nan, 'No Match']
df_list.loc[df_list[df_list['First Name'] + df_list['Last Name'] == 'AnnFromberger'].index,
               ['Match Index', 'Match Status']] = [np.nan, 'No Match']
df_list.loc[df_list[df_list['First Name'] + df_list['Last Name'] == 'JaneOlmsted'].index,
               ['Match Index', 'Match Status']] = [np.nan, 'No Match']

# there are some places where we have duplicates, drop these
# particular idiosyncracy related to our matching this time
ben_bosw_drop = df_list[df_list['First Name'] + " " + df_list['Last Name'] + df_list['Match Status'] == "Benjamin Bosworth3 Potential Matches Found"].index
df_list.drop(ben_bosw_drop, inplace=True)

rwaterman = df_list[df_list['First Name'] + " " + df_list['Last Name'] + df_list['Match Status'] == "Richard WatermanNo Match"].index
df_list.drop(rwaterman, inplace=True)

warnold = df_list[df_list['First Name'] + " " + df_list['Last Name'] + df_list['Match Status'] == "William ArnoldNo Match"].index
df_list.drop(warnold, inplace=True)

wpotter = df_list[df_list['First Name'] + " " + df_list['Last Name'] + df_list['Match Status'] == "William PotterNo Match"].index
df_list.drop(wpotter, inplace=True)


# In[20]:


# remove indices from match dataframe if that match is not in our dataframe
inds = df_list['Match Index'].apply(lambda x: str(x).split(" | ") if not pd.isnull(x) else [0]).explode().apply(lambda x: int(x)).drop_duplicates().tolist()
match_list = match_list.loc[inds]


# In[21]:


# make manual changes to some entries where the scraper bugged out
match_list.loc[match_list[match_list['Home in 1790 (City, County, State)'].isnull()].index, ['Home in 1790 (City, County, State)', 'Free White Persons - Females', 'Number of Household Members']] = ['Philadelphia City, Philadelphia, Pennsylvania', 2, 2]
match_list.loc[match_list[match_list['Name'].apply(lambda x: 'Rebecca Ha' in x)].index, 'Home in 1790 (City, County, State)'] = 'Sherburn, Nantucket, Massachusetts, USA'


# In[22]:


# Reformat names properly - some have brackets, too many new line or tab characters
brack_ind = match_list[match_list['Name'].apply(lambda x: "[" in x and "\n" not in x)].index
match_list.loc[brack_ind, 'Name'] = match_list.loc[brack_ind, 'Name'].apply(
    lambda x: x.replace("[", "").replace("]", ""))
space_ind = match_list[match_list['Name'].apply(lambda x: '\n' in x)].index
match_list.loc[space_ind, 'Name'] = match_list.loc[space_ind, 'Name'].apply(
    lambda x: x.replace('\n', ' ').replace('\t', '').replace('[', '| ').replace(']', '').replace('  ', ''))

# Add information about the town, county, state and type of our match
match_list['Match Type'] = match_list['Home in 1790 (City, County, State)'].apply(
    lambda x: 'town' if len(x.split(", ")) == 3 else 'county' if len(x.split(", ")) == 2 else 'state' if len(
        x.split(", ")) == 1 else 'state')
match_list['Match Town'] = match_list.apply(
    lambda x: x['Home in 1790 (City, County, State)'].split(", ")[0] if x['Match Type'] == 'town' else np.nan, axis=1)
match_list['Match County'] = match_list.apply(
    lambda x: x['Home in 1790 (City, County, State)'].split(", ")[1] + " County" if x['Match Type'] == 'town' else
    x['Home in 1790 (City, County, State)'].split(", ")[0] + " County" if x['Match Type'] == 'county' else np.nan,
    axis=1)
match_list['Match State'] = match_list.apply(lambda x: x['Home in 1790 (City, County, State)'].split(", ")[-1], axis=1)


# In[23]:


# manually edit two entry types since they cannot be parsed by our earlier commands
match_list.loc[match_list[match_list['Home in 1790 (City, County, State)'] == 'Hopewell, Newton, Tyborn, and Westpensboro, Cumberland, Pennsylvania'].index, ['Match Town', 'Match County', 'Match State', 'Match Type']] = ['Hopewell, Newton, Tyborn and Westpensboro', 'Cumberland County', 'Pennsylvania', 'town']
match_list.loc[match_list[match_list['Home in 1790 (City, County, State)'] == 'Fannet, Hamilton, Letterkenney, Montgomery, and Peters, Franklin, Pennsylvania'].index, ['Match Town', 'Match County', 'Match State', 'Match Type']] = ['Fannet, Hamilton, Letterkenney, Montgomery and Peters', 'Franklin County', 'Pennsylvania', 'town']


# ## Reset Index

# In[24]:


# next, we want to remove entries in match_list that are duplicated, and create a dictionary that maps the old indices in df_list to the new indices, after we drop duplicates in match_list

# save old index
match_list['index_old'] = match_list.index
# drop duplicates, create temporary index column
match_list_no_dup = match_list.drop_duplicates(subset=[ele for ele in match_list.columns if ele != 'index_old'])
match_list_no_dup.rename({'index_old': 'index_temp'}, axis=1, inplace=True)

# create mapping between old index, and temporary new index
# the temporary new index removes indices of repeated values without renumbering anything
match_dict_df = pd.merge(match_list.reset_index(),
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
df_list['Match Index'] = df_list['Match Index'].apply(
    lambda x: tNameList([str(match_dict[int(ele)]) for ele in x.split(' | ')]) if not pd.isnull(x) else x)
# change match_list dataframe so that it removes duplicates and is indexed by the new index method
match_list = pd.merge(match_list_no_dup, gen_newind)
match_list['index_new'] = match_list['index_new'].apply(lambda x: str(x))


# In[25]:


# correct times where two people matched to the same individual but they have the same info/are likely the same
# caused by our reindex scheme, does not occur frequently
double_rep_ind = df_list[df_list.apply(lambda x: (not pd.isnull(x['Match Index']) and ' | ' not in x['Match Index'])
                                                 and x['Match Status'] not in ['Complete Match', 'Poor Match'],
                                       axis=1)].index
df_list.loc[double_rep_ind, 'Match Status'] = 'Complete Match'


# In[235]:


# export our results
pd.merge(final_name_list, df_list.drop_duplicates(),
         how='left',
         left_on=['Fn_Fix', 'Ln_Fix', 'new_town', 'county', 'new_state', 'name_type'],
         right_on=['First Name', 'Last Name', 'Search Town', 'Search County', 'Search State', 'Name Type']).to_csv('scrape_tools/name_list_scraped.csv')

df_list.to_csv('scrape_tools/scrape_ids.csv')
match_list.to_csv('scrape_tools/scrape_results.csv')


# In[19]:


pd.read_csv('scrape_tools/scrape_results.csv', index_col = 0).loc[[0, 8, 9]]


# In[20]:


import pandas as pd
print(pd.read_csv('scrape_tools/name_list_scraped.csv', index_col = 0).loc[[1, 9, 21]][['Fn_Fix', 'Ln_Fix', 'new_town', 'county', 'new_state', 'country','name_type', 'Match Index', 'Match Status']].to_markdown())
print(pd.read_csv('scrape_tools/scrape_results.csv', index_col = 0).loc[[0, 8, 9]][['Name', 'Home in 1790 (City, County, State)','Free White Persons - Males - 16 and over','Free White Persons - Females', 'Number of Household Members','Free White Persons - Males - Under 16','Number of Slaves','Number of All Other Free Persons','Match Type']].to_markdown())

