from pathlib import Path
import pandas as pd
from rapidfuzz import process, fuzz
from source.lib.SaveData import SaveData

INDIR_RAW = Path("source/raw/pre1790/orig")
INDIR_DERIVED = Path("output/derived/prescrape/pre1790")
OUTDIR = Path("output/analysis/pre1790")
OUTDIR.mkdir(parents=True, exist_ok=True)

FUZZY_THRESHOLD = 90

STATE_FILES = {
    "RI": {
        "file": "liquidated_debt_certificates_RI.xlsx",
        "name_cols": ["First_Name", "Last_Name", "First_Name.1", "Last_Name.1"],
        "day_cols": ["Day", "Day_Due", "Day_Delivered"],
        "month_cols": ["Month", "Month_Due", "Month_Delivered"],
        "year_cols": ["Year", "Year_Due", "Year_Delivered"],
    },
    "PA": {
        "file": "liquidated_debt_certificates_PA_stelle.xlsx",
        "name_cols": ["First_Name", "Last_Name", "First_Name.1", "Last_Name.1"],
        "day_cols": ["Date", "Date_Due"],
        "month_cols": ["Month", "Month_Due"],
        "year_cols": ["Year", "Year_Due"],
    },
    "NY": {
        "file": "liquidated_debt_certificates_NY.xlsx",
        "name_cols": ["First_Name", "Last_Name", "First_Name.1", "Last_Name.1"],
        "day_cols": ["Day", "Day_Due"],
        "month_cols": ["Month", "Month_Due"],
        "year_cols": ["Year", "Year_Due"],
    },
    "NJ": {
        "file": "liquidated_debt_certificates_NJ.xlsx",
        "name_cols": ["First_Name", "Last_Name", "First_Name.1", "Last_Name.1"],
        "day_cols": ["Day", "Day_Due"],
        "month_cols": ["Month", "Month_Due"],
        "year_cols": ["Year", "Year_Due"],
    },
    "NH": {
        "file": "liquidated_debt_certificates_NH.xlsx",
        "name_cols": ["First_Name", "Last_Name"],
        "day_cols": ["Day", "Day_Due"],
        "month_cols": ["Month", "Month_Due"],
        "year_cols": ["Year", "Year_Due"],
    },
    "MA": {
        "file": "liquidated_debt_certificates_MA.xlsx",
        "name_cols": ["First_Name", "Last_Name", "First_Name.1", "Last_Name.1"],
        "day_cols": ["Date", "Date_Due"],
        "month_cols": ["Month", "Month_Due"],
        "year_cols": ["Year", "Year_Due"],
    },
    "DE": {
        "file": "liquidated_debt_certificates_DE.xlsx",
        "name_cols": ["First_Name", "Last_Name"],
        "day_cols": ["Date", "Date_Due"],
        "month_cols": ["Month", "Month_Due"],
        "year_cols": ["Year", "Year_Due"],
    },
    "CT": {
        "file": "liquidated_debt_certificates_CT.xlsx",
        "name_cols": ["First_Name", "Last_Name", "First_name.1", "Last_name.1"],
        "day_cols": ["Day", "Day_Due"],
        "month_cols": ["Month", "Month_Due"],
        "year_cols": ["Year", "Year_Due"],
    },
}


def Main():
    fuzzy_rows, val_rows = [], []

    for state, config in STATE_FILES.items():
        df = pd.read_excel(INDIR_RAW / config["file"])
        fuzzy_rows += FuzzyMatchCols(df, state, config["name_cols"])
        val_rows += DateMonthYearCounts(df, state, config["day_cols"], config["month_cols"], config["year_cols"])

    pierce_df = pd.read_excel(INDIR_RAW / "Pierce_Certs_cleaned_2019.xlsx")
    fuzzy_rows += FuzzyMatchCols(pierce_df, "Pierce", ["First", "Last"])

    marine_df = pd.read_excel(INDIR_RAW / "Marine_Liquidated_Debt_Certificates.xlsx")
    fuzzy_rows += FuzzyMatchCols(marine_df, "Marine", ["First_Name", "Last_Name"])
    val_rows += DateMonthYearCounts(marine_df, "Marine", ["Day", "Day_Due"], ["Month", "Month_Due"], ["Year", "Year_Due"])

    fuzzy_df = pd.DataFrame(fuzzy_rows, columns=["source_file", "column", "original", "match", "score"])
    SaveData(fuzzy_df, ["source_file", "column", "original", "match"], OUTDIR / "fuzzy_matches_pre1790.csv", log_file=OUTDIR / "fuzzy_matches_pre1790.log")

    val_df = pd.DataFrame(val_rows, columns=["source_file", "check", "count"])
    SaveData(val_df, ["source_file", "check"], OUTDIR / "validation_report_pre1790.csv", log_file=OUTDIR / "validation_report_pre1790.log")

    ValidateCombined()


def FuzzyMatchCols(df, source, cols):
    rows = []
    for col in cols:
        if col not in df.columns:
            continue
        unique_vals = [v for v in df[col].dropna().unique().tolist() if isinstance(v, str)]
        for val in unique_vals:
            for match_val, score, _ in process.extract(val, unique_vals, scorer=fuzz.token_sort_ratio):
                if val != match_val and score >= FUZZY_THRESHOLD:
                    rows.append((source, col, val, match_val, score))
    return rows


def DateMonthYearCounts(df, source, day_cols, month_cols, year_cols):
    rows = []
    for col in day_cols:
        if col in df.columns:
            rows.append((source, f"days_over_31_{col}", int((pd.to_numeric(df[col], errors="coerce") > 31).sum())))
    for col in month_cols:
        if col in df.columns:
            rows.append((source, f"months_over_12_{col}", int((pd.to_numeric(df[col], errors="coerce") > 12).sum())))
    for col in year_cols:
        if col in df.columns:
            rows.append((source, f"years_over_1790_{col}", int((pd.to_numeric(df[col], errors="coerce") > 1790).sum())))
    return rows


def ValidateCombined():
    pre1790 = pd.read_csv(INDIR_DERIVED / "pre1790_cleaned.csv")
    pre1790.drop_duplicates(inplace=True)

    amount_fields = [c for c in ["amount | dollars", "amount | 90th"] if c in pre1790.columns]
    name_cols = ["to whom due | first name", "to whom due | last name", "to whom due | first name.1", "to whom due | last name.1", "to whom due | title.1", "to whom due | title"]
    mask_name_missing = pre1790[[c for c in name_cols if c in pre1790.columns]].isnull().any(axis=1)
    mask_amount_present = pre1790[amount_fields].notnull().any(axis=1) if amount_fields else pd.Series([False] * len(pre1790))
    mask_uncombined = mask_name_missing & mask_amount_present

    numeric_pattern = ["amount"]
    numeric_obj_cols = [c for c in pre1790.select_dtypes(include="object").columns if any(p in c for p in numeric_pattern)]
    for col in numeric_obj_cols:
        pre1790[col] = pd.to_numeric(pre1790[col].astype(str).str.replace(",", ""), errors="coerce")

    mask_negative = pre1790[[c for c in pre1790.columns if any(p in c for p in numeric_pattern)]].lt(0).any(axis=1)

    day_col = "date of the certificate | day"
    month_col = "date of the certificate | month"
    mask_strange_date = (pd.to_numeric(pre1790.get(day_col), errors="coerce") > 31).fillna(False)
    mask_strange_month = (pd.to_numeric(pre1790.get(month_col), errors="coerce") > 12).fillna(False)

    pre1790["suspicious_row"] = False
    pre1790["suspicious_reason"] = ""

    mask_many_missing = pre1790.isnull().sum(axis=1) > pre1790.shape[1] / 4
    pre1790.loc[mask_many_missing, "suspicious_row"] = True
    pre1790.loc[mask_many_missing, "suspicious_reason"] += "More than 25% missing; "

    pre1790.loc[mask_negative, "suspicious_row"] = True
    pre1790.loc[mask_negative, "suspicious_reason"] += "Negative value; "

    pre1790.loc[mask_uncombined, "suspicious_row"] = True
    pre1790.loc[mask_uncombined, "suspicious_reason"] += "Uncombined row; "

    pre1790.loc[mask_strange_date, "suspicious_row"] = True
    pre1790.loc[mask_strange_date, "suspicious_reason"] += "Date over 31; "

    pre1790.loc[mask_strange_month, "suspicious_row"] = True
    pre1790.loc[mask_strange_month, "suspicious_reason"] += "Month over 12; "

    clean = pre1790[~pre1790["suspicious_row"]].copy()
    suspicious = pre1790[pre1790["suspicious_row"]].copy()

    SaveData(clean, ["row_id"], OUTDIR / "clean_pre1790.csv", log_file=OUTDIR / "clean_pre1790.log")
    SaveData(suspicious, ["row_id"], OUTDIR / "suspicious_pre1790.csv", log_file=OUTDIR / "suspicious_pre1790.log")


if __name__ == "__main__":
    Main()
