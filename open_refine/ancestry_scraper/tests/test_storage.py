import os
import json
import csv
import pytest
from ancestry_scraper.storage import load_progress, save_progress, append_result

def test_load_and_save_progress(tmp_path, monkeypatch):
    state = "DE"
    ckpt = tmp_path / f"progress_{state}.json" # points to a fresh temporary directory
    monkeypatch.setenv("CHECKPOINT_FILE", str(ckpt))  # target our temp file instead of a real one
    data = {"Alice": "done"} # create a simple dict
    save_progress(data, state) # save progress
    loaded = load_progress(state) # immediately load progress
    assert loaded == data # our dict should be the only data

def test_append_result_creates_and_appends(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    state = "DE"
    out = tmp_path / f"results_{state}.csv" 
    # monkeypatch.setattr("ancestry_scraper.storage.OUTPUT_CSV", str(out), raising=True)
    # first append writes header
    append_result(["A", "url", "County"], state)
    with open(out) as f:
        reader = list(csv.reader(f))
    assert reader[0] == ["name", "url", "county"] # row 0 should be the header
    assert reader[1] == ["A", "url", "County"] # row 1 should be the only data we added
    # second append just adds a new row
    append_result(["B", "u2", "C2"], state)
    with open(out) as f:
        reader = list(csv.reader(f))
    assert reader[2] == ["B", "u2", "C2"] # check if row 2 exists