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
from web_app.map_plot import create_map


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

    state_pops = pd.read_csv("data_raw/census_data/statePop.csv", header=0, usecols=[0, 1])
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


from web_app.map_plot import create_debt_map

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