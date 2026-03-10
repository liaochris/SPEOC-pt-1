import json
import pandas as pd
from pathlib import Path
from source.lib.wikitree_utils import Norm, ExtractStateCoords
from source.lib.SaveData import SaveData

INDIR_WIKITREE = Path("output/scrape/wikitree")
INDIR_POST1790 = Path("output/derived/postscrape/post1790_cd")
OUTDIR         = Path("output/derived/postscrape/family_tree")

EDGES_JSON   = INDIR_WIKITREE / "family_graph_edges.json"
PROFILES_CSV = INDIR_WIKITREE / "wikitree_profiles.csv"
POST1790_CSV = INDIR_POST1790 / "final_data_CD.csv"
OUT_CSV      = OUTDIR / "candidate_matches.csv"
OUTDIR.mkdir(parents=True, exist_ok=True)


def Main():
    edges     = json.loads(EDGES_JSON.read_text(encoding="utf-8"))
    child_ids = {e["child_id"] for e in edges if e.get("child_id")}

    profiles = pd.read_csv(PROFILES_CSV)
    profiles = profiles[profiles["id"].isin(child_ids)].copy()

    post_1790_df = pd.read_csv(POST1790_CSV)
    post_pairs   = set(zip(
        post_1790_df["Group Name"].fillna("").map(Norm),
        post_1790_df["Group State"].fillna("")
    ))

    profiles["child_name"] = profiles["name"].fillna("")
    profiles["name_norm"]  = profiles["child_name"].map(Norm)
    profiles["state"]      = profiles["birth_location"].fillna("").map(ExtractStateCoords)
    no_state = profiles["state"] == ""
    profiles.loc[no_state, "state"] = profiles.loc[no_state, "death_location"].fillna("").map(ExtractStateCoords)

    profiles["in_post1790"] = profiles.apply(
        lambda r: bool(r["name_norm"] and r["state"] and (r["name_norm"], r["state"]) in post_pairs),
        axis=1
    )

    result = profiles[["id", "child_name", "state", "in_post1790", "error"]].rename(columns={"id": "child_id"})

    SaveData(result, ["child_id"], OUT_CSV, log_file=OUTDIR / "candidate_matches.log")

    hits = result["in_post1790"].sum()
    print(f"Done. Checked {len(result)} children; matches in post-1790: {hits}. Results -> {OUT_CSV}")


if __name__ == "__main__":
    Main()
