from pathlib import Path
import json

import geopandas as gpd
import pandas as pd
import plotly.express as px
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from app import app

REPO_ROOT = Path(__file__).resolve().parents[2]
INDIR_SHAPEFILES = REPO_ROOT / "source/raw/shapefiles"
INDIR_CENSUS = REPO_ROOT / "source/raw/census_data"
INDIR_DERIVED = REPO_ROOT / "output/derived/prescrape/pre1790"

def CreatePopMap():

    # --- 1) Load NHGIS 1790 states ---
    shp = INDIR_SHAPEFILES / "orig/nhgis_state_1790/US_state_1790.shp"
    gdf = gpd.read_file(shp)
    # Reproject from Albers Equal Area to WGS84 lat/lon
    gdf = gdf.to_crs(epsg=4326)

    # Standardize a clean 'state' column
    gdf["state"] = gdf["STATENAM"].astype(str).str.strip().str.title()

    # Optional: light simplify for speed & clean edges
    gdf["geometry"] = gdf["geometry"].simplify(0.01).buffer(0)

    # --- 2) Load population data and normalize names ---
    _abbrev_to_state = {
        "CT": "Connecticut", "DE": "Delaware", "GA": "Georgia",
        "MD": "Maryland", "MA": "Massachusetts", "ME": "Massachusetts",
        "NH": "New Hampshire", "NJ": "New Jersey", "NY": "New York",
        "NC": "North Carolina", "PA": "Pennsylvania", "RI": "Rhode Island",
        "SC": "South Carolina", "VA": "Virginia", "KY": "Virginia",
    }
    _county_pop_raw = pd.read_csv(INDIR_CENSUS / "orig/county_pop_fips.csv", header=1)
    state_pops = _county_pop_raw.groupby("Geo_STUSAB")["SE_T001_001"].sum().reset_index()
    state_pops.columns = ["state", "population"]
    state_pops["state"] = state_pops["state"].map(_abbrev_to_state)
    state_pops = state_pops.dropna(subset=["state"]).groupby("state", as_index=False)["population"].sum()

    # If (rare) the NHGIS layer has separate Maine/Kentucky polygons, merge them visually too.
    if {"Maine", "Massachusetts"}.issubset(set(gdf["state"])):
        gdf["state"] = gdf["state"].replace({"Maine": "Massachusetts"})
        gdf = gdf.dissolve(by="state", as_index=False)
    if {"Kentucky", "Virginia"}.issubset(set(gdf["state"])):
        gdf["state"] = gdf["state"].replace({"Kentucky": "Virginia"})
        gdf = gdf.dissolve(by="state", as_index=False)

    # Finally, keep only the reporting units (NHGIS may already be limited, this is safe)
    colonies_1790 = set(_abbrev_to_state.values())
    gdf = gdf[gdf["state"].isin(colonies_1790)].copy()

    # --- 4) Merge population onto shapes ---
    gdf = gdf.merge(state_pops, on="state", how="left")
    gdf["population"] = gdf["population"].fillna(0)

    # --- 5) Choropleth ---
    minimal = gdf[["state", "population", "geometry"]].copy()
    geojson = json.loads(minimal.to_json())

    fig = px.choropleth(
        minimal,
        geojson=geojson,
        locations=minimal.index,
        color="population",
        hover_name="state",
        labels={"population": "Population (1790)"},
        color_continuous_scale="OrRd",
        title="State Population Map (1790 Boundaries — NHGIS)"
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})
    return fig

pop_layout = html.Div([
    html.H3("1790 Population Map"),
    dcc.Graph(figure=CreatePopMap())
])

def CreateDebtMap(q=5):

    # 1) Load NHGIS 1790 states and reproject to WGS84 (lon/lat for web maps)
    shp = INDIR_SHAPEFILES / "orig/nhgis_state_1790/US_state_1790.shp"
    states = gpd.read_file(shp).to_crs(epsg=4326)

    states["geometry"] = states.geometry.simplify(tolerance=0.05, preserve_topology=True)

    # NHGIS columns you have: ['NHGISST','ICPSRST','STATENAM','GISJOIN','GISJOIN2','SHAPE_AREA','SHAPE_LEN','geometry']
    states["state"] = states["STATENAM"].astype(str).str.strip().str.title()

    # 1790 reporting units rollups (defensive; dissolve removes seams if any)
    states["state"] = states["state"].replace({
        "Maine": "Massachusetts",
        "District Of Maine": "Massachusetts",
        "Kentucky": "Virginia",
        "District Of Kentucky": "Virginia",
        "Southwest Territory": "North Carolina",
    })
    states = states.dissolve(by="state", as_index=False)

    # Keep only the 13 1790 reporting states (Vermont admitted 1791)
    colonies_1790 = {
        "Connecticut","Delaware","Georgia","Maryland","Massachusetts",
        "New Hampshire","New Jersey","New York","North Carolina",
        "Pennsylvania","Rhode Island","South Carolina","Virginia"
    }
    states = states[states["state"].isin(colonies_1790)].copy()

    # 2) Load & clean the debt data
    df = pd.read_csv(INDIR_DERIVED / "pre1790_cleaned.csv", header=0, low_memory=False)
    df.columns = df.columns.str.strip()

    state_col  = "state"
    amount_col = "amount | dollars"

    df_map = df[[state_col, amount_col]].copy()
    df_map[state_col] = df_map[state_col].astype(str).str.strip().str.title()

    # minimal abbrev expansion (extend if needed)
    abbr_to_full = {
        "Ct":"Connecticut","CT":"Connecticut",
        "De":"Delaware","DE":"Delaware",
        "Ma":"Massachusetts","MA":"Massachusetts",
        "Md":"Maryland","MD":"Maryland",
        "Nh":"New Hampshire","NH":"New Hampshire",
        "Nj":"New Jersey","NJ":"New Jersey",
        "Ny":"New York","NY":"New York",
        "Pa":"Pennsylvania","PA":"Pennsylvania",
        "Ri":"Rhode Island","RI":"Rhode Island",
        "Va":"Virginia","VA":"Virginia",
        "Nc":"North Carolina","NC":"North Carolina",
        "Sc":"South Carolina","SC":"South Carolina",
        "Ga":"Georgia","GA":"Georgia",
    }
    df_map[state_col] = df_map[state_col].replace(abbr_to_full)

    df_map[amount_col] = pd.to_numeric(df_map[amount_col], errors="coerce")
    df_map = df_map.dropna(subset=[amount_col])

    df_agg = (df_map.groupby(state_col, as_index=False)[amount_col]
                    .sum()
                    .rename(columns={amount_col: "amount"}))

    # 3) Join to shapes; fill missing with 0
    gdf = states.merge(df_agg, on="state", how="left")

    gdf["amount"] = gdf["amount"].fillna(0)

    # 4) Quantile bins (robust to ties); convert to STRING labels for JSON
    ranks = gdf["amount"].rank(method="first")
    bins = pd.qcut(ranks, q, duplicates="drop")          # Categorical with Interval categories
    cat_order = bins.cat.categories.astype(str).tolist() # remember order for legend
    gdf["bin"] = bins.astype(str)                        # <-- make JSON-serializable

    # 5) Plot with Plotly (categorical scale)
    minimal = gdf[["state", "amount", "bin", "geometry"]]
    geojson = json.loads(minimal.to_json())

    # choose as many colors as bins we actually got
    n_bins = len(cat_order)
    palette_all = px.colors.sequential.OrRd
    palette = palette_all[-n_bins:] if n_bins and n_bins <= len(palette_all) else palette_all

    fig = px.choropleth(
        minimal,
        geojson=geojson,
        locations=minimal.index,
        color="amount",                                    # categorical strings now
        category_orders={"bin": cat_order},             # keep interval order in legend
        color_discrete_sequence=palette,
        hover_name="state",
        hover_data={"amount":":,.0f", "bin":False},
        title=f"Heatmap of State Debt ca. 1790"
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})

    return fig

debt_layout = html.Div([
    html.H3("1790 Debt Map"),
    dcc.Graph(figure=CreateDebtMap(q=5))
])

DESCRIPTION_COUNT = 2

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
        During the late 1780s, did debt in the South migrate North? Who owned the pre-1790 vs post-1790 securities? \
        Through interactive maps and tables, this website offers a data driven lens into how early financial systems shaped national development, \
        and how those historical dynamics are still relevant today.",
}

title = {
    0: 'Why Studying this Data is Important', 
    1: 'Driving Questions',
}

pre_project_desc = html.Div(className='box', children=[
    html.H2(id='pre1790_desc_title', className='box-title', style={'marginBottom': '20px'}),
    html.Div(className='slider-container', children=[
        html.Button('\u25C0', id='pre1790_left_arrow', className='slider-button',
                    style={'float': 'left', 'marginRight': '10px', 'flex': 1}),
        dcc.Markdown(id='pre1790_desc_text', style={'textAlign': 'center'}),
        html.Button('\u25B6', id='pre1790_right_arrow', className='slider-button',
                    style={'float': 'right', 'marginLeft': '10px', 'flex': 1}),
    ]),
])


@app.callback(
    Output('pre1790_desc_text', 'children'),
    Output('pre1790_desc_title', 'children'),
    [Input('pre1790_left_arrow', 'n_clicks'), Input('pre1790_right_arrow', 'n_clicks')]
)
def UpdateDescription(left_clicks, right_clicks):
    left_clicks = left_clicks or 0
    right_clicks = right_clicks or 0
    number = (right_clicks - left_clicks) % DESCRIPTION_COUNT
    return description[number], title[number]

def Layout():
    return html.Div([
        pre_project_desc,
        html.Hr(),
        pop_layout,
        html.Hr(),
        debt_layout
    ])