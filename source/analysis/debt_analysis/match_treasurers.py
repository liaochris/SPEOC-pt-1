#!/usr/bin/env python
# coding: utf-8

from pathlib import Path
import pandas as pd

INDIR_PRE1790 = Path("output/derived/pre1790")
OUTDIR = Path("output/analysis/debt_analysis")

TREASURERS = pd.DataFrame(
    [("WILLIAM GARDNER","NH"),
     ("SAMUEL MATTOCKS","VT"),
     ("ALEXANDER HODGDON","MA"),
     ("JOSEPH CLARK","RI"),
     ("JEDEDIAH HUNTINGTON","CT"),
     ("GERARD BANCKER","NY"),
     ("JAMES MOTT","NJ"),
     ("CHRISTIAN FEBIGER","PA"),
     ("SAMUEL PATTERSON","DE"),
     ("WILLIAM RICHARDSON","MD"),
     ("SAMUEL MATTOCKS","VA"),
     ("JOHN HAYWOOD","NC"),
     ("JOHN MEALS","GA")],
    columns=["raw_name", "state"]
)


def Main():
    SearchLiquidatedDebt()
    SearchLoanOfficeCerts()


def SearchLiquidatedDebt():
    input_csv = INDIR_PRE1790 / "liquidated_debt_certificates_combined.csv"
    output_csv = OUTDIR / "matches_liquidated_debt_certificates.csv"

    df = pd.read_csv(input_csv, usecols=["raw_name", "state", "Dollars", "90th"], low_memory=False)

    pairs = pd.MultiIndex.from_frame(TREASURERS[["raw_name", "state"]])
    mask = pd.MultiIndex.from_frame(df[["raw_name", "state"]]).isin(pairs)
    matches = df[mask].assign(original_row=df.index[mask]+1)[["original_row", "raw_name", "state", "Dollars", "90th"]]

    print(matches)
    matches.to_csv(output_csv, index=False)


def SearchLoanOfficeCerts():
    input_csv = INDIR_PRE1790 / "loan_office_certificates_cleaned.csv"
    output_csv = OUTDIR / "matches_loan_office_certificates.csv"
    totals_csv = OUTDIR / "matches_loan_office_certificates_totals.csv"

    df = pd.read_csv(input_csv, usecols=["raw_name", "state", "Face Value", "Specie Value"], low_memory=False)

    pairs = pd.MultiIndex.from_frame(TREASURERS[["raw_name", "state"]])
    mask = pd.MultiIndex.from_frame(df[["raw_name", "state"]]).isin(pairs)
    matches = df[mask].assign(original_row=df.index[mask]+1)[["original_row", "raw_name", "state", "Face Value", "Specie Value"]]

    print(matches)
    matches.to_csv(output_csv, index=False)

    totals_per_person = (
        matches.groupby(["raw_name", "state"], as_index=False)
               .agg({"Face Value": "sum", "Specie Value": "sum"})
               .rename(columns={
                   "Face Value": "Total Face Value",
                   "Specie Value": "Total Specie Value"
               })
    )

    totals_per_person.to_csv(totals_csv, index=False)
    print(totals_per_person)


if __name__ == "__main__":
    Main()
