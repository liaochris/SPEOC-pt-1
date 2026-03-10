#!/usr/bin/env python
# coding: utf-8

import json
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import element_to_be_clickable, presence_of_element_located
from selenium.webdriver.support.ui import Select
from source.lib.ancestry_scraper.auth import GetAuthenticatedDriver
from source.lib.ancestry_scraper.config import STATE_ABBREVIATIONS
import pandas as pd
import time

INDIR_POST1790_CD = Path("output/derived/post1790_cd")
OUTDIR = Path("output/scrape/post1790_cd_town_pop")
BROWSE_CHECKPOINT = OUTDIR / 'progress_browse.json'

COUNTY_EXCEPTIONS = {
    'Philadelphia County': 'Philadelphia',
    'Charleston County': 'Charleston',
    'New Haven County': 'New Haven'
}

# States without Ancestry 1790 census records — excluded from Part I
EXCLUDED_STATES = ['VA', 'GA', 'NJ', 'DE']


def Main():
    OUTDIR.mkdir(parents=True, exist_ok=True)

    # Part I: scrape towns drawn from CD data
    towns = LoadCDTowns()
    ScrapeLocations(browse_format=False, towns_l=towns)

    # Part II: enumerate all towns from Ancestry browse hierarchy, then scrape
    states_c = BrowseAncestryHierarchy()
    towns_browse = BuildBrowseTownList(states_c)
    town_pops_browse = ScrapeLocations(browse_format=True, towns_l=towns_browse, checkpoint_path=BROWSE_CHECKPOINT)

    # Format Part II raw results into separate city/county/state columns
    FormatBrowseResults(town_pops_browse)

    # Re-scrape rows that errored in Part II
    FixScrapeErrors()


def LoadCDTowns():
    cd_df = pd.read_csv(INDIR_POST1790_CD / "final_data_CD.csv")
    towns = cd_df[['Group State', 'Group County', 'Group Town']].drop_duplicates().dropna()
    towns = towns[~towns['Group State'].isin(EXCLUDED_STATES)]
    # Prepend dummy 0 so rows are [0, state, county, town] — same layout as browse format
    return [[0] + row for row in towns.values.tolist()]


def ScrapeLocations(browse_format, towns_l, checkpoint_path=None):
    if checkpoint_path and checkpoint_path.exists():
        with open(checkpoint_path) as f:
            town_pops = json.load(f)
    else:
        town_pops = {}

    driver = GetAuthenticatedDriver()
    wait = WebDriverWait(driver, 30)
    census_url = "https://www.ancestry.com/search/collections/5058/"
    try:
        for town in towns_l:
            if not browse_format:
                county = town[2][:-7].replace(' County', '')
                loc_add = town[3] + ", " + county + ", " + STATE_ABBREVIATIONS[town[1]] + ", USA"
            else:
                county = town[2]
                loc_add = town[3] + ", " + county + ", " + town[1] + ", USA"

            if loc_add in town_pops:
                continue

            try:
                try:
                    driver.get(census_url)
                except Exception:
                    driver.close()
                    driver.get(census_url)

                if county in COUNTY_EXCEPTIONS:
                    county = COUNTY_EXCEPTIONS[county]

                print("-------------------------")
                print(loc_add)

                xpath = "/html/body/div[3]/div/div/div/div/section/div/div/div/div/div/form/div[1]/div/fieldset[2]/div[2]/div/input"
                try:
                    wait.until(element_to_be_clickable((By.XPATH, xpath))).click()
                except Exception:
                    driver.close()
                    driver.get(census_url)
                    time.sleep(0.25)
                    wait.until(element_to_be_clickable((By.XPATH, xpath))).click()

                input_t = driver.find_element(By.XPATH, xpath)
                input_t.send_keys(loc_add)
                time.sleep(0.75)

                wait.until(element_to_be_clickable((By.XPATH, "/html/body/div[3]/div/div/div/div/section/div/div/div/div/div/form/div[1]/div/div[9]/div[1]/input"))).click()
                time.sleep(0.75)

                print(driver.current_url)
                driver.get(driver.current_url + "&event_x=0-0-0_1-0")

                title_pl = wait.until(presence_of_element_located((By.XPATH, "//*[@id='refineView']/form/div[3]/div/div[1]/div"))).get_attribute("title")
                if title_pl.strip() == loc_add.strip():
                    try:
                        pop = driver.find_element(By.CLASS_NAME, "resultsLabel")
                        town_pops[loc_add] = int(pop.text.split("of")[1].replace(',', ''))
                    except NoSuchElementException:
                        town_pops[loc_add] = "NR"
                else:
                    print("Titles don't match")
                    print("title on page = " + title_pl)
                    town_pops[loc_add] = "NR"

                print(town_pops[loc_add])
                print(len(town_pops))
                print(driver.current_url)
                print("-------------------------")

            except Exception as e:
                print("___________________________________")
                print("ERROR! Moving swiftly to next town")
                print(e)
                print("___________________________________")
                town_pops[loc_add] = 'ER'
                try:
                    driver.quit()
                except Exception:
                    pass
                driver = GetAuthenticatedDriver()
                wait = WebDriverWait(driver, 30)
                continue

            if checkpoint_path:
                with open(checkpoint_path, 'w') as f:
                    json.dump(town_pops, f)
    finally:
        try:
            driver.quit()
        except Exception:
            pass

    return town_pops


def BrowseAncestryHierarchy():
    driver = GetAuthenticatedDriver()
    wait = WebDriverWait(driver, 30)
    census_url = "https://www.ancestry.com/search/collections/5058/"
    driver.get(census_url)

    try:
        list_obj = driver.find_element(By.XPATH, "//*[@id='browseOptions0']")
        select_obj = Select(list_obj)
        state_op = select_obj.options
        del state_op[0]  # remove "Choose..."
        states_c = {}
        for state in state_op:
            states_c[state.text] = {}

        for state in states_c.keys():
            try:
                select_obj.select_by_visible_text(state)
            except Exception:
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
                states_c[state][county.text] = []

        print(states_c)

        for state in states_c.keys():
            state_ele = wait.until(presence_of_element_located((By.XPATH, "//*[@id='browseOptions0']")))
            select_obj = Select(state_ele)
            select_obj.select_by_visible_text(state)
            time.sleep(0.25)

            for county in states_c[state].keys():
                while True:
                    max_iterations = 10
                    try:
                        county_ele = wait.until(presence_of_element_located((By.XPATH, "//*[@id='browseOptions1']")))
                        select = Select(county_ele)
                        select.select_by_visible_text(county)
                        break
                    except (StaleElementReferenceException, NoSuchElementException):
                        max_iterations -= 1
                        if max_iterations == 0:
                            raise

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
    finally:
        try:
            driver.quit()
        except Exception:
            pass

    return states_c


def BuildBrowseTownList(states_c):
    towns_an = []
    for state in states_c.keys():
        for county in states_c[state].keys():
            for town in states_c[state][county]:
                towns_an.append([0, state, county, town])
    print(towns_an)
    return towns_an


def FormatBrowseResults(town_pops):
    rows = []
    for loc_add, population in town_pops.items():
        parts = [p.strip() for p in loc_add.rstrip().split(', ')]
        if len(parts) >= 4:
            city, county, state, country = parts[0], parts[1], parts[2], parts[3]
        elif len(parts) == 3:
            city, county, state, country = parts[0], parts[1], parts[2], ""
        else:
            continue
        rows.append({'city': city, 'county': county, 'state': state, 'country': country, 'population': population})
    towns_df = pd.DataFrame(rows)
    print(towns_df)
    towns_df.to_csv(OUTDIR / "town_pops_clean.csv", index=False)


def FixScrapeErrors():
    # Hardcoded indexes are manually identified rows that errored beyond those marked 'ER'
    # These will be stale if the browse scrape is re-run — verify against current output before use
    er_indexes = [901, 926, 992, 1065, 1142]

    csv_town = pd.read_csv(OUTDIR / "town_pops_clean.csv")
    csv_town = csv_town[["city", "state", "county", "country", "population"]]

    combined = pd.concat([
        csv_town.loc[csv_town['population'] == 'ER'],
        csv_town.loc[csv_town.index.isin(er_indexes)]
    ]).drop_duplicates()
    er_towns = [[0, row['state'], row['county'], row['city']] for _, row in combined.iterrows()]

    town_pops = ScrapeLocations(True, er_towns)

    location_key = csv_town["city"] + ", " + csv_town["county"] + ", " + csv_town["state"] + ", " + csv_town["country"]
    csv_town["population"] = location_key.map(town_pops).fillna(csv_town["population"])
    csv_town.to_csv(OUTDIR / "town_pops_clean.csv", index=False)

    nr_count = sum(x == 'NR' for x in csv_town["population"].values.tolist())
    er_count = sum(x == 'ER' for x in csv_town["population"].values.tolist())
    print(f"NR: {nr_count}, ER: {er_count}")


if __name__ == "__main__":
    Main()
