import json
import pandas as pd
from pathlib import Path
from source.lib.SaveData import SaveData

INDIR_WIKITREE = Path("output/scrape/wikitree")
INDIR          = Path("output/derived/postscrape/family_tree")
OUTDIR         = Path("output/derived/postscrape/family_tree")

EDGES_JSON   = INDIR_WIKITREE / "family_graph_edges.json"
PROFILES_CSV = INDIR_WIKITREE / "wikitree_profiles.csv"
IN_CSV       = INDIR / "candidate_matches.csv"
OUT_CSV      = OUTDIR / "filtered_matches.csv"

CENTER_YEAR          = 1760
YEAR_WINDOW          = 20
DROP_IF_MISSING_YEAR = True


def Main():
    child_to_parent, child_to_parents_all = ChildToParentMaps(EDGES_JSON)

    df  = pd.read_csv(IN_CSV)
    tmp = df[df["in_post1790"] == True].copy()

    profiles = pd.read_csv(PROFILES_CSV, usecols=["id", "birth_date"])
    profiles = profiles.rename(columns={"id": "child_id"})
    tmp = tmp.merge(profiles, on="child_id", how="left")
    tmp["birth_year"] = tmp["birth_date"].map(ToYear)

    lo, hi = CENTER_YEAR - YEAR_WINDOW, CENTER_YEAR + YEAR_WINDOW
    in_range = tmp["birth_year"].between(lo, hi)
    if DROP_IF_MISSING_YEAR:
        filtered = tmp[in_range].copy()
    else:
        filtered = tmp[in_range | tmp["birth_year"].isna()].copy()

    filtered = filtered.drop(columns=["birth_date", "birth_year"])
    filtered["parent_id"]      = filtered["child_id"].map(child_to_parent)
    filtered["parent_ids_all"] = filtered["child_id"].map(child_to_parents_all)

    print(f"Initial matches: {len(tmp)}")
    print(f"After birth-year filter [{lo}-{hi}]: {len(filtered)}")

    OUTDIR.mkdir(parents=True, exist_ok=True)
    SaveData(filtered, ["child_id"], OUT_CSV, log_file=OUTDIR / "filtered_matches.log")


def ChildToParentMaps(edges_json):
    edges = json.loads(Path(edges_json).read_text(encoding="utf-8"))
    parents_by_child = {}
    for e in edges:
        c = e.get("child_id")
        p = e.get("parent_id")
        if not c or not p:
            continue
        parents_by_child.setdefault(c, set()).add(p)

    single     = {}
    all_joined = {}
    for c, ps in parents_by_child.items():
        sorted_ps     = sorted(ps)
        single[c]     = sorted_ps[0]
        all_joined[c] = ";".join(sorted_ps)
    return single, all_joined


def ToYear(val):
    s = str(val or "")[:4]
    if not s.isdigit():
        return None
    return int(s)


if __name__ == "__main__":
    Main()
