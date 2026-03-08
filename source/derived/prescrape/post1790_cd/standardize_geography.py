#!/usr/bin/env python
# coding: utf-8

from pathlib import Path
import numpy as np
import pandas as pd
from rapidfuzz import process
from source.lib.SaveData import SaveData

INDIR_RAW = Path("source/raw/post1790_cd")
INDIR_CENSUS = Path("source/raw/census_data")
OUTDIR = Path("output/derived/prescrape/post1790_cd")

# Column layouts for raw XLSX files with 3 sub-columns per variable vs single column
TRIPLE_VAL_COLS = [
    'First Name', 'Last Name', 'town1', 'state1', 'occupation1', '6p_Dollar', '6p_Cents',
    'First Name.1', 'Last Name.1', 'town2', 'state2', 'occupation2', '6p_def_Dollar', '6p_def_Cents',
    'First Name.2', 'Last Name.2', 'town3', 'state3', 'occupation3', '3p_Dollar', '3p_Cents',
]
SINGLE_VAL_COLS = [
    'First Name', 'Last Name', 'town', 'state', 'occupation',
    '6p_Dollar', '6p_Cents', '6p_def_Dollar', '6p_def_Cents', '3p_Dollar', '3p_Cents',
]
AGG_COLS = [
    '6p_Dollar', '6p_Cents', '6p_def_Dollar', '6p_def_Cents', '3p_Dollar', '3p_Cents',
    'town', 'state', 'occupation', 'Name', 'First Name', 'Last Name', 'state_data', 'state_data_index',
]


def Main():
    raw_params = pd.read_csv(INDIR_RAW / 'docs/cd_import_metadata.csv', delimiter=',', header=0)
    raw_params.drop('Unnamed: 6', inplace=True, axis=1)

    CD_all, change_df_CD = LoadRawCDData(INDIR_RAW, raw_params)
    CD_all = pd.concat([CD_all, LoadNYData(INDIR_RAW)])

    city_county_cw = pd.read_csv(INDIR_CENSUS / 'orig/zip_code_database.csv')[
        ['primary_city', 'acceptable_cities', 'unacceptable_cities', 'county', 'state']]

    # town_text_replacements.csv: normalizes raw town strings (e.g. abbreviations, typos)
    # to improve automatic matching accuracy. Applied before matching inside BuildTownCrosswalk.
    text_replacements = list(
        pd.read_csv(INDIR_RAW / 'corrections/geo/prescrape/geo_town_replacements.csv').fillna('').itertuples(index=False, name=None))

    list_of_states = ['CT', 'GA', 'MD', 'NC', 'NH', 'NJ', 'PA', 'RI', 'SC', 'MA', 'VA', 'DE']
    match_log = []
    geo_cw = BuildTownCrosswalk(CD_all, city_county_cw, text_replacements, list_of_states, match_log)

    geo_cw = pd.merge(CD_all[['town', 'state']].drop_duplicates(), geo_cw, how='left', on=['town', 'state'])[
        ['town', 'state', 'new_town', 'county', 'new_state', 'country', 'geo_level']]
    geo_cw.reset_index(inplace=True, drop=True)

    # town_fix.csv: manual geographic overrides applied after automatic matching.
    # Corrects wrong matches and fills towns that could not be matched automatically.
    df_manual = pd.read_csv(INDIR_RAW / 'corrections/geo/prescrape/geo_town_fix.csv')
    geo_cw = ApplyTownFixes(geo_cw, df_manual, match_log)
    geo_cw.loc[geo_cw[geo_cw['country'].isnull()].index, 'country'] = 'US'

    # One person has the wrong state
    CD_all = pd.merge(CD_all, geo_cw, on=['town', 'state'], how='left')
    CD_all = ApplyPersonStateFixes(CD_all, pd.read_csv(INDIR_RAW / 'corrections/geo/prescrape/geo_person_state.csv'))
    CD_all = ComputeTotals(CD_all)

    # NY records have no town data; assign state-level defaults
    CD_all.loc[CD_all[CD_all['state_data'] == 'NY'].index, 'new_state'] = 'NY'
    CD_all.loc[CD_all[CD_all['state_data'] == 'NY'].index, 'geo_level'] = 'state'

    OUTDIR.mkdir(parents=True, exist_ok=True)
    SaveData(CD_all, ['state_data', 'state_data_index'], OUTDIR / 'geo_standardized_CD_post1790.csv')

    # town_occ_agg_check.csv: rows where town/state/occupation had conflicting values
    # across the three sub-columns (e.g. town1 != town2), the longest value was kept.
    # this file lets a researcher review all such conflicts.
    (OUTDIR / 'check').mkdir(parents=True, exist_ok=True)
    change_df_CD = change_df_CD.reset_index(drop=True)
    change_df_CD['old'] = change_df_CD['old'].apply(lambda x: str(x) if isinstance(x, set) else x)
    change_df_CD['row_id'] = change_df_CD.index
    SaveData(change_df_CD, ['row_id'], OUTDIR / 'check/town_occupation_aggregation_list.csv')

    # Keep only the last log entry per (state, town_original): later entries (e.g. manual_override)
    # supersede earlier intermediate ones (e.g. unmatched logged before ApplyTownFixes runs).
    match_log_df = pd.DataFrame(match_log)
    match_log_df = match_log_df.drop_duplicates(subset=['state', 'town_original'], keep='last').reset_index(drop=True)
    match_log_df['row_id'] = match_log_df.index
    SaveData(match_log_df, ['row_id'], OUTDIR / 'check/town_changes_list.csv')


def LoadRawCDData(indir, raw_params):
    CD_all = pd.DataFrame(columns=AGG_COLS)
    change_df_CD = pd.DataFrame(columns=['old', 'new', 'type', 'state'])
    conflict_splits = list(
        pd.read_csv(indir / 'corrections/geo/prescrape/geo_conflict_splits.csv').itertuples(index=False, name=None))

    for ind in raw_params.index:
        file, header, usecols, numcols, state, dropcols = raw_params.loc[
            ind, ['file', 'header', 'usecols', 'numcols', 'state', 'dropcols']]
        state_cd = pd.read_excel(file, header=header, usecols=usecols)
        state_cd.columns = TRIPLE_VAL_COLS if numcols == 3 else SINGLE_VAL_COLS
        if not pd.isnull(dropcols):
            dropcols = [int(x) for x in dropcols.split(",")]
            state_cd.drop(dropcols, inplace=True)
        if numcols == 3:
            state_splits = [(t, v1, v2) for st, t, v1, v2 in conflict_splits if st == state]
            if state_splits:
                state_cd = ExpandConflictingRows(state_cd, state_splits)
            cd_state, change_df = CombineCols(state_cd, state)
        else:
            cd_state, change_df = CleanSingleColumn(state_cd, state)
            cd_state = cd_state[AGG_COLS]
        CD_all = pd.concat([CD_all, cd_state])
        change_df_CD = pd.concat([change_df_CD, change_df])

    return CD_all, change_df_CD


def CombineCols(df, state, num=3, namenum=3):
    # change_df_agg logs rows where occupation had conflicting values across sub-columns.
    # Geographic conflicts (different town/state) are split into separate rows first.
    # These are saved to town_occ_agg_check.csv for manual review.
    change_df_agg = pd.DataFrame(columns=['old', 'new', 'type'])
    for col in ['town', 'state', 'occupation']:
        if num == 3:
            df[col] = [set([" ".join(x.split()) for x in [t1, t2, t3] if not pd.isnull(x)]) for t1, t2, t3 in
                       zip(df[col + '1'], df[col + '2'], df[col + '3'])]
        else:
            df[col] = [set([" ".join(x.split()) for x in [t1, t2] if not pd.isnull(x)]) for t1, t2 in
                       zip(df[col + '1'], df[col + '2'])]
        if not any(df[col].apply(lambda x: len(x) > 1).tolist()):
            df[col] = df[col].apply(lambda x: x.pop() if x != set() else np.nan)
        else:
            old = df[df[col].apply(lambda x: len(x) > 1)][col]
            df[col] = df[col].apply(
                lambda x: x.pop() if len(x) == 1 else np.nan if x == set() else max(list(x), key=len))

            change_df = pd.DataFrame([old, df.loc[old.index][col]]).T
            change_df.columns = ['old', 'new']
            change_df['type'] = col
            change_df_str = change_df.copy()
            change_df_str['old'] = change_df_str['old'].astype(str)
            change_df_str = change_df_str.drop_duplicates()
            change_df_agg = pd.concat([change_df_agg, change_df.loc[change_df_str.index]])

    if namenum == 3:
        df['Name 1'] = DeNaN(df['First Name']) + " " + DeNaN(df['Last Name'])
        df['Name 2'] = DeNaN(df['First Name.1']) + " " + DeNaN(df['Last Name.1'])
        df['Name 3'] = DeNaN(df['First Name.2']) + " " + DeNaN(df['Last Name.2'])
        df['Name'] = list(
            list(set([x.replace("  ", " ").strip() for x in [name1, name2, name3] if x.strip() != ""])) for
            name1, name2, name3 in zip(df['Name 1'], df['Name 2'], df['Name 3']))
        df['Name'] = df['Name'].apply(lambda x: " | ".join(sorted(x)))

    df.loc[df.query('state.isna() and town.isna()').index, 'state'] = state
    df['state_data'] = state
    df['state_data_index'] = np.arange(1, df.shape[0] + 1, 1)
    change_df_agg['state'] = state

    return df[AGG_COLS], change_df_agg


def ExpandConflictingRows(df, state_splits):
    """Split rows where specific sub-column conflicts are listed in conflict_row_splits.csv.
    Each split row keeps only the dollar amounts from sub-columns belonging to its group,
    so the sum of amounts across split rows equals the original unsplit row."""
    GROUP_COLS = [
        {'town': 'town1', 'state': 'state1', 'occ': 'occupation1',
         'fn': 'First Name', 'ln': 'Last Name',
         'dollar': '6p_Dollar', 'cents': '6p_Cents'},
        {'town': 'town2', 'state': 'state2', 'occ': 'occupation2',
         'fn': 'First Name.1', 'ln': 'Last Name.1',
         'dollar': '6p_def_Dollar', 'cents': '6p_def_Cents'},
        {'town': 'town3', 'state': 'state3', 'occ': 'occupation3',
         'fn': 'First Name.2', 'ln': 'Last Name.2',
         'dollar': '3p_Dollar', 'cents': '3p_Cents'},
    ]

    def norm(x):
        return " ".join(str(x).split()) if isinstance(x, str) and str(x).strip() else ''

    result = []
    for _, row in df.iterrows():
        split_applied = False
        for split_type, val1, val2 in state_splits:
            target_set = {val1, val2}
            if split_type == 'town':
                actual_set = {norm(row.get(cols['town'])) for cols in GROUP_COLS
                              if norm(row.get(cols['town']))}
                if actual_set != target_set:
                    continue
                # Group sub-columns by (town, state) signature
                sigs = {}
                for i, cols in enumerate(GROUP_COLS):
                    sig = (norm(row.get(cols['town'])), norm(row.get(cols['state'])))
                    sigs.setdefault(sig, []).append(i)
                non_empty = {sig: idxs for sig, idxs in sigs.items() if sig != ('', '')}
                empty_idxs = sigs.get(('', ''), [])
                first_sig = next(iter(non_empty))
                non_empty[first_sig] = non_empty[first_sig] + empty_idxs
                for (town, state), idxs in non_empty.items():
                    new_row = row.to_dict()
                    for i, cols in enumerate(GROUP_COLS):
                        new_row[cols['town']] = town if town else np.nan
                        new_row[cols['state']] = state if state else np.nan
                        if i not in idxs:
                            new_row[cols['dollar']] = np.nan
                            new_row[cols['cents']] = np.nan
                            new_row[cols['fn']] = ''
                            new_row[cols['ln']] = ''
                            new_row[cols['occ']] = np.nan
                    result.append(new_row)
                split_applied = True
                break
            elif split_type == 'occupation':
                actual_set = {norm(row.get(cols['occ'])) for cols in GROUP_COLS
                              if norm(row.get(cols['occ']))}
                if actual_set != target_set:
                    continue
                # Group sub-columns by occupation signature
                sigs = {}
                for i, cols in enumerate(GROUP_COLS):
                    sig = norm(row.get(cols['occ']))
                    sigs.setdefault(sig, []).append(i)
                non_empty = {sig: idxs for sig, idxs in sigs.items() if sig != ''}
                empty_idxs = sigs.get('', [])
                first_sig = next(iter(non_empty))
                non_empty[first_sig] = non_empty[first_sig] + empty_idxs
                for occ, idxs in non_empty.items():
                    new_row = row.to_dict()
                    for i, cols in enumerate(GROUP_COLS):
                        new_row[cols['occ']] = occ if occ else np.nan
                        if i not in idxs:
                            new_row[cols['dollar']] = np.nan
                            new_row[cols['cents']] = np.nan
                            new_row[cols['fn']] = ''
                            new_row[cols['ln']] = ''
                    result.append(new_row)
                split_applied = True
                break
        if not split_applied:
            result.append(row.to_dict())

    return pd.DataFrame(result, columns=df.columns).reset_index(drop=True)


def DeNaN(series):
    return series.apply(lambda x: "" if not isinstance(x, str) else x)


def CleanSingleColumn(df, state):
    df['Name'] = DeNaN(df['First Name']) + " " + DeNaN(df['Last Name'])
    df.loc[df.query('state.isna() and town.isna()').index, 'state'] = state
    df['state_data'] = state
    df['state_data_index'] = np.arange(1, df.shape[0] + 1, 1)
    change_df = pd.DataFrame(columns=['old', 'new', 'type', 'state'])
    return df, change_df


def LoadNYData(indir):
    ny_raw = pd.read_excel(indir / "orig/NY/NY_CD.xlsx",
                           header=11, usecols='H, I, M, N, X, Y, AC, AD, AM, AN, AR, AS')
    ny_raw.columns = ['First Name', 'Last Name', '6p_Dollar', '6p_Cents',
                      'First Name.1', 'Last Name.1', '6p_def_Dollar', '6p_def_Cents',
                      'First Name.2', 'Last Name.2', '3p_Dollar', '3p_Cents']
    ny_raw['Name 1'] = DeNaN(ny_raw['First Name']) + " " + DeNaN(ny_raw['Last Name'])
    ny_raw['Name 2'] = DeNaN(ny_raw['First Name.1']) + " " + DeNaN(ny_raw['Last Name.1'])
    ny_raw['Name 3'] = DeNaN(ny_raw['First Name.2']) + " " + DeNaN(ny_raw['Last Name.2'])
    ny_raw['Name'] = list(
        list(set([x.replace("  ", " ").strip() for x in [n1, n2, n3] if x.strip() != ""]))
        for n1, n2, n3 in zip(ny_raw['Name 1'], ny_raw['Name 2'], ny_raw['Name 3']))
    ny_raw['Name'] = ny_raw['Name'].apply(lambda x: " | ".join(sorted(x)))
    ny_raw['town'] = np.nan
    ny_raw['state'] = 'NY'
    ny_raw['occupation'] = np.nan
    ny_raw['state_data'] = 'NY'
    ny_raw['state_data_index'] = np.arange(1, ny_raw.shape[0] + 1, 1)
    return ny_raw[AGG_COLS]


def BuildTownCrosswalk(CD_all, city_county_cw, text_replacements, list_of_states, match_log):
    geo_cw = pd.DataFrame(columns=['town', 'county', 'state', 'geo_level', 'new_town', 'new_state', 'country'])

    for state in list_of_states:
        state_cw = city_county_cw[city_county_cw['state'] == state]
        if state == 'VA':
            state_cw = city_county_cw[city_county_cw['state'].apply(lambda x: x in ['VA', 'WV'])]
        state_cw = state_cw[state_cw['county'].apply(lambda x: 'county' in x.lower() if not pd.isnull(x) else False)]
        towns = ProcessState(state, CD_all, state_cw, text_replacements, match_log)
        geo_cw = pd.concat([geo_cw, towns])

    return geo_cw


def ProcessState(state, CD_all, state_cw, text_replacements, match_log):
    towns = CD_all[CD_all['state'] == state][['town']].drop_duplicates()
    towns = towns[towns['town'].apply(lambda x: not pd.isnull(x))]

    # Text pre-processing: normalize raw town strings before geographic matching
    state_fixes = [(old, new, order) for st, old, new, order in text_replacements if st == state]
    towns = PreprocessTownStrings(towns, state_fixes)

    # Geographic matching
    primary_dict, towns = DirectTownMatch(state_cw, towns, col='primary_city', towncol='town',
                                          match_log=match_log, state=state)
    towns['geo_level'] = towns['county'].apply(lambda x: 'town' if not pd.isnull(x) else np.nan)

    if state == 'CT':
        unmatched = towns[towns['county'].apply(pd.isnull)]['town']
        towns = FuzzyMatch(unmatched, towns, state_cw, primary_dict, dict_matchcol='primary_city', initial=True,
                           score_threshold=85, match_log=match_log, state=state)
        towns = AddType(towns)
        towns = FuzzyMatchUnmatchedTowns(towns, state_cw, primary_dict, match_log=match_log, state=state)

    if state == 'GA':
        towns = DirectCountyMatchAndType(state_cw, towns, towncol='town', loc_type='county',
                                         match_log=match_log, state=state)

    if state == 'MD':
        towns = DirectCountyMatchAndType(state_cw, towns, towncol='town2', loc_type='county',
                                         match_log=match_log, state=state)
        towns = FuzzyMatchUnmatchedTowns(towns, state_cw, primary_dict, col='county', loc_type='county',
                                         threshold=86, match_log=match_log, state=state)
        towns = FuzzyMatchUnmatchedTowns(towns, state_cw, primary_dict, match_log=match_log, state=state)
        towns['county'] = towns['county'].apply(
            lambda x: x.replace('Baltimore City', 'Baltimore County') if not pd.isnull(x) else x)
        towns = AddType(towns)

    if state == 'NC':
        towns = DirectCountyMatchAndType(state_cw, towns, towncol='town', loc_type='county',
                                         match_log=match_log, state=state)
        towns = FuzzyMatchUnmatchedTowns(towns, state_cw, primary_dict, match_log=match_log, state=state)

    if state == 'NH':
        towns = DirectTownMatchNull(state_cw, towns, col='acceptable_cities', towncol='town',
                                    match_log=match_log, state=state)
        towns = AddType(towns)
        towns = FuzzyMatchUnmatchedTowns(towns, state_cw, primary_dict, match_log=match_log, state=state)
        towns = DirectCountyMatchAndType(state_cw, towns, towncol='town2', match_log=match_log, state=state)

    if state == 'NJ':
        towns = FuzzyMatchUnmatchedTowns(towns, state_cw, primary_dict, match_log=match_log, state=state)
        towns = DirectCountyMatchAndType(state_cw, towns, towncol='town2', match_log=match_log, state=state)

    if state == 'PA':
        towns = DirectCountyMatchAndType(state_cw, towns, towncol='town', loc_type='county',
                                         match_log=match_log, state=state)
        towns = DirectTownMatchNull(state_cw, towns, col='acceptable_cities', towncol='town',
                                    match_log=match_log, state=state)
        towns = AddType(towns)
        towns = DirectCountyMatchAndType(state_cw, towns, towncol='town2', match_log=match_log, state=state)
        towns = DirectCountyMatchAndType(state_cw, towns, towncol='town', loc_type='county',
                                         match_log=match_log, state=state)
        towns = DirectTownMatchNull(state_cw, towns, col='acceptable_cities', towncol='town',
                                    match_log=match_log, state=state)
        towns = AddType(towns)
        towns = DirectCountyMatchAndType(state_cw, towns, towncol='town2', match_log=match_log, state=state)
        towns = FuzzyMatchUnmatchedTowns(towns, state_cw, primary_dict, match_log=match_log, state=state)
        towns = FuzzyMatchUnmatchedTowns(towns, state_cw, primary_dict, col='county', loc_type='county',
                                         match_log=match_log, state=state)
        towns = FuzzyMatchUnmatchedTowns(towns, state_cw, primary_dict, match_log=match_log, state=state)
        towns = FuzzyMatchUnmatchedTowns(towns, state_cw, primary_dict, col='county', loc_type='county',
                                         match_log=match_log, state=state)

    if state == 'RI':
        towns = FuzzyMatchUnmatchedTowns(towns, state_cw, primary_dict, match_log=match_log, state=state)

    if state == 'SC':
        towns = DirectTownMatchNull(state_cw, towns, col='acceptable_cities', towncol='town2',
                                    match_log=match_log, state=state)
        towns = AddType(towns)
        towns = FuzzyMatchUnmatchedTowns(towns, state_cw, primary_dict, match_log=match_log, state=state)
        towns = FuzzyMatchUnmatchedTowns(towns, state_cw, primary_dict, col='county', loc_type='county',
                                         match_log=match_log, state=state)

    if state == 'MA':
        towns = FuzzyMatchUnmatchedTowns(towns, state_cw, primary_dict, match_log=match_log, state=state)

    if state == 'VA':
        towns = FuzzyMatchUnmatchedTowns(towns, state_cw, primary_dict, match_log=match_log, state=state)
        towns = FuzzyMatchUnmatchedTowns(towns, state_cw, primary_dict, col='county', loc_type='county',
                                         match_log=match_log, state=state)

    if state == 'DE':
        towns = FuzzyMatchUnmatchedTowns(towns, state_cw, primary_dict, loc_type='county',
                                         match_log=match_log, state=state)
        towns = FuzzyMatchUnmatchedTowns(towns, state_cw, primary_dict, col='county', loc_type='county',
                                         match_log=match_log, state=state)

    unmatched = towns[towns['county'].apply(lambda x: pd.isnull(x))]
    for tn in unmatched['town']:
        match_log.append({'state': state, 'town_original': tn,
                          'town_preprocessed': towns.loc[towns['town'] == tn, 'town2'].iloc[0]
                          if 'town2' in towns.columns else tn,
                          'new_town': np.nan, 'county': np.nan, 'new_state': np.nan,
                          'match_method': 'unmatched'})
    towns = towns[towns['county'].apply(lambda x: not pd.isnull(x))]
    towns['state'] = state
    towns['new_state'] = towns['state']
    if state not in ['GA']:
        towns.drop('town2', axis=1, inplace=True)

    return towns


def PreprocessTownStrings(towns, state_fixes):
    if not state_fixes:
        towns['town2'] = towns['town']
        return towns
    order1 = [(old, new) for old, new, order in state_fixes if order == 1]
    order2 = [(old, new) for old, new, order in state_fixes if order == 2]
    order3 = [(old, new) for old, new, order in state_fixes if order == 3]
    towns['town2'] = towns['town'].apply(lambda x: NormalizeTownString(x, order1))
    if order2:
        towns['town2'] = towns['town2'].apply(lambda x: NormalizeTownString(x, order2))
    if order3:
        towns['town2'] = towns['town2'].apply(lambda x: NormalizeTownString(x, order3))
    return towns


def NormalizeTownString(town, replacements):
    for old, new in replacements:
        town = town.replace(old, new)
    return town.strip()


def DirectTownMatch(state_cw_given, towns, col='primary_city', towncol='town', match_log=None, state=None):
    state_cw = state_cw_given[[col, 'county']].groupby(col).county.agg(lambda x: x.mode()[0]).reset_index()
    primary_dict = dict(zip(state_cw[col], state_cw['county']))
    method = 'crosswalk_primary_city' if col == 'primary_city' else 'crosswalk_acceptable_city'

    if col == 'primary_city':
        county_vals = towns[towncol].apply(lambda x: primary_dict.get(x, None))
        towns['county'] = pd.array(county_vals.tolist(), dtype=object)
        towns['new_town'] = pd.array(
            [tn if cty is not None else None for cty, tn in zip(county_vals, towns['town'])], dtype=object)
    if col == 'acceptable_cities':
        for ind in towns.index:
            town = towns.loc[ind, 'town']
            county = state_cw[state_cw[col].apply(lambda x: town in x if not pd.isnull(x) else False)][
                'county'].tolist()
            if len(county) > 0:
                towns.loc[ind, 'county'] = county[0]
                towns.loc[ind, 'new_town'] = town

    if match_log is not None:
        matched = towns[towns['county'].apply(lambda x: not pd.isnull(x))]
        town_col = towncol
        for idx, row in matched.iterrows():
            match_log.append({
                'state': state,
                'town_original': row['town'],
                'town_preprocessed': row.get('town2', row['town']),
                'new_town': row['new_town'],
                'county': row['county'],
                'new_state': state,
                'match_method': method,
            })

    return primary_dict, towns


def AddType(towns, loc_type='town'):
    towns['geo_level'] = [geo_level if not pd.isnull(geo_level) else loc_type if not pd.isnull(county) else np.nan for
                          geo_level, county in
                          zip(towns['geo_level'], towns['county'])]
    return towns


def FuzzyMatch(unmatched_towns, towns, crosswalk, primary_dict, dict_matchcol='primary_city', initial=True,
               score_threshold=85, match_log=None, state=None):
    method = 'fuzzy_city_name' if dict_matchcol == 'primary_city' else 'fuzzy_county_name'
    printedtowns = []
    for town in unmatched_towns:
        match_tuple = process.extractOne(town, [x for x in crosswalk[dict_matchcol] if not pd.isnull(x)])
        score = match_tuple[1]
        match = match_tuple[0]
        if score >= score_threshold:
            if dict_matchcol == 'primary_city':
                county = primary_dict[match]
            if dict_matchcol == 'county':
                county = match
            if initial:
                town_index = towns[towns['town'] == town].index
                towns.loc[town_index, 'county'] = county
                towns.loc[town_index, 'new_town'] = match
                if match_log is not None:
                    match_log.append({
                        'state': state,
                        'town_original': town,
                        'town_preprocessed': town,
                        'new_town': match,
                        'county': county,
                        'new_state': state,
                        'match_method': method,
                    })
            else:
                original_town = towns[towns['town2'] == town]['town'].tolist()
                if town not in printedtowns:
                    printedtowns.append(town)
                town_index = towns[towns['town'].apply(lambda x: x in original_town)].index
                for idx in town_index:
                    towns.at[idx, 'county'] = county
                    towns.at[idx, 'new_town'] = match
                    if match_log is not None:
                        match_log.append({
                            'state': state,
                            'town_original': towns.at[idx, 'town'],
                            'town_preprocessed': town,
                            'new_town': match,
                            'county': county,
                            'new_state': state,
                            'match_method': method,
                        })
    return towns


def FuzzyMatchUnmatchedTowns(towns, state_cw, primary_dict, col='primary_city', loc_type='town', threshold=85,
                              match_log=None, state=None):
    unmatched = [x for x in towns[towns['county'].apply(pd.isnull)]['town2'] if x != '']
    towns = FuzzyMatch(unmatched, towns, state_cw, primary_dict, dict_matchcol=col, initial=False,
                       score_threshold=threshold, match_log=match_log, state=state)
    return AddType(towns, loc_type)


def DirectCountyMatchAndType(state_cw, towns, towncol, loc_type='county', match_log=None, state=None):
    towns = DirectCountyMatch(state_cw, towns, towncol=towncol, match_log=match_log, state=state)
    return AddType(towns, loc_type)


def DirectCountyMatch(state_cw, towns, towncol='town', match_log=None, state=None):
    counties = state_cw['county'].unique()
    nanindex = towns[towns['county'].apply(lambda x: pd.isnull(x))].index
    towns.loc[nanindex, 'county'] = towns.loc[nanindex, towncol].apply(
        lambda x: x if x in counties.tolist() else np.nan)
    towns2 = towns.loc[nanindex]
    nanindex2 = towns2[towns2['county'].apply(lambda x: not pd.isnull(x))].index
    if match_log is not None:
        for idx in nanindex2:
            row = towns.loc[idx]
            match_log.append({
                'state': state,
                'town_original': row['town'],
                'town_preprocessed': row.get('town2', row['town']),
                'new_town': row[towncol],
                'county': row['county'],
                'new_state': state,
                'match_method': 'crosswalk_county_name',
            })
    towns.loc[nanindex2, 'new_town'] = towns.loc[nanindex2, towncol]
    return towns


def DirectTownMatchNull(state_cw, towns, col='acceptable_cities', towncol='town', match_log=None, state=None):
    null_ind = towns[towns['county'].apply(pd.isnull)].index
    _, tn = DirectTownMatch(state_cw, towns.loc[null_ind], col=col, towncol=towncol,
                            match_log=match_log, state=state)
    towns.loc[null_ind] = tn
    return towns


def ApplyTownFixes(geo_cw, df_manual, match_log):
    for ind in df_manual.index:
        match_town = df_manual.loc[ind, 'town']
        match_state = df_manual.loc[ind, 'state']

        df_query = geo_cw.copy()
        if not pd.isnull(match_town):
            if match_town == "*":
                df_query = df_query.query('town.isnull()')
            else:
                df_query = df_query.query(f'town == "{match_town}"')
        if not pd.isnull(match_state):
            df_query = df_query.query(f'state == "{match_state}"')

        geo_cw.loc[df_query.index, ['new_town', 'county', 'new_state', 'geo_level', 'country']] = \
            df_manual.loc[ind, ['new_town', 'county', 'new_state', 'geo_level', 'country']].tolist()

        new_vals = df_manual.loc[ind, ['new_town', 'county', 'new_state', 'geo_level', 'country']]
        for idx in df_query.index:
            orig = df_query.loc[idx]
            match_log.append({
                'state': orig['state'],
                'town_original': orig['town'],
                'town_preprocessed': orig['town'],
                'new_town': new_vals['new_town'],
                'county': new_vals['county'],
                'new_state': new_vals['new_state'],
                'match_method': 'manual_override',
            })

    return geo_cw


def ApplyPersonStateFixes(CD_all, person_state_df):
    for _, row in person_state_df.iterrows():
        idx = CD_all[CD_all['Name'].apply(lambda x: row['name_contains'] in x)].index
        CD_all.loc[idx, 'new_state'] = row['new_state']
    return CD_all


def ComputeTotals(CD_all):
    for prefix in ['6p', '6p_def', '3p']:
        CD_all[f'{prefix}_total'] = (
            CD_all[f'{prefix}_Dollar'].apply(lambda x: 0 if pd.isnull(x) else x)
            + CD_all[f'{prefix}_Cents'].apply(lambda x: 0 if pd.isnull(x) else x) / 100
        )
    CD_all = CD_all[CD_all.apply(
        lambda x: not (x['6p_total'] == 0 and x['6p_def_total'] == 0 and x['3p_total'] == 0), axis=1
    )].reset_index(drop=True)
    return CD_all


if __name__ == "__main__":
    Main()
