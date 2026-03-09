import pandas as pd
from pathlib import Path
from source.lib.SaveData import SaveData
from source.lib.ancestry_scraper.config import STATE_COLLECTION_URLS

INDIR  = Path("output/derived/postscrape/family_tree")
OUTDIR = Path("output/derived/postscrape/family_tree")

IN_CSV        = INDIR / "filtered_matches_no_same_name.csv"
OUT_FINAL     = OUTDIR / "final_matches.csv"
OUT_REVIEW    = OUTDIR / "review_matches.csv"

VALID_STATES = set(STATE_COLLECTION_URLS.keys())


def Main():
    df = pd.read_csv(IN_CSV)

    df = df[df["state"].isin(VALID_STATES)]
    df = df.sort_values(["child_id"]).drop_duplicates("child_id", keep="first")
    df["multi_parent"] = df["parent_ids_all"].fillna("").str.contains(";")

    review_mask = df["multi_parent"] | df["state"].isna()
    keep   = df[~review_mask].copy()
    review = df[review_mask].copy()

    OUTDIR.mkdir(parents=True, exist_ok=True)
    SaveData(keep,   ["child_id"], OUT_FINAL,  log_file=OUTDIR / "final_matches.log")
    SaveData(review, ["child_id"], OUT_REVIEW, log_file=OUTDIR / "review_matches.log")

    print(f"Final: {len(keep)} | Review: {len(review)}")


if __name__ == "__main__":
    Main()
