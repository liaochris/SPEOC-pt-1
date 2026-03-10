#!/usr/bin/env python
# coding: utf-8

from pathlib import Path
import pandas as pd
from source.lib.SaveData import SaveData

INDIR_RAW = Path("source/raw/post1790_cd")
OUTDIR = Path("output/derived/prescrape/post1790_cd")
(OUTDIR / 'check').mkdir(parents=True, exist_ok=True)

def DeNaN(series):
    return series.apply(lambda x: "" if not isinstance(x, str) else x)


def BarSeparatedNames(lst):
    return " | ".join(sorted(list(set(x for x in lst if x))))


def ApplyCompDictPername(name_fix, company_partners_dict):
    all_names = []
    for name in name_fix.split(" | "):
        replacement = company_partners_dict.get(name.lower(), name)
        if replacement:
            all_names.extend(replacement.split(" | "))
    return BarSeparatedNames(all_names)


def LoadCorrections(indir):
    df_comp = pd.read_csv(indir / 'corrections/name/prescrape/name_known_partners.csv', index_col=0)
    company_partners_dict = dict(zip(df_comp['original'].str.lower(), df_comp['new'].fillna('')))

    strip_rules = pd.read_csv(indir / 'corrections/name/prescrape/name_remove_words.csv')
    name_suffixes = strip_rules[strip_rules['type'] == 'suffix']['value'].tolist()
    anchors = strip_rules[strip_rules['type'] == 'anchor']['value'].tolist()

    institution_names = set(pd.read_csv(indir / 'corrections/name/prescrape/name_unknown_partners.csv')['name'].tolist())

    return company_partners_dict, name_suffixes, institution_names, anchors


def StripNameSuffixesAnchors(name, name_suffixes, anchors):
    # Process each pipe-separated name independently
    names = [name for name in name.split(" | ")]
    cleaned_names = []
    for name in names:
        name = name.lower()
        for suffix in name_suffixes:
            name = name.replace(suffix, '')
        # Strip from first anchor occurrence to end of name
        for anchor in anchors:
            pos = name.find(anchor.lower())
            if pos != -1:
                name = name[:pos]
                break
        name = name.replace('  ', ' ').strip().title().replace("And", "and")
        if name:
            cleaned_names.append(name)
    return " | ".join(cleaned_names)


def ApplyInstitutionalFixes(names):
    name_fix_inds = names[names['Name_Fix'].apply(lambda x: ' and ' in x.lower() or
                                                            ' of ' in x.lower() or
                                                            'treas' in x.lower() or
                                                            ' to ' in x.lower() or
                                                            'adm ' in x.lower() or
                                                            ' adm' in x.lower() or
                                                            ' exec ' in x.lower() or
                                                            'agents' in x.lower() or
                                                            ' no ' in x.lower() or
                                                            ' comm' in x.lower() or
                                                            ' for ' in x.lower())].index

    t_ind = names.loc[name_fix_inds][names.loc[name_fix_inds, 'Name_Fix'].apply(
        lambda x: 'treasurer' in x.lower() and 'cincinnati' not in x.lower())].index
    newvals = names.loc[t_ind, 'Name_Fix'].apply(lambda x: BarSeparatedNames(
        [name.replace('Society', '').replace('Proprietors', '').split("Treasurer")[0].strip() for name in x.split(" | ")]))
    names.loc[t_ind, 'Name_Fix'] = newvals

    trans_ind = names.loc[name_fix_inds][names.loc[name_fix_inds, 'Name_Fix'].apply(
        lambda x: all(['transfer' in name.lower() and 'from' in name.lower() for name in x.split(" | ")]))].index
    newvals = names.loc[trans_ind, 'Name_Fix'].apply(lambda x: BarSeparatedNames(
        [name.lower().split("transfer")[0].strip().title().replace(" And", "").split("In Trust")[0].strip() for name in
         x.split(" | ")]))
    names.loc[trans_ind, 'Name_Fix'] = newvals

    s_ind = names.loc[name_fix_inds][
        names.loc[name_fix_inds, 'Name_Fix'].apply(lambda x: " school " in x.lower() and "com" in x.lower())].index
    newvals = names.loc[s_ind, 'Name_Fix'].apply(lambda x: BarSeparatedNames(
        [name.lower().split("school")[0].replace("hon", "").replace("society committee", "").strip().title() for name in
         x.split(" | ")]))
    names.loc[s_ind, 'Name_Fix'] = newvals

    return names


def SplitNameIntoFirstLast(names, institution_names):
    df_cols = ['Name', 'Fn_Fix', 'Ln_Fix', 'new_town', 'county', 'new_state', 'country', 'geo_level', 'Name_Fix']
    name_df = pd.DataFrame(columns=df_cols)

    for ind in names.index:
        if (not pd.isnull(names.loc[ind, 'Last Name']) or "|" in names.loc[ind, 'Name_Fix']) and names.loc[
                ind, 'Name_Fix'] not in institution_names:
            for name in names.loc[ind, 'Name_Fix'].split(" | "):
                # Skip individual names that are themselves institutional names
                if name in institution_names:
                    continue
                if ' van de ' in name.lower() or ' de la ' in name.lower():
                    if ' de la ' in name.lower():
                        ln = " ".join(name.split(" ")[-3:])
                        fn = " ".join(name.split(" ")[:-3])
                    else:
                        ln = " ".join(name.split(" ")[1:])
                        fn = " ".join(name.split(" ")[:1])
                elif ' de ' in name.lower():
                    ln = " ".join(name.split(" ")[-2:])
                    fn = " ".join(name.split(" ")[:-2])
                elif "ii" in name.lower() or '2nd' in name.lower() or ' van ' in name.lower() or ' ten ' in name.lower() or ' del ' in name.lower():
                    ln = " ".join(name.split(" ")[-2:])
                    fn = " ".join(name.split(" ")[:-2])
                else:
                    ln = " ".join(name.split(" ")[-1:])
                    fn = " ".join(name.split(" ")[:-1])
                res = names.loc[[ind]].copy()
                res['First Name'] = fn
                res['Last Name'] = ln
                res.columns = df_cols
                name_df = pd.concat([name_df, res])

    return name_df


def Main():
    company_partners_dict, name_suffixes, institution_names, anchors = LoadCorrections(INDIR_RAW)

    CD_merged = pd.read_csv(OUTDIR / "geo_standardized_CD_post1790.csv", index_col=0)

    names = CD_merged[
        ['Name', 'First Name', 'Last Name', 'new_town', 'county', 'new_state', 'country', 'geo_level']].fillna(
        "").drop_duplicates().reset_index(drop=True)

    names['Name_Fix'] = names['Name'].apply(lambda x: StripNameSuffixesAnchors(x, name_suffixes, anchors))

    names = ApplyInstitutionalFixes(names)

    names['Name_Fix'] = names['Name_Fix'].apply(
        lambda x: ApplyCompDictPername(x, company_partners_dict) if not pd.isnull(x) else x)

    # Full-string lookup: catches compound pipe-separated entries in company_partners.csv
    names['Name_Fix'] = names['Name_Fix'].apply(lambda x: company_partners_dict.get(x.lower(), x) if not pd.isnull(x) else x)
    names['Name_Fix'] = names['Name_Fix'].apply(lambda x: x.replace("  ", " ").strip())
    names['Name_Fix'] = names['Name_Fix'].apply(lambda x: BarSeparatedNames(x.split(" | ")))

    company_name_ind = names[names.apply(
        lambda x: (x['Name'] == x['Name_Fix'] and ' and ' in x['Name']) or 
        (x['Name'] != x['Name_Fix'] and ' and ' in x['Name_Fix']), axis=1)].index
    unknown_company_names = names.drop(['First Name', 'Last Name'], axis=1).loc[company_name_ind].drop_duplicates()
    SaveData(unknown_company_names, ['Name', 'Name_Fix'], OUTDIR / 'check/companies_unidentified_partners.csv',
             log_file=OUTDIR / 'check/companies_unidentified_partners.log')

    name_df = SplitNameIntoFirstLast(names, institution_names)

    OUTDIR.mkdir(parents=True, exist_ok=True)
    name_df = name_df.reset_index(drop=True)
    name_df['row_id'] = name_df.index
    SaveData(name_df, ['row_id'], OUTDIR / 'check/name_changes_list.csv',
             log_file=OUTDIR / 'check/name_changes_list.log')

    us_state_names = {
        'connecticut', 'delaware', 'georgia', 'maryland', 'massachusetts',
        'new hampshire', 'new jersey', 'new york', 'north carolina',
        'pennsylvania', 'rhode island', 'south carolina', 'vermont', 'virginia'
    }
    known_geos = set(CD_merged['new_town'].dropna().str.lower()) | us_state_names
    town_conflicts = name_df[name_df['Ln_Fix'].str.lower().isin(known_geos)][
        ['Name_Fix', 'Fn_Fix', 'Ln_Fix', 'new_town', 'new_state']].drop_duplicates()
    if not town_conflicts.empty:
        town_conflicts = town_conflicts.reset_index(drop=True)
        town_conflicts['row_id'] = town_conflicts.index
        SaveData(town_conflicts, ['row_id'], OUTDIR / 'check/name_town_conflicts_list.csv',
                 log_file=OUTDIR / 'check/name_town_conflicts_list.log')

    CD_merged_names = pd.merge(CD_merged.fillna(""), name_df[['Name', 'Name_Fix', 'new_town', 'county', 'new_state', 'country', 'geo_level']].drop_duplicates(), how='left')
    CD_merged_names.loc[CD_merged_names[CD_merged_names['Name_Fix'].isnull()].index, 'Name_Fix'] = CD_merged_names.loc[CD_merged_names[CD_merged_names['Name_Fix'].isnull()].index, 'Name']

    CD_merged_names = CD_merged_names.reset_index(drop=True)
    CD_merged_names['row_id'] = CD_merged_names.index
    SaveData(CD_merged_names, ['row_id'], OUTDIR / 'geo_name_standardized_CD_post1790.csv',
             log_file=OUTDIR / 'geo_name_standardized_CD_post1790.log')


if __name__ == "__main__":
    Main()
