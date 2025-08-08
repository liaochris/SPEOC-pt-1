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

import dash_html_components as html
import dash_core_components as dcc
from web_app.map_plot import create_map

from app import app

import matplotlib.pyplot as plt
import seaborn as sns

def create_map():
    folder_path = "data_raw/shapefiles/historicalstates"
    pre_map_df = gpd.read_file(folder_path)
    pre_map_df.rename(columns={'STATENAM': 'state'}, inplace=True)

    pre_map_df["geometry"] = pre_map_df["geometry"].simplify(0.01).buffer(0)
    pre_map_df = pre_map_df.set_crs('EPSG:4326', allow_override=True)

    pre_map_df.plot()
    for col in pre_map_df.select_dtypes(include='datetime'):
        pre_map_df[col] = pre_map_df[col].astype(str)

    pre_map_str = pre_map_df.to_json()

    pre_map_gj = json.loads(pre_map_str)

    state_pops_raw = pd.read_csv("data_raw/census_data/statePop.csv", header=None)

    state_pops = pd.read_csv("data_raw/census_data/statePop.csv", header=0, usecols=[0, 1])
    state_pops.columns = ['state', 'population']
    state_pops['state'] = state_pops['state'].str.strip().str.title()
    state_pops['population'] = pd.to_numeric(state_pops['population'], errors='coerce')
    state_pops['state'] = state_pops['state'].str.strip()

    pre_map_df['state'] = pre_map_df['FULL_NAME'].str.strip()



    valid_states = [
        'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut',
        'Delaware', 'District of Columbia', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois',
        'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland',
        'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana',
        'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico', 'New York',
        'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania',
        'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah',
        'Vermont', 'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming'
    ]

    pre_map_df = pre_map_df[pre_map_df['state'].isin(valid_states)]

    pre_map_df.rename(columns={'population': 'old_population'}, inplace=True)


    state_pops = state_pops[state_pops['state'].notna()]

    pre_map_df['state'] = pre_map_df['FULL_NAME'].str.strip().str.title()

    pre_map_df = pre_map_df.merge(
        state_pops[['state', 'population']],
        on='state',
        how='left'
    )

    missing_population = pre_map_df[pre_map_df['population'].isna()]
    if not missing_population.empty:
        pre_map_df['population'].fillna(0, inplace=True)  

    pre_map_df['population'] = pd.to_numeric(pre_map_df['population'], errors='coerce')


    ax = pre_map_df.plot(
        column='population',
        cmap='OrRd',
        legend=True,
        edgecolor='black',
        linewidth=0.2,
        figsize=(8, 6),
        missing_kwds={
            'color': 'lightgrey',
            'label': 'Missing population data',
            'hatch': '///'
        }
    )
    ax.set_aspect('equal')
    plt.title("State Population Map 1790")
    plt.axis('off')
    plt.tight_layout()
    plt.show()

fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
return fig

from web_app.map_plot import create_map

layout = html.Div([
    html.H3("1790 Population Map"),
    dcc.Graph(figure=create_map())
])
