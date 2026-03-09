from pathlib import Path
from selenium.webdriver.common.by import By
import json
import time
import pandas as pd
import numpy as np
from source.lib.ancestry_scraper.scraper import ScrapeCD, ProcessLocationString
from source.lib.ancestry_scraper.auth import GetAuthenticatedDriver

INDIR_DERIVED = Path("output/derived/post1790_cd")
OUTDIR = Path("output/scrape/post1790_cd_census_match")
PROGRESS_FILE = OUTDIR / 'progress.json'


def Main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    final_name_list = LoadNameList()
    driver = GetAuthenticatedDriver()
    df_list, match_list = ScrapeAllNames(final_name_list, driver)
    df_list = ApplyDfFixes(df_list)
    match_list = FilterAndFixMatchList(df_list['Match Index'], match_list)
    df_list, match_list = DeduplicateAndRemap(df_list, match_list)
    WriteOutputs(final_name_list, df_list, match_list)


def LoadNameList():
    return pd.read_csv(INDIR_DERIVED / 'name_list.csv', index_col=0)[
        ['Fn_Fix', 'Ln_Fix', 'new_town', 'county', 'new_state', 'country', 'geo_level']
    ].drop_duplicates().reset_index(drop=True)


def LoadCheckpoint():
    ids_path = OUTDIR / 'scrape_ids_prelim.csv'
    results_path = OUTDIR / 'scrape_results_prelim.csv'
    if ids_path.exists() and ids_path.stat().st_size > 0 and results_path.exists() and results_path.stat().st_size > 0:
        df_rows = pd.read_csv(ids_path, index_col=0).to_dict('records')
        match_rows = pd.read_csv(results_path, index_col=0).to_dict('records')
    else:
        df_rows, match_rows = [], []
    try:
        with open(PROGRESS_FILE) as f:
            done = set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        done = set()
    return df_rows, match_rows, done


def ScrapeAllNames(final_name_list, driver):
    df_rows, match_rows, done = LoadCheckpoint()

    def write_checkpoint():
        (pd.DataFrame(df_rows) if df_rows else pd.DataFrame(columns=[
            'First Name', 'Last Name', 'Search Town', 'Search County', 'Search State',
            'Name Type', 'url', 'Match Index', 'Match Status'
        ])).to_csv(OUTDIR / 'scrape_ids_prelim.csv')
        (pd.DataFrame(match_rows) if match_rows else pd.DataFrame(columns=[
            'Name', 'Home in 1790 (City, County, State)',
            'Free White Persons - Males - 16 and over',
            'Free White Persons - Females', 'Number of Household Members'
        ])).to_csv(OUTDIR / 'scrape_results_prelim.csv')
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(list(done), f)

    for index in final_name_list.index:
        fn = final_name_list.loc[index, 'Fn_Fix']
        ln = final_name_list.loc[index, 'Ln_Fix']
        search_town = final_name_list.loc[index, 'new_town']
        search_county = final_name_list.loc[index, 'county']
        search_state = final_name_list.loc[index, 'new_state']
        geo_level = final_name_list.loc[index, 'geo_level']

        if geo_level == "country":
            continue

        key = f"{fn}|{ln}|{search_town}|{search_county}|{search_state}|{geo_level}"
        if key in done:
            continue

        location = ProcessLocationString(geo_level, search_town, search_county, search_state)
        if not isinstance(fn, str):
            fn = ""
        name = fn + " " + ln
        print(f"Searching for {name} that lived in {location}")

        match = False
        tries = 0
        while not match and tries < 8:
            try:
                res = ScrapeCD(fn, ln, driver, search_town, search_county, search_state, geo_level)
                while res['Match Status'] == 'No Match' and PageHasResults(driver, res):
                    print("Need to obtain information again")
                    res = ScrapeCD(fn, ln, driver, search_town, search_county, search_state, geo_level)
                match = True
            except Exception:
                print("trying again")
                tries += 1

        print(tries, res)
        res = AddToResult(res, fn, ln, search_town, search_county, search_state, geo_level)
        df_rows, match_rows = ParseResult(res, df_rows, match_rows)
        done.add(key)
        write_checkpoint()

    df_list = pd.DataFrame(df_rows) if df_rows else pd.DataFrame(columns=[
        'First Name', 'Last Name', 'Search Town', 'Search County', 'Search State',
        'Name Type', 'url', 'Match Index', 'Match Status'
    ])
    match_list = pd.DataFrame(match_rows) if match_rows else pd.DataFrame(columns=[
        'Name', 'Home in 1790 (City, County, State)',
        'Free White Persons - Males - 16 and over',
        'Free White Persons - Females', 'Number of Household Members'
    ])
    return df_list, match_list


def ApplyDfFixes(df_list):
    for full_name in ['AnnCook', 'AnnFromberger', 'JaneOlmsted']:
        ind = df_list[df_list['First Name'] + df_list['Last Name'] == full_name].index
        df_list.loc[ind, ['Match Index', 'Match Status']] = [np.nan, 'No Match']

    drops = [
        ("Benjamin Bosworth", "3 Potential Matches Found"),
        ("Richard Waterman", "No Match"),
        ("William Arnold", "No Match"),
        ("William Potter", "No Match"),
    ]
    for full_name, status in drops:
        ind = df_list[df_list['First Name'] + " " + df_list['Last Name'] + df_list['Match Status'] == full_name + status].index
        df_list = df_list.drop(ind)

    return df_list


def FilterAndFixMatchList(match_index, match_list):
    inds = match_index.apply(
        lambda x: str(x).split(" | ") if not pd.isnull(x) else [0]
    ).explode().apply(lambda x: int(x)).drop_duplicates().tolist()
    match_list = match_list.loc[inds]

    match_list.loc[match_list[match_list['Home in 1790 (City, County, State)'].isnull()].index,
                   ['Home in 1790 (City, County, State)', 'Free White Persons - Females', 'Number of Household Members']] = [
        'Philadelphia City, Philadelphia, Pennsylvania', 2, 2]
    match_list.loc[match_list[match_list['Name'].apply(lambda x: 'Rebecca Ha' in x)].index,
                   'Home in 1790 (City, County, State)'] = 'Sherburn, Nantucket, Massachusetts, USA'

    brack_ind = match_list[match_list['Name'].apply(lambda x: "[" in x and "\n" not in x)].index
    match_list.loc[brack_ind, 'Name'] = match_list.loc[brack_ind, 'Name'].apply(
        lambda x: x.replace("[", "").replace("]", ""))
    space_ind = match_list[match_list['Name'].apply(lambda x: '\n' in x)].index
    match_list.loc[space_ind, 'Name'] = match_list.loc[space_ind, 'Name'].apply(
        lambda x: x.replace('\n', ' ').replace('\t', '').replace('[', '| ').replace(']', '').replace('  ', ''))

    match_list['Match Type'] = match_list['Home in 1790 (City, County, State)'].apply(
        lambda x: 'town' if len(x.split(", ")) == 3 else 'county' if len(x.split(", ")) == 2 else 'state')
    match_list['Match Town'] = match_list.apply(
        lambda x: x['Home in 1790 (City, County, State)'].split(", ")[0] if x['Match Type'] == 'town' else np.nan, axis=1)
    match_list['Match County'] = match_list.apply(
        lambda x: x['Home in 1790 (City, County, State)'].split(", ")[1] + " County" if x['Match Type'] == 'town' else
        x['Home in 1790 (City, County, State)'].split(", ")[0] + " County" if x['Match Type'] == 'county' else np.nan, axis=1)
    match_list['Match State'] = match_list.apply(
        lambda x: x['Home in 1790 (City, County, State)'].split(", ")[-1], axis=1)

    match_list.loc[match_list[match_list['Home in 1790 (City, County, State)'] == 'Hopewell, Newton, Tyborn, and Westpensboro, Cumberland, Pennsylvania'].index,
                   ['Match Town', 'Match County', 'Match State', 'Match Type']] = [
        'Hopewell, Newton, Tyborn and Westpensboro', 'Cumberland County', 'Pennsylvania', 'town']
    match_list.loc[match_list[match_list['Home in 1790 (City, County, State)'] == 'Fannet, Hamilton, Letterkenney, Montgomery, and Peters, Franklin, Pennsylvania'].index,
                   ['Match Town', 'Match County', 'Match State', 'Match Type']] = [
        'Fannet, Hamilton, Letterkenney, Montgomery and Peters', 'Franklin County', 'Pennsylvania', 'town']

    return match_list


def DeduplicateAndRemap(df_list, match_list):
    match_list['index_old'] = match_list.index
    match_list_no_dup = match_list.drop_duplicates(subset=[ele for ele in match_list.columns if ele != 'index_old'])
    match_list_no_dup.rename({'index_old': 'index_temp'}, axis=1, inplace=True)

    match_dict_df = pd.merge(match_list.reset_index(), match_list_no_dup, how='left').set_index('index')
    match_dict_df['index_old'] = match_dict_df.index
    gen_newind = match_dict_df[['index_temp']].drop_duplicates().reset_index(drop=True).copy()
    gen_newind['index_new'] = gen_newind.index
    match_dict_df = pd.merge(match_dict_df, gen_newind)
    match_dict = dict(zip(match_dict_df['index_old'], match_dict_df['index_new']))

    df_list['Match Index'] = df_list['Match Index'].apply(
        lambda x: JoinNames([str(match_dict[int(ele)]) for ele in x.split(' | ')]) if not pd.isnull(x) else x)
    match_list = pd.merge(match_list_no_dup, gen_newind)
    match_list['index_new'] = match_list['index_new'].apply(lambda x: str(x))

    double_rep_ind = df_list[df_list.apply(
        lambda x: (not pd.isnull(x['Match Index']) and ' | ' not in x['Match Index'])
                  and x['Match Status'] not in ['Complete Match', 'Poor Match'], axis=1)].index
    df_list.loc[double_rep_ind, 'Match Status'] = 'Complete Match'

    return df_list, match_list


def WriteOutputs(final_name_list, df_list, match_list):
    pd.merge(
        final_name_list, df_list.drop_duplicates(), how='left',
        left_on=['Fn_Fix', 'Ln_Fix', 'new_town', 'county', 'new_state', 'geo_level'],
        right_on=['First Name', 'Last Name', 'Search Town', 'Search County', 'Search State', 'Name Type']
    ).to_csv(OUTDIR / 'name_list_scraped.csv')
    df_list.to_csv(OUTDIR / 'scrape_ids.csv')
    match_list.to_csv(OUTDIR / 'scrape_results.csv')


def JoinNames(lst):
    return " | ".join(sorted(list(set([ele for ele in lst if ele != ""]))))


def AddToResult(res, fn, ln, search_town, search_county, search_state, geo_level):
    res['First Name'] = fn
    res['Last Name'] = ln
    res['Search Town'] = search_town
    res['Search County'] = search_county
    res['Search State'] = search_state
    res['Name Type'] = geo_level
    return res


def ParseResult(res, df_rows, match_rows):
    if 'No Match' not in res['Match Status']:
        match_count = sum(1 for k in res if k.startswith('Match '))
        match_inds = []
        for j in range(1, match_count + 1):
            match_rows.append(res[f'Match {j}'].copy())
            match_inds.append(str(len(match_rows) - 1))
            del res[f'Match {j}']
        res['Match Index'] = " | ".join(match_inds) if len(match_inds) > 1 else match_inds[0]
    df_rows.append(res)
    return df_rows, match_rows


def PageHasResults(driver, res):
    driver.get(res['url'])
    time.sleep(2)
    try:
        driver.find_element(By.XPATH, "//*[@id=\"results-footer\"]/h3").text
        return True
    except Exception:
        return False


if __name__ == "__main__":
    Main()
