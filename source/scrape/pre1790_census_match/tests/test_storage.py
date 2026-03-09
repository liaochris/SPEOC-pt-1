import json
import csv
import pytest
import source.lib.ancestry_scraper.storage as storage
from source.lib.ancestry_scraper.storage import LoadProgress, SaveProgress, AppendResult

def test_load_and_save_progress(tmp_path, monkeypatch):
    state = "DE"
    monkeypatch.setattr(storage, "_ProgressPath", lambda s: tmp_path / f"progress_{s}.json")
    data = {"Alice": "done"}
    SaveProgress(data, state)
    loaded = LoadProgress(state)
    assert loaded == data

def test_append_result_creates_and_appends(tmp_path, monkeypatch):
    state = "DE"
    out = tmp_path / f"results_{state}.csv"
    monkeypatch.setattr(storage, "_ResultsPath", lambda s: tmp_path / f"results_{s}.csv")
    AppendResult(["A", 1777, "1_1", 0, "url", "Complete Match", "County"], state)
    with open(out) as f:
        reader = list(csv.reader(f))
    assert reader[0] == ["name", "year", "match_strategy", "year_offset", "url", "match_status", "counties"]
    assert reader[1] == ["A", "1777", "1_1", "0", "url", "Complete Match", "County"]
    AppendResult(["B", 1780, "s_s", 1, "u2", "No Match", ""], state)
    with open(out) as f:
        reader = list(csv.reader(f))
    assert reader[2] == ["B", "1780", "s_s", "1", "u2", "No Match", ""]
