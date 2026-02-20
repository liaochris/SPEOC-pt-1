import csv, json
from pathlib import Path
from json import JSONDecodeError


OUTDIR = Path("output/scrape/ancestry_loan_office_scraper")
PROGRESS_DIR = OUTDIR / "progress"
RESULTS_DIR  = OUTDIR / "results"

def _ProgressPath(state):
    PROGRESS_DIR.mkdir(parents=True, exist_ok=True)
    return PROGRESS_DIR / f"progress_{state}.json"

def _ResultsPath(state):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    return RESULTS_DIR / f"results_{state}.csv"

def LoadProgress(state):
    path = _ProgressPath(state)
    try:
        return json.load(path.open())
    except (FileNotFoundError, JSONDecodeError):
        return {}

def SaveProgress(data, state):
    path = _ProgressPath(state)
    path.parent.mkdir(parents=True, exist_ok=True)
    json.dump(data, path.open("w"))


def AppendResult(row, state):
    path = _ResultsPath(state)
    need_header = (not path.exists()) or path.stat().st_size == 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", newline="") as f:
        w = csv.writer(f)
        if need_header:
            w.writerow(["name", "year", "match_strategy", "year_offset", "url", "match_status", "counties"])
        w.writerow(row)
