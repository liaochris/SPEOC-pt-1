### PROBABLY WANT TO MAKE THIS A CLEAN NAMES AND DEDUPLICATED SCRIPT. 

#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
from pathlib import Path

INDIR_DERIVED = Path("output/derived/prescrape/pre1790")
INDIR_RAW = Path("source/raw/pre1790")
OUTDIR = Path("output/derived/prescrape/pre1790")

DECEASED_KEYWORDS = [" dead", "deceased", " dec'd", " dec'", " decd", " deceasd", " dee"]

STATE_ORG_PREFIXES = ("state of ", "town of ")


def Main():
    agg_debt = pd.read_csv(INDIR_DERIVED / "combined_pre1790.csv")

    name_changes_list = []

    suffixes, anchors, prefixes, known_partners, unknown_partners, abbreviations, deceased_exceptions = LoadCorrections(INDIR_RAW)

    agg_debt["organization?"] = False

    OutputDroppedNames(agg_debt)
    agg_debt = agg_debt[agg_debt['to whom due | first name'].apply(lambda name: len(str(name).split()) <= 10)]
    agg_debt = agg_debt[agg_debt['to whom due | last name'].apply(lambda name: len(str(name).split()) <= 10)]

    agg_debt = agg_debt.apply(lambda row: StripNameWords(row, prefixes, suffixes, anchors, name_changes_list), axis=1)
    agg_debt = agg_debt.apply(lambda row: ApplyKnownPartners(row, known_partners, name_changes_list), axis=1)

    agg_debt[['to whom due | first name', 'to whom due | last name']] = agg_debt[['to whom due | first name', 'to whom due | last name']].astype(str)

    agg_debt = agg_debt.explode('to whom due | first name')
    agg_debt = agg_debt.explode('to whom due | last name')
    agg_debt['final_agg_debt index'] = agg_debt.index
    agg_debt["deceased?"] = False

    DetectSuspiciousNames(agg_debt, unknown_partners)

    agg_debt = agg_debt.apply(lambda row: CleanSplitNames(row, name_changes_list), axis=1)
    agg_debt = agg_debt.apply(lambda row: NormalizeNameTokens(row, deceased_exceptions, abbreviations, name_changes_list), axis=1)

    agg_debt['full name'] = agg_debt['to whom due | first name'] + ' ' + agg_debt['to whom due | last name']
    agg_debt = CollapseConsecutiveDuplicates(agg_debt)
    agg_debt['row_id'] = agg_debt.index

    OUTDIR.mkdir(parents=True, exist_ok=True)
    SaveData(agg_debt, ['row_id'], OUTDIR / 'agg_debt_grouped.csv')

    changed_org_indices = {entry['org_index'] for entry in name_changes_list}
    agg_debt['name_cleaned'] = agg_debt['org_index'].apply(
        lambda oi: any(x.strip() in changed_org_indices for x in str(oi).split(' | '))
    )
    name_list_df = agg_debt.groupby(
        ['to whom due | first name', 'to whom due | last name', 'state'], as_index=False
    ).agg(
        title=('to whom due | title', 'first'),
        org_index=('org_index', lambda x: ' | '.join(x.astype(str))),
        name_cleaned=('name_cleaned', 'any'),
    )
    name_list_df = name_list_df.rename(columns={
        'to whom due | first name': 'first name',
        'to whom due | last name': 'last name',
    })
    name_list_df = name_list_df.reset_index(drop=True)
    name_list_df['row_id'] = name_list_df.index
    SaveData(name_list_df, ['row_id'], OUTDIR / 'name_list.csv')

    name_changes = pd.DataFrame(name_changes_list)
    if not name_changes.empty:
        name_changes = name_changes.reset_index(drop=True)
        name_changes['change_id'] = name_changes.index
        SaveData(name_changes, ['change_id'], OUTDIR / 'check/name_changes_list.csv')


def LoadCorrections(indir):
    remove_words = pd.read_csv(indir / 'corrections/name/prescrape/name_remove_words.csv')
    suffixes = remove_words[remove_words['type'] == 'suffix']['value'].tolist()
    anchors = remove_words[remove_words['type'] == 'anchor']['value'].tolist()
    prefixes = remove_words[remove_words['type'] == 'prefix']['value'].tolist()

    partners_df = pd.read_csv(indir / 'corrections/name/prescrape/name_known_partners.csv', index_col=0)
    known_partners = dict(zip(partners_df['original'].str.lower(), partners_df['new'].fillna('')))

    unknown_df = pd.read_csv(indir / 'corrections/name/prescrape/name_unknown_partners.csv')
    unknown_partners = set(unknown_df['name'].str.lower().tolist())

    abbrev_df = pd.read_csv(indir / 'corrections/name/prescrape/name_abbreviations.csv')
    abbreviations = dict(zip(abbrev_df['abbreviation'], abbrev_df['full_name']))

    dec_exc_df = pd.read_csv(indir / 'corrections/name/prescrape/name_deceased_exceptions.csv')
    deceased_exceptions = set(dec_exc_df['name'].tolist())

    return suffixes, anchors, prefixes, known_partners, unknown_partners, abbreviations, deceased_exceptions


def AddChanges(name_changes_list, title_org, title_new, fn_org, ln_org, fn_new, ln_new, case, file, index):
    name_changes_list.append({
        'title_org': title_org, 'title_new': title_new,
        'first_name_org': fn_org, 'last_name_org': ln_org,
        'first_name_new': ' | '.join(fn_new) if isinstance(fn_new, list) else fn_new,
        'last_name_new': ' | '.join(ln_new) if isinstance(ln_new, list) else ln_new,
        'cleaning case': case, 'file_loc': file, 'org_index': index
    })


def OutputDroppedNames(agg_debt):
    mask = (
        agg_debt['to whom due | first name'].apply(lambda n: len(str(n).split()) > 10) |
        agg_debt['to whom due | last name'].apply(lambda n: len(str(n).split()) > 10)
    )
    dropped = agg_debt[mask][['org_file', 'org_index', 'to whom due | first name', 'to whom due | last name']]
    if not dropped.empty:
        (OUTDIR / 'check').mkdir(parents=True, exist_ok=True)
        dropped = dropped.reset_index(drop=True)
        dropped['row_id'] = dropped.index
        SaveData(dropped, ['row_id'], OUTDIR / 'check/name_dropped.csv')


def StripNameWords(row, prefixes, suffixes, anchors, name_changes_list):
    og_fname = str(row['to whom due | first name'])
    name = og_fname.replace('&', 'and').replace('.', '').lower().strip()

    for suffix in suffixes:
        if name.endswith(suffix):
            name = name[: -len(suffix)].strip()
            break

    for anchor in anchors:
        pos = name.find(anchor.lower())
        if pos != -1:
            name = name[:pos].strip()
            break

    for prefix in prefixes:
        if name.startswith(prefix.lower()):
            name = name[len(prefix):].strip()
            break

    name = name.replace('  ', ' ').strip().title()

    if name.lower() != og_fname.lower().replace('&', 'and').replace('.', '').strip():
        AddChanges(name_changes_list, row['to whom due | title'], row['to whom due | title'],
                   og_fname, row['to whom due | last name'], name, row['to whom due | last name'],
                   2, row['org_file'], row['org_index'])
        row['to whom due | first name'] = name

    return row


def ApplyKnownPartners(row, known_partners, name_changes_list):
    og_fname = str(row['to whom due | first name'])
    og_lname = str(row['to whom due | last name'])
    key = og_fname.lower().strip()

    if key not in known_partners:
        return row

    new_val = known_partners[key]
    if not new_val:
        return row

    names = [n.strip() for n in new_val.split(' | ')]
    fn_list = [' '.join(n.split()[:-1]) if len(n.split()) > 1 else '' for n in names]
    ln_list = [n.split()[-1] if n.split() else '' for n in names]

    if len(fn_list) == 1:
        row['to whom due | first name'] = fn_list[0]
        row['to whom due | last name'] = ln_list[0]
    else:
        row['to whom due | first name'] = fn_list
        row['to whom due | last name'] = ln_list

    AddChanges(name_changes_list, row['to whom due | title'], row['to whom due | title'],
               og_fname, og_lname, row['to whom due | first name'], row['to whom due | last name'],
               3, row['org_file'], row['org_index'])

    return row


def DetectSuspiciousNames(agg_debt, unknown_partners):
    fname_col = 'to whom due | first name'

    def IsSuspicious(name):
        n = str(name).lower().strip()
        if n in unknown_partners:
            return False
        return (' and ' in n or ' of ' in n or len(n.split()) > 5 or
                any(n.startswith(p) for p in STATE_ORG_PREFIXES))

    suspicious_mask = agg_debt[fname_col].apply(IsSuspicious)
    suspicious = agg_debt[suspicious_mask][[fname_col, 'state', 'org_file', 'org_index']].drop_duplicates(subset=[fname_col])

    if not suspicious.empty:
        (OUTDIR / 'check').mkdir(parents=True, exist_ok=True)
        suspicious = suspicious.reset_index(drop=True)
        suspicious['row_id'] = suspicious.index
        SaveData(suspicious, ['row_id'], OUTDIR / 'check/name_unknown_partners.csv')


def CleanSplitNames(row, name_changes_list):
    if row["organization?"] is True:
        return row
    fname = str(row["to whom due | first name"])
    lname = str(row["to whom due | last name"])
    name = None
    if (len(lname.split()) == 0 or "nan" in lname or "NaN" in lname) and len(fname.split()) >= 2:
        name = HumanName(fname)
    if (len(fname.split()) == 0 or "nan" in fname or "NaN" in fname) and len(lname.split()) >= 2:
        name = HumanName(lname)
    if name is not None:
        AddChanges(name_changes_list, row["to whom due | title"], row["to whom due | title"],
                   fname, lname, name.first, name.last, 9, row["org_file"], row["org_index"])
        row["to whom due | first name"] = name.first
        row["to whom due | last name"] = name.last
        return row

    if fname in ("", "nan", "NaN"):
        row["to whom due | first name"] = "UNDEFINED"
        AddChanges(name_changes_list, row["to whom due | title"], row["to whom due | title"],
                   fname, lname, "UNDEFINED", lname, 7, row["org_file"], row["org_index"])
    elif lname in ("", "nan", "NaN"):
        row["to whom due | last name"] = "UNDEFINED"
        AddChanges(name_changes_list, row["to whom due | title"], row["to whom due | title"],
                   fname, lname, fname, "UNDEFINED", 7, row["org_file"], row["org_index"])

    return row


def NormalizeNameTokens(row, deceased_exceptions, abbreviations, name_changes_list):
    fname = str(row["to whom due | first name"])
    lname = str(row["to whom due | last name"])
    fullname = fname + " " + lname

    if fullname not in deceased_exceptions:
        for keyword in DECEASED_KEYWORDS:
            if keyword in fullname.lower():
                row["deceased?"] = True
                fname = fname.replace(keyword, "")
                lname = lname.replace(keyword, "")
                AddChanges(name_changes_list, row["to whom due | title"], row["to whom due | title"],
                           row["to whom due | first name"], row["to whom due | last name"],
                           fname, lname, 12, row["org_file"], row["org_index"])
                row["to whom due | first name"] = fname
                row["to whom due | last name"] = lname
                break

    if fname in abbreviations:
        row["to whom due | first name"] = abbreviations[fname]
        AddChanges(name_changes_list, row["to whom due | title"], row["to whom due | title"],
                   fname, lname, row["to whom due | first name"], lname,
                   5, row["org_file"], row["org_index"])

    return row


def CollapseConsecutiveDuplicates(df):
    g = (df['full name'] != df['full name'].shift()).bfill().cumsum()
    df['org_index'] = df['org_index'].astype(str)
    df['final_agg_debt index'] = df['final_agg_debt index'].astype(str)
    agg_cols = {col: 'first' for col in df.columns}
    agg_cols['amount | dollars'] = 'sum'
    agg_cols['amount | 90th'] = 'sum'
    agg_cols['org_index'] = ' | '.join
    agg_cols['final_agg_debt index'] = ' | '.join
    return df.groupby(g).agg(agg_cols).drop('full name', axis=1).reset_index(drop=True)


if __name__ == "__main__":
    Main()
