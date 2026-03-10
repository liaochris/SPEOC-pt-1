#!/usr/bin/env python
# coding: utf-8

from pathlib import Path
import pandas as pd
from source.lib.SaveData import SaveData

INDIR_OPENREFINE = Path("output/analysis/open_refine_analysis")
OUTDIR = Path("output/analysis/debt_analysis")
OUTDIR.mkdir(parents=True, exist_ok=True)

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
    input_csv = INDIR_OPENREFINE / "liquidated_debt_certificates.csv"
    output_csv = OUTDIR / "matches_liquidated_debt_certificates.csv"

    df = pd.read_csv(input_csv, usecols=["raw_name", "state", "Dollars", "90th"], low_memory=False)

    pairs = pd.MultiIndex.from_frame(TREASURERS[["raw_name", "state"]])
    mask = pd.MultiIndex.from_frame(df[["raw_name", "state"]]).isin(pairs)
    matches = df[mask].assign(original_row=df.index[mask]+1)[["original_row", "raw_name", "state", "Dollars", "90th"]]

    print(matches)
    SaveData(matches, ['raw_name', 'state'], output_csv, log_file=output_csv.with_suffix('.log'))


def SearchLoanOfficeCerts():
    input_csv = INDIR_OPENREFINE / "loan_office_certificates_cleaned.csv"
    output_csv = OUTDIR / "matches_loan_office_certificates.csv"
    totals_csv = OUTDIR / "matches_loan_office_certificates_totals.csv"

    df = pd.read_csv(input_csv, usecols=["raw_name", "state", "Face Value", "Specie Value"], low_memory=False)

    pairs = pd.MultiIndex.from_frame(TREASURERS[["raw_name", "state"]])
    mask = pd.MultiIndex.from_frame(df[["raw_name", "state"]]).isin(pairs)
    matches = df[mask].assign(original_row=df.index[mask]+1)[["original_row", "raw_name", "state", "Face Value", "Specie Value"]]

    print(matches)
    SaveData(matches, ['raw_name', 'state', 'original_row'], output_csv, log_file=output_csv.with_suffix('.log'))

    totals_per_person = (
        matches.groupby(["raw_name", "state"], as_index=False)
               .agg({"Face Value": "sum", "Specie Value": "sum"})
               .rename(columns={
                   "Face Value": "Total Face Value",
                   "Specie Value": "Total Specie Value"
               })
    )

    SaveData(totals_per_person, ['raw_name', 'state'], totals_csv, log_file=totals_csv.with_suffix('.log'))
    print(totals_per_person)


if __name__ == "__main__":
    Main()
