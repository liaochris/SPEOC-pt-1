from pathlib import Path
import pandas as pd
import re

INDIR_RESULTS = Path("output/scrape/wikitree/results")
INDIR_DATA = Path("output/scrape/wikitree/data")

def norm_name(s):
    if pd.isna(s): return None
    s = str(s).lower().strip()
    s = re.sub(r"[.,'`]", "", s)
    s = re.sub(r"\s+", " ", s)
    return s

def norm_state(s):
    if pd.isna(s): return None
    return str(s).strip().upper()

# --- Load
task3 = pd.read_csv(INDIR_RESULTS / "candidate_matches.csv")
post1790 = pd.read_csv(INDIR_DATA / "post_1790.csv")

# --- Filter to non-matches (boolean False)
non_matches = task3[task3["in_post1790"] == False].copy()

# --- Normalize join keys
non_matches["_name"]  = non_matches["child_name"].map(norm_name)
non_matches["_state"] = non_matches["state"].map(norm_state)

post1790["_name"]  = post1790["Name_Fix_Clean"].map(norm_name)
post1790["_state"] = post1790["Group State"].map(norm_state)

# --- Count distinct candidates per (name,state) in post_1790
# use a stable identifier; Group Match Url is good. Fall back to Full Search Name if needed.
id_col = "Group Match Url" if "Group Match Url" in post1790.columns else "Full Search Name"

post_counts = (
    post1790
    .dropna(subset=["_name","_state"])
    .groupby(["_name","_state"], as_index=False)[id_col]
    .nunique()
    .rename(columns={id_col: "candidate_count"})
)

# --- Attach counts to each non-matched child
counts = non_matches.merge(
    post_counts,
    on=["_name","_state"],
    how="left"
)
counts["candidate_count"] = counts["candidate_count"].fillna(0).astype(int)

# --- Classify
def classify(n):
    if n == 0:  return "No entries"
    if n == 1:  return "Single entry (unmatched)"
    return "Multiple entries"

counts["reason"] = counts["candidate_count"].apply(classify)

# --- Summarize
summary = (
    counts["reason"]
    .value_counts()
    .to_frame("count")
)
summary["proportion"] = (summary["count"] / len(counts) * 100).round(2)

print(summary)