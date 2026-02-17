import csv, json
from pathlib import Path
from json import JSONDecodeError


ROOT = Path(__file__).parent.parent
PROGRESS_DIR = ROOT / "progress"
RESULTS_DIR  = ROOT / "results"

def _progress_path(state):
    PROGRESS_DIR.mkdir(exist_ok=True)
    return PROGRESS_DIR / f"progress_{state}.json"

def _results_path(state):
    RESULTS_DIR.mkdir(exist_ok=True)
    return RESULTS_DIR / f"results_{state}.csv"

def load_progress(state): # get current checkpoint file
    path = _progress_path(state)
    try:
        return json.load(path.open())
    except (FileNotFoundError, JSONDecodeError):
        return {}

def save_progress(data, state): # store data in checkpoint file 
    path = _progress_path(state)
    path.parent.mkdir(parents=True, exist_ok=True)
    json.dump(data, path.open("w"))


def append_result(row, state): # append row to csv file 
    path = _results_path(state)
    need_header = (not path.exists()) or path.stat().st_size == 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", newline="") as f:
        w = csv.writer(f)
        if need_header:
            w.writerow(["name","url","county"])
        w.writerow(row)