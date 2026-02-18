from pathlib import Path
import csv, json, os, time
from datetime import datetime, timezone
from source.scrape.wikitree.wikitree import get_profile
import logging
log = logging.getLogger(__name__)

OUTDIR = Path("output/scrape/wikitree/results")
INPUT_CSV = OUTDIR / "task_1.csv"
OUTPUT_JSONL = OUTDIR / "wikitree_bios.jsonl"
SLEEP_SEC = 0.5     # gentle on API
MAX_RETRIES = 3

def load_done_keys(path):
    """Return set of profile_keys already written to JSONL (for resume)."""
    if not os.path.exists(path):
        return set()
    done = set()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
                pk = obj.get("profile_key")
                if pk:
                    done.add(pk)
            except json.JSONDecodeError:
                pass
    return done


def main():
    count = 0
    done = load_done_keys(OUTPUT_JSONL)

    with open(INPUT_CSV, "r", encoding="utf-8-sig", newline="") as fin, \
         open(OUTPUT_JSONL, "a", encoding="utf-8") as fout:
        # initialize reader for input csv file 
        reader = csv.DictReader(fin)
        if "profile_key" not in reader.fieldnames:
            raise ValueError("task_1.csv must include a 'profile_key' column.")

        for row in reader:
            pk = (row.get("profile_key") or "").strip() # store profile key
            if not pk or pk in done: # skip if profile has already been looked up
                continue

            count += 1
            print(f"[{count}] Fetching profile {pk}...")

            # Basic record with the original CSV columns preserved
            record = dict(row)
            record["profile_key"] = pk
            record["pulled_at"] = datetime.now(timezone.utc).isoformat()
            record["status"] = "ok"
            record["error"] = None

            # Fetch with simple retries
            profile = None
            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    profile = get_profile(pk) or {}
                    break
                except Exception as e:
                    if attempt == MAX_RETRIES:
                        record["status"] = "error"
                        record["error"] = str(e)
                    else:
                        time.sleep(1.5 ** attempt)

            # Attach a few useful fields if present
            if profile:
                for f in [
                    "Id","Name","FirstName","LastNameCurrent","LastNameAtBirth","LongName",
                    "BirthDate","BirthLocation","DeathDate","DeathLocation","bio"
                ]:
                    record[f] = profile.get(f)

            print(f"Finished writing {pk} to file.")

            fout.write(json.dumps(record, ensure_ascii=False) + "\n")
            fout.flush()
            done.add(pk)
            time.sleep(SLEEP_SEC)

if __name__ == "__main__":
    main()