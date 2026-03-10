from pathlib import Path
import pandas as pd
import re
from source.lib.SaveData import SaveData

INDIR_RESULTS = Path("output/derived/postscrape/family_tree")
INDIR_DATA = Path("output/analysis/open_refine_analysis")
OUTDIR = Path("output/analysis/family_tree_analysis")
OUTDIR.mkdir(parents=True, exist_ok=True)


def Main():
    task3 = pd.read_csv(INDIR_RESULTS / "candidate_matches.csv")
    post1790 = pd.read_csv(INDIR_DATA / "post_1790.csv")
    summary = ClassifyNonMatches(task3, post1790)
    SaveData(summary, ['reason'], OUTDIR / "non_match_reasons.csv", log_file=OUTDIR / "non_match_reasons.log")


def NormName(s):
    if pd.isna(s):
        return None
    s = str(s).lower().strip()
    s = re.sub(r"[.,'`]", "", s)
    s = re.sub(r"\s+", " ", s)
    return s


def NormState(s):
    if pd.isna(s):
        return None
    return str(s).strip().upper()


def Classify(n):
    if n == 0:
        return "No entries"
    if n == 1:
        return "Single entry (unmatched)"
    return "Multiple entries"


def ClassifyNonMatches(task3, post1790):
    non_matches = task3[task3["in_post1790"] == False].copy()

    non_matches["_name"] = non_matches["child_name"].map(NormName)
    non_matches["_state"] = non_matches["state"].map(NormState)

    post1790["_name"] = post1790["raw_name"].map(NormName)
    post1790["_state"] = post1790["state"].map(NormState)

    id_col = "Group Match Url" if "Group Match Url" in post1790.columns else "Full Search Name"
    post_counts = (
        post1790
        .dropna(subset=["_name", "_state"])
        .groupby(["_name", "_state"], as_index=False)[id_col]
        .nunique()
        .rename(columns={id_col: "candidate_count"})
    )

    counts = non_matches.merge(post_counts, on=["_name", "_state"], how="left")
    counts["candidate_count"] = counts["candidate_count"].fillna(0).astype(int)
    counts["reason"] = counts["candidate_count"].apply(Classify)

    summary = counts["reason"].value_counts().to_frame("count")
    summary["proportion"] = (summary["count"] / len(counts) * 100).round(2)
    return summary.reset_index().rename(columns={"index": "reason"})


if __name__ == "__main__":
    Main()
