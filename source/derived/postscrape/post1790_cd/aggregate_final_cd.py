from pathlib import Path
import pandas as pd
from source.lib.ancestry_scraper.config import STATE_ABBREVIATIONS
from source.lib.SaveData import SaveData

# Pipeline documented in source/derived/postscrape/post1790_cd/pipeline_documentation.md

INDIR_RAW      = Path("source/raw/post1790_cd")
INDIR_PRESCRAPE = Path("output/derived/prescrape/post1790_cd")
INDIR_SCRAPE   = Path("output/scrape/post1790_cd_census_match")
OUTDIR         = Path("output/derived/postscrape/post1790_cd")
OUTDIR.mkdir(parents=True, exist_ok=True)

STATEDICT     = STATE_ABBREVIATIONS
STATEDICT_REV = {v: k for k, v in STATE_ABBREVIATIONS.items()}

# State abbreviation preferences when same name appears in multiple states at state-level only
# TODO: externalize to source/raw/post1790_cd/corrections/name/postscrape/state_preferences.csv
PICKSTATE = {
    'Samuel W Johnson': 'NY', 'Josiah Watson': 'VA', 'Gerrard Alexander': 'VA',
    'Benjamin Tallmadge': 'CT', 'Edward Chinn': 'NY', 'Forman Mount': 'PA',
    'Thomas Robinson': 'DE', 'Thomas Ross': 'SC', 'William Applegate': 'NJ',
}


def Main():
    cd_clean      = pd.read_csv(INDIR_PRESCRAPE / 'geo_standardized_CD_post1790.csv', index_col=0).fillna("").drop_duplicates().reset_index()
    scraped_names = pd.read_csv(INDIR_SCRAPE / 'name_list_scraped.csv', index_col=0).fillna("").drop_duplicates()
    match_df      = pd.read_csv(INDIR_SCRAPE / 'scrape_results.csv', index_col=0).fillna("").drop_duplicates()
    name_df       = pd.read_csv(INDIR_PRESCRAPE / 'check/name_changes_list.csv', index_col=0).fillna("").drop_duplicates()

    cd_clean  = AddOccupationsFromTitle(cd_clean)
    merged    = MergeScrapedData(cd_clean, name_df, scraped_names)
    merged    = GroupByAncestryMatchIndex(merged)

    rep_names = pd.read_csv(INDIR_RAW / 'corrections/name/postscrape/name_agg.csv')
    rep_names['original'] = rep_names['original'].apply(lambda x: x.replace("\t", " "))
    rep_names['new']      = rep_names['new'].apply(lambda x: x.replace("\t", " "))
    rep_names['location'] = rep_names['location'].apply(lambda x: x.replace("\t", " ") if not pd.isnull(x) else x)

    merged = GroupByFuzzyCorrections(merged, rep_names)
    merged = UnifyLocationWithinState(merged)

    df_final = AggregateIntoPersonTable(merged)
    df_final, exception_names = ImputeLocationFromPartners(df_final)

    namechange_dict = BuildNameChangeDictionary(df_final, exception_names)
    df_final = UnifyNameSpellings(df_final, namechange_dict)
    df_final = ApplyManualAdjustments(df_final)

    state_group_names = pd.read_csv(INDIR_RAW / 'corrections/name/postscrape/group_name_state.csv')
    df_final = CorrectWrongStateAssignments(df_final, state_group_names)

    match_df = AddVillageInfo(match_df)
    match_df = ExtractOccupationsFromCensus(match_df)
    df_final = ResolveMultipleMatches(df_final, match_df)
    df_final, match_df = EliminateBroadLocationMatches(df_final, match_df)
    df_final, match_df = ImputeLocationFromCensus(df_final, match_df)

    occ_data = pd.read_csv(INDIR_RAW / 'corrections/occ/postscrape/occ_fix.csv')
    df_final = StandardizeOccupations(df_final, match_df, occ_data)
    df_final, match_df = ReindexMatchData(df_final, match_df)
    df_final = AggregateDebtTotals(df_final)

    df_final['Group County'] = df_final['Group County'].apply(
        lambda x: x.replace('County County', 'County') if not pd.isnull(x) else x
    )

    keys = ['Group Name', 'Group State', 'Group County', 'Group Town',
            'Group Name Type', 'Group Match Index', 'Group Match Url']
    df_final[keys] = df_final[keys].fillna('')

    match_out = match_df.drop('index_temp', axis=1).reset_index(drop=True)
    SaveData(match_out, ['index_new'], OUTDIR / 'match_data_CD.csv',
             log_file=OUTDIR / 'match_data_CD.log')
    SaveData(df_final.reset_index(drop=True), keys,
             OUTDIR / 'final_data_CD.csv',
             log_file=OUTDIR / 'final_data_CD.log')


def AddOccupationsFromTitle(df):
    # TODO: externalize keyword→occupation mapping to source/raw/post1790_cd/corrections/occ/prescrape/title_keywords.csv
    for keyword, title in [
        ('treasurer', 'Treasurer'),
        (' adm', 'Administrator'), ('adm ', 'Administrator'),
        (' trust ', 'Administrator'),
        ('guard', 'Guardian'),
        ('school', 'School Committee'),
    ]:
        idx = df[df['Name'].apply(lambda x: keyword in x.lower())].index
        if keyword == 'guard':
            df.loc[idx, 'occupation'] = [
                ele if ele != 'Yeoman' else 'Guardian | Yeoman'
                for ele in df.loc[idx, 'occupation']
            ]
        else:
            df.loc[idx, 'occupation'] = [
                ele if ele != '' else title for ele in df.loc[idx, 'occupation']
            ]
    return df


def MergeScrapedData(cd_clean, name_df, scraped_names):
    merged = pd.merge(cd_clean, name_df, how='left',
                      on=['Name', 'new_town', 'county', 'new_state', 'country', 'geo_level'])
    scraped_names = scraped_names.rename(columns={'name_type': 'geo_level'})
    merged = pd.merge(merged,
                      scraped_names[['Fn_Fix', 'Ln_Fix', 'new_town', 'county', 'new_state', 'country', 'geo_level',
                                     'url', 'Match Index', 'Match Status']],
                      how='left',
                      on=['Fn_Fix', 'Ln_Fix', 'new_town', 'county', 'new_state', 'country', 'geo_level'])
    merged['Full Search Name'] = merged['Fn_Fix'] + ' ' + merged['Ln_Fix']
    return merged


def GroupByAncestryMatchIndex(df):
    grouped = df[df['Match Index'] != ""].groupby('Match Index').agg(
        {'Full Search Name': lambda x: list(set(x))}
    ).reset_index()
    group_name_df = grouped[grouped['Full Search Name'].apply(lambda x: len(x) > 1)]
    # Use longest name as representative — more characters usually means a more complete spelling
    # sorted() ensures deterministic tiebreaking: pick lexicographically smallest when lengths tie
    group_name_df['Rep Name'] = group_name_df['Full Search Name'].apply(lambda x: max(sorted(x), key=len))
    group_name_df = group_name_df.explode('Full Search Name').reset_index(drop=True)

    # TODO: externalize these name canonical overrides and drops to a corrections CSV
    group_name_df.loc[group_name_df[group_name_df['Full Search Name'].apply(
        lambda x: 'Israel Joseph' in x)].index, 'Rep Name'] = 'Israel Joseph'
    group_name_df.loc[group_name_df[group_name_df['Full Search Name'].apply(
        lambda x: 'William Larned' in x or 'William Learned' in x)].index, 'Rep Name'] = 'William Larned'
    group_name_df.loc[group_name_df[group_name_df['Full Search Name'].apply(
        lambda x: 'Mathew Watson' in x or 'Matthew Watson' in x)].index, 'Rep Name'] = 'Mathew Watson'
    group_name_df.loc[group_name_df[group_name_df['Full Search Name'].apply(
        lambda x: 'Thomas M Willing' in x or 'Thomas Mcwilling' in x)].index, 'Rep Name'] = 'Thomas M Willing'
    group_name_df.loc[group_name_df[group_name_df['Full Search Name'].apply(
        lambda x: 'Elijah Austin' in x or 'Elijah Auston' in x)].index, 'Rep Name'] = 'Elijah Austin'
    group_name_df.loc[group_name_df[group_name_df['Full Search Name'].apply(
        lambda x: 'Thomas Lloyd Halsey' in x or 'Thomas Cloyd Halsey' in x)].index, 'Rep Name'] = 'Thomas Lloyd Halsey'
    group_name_df.drop(group_name_df[group_name_df['Rep Name'] + group_name_df[
        'Full Search Name'] == 'Samuel Vernon 2NdSamuel Vernon Ii'].index, inplace=True)

    group_name_df = group_name_df[group_name_df['Full Search Name'] != group_name_df['Rep Name']]

    df[['Group Name', 'Group Town', 'Group County', 'Group State', 'Group Country', 'Group Name Type',
        'Group Match Index', 'Group Match Status', 'Group Match Url']] = df[
        ['Full Search Name', 'new_town', 'county', 'new_state', 'country', 'geo_level',
         'Match Index', 'Match Status', 'url']]

    for ind in group_name_df.index:
        match_ind, full_name, rep_name = group_name_df.loc[ind, ['Match Index', 'Full Search Name', 'Rep Name']]
        change_ind = df[df.apply(
            lambda x: x['Match Index'] == match_ind and (x['Full Search Name'] == full_name or x['Full Search Name'] == rep_name),
            axis=1)].index
        info_ind = df[df.apply(
            lambda x: x['Match Index'] == match_ind and x['Full Search Name'] == rep_name, axis=1)].index

        if df.loc[info_ind, ['Group Name', 'Group Town', 'Group County', 'Group State', 'Group Country',
                              'Group Name Type']].drop_duplicates().shape[0] > 1:
            possibilities = df.loc[info_ind, ['Group Name', 'Group Town', 'Group County', 'Group State',
                                              'Group Country', 'Group Name Type', 'Group Match Index',
                                              'Group Match Status', 'Group Match Url']].drop_duplicates()
            if possibilities[possibilities['Group Name Type'] == 'town'].shape[0] == 1:
                possibilities = possibilities[possibilities['Group Name Type'] == 'town'].values.tolist()
            elif possibilities[possibilities['Group Name Type'] == 'county'].shape[0] == 1:
                possibilities = possibilities[possibilities['Group Name Type'] == 'county'].values.tolist()
            elif possibilities[possibilities['Group Name Type'] == 'state'].shape[0] == 1 or rep_name == 'Benjamin Tallmadge':
                possibilities = possibilities[possibilities['Group Name Type'] == 'state'].values.tolist()
                if rep_name == 'Benjamin Tallmadge':
                    possibilities = [ele for ele in possibilities if ele[3] == 'CT']
            else:
                possibilities = possibilities[possibilities['Group Name Type'] == 'country'].values.tolist()
        else:
            possibilities = df.loc[info_ind, ['Group Name', 'Group Town', 'Group County', 'Group State',
                                              'Group Country', 'Group Name Type', 'Group Match Index',
                                              'Group Match Status', 'Group Match Url']].drop_duplicates().values.tolist()
        assert len(possibilities) == 1
        df.loc[change_ind, ['Group Name', 'Group Town', 'Group County', 'Group State', 'Group Country',
                             'Group Name Type', 'Group Match Index', 'Group Match Status',
                             'Group Match Url']] = [possibilities[0]] * len(change_ind)
    return df


def GroupByFuzzyCorrections(df, rep_names):
    for og_name, new_name, loc in zip(rep_names['original'], rep_names['new'], rep_names['location']):
        if pd.isnull(loc):
            vals = df[df['Group Name'] == new_name][
                ['Group Name', 'Group Town', 'Group County', 'Group State', 'Group Country', 'Group Name Type',
                 'Group Match Index', 'Group Match Status', 'Group Match Url']].drop_duplicates().values.tolist()
        else:
            town, county, state, nametype = ParseLocationString(loc, loc.split(" | ")[-1])
            vals = df[df.apply(
                lambda x: x['Group Name'] == new_name and x['Group Town'] == town and x['Group County'] == county
                          and x['Group State'] == state and x['Group Name Type'] == nametype, axis=1)][
                ['Group Name', 'Group Town', 'Group County', 'Group State', 'Group Country', 'Group Name Type',
                 'Group Match Index', 'Group Match Status', 'Group Match Url']].drop_duplicates().values.tolist()
        if new_name == 'Henry Huttenstein':
            vals = [ele for ele in vals if ele[1] == 'Lancaster']

        if df[df.apply(lambda x: x['Group Name'] == og_name, axis=1)][
                ['Group Town', 'Group County', 'Group State', 'Group Country', 'Group Name Type']].drop_duplicates().shape[0] > 1:
            if og_name == 'Benjamin Brown' or og_name == 'William Wheater':
                rep_ind = df[df.apply(lambda x: x['Group Name'] == og_name and x['Group State'] == 'RI', axis=1)].index
            else:
                rep_ind = df[df.apply(
                    lambda x: x['Group Name'] == og_name and x['Group Town'] == town and x['Group County'] == county
                              and x['Group State'] == state and x['Group Name Type'] == nametype, axis=1)].index
        else:
            rep_ind = df[df.apply(lambda x: x['Group Name'] == og_name, axis=1)].index

        if len(vals) == 1:
            df.loc[rep_ind, ['Group Name', 'Group Town', 'Group County', 'Group State', 'Group Country',
                             'Group Name Type', 'Group Match Index', 'Group Match Status',
                             'Group Match Url']] = vals[0]
    return df


def ParseLocationString(location, nametype):
    if nametype == 'town':
        return location.split(" | ")[0], location.split(" | ")[1], location.split(" | ")[2], location.split(" | ")[3]
    elif nametype == 'county':
        return "", location.split(" | ")[0], location.split(" | ")[1], location.split(" | ")[2]
    else:
        return "", "", location.split(" | ")[0], location.split(" | ")[1]


def UnifyLocationWithinState(df):
    # When a person has multiple location entries within the same state that are non-contradicting
    # (same town and county, just at different specificity levels), keep the most specific one.
    dup_state = df[['Group Name', 'Group State', 'Group County', 'Group Town', 'Group Name Type']].drop_duplicates(
    ).groupby(['Group Name', 'Group State']).count().reset_index()

    for ind in dup_state[dup_state['Group County'] > 1].index:
        name, state = dup_state.loc[ind, ['Group Name', 'Group State']]
        vals    = df[df.apply(lambda x: x['Group Name'] == name and x['Group State'] == state, axis=1)]['Group Name Type'].drop_duplicates().tolist()
        towns   = [ele for ele in df[df.apply(lambda x: x['Group Name'] == name and x['Group State'] == state, axis=1)]['Group Town'].drop_duplicates().tolist() if ele != ""]
        counties = [ele for ele in df[df.apply(lambda x: x['Group Name'] == name and x['Group State'] == state, axis=1)]['Group County'].drop_duplicates().tolist() if ele != ""]

        if len(vals) > 1 and dup_state.loc[ind, 'Group County'] < 3 and len(towns) == 1 and len(counties) == 1:
            if 'town' in vals:
                change_val = df.loc[df.apply(lambda x: x['Group Name'] == name and x['Group State'] == state and x['Group Name Type'] == 'town', axis=1),
                                    ['Group Name', 'Group Town', 'Group County', 'Group State', 'Group Name Type', 'Group Match Index', 'Group Match Status', 'Group Match Url']].drop_duplicates().values
            elif 'county' in vals:
                change_val = df.loc[df.apply(lambda x: x['Group Name'] == name and x['Group State'] == state and x['Group Name Type'] == 'county', axis=1),
                                    ['Group Name', 'Group Town', 'Group County', 'Group State', 'Group Name Type', 'Group Match Index', 'Group Match Status', 'Group Match Url']].drop_duplicates().values
            else:
                change_val = df.loc[df.apply(lambda x: x['Group Name'] == name and x['Group State'] == state and x['Group Name Type'] == 'state', axis=1),
                                    ['Group Name', 'Group Town', 'Group County', 'Group State', 'Group Name Type', 'Group Match Index', 'Group Match Status', 'Group Match Url']].drop_duplicates().values

            change_ind = df[df.apply(lambda x: x['Group Name'] == name and x['Group State'] == state, axis=1)].index
            df.loc[change_ind, ['Group Name', 'Group Town', 'Group County', 'Group State', 'Group Name Type',
                                'Group Match Index', 'Group Match Status', 'Group Match Url']] = change_val[0]
    return df


def AggregateIntoPersonTable(df):
    # data_index: "{state_file}_{row_index}" e.g. "PA_42"
    # assets: "{data_index} : {6% face}, {6% deferred face}, {3% face}" — the three CD debt types
    df['data_index'] = df['state_data'] + "_" + df['state_data_index'].astype(str)
    df['assets'] = (df['data_index'] + " : " + df['6p_total'].astype(str) + ", "
                    + df['6p_def_total'].astype(str) + ", " + df['3p_total'].astype(str))

    na_ind = df[df['Group Name'].isnull()].index
    df.loc[na_ind, 'Group Name']        = df.loc[na_ind, 'Name']
    df.loc[na_ind, 'Full Search Name']  = df.loc[na_ind, 'Name']
    df.loc[na_ind, 'Group Match Index'] = 'Unsearchable (not a name)'
    df.loc[na_ind, 'Group Match Url']   = 'Unsearchable (not a name)'
    df.loc[na_ind, 'Name_Fix']          = df.loc[na_ind, 'Name']

    df['Group Name'] = df['Group Name'].apply(
        lambda x: " ".join([ele.capitalize() if "ii" not in ele.lower() else ele.upper() for ele in x.split(" ")])
    )

    df.loc[df[df['Name'].apply(lambda x: 'Bowdle' in x)].index, 'Group Town'] = 'Annapolis'
    df.loc[df[df['Name'].apply(lambda x: 'Gassaway Watkins' in x)].index, 'Group Town'] = 'Annapolis'

    df_final = df.fillna("").groupby(
        ['Group Name', 'Group State', 'Group County', 'Group Town', 'Group Name Type',
         'Group Match Index', 'Group Match Url']
    ).agg({
        'Name_Fix':          lambda x: list(set(x)),
        'Full Search Name':  JoinNameList,
        'assets':            JoinNameList,
        'occupation':        JoinNameList,
    }).reset_index()
    return df_final


def JoinNameList(lst):
    return " | ".join(sorted(list(set([ele for ele in lst if ele != ""]))))


def ImputeLocationFromPartners(df_final):
    # When a person appears in multiple locations within a state, use co-holders (partners)
    # who share a row (Name_Fix entry) to resolve which location is correct.
    # Loop until stable: each iteration may resolve new cases that unblock others.
    exception_names = []

    dup_state_2 = df_final.explode("Name_Fix")[
        ['Name_Fix', 'Group Name', 'Group State', 'Group County', 'Group Town', 'Group Name Type']].drop_duplicates()
    dup_state_2['Name_Fix'] = dup_state_2['Name_Fix'].apply(lambda x: x.split(" | "))
    dup_state_2 = dup_state_2.explode('Name_Fix').drop_duplicates().groupby(
        ['Name_Fix', 'Group State']).nunique().reset_index()

    while len(exception_names) != dup_state_2[dup_state_2.apply(
            lambda x: x['Group County'] > 1 and x['Group Name'] > 1, axis=1)].shape[0]:
        dup_state_2 = df_final.explode("Name_Fix")[
            ['Name_Fix', 'Group Name', 'Group State', 'Group County', 'Group Town', 'Group Name Type']].drop_duplicates()
        dup_state_2['Name_Fix'] = dup_state_2['Name_Fix'].apply(lambda x: x.split(" | "))
        dup_state_2 = dup_state_2.explode('Name_Fix').drop_duplicates().groupby(
            ['Name_Fix', 'Group State']).nunique().reset_index()

        for ind in dup_state_2[dup_state_2.apply(lambda x: x['Group County'] > 1 and x['Group Name'] > 1, axis=1)].index:
            name, state = dup_state_2.loc[ind, ['Name_Fix', 'Group State']]
            matched = df_final[NameInState(df_final, name, state)]
            vals    = matched['Group Name Type'].drop_duplicates().tolist()
            towns   = [ele for ele in matched['Group Town'].drop_duplicates().tolist() if ele != ""]
            counties = [ele for ele in matched['Group County'].drop_duplicates().tolist() if ele != ""]

            if len(towns) <= 1 and len(counties) == 1:
                if 'town' in vals:
                    change_val = matched.loc[matched['Group Name Type'] == 'town',
                                             ['Group Town', 'Group County', 'Group State', 'Group Name Type']].drop_duplicates().values
                elif 'county' in vals:
                    change_val = matched.loc[matched['Group Name Type'] == 'county',
                                             ['Group Town', 'Group County', 'Group State', 'Group Name Type']].drop_duplicates().values
                else:
                    change_val = matched.loc[matched['Group Name Type'] == 'state',
                                             ['Group Town', 'Group County', 'Group State', 'Group Name Type']].drop_duplicates().values

                change_ind = matched.index
                assert len(change_val) == 1
                df_final.loc[change_ind, ['Group Town', 'Group County', 'Group State', 'Group Name Type']] = change_val[0]
            else:
                if [name, state] not in exception_names:
                    exception_names.append([name, state])

    return df_final, exception_names


def NameInState(df, name, state):
    return df.apply(
        lambda x: any(name in ele for ele in x['Name_Fix']) and x['Group State'] == state, axis=1)


def BuildNameChangeDictionary(df_final, exception_names):
    other_names = df_final[['Group Name', 'Group State', 'Group County', 'Group Town', 'Full Search Name']].copy()
    other_names['Full Search Name'] = other_names['Full Search Name'].apply(lambda x: x.split(" | "))
    other_names = other_names.explode('Full Search Name')
    namechange_dict = dict(zip(
        other_names['Full Search Name'] + other_names['Group Town'] + other_names['Group County'] + other_names['Group State'],
        other_names['Group Name']
    ))
    namechange_dict['DesdeilyNY'] = 'Desdeily'
    namechange_dict['GrundNY'] = 'Grund'
    namechange_dict['Thomas Cloyd HalseyProvidenceProvidence CountyRI'] = 'Thomas Lloyd Halsey'

    for ele in exception_names:
        name, state = ele[0], ele[1]
        vals = df_final[NameInState(df_final, name, state)][
            ['Group Town', 'Group County', 'Group State']].drop_duplicates()
        for ind in vals.index:
            town, county, state = vals.loc[ind, 'Group Town'], vals.loc[ind, 'Group County'], vals.loc[ind, 'Group State']
            if name + town + county + state not in namechange_dict.keys():
                reps = [e for e in namechange_dict.keys() if name in e]
                if name == 'Samuel Vernon':
                    namechange_dict[name + town + county + state] = name
                else:
                    assert len(list(set([namechange_dict[ele] for ele in reps]))) == 1
                    namechange_dict[name + town + county + state] = namechange_dict[reps[0]]
    return namechange_dict


def UnifyNameSpellings(df_final, namechange_dict):
    # "ASDSD" prefix is a sentinel: dict.get returns "ASDSD{key}" when a name has no dict entry,
    # making unresolved lookups visible in output instead of silently returning None.
    df_final['Name_Fix_Transfer'] = df_final.apply(lambda x: " : ".join(list(set([(JoinNameList([namechange_dict.get(
        subele + x['Group Town'] + x['Group County'] + x['Group State'],
        "ASDSD" + subele + x['Group Town'] + x['Group County'] + x['Group State']) for subele in ele.split(" | ")]) + " / " + ele) for ele
        in x['Name_Fix']]))), axis=1)
    df_final['Name_Fix_Clean'] = df_final.apply(lambda x: " : ".join(list(set([JoinNameList([namechange_dict.get(
        subele + x['Group Town'] + x['Group County'] + x['Group State'],
        "ASDSD" + subele + x['Group Town'] + x['Group County'] + x['Group State']) for subele in ele.split(" | ")]) for ele
        in x['Name_Fix']]))), axis=1)
    df_final.drop('Name_Fix', axis=1, inplace=True)
    return df_final


def ApplyManualAdjustments(df_final):
    # TODO: externalize these four person overrides to source/raw/post1790_cd/corrections/name/postscrape/manual_adjustments.csv
    df_final.loc[df_final[df_final['Group Name'] == 'Love Stone'].index,
                 ['Group Match Url', 'Name_Fix_Clean', 'Name_Fix_Transfer', 'assets', 'occupation']] = [
        'https://www.ancestrylibrary.com/search/collections/5058/?name=Love_Stone&name_x=1_1&residence=_charleston-south carolina-usa_552&residence_x=_1-0',
        'Joseph Vesey | Love Stone : Love Stone',
        'Joseph Vesey | Love Stone / Joseph Vesey | Love Stone : Love Stone / Love Stone',
        'SC_10 : 216.67, 108.33, 207.64 | SC_394 : 881.66, 2838.33, 856.64',
        'Administrators of Joseph Darrell | Widow']

    df_final.loc[df_final[df_final['Group Name'] == 'John Gale'].index,
                 ['Group Match Url', 'Group Match Index', 'Name_Fix_Clean', 'Name_Fix_Transfer', 'assets', 'occupation']] = [
        'https://www.ancestrylibrary.com/search/collections/5058/?name=John_Gale&name_x=1_1&residence=_Maryland-usa_23&residence_x=_1-0',
        '984 | 985', 'Ebenezer Finlays | John Gale : John Gale',
        'John Gale / John Gale : Ebenezer Finlays | John Gale / Ebenezer Finlays | John Gale',
        'MD_243 : 2148.66, 1074.34, 1409.32 | MD_244 : 1036.86, 518.43, 683.74 | PA_1080 : 176.58, 88.29, 201.48',
        ' | Executor of Ebenezer Finlay']

    df_final.loc[df_final[df_final['Group Name'] == 'Nathaniel Irwin'].index,
                 ['Group Match Index', 'Group Match Url', 'Name_Fix_Clean', 'Name_Fix_Transfer', 'assets', 'occupation']] = [
        '1988',
        'https://www.ancestrylibrary.com/search/collections/5058/?name=Nathaniel_Irwin&name_x=s_s&residence=_bucks-pennsylvania-usa_403&residence_x=_1-0',
        'Nathaniel Irwin : Nathaniel Irwin | Richard Walker',
        'Nathaniel Irwin | Richard Walker / Nathaniel Irwin | Richard Walker : Nathaniel Irwin / Nathaniel Irwin',
        'PA_693 : 276.68, 138.35, 93.77 | PA_1117 : 0.0, 0.0, 26.02 | PA_949 : 617.36, 308.69, 179.16',
        'Administer Estate of Richard Walker Deceased']

    df_final.loc[df_final[df_final['Group Name'].apply(lambda x: 'Peleg San' in x)].index,
                 ['Group Name', 'Group State', 'Group County', 'Group Town', 'Group Name Type',
                  'Group Match Index', 'Group Match Url', 'Name_Fix_Clean', 'Name_Fix_Transfer',
                  'Full Search Name', 'assets', 'occupation']] = [
        'Peleg Sanford', 'CT', 'Hartford County', 'Hartford', 'town', '13',
        'https://www.ancestrylibrary.com/search/collections/5058/?name=Peleg_Sanford&name_x=ps_ps&residence=_hartford-hartford-connecticut-usa_999&residence_x=_1-1-a',
        'Peleg Sanford', 'Peleg Sandford : Peleg Sandford / Peleg Sanford : Peleg Sanford / Peleg Sanford',
        'Peleg Sanford | Peleg Sandford',
        'CT_13 : 1000.17, 500.09, 1500.32 | CT_280 : 506.93, 253.47, 500.15 | CT_308 : 1200.0, 0.0, 0.0 | CT_672 : 389.47, 194.74, 177.76 | CT_836 : 39.82, 19.92, 0.0 | NY_1773 : 0.0, 0.0, 2665.61 | NY_2107 : 0.0, 0.0, 288.0 | NY_1773 : 0.0, 0.0, 2665.61 | NY_2107 : 0.0, 0.0, 288.0',
        'Merchant']

    df_final.drop_duplicates(inplace=True)
    return df_final


def CorrectWrongStateAssignments(df_final, state_group_names):
    for ind in state_group_names.index:
        group_name  = state_group_names.loc[ind, 'Group Name']
        df_ind      = df_final[df_final['Group Name'] == group_name].index
        df_final_sub = df_final.loc[df_ind]
        rep_vals    = [group_name]

        if (len(df_final.loc[df_ind, 'Group Name Type'].unique()) == 1
                and df_final.loc[df_ind, 'Group Name Type'].unique()[0] == 'state'):
            rep_vals.extend(df_final_sub[df_final_sub['Group State'].apply(
                lambda x: x == PICKSTATE[group_name])][
                ['Group State', 'Group County', 'Group Town', 'Group Name Type',
                 'Group Match Index', 'Group Match Url']].values.tolist()[0])
            for col in ['Full Search Name', 'assets', 'occupation', 'Name_Fix_Transfer', 'Name_Fix_Clean']:
                if col not in ('Name_Fix_Clean', 'Name_Fix_Transfer'):
                    rep_vals.append(JoinNameList(" | ".join(df_final_sub.loc[df_ind, col].tolist()).split(" | ")))
                else:
                    rep_vals.append(" : ".join(list(set(" : ".join(df_final_sub.loc[df_ind, col].tolist()).split(" : ")))))
        else:
            rep_vals.extend(df_final_sub[df_final_sub['Group Name Type'].apply(
                lambda x: x == 'town' or x == 'county')][
                ['Group State', 'Group County', 'Group Town', 'Group Name Type',
                 'Group Match Index', 'Group Match Url']].values.tolist()[0])
            for col in ['Full Search Name', 'assets', 'occupation', 'Name_Fix_Transfer', 'Name_Fix_Clean']:
                if col not in ('Name_Fix_Clean', 'Name_Fix_Transfer'):
                    rep_vals.append(JoinNameList(" | ".join(df_final_sub.loc[df_ind, col].tolist()).split(" | ")))
                else:
                    rep_vals.append(" : ".join(list(set(" : ".join(df_final_sub.loc[df_ind, col].tolist()).split(" : ")))))
        df_final.loc[df_ind] = rep_vals

    df_final.drop_duplicates(inplace=True)
    return df_final


def AddVillageInfo(match_df):
    match_df.loc[match_df[match_df['Home in 1790 (City, County, State)'].apply(
        lambda x: '\n' in x)].index, 'Match State'] = 'South Carolina'

    village_ind = match_df[match_df['Match County'].apply(
        lambda x: 'philadelphia' in x.lower() or 'charleston' in x.lower() or 'new york' in x.lower()
    )]['Match Town'].index
    match_df.loc[village_ind, 'Match Village'] = [
        ele if ele != 'Philadelphia City' else '' for ele in match_df.loc[village_ind, 'Match Town']
    ]
    match_df.loc[village_ind, 'Match Town'] = [
        'Philadelphia' if 'philadelphia' in ele.lower()
        else 'Charleston' if 'charleston' in ele.lower()
        else 'New York City'
        for ele in match_df.loc[village_ind, 'Match County']
    ]
    match_df.fillna("", inplace=True)
    match_df['Match Type'] = match_df.apply(
        lambda x: 'village' if x['Match Village'] != '' else x['Match Type'], axis=1
    )
    return match_df


def ExtractOccupationsFromCensus(match_df):
    # TODO: externalize title→occupation keyword table to source/raw/post1790_cd/corrections/occ/prescrape/title_keywords.csv
    opt_one_ind = match_df[match_df['Name'].apply(lambda x: '(' in x and ',' not in x)].index
    match_df.loc[opt_one_ind, 'Occupation'] = match_df.loc[opt_one_ind, 'Name'].apply(
        lambda x: JoinNameList([ele[ele.find("(") + 1:ele.find(")")] for ele in x.split(" | ") if '(' in ele]))
    match_df.loc[opt_one_ind, 'Name'] = match_df.loc[opt_one_ind].apply(lambda x: JoinNameList(
        [(ele[0:ele.find("(") - 1] + ele[ele.find(")") + 1:]) if '(' in ele else ele.replace(x['Occupation'], '')
         for ele in x['Name'].split(" | ")]), axis=1)

    esq_ind = match_df[match_df['Name'].apply(
        lambda x: ',' in x and '(' not in x and not any(char.isdigit() for char in x))].index
    match_df.loc[esq_ind, 'Occupation'] = match_df.loc[esq_ind, 'Name'].apply(
        lambda x: 'Esquire' if 'Esq' in x else '')
    match_df.loc[esq_ind, 'Occupation'] = match_df.loc[esq_ind].apply(
        lambda x: JoinNameList((x['Occupation'] + " | Colonel").split(" | ")) if 'Col' in x['Name'] else x['Occupation'], axis=1)
    match_df.loc[esq_ind, 'Occupation'] = match_df.loc[esq_ind].apply(
        lambda x: JoinNameList((x['Occupation'] + " | Judge").split(" | ")) if 'Exce' in x['Name'] or 'Judge' in x['Name'] else x['Occupation'], axis=1)
    match_df.loc[esq_ind, 'Name'] = match_df.loc[esq_ind].apply(lambda x: JoinNameList([
        ele.replace(',', '').replace('Esquire', '').replace('Esqr', '').replace('Esq.', '').replace('Esq', '')
           .replace('Colonel', '').replace('Col', '').replace('  ', ' ').replace('.', '')
           .replace('His Excely ', '').replace('r|', 'r |').replace('y|', 'y |').replace('n|', 'n |').strip()
        for ele in x['Name'].split(" | ")]), axis=1)

    both_ind = match_df[match_df['Name'].apply(lambda x: '(' in x and ',' in x)]['Name'].index
    match_df.loc[both_ind, 'Occupation'] = match_df.loc[both_ind, 'Name'].apply(
        lambda x: JoinNameList([ele[ele.find("(") + 1:ele.find(")")] for ele in x.split(" | ") if '(' in ele]))
    match_df.loc[both_ind, 'Name'] = match_df.loc[both_ind].apply(lambda x: JoinNameList(
        [(ele[0:ele.find("(") - 1] + ele[ele.find(")") + 1:]) if '(' in ele else ele.replace(x['Occupation'], '')
         for ele in x['Name'].split(" | ")]), axis=1)
    match_df.loc[both_ind, 'Occupation'] = match_df.loc[both_ind].apply(
        lambda x: JoinNameList((x['Occupation'] + " | Esquire").split(" | ")) if 'Esq' in x['Name'] else x['Occupation'], axis=1)
    match_df.loc[both_ind, 'Occupation'] = match_df.loc[both_ind].apply(
        lambda x: JoinNameList((x['Occupation'] + " | Colonel").split(" | ")) if 'Col' in x['Name'] else x['Occupation'], axis=1)
    match_df.loc[both_ind, 'Occupation'] = match_df.loc[both_ind].apply(
        lambda x: JoinNameList((x['Occupation'] + " | Judge").split(" | ")) if 'Exce' in x['Name'] or 'Judge' in x['Name'] else x['Occupation'], axis=1)
    match_df.loc[both_ind, 'Name'] = match_df.loc[both_ind].apply(lambda x: JoinNameList([
        ele.replace(',', '').replace('Esquire', '').replace('Esqr', '').replace('Esq.', '').replace('Esq', '')
           .replace('Colonel', '').replace('Col', '').replace('  ', ' ').replace('.', '')
           .replace('His Excely ', '').replace('r|', 'r |').replace('y|', 'y |').replace('n|', 'n |').strip()
        for ele in x['Name'].split(" | ")]), axis=1)

    honor_index = match_df[match_df['Name'].apply(lambda x: 'Honr.' in x or 'Honorable' in x or 'Honererable' in x)].index
    match_df.loc[honor_index, 'Occupation'] = match_df.fillna("").loc[honor_index, 'Occupation'].apply(
        lambda x: JoinNameList((x + " | Judge").split(" | ")))
    match_df.loc[honor_index, 'Name'] = match_df.loc[honor_index].apply(lambda x: JoinNameList(
        [ele.replace("Honr.", "").replace("Honorable", "").replace("Honererable", "").replace("  ", " ").strip()
         for ele in x['Name'].split(" | ")]), axis=1)

    rev_index = match_df[match_df['Name'].apply(lambda x: 'Revd' in x or 'Reverend' in x)].index
    match_df.loc[rev_index, 'Occupation'] = match_df.fillna("").loc[rev_index, 'Occupation'].apply(
        lambda x: JoinNameList((x + " | Reverend").split(" | ")))
    match_df.loc[rev_index, 'Name'] = match_df.loc[rev_index].apply(lambda x: JoinNameList(
        [ele.replace("Revd", "").replace("Reverend", "").replace("  ", " ").strip()
         for ele in x['Name'].split(" | ")]), axis=1)

    maj_index = match_df[match_df['Name'].apply(lambda x: 'Majr' in x or 'Major' in x)].index
    match_df.loc[maj_index, 'Occupation'] = match_df.fillna("").loc[maj_index, 'Occupation'].apply(
        lambda x: JoinNameList((x + " | Major").split(" | ")))
    match_df.loc[maj_index, 'Name'] = match_df.loc[maj_index].apply(lambda x: JoinNameList(
        [ele.replace("Majr", "").replace("Major", "").replace("  ", " ").strip()
         for ele in x['Name'].split(" | ")]), axis=1)

    doctor_index = match_df[match_df['Name'].apply(
        lambda x: 'Dr ' in x or 'Doctor' in x or 'Docr' in x or 'Doctr' in x or 'Dortoe' in x)].index
    match_df.loc[doctor_index, 'Occupation'] = match_df.fillna("").loc[doctor_index, 'Occupation'].apply(
        lambda x: JoinNameList((x + " | Doctor").split(" | ")))
    match_df.loc[doctor_index, 'Name'] = match_df.loc[doctor_index].apply(lambda x: JoinNameList([
        ele.replace("Doctor", "").replace("Docr", "").replace("Dortoe", "").replace("Dr ", "").replace("  ", " ").strip()
        for ele in x['Name'].split(" | ")]), axis=1)

    officer_index = match_df[match_df['Name'].apply(
        lambda x: 'Col.' in x or 'Cols' in x or 'Colonel' in x or 'Coln' in x or 'Colo' in x
                  or 'General' in x or 'Capt' in x or 'Captain' in x)].index
    match_df.loc[officer_index, 'Occupation'] = match_df.fillna("").loc[officer_index, 'Occupation'].apply(
        lambda x: JoinNameList((x + " | Military Officer").split(" | ")))
    match_df.loc[officer_index, 'Name'] = match_df.loc[officer_index].apply(lambda x: JoinNameList([
        ele.replace("Col.", "").replace("Cols", "").replace("Colonel", "").replace("Coln", "").replace("Colo", "")
           .replace("General", "").replace("Captain", "").replace("Capt", "").replace("  ", " ").strip()
        for ele in x['Name'].split(" | ")]), axis=1)

    return match_df


def ResolveMultipleMatches(df_final, match_df):
    mult_ind = df_final[df_final['Group Match Index'].apply(
        lambda x: 'Unsearchable' not in x and x != '' and len(x.split(" | ")) > 1)].index
    df_final.loc[mult_ind, 'temp'] = df_final.loc[mult_ind].apply(
        lambda x: [ind + " | " + match_df.loc[int(ind), 'Name'] for ind in x['Group Match Index'].split(" | ")], axis=1)
    df_final.loc[mult_ind, 'temp'] = df_final.loc[mult_ind].apply(
        lambda x: [ele.split(" | ")[0] for ele in x['temp'] if x['Group Name'] in ele], axis=1)
    df_final.loc[mult_ind, 'Group Match Index'] = df_final.loc[mult_ind].apply(
        lambda x: JoinNameList(x['temp']) if len(x['temp']) > 0 else x['Group Match Index'], axis=1)
    df_final.drop('temp', axis=1, inplace=True)
    return df_final


def EliminateBroadLocationMatches(df_final, match_df):
    match_df = match_df.loc[sorted(list(set([
        int(ele) for ele in df_final['Group Match Index'].apply(
            lambda x: x.split(" | ") if x != '' and x != 'Unsearchable (not a name)' else []
        ).explode().tolist() if not pd.isnull(ele)
    ])))]

    for ind in df_final[df_final['Group Match Index'].apply(lambda x: "|" in x)].index:
        match_data  = match_df.loc[[int(ele) for ele in df_final.loc[ind, 'Group Match Index'].split(" | ")]]
        town, county = df_final.loc[ind, 'Group Town'], df_final.loc[ind, 'Group County']
        match_town  = [ele for ele in list(set(match_data['Match Town'].tolist())) if ele != ""]
        match_county = [ele for ele in list(set(match_data['Match County'].tolist())) if ele != ""]

        if len(match_town) > 1 and town in match_town:
            match_ind = match_data[match_data['Match Town'] == town]['index_new'].tolist()
            df_final.loc[ind, 'Group Match Index'] = JoinNameList([str(ele) for ele in match_ind])
        elif len(match_county) == 2 and county in match_county:
            match_ind = match_data[match_data['Match County'] == county]['index_new'].tolist()
            df_final.loc[ind, 'Group Match Index'] = JoinNameList([str(ele) for ele in match_ind])

    return df_final, match_df


def ImputeLocationFromCensus(df_final, match_df):
    LOCATION_SPECIFICITY = {'state': 0, 'county': 1, 'town': 2, 'village': 3, '': -1}
    df_final['imputed_location'] = ''
    df_final['location conflict'] = ''

    has_match  = (~df_final['Group Match Index'].str.contains('Unsearchable', na=False)) & (df_final['Group Match Index'] != '')
    single_ind = df_final[has_match & ~df_final['Group Match Index'].str.contains(r' \| ', na=False)].index
    mult_ind   = df_final[has_match &  df_final['Group Match Index'].str.contains(r' \| ', na=False)].index

    df_final.loc[single_ind, 'temp'] = df_final.loc[single_ind].apply(
        lambda x: match_df.loc[int(x['Group Match Index'])][['Match State', 'Match County', 'Match Town', 'Match Village']].values.tolist()
        if LOCATION_SPECIFICITY[x['Group Name Type']] < LOCATION_SPECIFICITY[match_df.loc[int(x['Group Match Index']), 'Match Type']]
        else "", axis=1)

    df_final.loc[mult_ind, 'temp'] = df_final.loc[mult_ind].apply(
        lambda x: SameLocation(match_df.loc[[int(ele) for ele in x['Group Match Index'].split(" | ")],
                                            ['Match State', 'Match County', 'Match Town', 'Match Village']].values.tolist()), axis=1)
    df_final.loc[mult_ind, 'temp status'] = df_final.loc[mult_ind, 'temp'].apply(lambda x: x[1] if len(x) > 1 else '')
    df_final.loc[mult_ind, 'temp'] = df_final.loc[mult_ind].apply(
        lambda x: x['temp'][0] if LOCATION_SPECIFICITY[x['temp status']] > LOCATION_SPECIFICITY[x['Group Name Type']] else '', axis=1)

    # Drop rows where the census state doesn't match the group state (NY is exempted)
    temp_idx = df_final.index[df_final['temp'].fillna('') != '']
    rem_mask = df_final.loc[temp_idx].apply(
        lambda x: STATEDICT[x['Group State']] != x['temp'][0] and x['Group State'] != 'NY', axis=1)
    df_final.loc[rem_mask[rem_mask].index, 'Group Match Index'] = ''

    # Refresh after clearing mismatched match indices
    temp_idx = df_final.index[df_final['temp'].fillna('') != '']

    county_conflict = df_final.loc[temp_idx][
        (df_final.loc[temp_idx, 'Group County'] != '') &
        (df_final.loc[temp_idx, 'Group Match Index'] != '') &
        df_final.loc[temp_idx].apply(lambda x: x['Group County'] != x['temp'][1], axis=1)
    ].index
    df_final.loc[county_conflict, 'location conflict'] = 'county'

    town_conflict = df_final.loc[temp_idx][
        (df_final.loc[temp_idx, 'Group Town'] != '') &
        (df_final.loc[temp_idx, 'Group Match Index'] != '') &
        (df_final.loc[temp_idx, 'location conflict'] == '') &
        df_final.loc[temp_idx].apply(lambda x: x['Group Town'] != x['temp'][2], axis=1)
    ].index
    df_final.loc[town_conflict, 'location conflict'] = 'town'

    rep_ind = df_final.loc[temp_idx][
        (df_final.loc[temp_idx, 'location conflict'] == '') &
        (df_final.loc[temp_idx, 'Group Match Index'] != '')
    ].index
    df_final.loc[rep_ind, 'imputed_location'] = df_final.loc[rep_ind].apply(
        lambda x: match_df.loc[int(x['Group Match Index'])]['Match Type'] if pd.isnull(x.get('temp status')) else x.get('temp status', ''), axis=1)

    rep_ind = rep_ind[df_final.loc[rep_ind, 'temp'].apply(lambda x: x[0] in STATEDICT_REV)]
    df_final.loc[rep_ind, 'Group State']   = df_final.loc[rep_ind, 'temp'].apply(lambda x: STATEDICT_REV[x[0]])
    df_final.loc[rep_ind, 'Group County']  = df_final.loc[rep_ind, 'temp'].apply(lambda x: x[1] + ' County')
    df_final.loc[rep_ind, 'Group Town']    = df_final.loc[rep_ind, 'temp'].apply(lambda x: x[2])
    df_final.loc[rep_ind, 'Group Village'] = df_final.loc[rep_ind, 'temp'].apply(lambda x: x[3])

    df_final.fillna("", inplace=True)
    df_final.drop(['temp', 'temp status'], axis=1, inplace=True, errors='ignore')
    return df_final, match_df


def SameLocation(locations):
    states   = list(set([loc[0] for loc in locations]))
    counties = list(set([loc[1] for loc in locations]))
    towns    = list(set([loc[2] for loc in locations]))
    villages = list(set([loc[3] if len(loc) > 3 else '' for loc in locations]))
    loc = locations[0]
    if len(villages) == 1 and '' not in villages:
        return [loc, 'village']
    elif len(towns) == 1 and '' not in towns:
        return [[loc[0], loc[1], loc[2], ''], 'town']
    elif len(counties) == 1 and '' not in counties:
        return [[loc[0], loc[1], '', ''], 'county']
    elif len(states) == 1 and '' not in states:
        return [[loc[0], '', ''], 'state']
    else:
        return ['No Match']


def StandardizeOccupations(df_final, match_df, occ_data):
    match_df['Occupation'] = match_df['Occupation'].fillna('')
    df_final['occupation'] = df_final.apply(lambda x: JoinNameList((" | ".join(
        [match_df.loc[int(ele), 'Occupation'] for ele in x['Group Match Index'].split(" | ")]) + " | " + x['occupation']
    ).split(" | ")) if x['Group Match Index'] != '' and x['Group Match Index'] != 'Unsearchable (not a name)' else x['occupation'], axis=1)

    occ_dict = dict(zip(occ_data['Original'], occ_data['Corrected']))
    occ_dict[''] = ''
    df_final['occupation'] = df_final['occupation'].apply(
        lambda x: JoinNameList([str(occ_dict.get(ele, ele)) for ele in x.split(" | ")]))
    return df_final


def ReindexMatchData(df_final, match_df):
    match_df = match_df.loc[sorted(list(set([
        int(ele) for ele in df_final['Group Match Index'].apply(
            lambda x: x.split(" | ") if x != '' and x != 'Unsearchable (not a name)' else []
        ).explode().tolist() if not pd.isnull(ele)
    ])))]

    for ind in df_final[df_final['Group Match Index'].apply(lambda x: "|" in x)].index:
        match_data  = match_df.loc[[int(ele) for ele in df_final.loc[ind, 'Group Match Index'].split(" | ")]]
        town, county = df_final.loc[ind, 'Group Town'], df_final.loc[ind, 'Group County']
        match_town  = [ele for ele in list(set(match_data['Match Town'].tolist())) if ele != ""]
        match_county = [ele for ele in list(set(match_data['Match County'].tolist())) if ele != ""]
        if len(match_town) == 2 and town in match_town:
            match_ind = match_data[match_data['Match Town'] == town]['index_new'].tolist()
            df_final.loc[ind, 'Group Match Index'] = JoinNameList([str(ele) for ele in match_ind])
        elif len(match_county) == 2 and county in match_county:
            match_ind = match_data[match_data['Match County'] == county]['index_new'].tolist()
            df_final.loc[ind, 'Group Match Index'] = JoinNameList([str(ele) for ele in match_ind])

    match_df.drop(['index_temp', 'index_new'], inplace=True, axis=1)
    match_df['index_old'] = match_df.index
    match_list_no_dup = match_df.drop_duplicates(subset=[ele for ele in match_df.columns if ele != 'index_old'])
    match_list_no_dup.rename({'index_old': 'index_temp'}, axis=1, inplace=True)

    match_dict_df = pd.merge(match_df.reset_index(), match_list_no_dup, how='left').set_index('index')
    match_dict_df['index_old'] = match_dict_df.index
    gen_newind = match_dict_df[['index_temp']].drop_duplicates().reset_index(drop=True).copy()
    gen_newind['index_new'] = gen_newind.index
    match_dict_df = pd.merge(match_dict_df, gen_newind)
    match_dict = dict(zip(match_dict_df['index_old'], match_dict_df['index_new']))

    df_final['Group Match Index'] = df_final['Group Match Index'].apply(
        lambda x: JoinNameList([str(match_dict[int(ele)]) for ele in x.split(' | ')])
        if x not in ["", 'Unsearchable (not a name)'] else "")
    match_df = pd.merge(match_list_no_dup, gen_newind)
    match_df['index_new'] = match_df['index_new'].apply(lambda x: str(x))
    return df_final, match_df


def AggregateDebtTotals(df_final):
    # asset_count_dict: how many persons share each certificate (co-holders).
    # The count is appended as "{data_index}_{N}" so the adjusted totals can divide by N,
    # giving each co-holder's proportional share of the debt.
    asset_count_dict = df_final['assets'].apply(
        lambda x: [ele.split(" : ")[0] for ele in x.split(" | ")]
    ).explode().value_counts().to_dict()

    df_final['assets'] = df_final['assets'].apply(lambda x: " | ".join([
        ele.split(" : ")[0] + "_" + str(asset_count_dict[ele.split(" : ")[0]]) + " : " + ele.split(" : ")[1]
        for ele in x.split(" | ")
    ]))

    df_final['6p_total']     = df_final['assets'].apply(lambda x: sum([pd.to_numeric(ele.split(" : ")[1].split(",")[0]) for ele in x.split(" | ")]))
    df_final['6p_def_total'] = df_final['assets'].apply(lambda x: sum([pd.to_numeric(ele.split(" : ")[1].split(",")[1]) for ele in x.split(" | ")]))
    df_final['unpaid_interest'] = df_final['assets'].apply(lambda x: sum([pd.to_numeric(ele.split(" : ")[1].split(",")[2]) for ele in x.split(" | ")]))

    df_final['6p_total_adj']     = df_final['assets'].apply(lambda x: sum([pd.to_numeric(ele.split(" : ")[1].split(",")[0]) / pd.to_numeric(ele.split(" : ")[0].split("_")[2]) for ele in x.split(" | ")]))
    df_final['6p_def_total_adj'] = df_final['assets'].apply(lambda x: sum([pd.to_numeric(ele.split(" : ")[1].split(",")[1]) / pd.to_numeric(ele.split(" : ")[0].split("_")[2]) for ele in x.split(" | ")]))
    df_final['unpaid_interest_adj'] = df_final['assets'].apply(lambda x: sum([pd.to_numeric(ele.split(" : ")[1].split(",")[2]) / pd.to_numeric(ele.split(" : ")[0].split("_")[2]) for ele in x.split(" | ")]))

    df_final['final_total']     = df_final['6p_total']     + df_final['6p_def_total']
    df_final['final_total_adj'] = df_final['6p_total_adj'] + df_final['6p_def_total_adj']
    return df_final


if __name__ == "__main__":
    Main()
