from dash import html
from dash import dcc

pre1790_description = html.Div(className='box', children=[
    html.H1("Pre1790 Data Description", style={'marginBottom': '5px'}, className='section-title'),
    dcc.Markdown('''This section of this website analyzes the pre 1790 data sets provided. The findings will be shown in date tables and population maps''', style = {'font-size':'3vh'}),
    html.Hr(style={"height": "2px", "background-color": "black"}),  # Black line separator
    html.H2("Data Sources", style={'marginBottom': '5px'}, className='subsection-title'),
    dcc.Markdown('''This website has collected records of debt of the Continental Congress debt. It includes debt data sets from different states (Connecticut, Delaware, Massachusetts, New Hampshire, New Jersey, New York, Pennsylvania, and Rhode Island) as well as Pierce and Marine debt certificate data.
    ''', style = {'font-size':'3vh'}),
    html.H2("Data Cleaning", style={'marginBottom': '5px'}, className='subsection-title'),
    dcc.Markdown('''Initially, the raw pre 1790 data sets had many errors and issues, including misspellings by one or two letters or so of a name, having company or estate names in a First Name cell, having multiple names in one cell, and capitalization errors. As such, we underwent data cleaning through using OpenRefine. First, first and last name were capitalized. Next, leading and trailing whitespaces were trimmed, and then columns were renamed to raw_first_name and raw_last_name. Afterwards, 2+ names in one column were checked for. Following this, Estate and Company prefixes were removed, and finally the raw_name column was created by combining the raw_first_name and raw_last_name columns. 
''', style = {'font-size':'3vh'}),

    ])

data_layout = html.Div([
    pre1790_description,
    
])

