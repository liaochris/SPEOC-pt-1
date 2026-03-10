from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from source.lib.SaveData import SaveData

INDIR = Path("output/analysis/open_refine_analysis")
OUTDIR = Path("output/analysis/open_refine_analysis")
OUTDIR.mkdir(parents=True, exist_ok=True)

FEMALE_NAMES_1780 = {
    "Mary", "Elizabeth", "Sarah", "Hannah", "Nancy", "Margaret", "Anna",
    "Jane", "Catherine", "Lydia", "Martha", "Ann", "Rebecca", "Abigail",
    "Sally", "Catharine", "Betsey", "Polly", "Lucy", "Rachel", "Susannah",
    "Ruth", "Esther", "Maria", "Phebe", "Susan", "Eunice", "Susanna",
    "Barbara", "Rhoda", "Deborah", "Olive", "Eleanor", "Charlotte",
    "Frances", "Sophia", "Catharina", "Clarissa", "Anne", "Mercy", "Lois",
    "Magdalena", "Dorcas", "Amy", "Betsy", "Cynthia", "Fanny", "Eliza",
    "Charity", "Christina", "Lucinda", "Chloe", "Joanna", "Elisabeth",
    "Alice", "Huldah", "Jemima", "Isabella", "Patience", "Jerusha",
    "Judith", "Mehitable", "Prudence", "Agnes", "Priscilla", "Julia",
    "Ellen", "Dorothy", "Harriet", "Dolly", "Keziah", "Thankful", "Marie",
    "Matilda", "Lucretia", "Temperance", "Tabitha", "Rachael", "Phoebe",
    "Asenath", "Eve", "Salome", "Amelia", "Grace", "Patty", "Persis",
    "Comfort", "Eva", "Hester", "Louisa", "Naomi", "Rebekah", "Bridget",
    "Freelove", "Katherine", "Leah", "Caroline", "Marcy", "Annie", "Azubah",
}


def Main():
    loan_office_certs, post_1790 = LoadData()
    post_1790 = MarkMatchedStatus(loan_office_certs, post_1790)
    SaveData(
        post_1790,
        ["recon_id"],
        OUTDIR / "post_1790_with_matched_status.csv",
        log_file=OUTDIR / "post_1790_with_matched_status.log",
    )

    ExportTop5Debtholders(loan_office_certs)
    ExportStateDistribution(loan_office_certs)

    combined = ComputePercentChange(loan_office_certs, post_1790)
    ExportOutliers(combined)
    PlotPercentChangeDistribution(combined)

    ExportOccupationCounts(post_1790, loan_office_certs)
    ExportGenderSummary(loan_office_certs, post_1790)
    ExportRatioAnalysis(post_1790, loan_office_certs)
    PlotMatchedByState(loan_office_certs)


def LoadData():
    loan_office_certs = pd.read_csv(INDIR / "loan_office_certificates_cleaned.csv")
    loan_office_certs["raw_name_state"] = loan_office_certs["raw_name"] + "||" + loan_office_certs["state"]
    post_1790 = pd.read_csv(INDIR / "post_1790.csv")
    return loan_office_certs, post_1790


def MarkMatchedStatus(loan_office_certs, post_1790):
    post_1790["recon_id"] = post_1790["Column"].apply(lambda x: f"A{x + 2}:Z{x + 2}")
    matched_recon_ids = (
        loan_office_certs.loc[loan_office_certs["matched_status"], "recon_id"]
        .dropna()
        .unique()
    )
    post_1790["matched_status"] = post_1790["recon_id"].isin(matched_recon_ids)
    post_1790["raw_name_state"] = post_1790["Group Name"].str.upper() + "||" + post_1790["state"]
    return post_1790


def ExportTop5Debtholders(loan_office_certs):
    top5 = (
        loan_office_certs.groupby("raw_name_state")["Face Value"]
        .sum()
        .nlargest(5)
        .reset_index()
    )
    top5.columns = ["raw_name_state", "face_value"]
    SaveData(top5, ["raw_name_state"], OUTDIR / "top5_debtholders.csv", log_file=OUTDIR / "top5_debtholders.log")


def ExportStateDistribution(loan_office_certs):
    matched_df = loan_office_certs[loan_office_certs["matched_status"]]
    states_total = loan_office_certs.groupby("state")["raw_name_state"].nunique().sort_values(ascending=False)
    pct_states_total = (states_total / states_total.sum() * 100).rename("percent_total")
    matched_states = matched_df.groupby("state")["recon_id"].nunique().sort_values(ascending=False)
    matched_states.name = "debtholders"
    pct_matched = (matched_states / matched_states.sum() * 100).rename("percent_matched")
    state_dist = pd.concat([matched_states, pct_matched, pct_states_total], axis=1).reset_index()
    state_dist.columns = ["state", "debtholders", "percent_matched", "percent_total"]
    SaveData(state_dist, ["state"], OUTDIR / "state_distribution.csv", log_file=OUTDIR / "state_distribution.log")


def ComputePercentChange(loan_office_certs, post_1790):
    matched_df = loan_office_certs[loan_office_certs["matched_status"]]
    pre_totals = (
        matched_df.groupby(["recon_id", "raw_name_state"])["Face Value"]
        .sum()
        .rename("pre_value")
    )
    post_totals = (
        post_1790.groupby(["recon_id", "raw_name_state"])["final_total_adj"]
        .sum()
        .rename("post_value")
    )
    occ_map = (
        post_1790.drop_duplicates(subset="recon_id")
        .loc[:, ["recon_id", "occupation", "Group Town"]]
    )
    combined = (
        pre_totals.reset_index()
        .merge(post_totals.reset_index(), on=["recon_id", "raw_name_state"], how="inner")
        .merge(occ_map, on="recon_id", how="left")
    )
    combined["percent_change"] = (
        (combined["post_value"] - combined["pre_value"]) / combined["pre_value"] * 100
    )
    return combined


def ExportOutliers(combined):
    outliers = combined.sort_values(by="percent_change", ascending=False)
    top10 = outliers.head(10)[["recon_id", "raw_name_state", "pre_value", "post_value", "percent_change"]].copy()
    SaveData(
        top10,
        ["recon_id", "raw_name_state"],
        OUTDIR / "outliers_percent_change.csv",
        log_file=OUTDIR / "outliers_percent_change.log",
    )


def PlotPercentChangeDistribution(combined):
    min_percent = combined["percent_change"].min()
    max_percent = combined["percent_change"].max()

    fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True, figsize=(10, 4),
                                   gridspec_kw={"width_ratios": [3, 1]})
    bins_zoom = list(range(int(min_percent), 501, 20))
    ax1.hist(combined["percent_change"], bins=bins_zoom, edgecolor='black')
    ax1.set_xlim(int(min_percent), 500)
    ax1.set_title("Zoomed")
    ax1.set_xlabel("Percent Change")

    bins_full = [min_percent, -50, -25, 0, 25, 50, 100, 200, 500, 1000, 2000, 4000, max_percent]
    ax2.hist(combined["percent_change"], bins=bins_full, edgecolor='black')
    ax2.set_xlim(-100, 8000)
    ax2.set_title("Full Range")
    ax2.set_xlabel("Percent Change")

    fig.suptitle("Distribution of % Change in Holdings")
    ax1.set_ylabel("Number of Individuals")
    plt.tight_layout()
    plt.savefig(OUTDIR / "percent_change_distribution.png")
    plt.close()


def ExportOccupationCounts(post_1790, loan_office_certs):
    matched_df = loan_office_certs[loan_office_certs["matched_status"]]
    pre_totals = matched_df.groupby("recon_id")["Face Value"].sum().rename("pre_1790_total")
    post_1790_matched = post_1790[post_1790["matched_status"]].copy()
    post_1790_matched["pre_1790_total"] = post_1790_matched["recon_id"].map(pre_totals).fillna(0)

    occupation_counts = post_1790_matched.groupby("occupation").agg(
        count=("occupation", "size"),
        pre_1790_total=("pre_1790_total", "sum"),
        post_1790_total=("final_total_adj", "sum"),
    ).sort_values("count", ascending=False)

    total_post1790 = occupation_counts['post_1790_total'].sum()
    total_pre1790 = occupation_counts['pre_1790_total'].sum()
    occupation_counts['percent_of_pre1790_total'] = occupation_counts['pre_1790_total'] / total_pre1790 * 100
    occupation_counts['percent_of_post1790_total'] = occupation_counts['post_1790_total'] / total_post1790 * 100
    occupation_counts['net_pct_change'] = (
        (occupation_counts['post_1790_total'] - occupation_counts['pre_1790_total'])
        / occupation_counts['pre_1790_total'] * 100
    )
    occupation_counts = occupation_counts.reset_index()
    SaveData(
        occupation_counts,
        ["occupation"],
        OUTDIR / "occupation_counts.csv",
        log_file=OUTDIR / "occupation_counts.log",
    )


def IsFemale(raw_first_name):
    if not isinstance(raw_first_name, str) or not raw_first_name.strip():
        return False
    first = raw_first_name.strip().split()[0].strip(".,").capitalize()
    return first in FEMALE_NAMES_1780


def ExtractFirstName(full_name):
    return full_name.strip().split()[0].strip(".,").capitalize()


def ExportGenderSummary(loan_office_certs, post_1790):
    loc_copy = loan_office_certs.drop_duplicates(subset="raw_name_state").copy()
    loc_copy["is_female"] = loc_copy["raw_first_name_1"].apply(IsFemale)
    pct_women_loan_office = loc_copy["is_female"].mean() * 100

    liquidated_debt = pd.read_csv(INDIR / "liquidated_debt_certificates.csv")
    liquidated_debt.rename(columns={'uid': 'raw_name_state'}, inplace=True)
    liquidated_debt = liquidated_debt.drop_duplicates(subset="raw_name_state")
    liquidated_debt["is_female"] = liquidated_debt["raw_first_name_1"].apply(IsFemale)
    pct_women_liquidated = liquidated_debt["is_female"].mean() * 100

    pierce_certs = pd.read_csv(INDIR / "pierce_certificates.csv")
    pierce_certs = pierce_certs.drop_duplicates(subset="raw_name_state")
    pierce_certs["is_female"] = pierce_certs["raw_first_name_1"].apply(IsFemale)
    pct_women_pierce = pierce_certs["is_female"].mean() * 100

    post_1790_copy = post_1790.copy()
    post_1790_copy["first_name"] = post_1790_copy["Group Name"].apply(ExtractFirstName)
    post_1790_copy["is_female"] = post_1790_copy["first_name"].apply(IsFemale)
    pct_women_post1790 = post_1790_copy["is_female"].mean() * 100

    gender_summary = pd.DataFrame({
        "dataset": ["Loan Office Certs", "Liquidated Debt Certs", "Pierce Certs", "Post-1790"],
        "pct_women": [pct_women_loan_office, pct_women_liquidated, pct_women_pierce, pct_women_post1790],
    })
    SaveData(
        gender_summary,
        ["dataset"],
        OUTDIR / "gender_summary.csv",
        log_file=OUTDIR / "gender_summary.log",
    )


def ExportRatioAnalysis(post_1790, loan_office_certs):
    post_matched = post_1790[post_1790["matched_status"]].copy()
    summary = (
        post_matched.groupby("recon_id")[["6p_total_adj", "6p_def_total_adj"]]
        .sum()
        .rename(columns={"6p_total_adj": "six_percent_amt", "6p_def_total_adj": "deferred_amt"})
    )
    summary["post_total"] = summary["six_percent_amt"] + summary["deferred_amt"]
    summary["ratio_six"] = summary["six_percent_amt"] / summary["post_total"]
    summary["ratio_deferred"] = summary["deferred_amt"] / summary["post_total"]

    matched_df = loan_office_certs[loan_office_certs["matched_status"]]
    pre_totals = (
        matched_df.groupby("recon_id")["Face Value"]
        .sum()
        .rename("pre_total")
        .reset_index()
    )
    summary = summary.reset_index().merge(pre_totals, on="recon_id", how="left")

    EXPECTED_SIX, EXPECTED_DEF = 2 / 3, 1 / 3
    summary["expected_six_amt"] = summary["pre_total"] * EXPECTED_SIX
    summary["expected_deferred_amt"] = summary["pre_total"] * EXPECTED_DEF

    tol = 0.005
    summary["in_ratio_tolerance"] = summary["ratio_six"].between(
        EXPECTED_SIX - tol, EXPECTED_SIX + tol
    )
    print(f"Fraction matching within ±{tol * 100:.1f}%-points: {summary['in_ratio_tolerance'].mean():.3f}")
    SaveData(summary, ["recon_id"], OUTDIR / "ratio_analysis.csv", log_file=OUTDIR / "ratio_analysis.log")


def PlotMatchedByState(loan_office_certs):
    matched_df = loan_office_certs[loan_office_certs["matched_status"]]
    state_summary = (
        loan_office_certs.groupby("state")["raw_name_state"].nunique()
    )
    matched_summary = matched_df.groupby("state")["raw_name_state"].nunique()
    pct_matched = (matched_summary / state_summary * 100).sort_values(ascending=False).fillna(0)

    plt.figure(figsize=(10, 6))
    pct_matched.plot(kind='bar', color='steelblue')
    plt.ylabel("% Matched")
    plt.title("Percent Matched by State")
    plt.xlabel("State")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(OUTDIR / "pct_matched_by_state.png")
    plt.close()


if __name__ == "__main__":
    Main()
