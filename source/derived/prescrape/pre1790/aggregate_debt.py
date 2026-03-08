#!/usr/bin/env python
# coding: utf-8

from pathlib import Path
import pandas as pd
from source.lib.SaveData import SaveData

INDIR_RAW = Path("source/raw/pre1790")
OUTDIR = Path("output/derived/prescrape/pre1790")

LIQUIDATED_CLEANTABLE_CONFIGS = [
    {
        'path': 'orig/liquidated_debt_certificates_CT.xlsx',
        'state': 'ct',
        'drop_cols': ['Register Page', 'JPEG number', 'Number'],
    },
    {
        'path': 'orig/liquidated_debt_certificates_PA_stelle.xlsx',
        'state': 'pa',
        'drop_cols': ['Register Page', 'JPEG number', 'No.'],
    },
    {
        'path': 'orig/liquidated_debt_certificates_PA_story.xlsx',
        'state': 'pa',
        'drop_cols': ['Register Page', 'JPEG number', 'No.'],
        'positional_rename': {14: 'amount in specie | dollars', 15: 'amount in specie | cents'},
    },
    {
        'path': 'orig/liquidated_debt_certificates_RI.xlsx',
        'state': 'ri',
        'drop_cols': ['Register Page', 'JPEG number', 'Number'],
    },
]

MARINE_CONFIG = {
    'path': 'orig/Marine_Liquidated_Debt_Certificates.xlsx',
    'state': None,
    'drop_cols': ['Page', 'JPEG number', 'Number'],
    'positional_rename': {12: 'total dollars | notes', 13: 'total dollars | notes.1'},
}


def Main():
    column_renames = LoadColumnRenames()
    state_nums = LoadStateNums()

    # Load in order: loan office → liquidated → marine → pierce
    loan_office = LoadLoanOfficeCerts(state_nums, column_renames)
    liquidated_ct = [LoadCleanTable(cfg, column_renames) for cfg in LIQUIDATED_CLEANTABLE_CONFIGS]
    liquidated_manual = LoadLiquidatedManual()
    marine = LoadCleanTable(MARINE_CONFIG, column_renames)
    pierce = LoadPierce()

    all_dfs = [loan_office] + liquidated_ct + liquidated_manual + [marine, pierce]
    final = pd.concat(all_dfs, ignore_index=True)

    OUTDIR.mkdir(parents=True, exist_ok=True)
    SaveData(final, ['org_file', 'org_index'], OUTDIR / 'combined_pre1790.csv')


def LoadColumnRenames():
    df = pd.read_csv(INDIR_RAW / 'docs/column_renames.csv')
    return dict(zip(df['original'], df['new']))


def LoadStateNums():
    df = pd.read_csv(INDIR_RAW / 'docs/state_num_map.csv')
    return dict(zip(df['num'], df['state']))


def LoadLoanOfficeCerts(state_nums, column_renames):
    df = pd.read_excel(INDIR_RAW / 'orig/loan_office_certificates_9_states.xlsx', header=0)
    df['State'] = df['State'].apply(lambda x: state_nums[x])
    df.rename(columns=lambda x: x.lower().strip(), inplace=True)
    df.rename(columns=column_renames, inplace=True)
    df['org_file'] = 'loan_office_certificates_9_states.xlsx'
    df['org_index'] = range(len(df))
    return df


def LoadCleanTable(cfg, column_renames):
    df = pd.read_excel(INDIR_RAW / cfg['path'], header=[10, 11])
    if cfg.get('state'):
        df['state'] = cfg['state']
    df = CleanTable(df, cfg['drop_cols'])
    df.rename(columns=column_renames, inplace=True)

    if cfg.get('positional_rename'):
        new_cols = list(df.columns)
        for pos, name in cfg['positional_rename'].items():
            new_cols[pos] = name
        df.columns = new_cols

    df['org_file'] = Path(cfg['path']).name
    df['org_index'] = range(len(df))
    return df


def LoadLiquidatedManual():
    metadata = pd.read_csv(INDIR_RAW / 'docs/pre1790_import_metadata.csv')
    dfs = []
    for _, cfg in metadata.iterrows():
        df = pd.read_excel(INDIR_RAW / cfg['path'])
        df = df[cfg['row_start']:cfg['row_end']]

        named_cols = [c for c in df.columns if not str(c).startswith('Unnamed')]
        df = df.drop(columns=named_cols[:2])

        if cfg['leading_unnamed_drops'] > 0:
            remaining = list(df.columns)
            df = df.drop(columns=remaining[:cfg['leading_unnamed_drops']])

        if cfg['trailing_unnamed_drops'] > 0:
            remaining = list(df.columns)
            df = df.drop(columns=remaining[-cfg['trailing_unnamed_drops']:])

        df.columns = cfg['col_names'].split('~')
        df['state'] = cfg['state']
        df['org_file'] = Path(cfg['path']).name
        df['org_index'] = range(len(df))

        if cfg['add_secondary_empty']:
            df['to whom due | title.1'] = ''
            df['to whom due | first name.1'] = ''
            df['to whom due | last name.1'] = ''

        if cfg['use_strike_from_note']:
            df['line strike through? | yes?'] = 0
            df = df.apply(AddStrikeConf, axis=1)

        dfs.append(df)
    return dfs


def LoadManualFile(path, row_range, drop_cols, rename_dict, state, extra_cols=None):
    df = pd.read_excel(INDIR_RAW / path)
    df = df[row_range[0]:row_range[1]].drop(columns=drop_cols)
    df = df.rename(columns=rename_dict)
    if state:
        df['state'] = state
    df['org_file'] = Path(path).name
    df['org_index'] = range(len(df))
    if extra_cols:
        for col, val in extra_cols.items():
            df[col] = val
    return df


def LoadPierce():
    add_cols = [
        'letter', 'date of the certificate | month', 'date of the certificate | day',
        'date of the certificate | year', 'to whom due | title', 'to whom due | title.1',
        'to whom due | first name.1', 'to whom due | last name.1',
        'time when the debt became due | day', 'time when the debt became due | month',
        'time when the debt became due | year', 'amount | 90th', 'line strike through? | note',
        'notes',
    ]
    extra_cols = {col: '' for col in add_cols}
    extra_cols['line strike through? | yes?'] = ''
    df = LoadManualFile(
        path='orig/Pierce_Certs_cleaned_2019.xlsx',
        row_range=(1, 93308),
        drop_cols=['CN', 'Group', 'To Whom Issued', 'Officer'],
        rename_dict={
            'First': 'to whom due | first name',
            'Last': 'to whom due | last name',
            'Value': 'amount | dollars',
            'State': 'state',
        },
        state=None,
        extra_cols=extra_cols,
    )
    df = df.apply(LowercaseStateAbbr, axis=1)
    return df


def CleanTable(table, drp_cols):
    table.drop(columns=drp_cols, inplace=True)
    table.columns = table.columns.to_flat_index()
    for column in table.columns:
        if 'Unnamed' in column[1]:
            table.rename(columns={column: (column[0], '')}, inplace=True)
    table.rename(columns=lambda x: x[0].lower().strip() + ' | ' + x[1].lower().strip() if (x[1] != '') else x[0].lower().strip(), inplace=True)
    table.rename(columns={'state | ': 'state'}, inplace=True)
    return table


def AddStrikeConf(series):
    if str(series['line strike through? | note']) != 'nan':
        series['line strike through? | yes?'] = 1
    else:
        series['line strike through? | yes?'] = ''
    return series


def LowercaseStateAbbr(series):
    if str(series['state']) != 'nan':
        series['state'] = str.lower(series['state'])
    return series


if __name__ == '__main__':
    Main()
