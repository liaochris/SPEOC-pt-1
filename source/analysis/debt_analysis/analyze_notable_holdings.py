from pathlib import Path
import re
import os
import pandas as pd
from source.lib.SaveData import SaveData

INDIR_PRE1790 = Path("output/derived/prescrape/pre1790")
INDIR_SPECULATORS = Path("source/analysis/debt_analysis")
OUTDIR = Path("output/analysis/debt_analysis")
OUTDIR.mkdir(parents=True, exist_ok=True)

SPECULATORS = pd.read_csv(INDIR_SPECULATORS / "speculators.csv")["name"].tolist()

CSV_FILES = {
    "Pierce_Certs_cleaned_2019.csv": {"first": "First", "last": "Last", "dollars": "Value"},
    "liquidated_debt_certificates_DE.csv": {"first": "First", "last": "Last", "dollars": "Dollars"},
    "loan_office_certificates_9_states.csv": {"first": "First", "last": "Last", "dollars": "Specie Value"},
    "Marine_Liquidated_Debt_Certificates.csv": {"first": "First", "last": "Last", "dollars": "Dollars"},
    "liquidated_debt_certificates_CT.csv": {"first": "First", "last": "Last", "dollars": "Dollars"},
    "liquidated_debt_certificates_MA_cleaned.csv": {"first": "First", "last": "Last", "dollars": "Dollars"},
    "liquidated_debt_certificates_NH.csv": {"first": "First", "last": "Last", "dollars": "Dollars"},
    "liquidated_debt_certificates_NJ.csv": {"first": "First", "last": "Last", "dollars": "Dollars"},
    "liquidated_debt_certificates_NY.csv": {"first": "First", "last": "Last", "dollars": "Dollars"},
    "liquidated_debt_certificates_PA_stelle.csv": {"first": "First", "last": "Last", "dollars": "Dollars"},
    "liquidated_debt_certificates_PA_story.csv": {"first": "First", "last": "Last", "dollars": "Dollars"},
    "liquidated_debt_certificates_RI.csv": {"first": "First", "last": "Last", "dollars": "Dollars"},
}


def Main():
    MatchInCleaned()
    MatchAcrossFiles()
    ComputeDollarValues()


def FindSpeculator(name):
    name = str(name).lower()
    for speculator in SPECULATORS:
        if re.search(r'\b' + re.escape(speculator.lower()) + r'\b', name):
            return speculator
    return None


def IsSpeculator(first_name, last_name):
    if pd.isna(first_name) or pd.isna(last_name):
        return False
    full_name = f"{first_name} {last_name}".lower()
    return any(speculator.lower() in full_name for speculator in SPECULATORS)


def ProcessFile(file_name, df, columns):
    first_col, last_col = columns['first'], columns['last']
    if first_col not in df.columns or last_col not in df.columns:
        return {}
    df = df.copy()
    df['full_name'] = df[first_col].astype(str) + ' ' + df[last_col].astype(str)
    matches = df['full_name'].apply(FindSpeculator)
    found = {}
    for speculator in matches.dropna().unique():
        found[speculator] = file_name
    return found


def MatchInCleaned():
    df = pd.read_csv(INDIR_PRE1790 / "pre1790_cleaned.csv", low_memory=False)
    df['is_speculator'] = df.apply(
        lambda row: IsSpeculator(row['to whom due | first name'], row['to whom due | last name']), axis=1
    )
    speculator_rows = df[df['is_speculator']].copy()
    SaveData(
        speculator_rows,
        ['row_id'],
        OUTDIR / "speculator_matches_pre1790_cleaned.csv",
        log_file=OUTDIR / "speculator_matches_pre1790_cleaned.log",
    )


def MatchAcrossFiles():
    speculator_files = {name: set() for name in SPECULATORS}
    for file_name, columns in CSV_FILES.items():
        file_path = os.path.join(INDIR_PRE1790, file_name)
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path, low_memory=False)
                found = ProcessFile(file_name, df, columns)
                for speculator, fname in found.items():
                    speculator_files[speculator].add(fname)
            except Exception:
                pass

    results = [
        {"Speculator": spec, "Files": ', '.join(sorted(files))}
        for spec, files in speculator_files.items()
        if files
    ]
    results_df = pd.DataFrame(results) if results else pd.DataFrame(columns=["Speculator", "Files"])
    SaveData(
        results_df,
        ["Speculator"],
        OUTDIR / "speculator_file_matches.csv",
        log_file=OUTDIR / "speculator_file_matches.log",
    )


def ComputeDollarValues():
    speculator_totals = {speculator: 0 for speculator in SPECULATORS}
    for file_name, columns in CSV_FILES.items():
        file_path = os.path.join(INDIR_PRE1790, file_name)
        if not os.path.exists(file_path):
            continue
        try:
            df = pd.read_csv(file_path, low_memory=False)
            dollars_col = columns.get("dollars")
            if dollars_col is None or dollars_col not in df.columns:
                continue
            df = df.rename(columns={
                columns["first"]: "First",
                columns["last"]: "Last",
                dollars_col: "Dollars",
            })
            df["Dollars"] = pd.to_numeric(df["Dollars"], errors="coerce")
            df["Full Name"] = df["First"].astype(str) + " " + df["Last"].astype(str)
            df["Speculator"] = df["Full Name"].apply(FindSpeculator)
            for speculator in SPECULATORS:
                total = df.loc[df["Speculator"] == speculator, "Dollars"].sum()
                if total > 0:
                    speculator_totals[speculator] += total
        except Exception:
            pass

    results_df = pd.DataFrame(list(speculator_totals.items()), columns=["Speculator", "Total Dollar Value"])
    results_df = results_df[results_df["Total Dollar Value"] > 0].sort_values("Total Dollar Value", ascending=False)
    SaveData(
        results_df,
        ["Speculator"],
        OUTDIR / "speculator_dollar_values.csv",
        log_file=OUTDIR / "speculator_dollar_values.log",
    )


if __name__ == "__main__":
    Main()
