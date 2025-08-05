import pandas as pd
from dash import html, dash_table

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

            sort_action="none", # disable sorting
            filter_action="none", # disable filtering
            virtualization=True,

            style_table={
                "height": "400px",        # pick a height that fits your layout
                "overflowY": "auto",      # allow vertical scrolling
                "overflowX": "auto"
            }
        )
    ])