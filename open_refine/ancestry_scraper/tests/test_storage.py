import os
import json
import csv
import pytest
from ancestry_scraper.storage import load_progress, save_progress, append_result

def test_load_and_save_progress(tmp_path, monkeypatch):
    ckpt = tmp_path / "progress.json" # points to a fresh temporary directory
    monkeypatch.setenv("CHECKPOINT_FILE", str(ckpt))  # target our temp file instead of a real one
    data = {"Alice": "done"} # create a simple dict
    save_progress(data) # save progress
    loaded = load_progress() # immediately load progress
    assert loaded == data # our dict should be the only data

def test_append_result_creates_and_appends(tmp_path, monkeypatch):
    out = tmp_path / "results.csv" 
    monkeypatch.setattr("storage.OUTPUT_CSV", str(out), raising=True)
    # first append writes header
    append_result(["A", "url", "County"])
    with open(out) as f:
        reader = list(csv.reader(f))
    assert reader[0] == ["name", "search_url", "residence_county"] # row 0 should be the header
    assert reader[1] == ["A", "url", "County"] # row 1 should be the only data we added
    # second append just adds a new row
    append_result(["B", "u2", "C2"])
    with open(out) as f:
        reader = list(csv.reader(f))
    assert reader[2] == ["B", "u2", "C2"] # check if row 2 exists