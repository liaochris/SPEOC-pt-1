from dash import html
from dash import dcc

def project_description_layout():
    #Define javascript code to create image transition
    javascript_code = """
    <script>
    window.addEventListener('scroll', function() {
        const header = document.querySelector('.project-header');
        const contentContainer = document.getElementById('content-container');

        const scrollY = window.scrollY;
        if (scrollY > 100) { // Adjust the threshold value as needed
            header.style.opacity = '0.5'; // Adjust opacity value as needed
            header.style.transform = 'scale(0.9)'; // Adjust scaling as needed
            contentContainer.classList.add('content-transparent');
        } else {
            header.style.opacity = '1';
            header.style.transform = 'scale(1)';
            contentContainer.classList.remove('content-transparent');
        }
    });
    </script>
    """
    
    return html.Div(
        className='project-page',
        children=[
            html.H1('Project Description'),
            html.Div(
                className='project-description',
                children=[
                    html.Img(src='https://www.cui.edu/portals/0/adam/blog%20app/uarybrxxh0gt0ogq9utohg/image/we-the-people-header.jpg', className='project-header'),
                    html.H3('Historical Background', className='project-text'),
                    html.P("In the Revolutionary War, the Continental Congress and states accumulated debt to fund war efforts against the British. In exchange for goods and services that individuals provided to the Revolutionary cause, the Continental Congress issued two types of debt: interest-bearing debts and paper monies, called “Continental Dollars”. The interest-bearing debts periodically paid interest to the debtholder and promised principal payment of the original loaned amount at a later, unspecified date. Continental Dollars depreciated in value as the Continental Congress continued to issue them through 1780, causing inflation. Eventually, one Continental Dollar became worth much less than one Spanish Dollar at a 50:1 exchange rate due to overissuance. By 1781, two years before the end of the Revolutionary War and the Treaty of Paris, the Continental Congress owed 41 million Spanish Dollars, more than $1.6 billion today, and by 1789 the debt amount had grown 29% to 53 million Spanish dollars due to interest in arrears. Interest in arrears refers to unpaid interest; in 1784, the Continental Congress owed $2 million in interest in arrears but raised less than $1 million in revenue. The Articles of Confederation limited the Continental Congress’ ability to raise revenue through taxation. Having already exhausted printing and issuing Continental Dollars, the debt amount continued to grow. The Continental Congress’ growing inability to pay annual interest on the debt, much less the principal debt amount, ignited doubt in its ability as a credible borrower. Subsequent to this doubt, the specie (or market value) of the certificate of debt was much lower than the certificate’s face value."
                           "In efforts to resolve this issue, the first Secretary of the Treasury, Alexander Hamilton— appointed by George Washington—proposed a debt framework to use the large debt amount to the nation’s advantage. In his Funding Act of August 4, 1790, Hamilton proposed that the United States government, newly centralized, assume the debt both of the Continental Congress and the individual states’ debts. As a result, the federal government’s debt total reached 74.3 million Spanish Dollars in September of 1790. The Funding Act permitted the Department of the Treasury to issue three new types of loans: (1) consols that paid a 6% coupon, (2) consols that paid a 3% coupon, and (3) consols that paid a 6% coupon and deferred interest payments until 1801. Although many domestic creditors ultimately received less than the $100 promised by the face value of their certificate, many of them had purchased the debt amount for a far less value of about $20, and thus their return on investment was still positive by redeeming the certificate under Hamilton’s plan at a $75 market value."
                           "The consols established under Hamilton’s proposal were government debt certificates in the form of perpetual bonds that could be funded gradually by tax revenue. As perpetual bonds, these consols had no maturity date at which the principal payment of the bond must be paid back. Instead, the government could choose whenever, if ever, to redeem the bond., Hhowever, the creditor would receive annual interest payments for as long as the bond is held. The issuance of the consols under Hamilton’s plan thus served two main purposes: to raise the legitimacy of the new centralized government by assuming state debts and paying back its debt, and to create a system that allowed the government to gradually pay its debt to its constituents as tax revenue increases under the Constitution’s broader congressional power to tax."),
                    html.H3('What We Do', className='project-text'),
                    html.P("[drafted 07/23] Over 200 years later, the Alexander Hamilton Project has collected many of the debt records and data pertaining to debt holders before and after Hamilton’s 1790 Funding Act. In an effort to organize and analyze the data of these debt certificates, debt purchasers, and redeemers, the project has collected state census data from Ancestry.com. The data includes the household demographic, ownership of enslaved people, occupation, and residence of the security holders." 
                           "The Alexander Hamilton Project has obtained over 208,000 individual debt certificates issued by the Continental government. Such data is only based on the state debt assumed by the centralized government, not the debt issued by the states during the Revolution. To compare and match the creditors who assumed debt before 1790 by exchanging certificates of debt for goods and services to the individuals who exchanged debt for consols under Hamilton’s plan, members of our team have created an automated name cleaning and matching system to match individuals with records in pre- and post-1790s securities. In addition, using the cleaned post-1790 data, members could determine the geographical distribution of debt as well as the overall debt held by certain occupations."
                           "Further, the web application designed for this project includes data visualization tools depicting the matched pre-1790 creditors and post-1790 individuals. Our team has produced several heat maps to display data such as population, slave population, debt density, debt distribution, and average debt holdings at national, state, and county levels. Through our website, users can further customize the maps by adjusting metric thresholds and selecting additional statistical information to display. When displaying statistical information, users can select the amount of information they want to display. For example, they can display information pertaining to the entire nation, each individual state, or even down to every county.  [insert more information about the map tools and uses] Additionally, [insert more information about the tables tools]."
                           "[Insert analysis and conclusions/purpose of the web app and data]"),
                ],
                id='content-container',  # Add an id to the content container
                style={"margin": "0 200px", "position": "relative"}
            ),
            dcc.Markdown(javascript_code) #Adding JavaScript to layout
        ],
        style={"display": "flex", "flex-direction": "column", "align-items": "center"}
    )