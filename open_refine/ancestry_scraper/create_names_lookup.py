"""
import pandas as pd

df = pd.read_csv("data/loan_office_certificates_cleaned.csv")

de = df[df["state"] == "DE"]

to_lookup = de[["Year", "raw_name"]]

unique_to_lookup = to_lookup.drop_duplicates()
unique_to_lookup.to_csv("names_to_lookup/names_to_lookup_de.csv", index=False, header=["year", "name"])
"""

import pandas as pd
from pathlib import Path

def create_all_state_lookups(
    input_csv: Path = Path("data/loan_office_certificates_cleaned.csv"),
    output_dir: Path = Path("names_to_lookup")
):
    # 1) Read your master table
    df = pd.read_csv(input_csv)

    # 2) Make sure output dir exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # 3) For each unique state code, extract & dedupe Year+Name, write CSV
    for state in sorted(df["state"].dropna().unique()):
        sub = df[df["state"] == state]
        to_lookup = (
            sub[["Year", "raw_name"]]
              .drop_duplicates()
              .rename(columns={"Year": "year", "raw_name": "name"})
        )
        out_file = output_dir / f"names_to_lookup_{state.lower()}.csv"
        to_lookup.to_csv(out_file, index=False)
        print(f"Wrote {len(to_lookup)} rows → {out_file}")

if __name__ == "__main__":
    create_all_state_lookups()