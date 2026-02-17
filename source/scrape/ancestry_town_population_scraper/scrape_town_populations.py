#!/usr/bin/env python
# coding: utf-8

# In[1]:


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import element_to_be_clickable, presence_of_element_located
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import csv 
import pandas as pd
import time
import math


# In[2]:


# options
options = Options()
options.add_argument('--headless')
options.add_argument("--window-size=1000,1000")
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('--no-sandbox')   


# # Populations of Towns

# <font size="4"> The goal is to find the total population of every town in *final_data_CD.csv.* </font> <br>
# * **Input**
#     * ```final_data_CD.csv``` <br>
#        - This contains the continental debt held by individuals. For this particular project, we only care about the towns that these individuals are from. </a><br>
# * **Output**
#     * ```town_pops_clean.csv``` <br>
#        - This file will contain the populations of every town. 

# In[35]:


cd_df = pd.read_csv("final_data_CD.csv")
towns = cd_df[['Group State', 'Group County', 'Group Town']].drop_duplicates().dropna().reset_index()
towns.drop(columns={"index"}, inplace=True) 
print(towns)


# In[36]:


# drop states where census data ancestry does not have records for: VA, GA, NJ, DE
towns_c = towns.copy()
towns = towns.drop(towns[towns['Group State'].isin(['VA', 'GA', 'NJ', 'DE'])].index)
towns_d = towns_c[~towns_c.index.isin(towns.index)]
print(towns_d)


# In[3]:


# dictionary of state codes to actual state names (avoids potential errors)
codes = {
    'CT':'Connecticut',
    'ME':'Maine',
    'MD':'Maryland',
    'MA':'Massachusetts',
    'NH':'New Hampshire',
    'NY':'New York',
    'NC':'North Carolina',
    'PA':'Pennsylvania',
    'RI':'Rhode Island',
    'SC':'South Carolina',
    'VT':'Vermont',
    'VA':'Virginia',
    'GA':'Georgia',
    'NJ':'New Jersey',
    'DE':'Deleware'
}


# In[4]:


# handle naming exceptions
exceptions = {
    'Philadelphia County':'Philadelphia',
    'Charleston County':'Charleston',
    'New Haven County':'New Haven'
}


# ## Accessing Ancestry

# 1. Access the 1790 census on Ancestry.com using the Selenium library. 
# 2. Handle county names. Some county names have '[county name] County County'.
# 3. Access searchbar using Selenium. Selenium inputs [town, county, state, USA] into searchbar. 
# 4. Selenium clicks on the "Search" button and waits for 0.75 seconds. 
# 5. Once new webpage is loaded, ```&event_x=0-0-0_1-0```, is added to the current url. This restricts the search only to the town and excludes surrounding counties/towns. 
# 6. Selenium finds the total number of results, which corresponds to the population of the town. This population is added to the ```town_pops``` dictionary. If there are no results for that town, 'NR' is added to the dictionary instead. 
# 7. Steps 1-6 are repeated for every town. 
# 
# <span style="color: red;">**Note: Runtime will be long. There were approximately ~400 unique towns.**</span>

# In[5]:


def ancestry(error_handling, towns_l):
    town_pops = {} # dictionary of all the populations of each town 
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 30)
    census_url = "https://www.ancestry.com/search/collections/5058/"
    for town in towns_l:
        # handle '[name] county county'

        if not error_handling:
            county = town[2][:-7].replace(' County', '')
            loc_add = town[3] + ", " + county + ", " + codes[town[1]] + ", USA "
        else:
            county = town[2]
            loc_add = town[3] + ", " + county + ", " + town[1] + ", USA "

        try:
            # open 1790 census 
            try:
                driver.get(census_url)
            except:
                driver.close()
                driver.get(census_url)   

            # handle some exceptions to county names 
            if county in exceptions:
                county = exceptions[county]

            print("-------------------------")
            print(loc_add) ## 

            # wait until event searchbar is visible, then click on it: handles error i noticed
            xpath = "/html/body/div[3]/div/div/div/div/section/div/div/div/div/div/form/div[1]/div/fieldset[2]/div[2]/div/input"
            try:
                wait.until(element_to_be_clickable((By.XPATH, xpath))).click()
            except: # mostly to handle timeout exceptions: close tab and try again
                driver.close()
                driver.get(census_url)
                time.sleep(0.25)
                wait.until(element_to_be_clickable((By.XPATH, xpath))).click()

            input_t = driver.find_element(By.XPATH, xpath)
            input_t.send_keys(loc_add)
            time.sleep(0.75)

            # click on search button 
            wait.until(element_to_be_clickable((By.XPATH, "/html/body/div[3]/div/div/div/div/section/div/div/div/div/div/form/div[1]/div/div[9]/div[1]/input"))).click()
            time.sleep(0.75)

            # add restrictions: we want exact town population
            print(driver.current_url) ##
            driver.get(driver.current_url + "&event_x=0-0-0_1-0")

            # check if town is correct: handles error i noticed
            title_pl = wait.until(presence_of_element_located((By.XPATH, "//*[@id='refineView']/form/div[3]/div/div[1]/div"))).get_attribute("title")
            if (title_pl + " " == loc_add):
                # add to town_pops 
                try:
                    pop = driver.find_element(By.CLASS_NAME, "resultsLabel")
                    town_pops[loc_add] = int(pop.text.split("of")[1].replace(',','')) 
                except NoSuchElementException:
                    town_pops[loc_add] = "NR"
            else:

                print("Titles don't match")
                print("title on page = " + title_pl)
                town_pops[loc_add] = "NR"

            print(town_pops[loc_add]) ##
            print(len(town_pops)) ##
            print(driver.current_url) ##
            print("-------------------------")
            #driver.close() # close current tab 
            #driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options) # restart chrome 
            #wait = WebDriverWait(driver, 30)
        except Exception as e:
            print("___________________________________")
            print("ERROR! Moving swiftly to next town")
            print(e)
            print("___________________________________")
            town_pops[loc_add] = 'ER'
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options) # restart chrome 
            wait = WebDriverWait(driver, 30)
            continue
    
    return town_pops


# In[ ]:


town_pops = ancestry(False, towns.values.tolist())


# In[218]:


# save town_pops dictionary as a csv file 
df = pd.DataFrame.from_dict(town_pops, orient="index")
df.to_csv("town_pops.csv")
df = pd.read_csv("town_pops.csv", index_col=0)
print(df)
# printing result


# ## Fix Formatting

# Why? As of right now, there are only two columns. The first column has the location, which includes the town, county, state, and country all in one cell. This is not easy to read. Therefore, town, county, state, and country must become their own columns. The next column has the population. There are no column titles either. The code below fixes these issues. 

# In[27]:


# read csv 
towns_df = pd.read_csv("town_pops_2.csv")

# split location name into multiple columns 
towns_df = towns_df.assign(**towns_df['Unnamed: 0'].str.split(', ', expand=True).add_prefix('Info_'))

# rename columns
towns_df.rename(columns={'0':'population', 'Info_0':'city', 'Info_1':'county', 
                         'Info_2':'state', 'Info_3':'country'}, inplace=True)

# remove last three columns and original location column
towns_df.drop(columns={"Unnamed: 0"}, inplace=True)

# reorder columns
towns_df = towns_df[['city', 'county', 'state', 'country', 'population']]
print(towns_df)

towns_df.to_csv("town_pops_clean_2.csv")


# ## Handle Mistakes

# Why? The code isn't perfect. If Selenium crashed, the program marked that town as 'ER' in ```town_pops``` and moved onto the next town. It's time to go back and fix these. Also, there are individual discrepancies that must be taken care of. The code below essentially finds the rows in ```town_pops_clean.csv``` that have either 'ER' or are in the ```er_indexes``` list, which contains individual town indexes. 

# In[38]:


# handle individual cases (pass in their indexes)
er_indexes = [901, 926, 992, 1065, 1142]


# In[39]:


# find the populations of towns when webdriver crashed
csv_town = pd.read_csv("town_pops_clean_2.csv")
csv_town = csv_town[["Unnamed: 0", "state", "county", "city", "country", "population"]]

# handle errors (rows with 'ER')
errors = csv_town.loc[csv_town['population'].isin(["ER"])].drop(columns={'population', 'country'}).values.tolist()

# handle individual discrepancies 
indiv_disc = csv_town.loc[csv_town.index.isin(er_indexes)].drop(columns={'population', 'country'}).values.tolist()

er_towns = errors + indiv_disc
print(er_towns)


# ## Rerunning the Program

# At this point, the ```ancestry``` function is ran again: ```error_handling``` is set to ```True``` and ```towns_l``` is now set to ```er_towns```. Once that's done, the towns are replaced with their new populations. 

# In[40]:


town_pops = ancestry(True, er_towns)


# In[41]:


towns_d.replace({"Group State": codes}, inplace=True)
towns_d.rename(columns={"Group State":"state", "Group County":"county", "Group Town":"city"}, inplace=True)
towns_d["country"] = "USA"
towns_d["population"] = "NR"
towns_d = towns_d[["city", "county", "state", "country", "population"]]
print(towns_d)


# In[41]:


# after rerunning program
print(town_pops) # should print out the new populations for each wrong town 
town_copy = pd.read_csv("town_pops_clean_2.csv")
town_copy["location"] = town_copy["city"] + ", " + town_copy["county"] + ", " + town_copy["state"] + ", " + town_copy["country"]
print(town_copy[["population", "location"]]) 

for town in town_pops.keys():
    town_copy.loc[town_copy["location"] == town, "population"] = town_pops[town]
town_copy.drop(columns={"Unnamed: 0", "location"}, inplace=True)

# town_copy = pd.concat([town_copy, towns_d]).reset_index()

print(town_copy) 

town_copy.to_csv("town_pops_clean_2.csv")


# In[42]:


# find the frequencies of "no records"
town_pop_csv = pd.read_csv("town_pops_clean_2.csv")
res = sum(x == 'NR' for x in town_pop_csv["population"].values.tolist())
print("Frequency of NR is : " + str(res))


# # Part II

# Get all towns from Ancestry. Run the same program, again. This will prevent us from having to rerun the program again when Assumed State Debt is added. 

# In[17]:


from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import StaleElementReferenceException


# In[18]:


driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 30)
census_url = "https://www.ancestry.com/search/collections/5058/"
driver.get(census_url)


# In[19]:


list_obj = driver.find_element(By.XPATH, "//*[@id='browseOptions0']")
select_obj = Select(list_obj)
state_op = select_obj.options
del state_op[0] # remove "Choose..."
states_c = {} # we'll add the counties that are in each state, here 
for state in state_op:
    states_c[state.text] = {}
print(states_c)


# In[20]:


# go through each state (X)
# use selenium to find all the options for counties (X)
# store counties in the 'counties' dictionary (X) 

for state in states_c.keys():
    try:
        select_obj.select_by_visible_text(state)    
    except:
        list_obj = driver.find_element(By.XPATH, "//*[@id='browseOptions0']")
        select_obj = Select(list_obj)
        select_obj.select_by_visible_text(state)    
            
    time.sleep(0.25)
    county_ele = wait.until(presence_of_element_located((By.XPATH, "//*[@id='browseOptions1']")))
    county_obj = Select(county_ele)
    county_op = county_obj.options
    
    for county in county_op:
        if county.text == "Choose...":
            continue
        else:
            states_c[state][county.text] = []
    
print(states_c)


# In[21]:


# go through each county in each state (x)
# use selenium find towns in each county 
# add to dictionary 
# https://github.com/SeleniumHQ/selenium/issues/7186 

for state in states_c.keys():
        state_ele = wait.until(presence_of_element_located((By.XPATH, "//*[@id='browseOptions0']")))
        select_obj = Select(state_ele)
        select_obj.select_by_visible_text(state)  
        time.sleep(0.25)
        
        for county in states_c[state].keys():
            while True:
                maxIterations = 10
                try:
                    county_ele = wait.until(presence_of_element_located((By.XPATH, "//*[@id='browseOptions1']")))
                    select = Select(county_ele)
                    select.select_by_visible_text(county)
                    break
                except (StaleElementReferenceException, NoSuchElementException) as error:
                    maxIterations -= 1
                    if maxIterations == 0:
                        throw
                
            # get list of towns 
            time.sleep(1)
            town_ele = wait.until(presence_of_element_located((By.XPATH, "//*[@id='browselevel2']")))
            town_ele_t = town_ele.text
            print(state + ", " + county)
            print("______________")
            
            if town_ele_t is None:
                print("town_ele is None\n")
                time.sleep(1)
                town_ele = wait.until(presence_of_element_located((By.XPATH, "//*[@id='browselevel2']")))
            
            town_l = town_ele_t.split("\n")
            
            for town in town_l:
                town_x = town.strip()
                
                if town_x != "Not Stated":
                    states_c[state][county].append(town_x)
                    
            print(len(states_c[state][county]))
            print("\n")

print(states_c)


# In[22]:


# create list of towns
# go through entire dictionary 
# append each town into the list 

towns_an = []

for state in states_c.keys():
    for county in states_c[state].keys():
        for town in states_c[state][county]:
            towns_an.append([0, state, county, town])
            
print(towns_an)


# In[23]:


town_pops = ancestry(error_handling=True, towns_l=towns_an) 


# In[24]:


print(town_pops)


# In[26]:


# save town_pops dictionary as a csv file 
df = pd.DataFrame.from_dict(town_pops, orient="index")
df.to_csv("town_pops_2.csv")
df = pd.read_csv("town_pops_2.csv", index_col=0)
print(df)
# printing result


# In[ ]:





# In[ ]:




