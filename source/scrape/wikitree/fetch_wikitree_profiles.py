import csv
import json
import time
from pathlib import Path
from source.scrape.wikitree.wikitree import GetProfile
from source.lib.wikitree_utils import BuildName

INDIR  = Path("output/scrape/wikitree")
OUTDIR = Path("output/scrape/wikitree")

EDGES_JSON = INDIR / "family_graph_edges.json"
OUT_CSV    = OUTDIR / "wikitree_profiles.csv"
FIELDS     = ["id", "name", "birth_location", "death_location", "birth_date", "error"]

SLEEP_SEC   = 0.5
MAX_RETRIES = 3


def Main():
    edges   = json.loads(EDGES_JSON.read_text(encoding="utf-8"))
    all_ids = set()
    for e in edges:
        if e.get("child_id"):
            all_ids.add(e["child_id"])
        if e.get("parent_id"):
            all_ids.add(e["parent_id"])

    done  = LoadDoneIds(OUT_CSV)
    to_do = sorted(all_ids - done)
    print(f"Total IDs: {len(all_ids)} | Already fetched: {len(done)} | Remaining: {len(to_do)}")

    OUTDIR.mkdir(parents=True, exist_ok=True)
    for i, pid in enumerate(to_do, 1):
        row = {"id": pid, "name": "", "birth_location": "", "death_location": "", "birth_date": "", "error": ""}

        profile = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                profile = GetProfile(pid) or {}
                break
            except Exception as e:
                if attempt == MAX_RETRIES:
                    row["error"] = str(e)
                    print(f"[ERROR] {pid}: {e}")
                else:
                    time.sleep(1.5 ** attempt)

        if profile:
            row["name"]           = BuildName(profile)
            row["birth_location"] = profile.get("BirthLocation") or ""
            row["death_location"] = profile.get("DeathLocation") or ""
            row["birth_date"]     = profile.get("BirthDate") or ""

        AppendRow(row)
        print(f"[{i}/{len(to_do)}] {pid} -> {row['name'] or '(no name)'}")
        time.sleep(SLEEP_SEC)


def LoadDoneIds(path):
    if not path.exists():
        return set()
    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {row["id"] for row in reader if row.get("id")}


def AppendRow(row):
    new_file = not OUT_CSV.exists()
    with OUT_CSV.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new_file:
            w.writeheader()
        w.writerow(row)
        f.flush()


if __name__ == "__main__":
    Main()
