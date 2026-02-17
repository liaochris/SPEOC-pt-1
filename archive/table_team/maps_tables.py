from dash import html
from dash import dcc
from dash import dash_table
import pandas as pd
from dash import Input, Output, callback, State
import dash_bootstrap_components as dbc

project_desc = html.Div(className='box', children=[
    html.H2(children='Project Description', className='box-title', style={'marginBottom': '20px', 'textAlign': 'center'}),
    html.Div([
        html.P("After the long fight against great odds in the American Revolution, many citizens of the newly established United States of America held interest-bearing debt for the goods and services they provided to the Revolutionary cause. At the end of the Revolutionary War, the debt owed by the U.S. amounted to 41 million Spanish Dollars, more than $1.6 billion today, and by 1789 had grown 29% to 53 million Spanish dollars. After the war, the U.S.’ growing inability to pay annual interest on the debt certificates ignited doubt in the government’s ability as a credible borrower.")
    ], id='slide-1'),
    html.Div([
        html.P("To resolve this issue, after the Department of Treasury’s creation in 1789 and Alexander Hamilton’s appointment as the Secretary of the Treasury, Hamilton proposed a debt framework to pay off debt to all debt certificate holders immediately.Hamilton’s proposal succeeded in two goals: (1) raise the legitimacy of the new centralized government by assuming state debts; (2) issue consols (or perpetual bonds) that could be funded gradually by new tax revenue.")
    ], id='slide-2'),
    html.Div([
        html.P("The Alexander Hamilton Project collects and analyzes data from written records into digital debt records for individuals holding pre-1970 securities and individuals who exchanged debt for consols under Hamilton’s 1790 plan.")
    ], id='slide-3'),
    html.Div(className='slider-container', children=[
        html.Button('\u25C0', id='left_arrow', className='slider-button',
                    style={'float': 'left', 'marginRight': '10px'}),
        html.Span(id='project_desc_text', style={'fontWeight': 'bold', 'textAlign': 'center'}),
        html.Button('\u25B6', id='right_arrow', className='slider-button',
                    style={'float': 'right', 'marginLeft': '10px'})
    ]),
])

def maps_tables_layout():
    return html.Div(
        className='page',
        children=[
            html.H1('Maps & Tables'),
            project_desc,
        ]
    )
