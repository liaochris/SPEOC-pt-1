from pathlib import Path
import pandas as pd
from source.lib.SaveData import SaveData

INDIR_DERIVED = Path("output/derived/postscrape/post1790_cd")
OUTDIR = Path("output/analysis/debt_analysis")
OUTDIR.mkdir(parents=True, exist_ok=True)

NAMES = [
    "Jedediah Huntington", "Peter Colt", "John Gordon", "John Gibbons", "John Meals",
    "Benjamin Hardwood", "John Haywood", "John Taylor Gilman", "William Gardner",
    "Oliver Peabody", "Nathaniel Gilman", "John Stevens", "Gerard Bancker",
    "David Rittenhouse", "Henry Sherburne", "Thomas Taylor"
]
STATES = ["CT", "DE", "GA", "MA", "MD", "NC", "NH", "NJ", "NY", "PA", "RI", "SC"]


def Main():
    debt_data = pd.read_csv(INDIR_DERIVED / "final_data_CD.csv")
    debt_summary = BuildDebtSummary(debt_data)
    SaveData(debt_summary, ['State'], OUTDIR / "debt_summary.csv", log_file=OUTDIR / "debt_summary.log")


def BuildDebtSummary(debt_data):
    state_patterns = (
        ["state of " + s.lower() for s in STATES]
        + ["commonwealth of " + s.lower() for s in STATES]
    )
    filtered_data = debt_data[
        (debt_data["Group State"].isin(STATES))
        | (debt_data["Group Name"].isin(NAMES))
        | (debt_data["Group Name"].str.lower().isin(state_patterns))
    ]
    public_debt = filtered_data.groupby("Group State")["final_total_adj"].sum().reindex(STATES, fill_value=0)
    debt_summary = pd.DataFrame({
        "State": STATES,
        "Public Debt": public_debt.values.astype(int),
    })
    return debt_summary


if __name__ == "__main__":
    Main()
