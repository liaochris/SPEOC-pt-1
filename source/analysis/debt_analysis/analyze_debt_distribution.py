from pathlib import Path
import numpy as np
import pandas
import matplotlib.pyplot as plt
import gender_guesser.detector as gender
from source.lib.SaveData import SaveData

INDIR_DERIVED = Path("output/derived/prescrape/pre1790")
INDIR_DERIVED_POST1790 = Path("output/derived/postscrape/post1790_cd")
INDIR_DELEGATES = Path("source/raw/delegates/orig")
OUTDIR = Path("output/analysis/pre1790")
OUTDIR.mkdir(parents=True, exist_ok=True)


def Main():
    agg_debt = LoadAndPrepare()
    PlotDebtByBracket(agg_debt)
    PlotPercentDebtByBracket(agg_debt)
    ExportGenderDistribution(agg_debt)
    ExportTop10Debtholders(agg_debt)
    ExportConstitutionalDelegates(agg_debt)
    ExportStateDelegates()


def LoadAndPrepare():
    agg_debt = pandas.read_csv(INDIR_DERIVED / "pre1790_cleaned.csv")
    agg_debt.drop(
        agg_debt.loc[
            agg_debt["to whom due | first name"].isna()
            & agg_debt["to whom due | last name"].isna()
        ].index,
        inplace=True,
    )
    agg_debt[["amount | dollars", "amount in specie | dollars", "amount in specie | cents"]] = agg_debt[
        ["amount | dollars", "amount in specie | dollars", "amount in specie | cents"]
    ].fillna(0)
    agg_debt["amount_total"] = (
        agg_debt["amount | dollars"]
        + agg_debt["amount in specie | dollars"]
        + agg_debt["amount in specie | cents"]
    )
    agg_debt["full_name"] = (
        agg_debt["to whom due | first name"] + " " + agg_debt["to whom due | last name"]
    )
    return agg_debt


def PlotDebtByBracket(agg_debt):
    agg_debt_sorted = agg_debt.sort_values(by="amount_total", ascending=False)
    agg_debt_split = [agg_debt_sorted.iloc[idx] for idx in np.array_split(np.arange(len(agg_debt_sorted)), 4)]
    amounts = [round(agg_debt_split[i]["amount_total"].sum() / 1_000_000, 2) for i in range(4)]

    bars = plt.bar(x=range(4), height=amounts, tick_label=["75-100th", "50-75th", "25-50th", "0-25th"])
    bars[0].set_color("#e41a1c")
    bars[1].set_color("#377eb8")
    bars[2].set_color("#4daf4a")
    bars[3].set_color("#984ea3")
    plt.xlabel("Debt Bracket (percentile)")
    plt.ylabel("Amount of Debt (dollars in millions)")
    plt.bar_label(bars, padding=1)
    plt.title("Amount of Debt Held By Debt Bracket")

    labels = [
        "$" + str(agg_debt_split[i]["amount_total"].iloc[0]) + " - " + str(agg_debt_split[i]["amount_total"].iloc[-1])
        for i in range(4)
    ]
    handles = [plt.Rectangle((0, 0), 1, 1, color=c, ec="k") for c in ["#e41a1c", "#377eb8", "#4daf4a", "#984ea3"]]
    plt.legend(handles=handles, labels=labels)
    plt.savefig(OUTDIR / "debt_by_bracket.png")
    plt.close()


def PlotPercentDebtByBracket(agg_debt):
    agg_debt_sorted = agg_debt.sort_values(by="amount_total", ascending=False)
    agg_debt_split = [agg_debt_sorted.iloc[idx] for idx in np.array_split(np.arange(len(agg_debt_sorted)), 4)]
    amounts = [round(agg_debt_split[i]["amount_total"].sum() / 1_000_000, 2) for i in range(4)]
    total_amt = agg_debt["amount_total"].sum() / 1_000_000
    percentages = [round(((amounts[i] / total_amt) * 100), 1) for i in range(4)]

    bars = plt.bar(["75-100th", "50-75th", "25-50th", "0-25th"], percentages)
    plt.xlabel("Debt Bracket (percentile)")
    plt.ylabel("Percentage of Total Debt (%)")
    plt.bar_label(bars, padding=1)
    plt.title("Percentage of Total Debt by Debt Bracket")
    plt.savefig(OUTDIR / "percent_debt_by_debt_bracket.png")
    plt.close()


def CountGenders(name, d):
    if not isinstance(name, str) or not name.strip():
        return "Unknown"
    result = d.get_gender(name, country="usa")
    if result == "male":
        return "Male"
    elif result == "female":
        return "Female"
    return "Unknown"


def ExportGenderDistribution(agg_debt):
    d = gender.Detector(case_sensitive=False)
    agg_debt["to whom due | first name"] = agg_debt["to whom due | first name"].astype(str)
    agg_debt["gender_prediction"] = agg_debt["to whom due | first name"].apply(CountGenders, args=(d,))
    count = agg_debt["gender_prediction"].value_counts(normalize=True) * 100
    gender_df = count.reset_index()
    gender_df.columns = ["gender_prediction", "percentage"]
    SaveData(
        gender_df,
        ["gender_prediction"],
        OUTDIR / "gender_distribution.csv",
        log_file=OUTDIR / "gender_distribution.log",
    )


def ExportTop10Debtholders(agg_debt):
    agg_debt_sorted = agg_debt.sort_values(by="amount_total", ascending=False)
    top10 = agg_debt_sorted.head(10)[
        ["to whom due | first name", "to whom due | last name", "amount_total", "state", "date of the certificate | year"]
    ].reset_index(drop=True)
    top10.index = range(1, len(top10) + 1)
    top10.index.name = "rank"
    top10 = top10.reset_index()
    SaveData(top10, ["rank"], OUTDIR / "top10_debtholders.csv", log_file=OUTDIR / "top10_debtholders.log")


def ExportConstitutionalDelegates(agg_debt):
    const_delegates = pandas.read_csv(INDIR_DELEGATES / "constitutional_convention_1787.csv")
    const_delegates["full_name"] = const_delegates["first name"] + " " + const_delegates["last name"]
    const_delegates["state"] = const_delegates["state"].str.strip()
    state_map = {
        "Connecticut": "ct", "Delaware": "de", "Georgia": "ga", "Maryland": "md",
        "Massachusetts": "ma", "New Hampshire": "nh", "New Jersey": "nj", "New York": "ny",
        "North Carolina": "nc", "Pennsylvania": "pa", "Rhode Island": "ri",
        "South Carolina": "sc", "Virginia": "va",
    }
    const_delegates["state"] = const_delegates["state"].map(state_map)

    exists_in_both = const_delegates.merge(agg_debt, on=["full_name", "state"], how="inner")
    exists_in_both = exists_in_both[["full_name", "amount_total", "state"]]
    delegates_with_debt = exists_in_both.groupby(["full_name", "state"]).agg({"amount_total": "sum"}).reset_index()
    SaveData(
        delegates_with_debt,
        ["full_name", "state"],
        OUTDIR / "const_delegates_with_debt.csv",
        log_file=OUTDIR / "const_delegates_with_debt.log",
    )


def ExportStateDelegates():
    state_delegates = pandas.read_csv(INDIR_DELEGATES / "state_delegates.csv")
    state_delegates["First Name"] = state_delegates["First Name"].fillna("")
    state_delegates["Last Name"] = state_delegates["Last Name"].fillna("")
    state_delegates["full_name"] = state_delegates["First Name"] + " " + state_delegates["Last Name"]
    state_delegates["state"] = state_delegates["State"].str.lower()

    agg_debt = pandas.read_csv(INDIR_DERIVED_POST1790 / "final_data_CD.csv")
    agg_debt["state"] = agg_debt["Group State"].str.lower()
    agg_debt["full_name"] = agg_debt["Group Name"]
    agg_debt["amount_total"] = agg_debt["final_total_adj"]

    exists_in_both = state_delegates.merge(agg_debt, on=["full_name", "state"], how="inner")
    exists_in_both = exists_in_both[["full_name", "amount_total", "state"]]
    delegates_with_debt = exists_in_both.groupby(["full_name", "state"]).agg({"amount_total": "sum"}).reset_index()
    SaveData(
        delegates_with_debt,
        ["full_name", "state"],
        OUTDIR / "state_delegates_with_debt.csv",
        log_file=OUTDIR / "state_delegates_with_debt.log",
    )

    pct_delegates_with_debt = len(delegates_with_debt) / len(state_delegates) * 100
    pct_debt_by_delegates = delegates_with_debt["amount_total"].sum() / agg_debt["amount_total"].sum() * 100

    summary = pandas.DataFrame({
        "group": [
            "State delegates with post-1790 debt (%)",
            "Post-1790 debt held by state delegates (%)",
        ],
        "value": [
            round(pct_delegates_with_debt, 2),
            round(pct_debt_by_delegates, 2),
        ],
    })
    SaveData(summary, ["group"], OUTDIR / "society_delegate_summary.csv", log_file=OUTDIR / "society_delegate_summary.log")


if __name__ == "__main__":
    Main()
