from dash import html
from dash import dcc
from dash import Dash

app = Dash(__name__)

pre1790_description = html.Div(className='box', children=[
    html.H1("Pre1790 Data Description", style={'marginBottom': '5px'}, className='section-title'),
    dcc.Markdown('''
    This section of this website analyzes the pre 1790 data sets provided. The findings will be shown in date tables and population maps''', style = {'font-size':'3vh'}),
    html.Hr(style={"height": "2px", "background-color": "black"}),  
    html.H2("Data Introduction", style={'marginBottom': '5px'}, className='subsection-title'),
    dcc.Markdown('''
    This section of this website analyzes the pre 1790 data sets provided. The findings will be shown in date tables and population maps.
    ''', style = {'font-size':'3vh'}),
    html.H2("Data Sources", style={'marginBottom': '5px'}, className='subsection-title'),
    dcc.Markdown('''This website has collected records of debt of the Continental Congress debt. It includes debt data sets from different states (Connecticut, Delaware, Massachusetts, New Hampshire, New Jersey, New York, Pennsylvania, and Rhode Island) as well as Pierce and Marine debt certificate data.
    ''', style = {'font-size':'3vh'}),
    html.H2("Data Cleaning", style={'marginBottom': '5px'}, className='subsection-title'),
    dcc.Markdown('''Initially, the raw pre 1790 data sets had many errors and issues, including misspellings by one or two letters or so of a name, having company or estate names in a First Name cell, having multiple names in one cell, and capitalization errors. As such, we underwent data cleaning through using OpenRefine. First, first and last name were capitalized. Next, leading and trailing whitespaces were trimmed, and then columns were renamed to raw_first_name and raw_last_name. Afterwards, 2+ names in one column were checked for. Following this, Estate and Company prefixes were removed, and finally the raw_name column was created by combining the raw_first_name and raw_last_name columns. 
''', style = {'font-size':'3vh'}),
    html.H2("Importance of Studying the Data", style={'marginBottom': '5px'}, className='subsection-title'),
     dcc.Markdown('''By examining who held government debt in the years leading up to and following Hamilton’s 1790 funding plan, we are able to uncover patterns of financial power and inequality that helped shape the nation’s foundations. Drawing on detailed pre-1790 debt records, we explore how debt was distributed across regions and social groups, and how patterns of ownership shifted in the lead-up to federal assumption. 
     We ask, what share of the original founders of the American Revolution participated in Hamilton’s 1790 funding? In 1789, what share of the Confederation debt was held by merchants, traders, and brokers? During the late 1780s, did debt in the South migrate North? Who owned the pre-1790 vs post-1790 securities? 
     Through interactive maps and tables, this website offers a data driven lens into how early financial systems shaped national development, and how those historical dynamics are still relevant today. 
    ''', style = {'font-size':'3vh'}),
    ])


pre_data_layout = html.Div([
    pre1790_desc,    
])

app.layout = pre_data_layout

if __name__ == '__main__':
    app.run(debug=True)