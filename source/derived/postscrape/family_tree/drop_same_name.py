import pandas as pd
from pathlib import Path
from source.lib.wikitree_utils import Norm
from source.lib.SaveData import SaveData

INDIR_WIKITREE = Path("output/scrape/wikitree")
INDIR          = Path("output/derived/postscrape/family_tree")
OUTDIR         = Path("output/derived/postscrape/family_tree")

PROFILES_CSV = INDIR_WIKITREE / "wikitree_profiles.csv"
IN_CSV       = INDIR / "filtered_matches.csv"
OUT_CSV      = OUTDIR / "filtered_matches_no_same_name.csv"


def Main():
    df       = pd.read_csv(IN_CSV)
    profiles = pd.read_csv(PROFILES_CSV, usecols=["id", "name"])
    profiles = profiles.rename(columns={"id": "parent_id", "name": "parent_name"})

    df = df.merge(profiles, on="parent_id", how="left")
    df["child_name_norm"]  = df["child_name"].fillna("").map(Norm)
    df["parent_name_norm"] = df["parent_name"].fillna("").map(Norm)

    before   = len(df)
    filtered = df[df["child_name_norm"] != df["parent_name_norm"]].copy()
    removed  = before - len(filtered)
    filtered.drop(columns=["parent_name", "child_name_norm", "parent_name_norm"], inplace=True)

    print(f"[DONE] Input rows: {before} | Removed same-name rows: {removed} | Output rows: {len(filtered)}")

    OUTDIR.mkdir(parents=True, exist_ok=True)
    SaveData(filtered, ["child_id"], OUT_CSV, log_file=OUTDIR / "filtered_matches_no_same_name.log")


if __name__ == "__main__":
    Main()
