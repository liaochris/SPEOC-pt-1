from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.expected_conditions import element_to_be_clickable, presence_of_element_located
from selenium.webdriver.support.wait import WebDriverWait
from joblib import Parallel, delayed, cpu_count
import time
import getpass
import pickle
import ast
import numpy as np
import pandas as pd
from pathlib import Path
from source.lib.SaveData import SaveData

INDIR_PRESCRAPE = Path("output/derived/prescrape/pre1790")
OUTDIR          = Path("output/scrape/pre1790")

RECORDS = {
    'nh': ['https://www.ancestrylibrary.com/search/collections/5058/'],
    'nj': ['https://www.ancestrylibrary.com/search/collections/2234/',
           'https://www.ancestrylibrary.com/search/collections/3562/'],
    'ny': ['https://www.ancestrylibrary.com/search/collections/5058/'],
    'ma': ['https://www.ancestrylibrary.com/search/collections/5058/'],
    'ct': ['https://www.ancestrylibrary.com/search/collections/5058/'],
    'va': ['https://www.ancestrylibrary.com/search/collections/2234/',
           'https://www.ancestrylibrary.com/search/collections/3578/'],
    'pa': ['https://www.ancestrylibrary.com/search/collections/2702/',
           'https://www.ancestrylibrary.com/search/collections/2234/',
           'https://www.ancestrylibrary.com/search/collections/3570/'],
    'md': ['https://www.ancestrylibrary.com/search/collections/3552/'],
    'nc': ['https://www.ancestrylibrary.com/search/collections/3005/',
           'https://www.ancestrylibrary.com/search/collections/2234/'],
    'ga': ['https://www.ancestrylibrary.com/search/collections/2234/'],
    'ri': ['https://www.ancestrylibrary.com/search/collections/3571/'],
}

RESIDENCE_URLS = {
    'nh': '_new+hampshire-usa_32',
    'nj': '_new+jersey-usa_33',
    'ny': '_new+york-usa_35',
    'ma': '_massachusetts-usa_24',
    'ct': '_connecticut-usa_9',
    'va': '_virginia-usa_49',
    'pa': '_pennsylvania-usa_41',
    'md': '_maryland-usa_23',
    'nc': '_north+carolina-usa_36',
    'ga': '_georgia-usa_13',
    'ri': '_rhode+island-usa_42',
}

NETID_XPATH    = '/html/body/div[1]/div[2]/section/div[1]/div/form/fieldset/div[1]/input'
PASSWORD_XPATH = '/html/body/div[1]/div[2]/section/div[1]/div/form/fieldset/div[2]/input'
LOGIN_BTN0_XPATH = '/html/body/main/div/div/div/a'
LOGIN_BTN1_XPATH = '/html/body/div[1]/div[2]/section/div[1]/div/form/fieldset/div[3]/button'


def Main():
    OUTDIR.mkdir(parents=True, exist_ok=True)

    agg_debt = pd.read_csv(INDIR_PRESCRAPE / 'pre1790_cleaned.csv')
    agg_debt['to whom due | first name'] = agg_debt['to whom due | first name'].astype(str)
    agg_debt['to whom due | last name']  = agg_debt['to whom due | last name'].astype(str)

    agg_debt_copy = agg_debt[
        ~agg_debt['state'].isin(['cs', 'f', 'de'])
    ]
    agg_debt_sp = agg_debt_copy.groupby('state')

    similar_names_dfs = LoadSimilarNamesPerState(agg_debt_sp.groups, INDIR_PRESCRAPE)

    username = input('username: ')
    password = getpass.getpass(prompt='password: ')
    options  = SetupChromeOptions()
    driver_objs = AuthenticateDrivers(username, password, options)

    ancestry_name_changes = LoadCheckpoint('ancestry_name_changes')
    rerun_rows            = LoadCheckpoint('rerun_rows')
    checked               = LoadCheckpoint('checked')
    fixes                 = LoadCheckpoint('fixes')

    similar_names_df = pd.concat(list(similar_names_dfs.values()))

    df_split       = np.array_split(similar_names_df, cpu_count())
    ancestry_calls = [delayed(ProcessNameChunk)(df_split[i], driver_objs[i], agg_debt_copy)
                      for i in range(len(df_split))]
    Parallel(n_jobs=-1, backend="threading")(ancestry_calls)

    ancestry_name_changes = LoadCheckpoint('ancestry_name_changes')
    if ancestry_name_changes:
        raw_df = pd.DataFrame(ancestry_name_changes)
        SaveData(raw_df, list(raw_df.columns[:1]), OUTDIR / 'ancestry_name_changes_raw.csv',
                 log_file=OUTDIR / 'ancestry_name_changes_raw.log')


def SetupChromeOptions():
    options = Options()
    options.add_argument('--headless')
    options.add_argument("--window-size=1000,1000")
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--no-sandbox')
    return options


def AuthenticateDrivers(username, password, options):
    driver_objs = {}
    for i in range(cpu_count()):
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        wait   = WebDriverWait(driver, 30)
        driver_objs[i] = (driver, wait)

        driver.get('https://guides.libraries.emory.edu/ALE')
        wait.until(element_to_be_clickable((By.XPATH, LOGIN_BTN0_XPATH))).click()

        netid_input = wait.until(element_to_be_clickable((By.XPATH, NETID_XPATH)))
        netid_input.click()
        netid_input.send_keys(username)

        pass_input = wait.until(element_to_be_clickable((By.XPATH, PASSWORD_XPATH)))
        pass_input.click()
        pass_input.send_keys(password)
        wait.until(element_to_be_clickable((By.XPATH, LOGIN_BTN1_XPATH))).click()
        time.sleep(1)

        driver.get('https://www.ancestrylibrary.com/search/collections/5058/')
        print(driver.current_url)

    return driver_objs


def LoadSimilarNamesPerState(states, indir):
    similar_names_dfs = {}
    for state in states:
        similar_names_dfs[state] = pd.read_csv(indir / f'similar_names/similar_names_{state}.csv')
    print(len(similar_names_dfs))
    return similar_names_dfs


def ProcessNameChunk(similar_names_chunk, driver_wait, agg_debt):
    similar_names_chunk.apply(
        lambda row0: CheckNamePair(row0, row0['state'], driver_wait[0], driver_wait[1], agg_debt), axis=1
    )


def CheckNamePair(row0, state, driver, wait, agg_debt):
    ancestry_name_changes = LoadCheckpoint('ancestry_name_changes')
    rerun_rows            = LoadCheckpoint('rerun_rows')
    checked               = LoadCheckpoint('checked')
    fixes                 = LoadCheckpoint('fixes')

    fn0 = str(row0['to whom due | first name'])
    ln0 = str(row0['to whom due | last name'])
    matches = ast.literal_eval(row0['matches'])
    name0 = fn0 + ' ' + ln0

    for match in matches:
        row1 = agg_debt.loc[[match[2]]]
        fn1  = str(row1['to whom due | first name'].values[0])
        ln1  = str(row1['to whom due | last name'].values[0])
        name1 = fn1 + ' ' + ln1
        if (name0, name1, state) not in checked and (name1, name0, state) not in checked:
            SearchAncestryForPair(fn0, ln0, fn1, ln1, row0, row1, state, driver, wait,
                                  ancestry_name_changes, rerun_rows, fixes)
            checked.append((name0, name1, state))
            SaveCheckpoint('checked', checked)


def SearchAncestryForPair(fn0, ln0, fn1, ln1, row0, row1, state, driver, wait,
                          ancestry_name_changes, rerun_rows, fixes):
    name0 = fn0 + ' ' + ln0
    name1 = fn1 + ' ' + ln1

    for url in RECORDS[state]:
        try:
            url0 = (url + '?name=' + fn0 + '_' + ln0
                    + '&name_x=ps&residence=1780' + RESIDENCE_URLS[state] + '&residence_x=10-0-0_1-0')
            driver.get(url0)
            try:
                result0 = wait.until(presence_of_element_located((By.CLASS_NAME, 'srchHit'))).text
            except Exception:
                result0 = ''

            url1 = (url + '?name=' + fn1 + '_' + ln1
                    + '&name_x=ps&residence=1780' + RESIDENCE_URLS[state] + '&residence_x=10-0-0_1-0')
            driver.get(url1)
            try:
                result1 = wait.until(presence_of_element_located((By.CLASS_NAME, 'srchHit'))).text
            except Exception:
                result1 = ''

            print('---------------------------+')
            if result0 == result1 and result0 != '' and result1 != '':
                if name0 == result0 and name0 == result1:
                    title1    = row1['to whom due | title']
                    org_file1 = row1['org_file']
                    org_index1 = row1['org_index']
                    ancestry_name_changes.append(
                        [title1, title1, fn1, ln1, fn0, ln0, 6, org_file1, org_index1, state]
                    )
                    SaveCheckpoint('ancestry_name_changes', ancestry_name_changes)
                    fixes.append({fn1: fn0, ln1: ln0, 'state': state})
                    SaveCheckpoint('fixes', fixes)

                elif name1 == result0 and name1 == result1:
                    title0    = row0['to whom due | title']
                    org_file0 = row0['org_file']
                    org_index0 = row0['org_index']
                    ancestry_name_changes.append(
                        [title0, title0, fn0, ln0, fn1, ln1, 6, org_file0, org_index0, state]
                    )
                    SaveCheckpoint('ancestry_name_changes', ancestry_name_changes)
                    fixes.append({fn0: fn1, ln0: ln1, 'state': state})
                    SaveCheckpoint('fixes', fixes)

            print(f'name0={name0} | name1={name1} | state={state}')
            print(f'result0={result0} | result1={result1}')
            print('---------------------------+')

        except Exception as e:
            print('---------------------------+')
            print('Error:', e)
            print('---------------------------+')
            if (row0, row1) not in rerun_rows:
                rerun_rows.append((row0, row1))
                SaveCheckpoint('rerun_rows', rerun_rows)


def LoadCheckpoint(name):
    path = OUTDIR / f'ckpt_{name}.pkl'
    if not path.exists():
        return []
    with path.open('rb') as f:
        return pickle.load(f)


def SaveCheckpoint(name, obj):
    with (OUTDIR / f'ckpt_{name}.pkl').open('wb') as f:
        pickle.dump(obj, f)


if __name__ == "__main__":
    Main()
