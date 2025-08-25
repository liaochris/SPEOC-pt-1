import pandas as pd
import json
from pathlib import Path
from wikitree import get_profile  # your existing method
from task_3 import build_name, norm

IN_CSV = "results/task_3_matches.csv"
EDGES_JSON = "results/edges_task_2.json"
OUT_CSV = "results/task_4_matches_filtered.csv"

def to_year(val) -> int | None:
    s = str(val or "")[:4]

    if not s.isdigit():
        return None
    
    return int(s)

def _child_to_parent_maps(edges_json: str):
    """Return:
       - primary map: child_id -> a single parent_id (stable choice)
       - all map:     child_id -> 'p1;p2;...'(sorted, deduped)
    """
    edges = json.loads(Path(edges_json).read_text(encoding="utf-8"))
    parents_by_child = {}
    for e in edges:
        c = e.get("child_id")
        p = e.get("parent_id")
        if not c or not p:
            continue
        parents_by_child.setdefault(c, set()).add(p)

    single = {}
    all_joined = {}
    for c, ps in parents_by_child.items():
        sorted_ps = sorted(ps)
        single[c] = sorted_ps[0]            # pick the first, deterministically
        all_joined[c] = ";".join(sorted_ps) # keep all for transparency
    return single, all_joined


def refine_matches(
    in_csv: str = IN_CSV,
    edges_json: str = EDGES_JSON,
    out_csv: str = OUT_CSV,
    center_year: int = 1760,
    window: int = 20,
    drop_if_missing_year: bool = True,
    fetch_profile=get_profile
):
    # 0) Load edges -> child→parent maps
    child_to_parent, child_to_parents_all = _child_to_parent_maps(edges_json)

    df = pd.read_csv(in_csv)
    # 1) keep only matches
    tmp = df[df["in_post1790"] == True].copy()

    lo, hi = center_year - window, center_year + window
    keep_rows = []

    total = len(tmp)
    for i, (_, row) in enumerate(tmp.iterrows(), start=1):
        cid = row["child_id"]
        print(f"Child ID: {cid} | {i}/{total}")
        try:
            prof = fetch_profile(profile_key=cid) or {} # get child's profile
        except Exception:
            # if API fails, treat as drop (or keep by flipping this line)
            if not drop_if_missing_year:
                keep_rows.append(row)
            continue

        byear = to_year(prof.get("BirthDate")) # get birth date
        if byear is None:
            if not drop_if_missing_year: # keep row if there is no birth year
                keep_rows.append(row)
            continue

        if lo <= byear <= hi: # check if birth year is in range
            keep_rows.append(row)
        else:
            print(f"Child: {cid} birth date is out of range")
        # else: drop

    filtered = pd.DataFrame(keep_rows)


     # 2) Attach parent_id columns from edges
    if not filtered.empty:
        filtered["parent_id"] = filtered["child_id"].map(child_to_parent)
        filtered["parent_ids_all"] = filtered["child_id"].map(child_to_parents_all)

    Path(out_csv).parent.mkdir(parents=True, exist_ok=True)
    filtered.to_csv(out_csv, index=False)

    print(f"Initial matches: {len(tmp)}")
    print(f"After birth-year filter [{lo}-{hi}]: {len(filtered)}")
    return filtered

if __name__ == "__main__":
    refine_matches()