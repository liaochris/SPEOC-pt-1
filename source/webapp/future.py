from dash import html
from dash import dcc


# Project description tab
project_desc = html.Div(className='box', children=[
    html.H1("Future Steps", style={'marginBottom': '5px'}, className='section-title'),
    dcc.Markdown('''
    This page provides directions for future steps. If you have any other suggestions or feedback, please email chrisliao (at) uchicago (dot) edu''', style = {'font-size':'3vh'}),
    html.Hr(style={"height": "2px", "background-color": "black"}),  # Black line separator
    html.H2("Data-Related Improvements", style={'marginBottom': '5px'}, className='subsection-title'),
    dcc.Markdown('''
    - Finish cleaning Revolutionary War-era debt certificates (also known as pre-1790 data)
    - Clean ledger records for assumed state debt
    ''', style = {'font-size':'3vh'}),

    html.H2("Web App Improvements", style={'marginBottom': '5px'}, className='subsection-title'),
    dcc.Markdown('''
    - Provide general summary statistics related to the data (debtholder count, number of certificates)
    - Integrate more columns from the data such as 1790 Census matches, and the original unaggregated certifiacte references
    - Engineer more customizability (more flexibility with what color range is used for maps, number of rows to display for the tables)
    ''', style = {'font-size':'3vh'}),

    html.H2("General Analysis", style={'marginBottom': '5px'}, className='subsection-title'),
    dcc.Markdown('''
    - Explore data and summarize findings in a Jupyter Book report (that also explains how to use the web app to generate the relevant figures/tables)
    - Merge original debt certificates from the war with the debt redemption ledgers from Hamilton's plan
    - Analyze Constitutional Convention delegate and Society of the Cincinatti member debt holdings
    - Understand what the date of debt redemption tells us
    - Understand how debtholders differed from the average "American"

    ''', style = {'font-size':'3vh'}),


    ])

    # Create the layout
future_layout = html.Div([
    project_desc,
    
])
