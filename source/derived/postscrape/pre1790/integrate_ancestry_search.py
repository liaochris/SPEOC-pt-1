import pandas as pd
from pathlib import Path
from source.lib.SaveData import SaveData

INDIR_PRESCRAPE = Path("output/derived/prescrape/pre1790")
INDIR_SCRAPE    = Path("output/scrape/pre1790")
OUTDIR          = Path("output/derived/postscrape/pre1790")
OUTDIR.mkdir(parents=True, exist_ok=True)


def Main():
    agg_debt     = pd.read_csv(INDIR_PRESCRAPE / 'pre1790_cleaned.csv')
    name_changes = pd.read_csv(INDIR_PRESCRAPE / 'check/name_changes_list.csv')
    raw_changes  = pd.read_csv(INDIR_SCRAPE / 'ancestry_name_changes_raw.csv')

    agg_debt['to whom due | first name'] = agg_debt['to whom due | first name'].astype(str)
    agg_debt['to whom due | last name']  = agg_debt['to whom due | last name'].astype(str)

    ancestry_df = DeduplicateNameChanges(raw_changes)


    name_changes.drop(columns=['Unnamed: 0'], inplace=True, errors='ignore')
    name_changes = pd.concat([
        name_changes,
        ancestry_df[['Old Title', 'New Title',
                     'Old First Name', 'Old Last Name',
                     'New First Name', 'New Last Name',
                     'Obj. Num.', 'Original File', 'Original Index']]
    ], ignore_index=True)

    agg_debt = ApplyNameFixes(agg_debt, ancestry_df)
    
    SaveData(ancestry_df, ['Old Title'],
             OUTDIR / 'ancestry_name_changes_clean.csv',
             log_file=OUTDIR / 'ancestry_name_changes_clean.log')
    SaveData(name_changes, ['change_id'],
             OUTDIR / 'name_changes_david.csv',
             log_file=OUTDIR / 'name_changes_david.log')
    SaveData(agg_debt, ['row_id'],
             OUTDIR / 'final_agg_debt_cleaned.csv',
             log_file=OUTDIR / 'final_agg_debt_cleaned.log')


def DeduplicateNameChanges(raw_df):
    raw_df = raw_df.copy()
    raw_df.columns = [
        'Old Title', 'New Title',
        'Old First Name', 'Old Last Name',
        'New First Name', 'New Last Name',
        'Obj. Num.', 'Original File', 'Original Index', 'State'
    ]
    key_cols = ['Old First Name', 'Old Last Name', 'New First Name', 'New Last Name', 'State']
    raw_df = raw_df.drop_duplicates(subset=key_cols).reset_index(drop=True)

    for col in ['Old First Name', 'Old Last Name', 'New First Name', 'New Last Name', 'Original File', 'State']:
        raw_df[col] = raw_df[col].astype(str)
    for col in ['Obj. Num.', 'Original Index']:
        raw_df[col] = raw_df[col].astype(int)
    return raw_df


def ApplyNameFixes(agg_debt, ancestry_df):
    fixes = ancestry_df[['Old First Name', 'Old Last Name', 'State', 'New First Name', 'New Last Name']].drop_duplicates(
        subset=['Old First Name', 'Old Last Name', 'State'], keep='first'
    )
    merged = agg_debt.merge(
        fixes,
        left_on=['to whom due | first name', 'to whom due | last name', 'state'],
        right_on=['Old First Name', 'Old Last Name', 'State'],
        how='left'
    )
    mask = merged['New First Name'].notna()
    merged.loc[mask, 'to whom due | first name'] = merged.loc[mask, 'New First Name']
    merged.loc[mask, 'to whom due | last name']  = merged.loc[mask, 'New Last Name']
    return merged.drop(columns=['Old First Name', 'Old Last Name', 'State', 'New First Name', 'New Last Name'])


if __name__ == "__main__":
    Main()
