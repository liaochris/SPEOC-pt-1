import json

import dash_bootstrap_components as dbc
import geopandas as gpd
import numpy as np
import pandas as pd
import plotly.express as px
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from shapely import wkt
import requests


import plotly.graph_objects as go  

import matplotlib.pyplot as plt
import seaborn as sns
import us

from dash import Dash

app = Dash(__name__)

def create_pop_map():
    folder_path = "data_raw/shapefiles/historicalstates"
    pre_map_df = gpd.read_file(folder_path)
    pre_map_df = pre_map_df.set_crs('EPSG:4326', allow_override=True)

    pre_map_df['state'] = pre_map_df['FULL_NAME'].str.strip().str.title()
    pre_map_df["geometry"] = pre_map_df["geometry"].simplify(0.01).buffer(0)

    state_pops = pd.read_csv("data_raw/census_data/statePop.csv", header=0, usecols=[0, 1], low_memory=False)
    state_pops.columns = ['state', 'population']
    state_pops['state'] = state_pops['state'].str.strip().str.title()
    state_pops['population'] = pd.to_numeric(state_pops['population'], errors='coerce')

    valid_states = [
        'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut',
        'Delaware', 'District Of Columbia', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois',
        'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland',
        'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana',
        'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico', 'New York',
        'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania',
        'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah',
        'Vermont', 'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming'
    ]
    pre_map_df = pre_map_df[pre_map_df['state'].isin(valid_states)]

    merged_df = pre_map_df.merge(state_pops, on='state', how='left')
    merged_df['population'] = merged_df['population'].fillna(0)

    fig = px.choropleth(
        merged_df,
        geojson=merged_df.geometry.__geo_interface__,
        locations=merged_df.index,  
        color='population',
        hover_name='state',
        color_continuous_scale='OrRd',
        title='State Population Map (1790)'
    )

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r": 0, "t": 30, "l": 0, "b": 0})

    return fig

pop_layout = html.Div([
    html.H3("1790 Population Map"),
    dcc.Graph(figure=create_pop_map())
])


def create_debt_map():
    states = gpd.read_file("data_raw/shapefiles/historicalstates")
    states = states.rename(columns={'NAME': 'state'})
    states['state'] = states['state'].astype(str).str.strip().str.title()

    state_name_corrections = {
        "Alabama Territory": "Alabama", 
        "Alaska Department": "Alaska",
        "Alaska District": "Alaska",
        "Alaska Territory": "Alaska",
        "Arizona Territory": "Arizona",
        "Arkansas Territory": "Arkansas",
        "Colorado Territory": "Colorado",
        "Florida Territory": "Florida",
        "Florida Unorg. Ft": "Florida",
        "Hawaii Annexation": "Hawaii",
        "Hawaii Territory": "Hawaii",
        "Idaho Territory": 'Idaho',
        "Illinois Territory": "Illinois",
        "Indiana Territory": "Indiana",
        "Iowa Territory": "Iowa",
        "Kansas Territory": "Kansas", 
        "Louisiana Territory": "Louisiana Purchase",
        "Michigan Territory": "Michigan",
        "Minnesota Territory": "Minnesota",
        "Mississippi Terr.": "Mississippi",
        "Missouri Territory": "Missouri",
        "Montana Territory": "Montana",
        "Nebraska Territory": "Nebraska",
        "Nevada Territory": "Nevada",
        "New Mexico Territory": "New Mexico",
        "Oklahoma Territory": "Oklahoma",
        "Oregon Country": "Oregon",
        "Oregon Territory": "Oregon",
        "Oregon Unorg. Ft": "Oregon",
        "Orleans Territory": "Louisiana",
        "Southwest Territory": "Tennessee",
        "Texas Republic": "Texas",
        "Utah Territory": "Utah Territory",
        "Vermont Republic": "Vermont",
        "Washington Territory": "Washington",
        "Wisc. Terr. De Facto": "Wisconsin",
        "Wisconsin Territory": "Wisconsin",
        "Wyoming Territory": "Wyoming"
    }

    states['state'] = states['state'].replace(state_name_corrections)

    def merge_territory(states, group, name):
        geom = states[states['state'].isin(group)].unary_union
        row = gpd.GeoDataFrame({'state': [name], 'geometry': [geom]}, crs=states.crs)
        states = states[~states['state'].isin(group)]
        return pd.concat([states, row], ignore_index=True)

    states = merge_territory(states, ['North Dakota', 'South Dakota', 'Montana', 'Wyoming'], 'Dakota Territory')
    states = merge_territory(states, ['Arizona', 'New Mexico'], 'Gadsden Purchase')
    states = merge_territory(states, ['Louisiana', 'Arkansas', 'Missouri', 'Iowa', 'Oklahoma', 'Kansas', 'Nebraska', 
                                    'North Dakota', 'South Dakota', 'Minnesota', 'Montana', 'Wyoming', 'Colorado', 
                                    'New Mexico', 'Texas'], 'Louisiana Purchase')
    states = merge_territory(states, ['California', 'Nevada', 'Utah', 'Arizona', 'New Mexico', 'Colorado', 'Wyoming'], 'Mexican Cession')
    states = merge_territory(states, ['Ohio', 'Indiana', 'Illinois', 'Michigan', 'Wisconsin'], 'Northwest Territory')


    df = pd.read_csv("cleaning_CD/pre1790/data/agg_debt_david.csv", header=0)
    df.columns = df.columns.str.strip()

    abbr_to_full = {
        'Ct': 'Connecticut',
        'CT': 'Connecticut',
        'De': 'Delaware',
        'DE': 'Delaware',
        'Ma': 'Massachusetts',
        'MA': 'Massachusetts',
        'Md': 'Maryland',
        'MD': 'Maryland',
        'Nh': 'New Hampshire',
        'NH': 'New Hampshire',
        'Nj': 'New Jersey',
        'NJ': 'New Jersey',
        'Ny': 'New York',
        'NY': 'New York',
        'Pa': 'Pennsylvania',
        'PA': 'Pennsylvania',
        'Ri': 'Rhode Island',
        'RI': 'Rhode Island',
        'Va': 'Virginia',
        'VA': 'Virginia',
        'Al': 'Alabama',
        'AL': 'Alabama',
        'AK': 'Alaska',
        'Ak': 'Alaska',
        'AZ': 'Arizona',
        'Az': 'Arizona',
        'AR': 'Arkansas',
        'Ar': 'Arkansas',
        'CA': 'California',
        'Ca': 'California',
        'CO': 'Colorado',
        'Co': 'Colorado',
        'DC': 'District of Columbia',
        'Dc': 'District of Columbia',
        'FL': 'Florida',
        'Fl': 'Florida',
        'GA': 'Georgia',
        'Ga': 'Georgia',
        'HI': 'Hawaii',
        'Hi': 'Hawaii',
        'ID': 'Idaho',
        'Id': 'Idaho',
        'IL': 'Illinois',
        'Il': 'Illinois',
        'IN': 'Indiana',
        'In': 'Indiana',
        'IA': 'Iowa',
        'Ia': 'Iowa',
        'KA': 'Kansas',
        'Ka': 'Kansas',
        'KY': 'Kentucky',
        'Ky': 'Kentucky',
        'LA': 'Louisiana',
        'La': 'Louisiana',
        'ME': 'Maine',
        'Me': 'Maine',
        'MI': 'Michigan',
        'Mi': 'Michigan',
        'MN': 'Minnesota',
        'Mn': 'Minnesota',
        'Ms': 'Mississippi',
        'MS': 'Mississippi',
        'Mo': 'Missouri',
        'MO': 'Missouri',
        'Mt': 'Montana',
        'MT': 'Montana',
        'NE': 'Nebraska',
        'Ne': 'Nebraska',
        'NV': 'Nevada',
        'Nv': 'Nevada',
        'Nc': 'North Carolina',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'Nd': 'North Dakota',
        'OH': 'Ohio',
        'Oh': 'Ohio',
        'Ok': 'Oklahoma',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'Or': 'Oregon',
        'Sc': 'South Carolina',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'Sd': 'South Dakota',
        'Tn': 'Tennessee',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'Tx': 'Texas',
        'Ut': 'Utah',
        'UT': 'Utah',
        'VT': 'Vermont',
        'Vt': 'Vermont',
        'WA': 'Washington',
        'Wa': 'Washington',
        'WV': 'West Virginia',
        'Wv': 'West Virginia',
        'WI': 'Wisconsin',
        'Wi': 'Wisconsin',
        'WY': 'Wyoming',
        'Wy': 'Wyoming',
    }

    state_col = "state"
    amount_col = "amount | dollars"


    df_map = df[[state_col, amount_col]].copy()
    df_map['state'] = df_map['state'].astype(str).str.strip().str.title()

    df_map['state'] = df_map['state'].replace(abbr_to_full)

    df_map = df_map[df_map['state'].notna()]
    df_map = df_map[df_map['state'].str.lower() != 'nan']
    df_map[amount_col] = pd.to_numeric(df_map[amount_col], errors='coerce')
    df_map = df_map.dropna(subset=[amount_col])

    df_agg = df_map.groupby('state')[amount_col].sum().reset_index()

    df_agg = df_agg.rename(columns={amount_col: 'amount'})
    gdf = states.merge(df_agg, on='state', how='left')

    gdf = gpd.GeoDataFrame(gdf, geometry='geometry')
    gdf = gdf[gdf['geometry'].notnull()]
    gdf = gdf[gdf['geometry'].apply(lambda g: g.is_valid and not g.is_empty)]

    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326", allow_override=True)

    minx, miny, maxx, maxy = gdf.total_bounds
    ax = gdf.plot(
        column='amount',
        cmap='OrRd',
        legend=True,
        edgecolor='black',
        linewidth=0.2,
        figsize=(12, 8),
        missing_kwds={
            'color': 'lightgrey',
            'label': 'No data',
            'hatch': '///'
        }
    )

    ax.set_aspect(1 / np.cos(np.deg2rad((miny + maxy) / 2)))
    plt.title("Heatmap of State Debt ca. 1790")
    plt.axis('off')
    plt.tight_layout()
    plt.show()

debt_layout = html.Div([
    html.H3("1790 Debt Map"),
    dcc.Graph(figure=create_debt_map())
])

DESCRIPTION_COUNT = 2

pre_project_desc = html.Div(className='box', children=[
    html.H2(children=title[0], className='box-title', style={'marginBottom': '20px'}, id='slider-title'),
   
    html.Div(className='slider-container', children=[
        html.Button('\u25C0', id='left_arrow', className='slider-button',
                    style={'float': 'left', 'marginRight': '10px', 'flex': 1}),
        dcc.Markdown(description[0], id='project_desc_text', style={'textAlign': 'center'}),
        html.Button('\u25B6', id='right_arrow', className='slider-button',
                    style={'float': 'right', 'marginLeft': '10px', 'flex': 1})
    ]),
])

description = {
    0: "By examining who held government debt in the years leading up to and following Hamilton’s 1790 funding plan,\
        we are able to uncover patterns of financial power and inequality that helped shape the nation’s foundations. \
        Drawing on detailed pre-1790 debt records, we explore how debt was distributed across regions and social groups,  \
        and how patterns of ownership shifted in the lead-up to federal assumption.\
        We ask, what share of the original founders of the American Revolution participated in Hamilton’s 1790 funding? \
        In 1789, what share of the Confederation debt was held by merchants, traders, and brokers? \
        During the late 1780s, did debt in the South migrate North? Who owned the pre-1790 vs post-1790 securities? \
        Through interactive maps and tables, this website offers a data driven lens into how early financial systems shaped national development, \
        and how those historical dynamics are still relevant today.",
    1: "What share of the original founders of the American Revolution participated in Hamilton’s 1790 funding? \
        In 1789, what share of the Confederation debt was held by merchants, traders, and brokers? \
        During the late 1780s, did debt in the South migrate North? \
        Who owned the pre-1790 vs post-1790 securities?"
}
title = {
    0: 'Why Studying This Data is Important', 
    1: 'Driving Questions',
}

def update_pre_project_desc(left_clicks, right_clicks):
    if left_clicks is None:
        left_clicks = 0
    if right_clicks is None:
        right_clicks = 0

    number = (right_clicks - left_clicks) % DESCRIPTION_COUNT
    return description[number], title[number]

pre_map_layout = html.Div([
    pre_project_desc,    
])

@app.callback(
    Output('project_desc_text', 'children'),
    Output('slider-title', 'children'),
    Input('left_arrow', 'n_clicks'),
    Input('right_arrow', 'n_clicks')
)
def update_description(left_clicks, right_clicks):
    return update_pre_project_desc(left_clicks, right_clicks)

app.layout = pre_map_layout

if __name__ == '__main__':
    app.run(debug=True)