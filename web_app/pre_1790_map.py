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

from app import app

pre1790_state_codes = json.loads(requests.get('https://raw.githubusercontent.com/liaochris/SPEOC-pt-1/main/web_app/assets/state_codes.json').text)
pre1790_state_codes_inv = {v: k for k, v in pre1790_state_codes.items()}
