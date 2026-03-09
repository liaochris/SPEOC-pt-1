# task_3.py
import json, csv, os
import pandas as pd
from pathlib import Path
from source.scrape.wikitree.wikitree import get_profile

INDIR_WIKITREE = Path("output/scrape/wikitree")
INDIR_POST1790 = Path("output/derived/postscrape/post1790_cd")
OUTDIR         = Path("output/derived/postscrape/family_tree")

EDGES_JSON   = INDIR_WIKITREE / "family_graph_edges.json"
POST1790_CSV = INDIR_POST1790 / "final_data_CD.csv"
OUT_CSV      = OUTDIR / "candidate_matches.csv"
PROCESSED    = OUTDIR / "processed_children.txt"

STATE_FULL_TO_ABBR = {
    "CONNECTICUT": "CT",
    "DELAWARE": "DE",
    "MASSACHUSETTS": "MA",
    "MARYLAND": "MD",
    "NEW HAMPSHIRE": "NH",
    "NEW JERSEY": "NJ",
    "NEW YORK": "NY",
    "PENNSYLVANIA": "PA",
    "VIRGINIA": "VA",
}

STATE_FULL = list(STATE_FULL_TO_ABBR.keys())

def load_processed():
    if not PROCESSED.exists(): return set()
    with PROCESSED.open() as f:
        return {line.strip() for line in f if line.strip()}

def append_processed(child_id):
    with PROCESSED.open("a") as f:
        f.write(child_id + "\n")

def append_row(row: dict, out_csv: Path):
    new_file = not out_csv.exists()
    with out_csv.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["child_id","child_name","state","in_post1790","error"])
        if new_file:
            w.writeheader()
        w.writerow(row)
        f.flush()           # push to OS buffers
        os.fsync(f.fileno())# ensure durable write

def norm(s: str) -> str:
    return s.strip().lower()

def build_name(p: dict) -> str:
    # Prefer "RealName + LastNameCurrent/AtBirth"; fall back sensibly
    first = p.get("RealName") or p.get("FirstName") or ""
    last  = p.get("LastNameCurrent") or p.get("LastNameAtBirth") or ""
    full  = (f"{first} {last}").strip()
    if not full:
        full = p.get("LongName") or p.get("BirthName") or p.get("Name") or ""
    return full

def extract_state_coords(location: str) -> str:
    if not location:
        return ""
    t = location.upper()
    for full in STATE_FULL:
        if full in t:
            return STATE_FULL_TO_ABBR[full]
        
    return ""

def run_task3(edges_json: str, post1790_csv: str, out_csv: str, fetch_profile=get_profile) -> dict:
    out_csv = Path(out_csv)
    # 1) Load unique child_ids from edges
    edges = json.loads(Path(edges_json).read_text(encoding="utf-8"))

    child_ids = set()
    for e in edges:
        if e.get("child_id"):
            child_ids.add(e["child_id"])

    # 2) Load post-1790 names, state into a normalized set
    post_1790_df = pd.read_csv(post1790_csv)
    post_pairs = set(zip(post_1790_df["Group Name"].fillna("").map(norm), post_1790_df["Group State"].fillna("")))

    # 3) For each child_id: fetch profile, build name, test membership
    out_rows = []
    processed = load_processed()
    to_do = sorted(child_ids - processed)

    for i, cid in enumerate(sorted(to_do), 1):
        try:
            prof = fetch_profile(profile_key=cid) or {}
        except Exception as e:
            row = {"child_id": cid, "child_name": "", "state":"", "in_post1790": None, "error": str(e)}
            out_rows.append(row)
            append_row(row, out_csv=out_csv)
            continue

        child_name = build_name(prof)
        n_child = norm(child_name)

        # Extract state from BirthLocation, fallback to DeathLocation
        st_child = extract_state_coords(prof.get("BirthLocation") or "") or extract_state_coords(prof.get("DeathLocation") or "")

        if n_child and st_child:
            match = (n_child, st_child) in post_pairs
        else:
            match = False

        row = {
            "child_id": cid,
            "child_name": child_name,
            "state": st_child,
            "in_post1790": match,
            "error": ""
        }

        out_rows.append(row)
        append_row(row, out_csv=out_csv)       # checkpoint result
        append_processed(cid)

        print(f"[CHILD] {i}/{len(to_do)}: {cid} | {child_name} | State: {st_child or 'N/A'} | ")

    # Quick summary
    total = len(out_rows)
    hits = sum(1 for r in out_rows if r["in_post1790"] is True)
    print(f"Done. Checked {total} children; matches in post-1790: {hits}. Results -> {out_csv}")

    return {"total":total, "hits":hits}

if __name__ == "__main__":
    run_task3(EDGES_JSON, POST1790_CSV, OUT_CSV, fetch_profile=get_profile)