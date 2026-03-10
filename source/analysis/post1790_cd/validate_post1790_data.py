from pathlib import Path
import pandas as pd
from rapidfuzz import process, fuzz
from source.lib.SaveData import SaveData

INDIR_POST1790_CD = Path("source/raw/post1790_cd/orig")
INDIR_POST1790_ASD = Path("source/raw/post1790_asd/orig")
INDIR_DERIVED = Path("output/derived/prescrape/post1790_cd")
OUTDIR = Path("output/analysis/post1790_cd")
OUTDIR.mkdir(parents=True, exist_ok=True)

FUZZY_THRESHOLD = 90
ASD_DAY_COLS = ["Def_6p_Day", "6p_Day", "3p_Day"]
ASD_MONTH_COLS = ["Def_6p_Month", "6p_Month", "3p_Month"]
ASD_YEAR_COLS = ["Def_6p_Year", "6p_Year", "3p_Year"]
ASD_NAME_COLS = ["6p_First_Name", "6p_Last_Name", "Def_6p_First_Name", "Def_6p_Last_Name", "3p_First_Name", "3p_Last_Name"]


def Main():
    fuzzy_rows, val_rows = [], []

    for state in ["VA", "RI", "NY", "NH"]:
        df = pd.read_excel(INDIR_POST1790_ASD / f"{state}/{state}_ASD.xlsx")
        df.drop_duplicates(inplace=True)
        fuzzy_rows += FuzzyMatchCols(df, state, ASD_NAME_COLS)
        val_rows += DateMonthYearCounts(df, state, ASD_DAY_COLS, ASD_MONTH_COLS, ASD_YEAR_COLS, 1790)

    for state in ["SC", "PA"]:
        df = pd.read_excel(INDIR_POST1790_CD / f"{state}/{state}_CD.xlsx")
        df.columns = df.columns.str.strip()
        fuzzy_rows += FuzzyMatchCols(df, state, ASD_NAME_COLS)
        val_rows += DateMonthYearCounts(df, state, ASD_DAY_COLS, ASD_MONTH_COLS, ASD_YEAR_COLS, 1790)

    nc_df = pd.read_excel(INDIR_POST1790_ASD / "NC/NC_ASD.xlsx")
    nc_df.drop_duplicates(inplace=True)
    fuzzy_rows += FuzzyMatchCols(nc_df, "NC", ["First_Name", "Last_Name"])
    val_rows += DateMonthYearCounts(nc_df, "NC", ["Day"], ["Month"], ["Year"], 1790)

    md_df = pd.read_excel(INDIR_POST1790_ASD / "MD/MD_ASD.xlsx")
    md_df.drop_duplicates(inplace=True)
    fuzzy_rows += FuzzyMatchCols(md_df, "MD", ["6p_Name", "6p_Last Name", "6p_Def_First_Name", "6p_Def_Last_Name", "3p_First_Name", "3p_Last_Name"])
    val_rows += DateMonthYearCounts(md_df, "MD", ["6p_Day", "6p_Def_Day", "3p_Day"], ["6p_Def_Month", "6p_Month", "3p_Month"], ["6p_Def_Year", "6p_Year", "3p_Year"], 1790)

    nj_df = pd.read_excel(INDIR_POST1790_CD / "NJ/NJ_CD.xlsx")
    nj_df.drop_duplicates(inplace=True)
    fuzzy_rows += FuzzyMatchCols(nj_df, "NJ", ["First_Name", "Last_Name"])
    val_rows += DateMonthYearCounts(nj_df, "NJ", ["Day"], ["Month"], [], 1790)

    ga_df = pd.read_excel(INDIR_POST1790_CD / "GA/GA_CD.xlsx")
    ga_df.drop_duplicates(inplace=True)
    fuzzy_rows += FuzzyMatchCols(ga_df, "GA", ["First_Name", "Last_Name", "First_Name.1"])
    val_rows += DateMonthYearCounts(ga_df, "GA", ["Day"], ["Month"], ["Year"], 1790)

    ct_df = pd.read_excel(INDIR_POST1790_CD / "CT/CT_CD.xlsx")
    ct_df.drop_duplicates(inplace=True)
    ct_df.columns = ct_df.columns.str.strip()
    fuzzy_rows += FuzzyMatchCols(ct_df, "CT", ["6p_First_Name", "6p_Last_Name", "Def_6_Last_Name", "Def_6p_First_Name", "3p_First_Name", "3p_Last_Name"])

    fuzzy_df = pd.DataFrame(fuzzy_rows, columns=["state", "column", "original", "match", "score"])
    SaveData(fuzzy_df, ["state", "column", "original", "match"], OUTDIR / "fuzzy_matches_post1790.csv", log_file=OUTDIR / "fuzzy_matches_post1790.log")

    val_df = pd.DataFrame(val_rows, columns=["state", "check", "count"])
    SaveData(val_df, ["state", "check"], OUTDIR / "validation_report_post1790.csv", log_file=OUTDIR / "validation_report_post1790.log")

    ValidateAggregated()


def FuzzyMatchCols(df, state, cols):
    rows = []
    for col in cols:
        if col not in df.columns:
            continue
        unique_vals = df[col].dropna().unique().tolist()
        for val in unique_vals:
            for match_val, score, _ in process.extract(val, unique_vals, scorer=fuzz.token_sort_ratio):
                if val != match_val and score >= FUZZY_THRESHOLD:
                    rows.append((state, col, val, match_val, score))
    return rows


def DateMonthYearCounts(df, state, day_cols, month_cols, year_cols, year_limit):
    rows = []
    for col in day_cols:
        if col in df.columns:
            rows.append((state, f"days_over_31_{col}", int((pd.to_numeric(df[col], errors="coerce") > 31).sum())))
    for col in month_cols:
        if col in df.columns:
            rows.append((state, f"months_over_12_{col}", int((pd.to_numeric(df[col], errors="coerce") > 12).sum())))
    for col in year_cols:
        if col in df.columns:
            rows.append((state, f"years_before_{year_limit}_{col}", int((pd.to_numeric(df[col], errors="coerce") < year_limit).sum())))
    return rows


def FlagRare(df, col_name, threshold=1):
    if col_name not in df.columns:
        return pd.Series([False] * len(df), index=df.index)
    counts = df[col_name].fillna(" ").str.strip().value_counts()
    rare_vals = counts[counts <= threshold].index
    return df[col_name].fillna(" ").str.strip().isin(rare_vals)


def ValidateAggregated():
    post1790 = pd.read_csv(INDIR_DERIVED / "geo_standardized_CD_post1790.csv")
    post1790.drop_duplicates(inplace=True)

    amount_fields = [c for c in ["6p_Dollar", "6p_Cents", "6p_def_Dollar", "6p_def_Cents", "3p_Dollar", "3p_Cents", "6p_total", "6p_def_total", "3p_total"] if c in post1790.columns]
    mask_name_missing = post1790["Name"].isnull() if "Name" in post1790.columns else pd.Series([False] * len(post1790))
    mask_amount_present = post1790[amount_fields].notnull().any(axis=1) if amount_fields else pd.Series([False] * len(post1790))
    mask_uncombined = mask_name_missing & mask_amount_present

    numeric_pattern = ["Dollar", "Cents", "Total"]
    numeric_obj_cols = [c for c in post1790.select_dtypes(include="object").columns if any(p in c for p in numeric_pattern)]
    for col in numeric_obj_cols:
        post1790[col] = pd.to_numeric(post1790[col].astype(str).str.replace(",", ""), errors="coerce")

    mask_negative = post1790[[c for c in post1790.columns if any(p in c for p in numeric_pattern)]].lt(0).any(axis=1)

    post1790["suspicious_row"] = False
    post1790["suspicious_reason"] = ""

    mask_many_missing = post1790.isnull().sum(axis=1) > post1790.shape[1] / 4
    post1790.loc[mask_many_missing, "suspicious_row"] = True
    post1790.loc[mask_many_missing, "suspicious_reason"] += "More than 25% missing; "

    post1790.loc[mask_negative, "suspicious_row"] = True
    post1790.loc[mask_negative, "suspicious_reason"] += "Negative value; "

    post1790.loc[mask_uncombined, "suspicious_row"] = True
    post1790.loc[mask_uncombined, "suspicious_reason"] += "Uncombined row; "

    for col in ["new_town", "town", "county"]:
        mask_rare = FlagRare(post1790, col, 1)
        post1790.loc[mask_rare, "suspicious_row"] = True
        post1790.loc[mask_rare, "suspicious_reason"] += f"Rare {col}; "

    clean = post1790[~post1790["suspicious_row"]].copy().reset_index(drop=True).reset_index().rename(columns={"index": "row_id"})
    suspicious = post1790[post1790["suspicious_row"]].copy().reset_index(drop=True).reset_index().rename(columns={"index": "row_id"})

    SaveData(clean, ["row_id"], OUTDIR / "clean_geo_standardized_post1790.csv", log_file=OUTDIR / "clean_geo_standardized_post1790.log")
    SaveData(suspicious, ["row_id"], OUTDIR / "suspicious_geo_standardized_post1790.csv", log_file=OUTDIR / "suspicious_geo_standardized_post1790.log")


if __name__ == "__main__":
    Main()
