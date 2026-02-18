from dash import html
from dash import dcc


# Project description tab
project_desc = html.Div(className='box', children=[
    html.H1("Historical Background", style={'marginBottom': '5px'}, className='section-title'),
    dcc.Markdown('''
    This page provides a summary on the origins of American national debt and its relevance for us today. \
        For a more detailed treatment, see this [exposition](/assets/Hamilton_Exposition.pdf)
    ''', style = {'font-size':'3vh'}),
    html.Hr(style={"height": "2px", "background-color": "black"}),  # Black line separator
    html.H2("Origins of the National Debt", style={'marginBottom': '5px'}, className='subsection-title'),
    dcc.Markdown('''
    During the Revolutionary War, the Continental Congress and state governments accumulated debt to fund the war effort. The Conti​nental Congress issued two types of debt - interest-bearing debts and paper monies, called “Continental Dollars” - for goods and services that individuals provided to the Revolutionary cause. The interest-bearing debts promised to repay the original principal at a later date and periodically pay interest to the debtholder (until the principal was repaid). The Continental government was unable to repay most of the interest or principal on these debts; instead, sometimes it would issue new certificates that pushed back the payment date. In this project, we’re interested in interest-bearing debts, because debt ownership records exist. By 1781, two years before the end of the Revolutionary War and the Treaty of Paris, the Continental Congress owed 41 million Spanish Dollars, more than $1.6 billion today, and by 1789 the debt amount had grown 29% to 53 million Spanish dollars due to unpaid interest. In 1784, the Continental Congress owed $2 million in interest payments for just that year but raised less than $1 million in revenue, because the Articles of Confederation limited the Continental Congress’ ability to raise revenue through taxation. Congress’ inability to make interest payments on its debt, never mind the principal debt amount, ruined its financial credibility. This caused debt to trade at market values far lower than its face value (the promised principal payment). 
    ''', style = {'font-size':'3vh'}),
    html.H2("Hamilton's Plan", style={'marginBottom': '5px'}, className='subsection-title'),
    dcc.Markdown('''
    The first Secretary of the Treasury, Alexander Hamilton wanted to repay the national debt so that America could access debt markets in the future. In his Funding Act of August 4, 1790, Hamilton proposed that the United States government, newly centralized, assume the debt both of the Continental Congress and the individual states’ debts. As a result, the federal government’s debt total reached 74.3 million Spanish Dollars in September of 1790. The Funding Act permitted the Department of the Treasury to issue three new types of loans: (1) consols that paid a 6% coupon, (2) consols that paid a 3% coupon, and (3) consols that paid a 6% coupon starting in 1801. Debtholders received  6% and deferred 6% coupons based off the face value of their debt holdings, and 3% coupons based off their unpaid interest holdings. Although many domestic creditors ultimately received less than the $100 promised by the face value of their certificate (the market value of $100 in face value of debt was around $75), this was a vast improvement of what the debt had been trading at prior to Hamilton’s plan (around $20).
    ''', style = {'font-size':'3vh'}),
    dcc.Markdown('''
    The consols established under Hamilton’s proposal were government debt certificates in the form of perpetual bonds that could be funded gradually by tax revenue. As perpetual bonds, these consols had no maturity date at which the principal payment of the bond must be paid back. Instead, the government could choose whenever, if ever, to redeem the bond. However, the creditor would receive annual interest payments for as long as the bond is held. Hamilton’s plan allowed the government to gradually pay its debt to its constituents, supported by tax revenue. His plan also legitimized the new central government, as debtholders were now financially interested in the national government’s continued success. 
    ''', style = {'font-size':'3vh'}),
    html.H2("Our Role", style={'marginBottom': '5px'}, className='subsection-title'),

    dcc.Markdown('''
	Professor Sargent and Hall provided the team with ledger records for individuals who redeemed debt following Hamilton’s plan in 1790. Using this ledger, in conjunction with 1790 federal census data, the research team, over the summers of 2021, 2022 and 2023, transformed the ledger into a debtholder-level dataset containing aggregate debt holdings. Using this dataset, which you can learn more about in [data](/data_doc), along with supplementary datasets on population, we created tools that allow users to create customizable maps (available in [maps](/maps)) and tables + charts (available in [tables](/tables)) describing the data. Our hope is that the work done by the summer 2023 team to transform our previous analysis into an analytical tool will allow both us and other researchers to perform better, more in-depth analysis.
    ''', style = {'font-size':'3vh'}),
    ])


    # Create the layout
history_layout = html.Div([
    project_desc,
    
])
