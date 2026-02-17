import dash
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, 'https://raw.githubusercontent.com/liaochris/SPEOC-pt-1/main/web_app/assets/style.css'], \
                suppress_callback_exceptions=True)
