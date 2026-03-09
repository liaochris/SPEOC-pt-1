#!/usr/bin/env python
# coding: utf-8

# ## Ancestry Seach 

# <b>Goal: </b>Multiple different spellings of a name can be referring to the same identity. We will use a phonetics library and Ancestry to fix this. An example: ```David Schaffer``` and ```David Schafer``` from `MA`. 
# 
# <b>Steps: </b>
# 1. Login to Emory's Ancestry subscription 
# 2. Iterate through ```agg_debt```, through each debt entry. 
# 3. Use a combination of phonetics fuzzy string matching and normal fuzzy string matching to determine if two names from a state are similar.  
# 4. Search each name in Ancestry: Edit URL (state and person's name). 
# 5. Check if there are any results for both person's name:
#     - Yes: Check if one spelling of the name appears for both individuals (that's most likely the correct spelling of that name) 
#     - No: Leave entries as two separate entries. 
# 6. Record name change in ```fixes``` list (save ```fixes``` as ```out.csv``` too). 
# 7. Run ```agg_debt``` through ```fixes```, making changes as necessary. 
# 8. Save ```agg_debt``` as a new .csv file.
# 
# <b style="color: red;">Note: Runtime is long. This is due to the fact there are over 200,000 debt entries and accessing Ancestry takes time too. </b>

# In[ ]:


# import necessary fuzzy string libraries 
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.expected_conditions import element_to_be_clickable, presence_of_element_located
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from phonetics import metaphone
from rapidfuzz import fuzz
from joblib import Parallel, delayed, cpu_count
from itertools import zip_longest
import time 
import getpass
import pickle
from pathlib import Path
import pandas as pd
import numpy as np
import ast

INDIR_PRESCRAPE = Path("output/derived/prescrape/pre1790")
OUTDIR = Path("output/derived/postscrape/pre1790")


# In[ ]:


agg_debt = pd.read_csv(INDIR_PRESCRAPE / 'pre1790_cleaned.csv')


# In[ ]:


# Find number of unique individuals in `agg_debt`
agg_debt.groupby(['to whom due | first name', 'to whom due | last name']).ngroups 


# In[ ]:


agg_debt['to whom due | first name'] = agg_debt['to whom due | first name'].astype(str)
agg_debt['to whom due | last name'] = agg_debt['to whom due | last name'].astype(str)


# In[ ]:


name_changes = pd.read_csv(INDIR_PRESCRAPE / 'check/name_changes_list.csv')


# In[ ]:


agg_debt.head()


# In[ ]:


# Check to make sure pierce certificate first name and last name columns are properly swapped
agg_debt.loc[agg_debt['org_file'] == 'Pierce_Certs_cleaned_2019.xlsx'].head()


# In[ ]:


name_changes.tail()


# In[ ]:


# Options
options = Options()
options.add_argument('--headless')
options.add_argument("--window-size=1000,1000")
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('--no-sandbox')   


# In[ ]:


agg_debt.state.unique()


# In[ ]:


# Voter records and censuses available for every state 
records = {
    'nh':['https://www.ancestrylibrary.com/search/collections/5058/'],
    'nj':['https://www.ancestrylibrary.com/search/collections/2234/', 
          'https://www.ancestrylibrary.com/search/collections/3562/'],
    'ny':['https://www.ancestrylibrary.com/search/collections/5058/'],
    'ma':['https://www.ancestrylibrary.com/search/collections/5058/'], 
    'ct':['https://www.ancestrylibrary.com/search/collections/5058/'], 
    'va':['https://www.ancestrylibrary.com/search/collections/2234/', 
         'https://www.ancestrylibrary.com/search/collections/3578/'], 
    'pa':['https://www.ancestrylibrary.com/search/collections/2702/',
         'https://www.ancestrylibrary.com/search/collections/2234/',
         'https://www.ancestrylibrary.com/search/collections/3570/'],
    'md':['https://www.ancestrylibrary.com/search/collections/3552/'],
    'nc':['https://www.ancestrylibrary.com/search/collections/3005/', 
         'https://www.ancestrylibrary.com/search/collections/2234/'],
    'ga':['https://www.ancestrylibrary.com/search/collections/2234/'],
    'ri':['https://www.ancestrylibrary.com/search/collections/3571/']
}

# Ancestry has unique urls for each state
residence_urls = {
    'nh':'_new+hampshire-usa_32',
    'nj':'_new+jersey-usa_33', 
    'ny':'_new+york-usa_35',
    'ma':'_massachusetts-usa_24',
    'ct':'_connecticut-usa_9',
    'va':'_virginia-usa_49', 
    'pa':'_pennsylvania-usa_41',
    'md':'_maryland-usa_23',
    'nc':'_north+carolina-usa_36',
    'ga':'_georgia-usa_13',
    'ri':'_rhode+island-usa_42'
}


# In[ ]:


# Remove 'cs' (congress) and 'f' (foreign officers); these are not state, but specific regiments / types of officers
agg_debt_copy = agg_debt[(agg_debt['state'] != 'cs') & (agg_debt['state'] != 'f') & (agg_debt['state'] != 'de')]


# In[ ]:


# Store all similar_names files as Pandas Dataframes
similar_names_dfs = {}
for state in agg_debt_sp.groups:
    similar_names_dfs[state] = pd.read_csv(INDIR_PRESCRAPE / 'similar_names/similar_names_' + state + '.csv')

print(len(similar_names_dfs))


# In[ ]:


netid_xpath = '/html/body/div[1]/div[2]/section/div[1]/div/form/fieldset/div[1]/input'
password_xpath = '/html/body/div[1]/div[2]/section/div[1]/div/form/fieldset/div[2]/input'
login_btn0_xpath = '/html/body/main/div/div/div/a'
login_btn1_xpath = '/html/body/div[1]/div[2]/section/div[1]/div/form/fieldset/div[3]/button'

# Ask for a password and username 
username = input('username: ')
password = getpass.getpass(prompt='password: ')

driver_objs = {}

# Create a new driver object for each state
for i in range(cpu_count()):
    webdriver_obj = webdriver.Chrome(service=Service(executable_path="chromedriver.exe"), options=options)
    driver_objs[i] = (webdriver_obj, WebDriverWait(webdriver_obj, 30))

'''
# create a new wait object for each state
for st in cpu_count:
    webdriver_obj = driver_objs[st][0]
    driver_objs[st].append(WebDriverWait(webdriver_obj, 30))
'''
    
# For each driver object, access emory's ancestry's subscription 
for i in range(cpu_count()):
    webdriver_obj = driver_objs[i][0]
    wait_obj = driver_objs[i][1]
    
    # Go to Emory's library 
    webdriver_obj.get('https://guides.libraries.emory.edu/ALE')
    wait_obj.until(element_to_be_clickable((By.XPATH, login_btn0_xpath))).click()
    
    # Input login information and click 'login'
    netid_input = wait_obj.until(element_to_be_clickable((By.XPATH, netid_xpath)))
    netid_input.click()
    netid_input.send_keys(username)
    pass_input = wait_obj.until(element_to_be_clickable((By.XPATH, password_xpath)))
    pass_input.click()
    pass_input.send_keys(password) 
    wait_obj.until(element_to_be_clickable((By.XPATH, login_btn1_xpath))).click()
    time.sleep(1)
    
    webdriver_obj.get('https://www.ancestrylibrary.com/search/collections/5058/')
    print(webdriver_obj.current_url)
    
    print(webdriver_obj)


# In[ ]:


print(len(driver_objs))


# ## Accessing Ancestry

# In[ ]:


# When running this code for the first time, set all variables equal to '[]'

'''
ancestry_name_changes = []
rerun_rows = []
checked = []
fixes = []
'''


# In[ ]:


get_ipython().run_line_magic('store', '-r ancestry_name_changes')
get_ipython().run_line_magic('store', '-r rerun_rows')
get_ipython().run_line_magic('store', '-r checked')
get_ipython().run_line_magic('store', '-r fixes')


# In[ ]:


def access_ancestry(row0, state, driver, wait):
    fn0 = str(row0['to whom due | first name'])
    ln0 = str(row0['to whom due | last name'])
    matches = ast.literal_eval(row0['matches'])
    name0 = fn0 + ' ' + ln0

    for match in matches:
        row1 = agg_debt.loc[[match[2]]] 
        fn1 = str(row1['to whom due | first name'].values[0])
        ln1 = str(row1['to whom due | last name'].values[0])
        name1 = fn1 + ' ' + ln1
        if ((name0, name1, state) not in checked and (name1, name0, state) not in checked): 
            search_ancestry(fn0, ln0, fn1, ln1, row0, row1, state, driver, wait)
            checked.append((name0, name1, state))
            get_ipython().run_line_magic('store', 'checked')


# In[ ]:


# Look up both names in Ancestry's database
def search_ancestry(fn0, ln0, fn1, ln1, row0, row1, state, driver, wait):
    name0 = fn0 + ' ' + ln0
    name1 = fn1 + ' ' + ln1
    
    # Loop through state urls 
    for url in records[state]:        
        try:
            # Search for person 0
            url0 = url + '?name=' + fn0 + '_' + ln0 + '&name_x=ps&residence=1780' + residence_urls[state] + '&residence_x=10-0-0_1-0'
            driver.get(url0) 
            # Results were found for person 0
            try:
                # Use class_name to find result text
                result0 = wait.until(presence_of_element_located((By.CLASS_NAME, 'srchHit'))).text
            # No results were found; Keep entries separate  
            except:
                result0 = ''
            
            # Search for person 1
            url1 = url + '?name=' + fn1 + '_' + ln1 + '&name_x=ps&residence=1780' + residence_urls[state] + '&residence_x=10-0-0_1-0'
            driver.get(url1) 
            # results were found for person1
            try: 
                # use class_name to find result text
                result1 = wait.until(presence_of_element_located((By.CLASS_NAME, 'srchHit'))).text
            # no results were found; keep entries separate
            except:
                result1 = ''    

            '''
            compare results:
            if both results are empty, do not add to fixes dict 
            if both results are different, do not add to fixes dict
            if both results are the same, add to fixes dict
                find correct name
                if name0 = result0 and result1 : {name1 : name0}
                if name1 = result1 and result0 : {name0 : name0} 
            '''
            
            print('---------------------------+')
            if result0 == result1 and result0 != '' and result1 != '':
                if name0 == result0 and name0 == result1: # name0 must be the correct version of the name 
                    # record change
                    title1 = row1['to whom due | title']
                    org_file1 = row1['org_file']
                    org_index1 = row1['org_index'] 
                    ancestry_name_changes.append([title1, title1, fn1, ln1, fn0, ln0, 6, org_file1, org_index1, state])
                    get_ipython().run_line_magic('store', 'ancestry_name_changes')
                    fixes.append({fn1: fn0, ln1: ln0, 'state': state})
                    get_ipython().run_line_magic('store', 'fixes')

                elif name1 == result0 and name1 == result1: # name1 must be the correct version of the name 
                    # record change
                    title0 = row0['to whom due | title']
                    org_file0 = row0['org_file']
                    org_index0 = row0['org_index'] 
                    ancestry_name_changes.append([title0, title0, fn0, ln0, fn1, ln1, 6, org_file0, org_index0, state])
                    get_ipython().run_line_magic('store', 'ancestry_name_changes')
                    fixes.append({fn0: fn1, ln0: ln1, 'state': state})
                    get_ipython().run_line_magic('store', 'fixes')

            print('Summary')
            print('name0=' + str(name0))
            print('name1=' + str(name1))
            print('url-0=' + str(url0))
            print('url-1=' + str(url1))
            print('result0=' + str(result0))
            print('result1=' + str(result1))
            print('state=' + str(state))

            '''
            print('fn0=' + str(fn0))
            print('ln0=' + str(ln0))
            print('fn1=' + str(fn1))
            print('ln1=' + str(ln1))
            '''
            print('index=' + str(row0['index']))
            print('rerun_rows length=' + str(len(rerun_rows)))
            print('name_changes length=' + str(len(ancestry_name_changes)))
            print('fixes length=' + str(len(fixes)))
            '''
            print('file_name0=' + str(org_file0))
            print('file_name1=' + str(org_file1))
            '''
            print('---------------------------+')
        
        # there was error trying to access ancestry's records
        except Exception as e:
            print('---------------------------+')
            print('Error')
            print(e)
            '''
            print('name0=' + str(name0))
            print('name1=' + str(name1))
            print('title1=' + str(type(title1)))
            print('title0=' + str(type(title0)))
            print('title1=' + str(title1))
            print('title0=' + str(title0))
            print('org_file1=' + str(org_file1))
            print('org_file0=' + str(org_file0))
            print('index=' + str(index))
            '''
            print('---------------------------+')
            if (row0, row1) not in rerun_rows:
                rerun_rows.append((row0, row1)) 
                get_ipython().run_line_magic('store', 'rerun_rows')


# In[ ]:


print(len(ancestry_name_changes))
print(len(rerun_rows))


# In[ ]:


# Merge all the separate similar_names files into one larger DataFrame
similar_names = []
for state in agg_debt_sp.groups:
    similar_names.append(similar_names_dfs[state])
similar_names_df = pd.concat(similar_names)
print(len(similar_names_df))


# In[ ]:


def ancestry_wrap(similar_names, driver_wait):    
    similar_names.apply(lambda row0: access_ancestry(row0, row0['state'], driver_wait[0], driver_wait[1]), axis=1) 


# In[ ]:


df_split = np.array_split(similar_names_df, cpu_count())  
print(len(df_split))

# Initialize a parallelization job 
ancestry_calls = [delayed(ancestry_wrap)(df_split[i], driver_objs[i]) for i in range(7)]
results = Parallel(n_jobs=-1, backend="threading")(ancestry_calls) 


# In[ ]:


# Due to the number of entries in Pennsylvania, I decided to parallelize on PA's data only. 
split_pa = np.array_split(similar_names_dfs['pa'], cpu_count())
print(len(split_pa))


# In[ ]:


# Initialize a parallelization job 
ancestry_calls = [delayed(ancestry_wrap)(split_pa[i], driver_objs[i]) for i in range(cpu_count())]
results = Parallel(n_jobs=-1, backend="threading")(ancestry_calls) 


# In[ ]:


# Store the `ancestry_name_changes` list as a Pandas DataFrame
ancestry_df = pd.DataFrame(ancestry_name_changes)
# Store DataFrame as a .csv file 
ancestry_df.to_csv(OUTDIR / 'ancestry_name_changes.csv')


# ## Cleaning Name Changes

# In[ ]:


# Remove duplicates
print(len(ancestry_name_changes))
res = []
checked = []
for row in ancestry_name_changes:
    if (row[2], row[3], row[4], row[5], row[9]) not in checked:
        res.append(row)
        checked.append((row[2], row[3], row[4], row[5], row[9]))

print(len(res))


# In[ ]:


# Remove metadata 
for row in res:
    if (type(row[0]) == pd.core.series.Series and type(row[1]) == pd.core.series.Series and type(row[7]) == pd.core.series.Series and
       type(row[8]) == pd.core.series.Series):
        row[0] = row[0].values[0]
        row[1] = row[1].values[0]
        row[7] = row[7].values[0]
        row[8] = row[8].values[0]


# In[ ]:


print(res[2])


# In[ ]:


# Standardize datatypes for each row in each column
for row in res:
    row[2] = str(row[2])
    row[3] = str(row[3])
    row[4] = str(row[4])
    row[5] = str(row[5])
    row[6] = int(row[6])
    row[7] = str(row[7])
    row[8] = int(row[8])
    row[9] = str(row[9])


# In[ ]:


print(res[2])


# In[ ]:


ancestry_name_changes = res
# Store the `fixes` dictionary as a Pandas DataFrame
ancestry_df = pd.DataFrame(ancestry_name_changes)
ancestry_df.columns = ['Old Title', 'New Title', 'Old First Name', 'Old Last Name', 'New First Name', 'New Last Name', 
                       'Obj. Num.', 'Original File', 'Original Index', 'State']
# Store DataFrame as a .csv file 
ancestry_df.to_csv(OUTDIR / 'ancestry_name_changes_clean.csv')


# ## Add Ancestry Name Changes to the Name Changes Table

# In[ ]:


name_changes.drop(columns=['Unnamed: 0'], inplace=True)


# In[ ]:


name_changes.head()


# In[ ]:


# Add Ancestry name changes to name_changes file 
def add_changes(title_org, title_new, fn_org, ln_org, fn_new, ln_new, case, file, index):
    new_row = [title_org, title_new, fn_org, ln_org, fn_new, ln_new, case, file, index]
    name_changes.loc[len(name_changes.index)] = new_row


# In[ ]:


# Add Ancestry name changes to name_changes file 
for row in res:
    add_changes(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]) 


# In[ ]:


name_changes.tail()


# In[ ]:


# Save name_changes 
name_changes.to_csv(OUTDIR / 'name_changes_david.csv')


# ## Create a Final Debt Table

# In[ ]:


def fix_names(row):
    search_res = ancestry_df.loc[(ancestry_df['Old First Name'] == row['to whom due | first name']) & (ancestry_df['Old Last Name'] == row['to whom due | last name']) & (ancestry_df['State'] == row['state'])]
    if len(search_res != 0): 
        print(row['to whom due | first name'])
        print(row['to whom due | last name'])
        row['to whom due | first name'] = search_res['New First Name']
        row['to whom due | last name'] = search_res['New Last Name']
        print('+------------------+')
        print(row['to whom due | first name'])
        print(row['to whom due | last name'])
    return row


# In[ ]:


agg_debt.head()


# In[ ]:


print(type(agg_debt))


# In[ ]:


agg_debt = agg_debt.apply(lambda row: fix_names(row), axis=1)


# In[ ]:


agg_debt.to_csv(OUTDIR / 'final_agg_debt_cleaned.csv')

