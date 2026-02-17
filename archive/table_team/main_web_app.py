import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

app = dash.Dash(__name__)
external_stylesheets = ['styles.css']
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the app's layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dbc.Navbar(
        dbc.Container([
            html.A(
                dbc.Row([
                    dbc.Col(html.Img(src='/assets/logo.png', height="30px")),
                    dbc.Col(dbc.NavbarBrand("The Price of Liberty: Hamilton Resolution of the Revolutionary War Debt", className="ml-2")),
                ], align="center"),
                href="/",
            ),
            dbc.NavbarToggler(id="navbar-toggler"),
            dbc.Collapse(
                dbc.Nav([
                    dbc.NavItem(dbc.NavLink("Maps & Tables", href="/", className="nav-link")),
                    dbc.NavItem(dbc.NavLink("Project Description", href="/project_description", className="nav-link")),
                    dbc.NavItem(dbc.NavLink("About Us", href="/about_us", className="nav-link")),
                ], className="ml-auto", navbar=True),
                id="navbar-collapse",
                navbar=True,
            ),
        ]),
        color="primary",
        dark=True,
    ),
    html.Div(id='page-content', className="container mt-3"),
])

# Callback to update the page content based on the URL
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/about_us':
        from about_us import about_us_layout
        return html.Div([about_us_layout()])
    elif pathname == '/project_description':
        from project_description import project_description_layout
        return html.Div([project_description_layout()])
    else:
        from maps_tables import maps_tables_layout
        return html.Div([maps_tables_layout()])
    
if __name__ == '__main__':
    app.run_server(debug=True, host='localhost', port = 8051)
