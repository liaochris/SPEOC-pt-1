from dash import html
from dash import dcc


# Project description tab
project_desc = html.Div(className='box', children=[
    html.H1("Data Description", style={'marginBottom': '5px'}, className='section-title'),
    dcc.Markdown('''
    This page provides more detail on the data that is used to create maps and tables''', style = {'font-size':'3vh'}),
    html.Hr(style={"height": "2px", "background-color": "black"}),  # Black line separator
    html.H2("Data Sources", style={'marginBottom': '5px'}, className='subsection-title'),
    dcc.Markdown('''
    In this web app, we only consider debt entries from ledger records for the Continental Congress's debt. As of September 2023, we have not cleaned the ledgers containing records for debt that the national government assumed. Our data team is currently working on cleaning data on debt certificates that people received for providing goods or services during the Revolution. While the ledgers for the debt either incurred by Congress or the states date to after 1790, when Hamilton’s plan was first proposed, the aforementioned certificates are from the Revolutionary war era. 
    
    The maps define debt distribution as the value of all 6% coupons - that is, the total face value of all debt incurred. To learn more about the other data sources relating to the Hamilton project and techniques/tools we use in this process, see this [document](assets/Hamilton_Data.pdf).
    ''', style = {'font-size':'3vh'}),

    html.H2("Data Cleaning", style={'marginBottom': '5px'}, className='subsection-title'),
    dcc.Markdown('''
    The raw data - the Continental Congress debt ledgers - that our team started with possessed several problems. Among them included variations in the spelling of the same names and locations, and the fact that the data was not aggregated at the debtholder level. Our cleaning process involved standardizing name, location and occupation spellings, location imputation (through the 1790 census) and the addition of other valuable covariates (such as family size and slave owner status). For more details on the exact steps taken, see this markdown [document](assets/doc.pdf)
    ''', style = {'font-size':'3vh'}),

    ])

    # Create the layout
data_layout = html.Div([
    project_desc,
    
])
