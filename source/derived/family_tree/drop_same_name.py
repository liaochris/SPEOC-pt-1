# task_4_drop_same_name.py
import pandas as pd
from pathlib import Path
from source.scrape.wikitree.wikitree import get_profile
from source.derived.family_tree.match_candidates import build_name, norm

INDIR  = Path("output/derived/family_tree")
OUTDIR = Path("output/derived/family_tree")

IN_CSV  = INDIR / "task_4_matches_filtered.csv"
OUT_CSV = OUTDIR / "task_4_matches_filtered_nosamenames.csv"

def drop_same_parent_child_names(in_csv=IN_CSV, out_csv=OUT_CSV, fetch_profile=get_profile) -> pd.DataFrame:
    df = pd.read_csv(in_csv)

    # Build a cache of parent_id -> parent_name (one API call per unique parent)
    parent_ids = sorted({pid for pid in df.get("parent_id", []) if isinstance(pid, str) and pid.strip()})
    cache = {}
    for i, pid in enumerate(parent_ids, 1):
        try:
            prof = fetch_profile(profile_key=pid) or {}
        except Exception:
            prof = {}
        cache[pid] = build_name(prof)

        print(f"[PARENT] {i}/{len(parent_ids)} fetched: {pid} -> {cache[pid]}")

    # Attach parent_name and compare normalized names
    df["parent_name"] = df["parent_id"].map(cache).fillna("")
    df["child_name_norm"] = df["child_name"].map(norm)
    df["parent_name_norm"] = df["parent_name"].map(norm)

    before = len(df)
    filtered = df[df["child_name_norm"] != df["parent_name_norm"]].copy()
    removed = before - len(filtered)

    # Tidy helper cols
    filtered.drop(columns=["child_name_norm", "parent_name_norm"], inplace=True)

    Path(out_csv).parent.mkdir(parents=True, exist_ok=True)
    filtered.to_csv(out_csv, index=False)

    print(f"[DONE] Input rows: {before} | Removed same-name rows: {removed} | Output rows: {len(filtered)}")
    print(f"[OUT] {out_csv}")
    return filtered

if __name__ == "__main__":
    drop_same_parent_child_names()