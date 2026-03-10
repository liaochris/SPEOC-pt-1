from pathlib import Path

import dash_bootstrap_components as dbc
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
INDIR_DERIVED = REPO_ROOT / "output/derived/postscrape/post1790_cd"

df = pd.read_csv(INDIR_DERIVED / "final_data_CD.csv")
df = df.drop(
    ['Group Match Index', 'Group Match Url', 'Full Search Name', 'assets', 'Name_Fix_Transfer', 'Name_Fix_Clean',
     'imputed_location', 'location conflict', 'Group Name Type',
     '6p_total', '6p_def_total', 'unpaid_interest', 'final_total'], axis=1)
df[['6p_total_adj', '6p_def_total_adj', 'unpaid_interest_adj', 'final_total_adj']] = \
    df[['6p_total_adj', '6p_def_total_adj', 'unpaid_interest_adj', 'final_total_adj']].round(0)

df.rename({'Group Name': 'Name', 'Group State': 'State',
           'Group County': 'County', 'Group Town': 'Town', 'Group Village': "Neighborhood",
           'occupation': 'Occupation',
           '6p_total_adj': '6% Coupons',
           '6p_def_total_adj': '6% Deferred Coupons',
           'unpaid_interest_adj': '3% Coupons',
           'final_total_adj': 'All 6% Debt'}, axis=1, inplace=True)
df = df[['Name', 'State', 'County', 'Town', 'Occupation', 'Neighborhood', 'All 6% Debt', '6% Coupons', '6% Deferred Coupons', '3% Coupons']]

# Defining DataTable styling, unpacked later
style_data_table = {
    'maxHeight': '70vh',
    'maxWidth': '95vw',
    'overflowY': 'scroll',
    'border': 'thin lightgrey solid',
    'boxShadow': '0 4px 8px 0 rgba(0,0,0,0.2)',
    'borderRadius': '2px'
}

style_cell = {
    'fontFamily': 'Open Sans',
    'textAlign': 'left',
    'width': '{}%'.format(len(df.columns)),
    'maxWidth': '250px',
    'padding': '5px',
    'overflow': 'hidden',
    'textOverflow': 'ellipsis',
    'border': '1px solid grey'
}

style_header = {
    'backgroundColor': '#e8f4f2',
    'fontWeight': 'bold',
    'color': '#333333',
    'fontSize': '16px'
}

style_table = {
    'overflowX': 'auto',
}

style_data_conditional = [
    {
        'if': {'row_index': 'odd'},
        'backgroundColor': '#E8E8E8'
    },
    {
        'if': {'state': 'active'},
        'border': '1px solid #b2deda',
        'color': '#333333'
    }
]

custom_style = {
    'style_table': style_table,
    'style_header': style_header,
    'style_cell': style_cell,
    'style_data_conditional': style_data_conditional
}
