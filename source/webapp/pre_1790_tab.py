from pathlib import Path
import pandas as pd
from dash import html, dash_table

REPO_ROOT = Path(__file__).resolve().parents[2]
INDIR_RAW = REPO_ROOT / "source/raw/pre1790"
INDIR_OPENREFINE = REPO_ROOT / "output/analysis/open_refine_analysis"

loan_df = pd.read_excel(INDIR_RAW / "orig/loan_office_certificates_9_states.xlsx")
loan_df.columns = loan_df.columns.str.strip()
_loan_office_df = loan_df.drop_duplicates(subset=[
    "State", "Year", "Month", "Day", "Title 1", "First Name 1", "Last Name 1",
    "Title 2", "First Name 2", "Last Name 2", "Face Value", "Specie Value"
])

pierce_df = pd.read_excel(INDIR_RAW / "orig/Pierce_Certs_cleaned_2019.xlsx")
_pre1790_pierce_df = pierce_df.drop_duplicates(
    subset=["First", "Last", "Value", "Group", "To Whom Issued", "State", "Officer"])

_pre1790_df = (
    pd.read_csv(INDIR_OPENREFINE / "liquidated_debt_certificates.csv", low_memory=False)
    .drop_duplicates(subset="uid")
)

def GetPre1790LiquidatedLayout(page_size=10):
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


def GetPre1790PierceLayout(page_size=10):
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
            data=_pre1790_pierce_df.to_dict("records"), # pyright: ignore[reportArgumentType]
            page_action="native",
            page_current=0,
            page_size=page_size,
        )
    ])
    
def GetPre1790LoanLayout(page_size=10):
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
            ],
            data=_loan_office_df.to_dict('records'),  
            page_action="native",
            page_current=0,
            page_size=page_size,
        )
    ])
    
def Layout():
    return html.Div([
        html.H2("Pre-1790 Data"),
        GetPre1790LiquidatedLayout(),
        html.Hr(),
        GetPre1790PierceLayout(),
        html.Hr(),
        GetPre1790LoanLayout()
    ])
