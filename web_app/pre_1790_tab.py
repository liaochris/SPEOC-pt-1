import pandas as pd
from dash import html, dash_table
from dash import dcc
from dash import Dash

app = Dash(__name__)

_pre1790_df = (
    pd.read_csv("data_raw/pre1790/clean_files/liquidated_debt_certificates.csv")
      .drop_duplicates(subset="uid")
)

def get_pre1790_layout(page_size=10):
    return html.Div([
        html.H4("Liquidated Debt Certificates"),
        dash_table.DataTable(
            columns=[
                {"name": "Certificate Month", "id": "Date of the Certificate Month"},
                {"name": "Certitificate Day", "id": "Day"},
                {"name": "Certificate Year", "id": "Year"},
                {"name": "State", "id": "state"},
                {"name": "Title", "id": "Title"},
                {"name": "First Name", "id": "raw_first_name_1"},
                {"name": "Last Name", "id": "raw_last_name_1"},
                {"name": "Month Due", "id": "Time when the debt became due Month"},
                {"name": "Day Due", "id": "Day2"},
                {"name": "Year Due", "id": "Year2"},
                {"name": "Dollars", "id": "Dollars"},
                {"name": "90th", "id": "90th"}
            ],
            data=_pre1790_df.to_dict("records"),
            page_action="native",  
            page_current=0, 
            page_size=page_size,

            sort_action="none", 
            filter_action="none", 
            virtualization=True,

            style_table={
                "height": "400px",        
                "overflowY": "auto",      
                "overflowX": "auto"
            }
        )
    ])
_pre1790_pierce_df = (
    pd.read_csv("data_raw/pre1790/Pierce_Certs_cleaned_2019.csv")
        .drop_duplicates(subset="uid")
)

def get_pre1790_pierce_layout(page_size=10):
    return html.Div([
        html.H4("Cleaned Pierce Certificates"),
        dash_table.DataTable(
            columns=[
                {"name": "First Name", "id": "First"},
                {"name": "Last Name", "id": "Last"},
                {"name": "Dollars", "id": "Value"},
                {"name": "Issued to", "id": "To Whom Issued"},
                {"name": "State", "id": "State"},
            ],
            data=_pre1790_pierce_df.to_dict("records"),
            page_action="native",
            page_current=0,
            page_size=page_size,
        )
    ])
    
def get_pre1790_loan_layout(page_size=10):
    return html.Div([
        html.H4("Loan Office Certificates"),
        dash_table.DataTable(
            columns=[
                {"name": "Year", "id": "Year"},
                {"name": "Month", "id": "Month"},
                {"name": "Day", "id": "Day"},
                {"name": "Title (person 1)", "id": "Title 1"},
                {"name": "First Name (person 1)", "id": "First Name 1"},
                {"name": "Last Name (person 1)", "id": "Last Name 1"},
                {"name": "Title (person 2)", "id": "Title 2"},
                {"name": "First Name (person 2)", "id": "First Name 2"},
                {"name": "Last Name (person 2)", "id": "Last Name 2"},
                {"name": "Face Value", "id": "Face Value"},
                {"name": "Specie Value", "id": "Specie Value"},
            ]
        )
    ])
    
if __name__ == '__main__':
    app.run(debug=True)
