from dash import html
from dash import dcc

pre1790_description = html.Div(className='box', children=[
    html.H1("Pre1790 Data Overview", style={'marginBottom': '5px'}, className='section-title'),
    dcc.Markdown('''This project explores debt records from before 1790, offering insight into the financial history of the early United States. Using interactive tables and maps, we highlight patterns in who held government debt, where it was concentrated, and how it changed in the years surrounding Hamilton’s 1790 funding plan.''', style = {'font-size':'3vh'}),
    html.Hr(style={"height": "2px", "background-color": "black"}),  
    html.H2("Data Introduction", style={'marginBottom': '5px'}, className='subsection-title'),
    dcc.Markdown('''
    Before 1790, states issued debt certificates to help finance the Revolutionary War. These records provide a window into the early financial history of the United States. This project organizes, cleans, and visualizes the datasets to make them easier to understand and explore.
    ''', style = {'font-size':'3vh'}),
    html.H2("Data Sources", style={'marginBottom': '5px'}, className='subsection-title'),
    dcc.Markdown('''This website uses records of Continental Congress and state-issued debt. The collections include loan office certificates from Connecticut, Delaware, Massachusetts, New Hampshire, New Jersey, New York, Pennsylvania, and Rhode Island, as well as Pierce’s certificates and Marine debt certificates.
    ''', style = {'font-size':'3vh'}),
    html.H2("Data Cleaning", style={'marginBottom': '5px'}, className='subsection-title'),
    dcc.Markdown('''
The raw pre-1790 datasets contained many errors and inconsistencies. Examples included names misspelled by one or two letters, company or estate names placed in “First Name” fields, multiple names listed in a single cell, and capitalization errors.

We cleaned the data using OpenRefine. The main steps included:

* Capitalizing first and last names  
* Trimming leading and trailing spaces  
* Renaming columns to `raw_first_name` and `raw_last_name`  
* Checking for multiple names in one column  
* Removing “Estate” and “Company” prefixes  
* Creating a combined `raw_name` column from the first and last name fields  

These steps improved accuracy and made the data consistent across all sources.
''', style = {'font-size':'3vh'}),
    html.H2("Importance of Studying the Data", style={'marginBottom': '5px'}, className='subsection-title'),
     dcc.Markdown('''
By examining who held government debt in the years leading up to and following Hamilton’s 1790 funding plan, we can uncover patterns of financial power and inequality that shaped the nation’s foundations.

Some of the key questions we ask include:
* What share of the original participants in the Revolution held onto their debt after 1790?
* In 1789, what share of the Confederation debt was held by merchants, traders, and brokers?
* During the late 1780s, did debt in the South migrate to the North?
* Who owned the pre-1790 versus the post-1790 securities?

Through interactive maps and tables, this website offers a data-driven perspective on how early financial systems shaped national development—and how those historical dynamics remain relevant today.
    ''', style = {'font-size':'3vh'}),
    ])


Layout = html.Div([
    pre1790_description,
])