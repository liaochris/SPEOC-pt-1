from dash import html
from dash import dcc

pre1790_desc = html.Div(className='box', children=[
    html.H1("Historical Context", style={'marginBottom': '5px'}, className='section-title'),
    html.Hr(style={"height": "2px", "background-color": "black"}),  
    html.H2("Historical Background", style={'marginBottom': '5px'}, className='subsection-title'),
    dcc.Markdown('''
    In 1790, the new United States needed a plan when it came to debts from the war from the states, as well as a financial plan for the nation. As such, Alexander Hamilton, the Secretary of the Treasury introduced his First Report on Public Credit. This plan established a national bank for the United States, provided for assumption of state debts, funding at par value, establishment of excise taxes, and protective tariffs. Eventually, the plan was able to come to fruition after the Compromise of 1790, where Thomas Jefferson and James Madison (who opposed the plan) agreed to the passing of the Funding Act of 1790 and the assumption act if the capital of the United States could be moved to a place nearer to Virginia (to what is now the District of Columbia, or Washington DC). 
    In Hamilton’s financial plan, the Revolutionary war debts were assumed as federal debt. In total, the United States owed nearly $80 million in foreign, state, and domestic debts (“How”). This debt included debt from both states and the Continental Congress. The Funding Act of 1790 let The Department of the Treasury issue 3 types of issues. The first would be ⅔ of the Domestic Federal Debt with a 6% interest rate, the second would be the other ⅓ of the Domestic Federal Debt with a deferred 6% interest rate (no interest till 1801) and the third would be the outstanding debt, as securities with 3% interest (“Edling”). For state debts, 4/9 would have a 6% interest rate, 2/9 with a deferred 6% interest rate, and 3/9 with a 3% rate. Then, in 1795, the foreign debt was refinanced with 50% of a higher interest rate. As such, the United States used this plan to assume debts of the federal debt and the state debt, and was able to slowly pay off debts from the war. 
    ''', style = {'font-size':'3vh'}),
    html.H2("Project Goal", style={'marginBottom': '5px'}, className='subsection-title'),
    dcc.Markdown('''
    Our goal in this project is to look into patterns within the pre 1790 data sets provided to the team by Professors Sargeant and Hall, such as the share of original founders participating in the 1790 funding, the share of Confederation debt held by people with different occupations, whether Southern debt migrated North in the 1780s, and who owned the pre 1790 vs post 1790 securities. We demonstrated findings and patterns within maps (see the Maps tab) and tables (Tables tab). Our goal is to use these findings and these maps and tables as well to make analyses based around our driving questions. 
    ''', style = {'font-size':'3vh'}),
    ])
pre_hist_layout = html.Div([
    pre1790_desc,    
])
