from collections import namedtuple
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from .config import STATE_ABBREVIATIONS, NAME_X_STRATEGIES, YEAR_OFFSETS
from .parser import ParseAllResidenceCounties
from .search import FetchSearchPage

MatchResult = namedtuple('MatchResult', ['counties', 'match_status', 'url', 'match_strategy', 'year_offset'])

LOCATIONSUFFIX = {
    'Littleton, Middlesex County, Massachusetts': 4534
}


def ScrapeLoanOffice(name, state, event_year):
    last_url = None
    for name_x in NAME_X_STRATEGIES:
        for year_offset in YEAR_OFFSETS:
            try:
                html, url = FetchSearchPage(name, state, event_year, year_offset, name_x)
                last_url = url
                counties = ParseAllResidenceCounties(html)
                count = len(counties)
                if count == 0:
                    continue
                elif count == 1:
                    return MatchResult(counties, "Complete Match", url, name_x, year_offset)
                elif count <= 4:
                    return MatchResult(counties, f"{count} Potential Matches", url, name_x, year_offset)
                else:
                    return MatchResult(counties, "Too Many Results", url, name_x, year_offset)
            except Exception:
                continue
    return MatchResult([], "No Match", last_url, None, None)


def ScrapeCD(fn, ln, driver, search_town, search_county, search_state, name_type):
    return FindMatches(fn, ln, driver, search_town, search_county, search_state, name_type)


def DetermineMatchList(name_type, state):
    if name_type == "town":
        return ["name_x=1_1&residence_x=_1-0", "name_x=s_s&residence_x=_1-0", "name_x=ps_ps&residence_x=_1-0",
                "name_x=ps_ps&residence_x=_1-1", "name_x=ps_ps&residence_x=_1-1-a"]
    elif name_type == "county":
        return ["name_x=1_1&residence_x=_1-0", "name_x=s_s&residence_x=_1-0", "name_x=ps_ps&residence_x=_1-0",
                "name_x=ps_ps&residence_x=_1-0-a", "name_x=ps_ps&residence_x=_1-1"]
    else:
        if state == 'NY':
            return ["name_x=1_1&residence_x=_1-0", "name_x=s_s&residence_x=_1-0", "name_x=ps_ps&residence_x=_1-0",
                    "name_x=ps_ps&residence_x=_1-0-a"]
        else:
            return ["name_x=1_1&residence_x=_1-0", "name_x=s_s&residence_x=_1-0", "name_x=ps_ps&residence_x=_1-0",
                    "name_x=ps_ps&residence_x=_1-0"]


def ProcessLocationString(name_type, town, county, state, keep_county=True):
    if not keep_county and name_type != 'state':
        county = county.replace(" County", "").strip()
    if name_type == "town":
        return town + ", " + county + ", " + STATE_ABBREVIATIONS[state]
    elif name_type == "county":
        return county + ", " + STATE_ABBREVIATIONS[state]
    else:
        return STATE_ABBREVIATIONS[state]


def FindMatches(fn, ln, driver, search_town, search_county, search_state, name_type):
    max_searchind = 4 if name_type != "state" else 3
    search_ind = 0
    driver, url = NavigateTo(fn, ln, driver, search_ind, search_town, search_county, search_state, name_type, initial=True)
    time.sleep(1)
    val, search_ind = ListPeople(driver, search_ind, name_type)
    while search_ind < max_searchind:
        search_ind += 1
        driver, url = NavigateTo(fn, ln, driver, search_ind, search_town, search_county, search_state, name_type)
        time.sleep(1.5)
        val, search_ind = ListPeople(driver, search_ind, name_type)
    val['url'] = url
    return val


def NavigateTo(fn, ln, driver, search_ind, search_town, search_county, search_state, name_type, initial=False):
    fn = fn.replace(" ", "+")
    ln = ln.replace(" ", "+")
    searchstr = SearchLocationString(name_type, search_town, search_county, search_state)
    search_params = DetermineMatchList(name_type, search_state)[search_ind]
    namesuffix = search_params.split("&")[0].replace("name_x=", "")
    locsuffix = search_params.split("&")[1].replace("residence_x=", "")

    if initial:
        locationstr_keep = ProcessLocationString(name_type, search_town, search_county, search_state, True)
        locationstr_disc = ProcessLocationString(name_type, search_town, search_county, search_state, False)
        if locationstr_disc in LOCATIONSUFFIX:
            locationstr = locationstr_disc
        else:
            locationstr = locationstr_keep

        if locationstr in LOCATIONSUFFIX:
            locationnum = LOCATIONSUFFIX[locationstr]
            url = f"https://www.ancestrylibrary.com/search/collections/5058/?name={fn}_{ln}&name_x={namesuffix}&residence=_{searchstr}_{locationnum}&residence_x={locsuffix}"
            driver.get(url)
            time.sleep(3)
        else:
            driver.get('https://www.ancestrylibrary.com/search/collections/5058/')
            time.sleep(2)
            try:
                driver.find_element(by=By.XPATH, value=f"//*[@id=\"sfs__SelfResidencePlace\"]").send_keys(locationstr_keep)
                time.sleep(2)
                driver.find_element(by=By.XPATH, value=f"//*[@id=\"sfs__SelfResidencePlaceAutocomplete0\"]").click()
                time.sleep(1)
                driver.find_element(by=By.XPATH, value=f"//*[@id=\"sfs__SelfResidencePlace\"]").send_keys(Keys.ENTER)
                time.sleep(2)
                currurl = driver.current_url
                code = currurl.split("usa_")[1]
                LOCATIONSUFFIX[locationstr] = code
            except Exception:
                driver.get('https://www.ancestrylibrary.com/search/collections/5058/')
                time.sleep(3)
                driver.find_element(by=By.XPATH, value=f"//*[@id=\"sfs__SelfResidencePlace\"]").send_keys(locationstr_disc)
                time.sleep(2)
                driver.find_element(by=By.XPATH, value=f"//*[@id=\"sfs__SelfResidencePlaceAutocomplete0\"]").click()
                time.sleep(1)
                driver.find_element(by=By.XPATH, value=f"//*[@id=\"sfs__SelfResidencePlace\"]").send_keys(Keys.ENTER)
                time.sleep(2)
                currurl = driver.current_url
                code = currurl.split("usa_")[1]
                LOCATIONSUFFIX[locationstr] = code
            url = f"https://www.ancestrylibrary.com/search/collections/5058/?name={fn}_{ln}&name_x={namesuffix}&residence=_{searchstr}_{code}&residence_x={locsuffix}"
            driver.get(url)
            time.sleep(3)
    else:
        currurl = driver.current_url
        url = (currurl.split("&name_x")[0] + f"&name_x={namesuffix}" + "&residence=_" +
               currurl.split("&residence=_")[1].split("&residence_x=")[0] + f"&residence_x={locsuffix}")
    driver.get(url)
    return driver, url


def ListPeople(driver, search_ind, name_type):
    max_searchind = 4 if name_type != "state" else 3
    info = dict()
    try:
        count_text = driver.find_element(By.XPATH, "//*[@id=\"results-footer\"]/h3").text
        search_ind = max_searchind
    except Exception:
        if search_ind == max_searchind:
            info['Match Status'] = 'No Match'
            return info, search_ind
        else:
            return "continue searching", search_ind

    count = int(count_text.split(" of ")[1])
    if count > 1:
        if count < 5:
            info['Match Status'] = f'{count} Potential Matches Found'
            for i in range(count):
                currurl = driver.current_url
                p_info = GetInfo(driver, i)
                info[f'Match {i + 1}'] = p_info
                driver.get(currurl)
        else:
            info['Match Status'] = f'No Match: Too Many Potential Matches Found {count}'
        return info, search_ind
    else:
        p_info = GetInfo(driver, 0)
        info['Match Status'] = 'Complete Match'
        info[f'Match 1'] = p_info
        return info, search_ind


def GetInfo(driver, i):
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
        except Exception:
            success = False
    return info


def SearchLocationString(name_type, town, county, state):
    if not pd.isnull(county):
        county = county.replace('County', '').strip().replace(' ', '+').replace('\'', '+').lower()
    if name_type == "town":
        return town.lower() + "-" + county + "-" + STATE_ABBREVIATIONS[state].lower() + "-usa"
    elif name_type == "county":
        return county + "-" + STATE_ABBREVIATIONS[state].lower() + "-usa"
    elif name_type == "state" or name_type == "state_flag":
        return STATE_ABBREVIATIONS[state] + "-usa"
    else:
        return "usa"
